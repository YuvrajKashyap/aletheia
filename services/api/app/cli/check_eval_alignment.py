from __future__ import annotations

import argparse
import json
import sys

from app.db.session import SessionLocal
from app.evaluation.correctness import validate_dataset_qrels_alignment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check benchmark qrels alignment for evaluation.")
    parser.add_argument("--dataset-name", default="beir/scifact")
    parser.add_argument("--dataset-version", default="test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        with SessionLocal() as db:
            summary = validate_dataset_qrels_alignment(
                db,
                dataset_name=args.dataset_name,
                dataset_version=args.dataset_version,
            )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0 if summary.get("ready_for_evaluation") else 1
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
