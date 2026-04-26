from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import re
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.indexing import statuses
from app.models.datasets import Chunk, Dataset, Document
from app.models.indexing import IndexVersion


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def safe_name(value: str) -> str:
    normalized = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9]+", "-", normalized)
    return normalized.strip("-") or "index"


def short_suffix(*parts: str | None) -> str:
    joined = "|".join(part or "" for part in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:8]


def get_dataset_by_name_version(
    db: Session,
    dataset_name: str,
    dataset_version: str,
) -> Dataset | None:
    return db.scalar(
        select(Dataset).where(Dataset.name == dataset_name, Dataset.version == dataset_version)
    )


def generate_index_version_name(
    dataset_name: str,
    dataset_version: str,
    chunking_strategy: str,
    chunking_version: str,
    embedding_model: str | None = None,
) -> str:
    base = "-".join(
        safe_name(part)
        for part in [dataset_name, dataset_version, chunking_strategy, chunking_version]
    )
    if embedding_model:
        base = f"{base}-{safe_name(embedding_model)}"
    return f"{base}-{short_suffix(dataset_name, dataset_version, chunking_strategy, chunking_version, embedding_model)}"


def generate_lexical_index_name(
    dataset_name: str,
    dataset_version: str,
    chunking_strategy: str,
    chunking_version: str,
) -> str:
    return f"aletheia-lexical-{generate_index_version_name(dataset_name, dataset_version, chunking_strategy, chunking_version)}"


def generate_vector_collection_name(
    dataset_name: str,
    dataset_version: str,
    chunking_strategy: str,
    chunking_version: str,
    embedding_model: str | None = None,
) -> str:
    return f"aletheia-vector-{generate_index_version_name(dataset_name, dataset_version, chunking_strategy, chunking_version, embedding_model)}"


def _count(db: Session, statement) -> int:
    return int(db.scalar(statement) or 0)


def _dataset_counts(db: Session, dataset_id: UUID) -> tuple[int, int]:
    document_count = _count(
        db,
        select(func.count()).select_from(Document).where(Document.dataset_id == dataset_id),
    )
    chunk_count = _count(
        db,
        select(func.count()).select_from(Chunk).where(Chunk.dataset_id == dataset_id),
    )
    return document_count, chunk_count


def create_index_version(
    db: Session,
    dataset_id: UUID,
    name: str | None = None,
    lexical_index_name: str | None = None,
    vector_collection_name: str | None = None,
    embedding_model: str | None = None,
    embedding_dimension: int | None = None,
    chunking_strategy: str | None = None,
    chunking_version: str | None = None,
    document_count: int | None = None,
    chunk_count: int | None = None,
    vector_count: int = 0,
    config_json: dict | None = None,
    notes: str | None = None,
    status: str = statuses.PENDING,
) -> IndexVersion:
    dataset = db.get(Dataset, dataset_id)
    if dataset is None:
        raise ValueError(f"Dataset not found: {dataset_id}")

    strategy = chunking_strategy or "scifact_document_v1"
    version = chunking_version or "1.0"
    document_total, chunk_total = _dataset_counts(db, dataset.id)
    resolved_document_count = document_count if document_count is not None else document_total
    resolved_chunk_count = chunk_count if chunk_count is not None else chunk_total
    resolved_name = name or generate_index_version_name(
        dataset.name,
        dataset.version,
        strategy,
        version,
        embedding_model,
    )

    existing = db.scalar(
        select(IndexVersion).where(
            IndexVersion.dataset_id == dataset.id,
            IndexVersion.name == resolved_name,
        )
    )
    index_version = existing or IndexVersion(dataset_id=dataset.id, name=resolved_name)
    if existing is None:
        db.add(index_version)

    index_version.status = index_version.status if existing and index_version.is_active else status
    index_version.is_active = bool(index_version.is_active)
    index_version.lexical_index_name = lexical_index_name or generate_lexical_index_name(
        dataset.name,
        dataset.version,
        strategy,
        version,
    )
    index_version.vector_collection_name = vector_collection_name or generate_vector_collection_name(
        dataset.name,
        dataset.version,
        strategy,
        version,
        embedding_model,
    )
    index_version.embedding_model = embedding_model
    index_version.embedding_dimension = embedding_dimension
    index_version.chunking_strategy = strategy
    index_version.chunking_version = version
    index_version.document_count = resolved_document_count
    index_version.chunk_count = resolved_chunk_count
    index_version.vector_count = vector_count
    index_version.config_json = config_json or {}
    index_version.notes = notes

    db.commit()
    db.refresh(index_version)
    return index_version


def list_index_versions(
    db: Session,
    dataset_id: UUID | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[IndexVersion], int]:
    filters = []
    if dataset_id is not None:
        filters.append(IndexVersion.dataset_id == dataset_id)
    if status is not None:
        filters.append(IndexVersion.status == status)

    total_statement = select(func.count()).select_from(IndexVersion)
    item_statement = (
        select(IndexVersion).order_by(IndexVersion.created_at.desc()).limit(limit).offset(offset)
    )
    if filters:
        total_statement = total_statement.where(*filters)
        item_statement = item_statement.where(*filters)

    total = _count(db, total_statement)
    return db.scalars(item_statement).all(), total


