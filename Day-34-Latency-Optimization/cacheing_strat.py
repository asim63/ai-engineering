import hashlib
import json
import os
import ollama
from pypdf import PdfReader
CACHE_DIR = "embedding_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_key(text: str) -> str:
    """A stable, unique fingerprint for a piece of text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_cached_embedding(text: str) -> list[float] | None:
    key = _cache_key(text)
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def save_embedding_to_cache(text: str, embedding: list[float]) -> None:
    key = _cache_key(text)
    path = os.path.join(CACHE_DIR, f"{key}.json")
    with open(path, "w") as f:
        json.dump(embedding, f)

def embed_with_cache(text: str) -> list[float]:
    cached = get_cached_embedding(text)
    if cached is not None:
        return cached
    embedding = ollama.embeddings(model="qwen3:8b", prompt=text)["embedding"]
    save_embedding_to_cache(text, embedding)
    return embedding

def embed_chunks_cached(chunks: list[str]) -> list[list[float]]:
    return [embed_with_cache(c) for c in chunks]

import time

def load_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

chunks = chunk_text(load_pdf_text("your_document.pdf"))

t0 = time.perf_counter()
embed_chunks_cached(chunks)
print(f"First run (cold cache): {time.perf_counter() - t0:.2f}s")

t0 = time.perf_counter()
embed_chunks_cached(chunks)  # same chunks — should hit cache
print(f"Second run (warm cache): {time.perf_counter() - t0:.2f}s")