import math

import pytest

from app.evaluation.metrics import (
    aggregate_query_metrics,
    dcg_at_k,
    deduplicate_ranked_ids,
    evaluate_single_query,
    idcg_at_k,
    mrr_at_k,
    ndcg_at_k,
    recall_at_k,
    reciprocal_rank_at_k,
)


def test_deduplicate_ranked_ids_preserves_order_and_ignores_empty_values() -> None:
    assert deduplicate_ranked_ids(["d1", "d2", "d1", "", None, " d3 "]) == [
        "d1",
        "d2",
        "d3",
    ]


def test_recall_at_k_handles_perfect_partial_miss_and_duplicates() -> None:
    assert recall_at_k(["d1", "d2"], {"d1", "d2"}, 2) == 1.0
    assert recall_at_k(["d1"], {"d1", "d2"}, 1) == 0.5
    assert recall_at_k(["x"], {"d1"}, 1) == 0.0
    assert recall_at_k(["x", "x", "d1"], {"d1"}, 2) == 1.0


def test_recall_at_k_rejects_invalid_k() -> None:
    with pytest.raises(ValueError, match="k"):
        recall_at_k(["d1"], {"d1"}, 0)


def test_reciprocal_rank_at_k_handles_first_late_miss_and_duplicates() -> None:
    assert reciprocal_rank_at_k(["d1"], {"d1"}, 10) == 1.0
    assert reciprocal_rank_at_k(["x", "d1"], {"d1"}, 10) == 0.5
    assert reciprocal_rank_at_k(["x"], {"d1"}, 10) == 0.0
    assert reciprocal_rank_at_k(["x", "x", "d1"], {"d1"}, 10) == 0.5


def test_reciprocal_rank_at_k_rejects_invalid_k() -> None:
    with pytest.raises(ValueError, match="k"):
        reciprocal_rank_at_k(["d1"], {"d1"}, -1)


def test_mrr_at_k_averages_and_empty_returns_zero() -> None:
    assert mrr_at_k([1.0, 0.5, 0.0]) == pytest.approx(0.5)
    assert mrr_at_k([]) == 0.0


def test_dcg_idcg_and_ndcg_known_values() -> None:
    assert dcg_at_k(["d1"], {"d1": 1}, 1) == 1.0
    assert idcg_at_k({"d1": 1}, 1) == 1.0
    assert ndcg_at_k(["d1"], {"d1": 1}, 10) == 1.0
    assert ndcg_at_k(["x"], {"d1": 1}, 10) == 0.0

    graded = ndcg_at_k(["d2", "d1"], {"d1": 2, "d2": 1}, 2)
    expected_dcg = 1.0 + 3.0 / math.log2(3)
    expected_idcg = 3.0 + 1.0 / math.log2(3)
    assert graded == pytest.approx(expected_dcg / expected_idcg)


def test_dcg_rejects_invalid_k() -> None:
    with pytest.raises(ValueError, match="k"):
        dcg_at_k(["d1"], {"d1": 1}, 0)


def test_evaluate_single_query_returns_expected_fields_and_hits() -> None:
    metrics = evaluate_single_query(
        retrieved_document_ids=["x1", "d1", "d1", "x2"],
        relevant_document_ids=["d1", "d2"],
    )

    assert metrics["retrieved_count"] == 3
    assert metrics["relevant_count"] == 2
    assert metrics["recall_at_5"] == 0.5
    assert metrics["recall_at_10"] == 0.5
    assert metrics["reciprocal_rank_at_10"] == 0.5
    assert metrics["ndcg_at_10"] > 0
    assert metrics["hit_at_5"] == 1.0
    assert metrics["hit_at_10"] == 1.0


def test_aggregate_query_metrics_averages_correctly() -> None:
    aggregate = aggregate_query_metrics(
        [
            {
                "recall_at_5": 1.0,
                "recall_at_10": 1.0,
                "reciprocal_rank_at_10": 1.0,
                "ndcg_at_10": 1.0,
                "hit_at_5": 1.0,
                "hit_at_10": 1.0,
            },
            {
                "recall_at_5": 0.0,
                "recall_at_10": 0.5,
                "reciprocal_rank_at_10": 0.25,
                "ndcg_at_10": 0.3,
                "hit_at_5": 0.0,
                "hit_at_10": 1.0,
            },
        ]
    )

    assert aggregate["query_count"] == 2
    assert aggregate["recall_at_5"] == 0.5
    assert aggregate["recall_at_10"] == 0.75
    assert aggregate["mrr_at_10"] == 0.625
    assert aggregate["ndcg_at_10"] == 0.65
    assert aggregate["hit_rate_at_5"] == 0.5
    assert aggregate["hit_rate_at_10"] == 1.0


def test_empty_aggregate_returns_zeros() -> None:
    assert aggregate_query_metrics([]) == {
        "query_count": 0,
        "recall_at_5": 0.0,
        "recall_at_10": 0.0,
        "mrr_at_10": 0.0,
        "ndcg_at_10": 0.0,
        "hit_rate_at_5": 0.0,
        "hit_rate_at_10": 0.0,
    }

