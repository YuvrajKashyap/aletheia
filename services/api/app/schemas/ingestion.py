from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class StartSciFactIngestionRequest(BaseModel):
    document_limit: int | None = None
    query_limit: int | None = None
    qrel_limit: int | None = None
    split: str = "test"
    chunk_after_load: bool = True
    chunk_document_limit: int | None = None
    dry_run: bool = False


class StartIngestionResponse(BaseModel):
    job_id: str
    queue: str
    status: str
    ingestion_run_id: str | None = None
    message: str


class IngestionRunItem(BaseModel):
    id: UUID
    dataset_id: UUID | None
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    documents_loaded: int
    chunks_created: int
    queries_loaded: int
    qrels_loaded: int
    errors_count: int
    config_json: dict
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class IngestionRunDetail(IngestionRunItem):
    pass


class IngestionRunListResponse(BaseModel):
    items: list[IngestionRunItem]
    total: int
    limit: int
    offset: int
