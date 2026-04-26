from __future__ import annotations

from time import perf_counter
from uuid import UUID

from sqlalchemy.orm import Session

from app.search.dense_retriever import search_dense
from app.search.fusion import FusedCandidate, reciprocal_rank_fusion
from app.search.lexical_retriever import search_bm25
from app.search.retrieval_models import (
    DenseSearchResponse,
    HybridSearchResponse,
    HybridSearchResult,
    LexicalSearchResponse,
)


class HybridRetrievalError(RuntimeError):
    pass


class InvalidHybridSearchRequestError(ValueError):
    pass


def _validate_hybrid_search_request(
    query: str,
    top_k: int,
    bm25_candidate_k: int,
    dense_candidate_k: int,
    rrf_k: int,
) -> str:
    normalized_query = query.strip()
    if not normalized_query:
        raise InvalidHybridSearchRequestError("Hybrid query must not be empty.")
    if top_k < 1 or top_k > 100:
        raise InvalidHybridSearchRequestError("top_k must be between 1 and 100.")
    if bm25_candidate_k < top_k:
        raise InvalidHybridSearchRequestError("bm25_candidate_k must be greater than or equal to top_k.")
    if dense_candidate_k < top_k:
        raise InvalidHybridSearchRequestError("dense_candidate_k must be greater than or equal to top_k.")
    if rrf_k <= 0:
        raise InvalidHybridSearchRequestError("rrf_k must be greater than 0.")
    return normalized_query


def _preferred_candidate(fused: FusedCandidate):
    return fused.candidates_by_source.get("bm25") or fused.candidates_by_source.get("dense")


def _hybrid_result_from_fused(fused: FusedCandidate) -> HybridSearchResult:
    candidate = _preferred_candidate(fused)
    dense_candidate = fused.candidates_by_source.get("dense")
    return HybridSearchResult(
        rank=fused.fusion_rank,
        chunk_id=str(fused.chunk_id),
        document_id=getattr(candidate, "document_id", None),
        dataset_id=getattr(candidate, "dataset_id", None),
        index_version_id=getattr(dense_candidate, "index_version_id", None),
        document_external_id=getattr(candidate, "document_external_id", None),
        chunk_external_id=getattr(candidate, "chunk_external_id", None),
        title=getattr(candidate, "title", None),
        text=str(getattr(candidate, "text", "") or ""),
        fusion_score=fused.fusion_score,
        bm25_rank=fused.source_ranks.get("bm25"),
        dense_rank=fused.source_ranks.get("dense"),
        bm25_score=fused.source_scores.get("bm25"),
        dense_score=fused.source_scores.get("dense"),
        token_count=getattr(candidate, "token_count", None),
        content_hash=getattr(candidate, "content_hash", None),
        chunking_strategy=getattr(candidate, "chunking_strategy", None),
        chunking_version=getattr(candidate, "chunking_version", None),
        metadata_json=dict(getattr(candidate, "metadata_json", None) or {}),
    )


def search_hybrid_from_results(
    query: str,
    bm25_response: LexicalSearchResponse,
    dense_response: DenseSearchResponse,
    top_k: int,
    rrf_k: int,
    fusion_latency_ms: float | None = None,
) -> HybridSearchResponse:
    if not query.strip():
        raise InvalidHybridSearchRequestError("Hybrid query must not be empty.")
    if top_k < 1 or top_k > 100:
        raise InvalidHybridSearchRequestError("top_k must be between 1 and 100.")
    if rrf_k <= 0:
        raise InvalidHybridSearchRequestError("rrf_k must be greater than 0.")
    fusion_started = perf_counter()
    fused_candidates = reciprocal_rank_fusion(
        ranked_lists={
            "bm25": bm25_response.results,
            "dense": dense_response.results,
        },
        id_getter=lambda candidate: candidate.chunk_id,
        rrf_k=rrf_k,
    )
    resolved_fusion_latency_ms = (
        fusion_latency_ms
        if fusion_latency_ms is not None
        else round((perf_counter() - fusion_started) * 1000, 2)
    )
    results = [_hybrid_result_from_fused(candidate) for candidate in fused_candidates[:top_k]]
    return HybridSearchResponse(
        query=query.strip(),
        index_version_id=bm25_response.index_version_id or dense_response.index_version_id,
        lexical_index_name=bm25_response.index_name,
        vector_collection_name=dense_response.collection_name,
        top_k=top_k,
        bm25_candidate_k=len(bm25_response.results),
        dense_candidate_k=len(dense_response.results),
        rrf_k=rrf_k,
        result_count=len(results),
        results=results,
        latency_ms=round(
            (bm25_response.latency_ms or 0.0)
            + (dense_response.latency_ms or 0.0)
            + (resolved_fusion_latency_ms or 0.0),
            2,
        ),
        bm25_latency_ms=bm25_response.latency_ms,
        dense_latency_ms=dense_response.latency_ms,
        fusion_latency_ms=resolved_fusion_latency_ms,
        embedding_latency_ms=dense_response.embedding_latency_ms,
        qdrant_latency_ms=dense_response.qdrant_latency_ms,
    )


def search_hybrid(
    db: Session,
    query: str,
    index_version_id: UUID | str | None = None,
    top_k: int = 10,
    bm25_candidate_k: int = 50,
    dense_candidate_k: int = 50,
    rrf_k: int = 60,
) -> HybridSearchResponse:
    normalized_query = _validate_hybrid_search_request(
        query,
        top_k,
        bm25_candidate_k,
        dense_candidate_k,
        rrf_k,
    )
    started = perf_counter()
    bm25_response = search_bm25(
        db,
        query=normalized_query,
        index_version_id=index_version_id,
        top_k=bm25_candidate_k,
        candidate_k=bm25_candidate_k,
    )
    dense_response = search_dense(
        db,
        query=normalized_query,
        index_version_id=index_version_id,
        top_k=dense_candidate_k,
        candidate_k=dense_candidate_k,
    )
    fusion_started = perf_counter()
    response = search_hybrid_from_results(
        query=normalized_query,
        bm25_response=bm25_response,
        dense_response=dense_response,
        top_k=top_k,
        rrf_k=rrf_k,
        fusion_latency_ms=None,
    )
    fusion_latency_ms = round((perf_counter() - fusion_started) * 1000, 2)
    return HybridSearchResponse(
        query=response.query,
        index_version_id=response.index_version_id,
        lexical_index_name=response.lexical_index_name,
        vector_collection_name=response.vector_collection_name,
        top_k=top_k,
        bm25_candidate_k=bm25_candidate_k,
        dense_candidate_k=dense_candidate_k,
        rrf_k=rrf_k,
        result_count=response.result_count,
        results=response.results,
        latency_ms=round((perf_counter() - started) * 1000, 2),
        bm25_latency_ms=bm25_response.latency_ms,
        dense_latency_ms=dense_response.latency_ms,
        fusion_latency_ms=fusion_latency_ms,
        embedding_latency_ms=dense_response.embedding_latency_ms,
        qdrant_latency_ms=dense_response.qdrant_latency_ms,
    )
