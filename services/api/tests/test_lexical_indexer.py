from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

from app.indexing import statuses
from app.models.indexing import IndexVersion
from app.search import lexical_indexer
from app.search.lexical_indexer import build_lexical_index_for_version, chunk_to_opensearch_doc, ensure_lexical_index


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


def test_limited_lexical_build_does_not_reduce_index_version_chunk_count(monkeypatch) -> None:
    index_version = SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000010"),
        dataset_id=UUID("00000000-0000-0000-0000-000000000011"),
        lexical_index_name="aletheia-lexical-test",
        chunking_strategy="scifact_document_v1",
        chunking_version="1.0",
        status=statuses.READY,
        document_count=5183,
        chunk_count=5183,
        config_json={},
    )

    class FakeDb:
        index_job = None

        def get(self, model, key):
            assert model is IndexVersion
            assert key == index_version.id
            return index_version

        def add(self, item):
            self.index_job = item

        def commit(self):
            pass

        def refresh(self, item):
            pass

    def fake_chunk_count(db, dataset_id, chunking_strategy=None, chunking_version=None, limit=None):
        return min(5183, limit) if limit is not None else 5183

    monkeypatch.setattr(lexical_indexer, "_chunk_count", fake_chunk_count)
    monkeypatch.setattr(lexical_indexer, "_document_count", lambda db, dataset_id: 5183)
    monkeypatch.setattr(lexical_indexer, "ensure_lexical_index", lambda client, index_name, recreate=False: {})
    monkeypatch.setattr(
        lexical_indexer,
        "bulk_index_chunks",
        lambda *args, **kwargs: {
            "chunks_seen": 10,
            "chunks_indexed": 10,
            "chunks_failed": 0,
            "errors": [],
            "refresh": True,
            "opensearch_count": 5183,
        },
    )

    db = FakeDb()
    result = build_lexical_index_for_version(
        db,
        SimpleNamespace(),
        index_version_id=index_version.id,
        limit=10,
    )

    assert result["chunks_total"] == 10
    assert result["chunks_indexed"] == 10
    assert db.index_job.chunks_total == 10
    assert db.index_job.chunks_completed == 10
    assert index_version.chunk_count == 5183
    assert index_version.document_count == 5183
