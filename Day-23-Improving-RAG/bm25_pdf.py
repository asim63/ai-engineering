from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi
import re

loader = PyPDFLoader(r"Day-23-Improving-RAG\try2.pdf")
documents = loader.load()

def clean(text):
    text = re.sub(r"\s+"," ",text)
    text = re.sub(r"Page \d+","",text)
    return text.strip()

for doc in documents:
    doc.page_content = clean(doc.page_content)
    

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200, 
    chunk_overlap=20, 
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.split_documents(documents)
chunks =  [c for c in chunks if len(c.page_content.strip()) >= 100 and len(c.page_content.split()) >= 20]

tokenized_docs = []
for chunk in chunks:
    tokenized_docs.append(
        chunk.page_content.split()
    )
# print(tokenized_docs)
bm25 = BM25Okapi(tokenized_docs)
query = "Neural Information"
tokenized_query = query.split()

scores = bm25.get_scores(tokenized_query)
print(scores)

scores = bm25.get_scores(tokenized_query)

result = list(zip(chunks,scores))
result.sort(
    key = lambda x:x[1],
    reverse = True
)

print(f"Your query: {query}\n\n")
for chunk, score in result[:5]:
    print(f"Score: {score:.4f}")
    # print(chunk.metadata)
    print(chunk.page_content[:200])
    print("-" * 50)