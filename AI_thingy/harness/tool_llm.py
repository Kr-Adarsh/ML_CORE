import os 
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel
from tools import tools, lookup_order, lookup_tracking
import json


app = FastAPI()

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_KEY"),)




#removed async cause we're not awaiting anything
def agent(messages):
    print("Agent called! \n")

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        stream=False,
        tools= tools,
        tool_choice="auto",
        messages = messages,
        temperature=0.2,
        max_tokens=400
    )

    return response.choices[0].message

    # paused streaming as playing with tools:
    # print("Streaming: \n")
    # for i in response:
    #     text = i.choices[0].delta.content
    #     if text:
    #         yield text
    # yield "\n"


class Response(BaseModel):
    query: str


@app.get("/")
def root():
    return "Welcome to my LLM endpoint"


@app.post("/chat")
def chat(prompt: Response):
    return StreamingResponse(agent(prompt.query))

@app.post("/tool")
def use_tool(prompt: Response):
    #conversation history
    messages = [
        {
            "role":"user",
            "content":prompt.query
        }
    ]
    message = agent(messages)

    if not message.tool_calls:
        return {"answer":message.content}

    tool_call = message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    result = None
    if function_name == "lookup_order":
        result = lookup_order(**arguments)
    elif function_name == "lookup_tracking":
        result = lookup_tracking(**arguments)
    else:
        result = {"error": "Unknown tool"}

    messages.append(
        {
            "role": "assistant",
            "content":message.content,
            "tool_calls": [
                tool_call.model_dump()
            ]
        }
    )
    messages.append({
        "role":"tool",
        "tool_call_id": tool_call.id,
        "content":json.dumps(result)
    })

    final_message = agent(messages)
    print(messages)
    return {"Answer" : final_message.content}









# ------------------------------------ single tool call
# @app.post("/tool")
# def use_tool(prompt: Response):
#     message = agent(prompt.query)

#     tool_call = message.tool_calls[0] 
#     #we get: ChatCompletionMessageToolCall(id='1afqacnw8', function=Function(arguments='{"order_id":"ORD-101"}', name='lookup_order'), type='function')
    
#     function_name = tool_call.function.name
#     arguments = json.loads(tool_call.function.arguments)
    
#     result = None 
#     if function_name == "lookup_order":
#         result= lookup_order(**arguments)

#     message.append([
#         "role":"tool",
#         "tool_call_id": tool_call.id,
#         "content" : json.dumps(result)
#     ])
#     return result
#     # return function_name, arguments