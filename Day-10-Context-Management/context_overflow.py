from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
MAX_TOKEN_COUNT = 200
def get_count_tokens(contents):
    return client.models.count_tokens(
        model="gemini-2.5-flash-lite",
        contents=contents
    ).total_tokens
history = []
prompts = [
    "Hello I am asim.",
    "How are you?",
    "Nice to meet you",
    "Can you tell me a joke",
    "Whats my name again?"
]
for prompt in prompts:
    history.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })
    while get_count_tokens(history) > MAX_TOKEN_COUNT:
        history.pop(0)
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=history
    )
    history.append({
        "role": "model",
        "parts": [{"text": response.text}]
    })
    print("Tokens:", get_count_tokens(history))