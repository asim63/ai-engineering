from google import genai
from dotenv import load_dotenv
import os
load_dotenv()
client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
prompt = """
Suhan is an engineering student and currently is a member of Robotics Club. Sumoon is his friend who goes to gym.
Extract the information in valid Json format, only json no text. 
"""
response = client.models.generate_content(
    model= "gemini-2.5-flash-lite",
    contents = prompt
)
print(response.text)
