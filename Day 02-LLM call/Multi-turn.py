from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key = os.getenv("Gemini_API_Key"))

chat = client.chats.create(model = "gemini-2.5-flash")

response1 = chat.send_message("I have 3 footballs in my room.")
print(f"Response 1 : {response1.text}")

response2 = chat.send_message("Tell me the no of footballs.")
print(f"Response 2: {response2.text}")

# print((response2))
response = chat.send_message(
    "Hi"
)

print(response.usage_metadata)