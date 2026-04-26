from __future__ import annotations

from dataclasses import asdict, dataclass
import os
from typing import Any, Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.datasets import BenchmarkQuery, Dataset, Document, RelevanceJudgment

SCIFACT_SOURCE_URL = "https://ir-datasets.com/beir.html#beir/scifact"


@dataclass(frozen=True)
class SciFactDocumentRecord:
    external_id: str
    title: str | None
    text: str
    source_url: str | None
    metadata_json: dict[str, Any]


@dataclass(frozen=True)
class SciFactQueryRecord:
    external_id: str
    text: str
    split: str
    metadata_json: dict[str, Any]


@dataclass(frozen=True)
class SciFactQrelRecord:
    query_external_id: str
    document_external_id: str
    relevance_score: float
    metadata_json: dict[str, Any]


@dataclass
class SciFactLoadSummary:
    documents_seen: int = 0
    documents_loaded: int = 0
    queries_seen: int = 0
    queries_loaded: int = 0
    qrels_seen: int = 0
    qrels_loaded: int = 0
    qrels_skipped_missing_query: int = 0
    qrels_skipped_missing_document: int = 0
    dataset_id: UUID | None = None
    dry_run: bool = False
    split: str = "test"
    corpus_dataset_id: str = "beir/scifact"
    eval_dataset_id: str = "beir/scifact/test"

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["dataset_id"] = str(self.dataset_id) if self.dataset_id else None
        return result


def _limit_iterable(records: Iterable[Any], limit: int | None) -> Iterable[Any]:
    for index, record in enumerate(records):
        if limit is not None and index >= limit:
            break
        yield record


def _get_record_id(record: Any, *names: str) -> str:
    for name in names:
        value = getattr(record, name, None)
        if value is not None:
            return str(value)
    raise ValueError(f"Record is missing required id field candidates: {names}")


def _get_record_text(record: Any, *names: str) -> str:
    for name in names:
        value = getattr(record, name, None)
        if value:
            return str(value)
    return ""


def _raw_metadata(record: Any, source_dataset_id: str, split: str | None = None) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "source_dataset_id": source_dataset_id,
        "raw_fields": {},
    }
    if split is not None:
        metadata["split"] = split

    for name in getattr(record, "_fields", ()):
        value = getattr(record, name, None)
        if isinstance(value, (str, int, float, bool)) or value is None:
            metadata["raw_fields"][name] = value
        else:
            metadata["raw_fields"][name] = str(value)

    return metadata


def _load_ir_dataset(dataset_id: str):
    settings = get_settings()
    os.environ.setdefault("IR_DATASETS_HOME", settings.IR_DATASETS_HOME)

    import ir_datasets

    return ir_datasets.load(dataset_id)


def get_scifact_dataset_metadata() -> dict[str, str]:
    settings = get_settings()
    return {
        "name": settings.SCIFACT_CORPUS_DATASET_ID,
        "version": settings.SCIFACT_DEFAULT_SPLIT,
        "source": "ir_datasets",
        "source_url": SCIFACT_SOURCE_URL,
        "corpus_dataset_id": settings.SCIFACT_CORPUS_DATASET_ID,
        "eval_dataset_id": settings.SCIFACT_EVAL_DATASET_ID,
    }


def document_from_ir_record(record: Any, corpus_dataset_id: str) -> SciFactDocumentRecord:
    external_id = _get_record_id(record, "doc_id", "docid", "id")
    title = getattr(record, "title", None)
    text = _get_record_text(record, "text", "body", "abstract")
    source_url = getattr(record, "url", None)
    return SciFactDocumentRecord(
        external_id=external_id,
        title=str(title) if title else None,
        text=text,
        source_url=str(source_url) if source_url else None,
        metadata_json=_raw_metadata(record, corpus_dataset_id),
    )


def query_from_ir_record(
    record: Any,
    eval_dataset_id: str,
    split: str,
) -> SciFactQueryRecord:
    return SciFactQueryRecord(
        external_id=_get_record_id(record, "query_id", "query_id", "qid", "id"),
        text=_get_record_text(record, "text", "query", "title"),
        split=split,
        metadata_json=_raw_metadata(record, eval_dataset_id, split),
    )


def qrel_from_ir_record(record: Any, eval_dataset_id: str, split: str) -> SciFactQrelRecord:
    relevance = getattr(record, "relevance", getattr(record, "score", 1.0))
    return SciFactQrelRecord(
        query_external_id=_get_record_id(record, "query_id", "qid"),
        document_external_id=_get_record_id(record, "doc_id", "docid"),
        relevance_score=float(relevance),
        metadata_json=_raw_metadata(record, eval_dataset_id, split),
    )


def iter_scifact_documents(limit: int | None = None) -> Iterable[SciFactDocumentRecord]:
    settings = get_settings()
    dataset = _load_ir_dataset(settings.SCIFACT_CORPUS_DATASET_ID)
    for record in _limit_iterable(dataset.docs_iter(), limit):
        yield document_from_ir_record(record, settings.SCIFACT_CORPUS_DATASET_ID)


def iter_scifact_queries(
    split: str = "test",
    limit: int | None = None,
) -> Iterable[SciFactQueryRecord]:
    settings = get_settings()
    dataset = _load_ir_dataset(settings.SCIFACT_EVAL_DATASET_ID)
    for record in _limit_iterable(dataset.queries_iter(), limit):
        yield query_from_ir_record(record, settings.SCIFACT_EVAL_DATASET_ID, split)


