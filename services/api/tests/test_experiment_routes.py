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


def fake_config(config_id: str = "00000000-0000-0000-0000-000000000001"):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=UUID(config_id),
        name="bm25_baseline",
        retrieval_mode="bm25",
        bm25_candidate_k=10,
        dense_candidate_k=0,
        hybrid_candidate_k=0,
        rerank_top_n=0,
        top_k_final=10,
        fusion_method=None,
        fusion_params_json={},
        embedding_model=None,
        reranker_model=None,
        config_json={},
        is_default=True,
        created_at=now,
        updated_at=now,
    )


def test_get_configs_does_not_require_admin(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.experiments.experiment_service.list_experiment_configs",
        lambda db, retrieval_mode=None, is_default=None, limit=50, offset=0: {
            "total": 1,
            "limit": limit,
            "offset": offset,
            "items": [fake_config()],
        },
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/experiments/configs")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["items"][0]["name"] == "bm25_baseline"


def test_post_config_requires_admin() -> None:
    response = client.post(
        "/api/v1/experiments/configs",
        json={"name": "bm25", "retrieval_mode": "bm25", "bm25_candidate_k": 10},
    )
    assert response.status_code == 401


def test_post_config_with_admin_creates(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.experiments.experiment_service.create_experiment_config",
        lambda db, **kwargs: fake_config(),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/experiments/configs",
            json={"name": "bm25", "retrieval_mode": "bm25", "bm25_candidate_k": 10},
            headers={"X-Admin-API-Key": "replace-me"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["retrieval_mode"] == "bm25"


def test_get_config_detail_read_only(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.experiments.experiment_service.get_experiment_config",
        lambda db, config_id: fake_config(str(config_id)),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/experiments/configs/00000000-0000-0000-0000-000000000001")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["config_json"] == {}


def test_patch_and_delete_require_admin() -> None:
    config_id = "00000000-0000-0000-0000-000000000001"
    assert client.patch(f"/api/v1/experiments/configs/{config_id}", json={"name": "new"}).status_code == 401
    assert client.delete(f"/api/v1/experiments/configs/{config_id}").status_code == 401


def test_seed_defaults_requires_admin() -> None:
    response = client.post("/api/v1/experiments/configs/seed-defaults")
    assert response.status_code == 401


def test_start_comparison_requires_admin() -> None:
    response = client.post("/api/v1/experiments/comparisons", json={"use_defaults": True})
    assert response.status_code == 401


def test_start_comparison_with_admin_enqueues(monkeypatch) -> None:
    calls = []

    def fake_enqueue(**kwargs):
        calls.append(kwargs)
        return {
            "job_id": "job-1",
            "queue": "default",
            "status": "queued",
            "message": "Evaluation comparison job enqueued.",
        }

    monkeypatch.setattr(
        "app.api.v1.routes.experiments.job_queue.enqueue_evaluation_comparison_job",
        fake_enqueue,
    )
    response = client.post(
        "/api/v1/experiments/comparisons",
        json={"use_defaults": True, "query_limit": 3},
        headers={"X-Admin-API-Key": "replace-me"},
    )

    assert response.status_code == 200
    assert response.json()["job_id"] == "job-1"
    assert calls[0]["use_defaults"] is True
    assert calls[0]["query_limit"] == 3
