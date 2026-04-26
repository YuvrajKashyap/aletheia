from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.admin import AdminContext, require_admin
from app.db.session import get_db
from app.jobs import queue as job_queue
from app.ml.embeddings import get_embedding_model_status
from app.ml.reranker import get_reranker_model_status
from app.models.system import WorkerHeartbeat
from app.search.opensearch_client import check_opensearch_health
from app.search.qdrant_client import check_qdrant_health
from app.schemas.system import (
    EmbeddingModelStatusResponse,
    EnqueueJobResponse,
    EnqueueTestJobRequest,
    JobStatusResponse,
    OpenSearchHealthResponse,
    QdrantHealthResponse,
    QueueStatusResponse,
    RerankerModelStatusResponse,
    WorkerHeartbeatItem,
    WorkerHeartbeatListResponse,
)

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/queue", response_model=QueueStatusResponse)
async def queue_status() -> QueueStatusResponse:
    try:
        return QueueStatusResponse(**job_queue.get_queue_status())
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis queue unavailable: {exc}",
        ) from exc


@router.get("/opensearch", response_model=OpenSearchHealthResponse)
async def opensearch_status() -> OpenSearchHealthResponse:
    return OpenSearchHealthResponse(**check_opensearch_health())


@router.get("/qdrant", response_model=QdrantHealthResponse)
async def qdrant_status() -> QdrantHealthResponse:
    return QdrantHealthResponse(**check_qdrant_health())


@router.get("/models/embedding", response_model=EmbeddingModelStatusResponse)
async def embedding_model_status() -> EmbeddingModelStatusResponse:
    return EmbeddingModelStatusResponse(**get_embedding_model_status())


@router.get("/models/reranker", response_model=RerankerModelStatusResponse)
async def reranker_model_status() -> RerankerModelStatusResponse:
    return RerankerModelStatusResponse(**get_reranker_model_status())


@router.post("/jobs/test", response_model=EnqueueJobResponse)
async def enqueue_test_job(
    request: EnqueueTestJobRequest,
    _admin_context: AdminContext = Depends(require_admin),
) -> EnqueueJobResponse:
    try:
        return EnqueueJobResponse(**job_queue.enqueue_ping_job(request.message))
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis queue unavailable: {exc}",
        ) from exc


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def job_status(job_id: str) -> JobStatusResponse:
    result = job_queue.get_job_status(job_id)
    if not result["found"] and result["error"] is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}",
        )
    if not result["found"] and result["error"] is not None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis queue unavailable: {result['error']}",
        )
    return JobStatusResponse(**result)


@router.get("/worker-heartbeats", response_model=WorkerHeartbeatListResponse)
async def worker_heartbeats(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> WorkerHeartbeatListResponse:
    workers = db.scalars(
        select(WorkerHeartbeat).order_by(WorkerHeartbeat.last_seen_at.desc()).limit(limit)
    ).all()
    return WorkerHeartbeatListResponse(
        workers=[
            WorkerHeartbeatItem(
                worker_name=worker.worker_name,
                queue_name=worker.queue_name,
                status=worker.status,
                current_job_id=worker.current_job_id,
                metadata_json=worker.metadata_json,
                last_seen_at=worker.last_seen_at,
                updated_at=worker.updated_at,
            )
            for worker in workers
        ]
    )
