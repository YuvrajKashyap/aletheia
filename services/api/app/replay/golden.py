from __future__ import annotations

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.evaluation.correctness import normalize_id
from app.models.datasets import BenchmarkQuery, Dataset, RelevanceJudgment


DEFAULT_GOLDEN_QUERY_SOURCE = "golden_scifact"


def get_default_golden_query_limit() -> int:
    return 20


def _get_dataset(db: Session, dataset_name: str, dataset_version: str) -> Dataset:
    dataset = db.scalar(
        select(Dataset).where(Dataset.name == dataset_name, Dataset.version == dataset_version)
    )
    if dataset is None:
        raise LookupError(f"Dataset not found: {dataset_name} version {dataset_version}")
    return dataset


def build_saved_query_metadata_from_benchmark_query(
    db: Session,
    benchmark_query: BenchmarkQuery,
    dataset: Dataset,
) -> dict:
    judgments = list(
        db.scalars(
            select(RelevanceJudgment)
            .where(RelevanceJudgment.query_id == benchmark_query.id)
            .order_by(RelevanceJudgment.document_external_id, RelevanceJudgment.document_id)
        ).all()
    )
    relevant_document_ids = [normalize_id(judgment.document_id) for judgment in judgments]
    relevant_document_external_ids = [
        normalize_id(judgment.document_external_id) for judgment in judgments
    ]
    return {
        "dataset_name": dataset.name,
        "dataset_version": dataset.version,
        "benchmark_query_id": normalize_id(benchmark_query.id),
        "query_external_id": benchmark_query.external_id,
        "relevant_document_ids": [value for value in relevant_document_ids if value],
        "relevant_document_external_ids": [
            value for value in relevant_document_external_ids if value
        ],
        "relevance_count": len(judgments),
        "source": DEFAULT_GOLDEN_QUERY_SOURCE,
    }


def select_scifact_golden_queries(
    db: Session,
    dataset_name: str = "beir/scifact",
    dataset_version: str = "test",
    limit: int = 20,
    offset: int = 0,
) -> list[BenchmarkQuery]:
    if limit <= 0:
        raise ValueError("limit must be greater than 0")
    if offset < 0:
        raise ValueError("offset must be greater than or equal to 0")
    dataset = _get_dataset(db, dataset_name, dataset_version)
    has_qrel = exists().where(RelevanceJudgment.query_id == BenchmarkQuery.id)
    statement = (
        select(BenchmarkQuery)
        .where(BenchmarkQuery.dataset_id == dataset.id, has_qrel)
        .order_by(BenchmarkQuery.external_id, BenchmarkQuery.created_at, BenchmarkQuery.id)
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(statement).all())
