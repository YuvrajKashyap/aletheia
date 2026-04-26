from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

from app.search.lexical_indexer import chunk_to_opensearch_doc, ensure_lexical_index


def test_chunk_to_opensearch_doc_serializes_required_fields() -> None:
    created_at = datetime(2026, 4, 25, tzinfo=timezone.utc)
    dataset = SimpleNamespace(id=UUID("00000000-0000-0000-0000-000000000001"))
    document = SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        external_id="doc-1",
        title="A SciFact Title",
    )
    chunk = SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000003"),
        external_id="doc-1:0",
        chunk_index=0,
        text="Chunk text",
        token_count=2,
        content_hash="abc123",
        chunking_strategy="scifact_document_v1",
        chunking_version="1.0",
        metadata_json={"source_document_external_id": "doc-1"},
        created_at=created_at,
    )

    payload = chunk_to_opensearch_doc(chunk, document, dataset)

    assert payload["chunk_id"] == str(chunk.id)
    assert payload["document_id"] == str(document.id)
    assert payload["dataset_id"] == str(dataset.id)
    assert payload["document_external_id"] == "doc-1"
    assert payload["chunk_external_id"] == "doc-1:0"
    assert payload["title"] == "A SciFact Title"
    assert payload["text"] == "Chunk text"
    assert payload["token_count"] == 2
    assert payload["content_hash"] == "abc123"
    assert payload["metadata_json"] == {"source_document_external_id": "doc-1"}
    assert payload["created_at"] == created_at.isoformat()


def test_chunk_to_opensearch_doc_handles_empty_metadata() -> None:
    dataset = SimpleNamespace(id=UUID("00000000-0000-0000-0000-000000000001"))
    document = SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        external_id="doc-1",
        title=None,
    )
    chunk = SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000003"),
        external_id=None,
        chunk_index=0,
        text="Chunk text",
        token_count=None,
        content_hash="abc123",
        chunking_strategy="scifact_document_v1",
        chunking_version="1.0",
        metadata_json=None,
        created_at=None,
    )

    payload = chunk_to_opensearch_doc(chunk, document, dataset)

    assert payload["metadata_json"] == {}
    assert payload["title"] is None
    assert payload["created_at"] is None


def test_ensure_lexical_index_keeps_existing_index_without_recreate() -> None:
    calls = []

    class FakeIndices:
        def exists(self, index):
            return True

        def delete(self, index):
            calls.append(("delete", index))

        def create(self, index, body):
            calls.append(("create", index, body))

    client = SimpleNamespace(indices=FakeIndices())

    result = ensure_lexical_index(client, "aletheia-lexical-test", recreate=False)

    assert result == {
        "index_name": "aletheia-lexical-test",
        "created": False,
        "recreated": False,
    }
    assert calls == []


def test_ensure_lexical_index_recreates_existing_index() -> None:
    calls = []

    class FakeIndices:
        def exists(self, index):
            return True

        def delete(self, index):
            calls.append(("delete", index))

        def create(self, index, body):
            calls.append(("create", index, body))

    client = SimpleNamespace(indices=FakeIndices())

    result = ensure_lexical_index(client, "aletheia-lexical-test", recreate=True)

    assert result["created"] is True
    assert result["recreated"] is True
    assert calls[0] == ("delete", "aletheia-lexical-test")
    assert calls[1][0] == "create"
