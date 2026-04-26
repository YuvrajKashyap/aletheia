import json
from pathlib import Path

import pytest

from app.cli.evaluate_metrics_fixture import evaluate_fixture, load_fixture


def test_evaluate_metrics_fixture_sample_shape() -> None:
    fixture_path = Path(__file__).resolve().parents[3] / "data" / "samples" / "metrics-fixture.json"

    output = evaluate_fixture(load_fixture(fixture_path))

    assert set(output) == {"per_query", "aggregate", "latency_summary"}
    assert len(output["per_query"]) == 3
    assert output["per_query"][0]["query_id"] == "q_perfect"
    assert output["aggregate"]["query_count"] == 3
    assert output["aggregate"]["recall_at_5"] == pytest.approx(2 / 3)
    assert output["latency_summary"]["p95_latency_ms"] == 100.0


def test_evaluate_metrics_fixture_rejects_missing_queries(tmp_path) -> None:
    fixture = tmp_path / "bad.json"
    fixture.write_text(json.dumps({"latencies_ms": [1.0]}), encoding="utf-8")

    with pytest.raises(ValueError, match="queries"):
        load_fixture(fixture)


def test_evaluate_metrics_fixture_custom_payload() -> None:
    output = evaluate_fixture(
        {
            "queries": [
                {
                    "query_id": "q1",
                    "retrieved_document_ids": ["d1", "d2"],
                    "relevant_document_ids": ["d2"],
                    "relevance_by_id": {"d2": 1},
                }
            ],
            "latencies_ms": [12.5, 20.0],
        }
    )

    assert output["per_query"][0]["metrics"]["reciprocal_rank_at_10"] == 0.5
    assert output["aggregate"]["mrr_at_10"] == 0.5
    assert output["latency_summary"]["avg_latency_ms"] == 16.25
