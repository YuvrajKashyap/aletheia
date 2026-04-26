from __future__ import annotations

from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.indexing import IndexVersion
from app.models.queries import Query, QueryTrace, RetrievalCandidate
from app.models.system import SystemEvent
from app.schemas.search import (
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    TraceDetailResponse,
    TraceListResponse,
)
from app.search import trace_service
from app.search.dense_retriever import search_dense
from app.search.hybrid_retriever import search_hybrid
from app.search.lexical_retriever import search_bm25
from app.search.reranker import search_hybrid_rerank
from app.search.tracing import (
    build_base_trace,
    build_bm25_stage,
    build_dense_stage,
    build_fusion_stage,
    build_ranking_summary,
    build_reranker_stage,
)
from app.search.retrieval_models import (
    DenseSearchResponse,
    DenseSearchResult,
    HybridSearchResponse,
    HybridSearchResult,
    LexicalSearchResult,
    RerankedSearchResponse,
    RerankedSearchResult,
)


BM25_TRACE_NOTE = (
    "Step 15 trace skeleton: BM25 only. Dense, hybrid, and reranker stages are not "
    "implemented yet."
)
DENSE_TRACE_NOTE = (
    "Step 18 trace skeleton: dense only. Hybrid and reranker stages are not implemented yet."
)
HYBRID_TRACE_NOTE = (
    "Step 19 trace: hybrid BM25 + dense using Reciprocal Rank Fusion. "
    "Reranker is not implemented yet."
)
RERANK_TRACE_NOTE = (
    "Step 20 trace: hybrid retrieval reranked with cross-encoder. "
    "Evaluation metrics are not implemented yet."
)


def _uuid_or_none(value: str | UUID | None) -> UUID | None:
    if value is None:
        return None
    try:
        return value if isinstance(value, UUID) else UUID(str(value))
    except ValueError:
        return None


def _search_parameters(request: SearchRequest) -> dict[str, Any]:
    return {
        "top_k": request.top_k,
        "candidate_k": request.candidate_k,
        "bm25_candidate_k": request.bm25_candidate_k,
        "dense_candidate_k": request.dense_candidate_k,
        "hybrid_candidate_k": request.hybrid_candidate_k,
        "rerank_top_n": request.rerank_top_n,
        "rrf_k": request.rrf_k,
    }


def _load_index_version(db: Session, index_version_id: str | UUID | None):
    if index_version_id is None:
        return None
    try:
        return db.get(IndexVersion, UUID(str(index_version_id)))
    except Exception:
        return None


def _record_system_event(
    db: Session,
    event_type: str,
    severity: str,
    message: str,
    request_id: str | None,
    trace_id,
    metadata_json: dict[str, Any],
) -> None:
    try:
        db.add(
            SystemEvent(
                event_type=event_type,
                severity=severity,
                message=message,
                request_id=request_id,
                trace_id=_uuid_or_none(trace_id),
                metadata_json=metadata_json,
            )
        )
    except Exception:
        return


def _record_slow_query_event(
    db: Session,
    query_row: Query,
    trace_id,
) -> None:
    settings = get_settings()
    if query_row.total_latency_ms is None:
        return
    if query_row.total_latency_ms < settings.SEARCH_SLOW_QUERY_THRESHOLD_MS:
        return
    _record_system_event(
        db,
        event_type="SLOW_SEARCH_QUERY",
        severity="warning",
        message=f"Slow {query_row.retrieval_mode} search completed in {query_row.total_latency_ms} ms.",
        request_id=query_row.request_id,
        trace_id=trace_id,
        metadata_json={
            "query_id": str(query_row.id),
            "retrieval_mode": query_row.retrieval_mode,
            "total_latency_ms": query_row.total_latency_ms,
        },
    )


def _record_failed_query_event(
    db: Session,
    query_row: Query,
    trace_id,
    error: Exception,
) -> None:
    _record_system_event(
        db,
        event_type="SEARCH_QUERY_FAILED",
        severity="error",
        message=f"{query_row.retrieval_mode} search failed: {error}",
        request_id=query_row.request_id,
        trace_id=trace_id,
        metadata_json={
            "query_id": str(query_row.id),
            "retrieval_mode": query_row.retrieval_mode,
            "error": str(error),
        },
    )


