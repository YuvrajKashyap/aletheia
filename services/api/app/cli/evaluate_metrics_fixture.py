from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from app.evaluation.latency import summarize_latencies
from app.evaluation.metrics import aggregate_query_metrics, evaluate_single_query


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate benchmark metrics from a JSON fixture.")
    parser.add_argument("--input", required=True, help="Path to a JSON metrics fixture.")
    return parser.parse_args()


def load_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    with fixture_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload.get("queries"), list):
        raise ValueError("Fixture must contain a 'queries' list.")
    return payload


def evaluate_fixture(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload.get("queries"), list):
        raise ValueError("Fixture must contain a 'queries' list.")

    per_query = []
    metric_rows = []
    for item in payload["queries"]:
        query_id = item.get("query_id")
        metrics = evaluate_single_query(
            retrieved_document_ids=item.get("retrieved_document_ids") or [],
            relevant_document_ids=item.get("relevant_document_ids") or [],
            relevance_by_id=item.get("relevance_by_id"),
        )
        per_query.append({"query_id": query_id, "metrics": metrics})
        metric_rows.append(metrics)

    return {
        "per_query": per_query,
        "aggregate": aggregate_query_metrics(metric_rows),
        "latency_summary": summarize_latencies(payload.get("latencies_ms") or []),
    }


def main() -> int:
    args = parse_args()
    try:
        output = evaluate_fixture(load_fixture(args.input))
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2, sort_keys=True))
        return 1


if __name__ == "__main__":
    sys.exit(main())
