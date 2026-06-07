from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
roles = [
    "You are a 10 year old kid",
    "You are a physics student",
    "You are a professional tutor",
    "You are a comedian",
    "You are a cat."
]

for role in roles:
    response = client.models.generate_content(
        model = "gemini-2.5-flash-lite",
        contents = f"{role} What is gravity?",
        config = types.GenerateContentConfig(
            system_instruction = "Answer in one line only."
        )
    )   
    
    with open(r"Day-07-Advanced-Prompting\role_prompt.txt","a") as file:
        file.write(f"{role}: {response.text}\n\n")