def _create_trace_row(db: Session, query_row: Query, trace_json: dict[str, Any]) -> QueryTrace:
    trace_row = QueryTrace(query_id=query_row.id, trace_json=trace_json)
    db.add(trace_row)
    db.flush()
    trace_json["trace_id"] = str(trace_row.id)
    trace_row.trace_json = trace_json
    return trace_row


def _bm25_result_item(result: LexicalSearchResult) -> SearchResultItem:
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


def _dense_result_item(result: DenseSearchResult) -> SearchResultItem:
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
        score_breakdown={"dense": result.score},
        token_count=result.token_count,
        chunking_strategy=result.chunking_strategy,
        chunking_version=result.chunking_version,
        metadata_json=result.metadata_json,
    )


def _hybrid_score_breakdown(result: HybridSearchResult) -> dict[str, Any]:
    breakdown: dict[str, Any] = {"fusion": result.fusion_score}
    if result.bm25_score is not None:
        breakdown["bm25"] = result.bm25_score
    if result.dense_score is not None:
        breakdown["dense"] = result.dense_score
    if result.bm25_rank is not None:
        breakdown["bm25_rank"] = result.bm25_rank
    if result.dense_rank is not None:
        breakdown["dense_rank"] = result.dense_rank
    return breakdown


def _rerank_score_breakdown(result: RerankedSearchResult) -> dict[str, Any]:
    breakdown: dict[str, Any] = {
        "reranker": result.reranker_score,
        "rerank_rank": result.rerank_rank,
    }
    if result.fusion_score is not None:
        breakdown["fusion"] = result.fusion_score
    if result.bm25_score is not None:
        breakdown["bm25"] = result.bm25_score
    if result.dense_score is not None:
        breakdown["dense"] = result.dense_score
    if result.bm25_rank is not None:
        breakdown["bm25_rank"] = result.bm25_rank
    if result.dense_rank is not None:
        breakdown["dense_rank"] = result.dense_rank
    if result.fusion_rank is not None:
        breakdown["fusion_rank"] = result.fusion_rank
    return breakdown


def _hybrid_result_item(result: HybridSearchResult) -> SearchResultItem:
    return SearchResultItem(
        rank=result.rank,
        chunk_id=result.chunk_id,
        document_id=result.document_id,
        dataset_id=result.dataset_id,
        document_external_id=result.document_external_id,
        chunk_external_id=result.chunk_external_id,
        title=result.title,
        text=result.text,
        score=result.fusion_score,
        score_breakdown=_hybrid_score_breakdown(result),
        token_count=result.token_count,
        chunking_strategy=result.chunking_strategy,
        chunking_version=result.chunking_version,
        metadata_json=result.metadata_json,
    )


