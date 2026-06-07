from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
prompt = """
    A farmer has 17 sheep.
All but 9 die.
How many remain?

Think step by step
"""
response = client.models.generate_content(
    model = "gemini-2.5-flash-lite",
    contents = prompt
)

with open(r"Day-06-Chain-of-Thoughts\experiment.txt", "a")as file:
    file.write(f"\n\n\nWith CoT: {response.text}")