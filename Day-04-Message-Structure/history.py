from google import genai
from dotenv import load_dotenv
import os
load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
history = []

history.append(
    {
        "role": "user",
        "parts":[{"text": "What is my name?"}]
    }
)
response = client.models.generate_content(
    model = "gemini-2.5-flash",
    contents = history
)
print(response.text)
history.append(
    {
        "role":"model",
        "parts":[{"text":response.text}]
    }
)
history.append(
    {
        "role": "user",
        "parts":[{"text": "My name is Asim"}]
    }
)
response = client.models.generate_content(
    model = "gemini-2.5-flash",
    contents = history
)
print(response.text)

history.append(
    {
        "role":"model",
        "parts":[{"text":response.text}]
    }
)
history.append(
    {
        "role": "user",
        "parts":[{"text": "What is my name?."}]
    }
)
response = client.models.generate_content(
    model = "gemini-2.5-flash",
    contents = history
)
print(response.text)