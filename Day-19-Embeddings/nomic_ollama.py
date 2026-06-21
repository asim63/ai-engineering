from ollama import embeddings
import numpy as np

cat = embeddings(
    model="nomic-embed-text",
    prompt="The cat sat on the mat"
)["embedding"]
sky = embeddings(
    model="nomic-embed-text",
    prompt="The sky is blue"
)["embedding"]
dog = embeddings(
    model="nomic-embed-text",
    prompt="The dog sat on the mat"
)["embedding"]

def similarity(a,b):
    return np.dot(a, b)/(
             np.linalg.norm(a) * np.linalg.norm(b)
             )

print(similarity(cat,sky))
print(similarity(cat,dog))