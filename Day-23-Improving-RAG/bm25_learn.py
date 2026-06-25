from rank_bm25 import BM25Okapi

documents = [
    "I love apples",
    "Apples and oranges are fruit",
    "I love phonse by apple",
    "The sky is green"
]
# we need to tokenize the document first, BM250kapi expects ["Dogs","are","loyal"]

tokenized_docs = [doc.split() for doc in documents]
# print(tokenized_docs)

bm25 = BM25Okapi(tokenized_docs)

query = "a green fruit"
tokenized_query = query.split()

scores = bm25.get_scores(tokenized_query)

# print(scores)
print(f"Your query: {query}")
print("Using BM25: \n")
for doc,score in zip(documents,scores):
    print(f"Score = {score:.4f}")
    print(doc)
    print("-"*50)