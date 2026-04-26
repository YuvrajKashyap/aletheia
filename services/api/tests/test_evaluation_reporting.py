from app.evaluation import reporting


def test_report_directory_creation(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(reporting, "_repo_root", lambda: tmp_path)

    reports_dir = reporting.ensure_reports_dir()

    assert reports_dir == tmp_path / "reports" / "evaluations"
    assert reports_dir.is_dir()
    assert (reports_dir / ".gitkeep").is_file()


def test_report_write_and_load(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(reporting, "_repo_root", lambda: tmp_path)
    report = {"evaluation_run_id": "run-1", "aggregate_metrics": {"recall_at_5": 1.0}}

    report_path = reporting.write_evaluation_report(report, "run-1")
    loaded = reporting.load_evaluation_report(report_path)

    assert report_path == "reports\\evaluations\\evaluation_run-1.json" or report_path == (
        "reports/evaluations/evaluation_run-1.json"
    )
    assert loaded["evaluation_run_id"] == "run-1"
    assert (tmp_path / report_path).is_file()

