import sys
sys.path.append(r"d:\Projects\ai-engineering")

from rag import RAGConfig, RAGPipeline

config = RAGConfig(
    persist_directory="D:/AI_Data/Day25",
    collection_name="day25-test-config",
    use_hyde=True,
    use_multi_query=True,
    use_parent_child=False,
    use_hybrid_search=True,
)

rag = RAGPipeline(config)
rag.load_pdf(r"Day-25-Intro-to-Agents\rag_test.pdf")

while True:
    q = input("\nQuery: ")
    if q == "/exit":
        break
    rag.query(q)