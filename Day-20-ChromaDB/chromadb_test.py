import chromadb

client = chromadb.Client()
collection = client.create_collection(name="vehicles")

print(collection.name)

# Add data
collection.add(
    documents=[
        "Car runs in highway.",
        "Plane flies in the sky.",
        "Boat travels by water.",
        "Bus is a public transport vehicle on road."
    ],
    ids = ["car1","plane1","boat1","bus1"]
)

# Query the collection

result = collection.query(
    query_texts=["I want to reach US in 2 hours. I live in Nepal"],
    n_results=2
)

print(result)