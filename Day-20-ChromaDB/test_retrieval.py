import chromadb
client   = chromadb.Client()

collection = client.create_collection(name = "collection1")
programming_docs = [
    "Python is a high-level programming language.",
    "Functions help organize reusable code.",
    "Recursion is when a function calls itself.",
    "Lists are mutable data structures in Python.",
    "Binary search runs in O(log n) time."
]
ai_docs = [
    "Embeddings convert text into vectors.",
    "RAG combines retrieval and generation.",
    "Vector databases store embeddings efficiently.",
    "Large language models predict the next token.",
    "Cosine similarity measures vector similarity."
]
finance_docs = [
    "Stocks represent ownership in a company.",
    "Inflation reduces purchasing power over time.",
    "Interest rates influence borrowing costs.",
    "Bonds are debt instruments issued by governments.",
    "Diversification helps reduce investment risk."
]

documents = (programming_docs + ai_docs + finance_docs)
ids = [f"doc{i}" for i in range(len(documents))]
metadatas = (
    [{"category":"programming"}] * 5 +
    [{"category":"ai"}] * 5 +
    [{"category":"finance"}] * 5
)
collection.add(
    documents = documents,
    ids = ids,
    metadatas= metadatas
)

results = collection.query(
    query_texts=["How can i embed text into vector?"],
    where = {
        "category":"finance"
    },
    n_results= 3
)

print(results)