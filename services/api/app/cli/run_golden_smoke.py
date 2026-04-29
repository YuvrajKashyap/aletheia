from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.db.session import SessionLocal
from app.evaluation.runner import run_offline_evaluation
from app.evaluation.smoke import (
    evaluate_smoke_thresholds,
    load_smoke_thresholds,
    write_smoke_report,
)


SUPPORTED_MODES = ("bm25", "dense", "hybrid", "hybrid_rerank")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def resolve_repo_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return repo_root() / path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a local qrels-backed golden retrieval smoke check."
    )
    parser.add_argument("--mode", choices=SUPPORTED_MODES, default="hybrid")
    parser.add_argument("--query-limit", type=int, default=5)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--thresholds", default="configs/golden-smoke-thresholds.json")
    parser.add_argument("--output", default="reports/smoke/golden-smoke-latest.json")
    parser.add_argument("--fail-on-threshold", action="store_true")
    parser.add_argument("--notes")
    return parser.parse_args()


def _summary_metrics(summary: dict) -> dict:
    aggregate_metrics = summary.get("aggregate_metrics", {})
    if not isinstance(aggregate_metrics, dict):
        aggregate_metrics = {}
    return {
        "query_count": summary.get("query_count"),
        "failed_query_count": summary.get("failed_query_count"),
        "recall_at_10": aggregate_metrics.get("recall_at_10"),
        "mrr_at_10": aggregate_metrics.get("mrr_at_10"),
        "ndcg_at_10": aggregate_metrics.get("ndcg_at_10"),
        "retrieval_mode": summary.get("retrieval_mode"),
    }


def main() -> int:
    args = parse_args()
    threshold_path = resolve_repo_path(args.thresholds)
    output_path = resolve_repo_path(args.output)

    try:
        threshold_config = load_smoke_thresholds(str(threshold_path))
        generated_at = datetime.now(timezone.utc).isoformat()
        name = f"Golden smoke {args.mode}"
        notes = args.notes or "Local qrels-backed golden smoke run"

        with SessionLocal() as db:
            evaluation_summary = run_offline_evaluation(
                db,
                name=name,
                retrieval_mode=args.mode,
                dataset_name="beir/scifact",
                dataset_version="test",
                query_limit=args.query_limit,
                top_k=args.top_k,
                notes=notes,
            )

        summary_metrics = _summary_metrics(evaluation_summary)
        summary_metrics["top_k"] = args.top_k
        threshold_result = evaluate_smoke_thresholds(summary_metrics, threshold_config)

        report = {
            "generated_at": generated_at,
            "name": name,
            "notes": notes,
            "retrieval_mode": args.mode,
            "query_limit": args.query_limit,
            "top_k": args.top_k,
            "evaluation_run_id": evaluation_summary.get("evaluation_run_id"),
            "summary": summary_metrics,
            "thresholds_config_path": str(threshold_path),
            "threshold_result": threshold_result,
            "report_output_path": str(output_path),
            "evaluation_summary": evaluation_summary,
        }
        written_path = write_smoke_report(report, str(output_path))
        report["report_output_path"] = written_path

        print(
            json.dumps(
                {
                    "status": threshold_result["status"],
                    "mode": threshold_result["mode"],
                    "evaluation_run_id": report["evaluation_run_id"],
                    "retrieval_mode": args.mode,
                    "query_limit": args.query_limit,
                    "top_k": args.top_k,
                    "report_output_path": written_path,
                    "warnings": threshold_result["warnings"],
                    "failures": threshold_result["failures"],
                },
                indent=2,
                sort_keys=True,
            )
        )
        if args.fail_on_threshold and threshold_result["status"] == "fail":
            return 1
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
