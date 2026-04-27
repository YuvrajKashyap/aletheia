from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.evaluation.runner import run_offline_evaluation
from app.experiments.defaults import get_default_experiment_configs
from app.experiments.reporting import write_comparison_report
from app.experiments.service import (
    get_experiment_config,
    get_experiment_config_by_name,
    seed_default_experiment_configs,
)
from app.models.experiments import ExperimentConfig


def _resolve_configs(
    db: Session,
    experiment_config_ids: list[str] | None,
    experiment_config_names: list[str] | None,
    use_defaults: bool,
) -> list[ExperimentConfig]:
    configs: list[ExperimentConfig] = []
    if use_defaults:
        seed_default_experiment_configs(db)
        for spec in get_default_experiment_configs():
            config = get_experiment_config_by_name(db, spec["name"])
            if config is None:
                raise LookupError(f"Default experiment config missing after seed: {spec['name']}")
            configs.append(config)
    for config_id in experiment_config_ids or []:
        config = get_experiment_config(db, config_id)
        if config is None:
            raise LookupError(f"Experiment config not found: {config_id}")
        configs.append(config)
    for name in experiment_config_names or []:
        config = get_experiment_config_by_name(db, name)
        if config is None:
            raise LookupError(f"Experiment config not found: {name}")
        configs.append(config)

    seen: set[str] = set()
    deduped: list[ExperimentConfig] = []
    for config in configs:
        key = str(config.id)
        if key not in seen:
            seen.add(key)
            deduped.append(config)
    if not deduped:
        raise ValueError("At least one experiment config is required for comparison")
    return deduped


def _metric_value(row: dict[str, Any], metric: str) -> float | None:
    value = row.get(metric)
    return float(value) if value is not None else None


def _best_max(rows: list[dict[str, Any]], metric: str) -> dict[str, Any] | None:
    candidates = [row for row in rows if _metric_value(row, metric) is not None]
    if not candidates:
        return None
    best = max(candidates, key=lambda row: (_metric_value(row, metric), -rows.index(row)))
    return {
        "metric": metric,
        "experiment_config_id": best["experiment_config_id"],
        "experiment_config_name": best["experiment_config_name"],
        "evaluation_run_id": best["evaluation_run_id"],
        "value": best[metric],
    }


def _best_min(rows: list[dict[str, Any]], metric: str) -> dict[str, Any] | None:
    candidates = [row for row in rows if _metric_value(row, metric) is not None]
    if not candidates:
        return None
    best = min(candidates, key=lambda row: (_metric_value(row, metric), rows.index(row)))
    return {
        "metric": metric,
        "experiment_config_id": best["experiment_config_id"],
        "experiment_config_name": best["experiment_config_name"],
        "evaluation_run_id": best["evaluation_run_id"],
        "value": best[metric],
    }


def _comparison_row(config: ExperimentConfig, summary: dict[str, Any]) -> dict[str, Any]:
    aggregate = summary.get("aggregate_metrics", {})
    latency = summary.get("latency_summary", {})
    return {
        "experiment_config_id": str(config.id),
        "experiment_config_name": config.name,
        "evaluation_run_id": summary.get("evaluation_run_id"),
        "retrieval_mode": config.retrieval_mode,
        "query_count": summary.get("query_count", aggregate.get("query_count", 0)),
        "failed_query_count": summary.get(
            "failed_query_count",
            aggregate.get("failed_query_count", 0),
        ),
        "recall_at_5": aggregate.get("recall_at_5"),
        "recall_at_10": aggregate.get("recall_at_10"),
        "mrr_at_10": aggregate.get("mrr_at_10"),
        "ndcg_at_10": aggregate.get("ndcg_at_10"),
        "avg_latency_ms": latency.get("avg_latency_ms"),
        "p50_latency_ms": latency.get("p50_latency_ms"),
        "p95_latency_ms": latency.get("p95_latency_ms"),
        "report_path": summary.get("report_path"),
    }


def run_evaluation_comparison(
    db: Session,
    name: str,
    experiment_config_ids: list[str] | None = None,
    experiment_config_names: list[str] | None = None,
    use_defaults: bool = False,
    dataset_name: str = "beir/scifact",
    dataset_version: str = "test",
    index_version_id: str | None = None,
    query_limit: int | None = None,
    query_offset: int = 0,
    notes: str | None = None,
) -> dict[str, Any]:
    comparison_name = (name or "").strip() or f"comparison {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    configs = _resolve_configs(db, experiment_config_ids, experiment_config_names, use_defaults)
    rows: list[dict[str, Any]] = []
    evaluation_run_ids: list[str] = []

    for config in configs:
        summary = run_offline_evaluation(
            db,
            name=f"{comparison_name} - {config.name}",
            retrieval_mode=config.retrieval_mode,
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            index_version_id=index_version_id,
            query_limit=query_limit,
            query_offset=query_offset,
            notes=notes,
            experiment_config_id=str(config.id),
        )
        evaluation_run_ids.append(str(summary["evaluation_run_id"]))
        rows.append(_comparison_row(config, summary))

    best_by_metric = {
        "recall_at_10": _best_max(rows, "recall_at_10"),
        "mrr_at_10": _best_max(rows, "mrr_at_10"),
        "ndcg_at_10": _best_max(rows, "ndcg_at_10"),
        "avg_latency_ms": _best_min(rows, "avg_latency_ms"),
    }
    report = {
        "comparison_name": comparison_name,
        "dataset": {
            "name": dataset_name,
            "version": dataset_version,
        },
        "query_limit": query_limit,
        "query_offset": query_offset,
        "evaluation_run_ids": evaluation_run_ids,
        "rows": rows,
        "best_by_metric": best_by_metric,
        "notes": notes,
    }
    report_path = write_comparison_report(report, comparison_name)
    return {**report, "report_path": report_path}
