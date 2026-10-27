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



if __name__ == "__main__":
    query = input("Ask the agent: ")

    # response = agent(query)

    for chunk in agent(query):
        # text = chunk.choices[0].delta.content
        # if chunk:
        print(chunk, end="", flush=True)
    print()

# def nums():
#     yield 1
#     yield 2
#     yield 3

# def raw_nums():
#     return [1,2,3]

# print(list(nums()), raw_nums())

# the core diffrence is that using yeild you can resume from where the return leftoff.. 