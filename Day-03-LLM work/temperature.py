from google import genai
import os
from dotenv import load_dotenv
from google.genai import types

load_dotenv()

client = genai.Client(api_key = os.getenv("GEMINI_API_KEY"))
temperatures = [0, 0.3, 0.6, 1, 1.5, 2]

#get response for each temperature
for temp in temperatures:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents ="The color of sky is ..",
        config= types.GenerateContentConfig(
            temperature = temp
        )
    )
    
    print(f"For temperature {temp}: ")
    print(response.text)
    print("\n\n\n")
    