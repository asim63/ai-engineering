# Day-19 Embeddings

## Sentence Transformers

* Installed `sentence-transformers`
* Downloaded and used `all-MiniLM-L6-v2`
* Generated first embedding successfully
* Observed embedding shape `(384,)`
* Learned that embeddings are dense vector representations of text
* Understood that each sentence is converted into a fixed-length vector

## nomic-embed-text

* Installed `nomic-embed-text`
```bash 
ollama pull nomic-embed-text
```
* Calculate cosine similarities
```python
from ollama import embeddings

response = embeddings(
    model = "nomic-embed-text",
    prompt = "text here"
)
emb = response["embeddings"]
print(len(emb))

```

## Model Loading vs Inference

* Measured model loading and embedding generation times
* Model loading took approximately 6.7 seconds
* Embedding generation took approximately 0.05 seconds
* Learned that startup overhead is the main cost, not vector generation

## Hugging Face Model Caching

* Learned that models are downloaded locally and cached
* No API key is required for Sentence Transformers
* Understood Hugging Face cache warnings and why they can be ignored for learning purposes

## Embedding Concepts

* Learned that similar sentences generate similar vectors
* Learned that unrelated sentences generate dissimilar vectors
* Understood vector dimensions and semantic representation

## Cosine Similarity

* Learned how cosine similarity measures semantic closeness between vectors
* Prepared to test:

  * "The cat sat on the mat"
  * "A feline rested on a rug"
  * "Stock markets rose today"

## Semantic Search

* Learned the semantic search workflow:

  1. Embed all documents
  2. Embed the query
  3. Calculate cosine similarity
  4. Sort by similarity score
  5. Return top matching documents

* Understood that `model.encode(documents)` creates one embedding per document, not one embedding for the whole list


