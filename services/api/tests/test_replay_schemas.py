import pytest
from pydantic import ValidationError

from app.schemas.replay import ReplaySavedQueryRequest, StartGoldenReplayRequest


def test_valid_replay_request_with_mode() -> None:
    request = ReplaySavedQueryRequest(retrieval_mode="bm25", top_k=10, candidate_k=10)
    assert request.retrieval_mode == "bm25"


def test_valid_replay_request_with_experiment_config() -> None:
    request = ReplaySavedQueryRequest(experiment_config_name="bm25_baseline")
    assert request.experiment_config_name == "bm25_baseline"


def test_invalid_request_missing_mode_and_config() -> None:
    with pytest.raises(ValidationError, match="retrieval_mode is required"):
        ReplaySavedQueryRequest()


def test_invalid_retrieval_mode_rejected() -> None:
    with pytest.raises(ValidationError):
        ReplaySavedQueryRequest(retrieval_mode="future")


def test_candidate_constraints_rejected() -> None:
    with pytest.raises(ValidationError, match="candidate_k"):
        ReplaySavedQueryRequest(retrieval_mode="bm25", top_k=10, candidate_k=5)
    with pytest.raises(ValidationError, match="hybrid_candidate_k"):
        ReplaySavedQueryRequest(
            retrieval_mode="hybrid_rerank",
            top_k=10,
            hybrid_candidate_k=20,
            rerank_top_n=25,
        )


def test_golden_replay_limit_bounds() -> None:
    assert StartGoldenReplayRequest(retrieval_mode="bm25", limit=300)
    with pytest.raises(ValidationError):
        StartGoldenReplayRequest(retrieval_mode="bm25", limit=301)
