from uuid import UUID

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin, UpdatedAtMixin


class Dataset(UUIDPrimaryKeyMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "datasets"
    __table_args__ = (
        UniqueConstraint("name", "version"),
        Index("ix_datasets_name", "name"),
        Index("ix_datasets_source", "source"),
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str | None] = mapped_column(String, nullable=True)
    version: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    license_name: Mapped[str | None] = mapped_column(String, nullable=True)
    license_url: Mapped[str | None] = mapped_column(String, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    documents: Mapped[list["Document"]] = relationship(back_populates="dataset")
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="dataset")
    benchmark_queries: Mapped[list["BenchmarkQuery"]] = relationship(back_populates="dataset")
    relevance_judgments: Mapped[list["RelevanceJudgment"]] = relationship(back_populates="dataset")


class Document(UUIDPrimaryKeyMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("dataset_id", "external_id"),
        Index("ix_documents_dataset_id", "dataset_id"),
        Index("ix_documents_external_id", "external_id"),
    )

    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    dataset: Mapped["Dataset"] = relationship(back_populates="documents")
    chunks: Mapped[list["Chunk"]] = relationship(back_populates="document")
    relevance_judgments: Mapped[list["RelevanceJudgment"]] = relationship(back_populates="document")


class Chunk(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", "chunking_strategy", "chunking_version"),
        Index("ix_chunks_dataset_id", "dataset_id"),
        Index("ix_chunks_document_id", "document_id"),
        Index("ix_chunks_content_hash", "content_hash"),
        Index("ix_chunks_chunking_strategy_chunking_version", "chunking_strategy", "chunking_version"),
    )

    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id"), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    char_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    char_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content_hash: Mapped[str] = mapped_column(String, nullable=False)
    chunking_strategy: Mapped[str] = mapped_column(String, nullable=False)
    chunking_version: Mapped[str] = mapped_column(String, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    dataset: Mapped["Dataset"] = relationship(back_populates="chunks")
    document: Mapped["Document"] = relationship(back_populates="chunks")


class BenchmarkQuery(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "benchmark_queries"
    __table_args__ = (
        UniqueConstraint("dataset_id", "external_id"),
        Index("ix_benchmark_queries_dataset_id", "dataset_id"),
        Index("ix_benchmark_queries_split", "split"),
    )

    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    split: Mapped[str | None] = mapped_column(String, default="test", nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    dataset: Mapped["Dataset"] = relationship(back_populates="benchmark_queries")
    relevance_judgments: Mapped[list["RelevanceJudgment"]] = relationship(back_populates="query")


class RelevanceJudgment(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "relevance_judgments"
    __table_args__ = (
        UniqueConstraint("query_id", "document_id"),
        Index("ix_relevance_judgments_dataset_id", "dataset_id"),
        Index("ix_relevance_judgments_query_external_id", "query_external_id"),
        Index("ix_relevance_judgments_document_external_id", "document_external_id"),
    )

    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    query_id: Mapped[UUID] = mapped_column(ForeignKey("benchmark_queries.id"), nullable=False)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id"), nullable=False)
    query_external_id: Mapped[str] = mapped_column(String, nullable=False)
    document_external_id: Mapped[str] = mapped_column(String, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    dataset: Mapped["Dataset"] = relationship(back_populates="relevance_judgments")
    query: Mapped["BenchmarkQuery"] = relationship(back_populates="relevance_judgments")
    document: Mapped["Document"] = relationship(back_populates="relevance_judgments")
