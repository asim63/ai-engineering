# Day-22 — PDF Chat System (First Complete RAG Application)

## Topics Covered

* PDF Loading using PyPDFLoader
* Document Cleaning
* Recursive Character Chunking
* Embeddings using all-MiniLM-L6-v2
* ChromaDB Vector Storage
* Similarity Search Retrieval
* Source Citations
* Confidence Scoring Concepts
* Preparing Retrieval Context for LLMs
* Local RAG Architecture

---

## What I Built

Built the foundation of a PDF Chat System capable of:

1. Loading PDFs
2. Cleaning extracted text
3. Chunking documents
4. Creating embeddings
5. Storing chunks inside ChromaDB
6. Retrieving relevant chunks based on user questions

Current pipeline:

PDF → Loader → Cleaner → Chunker → Embeddings → ChromaDB → Retrieval

---

## Important Learnings

### Why Cleaning Matters

PDFs often contain:

* Extra spaces
* Page numbers
* Repeated headers
* Formatting artifacts

Cleaning improves chunk quality and retrieval accuracy.

---

### Why Chunking Matters

Embedding an entire PDF is inefficient.

Chunking allows:

* Better retrieval precision
* Lower embedding cost
* Better context selection

Used:

* RecursiveCharacterTextSplitter
* chunk_size = 1000
* chunk_overlap = 100

---

### Why Vector Databases Matter

Instead of searching raw text, documents are converted into embeddings.

ChromaDB stores:

* Chunks
* Embeddings
* Metadata
* IDs

and retrieves semantically similar content.

---

### Retrieval Before LLM

A key lesson:

Poor retrieval leads to poor answers.

Testing retrieval independently is critical before connecting an LLM.

---

### Citations

Retrieved chunks preserve metadata such as:

* Source file
* Page number

This allows answers to reference where information originated.

---

### Confidence Scores

Using similarity_search_with_score() enables measuring retrieval quality.

Lower scores indicate more relevant chunks.

Potential confidence levels:

* High
* Medium
* Low

based on average retrieval distance.

---

### Preparing Context

Retrieved chunks must be combined into text before sending to the LLM.

Example:

context = "\n\n".join(chunk.page_content for chunk in results)

This becomes the context supplied to the model.

---

## Next Steps

* Connect Ollama Qwen3:8B
* Generate answers using retrieved context
* Show citations alongside answers
* Add confidence indicators
* Implement persistent vector store loading

---

## Reflection

This project combines nearly every major concept learned so far:

* Document Loading
* Cleaning
* Chunking
* Embeddings
* Vector Databases
* Retrieval
* Prompt Construction

This is my first complete local RAG system.
