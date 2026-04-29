from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.benchmarks.reporting import write_benchmark_summary
from app.evaluation.runner import run_offline_evaluation


SUPPORTED_RETRIEVAL_MODES = {"bm25", "dense", "hybrid", "hybrid_rerank"}
HIGHER_IS_BETTER = ("recall_at_5", "recall_at_10", "mrr_at_10", "ndcg_at_10")
LOWER_IS_BETTER = ("avg_latency_ms", "p50_latency_ms", "p95_latency_ms")


def load_benchmark_suite_config(path: str) -> dict:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    if not isinstance(config, dict):
        raise ValueError("Benchmark suite config must be a JSON object")

    runs = config.get("runs")
    if not isinstance(runs, list):
        raise ValueError("Benchmark suite config field 'runs' must be a list")

    for index, run in enumerate(runs):
        if not isinstance(run, dict):
            raise ValueError(f"Benchmark run at index {index} must be an object")
        if not isinstance(run.get("name"), str) or not run["name"].strip():
            raise ValueError(f"Benchmark run at index {index} must include name")
        retrieval_mode = run.get("retrieval_mode")
        if retrieval_mode not in SUPPORTED_RETRIEVAL_MODES:
            raise ValueError(f"Unsupported retrieval_mode in benchmark run: {retrieval_mode}")

    return config


def get_run_scope(run_config: dict, query_count: int | None = None) -> str:
    if run_config.get("query_limit") is None:
        return "Full"
    if query_count is not None and run_config.get("query_limit") == query_count:
        return "Sampled"
    return "Sampled"


def build_planned_runs(
    config: dict,
    skip_rerank: bool = False,
    only_modes: list[str] | None = None,
    rerank_full: bool = False,
) -> list[dict]:
    only_mode_set = set(only_modes or [])
    planned: list[dict] = []
    for run in config.get("runs", []):
        retrieval_mode = run.get("retrieval_mode")
        if skip_rerank and retrieval_mode == "hybrid_rerank":
            continue
        if only_mode_set and retrieval_mode not in only_mode_set:
            continue
        planned_run = copy.deepcopy(run)
        if rerank_full and retrieval_mode == "hybrid_rerank":
            planned_run["query_limit"] = None
            notes = planned_run.get("notes") or ""
            planned_run["notes"] = f"{notes} Full rerank override enabled.".strip()
        planned_run["scope"] = get_run_scope(planned_run)
        planned.append(planned_run)
    return planned


def _numeric(value: object) -> float | None:
    if isinstance(value, int | float):
        return float(value)
    return None


def compute_best_by_metric(runs: list[dict]) -> dict:
    completed = [run for run in runs if run.get("status") == "completed"]
    best: dict[str, dict[str, Any]] = {}

    for metric in HIGHER_IS_BETTER:
        candidates = [(run, _numeric(run.get(metric))) for run in completed]
        candidates = [(run, value) for run, value in candidates if value is not None]
        if not candidates:
            continue
        max_value = max(value for _, value in candidates)
        winners = [run for run, value in candidates if value == max_value]
        best[metric] = {
            "direction": "higher",
            "value": max_value,
            "runs": [
                {
                    "name": winner.get("name"),
                    "retrieval_mode": winner.get("retrieval_mode"),
                    "scope": winner.get("scope"),
                    "evaluation_run_id": winner.get("evaluation_run_id"),
                }
                for winner in winners
            ],
        }

    for metric in LOWER_IS_BETTER:
        candidates = [(run, _numeric(run.get(metric))) for run in completed]
        candidates = [(run, value) for run, value in candidates if value is not None]
        if not candidates:
            continue
        min_value = min(value for _, value in candidates)
        winners = [run for run, value in candidates if value == min_value]
        best[metric] = {
            "direction": "lower",
            "value": min_value,
            "runs": [
                {
                    "name": winner.get("name"),
                    "retrieval_mode": winner.get("retrieval_mode"),
                    "scope": winner.get("scope"),
                    "evaluation_run_id": winner.get("evaluation_run_id"),
                }
                for winner in winners
            ],
        }

    return best


def _mixed_scope_warnings(runs: list[dict], best_by_metric: dict) -> list[str]:
    warnings: list[str] = []
    for metric, result in best_by_metric.items():
        scopes = {run.get("scope") for run in runs if run.get("status") == "completed"}
        if len(scopes) > 1:
            warnings.append(
                f"{metric} best result was computed across mixed scopes. Compare full and sampled runs carefully."
            )
    return warnings


