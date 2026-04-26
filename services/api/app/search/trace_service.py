from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.queries import Query, QueryTrace, RetrievalCandidate
from app.schemas.search import (
    TraceCandidateItem,
    TraceCandidateListResponse,
    TraceDetailResponse,
    TraceListItem,
    TraceListResponse,
)
from app.search.tracing import group_candidates_by_source, serialize_candidate_for_trace


def _result_count(trace_json: dict) -> int | None:
    summary = trace_json.get("ranking_summary") or {}
    if summary.get("result_count") is not None:
        return int(summary["result_count"])
    stages = trace_json.get("stages") or {}
    for stage_name in ("reranker", "fusion", "dense", "bm25"):
        stage = stages.get(stage_name) or {}
        if stage.get("result_count") is not None:
            return int(stage["result_count"])
    return None


def _candidate_item(candidate: RetrievalCandidate) -> TraceCandidateItem:
    return TraceCandidateItem(**serialize_candidate_for_trace(candidate))


def list_query_traces(
    db: Session,
    retrieval_mode: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> TraceListResponse:
    total_statement = select(func.count()).select_from(QueryTrace).join(Query, QueryTrace.query_id == Query.id)
    rows_statement = (
        select(QueryTrace, Query)
        .join(Query, QueryTrace.query_id == Query.id)
        .order_by(QueryTrace.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if retrieval_mode is not None:
        total_statement = total_statement.where(Query.retrieval_mode == retrieval_mode)
        rows_statement = rows_statement.where(Query.retrieval_mode == retrieval_mode)
    if status is not None:
        total_statement = total_statement.where(Query.status == status)
        rows_statement = rows_statement.where(Query.status == status)

    total = int(db.scalar(total_statement) or 0)
    rows = db.execute(rows_statement).all()
    return TraceListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[
            TraceListItem(
                trace_id=trace.id,
                query_id=query.id,
                query_text=query.text,
                retrieval_mode=query.retrieval_mode,
                status=query.status,
                total_latency_ms=query.total_latency_ms,
                result_count=_result_count(getattr(trace, "trace_json", {}) or {}),
                created_at=trace.created_at,
            )
            for trace, query in rows
        ],
    )


def list_trace_candidates(
    db: Session,
    trace_id,
    source: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> TraceCandidateListResponse | None:
    trace = db.get(QueryTrace, UUID(str(trace_id)))
    if trace is None:
        return None

    total_statement = select(func.count()).select_from(RetrievalCandidate).where(
        RetrievalCandidate.trace_id == trace.id
    )
    rows_statement = (
        select(RetrievalCandidate)
        .where(RetrievalCandidate.trace_id == trace.id)
        .order_by(
            RetrievalCandidate.final_rank.asc().nullslast(),
            RetrievalCandidate.created_at.asc(),
            RetrievalCandidate.id.asc(),
        )
        .limit(limit)
        .offset(offset)
    )
    if source is not None:
        total_statement = total_statement.where(RetrievalCandidate.source == source)
        rows_statement = rows_statement.where(RetrievalCandidate.source == source)

    total = int(db.scalar(total_statement) or 0)
    candidates = db.scalars(rows_statement).all()
    return TraceCandidateListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[_candidate_item(candidate) for candidate in candidates],
    )


def get_query_trace_detail(
    db: Session,
    trace_id,
) -> TraceDetailResponse | None:
    row = db.execute(
        select(QueryTrace, Query)
        .join(Query, QueryTrace.query_id == Query.id)
        .where(QueryTrace.id == trace_id)
    ).first()
    if row is None:
        return None
    trace, query = row
    candidates = db.scalars(
        select(RetrievalCandidate)
        .where(RetrievalCandidate.trace_id == trace.id)
        .order_by(
            RetrievalCandidate.final_rank.asc().nullslast(),
            RetrievalCandidate.created_at.asc(),
            RetrievalCandidate.id.asc(),
        )
    ).all()
    serialized_candidates = [serialize_candidate_for_trace(candidate) for candidate in candidates]
    trace_json = trace.trace_json or {}
    return TraceDetailResponse(
        trace_id=trace.id,
        query_id=query.id,
        query_text=query.text,
        retrieval_mode=query.retrieval_mode,
        index_version_id=query.index_version_id,
        status=query.status,
        total_latency_ms=query.total_latency_ms,
        trace_schema_version=trace_json.get("trace_schema_version"),
        trace_json=trace_json,
        ranking_summary=trace_json.get("ranking_summary") or {},
        candidates=[TraceCandidateItem(**candidate) for candidate in serialized_candidates],
        candidates_by_source=group_candidates_by_source(serialized_candidates),
        created_at=trace.created_at,
    )
