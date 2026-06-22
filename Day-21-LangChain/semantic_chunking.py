from langchain_experimental.text_splitter import SemanticChunker
import re
from langchain_huggingface import HuggingFaceEmbeddings


def clean_text(text):
    text = re.sub(r'Page \d+','', text)
    text = re.sub(r'\s+',' ', text)
    text = re.sub(r'\n+','\n', text)
    return text.strip()

sample_text = """
Python is a programming language.
Python supports object-oriented programming.
Classes and objects are important concepts.
Inheritance promotes code reuse.
Polymorphism allows flexible design.

Machine learning uses data.
Embeddings convert text into vectors.
Vector databases store embeddings.
RAG combines retrieval and generation.
Semantic search uses embeddings.

Football is played with eleven players.
The World Cup is very popular.
Messi won the World Cup.
Teams compete in tournaments.
Fans watch matches worldwide.
"""

cleaned_text = clean_text(sample_text)

embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")

semantic_splitter = SemanticChunker(
    embeddings,
    breakpoint_threshold_type="standard_deviation",
    breakpoint_threshold_amount=1
    )

chunks = semantic_splitter.split_text(cleaned_text)

print(f"Total Chunks: {len(chunks)}")

for i, chunk in enumerate(chunks, start=1):
    print(f"\n----- Chunk {i} -----")
    print(chunk)