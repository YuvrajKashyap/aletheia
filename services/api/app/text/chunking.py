from dataclasses import dataclass
import re

from app.text.hashing import content_hash
from app.text.normalization import normalize_text

SCIFACT_CHUNKING_STRATEGY = "scifact_document_v1"
SCIFACT_CHUNKING_VERSION = "1.0"
WINDOW_CHUNKING_STRATEGY = "window_v1"


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    text: str
    token_count: int
    char_start: int | None
    char_end: int | None
    content_hash: str


def approximate_token_count(text: str) -> int:
    return len(re.findall(r"\S+", normalize_text(text)))


def chunk_document_level(text: str) -> list[TextChunk]:
    normalized = normalize_text(text)
    if not normalized:
        return []

    return [
        TextChunk(
            chunk_index=0,
            text=normalized,
            token_count=approximate_token_count(normalized),
            char_start=0,
            # char_end uses normalized-text length because stored chunks use normalized text.
            char_end=len(normalized),
            content_hash=content_hash(normalized),
        )
    ]


def chunk_by_window(text: str, max_tokens: int = 256, overlap_tokens: int = 32) -> list[TextChunk]:
    if max_tokens <= 0:
        raise ValueError("max_tokens must be greater than 0.")
    if overlap_tokens < 0:
        raise ValueError("overlap_tokens must be greater than or equal to 0.")
    if overlap_tokens >= max_tokens:
        raise ValueError("overlap_tokens must be less than max_tokens.")

    normalized = normalize_text(text)
    if not normalized:
        return []

    tokens = re.findall(r"\S+", normalized)
    chunks: list[TextChunk] = []
    step = max_tokens - overlap_tokens
    for start in range(0, len(tokens), step):
        window_tokens = tokens[start : start + max_tokens]
        if not window_tokens:
            break
        chunk_text = " ".join(window_tokens)
        chunks.append(
            TextChunk(
                chunk_index=len(chunks),
                text=chunk_text,
                token_count=len(window_tokens),
                char_start=None,
                char_end=None,
                content_hash=content_hash(chunk_text),
            )
        )
        if start + max_tokens >= len(tokens):
            break

    return chunks
