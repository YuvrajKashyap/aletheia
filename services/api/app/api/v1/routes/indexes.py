from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.api.dependencies.admin import AdminContext, require_admin
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.indexing import service as index_service
from app.jobs import queue as job_queue
from app.schemas.indexes import (
    ActivateIndexVersionResponse,
    BuildLexicalIndexRequest,
    BuildLexicalIndexResponse,
    BuildVectorIndexRequest,
    BuildVectorIndexResponse,
    CreateIndexVersionRequest,
    IndexJobItem,
    IndexJobListResponse,
    IndexStatusResponse,
    IndexVersionDetail,
    IndexVersionItem,
    IndexVersionListResponse,
    MarkIndexVersionStatusRequest,
)

router = APIRouter(prefix="/indexes", tags=["indexes"])


def _item(index_version) -> IndexVersionItem:
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
    )


def _detail(index_version) -> IndexVersionDetail:
    return IndexVersionDetail(**_item(index_version).model_dump())


def _job_item(index_job) -> IndexJobItem:
    return IndexJobItem(
        id=index_job.id,
        index_version_id=index_job.index_version_id,
        job_id=index_job.job_id,
        job_type=index_job.job_type,
        status=index_job.status,
        started_at=index_job.started_at,
        completed_at=index_job.completed_at,
        chunks_total=index_job.chunks_total,
        chunks_completed=index_job.chunks_completed,
        chunks_failed=index_job.chunks_failed,
        error_message=index_job.error_message,
        created_at=index_job.created_at,
        updated_at=index_job.updated_at,
    )


