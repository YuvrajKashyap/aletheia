from __future__ import annotations

from time import perf_counter
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.ml.embeddings import embed_text
from app.models.indexing import IndexVersion
from app.search.qdrant_client import get_qdrant_client
from app.search.retrieval_models import DenseSearchResponse, DenseSearchResult


class DenseRetrievalError(RuntimeError):
    pass


class NoVectorIndexError(DenseRetrievalError):
    pass


class InvalidDenseSearchRequestError(ValueError):
    pass


def _validate_dense_search_request(
    query: str,
    top_k: int,
    candidate_k: int | None,
) -> tuple[str, int]:
    normalized_query = query.strip()
    if not normalized_query:
        raise InvalidDenseSearchRequestError("Dense query must not be empty.")
    if top_k < 1 or top_k > 100:
        raise InvalidDenseSearchRequestError("top_k must be between 1 and 100.")
    resolved_candidate_k = candidate_k if candidate_k is not None else top_k
    if resolved_candidate_k < top_k:
        raise InvalidDenseSearchRequestError("candidate_k must be greater than or equal to top_k.")
    return normalized_query, resolved_candidate_k


def _payload_value(payload: dict[str, Any], key: str) -> Any:
    return payload.get(key)


def _point_payload(point: Any) -> dict[str, Any]:
    if isinstance(point, dict):
        return dict(point.get("payload") or {})
    return dict(getattr(point, "payload", None) or {})


def _point_score(point: Any) -> float:
    if isinstance(point, dict):
        return float(point.get("score") or 0.0)
    return float(getattr(point, "score", 0.0) or 0.0)


def _point_id(point: Any) -> str | None:
    if isinstance(point, dict):
        value = point.get("id")
    else:
        value = getattr(point, "id", None)
    return str(value) if value is not None else None


def _result_from_point(rank: int, point: Any) -> DenseSearchResult:
    payload = _point_payload(point)
    chunk_id = _payload_value(payload, "chunk_id") or _point_id(point) or ""
    return DenseSearchResult(
        rank=rank,
        chunk_id=str(chunk_id),
        document_id=(
            str(_payload_value(payload, "document_id"))
            if _payload_value(payload, "document_id") is not None
            else None
        ),
        dataset_id=(
            str(_payload_value(payload, "dataset_id"))
            if _payload_value(payload, "dataset_id") is not None
            else None
        ),
        index_version_id=(
            str(_payload_value(payload, "index_version_id"))
            if _payload_value(payload, "index_version_id") is not None
            else None
        ),
        document_external_id=_payload_value(payload, "document_external_id"),
        chunk_external_id=_payload_value(payload, "chunk_external_id"),
        title=_payload_value(payload, "title"),
        text=str(_payload_value(payload, "text") or ""),
        score=_point_score(point),
        token_count=_payload_value(payload, "token_count"),
        content_hash=_payload_value(payload, "content_hash"),
        chunking_strategy=_payload_value(payload, "chunking_strategy"),
        chunking_version=_payload_value(payload, "chunking_version"),
        metadata_json=dict(_payload_value(payload, "metadata_json") or {}),
    )


def _query_qdrant(client, collection_name: str, vector: list[float], limit: int):
    if hasattr(client, "query_points"):
        response = client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit,
            with_payload=True,
        )
        return getattr(response, "points", response)
    return client.search(
        collection_name=collection_name,
        query_vector=vector,
        limit=limit,
        with_payload=True,
    )


def search_dense_by_collection_name(
    query: str,
    collection_name: str,
    top_k: int = 10,
    candidate_k: int | None = None,
    model_name: str | None = None,
) -> DenseSearchResponse:
    normalized_query, resolved_candidate_k = _validate_dense_search_request(
        query,
        top_k,
        candidate_k,
    )
    started = perf_counter()
    embedding_started = perf_counter()
    query_vector = embed_text(normalized_query, model_name=model_name)
    embedding_latency_ms = round((perf_counter() - embedding_started) * 1000, 2)

    client = get_qdrant_client()
    qdrant_started = perf_counter()
    points = list(_query_qdrant(client, collection_name, query_vector, resolved_candidate_k) or [])
    qdrant_latency_ms = round((perf_counter() - qdrant_started) * 1000, 2)
    results = [
        _result_from_point(rank, point)
        for rank, point in enumerate(points[:top_k], start=1)
    ]
    return DenseSearchResponse(
        query=normalized_query,
        index_version_id=None,
        collection_name=collection_name,
        top_k=top_k,
        total_hits=len(points),
        query_embedding_dimension=len(query_vector),
        results=results,
        latency_ms=round((perf_counter() - started) * 1000, 2),
        embedding_latency_ms=embedding_latency_ms,
        qdrant_latency_ms=qdrant_latency_ms,
    )


def search_dense(
    db: Session,
    query: str,
    index_version_id: UUID | str | None = None,
    top_k: int = 10,
    candidate_k: int | None = None,
) -> DenseSearchResponse:
    _validate_dense_search_request(query, top_k, candidate_k)
    if index_version_id is not None:
        index_version = db.get(IndexVersion, UUID(str(index_version_id)))
        if index_version is None:
            raise DenseRetrievalError(f"Index version not found: {index_version_id}")
    else:
        index_version = db.scalar(
            select(IndexVersion)
            .where(IndexVersion.is_active.is_(True))
            .order_by(IndexVersion.activated_at.desc(), IndexVersion.created_at.desc())
            .limit(1)
        )
        if index_version is None:
            raise NoVectorIndexError("No active index version is available for dense retrieval.")

    if not index_version.vector_collection_name:
        raise NoVectorIndexError("Index version does not have a Qdrant vector collection name.")
    if index_version.vector_count is not None and index_version.vector_count <= 0:
        raise NoVectorIndexError("Index version does not have indexed vectors.")

    settings = get_settings()
    embedding_model = index_version.embedding_model or settings.EMBEDDING_MODEL
    response = search_dense_by_collection_name(
        query=query,
        collection_name=index_version.vector_collection_name,
        top_k=top_k,
        candidate_k=candidate_k,
        model_name=embedding_model,
    )
    return DenseSearchResponse(
        query=response.query,
        index_version_id=str(index_version.id),
        collection_name=response.collection_name,
        top_k=response.top_k,
        total_hits=response.total_hits,
        query_embedding_dimension=response.query_embedding_dimension,
        results=response.results,
        latency_ms=response.latency_ms,
        embedding_latency_ms=response.embedding_latency_ms,
        qdrant_latency_ms=response.qdrant_latency_ms,
    )
