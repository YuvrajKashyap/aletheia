from hashlib import sha256

from app.text.normalization import normalize_text


def content_hash(text: str) -> str:
    """Return a SHA-256 hex digest of the conservatively normalized text."""
    return sha256(normalize_text(text).encode("utf-8")).hexdigest()
