from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FusedCandidate:
    chunk_id: str
    fusion_score: float
    fusion_rank: int
    source_ranks: dict[str, int] = field(default_factory=dict)
    source_scores: dict[str, float | None] = field(default_factory=dict)
    best_rank: int = 0
    candidates_by_source: dict[str, Any] = field(default_factory=dict)


def _default_rank_getter(candidate: Any) -> int:
    return int(getattr(candidate, "rank"))


def _default_score_getter(candidate: Any) -> float | None:
    score = getattr(candidate, "score", None)
    return float(score) if score is not None else None


def reciprocal_rank_fusion(
    ranked_lists: dict[str, list],
    id_getter: Callable[[Any], str],
    rank_getter: Callable[[Any], int] | None = None,
    score_getter: Callable[[Any], float | None] | None = None,
    rrf_k: int = 60,
) -> list[FusedCandidate]:
    if rrf_k <= 0:
        raise ValueError("rrf_k must be greater than 0.")

    resolved_rank_getter = rank_getter or _default_rank_getter
    resolved_score_getter = score_getter or _default_score_getter
    by_chunk_id: dict[str, dict[str, Any]] = {}

    for source, candidates in ranked_lists.items():
        for candidate in candidates:
            chunk_id = str(id_getter(candidate))
            rank = int(resolved_rank_getter(candidate))
            score = resolved_score_getter(candidate)
            entry = by_chunk_id.setdefault(
                chunk_id,
                {
                    "fusion_score": 0.0,
                    "source_ranks": {},
                    "source_scores": {},
                    "best_rank": rank,
                    "candidates_by_source": {},
                },
            )
            if source in entry["source_ranks"]:
                continue
            entry["fusion_score"] += 1.0 / (rrf_k + rank)
            entry["source_ranks"][source] = rank
            entry["source_scores"][source] = score
            entry["best_rank"] = min(entry["best_rank"], rank)
            entry["candidates_by_source"][source] = candidate

    sorted_items = sorted(
        by_chunk_id.items(),
        key=lambda item: (-item[1]["fusion_score"], item[1]["best_rank"], item[0]),
    )
    return [
        FusedCandidate(
            chunk_id=chunk_id,
            fusion_score=values["fusion_score"],
            fusion_rank=rank,
            source_ranks=dict(values["source_ranks"]),
            source_scores=dict(values["source_scores"]),
            best_rank=values["best_rank"],
            candidates_by_source=dict(values["candidates_by_source"]),
        )
        for rank, (chunk_id, values) in enumerate(sorted_items, start=1)
    ]
