from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()
import json
history = []
client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
MAX_HISTORY = 10

def add_user_history(text):
    global history
    history.append(
        {
        "role":"user",
        "parts":[{"text": text}]
        }
    )
def add_model_history(text):
    global history
    history.append(
        {
        "role":"model",
        "parts":[{"text": text}]
        }
    )
def truncate():
    global history
    if len(history)> MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    
while True:
    user_input = input("You: ")
    
    if user_input == "/exit":
        print("Goodbye")
        break    
    add_user_history(user_input)
    truncate()
        
    response = client.models.generate_content(
        model = "gemini-2.5-flash-lite",
        contents = history,
        config = types.GenerateContentConfig(
            system_instruction="""
            You are an AI Engineering mentor.
            Be concise.
            """
        )
    )
    print(f"Bot: {response.text}")
    add_model_history(response.text)
    truncate()
    
    with open(r"Day-14-Multiturn_Pattern_and_State_Management\converstation.txt","w") as file:
        json.dump(history, file, indent=4)
        