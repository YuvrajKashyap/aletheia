from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from app.evaluation import correctness


def test_normalize_id_handles_uuid_string_none_and_empty() -> None:
    value = uuid4()
    assert correctness.normalize_id(value) == str(value)
    assert correctness.normalize_id("  abc  ") == "abc"
    assert correctness.normalize_id(None) == ""
    assert correctness.normalize_id("   ") == ""


def test_deduplicate_ranked_document_ids_preserves_order_and_ignores_empty() -> None:
    assert correctness.deduplicate_ranked_document_ids(["d1", "d2", "d1", None, "", "d3"]) == [
        "d1",
        "d2",
        "d3",
    ]


def test_candidate_rows_to_ranked_document_ids_sorts_by_final_rank_and_dedupes() -> None:
    candidates = [
        SimpleNamespace(document_id="d2", final_rank=2),
        SimpleNamespace(document_id="d1", final_rank=1),
        SimpleNamespace(document_id="d1", final_rank=3),
        SimpleNamespace(document_id="", final_rank=4),
        SimpleNamespace(document_id="d4", final_rank=None),
    ]

    assert correctness.candidate_rows_to_ranked_document_ids(candidates) == ["d1", "d2", "d4"]


def test_candidate_rows_to_ranked_document_ids_preserves_order_when_rank_missing() -> None:
    candidates = [
        SimpleNamespace(document_id="d3", final_rank=None),
        SimpleNamespace(document_id="d2", final_rank=None),
        SimpleNamespace(document_id="d3", final_rank=None),
    ]

    assert correctness.candidate_rows_to_ranked_document_ids(candidates) == ["d3", "d2"]


def test_search_results_to_ranked_document_ids_supports_dicts_and_objects() -> None:
    results = [
        {"document_id": "d1"},
        SimpleNamespace(document_id="d2"),
        {"document_id": "d1"},
        SimpleNamespace(document_id=None),
    ]

    assert correctness.search_results_to_ranked_document_ids(results) == ["d1", "d2"]


def test_evaluate_ranked_documents_for_query_scores_document_ids_and_matches() -> None:
    payload = {
        "relevant_document_ids": ["d2", "d4"],
        "relevance_by_id": {"d2": 1, "d4": 1},
    }

    result = correctness.evaluate_ranked_documents_for_query(
        ranked_document_ids=["d1", "d1", "d2", "d3"],
        relevance_payload=payload,
        latency_ms=12.5,
    )

    assert result["recall_at_5"] == 0.5
    assert result["recall_at_10"] == 0.5
    assert result["reciprocal_rank_at_10"] == 0.5
    assert result["mrr_at_10"] == result["reciprocal_rank_at_10"]
    assert result["hit_at_5"] == 1.0
    assert result["hit_at_10"] == 1.0
    assert result["retrieved_count"] == 3
    assert result["relevant_count"] == 2
    assert result["latency_ms"] == 12.5
    assert result["ranked_document_ids"] == ["d1", "d2", "d3"]
    assert result["matched_relevant_document_ids"] == ["d2"]
    assert result["missed_relevant_document_ids"] == ["d4"]


def test_find_benchmark_query_by_exact_text_uses_stripped_exact_match(monkeypatch) -> None:
    dataset = SimpleNamespace(id=UUID("00000000-0000-0000-0000-000000000001"))
    benchmark_query = SimpleNamespace(id=uuid4(), text="exact query")
    calls = []

    class FakeDb:
        def scalar(self, statement):
            calls.append(statement)
            return dataset if len(calls) == 1 else benchmark_query

    result = correctness.find_benchmark_query_by_exact_text(
        FakeDb(),
        dataset_name="beir/scifact",
        dataset_version="test",
        query_text="  exact query  ",
    )

    assert result is benchmark_query
    assert len(calls) == 2


def test_find_benchmark_query_by_exact_text_returns_none_when_dataset_missing() -> None:
    class FakeDb:
        def scalar(self, statement):
            return None

    assert (
        correctness.find_benchmark_query_by_exact_text(
            FakeDb(),
            dataset_name="missing",
            dataset_version="test",
            query_text="query",
        )
        is None
    )


def test_evaluate_trace_requires_resolvable_benchmark_query(monkeypatch) -> None:
    trace = SimpleNamespace(id=uuid4(), query_id=uuid4())
    query = SimpleNamespace(
        id=trace.query_id,
        text="not benchmark",
        retrieval_mode="bm25",
        total_latency_ms=5.0,
    )

    class FakeScalars:
        def all(self):
            return []

    class FakeDb:
        def get(self, model, object_id):
            if model.__name__ == "QueryTrace":
                return trace
            if model.__name__ == "Query":
                return query
            return None

        def scalars(self, statement):
            return FakeScalars()

    monkeypatch.setattr(correctness, "find_benchmark_query_by_exact_text", lambda *args, **kwargs: None)

    with pytest.raises(LookupError, match="query_external_id"):
        correctness.evaluate_trace_against_benchmark_query(FakeDb(), trace.id)
