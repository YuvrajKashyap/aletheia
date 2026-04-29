from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def ensure_benchmark_reports_dir(output_dir: str = "reports/benchmarks") -> str:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def write_benchmark_summary(report: dict, output_dir: str) -> str:
    reports_dir = Path(ensure_benchmark_reports_dir(output_dir))
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_path = reports_dir / f"final-benchmark-suite-{timestamp}.json"
    report["report_path"] = str(report_path)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return str(report_path)


def _metric(value: object, digits: int = 4) -> str:
    if isinstance(value, int | float):
        return f"{float(value):.{digits}f}"
    return "n/a"


def _latency(value: object) -> str:
    if isinstance(value, int | float):
        return f"{float(value):.1f}"
    return "n/a"


def _text(value: object) -> str:
    if value is None:
        return "n/a"
    text = str(value).replace("\n", " ").replace("|", "\\|").strip()
    return text if text else "n/a"


def format_markdown_benchmark_table(report: dict) -> str:
    rows = report.get("runs", [])
    if not isinstance(rows, list):
        rows = []

    lines = [
        "| Mode | Scope | Queries | Failed | Recall@5 | Recall@10 | MRR@10 | NDCG@10 | Avg ms | P95 ms | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        if not isinstance(row, dict):
            continue
        lines.append(
            " | ".join(
                [
                    f"| {_text(row.get('retrieval_mode'))}",
                    _text(row.get("scope")),
                    _text(row.get("query_count")),
                    _text(row.get("failed_query_count")),
                    _metric(row.get("recall_at_5")),
                    _metric(row.get("recall_at_10")),
                    _metric(row.get("mrr_at_10")),
                    _metric(row.get("ndcg_at_10")),
                    _latency(row.get("avg_latency_ms")),
                    _latency(row.get("p95_latency_ms")),
                    f"{_text(row.get('notes') or row.get('error'))} |",
                ]
            )
        )
    return "\n".join(lines)
