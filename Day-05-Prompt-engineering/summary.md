# Day 05- Prompt Engineering

## Zeroshot
- Learned zeroshot prompting where no examples in given to the model for generating the response.
- Observed that zero-shot prompting works well for straightforward tasks while using fewer tokens.

## Fewshot
- Few examples(referred as shots) are provided, on basis of which the model's response is affected. 
- Observed how examples influence model behavior and output format.

## Output Formatting
- Learned to control model responses through prompt design.
- Used instructions such as:
```python
"""Respond ONLY in JSON."""
```
- Learned that clear formatting instructions produce more predictable outputs.

## Fewshot experiment 
- I performed an experiment where i provided 1, 3 and 5 shots respectively and observed the total_token_count
```python
print(response.usage_metadata)
```
- From the observation, zero-shot prompting used the fewest tokens and worked well for straightforward inputs. However, it was less reliable for ambiguous cases.

- Few-shot prompting improved consistency and helped the model better understand the expected output format. 3-shot prompting provided the best balance between output quality and token cost. 
- It produced more reliable results than 1-shot while using considerably fewer tokens than 5-shot.
