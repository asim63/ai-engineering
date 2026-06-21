import chromadb
client = chromadb.PersistentClient(
    path=r"D:\AI_Data\chroma_db"
)
collection = client.get_or_create_collection(name = "note")

results = collection.query(
    query_texts=["what is python"],
    n_results=2
)
print(results)