def _rerank_result_item(result: RerankedSearchResult) -> SearchResultItem:
    return SearchResultItem(
        rank=result.rank,
        chunk_id=result.chunk_id,
        document_id=result.document_id,
        dataset_id=result.dataset_id,
        document_external_id=result.document_external_id,
        chunk_external_id=result.chunk_external_id,
        title=result.title,
        text=result.text,
        score=result.reranker_score,
        score_breakdown=_rerank_score_breakdown(result),
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


def _dense_candidate_metadata(
    result: DenseSearchResult,
    collection_name: str,
    query_embedding_dimension: int | None,
) -> dict[str, Any]:
    return {
        "document_external_id": result.document_external_id,
        "chunk_external_id": result.chunk_external_id,
        "title": result.title,
        "collection_name": collection_name,
        "query_embedding_dimension": query_embedding_dimension,
        "score_breakdown": {"dense": result.score},
        "metadata_json": result.metadata_json,
    }


def _hybrid_candidate_metadata(
    result: HybridSearchResult,
    lexical_index_name: str | None,
    vector_collection_name: str | None,
    rrf_k: int,
) -> dict[str, Any]:
    return {
        "document_external_id": result.document_external_id,
        "chunk_external_id": result.chunk_external_id,
        "title": result.title,
        "lexical_index_name": lexical_index_name,
        "vector_collection_name": vector_collection_name,
        "rrf_k": rrf_k,
        "score_breakdown": _hybrid_score_breakdown(result),
        "metadata_json": result.metadata_json,
    }


def _rerank_candidate_metadata(
    result: RerankedSearchResult,
    lexical_index_name: str | None,
    vector_collection_name: str | None,
    rerank_top_n: int,
    rrf_k: int,
) -> dict[str, Any]:
    return {
        "document_external_id": result.document_external_id,
        "chunk_external_id": result.chunk_external_id,
        "title": result.title,
        "lexical_index_name": lexical_index_name,
        "vector_collection_name": vector_collection_name,
        "rerank_top_n": rerank_top_n,
        "rrf_k": rrf_k,
        "score_breakdown": _rerank_score_breakdown(result),
        "metadata_json": result.metadata_json,
    }


def _trace_json(
    request: SearchRequest,
    index_name: str,
    index_version_id: str | None,
    candidate_k: int,
    bm25_latency_ms: float,
    result_count: int,
    query_row: Query | None = None,
    trace_id=None,
    index_version=None,
    total_latency_ms: float | None = None,
    request_id: str | None = None,
    results: list[LexicalSearchResult] | None = None,
) -> dict[str, Any]:
    parameters = _search_parameters(request)
    parameters["candidate_k"] = candidate_k
    trace = build_base_trace(
        query=request.query,
        retrieval_mode=request.retrieval_mode,
        request_id=request_id or (query_row.request_id if query_row is not None else None),
        query_id=query_row.id if query_row is not None else None,
        trace_id=trace_id,
        index_version=index_version,
        parameters=parameters,
        total_latency_ms=total_latency_ms,
        warnings=[],
        errors=[],
    )
    trace["index_name"] = index_name
    trace["index_version_id"] = index_version_id
    trace["stages"]["bm25"] = build_bm25_stage(
        latency_ms=bm25_latency_ms,
        index_name=index_name,
        candidate_count=candidate_k,
        result_count=result_count,
    )
    trace["ranking_summary"] = build_ranking_summary(results or [], "bm25")
    trace["notes"] = [BM25_TRACE_NOTE]
    return trace


def _dense_trace_json(
    request: SearchRequest,
    dense_response: DenseSearchResponse,
    candidate_k: int,
    query_row: Query | None = None,
    trace_id=None,
    index_version=None,
    total_latency_ms: float | None = None,
) -> dict[str, Any]:
    parameters = _search_parameters(request)
    parameters["candidate_k"] = candidate_k
    trace = build_base_trace(
        query=request.query,
        retrieval_mode=request.retrieval_mode,
        request_id=query_row.request_id if query_row is not None else None,
        query_id=query_row.id if query_row is not None else None,
        trace_id=trace_id,
        index_version=index_version,
        parameters=parameters,
        total_latency_ms=total_latency_ms,
    )
    trace["collection_name"] = dense_response.collection_name
    trace["index_version_id"] = dense_response.index_version_id
    trace["stages"]["dense"] = build_dense_stage(
        latency_ms=dense_response.latency_ms,
        collection_name=dense_response.collection_name,
        candidate_count=candidate_k,
        result_count=len(dense_response.results),
        embedding_latency_ms=dense_response.embedding_latency_ms,
        qdrant_latency_ms=dense_response.qdrant_latency_ms,
        query_embedding_dimension=dense_response.query_embedding_dimension,
    )
    trace["ranking_summary"] = build_ranking_summary(dense_response.results, "dense")
    trace["notes"] = [DENSE_TRACE_NOTE]
    return trace


def _hybrid_trace_json(
    request: SearchRequest,
    hybrid_response: HybridSearchResponse,
    query_row: Query | None = None,
    trace_id=None,
    index_version=None,
    total_latency_ms: float | None = None,
) -> dict[str, Any]:
    trace = build_base_trace(
        query=request.query,
        retrieval_mode=request.retrieval_mode,
        request_id=query_row.request_id if query_row is not None else None,
        query_id=query_row.id if query_row is not None else None,
        trace_id=trace_id,
        index_version=index_version,
        parameters=_search_parameters(request),
        total_latency_ms=total_latency_ms,
    )
    trace["index_version_id"] = hybrid_response.index_version_id
    trace["lexical_index_name"] = hybrid_response.lexical_index_name
    trace["vector_collection_name"] = hybrid_response.vector_collection_name
    trace["stages"]["bm25"] = build_bm25_stage(
        latency_ms=hybrid_response.bm25_latency_ms,
        index_name=hybrid_response.lexical_index_name,
        candidate_count=hybrid_response.bm25_candidate_k,
        result_count=hybrid_response.bm25_candidate_k,
    )
    trace["stages"]["dense"] = build_dense_stage(
        latency_ms=hybrid_response.dense_latency_ms,
        collection_name=hybrid_response.vector_collection_name,
        candidate_count=hybrid_response.dense_candidate_k,
        result_count=hybrid_response.dense_candidate_k,
        embedding_latency_ms=hybrid_response.embedding_latency_ms,
        qdrant_latency_ms=hybrid_response.qdrant_latency_ms,
    )
    trace["stages"]["fusion"] = build_fusion_stage(
        latency_ms=hybrid_response.fusion_latency_ms,
        rrf_k=hybrid_response.rrf_k,
        fused_candidate_count=hybrid_response.result_count,
        result_count=len(hybrid_response.results),
    )
    trace["ranking_summary"] = build_ranking_summary(hybrid_response.results, "hybrid")
    trace["notes"] = [HYBRID_TRACE_NOTE]
    return trace


def _rerank_trace_json(
    request: SearchRequest,
    rerank_response: RerankedSearchResponse,
    query_row: Query | None = None,
    trace_id=None,
    index_version=None,
    total_latency_ms: float | None = None,
) -> dict[str, Any]:
    trace = build_base_trace(
        query=request.query,
        retrieval_mode=request.retrieval_mode,
        request_id=query_row.request_id if query_row is not None else None,
        query_id=query_row.id if query_row is not None else None,
        trace_id=trace_id,
        index_version=index_version,
        parameters=_search_parameters(request),
        total_latency_ms=total_latency_ms,
    )
    trace["index_version_id"] = rerank_response.index_version_id
    trace["lexical_index_name"] = rerank_response.lexical_index_name
    trace["vector_collection_name"] = rerank_response.vector_collection_name
    trace["stages"]["bm25"] = build_bm25_stage(
        latency_ms=rerank_response.bm25_latency_ms,
        index_name=rerank_response.lexical_index_name,
        candidate_count=rerank_response.bm25_candidate_k,
        result_count=rerank_response.bm25_candidate_k,
    )
    trace["stages"]["dense"] = build_dense_stage(
        latency_ms=rerank_response.dense_latency_ms,
        collection_name=rerank_response.vector_collection_name,
        candidate_count=rerank_response.dense_candidate_k,
        result_count=rerank_response.dense_candidate_k,
        embedding_latency_ms=rerank_response.embedding_latency_ms,
        qdrant_latency_ms=rerank_response.qdrant_latency_ms,
    )
    trace["stages"]["fusion"] = build_fusion_stage(
        latency_ms=rerank_response.fusion_latency_ms,
        rrf_k=rerank_response.rrf_k,
        fused_candidate_count=rerank_response.hybrid_candidate_k,
        result_count=rerank_response.hybrid_candidate_k,
    )
    trace["stages"]["reranker"] = build_reranker_stage(
        latency_ms=rerank_response.reranker_latency_ms,
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
        rerank_top_n=rerank_response.rerank_top_n,
        scored_count=min(rerank_response.rerank_top_n, rerank_response.hybrid_candidate_k),
        result_count=len(rerank_response.results),
    )
    trace["ranking_summary"] = build_ranking_summary(rerank_response.results, "hybrid_rerank")
    trace["notes"] = [RERANK_TRACE_NOTE]
    return trace


def _run_bm25_search(
    db: Session,
    request: SearchRequest,
    query_row: Query,
    started: float,
) -> SearchResponse:
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

    index_version = _load_index_version(db, lexical_response.index_version_id)
    trace_row = _create_trace_row(
        db,
        query_row,
        _trace_json(
            request=request,
            index_name=lexical_response.index_name,
            index_version_id=lexical_response.index_version_id,
            candidate_k=candidate_k,
            bm25_latency_ms=lexical_response.latency_ms,
            result_count=len(lexical_response.results),
            query_row=query_row,
            index_version=index_version,
            total_latency_ms=total_latency_ms,
            results=lexical_response.results,
        ),
    )

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

    _record_slow_query_event(db, query_row, trace_row.id)
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
        collection_name=None,
        lexical_index_name=lexical_response.index_name,
        vector_collection_name=None,
        top_k=request.top_k,
        candidate_k=candidate_k,
        latency_ms=total_latency_ms,
        bm25_latency_ms=lexical_response.latency_ms,
        result_count=len(lexical_response.results),
        results=[_bm25_result_item(result) for result in lexical_response.results],
    )


