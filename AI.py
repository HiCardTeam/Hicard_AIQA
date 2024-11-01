
from openai import OpenAI
from googlesearch import search
import os
client = OpenAI(api_key=os.environ.get('openAI_api_key'))

ASSISTANT_ID=os.environ.get('ASSISTANT_ID')
def google_res(user_msg, num_results=5, verbose=False):
    content = "以下是根據搜尋得到的可信資料：\n"  # 強調資料可靠
    results = search(user_msg, advanced=True, num_results=num_results, lang='zh-TW')
    
    # 確保搜尋到結果
    if results:
        for res in results:
            content += f"標題：{res.title}\n摘要：{res.description}\n\n"
        content += "請依照以上資料回答您的問題。\n"  # 增加回應的指導性
    else:
        content += "抱歉，沒有找到相關結果，可能需要更多信息或精確的問題描述。\n"
    
    if verbose:
        print('------------')
        print(content)
        print('------------')
        
    return content
tools_list=[
    {"type": "code_interpreter"}, 
    {"type": "file_search"},
    {
        "type": "function",
        "function": {
            "name": "google_res",
            "description": "在遇到難以確認或實時性問題時，自動以 Google 搜尋結果補充參考資料。適用於學術問題，回傳搜尋到的相關事實資料以幫助回答。",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_msg": {
                        "type": "string",
                        "description": "從使用者的問題中擷取的主要關鍵字，用於 Google 搜尋。"
                    }
                },
                "required": ["user_msg"]
            }
        }
    }
]


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

def statusHandler(run,_threadId):
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
    elif run.status=='requires_action':
        tool_outputs = []
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "google_res":
                arguments=tool.function.arguments
                tool_outputs.append({"tool_call_id": tool.id, "output": google_res(arguments)})
                print(f'呼叫google search，關鍵字:{arguments}')
            else:
                print('找不到要呼叫的function')
        client.beta.threads.runs.submit_tool_outputs_stream(
        thread_id=_threadId,
        run_id=run.id,
        tool_outputs=tool_outputs
        ) 
    else:
        print('對話未完成。')

def  create_run(_threadId):
    global ASSISTANT_ID
    run=client.beta.threads.runs.create_and_poll(
        thread_id=_threadId,
        assistant_id=ASSISTANT_ID,
    )
    print("Run completed with status: " + run.status)
    response=statusHandler(run,_threadId)
    if(response):
        return response

def show_message(_threadId):
    message=client.beta.threads.messages.list(thread_id=_threadId)
    print(message)

  
