from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
from pydantic import BaseModel

load_dotenv()
MAX_HISTORY = 10

class TaskResponse(BaseModel):
    task: str
    
class CodeExp():
    
    
    def __init__(self):
        self.history = []
        self.client = genai.Client(api_key=os.getenv("Gemini_API_Key"))
    
    def load_conversation(self):
        try:
            with open(r"Day-15-Project2\conversation.txt","r") as file:
                self.history = json.load(file)
        except:
            print("Creating a new session...")
            self.history = []
    def save_conversation(self):
        try:
            with open(r"Day-15-Project2\conversation.txt","w") as file:
                json.dump(self.history,file,indent = 4)
        except Exception as e:
            print("Error occured saving the conversation.")
            print(e)
            
    def clear_history(self):
        self.history.clear()
        print("History Cleared")
        self.save_conversation()
    
    def truncate(self):
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]        
    
    def add_user_prompt(self,text):
        self.history.append({
            "role":"user",
            "parts":[{"text":text}]
        })
        self.truncate()        
    
    def add_model_prompt(self,text):
        self.history.append({
            "role":"model",
            "parts":[{"text":text}]
        })
        self.truncate()
    
    def explain(self,prompt):
        self.add_user_prompt(prompt)
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents = self.history,
                config = types.GenerateContentConfig(
                    system_instruction= """
                    You are an insane coder. You can explain any code along with their complexities.
                    Explain the given code in this format.
                    Purpose:

                    Time Complexity:
                    O(n)

                    Space Complexity:
                    O(n)

                    Explanation:
                    """
                    
                )
            )
            self.add_model_prompt(response.text)
            print(f"Bot: {response.text}")
        except Exception as e:
            print(f"Error : {e}")
            
            
    def debug(self,prompt):
        self.add_user_prompt(prompt)
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents = self.history,
                config = types.GenerateContentConfig(
                    system_instruction= """
                    You are an insane coder debugger. You can debug any code along with their solution
                    Explain the given code in this format.
                    Bug Found:

                    Solution:
                    """
                    
                )
            )
            self.add_model_prompt(response.text)
            print(f"Bot: {response.text}")
            
        except Exception as e:
            print(f"Error : {e}")
    
    def complexity(self,prompt):
        self.add_user_prompt(prompt)
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents = self.history,
                config = types.GenerateContentConfig(
                    system_instruction= """
                    You are an algorithm expert. You know the time and space complexities of all algorithm. Be consise and clear.
                    Respond in following format:
                    Time Complexity:
                    O(n)
                    Space Complexity:
                    O(1)
                    """
                    
                )
            )
            self.add_model_prompt(response.text)
            print(f"Bot: {response.text}")
            
        except Exception as e:
            print(f"Error : {e}")
            
    def chat(self,prompt):
        self.add_user_prompt(prompt)
        try:
            response = self.client.models.generate_content(
                model = "gemini-2.5-flash-lite",
                contents = self.history,
                config = types.GenerateContentConfig(
                    system_instruction="""
                    You are a very humble person. You speak less and only speak when required.
                    Be concise and just reply accordingly.
                    Do not try to link the conversation with history. Reply based on the user's prompt.
                    """
                    
                )
            )
            self.add_model_prompt(response.text)   
            print(f"Bot: {response.text}")
        except Exception as e:
            print(f"Error : {e}")
        
    def classify(self,prompt):
        response = self.client.models.generate_content(
            model = "gemini-2.5-flash-lite",
            contents = prompt,
            config = types.GenerateContentConfig(
                system_instruction="""
                Classify the request as any one either:
                - explain
                - debug
                - complexity
                - NoCode

                {
                    "task": "explain"
                }

                Return ONLY valid JSON.
                - No markdown.
                - No explanation.
                -Only JSON.
                """
                
            )
        )
        data = response.text
        data = data.replace("```json", "")
        data = data.replace("```", "")

        try:
            parsed = json.loads(data)
            result = TaskResponse(**parsed)
            print(f"Task: {result}")
            return result

        except Exception as e:
            print(f"Error: {e}")
            return TaskResponse(task="UNKNOWN")
        
        
bot = CodeExp()
bot.load_conversation()
print("Welcome to Code Explainer")
print("Enter any queries for your code.")
print("Commands are:")
print("/exit -> exit the session")
print("/clear -> Clear the conversation")

while True:
    user_input = input("You: ")
    if user_input =="/exit":
        print("Goodbye, saving the convo...")
        bot.save_conversation()
        break
    
    elif user_input == "/clear":
        print("Clearing history...")
        bot.clear_history()
    else:    
        task = bot.classify(user_input).task
        
        if task == "explain":
            bot.explain(user_input)
        elif task == "debug":
            bot.debug(user_input)
        elif task == "complexity":
            bot.complexity(user_input)
        else:
            bot.chat(user_input)
    bot.save_conversation() 
    


    
    
    