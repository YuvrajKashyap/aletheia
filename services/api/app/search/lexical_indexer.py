from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from time import perf_counter
from typing import Any
from uuid import UUID

from opensearchpy import NotFoundError
from opensearchpy.helpers import streaming_bulk
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.indexing import statuses
from app.models.datasets import Chunk, Dataset, Document
from app.models.indexing import IndexJob, IndexVersion
from app.search.lexical_mapping import build_lexical_index_body

LEXICAL_INDEX_JOB_TYPE = "lexical_index_build"


def _utc_now() -> datetime:
    from datetime import timezone

    return datetime.now(timezone.utc)


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _count(db: Session, statement) -> int:
    return int(db.scalar(statement) or 0)


def ensure_lexical_index(client, index_name: str, recreate: bool = False) -> dict:
    exists = client.indices.exists(index=index_name)
    if exists and recreate:
        client.indices.delete(index=index_name)
        exists = False

    if not exists:
        client.indices.create(index=index_name, body=build_lexical_index_body())
        return {"index_name": index_name, "created": True, "recreated": recreate}

    return {"index_name": index_name, "created": False, "recreated": False}


def chunk_to_opensearch_doc(chunk, document, dataset) -> dict:
    return {
        "chunk_id": str(chunk.id),
        "document_id": str(document.id),
        "dataset_id": str(dataset.id),
        "document_external_id": document.external_id,
        "chunk_external_id": chunk.external_id,
        "chunk_index": chunk.chunk_index,
        "title": document.title,
        "text": chunk.text,
        "token_count": chunk.token_count,
        "content_hash": chunk.content_hash,
        "chunking_strategy": chunk.chunking_strategy,
        "chunking_version": chunk.chunking_version,
        "metadata_json": dict(chunk.metadata_json or {}),
        "created_at": _iso(getattr(chunk, "created_at", None)),
    }


def iter_chunks_for_indexing(
    db: Session,
    dataset_id: UUID,
    chunking_strategy: str | None = None,
    chunking_version: str | None = None,
    limit: int | None = None,
) -> Iterator[tuple[Chunk, Document, Dataset]]:
    statement = (
        select(Chunk, Document, Dataset)
        .join(Document, Chunk.document_id == Document.id)
        .join(Dataset, Chunk.dataset_id == Dataset.id)
        .where(Chunk.dataset_id == dataset_id)
        .order_by(Document.external_id.asc(), Chunk.chunk_index.asc(), Chunk.id.asc())
    )
    if chunking_strategy is not None:
        statement = statement.where(Chunk.chunking_strategy == chunking_strategy)
    if chunking_version is not None:
        statement = statement.where(Chunk.chunking_version == chunking_version)
    if limit is not None:
        statement = statement.limit(limit)

    for row in db.execute(statement):
        yield row[0], row[1], row[2]


def _chunk_count(
    db: Session,
    dataset_id: UUID,
    chunking_strategy: str | None = None,
    chunking_version: str | None = None,
    limit: int | None = None,
) -> int:
    statement = select(func.count()).select_from(Chunk).where(Chunk.dataset_id == dataset_id)
    if chunking_strategy is not None:
        statement = statement.where(Chunk.chunking_strategy == chunking_strategy)
    if chunking_version is not None:
        statement = statement.where(Chunk.chunking_version == chunking_version)
    count = _count(db, statement)
    return min(count, limit) if limit is not None else count


def _document_count(db: Session, dataset_id: UUID) -> int:
    return _count(db, select(func.count()).select_from(Document).where(Document.dataset_id == dataset_id))


def get_index_document_count(client, index_name: str) -> int:
    try:
        return int(client.count(index=index_name).get("count", 0))
    except NotFoundError:
        return 0


def bulk_index_chunks(
    db: Session,
    client,
    index_name: str,
    dataset_id: UUID,
    chunking_strategy: str | None = None,
    chunking_version: str | None = None,
    batch_size: int = 500,
    limit: int | None = None,
    refresh: bool = True,
) -> dict:
    chunks_seen = 0
    chunks_indexed = 0
    chunks_failed = 0
    errors: list[str] = []

    def actions() -> Iterator[dict]:
        nonlocal chunks_seen
        for chunk, document, dataset in iter_chunks_for_indexing(
            db,
            dataset_id=dataset_id,
            chunking_strategy=chunking_strategy,
            chunking_version=chunking_version,
            limit=limit,
        ):
            chunks_seen += 1
            yield {
                "_op_type": "index",
                "_index": index_name,
                "_id": str(chunk.id),
                "_source": chunk_to_opensearch_doc(chunk, document, dataset),
            }

    for ok, item in streaming_bulk(
        client,
        actions(),
        chunk_size=batch_size,
        raise_on_error=False,
        raise_on_exception=False,
    ):
        if ok:
            chunks_indexed += 1
        else:
            chunks_failed += 1
            if len(errors) < 10:
                errors.append(str(item))

    if refresh:
        client.indices.refresh(index=index_name)

    return {
        "index_name": index_name,
        "chunks_seen": chunks_seen,
        "chunks_indexed": chunks_indexed,
        "chunks_failed": chunks_failed,
        "errors": errors,
        "refresh": refresh,
        "opensearch_count": get_index_document_count(client, index_name),
    }


