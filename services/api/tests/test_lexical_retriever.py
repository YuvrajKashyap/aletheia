from types import SimpleNamespace
from uuid import UUID

import pytest

from app.search import lexical_retriever
from app.search.lexical_retriever import (
    InvalidSearchRequestError,
    NoActiveIndexError,
    search_bm25,
    search_bm25_by_index_name,
)


class FakeOpenSearchClient:
    def __init__(self, total=None):
        self.total = {"value": 42, "relation": "eq"} if total is None else total
        self.calls = []

    def search(self, index, body):
        self.calls.append({"index": index, "body": body})
        return {
            "hits": {
                "total": self.total,
                "hits": [
                    {
                        "_id": "chunk-1",
                        "_score": 12.5,
                        "_source": {
                            "chunk_id": "chunk-1",
                            "document_id": str(UUID("00000000-0000-0000-0000-000000000002")),
                            "dataset_id": str(UUID("00000000-0000-0000-0000-000000000003")),
                            "document_external_id": "doc-1",
                            "chunk_external_id": "doc-1:0",
                            "title": "Aspirin and heart attack risk",
                            "text": "Aspirin may reduce heart attack risk in some populations.",
                            "token_count": 9,
                            "content_hash": "hash-1",
                            "chunking_strategy": "scifact_document_v1",
                            "chunking_version": "1.0",
                            "metadata_json": {"source_document_external_id": "doc-1"},
                        },
                    },
                    {
                        "_id": "chunk-2",
                        "_score": 8.0,
                        "_source": {
                            "chunk_id": "chunk-2",
                            "document_id": "doc-uuid-2",
                            "dataset_id": "dataset-uuid",
                            "document_external_id": "doc-2",
                            "chunk_external_id": "doc-2:0",
                            "title": None,
                            "text": "A second result.",
                            "token_count": None,
                            "content_hash": None,
                            "chunking_strategy": "scifact_document_v1",
                            "chunking_version": "1.0",
                            "metadata_json": None,
                        },
                    },
                ],
            }
        }


def test_empty_query_raises_validation_error() -> None:
    with pytest.raises(InvalidSearchRequestError):
        search_bm25_by_index_name("", "index")


def test_whitespace_only_query_raises_validation_error() -> None:
    with pytest.raises(InvalidSearchRequestError):
        search_bm25_by_index_name("   ", "index")


def test_top_k_validation_works() -> None:
    with pytest.raises(InvalidSearchRequestError):
        search_bm25_by_index_name("aspirin", "index", top_k=0)

    with pytest.raises(InvalidSearchRequestError):
        search_bm25_by_index_name("aspirin", "index", top_k=101)


def test_candidate_k_defaults_to_top_k(monkeypatch) -> None:
    client = FakeOpenSearchClient()
    monkeypatch.setattr(lexical_retriever, "get_opensearch_client", lambda: client)

    search_bm25_by_index_name("aspirin", "test-index", top_k=5)

    assert client.calls[0]["body"]["size"] == 5


def test_candidate_k_cannot_be_less_than_top_k() -> None:
    with pytest.raises(InvalidSearchRequestError):
        search_bm25_by_index_name("aspirin", "index", top_k=10, candidate_k=5)


def test_hit_parsing_maps_opensearch_hits(monkeypatch) -> None:
    client = FakeOpenSearchClient()
    monkeypatch.setattr(lexical_retriever, "get_opensearch_client", lambda: client)

    response = search_bm25_by_index_name("aspirin heart attack", "test-index", top_k=1, candidate_k=2)

    assert response.query == "aspirin heart attack"
    assert response.index_name == "test-index"
    assert response.index_version_id is None
    assert response.retrieval_mode == "bm25"
    assert response.top_k == 1
    assert response.total_hits == 42
    assert response.latency_ms >= 0
    assert len(response.results) == 1
    result = response.results[0]
    assert result.rank == 1
    assert result.score == 12.5
    assert result.chunk_id == "chunk-1"
    assert result.document_external_id == "doc-1"
    assert result.title == "Aspirin and heart attack risk"
    assert result.text.startswith("Aspirin may reduce")
    assert result.token_count == 9
    assert result.content_hash == "hash-1"
    assert result.metadata_json == {"source_document_external_id": "doc-1"}


def test_total_hits_parsing_handles_integer_format(monkeypatch) -> None:
    client = FakeOpenSearchClient(total=7)
    monkeypatch.setattr(lexical_retriever, "get_opensearch_client", lambda: client)

    response = search_bm25_by_index_name("aspirin", "test-index")

    assert response.total_hits == 7


def test_uuid_id_fields_serialize_as_strings(monkeypatch) -> None:
    client = FakeOpenSearchClient()
    monkeypatch.setattr(lexical_retriever, "get_opensearch_client", lambda: client)

    response = search_bm25_by_index_name("aspirin", "test-index")
    payload = response.to_dict()

    assert isinstance(payload["results"][0]["document_id"], str)
    assert isinstance(payload["results"][0]["dataset_id"], str)
    assert payload["results"][0]["metadata_json"] == {"source_document_external_id": "doc-1"}
    assert payload["results"][1]["metadata_json"] == {}


class FakeReadOnlyDb:
    def __init__(self, index_version=None):
        self.index_version = index_version

    def get(self, model, object_id):
        return self.index_version

    def scalar(self, statement):
        return self.index_version

    def add(self, value):
        raise AssertionError("BM25 retrieval must not write to the database.")

    def commit(self):
        raise AssertionError("BM25 retrieval must not write to the database.")

    def flush(self):
        raise AssertionError("BM25 retrieval must not write to the database.")


def test_search_bm25_uses_index_version_without_db_writes(monkeypatch) -> None:
    client = FakeOpenSearchClient()
    monkeypatch.setattr(lexical_retriever, "get_opensearch_client", lambda: client)
    index_version = SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        lexical_index_name="test-index",
    )
    db = FakeReadOnlyDb(index_version)

    response = search_bm25(
        db,
        "aspirin",
        index_version_id=index_version.id,
        top_k=1,
    )

    assert response.index_version_id == str(index_version.id)
    assert response.index_name == "test-index"
    assert response.results[0].rank == 1


def test_search_bm25_without_active_index_raises(monkeypatch) -> None:
    client = FakeOpenSearchClient()
    monkeypatch.setattr(lexical_retriever, "get_opensearch_client", lambda: client)
    db = FakeReadOnlyDb(index_version=None)

    with pytest.raises(NoActiveIndexError):
        search_bm25(db, "aspirin")
