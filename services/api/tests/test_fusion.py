from types import SimpleNamespace

import pytest

from app.search.fusion import reciprocal_rank_fusion


def candidate(chunk_id: str, rank: int, score: float):
    return SimpleNamespace(chunk_id=chunk_id, rank=rank, score=score)


def test_rrf_combines_two_ranked_lists_and_preserves_sources() -> None:
    bm25 = [candidate("shared", 1, 100.0), candidate("bm25-only", 2, 99.0)]
    dense = [candidate("shared", 2, 0.2), candidate("dense-only", 1, 0.9)]

    fused = reciprocal_rank_fusion(
        {"bm25": bm25, "dense": dense},
        id_getter=lambda value: value.chunk_id,
    )

    shared = next(value for value in fused if value.chunk_id == "shared")
    assert shared.source_ranks == {"bm25": 1, "dense": 2}
    assert shared.source_scores == {"bm25": 100.0, "dense": 0.2}
    assert shared.candidates_by_source["bm25"] is bm25[0]
    assert shared.candidates_by_source["dense"] is dense[0]
    assert shared.fusion_rank == 1


def test_candidate_in_both_lists_scores_higher_when_ranks_are_comparable() -> None:
    fused = reciprocal_rank_fusion(
        {
            "bm25": [candidate("shared", 2, 1.0), candidate("bm25-only", 1, 999.0)],
            "dense": [candidate("shared", 2, 1.0), candidate("dense-only", 1, 999.0)],
        },
        id_getter=lambda value: value.chunk_id,
    )

    assert fused[0].chunk_id == "shared"


def test_duplicate_chunk_ids_are_deduped_per_source() -> None:
    fused = reciprocal_rank_fusion(
        {"bm25": [candidate("same", 1, 1.0), candidate("same", 2, 2.0)]},
        id_getter=lambda value: value.chunk_id,
    )

    assert len(fused) == 1
    assert fused[0].source_ranks == {"bm25": 1}


def test_tie_breaking_is_deterministic() -> None:
    fused = reciprocal_rank_fusion(
        {"bm25": [candidate("b", 1, 1.0), candidate("a", 1, 2.0)]},
        id_getter=lambda value: value.chunk_id,
    )

    assert [value.chunk_id for value in fused] == ["a", "b"]


def test_empty_lists_return_empty_result() -> None:
    assert reciprocal_rank_fusion({"bm25": []}, id_getter=lambda value: value.chunk_id) == []


def test_invalid_rrf_k_rejected() -> None:
    with pytest.raises(ValueError):
        reciprocal_rank_fusion({"bm25": []}, id_getter=lambda value: value.chunk_id, rrf_k=0)


def test_raw_scores_are_not_used_for_fusion_ordering() -> None:
    fused = reciprocal_rank_fusion(
        {"bm25": [candidate("low-score-first", 1, 0.01), candidate("high-score-second", 2, 1000.0)]},
        id_getter=lambda value: value.chunk_id,
    )

    assert [value.chunk_id for value in fused] == ["low-score-first", "high-score-second"]
