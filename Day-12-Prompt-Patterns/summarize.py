from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()

def summarize(paragraph, summary_type):
    client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
    if summary_type == "bullet":
        instruction = "Summarize the paragraph in bullet points."
    elif summary_type == "paragraph":
        instruction = "Summarize the paragraph in one paragraph(small)"
    elif summary_type == "eli5":
        instruction = "Explain like I am 5 years old."

    elif summary_type == "executive":
        instruction = "Summarize for a company executive."
    else:
        return "unknown command"
    
    response = client.models.generate_content(
        model = "gemini-2.5-flash-lite",
        contents = paragraph,
        config = types.GenerateContentConfig(
            system_instruction = instruction
        )
    )
    with open(r"Day-12-Prompt-Patterns\summarize.txt","a",encoding = "utf-8") as file:
        file.write(f"---{summary_type}---\n {response.text}\n\n")
    return response.text
        
# summary = ["bullet","paragraph","eli5","executive"]
# para = input("Enter the long paragraph / article:")
# for suma in summary:
#     summarize(para,suma)
    
