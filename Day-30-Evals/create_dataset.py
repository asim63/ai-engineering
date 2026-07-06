# from ragas.llms import LangchainLLMWrapper
# from ragas.embeddings import LangchainEmbeddingsWrapper
# from langchain_ollama import ChatOllama
# from langchain_huggingface import HuggingFaceEmbeddings

# ragas_llm = LangchainLLMWrapper(ChatOllama(model="qwen3:8b"))

# ragas_embeddings = LangchainEmbeddingsWrapper(
#     HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")
# )
import sys
sys.path.append(r"d:\Projects\ai-engineering")
import json
from rag import RAGConfig, RAGPipeline

config = RAGConfig(
    persist_directory="D:/AI_Data/Day30",
    collection_name="day30-evals",
    use_hyde=False,
    use_multi_query=True,
    use_parent_child=False,
    use_hybrid_search=True,
)
rag = RAGPipeline(config)
rag.load_pdf(r"Day-30-Evals\northwind_handbook.pdf")

results = []
with open(r"Day-30-Evals\golden_dat.json", "r", encoding="utf-8") as file:
    dataset = json.load(file)
for data in dataset: 
    q = data["question"]
    ans, context = rag.query(q)
    results.append({
        "question":data["question"],
        "answer": ans,
        "context":context,
        "ground_truth": data["ground_truth"]
    })
  
with open(r"Day-30-Evals\dataset.json","w",encoding="utf-8") as file:
    json.dump(results, file, ensure_ascii=False, indent=2)