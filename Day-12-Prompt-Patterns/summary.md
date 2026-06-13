# Day 11 - Prompt Patterns for Real Applications

## Overview
Today, I explored core LLM prompt patterns used in real-world AI applications and learned how to structure prompts based on task type and system design.

---

## 1. Core LLM Task Types

I learned the four fundamental LLM task categories:

- **Classification** → Assigning labels or categories to input data  
- **Extraction** → Pulling structured data from unstructured text  
- **Summarization** → Compressing information into shorter meaningful forms  
- **Generation** → Creating new content based on instructions  

---

## 2. Classification Pattern

- Built a multi-label classifier using LLM prompts  
- Designed output in **strict JSON format**  
- Included **confidence scores** for each label  
- Focused on consistency and structured outputs  

---

## 3. Extraction Pattern

- Extracted structured fields from messy/unstructured text  
- Ensured reliability by enforcing strict schema-based outputs  
- Practiced converting natural language into structured JSON  

---

## 4. Summarization Pattern

- Generated multiple types of summaries from the same input:
  - Bullet point summary  
  - Paragraph summary  
  - ELI5 (Explain Like I’m 5)  
  - Executive summary  
- Learned how different audiences require different summary styles  

---

## 5. Generation Pattern

- Practiced constrained creative generation  
- Controlled:
  - Format (JSON, markdown, structured text)  
  - Tone (formal, casual, technical)  
  - Output boundaries and constraints  
- Focused on predictable and reusable outputs  

---

## 6. Chain Patterns (Pipeline Thinking)

- Learned how to connect multiple LLM calls in sequence  
- Output of one model call becomes input for another  

---

## 7. Router Pattern

- Built a routing system using a fast/cheap model  
- Model decides which prompt pattern to use  
- Then forwards the task to the appropriate specialized prompt  
- Learned early-stage **LLM orchestration design**

---
