import sys
sys.path.append(r"d:\Projects\ai-engineering")

from rag import RAGConfig, RAGPipeline
from ollama import chat
import json
from rag.utils import strip_think_tags   # you already have this

def extract_claims(answer: str, model: str) -> list[str]:
    """Break an answer into individual atomic factual claims."""
    response = chat(
        model=model,
        messages=[{
            "role": "user",
            "content": f"""Break the following answer into individual atomic factual claims.
            Each claim should be a single, standalone fact. Return ONLY valid JSON, no explanation.

            Answer: {answer}

            {{"claims": ["...", "..."]}}"""
        }]
    )
    raw = strip_think_tags(response["message"]["content"])
    try:
        return json.loads(raw)["claims"]
    except Exception:
        return [answer]  # fallback: treat whole answer as one claim


def check_faithfulness(claims: list[str], context: str, model: str) -> dict:
    """For each claim, ask the judge whether it's supported by the context."""
    results = []
    for claim in claims:
        response = chat(
            model=model,
            messages=[{
                "role": "user",
                "content": f"""Context:
                {context}

                Claim: {claim}

                Is this claim directly supported by the context above? Answer with exactly one word: YES or NO."""
            }]
        )
        verdict = strip_think_tags(response["message"]["content"]).strip().upper()
        supported = verdict.startswith("YES")
        results.append({"claim": claim, "supported": supported})

    score = sum(r["supported"] for r in results) / len(results) if results else 0
    return {"score": score, "details": results}


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
    

    claims = extract_claims(ans, model="qwen3:8b")
    result = check_faithfulness(claims, context, model="qwen3:8b")

    print(result["score"])
    for d in result["details"]:
        print(d["supported"], "-", d["claim"])