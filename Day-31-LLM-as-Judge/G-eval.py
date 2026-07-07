from ollama import chat

def call_llm(prompt, temperature=0):
    stream = chat(
        model = "qwen3:8b",
        messages=[{
            "role":"user",
            "content":prompt,
        }],
        options={"temperature": temperature},
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
def geval_generate_steps(task_description, criterion):
    """Step 1: Auto-CoT — have the model design its own eval steps."""
    prompt = f"""You are designing an evaluation procedure.

Task: {task_description}
Criterion to evaluate: {criterion}

Write a numbered list of 3-5 concrete evaluation steps a grader should follow to
score a response on this criterion from 1-5. Output ONLY the numbered steps."""
    return call_llm(prompt)

def geval_score(task, response, criterion, eval_steps, n_samples=5):
    """Step 2: apply steps, sample multiple times, average = probability-weighted approximation."""
    prompt = f"""Evaluate the response using these steps:
{eval_steps}

Task: {task}
Response: {response}
Criterion: {criterion}

Follow the steps internally, then output ONLY a single integer score 1-5, nothing else."""

    scores = []
    for _ in range(n_samples):
        out = call_llm(prompt, temperature=0.7)  # nonzero temp needed for sampling variance
        digits = [int(c) for c in out if c.isdigit() and c in "12345"]
        if digits:
            scores.append(digits[0])
    return sum(scores) / len(scores) if scores else None

# Example
task = "Summarize a news article about a tech company earnings report."
response = "The company beat expectations with strong cloud growth, though it warned of headwinds next quarter."
criterion = "Coherence: does the summary flow logically and read naturally?"

steps = geval_generate_steps(task, criterion)
print("Generated eval steps:\n", steps)
score = geval_score(task, response, criterion, steps)
print("G-Eval score (averaged):", score)