# Day-21: Document Loading and Chunking for RAG

## What I Learned

### Why Documents Need Cleaning

Before chunking, documents often contain:

* Extra whitespace
* Page numbers
* Headers and footers
* Formatting artifacts

Cleaning improves chunk quality and retrieval performance.

Example:

```python
def clean(text):
    text = re.sub(r'Page \d+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()
```

---

### Fixed-Size Chunking

Used:

```python
CharacterTextSplitter
```

Splits documents strictly by character count.

Pros:

* Simple
* Fast

Cons:

* Can split sentences in half
* May break important context

---

### Recursive Chunking

Used:

```python
RecursiveCharacterTextSplitter
```

Attempts to split using:

1. Paragraphs
2. Lines
3. Spaces
4. Characters

Pros:

* Preserves meaning better
* Industry standard for many RAG systems

---

### Semantic Chunking

Used:

```python
SemanticChunker
```

Uses embeddings to group sentences with similar meaning.

Pros:

* Produces more meaningful chunks
* Better retrieval quality

Cons:

* Slower
* Requires embedding model

---

### Chunk Size Tradeoffs

Small chunks:

* More precise retrieval
* Less context

Large chunks:

* More context
* More noise

Typical production values:

* Chunk Size: 500–1000
* Overlap: 50–200

---

### Chunk Overlap

Overlap prevents losing information at chunk boundaries.

Example:

```python
chunk_size=500
chunk_overlap=50
```

Without overlap, important information can be split between chunks.

---

### RAG Pipeline

A standard RAG pipeline:

Document
↓
Clean
↓
Chunk
↓
Embed
↓
Store in Vector Database
↓
Retrieve
↓
LLM

---
