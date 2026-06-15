from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
load_dotenv()

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
def summary():
    global history
    global conversation_summary
    if len(history) > MAX_HISTORY:
        old_messages = history[:MAX_HISTORY]
        conversation_summary = client.models.generate_content(
        model = "gemini-2.5-flash-lite",
        contents = f"""
            Previous Summary:
            {conversation_summary}

            New Messages:
            {old_messages}

            Update the summary.
            """,
        config = types.GenerateContentConfig(
            system_instruction = """
            You are an amazing summary writer.
            Summarize keeping the important parts. Dont miss out any significant information from the conversation.
            """
        )
        ).text
        history = history[:-MAX_HISTORY]
    
def save_state():
    with open("Day-14-Multiturn_Pattern_and_State_Management/converstation.txt", "w") as file:
        json.dump(history, file, indent=4)

    with open("Day-14-Multiturn_Pattern_and_State_Management/summary.txt", "w") as file:
        json.dump(conversation_summary, file)

client = genai.Client(api_key=os.getenv("Gemini_API_Key"))

try:
    with open("Day-14-Multiturn_Pattern_and_State_Management/converstation.txt", "r") as file:
        history = json.load(file)
except:
    history = []

try:
    with open("Day-14-Multiturn_Pattern_and_State_Management/summary.txt", "r") as file:
        conversation_summary = json.load(file)
except:
    conversation_summary = ""

    
while True:
    user_input = input("You: ")
    if user_input == "/exit":
        print("Goodbye")
        break
    
    add_user_history(user_input)
    response = client.models.generate_content(
        model = "gemini-2.5-flash-lite",
        contents = f"""
        Summary: {conversation_summary}
        History: {history}
        """,
        config = types.GenerateContentConfig(
            system_instruction = """
            You are a smart fella. Give consise response. 
            """
        )
    )
    print(f"Bot: {response.text}")
    add_model_history(response.text)    
    summary()
    
    save_state()
    
    