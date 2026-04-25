from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "aletheia"
    assert payload["version"] == "0.1.0"
    assert payload["app_mode"] == "local"
    assert payload["request_id"]
    assert response.headers["X-Request-ID"] == payload["request_id"]


def test_health_preserves_custom_request_id() -> None:
    request_id = "test-request-id-123"

    response = client.get(
        "/api/v1/health",
        headers={"X-Request-ID": request_id},
    )

    assert response.status_code == 200
    assert response.json()["request_id"] == request_id
    assert response.headers["X-Request-ID"] == request_id


def test_root_returns_ok() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "aletheia-api",
        "status": "ok",
        "docs": "/api/docs",
    }
