import re

def clean_text(text:str) -> str:
    text = re.sub(r"\s+"," ",text)
    text = re.sub(r"Page \d+","", text)
    return text.strip()

def strip_think_tags(text: str) -> str:
    """Remove <think>...</think> blocks that qwen3 adds."""
    if "<think>" in text:
        text = text[text.rfind("</think>") + 8:].strip()
    return text