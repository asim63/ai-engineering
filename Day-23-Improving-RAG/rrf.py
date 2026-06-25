from rank_bm25 import BM25Okapi
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from collections import defaultdict

documents = [
    "Peterson's solution is a software based mutual exclusion algorithm.",
    
    "A semaphore is a synchronization mechanism used to control access to shared resources.",
    
    "Race conditions occur when multiple processes access shared data concurrently.",
    
    "Deadlock occurs when processes wait indefinitely for resources held by each other.",
    
    "Critical sections are portions of code that access shared resources.",
    
    "Barcelona is a football club from Spain.",
    
    "Lionel Messi played for Barcelona for many years."
]
chunks = [chunk for chunk in documents]
embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
# db = Chroma.from_texts(
#     texts=chunks,
#     embedding=embeddings,
#     persist_directory=r"D:\AI_Data\hybrid"
# )
query = "What is Peterson's solution?"
db = Chroma(
    persist_directory=r"D:\AI_Data\hybrid",
    embedding_function=embeddings
)
results = db.similarity_search_with_score(
    query=query,
    k = len(documents)
)
vector_result = []
for doc, score in results:
    text = doc.page_content
    vector_result.append((text,score))

vector_result.sort(
    key = lambda x: x[1],
    reverse=False
)
print("\n"+"-"*50 + "Vector Results" + "-"*50)
for rank, (doc, score) in enumerate(vector_result, 1):
    print(f"{rank}. Similarity={score:.4f} | {doc}")


tokenized_docs = [doc.split() for doc in documents]
bm25 = BM25Okapi(tokenized_docs)
tokenized_query = query.split()
scores = bm25.get_scores(tokenized_query)


result = list(zip(chunks,scores))
result.sort(
    key = lambda x:x[1],
    reverse = True
)
print("\n"+"-"*50 + "BM25 Results" + "-"*50)
for rank, (doc, score) in enumerate(result, 1):
    print(f"{rank}. Similarity={score:.4f} | {doc}")


rrf_scores = defaultdict(float)
k = 60

#Vector ranking 
for rank,(doc,_) in enumerate(vector_result,start = 1):
    rrf_scores[doc] += 1/(k+rank)
    
#BM25 ranking
for rank,(doc,_) in enumerate(result,start = 1):
    rrf_scores[doc] += 1/(k+rank)
    
hybrid_results = sorted(
    rrf_scores.items(),
    key = lambda x:x[1],
    reverse = True
    )

print("\n"+"-"*50 + "Hybrid Results" + "-"*50)
for rank, (doc, score) in enumerate(hybrid_results, 1):
    print(f"{rank}. RRF Score={score:.4f} | {doc}")
