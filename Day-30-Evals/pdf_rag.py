import sys
sys.path.append(r"d:\Projects\ai-engineering")

from rag import RAGConfig, RAGPipeline
from ollama import chat
from rag.utils import strip_think_tags  


config = RAGConfig(
    persist_directory="D:/AI_Data/Day30",
    collection_name="day30-evals",
    use_hyde=True,
    use_multi_query=True,
    use_parent_child=False,
    use_hybrid_search=True,
)

rag = RAGPipeline(config)
rag.load_pdf(r"Day-30-Evals\northwind_handbook.pdf")

while True:
    q = input("\nQuery: ")
    if q == "/exit":
        break
    ans, context = rag.query(q)
    