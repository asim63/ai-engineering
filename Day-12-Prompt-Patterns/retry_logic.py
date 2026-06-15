from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))

class Person(BaseModel):
    name: str
    age: int
    city: str

prompt = """
Extract information from this text.

Text:
My name is Asim. I live in Bhaktapur.

Return JSON only.
"""

for attempt in range(3):

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    data = response.text
    data = data.replace("```json", "")
    data = data.replace("```", "")

    try:
        parsed = json.loads(data)

        result = Person(**parsed)

        print("Valid Output")
        print(result)

        break

    except (json.JSONDecodeError, ValidationError) as e:

        print(f"Attempt {attempt + 1} failed")

        prompt = f"""
Your previous response was invalid.

Error:
{e}

Previous response:
{response.text}

Required schema:
{{
    "name": "string",
    "age": integer,
    "city": "string"
}}

Fix the response.
Return ONLY valid JSON.
"""