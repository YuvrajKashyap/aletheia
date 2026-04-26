import argparse
import json
import sys

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.indexing.service import (
    create_index_version,
    get_dataset_by_name_version,
    mark_index_version_ready,
)
from app.schemas.indexes import IndexVersionItem


def parse_args() -> argparse.Namespace:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Create metadata-only index version records.")
    parser.add_argument("--dataset-name", default="beir/scifact")
    parser.add_argument("--dataset-version", default="test")
    parser.add_argument("--chunking-strategy", default="scifact_document_v1")
    parser.add_argument("--chunking-version", default="1.0")
    parser.add_argument("--embedding-model", default=settings.EMBEDDING_MODEL)
    parser.add_argument("--embedding-dimension", type=int, default=None)
    parser.add_argument("--notes", default=None)
    parser.add_argument("--mark-ready", action="store_true")
    return parser.parse_args()


def _serialize(index_version) -> dict:
    return IndexVersionItem(
        id=index_version.id,
        dataset_id=index_version.dataset_id,
        name=index_version.name,
        status=index_version.status,
        is_active=index_version.is_active,
        lexical_index_name=index_version.lexical_index_name,
        vector_collection_name=index_version.vector_collection_name,
        embedding_model=index_version.embedding_model,
        embedding_dimension=index_version.embedding_dimension,
        chunking_strategy=index_version.chunking_strategy,
        chunking_version=index_version.chunking_version,
        document_count=index_version.document_count,
        chunk_count=index_version.chunk_count,
        vector_count=index_version.vector_count,
        config_json=index_version.config_json,
        notes=index_version.notes,
        created_at=index_version.created_at,
        updated_at=index_version.updated_at,
        activated_at=index_version.activated_at,
    ).model_dump(mode="json")


def main() -> int:
    args = parse_args()
    try:
        with SessionLocal() as db:
            dataset = get_dataset_by_name_version(db, args.dataset_name, args.dataset_version)
            if dataset is None:
                raise ValueError(f"Dataset not found: {args.dataset_name} version {args.dataset_version}")

            index_version = create_index_version(
                db,
                dataset_id=dataset.id,
                embedding_model=args.embedding_model,
                embedding_dimension=args.embedding_dimension,
                chunking_strategy=args.chunking_strategy,
                chunking_version=args.chunking_version,
                notes=args.notes,
                config_json={"created_by": "cli", "metadata_only": True},
            )
            if args.mark_ready:
                index_version = mark_index_version_ready(db, index_version.id)

        print(json.dumps(_serialize(index_version), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
