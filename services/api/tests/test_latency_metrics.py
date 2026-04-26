import pytest

from app.evaluation.latency import percentile, summarize_latencies


def test_empty_latency_summary_returns_zeros() -> None:
    assert summarize_latencies([]) == {
        "count": 0,
        "avg_latency_ms": 0.0,
        "p50_latency_ms": 0.0,
        "p95_latency_ms": 0.0,
        "min_latency_ms": 0.0,
        "max_latency_ms": 0.0,
    }


def test_single_latency_value_summary() -> None:
    assert summarize_latencies([12.5]) == {
        "count": 1,
        "avg_latency_ms": 12.5,
        "p50_latency_ms": 12.5,
        "p95_latency_ms": 12.5,
        "min_latency_ms": 12.5,
        "max_latency_ms": 12.5,
    }


def test_latency_summary_uses_nearest_rank_percentiles() -> None:
    summary = summarize_latencies([100.0, 10.0, 20.0, 30.0])

    assert summary["count"] == 4
    assert summary["avg_latency_ms"] == 40.0
    assert summary["p50_latency_ms"] == 20.0
    assert summary["p95_latency_ms"] == 100.0
    assert summary["min_latency_ms"] == 10.0
    assert summary["max_latency_ms"] == 100.0


def test_percentile_rejects_invalid_p() -> None:
    with pytest.raises(ValueError, match="between"):
        percentile([1.0], -1)
    with pytest.raises(ValueError, match="between"):
        percentile([1.0], 101)


def test_percentile_empty_returns_zero() -> None:
    assert percentile([], 50) == 0.0

