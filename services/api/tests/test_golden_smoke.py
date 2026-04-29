from __future__ import annotations

import json

from app.evaluation.smoke import (
    evaluate_smoke_thresholds,
    load_smoke_thresholds,
    write_smoke_report,
)


def test_load_smoke_thresholds_reads_valid_config_json(tmp_path):
    config_path = tmp_path / "thresholds.json"
    config_path.write_text(
        json.dumps(
            {
                "mode": "warn",
                "description": "test thresholds",
                "query_limit": 5,
                "retrieval_mode": "hybrid",
                "thresholds": {
                    "failed_query_count_max": 0,
                    "recall_at_10_min": 0.2,
                    "mrr_at_10_min": 0.0,
                    "ndcg_at_10_min": 0.0,
                },
            }
        ),
        encoding="utf-8",
    )

    config = load_smoke_thresholds(str(config_path))

    assert config["mode"] == "warn"
    assert config["thresholds"]["recall_at_10_min"] == 0.2


def test_evaluate_smoke_thresholds_passes_when_metrics_satisfy_thresholds():
    result = evaluate_smoke_thresholds(
        {
            "failed_query_count": 0,
            "recall_at_10": 0.5,
            "mrr_at_10": 0.1,
            "ndcg_at_10": 0.2,
        },
        {
            "mode": "warn",
            "thresholds": {
                "failed_query_count_max": 0,
                "recall_at_10_min": 0.2,
                "mrr_at_10_min": 0.0,
                "ndcg_at_10_min": 0.0,
            },
        },
    )

    assert result["status"] == "pass"
    assert result["warnings"] == []
    assert result["failures"] == []


def test_evaluate_smoke_thresholds_warn_mode_warns_on_threshold_miss():
    result = evaluate_smoke_thresholds(
        {"failed_query_count": 0, "recall_at_10": 0.1},
        {"mode": "warn", "thresholds": {"recall_at_10_min": 0.2}},
    )

    assert result["status"] == "warning"
    assert result["warnings"]
    assert result["failures"] == []


def test_evaluate_smoke_thresholds_fail_mode_fails_on_threshold_miss():
    result = evaluate_smoke_thresholds(
        {"failed_query_count": 0, "recall_at_10": 0.1},
        {"mode": "fail", "thresholds": {"recall_at_10_min": 0.2}},
    )

    assert result["status"] == "fail"
    assert result["warnings"] == []
    assert result["failures"]


def test_evaluate_smoke_thresholds_missing_metrics_warn():
    result = evaluate_smoke_thresholds(
        {"failed_query_count": 0},
        {"mode": "fail", "thresholds": {"mrr_at_10_min": 0.0}},
    )

    assert result["status"] == "warning"
    assert "missing" in result["warnings"][0]
    assert result["failures"] == []


def test_evaluate_smoke_thresholds_failed_query_count_max_check():
    result = evaluate_smoke_thresholds(
        {"failed_query_count": 1},
        {"mode": "fail", "thresholds": {"failed_query_count_max": 0}},
    )

    assert result["status"] == "fail"
    assert result["checks"][0]["name"] == "failed_query_count"
    assert result["checks"][0]["operator"] == "<="


def test_write_smoke_report_writes_json_and_creates_parent_dirs(tmp_path):
    output_path = tmp_path / "nested" / "smoke.json"

    written_path = write_smoke_report({"status": "pass"}, str(output_path))

    assert written_path == str(output_path)
    assert json.loads(output_path.read_text(encoding="utf-8")) == {"status": "pass"}
