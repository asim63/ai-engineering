squares = [i*i for i in range(5)]
print(squares)


history = []
history.append({
    "role":"user",
    "parts":[{"text":"your_prompt"}]
})
texts = [msg["parts"][0]["text"] for msg in history]
print(texts)