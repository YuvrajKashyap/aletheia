import pytest

from app.text.chunking import approximate_token_count, chunk_by_window, chunk_document_level
from app.text.hashing import content_hash
from app.text.normalization import normalize_text, normalize_whitespace


def test_normalize_whitespace_collapses_runs() -> None:
    assert normalize_whitespace("  alpha\t beta\n\n gamma  ") == "alpha beta gamma"


def test_normalize_text_preserves_case() -> None:
    assert normalize_text("BRCA Gene") == "BRCA Gene"


def test_normalize_text_preserves_punctuation_and_numbers() -> None:
    assert normalize_text("IL-6 increased by 12.5% (p<0.05).") == "IL-6 increased by 12.5% (p<0.05)."


def test_content_hash_is_deterministic() -> None:
    assert content_hash("same text") == content_hash("same text")


def test_content_hash_uses_normalized_text() -> None:
    assert content_hash("same   text") == content_hash(" same text\n")


def test_approximate_token_count_for_simple_text() -> None:
    assert approximate_token_count("one two\nthree") == 3


def test_chunk_document_level_returns_one_normalized_chunk() -> None:
    chunks = chunk_document_level("  Alpha\n beta  ")

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0
    assert chunks[0].text == "Alpha beta"
    assert chunks[0].char_start == 0
    assert chunks[0].char_end == len("Alpha beta")
    assert chunks[0].content_hash == content_hash("Alpha beta")


def test_chunk_by_window_creates_multiple_chunks() -> None:
    chunks = chunk_by_window("one two three four five six", max_tokens=3, overlap_tokens=1)

    assert [chunk.text for chunk in chunks] == ["one two three", "three four five", "five six"]


def test_chunk_by_window_validates_overlap() -> None:
    with pytest.raises(ValueError, match="overlap_tokens must be less than max_tokens"):
        chunk_by_window("one two", max_tokens=2, overlap_tokens=2)


def test_chunk_by_window_validates_max_tokens() -> None:
    with pytest.raises(ValueError, match="max_tokens must be greater than 0"):
        chunk_by_window("one two", max_tokens=0)
