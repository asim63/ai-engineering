import sys
import uuid
from dotenv import load_dotenv
load_dotenv()

from langsmith import traceable
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from ollama import chat

PDF_PATH = r"Day-32-Tracing\northwind_handbook.pdf"
PERSIST_DIR = "D:/AI_Data/simple_pdf_chat"
COLLECTION_NAME = "pdf_chat"

embeddings = OllamaEmbeddings(model="nomic-embed-text")


@traceable(name="load_pdf")
def load_pdf(path):
    return PyPDFLoader(path).load()


@traceable(name="chunk_documents")
def chunk_documents(docs, chunk_size=1000, chunk_overlap=150):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(docs)


@traceable(name="build_vectorstore")
def build_vectorstore(chunks):
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
        collection_name=COLLECTION_NAME,
    )


@traceable(name="retrieve_chunks")
def retrieve(vectorstore, question, k=4):
    results = vectorstore.similarity_search(question, k=k)
    return [{"content": d.page_content, "metadata": d.metadata} for d in results]


@traceable(name="generate_answer")
def generate_answer(question, retrieved_chunks, model="qwen3:8b"):
    context_text = "\n\n---\n\n".join(c["content"] for c in retrieved_chunks)
    prompt = f"""Answer the question using ONLY the context below. If the context doesn't contain the answer, say so.

CONTEXT:
{context_text}

QUESTION:
{question}

ANSWER:"""
    response = chat(model=model, messages=[{"role": "user", "content": prompt}], options={"temperature": 0})
    return response["message"]["content"]


@traceable(name="pdf_chat_query", metadata={"task_type": "pdf_qa"})
def answer_question(vectorstore, question, k=4):
    chunks = retrieve(vectorstore, question, k=k)
    answer = generate_answer(question, chunks)
    return {"answer": answer, "context": chunks}


def main():
    print("Loading and indexing PDF...")
    docs = load_pdf(PDF_PATH)
    chunks = chunk_documents(docs)
    vectorstore = build_vectorstore(chunks)
    print(f"Indexed {len(chunks)} chunks from {len(docs)} pages.\n")

    session_id = str(uuid.uuid4())

    while True:
        q = input("\nQuery: ")
        if q == "/exit":
            break
        result = answer_question(
            vectorstore,
            q,
            langsmith_extra={"metadata": {"session_id": session_id}}
        )
        print(f"\n{result['answer']}")


if __name__ == "__main__":
    main()