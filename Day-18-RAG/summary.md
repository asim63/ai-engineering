# Day 18 — Introduction to RAG (Retrieval-Augmented Generation)

## Overview

Today focused on understanding RAG conceptually before implementing it. The goal was to build a strong mental model of how external knowledge is supplied to Large Language Models at query time.

---

## Why RAG?

Large Language Models have limitations:

* Knowledge cutoff dates
* No awareness of private company data
* No access to personal documents by default
* Retraining or fine-tuning is expensive and slow

RAG solves this by retrieving relevant information when a question is asked and providing that information as context to the model.

---

## Core Idea

Instead of storing knowledge inside model weights:

```text
Question
    ↓
Retrieve Relevant Information
    ↓
Provide Context to LLM
    ↓
Generate Answer
```

This allows the model to answer questions using up-to-date and domain-specific information.

---

## RAG Pipeline

### 1. Load Data

Documents are collected from sources such as:

* PDFs
* Websites
* Databases
* Internal company documents

### 2. Chunking

Large documents are divided into smaller pieces called chunks.

### 3. Embedding

Each chunk is converted into a numerical vector representation.

### 4. Store

Embeddings are stored in a vector database.

### 5. Query

A user asks a question.

### 6. Retrieve

The question is embedded and compared against stored vectors.

### 7. Generate

The most relevant chunks are added to the prompt and sent to the LLM.

---

## Embeddings

Embeddings are numerical representations of text.

Key idea:

* Similar meanings → vectors close together
* Different meanings → vectors farther apart

Example:

```text
Cat
Dog
Tiger
Lion
```

would generally be closer together than:

```text
Cat
Database
Airplane
Tax
```

---

## Cosine Similarity

Cosine similarity measures how similar two vectors are.

General interpretation:

* 1.0 → very similar
* 0.8 → similar
* 0.5 → somewhat related
* 0.0 → unrelated

Vector databases use similarity metrics to retrieve relevant information efficiently.

---

## Vector Databases

A vector database stores embeddings and performs similarity searches.

Purpose:

* Fast retrieval
* Efficient nearest-neighbor search
* Scales to large document collections

Examples:

* FAISS
* ChromaDB
* Pinecone

---

## Tradeoffs of RAG

Advantages:

* Up-to-date information
* No retraining required
* Works with private data
* Lower cost than fine-tuning

Limitations:

* Retrieval can fail
* Irrelevant chunks may be returned
* Context windows are limited
* Answer quality depends on retrieval quality

---

## Real-World Applications

### Customer Support

Retrieve support articles and generate answers.

### Enterprise Knowledge Search

Search internal company documentation.

### Document Q&A Systems

Answer questions from PDFs, manuals, and reports.

---