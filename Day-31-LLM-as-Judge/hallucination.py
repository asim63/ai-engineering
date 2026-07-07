from ollama import chat

def llm_chat(prompt):
    stream = chat(
        model="qwen3:8b",
        messages=[{
            "role":"user",
            "content":prompt
        }],
        stream=True,
        think=False,
        options={"temperature": 0}
    )
    full = ""
    for chunks in stream:
        piece = chunks['message']['content']
        print(piece, end="", flush= True )
        full += piece
    return full

HALLUCINATION_PROMPT = """
You are an expert hallucinate analyser. Determine if the CLAIM is fully supported by SOURCE TEXT.

SOURCE TEXT:{source}
CLAIN:{claim}

Instructions:
- ONLY use the source text - do not use outside/world knowledge.
- Mark as "SUPPORTED" only if every part of the claim is explicitly backed by the source.
- Mark as "UNSUPPORTED" if any part is not stated in the source, is an inference beyond what is stated, or contradicts etc.

Respond in this format:
Unsupported parts: <quote the specific phrase(s) not backed by source, or "none">
Verdict: <SUPPORTED or UNSUPPORTED>
"""

def check_hallucination(source, claim):
    prompt = HALLUCINATION_PROMPT.format(source= source, claim=claim)
    result = llm_chat(prompt)
    verdict = "UNSUPPORTED" if "UNSUPPORTED" in result.split("Verdict:")[-1] else "SUPPORTED"
    return {"raw":result, "verdict":verdict}

def hallucination_rate(source, generated_answer):
    claims = [s.strip() for s in generated_answer.split(".") if s.strip()]
    results = [check_hallucination(source, c) for c in claims]
    unsupported = [r for r in results if r["verdict"] == "UNSUPPORTED"]
    rate = len(unsupported) / len(claims) if claims else 0
    return {"rate": rate, "unsupported_claims": unsupported, "total_claims": len(claims)}



source = "The company reported Q3 revenue of $2.1 billion, up 12% year-over-year. It did not provide guidance for Q4."
answer = "The company's Q3 revenue was $2.1 billion, a 12% increase. It expects Q4 revenue to grow further."

print(hallucination_rate(source, answer))