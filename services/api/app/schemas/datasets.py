from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DatasetSummary(BaseModel):
    id: UUID
    name: str
    version: str
    source: str | None
    document_count: int
    benchmark_query_count: int
    relevance_judgment_count: int
    created_at: datetime


class DatasetStatsResponse(BaseModel):
    id: UUID
    name: str
    version: str
    source: str | None
    document_count: int
    chunk_count: int
    benchmark_query_count: int
    relevance_judgment_count: int


class DocumentListItem(BaseModel):
    id: UUID
    dataset_id: UUID
    external_id: str
    title: str | None
    source_url: str | None
    created_at: datetime


class DocumentListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[DocumentListItem]


class BenchmarkQueryListItem(BaseModel):
    id: UUID
    dataset_id: UUID
    external_id: str
    text: str
    split: str | None
    created_at: datetime


class BenchmarkQueryListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[BenchmarkQueryListItem]


class ChunkListItem(BaseModel):
    id: UUID
    dataset_id: UUID
    document_id: UUID
    external_id: str | None
    chunk_index: int
    text_preview: str
    token_count: int | None
    content_hash: str
    chunking_strategy: str
    chunking_version: str
    created_at: datetime


class ChunkListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[ChunkListItem]


class ChunkDetailResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    document_id: UUID
    external_id: str | None
    chunk_index: int
    text: str
    token_count: int | None
    char_start: int | None
    char_end: int | None
    content_hash: str
    chunking_strategy: str
    chunking_version: str
    metadata_json: dict
    created_at: datetime
