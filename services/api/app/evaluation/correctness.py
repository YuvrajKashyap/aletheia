from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.evaluation.metrics import deduplicate_ranked_ids, evaluate_single_query
from app.models.datasets import BenchmarkQuery, Chunk, Dataset, Document, RelevanceJudgment
from app.models.queries import Query, QueryTrace, RetrievalCandidate


def normalize_id(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _uuid_or_none(value) -> UUID | None:
    normalized = normalize_id(value)
    if not normalized:
        return None
    try:
        return UUID(normalized)
    except ValueError:
        return None


def deduplicate_ranked_document_ids(document_ids: list[str]) -> list[str]:
    return deduplicate_ranked_ids(document_ids)


def candidate_rows_to_ranked_document_ids(candidates) -> list[str]:
    indexed = list(enumerate(candidates))
    ordered = sorted(
        indexed,
        key=lambda item: (
            getattr(item[1], "final_rank", None) is None,
            getattr(item[1], "final_rank", None) or item[0],
            item[0],
        ),
    )
    return deduplicate_ranked_document_ids(
        [normalize_id(getattr(candidate, "document_id", None)) for _, candidate in ordered]
    )


def chunk_ids_to_ranked_document_ids(db: Session, chunk_ids: list[str]) -> list[str]:
    normalized_ids = [normalize_id(value) for value in chunk_ids]
    chunk_uuid_ids = [parsed for value in normalized_ids if (parsed := _uuid_or_none(value))]
    if not chunk_uuid_ids:
        return []

    chunks = db.scalars(select(Chunk).where(Chunk.id.in_(chunk_uuid_ids))).all()
    document_by_chunk_id = {str(chunk.id): normalize_id(chunk.document_id) for chunk in chunks}
    return deduplicate_ranked_document_ids(
        [document_by_chunk_id.get(chunk_id, "") for chunk_id in normalized_ids]
    )


def search_results_to_ranked_document_ids(results) -> list[str]:
    document_ids = []
    for result in results:
        if isinstance(result, dict):
            document_ids.append(normalize_id(result.get("document_id")))
        else:
            document_ids.append(normalize_id(getattr(result, "document_id", None)))
    return deduplicate_ranked_document_ids(document_ids)


def _get_dataset_by_name_version(
    db: Session,
    dataset_name: str,
    dataset_version: str,
) -> Dataset | None:
    return db.scalar(
        select(Dataset).where(Dataset.name == dataset_name, Dataset.version == dataset_version)
    )


def load_relevance_for_benchmark_query(db: Session, benchmark_query_id) -> dict:
    query_uuid = _uuid_or_none(benchmark_query_id)
    if query_uuid is None:
        raise ValueError(f"Invalid benchmark query id: {benchmark_query_id}")

    benchmark_query = db.get(BenchmarkQuery, query_uuid)
    if benchmark_query is None:
        raise LookupError(f"Benchmark query not found: {benchmark_query_id}")

    judgments = db.scalars(
        select(RelevanceJudgment)
        .where(RelevanceJudgment.query_id == benchmark_query.id)
        .order_by(RelevanceJudgment.document_external_id, RelevanceJudgment.document_id)
    ).all()
    relevant_document_ids = [normalize_id(judgment.document_id) for judgment in judgments]
    relevance_by_id = {
        normalize_id(judgment.document_id): float(judgment.relevance_score)
        for judgment in judgments
        if normalize_id(judgment.document_id)
    }
    return {
        "benchmark_query_id": normalize_id(benchmark_query.id),
        "query_external_id": benchmark_query.external_id,
        "query_text": benchmark_query.text,
        "relevant_document_ids": deduplicate_ranked_document_ids(relevant_document_ids),
        "relevance_by_id": relevance_by_id,
    }


def load_relevance_by_query_external_id(
    db: Session,
    dataset_name: str,
    dataset_version: str,
    query_external_id: str,
) -> dict:
    dataset = _get_dataset_by_name_version(db, dataset_name, dataset_version)
    if dataset is None:
        raise LookupError(f"Dataset not found: {dataset_name} version {dataset_version}")

    benchmark_query = db.scalar(
        select(BenchmarkQuery).where(
            BenchmarkQuery.dataset_id == dataset.id,
            BenchmarkQuery.external_id == query_external_id,
        )
    )
    if benchmark_query is None:
        raise LookupError(f"Benchmark query not found for external_id: {query_external_id}")
    return load_relevance_for_benchmark_query(db, benchmark_query.id)


def find_benchmark_query_by_exact_text(
    db: Session,
    dataset_name: str,
    dataset_version: str,
    query_text: str,
):
    dataset = _get_dataset_by_name_version(db, dataset_name, dataset_version)
    if dataset is None:
        return None
    return db.scalar(
        select(BenchmarkQuery).where(
            BenchmarkQuery.dataset_id == dataset.id,
            BenchmarkQuery.text == query_text.strip(),
        )
    )


def evaluate_ranked_documents_for_query(
    ranked_document_ids: list[str],
    relevance_payload: dict,
    latency_ms: float | None = None,
) -> dict:
    ranked = deduplicate_ranked_document_ids(ranked_document_ids)
    relevant = deduplicate_ranked_document_ids(relevance_payload.get("relevant_document_ids") or [])
    relevant_set = set(relevant)
    metrics = evaluate_single_query(
        retrieved_document_ids=ranked,
        relevant_document_ids=relevant,
        relevance_by_id=relevance_payload.get("relevance_by_id"),
    )
    matched = [document_id for document_id in ranked if document_id in relevant_set]
    matched_set = set(matched)
    missed = [document_id for document_id in relevant if document_id not in matched_set]
    return {
        **metrics,
        "mrr_at_10": metrics["reciprocal_rank_at_10"],
        "latency_ms": latency_ms,
        "ranked_document_ids": ranked,
        "relevant_document_ids": relevant,
        "matched_relevant_document_ids": matched,
        "missed_relevant_document_ids": missed,
    }


def evaluate_trace_against_benchmark_query(
    db: Session,
    trace_id,
    benchmark_query_id=None,
    query_external_id: str | None = None,
    dataset_name: str = "beir/scifact",
    dataset_version: str = "test",
) -> dict:
    trace_uuid = _uuid_or_none(trace_id)
    if trace_uuid is None:
        raise ValueError(f"Invalid trace id: {trace_id}")

    trace = db.get(QueryTrace, trace_uuid)
    if trace is None:
        raise LookupError(f"Query trace not found: {trace_id}")

    query = db.get(Query, trace.query_id)
    if query is None:
        raise LookupError(f"Query not found for trace: {trace_id}")

    candidates = db.scalars(
        select(RetrievalCandidate).where(RetrievalCandidate.trace_id == trace.id)
    ).all()
    ranked_document_ids = candidate_rows_to_ranked_document_ids(candidates)

    if benchmark_query_id is not None:
        relevance_payload = load_relevance_for_benchmark_query(db, benchmark_query_id)
    elif query_external_id:
        relevance_payload = load_relevance_by_query_external_id(
            db,
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            query_external_id=query_external_id,
        )
    else:
        benchmark_query = find_benchmark_query_by_exact_text(
            db,
            dataset_name=dataset_name,
            dataset_version=dataset_version,
            query_text=query.text,
        )
        if benchmark_query is None:
            raise LookupError(
                "Could not resolve benchmark query by exact text; provide query_external_id "
                "or benchmark_query_id."
            )
        relevance_payload = load_relevance_for_benchmark_query(db, benchmark_query.id)

    metrics = evaluate_ranked_documents_for_query(
        ranked_document_ids=ranked_document_ids,
        relevance_payload=relevance_payload,
        latency_ms=query.total_latency_ms,
    )
    metric_fields = {
        key: value
        for key, value in metrics.items()
        if key
        not in {
            "ranked_document_ids",
            "relevant_document_ids",
            "matched_relevant_document_ids",
            "missed_relevant_document_ids",
        }
    }
    return {
        "trace_id": normalize_id(trace.id),
        "query_id": normalize_id(query.id),
        "query_text": query.text,
        "retrieval_mode": query.retrieval_mode,
        "benchmark_query_id": relevance_payload["benchmark_query_id"],
        "query_external_id": relevance_payload["query_external_id"],
        "metrics": metric_fields,
        "ranked_document_ids": metrics["ranked_document_ids"],
        "relevant_document_ids": metrics["relevant_document_ids"],
        "matched_relevant_document_ids": metrics["matched_relevant_document_ids"],
        "missed_relevant_document_ids": metrics["missed_relevant_document_ids"],
    }


def _count(db: Session, statement) -> int:
    return int(db.scalar(statement) or 0)


def validate_dataset_qrels_alignment(
    db: Session,
    dataset_name: str = "beir/scifact",
    dataset_version: str = "test",
) -> dict:
    dataset = _get_dataset_by_name_version(db, dataset_name, dataset_version)
    if dataset is None:
        raise LookupError(f"Dataset not found: {dataset_name} version {dataset_version}")

    document_count = _count(db, select(func.count()).select_from(Document).where(Document.dataset_id == dataset.id))
    benchmark_query_count = _count(
        db,
        select(func.count()).select_from(BenchmarkQuery).where(BenchmarkQuery.dataset_id == dataset.id),
    )
    relevance_judgment_count = _count(
        db,
        select(func.count())
        .select_from(RelevanceJudgment)
        .where(RelevanceJudgment.dataset_id == dataset.id),
    )
    qrel_query_count = _count(
        db,
        select(func.count(func.distinct(RelevanceJudgment.query_id))).where(
            RelevanceJudgment.dataset_id == dataset.id
        ),
    )
    qrel_document_count = _count(
        db,
        select(func.count(func.distinct(RelevanceJudgment.document_id))).where(
            RelevanceJudgment.dataset_id == dataset.id
        ),
    )
    qrels_missing_query_count = 0
    qrels_missing_document_count = 0
    ready = (
        document_count > 0
        and benchmark_query_count > 0
        and relevance_judgment_count > 0
        and qrels_missing_query_count == 0
        and qrels_missing_document_count == 0
    )
    return {
        "dataset_id": normalize_id(dataset.id),
        "dataset_name": dataset.name,
        "dataset_version": dataset.version,
        "document_count": document_count,
        "benchmark_query_count": benchmark_query_count,
        "relevance_judgment_count": relevance_judgment_count,
        "qrel_query_count": qrel_query_count,
        "qrel_document_count": qrel_document_count,
        "qrels_missing_query_count": qrels_missing_query_count,
        "qrels_missing_document_count": qrels_missing_document_count,
        "ready_for_evaluation": ready,
    }
