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


def fake_index_version(index_id: str = "00000000-0000-0000-0000-000000000001"):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=UUID(index_id),
        dataset_id=UUID("00000000-0000-0000-0000-000000000002"),
        name="beir-scifact-test-scifact-document-v1-1-0",
        status="ready",
        is_active=False,
        lexical_index_name="aletheia-lexical-beir-scifact",
        vector_collection_name="aletheia-vector-beir-scifact",
        embedding_model="BAAI/bge-small-en-v1.5",
        embedding_dimension=None,
        chunking_strategy="scifact_document_v1",
        chunking_version="1.0",
        document_count=5183,
        chunk_count=5183,
        vector_count=0,
        config_json={"metadata_only": True},
        notes=None,
        created_at=now,
        updated_at=now,
        activated_at=None,
    )


def test_index_status_route_exists(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.indexes.index_service.index_status",
        lambda db: {
            "active_index_version": None,
            "dataset_count": 1,
            "index_version_count": 0,
            "ready_index_version_count": 0,
            "active_index_version_count": 0,
            "latest_index_versions": [],
        },
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/indexes/status")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["dataset_count"] == 1


def test_index_versions_route_exists(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.indexes.index_service.list_index_versions",
        lambda db, dataset_id=None, status=None, limit=50, offset=0: ([fake_index_version()], 1),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/indexes/versions")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["status"] == "ready"


def test_index_version_detail_missing_returns_404(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.indexes.index_service.get_index_version",
        lambda db, index_version_id: None,
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/indexes/versions/00000000-0000-0000-0000-000000000001")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404


def test_create_index_version_requires_admin_key() -> None:
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post("/api/v1/indexes/versions", json={})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401


def test_create_index_version_wrong_admin_key_fails() -> None:
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/indexes/versions",
            json={},
            headers={"X-Admin-API-Key": "wrong"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_create_index_version_with_admin_key_returns_created_shape(monkeypatch) -> None:
    dataset = SimpleNamespace(id=UUID("00000000-0000-0000-0000-000000000002"))
    monkeypatch.setattr(
        "app.api.v1.routes.indexes.index_service.get_dataset_by_name_version",
        lambda db, dataset_name, dataset_version: dataset,
    )
    monkeypatch.setattr(
        "app.api.v1.routes.indexes.index_service.create_index_version",
        lambda *args, **kwargs: fake_index_version(),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/indexes/versions",
            json={},
            headers={"X-Admin-API-Key": "replace-me"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["name"] == "beir-scifact-test-scifact-document-v1-1-0"
    assert response.json()["status"] == "ready"
    assert response.json()["is_active"] is False


def test_activation_endpoint_requires_admin_key() -> None:
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/indexes/versions/00000000-0000-0000-0000-000000000001/activate"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401


def test_activation_endpoint_with_admin_key_returns_response(monkeypatch) -> None:
    active = fake_index_version()
    active.status = "active"
    active.is_active = True
    monkeypatch.setattr(
        "app.api.v1.routes.indexes.index_service.activate_index_version",
        lambda db, index_version_id: active,
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/indexes/versions/00000000-0000-0000-0000-000000000001/activate",
            headers={"X-Admin-API-Key": "replace-me"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["index_version"]["is_active"] is True
    assert response.json()["message"] == "metadata-only index version activated."


def test_build_lexical_endpoint_requires_admin_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.indexes.index_service.get_index_version",
        lambda db, index_version_id: fake_index_version(str(index_version_id)),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/indexes/versions/00000000-0000-0000-0000-000000000001/build-lexical",
            json={},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401


def test_build_lexical_endpoint_wrong_admin_key_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.indexes.index_service.get_index_version",
        lambda db, index_version_id: fake_index_version(str(index_version_id)),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/indexes/versions/00000000-0000-0000-0000-000000000001/build-lexical",
            json={},
            headers={"X-Admin-API-Key": "wrong"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 403


def test_build_lexical_endpoint_enqueues_job_without_opensearch(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.indexes.index_service.get_index_version",
        lambda db, index_version_id: fake_index_version(str(index_version_id)),
    )
    monkeypatch.setattr(
        "app.api.v1.routes.indexes.job_queue.enqueue_lexical_index_build_job",
        lambda index_version_id, recreate=False, limit=None, refresh=True: {
            "job_id": "job-lexical-123",
            "queue": "default",
            "status": "queued",
            "index_version_id": index_version_id,
            "message": "Lexical index build job enqueued.",
        },
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/indexes/versions/00000000-0000-0000-0000-000000000001/build-lexical",
            json={"recreate": True, "limit": 10, "refresh": False},
            headers={"X-Admin-API-Key": "replace-me"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["job_id"] == "job-lexical-123"
    assert response.json()["index_version_id"] == "00000000-0000-0000-0000-000000000001"
