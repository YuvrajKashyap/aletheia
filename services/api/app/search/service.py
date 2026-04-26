from __future__ import annotations

from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.queries import Query, QueryTrace, RetrievalCandidate
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    TraceCandidateItem,
    TraceDetailResponse,
    TraceListItem,
    TraceListResponse,
)
from app.search.lexical_retriever import search_bm25
from app.search.retrieval_models import LexicalSearchResult


TRACE_NOTE = (
    "Step 15 trace skeleton: BM25 only. Dense, hybrid, and reranker stages are not "
    "implemented yet."
)


def _uuid_or_none(value: str | UUID | None) -> UUID | None:
    if value is None:
        return None
    try:
        return value if isinstance(value, UUID) else UUID(str(value))
    except ValueError:
        return None


def _result_item(result: LexicalSearchResult) -> SearchResultItem:
    return SearchResultItem(
        rank=result.rank,
        chunk_id=result.chunk_id,
        document_id=result.document_id,
        dataset_id=result.dataset_id,
        document_external_id=result.document_external_id,
        chunk_external_id=result.chunk_external_id,
        title=result.title,
        text=result.text,
        score=result.score,
        score_breakdown={"bm25": result.score},
        token_count=result.token_count,
        chunking_strategy=result.chunking_strategy,
        chunking_version=result.chunking_version,
        metadata_json=result.metadata_json,
    )


def _candidate_metadata(result: LexicalSearchResult) -> dict[str, Any]:
    return {
        "document_external_id": result.document_external_id,
        "chunk_external_id": result.chunk_external_id,
        "title": result.title,
        "score_breakdown": {"bm25": result.score},
        "metadata_json": result.metadata_json,
    }


def _trace_json(
    request: SearchRequest,
    index_name: str,
    index_version_id: str | None,
    candidate_k: int,
    bm25_latency_ms: float,
    result_count: int,
) -> dict[str, Any]:
    return {
        "query": request.query,
        "retrieval_mode": request.retrieval_mode,
        "index_name": index_name,
        "index_version_id": index_version_id,
        "top_k": request.top_k,
        "candidate_k": candidate_k,
        "stages": {
            "bm25": {
                "latency_ms": bm25_latency_ms,
                "result_count": result_count,
                "index_name": index_name,
            }
        },
        "notes": [TRACE_NOTE],
    }


def run_search(
    db: Session,
    request: SearchRequest,
    request_id: str | None = None,
) -> SearchResponse:
    started = perf_counter()
    query_row = Query(
        text=request.query,
        retrieval_mode=request.retrieval_mode,
        index_version_id=request.index_version_id,
        request_id=request_id,
        status="running",
        metadata_json={
            "top_k": request.top_k,
            "candidate_k": request.candidate_k,
        },
    )
    db.add(query_row)
    db.commit()
    db.refresh(query_row)

    try:
        lexical_response = search_bm25(
            db,
            query=request.query,
            index_version_id=request.index_version_id,
            top_k=request.top_k,
            candidate_k=request.candidate_k,
        )
        candidate_k = request.candidate_k or request.top_k
        total_latency_ms = round((perf_counter() - started) * 1000, 2)
        resolved_index_version_id = _uuid_or_none(lexical_response.index_version_id)
        query_row.status = "completed"
        query_row.total_latency_ms = total_latency_ms
        query_row.index_version_id = resolved_index_version_id

        trace_row = QueryTrace(
            query_id=query_row.id,
            trace_json=_trace_json(
                request=request,
                index_name=lexical_response.index_name,
                index_version_id=lexical_response.index_version_id,
                candidate_k=candidate_k,
                bm25_latency_ms=lexical_response.latency_ms,
                result_count=len(lexical_response.results),
            ),
        )
        db.add(trace_row)
        db.flush()

        for result in lexical_response.results:
            db.add(
                RetrievalCandidate(
                    query_id=query_row.id,
                    trace_id=trace_row.id,
                    chunk_id=_uuid_or_none(result.chunk_id),
                    document_id=_uuid_or_none(result.document_id),
                    source="bm25",
                    bm25_rank=result.rank,
                    final_rank=result.rank,
                    bm25_score=result.score,
                    latency_ms=lexical_response.latency_ms,
                    metadata_json=_candidate_metadata(result),
                )
            )

        db.commit()
        db.refresh(query_row)
        db.refresh(trace_row)
        return SearchResponse(
            query_id=query_row.id,
            trace_id=trace_row.id,
            request_id=query_row.request_id,
            query=query_row.text,
            retrieval_mode=query_row.retrieval_mode,
            index_version_id=lexical_response.index_version_id,
            index_name=lexical_response.index_name,
            top_k=request.top_k,
            candidate_k=candidate_k,
            latency_ms=total_latency_ms,
            result_count=len(lexical_response.results),
            results=[_result_item(result) for result in lexical_response.results],
        )
    except Exception as exc:
        db.rollback()
        query_row = db.get(Query, query_row.id)
        if query_row is not None:
            query_row.status = "failed"
            query_row.error_message = str(exc)
            query_row.total_latency_ms = round((perf_counter() - started) * 1000, 2)
            db.commit()
        raise


def list_query_traces(
    db: Session,
    limit: int = 50,
    offset: int = 0,
) -> TraceListResponse:
    total = int(db.scalar(select(func.count()).select_from(QueryTrace)) or 0)
    rows = db.execute(
        select(QueryTrace, Query)
        .join(Query, QueryTrace.query_id == Query.id)
        .order_by(QueryTrace.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
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
                created_at=trace.created_at,
            )
            for trace, query in rows
        ],
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
        .order_by(RetrievalCandidate.final_rank.asc(), RetrievalCandidate.created_at.asc())
    ).all()
    return TraceDetailResponse(
        trace_id=trace.id,
        query_id=query.id,
        query_text=query.text,
        retrieval_mode=query.retrieval_mode,
        index_version_id=query.index_version_id,
        status=query.status,
        total_latency_ms=query.total_latency_ms,
        trace_json=trace.trace_json,
        candidates=[
            TraceCandidateItem(
                chunk_id=candidate.chunk_id,
                document_id=candidate.document_id,
                source=candidate.source,
                bm25_rank=candidate.bm25_rank,
                dense_rank=candidate.dense_rank,
                fusion_rank=candidate.fusion_rank,
                rerank_rank=candidate.rerank_rank,
                final_rank=candidate.final_rank,
                bm25_score=candidate.bm25_score,
                dense_score=candidate.dense_score,
                fusion_score=candidate.fusion_score,
                reranker_score=candidate.reranker_score,
                metadata_json=candidate.metadata_json,
            )
            for candidate in candidates
        ],
        created_at=trace.created_at,
    )
