import json

from app.cli import evaluate_trace


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def _payload() -> dict:
    return {
        "trace_id": "00000000-0000-0000-0000-000000000001",
        "query_id": "00000000-0000-0000-0000-000000000002",
        "query_text": "query",
        "retrieval_mode": "hybrid_rerank",
        "benchmark_query_id": "00000000-0000-0000-0000-000000000003",
        "query_external_id": "q1",
        "metrics": {"recall_at_5": 1.0, "mrr_at_10": 1.0},
        "ranked_document_ids": ["d1"],
        "relevant_document_ids": ["d1"],
        "matched_relevant_document_ids": ["d1"],
        "missed_relevant_document_ids": [],
    }


def test_evaluate_trace_cli_json_output(monkeypatch, capsys) -> None:
    calls = []

    def fake_evaluate(db, **kwargs):
        calls.append(kwargs)
        return _payload()

    monkeypatch.setattr(evaluate_trace, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(evaluate_trace, "evaluate_trace_against_benchmark_query", fake_evaluate)
    monkeypatch.setattr(
        "sys.argv",
        [
            "evaluate_trace.py",
            "--trace-id",
            "00000000-0000-0000-0000-000000000001",
            "--query-external-id",
            "q1",
        ],
    )

    assert evaluate_trace.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["query_external_id"] == "q1"
    assert calls[0]["query_external_id"] == "q1"


def test_evaluate_trace_cli_text_output(monkeypatch, capsys) -> None:
    monkeypatch.setattr(evaluate_trace, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(
        evaluate_trace,
        "evaluate_trace_against_benchmark_query",
        lambda *args, **kwargs: _payload(),
    )
    monkeypatch.setattr(
        "sys.argv",
        [
            "evaluate_trace.py",
            "--trace-id",
            "00000000-0000-0000-0000-000000000001",
            "--query-external-id",
            "q1",
            "--text",
        ],
    )

    assert evaluate_trace.main() == 0
    assert "retrieval_mode: hybrid_rerank" in capsys.readouterr().out


def test_evaluate_trace_cli_returns_nonzero_on_resolution_error(monkeypatch, capsys) -> None:
    def fail(*args, **kwargs):
        raise LookupError("provide query_external_id")

    monkeypatch.setattr(evaluate_trace, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(evaluate_trace, "evaluate_trace_against_benchmark_query", fail)
    monkeypatch.setattr(
        "sys.argv",
        ["evaluate_trace.py", "--trace-id", "00000000-0000-0000-0000-000000000001"],
    )

    assert evaluate_trace.main() == 1
    payload = json.loads(capsys.readouterr().err)
    assert "query_external_id" in payload["error"]