def get_index_version(db: Session, index_version_id: UUID) -> IndexVersion | None:
    return db.get(IndexVersion, index_version_id)


def get_active_index_version(db: Session, dataset_id: UUID) -> IndexVersion | None:
    return db.scalar(
        select(IndexVersion).where(
            IndexVersion.dataset_id == dataset_id,
            IndexVersion.is_active.is_(True),
        )
    )


def _require_index_version(db: Session, index_version_id: UUID) -> IndexVersion:
    index_version = get_index_version(db, index_version_id)
    if index_version is None:
        raise ValueError(f"Index version not found: {index_version_id}")
    return index_version


def mark_index_version_building(db: Session, index_version_id: UUID) -> IndexVersion:
    index_version = _require_index_version(db, index_version_id)
    if index_version.status != statuses.PENDING:
        raise ValueError("Only pending index versions can be marked building.")
    index_version.status = statuses.BUILDING
    db.commit()
    db.refresh(index_version)
    return index_version


def mark_index_version_ready(
    db: Session,
    index_version_id: UUID,
    document_count: int | None = None,
    chunk_count: int | None = None,
    vector_count: int | None = None,
) -> IndexVersion:
    index_version = _require_index_version(db, index_version_id)
    if index_version.status not in {statuses.PENDING, statuses.BUILDING}:
        raise ValueError("Only pending or building index versions can be marked ready.")
    index_version.status = statuses.READY
    if document_count is not None:
        index_version.document_count = document_count
    if chunk_count is not None:
        index_version.chunk_count = chunk_count
    if vector_count is not None:
        index_version.vector_count = vector_count
    db.commit()
    db.refresh(index_version)
    return index_version


def mark_index_version_failed(
    db: Session,
    index_version_id: UUID,
    error_message: str | None = None,
) -> IndexVersion:
    index_version = _require_index_version(db, index_version_id)
    if index_version.is_active:
        raise ValueError("Active index versions cannot be marked failed.")
    index_version.status = statuses.FAILED
    index_version.is_active = False
    config = dict(index_version.config_json or {})
    if error_message:
        config["error_message"] = error_message
    index_version.config_json = config
    db.commit()
    db.refresh(index_version)
    return index_version


def _activate(db: Session, target: IndexVersion, message: str) -> IndexVersion:
    current_versions = db.scalars(
        select(IndexVersion).where(
            IndexVersion.dataset_id == target.dataset_id,
            IndexVersion.id != target.id,
            IndexVersion.is_active.is_(True),
        )
    ).all()
    for current in current_versions:
        current.status = statuses.DEPRECATED
        current.is_active = False

    target.status = statuses.ACTIVE
    target.is_active = True
    target.activated_at = utc_now()
    config = dict(target.config_json or {})
    config["last_activation_message"] = message
    target.config_json = config
    db.commit()
    db.refresh(target)
    return target


def activate_index_version(db: Session, index_version_id: UUID) -> IndexVersion:
    index_version = _require_index_version(db, index_version_id)
    if index_version.is_active and index_version.status == statuses.ACTIVE:
        return index_version
    if index_version.status != statuses.READY:
        raise ValueError("Only ready index versions can be activated.")
    return _activate(db, index_version, "metadata-only index version activated.")


def rollback_to_index_version(db: Session, index_version_id: UUID) -> IndexVersion:
    index_version = _require_index_version(db, index_version_id)
    if index_version.status not in {statuses.READY, statuses.DEPRECATED, statuses.ACTIVE}:
        raise ValueError("Rollback target must be ready, deprecated, or active.")
    if not index_version.lexical_index_name or not index_version.vector_collection_name:
        raise ValueError("Rollback target must have lexical and vector resource names.")
    if index_version.is_active and index_version.status == statuses.ACTIVE:
        return index_version
    return _activate(db, index_version, "metadata-only rollback activated.")


def index_status(db: Session) -> dict[str, Any]:
    dataset_count = _count(db, select(func.count()).select_from(Dataset))
    index_version_count = _count(db, select(func.count()).select_from(IndexVersion))
    ready_index_version_count = _count(
        db,
        select(func.count()).select_from(IndexVersion).where(IndexVersion.status == statuses.READY),
    )
    active_index_version_count = _count(
        db,
        select(func.count()).select_from(IndexVersion).where(IndexVersion.is_active.is_(True)),
    )
    latest = db.scalars(select(IndexVersion).order_by(IndexVersion.created_at.desc()).limit(5)).all()
    active = db.scalar(
        select(IndexVersion)
        .where(IndexVersion.is_active.is_(True))
        .order_by(IndexVersion.activated_at.desc())
        .limit(1)
    )
    return {
        "active_index_version": active,
        "dataset_count": dataset_count,
        "index_version_count": index_version_count,
        "ready_index_version_count": ready_index_version_count,
        "active_index_version_count": active_index_version_count,
        "latest_index_versions": latest,
    }
