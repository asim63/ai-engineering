from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

chunks = [
    "Python supports object oriented programming.",
    "Embeddings convert text into vectors.",
    "The World Cup is a football tournament."
]

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

db = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings,
    persist_directory="./demo_db"
)

results = db.similarity_search(
    "How do embeddings work?",
    k=2
)

for doc in results:
    print(doc.page_content)