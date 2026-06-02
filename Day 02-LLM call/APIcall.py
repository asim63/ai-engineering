import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key = os.getenv("Gemini_API_Key"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="what is football in 1 sentence."
)
json = response.json
data = response.text
print(json)
print(type(json))
print(data)
print(response)

# #stream responses
# response2 = client.models.generate_content_stream(
#     model="gemini-3.5-flash",
#     contents="how are you?"
# )
# for chunk in response2:
#     print(chunk.text, end="", flush= True)
