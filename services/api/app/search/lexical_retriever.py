from __future__ import annotations

from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.indexing import IndexVersion
from app.search.opensearch_client import get_opensearch_client
from app.search.retrieval_models import LexicalSearchResponse, LexicalSearchResult


class RetrievalError(RuntimeError):
    pass


class NoActiveIndexError(RetrievalError):
    pass


class InvalidSearchRequestError(ValueError):
    pass


def _validate_search_request(
    query: str,
    top_k: int,
    candidate_k: int | None,
) -> tuple[str, int]:
    normalized_query = query.strip()
    if not normalized_query:
        raise InvalidSearchRequestError("BM25 query must not be empty.")
    if top_k < 1 or top_k > 100:
        raise InvalidSearchRequestError("top_k must be between 1 and 100.")
    resolved_candidate_k = candidate_k if candidate_k is not None else top_k
    if resolved_candidate_k < top_k:
        raise InvalidSearchRequestError("candidate_k must be greater than or equal to top_k.")
    return normalized_query, resolved_candidate_k


def _parse_total_hits(total_hits: Any) -> int | None:
    if isinstance(total_hits, dict):
        value = total_hits.get("value")
        return int(value) if value is not None else None
    if isinstance(total_hits, int):
        return total_hits
    return None


def _source_value(source: dict, key: str) -> Any:
    return source.get(key)


def _result_from_hit(rank: int, hit: dict) -> LexicalSearchResult:
    source = hit.get("_source") or {}
    return LexicalSearchResult(
        rank=rank,
        chunk_id=str(_source_value(source, "chunk_id") or hit.get("_id") or ""),
        document_id=(
            str(_source_value(source, "document_id"))
            if _source_value(source, "document_id") is not None
            else None
        ),
        dataset_id=(
            str(_source_value(source, "dataset_id"))
            if _source_value(source, "dataset_id") is not None
            else None
        ),
        document_external_id=_source_value(source, "document_external_id"),
        chunk_external_id=_source_value(source, "chunk_external_id"),
        title=_source_value(source, "title"),
        text=str(_source_value(source, "text") or ""),
        score=float(hit.get("_score") or 0.0),
        token_count=_source_value(source, "token_count"),
        content_hash=_source_value(source, "content_hash"),
        chunking_strategy=_source_value(source, "chunking_strategy"),
        chunking_version=_source_value(source, "chunking_version"),
        metadata_json=dict(_source_value(source, "metadata_json") or {}),
    )


def _bm25_query_body(query: str, candidate_k: int) -> dict:
    return {
        "size": candidate_k,
        "query": {
            "bool": {
                "should": [
                    {"match": {"text": {"query": query}}},
                    {"match": {"title": {"query": query, "boost": 0.5}}},
                ],
                "minimum_should_match": 1,
            }
        },
    }


def search_bm25_by_index_name(
    query: str,
    index_name: str,
    top_k: int = 10,
    candidate_k: int | None = None,
) -> LexicalSearchResponse:
    normalized_query, resolved_candidate_k = _validate_search_request(query, top_k, candidate_k)
    started = perf_counter()
    client = get_opensearch_client()
    response = client.search(
        index=index_name,
        body=_bm25_query_body(normalized_query, resolved_candidate_k),
    )
    hits_payload = response.get("hits") or {}
    hits = hits_payload.get("hits") or []
    results = [
        _result_from_hit(rank, hit)
        for rank, hit in enumerate(hits[:top_k], start=1)
    ]
    return LexicalSearchResponse(
        query=normalized_query,
        index_version_id=None,
        index_name=index_name,
        top_k=top_k,
        total_hits=_parse_total_hits(hits_payload.get("total")),
        results=results,
        latency_ms=round((perf_counter() - started) * 1000, 2),
    )


def search_bm25(
    db: Session,
    query: str,
    index_version_id: UUID | str | None = None,
    top_k: int = 10,
    candidate_k: int | None = None,
) -> LexicalSearchResponse:
    _validate_search_request(query, top_k, candidate_k)
    if index_version_id is not None:
        index_version = db.get(IndexVersion, UUID(str(index_version_id)))
        if index_version is None:
            raise RetrievalError(f"Index version not found: {index_version_id}")
    else:
        index_version = db.scalar(
            select(IndexVersion)
            .where(IndexVersion.is_active.is_(True))
            .order_by(IndexVersion.activated_at.desc(), IndexVersion.created_at.desc())
            .limit(1)
        )
        if index_version is None:
            raise NoActiveIndexError("No active index version is available for BM25 retrieval.")

    if not index_version.lexical_index_name:
        raise RetrievalError("Index version does not have a lexical OpenSearch index name.")

    response = search_bm25_by_index_name(
        query=query,
        index_name=index_version.lexical_index_name,
        top_k=top_k,
        candidate_k=candidate_k,
    )
    return LexicalSearchResponse(
        query=response.query,
        index_version_id=str(index_version.id),
        index_name=response.index_name,
        top_k=response.top_k,
        total_hits=response.total_hits,
        results=response.results,
        latency_ms=response.latency_ms,
    )
