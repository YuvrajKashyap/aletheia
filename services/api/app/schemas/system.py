from datetime import datetime

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
