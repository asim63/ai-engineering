from pydantic import BaseModel
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key") )

class Person(BaseModel):
    name: str
    email: str
    date: str
    
prompt = """
Asim lives in California with his family. Tomorrow on May 8th 2029, he is going to come to Nepal.
I emailed him on asimdkt@gmail.com and he actually replied
"""

response = client.models.generate_content(
    model = "gemini-2.5-flash-lite",
    contents = prompt,
    config = {
        "response_mime_type" : "application/json",
        "response_schema" : Person
    }
)
print(response.text)

