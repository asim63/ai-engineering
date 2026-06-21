from sentence_transformers import SentenceTransformer
import numpy as np
model = SentenceTransformer("all-MiniLM-L6-v2")

def cosine_sim(a,b):
    return np.dot(a,b)/(
        np.linalg.norm(a) * np.linalg.norm(b)
    )
    
documents = [
    "Python is a programming language",
    "Cats are domestic animals",
    "RAG combines retrieval and generation",
    "The stock market increased today",
    "Machine learning uses data"
]

query = "How does retrival acutally work?"
query_emb = model.encode(query)
results = []

for doc in documents:
    doc_emb = model.encode(doc)

    similarity = cosine_sim(
        doc_emb,
        query_emb
    )
    results.append(
        {
            "document": doc,
            "similarity": similarity
        }
    )

results.sort(
    key = lambda x: x["similarity"],
    reverse=True
)
print(results[:3])