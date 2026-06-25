import os
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder
from ollama import chat
from rank_bm25 import BM25Okapi
from collections import defaultdict
from langchain_core.documents import Document

class ChatPDF:
    def __init__(self):
        self.persist_directory = r"D:\AI_Data\Hybrid_PDF"
        self.collection_name = "pdf-chat"
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        # Load local cross-encoder for re-ranking
        self.reranker = CrossEncoder("BAAI/bge-reranker-base")
        self.bm25 = None
        self.chunks = None
    def rebuild_bm25_from_db(self, db):
        data = db.get()
        chunks = [
            Document(
                page_content=text,
                metadata=metadata
            )
            for text, metadata in zip(
                data["documents"],
                data["metadatas"]
            )
        ]
        self.build_bm25(chunks)   
    def clean_document(self, text):
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n+", "\n", text)
        text = re.sub(r"Page \d+", "", text)
        return text.strip()
    
    def build_bm25(self, chunks):
        self.chunks = chunks
        tokenized_docs = [
            chunk.page_content.lower().split()
            for chunk in chunks
        ]
        self.bm25 = BM25Okapi(tokenized_docs)
        print("BM25 Index Built")
    
    def load_document(self):
        dir_path = r"Day-23-Improving-RAG/"
        filename = input("Enter the name of the PDF (e.g., file.pdf): ")
        ultimate_path = os.path.join(dir_path, filename)
        try:
            loader = PyPDFLoader(ultimate_path)
            documents = loader.load()
            
            # Prevent duplicates by tagging metadata source with filename
            for doc in documents:
                doc.page_content = self.clean_document(doc.page_content)
                doc.metadata["source"] = filename
            return documents
        except Exception as e:
            print(f"Error loading document: {e}")
            return []
            
    def chunk_document(self, doc):
        splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=40, separators=["\n\n", "\n", ". ", " ", ""])
        return splitter.split_documents(doc)
    
    def filter_chunks(self, chunks):
        return [c for c in chunks if len(c.page_content.strip()) >= 100 and len(c.page_content.split()) >= 20]
    
    def get_or_create_db(self, chunks=None):
        """Handles seamless loading, updating without duplicates, or initial initialization"""
        db_exists = os.path.exists(self.persist_directory) and len(os.listdir(self.persist_directory)) > 0
        
        if db_exists:
            db = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings, collection_name=self.collection_name)
            if chunks:
                # Check if this file's chunks already exist in the database metadata
                filename = chunks[0].metadata.get("source")
                existing = db.get(where={"source": filename})
                if existing and existing["ids"]:
                    print(f"'{filename}' already exists in DB. Skipping ingestion.")
                else:
                    print(f"Appending new chunks from '{filename}' to existing DB...")
                    db.add_documents(chunks)
            return db
        else:
            if not chunks:
                return None
            print("Creating fresh database...")
            return Chroma.from_documents(documents=chunks, embedding=self.embeddings, persist_directory=self.persist_directory, collection_name=self.collection_name)
        
    def ask_query(self, db):
        query = input("\nEnter your query (or type '/exit' to exit): ")
        if query.lower() == "/exit": return None, None 
        doc_lookup = {}
        #bm25 results
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        bm25_results = list(zip(self.chunks,scores))
        
        bm25_results.sort(
            key = lambda x:x[1],
            reverse=True
        )
        final_bm25 = bm25_results[:15]
        
        #vector_results
        vector_results = db.similarity_search_with_score(
            query=query,
            k=15
        )
        vector_results.sort(
            key = lambda x: x[1],
            reverse=False
        )
        #RRF
        rrf_scores = defaultdict(float)
        k = 60
        #bm25
        for rank,(doc,_) in enumerate(final_bm25,start=1):
            key = doc.page_content
            doc_lookup[key] = doc
            rrf_scores[key] += 1/(k+rank)
            
        #vector
        for rank,(doc,_) in enumerate(vector_results,start = 1):
            key = doc.page_content
            doc_lookup[key] = doc
            rrf_scores[key] += 1/(k+rank)
        
        hybrid_results = [
            (doc_lookup[text], score)
            for text, score in sorted(
                rrf_scores.items(),
                key=lambda x:x[1],
                reverse=True
            )
        ]
        print("\n=== Hybrid Results ===")
        for i, (doc, score) in enumerate(hybrid_results[:10], 1):
            print(
                f"{i}. {score:.4f} | "
                f"{doc.metadata.get('page')} | "
                f"{doc.page_content[:80]}"
            )
        initial_results = hybrid_results
        
        
        if not initial_results: return query, []

        # Cross-Encoder Re-ranking Phase
        pairs = [[query, doc.page_content] for doc, _ in initial_results]
        rerank_scores = self.reranker.predict(pairs)
        
        # Attach the new scores back and sort descending by accuracy
        reranked_docs = [(initial_results[i][0], float(rerank_scores[i])) for i in range(len(initial_results))]
        reranked_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Sift the best top 3 high-precision matches
        return query, reranked_docs[:3]


if __name__ == "__main__":
    chat_pdf = ChatPDF()
    print("\n=== AI PDF Chat System (With Re-ranking) ===")
    print("1. Ingest/Add a PDF into the database\n2. Chat with the existing database")
    choice = input("Select an option (1 or 2): ")

    if choice == '1':
        documents = chat_pdf.load_document()
        if documents:
            chunks = chat_pdf.filter_chunks(chat_pdf.chunk_document(documents))
            chat_pdf.build_bm25(chunks)
            db = chat_pdf.get_or_create_db(chunks)
        else:
            exit()
    elif choice == '2':
        db = chat_pdf.get_or_create_db()
        if not db:
            print("No existing database found! Run option 1 first.")
            exit()

        chat_pdf.rebuild_bm25_from_db(db)
    else:
        exit()

    print(f"\nDatabase loaded. Chunks in collection: {db._collection.count()}")

    while True:
        query, results = chat_pdf.ask_query(db)
        if query is None: break
        if not results:
            print("No matches found.")
            continue
            
        context = "\n\n".join(doc.page_content for doc, _ in results)
        
        print("\n" + "="*20 + " Top Re-ranked Context " + "="*20)
        for i, (doc, score) in enumerate(results, start=1):
            print(f"[{i}] File: {doc.metadata.get('source')} | Page: {doc.metadata.get('page', 'Unknown')} | Re-rank Score: {score:.4f}")
        print("=" * 63)
        
        prompt = f"Answer ONLY using the provided context. If you do not know, say so.\n\nContext:\n{context}\n\nQuestion:\n{query}\n\nAnswer:\n"
        
        try:
            stream = chat(model="qwen3:8b", messages=[{"role": "user", "content": prompt}], stream=True)
            print("\nAI Answer: ", end="", flush=True)
            for chunk in stream:
                print(chunk["message"]["content"], end="", flush=True)
            print()
        except Exception as e:
            print(f"\nError calling Ollama: {e}")