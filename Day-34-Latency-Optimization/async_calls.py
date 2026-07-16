import asyncio
from ollama import chat, embeddings
import numpy as np
from pypdf import PdfReader

def load_pdf_text(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)

def cosine_similarity(a,b):
    return np.dot(a,b)/(
        np.linalg.norm(a) * np.linalg.norm(b)
    ) 
def chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def embed_chunks(chunks: list[str]) -> list[list[float]]:
    return [embeddings(model="nomic-embed-text", prompt=c)["embedding"] for c in chunks]

async def retrieve_top_chunk_async(question: str, chunks: list[str], chunk_embeddings: list[list[float]]) -> str:
    # ollama's sync client blocks; run it in a thread so it doesn't block the event loop
    q_emb = await asyncio.to_thread(lambda: embeddings(model="nomic-embed-text", prompt=question)["embedding"])
    scores = [cosine_similarity(q_emb, c_emb) for c_emb in chunk_embeddings]
    best_idx = scores.index(max(scores))
    return chunks[best_idx]

async def classify_query_intent_async(question: str) -> str:
    """A second, independent LLM call — e.g., to tag the query type for analytics/routing."""
    def _call():
        response = chat(
            model="qwen3:8b",
            messages=[{"role": "user", "content": f"In one word, classify this query as 'factual', 'summary', or 'opinion': {question}"}]
        )
        return response["message"]["content"].strip()
    return await asyncio.to_thread(_call)

async def handle_question(question: str, chunks: list[str], chunk_embeddings: list[list[float]]):
    # Run retrieval AND intent classification concurrently — not one after another
    context, intent = await asyncio.gather(
        retrieve_top_chunk_async(question, chunks, chunk_embeddings),
        classify_query_intent_async(question),
    )
    print(f"[intent: {intent}]")

    # Now use the retrieved context for the final answer
    prompt = f"Answer using only this context:\n\n{context}\n\nQuestion: {question}"
    response = await asyncio.to_thread(
        lambda: chat(model="qwen3:8b", messages=[{"role": "user", "content": prompt}])
    )
    return response["message"]["content"]



text = load_pdf_text(r"Day-34-Latency-Optimization\northwind_handbook.pdf")
    
chunks = chunk_text(text)

chunk_embeddings = embed_chunks(chunks)

answer = asyncio.run(handle_question("What is the refund policy?", chunks, chunk_embeddings))