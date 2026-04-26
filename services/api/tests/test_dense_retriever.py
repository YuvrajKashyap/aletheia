from types import SimpleNamespace

import pytest

from app.search import dense_retriever


class FakeQdrantClient:
    def __init__(self):
        self.calls = []

    def query_points(self, collection_name, query, limit, with_payload):
        self.calls.append(
            {
                "collection_name": collection_name,
                "query": query,
                "limit": limit,
                "with_payload": with_payload,
            }
        )
        return SimpleNamespace(
            points=[
                SimpleNamespace(
                    id="point-1",
                    score=0.91,
                    payload={
                        "chunk_id": "00000000-0000-0000-0000-000000000001",
                        "document_id": "00000000-0000-0000-0000-000000000002",
                        "dataset_id": "00000000-0000-0000-0000-000000000003",
                        "index_version_id": "00000000-0000-0000-0000-000000000004",
                        "document_external_id": "doc-1",
                        "chunk_external_id": "doc-1:0",
                        "title": "Dense result",
                        "text": "Dense retrieval result text.",
                        "token_count": 4,
                        "content_hash": "hash",
                        "chunking_strategy": "scifact_document_v1",
                        "chunking_version": "1.0",
                        "metadata_json": {"source_document_external_id": "doc-1"},
                    },
                )
            ]
        )


def test_empty_query_rejected() -> None:
    with pytest.raises(dense_retriever.InvalidDenseSearchRequestError):
        dense_retriever.search_dense_by_collection_name("", "collection")


def test_top_k_validation() -> None:
    with pytest.raises(dense_retriever.InvalidDenseSearchRequestError):
        dense_retriever.search_dense_by_collection_name("query", "collection", top_k=0)


def test_candidate_k_validation() -> None:
    with pytest.raises(dense_retriever.InvalidDenseSearchRequestError):
        dense_retriever.search_dense_by_collection_name(
            "query",
            "collection",
            top_k=10,
            candidate_k=5,
        )


def test_dense_search_embeds_query_and_maps_qdrant_hits(monkeypatch) -> None:
    fake_client = FakeQdrantClient()
    embed_calls = []

    def fake_embed_text(text, model_name=None):
        embed_calls.append({"text": text, "model_name": model_name})
        return [0.1, 0.2, 0.3]

    monkeypatch.setattr(dense_retriever, "embed_text", fake_embed_text)
    monkeypatch.setattr(dense_retriever, "get_qdrant_client", lambda: fake_client)

    response = dense_retriever.search_dense_by_collection_name(
        " dense query ",
        "qdrant-collection",
        top_k=1,
        candidate_k=7,
        model_name="test-model",
    )

    assert embed_calls == [{"text": "dense query", "model_name": "test-model"}]
    assert fake_client.calls == [
        {
            "collection_name": "qdrant-collection",
            "query": [0.1, 0.2, 0.3],
            "limit": 7,
            "with_payload": True,
        }
    ]
    assert response.retrieval_mode == "dense"
    assert response.collection_name == "qdrant-collection"
    assert response.query_embedding_dimension == 3
    assert response.total_hits == 1
    assert response.embedding_latency_ms is not None
    assert response.qdrant_latency_ms is not None
    assert response.latency_ms >= 0
    assert response.results[0].rank == 1
    assert response.results[0].score == 0.91
    assert response.results[0].chunk_id == "00000000-0000-0000-0000-000000000001"
    assert response.results[0].document_id == "00000000-0000-0000-0000-000000000002"
    assert response.results[0].title == "Dense result"
    assert response.results[0].metadata_json == {"source_document_external_id": "doc-1"}
