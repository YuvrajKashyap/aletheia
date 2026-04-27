from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


SUPPORTED_RETRIEVAL_MODES = {"bm25", "dense", "hybrid", "hybrid_rerank"}


class StartEvaluationRequest(BaseModel):
    name: str | None = None
    retrieval_mode: str
    dataset_name: str = "beir/scifact"
    dataset_version: str = "test"
    index_version_id: UUID | None = None
    query_limit: int | None = Field(default=None, ge=1, le=300)
    query_offset: int = Field(default=0, ge=0)
    top_k: int = Field(default=10, ge=1, le=100)
    candidate_k: int | None = Field(default=None, ge=1, le=500)
    bm25_candidate_k: int | None = Field(default=None, ge=1, le=500)
    dense_candidate_k: int | None = Field(default=None, ge=1, le=500)
    hybrid_candidate_k: int | None = Field(default=None, ge=1, le=500)
    rerank_top_n: int | None = Field(default=None, ge=1, le=500)
    rrf_k: int = Field(default=60, ge=1)
    notes: str | None = None

    @field_validator("retrieval_mode")
    @classmethod
    def retrieval_mode_supported(cls, value: str) -> str:
        if value not in SUPPORTED_RETRIEVAL_MODES:
            raise ValueError("retrieval_mode must be bm25, dense, hybrid, or hybrid_rerank")
        return value

    @model_validator(mode="after")
    def validate_candidate_depths(self) -> "StartEvaluationRequest":
        if self.candidate_k is not None and self.candidate_k < self.top_k:
            raise ValueError("candidate_k must be greater than or equal to top_k")
        if self.retrieval_mode in {"hybrid", "hybrid_rerank"}:
            if self.bm25_candidate_k is not None and self.bm25_candidate_k < self.top_k:
                raise ValueError("bm25_candidate_k must be greater than or equal to top_k")
            if self.dense_candidate_k is not None and self.dense_candidate_k < self.top_k:
                raise ValueError("dense_candidate_k must be greater than or equal to top_k")
        if self.retrieval_mode == "hybrid_rerank":
            rerank_floor = self.rerank_top_n if self.rerank_top_n is not None else self.top_k
            if self.rerank_top_n is not None and self.rerank_top_n < self.top_k:
                raise ValueError("rerank_top_n must be greater than or equal to top_k")
            if self.hybrid_candidate_k is not None and self.hybrid_candidate_k < rerank_floor:
                raise ValueError("hybrid_candidate_k must be greater than or equal to rerank_top_n")
        return self


class StartEvaluationResponse(BaseModel):
    job_id: str
    queue: str
    status: str
    retrieval_mode: str
    message: str


class EvaluationRunItem(BaseModel):
    id: UUID | str
    name: str
    dataset_id: UUID | str
    index_version_id: UUID | str | None
    status: str
    query_count: int
    failed_query_count: int
    recall_at_5: float | None
    recall_at_10: float | None
    mrr_at_10: float | None
    ndcg_at_10: float | None
    avg_latency_ms: float | None
    p50_latency_ms: float | None
    p95_latency_ms: float | None
    report_path: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class EvaluationRunListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[EvaluationRunItem]


class EvaluationRunDetail(EvaluationRunItem):
    config_json: dict[str, Any]
    notes: str | None


class EvaluationQueryResultItem(BaseModel):
    id: UUID | str
    evaluation_run_id: UUID | str
    benchmark_query_id: UUID | str | None
    query_external_id: str
    query_text: str
    recall_at_5: float | None
    recall_at_10: float | None
    mrr_at_10: float | None
    ndcg_at_10: float | None
    latency_ms: float | None
    trace_id: UUID | str | None
    error_message: str | None
    created_at: datetime


class EvaluationQueryResultListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[EvaluationQueryResultItem]


class EvaluationReportResponse(BaseModel):
    evaluation_run_id: UUID | str
    report_path: str | None
    report_format: str | None
    summary_json: dict[str, Any]
    report_json: dict[str, Any] | None = None
    warning: str | None = None
