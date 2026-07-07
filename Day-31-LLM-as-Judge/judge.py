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
## Rubric
1 = Completely fails the task, irrelevant or incorrect
2 = Major issues, only partially addresses the task
3 = Adequate, addresses the task but has notable flaws
4 = Good, addresses the task well with minor issues
5 = Excellent, fully addresses the task with no notable flaws

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
    
task = "Explain what a minimum spanning tree is."
print("Generating response...")
response = call_llm(task)

print(f"Task: {task}")
print(f"Response: {response}")

print("\n Getting judged...")
judge(task, response)