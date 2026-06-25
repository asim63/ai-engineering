from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

import os
import re

from sentence_transformers import CrossEncoder

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

persistent_directory = r"D:\AI_Data\Improving_RAG"
embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
collection_name = "pdf-chat"

def get_or_create_db(chunks=None):
    db_exists = os.path.exists(persistent_directory) and len(os.listdir(persistent_directory))>0
    
    if db_exists:
        db = Chroma(
            persist_directory=persistent_directory,
            embedding_function=embeddings,
            collection_name = collection_name
            )
        if chunks:
            filename = chunks[0].metadata.get("source")
            existing = db.get(where = {"source": filename})
            if existing and existing["ids"]:
                print(f"'{filename}' already exists in DB. Skipping ingestion.")
            else:
                print(f"Appending new chunks from '{filename}' to existing DB...")
                db.add_documents(chunks)
        return db
    else:
        if not chunks:
            return None
        print("Creating a fresh database")
        return Chroma.from_documents(
            documents= chunks,
            embedding= embeddings,
            persist_directory=persistent_directory,
            collection_name=collection_name
        )
    

def clean(text):
    text = re.sub(r"\s+"," ",text)
    text = re.sub(r"\n\n","\n",text)
    text = re.sub(r"Page \d+", "", text)
    return text.strip()

def load_pdf():
    filename = input("Enter your path to pdf (including .pdf): ")
    ultimate_path = "Day-23-Improving-RAG/" + filename
    try:
        loader = PyPDFLoader(ultimate_path)
        documents = loader.load()
        
        # Prevent duplicates by tagging metadata source with filename
        for doc in documents:
            doc.page_content = clean(doc.page_content)
            doc.metadata["source"] = filename
        return documents
    except Exception as e:
        print(f"Error loading document: {e}")
        return []

def chunk_document(doc):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 400,
        chunk_overlap = 40,
        separators=["\n\n","\n",". "," ",""]
    )
    return splitter.split_documents(doc)

def filter_chunks(chunks):
     return [c for c in chunks 
             if len(c.page_content.strip()) >= 100 and len(c.page_content.split()) >= 20]
     
def ask_query(db):
    query = input("Enter your query: ")
    if query.lower() == "/exit":
        return None, None

    initial_results = db.similarity_search_with_score(
        query=query,
        k=10
    )
    if not initial_results:
        return query, []
    
    print("\n=== Initial Chroma Ranking ===")

    for i, (doc, score) in enumerate(initial_results[:10], 1):
        print(f"\nRank {i}")
        print(f"Distance: {score:.4f}")
        print(doc.page_content[:150])
        print("-" * 50)

    pairs = [
        [query, doc.page_content]
        for doc, _ in initial_results
    ]
    rerank_scores = reranker.predict(pairs)
    ranked = list(zip(initial_results, rerank_scores))
    ranked.sort(
        key=lambda x: x[1],
        reverse=True
    )
    print("\n=== After Reranking ===")

    for i, ((doc, distance), rerank_score) in enumerate(ranked[:3], 1):
        print(f"\nRank {i}")
        print(f"CrossEncoder Score: {rerank_score:.4f}")
        print(f"Original Distance: {distance:.4f}")
        print(doc.page_content[:150])
        print("-" * 50)

    best_docs = [item[0] for item in ranked[:3]
    ]

    return query, best_docs


# Main Execution Loop
if __name__ == "__main__":
    print("\n=== AI PDF Chat System ===")
    print("1. Ingest a new PDF\n2. Chat with existing collection")
    choice = input("Select an option (1 or 2): ")

    if choice == '1':
        documents = load_pdf()
        if documents:
            chunks = filter_chunks(chunk_document(documents))
            db = get_or_create_db(chunks)
            print("Processing complete.")
        else:
            exit()
    elif choice == '2':
        db = get_or_create_db()
        if not db:
            print("No database found. Run option 1 first.")
            exit()
    else:
        exit()

    while True:
        query, top_results = ask_query(db)
        if query is None:
            print("Goodbye!")
            break
        if not top_results:
            print("No matching contexts found.")