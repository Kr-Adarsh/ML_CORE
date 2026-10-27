from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from groq import Groq 
import os 
from dotenv import load_dotenv


load_dotenv()

client = Groq(
    api_key=os.environ.get("GROQ_KEY"),
)

async def agent(query):
    response = client.chat.completions.create(
        model = "qwen/qwen3.8-27b",
        stream=True,
        messages = [
            {
                "role": "user",
                "content": query
            }
        ],
        temperature=0.2
    )

    for i in response:
        text = i.choices[0].delta.content
        if text: 
            yield text
    yield "\n"


class chatReq(BaseModel):
    query:str

app = FastAPI()

@app.get("/")
def root():
    return "hello world"

@app.post("/chat")
def chat(req: chatReq):
    return StreamingResponse(agent(req.query), media_type="text/plain")
    # return {"received": req.query.strip}

