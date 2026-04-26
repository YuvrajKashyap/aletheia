from __future__ import annotations

from time import perf_counter
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.ml.reranker import score_query_documents
from app.search.hybrid_retriever import search_hybrid
from app.search.retrieval_models import (
    HybridSearchResult,
    RerankedSearchResponse,
    RerankedSearchResult,
)


class RerankSearchError(RuntimeError):
    pass


class InvalidRerankSearchRequestError(ValueError):
    pass


def _validate_rerank_request(
    query: str,
    top_k: int,
    rerank_top_n: int,
) -> str:
    normalized_query = query.strip()
    if not normalized_query:
        raise InvalidRerankSearchRequestError("Reranker query must not be empty.")
    if top_k < 1 or top_k > 100:
        raise InvalidRerankSearchRequestError("top_k must be between 1 and 100.")
    if rerank_top_n < top_k:
        raise InvalidRerankSearchRequestError("rerank_top_n must be greater than or equal to top_k.")
    return normalized_query


def _validate_hybrid_rerank_request(
    query: str,
    top_k: int,
    bm25_candidate_k: int,
    dense_candidate_k: int,
    hybrid_candidate_k: int,
    rerank_top_n: int,
    rrf_k: int,
) -> str:
    normalized_query = _validate_rerank_request(query, top_k, rerank_top_n)
    if hybrid_candidate_k < rerank_top_n:
        raise InvalidRerankSearchRequestError(
            "hybrid_candidate_k must be greater than or equal to rerank_top_n."
        )
    if bm25_candidate_k < hybrid_candidate_k:
        raise InvalidRerankSearchRequestError(
            "bm25_candidate_k must be greater than or equal to hybrid_candidate_k."
        )
    if dense_candidate_k < hybrid_candidate_k:
        raise InvalidRerankSearchRequestError(
            "dense_candidate_k must be greater than or equal to hybrid_candidate_k."
        )
    if rrf_k <= 0:
        raise InvalidRerankSearchRequestError("rrf_k must be greater than 0.")
    return normalized_query


def _reranked_result_from_hybrid(
    candidate: HybridSearchResult,
    reranker_score: float,
    rerank_rank: int,
    final_rank: int,
) -> RerankedSearchResult:
    return RerankedSearchResult(
        rank=final_rank,
        chunk_id=candidate.chunk_id,
        document_id=candidate.document_id,
        dataset_id=candidate.dataset_id,
        index_version_id=candidate.index_version_id,
        document_external_id=candidate.document_external_id,
        chunk_external_id=candidate.chunk_external_id,
        title=candidate.title,
        text=candidate.text,
        reranker_score=reranker_score,
        rerank_rank=rerank_rank,
        fusion_rank=candidate.rank,
        fusion_score=candidate.fusion_score,
        bm25_rank=candidate.bm25_rank,
        dense_rank=candidate.dense_rank,
        bm25_score=candidate.bm25_score,
        dense_score=candidate.dense_score,
        token_count=candidate.token_count,
        content_hash=candidate.content_hash,
        chunking_strategy=candidate.chunking_strategy,
        chunking_version=candidate.chunking_version,
        metadata_json=dict(candidate.metadata_json or {}),
    )


def rerank_candidates(
    query: str,
    candidates: list[HybridSearchResult],
    rerank_top_n: int = 25,
    top_k: int = 10,
) -> tuple[list[RerankedSearchResult], dict]:
    settings = get_settings()
    normalized_query = _validate_rerank_request(query, top_k, rerank_top_n)
    candidates_to_score = candidates[:rerank_top_n]
    started = perf_counter()
    if not candidates_to_score:
        return [], {
            "rerank_top_n": rerank_top_n,
            "scored_count": 0,
            "model_name": settings.RERANKER_MODEL,
            "reranker_latency_ms": 0.0,
        }
    scores = score_query_documents(
        normalized_query,
        [candidate.text for candidate in candidates_to_score],
        batch_size=settings.RERANKER_BATCH_SIZE,
    )
    scored = list(zip(candidates_to_score, scores, strict=True))
    scored.sort(key=lambda item: (-float(item[1]), item[0].rank, item[0].chunk_id))
    reranked = [
        _reranked_result_from_hybrid(
            candidate,
            reranker_score=float(score),
            rerank_rank=rerank_rank,
            final_rank=rerank_rank,
        )
        for rerank_rank, (candidate, score) in enumerate(scored, start=1)
    ]
    metadata = {
        "rerank_top_n": rerank_top_n,
        "scored_count": len(candidates_to_score),
        "model_name": settings.RERANKER_MODEL,
        "reranker_latency_ms": round((perf_counter() - started) * 1000, 2),
    }
    return reranked[:top_k], metadata


def search_hybrid_rerank(
    db: Session,
    query: str,
    index_version_id: UUID | str | None = None,
    top_k: int = 10,
    bm25_candidate_k: int = 50,
    dense_candidate_k: int = 50,
    hybrid_candidate_k: int = 50,
    rerank_top_n: int = 25,
    rrf_k: int = 60,
) -> RerankedSearchResponse:
    normalized_query = _validate_hybrid_rerank_request(
        query,
        top_k,
        bm25_candidate_k,
        dense_candidate_k,
        hybrid_candidate_k,
        rerank_top_n,
        rrf_k,
    )
    started = perf_counter()
    hybrid_response = search_hybrid(
        db,
        query=normalized_query,
        index_version_id=index_version_id,
        top_k=hybrid_candidate_k,
        bm25_candidate_k=bm25_candidate_k,
        dense_candidate_k=dense_candidate_k,
        rrf_k=rrf_k,
    )
    results, rerank_metadata = rerank_candidates(
        normalized_query,
        hybrid_response.results,
        rerank_top_n=rerank_top_n,
        top_k=top_k,
    )
    return RerankedSearchResponse(
        query=normalized_query,
        index_version_id=hybrid_response.index_version_id,
        lexical_index_name=hybrid_response.lexical_index_name,
        vector_collection_name=hybrid_response.vector_collection_name,
        top_k=top_k,
        bm25_candidate_k=bm25_candidate_k,
        dense_candidate_k=dense_candidate_k,
        hybrid_candidate_k=hybrid_candidate_k,
        rerank_top_n=rerank_top_n,
        rrf_k=rrf_k,
        result_count=len(results),
        results=results,
        latency_ms=round((perf_counter() - started) * 1000, 2),
        bm25_latency_ms=hybrid_response.bm25_latency_ms,
        dense_latency_ms=hybrid_response.dense_latency_ms,
        fusion_latency_ms=hybrid_response.fusion_latency_ms,
        reranker_latency_ms=rerank_metadata["reranker_latency_ms"],
        embedding_latency_ms=hybrid_response.embedding_latency_ms,
        qdrant_latency_ms=hybrid_response.qdrant_latency_ms,
    )