def _run_dense_search(
    db: Session,
    request: SearchRequest,
    query_row: Query,
    started: float,
) -> SearchResponse:
    dense_response = search_dense(
        db,
        query=request.query,
        index_version_id=request.index_version_id,
        top_k=request.top_k,
        candidate_k=request.candidate_k,
    )
    candidate_k = request.candidate_k or request.top_k
    total_latency_ms = round((perf_counter() - started) * 1000, 2)
    resolved_index_version_id = _uuid_or_none(dense_response.index_version_id)
    query_row.status = "completed"
    query_row.total_latency_ms = total_latency_ms
    query_row.index_version_id = resolved_index_version_id

    index_version = _load_index_version(db, dense_response.index_version_id)
    trace_row = _create_trace_row(
        db,
        query_row,
        _dense_trace_json(
            request=request,
            dense_response=dense_response,
            candidate_k=candidate_k,
            query_row=query_row,
            index_version=index_version,
            total_latency_ms=total_latency_ms,
        ),
    )

    for result in dense_response.results:
        db.add(
            RetrievalCandidate(
                query_id=query_row.id,
                trace_id=trace_row.id,
                chunk_id=_uuid_or_none(result.chunk_id),
                document_id=_uuid_or_none(result.document_id),
                source="dense",
                dense_rank=result.rank,
                final_rank=result.rank,
                dense_score=result.score,
                latency_ms=dense_response.latency_ms,
                metadata_json=_dense_candidate_metadata(
                    result,
                    dense_response.collection_name,
                    dense_response.query_embedding_dimension,
                ),
            )
        )

    _record_slow_query_event(db, query_row, trace_row.id)
    db.commit()
    db.refresh(query_row)
    db.refresh(trace_row)
    return SearchResponse(
        query_id=query_row.id,
        trace_id=trace_row.id,
        request_id=query_row.request_id,
        query=query_row.text,
        retrieval_mode=query_row.retrieval_mode,
        index_version_id=dense_response.index_version_id,
        index_name=None,
        collection_name=dense_response.collection_name,
        lexical_index_name=None,
        vector_collection_name=dense_response.collection_name,
        top_k=request.top_k,
        candidate_k=candidate_k,
        latency_ms=total_latency_ms,
        embedding_latency_ms=dense_response.embedding_latency_ms,
        qdrant_latency_ms=dense_response.qdrant_latency_ms,
        result_count=len(dense_response.results),
        results=[_dense_result_item(result) for result in dense_response.results],
    )


