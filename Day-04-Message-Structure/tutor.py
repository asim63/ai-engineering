from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
prompts = [
    {
        "instruction":"You are secondary level tutor.",
        "question": "Explain AI(in few lines, three at most)."
    },
    {
        "instruction":"You are a arrogant tutor.",
        "question": "Explain AI(in few lines, three at most)."   
    },
    {
        "instruction":"You are a strict tutor.",
        "question": "Explain AI(in few lines, three at most)."   
    },
    {
        "instruction":"You are a very skilled tutor.",
        "question": "Explain AI(in few lines, three at most)."   
    },
    {
        "instruction":"You hold PhD in AI.",
        "question": "Explain AI(in few lines, three at most)."   
    }
]
for prompt in prompts:   
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents = prompt['question'],
        config = types.GenerateContentConfig(
            system_instruction = prompt['instruction']
        )
    )
    with open(r"Day-04-Message-Structure\tutor_response.txt","a") as file:
        file.write(f"\ninstruction: {prompt['instruction']}\nquestion:{prompt['question']}\nresponse:{response.text}\n")