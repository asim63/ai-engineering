# Day 04- Message Structure

## Roles in LLM
- Learned about system, user and model(assistant) roles in LLM.
- Learned how the responses of same prompt can be changed by differing the system prompt. 
```python
from google.genai import types
# rest of the code...
response = client.models.generate_content(
    model= "",
    contents= "",
    config= types.GenerateContentConfig(
        system_instruction = "Instruction here"
    )
)
```
## System Prompt Experiments
- Compared multiple tutor personalities:
    * Secondary-level tutor
    * Strict tutor
    * Arrogant tutor
    * Skilled tutor
    * AI PhD tutor
- Learned that system prompts strongly influence model behavior.
- Experimented with conflicting instructions between system and user prompts.

## Multi-turn conversation
- Built a simple multi-turn conversation by appending to message list manually.
- Understand why the full history must be sent every request — no server-side memory by default

## Understanding LLM Memory
- Learned that LLMs do not automatically remember previous interactions.
- Understood that conversation history acts as the model's temporary memory.
- Observed how removing previous messages affects the model's ability to recall information.
- Experimented with storing only user messages versus storing both user and model messages