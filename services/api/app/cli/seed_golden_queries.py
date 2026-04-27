from __future__ import annotations

import argparse
import json
import sys

from app.db.session import SessionLocal
from app.replay.service import seed_golden_queries_from_scifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed saved golden queries from SciFact qrels.")
    parser.add_argument("--dataset-name", default="beir/scifact")
    parser.add_argument("--dataset-version", default="test")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--offset", type=int, default=0)
    return parser.parse_args()


def _item(saved_query) -> dict:
    return {
        "id": str(saved_query.id),
        "name": saved_query.name,
        "text": saved_query.text,
        "source": saved_query.source,
        "dataset_id": str(saved_query.dataset_id) if saved_query.dataset_id else None,
        "metadata_json": saved_query.metadata_json,
    }


def main() -> int:
    args = parse_args()
    try:
        with SessionLocal() as db:
            result = seed_golden_queries_from_scifact(
                db,
                dataset_name=args.dataset_name,
                dataset_version=args.dataset_version,
                limit=args.limit,
                offset=args.offset,
            )
            payload = {
                "created_count": result["created_count"],
                "existing_count": result["existing_count"],
                "total_selected": result["total_selected"],
                "items": [_item(item) for item in result["items"]],
            }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
