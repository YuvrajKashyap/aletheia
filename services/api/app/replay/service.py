from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.evaluation.correctness import (
    evaluate_ranked_documents_for_query,
    load_relevance_for_benchmark_query,
    load_relevance_by_query_external_id,
    normalize_id,
)
from app.evaluation.latency import summarize_latencies
from app.evaluation.metrics import aggregate_query_metrics
from app.experiments.service import (
    experiment_config_to_evaluation_params,
    get_experiment_config,
    get_experiment_config_by_name,
)
from app.models.queries import QueryReplay, QueryTrace, SavedQuery
from app.replay.comparison import build_replay_comparison_json, extract_ranked_document_ids_from_search_response
from app.replay.golden import (
    DEFAULT_GOLDEN_QUERY_SOURCE,
    build_saved_query_metadata_from_benchmark_query,
    select_scifact_golden_queries,
)
from app.replay.reporting import write_replay_report
from app.schemas.search import SearchRequest
from app.search.service import run_search


SUPPORTED_RETRIEVAL_MODES = {"bm25", "dense", "hybrid", "hybrid_rerank"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid_or_none(value) -> UUID | None:
    normalized = normalize_id(value)
    if not normalized:
        return None
    return UUID(normalized)


def _validate_text(text: str) -> str:
    normalized = (text or "").strip()
    if not normalized:
        raise ValueError("Saved query text is required")
    return normalized


def create_saved_query(
    db: Session,
    text: str,
    name: str | None = None,
    source: str = "manual",
    dataset_id: str | None = None,
    metadata_json: dict | None = None,
) -> SavedQuery:
    saved_query = SavedQuery(
        text=_validate_text(text),
        name=(name or "").strip() or None,
        source=(source or "manual").strip() or "manual",
        dataset_id=_uuid_or_none(dataset_id),
        metadata_json=metadata_json or {},
    )
    db.add(saved_query)
    db.commit()
    db.refresh(saved_query)
    return saved_query


def get_saved_query(db: Session, saved_query_id) -> SavedQuery | None:
    return db.get(SavedQuery, UUID(str(saved_query_id)))


def list_saved_queries(
    db: Session,
    source: str | None = None,
    dataset_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    statement = select(SavedQuery)
    count_statement = select(func.count()).select_from(SavedQuery)
    filters = []
    if source:
        filters.append(SavedQuery.source == source)
    if dataset_id:
        filters.append(SavedQuery.dataset_id == UUID(str(dataset_id)))
    if filters:
        statement = statement.where(*filters)
        count_statement = count_statement.where(*filters)
    total = int(db.scalar(count_statement) or 0)
    items = list(
        db.scalars(
            statement.order_by(SavedQuery.created_at.desc(), SavedQuery.id.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return {"total": total, "limit": limit, "offset": offset, "items": items}


def delete_saved_query(db: Session, saved_query_id) -> None:
    saved_query = get_saved_query(db, saved_query_id)
    if saved_query is None:
        raise LookupError(f"Saved query not found: {saved_query_id}")
    replay_count = int(
        db.scalar(
            select(func.count())
            .select_from(QueryReplay)
            .where(QueryReplay.saved_query_id == saved_query.id)
        )
        or 0
    )
    if replay_count > 0:
        raise ValueError("Saved query is used by query replays and cannot be deleted")
    db.delete(saved_query)
    db.commit()


def _existing_golden_query(db: Session, dataset_id, query_external_id: str) -> SavedQuery | None:
    return db.scalar(
        select(SavedQuery).where(
            SavedQuery.dataset_id == dataset_id,
            SavedQuery.source == DEFAULT_GOLDEN_QUERY_SOURCE,
            SavedQuery.metadata_json["query_external_id"].astext == query_external_id,
        )
    )


def seed_golden_queries_from_scifact(
    db: Session,
    dataset_name: str = "beir/scifact",
    dataset_version: str = "test",
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    selected = select_scifact_golden_queries(
        db,
        dataset_name=dataset_name,
        dataset_version=dataset_version,
        limit=limit,
        offset=offset,
    )
    created = 0
    existing = 0
    items: list[SavedQuery] = []
    for benchmark_query in selected:
        dataset = benchmark_query.dataset
        current = _existing_golden_query(db, benchmark_query.dataset_id, benchmark_query.external_id)
        if current is not None:
            existing += 1
            items.append(current)
            continue
        metadata = build_saved_query_metadata_from_benchmark_query(db, benchmark_query, dataset)
        saved_query = SavedQuery(
            dataset_id=benchmark_query.dataset_id,
            name=f"SciFact {benchmark_query.external_id}",
            text=benchmark_query.text,
            source=DEFAULT_GOLDEN_QUERY_SOURCE,
            metadata_json=metadata,
        )
        db.add(saved_query)
        db.flush()
        created += 1
        items.append(saved_query)
    db.commit()
    for item in items:
        db.refresh(item)
    return {
        "created_count": created,
        "existing_count": existing,
        "total_selected": len(selected),
        "items": items,
    }


def _resolve_experiment_config(db: Session, config_id: str | None, config_name: str | None):
    if config_id:
        config = get_experiment_config(db, config_id)
        if config is None:
            raise LookupError(f"Experiment config not found: {config_id}")
        return config
    if config_name:
        config = get_experiment_config_by_name(db, config_name)
        if config is None:
            raise LookupError(f"Experiment config not found: {config_name}")
        return config
    return None


def _resolve_replay_params(
    db: Session,
    retrieval_mode: str | None,
    experiment_config_id: str | None,
    experiment_config_name: str | None,
    top_k: int,
    candidate_k: int | None,
    bm25_candidate_k: int | None,
    dense_candidate_k: int | None,
    hybrid_candidate_k: int | None,
    rerank_top_n: int | None,
    rrf_k: int,
) -> tuple[str, dict[str, Any], Any | None]:
    config = _resolve_experiment_config(db, experiment_config_id, experiment_config_name)
    if config is not None:
        params = experiment_config_to_evaluation_params(config)
        return params["retrieval_mode"], params, config
    if retrieval_mode not in SUPPORTED_RETRIEVAL_MODES:
        raise ValueError("retrieval_mode must be bm25, dense, hybrid, or hybrid_rerank")
    return retrieval_mode, {
        "top_k": top_k,
        "candidate_k": candidate_k,
        "bm25_candidate_k": bm25_candidate_k,
        "dense_candidate_k": dense_candidate_k,
        "hybrid_candidate_k": hybrid_candidate_k,
        "rerank_top_n": rerank_top_n,
        "rrf_k": rrf_k,
    }, None


def _metrics_from_saved_query(db: Session, saved_query: SavedQuery, ranked_document_ids: list[str], latency_ms):
    metadata = saved_query.metadata_json or {}
    try:
        if metadata.get("benchmark_query_id"):
            relevance = load_relevance_for_benchmark_query(db, metadata["benchmark_query_id"])
        elif metadata.get("query_external_id") and metadata.get("dataset_name") and metadata.get("dataset_version"):
            relevance = load_relevance_by_query_external_id(
                db,
                metadata["dataset_name"],
                metadata["dataset_version"],
                metadata["query_external_id"],
            )
        else:
            return None
        return evaluate_ranked_documents_for_query(ranked_document_ids, relevance, latency_ms=latency_ms)
    except Exception:
        return None


def _create_replay_row(
    saved_query: SavedQuery | None,
    status: str,
    comparison_json: dict,
    source_trace_id: str | None = None,
    target_trace_id: str | None = None,
    experiment_config_id: str | None = None,
    index_version_id: str | None = None,
    error_message: str | None = None,
    started_at=None,
    completed_at=None,
) -> QueryReplay:
    original_query_id = None
    if source_trace_id and comparison_json.get("source_query_id"):
        original_query_id = _uuid_or_none(comparison_json["source_query_id"])
    return QueryReplay(
        saved_query_id=saved_query.id if saved_query else None,
        original_query_id=original_query_id,
        source_trace_id=_uuid_or_none(source_trace_id),
        target_trace_id=_uuid_or_none(target_trace_id),
        experiment_config_id=_uuid_or_none(experiment_config_id),
        index_version_id=_uuid_or_none(index_version_id),
        status=status,
        comparison_json=comparison_json,
        error_message=error_message,
        started_at=started_at,
        completed_at=completed_at,
    )


def run_saved_query_replay(
    db: Session,
    saved_query_id: str,
    retrieval_mode: str | None = None,
    experiment_config_id: str | None = None,
    experiment_config_name: str | None = None,
    index_version_id: str | None = None,
    source_trace_id: str | None = None,
    top_k: int = 10,
    candidate_k: int | None = None,
    bm25_candidate_k: int | None = None,
    dense_candidate_k: int | None = None,
    hybrid_candidate_k: int | None = None,
    rerank_top_n: int | None = None,
    rrf_k: int = 60,
    started_by: str = "manual",
) -> dict[str, Any]:
    saved_query = get_saved_query(db, saved_query_id)
    if saved_query is None:
        raise LookupError(f"Saved query not found: {saved_query_id}")
    started_at = utc_now()
    try:
        resolved_mode, params, config = _resolve_replay_params(
            db,
            retrieval_mode,
            experiment_config_id,
            experiment_config_name,
            top_k,
            candidate_k,
            bm25_candidate_k,
            dense_candidate_k,
            hybrid_candidate_k,
            rerank_top_n,
            rrf_k,
        )
        request = SearchRequest(
            query=saved_query.text,
            retrieval_mode=resolved_mode,
            top_k=params["top_k"],
            candidate_k=params.get("candidate_k"),
            bm25_candidate_k=params.get("bm25_candidate_k"),
            dense_candidate_k=params.get("dense_candidate_k"),
            hybrid_candidate_k=params.get("hybrid_candidate_k"),
            rerank_top_n=params.get("rerank_top_n"),
            rrf_k=params.get("rrf_k", rrf_k),
            index_version_id=_uuid_or_none(index_version_id),
        )
        response = run_search(db, request, request_id=f"replay:{saved_query.id}")
        ranked_document_ids = extract_ranked_document_ids_from_search_response(response)
        metrics = _metrics_from_saved_query(db, saved_query, ranked_document_ids, response.latency_ms)
        source_trace = db.get(QueryTrace, _uuid_or_none(source_trace_id)) if source_trace_id else None
        comparison_json = build_replay_comparison_json(
            saved_query,
            response,
            resolved_mode,
            experiment_config=config,
            source_trace=source_trace,
            metrics=metrics,
            top_k=request.top_k,
        )
        if source_trace is not None:
            comparison_json["source_query_id"] = normalize_id(source_trace.query_id)
        comparison_json["started_by"] = started_by
        replay = _create_replay_row(
            saved_query,
            "completed",
            comparison_json,
            source_trace_id=source_trace_id,
            target_trace_id=normalize_id(response.trace_id),
            experiment_config_id=normalize_id(getattr(config, "id", None)),
            index_version_id=normalize_id(response.index_version_id),
            started_at=started_at,
            completed_at=utc_now(),
        )
        db.add(replay)
        db.commit()
        db.refresh(replay)
        return {
            "query_replay_id": normalize_id(replay.id),
            "saved_query_id": normalize_id(saved_query.id),
            "retrieval_mode": resolved_mode,
            "experiment_config_id": normalize_id(getattr(config, "id", None)),
            "target_trace_id": normalize_id(response.trace_id),
            "target_query_id": normalize_id(response.query_id),
            "metrics": metrics,
            "status": replay.status,
        }
    except Exception as exc:
        comparison_json = {
            "saved_query_id": normalize_id(saved_query.id),
            "query_text": saved_query.text,
            "retrieval_mode": retrieval_mode,
            "errors": [str(exc)],
            "warnings": [],
        }
        replay = _create_replay_row(
            saved_query,
            "failed",
            comparison_json,
            source_trace_id=source_trace_id,
            experiment_config_id=experiment_config_id,
            index_version_id=index_version_id,
            error_message=str(exc),
            started_at=started_at,
            completed_at=utc_now(),
        )
        db.add(replay)
        db.commit()
        db.refresh(replay)
        return {
            "query_replay_id": normalize_id(replay.id),
            "saved_query_id": normalize_id(saved_query.id),
            "retrieval_mode": retrieval_mode,
            "experiment_config_id": experiment_config_id,
            "target_trace_id": None,
            "target_query_id": None,
            "metrics": None,
            "status": "failed",
            "error_message": str(exc),
        }


def get_query_replay(db: Session, query_replay_id) -> QueryReplay | None:
    return db.get(QueryReplay, UUID(str(query_replay_id)))


def list_query_replays(
    db: Session,
    saved_query_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    statement = select(QueryReplay)
    count_statement = select(func.count()).select_from(QueryReplay)
    filters = []
    if saved_query_id:
        filters.append(QueryReplay.saved_query_id == UUID(str(saved_query_id)))
    if status:
        filters.append(QueryReplay.status == status)
    if filters:
        statement = statement.where(*filters)
        count_statement = count_statement.where(*filters)
    total = int(db.scalar(count_statement) or 0)
    items = list(
        db.scalars(
            statement.order_by(QueryReplay.created_at.desc(), QueryReplay.id.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return {"total": total, "limit": limit, "offset": offset, "items": items}


def run_golden_query_replay(
    db: Session,
    name: str,
    source: str = DEFAULT_GOLDEN_QUERY_SOURCE,
    retrieval_mode: str | None = None,
    experiment_config_id: str | None = None,
    experiment_config_name: str | None = None,
    limit: int | None = None,
    offset: int = 0,
    top_k: int = 10,
    candidate_k: int | None = None,
    bm25_candidate_k: int | None = None,
    dense_candidate_k: int | None = None,
    hybrid_candidate_k: int | None = None,
    rerank_top_n: int | None = None,
    rrf_k: int = 60,
    notes: str | None = None,
) -> dict[str, Any]:
    if offset < 0:
        raise ValueError("offset must be greater than or equal to 0")
    selected_limit = limit or 50
    saved_queries = list_saved_queries(db, source=source, limit=selected_limit, offset=offset)["items"]
    if not saved_queries:
        raise ValueError(f"No saved queries found for source: {source}")
    replay_summaries = []
    metrics = []
    latencies = []
    failures = 0
    for saved_query in saved_queries:
        summary = run_saved_query_replay(
            db,
            saved_query_id=normalize_id(saved_query.id),
            retrieval_mode=retrieval_mode,
            experiment_config_id=experiment_config_id,
            experiment_config_name=experiment_config_name,
            top_k=top_k,
            candidate_k=candidate_k,
            bm25_candidate_k=bm25_candidate_k,
            dense_candidate_k=dense_candidate_k,
            hybrid_candidate_k=hybrid_candidate_k,
            rerank_top_n=rerank_top_n,
            rrf_k=rrf_k,
            started_by="golden_replay",
        )
        replay_summaries.append(summary)
        if summary.get("status") == "failed":
            failures += 1
            continue
        if summary.get("metrics"):
            metrics.append(summary["metrics"])
            if summary["metrics"].get("latency_ms") is not None:
                latencies.append(float(summary["metrics"]["latency_ms"]))
    aggregate = aggregate_query_metrics(metrics)
    latency_summary = summarize_latencies(latencies)
    report = {
        "name": name,
        "source": source,
        "saved_query_count": len(saved_queries),
        "replay_count": len(replay_summaries),
        "failed_replay_count": failures,
        "aggregate_metrics": aggregate,
        "latency_summary": latency_summary,
        "replays": replay_summaries,
        "notes": notes,
    }
    report_path = write_replay_report(report, name)
    return {
        **report,
        "avg_latency_ms": latency_summary["avg_latency_ms"],
        "report_path": report_path,
        "replay_ids": [item.get("query_replay_id") for item in replay_summaries],
    }
