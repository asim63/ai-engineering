import chromadb

client = chromadb.Client()

collection = client.create_collection(name = "space")

collection.add(
    documents=[
        "Earth lies in Milky Way galaxy.",
        "Sun is the closest start to Earth.",
        "Andromeda is the closest galaxy to Milky Way",
        "Blackhole is located at the center of Galaxy.",
        "The dog is playing in the park."    
    ],
    ids = ["MilkyWay","sun","andromeda","blackhole","dog"],
    metadatas=[
        {"category": "galaxy" },
        {"category": "star" },
        {"category": "galaxy" },
        {"category": "supernova" },
        {"category": "animal" },
        
    ]
)

results = collection.query(
    query_texts=["Name of two or more galaxies."],
    where={
        "category":"galaxy"
    },
    n_results= 4
)
print(results)