from types import SimpleNamespace

import pytest

from app.chunking.service import (
    ChunkDocumentsSummary,
    chunk_external_id,
    chunk_metadata,
    chunk_needs_update,
    chunks_for_strategy,
)
from app.text.chunking import SCIFACT_CHUNKING_STRATEGY, TextChunk


def test_chunk_documents_summary_serializes() -> None:
    summary = ChunkDocumentsSummary(
        dataset_id="dataset-1",
        documents_seen=2,
        chunks_created=2,
        dry_run=True,
    )

    payload = summary.to_dict()

    assert payload["dataset_id"] == "dataset-1"
    assert payload["documents_seen"] == 2
    assert payload["chunks_created"] == 2
    assert payload["dry_run"] is True


def test_unknown_strategy_raises_clear_error() -> None:
    with pytest.raises(ValueError, match="Unknown chunking strategy"):
        chunks_for_strategy("unknown", "text")


def test_scifact_strategy_uses_document_level_chunking() -> None:
    chunks = chunks_for_strategy(SCIFACT_CHUNKING_STRATEGY, "one two")

    assert len(chunks) == 1
    assert chunks[0].chunk_index == 0


def test_chunk_external_id_uses_document_external_id_and_index() -> None:
    assert chunk_external_id("doc-1", 2) == "doc-1:2"


def test_chunk_metadata_preserves_parent_document_external_id() -> None:
    document = SimpleNamespace(external_id="doc-1")

    assert chunk_metadata(document, "strategy", "1.0") == {
        "source_document_external_id": "doc-1",
        "strategy": "strategy",
        "version": "1.0",
    }


def test_chunk_needs_update_detects_changed_hash() -> None:
    existing = SimpleNamespace(
        external_id="doc-1:0",
        text="old",
        token_count=1,
        char_start=0,
        char_end=3,
        content_hash="old-hash",
    )
    text_chunk = TextChunk(
        chunk_index=0,
        text="new",
        token_count=1,
        char_start=0,
        char_end=3,
        content_hash="new-hash",
    )

    assert chunk_needs_update(existing, text_chunk, "doc-1:0") is True
