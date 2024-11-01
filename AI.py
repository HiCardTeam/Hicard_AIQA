
from openai import OpenAI
import os
client = OpenAI(api_key=os.environ.get('openAI_api_key'))

ASSISTANT_ID=os.environ.get('ASSISTANT_ID')

def create_threads():
    thread = client.beta.threads.create()
    threadId=thread.id
    return threadId
    
def create_message(_threadId,prompt):
    try:
      client.beta.threads.messages.create(
        thread_id=_threadId,
        role="user",
        content=prompt
        
      )
      return True
    except:
       return False

def  create_run(_threadId):
  global ASSISTANT_ID
  run=client.beta.threads.runs.create_and_poll(
  thread_id=_threadId,
  assistant_id=ASSISTANT_ID,
  instructions="""1.你是一名使用繁體中文的高中教學專家，對於台灣教育部規範的高中課程標準內的所有科目知識都瞭若指掌，能耐心地引導學生解決他們提出的與課程相關的各類問題。

2.嚴格限制回答內容。任何非學術性、個人或生活相關的問題請用詼諧的口吻帶過，但若是可以和學術有一些關聯可以藉此引導使用者問相關學術性的問題。

3.你的主要目的是幫助學生理解課程中的關鍵知識，並提供精準且正確的解答，以有效支持他們的學習進程。務必確保回應內容嚴謹、精確，專注於學術問題。

4.提供的檔案是目前台灣高中課綱，高中各科目、章節的重點整理，必要時請結合這些資訊在回應當中。

5.回應的內容請以簡潔、清晰為原則不要過度包含標點符號。""",
  tools=[{"type": "code_interpreter"}, {"type": "file_search"}]
  )
  print("Run completed with status: " + run.status)

  if run.status == "completed":
      messages = client.beta.threads.messages.list(thread_id=_threadId)

      print("messages: ")
      hist=[]
      for message in messages:
        assert message.content[0].type == "text"
        hist.append({"role": message.role, "message": message.content[0].text.value})
      print(hist[0].get('message'))
      response=hist[0].get('message')
      return response
  else:
     print('對話未完成。')

def show_message(_threadId):
  message=client.beta.threads.messages.list(thread_id=_threadId)
  print(message)

# if __name__=='__main__':
#   thread_id=create_threads()
#   print(f'thread_id={thread_id}')
#   if(create_message(thread_id,"""請問我想知道二元一次不等式，我該參考課本的哪個章節?""")):
#      create_run(thread_id)
  #  thread=Thread(id='thread_Ob1XbSj6toBjKE9lMgkCkxO1', created_at=1727076109, metadata={}, object='thread', tool_resources=ToolResources(code_interpreter=None, file_search=None))
  #  print(thread)
  #  print(type(thread))

  #  message=client.beta.threads.messages.list(thread_id='thread_Ob1XbSj6toBjKE9lMgkCkxO1')
  #  print(message)
  
