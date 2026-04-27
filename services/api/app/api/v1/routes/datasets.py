from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.datasets import BenchmarkQuery, Chunk, Dataset, Document, RelevanceJudgment
from app.schemas.datasets import (
    BenchmarkQueryDetailResponse,
    BenchmarkQueryListItem,
    BenchmarkQueryListResponse,
    ChunkDetailResponse,
    ChunkListItem,
    ChunkListResponse,
    DatasetStatsResponse,
    DatasetSummary,
    DocumentDetailResponse,
    DocumentListItem,
    DocumentListResponse,
    RelevanceJudgmentItem,
    RelevanceJudgmentListResponse,
)

router = APIRouter(tags=["datasets"])


def _count(db: Session, statement) -> int:
    return int(db.scalar(statement) or 0)


def _preview(text: str, max_length: int = 240) -> str:
    if len(text) <= max_length:
        return text
    return f"{text[: max_length - 3]}..."


def _dataset_counts(db: Session, dataset_id: UUID) -> dict[str, int]:
    return {
        "document_count": _count(
            db,
            select(func.count()).select_from(Document).where(Document.dataset_id == dataset_id),
        ),
        "chunk_count": _count(
            db,
            select(func.count()).select_from(Chunk).where(Chunk.dataset_id == dataset_id),
        ),
        "benchmark_query_count": _count(
            db,
            select(func.count()).select_from(BenchmarkQuery).where(
                BenchmarkQuery.dataset_id == dataset_id
            ),
        ),
        "relevance_judgment_count": _count(
            db,
            select(func.count()).select_from(RelevanceJudgment).where(
                RelevanceJudgment.dataset_id == dataset_id
            ),
        ),
    }


def _chunk_list_item(chunk: Chunk) -> ChunkListItem:
    return ChunkListItem(
        id=chunk.id,
        dataset_id=chunk.dataset_id,
        document_id=chunk.document_id,
        external_id=chunk.external_id,
        chunk_index=chunk.chunk_index,
        text_preview=_preview(chunk.text),
        token_count=chunk.token_count,
        content_hash=chunk.content_hash,
        chunking_strategy=chunk.chunking_strategy,
        chunking_version=chunk.chunking_version,
        created_at=chunk.created_at,
    )


@router.get("/datasets", response_model=list[DatasetSummary])
async def list_datasets(db: Session = Depends(get_db)) -> list[DatasetSummary]:
    datasets = db.scalars(select(Dataset).order_by(Dataset.created_at.desc())).all()
    return [
        DatasetSummary(
            id=dataset.id,
            name=dataset.name,
            version=dataset.version,
            source=dataset.source,
            description=dataset.description,
            created_at=dataset.created_at,
            document_count=counts["document_count"],
            chunk_count=counts["chunk_count"],
            benchmark_query_count=counts["benchmark_query_count"],
            relevance_judgment_count=counts["relevance_judgment_count"],
        )
        for dataset in datasets
        for counts in [_dataset_counts(db, dataset.id)]
    ]


@router.get("/datasets/{dataset_id}/stats", response_model=DatasetStatsResponse)
async def dataset_stats(dataset_id: UUID, db: Session = Depends(get_db)) -> DatasetStatsResponse:
    dataset = db.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset not found: {dataset_id}",
        )

    counts = _dataset_counts(db, dataset.id)
    return DatasetStatsResponse(
        id=dataset.id,
        name=dataset.name,
        version=dataset.version,
        source=dataset.source,
        **counts,
    )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    dataset_id: UUID | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    filters = []
    if dataset_id is not None:
        filters.append(Document.dataset_id == dataset_id)

    total_statement = select(func.count()).select_from(Document)
    item_statement = select(Document).order_by(Document.created_at.desc()).limit(limit).offset(offset)
    if filters:
        total_statement = total_statement.where(*filters)
        item_statement = item_statement.where(*filters)

    total = _count(db, total_statement)
    documents = db.scalars(item_statement).all()
    return DocumentListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[
            DocumentListItem(
                id=document.id,
                dataset_id=document.dataset_id,
                external_id=document.external_id,
                title=document.title,
                text_preview=_preview(document.text),
                source_url=document.source_url,
                metadata_json=document.metadata_json,
                created_at=document.created_at,
                updated_at=document.updated_at,
            )
            for document in documents
        ],
    )


@router.get("/documents/{document_id}", response_model=DocumentDetailResponse)
async def document_detail(
    document_id: UUID,
    db: Session = Depends(get_db),
) -> DocumentDetailResponse:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document not found: {document_id}",
        )

    chunk_count = _count(
        db,
        select(func.count()).select_from(Chunk).where(Chunk.document_id == document.id),
    )
    preview_chunks = db.scalars(
        select(Chunk)
        .where(Chunk.document_id == document.id)
        .order_by(Chunk.chunk_index.asc(), Chunk.created_at.asc())
        .limit(5)
    ).all()

    return DocumentDetailResponse(
        id=document.id,
        dataset_id=document.dataset_id,
        external_id=document.external_id,
        title=document.title,
        text=document.text,
        source_url=document.source_url,
        metadata_json=document.metadata_json,
        created_at=document.created_at,
        updated_at=document.updated_at,
        chunk_count=chunk_count,
        chunks_preview=[_chunk_list_item(chunk) for chunk in preview_chunks],
    )


