from ollama import chat
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import re 
import json,os
from sentence_transformers import CrossEncoder

collection_name = "HyDE-RAG-Test"
persist_directory=r"D:\AI_Data\HyDE"
embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
loader = PyPDFLoader(r"Day-24-Advance-RAG-Patterns\rag_test.pdf")
reranker = CrossEncoder("BAAI/bge-reranker-base")

def clean_text(text):
    text = re.sub(r"\s+"," ", text)
    text = re.sub(r"Page /d+","", text)
    return text.strip()

def create_or_get_db(chunks):
    db_exists =  os.path.exists(persist_directory) and len(os.listdir(persist_directory)) > 0
    
    if db_exists:
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, collection_name=collection_name)
        return db
    else:
        if not chunks:
            return None
        print("Creating fresh database...")
        return Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=persist_directory, collection_name=collection_name)  

def retrieve_result(db,query):

    results = db.similarity_search_with_score(
        query = query,
        k = 10
    )
    pairs = [[query,doc.page_content] for doc,_ in results]
    rerank_scores = reranker.predict(pairs)
    reranked_docs = [(results[i][0], float(rerank_scores[i])) for i in range(len(results))]
    reranked_docs.sort(
        key = lambda x:x[1],
        reverse = True
    )
    return reranked_docs[:3]

def hyde_result(query):
    response = chat(
        model="qwen3:8b",
        messages=[{
            "role":"user",
            "content": f"""Write a short factual paragraph that directly answers this question.
            Do not mention that you are generating a hypothetical answer.
            Just write the answer as if you found it in a document.

            Question: {query}
            Answer:
            """
        }]
    )
    return response["message"]["content"]



document = loader.load()

for doc in document:
    doc.page_content = clean_text(doc.page_content)

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 400,
    chunk_overlap = 40,
    separators = ["\n\n","\n",". "," ",""]
)
chunks = splitter.split_documents(document)

# for i,chunk in enumerate(chunks,start=1):
#     print(f"Chunk {i}")
#     print(f"{chunk}")

db = create_or_get_db(chunks)
while True:
    true_query = input("Enter your query:")
    if true_query == "/exit": break
    
    hyde_answer = hyde_result(true_query)
    print("-"*30+ "Hyde Answer "+ "-"*30)
    
    print(hyde_answer)
    print("-"*30+ "Response for query: "+ "-"*30)
    result1 =  retrieve_result(db,true_query)
    for rank, (doc, score) in enumerate(result1, 1):
        print(f"{rank}. {score:.4f}")
        print(doc.page_content)
        print("-"*60)
    
    
    print("-"*30+ "Response for HyDE : "+ "-"*30)
    result2 =  retrieve_result(db,hyde_answer)
    for rank, (doc, score) in enumerate(result2, 1):
        print(f"{rank}. {score:.4f}")
        print(doc.page_content)
        print("-"*60)