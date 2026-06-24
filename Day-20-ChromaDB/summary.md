# Day-20 ChromaDB

## ChromaDB Basics

* Installed ChromaDB locally
* Learned the concept of:

  * Collections
  * Documents
  * Embeddings
  * Metadata
  * IDs

## Creating a Collection

Created a local collection and added documents.

```python
collection = client.create_collection(
    name="documents"
)
```

## Querying Documents

Used natural language queries to retrieve semantically similar documents.

```python
collection.query(
    query_texts=["How do embeddings work?"],
    n_results=3
)
```

## Understanding Results

Learned the structure of the returned object:

* documents
* ids
* metadatas
* distances

Observed that Chroma automatically performs:

1. Embedding generation
2. Similarity search
3. Ranking

## Metadata

Added metadata fields such as:

* category
* source

Example:

```python
{
    "category":"ai"
}
```

## Metadata Filtering

Tested metadata filtering using:

```python
where={
    "category":"ai"
}
```

Observed that metadata filtering is applied before similarity search.

Query execution flow:

All Documents
↓
Metadata Filter
↓
Similarity Search
↓
Top Results

## Retrieval Testing

Created documents in three categories:

* Programming
* AI
* Finance

Verified that:

* AI questions retrieved AI documents
* Programming questions retrieved Programming documents
* Finance questions retrieved Finance documents

Successfully validated semantic retrieval.

## Persistent Storage

Learned the difference between:

```python
chromadb.Client()
```

and

```python
chromadb.PersistentClient()
```

* Client() stores data only in memory
* PersistentClient() stores data on disk

Learned that Chroma persists:

* Document text
* Embeddings
* Metadata
* IDs
* Search indexes

## RAG Understanding

A major realization today:

RAG does not retrain the LLM.

Instead:

Private Documents
↓
Embeddings
↓
Vector Database
↓
Similarity Search
↓
Relevant Chunks
↓
LLM Context
↓
Answer

The vector database acts as external knowledge storage while the LLM remains unchanged.

