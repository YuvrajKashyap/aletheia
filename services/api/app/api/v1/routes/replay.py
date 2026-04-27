from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.api.dependencies.admin import AdminContext, require_admin
from app.db.session import get_db
from app.jobs import queue as job_queue
from app.models.queries import QueryReplay, SavedQuery
from app.replay import service as replay_service
from app.schemas.replay import (
    QueryReplayDetail,
    QueryReplayItem,
    QueryReplayListResponse,
    ReplayResponse,
    ReplaySavedQueryRequest,
    SavedQueryCreateRequest,
    SavedQueryDetail,
    SavedQueryItem,
    SavedQueryListResponse,
    SeedGoldenQueriesRequest,
    SeedGoldenQueriesResponse,
    StartGoldenReplayRequest,
    StartGoldenReplayResponse,
)

router = APIRouter(prefix="/replay", tags=["replay"])


def _saved_query_item(saved_query: SavedQuery) -> SavedQueryItem:
    return SavedQueryItem(
        id=saved_query.id,
        name=saved_query.name,
        text=saved_query.text,
        source=saved_query.source,
        dataset_id=saved_query.dataset_id,
        metadata_json=saved_query.metadata_json,
        created_at=saved_query.created_at,
    )


def _saved_query_detail(saved_query: SavedQuery) -> SavedQueryDetail:
    return SavedQueryDetail(**_saved_query_item(saved_query).model_dump())


def _replay_item(replay: QueryReplay) -> QueryReplayItem:
    return QueryReplayItem(
        id=replay.id,
        saved_query_id=replay.saved_query_id,
        original_query_id=replay.original_query_id,
        source_trace_id=replay.source_trace_id,
        target_trace_id=replay.target_trace_id,
        experiment_config_id=replay.experiment_config_id,
        index_version_id=replay.index_version_id,
        status=replay.status,
        error_message=replay.error_message,
        created_at=replay.created_at,
        started_at=replay.started_at,
        completed_at=replay.completed_at,
    )


def _replay_detail(replay: QueryReplay) -> QueryReplayDetail:
    return QueryReplayDetail(**_replay_item(replay).model_dump(), comparison_json=replay.comparison_json)


def _default_golden_replay_name() -> str:
    return f"golden replay {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


@router.get("/saved-queries", response_model=SavedQueryListResponse)
async def list_saved_queries(
    source: str | None = None,
    dataset_id: UUID | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> SavedQueryListResponse:
    result = replay_service.list_saved_queries(
        db,
        source=source,
        dataset_id=str(dataset_id) if dataset_id else None,
        limit=limit,
        offset=offset,
    )
    return SavedQueryListResponse(
        total=result["total"],
        limit=result["limit"],
        offset=result["offset"],
        items=[_saved_query_item(item) for item in result["items"]],
    )


@router.post("/saved-queries", response_model=SavedQueryDetail)
async def create_saved_query(
    request: SavedQueryCreateRequest,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SavedQueryDetail:
    try:
        saved_query = replay_service.create_saved_query(
            db,
            text=request.text,
            name=request.name,
            source=request.source,
            dataset_id=str(request.dataset_id) if request.dataset_id else None,
            metadata_json=request.metadata_json,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _saved_query_detail(saved_query)


@router.post("/saved-queries/seed-golden", response_model=SeedGoldenQueriesResponse)
async def seed_golden_queries(
    request: SeedGoldenQueriesRequest,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SeedGoldenQueriesResponse:
    try:
        result = replay_service.seed_golden_queries_from_scifact(
            db,
            dataset_name=request.dataset_name,
            dataset_version=request.dataset_version,
            limit=request.limit,
            offset=request.offset,
        )
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return SeedGoldenQueriesResponse(
        created_count=result["created_count"],
        existing_count=result["existing_count"],
        total_selected=result["total_selected"],
        items=[_saved_query_item(item) for item in result["items"]],
    )


@router.post("/golden/run", response_model=StartGoldenReplayResponse)
async def start_golden_replay(
    request: StartGoldenReplayRequest,
    _admin_context: AdminContext = Depends(require_admin),
) -> StartGoldenReplayResponse:
    try:
        result = job_queue.enqueue_golden_query_replay_job(
            name=request.name or _default_golden_replay_name(),
            source=request.source,
            retrieval_mode=request.retrieval_mode,
            experiment_config_id=str(request.experiment_config_id)
            if request.experiment_config_id
            else None,
            experiment_config_name=request.experiment_config_name,
            limit=request.limit,
            offset=request.offset,
            top_k=request.top_k,
            candidate_k=request.candidate_k,
            bm25_candidate_k=request.bm25_candidate_k,
            dense_candidate_k=request.dense_candidate_k,
            hybrid_candidate_k=request.hybrid_candidate_k,
            rerank_top_n=request.rerank_top_n,
            rrf_k=request.rrf_k,
            notes=request.notes,
        )
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis queue unavailable for golden replay job.",
        ) from exc
    return StartGoldenReplayResponse(**result)


@router.get("/saved-queries/{saved_query_id}", response_model=SavedQueryDetail)
async def get_saved_query(
    saved_query_id: UUID,
    db: Session = Depends(get_db),
) -> SavedQueryDetail:
    saved_query = replay_service.get_saved_query(db, saved_query_id)
    if saved_query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Saved query not found: {saved_query_id}",
        )
    return _saved_query_detail(saved_query)


@router.delete("/saved-queries/{saved_query_id}")
async def delete_saved_query(
    saved_query_id: UUID,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    try:
        replay_service.delete_saved_query(db, saved_query_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"deleted": True, "id": str(saved_query_id)}


@router.post("/saved-queries/{saved_query_id}/run", response_model=ReplayResponse)
async def start_saved_query_replay(
    saved_query_id: UUID,
    request: ReplaySavedQueryRequest,
    _admin_context: AdminContext = Depends(require_admin),
) -> ReplayResponse:
    try:
        result = job_queue.enqueue_saved_query_replay_job(
            saved_query_id=str(saved_query_id),
            retrieval_mode=request.retrieval_mode,
            experiment_config_id=str(request.experiment_config_id)
            if request.experiment_config_id
            else None,
            experiment_config_name=request.experiment_config_name,
            index_version_id=str(request.index_version_id) if request.index_version_id else None,
            source_trace_id=str(request.source_trace_id) if request.source_trace_id else None,
            top_k=request.top_k,
            candidate_k=request.candidate_k,
            bm25_candidate_k=request.bm25_candidate_k,
            dense_candidate_k=request.dense_candidate_k,
            hybrid_candidate_k=request.hybrid_candidate_k,
            rerank_top_n=request.rerank_top_n,
            rrf_k=request.rrf_k,
        )
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis queue unavailable for saved query replay job.",
        ) from exc
    return ReplayResponse(**result)


@router.get("/runs", response_model=QueryReplayListResponse)
async def list_query_replays(
    saved_query_id: UUID | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> QueryReplayListResponse:
    result = replay_service.list_query_replays(
        db,
        saved_query_id=str(saved_query_id) if saved_query_id else None,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return QueryReplayListResponse(
        total=result["total"],
        limit=result["limit"],
        offset=result["offset"],
        items=[_replay_item(item) for item in result["items"]],
    )


@router.get("/runs/{query_replay_id}", response_model=QueryReplayDetail)
async def get_query_replay(
    query_replay_id: UUID,
    db: Session = Depends(get_db),
) -> QueryReplayDetail:
    replay = replay_service.get_query_replay(db, query_replay_id)
    if replay is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query replay not found: {query_replay_id}",
        )
    return _replay_detail(replay)
