import pytest
from pydantic import ValidationError

from app.schemas.evaluations import StartEvaluationRequest


def test_valid_bm25_request() -> None:
    request = StartEvaluationRequest(retrieval_mode="bm25", top_k=10, candidate_k=10)
    assert request.retrieval_mode == "bm25"


def test_valid_dense_request() -> None:
    request = StartEvaluationRequest(retrieval_mode="dense", top_k=10, candidate_k=20)
    assert request.candidate_k == 20


def test_valid_hybrid_request() -> None:
    request = StartEvaluationRequest(
        retrieval_mode="hybrid",
        top_k=10,
        bm25_candidate_k=50,
        dense_candidate_k=50,
    )
    assert request.retrieval_mode == "hybrid"


def test_valid_hybrid_rerank_request() -> None:
    request = StartEvaluationRequest(
        retrieval_mode="hybrid_rerank",
        top_k=10,
        bm25_candidate_k=50,
        dense_candidate_k=50,
        hybrid_candidate_k=50,
        rerank_top_n=25,
    )
    assert request.rerank_top_n == 25


def test_invalid_mode_rejected() -> None:
    with pytest.raises(ValidationError):
        StartEvaluationRequest(retrieval_mode="hybrid_rerank_eval")


def test_candidate_constraints_rejected() -> None:
    with pytest.raises(ValidationError, match="candidate_k"):
        StartEvaluationRequest(retrieval_mode="bm25", top_k=10, candidate_k=5)
    with pytest.raises(ValidationError, match="bm25_candidate_k"):
        StartEvaluationRequest(retrieval_mode="hybrid", top_k=10, bm25_candidate_k=5)
    with pytest.raises(ValidationError, match="rerank_top_n"):
        StartEvaluationRequest(retrieval_mode="hybrid_rerank", top_k=10, rerank_top_n=5)
    with pytest.raises(ValidationError, match="hybrid_candidate_k"):
        StartEvaluationRequest(
            retrieval_mode="hybrid_rerank",
            top_k=10,
            hybrid_candidate_k=20,
            rerank_top_n=25,
        )


def test_bounds_rejected() -> None:
    with pytest.raises(ValidationError):
        StartEvaluationRequest(retrieval_mode="bm25", query_limit=0)
    with pytest.raises(ValidationError):
        StartEvaluationRequest(retrieval_mode="bm25", query_limit=301)
    with pytest.raises(ValidationError):
        StartEvaluationRequest(retrieval_mode="bm25", top_k=0)
    with pytest.raises(ValidationError):
        StartEvaluationRequest(retrieval_mode="bm25", query_offset=-1)
    with pytest.raises(ValidationError):
        StartEvaluationRequest(retrieval_mode="bm25", rrf_k=0)
