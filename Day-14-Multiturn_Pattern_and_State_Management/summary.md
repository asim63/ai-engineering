# Day 14 - Multiturn Pattern and State Management

## Overview

Today focused on one of the most important concepts in AI application development: **memory and state management**.

LLM APIs are inherently stateless, meaning they do not remember previous interactions unless that information is explicitly provided with each request. To build conversational AI applications, memory must be managed by the developer.

---

# Stateless Nature of LLM APIs

- Large Language Models do not maintain memory between API calls.
- Every request is independent.
Example:

```python
response = model.generate_content("What is my name?")
```
- The model has no idea who the user is unless previous messages are supplied as context.
- Developers are responsible for providing memory.

---

# Memory Strategies

## 1. In-Context Memory

The entire conversation history is sent with every request.

Example:

```python
history = [
    {"role": "user", "parts": [{"text": "Hello"}]},
    {"role": "model", "parts": [{"text": "Hi"}]}
]
```

---

## 2. External Memory

- Conversation history is stored outside the model.

Example:

```python
json.dump(history, file)
```

and later:

```python
history = json.load(file)
```

---

## 3. Summarized Memory

- Older messages are periodically compressed into a summary.
- The summary becomes long-term memory while only recent messages remain in history.
- Some details may be lost

---

# User Identity vs Session Identity

A critical distinction in AI applications.

## User Identity

- Represents who is talking.

Examples:

* Asim
* user_123
* john_smith

User identity persists across multiple conversations.

Stores:

* Name
* Preferences
* Long-term facts
* Personal settings

---

## Session Identity

- Represents a specific conversation.

Each session has its own:

* History
* Summary
* Temporary context
---

# Comparing Memory Strategies

| Strategy   | Best For    | Pros                   | Cons                             |
| ---------- | ----------- | ---------------------- | -------------------------------- |
| In-Context | Short chats | Simple and accurate    | Expensive for long conversations |
| External   | Persistence | Survives restarts      | Requires manual loading          |
| Summary    | Long chats  | Efficient and scalable | May lose details                 |


# Stateful vs Stateless Architecture

## Stateless Architecture

- A server does not store user state between requests.
- Each request contains everything needed to process it.
Example:

```text
Request 1 → Process → Response
Request 2 → Process → Response
```

No memory exists inside the server.

## Stateful Architecture

- The server remembers previous interactions.

Example:

```text
Request 1
Server stores state

Request 2
Server reuses stored state
```

---

# Why Stateless Is Preferred in Production

Imagine one million users chatting simultaneously.

If every server stored conversation state:

* Memory usage would explode
* Servers could not be freely replaced
* Load balancing becomes difficult

Instead:

```text
Client
   ↓
Stateless Server
   ↓
Database / Memory Store
```

The server remains lightweight while memory is stored externally.

