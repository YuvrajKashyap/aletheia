from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest

from app.models.queries import QueryReplay, SavedQuery
from app.replay import service


class FakeDb:
    def __init__(self):
        self.added = []
        self.commits = 0
        self.refreshed = []

    def add(self, value):
        if getattr(value, "id", None) is None:
            value.id = uuid4()
        self.added.append(value)

    def flush(self):
        for value in self.added:
            if getattr(value, "id", None) is None:
                value.id = uuid4()

    def commit(self):
        self.commits += 1

    def refresh(self, value):
        self.refreshed.append(value)

    def get(self, model, value):
        return None


def saved_query() -> SimpleNamespace:
    return SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        text="Do statins lower cholesterol?",
        metadata_json={
            "benchmark_query_id": "00000000-0000-0000-0000-000000000010",
            "query_external_id": "q1",
            "dataset_name": "beir/scifact",
            "dataset_version": "test",
        },
    )


def response() -> SimpleNamespace:
    return SimpleNamespace(
        query_id="00000000-0000-0000-0000-000000000020",
        trace_id="00000000-0000-0000-0000-000000000021",
        index_version_id="00000000-0000-0000-0000-000000000022",
        latency_ms=10.0,
        results=[SimpleNamespace(document_id="d1"), SimpleNamespace(document_id="d1")],
    )


def test_create_saved_query_validates_non_empty_text() -> None:
    with pytest.raises(ValueError):
        service.create_saved_query(FakeDb(), text=" ")


def test_run_saved_query_replay_calls_search_and_records_metrics(monkeypatch) -> None:
    db = FakeDb()
    calls = []
    monkeypatch.setattr(service, "get_saved_query", lambda db, saved_query_id: saved_query())

    def fake_search(db, request, request_id=None):
        calls.append({"request": request, "request_id": request_id})
        return response()

    monkeypatch.setattr(service, "run_search", fake_search)
    monkeypatch.setattr(
        service,
        "load_relevance_for_benchmark_query",
        lambda db, query_id: {"relevant_document_ids": ["d1"], "relevance_by_id": {"d1": 1}},
    )

    summary = service.run_saved_query_replay(db, str(saved_query().id), retrieval_mode="bm25")

    replay_rows = [item for item in db.added if isinstance(item, QueryReplay)]
    assert calls[0]["request"].query == "Do statins lower cholesterol?"
    assert calls[0]["request_id"].startswith("replay:")
    assert summary["status"] == "completed"
    assert summary["metrics"]["recall_at_10"] == 1.0
    assert replay_rows[0].comparison_json["ranked_document_ids"] == ["d1"]


def test_failed_replay_records_failed_status(monkeypatch) -> None:
    db = FakeDb()
    monkeypatch.setattr(service, "get_saved_query", lambda db, saved_query_id: saved_query())
    monkeypatch.setattr(
        service,
        "run_search",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("search failed")),
    )

    summary = service.run_saved_query_replay(db, str(saved_query().id), retrieval_mode="bm25")

    replay_rows = [item for item in db.added if isinstance(item, QueryReplay)]
    assert summary["status"] == "failed"
    assert replay_rows[0].status == "failed"
    assert replay_rows[0].error_message == "search failed"


def test_golden_replay_aggregates_metrics_and_failures(monkeypatch) -> None:
    queries = [SimpleNamespace(id="sq1"), SimpleNamespace(id="sq2")]
    monkeypatch.setattr(
        service,
        "list_saved_queries",
        lambda db, source=None, limit=50, offset=0: {"items": queries},
    )
    monkeypatch.setattr(
        service,
        "run_saved_query_replay",
        lambda db, saved_query_id, **kwargs: {
            "query_replay_id": saved_query_id,
            "status": "completed" if saved_query_id == "sq1" else "failed",
            "metrics": {
                "recall_at_5": 1.0,
                "recall_at_10": 1.0,
                "reciprocal_rank_at_10": 1.0,
                "mrr_at_10": 1.0,
                "ndcg_at_10": 1.0,
                "hit_at_5": 1.0,
                "hit_at_10": 1.0,
                "latency_ms": 5.0,
            }
            if saved_query_id == "sq1"
            else None,
        },
    )
    monkeypatch.setattr(service, "write_replay_report", lambda report, name: "reports/replays/test.json")

    summary = service.run_golden_query_replay(FakeDb(), name="test", retrieval_mode="bm25")

    assert summary["replay_count"] == 2
    assert summary["failed_replay_count"] == 1
    assert summary["aggregate_metrics"]["recall_at_10"] == 1.0
    assert summary["report_path"] == "reports/replays/test.json"


def test_seed_golden_avoids_duplicates(monkeypatch) -> None:
    db = FakeDb()
    benchmark_query = SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000010"),
        dataset_id=UUID("00000000-0000-0000-0000-000000000011"),
        external_id="q1",
        text="query",
        dataset=SimpleNamespace(name="beir/scifact", version="test"),
    )
    existing = SavedQuery(text="query", source="golden_scifact", metadata_json={})
    existing.id = uuid4()
    monkeypatch.setattr(service, "select_scifact_golden_queries", lambda *args, **kwargs: [benchmark_query])
    monkeypatch.setattr(service, "_existing_golden_query", lambda *args, **kwargs: existing)

    result = service.seed_golden_queries_from_scifact(db)

    assert result["created_count"] == 0
    assert result["existing_count"] == 1
    assert result["items"] == [existing]
