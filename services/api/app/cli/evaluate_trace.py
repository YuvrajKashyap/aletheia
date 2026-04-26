from __future__ import annotations

import argparse
import json
import sys
from uuid import UUID

from app.db.session import SessionLocal
from app.evaluation.correctness import evaluate_trace_against_benchmark_query


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate one stored search trace against qrels.")
    parser.add_argument("--trace-id", required=True)
    parser.add_argument("--benchmark-query-id")
    parser.add_argument("--query-external-id")
    parser.add_argument("--dataset-name", default="beir/scifact")
    parser.add_argument("--dataset-version", default="test")
    parser.add_argument("--text", action="store_true")
    return parser.parse_args()


def _uuid_or_none(value: str | None):
    return UUID(value) if value else None


def _print_text(payload: dict) -> None:
    print(f"trace_id: {payload['trace_id']}")
    print(f"retrieval_mode: {payload['retrieval_mode']}")
    print(f"query_external_id: {payload['query_external_id']}")
    print("metrics:")
    for key, value in payload["metrics"].items():
        print(f"  {key}: {value}")
    print("matched_relevant_document_ids:")
    for document_id in payload["matched_relevant_document_ids"]:
        print(f"  {document_id}")
    print("missed_relevant_document_ids:")
    for document_id in payload["missed_relevant_document_ids"]:
        print(f"  {document_id}")


def main() -> int:
    args = parse_args()
    try:
        with SessionLocal() as db:
            payload = evaluate_trace_against_benchmark_query(
                db,
                trace_id=UUID(args.trace_id),
                benchmark_query_id=_uuid_or_none(args.benchmark_query_id),
                query_external_id=args.query_external_id,
                dataset_name=args.dataset_name,
                dataset_version=args.dataset_version,
            )
        if args.text:
            _print_text(payload)
        else:
            print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
