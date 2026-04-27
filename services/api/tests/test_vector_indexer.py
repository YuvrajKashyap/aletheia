from types import SimpleNamespace
from uuid import UUID

import pytest

from app.search import vector_indexer
from app.search.vector_indexer import (
    build_vector_index_for_version,
    chunk_to_qdrant_payload,
    ensure_vector_collection,
    get_collection_vector_count,
)


def fake_objects():
    dataset = SimpleNamespace(id=UUID("00000000-0000-0000-0000-000000000001"))
    document = SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        external_id="doc-1",
        title="Title",
    )
    chunk = SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000003"),
        external_id="doc-1:0",
        chunk_index=0,
        text="Chunk text",
        token_count=2,
        content_hash="hash",
        chunking_strategy="scifact_document_v1",
        chunking_version="1.0",
        metadata_json={"source": "test"},
    )
    index_version = SimpleNamespace(id=UUID("00000000-0000-0000-0000-000000000004"))
    return chunk, document, dataset, index_version


def test_chunk_to_qdrant_payload_serializes_expected_metadata() -> None:
    chunk, document, dataset, index_version = fake_objects()

    payload = chunk_to_qdrant_payload(chunk, document, dataset, index_version)

    assert payload["chunk_id"] == str(chunk.id)
    assert payload["document_id"] == str(document.id)
    assert payload["dataset_id"] == str(dataset.id)
    assert payload["index_version_id"] == str(index_version.id)
    assert payload["document_external_id"] == "doc-1"
    assert payload["chunk_external_id"] == "doc-1:0"
    assert payload["text"] == "Chunk text"
    assert payload["metadata_json"] == {"source": "test"}


def test_ensure_vector_collection_keeps_existing_collection() -> None:
    calls = []

    class FakeClient:
        def collection_exists(self, collection_name):
            return True

        def delete_collection(self, collection_name):
            calls.append(("delete", collection_name))

        def create_collection(self, collection_name, vectors_config):
            calls.append(("create", collection_name, vectors_config))

    result = ensure_vector_collection(FakeClient(), "collection", 384, recreate=False)

    assert result["existed"] is True
    assert result["created"] is False
    assert calls == []


def test_ensure_vector_collection_recreates_existing_collection() -> None:
    calls = []

    class FakeClient:
        def collection_exists(self, collection_name):
            return True

        def delete_collection(self, collection_name):
            calls.append(("delete", collection_name))

        def create_collection(self, collection_name, vectors_config):
            calls.append(("create", collection_name, vectors_config))

    result = ensure_vector_collection(FakeClient(), "collection", 384, recreate=True)

    assert result["created"] is True
    assert result["recreated"] is True
    assert calls[0] == ("delete", "collection")
    assert calls[1][0] == "create"


def test_ensure_vector_collection_rejects_unknown_distance() -> None:
    class FakeClient:
        def collection_exists(self, collection_name):
            return False

    with pytest.raises(ValueError):
        ensure_vector_collection(FakeClient(), "collection", 384, distance="bad")


def test_upsert_batch_uses_deterministic_point_ids_and_payloads() -> None:
    chunk, document, dataset, index_version = fake_objects()
    upserts = []

    class FakeClient:
        def upsert(self, collection_name, points):
            upserts.append((collection_name, points))

    count = vector_indexer._upsert_batch(
        FakeClient(),
        "collection",
        [(chunk, document, dataset)],
        [[0.1, 0.2, 0.3]],
        index_version,
    )

    assert count == 1
    collection_name, points = upserts[0]
    assert collection_name == "collection"
    assert points[0].id == str(chunk.id)
    assert points[0].vector == [0.1, 0.2, 0.3]
    assert points[0].payload["chunk_id"] == str(chunk.id)


def test_get_collection_vector_count_reads_qdrant_count() -> None:
    class FakeClient:
        def count(self, collection_name, exact=True):
            return SimpleNamespace(count=5183)

    assert get_collection_vector_count(FakeClient(), "collection") == 5183


def test_limited_vector_build_does_not_reduce_index_version_vector_count(monkeypatch) -> None:
    index_version = SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000010"),
        dataset_id=UUID("00000000-0000-0000-0000-000000000011"),
        vector_collection_name="aletheia-vector-test",
        chunking_strategy="scifact_document_v1",
        chunking_version="1.0",
        embedding_model="BAAI/bge-small-en-v1.5",
        embedding_dimension=384,
        status="ready",
        vector_count=5183,
        config_json={},
    )
    rows = [fake_objects()[:3] for _ in range(10)]

    class FakeDb:
        index_job = None

        def get(self, model, key):
            return index_version

        def add(self, item):
            self.index_job = item

        def commit(self):
            pass

        def refresh(self, item):
            pass

    monkeypatch.setattr(
        vector_indexer,
        "_chunk_count",
        lambda db, dataset_id, chunking_strategy, chunking_version, limit: min(5183, limit) if limit is not None else 5183,
    )
    monkeypatch.setattr(vector_indexer, "get_qdrant_client", lambda: SimpleNamespace())
    monkeypatch.setattr(vector_indexer, "ensure_vector_collection", lambda *args, **kwargs: {})
    monkeypatch.setattr(vector_indexer, "iter_chunks_for_vector_indexing", lambda *args, **kwargs: iter(rows))
    monkeypatch.setattr(
        vector_indexer,
        "embed_texts",
        lambda texts, model_name, batch_size: [[0.1, 0.2, 0.3] for _ in texts],
    )
    monkeypatch.setattr(vector_indexer, "_upsert_batch", lambda client, collection_name, batch, vectors, index_version: len(batch))
    monkeypatch.setattr(vector_indexer, "get_collection_vector_count", lambda client, collection_name: 10)

    db = FakeDb()
    result = build_vector_index_for_version(db, index_version.id, limit=10, batch_size=4)

    assert result["chunks_total"] == 10
    assert result["vectors_upserted"] == 10
    assert result["qdrant_count"] == 10
    assert db.index_job.chunks_total == 10
    assert db.index_job.chunks_completed == 10
    assert index_version.vector_count == 5183
