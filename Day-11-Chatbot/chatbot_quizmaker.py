from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()
MAX_HISTORY = 10

class Chatbot:
    def __init__(self):
        self.history = []
        self.questions = []

        self.system_instruction = """
        You are a quiz mentor.
        Generate exactly 2 quiz questions from the provided paragraph.
        Return ONLY valid JSON.
        Format:
        [
            {
                "question": "",
                "answer": ""
            },
            {
                "question": "",
                "answer": ""
            }
        ]
        Rules:
        - Answer must be one word.
        - No markdown.
        - No explanation.
        - Only JSON.
        """
        self.client = genai.Client(
            api_key=os.getenv("Gemini_API_Key")
        )

    def truncate_history(self):
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]

    def add_user_message(self, content):
        self.history.append(
            {
                "role": "user",
                "parts": [{"text": content}]
            }
        )
        self.truncate_history()

    def add_model_response(self, content):
        self.history.append(
            {
                "role": "model",
                "parts": [{"text": content}]
            }
        )
        self.truncate_history()

    def clear_history(self):
        self.history.clear()
        print("History Cleared")

    def save_history(self):
        with open(r"Day-11-Chatbot\conversation.txt","w",encoding="utf-8") as file:
            for message in self.history:
                role = message["role"]
                text = message["parts"][0]["text"]
                file.write(
                    f"{role.upper()}: {text}\n\n"
                )

        print("Conversation saved.")

    def retry_generate(self, prompt):
        wait_time = 1
        for attempt in range(5):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_instruction
                    )
                )
                return response
            except Exception as e:
                print(f"Attempt {attempt + 1} failed:")
                print(e)
                time.sleep(wait_time)
                wait_time *= 2
        raise Exception(
            "Maximum retries exceeded."
        )

    def generate_questions(self, prompt):
        response = self.retry_generate(prompt)
        data = response.text
        data = data.replace(
            "```json",
            ""
        )
        data = data.replace(
            "```",
            ""
        )
        self.questions = json.loads(data)
        self.add_user_message(prompt)
        self.add_model_response("Generated 2 quiz questions.")
        print("\nQuestions generated.")
        
    def start_quiz(self):
        if len(self.questions) == 0:
            print("No quiz available. Use /generate first.")
            return
        score = 0
        
        for item in self.questions:
            question = item["question"]
            answer = item["answer"]
            print(f"\nQuestion: {question}")
            self.add_model_response(question)
            user_answer = input("Your answer: ")
            self.add_user_message(user_answer)
            if (user_answer.strip().lower() == answer.strip().lower()):
                print("Correct!")
                self.add_model_response(
                    "Correct"
                )
                score += 1
            else:
                print(f"Wrong. Answer: {answer}")
                self.add_model_response(
                    f"Wrong. Answer: {answer}"
                )

        print(
            f"\nFinal Score: {score}/{len(self.questions)}"
        )

bot = Chatbot()

print("Welcome to Quiz Bot.")
print("/generate")
print("/start")
print("/save")
print("/clear")
print("/exit")

while True:
    user_input = input("\nYou: ")
    if user_input == "/exit":
        bot.save_history()
        print("Goodbye.")
        break
    elif user_input == "/clear":
        bot.clear_history()
    elif user_input == "/save":
        bot.save_history()
    elif user_input == "/generate":
        paragraph = input("\nPaste paragraph:\n")
        try:
            bot.generate_questions(paragraph)
        except Exception as e:
            print(f"Generation Error: {e}"
)
    elif user_input == "/start":
        bot.start_quiz()
    else:
        print("Unknown command.")