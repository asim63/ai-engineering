from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
load_dotenv()

def generate(text):
    client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
    instruction = """
    <format>
    #LSPPDayXX
    <text></text>
    @lftechnology  #60DaysofLearning2026 #LearningWithLeapfrog
    </format>
    Generate a social media post for leapfrog from the text.
    - Must be under 150 letters.
    - Use bullet points
    - Use professional tone
    - Strictly follow the format, write the content inside content area only.
    """
    
    response = client.models.generate_content(
        model = "gemini-2.5-flash-lite",
        contents = text,
        config = types.GenerateContentConfig(
            system_instruction = instruction
        )
    )
    with open(r"Day-12-Prompt-Patterns\generation.txt","a",encoding = "utf-8") as file:
        file.write(f"{response.text}\n\n")
    return response.text

# text = input("Enter the things you did today for LSPP: ")
# generate(text)