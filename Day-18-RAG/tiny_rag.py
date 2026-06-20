from ollama import chat
document = [
    "I eat dinner by 9 pm at the evening.",
    "Ram works as an electrician."
]
context = ""
question = "What does Ram do ?"

for doc in document:
    if "Ram" in doc:
        context = doc
response = chat(
    model = "qwen3:8b",
    messages=
    [{
        "role":"user",
        "content":f"""
        Context:
        {context}
        Question:
        {question}
        
        Answer from context only
        """
    }],
    stream= True
)
for chunk in response:
    print(chunk["message"]["content"], end="", flush= True)

