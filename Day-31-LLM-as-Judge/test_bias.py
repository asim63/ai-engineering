from ollama import chat

def call_llm(prompt):
    stream = chat(
        model = "qwen3:8b",
        messages=[{
            "role":"user",
            "content":prompt,
        }],
        options={"temperature": 0},
        think = False,
        stream= True
    )
    full = ""
    for chunk in stream:
        piece = chunk["message"]["content"]
        print(piece, end="", flush=True)
        full += piece
    print()
    return full

JUDGE_PROMPT = """ You are a expert evaluator. Rate the AI response below on the scale of 1 to 5.

##Task 
{task}

#AI
{response}
## GOOD_RUBRIC 
Evaluate on these SEPARATE observable dimensions (each 1-5), not overall vibe:

1. Correctness: Are all factual claims accurate? (Ignore length/style entirely)
2. Completeness: Does it address every part of the user's question?
3. Conciseness: Is it free of unnecessary padding? (A short, complete answer scores 5 here; a bloated one scores low even if correct)
4. Actionability: Could the user act on this without needing to ask a follow-up?

For each dimension, quote the specific part of the response that justifies your score before giving the number.

## Instructions
Think step by step about how well the response meets the rubric, then give your final score.
Respond ONLY in this exact format:

Reasoning: <your reasoning in 2-3 sentences>
Score: <a single integer 1-5>
"""

def judge(task,response):
    prompt = JUDGE_PROMPT.format(task = task, response = response)
    result = call_llm(prompt)
    print(f"Result : {result}")
    
short_answer = "Paris."
long_answer = "Paris is the capital of France. It has been the capital since... [500 more words]"

print(judge("What is the capital of France?", short_answer))
print(judge("What is the capital of France?", long_answer))