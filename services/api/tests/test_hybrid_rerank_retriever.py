import pytest

from app.search import reranker as search_reranker
from app.search.retrieval_models import HybridSearchResponse, HybridSearchResult, RerankedSearchResult


def hybrid_result(chunk_id: str, rank: int) -> HybridSearchResult:
    return HybridSearchResult(
        rank=rank,
        chunk_id=chunk_id,
        document_id=f"doc-{chunk_id}",
        dataset_id="dataset",
        index_version_id="version",
        document_external_id=f"doc-{chunk_id}",
        chunk_external_id=f"{chunk_id}:0",
        title=f"title {chunk_id}",
        text=f"text {chunk_id}",
        fusion_score=1.0 / rank,
        bm25_rank=rank,
        dense_rank=rank,
        bm25_score=10.0,
        dense_score=0.5,
        token_count=3,
        content_hash=f"hash-{chunk_id}",
        chunking_strategy="scifact_document_v1",
        chunking_version="1.0",
        metadata_json={},
    )


def reranked_result(chunk_id: str, rank: int) -> RerankedSearchResult:
    return RerankedSearchResult(
        rank=rank,
        chunk_id=chunk_id,
        document_id=f"doc-{chunk_id}",
        dataset_id="dataset",
        index_version_id="version",
        document_external_id=f"doc-{chunk_id}",
        chunk_external_id=f"{chunk_id}:0",
        title=f"title {chunk_id}",
        text=f"text {chunk_id}",
        reranker_score=1.0,
        rerank_rank=rank,
        fusion_rank=rank + 1,
        fusion_score=0.01,
        bm25_rank=rank,
        dense_rank=rank,
        bm25_score=10.0,
        dense_score=0.5,
        token_count=3,
        content_hash=f"hash-{chunk_id}",
        chunking_strategy="scifact_document_v1",
        chunking_version="1.0",
        metadata_json={},
    )


def fake_hybrid_response() -> HybridSearchResponse:
    return HybridSearchResponse(
        query="query",
        index_version_id="version",
        lexical_index_name="lexical",
        vector_collection_name="vector",
        top_k=50,
        bm25_candidate_k=50,
        dense_candidate_k=50,
        rrf_k=60,
        result_count=2,
        results=[hybrid_result("a", 1), hybrid_result("b", 2)],
        latency_ms=12.0,
        bm25_latency_ms=4.0,
        dense_latency_ms=5.0,
        fusion_latency_ms=1.0,
        embedding_latency_ms=2.0,
        qdrant_latency_ms=3.0,
    )


def test_search_hybrid_rerank_calls_hybrid_with_hybrid_candidate_k(monkeypatch) -> None:
    calls = []

    def fake_search_hybrid(db, query, index_version_id=None, top_k=10, bm25_candidate_k=50, dense_candidate_k=50, rrf_k=60):
        calls.append(
            {
                "query": query,
                "index_version_id": index_version_id,
                "top_k": top_k,
                "bm25_candidate_k": bm25_candidate_k,
                "dense_candidate_k": dense_candidate_k,
                "rrf_k": rrf_k,
            }
        )
        return fake_hybrid_response()

    def fake_rerank_candidates(query, candidates, rerank_top_n=25, top_k=10):
        return [reranked_result("b", 1)], {
            "reranker_latency_ms": 7.0,
            "scored_count": 2,
            "rerank_top_n": rerank_top_n,
            "model_name": "model",
        }

    monkeypatch.setattr(search_reranker, "search_hybrid", fake_search_hybrid)
    monkeypatch.setattr(search_reranker, "rerank_candidates", fake_rerank_candidates)

    response = search_reranker.search_hybrid_rerank(
        object(),
        " query ",
        index_version_id="version",
        top_k=1,
        bm25_candidate_k=50,
        dense_candidate_k=50,
        hybrid_candidate_k=25,
        rerank_top_n=10,
        rrf_k=60,
    )

    assert calls[0]["top_k"] == 25
    assert response.retrieval_mode == "hybrid_rerank"
    assert response.result_count == 1
    assert response.reranker_latency_ms == 7.0
    assert response.bm25_latency_ms == 4.0
    assert response.dense_latency_ms == 5.0


def test_search_hybrid_rerank_validates_candidate_counts() -> None:
    with pytest.raises(search_reranker.InvalidRerankSearchRequestError):
        search_reranker.search_hybrid_rerank(object(), "query", top_k=5, rerank_top_n=4)
    with pytest.raises(search_reranker.InvalidRerankSearchRequestError):
        search_reranker.search_hybrid_rerank(object(), "query", rerank_top_n=25, hybrid_candidate_k=10)
    with pytest.raises(search_reranker.InvalidRerankSearchRequestError):
        search_reranker.search_hybrid_rerank(object(), "query", bm25_candidate_k=10, hybrid_candidate_k=25)
