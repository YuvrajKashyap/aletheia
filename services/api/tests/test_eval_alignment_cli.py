import json

from app.cli import check_eval_alignment


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_check_eval_alignment_cli_success(monkeypatch, capsys) -> None:
    def fake_validator(db, dataset_name, dataset_version):
        return {
            "dataset_name": dataset_name,
            "dataset_version": dataset_version,
            "ready_for_evaluation": True,
        }

    monkeypatch.setattr(check_eval_alignment, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(check_eval_alignment, "validate_dataset_qrels_alignment", fake_validator)
    monkeypatch.setattr(
        "sys.argv",
        ["check_eval_alignment.py", "--dataset-name", "beir/scifact", "--dataset-version", "test"],
    )

    assert check_eval_alignment.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ready_for_evaluation"] is True


def test_check_eval_alignment_cli_returns_nonzero_when_not_ready(monkeypatch, capsys) -> None:
    monkeypatch.setattr(check_eval_alignment, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(
        check_eval_alignment,
        "validate_dataset_qrels_alignment",
        lambda *args, **kwargs: {"ready_for_evaluation": False},
    )
    monkeypatch.setattr("sys.argv", ["check_eval_alignment.py"])

    assert check_eval_alignment.main() == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["ready_for_evaluation"] is False


def test_check_eval_alignment_cli_returns_nonzero_on_error(monkeypatch, capsys) -> None:
    def fail(*args, **kwargs):
        raise LookupError("missing dataset")

    monkeypatch.setattr(check_eval_alignment, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(check_eval_alignment, "validate_dataset_qrels_alignment", fail)
    monkeypatch.setattr("sys.argv", ["check_eval_alignment.py"])

    assert check_eval_alignment.main() == 1
    payload = json.loads(capsys.readouterr().err)
    assert payload["status"] == "error"

