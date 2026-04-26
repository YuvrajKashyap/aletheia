from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from time import perf_counter
from uuid import UUID

from qdrant_client.models import Distance, PointStruct, VectorParams
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.indexing import statuses
from app.ml.embeddings import embed_texts, get_embedding_dimension
from app.models.datasets import Chunk, Dataset, Document
from app.models.indexing import IndexJob, IndexVersion
from app.search.qdrant_client import get_qdrant_client

VECTOR_INDEX_JOB_TYPE = "vector_index_build"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _count(db: Session, statement) -> int:
    return int(db.scalar(statement) or 0)


def _distance(value: str) -> Distance:
    normalized = value.strip().lower()
    if normalized == "cosine":
        return Distance.COSINE
    if normalized == "dot":
        return Distance.DOT
    if normalized in {"euclid", "euclidean"}:
        return Distance.EUCLID
    raise ValueError(f"Unsupported Qdrant vector distance: {value}")


def _collection_exists(client, collection_name: str) -> bool:
    if hasattr(client, "collection_exists"):
        return bool(client.collection_exists(collection_name=collection_name))
    try:
        client.get_collection(collection_name=collection_name)
        return True
    except Exception:
        return False


def ensure_vector_collection(
    client,
    collection_name: str,
    vector_size: int,
    distance: str = "Cosine",
    recreate: bool = False,
) -> dict:
    if vector_size <= 0:
        raise ValueError("Vector size must be greater than 0.")
    resolved_distance = _distance(distance)

    existed = _collection_exists(client, collection_name)
    if existed and recreate:
        client.delete_collection(collection_name=collection_name)
        existed = False

    created = False
    if not existed:
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=resolved_distance),
        )
        created = True

    return {
        "collection_name": collection_name,
        "vector_size": vector_size,
        "distance": distance,
        "created": created,
        "recreated": recreate and created,
        "existed": existed,
    }


def chunk_to_qdrant_payload(chunk, document, dataset, index_version) -> dict:
    return {
        "chunk_id": str(chunk.id),
        "document_id": str(document.id),
        "dataset_id": str(dataset.id),
        "index_version_id": str(index_version.id),
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
    }


def iter_chunks_for_vector_indexing(
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
    chunking_strategy: str | None,
    chunking_version: str | None,
    limit: int | None,
) -> int:
    statement = select(func.count()).select_from(Chunk).where(Chunk.dataset_id == dataset_id)
    if chunking_strategy is not None:
        statement = statement.where(Chunk.chunking_strategy == chunking_strategy)
    if chunking_version is not None:
        statement = statement.where(Chunk.chunking_version == chunking_version)
    total = _count(db, statement)
    return min(total, limit) if limit is not None else total


def get_collection_vector_count(client, collection_name: str) -> int:
    result = client.count(collection_name=collection_name, exact=True)
    return int(getattr(result, "count", result.get("count", 0) if isinstance(result, dict) else 0))


def _upsert_batch(client, collection_name: str, rows: list, vectors: list[list[float]], index_version) -> int:
    points = []
    for (chunk, document, dataset), vector in zip(rows, vectors, strict=True):
        points.append(
            PointStruct(
                id=str(chunk.id),
                vector=vector,
                payload=chunk_to_qdrant_payload(chunk, document, dataset, index_version),
            )
        )
    if points:
        client.upsert(collection_name=collection_name, points=points)
    return len(points)


