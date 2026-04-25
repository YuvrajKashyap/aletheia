from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin, UpdatedAtMixin


class EvaluationRun(UUIDPrimaryKeyMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "evaluation_runs"
    __table_args__ = (
        Index("ix_evaluation_runs_dataset_id", "dataset_id"),
        Index("ix_evaluation_runs_index_version_id", "index_version_id"),
        Index("ix_evaluation_runs_experiment_config_id", "experiment_config_id"),
        Index("ix_evaluation_runs_status", "status"),
        Index("ix_evaluation_runs_started_at", "started_at"),
        Index("ix_evaluation_runs_created_at", "created_at"),
    )

    name: Mapped[str] = mapped_column(String, nullable=False)
    dataset_id: Mapped[UUID] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    index_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("index_versions.id"),
        nullable=True,
    )
    experiment_config_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("experiment_configs.id"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    query_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_query_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    recall_at_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    recall_at_10: Mapped[float | None] = mapped_column(Float, nullable=True)
    mrr_at_10: Mapped[float | None] = mapped_column(Float, nullable=True)
    ndcg_at_10: Mapped[float | None] = mapped_column(Float, nullable=True)
    p50_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    p95_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    config_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_path: Mapped[str | None] = mapped_column(String, nullable=True)


class EvaluationQueryResult(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "evaluation_query_results"
    __table_args__ = (
        UniqueConstraint("evaluation_run_id", "query_external_id"),
        Index("ix_evaluation_query_results_evaluation_run_id", "evaluation_run_id"),
        Index("ix_evaluation_query_results_benchmark_query_id", "benchmark_query_id"),
        Index("ix_evaluation_query_results_trace_id", "trace_id"),
    )

    evaluation_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("evaluation_runs.id"),
        nullable=False,
    )
    benchmark_query_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("benchmark_queries.id"),
        nullable=True,
    )
    query_external_id: Mapped[str] = mapped_column(String, nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    relevant_document_ids_json: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    retrieved_document_ids_json: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    recall_at_5: Mapped[float | None] = mapped_column(Float, nullable=True)
    recall_at_10: Mapped[float | None] = mapped_column(Float, nullable=True)
    mrr_at_10: Mapped[float | None] = mapped_column(Float, nullable=True)
    ndcg_at_10: Mapped[float | None] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    trace_id: Mapped[UUID | None] = mapped_column(ForeignKey("query_traces.id"), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class EvaluationReport(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "evaluation_reports"
    __table_args__ = (
        Index("ix_evaluation_reports_evaluation_run_id", "evaluation_run_id"),
        Index("ix_evaluation_reports_report_format", "report_format"),
        Index("ix_evaluation_reports_created_at", "created_at"),
    )

    evaluation_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("evaluation_runs.id"),
        nullable=False,
    )
    report_format: Mapped[str] = mapped_column(String, nullable=False)
    report_path: Mapped[str | None] = mapped_column(String, nullable=True)
    summary_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
