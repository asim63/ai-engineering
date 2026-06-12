# Day 11 - Building a Real Chatbot with Memory

## Chatbot Design

* Designed and implemented a quiz chatbot using Python OOP.
* Created a `Chatbot` class to manage conversation state, quiz generation, and commands.
* Learned how classes help organize functionality into reusable methods and attributes.

## Conversation History Management

* Implemented conversation history using a list of messages.
* Learned why chat applications must resend conversation history with each request.
* Applied a truncation strategy to limit context growth and reduce token usage.
* Understood the tradeoff of truncation: lower token cost but loss of older context.

## Command System

* Added custom chatbot commands:

  * `/generate` to generate quiz questions
  * `/save` to save conversation history
  * `/clear` to reset conversation history
  * `/exit` to terminate the application
* Learned how command parsing works before sending user input to the LLM.

## Quiz Generation with Structured Output

* Used system instructions to force the model to generate quiz questions in JSON format.
* Parsed JSON responses into Python objects using `json.loads()`.
* Stored generated questions and answers separately from conversation history.
* Built a simple quiz flow that validates user answers and tracks quiz progress.

## Error Handling and Retry Logic

* Implemented exception handling using `try/except`.
* Learned how API failures can occur due to network issues or rate limits.
* Built a retry mechanism with exponential backoff:

  * Wait 1 second
  * Retry
  * Wait 2 seconds
  * Retry
  * Wait 4 seconds, and so on
* Understood why retry logic improves application reliability.

## Streaming API

* Learned the difference between standard response generation and streaming responses.
* Understood how streaming improves user experience by displaying output as it is generated.
* Explored how `generate_content_stream()` can be used for real-time response rendering.

## Key Learnings

* A chatbot is more than a single API call; it requires memory, state management, error handling, and user commands.
* Context management is necessary to prevent token usage from growing indefinitely.
* Structured JSON outputs make LLM responses easier to integrate into applications.
* Separating application logic from model prompts leads to cleaner and more maintainable code.
