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
        SearchRequest(query="statins", retrieval_mode="dense")


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


def test_valid_search_request_defaults_to_bm25() -> None:
    request = SearchRequest(query="statins")

    assert request.retrieval_mode == "bm25"
    assert request.top_k == 10
    assert request.candidate_k is None
