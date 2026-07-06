from datasets import Dataset
import json
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from langchain_huggingface import HuggingFaceEmbeddings

#dataset retrival
def get_dataset():
    with open(r"Day-30-Evals/dataset.json","r",encoding="utf-8") as file:
        content = json.load(file)
        return content

golden_dataset = get_dataset()
dataset = Dataset.from_dict({
    "question": [r["question"] for r in golden_dataset],
    "answer": [r["answer"] for r in golden_dataset],
    "contexts": [r["context"] for r in golden_dataset],
    "ground_truth": [r["ground_truth"] for r in golden_dataset],
})

llm = LangchainLLMWrapper(ChatOllama(model="qwen3:8b", temperature=0, extra_body={"think": False}))
embeddings = LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(model_name ="sentence-transformers/all-MiniLM-L6-v2"))
from ragas.run_config import RunConfig

run_config = RunConfig(
    timeout=300,        # allow up to 5 minutes per call
    max_workers=2,       # only 1-2 concurrent requests to Ollama at a time
)

result = evaluate(
    dataset=dataset.select(range(5)),
    metrics=[
        faithfulness, answer_relevancy, context_precision, context_recall
    ],
    llm=llm,
    embeddings=embeddings,
    run_config=run_config,
)
print(result)
df = result.to_pandas()
df.to_csv(r"Day-30-Evals/ragas_eval_results.csv", index = False)