def _run_result_from_summary(run_config: dict, summary: dict) -> dict:
    aggregate_metrics = summary.get("aggregate_metrics", {})
    latency_summary = summary.get("latency_summary", {})
    if not isinstance(aggregate_metrics, dict):
        aggregate_metrics = {}
    if not isinstance(latency_summary, dict):
        latency_summary = {}

    query_count = summary.get("query_count")
    return {
        "name": run_config.get("name"),
        "retrieval_mode": summary.get("retrieval_mode") or run_config.get("retrieval_mode"),
        "scope": get_run_scope(run_config, query_count if isinstance(query_count, int) else None),
        "query_limit": run_config.get("query_limit"),
        "top_k": run_config.get("top_k"),
        "failed_query_count": summary.get("failed_query_count"),
        "query_count": query_count,
        "recall_at_5": aggregate_metrics.get("recall_at_5"),
        "recall_at_10": aggregate_metrics.get("recall_at_10"),
        "mrr_at_10": aggregate_metrics.get("mrr_at_10"),
        "ndcg_at_10": aggregate_metrics.get("ndcg_at_10"),
        "avg_latency_ms": latency_summary.get("avg_latency_ms"),
        "p50_latency_ms": latency_summary.get("p50_latency_ms"),
        "p95_latency_ms": latency_summary.get("p95_latency_ms"),
        "notes": run_config.get("notes"),
        "report_path": summary.get("report_path"),
        "evaluation_run_id": summary.get("evaluation_run_id"),
        "experiment_config": summary.get("experiment_config_name")
        or summary.get("experiment_config_id"),
        "status": summary.get("status"),
    }


def _call_evaluation_runner(db: Session, config: dict, run_config: dict) -> dict:
    return run_offline_evaluation(
        db,
        name=run_config["name"],
        retrieval_mode=run_config["retrieval_mode"],
        dataset_name=config.get("dataset_name", "beir/scifact"),
        dataset_version=config.get("dataset_version", "test"),
        query_limit=run_config.get("query_limit"),
        top_k=run_config.get("top_k", config.get("default_top_k", 10)),
        candidate_k=run_config.get("candidate_k"),
        bm25_candidate_k=run_config.get("bm25_candidate_k"),
        dense_candidate_k=run_config.get("dense_candidate_k"),
        hybrid_candidate_k=run_config.get("hybrid_candidate_k"),
        rerank_top_n=run_config.get("rerank_top_n"),
        rrf_k=run_config.get("rrf_k", 60),
        notes=run_config.get("notes"),
    )


def run_benchmark_suite(db: Session, config: dict, output_dir: str = "reports/benchmarks") -> dict:
    started_at = datetime.now(timezone.utc)
    suite_id = started_at.strftime("final-benchmark-suite-%Y%m%d-%H%M%S")
    runs: list[dict] = []
    warnings: list[str] = []

    for run_config in build_planned_runs(config):
        try:
            summary = _call_evaluation_runner(db, config, run_config)
            runs.append(_run_result_from_summary(run_config, summary))
        except Exception as exc:
            runs.append(
                {
                    "name": run_config.get("name"),
                    "retrieval_mode": run_config.get("retrieval_mode"),
                    "scope": get_run_scope(run_config),
                    "query_limit": run_config.get("query_limit"),
                    "top_k": run_config.get("top_k"),
                    "notes": run_config.get("notes"),
                    "status": "failed",
                    "error": str(exc),
                }
            )
            warnings.append(f"{run_config.get('name')} failed: {exc}")

    best_by_metric = compute_best_by_metric(runs)
    warnings.extend(_mixed_scope_warnings(runs, best_by_metric))
    completed_at = datetime.now(timezone.utc)
    report = {
        "benchmark_suite_id": suite_id,
        "dataset_name": config.get("dataset_name"),
        "dataset_version": config.get("dataset_version"),
        "started_at": started_at.isoformat(),
        "completed_at": completed_at.isoformat(),
        "runs": runs,
        "best_by_metric": best_by_metric,
        "warnings": warnings,
        "notes": config.get("description"),
    }
    write_benchmark_summary(report, output_dir)
    return report
