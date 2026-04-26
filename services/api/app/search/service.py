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
from app.search.dense_retriever import search_dense
from app.search.hybrid_retriever import search_hybrid
from app.search.lexical_retriever import search_bm25
from app.search.reranker import search_hybrid_rerank
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
        "notes": [BM25_TRACE_NOTE],
    }


def _dense_trace_json(
    request: SearchRequest,
    dense_response: DenseSearchResponse,
    candidate_k: int,
) -> dict[str, Any]:
    return {
        "query": request.query,
        "retrieval_mode": request.retrieval_mode,
        "collection_name": dense_response.collection_name,
        "index_version_id": dense_response.index_version_id,
        "top_k": request.top_k,
        "candidate_k": candidate_k,
        "stages": {
            "dense": {
                "total_latency_ms": dense_response.latency_ms,
                "embedding_latency_ms": dense_response.embedding_latency_ms,
                "qdrant_latency_ms": dense_response.qdrant_latency_ms,
                "result_count": len(dense_response.results),
                "collection_name": dense_response.collection_name,
                "query_embedding_dimension": dense_response.query_embedding_dimension,
            }
        },
        "notes": [DENSE_TRACE_NOTE],
    }


def _hybrid_trace_json(
    request: SearchRequest,
    hybrid_response: HybridSearchResponse,
) -> dict[str, Any]:
    return {
        "query": request.query,
        "retrieval_mode": request.retrieval_mode,
        "index_version_id": hybrid_response.index_version_id,
        "lexical_index_name": hybrid_response.lexical_index_name,
        "vector_collection_name": hybrid_response.vector_collection_name,
        "top_k": request.top_k,
        "bm25_candidate_k": hybrid_response.bm25_candidate_k,
        "dense_candidate_k": hybrid_response.dense_candidate_k,
        "rrf_k": hybrid_response.rrf_k,
        "stages": {
            "bm25": {
                "latency_ms": hybrid_response.bm25_latency_ms,
                "candidate_count": hybrid_response.bm25_candidate_k,
                "index_name": hybrid_response.lexical_index_name,
            },
            "dense": {
                "latency_ms": hybrid_response.dense_latency_ms,
                "embedding_latency_ms": hybrid_response.embedding_latency_ms,
                "qdrant_latency_ms": hybrid_response.qdrant_latency_ms,
                "candidate_count": hybrid_response.dense_candidate_k,
                "collection_name": hybrid_response.vector_collection_name,
            },
            "fusion": {
                "latency_ms": hybrid_response.fusion_latency_ms,
                "method": "reciprocal_rank_fusion",
                "rrf_k": hybrid_response.rrf_k,
                "fused_candidate_count": hybrid_response.result_count,
                "result_count": len(hybrid_response.results),
            },
        },
        "notes": [HYBRID_TRACE_NOTE],
    }


def _rerank_trace_json(
    request: SearchRequest,
    rerank_response: RerankedSearchResponse,
) -> dict[str, Any]:
    return {
        "query": request.query,
        "retrieval_mode": request.retrieval_mode,
        "index_version_id": rerank_response.index_version_id,
        "lexical_index_name": rerank_response.lexical_index_name,
        "vector_collection_name": rerank_response.vector_collection_name,
        "top_k": request.top_k,
        "bm25_candidate_k": rerank_response.bm25_candidate_k,
        "dense_candidate_k": rerank_response.dense_candidate_k,
        "hybrid_candidate_k": rerank_response.hybrid_candidate_k,
        "rerank_top_n": rerank_response.rerank_top_n,
        "rrf_k": rerank_response.rrf_k,
        "stages": {
            "bm25": {
                "latency_ms": rerank_response.bm25_latency_ms,
                "candidate_count": rerank_response.bm25_candidate_k,
                "index_name": rerank_response.lexical_index_name,
            },
            "dense": {
                "latency_ms": rerank_response.dense_latency_ms,
                "embedding_latency_ms": rerank_response.embedding_latency_ms,
                "qdrant_latency_ms": rerank_response.qdrant_latency_ms,
                "candidate_count": rerank_response.dense_candidate_k,
                "collection_name": rerank_response.vector_collection_name,
            },
            "fusion": {
                "latency_ms": rerank_response.fusion_latency_ms,
                "method": "reciprocal_rank_fusion",
                "rrf_k": rerank_response.rrf_k,
                "fused_candidate_count": rerank_response.hybrid_candidate_k,
            },
            "reranker": {
                "latency_ms": rerank_response.reranker_latency_ms,
                "model_name": "cross-encoder/ms-marco-MiniLM-L-6-v2",
                "rerank_top_n": rerank_response.rerank_top_n,
                "scored_count": min(rerank_response.rerank_top_n, rerank_response.hybrid_candidate_k),
                "result_count": len(rerank_response.results),
            },
        },
        "notes": [RERANK_TRACE_NOTE],
    }


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

    trace_row = QueryTrace(
        query_id=query_row.id,
        trace_json=_dense_trace_json(
            request=request,
            dense_response=dense_response,
            candidate_k=candidate_k,
        ),
    )
    db.add(trace_row)
    db.flush()

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

    trace_row = QueryTrace(
        query_id=query_row.id,
        trace_json=_hybrid_trace_json(
            request=request,
            hybrid_response=hybrid_response,
        ),
    )
    db.add(trace_row)
    db.flush()

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

    trace_row = QueryTrace(
        query_id=query_row.id,
        trace_json=_rerank_trace_json(
            request=request,
            rerank_response=rerank_response,
        ),
    )
    db.add(trace_row)
    db.flush()

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
