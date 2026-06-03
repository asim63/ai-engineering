# Day 03- LLM work
## LLM
- Learned how Large Language Models generate responses by repeatedly predicting the most likely next token.
- It contains billions of parameters, it is trained on large data followed by finetuning and reinforcement learning.

## Token
- Learned more on token, its is basically the smallest unit that the LLM recognizes or works on.
- It may be a single letter, word, or even a multi-word.

## Tokenizer
- Using OpenAI tokenizer Playground, i analyzed how different text lead to different tokens. I tried to put mathematical expressions as well. 

## Base Model vs Instruction-Tuned Model
- Learned that a base model is trained to predict the next token.
- Instruction-tuned models are further trained to follow human instructions and behave like assistants.
- Base model ≈ autocomplete.
- Instruction-tuned model ≈ helpful assistant.

## Context window 
- It is measured based on tokens. 
- It is basically the amount of tokens that can be provided to the model in a single request.
- Learned challenges of larger context window.
- Large context window might make it harder for models to effectively use all information within the context negatively affecting the performance of LLM models. Much more computational power required.

## Hallucination
- Learned about why LLM models hallucinate.
- Learned how LLM tried to fill in the gaps and generates tokens based on probability rather than factual correctness.

## Temperature
- It refers to how much the model is willing to explore, more temperature means more exploration. 
- Lower temperature leads to conservative response while higher temperature lead to creative response.
```python
from google.genai import types

response = client.models.generate_content(
    model="",
    contents="",
    config = types.GenerateContentConfig(
        temperature = temp
    )
)
print(response.text)
```