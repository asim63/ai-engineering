# Day-17 SDKs in depth and Ollama Setup

## Understand all parameters
- Learned/ Reviewed the parameters like temperature, max_output_tokens, stream.
```python
from google.genai import types
...
response = client.models.generate_content(
    model="",
    contents= "",
    config = types.GenerateConfigContent(
        temperature = 0.5,
        max_output_tokens = 400
    )
)
```
---
## Router pattern
- Built a model router function that picks the right model based on task complexity.
```python
def pick_model(task):
    pass
```
---
## ollama setup
- Setup ollama
```bash
pip install ollama
```
- pull model
```bash
ollama pull qwen3:8b
```
-run model
```bash
ollama run qwen3:8b
```
---
## ollama using python
- Learned to make request using ollama.
```python
from ollama import chat

response = chat(
    model = "quen3:8b",
    messages = [
        {"role":"user",
         "content":""
         }
        ]
)
print(response["message"]["content"])
```
- Using Stream
```py
stream = chat(
    model = "qwen3:8b",
    messages=[
        {"role":"user","content":""}
    ],
    stream= True
)

for chunk in stream:
    print(chunk["message"]["content"],end="",flush=True)
```