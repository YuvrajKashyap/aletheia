import json

from app.cli import run_comparison


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_run_comparison_cli_passes_args(monkeypatch, capsys) -> None:
    calls = []

    def fake_runner(db, **kwargs):
        calls.append(kwargs)
        return {
            "comparison_name": kwargs["name"],
            "evaluation_run_ids": ["run-1"],
            "rows": [],
            "best_by_metric": {},
            "report_path": "reports/evaluations/comparisons/comparison_test.json",
        }

    monkeypatch.setattr(run_comparison, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(run_comparison, "run_evaluation_comparison", fake_runner)
    monkeypatch.setattr(
        "sys.argv",
        [
            "run_comparison.py",
            "--use-defaults",
            "--query-limit",
            "3",
            "--name",
            "Step 26 comparison",
        ],
    )

    assert run_comparison.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["comparison_name"] == "Step 26 comparison"
    assert calls[0]["use_defaults"] is True
    assert calls[0]["query_limit"] == 3


def test_run_comparison_cli_returns_nonzero_on_error(monkeypatch, capsys) -> None:
    monkeypatch.setattr(run_comparison, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(
        run_comparison,
        "run_evaluation_comparison",
        lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("comparison failed")),
    )
    monkeypatch.setattr("sys.argv", ["run_comparison.py", "--use-defaults"])

    assert run_comparison.main() == 1
    payload = json.loads(capsys.readouterr().err)
    assert payload["status"] == "error"