def build_vector_index_for_version(
    db: Session,
    index_version_id,
    recreate: bool = False,
    limit: int | None = None,
    batch_size: int | None = None,
    rq_job_id: str | None = None,
) -> dict:
    started = perf_counter()
    settings = get_settings()
    resolved_batch_size = batch_size or settings.VECTOR_INDEX_BATCH_SIZE
    if resolved_batch_size < 1:
        raise ValueError("Batch size must be at least 1.")

    index_version = db.get(IndexVersion, UUID(str(index_version_id)))
    if index_version is None:
        raise ValueError(f"Index version not found: {index_version_id}")
    if not index_version.dataset_id:
        raise ValueError("Index version must have a dataset_id.")
    if not index_version.vector_collection_name:
        raise ValueError("Index version must have a vector_collection_name.")

    embedding_model = index_version.embedding_model or settings.EMBEDDING_MODEL
    embedding_dimension = (
        index_version.embedding_dimension
        or get_embedding_dimension(embedding_model, load_if_needed=False)
        or settings.EMBEDDING_DIMENSION
    )
    chunks_total = _chunk_count(
        db,
        index_version.dataset_id,
        index_version.chunking_strategy,
        index_version.chunking_version,
        limit,
    )
    index_job = IndexJob(
        index_version_id=index_version.id,
        job_id=rq_job_id,
        job_type=VECTOR_INDEX_JOB_TYPE,
        status="running",
        started_at=_utc_now(),
        chunks_total=chunks_total,
        config_json={
            "recreate": recreate,
            "limit": limit,
            "batch_size": resolved_batch_size,
            "collection_name": index_version.vector_collection_name,
        },
    )
    db.add(index_job)
    if index_version.status in {statuses.PENDING, statuses.BUILDING}:
        index_version.status = statuses.BUILDING
    db.commit()
    db.refresh(index_job)

    client = get_qdrant_client()
    chunks_seen = 0
    vectors_upserted = 0
    chunks_failed = 0
    errors: list[str] = []

    try:
        ensure_vector_collection(
            client,
            collection_name=index_version.vector_collection_name,
            vector_size=embedding_dimension,
            distance=settings.VECTOR_DISTANCE,
            recreate=recreate,
        )
        batch: list[tuple[Chunk, Document, Dataset]] = []
        for row in iter_chunks_for_vector_indexing(
            db,
            index_version.dataset_id,
            chunking_strategy=index_version.chunking_strategy,
            chunking_version=index_version.chunking_version,
            limit=limit,
        ):
            chunks_seen += 1
            batch.append(row)
            if len(batch) >= resolved_batch_size:
                texts = [chunk.text for chunk, _, _ in batch]
                vectors = embed_texts(texts, model_name=embedding_model, batch_size=resolved_batch_size)
                vectors_upserted += _upsert_batch(client, index_version.vector_collection_name, batch, vectors, index_version)
                batch = []

        if batch:
            texts = [chunk.text for chunk, _, _ in batch]
            vectors = embed_texts(texts, model_name=embedding_model, batch_size=resolved_batch_size)
            vectors_upserted += _upsert_batch(client, index_version.vector_collection_name, batch, vectors, index_version)

        qdrant_count = get_collection_vector_count(client, index_version.vector_collection_name)
        index_job.chunks_total = chunks_total
        index_job.chunks_completed = vectors_upserted
        index_job.chunks_failed = chunks_failed
        index_job.status = "completed"
        index_job.completed_at = _utc_now()
        index_version.vector_count = qdrant_count
        index_version.embedding_model = embedding_model
        index_version.embedding_dimension = embedding_dimension
        config = dict(index_version.config_json or {})
        config.update(
            {
                "vector_built": True,
                "qdrant_collection": index_version.vector_collection_name,
                "embedding_model": embedding_model,
                "embedding_dimension": embedding_dimension,
                "last_vector_index_job_id": str(index_job.id),
            }
        )
        index_version.config_json = config
        if index_version.status in {statuses.PENDING, statuses.BUILDING}:
            index_version.status = statuses.READY
        db.commit()
        db.refresh(index_job)
        db.refresh(index_version)
    except Exception as exc:
        chunks_failed = max(chunks_total - vectors_upserted, 0)
        errors.append(str(exc))
        index_job.status = "failed"
        index_job.completed_at = _utc_now()
        index_job.chunks_completed = vectors_upserted
        index_job.chunks_failed = chunks_failed
        index_job.error_message = str(exc)
        config = dict(index_version.config_json or {})
        config.update({"vector_built": False, "last_vector_error": str(exc)})
        index_version.config_json = config
        if index_version.status in {statuses.PENDING, statuses.BUILDING}:
            index_version.status = statuses.FAILED
        db.commit()
        raise

    return {
        "index_version_id": str(index_version.id),
        "collection_name": index_version.vector_collection_name,
        "embedding_model": embedding_model,
        "embedding_dimension": embedding_dimension,
        "chunks_total": chunks_total,
        "chunks_seen": chunks_seen,
        "vectors_upserted": vectors_upserted,
        "chunks_failed": chunks_failed,
        "qdrant_count": qdrant_count,
        "status": index_job.status,
        "errors": errors,
        "recreate": recreate,
        "limit": limit,
        "batch_size": resolved_batch_size,
        "duration_ms": round((perf_counter() - started) * 1000, 2),
    }
