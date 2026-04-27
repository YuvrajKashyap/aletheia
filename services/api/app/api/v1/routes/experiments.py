from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.exceptions import RedisError
from sqlalchemy.orm import Session

from app.api.dependencies.admin import AdminContext, require_admin
from app.db.session import get_db
from app.experiments import service as experiment_service
from app.jobs import queue as job_queue
from app.models.experiments import ExperimentConfig
from app.schemas.experiments import (
    ExperimentConfigCreateRequest,
    ExperimentConfigDetail,
    ExperimentConfigItem,
    ExperimentConfigListResponse,
    ExperimentConfigUpdateRequest,
    SeedExperimentConfigsResponse,
    StartComparisonRequest,
    StartComparisonResponse,
)

router = APIRouter(prefix="/experiments", tags=["experiments"])


def _config_item(config: ExperimentConfig) -> ExperimentConfigItem:
    return ExperimentConfigItem(
        id=config.id,
        name=config.name,
        retrieval_mode=config.retrieval_mode,
        bm25_candidate_k=config.bm25_candidate_k,
        dense_candidate_k=config.dense_candidate_k,
        hybrid_candidate_k=config.hybrid_candidate_k,
        rerank_top_n=config.rerank_top_n,
        top_k_final=config.top_k_final,
        fusion_method=config.fusion_method,
        fusion_params_json=config.fusion_params_json,
        embedding_model=config.embedding_model,
        reranker_model=config.reranker_model,
        is_default=config.is_default,
        created_at=config.created_at,
        updated_at=config.updated_at,
    )


def _config_detail(config: ExperimentConfig) -> ExperimentConfigDetail:
    return ExperimentConfigDetail(
        **_config_item(config).model_dump(),
        config_json=config.config_json,
    )


def _default_comparison_name() -> str:
    return f"evaluation comparison {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


@router.get("/configs", response_model=ExperimentConfigListResponse)
async def list_experiment_configs(
    retrieval_mode: str | None = None,
    is_default: bool | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ExperimentConfigListResponse:
    result = experiment_service.list_experiment_configs(
        db,
        retrieval_mode=retrieval_mode,
        is_default=is_default,
        limit=limit,
        offset=offset,
    )
    return ExperimentConfigListResponse(
        total=result["total"],
        limit=result["limit"],
        offset=result["offset"],
        items=[_config_item(config) for config in result["items"]],
    )


@router.post("/configs", response_model=ExperimentConfigDetail)
async def create_experiment_config(
    request: ExperimentConfigCreateRequest,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ExperimentConfigDetail:
    try:
        config = experiment_service.create_experiment_config(db, **request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _config_detail(config)


@router.post("/configs/seed-defaults", response_model=SeedExperimentConfigsResponse)
async def seed_default_experiment_configs(
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> SeedExperimentConfigsResponse:
    result = experiment_service.seed_default_experiment_configs(db)
    return SeedExperimentConfigsResponse(
        created_count=result["created_count"],
        updated_count=result["updated_count"],
        existing_count=result["existing_count"],
        configs=[_config_item(config) for config in result["configs"]],
    )


@router.post("/comparisons", response_model=StartComparisonResponse)
async def start_evaluation_comparison(
    request: StartComparisonRequest,
    _admin_context: AdminContext = Depends(require_admin),
) -> StartComparisonResponse:
    name = request.name or _default_comparison_name()
    try:
        result = job_queue.enqueue_evaluation_comparison_job(
            name=name,
            experiment_config_ids=[str(value) for value in request.experiment_config_ids or []],
            experiment_config_names=request.experiment_config_names,
            use_defaults=request.use_defaults,
            dataset_name=request.dataset_name,
            dataset_version=request.dataset_version,
            index_version_id=str(request.index_version_id) if request.index_version_id else None,
            query_limit=request.query_limit,
            query_offset=request.query_offset,
            notes=request.notes,
        )
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis queue unavailable for evaluation comparison job.",
        ) from exc
    return StartComparisonResponse(**result)


@router.get("/configs/{config_id}", response_model=ExperimentConfigDetail)
async def get_experiment_config(
    config_id: UUID,
    db: Session = Depends(get_db),
) -> ExperimentConfigDetail:
    config = experiment_service.get_experiment_config(db, config_id)
    if config is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment config not found: {config_id}",
        )
    return _config_detail(config)


@router.patch("/configs/{config_id}", response_model=ExperimentConfigDetail)
async def update_experiment_config(
    config_id: UUID,
    request: ExperimentConfigUpdateRequest,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> ExperimentConfigDetail:
    try:
        config = experiment_service.update_experiment_config(
            db,
            config_id,
            **request.model_dump(exclude_unset=True),
        )
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _config_detail(config)


@router.delete("/configs/{config_id}")
async def delete_experiment_config(
    config_id: UUID,
    _admin_context: AdminContext = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    try:
        experiment_service.delete_experiment_config(db, config_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"deleted": True, "id": str(config_id)}
