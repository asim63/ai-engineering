# Day 10- Context Management

## Prompt usage Experiment
- I observed the prompt_token_count for each message in a conversation by saving history.
- Prompt_token_count kept on increasing with each new message in the conversation.
- Found out, with each new request, the entire history will be sent along with it( thus increasing the prompt_token_count)

## Truncate
- Way to manage the context where a limit is set in history.
- If the history exceeds the limit, the old messages are deleted from history.
```python
MAX_HISTORY = 6
if (len(history)>MAX_HISTORY):
    history = history[-MAX_HISTORY:]
```
## Summarize
- Keeps summary of the message after the `MAX_HISTORY` limit is crossed.

## Sliding Window
- Keeps both summary and recent messages in the history.

## Cost & latency tradeoff
- More context → better memory
- More context → slower + expensive
- Less context → faster but forgetful

## Count Tokens
- Learned to count token before sending request.
```python 
count = client.models.count_tokens(
    model = "gemini-2.0",
    contents = f"{prompt}"
).total_tokens
print(count)
```

## Handle Context Overflow
- I built a conversation that handles context overflow, based on `MAX_COUNT` for tokens.
```python
while get_total_tokens(content) > MAX_COUNT:
    history.pop(0)
```

