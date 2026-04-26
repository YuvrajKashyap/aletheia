import pytest

from app.search import hybrid_retriever
from app.search.retrieval_models import (
    DenseSearchResponse,
    DenseSearchResult,
    LexicalSearchResponse,
    LexicalSearchResult,
)


def bm25_response() -> LexicalSearchResponse:
    return LexicalSearchResponse(
        query="statins",
        index_version_id="version-1",
        index_name="lexical-index",
        top_k=3,
        results=[
            LexicalSearchResult(
                rank=1,
                chunk_id="shared",
                document_id="doc-shared",
                dataset_id="dataset",
                document_external_id="doc-shared-ext",
                chunk_external_id="doc-shared:0",
                title="BM25 shared title",
                text="BM25 shared text",
                score=12.0,
                token_count=4,
                content_hash="hash-shared",
                chunking_strategy="scifact_document_v1",
                chunking_version="1.0",
                metadata_json={"source": "bm25"},
            ),
            LexicalSearchResult(
                rank=2,
                chunk_id="bm25-only",
                document_id="doc-bm25",
                dataset_id="dataset",
                document_external_id="doc-bm25-ext",
                chunk_external_id="doc-bm25:0",
                title="BM25 only title",
                text="BM25 only text",
                score=11.0,
                token_count=4,
                content_hash="hash-bm25",
                chunking_strategy="scifact_document_v1",
                chunking_version="1.0",
                metadata_json={"source": "bm25"},
            ),
        ],
        latency_ms=4.0,
    )


def dense_response() -> DenseSearchResponse:
    return DenseSearchResponse(
        query="statins",
        index_version_id="version-1",
        collection_name="vector-collection",
        top_k=3,
        query_embedding_dimension=384,
        results=[
            DenseSearchResult(
                rank=1,
                chunk_id="dense-only",
                document_id="doc-dense",
                dataset_id="dataset",
                index_version_id="version-1",
                document_external_id="doc-dense-ext",
                chunk_external_id="doc-dense:0",
                title="Dense only title",
                text="Dense only text",
                score=0.9,
                token_count=4,
                content_hash="hash-dense",
                chunking_strategy="scifact_document_v1",
                chunking_version="1.0",
                metadata_json={"source": "dense"},
            ),
            DenseSearchResult(
                rank=2,
                chunk_id="shared",
                document_id="doc-shared",
                dataset_id="dataset",
                index_version_id="version-1",
                document_external_id="doc-shared-ext",
                chunk_external_id="doc-shared:0",
                title="Dense shared title",
                text="Dense shared text",
                score=0.8,
                token_count=4,
                content_hash="hash-shared",
                chunking_strategy="scifact_document_v1",
                chunking_version="1.0",
                metadata_json={"source": "dense"},
            ),
        ],
        latency_ms=8.0,
        embedding_latency_ms=2.0,
        qdrant_latency_ms=3.0,
    )


def test_hybrid_validation_rejects_empty_query() -> None:
    with pytest.raises(hybrid_retriever.InvalidHybridSearchRequestError):
        hybrid_retriever.search_hybrid_from_results("", bm25_response(), dense_response(), top_k=1, rrf_k=60)


def test_hybrid_validation_helpers() -> None:
    with pytest.raises(hybrid_retriever.InvalidHybridSearchRequestError):
        hybrid_retriever._validate_hybrid_search_request("q", 0, 50, 50, 60)
    with pytest.raises(hybrid_retriever.InvalidHybridSearchRequestError):
        hybrid_retriever._validate_hybrid_search_request("q", 10, 5, 50, 60)
    with pytest.raises(hybrid_retriever.InvalidHybridSearchRequestError):
        hybrid_retriever._validate_hybrid_search_request("q", 10, 50, 5, 60)
    with pytest.raises(hybrid_retriever.InvalidHybridSearchRequestError):
        hybrid_retriever._validate_hybrid_search_request("q", 10, 50, 50, 0)


def test_hybrid_calls_bm25_and_dense_with_candidate_counts(monkeypatch) -> None:
    calls = []

    def fake_bm25(db, query, index_version_id=None, top_k=10, candidate_k=None):
        calls.append(("bm25", query, index_version_id, top_k, candidate_k))
        return bm25_response()

    def fake_dense(db, query, index_version_id=None, top_k=10, candidate_k=None):
        calls.append(("dense", query, index_version_id, top_k, candidate_k))
        return dense_response()

    monkeypatch.setattr(hybrid_retriever, "search_bm25", fake_bm25)
    monkeypatch.setattr(hybrid_retriever, "search_dense", fake_dense)

    response = hybrid_retriever.search_hybrid(
        object(),
        " statins ",
        index_version_id="00000000-0000-0000-0000-000000000001",
        top_k=2,
        bm25_candidate_k=7,
        dense_candidate_k=8,
        rrf_k=60,
    )

    assert calls == [
        ("bm25", "statins", "00000000-0000-0000-0000-000000000001", 7, 7),
        ("dense", "statins", "00000000-0000-0000-0000-000000000001", 8, 8),
    ]
    assert response.retrieval_mode == "hybrid"
    assert response.result_count == 2
    assert response.bm25_candidate_k == 7
    assert response.dense_candidate_k == 8


def test_fused_results_preserve_rank_scores_and_metadata() -> None:
    response = hybrid_retriever.search_hybrid_from_results(
        query="statins",
        bm25_response=bm25_response(),
        dense_response=dense_response(),
        top_k=3,
        rrf_k=60,
    )

    shared = next(result for result in response.results if result.chunk_id == "shared")
    dense_only = next(result for result in response.results if result.chunk_id == "dense-only")

    assert shared.rank == 1
    assert shared.fusion_score > 0
    assert shared.bm25_rank == 1
    assert shared.dense_rank == 2
    assert shared.bm25_score == 12.0
    assert shared.dense_score == 0.8
    assert shared.title == "BM25 shared title"
    assert shared.metadata_json == {"source": "bm25"}
    assert dense_only.title == "Dense only title"
    assert response.lexical_index_name == "lexical-index"
    assert response.vector_collection_name == "vector-collection"
