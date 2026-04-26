import argparse
import json
import sys

from app.chunking.service import chunk_dataset_documents
from app.db.session import SessionLocal
from app.text.chunking import SCIFACT_CHUNKING_STRATEGY, SCIFACT_CHUNKING_VERSION


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate database chunks for loaded documents.")
    parser.add_argument("--dataset-name", default="beir/scifact")
    parser.add_argument("--dataset-version", default="test")
    parser.add_argument("--document-limit", type=int, default=None)
    parser.add_argument("--strategy", default=SCIFACT_CHUNKING_STRATEGY)
    parser.add_argument("--chunking-version", default=SCIFACT_CHUNKING_VERSION)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        with SessionLocal() as db:
            summary = chunk_dataset_documents(
                db,
                dataset_name=args.dataset_name,
                dataset_version=args.dataset_version,
                document_limit=args.document_limit,
                strategy=args.strategy,
                chunking_version=args.chunking_version,
                dry_run=args.dry_run,
            )
        print(json.dumps(summary.to_dict(), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