def build_lexical_index_for_version(
    db: Session,
    client,
    index_version_id: UUID,
    recreate: bool = False,
    limit: int | None = None,
    refresh: bool = True,
    rq_job_id: str | None = None,
) -> dict:
    started = perf_counter()
    index_version = db.get(IndexVersion, index_version_id)
    if index_version is None:
        raise ValueError(f"Index version not found: {index_version_id}")
    if not index_version.dataset_id:
        raise ValueError("Index version must have a dataset_id.")
    if not index_version.lexical_index_name:
        raise ValueError("Index version must have a lexical_index_name.")

    chunks_total = _chunk_count(
        db,
        dataset_id=index_version.dataset_id,
        chunking_strategy=index_version.chunking_strategy,
        chunking_version=index_version.chunking_version,
        limit=limit,
    )
    index_job = IndexJob(
        index_version_id=index_version.id,
        job_id=rq_job_id,
        job_type=LEXICAL_INDEX_JOB_TYPE,
        status="running",
        started_at=_utc_now(),
        chunks_total=chunks_total,
        config_json={
            "recreate": recreate,
            "limit": limit,
            "refresh": refresh,
            "index_name": index_version.lexical_index_name,
        },
    )
    db.add(index_job)
    if index_version.status in {statuses.PENDING, statuses.BUILDING}:
        index_version.status = statuses.BUILDING
    db.commit()
    db.refresh(index_job)

    try:
        ensure_lexical_index(client, index_version.lexical_index_name, recreate=recreate)
        bulk_summary = bulk_index_chunks(
            db,
            client,
            index_name=index_version.lexical_index_name,
            dataset_id=index_version.dataset_id,
            chunking_strategy=index_version.chunking_strategy,
            chunking_version=index_version.chunking_version,
            batch_size=get_settings().LEXICAL_INDEX_BATCH_SIZE,
            limit=limit,
            refresh=refresh,
        )

        index_job.chunks_total = chunks_total
        index_job.chunks_completed = bulk_summary["chunks_indexed"]
        index_job.chunks_failed = bulk_summary["chunks_failed"]
        index_job.status = "completed" if bulk_summary["chunks_failed"] == 0 else "failed"
        index_job.completed_at = _utc_now()
        if bulk_summary["chunks_failed"]:
            index_job.error_message = "One or more chunks failed during OpenSearch bulk indexing."

        index_version.document_count = _document_count(db, index_version.dataset_id)
        index_version.chunk_count = chunks_total
        config = dict(index_version.config_json or {})
        config.update(
            {
                "lexical_built": bulk_summary["chunks_failed"] == 0,
                "vector_built": False,
                "last_lexical_index_job_id": str(index_job.id),
                "last_lexical_index_name": index_version.lexical_index_name,
                "last_lexical_index_count": bulk_summary["opensearch_count"],
            }
        )
        index_version.config_json = config
        if index_version.status in {statuses.PENDING, statuses.BUILDING} and not bulk_summary["chunks_failed"]:
            index_version.status = statuses.READY

        db.commit()
        db.refresh(index_job)
        db.refresh(index_version)
    except Exception as exc:
        index_job.status = "failed"
        index_job.completed_at = _utc_now()
        index_job.error_message = str(exc)
        index_job.chunks_failed = chunks_total
        config = dict(index_version.config_json or {})
        config.update({"lexical_built": False, "vector_built": False, "last_lexical_error": str(exc)})
        index_version.config_json = config
        if index_version.status in {statuses.PENDING, statuses.BUILDING}:
            index_version.status = statuses.FAILED
        db.commit()
        raise

    return {
        "index_version_id": str(index_version.id),
        "index_name": index_version.lexical_index_name,
        "index_job_id": str(index_job.id),
        "status": index_job.status,
        "chunks_total": chunks_total,
        "chunks_seen": bulk_summary["chunks_seen"],
        "chunks_indexed": bulk_summary["chunks_indexed"],
        "chunks_failed": bulk_summary["chunks_failed"],
        "opensearch_count": bulk_summary["opensearch_count"],
        "recreate": recreate,
        "refresh": refresh,
        "limit": limit,
        "duration_ms": round((perf_counter() - started) * 1000, 2),
    }