def _run_hybrid_search(
    db: Session,
    request: SearchRequest,
    query_row: Query,
    started: float,
) -> SearchResponse:
    hybrid_response = search_hybrid(
        db,
        query=request.query,
        index_version_id=request.index_version_id,
        top_k=request.top_k,
        bm25_candidate_k=request.bm25_candidate_k or 50,
        dense_candidate_k=request.dense_candidate_k or 50,
        rrf_k=request.rrf_k,
    )
    total_latency_ms = round((perf_counter() - started) * 1000, 2)
    resolved_index_version_id = _uuid_or_none(hybrid_response.index_version_id)
    query_row.status = "completed"
    query_row.total_latency_ms = total_latency_ms
    query_row.index_version_id = resolved_index_version_id

    index_version = _load_index_version(db, hybrid_response.index_version_id)
    trace_row = _create_trace_row(
        db,
        query_row,
        _hybrid_trace_json(
            request=request,
            hybrid_response=hybrid_response,
            query_row=query_row,
            index_version=index_version,
            total_latency_ms=total_latency_ms,
        ),
    )

    for result in hybrid_response.results:
        db.add(
            RetrievalCandidate(
                query_id=query_row.id,
                trace_id=trace_row.id,
                chunk_id=_uuid_or_none(result.chunk_id),
                document_id=_uuid_or_none(result.document_id),
                source="hybrid_rrf",
                bm25_rank=result.bm25_rank,
                dense_rank=result.dense_rank,
                fusion_rank=result.rank,
                final_rank=result.rank,
                bm25_score=result.bm25_score,
                dense_score=result.dense_score,
                fusion_score=result.fusion_score,
                latency_ms=hybrid_response.latency_ms,
                metadata_json=_hybrid_candidate_metadata(
                    result,
                    hybrid_response.lexical_index_name,
                    hybrid_response.vector_collection_name,
                    hybrid_response.rrf_k,
                ),
            )
        )

    _record_slow_query_event(db, query_row, trace_row.id)
    db.commit()
    db.refresh(query_row)
    db.refresh(trace_row)
    return SearchResponse(
        query_id=query_row.id,
        trace_id=trace_row.id,
        request_id=query_row.request_id,
        query=query_row.text,
        retrieval_mode=query_row.retrieval_mode,
        index_version_id=hybrid_response.index_version_id,
        index_name=hybrid_response.lexical_index_name,
        collection_name=hybrid_response.vector_collection_name,
        lexical_index_name=hybrid_response.lexical_index_name,
        vector_collection_name=hybrid_response.vector_collection_name,
        top_k=request.top_k,
        candidate_k=max(hybrid_response.bm25_candidate_k, hybrid_response.dense_candidate_k),
        bm25_candidate_k=hybrid_response.bm25_candidate_k,
        dense_candidate_k=hybrid_response.dense_candidate_k,
        rrf_k=hybrid_response.rrf_k,
        latency_ms=total_latency_ms,
        bm25_latency_ms=hybrid_response.bm25_latency_ms,
        embedding_latency_ms=hybrid_response.embedding_latency_ms,
        qdrant_latency_ms=hybrid_response.qdrant_latency_ms,
        fusion_latency_ms=hybrid_response.fusion_latency_ms,
        result_count=len(hybrid_response.results),
        results=[_hybrid_result_item(result) for result in hybrid_response.results],
    )


