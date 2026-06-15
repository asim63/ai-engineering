from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
load_dotenv()
import json
MAX_HISTORY = 15
client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
history = []
try: 
    with open(r"Day-14-Multiturn_Pattern_and_State_Management\users.txt","r",encoding="utf-8") as file:
        users = json.load(file)
except:
    users = []

def check_user(name):
    global users
    for user in users:
        if user["name"] == name:
            print("user exists... loading previous conversations")
            return True
    print("new user... creating new session")
    users.append({
        f"name" : f"{name}",
        f"session" : f"{name}_history"
    })
            
    with open(r"Day-14-Multiturn_Pattern_and_State_Management\users.txt","w",encoding="utf-8") as file:
        json.dump(users,file,indent = 4)
    return False

def get_session(name):
    global users
    for user in users:
        if user["name"] == name:
            return user["session"]
        
def load_conversation(name):
    session_name = get_session(name)
    try:
        with open(rf"Day-14-Multiturn_Pattern_and_State_Management\convos\{session_name}.txt","r",encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        print("Conversation file corrupted. Starting fresh session.")
        return []

    except Exception as e:
        print(f"Unexpected error loading conversation: {e}")
        return []

def save_conversation(name,history):
    session_name = get_session(name)
    try:
        with open(rf"Day-14-Multiturn_Pattern_and_State_Management\convos\{session_name}.txt","w",encoding="utf-8") as file:
            json.dump(history, file, indent = 4)
    except Exception as e:
        print(e)
        print("Error occured saving convo")

def truncate():
    global history
    if len(history)> MAX_HISTORY:
        history = history[-MAX_HISTORY:]


def add_user_history(text):
    global history
    history.append(
        {
        "role":"user",
        "parts":[{"text": text}]
        }
    )
    truncate()
    
def add_model_history(text):
    global history
    history.append(
        {
        "role":"model",
        "parts":[{"text": text}]
        }
    )
    truncate()
    
name = input("Enter user name:")
check_user(name)
history =  load_conversation(name)

while True:
    user_input = input("You: ")
    if user_input == "/exit":
        save_conversation(name, history)
        print("Goodbye")
        break
    add_user_history(user_input)
    try:
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = history,
            config = types.GenerateContentConfig(
                system_instruction= """
                You are a professional mentor. Be concise and elegant in your way of speaking.
                You dont talk much, you only talk whats required.
                """
            )
        )
    except Exception as e:
        print(e)    
        
    print(f"Bot: {response.text}")
    add_model_history(response.text)

    save_conversation(name,history)


