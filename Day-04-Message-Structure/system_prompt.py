from google import genai
from dotenv import load_dotenv
from google.genai import types
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))

instruction = "Answer the question in single word"
question = "Answer in 50 words, What is space?"

response = client.models.generate_content(
model ="gemini-2.5-flash",
contents= question,
config = types.GenerateContentConfig(
    system_instruction = instruction
)
)

with open(r"Day-04-Message-Structure\response.txt","a") as file:
    
    file.write(f"Instruction: {instruction}\nquestion: {question}\n response: {response.text}\n")
    
    