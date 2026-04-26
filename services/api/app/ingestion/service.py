from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.chunking.service import chunk_dataset_documents
from app.datasets.scifact import load_scifact_to_db
from app.ingestion.statuses import ACTIVE_STATUSES, COMPLETED, FAILED, PENDING, RUNNING
from app.models.datasets import Dataset
from app.models.indexing import IngestionRun

SCIFACT_DATASET_NAME = "beir/scifact"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def scifact_ingestion_config(
    document_limit: int | None = None,
    query_limit: int | None = None,
    qrel_limit: int | None = None,
    split: str = "test",
    chunk_after_load: bool = True,
    chunk_document_limit: int | None = None,
    dry_run: bool = False,
    started_by: str = "manual",
    rq_job_id: str | None = None,
) -> dict[str, Any]:
    return {
        "dataset": SCIFACT_DATASET_NAME,
        "split": split,
        "document_limit": document_limit,
        "query_limit": query_limit,
        "qrel_limit": qrel_limit,
        "chunk_after_load": chunk_after_load,
        "chunk_document_limit": chunk_document_limit,
        "dry_run": dry_run,
        "started_by": started_by,
        "rq_job_id": rq_job_id,
    }


def create_ingestion_run(
    db: Session,
    status: str = PENDING,
    config_json: dict | None = None,
    rq_job_id: str | None = None,
) -> IngestionRun:
    config = dict(config_json or {})
    if rq_job_id is not None:
        config["rq_job_id"] = rq_job_id

    run = IngestionRun(
        status=status,
        config_json=config,
        started_at=None,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_ingestion_run(db: Session, run_id: UUID) -> IngestionRun | None:
    return db.get(IngestionRun, run_id)


def list_ingestion_runs(
    db: Session,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[IngestionRun], int]:
    filters = []
    if status is not None:
        filters.append(IngestionRun.status == status)

    total_statement = select(func.count()).select_from(IngestionRun)
    item_statement = (
        select(IngestionRun).order_by(IngestionRun.created_at.desc()).limit(limit).offset(offset)
    )
    if filters:
        total_statement = total_statement.where(*filters)
        item_statement = item_statement.where(*filters)

    total = int(db.scalar(total_statement) or 0)
    return db.scalars(item_statement).all(), total


def find_active_scifact_ingestion_run(db: Session) -> IngestionRun | None:
    active_runs = db.scalars(
        select(IngestionRun)
        .where(IngestionRun.status.in_(ACTIVE_STATUSES))
        .order_by(IngestionRun.created_at.desc())
    ).all()
    for run in active_runs:
        if (run.config_json or {}).get("dataset") == SCIFACT_DATASET_NAME:
            return run
    return None


def _get_scifact_dataset(db: Session, split: str) -> Dataset | None:
    return db.scalar(
        select(Dataset).where(Dataset.name == SCIFACT_DATASET_NAME, Dataset.version == split)
    )


def _summary(
    run: IngestionRun,
    *,
    chunks_existing: int = 0,
    chunks_updated: int = 0,
    dry_run: bool,
    split: str,
    duration_ms: float,
) -> dict[str, Any]:
    return {
        "ingestion_run_id": str(run.id),
        "status": run.status,
        "dataset_id": str(run.dataset_id) if run.dataset_id else None,
        "documents_loaded": run.documents_loaded,
        "queries_loaded": run.queries_loaded,
        "qrels_loaded": run.qrels_loaded,
        "chunks_created": run.chunks_created,
        "chunks_existing": chunks_existing,
        "chunks_updated": chunks_updated,
        "errors_count": run.errors_count,
        "dry_run": dry_run,
        "split": split,
        "duration_ms": round(duration_ms, 2),
    }


def run_scifact_ingestion(
    db: Session,
    document_limit: int | None = None,
    query_limit: int | None = None,
    qrel_limit: int | None = None,
    split: str = "test",
    chunk_after_load: bool = True,
    chunk_document_limit: int | None = None,
    dry_run: bool = False,
    started_by: str = "manual",
    rq_job_id: str | None = None,
    ingestion_run_id: UUID | str | None = None,
) -> dict:
    started = perf_counter()
    chunks_existing = 0
    chunks_updated = 0
    config = scifact_ingestion_config(
        document_limit=document_limit,
        query_limit=query_limit,
        qrel_limit=qrel_limit,
        split=split,
        chunk_after_load=chunk_after_load,
        chunk_document_limit=chunk_document_limit,
        dry_run=dry_run,
        started_by=started_by,
        rq_job_id=rq_job_id,
    )

    run = get_ingestion_run(db, UUID(str(ingestion_run_id))) if ingestion_run_id else None
    if run is None:
        run = create_ingestion_run(db, status=PENDING, config_json=config, rq_job_id=rq_job_id)
    elif rq_job_id is None:
        config["rq_job_id"] = (run.config_json or {}).get("rq_job_id")

    try:
        run.status = RUNNING
        run.started_at = utc_now()
        run.config_json = config
        db.commit()

        load_summary = load_scifact_to_db(
            db,
            document_limit=document_limit,
            query_limit=query_limit,
            qrel_limit=qrel_limit,
            split=split,
            dry_run=dry_run,
        )

        dataset = _get_scifact_dataset(db, split)
        if dataset is not None:
            run.dataset_id = dataset.id

        run.documents_loaded = load_summary.documents_loaded
        run.queries_loaded = load_summary.queries_loaded
        run.qrels_loaded = load_summary.qrels_loaded

        if chunk_after_load and not dry_run:
            chunk_summary = chunk_dataset_documents(
                db,
                dataset_name=SCIFACT_DATASET_NAME,
                dataset_version=split,
                document_limit=chunk_document_limit,
                dry_run=False,
            )
            run.chunks_created = chunk_summary.chunks_created
            chunks_existing = chunk_summary.chunks_existing
            chunks_updated = chunk_summary.chunks_updated
        else:
            run.chunks_created = 0

        run.errors_count = load_summary.qrels_skipped_missing_query + (
            load_summary.qrels_skipped_missing_document
        )
        run.status = COMPLETED
        run.completed_at = utc_now()
        run.error_message = None
        db.commit()
        db.refresh(run)
        return _summary(
            run,
            chunks_existing=chunks_existing,
            chunks_updated=chunks_updated,
            dry_run=dry_run,
            split=split,
            duration_ms=(perf_counter() - started) * 1000,
        )
    except Exception as exc:
        run.status = FAILED
        run.errors_count = max(run.errors_count or 0, 1)
        run.error_message = str(exc)
        run.completed_at = utc_now()
        db.commit()
        raise
