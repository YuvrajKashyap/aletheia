from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

from app.db.session import SessionLocal
from app.experiments.comparison import run_evaluation_comparison


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a synchronous evaluation comparison.")
    parser.add_argument("--name")
    parser.add_argument("--use-defaults", action="store_true")
    parser.add_argument("--config-id", action="append", dest="config_ids")
    parser.add_argument("--config-name", action="append", dest="config_names")
    parser.add_argument("--dataset-name", default="beir/scifact")
    parser.add_argument("--dataset-version", default="test")
    parser.add_argument("--index-version-id")
    parser.add_argument("--query-limit", type=int)
    parser.add_argument("--query-offset", type=int, default=0)
    parser.add_argument("--notes")
    return parser.parse_args()


def _default_name() -> str:
    return f"comparison {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


def main() -> int:
    args = parse_args()
    try:
        with SessionLocal() as db:
            summary = run_evaluation_comparison(
                db,
                name=args.name or _default_name(),
                experiment_config_ids=args.config_ids,
                experiment_config_names=args.config_names,
                use_defaults=args.use_defaults,
                dataset_name=args.dataset_name,
                dataset_version=args.dataset_version,
                index_version_id=args.index_version_id,
                query_limit=args.query_limit,
                query_offset=args.query_offset,
                notes=args.notes,
            )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
