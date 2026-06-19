from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()

client = genai.Client(api_key= os.getenv("Gemini_API_Key"))

response = client.models.generate_content(
    model = "gemini-2.5-flash",
    contents = """ What do you think came first? Chicken or egg? """,
    config = types.GenerateContentConfig(
        temperature= 0.5,
        max_output_tokens= 200
    )
    
)
  
print(response.text)
print("\n\n\n")
