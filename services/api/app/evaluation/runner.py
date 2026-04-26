from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.evaluation.correctness import (
    evaluate_ranked_documents_for_query,
    load_relevance_for_benchmark_query,
    normalize_id,
    search_results_to_ranked_document_ids,
)
from app.evaluation.latency import summarize_latencies
from app.evaluation.metrics import aggregate_query_metrics
from app.evaluation.reporting import write_evaluation_report
from app.indexing.service import get_active_index_version
from app.models.datasets import BenchmarkQuery, Dataset
from app.models.evaluation import EvaluationQueryResult, EvaluationReport, EvaluationRun
from app.models.indexing import IndexVersion
from app.schemas.search import SearchRequest
from app.search.service import run_search


SUPPORTED_RETRIEVAL_MODES = {"bm25", "dense", "hybrid", "hybrid_rerank"}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _validate_inputs(
    retrieval_mode: str,
    query_limit: int | None,
    query_offset: int,
    top_k: int,
    rrf_k: int,
) -> None:
    if retrieval_mode not in SUPPORTED_RETRIEVAL_MODES:
        raise ValueError(f"Unsupported retrieval mode: {retrieval_mode}")
    if query_limit is not None and query_limit <= 0:
        raise ValueError("query_limit must be greater than 0 when provided")
    if query_offset < 0:
        raise ValueError("query_offset must be greater than or equal to 0")
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")
    if rrf_k <= 0:
        raise ValueError("rrf_k must be greater than 0")


def _get_dataset(db: Session, dataset_name: str, dataset_version: str) -> Dataset:
    dataset = db.scalar(
        select(Dataset).where(Dataset.name == dataset_name, Dataset.version == dataset_version)
    )
    if dataset is None:
        raise LookupError(f"Dataset not found: {dataset_name} version {dataset_version}")
    return dataset


def _resolve_index_version(
    db: Session,
    dataset_id: UUID,
    index_version_id: str | None,
) -> IndexVersion:
    if index_version_id:
        index_version = db.get(IndexVersion, UUID(str(index_version_id)))
        if index_version is None:
            raise LookupError(f"Index version not found: {index_version_id}")
        if index_version.dataset_id != dataset_id:
            raise ValueError("Index version does not belong to the selected dataset")
        return index_version

    index_version = get_active_index_version(db, dataset_id)
    if index_version is None:
        raise LookupError("No active index version found for selected dataset")
    return index_version


def _load_benchmark_queries(
    db: Session,
    dataset_id: UUID,
    query_limit: int | None,
    query_offset: int,
) -> list[BenchmarkQuery]:
    statement = (
        select(BenchmarkQuery)
        .where(BenchmarkQuery.dataset_id == dataset_id)
        .order_by(BenchmarkQuery.external_id, BenchmarkQuery.created_at, BenchmarkQuery.id)
        .offset(query_offset)
    )
    if query_limit is not None:
        statement = statement.limit(query_limit)
    return list(db.scalars(statement).all())


def _evaluation_config(
    retrieval_mode: str,
    dataset_name: str,
    dataset_version: str,
    index_version_id: str | None,
    query_limit: int | None,
    query_offset: int,
    top_k: int,
    candidate_k: int | None,
    bm25_candidate_k: int | None,
    dense_candidate_k: int | None,
    hybrid_candidate_k: int | None,
    rerank_top_n: int | None,
    rrf_k: int,
) -> dict[str, Any]:
    return {
        "retrieval_mode": retrieval_mode,
        "dataset_name": dataset_name,
        "dataset_version": dataset_version,
        "index_version_id": index_version_id,
        "query_limit": query_limit,
        "query_offset": query_offset,
        "top_k": top_k,
        "candidate_k": candidate_k,
        "bm25_candidate_k": bm25_candidate_k,
        "dense_candidate_k": dense_candidate_k,
        "hybrid_candidate_k": hybrid_candidate_k,
        "rerank_top_n": rerank_top_n,
        "rrf_k": rrf_k,
    }


def _build_search_request(
    benchmark_query: BenchmarkQuery,
    retrieval_mode: str,
    index_version_id: UUID,
    top_k: int,
    candidate_k: int | None,
    bm25_candidate_k: int | None,
    dense_candidate_k: int | None,
    hybrid_candidate_k: int | None,
    rerank_top_n: int | None,
    rrf_k: int,
) -> SearchRequest:
    return SearchRequest(
        query=benchmark_query.text,
        retrieval_mode=retrieval_mode,
        top_k=top_k,
        candidate_k=candidate_k,
        bm25_candidate_k=bm25_candidate_k,
        dense_candidate_k=dense_candidate_k,
        hybrid_candidate_k=hybrid_candidate_k,
        rerank_top_n=rerank_top_n,
        rrf_k=rrf_k,
        index_version_id=index_version_id,
    )


