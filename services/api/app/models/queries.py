from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin, UpdatedAtMixin


class Query(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "queries"
    __table_args__ = (
        Index("ix_queries_retrieval_mode", "retrieval_mode"),
        Index("ix_queries_status", "status"),
        Index("ix_queries_created_at", "created_at"),
        Index("ix_queries_request_id", "request_id"),
        Index("ix_queries_index_version_id", "index_version_id"),
    )

    text: Mapped[str] = mapped_column(Text, nullable=False)
    retrieval_mode: Mapped[str] = mapped_column(String, nullable=False)
    index_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("index_versions.id"),
        nullable=True,
    )
    request_id: Mapped[str | None] = mapped_column(String, nullable=True)
    total_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class QueryTrace(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "query_traces"
    __table_args__ = (
        UniqueConstraint("query_id"),
        Index("ix_query_traces_created_at", "created_at"),
    )

    query_id: Mapped[UUID] = mapped_column(ForeignKey("queries.id"), nullable=False)
    trace_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class RetrievalCandidate(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "retrieval_candidates"
    __table_args__ = (
        Index("ix_retrieval_candidates_query_id", "query_id"),
        Index("ix_retrieval_candidates_trace_id", "trace_id"),
        Index("ix_retrieval_candidates_chunk_id", "chunk_id"),
        Index("ix_retrieval_candidates_document_id", "document_id"),
        Index("ix_retrieval_candidates_source", "source"),
        Index("ix_retrieval_candidates_final_rank", "final_rank"),
    )

    query_id: Mapped[UUID] = mapped_column(ForeignKey("queries.id"), nullable=False)
    trace_id: Mapped[UUID | None] = mapped_column(ForeignKey("query_traces.id"), nullable=True)
    chunk_id: Mapped[UUID | None] = mapped_column(ForeignKey("chunks.id"), nullable=True)
    document_id: Mapped[UUID | None] = mapped_column(ForeignKey("documents.id"), nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    bm25_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dense_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fusion_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rerank_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    final_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bm25_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    dense_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    fusion_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reranker_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class SavedQuery(UUIDPrimaryKeyMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "saved_queries"
    __table_args__ = (
        Index("ix_saved_queries_dataset_id", "dataset_id"),
        Index("ix_saved_queries_source", "source"),
        Index("ix_saved_queries_created_at", "created_at"),
    )

    dataset_id: Mapped[UUID | None] = mapped_column(ForeignKey("datasets.id"), nullable=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String, default="manual", nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class QueryReplay(UUIDPrimaryKeyMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "query_replays"
    __table_args__ = (
        Index("ix_query_replays_saved_query_id", "saved_query_id"),
        Index("ix_query_replays_original_query_id", "original_query_id"),
        Index("ix_query_replays_experiment_config_id", "experiment_config_id"),
        Index("ix_query_replays_index_version_id", "index_version_id"),
        Index("ix_query_replays_status", "status"),
        Index("ix_query_replays_started_at", "started_at"),
    )

    saved_query_id: Mapped[UUID | None] = mapped_column(ForeignKey("saved_queries.id"), nullable=True)
    original_query_id: Mapped[UUID | None] = mapped_column(ForeignKey("queries.id"), nullable=True)
    source_trace_id: Mapped[UUID | None] = mapped_column(ForeignKey("query_traces.id"), nullable=True)
    target_trace_id: Mapped[UUID | None] = mapped_column(ForeignKey("query_traces.id"), nullable=True)
    experiment_config_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("experiment_configs.id"),
        nullable=True,
    )
    index_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("index_versions.id"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String, nullable=False)
    comparison_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
