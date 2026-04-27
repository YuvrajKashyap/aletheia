from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


SUPPORTED_RETRIEVAL_MODES = {"bm25", "dense", "hybrid", "hybrid_rerank"}


def _validate_mode(value: str | None) -> str | None:
    if value is not None and value not in SUPPORTED_RETRIEVAL_MODES:
        raise ValueError("retrieval_mode must be bm25, dense, hybrid, or hybrid_rerank")
    return value


class SavedQueryCreateRequest(BaseModel):
    text: str = Field(min_length=1)
    name: str | None = None
    source: str = "manual"
    dataset_id: UUID | None = None
    metadata_json: dict[str, Any] | None = None

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be empty")
        return value


class SavedQueryItem(BaseModel):
    id: UUID | str
    name: str | None
    text: str
    source: str
    dataset_id: UUID | str | None
    metadata_json: dict[str, Any]
    created_at: datetime


class SavedQueryDetail(SavedQueryItem):
    pass


class SavedQueryListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[SavedQueryItem]


class SeedGoldenQueriesRequest(BaseModel):
    dataset_name: str = "beir/scifact"
    dataset_version: str = "test"
    limit: int = Field(default=20, ge=1, le=300)
    offset: int = Field(default=0, ge=0)


class SeedGoldenQueriesResponse(BaseModel):
    created_count: int
    existing_count: int
    total_selected: int
    items: list[SavedQueryItem]


class ReplayParamsMixin(BaseModel):
    retrieval_mode: str | None = None
    experiment_config_id: UUID | None = None
    experiment_config_name: str | None = None
    top_k: int = Field(default=10, ge=1, le=100)
    candidate_k: int | None = Field(default=None, ge=1, le=500)
    bm25_candidate_k: int | None = Field(default=None, ge=1, le=500)
    dense_candidate_k: int | None = Field(default=None, ge=1, le=500)
    hybrid_candidate_k: int | None = Field(default=None, ge=1, le=500)
    rerank_top_n: int | None = Field(default=None, ge=1, le=500)
    rrf_k: int = Field(default=60, ge=1)

    @field_validator("retrieval_mode")
    @classmethod
    def retrieval_mode_supported(cls, value: str | None) -> str | None:
        return _validate_mode(value)

    @model_validator(mode="after")
    def validate_replay_params(self):
        if self.retrieval_mode is None and not self.experiment_config_id and not self.experiment_config_name:
            raise ValueError(
                "retrieval_mode is required unless experiment_config_id or experiment_config_name is provided"
            )
        if self.candidate_k is not None and self.candidate_k < self.top_k:
            raise ValueError("candidate_k must be greater than or equal to top_k")
        if self.retrieval_mode in {"hybrid", "hybrid_rerank"}:
            if self.bm25_candidate_k is not None and self.bm25_candidate_k < self.top_k:
                raise ValueError("bm25_candidate_k must be greater than or equal to top_k")
            if self.dense_candidate_k is not None and self.dense_candidate_k < self.top_k:
                raise ValueError("dense_candidate_k must be greater than or equal to top_k")
        if self.retrieval_mode == "hybrid_rerank":
            if self.rerank_top_n is not None and self.rerank_top_n < self.top_k:
                raise ValueError("rerank_top_n must be greater than or equal to top_k")
            rerank_floor = self.rerank_top_n if self.rerank_top_n is not None else self.top_k
            if self.hybrid_candidate_k is not None and self.hybrid_candidate_k < rerank_floor:
                raise ValueError("hybrid_candidate_k must be greater than or equal to rerank_top_n")
        return self


class ReplaySavedQueryRequest(ReplayParamsMixin):
    index_version_id: UUID | None = None
    source_trace_id: UUID | None = None


class ReplayResponse(BaseModel):
    job_id: str
    queue: str
    status: str
    message: str


class QueryReplayItem(BaseModel):
    id: UUID | str
    saved_query_id: UUID | str | None
    original_query_id: UUID | str | None
    source_trace_id: UUID | str | None
    target_trace_id: UUID | str | None
    experiment_config_id: UUID | str | None
    index_version_id: UUID | str | None
    status: str
    error_message: str | None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class QueryReplayDetail(QueryReplayItem):
    comparison_json: dict[str, Any]


class QueryReplayListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[QueryReplayItem]


class StartGoldenReplayRequest(ReplayParamsMixin):
    name: str | None = None
    source: str = "golden_scifact"
    limit: int | None = Field(default=None, ge=1, le=300)
    offset: int = Field(default=0, ge=0)
    notes: str | None = None


class StartGoldenReplayResponse(BaseModel):
    job_id: str
    queue: str
    status: str
    message: str
