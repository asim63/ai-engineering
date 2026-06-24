import os
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from ollama import chat

class ChatPDF:
    def __init__(self):
        self.persist_directory = r"D:\AI_Data\PDF_Chat_System"
        self.collection_name = "pdf-chat"  # Shared collection key
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
    def clean_document(self, text):
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\n+", "\n", text)
        text = re.sub(r"Page \d+", "", text)
        return text.strip()
    
    def load_document(self):
        path = r"Day-22-Project3/"
        ultimate_path = path + input("Enter the name of the PDF (e.g., file.pdf): ")
        try:
            loader = PyPDFLoader(ultimate_path)
            documents = loader.load()
            
            for doc in documents:
                doc.page_content = self.clean_document(doc.page_content)
            return documents
        except FileNotFoundError:
            print("Is the path correct? There was no pdf in the path. Please recheck")
            return []
        except Exception as e:
            print(f"Error : {e}")
            return []
            
    def chunk_document(self, doc):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=40,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = splitter.split_documents(doc)
        return chunks
    
    def filter_chunks(self, chunks):
        filtered = []
        for chunk in chunks:
            text = chunk.page_content.strip()
            if len(text) < 100:
                continue
            if len(text.split()) < 20:
                continue
            filtered.append(chunk)
        return filtered
    
    def ingest_new_documents(self, chunks):
        """Creates or adds to a Chroma database using fresh chunks"""
        print("Embedding and storing documents...")
        db = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name 
        )
        return db
        
    def load_existing_db(self):
        """Loads an existing Chroma database directly from the disk."""
        print(f"Loading existing database from {self.persist_directory}")
        db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name=self.collection_name 
        )
        return db
        
    def ask_query(self, db):
        query = input("\nEnter your query (or type '/exit' to exit): ")
        if query.lower() == "/exit":
            return None, None 
            
        results = db.similarity_search_with_score(query=query, k=3)
        return query, results


if __name__ == "__main__":
    chat_pdf = ChatPDF()

    print("\n=== AI PDF Chat System ===")
    print("1. Ingest a new PDF into the database")
    print("2. Chat with the existing database")
    
    choice = input("Select an option (1 or 2): ")

    if choice == '1':
        documents = chat_pdf.load_document()
        if documents:
            chunks = chat_pdf.chunk_document(documents)
            chunks = chat_pdf.filter_chunks(chunks)
            db = chat_pdf.ingest_new_documents(chunks)
            print("Successfully processed and saved to database!")
        else:
            print("Exiting due to document load failure.")
            exit()
            
    elif choice == '2':
        
        if not os.path.exists(chat_pdf.persist_directory):
            print("No existing database found! Please run option 1 first.")
            exit() 
            
        db = chat_pdf.load_existing_db()
        
    else:
        print("Invalid choice.")
        exit()

    print("\nDatabase loaded. You can now ask questions!")
    print(f"Total chunks in database: {db._collection.count()}")

    while True:
        query, results = chat_pdf.ask_query(db)
        
        # Check if the user opted to exit
        if query is None:  
            print("Goodbye!")
            break
            
        if not results:
            print("No matches found in the document database.")
            continue
            
        context = "\n\n".join(
            doc.page_content for doc, score in results
        )
        
        avg_score = sum(score for _, score in results) / len(results)

        if avg_score < 1.0:
            confidence = "High"
        elif avg_score < 1.5:
            confidence = "Medium"
        else:
            confidence = "Low"

        print("\n" + "="*20 + " Context Retrieved " + "="*20)
        for i, (doc, score) in enumerate(results, start=1):
            page = doc.metadata.get("page", "Unknown")
            print(f"[{i}] Page {page} | Distance Score: {score:.4f}")
        print(f"Confidence: {confidence} (Avg Distance: {avg_score:.4f})")
        print("=" * 59)
        
        prompt = f"""Answer ONLY using the provided context. If the context does not contain the information, state that you do not know.

                Context:
                {context}

                Question:
                {query}

                Answer:
                """
        
        try:
            stream = chat(
                model="qwen3:8b",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            
            print("\nAI Answer: ", end="", flush=True)
            for chunk in stream:
                print(chunk["message"]["content"], end="", flush=True)
            print()
            
        except Exception as e:
            print(f"\nError calling local Ollama model: {e}")