def iter_scifact_qrels(split: str = "test", limit: int | None = None) -> Iterable[SciFactQrelRecord]:
    settings = get_settings()
    dataset = _load_ir_dataset(settings.SCIFACT_EVAL_DATASET_ID)
    for record in _limit_iterable(dataset.qrels_iter(), limit):
        yield qrel_from_ir_record(record, settings.SCIFACT_EVAL_DATASET_ID, split)


def _get_or_create_dataset(db: Session, split: str, dry_run: bool) -> Dataset | None:
    settings = get_settings()
    dataset = db.scalar(
        select(Dataset).where(
            Dataset.name == settings.SCIFACT_CORPUS_DATASET_ID,
            Dataset.version == split,
        )
    )

    if dry_run:
        return dataset

    if dataset is None:
        dataset = Dataset(
            name=settings.SCIFACT_CORPUS_DATASET_ID,
            source="ir_datasets",
            version=split,
            description="BEIR SciFact corpus and benchmark metadata loaded via ir_datasets.",
            source_url=SCIFACT_SOURCE_URL,
            metadata_json=get_scifact_dataset_metadata(),
        )
        db.add(dataset)
    else:
        dataset.source = "ir_datasets"
        dataset.source_url = SCIFACT_SOURCE_URL
        dataset.metadata_json = get_scifact_dataset_metadata()

    db.commit()
    db.refresh(dataset)
    return dataset


def _upsert_document(db: Session, dataset: Dataset, record: SciFactDocumentRecord) -> bool:
    document = db.scalar(
        select(Document).where(
            Document.dataset_id == dataset.id,
            Document.external_id == record.external_id,
        )
    )
    created = document is None
    if document is None:
        document = Document(dataset_id=dataset.id, external_id=record.external_id, text=record.text)
        db.add(document)

    document.title = record.title
    document.text = record.text
    document.source_url = record.source_url
    document.metadata_json = record.metadata_json
    return created


def _upsert_query(db: Session, dataset: Dataset, record: SciFactQueryRecord) -> bool:
    query = db.scalar(
        select(BenchmarkQuery).where(
            BenchmarkQuery.dataset_id == dataset.id,
            BenchmarkQuery.external_id == record.external_id,
        )
    )
    created = query is None
    if query is None:
        query = BenchmarkQuery(
            dataset_id=dataset.id,
            external_id=record.external_id,
            text=record.text,
        )
        db.add(query)

    query.text = record.text
    query.split = record.split
    query.metadata_json = record.metadata_json
    return created


def _upsert_qrel(
    db: Session,
    dataset: Dataset,
    query: BenchmarkQuery,
    document: Document,
    record: SciFactQrelRecord,
) -> bool:
    judgment = db.scalar(
        select(RelevanceJudgment).where(
            RelevanceJudgment.query_id == query.id,
            RelevanceJudgment.document_id == document.id,
        )
    )
    created = judgment is None
    if judgment is None:
        judgment = RelevanceJudgment(
            dataset_id=dataset.id,
            query_id=query.id,
            document_id=document.id,
            query_external_id=record.query_external_id,
            document_external_id=record.document_external_id,
        )
        db.add(judgment)

    judgment.relevance_score = record.relevance_score
    judgment.metadata_json = record.metadata_json
    return created


def load_scifact_to_db(
    db: Session,
    document_limit: int | None = None,
    query_limit: int | None = None,
    qrel_limit: int | None = None,
    split: str = "test",
    dry_run: bool = False,
) -> SciFactLoadSummary:
    settings = get_settings()
    summary = SciFactLoadSummary(
        dry_run=dry_run,
        split=split,
        corpus_dataset_id=settings.SCIFACT_CORPUS_DATASET_ID,
        eval_dataset_id=settings.SCIFACT_EVAL_DATASET_ID,
    )

    dataset = _get_or_create_dataset(db, split, dry_run)
    if dataset is not None:
        summary.dataset_id = dataset.id

    seen_document_ids: set[str] = set()
    seen_query_ids: set[str] = set()

    for record in iter_scifact_documents(document_limit):
        summary.documents_seen += 1
        seen_document_ids.add(record.external_id)
        if dataset is not None and not dry_run:
            _upsert_document(db, dataset, record)
            summary.documents_loaded += 1
        elif dry_run:
            summary.documents_loaded += 1
    if not dry_run:
        db.commit()

    for record in iter_scifact_queries(split=split, limit=query_limit):
        summary.queries_seen += 1
        seen_query_ids.add(record.external_id)
        if dataset is not None and not dry_run:
            _upsert_query(db, dataset, record)
            summary.queries_loaded += 1
        elif dry_run:
            summary.queries_loaded += 1
    if not dry_run:
        db.commit()

    for record in iter_scifact_qrels(split=split, limit=qrel_limit):
        summary.qrels_seen += 1

        if dry_run:
            if record.query_external_id not in seen_query_ids:
                summary.qrels_skipped_missing_query += 1
                continue
            if record.document_external_id not in seen_document_ids:
                summary.qrels_skipped_missing_document += 1
                continue
            summary.qrels_loaded += 1
            continue

        if dataset is None:
            continue

        query = db.scalar(
            select(BenchmarkQuery).where(
                BenchmarkQuery.dataset_id == dataset.id,
                BenchmarkQuery.external_id == record.query_external_id,
            )
        )
        if query is None:
            summary.qrels_skipped_missing_query += 1
            continue

        document = db.scalar(
            select(Document).where(
                Document.dataset_id == dataset.id,
                Document.external_id == record.document_external_id,
            )
        )
        if document is None:
            summary.qrels_skipped_missing_document += 1
            continue

        _upsert_qrel(db, dataset, query, document, record)
        summary.qrels_loaded += 1

    if dry_run:
        db.rollback()
    else:
        db.commit()

    return summary
