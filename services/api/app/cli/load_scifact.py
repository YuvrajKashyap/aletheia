import argparse
import json
import sys

from app.db.session import SessionLocal
from app.ingestion.service import run_scifact_ingestion


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load BEIR SciFact data into PostgreSQL.")
    parser.add_argument("--document-limit", type=int, default=None)
    parser.add_argument("--query-limit", type=int, default=None)
    parser.add_argument("--qrel-limit", type=int, default=None)
    parser.add_argument("--split", default="test")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-chunk", action="store_true")
    parser.add_argument("--chunk-document-limit", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        with SessionLocal() as db:
            summary = run_scifact_ingestion(
                db,
                document_limit=args.document_limit,
                query_limit=args.query_limit,
                qrel_limit=args.qrel_limit,
                split=args.split,
                dry_run=args.dry_run,
                chunk_after_load=not args.no_chunk,
                chunk_document_limit=args.chunk_document_limit,
                started_by="cli",
            )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
