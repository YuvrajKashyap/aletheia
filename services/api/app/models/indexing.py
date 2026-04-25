from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Boolean, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin, UpdatedAtMixin


class IngestionRun(UUIDPrimaryKeyMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "ingestion_runs"
    __table_args__ = (
        Index("ix_ingestion_runs_status", "status"),
        Index("ix_ingestion_runs_started_at", "started_at"),
        Index("ix_ingestion_runs_dataset_id", "dataset_id"),
    )

    dataset_id: Mapped[UUID | None] = mapped_column(ForeignKey("datasets.id"), nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    documents_loaded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunks_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    queries_loaded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    qrels_loaded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    config_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class IndexVersion(UUIDPrimaryKeyMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "index_versions"
    __table_args__ = (
        UniqueConstraint("dataset_id", "name"),
        Index("ix_index_versions_dataset_id", "dataset_id"),
        Index("ix_index_versions_status", "status"),
        Index("ix_index_versions_is_active", "is_active"),
        Index(
            "uq_index_versions_active_dataset",
            "dataset_id",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
    )

    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    lexical_index_name: Mapped[str | None] = mapped_column(String, nullable=True)
    vector_collection_name: Mapped[str | None] = mapped_column(String, nullable=True)
    embedding_model: Mapped[str | None] = mapped_column(String, nullable=True)
    embedding_dimension: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunking_strategy: Mapped[str | None] = mapped_column(String, nullable=True)
    chunking_version: Mapped[str | None] = mapped_column(String, nullable=True)
    document_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    vector_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    config_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class IndexJob(UUIDPrimaryKeyMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "index_jobs"
    __table_args__ = (
        Index("ix_index_jobs_index_version_id", "index_version_id"),
        Index("ix_index_jobs_job_id", "job_id"),
        Index("ix_index_jobs_job_type", "job_type"),
        Index("ix_index_jobs_status", "status"),
        Index("ix_index_jobs_started_at", "started_at"),
    )

    index_version_id: Mapped[UUID] = mapped_column(ForeignKey("index_versions.id"), nullable=False)
    job_id: Mapped[str | None] = mapped_column(String, nullable=True)
    job_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    chunks_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunks_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    chunks_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    config_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