def _metric_fields(metrics: dict) -> dict[str, float | int | None]:
    return {
        "recall_at_5": metrics.get("recall_at_5"),
        "recall_at_10": metrics.get("recall_at_10"),
        "mrr_at_10": metrics.get("mrr_at_10"),
        "ndcg_at_10": metrics.get("ndcg_at_10"),
        "latency_ms": metrics.get("latency_ms"),
    }


def _query_report_item(
    benchmark_query: BenchmarkQuery,
    trace_id: str | None,
    metrics: dict | None,
    error_message: str | None = None,
) -> dict:
    return {
        "benchmark_query_id": normalize_id(benchmark_query.id),
        "query_external_id": benchmark_query.external_id,
        "query_text": benchmark_query.text,
        "trace_id": trace_id,
        "retrieved_document_ids": (metrics or {}).get("ranked_document_ids", []),
        "relevant_document_ids": (metrics or {}).get("relevant_document_ids", []),
        "metrics": _metric_fields(metrics or {}),
        "error_message": error_message,
    }


def _create_query_result(
    evaluation_run_id: UUID,
    benchmark_query: BenchmarkQuery,
    metrics: dict | None,
    trace_id: str | None,
    error_message: str | None = None,
) -> EvaluationQueryResult:
    return EvaluationQueryResult(
        evaluation_run_id=evaluation_run_id,
        benchmark_query_id=benchmark_query.id,
        query_external_id=benchmark_query.external_id,
        query_text=benchmark_query.text,
        relevant_document_ids_json=(metrics or {}).get("relevant_document_ids", []),
        retrieved_document_ids_json=(metrics or {}).get("ranked_document_ids", []),
        recall_at_5=(metrics or {}).get("recall_at_5"),
        recall_at_10=(metrics or {}).get("recall_at_10"),
        mrr_at_10=(metrics or {}).get("mrr_at_10"),
        ndcg_at_10=(metrics or {}).get("ndcg_at_10"),
        latency_ms=(metrics or {}).get("latency_ms"),
        trace_id=UUID(str(trace_id)) if trace_id else None,
        error_message=error_message,
    )


def _summary(
    evaluation_run: EvaluationRun,
    dataset: Dataset,
    retrieval_mode: str,
    aggregate_metrics: dict,
    latency_summary: dict,
) -> dict:
    return {
        "evaluation_run_id": normalize_id(evaluation_run.id),
        "name": evaluation_run.name,
        "retrieval_mode": retrieval_mode,
        "dataset_name": dataset.name,
        "dataset_version": dataset.version,
        "status": evaluation_run.status,
        "query_count": evaluation_run.query_count,
        "failed_query_count": evaluation_run.failed_query_count,
        "aggregate_metrics": aggregate_metrics,
        "latency_summary": latency_summary,
        "report_path": evaluation_run.report_path,
    }


