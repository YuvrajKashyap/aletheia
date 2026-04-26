from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app

client = TestClient(app)


class FakeDb:
    def commit(self) -> None:
        pass


def fake_db():
    return FakeDb()


def fake_run(run_id: str = "00000000-0000-0000-0000-000000000001"):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=UUID(run_id),
        dataset_id=None,
        status="pending",
        started_at=None,
        completed_at=None,
        documents_loaded=0,
        chunks_created=0,
        queries_loaded=0,
        qrels_loaded=0,
        errors_count=0,
        config_json={"dataset": "beir/scifact"},
        error_message=None,
        created_at=now,
        updated_at=now,
    )


def test_start_scifact_ingestion_requires_admin_key(monkeypatch) -> None:
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post("/api/v1/ingestion/datasets/scifact", json={})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401


def test_start_scifact_ingestion_wrong_admin_key_fails(monkeypatch) -> None:
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/ingestion/datasets/scifact",
            json={},
            headers={"X-Admin-API-Key": "wrong"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_start_scifact_ingestion_enqueues_when_no_active_run(monkeypatch) -> None:
    run = fake_run()
    monkeypatch.setattr(
        "app.api.v1.routes.ingestion.ingestion_service.find_active_scifact_ingestion_run",
        lambda db: None,
    )
    monkeypatch.setattr(
        "app.api.v1.routes.ingestion.ingestion_service.create_ingestion_run",
        lambda db, status, config_json: run,
    )
    monkeypatch.setattr(
        "app.api.v1.routes.ingestion.job_queue.enqueue_scifact_ingestion_job",
        lambda **kwargs: {
            "job_id": "job-1",
            "queue": "default",
            "status": "queued",
            "ingestion_run_id": str(run.id),
            "message": "SciFact ingestion job enqueued.",
        },
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/ingestion/datasets/scifact",
            json={"document_limit": 1},
            headers={"X-Admin-API-Key": "replace-me"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["job_id"] == "job-1"
    assert response.json()["ingestion_run_id"] == str(run.id)


def test_start_scifact_ingestion_active_run_returns_409(monkeypatch) -> None:
    run = fake_run()
    monkeypatch.setattr(
        "app.api.v1.routes.ingestion.ingestion_service.find_active_scifact_ingestion_run",
        lambda db: run,
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/ingestion/datasets/scifact",
            json={},
            headers={"X-Admin-API-Key": "replace-me"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409


def test_list_ingestion_runs_route_exists(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.ingestion.ingestion_service.list_ingestion_runs",
        lambda db, status=None, limit=50, offset=0: ([fake_run()], 1),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/ingestion/runs")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["status"] == "pending"


def test_ingestion_run_detail_missing_returns_404(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.ingestion.ingestion_service.get_ingestion_run",
        lambda db, run_id: None,
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/ingestion/runs/00000000-0000-0000-0000-000000000001")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
