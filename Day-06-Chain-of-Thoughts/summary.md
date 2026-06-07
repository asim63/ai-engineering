# Day 06 - Chain of Thought & Structured Outputs

## Chain of Thought (CoT)

- Learned how Chain of Thought prompting encourages the model to reason through intermediate steps before producing an answer.
- Compared responses with and without "Think step by step" instructions.

## Structured Outputs

- Learned why structured outputs are important for AI applications.
- Practiced prompting models to return responses in JSON format.
- Extracted structured information such as names, occupations, and other fields from unstructured text.

```python
prompt = """
Extract the information.
Respond only in valid JSON.
"""
```

## Pydantic
- Its a library used to validate the response of an LLM and enforce data structure.
- Created custom schemas using BaseModel.
- Understood how Pydantic helps catch missing fields and incorrect data types.
```bash
pip install pydantic
```
```python
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    occupation: str
```