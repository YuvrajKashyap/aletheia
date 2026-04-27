from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app

client = TestClient(app)


class FakeDb:
    pass


def fake_db():
    return FakeDb()


def fake_saved_query():
    return SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        name="SciFact q1",
        text="query",
        source="golden_scifact",
        dataset_id=UUID("00000000-0000-0000-0000-000000000002"),
        metadata_json={"query_external_id": "q1"},
        created_at=datetime.now(timezone.utc),
    )


def fake_replay():
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000010"),
        saved_query_id=UUID("00000000-0000-0000-0000-000000000001"),
        original_query_id=None,
        source_trace_id=None,
        target_trace_id=UUID("00000000-0000-0000-0000-000000000011"),
        experiment_config_id=None,
        index_version_id=None,
        status="completed",
        error_message=None,
        comparison_json={"ranked_document_ids": ["d1"]},
        created_at=now,
        started_at=now,
        completed_at=now,
    )


def test_get_saved_queries_read_only(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.replay.replay_service.list_saved_queries",
        lambda db, source=None, dataset_id=None, limit=50, offset=0: {
            "total": 1,
            "limit": limit,
            "offset": offset,
            "items": [fake_saved_query()],
        },
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/replay/saved-queries")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["items"][0]["source"] == "golden_scifact"


def test_post_saved_query_requires_admin() -> None:
    response = client.post("/api/v1/replay/saved-queries", json={"text": "query"})
    assert response.status_code == 401


def test_seed_golden_requires_admin() -> None:
    response = client.post("/api/v1/replay/saved-queries/seed-golden", json={})
    assert response.status_code == 401


def test_replay_saved_query_requires_admin() -> None:
    response = client.post(
        "/api/v1/replay/saved-queries/00000000-0000-0000-0000-000000000001/run",
        json={"retrieval_mode": "bm25"},
    )
    assert response.status_code == 401


def test_golden_run_requires_admin() -> None:
    response = client.post("/api/v1/replay/golden/run", json={"retrieval_mode": "bm25"})
    assert response.status_code == 401


def test_get_replay_runs_read_only(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.replay.replay_service.list_query_replays",
        lambda db, saved_query_id=None, status=None, limit=50, offset=0: {
            "total": 1,
            "limit": limit,
            "offset": offset,
            "items": [fake_replay()],
        },
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/replay/runs")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["items"][0]["status"] == "completed"


def test_get_replay_detail_read_only(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.replay.replay_service.get_query_replay",
        lambda db, query_replay_id: fake_replay(),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/replay/runs/00000000-0000-0000-0000-000000000010")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["comparison_json"]["ranked_document_ids"] == ["d1"]


def test_valid_admin_enqueues_replay_jobs(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.replay.job_queue.enqueue_saved_query_replay_job",
        lambda **kwargs: {
            "job_id": "job-1",
            "queue": "default",
            "status": "queued",
            "message": "Saved query replay job enqueued.",
        },
    )
    monkeypatch.setattr(
        "app.api.v1.routes.replay.job_queue.enqueue_golden_query_replay_job",
        lambda **kwargs: {
            "job_id": "job-2",
            "queue": "default",
            "status": "queued",
            "message": "Golden query replay job enqueued.",
        },
    )

    saved_response = client.post(
        "/api/v1/replay/saved-queries/00000000-0000-0000-0000-000000000001/run",
        json={"retrieval_mode": "bm25"},
        headers={"X-Admin-API-Key": "replace-me"},
    )
    golden_response = client.post(
        "/api/v1/replay/golden/run",
        json={"retrieval_mode": "bm25"},
        headers={"X-Admin-API-Key": "replace-me"},
    )

    assert saved_response.status_code == 200
    assert saved_response.json()["job_id"] == "job-1"
    assert golden_response.status_code == 200
    assert golden_response.json()["job_id"] == "job-2"