def run_offline_evaluation(
    db: Session,
    name: str,
    retrieval_mode: str,
    dataset_name: str = "beir/scifact",
    dataset_version: str = "test",
    index_version_id: str | None = None,
    query_limit: int | None = None,
    query_offset: int = 0,
    top_k: int = 10,
    candidate_k: int | None = None,
    bm25_candidate_k: int | None = None,
    dense_candidate_k: int | None = None,
    hybrid_candidate_k: int | None = None,
    rerank_top_n: int | None = None,
    rrf_k: int = 60,
    notes: str | None = None,
) -> dict:
    _validate_inputs(retrieval_mode, query_limit, query_offset, top_k, rrf_k)
    dataset = _get_dataset(db, dataset_name, dataset_version)
    index_version = _resolve_index_version(db, dataset.id, index_version_id)
    config = _evaluation_config(
        retrieval_mode,
        dataset_name,
        dataset_version,
        normalize_id(index_version.id),
        query_limit,
        query_offset,
        top_k,
        candidate_k,
        bm25_candidate_k,
        dense_candidate_k,
        hybrid_candidate_k,
        rerank_top_n,
        rrf_k,
    )
    evaluation_run = EvaluationRun(
        name=name,
        dataset_id=dataset.id,
        index_version_id=index_version.id,
        status="running",
        started_at=utc_now(),
        query_count=0,
        failed_query_count=0,
        config_json=config,
        notes=notes,
    )
    db.add(evaluation_run)
    db.flush()

    query_results: list[dict] = []
    successful_metrics: list[dict] = []
    latencies: list[float] = []
    selected_queries = _load_benchmark_queries(db, dataset.id, query_limit, query_offset)

    try:
        for benchmark_query in selected_queries:
            trace_id = None
            try:
                request = _build_search_request(
                    benchmark_query,
                    retrieval_mode,
                    index_version.id,
                    top_k,
                    candidate_k,
                    bm25_candidate_k,
                    dense_candidate_k,
                    hybrid_candidate_k,
                    rerank_top_n,
                    rrf_k,
                )
                response = run_search(
                    db,
                    request,
                    request_id=f"eval:{evaluation_run.id}:{benchmark_query.external_id}",
                )
                trace_id = normalize_id(response.trace_id)
                ranked_document_ids = search_results_to_ranked_document_ids(response.results)
                relevance_payload = load_relevance_for_benchmark_query(db, benchmark_query.id)
                metrics = evaluate_ranked_documents_for_query(
                    ranked_document_ids,
                    relevance_payload,
                    latency_ms=response.latency_ms,
                )
                db.add(
                    _create_query_result(
                        evaluation_run.id,
                        benchmark_query,
                        metrics,
                        trace_id,
                    )
                )
                successful_metrics.append(metrics)
                if metrics.get("latency_ms") is not None:
                    latencies.append(float(metrics["latency_ms"]))
                query_results.append(_query_report_item(benchmark_query, trace_id, metrics))
            except Exception as exc:
                evaluation_run.failed_query_count += 1
                error_message = str(exc)
                db.add(
                    _create_query_result(
                        evaluation_run.id,
                        benchmark_query,
                        None,
                        trace_id,
                        error_message=error_message,
                    )
                )
                query_results.append(
                    _query_report_item(
                        benchmark_query,
                        trace_id,
                        None,
                        error_message=error_message,
                    )
                )
            finally:
                db.flush()

        aggregate_metrics = aggregate_query_metrics(successful_metrics)
        latency_summary = summarize_latencies(latencies)
        evaluation_run.status = "completed"
        evaluation_run.completed_at = utc_now()
        evaluation_run.query_count = len(selected_queries)
        evaluation_run.recall_at_5 = aggregate_metrics["recall_at_5"]
        evaluation_run.recall_at_10 = aggregate_metrics["recall_at_10"]
        evaluation_run.mrr_at_10 = aggregate_metrics["mrr_at_10"]
        evaluation_run.ndcg_at_10 = aggregate_metrics["ndcg_at_10"]
        evaluation_run.avg_latency_ms = latency_summary["avg_latency_ms"]
        evaluation_run.p50_latency_ms = latency_summary["p50_latency_ms"]
        evaluation_run.p95_latency_ms = latency_summary["p95_latency_ms"]

        report = {
            "evaluation_run_id": normalize_id(evaluation_run.id),
            "name": evaluation_run.name,
            "dataset": {
                "id": normalize_id(dataset.id),
                "name": dataset.name,
                "version": dataset.version,
            },
            "retrieval_mode": retrieval_mode,
            "index_version_id": normalize_id(index_version.id),
            "config": config,
            "aggregate_metrics": {
                **aggregate_metrics,
                "query_count": len(selected_queries),
                "failed_query_count": evaluation_run.failed_query_count,
            },
            "latency_summary": latency_summary,
            "query_results": query_results,
        }
        report_path = write_evaluation_report(report, normalize_id(evaluation_run.id))
        evaluation_run.report_path = report_path
        db.add(
            EvaluationReport(
                evaluation_run_id=evaluation_run.id,
                report_format="json",
                report_path=report_path,
                summary_json={
                    "aggregate_metrics": report["aggregate_metrics"],
                    "latency_summary": latency_summary,
                },
            )
        )
        db.commit()
        db.refresh(evaluation_run)
        return _summary(evaluation_run, dataset, retrieval_mode, aggregate_metrics, latency_summary)
    except Exception:
        evaluation_run.status = "failed"
        evaluation_run.completed_at = utc_now()
        db.commit()
        raise