@router.get("/benchmark-queries", response_model=BenchmarkQueryListResponse)
async def list_benchmark_queries(
    dataset_id: UUID | None = None,
    split: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> BenchmarkQueryListResponse:
    filters = []
    if dataset_id is not None:
        filters.append(BenchmarkQuery.dataset_id == dataset_id)
    if split is not None:
        filters.append(BenchmarkQuery.split == split)

    total_statement = select(func.count()).select_from(BenchmarkQuery)
    item_statement = (
        select(BenchmarkQuery).order_by(BenchmarkQuery.created_at.desc()).limit(limit).offset(offset)
    )
    if filters:
        total_statement = total_statement.where(*filters)
        item_statement = item_statement.where(*filters)

    total = _count(db, total_statement)
    queries = db.scalars(item_statement).all()
    return BenchmarkQueryListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[
            BenchmarkQueryListItem(
                id=query.id,
                dataset_id=query.dataset_id,
                external_id=query.external_id,
                text=query.text,
                split=query.split,
                created_at=query.created_at,
            )
            for query in queries
        ],
    )


@router.get("/benchmark-queries/{query_id}", response_model=BenchmarkQueryDetailResponse)
async def benchmark_query_detail(
    query_id: UUID,
    db: Session = Depends(get_db),
) -> BenchmarkQueryDetailResponse:
    query = db.get(BenchmarkQuery, query_id)
    if query is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Benchmark query not found: {query_id}",
        )

    relevance_judgment_count = _count(
        db,
        select(func.count()).select_from(RelevanceJudgment).where(
            RelevanceJudgment.query_id == query.id
        ),
    )
    return BenchmarkQueryDetailResponse(
        id=query.id,
        dataset_id=query.dataset_id,
        external_id=query.external_id,
        text=query.text,
        split=query.split,
        metadata_json=query.metadata_json,
        created_at=query.created_at,
        relevance_judgment_count=relevance_judgment_count,
    )


@router.get("/chunks", response_model=ChunkListResponse)
async def list_chunks(
    dataset_id: UUID | None = None,
    document_id: UUID | None = None,
    chunking_strategy: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> ChunkListResponse:
    filters = []
    if dataset_id is not None:
        filters.append(Chunk.dataset_id == dataset_id)
    if document_id is not None:
        filters.append(Chunk.document_id == document_id)
    if chunking_strategy is not None:
        filters.append(Chunk.chunking_strategy == chunking_strategy)

    total_statement = select(func.count()).select_from(Chunk)
    item_statement = (
        select(Chunk)
        .order_by(Chunk.created_at.desc(), Chunk.chunk_index.asc())
        .limit(limit)
        .offset(offset)
    )
    if filters:
        total_statement = total_statement.where(*filters)
        item_statement = item_statement.where(*filters)

    total = _count(db, total_statement)
    chunks = db.scalars(item_statement).all()
    return ChunkListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[_chunk_list_item(chunk) for chunk in chunks],
    )


@router.get("/chunks/{chunk_id}", response_model=ChunkDetailResponse)
async def chunk_detail(chunk_id: UUID, db: Session = Depends(get_db)) -> ChunkDetailResponse:
    chunk = db.get(Chunk, chunk_id)
    if chunk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chunk not found: {chunk_id}",
        )

    return ChunkDetailResponse(
        id=chunk.id,
        dataset_id=chunk.dataset_id,
        document_id=chunk.document_id,
        external_id=chunk.external_id,
        chunk_index=chunk.chunk_index,
        text=chunk.text,
        token_count=chunk.token_count,
        char_start=chunk.char_start,
        char_end=chunk.char_end,
        content_hash=chunk.content_hash,
        chunking_strategy=chunk.chunking_strategy,
        chunking_version=chunk.chunking_version,
        metadata_json=chunk.metadata_json,
        created_at=chunk.created_at,
    )


@router.get("/relevance-judgments", response_model=RelevanceJudgmentListResponse)
async def list_relevance_judgments(
    dataset_id: UUID | None = None,
    query_id: UUID | None = None,
    document_id: UUID | None = None,
    query_external_id: str | None = None,
    document_external_id: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> RelevanceJudgmentListResponse:
    filters = []
    if dataset_id is not None:
        filters.append(RelevanceJudgment.dataset_id == dataset_id)
    if query_id is not None:
        filters.append(RelevanceJudgment.query_id == query_id)
    if document_id is not None:
        filters.append(RelevanceJudgment.document_id == document_id)
    if query_external_id:
        filters.append(RelevanceJudgment.query_external_id == query_external_id)
    if document_external_id:
        filters.append(RelevanceJudgment.document_external_id == document_external_id)

    total_statement = select(func.count()).select_from(RelevanceJudgment)
    item_statement = (
        select(RelevanceJudgment, BenchmarkQuery.text, Document.title)
        .join(BenchmarkQuery, BenchmarkQuery.id == RelevanceJudgment.query_id)
        .join(Document, Document.id == RelevanceJudgment.document_id)
        .order_by(RelevanceJudgment.created_at.desc(), RelevanceJudgment.id.asc())
        .limit(limit)
        .offset(offset)
    )
    if filters:
        total_statement = total_statement.where(*filters)
        item_statement = item_statement.where(*filters)

    total = _count(db, total_statement)
    rows = db.execute(item_statement).all()
    return RelevanceJudgmentListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[
            RelevanceJudgmentItem(
                id=judgment.id,
                dataset_id=judgment.dataset_id,
                query_id=judgment.query_id,
                document_id=judgment.document_id,
                query_external_id=judgment.query_external_id,
                document_external_id=judgment.document_external_id,
                relevance_score=judgment.relevance_score,
                metadata_json=judgment.metadata_json,
                created_at=judgment.created_at,
                query_text=query_text,
                document_title=document_title,
            )
            for judgment, query_text, document_title in rows
        ],
    )
