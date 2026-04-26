from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from app.evaluation import runner
from app.models.evaluation import EvaluationQueryResult, EvaluationReport, EvaluationRun


class FakeDb:
    def __init__(self):
        self.added = []
        self.flushes = 0
        self.commits = 0
        self.refreshed = []

    def add(self, value):
        if getattr(value, "id", None) is None:
            value.id = uuid4()
        self.added.append(value)

    def flush(self):
        self.flushes += 1
        for value in self.added:
            if getattr(value, "id", None) is None:
                value.id = uuid4()

    def commit(self):
        self.commits += 1

    def refresh(self, value):
        self.refreshed.append(value)


def dataset() -> SimpleNamespace:
    return SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        name="beir/scifact",
        version="test",
    )


def index_version() -> SimpleNamespace:
    return SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        dataset_id=dataset().id,
    )


def benchmark_query(external_id: str = "q1") -> SimpleNamespace:
    return SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000003"),
        external_id=external_id,
        text="Do statins lower cholesterol?",
    )


def search_response() -> SimpleNamespace:
    return SimpleNamespace(
        trace_id="00000000-0000-0000-0000-000000000004",
        latency_ms=12.5,
        results=[
            SimpleNamespace(document_id="d1"),
            SimpleNamespace(document_id="d1"),
            SimpleNamespace(document_id="d2"),
        ],
    )


def patch_basics(monkeypatch, queries=None):
    monkeypatch.setattr(runner, "_get_dataset", lambda *args, **kwargs: dataset())
    monkeypatch.setattr(runner, "_resolve_index_version", lambda *args, **kwargs: index_version())
    monkeypatch.setattr(
        runner,
        "_load_benchmark_queries",
        lambda *args, **kwargs: queries if queries is not None else [benchmark_query()],
    )
    monkeypatch.setattr(runner, "write_evaluation_report", lambda report, run_id: f"reports/{run_id}.json")


def test_retrieval_mode_validation_rejects_unsupported_mode() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        runner.run_offline_evaluation(FakeDb(), name="bad", retrieval_mode="unsupported")


def test_runner_writes_rows_and_scores_document_ids(monkeypatch) -> None:
    patch_basics(monkeypatch)
    run_search_calls = []

    def fake_run_search(db, request, request_id=None):
        run_search_calls.append({"query": request.query, "request_id": request_id})
        return search_response()

    monkeypatch.setattr(runner, "run_search", fake_run_search)
    monkeypatch.setattr(
        runner,
        "load_relevance_for_benchmark_query",
        lambda db, query_id: {"relevant_document_ids": ["d2"], "relevance_by_id": {"d2": 1}},
    )
    db = FakeDb()

    summary = runner.run_offline_evaluation(
        db,
        name="BM25 limited",
        retrieval_mode="bm25",
        query_limit=1,
        top_k=10,
        candidate_k=10,
    )

    eval_runs = [item for item in db.added if isinstance(item, EvaluationRun)]
    query_results = [item for item in db.added if isinstance(item, EvaluationQueryResult)]
    reports = [item for item in db.added if isinstance(item, EvaluationReport)]

    assert summary["status"] == "completed"
    assert summary["query_count"] == 1
    assert summary["failed_query_count"] == 0
    assert run_search_calls[0]["query"] == "Do statins lower cholesterol?"
    assert run_search_calls[0]["request_id"].startswith(f"eval:{eval_runs[0].id}:q1")
    assert eval_runs[0].config_json["retrieval_mode"] == "bm25"
    assert eval_runs[0].config_json["candidate_k"] == 10
    assert query_results[0].retrieved_document_ids_json == ["d1", "d2"]
    assert query_results[0].relevant_document_ids_json == ["d2"]
    assert query_results[0].recall_at_5 == 1.0
    assert query_results[0].mrr_at_10 == 0.5
    assert query_results[0].trace_id == UUID("00000000-0000-0000-0000-000000000004")
    assert reports[0].report_format == "json"
    assert eval_runs[0].report_path.startswith("reports/")
    assert summary["latency_summary"]["avg_latency_ms"] == 12.5


def test_runner_continues_after_query_failure(monkeypatch) -> None:
    queries = [benchmark_query("q1"), benchmark_query("q2")]
    patch_basics(monkeypatch, queries=queries)

    def fake_run_search(db, request, request_id=None):
        if "q1" in request_id:
            raise RuntimeError("search failed")
        return search_response()

    monkeypatch.setattr(runner, "run_search", fake_run_search)
    monkeypatch.setattr(
        runner,
        "load_relevance_for_benchmark_query",
        lambda db, query_id: {"relevant_document_ids": ["d2"], "relevance_by_id": {"d2": 1}},
    )
    db = FakeDb()

    summary = runner.run_offline_evaluation(db, name="eval", retrieval_mode="bm25")

    query_results = [item for item in db.added if isinstance(item, EvaluationQueryResult)]
    assert summary["status"] == "completed"
    assert summary["query_count"] == 2
    assert summary["failed_query_count"] == 1
    assert query_results[0].error_message == "search failed"
    assert query_results[1].error_message is None


def test_runner_marks_run_failed_on_catastrophic_failure(monkeypatch) -> None:
    patch_basics(monkeypatch)
    monkeypatch.setattr(runner, "run_search", lambda *args, **kwargs: search_response())
    monkeypatch.setattr(
        runner,
        "load_relevance_for_benchmark_query",
        lambda db, query_id: {"relevant_document_ids": ["d2"], "relevance_by_id": {"d2": 1}},
    )
    monkeypatch.setattr(
        runner,
        "write_evaluation_report",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("report failed")),
    )
    db = FakeDb()

    with pytest.raises(RuntimeError, match="report failed"):
        runner.run_offline_evaluation(db, name="eval", retrieval_mode="bm25")

    eval_run = [item for item in db.added if isinstance(item, EvaluationRun)][0]
    assert eval_run.status == "failed"
    assert db.commits == 1
