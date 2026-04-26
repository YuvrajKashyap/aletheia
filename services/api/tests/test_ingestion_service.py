from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.ingestion import statuses
from app.ingestion.service import find_active_scifact_ingestion_run, run_scifact_ingestion


def test_ingestion_status_sets() -> None:
    assert statuses.PENDING == "pending"
    assert statuses.RUNNING == "running"
    assert statuses.COMPLETED == "completed"
    assert statuses.FAILED == "failed"
    assert statuses.CANCELLED == "cancelled"
    assert statuses.ACTIVE_STATUSES == {"pending", "running"}
    assert statuses.TERMINAL_STATUSES == {"completed", "failed", "cancelled"}


class FakeScalars:
    def __init__(self, items):
        self.items = items

    def all(self):
        return self.items


class FakeDb:
    def __init__(self, scalar_value=None, active_runs=None):
        self.scalar_value = scalar_value
        self.active_runs = active_runs or []
        self.added = []
        self.commits = 0

    def add(self, item) -> None:
        self.added.append(item)

    def commit(self) -> None:
        self.commits += 1

    def refresh(self, item) -> None:
        if getattr(item, "id", None) is None:
            item.id = uuid4()
        if getattr(item, "created_at", None) is None:
            item.created_at = datetime.now(timezone.utc)
        if getattr(item, "updated_at", None) is None:
            item.updated_at = datetime.now(timezone.utc)

    def scalar(self, statement):
        return self.scalar_value

    def scalars(self, statement):
        return FakeScalars(self.active_runs)


def test_active_run_guard_finds_scifact_run() -> None:
    run = SimpleNamespace(status="running", config_json={"dataset": "beir/scifact"})
    db = FakeDb(active_runs=[run])

    assert find_active_scifact_ingestion_run(db) is run


def test_active_run_guard_ignores_other_dataset() -> None:
    run = SimpleNamespace(status="running", config_json={"dataset": "other"})
    db = FakeDb(active_runs=[run])

    assert find_active_scifact_ingestion_run(db) is None


def test_run_scifact_ingestion_summary_with_mocked_loader_and_chunker(monkeypatch) -> None:
    dataset_id = uuid4()
    db = FakeDb(scalar_value=SimpleNamespace(id=dataset_id))

    monkeypatch.setattr(
        "app.ingestion.service.load_scifact_to_db",
        lambda *args, **kwargs: SimpleNamespace(
            documents_loaded=2,
            queries_loaded=3,
            qrels_loaded=4,
            qrels_skipped_missing_query=0,
            qrels_skipped_missing_document=0,
        ),
    )
    monkeypatch.setattr(
        "app.ingestion.service.chunk_dataset_documents",
        lambda *args, **kwargs: SimpleNamespace(
            chunks_created=1,
            chunks_existing=2,
            chunks_updated=3,
        ),
    )

    summary = run_scifact_ingestion(db, document_limit=2)

    assert summary["status"] == "completed"
    assert summary["dataset_id"] == str(dataset_id)
    assert summary["documents_loaded"] == 2
    assert summary["queries_loaded"] == 3
    assert summary["qrels_loaded"] == 4
    assert summary["chunks_created"] == 1
    assert summary["chunks_existing"] == 2
    assert summary["chunks_updated"] == 3


def test_run_scifact_ingestion_marks_failed_on_loader_error(monkeypatch) -> None:
    db = FakeDb()

    def fail_loader(*args, **kwargs):
        raise RuntimeError("loader failed")

    monkeypatch.setattr("app.ingestion.service.load_scifact_to_db", fail_loader)

    with pytest.raises(RuntimeError, match="loader failed"):
        run_scifact_ingestion(db)

    run = db.added[0]
    assert run.status == "failed"
    assert run.errors_count == 1
    assert run.error_message == "loader failed"
