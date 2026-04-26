import re


def normalize_whitespace(text: str) -> str:
    if text is None:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def normalize_text(text: str) -> str:
    return normalize_whitespace(text)
