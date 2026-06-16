# Day 15 - AI Project: Code Explainer Assistant

## Objective

Build a complete AI application by combining concepts learned from Weeks 1 and 2:

* Prompt Engineering
* Routing Pattern
* JSON Structured Outputs
* Memory Management
* OOP Design
* Error Handling
* Conversation Persistence
* Evaluation with Test Sets

---

## Project Chosen

### Code Explainer Assistant

An AI-powered assistant capable of:

* Explaining code snippets
* Debugging code
* Analyzing time and space complexity
* Handling general conversation

The system automatically routes user requests to the correct prompt based on the detected task.

---

## Key Concepts Applied

### 1. Router Pattern

Instead of using a single prompt for every request, a routing model first classifies the user's intent.

Supported tasks:

* explain
* debug
* complexity
* NoCode

Example:

Input:

```python
for i in range(5):
    print(i)
```

Router Output:

```json
{
    "task": "explain"
}
```

The request is then sent to the Explain Handler.

---

### 2. Structured JSON Output

The router was instructed to return valid JSON only.

Example:

```json
{
    "task": "debug"
}
```

The JSON response was parsed using:

```python
json.loads()
```

and validated using:

```python
Pydantic BaseModel
```

---

### 3. OOP Design

The application was implemented using a class:

```python
class CodeExp:
```

Responsibilities:

* Conversation management
* Routing
* Memory handling
* Prompt execution
* Saving/loading conversations

Methods:

* load_conversation()
* save_conversation()
* clear_history()
* truncate()
* explain()
* debug()
* complexity()
* classify()
* chat()

---

### 4. Memory Management

Conversation history is stored in:

```text
conversation.txt
```

History is loaded when the application starts and saved after every interaction.

To prevent context overflow:

```python
MAX_HISTORY = 10
```

Only the latest messages are retained.

This is called the Truncation Strategy.

---

### 5. Prompt Engineering

Separate system prompts were created for:

#### Explain

Returns:

* Purpose
* Time Complexity
* Space Complexity
* Explanation

#### Debug

Returns:

* Bug Found
* Solution

#### Complexity

Returns:

* Time Complexity
* Space Complexity

#### Chat

Handles general conversation.

---

### 6. Error Handling

Implemented using:

```python
try:
except:
```

Used for:

* File operations
* API requests
* JSON parsing

This prevents application crashes and improves reliability.

---

### 7. Evaluation

A test set was designed to validate routing accuracy.

Categories tested:

* Explain
* Debug
* Complexity
* General Chat

The router's predictions are compared against expected labels to calculate accuracy.

Formula:

```python
accuracy = (correct / total) * 100
```

Target:

```text
85%+
```

---

## Challenges Faced

### Pydantic Misuse

Initially attempted:

```python
class CodeExp(BaseModel)
```

This caused design issues because the chatbot itself is not a data model.

Solution:

Use:

```python
class TaskResponse(BaseModel)
```

only for JSON validation.

---

### Conversation Persistence

Initially saved history in an invalid format.

Learned proper usage of:

```python
json.dump()
json.load()
```

for storing structured conversation history.

---

### Routing Accuracy

Some requests can belong to multiple categories.

Example:

```text
Explain this code and give complexity.
```

Current implementation supports only one route.

Future improvement:

```json
{
    "tasks": ["explain", "complexity"]
}
```

---

## Lessons Learned

* Router patterns make AI systems more scalable.
* Structured outputs are easier to validate than free-form text.
* Pydantic improves reliability when working with JSON.
* Memory management is essential to prevent context overflow.
* OOP helps organize growing AI applications.
* Building a complete application is significantly different from isolated prompt experiments.

---

## Next Improvements

* Multi-task routing
* Retry with feedback loop
* Streaming responses
* Better evaluation framework
* Modular architecture using multiple Python files
* Local model support using Ollama

---

## Conclusion

Successfully built a Code Explainer Assistant that combines routing, prompt engineering, memory management, structured outputs, persistence, and OOP design into a single AI application.

This project represents the first complete AI system built from concepts learned during the AI Engineering roadmap.
