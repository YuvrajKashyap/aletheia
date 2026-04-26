from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app

client = TestClient(app)


def test_system_queue_returns_mocked_queue_info(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.system.job_queue.get_queue_status",
        lambda: {"queue": "default", "job_count": 3},
    )

    response = client.get("/api/v1/system/queue")

    assert response.status_code == 200
    assert response.json() == {"queue": "default", "job_count": 3}


def test_enqueue_test_job_missing_admin_key_returns_401(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.system.job_queue.enqueue_ping_job",
        lambda message: {"job_id": "job-123", "queue": "default", "status": "queued"},
    )

    response = client.post("/api/v1/system/jobs/test", json={"message": "hello"})

    assert response.status_code == 401


def test_enqueue_test_job_wrong_admin_key_returns_403(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.system.job_queue.enqueue_ping_job",
        lambda message: {"job_id": "job-123", "queue": "default", "status": "queued"},
    )

    response = client.post(
        "/api/v1/system/jobs/test",
        json={"message": "hello"},
        headers={"X-Admin-API-Key": "wrong"},
    )

    assert response.status_code == 403


def test_enqueue_test_job_returns_mocked_job_id_with_admin_key(monkeypatch) -> None:
    def fake_enqueue_ping_job(message: str) -> dict:
        return {"job_id": "job-123", "queue": "default", "status": "queued"}

    monkeypatch.setattr(
        "app.api.v1.routes.system.job_queue.enqueue_ping_job",
        fake_enqueue_ping_job,
    )

    response = client.post(
        "/api/v1/system/jobs/test",
        json={"message": "hello"},
        headers={"X-Admin-API-Key": "replace-me"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "job_id": "job-123",
        "queue": "default",
        "status": "queued",
    }


def test_job_status_returns_mocked_status(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.system.job_queue.get_job_status",
        lambda job_id: {
            "found": True,
            "job_id": job_id,
            "status": "finished",
            "result": {"status": "ok"},
            "error": None,
            "enqueued_at": None,
            "ended_at": None,
        },
    )

    response = client.get("/api/v1/system/jobs/job-123")

    assert response.status_code == 200
    assert response.json() == {
        "job_id": "job-123",
        "status": "finished",
        "result": {"status": "ok"},
        "error": None,
        "found": True,
    }


def test_missing_job_returns_404(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.system.job_queue.get_job_status",
        lambda job_id: {
            "found": False,
            "job_id": job_id,
            "status": None,
            "result": None,
            "error": None,
            "enqueued_at": None,
            "ended_at": None,
        },
    )

    response = client.get("/api/v1/system/jobs/missing-job")

    assert response.status_code == 404


def test_worker_heartbeat_endpoint_serializes_workers() -> None:
    class FakeWorker:
        worker_name = "worker-a"
        queue_name = "default"
        status = "running"
        current_job_id = None
        metadata_json = {"hostname": "test-host"}
        last_seen_at = datetime(2026, 4, 25, tzinfo=timezone.utc)
        updated_at = datetime(2026, 4, 25, tzinfo=timezone.utc)

    class FakeScalars:
        def all(self) -> list[FakeWorker]:
            return [FakeWorker()]

    class FakeDb:
        def scalars(self, statement) -> FakeScalars:
            return FakeScalars()

    app.dependency_overrides[get_db] = lambda: FakeDb()
    try:
        response = client.get("/api/v1/system/worker-heartbeats")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["workers"][0]["worker_name"] == "worker-a"
    assert payload["workers"][0]["metadata_json"] == {"hostname": "test-host"}


def test_opensearch_health_route_returns_mocked_status(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.system.check_opensearch_health",
        lambda: {
            "status": "healthy",
            "url": "http://localhost:9200",
            "cluster_name": "docker-cluster",
            "version": "2.19.3",
            "error": None,
        },
    )

    response = client.get("/api/v1/system/opensearch")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["version"] == "2.19.3"


def test_embedding_model_status_route_returns_mocked_status_without_admin(monkeypatch) -> None:
    def fake_status() -> dict:
        return {
            "model_name": "BAAI/bge-small-en-v1.5",
            "device": "cpu",
            "loaded": False,
            "embedding_dimension": 384,
            "cache_dir": "data/models",
            "error": None,
        }

    monkeypatch.setattr("app.api.v1.routes.system.get_embedding_model_status", fake_status)

    response = client.get("/api/v1/system/models/embedding")

    assert response.status_code == 200
    assert response.json() == {
        "model_name": "BAAI/bge-small-en-v1.5",
        "device": "cpu",
        "loaded": False,
        "embedding_dimension": 384,
        "cache_dir": "data/models",
        "error": None,
    }


def test_health_route_still_registered() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
