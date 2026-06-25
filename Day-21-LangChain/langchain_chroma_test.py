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

# db = Chroma.from_texts(
#     texts=chunks,
#     embedding=embeddings,
#     persist_directory=r"D:\AI_Data\lang_chain_chroma"
# )
db = Chroma(
        persist_directory=r"D:\AI_Data\lang_chain_chroma",
        embedding_function=embeddings,
    )

results = db.similarity_search_with_score(
    "How do embeddings work?",
    k=3
)
print(results)
for doc,score in results:
    print(score)
    print(doc.page_content)