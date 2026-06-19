from ollama import chat

stream = chat(
    model = "qwen3:8b",
    messages=[
        {"role":"user","content":"Why is music important?"}
    ],
    stream= True
)

for chunk in stream:
    print(chunk["message"]["content"],end="",flush=True)
