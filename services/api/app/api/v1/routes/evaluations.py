from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.exceptions import RedisError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies.admin import AdminContext, require_admin
from app.db.session import get_db
from app.evaluation.reporting import load_evaluation_report
from app.jobs import queue as job_queue
from app.models.evaluation import EvaluationQueryResult, EvaluationReport, EvaluationRun
from app.schemas.evaluations import (
    EvaluationQueryResultItem,
    EvaluationQueryResultListResponse,
    EvaluationReportResponse,
    EvaluationRunDetail,
    EvaluationRunItem,
    EvaluationRunListResponse,
    StartEvaluationRequest,
    StartEvaluationResponse,
)

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


def _run_item(run: EvaluationRun) -> EvaluationRunItem:
    return EvaluationRunItem(
        id=run.id,
        name=run.name,
        dataset_id=run.dataset_id,
        index_version_id=run.index_version_id,
        experiment_config_id=run.experiment_config_id,
        status=run.status,
        query_count=run.query_count,
        failed_query_count=run.failed_query_count,
        recall_at_5=run.recall_at_5,
        recall_at_10=run.recall_at_10,
        mrr_at_10=run.mrr_at_10,
        ndcg_at_10=run.ndcg_at_10,
        avg_latency_ms=run.avg_latency_ms,
        p50_latency_ms=run.p50_latency_ms,
        p95_latency_ms=run.p95_latency_ms,
        report_path=run.report_path,
        created_at=run.created_at,
        started_at=run.started_at,
        completed_at=run.completed_at,
    )


def _run_detail(run: EvaluationRun) -> EvaluationRunDetail:
    return EvaluationRunDetail(
        **_run_item(run).model_dump(),
        config_json=run.config_json,
        notes=run.notes,
    )


def _result_item(result: EvaluationQueryResult) -> EvaluationQueryResultItem:
    return EvaluationQueryResultItem(
        id=result.id,
        evaluation_run_id=result.evaluation_run_id,
        benchmark_query_id=result.benchmark_query_id,
        query_external_id=result.query_external_id,
        query_text=result.query_text,
        recall_at_5=result.recall_at_5,
        recall_at_10=result.recall_at_10,
        mrr_at_10=result.mrr_at_10,
        ndcg_at_10=result.ndcg_at_10,
        latency_ms=result.latency_ms,
        trace_id=result.trace_id,
        error_message=result.error_message,
        created_at=result.created_at,
    )


def _default_name(retrieval_mode: str | None) -> str:
    label = retrieval_mode or "configured"
    return f"{label} evaluation {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


def list_evaluation_runs_query(
    db: Session,
    retrieval_mode: str | None = None,
    status_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[EvaluationRun], int]:
    statement = select(EvaluationRun)
    count_statement = select(func.count()).select_from(EvaluationRun)
    filters = []
    if status_filter:
        filters.append(EvaluationRun.status == status_filter)
    if retrieval_mode:
        filters.append(EvaluationRun.config_json["retrieval_mode"].astext == retrieval_mode)
    if filters:
        statement = statement.where(*filters)
        count_statement = count_statement.where(*filters)
    total = int(db.scalar(count_statement) or 0)
    runs = list(
        db.scalars(
            statement.order_by(EvaluationRun.created_at.desc(), EvaluationRun.id.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return runs, total


def get_evaluation_run_query(db: Session, evaluation_run_id: UUID) -> EvaluationRun | None:
    return db.get(EvaluationRun, evaluation_run_id)


def list_evaluation_results_query(
    db: Session,
    evaluation_run_id: UUID,
    failed_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[EvaluationQueryResult], int]:
    filters = [EvaluationQueryResult.evaluation_run_id == evaluation_run_id]
    if failed_only:
        filters.append(EvaluationQueryResult.error_message.is_not(None))
    total = int(
        db.scalar(select(func.count()).select_from(EvaluationQueryResult).where(*filters)) or 0
    )
    results = list(
        db.scalars(
            select(EvaluationQueryResult)
            .where(*filters)
            .order_by(EvaluationQueryResult.created_at, EvaluationQueryResult.id)
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return results, total


def get_evaluation_report_query(
    db: Session,
    evaluation_run_id: UUID,
) -> EvaluationReport | None:
    return db.scalar(
        select(EvaluationReport)
        .where(EvaluationReport.evaluation_run_id == evaluation_run_id)
        .order_by(EvaluationReport.created_at.desc(), EvaluationReport.id.desc())
    )


@router.post("/runs", response_model=StartEvaluationResponse)
async def start_evaluation_run(
    request: StartEvaluationRequest,
    _admin_context: AdminContext = Depends(require_admin),
) -> StartEvaluationResponse:
    name = request.name or _default_name(request.retrieval_mode)
    try:
        result = job_queue.enqueue_evaluation_job(
            name=name,
            retrieval_mode=request.retrieval_mode,
            experiment_config_id=str(request.experiment_config_id)
            if request.experiment_config_id
            else None,
            experiment_config_name=request.experiment_config_name,
            dataset_name=request.dataset_name,
            dataset_version=request.dataset_version,
            index_version_id=str(request.index_version_id) if request.index_version_id else None,
            query_limit=request.query_limit,
            query_offset=request.query_offset,
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
            detail="Redis queue unavailable for evaluation job.",
        ) from exc
    return StartEvaluationResponse(**result)


@router.get("/runs", response_model=EvaluationRunListResponse)
async def list_evaluation_runs(
    retrieval_mode: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> EvaluationRunListResponse:
    runs, total = list_evaluation_runs_query(
        db,
        retrieval_mode=retrieval_mode,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )
    return EvaluationRunListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[_run_item(run) for run in runs],
    )


@router.get("/runs/{evaluation_run_id}", response_model=EvaluationRunDetail)
async def get_evaluation_run(
    evaluation_run_id: UUID,
    db: Session = Depends(get_db),
) -> EvaluationRunDetail:
    run = get_evaluation_run_query(db, evaluation_run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation run not found: {evaluation_run_id}",
        )
    return _run_detail(run)


@router.get("/runs/{evaluation_run_id}/results", response_model=EvaluationQueryResultListResponse)
async def list_evaluation_results(
    evaluation_run_id: UUID,
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    failed_only: bool = False,
    db: Session = Depends(get_db),
) -> EvaluationQueryResultListResponse:
    if get_evaluation_run_query(db, evaluation_run_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation run not found: {evaluation_run_id}",
        )
    results, total = list_evaluation_results_query(
        db,
        evaluation_run_id=evaluation_run_id,
        failed_only=failed_only,
        limit=limit,
        offset=offset,
    )
    return EvaluationQueryResultListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[_result_item(result) for result in results],
    )


@router.get("/runs/{evaluation_run_id}/report", response_model=EvaluationReportResponse)
async def get_evaluation_report(
    evaluation_run_id: UUID,
    include_json: bool = True,
    db: Session = Depends(get_db),
) -> EvaluationReportResponse:
    if get_evaluation_run_query(db, evaluation_run_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation run not found: {evaluation_run_id}",
        )
    report = get_evaluation_report_query(db, evaluation_run_id)
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evaluation report not found for run: {evaluation_run_id}",
        )
    report_json = None
    warning = None
    if include_json and report.report_path:
        try:
            report_json = load_evaluation_report(report.report_path)
        except FileNotFoundError:
            warning = f"Report file missing: {report.report_path}"
    return EvaluationReportResponse(
        evaluation_run_id=evaluation_run_id,
        report_path=report.report_path,
        report_format=report.report_format,
        summary_json=report.summary_json,
        report_json=report_json,
        warning=warning,
    )
