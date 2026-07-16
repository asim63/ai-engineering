import time
import ollama
from pypdf import PdfReader

def load_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def embed_chunks(chunks: list[str]) -> list[list[float]]:
    return [ollama.embeddings(model="nomic-embed-text", prompt=c)["embedding"] for c in chunks]

def cosine_sim(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    return dot / (norm_a * norm_b + 1e-8)

def retrieve_top_chunk(question: str, chunks: list[str], chunk_embeddings: list[list[float]]) -> str:
    q_emb = ollama.embeddings(model="nomic-embed-text", prompt=question)["embedding"]
    scores = [cosine_sim(q_emb, c_emb) for c_emb in chunk_embeddings]
    best_idx = scores.index(max(scores))
    return chunks[best_idx]

def ask_llm(question: str, context: str) -> str:
    prompt = f"Answer the question using only this context:\n\n{context}\n\nQuestion: {question}"
    response = ollama.chat(model="qwen3:8b", messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]


def timed_pipeline(pdf_path: str, question: str):
    timings = {}

    t0 = time.perf_counter()
    text = load_pdf_text(pdf_path)
    timings["load_pdf"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    chunks = chunk_text(text)
    timings["chunk_text"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    chunk_embeddings = embed_chunks(chunks)
    timings["embed_chunks"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    context = retrieve_top_chunk(question, chunks, chunk_embeddings)
    timings["retrieve"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    answer = ask_llm(question, context)
    timings["llm_call"] = time.perf_counter() - t0

    timings["total"] = sum(timings.values())
    return answer, timings

answer, timings = timed_pipeline(r"Day-34-Latency-Optimization\northwind_handbook.pdf", "What is this document about?")
for step, duration in timings.items():
    print(f"{step:15s}: {duration:.2f}s")