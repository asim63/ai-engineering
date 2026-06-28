# Day 23 & 24 — Advanced RAG Patterns

## What I Built Today
A full Advanced RAG pipeline combining **Multi-Query**, **HyDE**, **Parent-Child chunking**,
**Hybrid Search (BM25 + Vector + RRF)**, **Cross-Encoder Reranking**, **Contextual Compression**,
and a reusable **RAGConfig + RAGPipeline** package.

---

## 1. Multi-Query Retrieval

**Problem:** A single query might miss relevant chunks because the wording doesn't match how
the document phrases the answer.

**Solution:** Use an LLM to rephrase the query into 3 variations, run retrieval for all of them,
pool the results, deduplicate, then rerank against the **original** query.

```python
queries = retrieve_queries(true_query)   # LLM generates 3 rephrases
queries.append(true_query)              # always include the original

all_results = []
for q in queries:
    results = retrieve_result(q, db)
    all_results.extend(results)
```

**Key bug to avoid:** use `q` as the loop variable, NOT `query` — otherwise you overwrite
the original `true_query` and the reranker gets the wrong query.

**Deduplication pattern:**
```python
seen = {}
for doc, score in all_results:
    key = doc.page_content
    if key not in seen:
        seen[key] = (doc, score)
unique_results = list(seen.values())
```

---

## 2. HyDE — Hypothetical Document Embeddings

**Problem:** A question and its answer live in different places in vector space.
"What is attention?" is semantically far from "Attention is a mechanism that..."

**Solution:** Ask the LLM to write a fake answer first, embed the fake answer, use THAT for
retrieval. A hypothetical answer lives in the same semantic space as real answers.

```
user question → LLM generates fake answer → embed fake answer → search → retrieve real chunks
```

```python
def hyde_result(query):
    response = chat(model="qwen3:8b", messages=[{
        "role": "user",
        "content": f"Write a short factual paragraph answering this. No preamble.\n\nQuestion: {query}\nAnswer:"
    }])
    raw = response["message"]["content"]
    if "<think>" in raw:
        raw = raw[raw.rfind("</think>") + 8:].strip()
    return raw
```

**Important:** retrieve with the hypothetical answer, but **rerank and prompt with the real query**.
The fake answer is only for retrieval — never shown to the user.

**What good HyDE looks like in practice:**
```
Query retrieval scores:   0.49, 0.42, 0.26   ← okay
HyDE retrieval scores:    0.99, 0.97          ← much more confident, same chunks
```

---

## 3. Parent-Child Chunking

**Problem:** Small chunks = better retrieval precision. Large chunks = better LLM context.
You can't have both with one chunk size.

**Solution:** Split twice. Store **small child chunks** in the vector DB for retrieval.
When a child matches, return its **large parent chunk** to the LLM.

```
Document
├── Parent Chunk 1  (800 tokens) ← LLM sees this
│   ├── Child 1a (200 tokens)   ← vector DB stores this
│   ├── Child 1b (200 tokens)
│   └── Child 1c (200 tokens)
```

**Implementation — tag each child with its parent's ID:**
```python
for i, parent in enumerate(parent_splitter.split_documents(documents)):
    parent_id = f"parent_{i}"
    parent_chunks[parent_id] = parent          # stored in memory dict

    for child in child_splitter.split_documents([parent]):
        child.metadata["parent_id"] = parent_id   # tag the child
        child_chunks.append(child)                 # goes into vector DB
```

**Retrieval — swap child for parent:**
```python
seen = set()
for child_doc, score in top_children:
    parent_id = child_doc.metadata.get("parent_id")
    if parent_id and parent_id not in seen:
        seen.add(parent_id)
        parent_doc = parent_chunks[parent_id]
        final_docs.append((parent_doc, score))
```

**`seen` must be a `set()`, not a `dict()`.** Sets have `.add()`, dicts don't.

**Watch out:** `parent_chunks[parent_id] = parent,` — that trailing comma wraps the Document
in a tuple. Remove the comma.

**Delete your old ChromaDB folder** when switching to parent-child — old chunks won't have
`parent_id` in metadata and retrieval will silently return nothing.

---

## 4. Metadata Filtering

Filter the vector search **before** similarity runs — narrows the search space.

```python
# Only search chunks from pages 2-4
results = db.similarity_search_with_score(
    query=query,
    k=10,
    filter={"page": {"$gte": 2, "$lte": 4}}
)

# Only search a specific section
results = db.similarity_search_with_score(
    query=query,
    k=10,
    filter={"section": "Chapter 2"}
)
```

**ChromaDB filter operators:** `$eq`, `$ne`, `$in`, `$nin`, `$gt`, `$gte`, `$lt`, `$lte`

Enrich chunk metadata during chunking by detecting headings with regex:
```python
match = re.search(r"Chapter \d+[:\s]+([^\n\.]+)", parent.page_content)
if match:
    current_section = match.group(0).strip()
parent.metadata["section"] = current_section
```

