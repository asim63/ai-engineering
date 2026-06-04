messages = [
    {
        "role": "system",
        "content": "You are a teacher)"
    },
    {
        "role": "user",
        "content": "Explain what is AI engineering."
    }
]

print(messages)
for item in messages:
    print(type(item)) #dictionary