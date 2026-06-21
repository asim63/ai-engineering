import chromadb

client = chromadb.PersistentClient(
    path=r"D:\AI_Data\chroma_db"
)

collection = client.get_or_create_collection(name = "note")

collection.add(
    documents= ["Python is a high level language"],
    ids = ["doc1"]
)

print("collection added")