---

## 5. Contextual Compression

After retrieval you have 3 parent chunks (800 tokens each). But most of that might be
irrelevant to the specific question. Compression asks the LLM to extract only the
relevant sentences before passing to the final answer LLM.

```python
def compress_chunks(query, docs):
    compressed = []
    for doc, score in docs:
        response = chat(model="qwen3:8b", messages=[{
            "role": "user",
            "content": f"""Extract only sentences directly relevant to the question.
If nothing is relevant, reply with NOT RELEVANT.

Question: {query}
Passage: {doc.page_content}
Extract:"""
        }])
        extract = strip_think_tags(response["message"]["content"])
        if "NOT RELEVANT" not in extract and len(extract.strip()) > 20:
            compressed.append((doc, score, extract))
    return compressed

# Build context from compressed text, not full chunks
context = "\n\n".join(extract for _, _, extract in compressed)
```

**Trade-off:** Better context quality, but costs one extra LLM call per chunk. Keep
`use_compression: bool = False` by default and turn on only when needed.

---

## 6. RAG Config Object

A dataclass that holds all settings in one place. No hardcoded values scattered across functions.

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class RAGConfig:
    # Chunking
    parent_chunk_size: int = 800
    child_chunk_size: int = 200

    # Retrieval
    retrieval_k: int = 10
    top_n_rerank: int = 3

    # Models
    llm_model: str = "qwen3:8b"
    embedding_model: str = "all-MiniLM-L6-v2"
    reranker_model: str = "BAAI/bge-reranker-base"

    # Feature toggles
    use_hyde: bool = True
    use_multi_query: bool = True
    use_parent_child: bool = True
    use_hybrid_search: bool = True
    use_compression: bool = False

    # Optional metadata filter
    metadata_filter: Optional[dict] = None
```

**What `@dataclass` does:** auto-generates `__init__` so you don't write it manually.
`field_name: type = default` is the syntax for each field.

**What `Optional[dict]` means:** the value is either a `dict` or `None`.
Comes from the `typing` module. For `int`, `str`, `bool` you don't need `typing` — those
are built-in. Only needed for complex types like `Optional`, `List`, `Dict`.

**Switch strategies instantly:**
```python
fast_config = RAGConfig(use_hyde=False, use_compression=False, retrieval_k=5)
deep_config  = RAGConfig(use_hyde=True,  use_compression=True,  retrieval_k=20)
```

---

## 7. RAGPipeline Package

Organized as an importable Python package so any future project can reuse everything.

```
rag/
├── __init__.py      ← from .pipeline import RAGPipeline; from .config import RAGConfig
├── config.py        ← RAGConfig dataclass (settings only, no logic)
├── pipeline.py      ← RAGPipeline class (all functions)
└── utils.py         ← clean_text(), strip_think_tags()
```

**`__init__.py`** is what makes the folder a package. Without it, Python won't recognize
the folder as importable.

**Any project now becomes:**
```python
from rag import RAGPipeline, RAGConfig

config = RAGConfig(persist_directory="D:/AI_Data/Day25", use_hyde=True)
rag = RAGPipeline(config)
rag.load_pdf("my_document.pdf")
rag.query("What is attention?")
```

---

## Bugs I Hit and Fixed

| Bug | Symptom | Fix |
|-----|---------|-----|
| Used `query` as loop variable in multi-query | Reranker got wrong query | Rename loop var to `q`, keep `true_query` separate |
| `result1` overwritten by second assignment | First retrieval result lost | Use `result_query` and `result_hyde` separately |
| `create_or_get_db()` inside while loop | DB reconnects on every query | Move it above the loop |
| `seen = {}` with `.add()` | AttributeError: dict has no .add | Change to `seen = set()` |
| Trailing comma: `parent_chunks[id] = parent,` | Stored a tuple, not a Document | Remove the comma |
| Old ChromaDB loaded after adding parent-child | `parent_id` always None, empty results | Delete the DB folder and rebuild |
| `Chroma.from_texts(texts=chunks)` with Document objects | Wrong data stored | Use `Chroma.from_documents(documents=chunks)` |
| `Page /d+` in regex | Regex never matched | Change `/d` to `\d` |

---

## The Full Pipeline Flow

```
User Query
    │
    ├── Multi-Query → 3 rephrased versions
    │
    ├── HyDE → 1 hypothetical answer
    │
    └── All queries (original + rephrases + HyDE answer)
            │
            ▼
        Hybrid Search (BM25 + Vector → RRF fusion)  [per query]
            │
            ▼
        Pool all results → Deduplicate by page_content
            │
            ▼
        Parent Swap (child_id → parent document)
            │
            ▼
        Final Rerank against TRUE query (CrossEncoder)
            │
            ▼
        Contextual Compression (optional)
            │
            ▼
        LLM generates answer from compressed context
```

---
