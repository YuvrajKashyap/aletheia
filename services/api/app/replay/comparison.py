from __future__ import annotations

from typing import Any

from app.evaluation.correctness import deduplicate_ranked_document_ids, normalize_id


def _get_value(item: Any, key: str):
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def extract_ranked_document_ids_from_search_response(response) -> list[str]:
    results = response.get("results", []) if isinstance(response, dict) else getattr(response, "results", [])
    document_ids = [normalize_id(_get_value(result, "document_id")) for result in results]
    return deduplicate_ranked_document_ids(document_ids)


def compare_ranked_lists(
    source_document_ids: list[str],
    target_document_ids: list[str],
    top_k: int = 10,
) -> dict[str, Any]:
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")
    source = deduplicate_ranked_document_ids(source_document_ids)[:top_k]
    target = deduplicate_ranked_document_ids(target_document_ids)[:top_k]
    source_ranks = {document_id: rank for rank, document_id in enumerate(source, start=1)}
    target_ranks = {document_id: rank for rank, document_id in enumerate(target, start=1)}
    overlap = [document_id for document_id in source if document_id in target_ranks]
    rank_changes = [
        {
            "document_id": document_id,
            "source_rank": source_ranks[document_id],
            "target_rank": target_ranks[document_id],
            "movement": source_ranks[document_id] - target_ranks[document_id],
        }
        for document_id in overlap
    ]
    movements = [item["movement"] for item in rank_changes]
    upward = [movement for movement in movements if movement > 0]
    downward = [movement for movement in movements if movement < 0]
    return {
        "overlap_at_k": len(overlap),
        "added_document_ids": [document_id for document_id in target if document_id not in source_ranks],
        "removed_document_ids": [document_id for document_id in source if document_id not in target_ranks],
        "rank_changes": rank_changes,
        "largest_upward_move": max(upward) if upward else 0,
        "largest_downward_move": min(downward) if downward else 0,
    }


def _source_ranked_document_ids(source_trace) -> tuple[list[str], str | None]:
    if source_trace is None:
        return [], None
    trace_json = getattr(source_trace, "trace_json", None) or {}
    ranking_summary = trace_json.get("ranking_summary") or {}
    ranked = ranking_summary.get("ranked_document_ids") or trace_json.get("ranked_document_ids")
    if ranked:
        return deduplicate_ranked_document_ids(ranked), None
    return [], "Source trace did not contain ranked_document_ids; rank comparison was skipped."


def build_replay_comparison_json(
    saved_query,
    search_response,
    retrieval_mode: str,
    experiment_config=None,
    source_trace=None,
    metrics: dict | None = None,
    top_k: int = 10,
) -> dict[str, Any]:
    warnings: list[str] = []
    ranked_document_ids = extract_ranked_document_ids_from_search_response(search_response)
    source_ranked_ids, source_warning = _source_ranked_document_ids(source_trace)
    if source_warning:
        warnings.append(source_warning)
    target_trace_id = _get_value(search_response, "trace_id")
    target_query_id = _get_value(search_response, "query_id")
    source_trace_id = getattr(source_trace, "id", None) if source_trace is not None else None
    comparison = {
        "saved_query_id": normalize_id(getattr(saved_query, "id", None)),
        "query_text": getattr(saved_query, "text", ""),
        "retrieval_mode": retrieval_mode,
        "experiment_config_id": normalize_id(getattr(experiment_config, "id", None)),
        "experiment_config_name": getattr(experiment_config, "name", None),
        "target_query_id": normalize_id(target_query_id),
        "target_trace_id": normalize_id(target_trace_id),
        "top_k": top_k,
        "ranked_document_ids": ranked_document_ids,
        "metrics": metrics,
        "source_trace_id": normalize_id(source_trace_id),
        "rank_comparison": None,
        "latency_ms": _get_value(search_response, "latency_ms"),
        "warnings": warnings,
        "errors": [],
    }
    if source_ranked_ids:
        comparison["source_ranked_document_ids"] = source_ranked_ids
        comparison["rank_comparison"] = compare_ranked_lists(
            source_ranked_ids,
            ranked_document_ids,
            top_k=top_k,
        )
    return comparison