def _run_hybrid_rerank_search(
    db: Session,
    request: SearchRequest,
    query_row: Query,
    started: float,
) -> SearchResponse:
    rerank_response = search_hybrid_rerank(
        db,
        query=request.query,
        index_version_id=request.index_version_id,
        top_k=request.top_k,
        bm25_candidate_k=request.bm25_candidate_k or 50,
        dense_candidate_k=request.dense_candidate_k or 50,
        hybrid_candidate_k=request.hybrid_candidate_k or 50,
        rerank_top_n=request.rerank_top_n or 25,
        rrf_k=request.rrf_k,
    )
    total_latency_ms = round((perf_counter() - started) * 1000, 2)
    resolved_index_version_id = _uuid_or_none(rerank_response.index_version_id)
    query_row.status = "completed"
    query_row.total_latency_ms = total_latency_ms
    query_row.index_version_id = resolved_index_version_id

    index_version = _load_index_version(db, rerank_response.index_version_id)
    trace_row = _create_trace_row(
        db,
        query_row,
        _rerank_trace_json(
            request=request,
            rerank_response=rerank_response,
            query_row=query_row,
            index_version=index_version,
            total_latency_ms=total_latency_ms,
        ),
    )

    for result in rerank_response.results:
        db.add(
            RetrievalCandidate(
                query_id=query_row.id,
                trace_id=trace_row.id,
                chunk_id=_uuid_or_none(result.chunk_id),
                document_id=_uuid_or_none(result.document_id),
                source="hybrid_rerank",
                bm25_rank=result.bm25_rank,
                dense_rank=result.dense_rank,
                fusion_rank=result.fusion_rank,
                rerank_rank=result.rerank_rank,
                final_rank=result.rank,
                bm25_score=result.bm25_score,
                dense_score=result.dense_score,
                fusion_score=result.fusion_score,
                reranker_score=result.reranker_score,
                latency_ms=rerank_response.latency_ms,
                metadata_json=_rerank_candidate_metadata(
                    result,
                    rerank_response.lexical_index_name,
                    rerank_response.vector_collection_name,
                    rerank_response.rerank_top_n,
                    rerank_response.rrf_k,
                ),
            )
        )

    _record_slow_query_event(db, query_row, trace_row.id)
    db.commit()
    db.refresh(query_row)
    db.refresh(trace_row)
    return SearchResponse(
        query_id=query_row.id,
        trace_id=trace_row.id,
        request_id=query_row.request_id,
        query=query_row.text,
        retrieval_mode=query_row.retrieval_mode,
        index_version_id=rerank_response.index_version_id,
        index_name=rerank_response.lexical_index_name,
        collection_name=rerank_response.vector_collection_name,
        lexical_index_name=rerank_response.lexical_index_name,
        vector_collection_name=rerank_response.vector_collection_name,
        top_k=request.top_k,
        candidate_k=max(rerank_response.bm25_candidate_k, rerank_response.dense_candidate_k),
        bm25_candidate_k=rerank_response.bm25_candidate_k,
        dense_candidate_k=rerank_response.dense_candidate_k,
        hybrid_candidate_k=rerank_response.hybrid_candidate_k,
        rerank_top_n=rerank_response.rerank_top_n,
        rrf_k=rerank_response.rrf_k,
        latency_ms=total_latency_ms,
        bm25_latency_ms=rerank_response.bm25_latency_ms,
        embedding_latency_ms=rerank_response.embedding_latency_ms,
        qdrant_latency_ms=rerank_response.qdrant_latency_ms,
        fusion_latency_ms=rerank_response.fusion_latency_ms,
        reranker_latency_ms=rerank_response.reranker_latency_ms,
        result_count=len(rerank_response.results),
        results=[_rerank_result_item(result) for result in rerank_response.results],
    )


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
            "bm25_candidate_k": request.bm25_candidate_k,
            "dense_candidate_k": request.dense_candidate_k,
            "hybrid_candidate_k": request.hybrid_candidate_k,
            "rerank_top_n": request.rerank_top_n,
            "rrf_k": request.rrf_k,
        },
    )
    db.add(query_row)
    db.commit()
    db.refresh(query_row)

    try:
        if request.retrieval_mode == "bm25":
            return _run_bm25_search(db, request, query_row, started)
        if request.retrieval_mode == "dense":
            return _run_dense_search(db, request, query_row, started)
        if request.retrieval_mode == "hybrid":
            return _run_hybrid_search(db, request, query_row, started)
        if request.retrieval_mode == "hybrid_rerank":
            return _run_hybrid_rerank_search(db, request, query_row, started)
        raise ValueError(f"Unsupported retrieval mode: {request.retrieval_mode}")
    except Exception as exc:
        db.rollback()
        query_row = db.get(Query, query_row.id)
        if query_row is not None:
            query_row.status = "failed"
            query_row.error_message = str(exc)
            query_row.total_latency_ms = round((perf_counter() - started) * 1000, 2)
            trace_row = None
            try:
                trace_row = _create_trace_row(
                    db,
                    query_row,
                    build_base_trace(
                        query=request.query,
                        retrieval_mode=request.retrieval_mode,
                        request_id=query_row.request_id,
                        query_id=query_row.id,
                        trace_id=None,
                        index_version=_load_index_version(db, query_row.index_version_id),
                        parameters=_search_parameters(request),
                        total_latency_ms=query_row.total_latency_ms,
                        errors=[
                            {
                                "type": exc.__class__.__name__,
                                "message": str(exc),
                            }
                        ],
                    ),
                )
            except Exception:
                db.rollback()
                query_row = db.get(Query, query_row.id)
                if query_row is not None:
                    query_row.status = "failed"
                    query_row.error_message = str(exc)
                    query_row.total_latency_ms = round((perf_counter() - started) * 1000, 2)
            if query_row is not None:
                _record_failed_query_event(
                    db,
                    query_row,
                    trace_row.id if trace_row is not None else None,
                    exc,
                )
            db.commit()
        raise


def list_query_traces(
    db: Session,
    retrieval_mode: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> TraceListResponse:
    return trace_service.list_query_traces(
        db,
        retrieval_mode=retrieval_mode,
        status=status,
        limit=limit,
        offset=offset,
    )


def get_query_trace_detail(
    db: Session,
    trace_id,
) -> TraceDetailResponse | None:
    return trace_service.get_query_trace_detail(db, trace_id)


def list_trace_candidates(
    db: Session,
    trace_id,
    source: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    return trace_service.list_trace_candidates(
        db,
        trace_id=trace_id,
        source=source,
        limit=limit,
        offset=offset,
    )