def _bad_request(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/status", response_model=IndexStatusResponse)
async def index_status(db: Session = Depends(get_db)) -> IndexStatusResponse:
    payload = index_service.index_status(db)
    return IndexStatusResponse(
        active_index_version=(
            _item(payload["active_index_version"]) if payload["active_index_version"] else None
        ),
        dataset_count=payload["dataset_count"],
        index_version_count=payload["index_version_count"],
        ready_index_version_count=payload["ready_index_version_count"],
        active_index_version_count=payload["active_index_version_count"],
        latest_index_versions=[_item(version) for version in payload["latest_index_versions"]],
    )


@router.get("/versions", response_model=IndexVersionListResponse)
async def list_index_versions(
    dataset_id: UUID | None = None,
    status: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> IndexVersionListResponse:
    versions, total = index_service.list_index_versions(
        db,
        dataset_id=dataset_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    return IndexVersionListResponse(
        items=[_item(version) for version in versions],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/jobs", response_model=IndexJobListResponse)
async def list_index_jobs(
    index_version_id: UUID | None = None,
    job_type: str | None = None,
    status: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> IndexJobListResponse:
    jobs, total = index_service.list_index_jobs(
        db,
        index_version_id=index_version_id,
        job_type=job_type,
        status=status,
        limit=limit,
        offset=offset,
    )
    return IndexJobListResponse(
        items=[_job_item(job) for job in jobs],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/versions/{index_version_id}", response_model=IndexVersionDetail)
async def index_version_detail(
    index_version_id: UUID,
    db: Session = Depends(get_db),
) -> IndexVersionDetail:
    index_version = index_service.get_index_version(db, index_version_id)
    if index_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Index version not found: {index_version_id}",
        )
    return _detail(index_version)


@router.post("/versions", response_model=IndexVersionDetail)
async def create_index_version(
    request: CreateIndexVersionRequest,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> IndexVersionDetail:
    dataset_id = request.dataset_id
    if dataset_id is None:
        dataset = index_service.get_dataset_by_name_version(
            db,
            request.dataset_name,
            request.dataset_version,
        )
        if dataset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset not found: {request.dataset_name} version {request.dataset_version}",
            )
        dataset_id = dataset.id

    try:
        index_version = index_service.create_index_version(
            db,
            dataset_id=dataset_id,
            name=request.name,
            lexical_index_name=request.lexical_index_name,
            vector_collection_name=request.vector_collection_name,
            embedding_model=request.embedding_model or settings.EMBEDDING_MODEL,
            embedding_dimension=request.embedding_dimension,
            chunking_strategy=request.chunking_strategy,
            chunking_version=request.chunking_version,
            config_json=request.config_json,
            notes=request.notes,
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc
    return _detail(index_version)


@router.post("/versions/{index_version_id}/mark-building", response_model=IndexVersionDetail)
async def mark_index_version_building(
    index_version_id: UUID,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> IndexVersionDetail:
    try:
        return _detail(index_service.mark_index_version_building(db, index_version_id))
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/versions/{index_version_id}/mark-ready", response_model=IndexVersionDetail)
async def mark_index_version_ready(
    index_version_id: UUID,
    request: MarkIndexVersionStatusRequest | None = None,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> IndexVersionDetail:
    body = request or MarkIndexVersionStatusRequest()
    try:
        return _detail(
            index_service.mark_index_version_ready(
                db,
                index_version_id,
                document_count=body.document_count,
                chunk_count=body.chunk_count,
                vector_count=body.vector_count,
            )
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/versions/{index_version_id}/mark-failed", response_model=IndexVersionDetail)
async def mark_index_version_failed(
    index_version_id: UUID,
    request: MarkIndexVersionStatusRequest | None = None,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> IndexVersionDetail:
    body = request or MarkIndexVersionStatusRequest()
    try:
        return _detail(
            index_service.mark_index_version_failed(
                db,
                index_version_id,
                error_message=body.error_message,
            )
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc


@router.post("/versions/{index_version_id}/activate", response_model=ActivateIndexVersionResponse)
async def activate_index_version(
    index_version_id: UUID,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ActivateIndexVersionResponse:
    try:
        index_version = index_service.activate_index_version(db, index_version_id)
    except ValueError as exc:
        raise _bad_request(exc) from exc
    return ActivateIndexVersionResponse(
        index_version=_item(index_version),
        message="metadata-only index version activated.",
    )


@router.post("/versions/{index_version_id}/rollback", response_model=ActivateIndexVersionResponse)
async def rollback_to_index_version(
    index_version_id: UUID,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ActivateIndexVersionResponse:
    try:
        index_version = index_service.rollback_to_index_version(db, index_version_id)
    except ValueError as exc:
        raise _bad_request(exc) from exc
    return ActivateIndexVersionResponse(
        index_version=_item(index_version),
        message="metadata-only rollback activated.",
    )


@router.post(
    "/versions/{index_version_id}/build-lexical",
    response_model=BuildLexicalIndexResponse,
)
async def build_lexical_index(
    index_version_id: UUID,
    request: BuildLexicalIndexRequest | None = None,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> BuildLexicalIndexResponse:
    if index_service.get_index_version(db, index_version_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Index version not found: {index_version_id}",
        )

    body = request or BuildLexicalIndexRequest()
    try:
        payload = job_queue.enqueue_lexical_index_build_job(
            index_version_id=str(index_version_id),
            recreate=body.recreate,
            limit=body.limit,
            refresh=body.refresh,
        )
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis queue unavailable: {exc}",
        ) from exc
    return BuildLexicalIndexResponse(**payload)


@router.post(
    "/versions/{index_version_id}/build-vector",
    response_model=BuildVectorIndexResponse,
)
async def build_vector_index(
    index_version_id: UUID,
    request: BuildVectorIndexRequest | None = None,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> BuildVectorIndexResponse:
    if index_service.get_index_version(db, index_version_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Index version not found: {index_version_id}",
        )

    body = request or BuildVectorIndexRequest()
    try:
        payload = job_queue.enqueue_vector_index_build_job(
            index_version_id=str(index_version_id),
            recreate=body.recreate,
            limit=body.limit,
            batch_size=body.batch_size,
        )
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis queue unavailable: {exc}",
        ) from exc
    return BuildVectorIndexResponse(**payload)
