from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class SearchRequest(BaseModel):
    query: str
    retrieval_mode: str = "bm25"
    top_k: int = Field(default=10, ge=1, le=100)
    candidate_k: int | None = Field(default=None, ge=1, le=500)
    index_version_id: UUID | None = None

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query must not be empty")
        return value

    @field_validator("retrieval_mode")
    @classmethod
    def retrieval_mode_must_be_bm25(cls, value: str) -> str:
        if value != "bm25":
            raise ValueError('retrieval_mode must be "bm25"')
        return value

    @model_validator(mode="after")
    def candidate_k_must_cover_top_k(self) -> "SearchRequest":
        if self.candidate_k is not None and self.candidate_k < self.top_k:
            raise ValueError("candidate_k must be greater than or equal to top_k")
        return self


class SearchResultItem(BaseModel):
    rank: int
    chunk_id: UUID | str
    document_id: UUID | str | None
    dataset_id: UUID | str | None
    document_external_id: str | None
    chunk_external_id: str | None
    title: str | None
    text: str
    score: float
    score_breakdown: dict[str, Any]
    token_count: int | None
    chunking_strategy: str | None
    chunking_version: str | None
    metadata_json: dict[str, Any]


class SearchResponse(BaseModel):
    query_id: UUID | str
    trace_id: UUID | str
    request_id: str | None
    query: str
    retrieval_mode: str
    index_version_id: UUID | str | None
    index_name: str
    top_k: int
    candidate_k: int
    latency_ms: float
    result_count: int
    results: list[SearchResultItem]


class TraceListItem(BaseModel):
    trace_id: UUID | str
    query_id: UUID | str
    query_text: str
    retrieval_mode: str
    status: str
    total_latency_ms: float | None
    created_at: datetime


class TraceListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[TraceListItem]


class TraceCandidateItem(BaseModel):
    chunk_id: UUID | str | None
    document_id: UUID | str | None
    source: str
    bm25_rank: int | None
    dense_rank: int | None
    fusion_rank: int | None
    rerank_rank: int | None
    final_rank: int | None
    bm25_score: float | None
    dense_score: float | None
    fusion_score: float | None
    reranker_score: float | None
    metadata_json: dict[str, Any]


class TraceDetailResponse(BaseModel):
    trace_id: UUID | str
    query_id: UUID | str
    query_text: str
    retrieval_mode: str
    index_version_id: UUID | str | None
    status: str
    total_latency_ms: float | None
    trace_json: dict[str, Any]
    candidates: list[TraceCandidateItem]
    created_at: datetime
