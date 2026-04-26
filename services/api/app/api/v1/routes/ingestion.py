from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.api.dependencies.admin import AdminContext, require_admin
from app.db.session import get_db
from app.ingestion import service as ingestion_service
from app.ingestion.statuses import FAILED, PENDING
from app.jobs import queue as job_queue
from app.schemas.ingestion import (
    IngestionRunDetail,
    IngestionRunItem,
    IngestionRunListResponse,
    StartIngestionResponse,
    StartSciFactIngestionRequest,
)

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


def _run_item(run) -> IngestionRunItem:
    return IngestionRunItem(
        id=run.id,
        dataset_id=run.dataset_id,
        status=run.status,
        started_at=run.started_at,
        completed_at=run.completed_at,
        documents_loaded=run.documents_loaded,
        chunks_created=run.chunks_created,
        queries_loaded=run.queries_loaded,
        qrels_loaded=run.qrels_loaded,
        errors_count=run.errors_count,
        config_json=run.config_json,
        error_message=run.error_message,
        created_at=run.created_at,
        updated_at=run.updated_at,
    )


@router.post("/datasets/scifact", response_model=StartIngestionResponse)
async def start_scifact_ingestion(
    request: StartSciFactIngestionRequest,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> StartIngestionResponse:
    active_run = ingestion_service.find_active_scifact_ingestion_run(db)
    if active_run is not None and not request.dry_run:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Active SciFact ingestion run already exists: {active_run.id}",
        )

    config = ingestion_service.scifact_ingestion_config(
        document_limit=request.document_limit,
        query_limit=request.query_limit,
        qrel_limit=request.qrel_limit,
        split=request.split,
        chunk_after_load=request.chunk_after_load,
        chunk_document_limit=request.chunk_document_limit,
        dry_run=request.dry_run,
        started_by="api",
    )
    run = ingestion_service.create_ingestion_run(db, status=PENDING, config_json=config)

    try:
        enqueue_result = job_queue.enqueue_scifact_ingestion_job(
            ingestion_run_id=str(run.id),
            document_limit=request.document_limit,
            query_limit=request.query_limit,
            qrel_limit=request.qrel_limit,
            split=request.split,
            chunk_after_load=request.chunk_after_load,
            chunk_document_limit=request.chunk_document_limit,
            dry_run=request.dry_run,
            started_by="api",
        )
    except RedisError as exc:
        run.status = FAILED
        run.error_message = f"Failed to enqueue ingestion job: {exc}"
        run.errors_count = 1
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis queue unavailable for ingestion job.",
        ) from exc

    run.config_json = {
        **config,
        "rq_job_id": enqueue_result["job_id"],
    }
    db.commit()
    return StartIngestionResponse(**enqueue_result)


@router.get("/runs", response_model=IngestionRunListResponse)
async def list_ingestion_runs(
    status: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> IngestionRunListResponse:
    runs, total = ingestion_service.list_ingestion_runs(
        db,
        status=status,
        limit=limit,
        offset=offset,
    )
    return IngestionRunListResponse(
        items=[_run_item(run) for run in runs],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/runs/{run_id}", response_model=IngestionRunDetail)
async def ingestion_run_detail(run_id: UUID, db: Session = Depends(get_db)) -> IngestionRunDetail:
    run = ingestion_service.get_ingestion_run(db, run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingestion run not found: {run_id}",
        )
    return IngestionRunDetail(**_run_item(run).model_dump())
