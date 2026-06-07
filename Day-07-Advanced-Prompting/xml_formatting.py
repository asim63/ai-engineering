from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
def generate_prompt(instruction, context, input ):
    return f"""
    <instruction>
    {instruction}
    </instruction>
    <context>
    {context}
    </context>
    <input>
    {input}
    </input>
"""

prompt = generate_prompt(
    instruction = "Answer in only one line",
    context = "You are a comedian",
    input = "What is bicycle?"
)

response = client.models.generate_content(
    model = "gemini-2.5-flash-lite",
    contents = prompt
)
print(response.text)
