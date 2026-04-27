from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class QueueStatusResponse(BaseModel):
    queue: str
    job_count: int


class EnqueueTestJobRequest(BaseModel):
    message: str = "pong"


class EnqueueJobResponse(BaseModel):
    job_id: str
    queue: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str | None
    result: dict | None = None
    error: str | None = None
    found: bool = True


class WorkerHeartbeatItem(BaseModel):
    worker_name: str
    queue_name: str | None
    status: str
    current_job_id: str | None
    metadata_json: dict
    last_seen_at: datetime
    updated_at: datetime | None = None


class WorkerHeartbeatListResponse(BaseModel):
    workers: list[WorkerHeartbeatItem]


class OpenSearchHealthResponse(BaseModel):
    status: str
    url: str
    cluster_name: str | None = None
    version: str | None = None
    error: str | None = None


class QdrantHealthResponse(BaseModel):
    status: str
    url: str
    version: str | None = None
    collections_count: int | None = None
    error: str | None = None


class EmbeddingModelStatusResponse(BaseModel):
    model_name: str
    device: str
    loaded: bool
    embedding_dimension: int | None
    cache_dir: str
    error: str | None = None


class RerankerModelStatusResponse(BaseModel):
    model_name: str
    device: str
    loaded: bool
    cache_dir: str
    error: str | None = None


class SystemEventItem(BaseModel):
    id: UUID
    event_type: str
    severity: str
    message: str
    request_id: str | None = None
    job_id: str | None = None
    trace_id: UUID | None = None
    metadata_json: dict
    created_at: datetime


class SystemEventListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[SystemEventItem]
