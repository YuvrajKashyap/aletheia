from __future__ import annotations

import argparse
import json
import sys
from uuid import UUID

from sqlalchemy import select

from app.db.session import SessionLocal
from app.indexing.service import get_active_index_version, get_dataset_by_name_version
from app.models.indexing import IndexVersion
from app.search.vector_indexer import build_vector_index_for_version


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Qdrant vector index.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--index-version-id")
    target.add_argument("--active", action="store_true")
    parser.add_argument("--recreate", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--batch-size", type=int)
    return parser.parse_args()


def _active_index_version_id(db) -> UUID:
    dataset = get_dataset_by_name_version(db, "beir/scifact", "test")
    if dataset is not None:
        active = get_active_index_version(db, dataset.id)
        if active is not None:
            return active.id

    active = db.scalar(select(IndexVersion).where(IndexVersion.is_active.is_(True)).limit(1))
    if active is None:
        raise ValueError("No active index version found.")
    return active.id


def main() -> int:
    args = parse_args()
    db = SessionLocal()
    try:
        index_version_id = _active_index_version_id(db) if args.active else UUID(args.index_version_id)
        summary = build_vector_index_for_version(
            db,
            index_version_id=index_version_id,
            recreate=args.recreate,
            limit=args.limit,
            batch_size=args.batch_size,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
