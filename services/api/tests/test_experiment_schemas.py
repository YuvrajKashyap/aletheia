import pytest
from pydantic import ValidationError

from app.schemas.experiments import ExperimentConfigCreateRequest, StartComparisonRequest


def test_valid_defaultish_configs() -> None:
    assert ExperimentConfigCreateRequest(
        name="bm25_baseline",
        retrieval_mode="bm25",
        bm25_candidate_k=10,
        dense_candidate_k=0,
        hybrid_candidate_k=0,
        rerank_top_n=0,
        top_k_final=10,
    )
    assert ExperimentConfigCreateRequest(
        name="hybrid_rerank_default",
        retrieval_mode="hybrid_rerank",
        bm25_candidate_k=50,
        dense_candidate_k=50,
        hybrid_candidate_k=50,
        rerank_top_n=25,
        top_k_final=10,
    )


def test_invalid_retrieval_mode_rejected() -> None:
    with pytest.raises(ValidationError):
        ExperimentConfigCreateRequest(name="bad", retrieval_mode="future")


def test_invalid_candidate_constraints_rejected() -> None:
    with pytest.raises(ValidationError, match="bm25_candidate_k"):
        ExperimentConfigCreateRequest(
            name="bad",
            retrieval_mode="bm25",
            bm25_candidate_k=5,
            top_k_final=10,
        )
    with pytest.raises(ValidationError, match="hybrid_candidate_k"):
        ExperimentConfigCreateRequest(
            name="bad",
            retrieval_mode="hybrid_rerank",
            bm25_candidate_k=50,
            dense_candidate_k=50,
            hybrid_candidate_k=20,
            rerank_top_n=25,
            top_k_final=10,
        )


def test_comparison_request_validation() -> None:
    assert StartComparisonRequest(use_defaults=True, query_limit=10)
    assert StartComparisonRequest(experiment_config_names=["bm25_baseline"])
    with pytest.raises(ValidationError):
        StartComparisonRequest()


def test_comparison_bounds() -> None:
    with pytest.raises(ValidationError):
        StartComparisonRequest(use_defaults=True, query_limit=301)
    with pytest.raises(ValidationError):
        StartComparisonRequest(use_defaults=True, query_offset=-1)
