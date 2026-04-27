from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateIndexVersionRequest(BaseModel):
    dataset_id: UUID | None = None
    dataset_name: str = "beir/scifact"
    dataset_version: str = "test"
    name: str | None = None
    lexical_index_name: str | None = None
    vector_collection_name: str | None = None
    embedding_model: str | None = None
    embedding_dimension: int | None = None
    chunking_strategy: str = "scifact_document_v1"
    chunking_version: str = "1.0"
    notes: str | None = None
    config_json: dict = Field(default_factory=dict)


class IndexVersionItem(BaseModel):
    id: UUID
    dataset_id: UUID
    name: str
    status: str
    is_active: bool
    lexical_index_name: str | None
    vector_collection_name: str | None
    embedding_model: str | None
    embedding_dimension: int | None
    chunking_strategy: str | None
    chunking_version: str | None
    document_count: int
    chunk_count: int
    vector_count: int
    config_json: dict
    notes: str | None
    created_at: datetime
    updated_at: datetime
    activated_at: datetime | None


class IndexVersionDetail(IndexVersionItem):
    pass


class IndexVersionListResponse(BaseModel):
    items: list[IndexVersionItem]
    total: int
    limit: int
    offset: int


class IndexJobItem(BaseModel):
    id: UUID
    index_version_id: UUID
    job_id: str | None
    job_type: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    chunks_total: int
    chunks_completed: int
    chunks_failed: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime | None


class IndexJobListResponse(BaseModel):
    items: list[IndexJobItem]
    total: int
    limit: int
    offset: int


class IndexStatusResponse(BaseModel):
    active_index_version: IndexVersionItem | None
    dataset_count: int
    index_version_count: int
    ready_index_version_count: int
    active_index_version_count: int
    latest_index_versions: list[IndexVersionItem]


class ActivateIndexVersionResponse(BaseModel):
    index_version: IndexVersionItem
    message: str


class MarkIndexVersionStatusRequest(BaseModel):
    error_message: str | None = None
    document_count: int | None = None
    chunk_count: int | None = None
    vector_count: int | None = None


class BuildLexicalIndexRequest(BaseModel):
    recreate: bool = False
    limit: int | None = Field(default=None, ge=1)
    refresh: bool = True


class BuildLexicalIndexResponse(BaseModel):
    job_id: str
    queue: str
    status: str
    index_version_id: UUID
    message: str


class BuildVectorIndexRequest(BaseModel):
    recreate: bool = False
    limit: int | None = Field(default=None, ge=1)
    batch_size: int | None = Field(default=None, ge=1)


class BuildVectorIndexResponse(BaseModel):
    job_id: str
    queue: str
    status: str
    index_version_id: UUID
    message: str
