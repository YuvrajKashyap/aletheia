from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DatasetSummary(BaseModel):
    id: UUID
    name: str
    version: str
    source: str | None
    description: str | None = None
    document_count: int
    chunk_count: int | None = None
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
    text_preview: str | None = None
    source_url: str | None
    metadata_json: dict | None = None
    created_at: datetime
    updated_at: datetime | None = None


class DocumentListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[DocumentListItem]


class DocumentDetailResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    external_id: str
    title: str | None
    text: str
    source_url: str | None
    metadata_json: dict
    created_at: datetime
    updated_at: datetime | None = None
    chunk_count: int
    chunks_preview: list["ChunkListItem"] = []


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


class BenchmarkQueryDetailResponse(BaseModel):
    id: UUID
    dataset_id: UUID
    external_id: str
    text: str
    split: str | None
    metadata_json: dict
    created_at: datetime
    relevance_judgment_count: int


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


class RelevanceJudgmentItem(BaseModel):
    id: UUID
    dataset_id: UUID
    query_id: UUID
    document_id: UUID
    query_external_id: str
    document_external_id: str
    relevance_score: float
    metadata_json: dict
    created_at: datetime
    query_text: str | None = None
    document_title: str | None = None


class RelevanceJudgmentListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[RelevanceJudgmentItem]
