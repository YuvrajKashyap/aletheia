import pytest

from app.search import reranker as search_reranker
from app.search.retrieval_models import HybridSearchResult


def hybrid_candidate(chunk_id: str, rank: int, text: str = "text") -> HybridSearchResult:
    return HybridSearchResult(
        rank=rank,
        chunk_id=chunk_id,
        document_id=f"doc-{chunk_id}",
        dataset_id="dataset",
        index_version_id="version",
        document_external_id=f"doc-{chunk_id}",
        chunk_external_id=f"{chunk_id}:0",
        title=f"title {chunk_id}",
        text=text,
        fusion_score=1.0 / rank,
        bm25_rank=rank,
        dense_rank=rank + 1,
        bm25_score=10.0 - rank,
        dense_score=1.0 - (rank / 100.0),
        token_count=4,
        content_hash=f"hash-{chunk_id}",
        chunking_strategy="scifact_document_v1",
        chunking_version="1.0",
        metadata_json={"chunk": chunk_id},
    )


def test_rerank_candidates_assigns_ranks_and_orders_by_score(monkeypatch) -> None:
    monkeypatch.setattr(
        search_reranker,
        "score_query_documents",
        lambda query, documents, batch_size=None: [0.1, 0.9, 0.2],
    )
    candidates = [hybrid_candidate("a", 1), hybrid_candidate("b", 2), hybrid_candidate("c", 3)]

    results, metadata = search_reranker.rerank_candidates("query", candidates, rerank_top_n=3, top_k=2)

    assert [result.chunk_id for result in results] == ["b", "c"]
    assert [result.rank for result in results] == [1, 2]
    assert [result.rerank_rank for result in results] == [1, 2]
    assert results[0].reranker_score == 0.9
    assert results[0].fusion_rank == 2
    assert results[0].bm25_rank == 2
    assert results[0].dense_rank == 3
    assert results[0].metadata_json == {"chunk": "b"}
    assert metadata["scored_count"] == 3
    assert "reranker_latency_ms" in metadata


def test_rerank_tie_breaks_by_fusion_rank_then_chunk_id(monkeypatch) -> None:
    monkeypatch.setattr(
        search_reranker,
        "score_query_documents",
        lambda query, documents, batch_size=None: [1.0, 1.0, 1.0],
    )
    candidates = [hybrid_candidate("c", 2), hybrid_candidate("b", 1), hybrid_candidate("a", 2)]

    results, _metadata = search_reranker.rerank_candidates("query", candidates, rerank_top_n=3, top_k=3)

    assert [result.chunk_id for result in results] == ["b", "a", "c"]


def test_rerank_top_n_must_cover_top_k() -> None:
    with pytest.raises(search_reranker.InvalidRerankSearchRequestError):
        search_reranker.rerank_candidates("query", [hybrid_candidate("a", 1)], rerank_top_n=1, top_k=2)


def test_no_evaluation_metrics_are_produced(monkeypatch) -> None:
    monkeypatch.setattr(search_reranker, "score_query_documents", lambda query, documents, batch_size=None: [1.0])

    _results, metadata = search_reranker.rerank_candidates(
        "query",
        [hybrid_candidate("a", 1)],
        rerank_top_n=1,
        top_k=1,
    )

    assert "recall_at_10" not in metadata
    assert "mrr_at_10" not in metadata
