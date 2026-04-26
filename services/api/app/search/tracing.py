from __future__ import annotations

from datetime import datetime
from typing import Any

TRACE_SCHEMA_VERSION = "search_trace_v1"


def _string_or_none(value: Any) -> str | None:
    return str(value) if value is not None else None


def candidate_preview(text: str | None, max_chars: int) -> str:
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return "." * max_chars
    return f"{text[: max_chars - 3]}..."


def index_version_snapshot(index_version: Any | None) -> dict[str, Any]:
    if index_version is None:
        return {
            "id": None,
            "name": None,
            "status": None,
            "is_active": None,
            "lexical_index_name": None,
            "vector_collection_name": None,
            "embedding_model": None,
            "embedding_dimension": None,
            "chunking_strategy": None,
            "chunking_version": None,
        }
    return {
        "id": _string_or_none(getattr(index_version, "id", None)),
        "name": getattr(index_version, "name", None),
        "status": getattr(index_version, "status", None),
        "is_active": getattr(index_version, "is_active", None),
        "lexical_index_name": getattr(index_version, "lexical_index_name", None),
        "vector_collection_name": getattr(index_version, "vector_collection_name", None),
        "embedding_model": getattr(index_version, "embedding_model", None),
        "embedding_dimension": getattr(index_version, "embedding_dimension", None),
        "chunking_strategy": getattr(index_version, "chunking_strategy", None),
        "chunking_version": getattr(index_version, "chunking_version", None),
    }


def build_base_trace(
    query: str,
    retrieval_mode: str,
    request_id: str | None,
    query_id: Any | None,
    trace_id: Any | None,
    index_version: Any | None,
    parameters: dict[str, Any],
    total_latency_ms: float | None = None,
    warnings: list[str] | None = None,
    errors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "trace_schema_version": TRACE_SCHEMA_VERSION,
        "query": query,
        "retrieval_mode": retrieval_mode,
        "request_id": request_id,
        "query_id": _string_or_none(query_id),
        "trace_id": _string_or_none(trace_id),
        "index_version": index_version_snapshot(index_version),
        "parameters": parameters,
        "stages": {},
        "ranking_summary": {},
        "warnings": warnings or [],
        "errors": errors or [],
        "total_latency_ms": total_latency_ms,
    }


def build_bm25_stage(
    latency_ms: float | None,
    index_name: str | None,
    candidate_count: int | None,
    result_count: int | None,
    enabled: bool = True,
) -> dict[str, Any]:
    return {
        "enabled": enabled,
        "latency_ms": latency_ms,
        "index_name": index_name,
        "candidate_count": candidate_count,
        "result_count": result_count,
    }


def build_dense_stage(
    latency_ms: float | None,
    collection_name: str | None,
    candidate_count: int | None,
    result_count: int | None,
    embedding_latency_ms: float | None,
    qdrant_latency_ms: float | None,
    query_embedding_dimension: int | None = None,
    enabled: bool = True,
) -> dict[str, Any]:
    return {
        "enabled": enabled,
        "latency_ms": latency_ms,
        "collection_name": collection_name,
        "candidate_count": candidate_count,
        "result_count": result_count,
        "embedding_latency_ms": embedding_latency_ms,
        "qdrant_latency_ms": qdrant_latency_ms,
        "query_embedding_dimension": query_embedding_dimension,
    }


def build_fusion_stage(
    latency_ms: float | None,
    rrf_k: int | None,
    fused_candidate_count: int | None,
    result_count: int | None,
    enabled: bool = True,
) -> dict[str, Any]:
    return {
        "enabled": enabled,
        "latency_ms": latency_ms,
        "method": "reciprocal_rank_fusion",
        "rrf_k": rrf_k,
        "fused_candidate_count": fused_candidate_count,
        "result_count": result_count,
    }


def build_reranker_stage(
    latency_ms: float | None,
    model_name: str | None,
    rerank_top_n: int | None,
    scored_count: int | None,
    result_count: int | None,
    enabled: bool = True,
) -> dict[str, Any]:
    return {
        "enabled": enabled,
        "latency_ms": latency_ms,
        "model_name": model_name,
        "rerank_top_n": rerank_top_n,
        "scored_count": scored_count,
        "result_count": result_count,
    }


def _range(values: list[float]) -> dict[str, float | None]:
    return {
        "min": min(values) if values else None,
        "max": max(values) if values else None,
    }


