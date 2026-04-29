from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from app.benchmarks.reporting import format_markdown_benchmark_table, write_benchmark_summary
from app.benchmarks.suite import (
    build_planned_runs,
    compute_best_by_metric,
    load_benchmark_suite_config,
)


def _config() -> dict:
    return {
        "description": "test",
        "dataset_name": "beir/scifact",
        "dataset_version": "test",
        "runs": [
            {
                "name": "BM25",
                "retrieval_mode": "bm25",
                "query_limit": None,
                "top_k": 10,
            },
            {
                "name": "Hybrid rerank",
                "retrieval_mode": "hybrid_rerank",
                "query_limit": 50,
                "top_k": 10,
            },
        ],
    }


def test_benchmark_config_loader_reads_valid_config_json(tmp_path):
    config_path = tmp_path / "suite.json"
    config_path.write_text(json.dumps(_config()), encoding="utf-8")

    config = load_benchmark_suite_config(str(config_path))

    assert config["dataset_name"] == "beir/scifact"
    assert len(config["runs"]) == 2


def test_benchmark_config_loader_rejects_invalid_retrieval_mode(tmp_path):
    config = _config()
    config["runs"][0]["retrieval_mode"] = "invalid"
    config_path = tmp_path / "suite.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported retrieval_mode"):
        load_benchmark_suite_config(str(config_path))


def test_build_planned_runs_filters_skip_rerank():
    planned = build_planned_runs(_config(), skip_rerank=True)

    assert [run["retrieval_mode"] for run in planned] == ["bm25"]


def test_build_planned_runs_filters_only_mode():
    planned = build_planned_runs(_config(), only_modes=["hybrid_rerank"])

    assert [run["retrieval_mode"] for run in planned] == ["hybrid_rerank"]


def test_build_planned_runs_rerank_full_sets_query_limit_to_none():
    planned = build_planned_runs(_config(), rerank_full=True, only_modes=["hybrid_rerank"])

    assert planned[0]["query_limit"] is None
    assert planned[0]["scope"] == "Full"


def test_compute_best_by_metric_ignores_failed_runs_and_uses_values():
    result = compute_best_by_metric(
        [
            {
                "name": "failed",
                "retrieval_mode": "bm25",
                "status": "failed",
                "recall_at_10": 1.0,
                "scope": "Full",
            },
            {
                "name": "completed",
                "retrieval_mode": "dense",
                "status": "completed",
                "recall_at_10": 0.2,
                "scope": "Full",
                "evaluation_run_id": "run-1",
            },
        ]
    )

    assert result["recall_at_10"]["runs"][0]["retrieval_mode"] == "dense"
    assert result["recall_at_10"]["value"] == 0.2


def test_compute_best_by_metric_does_not_hardcode_winners():
    result = compute_best_by_metric(
        [
            {
                "name": "bm25",
                "retrieval_mode": "bm25",
                "status": "completed",
                "recall_at_10": 0.1,
                "scope": "Full",
            },
            {
                "name": "hybrid",
                "retrieval_mode": "hybrid",
                "status": "completed",
                "recall_at_10": 0.1,
                "scope": "Full",
            },
        ]
    )

    assert {run["retrieval_mode"] for run in result["recall_at_10"]["runs"]} == {
        "bm25",
        "hybrid",
    }


def test_markdown_table_includes_full_and_sampled_scope():
    table = format_markdown_benchmark_table(
        {
            "runs": [
                {"retrieval_mode": "bm25", "scope": "Full", "query_count": 300},
                {"retrieval_mode": "hybrid_rerank", "scope": "Sampled", "query_count": 50},
            ]
        }
    )

    assert "Full" in table
    assert "Sampled" in table


def test_markdown_table_includes_failure_rows_honestly():
    table = format_markdown_benchmark_table(
        {
            "runs": [
                {
                    "retrieval_mode": "dense",
                    "scope": "Full",
                    "status": "failed",
                    "error": "Qdrant unavailable",
                }
            ]
        }
    )

    assert "Qdrant unavailable" in table
    assert "n/a" in table


def test_write_benchmark_summary_writes_json_to_temp_directory(tmp_path):
    report = {"runs": []}
    path = write_benchmark_summary(report, str(tmp_path))

    assert json.loads(Path(path).read_text(encoding="utf-8"))["runs"] == []


def test_write_benchmark_summary_path_format(tmp_path):
    path = write_benchmark_summary({"runs": []}, str(tmp_path))
    name = path.replace("\\", "/").split("/")[-1]

    assert re.fullmatch(r"final-benchmark-suite-\d{8}-\d{6}\.json", name)
