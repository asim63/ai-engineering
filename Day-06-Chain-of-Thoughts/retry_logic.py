from google import genai
import os
from dotenv import load_dotenv
load_dotenv()
import json

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
prompt = """
Sita works on a diary shop. She listens to music on her leisure time. Her favourite artist is Clairo.
Respond in valid JSON format, no text only JSON
"""

for i in range(3):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    print(response.text)
    try:
        data = json.loads(response.text)
        print("Valid JSON received")
        print(data)
        break

    except json.JSONDecodeError:
        print(f"Attempt {i+1} failed. Retrying...") #The attempt failed thats why Pydantic is actually important.
        