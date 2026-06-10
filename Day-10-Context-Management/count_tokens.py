from google import genai
from dotenv import load_dotenv
import os
load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))

prompt = "Hi, what are you up to?" 
long_prompt = "Can you tell me the difference between speed and velocity? Also write the derivation for both of them."

count = client.models.count_tokens(
    model = "gemini-2.5-flash-lite",
    contents = long_prompt
).total_tokens

print(count)