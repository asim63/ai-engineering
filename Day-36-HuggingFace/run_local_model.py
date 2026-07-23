from transformers import pipeline

# Downloads model+tokenizer automatically on first run, caches locally
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

result = classifier("I absolutely love learning about Hugging Face!")
print(result)
# [{'label': 'POSITIVE', 'score': 0.9998}]

# Batch input
results = classifier([
    "This tutorial is confusing.",
    "This is the best AI roadmap ever."
])
print(results)