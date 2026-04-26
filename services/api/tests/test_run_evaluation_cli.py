import json

from app.cli import run_evaluation


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_run_evaluation_cli_passes_args(monkeypatch, capsys) -> None:
    calls = []

    def fake_runner(db, **kwargs):
        calls.append(kwargs)
        return {
            "evaluation_run_id": "run-1",
            "name": kwargs["name"],
            "retrieval_mode": kwargs["retrieval_mode"],
            "status": "completed",
        }

    monkeypatch.setattr(run_evaluation, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(run_evaluation, "run_offline_evaluation", fake_runner)
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_evaluation.py",
            "--mode",
            "bm25",
            "--name",
            "BM25 test",
            "--query-limit",
            "3",
            "--top-k",
            "5",
            "--candidate-k",
            "10",
        ],
    )

    assert run_evaluation.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["evaluation_run_id"] == "run-1"
    assert calls[0]["retrieval_mode"] == "bm25"
    assert calls[0]["name"] == "BM25 test"
    assert calls[0]["query_limit"] == 3
    assert calls[0]["top_k"] == 5
    assert calls[0]["candidate_k"] == 10


def test_run_evaluation_cli_returns_nonzero_on_error(monkeypatch, capsys) -> None:
    def fail(*args, **kwargs):
        raise ValueError("evaluation failed")

    monkeypatch.setattr(run_evaluation, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(run_evaluation, "run_offline_evaluation", fail)
    monkeypatch.setattr("sys.argv", ["run_evaluation.py", "--mode", "bm25"])

    assert run_evaluation.main() == 1
    payload = json.loads(capsys.readouterr().err)
    assert payload["status"] == "error"

