from ollama import chat

prompt = "What is the capital of France?"

for i in range(3):
    response = chat(
        model="qwen3:8b",
        messages=[{
            "role":"user",
            "content":prompt
        }],
        options={"temperature": 1.0}
    )
    print(f"\nRun {i}: ")
    print(response["message"]["content"])
    