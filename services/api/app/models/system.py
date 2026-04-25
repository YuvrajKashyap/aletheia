from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin, UpdatedAtMixin


class SystemEvent(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "system_events"
    __table_args__ = (
        Index("ix_system_events_event_type", "event_type"),
        Index("ix_system_events_severity", "severity"),
        Index("ix_system_events_request_id", "request_id"),
        Index("ix_system_events_job_id", "job_id"),
        Index("ix_system_events_trace_id", "trace_id"),
        Index("ix_system_events_created_at", "created_at"),
        Index("ix_system_events_severity_created_at", "severity", "created_at"),
    )

    event_type: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    request_id: Mapped[str | None] = mapped_column(String, nullable=True)
    job_id: Mapped[str | None] = mapped_column(String, nullable=True)
    trace_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)


class WorkerHeartbeat(UUIDPrimaryKeyMixin, CreatedAtMixin, UpdatedAtMixin, Base):
    __tablename__ = "worker_heartbeats"
    __table_args__ = (
        UniqueConstraint("worker_name"),
        Index("ix_worker_heartbeats_status", "status"),
        Index("ix_worker_heartbeats_queue_name", "queue_name"),
        Index("ix_worker_heartbeats_last_seen_at", "last_seen_at"),
    )

    worker_name: Mapped[str] = mapped_column(String, nullable=False)
    queue_name: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    current_job_id: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
