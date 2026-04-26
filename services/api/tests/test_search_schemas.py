import pytest
from pydantic import ValidationError

from app.schemas.search import SearchRequest


def test_empty_query_rejected() -> None:
    with pytest.raises(ValidationError):
        SearchRequest(query="")


def test_whitespace_query_rejected() -> None:
    with pytest.raises(ValidationError):
        SearchRequest(query="   ")


def test_unsupported_retrieval_mode_rejected() -> None:
    with pytest.raises(ValidationError):
        SearchRequest(query="statins", retrieval_mode="hybrid_rerank")


def test_dense_retrieval_mode_accepted() -> None:
    request = SearchRequest(query="statins", retrieval_mode="dense")

    assert request.retrieval_mode == "dense"


def test_hybrid_retrieval_mode_accepted_and_defaults_candidates() -> None:
    request = SearchRequest(query="statins", retrieval_mode="hybrid", top_k=5)

    assert request.retrieval_mode == "hybrid"
    assert request.bm25_candidate_k == 50
    assert request.dense_candidate_k == 50
    assert request.rrf_k == 60


def test_top_k_lower_bound() -> None:
    with pytest.raises(ValidationError):
        SearchRequest(query="statins", top_k=0)


def test_top_k_upper_bound() -> None:
    with pytest.raises(ValidationError):
        SearchRequest(query="statins", top_k=101)


def test_candidate_k_lower_bound() -> None:
    with pytest.raises(ValidationError):
        SearchRequest(query="statins", candidate_k=0)


def test_candidate_k_must_be_greater_than_or_equal_to_top_k() -> None:
    with pytest.raises(ValidationError):
        SearchRequest(query="statins", top_k=10, candidate_k=5)


def test_hybrid_candidate_counts_must_cover_top_k() -> None:
    with pytest.raises(ValidationError):
        SearchRequest(query="statins", retrieval_mode="hybrid", top_k=10, bm25_candidate_k=5)
    with pytest.raises(ValidationError):
        SearchRequest(query="statins", retrieval_mode="hybrid", top_k=10, dense_candidate_k=5)


def test_rrf_k_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        SearchRequest(query="statins", retrieval_mode="hybrid", rrf_k=0)


def test_valid_search_request_defaults_to_bm25() -> None:
    request = SearchRequest(query="statins")

    assert request.retrieval_mode == "bm25"
    assert request.top_k == 10
    assert request.candidate_k is None
