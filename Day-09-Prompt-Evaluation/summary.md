# Day 09 - Prompt Evaluation & Testing Methodology

## Why Evaluation Matters
- Learned that a prompt should be measured against a test set rather than evaluated on a few random examples.
- Understood the importance of defining evaluation criteria before optimizing prompts.
---
## Precision vs Recall 
- Precision is the ratio of true positive and total observations in the classification. (TP /TP + FP)
- Recall is the ratio of true positive and total actual positives in the classification. (TP / TP + FN)

## Building a Test Set

Created a sentiment classification dataset containing positive, negative and neutral examples.

```python
test_set = [
    ("I am feeling happy.", "Positive"),
    ("I hate that place.", "Negative"),
    ...
]
```
- Learned that the quality of the test set directly impacts the quality of evaluation.
- Understood that ambiguous examples can make evaluation more difficult and require careful labeling.
---

## Evaluation Harness
Built a simple evaluation script that:
1. Iterates through a test set.
2. Sends each example to the LLM.
3. Compares predicted output with expected output.
4. Calculates overall accuracy.

```python
if result == expected:
    count += 1

accuracy = (count / len(test_set)) * 100
```
---

## Prompt Comparison
Compared multiple prompting strategies on the same task:
- Basic Prompt: 83.33%
- Role Prompt: 83.33%
- Few-shot Prompt: 66.67%

This demonstrated that few-shot prompting does not always improve performance and can reduce accuracy if the examples are poorly chosen.

---

## LLM-as-Judge
Built an LLM that evaluate email subject lines generated with different prompting techniques.
Evaluated:
- Basic Prompt
- Role Prompt
- Few-shot Prompt
- XML Prompt
- JSON Prompt

Results:

| Technique | Score |
|------------|--------|
| Basic | 8/10 |
| Role | 8/10 |
| Few-shot | 8/10 |
| XML | 8/10 |
| JSON | 7/10 |

Observations:

- Prompt complexity did not significantly improve output quality.
- Simpler prompts performed just as well as advanced prompting techniques for this task.
- JSON formatting changed output style but did not necessarily improve quality.
