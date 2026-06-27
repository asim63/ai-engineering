from ollama import chat
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import json
from sentence_transformers import CrossEncoder
from rank_bm25 import BM25Okapi
import os
from collections import defaultdict


embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
persist_directory=r"D:\AI_Data\multi-query"
collection_name = "multi-query"
reranker = CrossEncoder("BAAI/bge-reranker-base")

def retrieve_queries(query):
    response = chat(
        model = "qwen3:8b",
        messages=[{
            "role":"user",
            "content": f""" You are a search query generator.
                Generate exactly 3 alternative search queries.
                Requirements:
                - Preserve the original meaning.
                - Use different wording.
                - Do NOT answer the question.
                - Do NOT explain anything.
                - Return ONLY valid JSON.
                Query:
                {query}
                Example output:
                    "queries":[
                        "...",
                        "...",
                        "..."
                    ]
            """
        }],
    )
    
    queries = json.loads(
        response["message"]["content"])["queries"]
    
    return queries

def chunking(document):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 100,
        chunk_overlap = 10,
        separators=["\n\n","\n",". "," ",""]
    )
    chunks = splitter.split_text(document)
    
    return chunks

def create_or_get_db(chunks):
    db_exists =  os.path.exists(persist_directory) and len(os.listdir(persist_directory)) > 0
    
    if db_exists:
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, collection_name=collection_name)
        return db
    else:
        if not chunks:
            return None
        print("Creating fresh database...")
        return Chroma.from_texts(texts=chunks, embedding=embeddings, persist_directory=persist_directory, collection_name=collection_name)

def retrieve_results(db,query,chunks):
    global BM25
    global true_query
    #vector_results
    vector_results = db.similarity_search_with_score(
        query = query,
        k = 10
    )
    vector_results.sort(
            key = lambda x: x[1],
            reverse=False #returns distance therefore,
        )

    #bm25_results
    tokenized_query = query.lower().split()
    scores = BM25.get_scores(tokenized_query)
    
    bm25_results = list(zip(chunks,scores))
    bm25_results.sort(
        key = lambda x:x[1],
        reverse = True
    )
    final_bm25 = bm25_results[:15]
    
    # RRF
    rrf_scores = defaultdict(float)
    k = 60
    
    #Vector ranking 
    for rank, (doc, _) in enumerate(vector_results, 1):
        text = doc.page_content
        rrf_scores[text] += 1/(k+rank)
    
    #BM25 ranking
    for rank,(doc,_) in enumerate(final_bm25,start = 1):
        rrf_scores[doc] += 1/(k+rank)
    
    
    hybrid_results = sorted(
    rrf_scores.items(),
    key = lambda x:x[1],
    reverse = True
    )
    return hybrid_results[:10]
        
        
documents = [
    "Peterson's solution is a software based mutual exclusion algorithm.",
    
    "A semaphore is a synchronization mechanism used to control access to shared resources.",
    
    "Race conditions occur when multiple processes access shared data concurrently.",
    
    "Deadlock occurs when processes wait indefinitely for resources held by each other.",
    
    "Critical sections are portions of code that access shared resources.",
    
    "Barcelona is a football club from Spain.",
    
    "Lionel Messi played for Barcelona for many years."
]

tokenized_doc = [doc.lower().split() for doc in documents]
BM25 = BM25Okapi(tokenized_doc)
# print(tokenized_doc)
true_query = "Who is the legend who wears blaugrana?"

chunks = documents

db = create_or_get_db(chunks)

queries = retrieve_queries(true_query)
if true_query not in queries:
    queries.append(true_query)
print(queries)
print()
all_results = []

for query in queries:
    results = retrieve_results(db, query, chunks)
    all_results.extend(results)

unique_docs = {}

for doc, _ in all_results:
    unique_docs[doc] = doc

unique_docs = list(unique_docs.values())

print(unique_docs)

# Rerank
pairs = [[true_query,doc] for doc in unique_docs]
scores = reranker.predict(pairs)
reranked = list(zip(unique_docs,scores))
reranked.sort(
    key = lambda x:x[1],
    reverse = True
)

print("\n=== Final Results ===")

for rank, (doc, score) in enumerate(reranked[:3], 1):
    print(f"{rank}. {score:.4f}")
    print(doc)
    print("-"*60)