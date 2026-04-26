from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.datasets import Chunk, Dataset, Document
from app.text.chunking import (
    SCIFACT_CHUNKING_STRATEGY,
    SCIFACT_CHUNKING_VERSION,
    WINDOW_CHUNKING_STRATEGY,
    TextChunk,
    chunk_by_window,
    chunk_document_level,
)
from app.text.normalization import normalize_text


@dataclass
class ChunkDocumentsSummary:
    dataset_id: str | None = None
    dataset_name: str = "beir/scifact"
    dataset_version: str = "test"
    chunking_strategy: str = SCIFACT_CHUNKING_STRATEGY
    chunking_version: str = SCIFACT_CHUNKING_VERSION
    dry_run: bool = False
    documents_seen: int = 0
    chunks_created: int = 0
    chunks_existing: int = 0
    chunks_updated: int = 0
    documents_skipped_empty_text: int = 0
    errors_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def chunks_for_strategy(strategy: str, text: str) -> list[TextChunk]:
    if strategy == SCIFACT_CHUNKING_STRATEGY:
        return chunk_document_level(text)
    if strategy == WINDOW_CHUNKING_STRATEGY:
        return chunk_by_window(text)
    raise ValueError(f"Unknown chunking strategy: {strategy}")


def chunk_external_id(document_external_id: str, chunk_index: int) -> str:
    return f"{document_external_id}:{chunk_index}"


def chunk_metadata(document: Document, strategy: str, version: str) -> dict[str, str]:
    return {
        "source_document_external_id": document.external_id,
        "strategy": strategy,
        "version": version,
    }


def chunk_needs_update(chunk: Chunk, text_chunk: TextChunk, external_id: str) -> bool:
    return any(
        [
            chunk.external_id != external_id,
            chunk.text != text_chunk.text,
            chunk.token_count != text_chunk.token_count,
            chunk.char_start != text_chunk.char_start,
            chunk.char_end != text_chunk.char_end,
            chunk.content_hash != text_chunk.content_hash,
        ]
    )


def _document_query(dataset_id, document_limit: int | None):
    statement = (
        select(Document)
        .where(Document.dataset_id == dataset_id)
        .order_by(Document.external_id.asc(), Document.created_at.asc())
    )
    if document_limit is not None:
        statement = statement.limit(document_limit)
    return statement


def chunk_dataset_documents(
    db: Session,
    dataset_name: str = "beir/scifact",
    dataset_version: str = "test",
    document_limit: int | None = None,
    strategy: str = SCIFACT_CHUNKING_STRATEGY,
    chunking_version: str = SCIFACT_CHUNKING_VERSION,
    dry_run: bool = False,
) -> ChunkDocumentsSummary:
    summary = ChunkDocumentsSummary(
        dataset_name=dataset_name,
        dataset_version=dataset_version,
        chunking_strategy=strategy,
        chunking_version=chunking_version,
        dry_run=dry_run,
    )

    dataset = db.scalar(
        select(Dataset).where(Dataset.name == dataset_name, Dataset.version == dataset_version)
    )
    if dataset is None:
        raise ValueError(f"Dataset not found: {dataset_name} version {dataset_version}")

    summary.dataset_id = str(dataset.id)
    documents = db.scalars(_document_query(dataset.id, document_limit)).all()

    for document in documents:
        summary.documents_seen += 1
        normalized_text = normalize_text(document.text)
        if not normalized_text:
            summary.documents_skipped_empty_text += 1
            continue

        try:
            text_chunks = chunks_for_strategy(strategy, document.text)
        except Exception:
            summary.errors_count += 1
            raise

        if dry_run:
            summary.chunks_created += len(text_chunks)
            continue

        for text_chunk in text_chunks:
            existing = db.scalar(
                select(Chunk).where(
                    Chunk.document_id == document.id,
                    Chunk.chunk_index == text_chunk.chunk_index,
                    Chunk.chunking_strategy == strategy,
                    Chunk.chunking_version == chunking_version,
                )
            )
            external_id = chunk_external_id(document.external_id, text_chunk.chunk_index)

            if existing is None:
                db.add(
                    Chunk(
                        dataset_id=document.dataset_id,
                        document_id=document.id,
                        external_id=external_id,
                        chunk_index=text_chunk.chunk_index,
                        text=text_chunk.text,
                        token_count=text_chunk.token_count,
                        char_start=text_chunk.char_start,
                        char_end=text_chunk.char_end,
                        content_hash=text_chunk.content_hash,
                        chunking_strategy=strategy,
                        chunking_version=chunking_version,
                        metadata_json=chunk_metadata(document, strategy, chunking_version),
                    )
                )
                summary.chunks_created += 1
                continue

            if chunk_needs_update(existing, text_chunk, external_id):
                existing.external_id = external_id
                existing.text = text_chunk.text
                existing.token_count = text_chunk.token_count
                existing.char_start = text_chunk.char_start
                existing.char_end = text_chunk.char_end
                existing.content_hash = text_chunk.content_hash
                existing.metadata_json = chunk_metadata(document, strategy, chunking_version)
                summary.chunks_updated += 1
            else:
                summary.chunks_existing += 1

    if dry_run:
        db.rollback()
    else:
        db.commit()

    return summary
