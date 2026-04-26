from __future__ import annotations

import math
from collections.abc import Iterable
from typing import Any


def _normalize_id(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_relevant_ids(relevant_ids: set[str] | list[str]) -> set[str]:
    return {normalized for value in relevant_ids if (normalized := _normalize_id(value))}


def _normalize_relevance_by_id(
    relevance_by_id: dict[str, float] | dict[str, int],
) -> dict[str, float]:
    return {
        normalized: float(score)
        for value, score in relevance_by_id.items()
        if (normalized := _normalize_id(value)) and float(score) > 0
    }


def _validate_k(k: int) -> None:
    if k <= 0:
        raise ValueError("k must be greater than 0")


def deduplicate_ranked_ids(ranked_ids: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in ranked_ids:
        normalized = _normalize_id(value)
        if normalized is None or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def recall_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str] | list[str],
    k: int,
) -> float:
    _validate_k(k)
    relevant = _normalize_relevant_ids(relevant_ids)
    if not relevant:
        return 0.0
    retrieved = deduplicate_ranked_ids(retrieved_ids)[:k]
    return len(set(retrieved) & relevant) / len(relevant)


def reciprocal_rank_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str] | list[str],
    k: int,
) -> float:
    _validate_k(k)
    relevant = _normalize_relevant_ids(relevant_ids)
    if not relevant:
        return 0.0
    for rank, document_id in enumerate(deduplicate_ranked_ids(retrieved_ids)[:k], start=1):
        if document_id in relevant:
            return 1.0 / rank
    return 0.0


def mrr_at_k(per_query_reciprocal_ranks: list[float]) -> float:
    if not per_query_reciprocal_ranks:
        return 0.0
    return sum(float(value) for value in per_query_reciprocal_ranks) / len(
        per_query_reciprocal_ranks
    )


def dcg_at_k(
    retrieved_ids: list[str],
    relevance_by_id: dict[str, float] | dict[str, int],
    k: int,
) -> float:
    _validate_k(k)
    relevance = _normalize_relevance_by_id(relevance_by_id)
    total = 0.0
    for rank, document_id in enumerate(deduplicate_ranked_ids(retrieved_ids)[:k], start=1):
        score = relevance.get(document_id, 0.0)
        if score <= 0:
            continue
        total += (math.pow(2.0, score) - 1.0) / math.log2(rank + 1)
    return total


def idcg_at_k(
    relevance_by_id: dict[str, float] | dict[str, int],
    k: int,
) -> float:
    _validate_k(k)
    relevance_scores = sorted(
        (score for score in _normalize_relevance_by_id(relevance_by_id).values() if score > 0),
        reverse=True,
    )
    total = 0.0
    for rank, score in enumerate(relevance_scores[:k], start=1):
        total += (math.pow(2.0, score) - 1.0) / math.log2(rank + 1)
    return total


def ndcg_at_k(
    retrieved_ids: list[str],
    relevance_by_id: dict[str, float] | dict[str, int],
    k: int,
) -> float:
    ideal = idcg_at_k(relevance_by_id, k)
    if ideal == 0:
        return 0.0
    return dcg_at_k(retrieved_ids, relevance_by_id, k) / ideal


def evaluate_single_query(
    retrieved_document_ids: list[str],
    relevant_document_ids: set[str] | list[str],
    relevance_by_id: dict[str, float] | dict[str, int] | None = None,
    ks: tuple[int, ...] = (5, 10),
) -> dict:
    retrieved = deduplicate_ranked_ids(retrieved_document_ids)
    relevant = _normalize_relevant_ids(relevant_document_ids)
    relevance = (
        _normalize_relevance_by_id(relevance_by_id)
        if relevance_by_id is not None
        else {document_id: 1.0 for document_id in relevant}
    )
    metrics: dict[str, float | int] = {
        "retrieved_count": len(retrieved),
        "relevant_count": len(relevant),
    }
    for k in ks:
        metrics[f"recall_at_{k}"] = recall_at_k(retrieved, relevant, k)
        metrics[f"hit_at_{k}"] = 1.0 if metrics[f"recall_at_{k}"] > 0 else 0.0

    metrics.setdefault("recall_at_5", recall_at_k(retrieved, relevant, 5))
    metrics.setdefault("recall_at_10", recall_at_k(retrieved, relevant, 10))
    metrics.setdefault("hit_at_5", 1.0 if metrics["recall_at_5"] > 0 else 0.0)
    metrics.setdefault("hit_at_10", 1.0 if metrics["recall_at_10"] > 0 else 0.0)
    metrics["reciprocal_rank_at_10"] = reciprocal_rank_at_k(retrieved, relevant, 10)
    metrics["ndcg_at_10"] = ndcg_at_k(retrieved, relevance, 10)
    return metrics


def _mean(values: Iterable[float]) -> float:
    materialized = list(values)
    if not materialized:
        return 0.0
    return sum(materialized) / len(materialized)


def aggregate_query_metrics(per_query_metrics: list[dict]) -> dict:
    if not per_query_metrics:
        return {
            "query_count": 0,
            "recall_at_5": 0.0,
            "recall_at_10": 0.0,
            "mrr_at_10": 0.0,
            "ndcg_at_10": 0.0,
            "hit_rate_at_5": 0.0,
            "hit_rate_at_10": 0.0,
        }

    return {
        "query_count": len(per_query_metrics),
        "recall_at_5": _mean(float(item.get("recall_at_5", 0.0)) for item in per_query_metrics),
        "recall_at_10": _mean(float(item.get("recall_at_10", 0.0)) for item in per_query_metrics),
        "mrr_at_10": mrr_at_k(
            [float(item.get("reciprocal_rank_at_10", 0.0)) for item in per_query_metrics]
        ),
        "ndcg_at_10": _mean(float(item.get("ndcg_at_10", 0.0)) for item in per_query_metrics),
        "hit_rate_at_5": _mean(float(item.get("hit_at_5", 0.0)) for item in per_query_metrics),
        "hit_rate_at_10": _mean(float(item.get("hit_at_10", 0.0)) for item in per_query_metrics),
    }

