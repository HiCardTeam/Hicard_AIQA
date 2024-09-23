from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent,TextMessage,TextSendMessage
import AI
import os

line_bot_api=LineBotApi(os.environ.get('Channel_Access_Token','1KKOJpceMmNof1Xz/JzRmh63Iokah8moV7KXm+uQFsFmnHKY+mTPOjCuf4lyiZpFhLPj0i0X7IKHbaAbC9NQKRUY55bCoDIAnwg8ujKBnNnxi6rVs3EBR3eRIoF7+qvL+BTx2TlxWXkYQc0nvdjhGAdB04t89/1O/w1cDnyilFU='))
handler=WebhookHandler(os.environ.get('Channel_Secret','8419465688f737a4827064f51a49793d') )#secret

usingAI={}

@app.route("/callback" , methods = ['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    mtext=event.message.text

    if user_id in usingAI:
        threadId=usingAI[user_id].get('thread_id')
        print(f'user_id:{user_id} is in thread:{threadId}')
    else:
        threadId=AI.create_threads()
        if threadId!='':
            usingAI[user_id]={'thread_id':threadId}
            print(f'user_id:{user_id} is now in thread:{threadId}')
    
    if(AI.create_message(threadId,mtext)):
        pushMSG(user_id)
        response=AI.create_run(threadId)
    message=TextSendMessage(text=response)
    line_bot_api.reply_message(event.reply_token,message)

def pushMSG(user_id):
    message=TextSendMessage(text='回應生成中...')
    line_bot_api.push_message(to=user_id,messages=[message])
    return True
if __name__ == '__main__':
    app.run()
    
