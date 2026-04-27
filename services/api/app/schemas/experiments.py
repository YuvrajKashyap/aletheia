from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


SUPPORTED_RETRIEVAL_MODES = {"bm25", "dense", "hybrid", "hybrid_rerank"}


def _validate_mode_values(
    retrieval_mode: str,
    top_k_final: int,
    bm25_candidate_k: int,
    dense_candidate_k: int,
    hybrid_candidate_k: int,
    rerank_top_n: int,
) -> None:
    if retrieval_mode not in SUPPORTED_RETRIEVAL_MODES:
        raise ValueError("retrieval_mode must be bm25, dense, hybrid, or hybrid_rerank")
    if retrieval_mode == "bm25" and bm25_candidate_k < top_k_final:
        raise ValueError("bm25_candidate_k must be greater than or equal to top_k_final")
    if retrieval_mode == "dense" and dense_candidate_k < top_k_final:
        raise ValueError("dense_candidate_k must be greater than or equal to top_k_final")
    if retrieval_mode == "hybrid":
        if bm25_candidate_k < top_k_final:
            raise ValueError("bm25_candidate_k must be greater than or equal to top_k_final")
        if dense_candidate_k < top_k_final:
            raise ValueError("dense_candidate_k must be greater than or equal to top_k_final")
    if retrieval_mode == "hybrid_rerank":
        if bm25_candidate_k < top_k_final:
            raise ValueError("bm25_candidate_k must be greater than or equal to top_k_final")
        if dense_candidate_k < top_k_final:
            raise ValueError("dense_candidate_k must be greater than or equal to top_k_final")
        if hybrid_candidate_k < top_k_final:
            raise ValueError("hybrid_candidate_k must be greater than or equal to top_k_final")
        if rerank_top_n < top_k_final:
            raise ValueError("rerank_top_n must be greater than or equal to top_k_final")
        if hybrid_candidate_k < rerank_top_n:
            raise ValueError("hybrid_candidate_k must be greater than or equal to rerank_top_n")


class ExperimentConfigCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    retrieval_mode: str
    bm25_candidate_k: int = Field(default=50, ge=0, le=500)
    dense_candidate_k: int = Field(default=50, ge=0, le=500)
    hybrid_candidate_k: int = Field(default=50, ge=0, le=500)
    rerank_top_n: int = Field(default=25, ge=0, le=500)
    top_k_final: int = Field(default=10, ge=1, le=100)
    fusion_method: str | None = None
    fusion_params_json: dict[str, Any] | None = None
    embedding_model: str | None = None
    reranker_model: str | None = None
    config_json: dict[str, Any] | None = None
    is_default: bool = False

    @field_validator("retrieval_mode")
    @classmethod
    def retrieval_mode_supported(cls, value: str) -> str:
        if value not in SUPPORTED_RETRIEVAL_MODES:
            raise ValueError("retrieval_mode must be bm25, dense, hybrid, or hybrid_rerank")
        return value

    @model_validator(mode="after")
    def validate_candidate_depths(self) -> "ExperimentConfigCreateRequest":
        _validate_mode_values(
            self.retrieval_mode,
            self.top_k_final,
            self.bm25_candidate_k,
            self.dense_candidate_k,
            self.hybrid_candidate_k,
            self.rerank_top_n,
        )
        return self


class ExperimentConfigUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    retrieval_mode: str | None = None
    bm25_candidate_k: int | None = Field(default=None, ge=0, le=500)
    dense_candidate_k: int | None = Field(default=None, ge=0, le=500)
    hybrid_candidate_k: int | None = Field(default=None, ge=0, le=500)
    rerank_top_n: int | None = Field(default=None, ge=0, le=500)
    top_k_final: int | None = Field(default=None, ge=1, le=100)
    fusion_method: str | None = None
    fusion_params_json: dict[str, Any] | None = None
    embedding_model: str | None = None
    reranker_model: str | None = None
    config_json: dict[str, Any] | None = None
    is_default: bool | None = None

    @field_validator("retrieval_mode")
    @classmethod
    def retrieval_mode_supported(cls, value: str | None) -> str | None:
        if value is not None and value not in SUPPORTED_RETRIEVAL_MODES:
            raise ValueError("retrieval_mode must be bm25, dense, hybrid, or hybrid_rerank")
        return value


class ExperimentConfigItem(BaseModel):
    id: UUID | str
    name: str
    retrieval_mode: str
    bm25_candidate_k: int
    dense_candidate_k: int
    hybrid_candidate_k: int
    rerank_top_n: int
    top_k_final: int
    fusion_method: str | None
    fusion_params_json: dict[str, Any]
    embedding_model: str | None
    reranker_model: str | None
    is_default: bool
    created_at: datetime
    updated_at: datetime | None = None


class ExperimentConfigDetail(ExperimentConfigItem):
    config_json: dict[str, Any]


class ExperimentConfigListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[ExperimentConfigItem]


class SeedExperimentConfigsResponse(BaseModel):
    created_count: int
    updated_count: int
    existing_count: int
    configs: list[ExperimentConfigItem]


class StartComparisonRequest(BaseModel):
    name: str | None = None
    use_defaults: bool = False
    experiment_config_ids: list[UUID] | None = None
    experiment_config_names: list[str] | None = None
    dataset_name: str = "beir/scifact"
    dataset_version: str = "test"
    index_version_id: UUID | None = None
    query_limit: int | None = Field(default=None, ge=1, le=300)
    query_offset: int = Field(default=0, ge=0)
    notes: str | None = None

    @model_validator(mode="after")
    def validate_config_selection(self) -> "StartComparisonRequest":
        if not self.use_defaults and not self.experiment_config_ids and not self.experiment_config_names:
            raise ValueError(
                "use_defaults must be true or at least one experiment config id/name is required"
            )
        return self


class StartComparisonResponse(BaseModel):
    job_id: str
    queue: str
    status: str
    message: str