def _top_ids(results: list[Any]) -> list[dict[str, Any]]:
    return [
        {
            "rank": getattr(result, "rank", None),
            "chunk_id": _string_or_none(getattr(result, "chunk_id", None)),
            "document_id": _string_or_none(getattr(result, "document_id", None)),
        }
        for result in results
    ]


def build_ranking_summary(results: list[Any], retrieval_mode: str) -> dict[str, Any]:
    if retrieval_mode == "bm25":
        scores = [float(result.score) for result in results if getattr(result, "score", None) is not None]
        return {
            "top_results": _top_ids(results),
            "bm25_score_range": _range(scores),
            "result_count": len(results),
        }
    if retrieval_mode == "dense":
        scores = [float(result.score) for result in results if getattr(result, "score", None) is not None]
        return {
            "top_results": _top_ids(results),
            "dense_score_range": _range(scores),
            "result_count": len(results),
        }
    if retrieval_mode == "hybrid":
        bm25_only = dense_only = both = 0
        fusion_scores = []
        for result in results:
            has_bm25 = getattr(result, "bm25_rank", None) is not None
            has_dense = getattr(result, "dense_rank", None) is not None
            if has_bm25 and has_dense:
                both += 1
            elif has_bm25:
                bm25_only += 1
            elif has_dense:
                dense_only += 1
            if getattr(result, "fusion_score", None) is not None:
                fusion_scores.append(float(result.fusion_score))
        return {
            "top_results": _top_ids(results),
            "bm25_only_count": bm25_only,
            "dense_only_count": dense_only,
            "both_sources_count": both,
            "top_fusion_scores": fusion_scores[:10],
            "result_count": len(results),
        }
    if retrieval_mode == "hybrid_rerank":
        moved_up = moved_down = unchanged = 0
        largest_upward_move = 0
        largest_downward_move = 0
        movements = []
        reranker_scores = []
        for result in results:
            fusion_rank = getattr(result, "fusion_rank", None)
            rerank_rank = getattr(result, "rerank_rank", None)
            movement = None
            if fusion_rank is not None and rerank_rank is not None:
                movement = int(fusion_rank) - int(rerank_rank)
                if movement > 0:
                    moved_up += 1
                    largest_upward_move = max(largest_upward_move, movement)
                elif movement < 0:
                    moved_down += 1
                    largest_downward_move = min(largest_downward_move, movement)
                else:
                    unchanged += 1
            if getattr(result, "reranker_score", None) is not None:
                reranker_scores.append(float(result.reranker_score))
            movements.append(
                {
                    "chunk_id": _string_or_none(getattr(result, "chunk_id", None)),
                    "fusion_rank": fusion_rank,
                    "rerank_rank": rerank_rank,
                    "movement": movement,
                }
            )
        return {
            "top_results": _top_ids(results),
            "moved_up": moved_up,
            "moved_down": moved_down,
            "unchanged": unchanged,
            "largest_upward_move": largest_upward_move,
            "largest_downward_move": largest_downward_move,
            "movements": movements[:25],
            "reranker_score_range": _range(reranker_scores),
            "result_count": len(results),
        }
    return {"top_results": _top_ids(results), "result_count": len(results)}


def serialize_candidate_for_trace(candidate: Any) -> dict[str, Any]:
    created_at = getattr(candidate, "created_at", None)
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()
    return {
        "id": _string_or_none(getattr(candidate, "id", None)),
        "source": getattr(candidate, "source", None),
        "final_rank": getattr(candidate, "final_rank", None),
        "bm25_rank": getattr(candidate, "bm25_rank", None),
        "dense_rank": getattr(candidate, "dense_rank", None),
        "fusion_rank": getattr(candidate, "fusion_rank", None),
        "rerank_rank": getattr(candidate, "rerank_rank", None),
        "bm25_score": getattr(candidate, "bm25_score", None),
        "dense_score": getattr(candidate, "dense_score", None),
        "fusion_score": getattr(candidate, "fusion_score", None),
        "reranker_score": getattr(candidate, "reranker_score", None),
        "chunk_id": _string_or_none(getattr(candidate, "chunk_id", None)),
        "document_id": _string_or_none(getattr(candidate, "document_id", None)),
        "metadata_json": dict(getattr(candidate, "metadata_json", None) or {}),
        "created_at": created_at,
    }


def group_candidates_by_source(candidates: list[Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        serialized = (
            candidate if isinstance(candidate, dict) else serialize_candidate_for_trace(candidate)
        )
        source = serialized.get("source") or "unknown"
        grouped.setdefault(source, []).append(serialized)
    return grouped
