from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
load_dotenv()

def extract(text):
    client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
    instruction = """
    Extract valuable insights from the paragraph in JSON format. Ignore the unnecessary part, only include significant attributes.
    <user_input>
    My name is Asim. I live in bhaktapur. I was doing code and suddenly i felt a bit bored then i started watching youtube.
    </user_input>
    <output>
    {
        "name":"Asim",
        "city":"Bhaktapur",
        "hobby":"coding",
    }
    </output>
    
    <user_input>
    I need to send these letters to my boss as soon as possible. Its really urgent, please give it to him on time orelse i might get fired.
    </user_input>
    <output>
    {
        "sender":"employee",
        "ask":"send letters",
        "receiver":"boss",
        "type":"urgent",
        "consequences":"fired"
    }
    </output>
    Return ONLY valid JSON
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents = text,
        config=types.GenerateContentConfig(
            system_instruction=instruction
        )
    )
    
    data = response.text
    data = data.replace("```json","")
    data = data.replace("```","")
    try:
        result = json.loads(data)
        print(result)
        return result
    except json.JSONDecodeError:
        return "Error"

# prompt = input("Enter the paragraph:")
# extract(prompt)