from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_database_health_returns_healthy(monkeypatch) -> None:
    def fake_check_database_health() -> dict[str, str | None]:
        return {
            "status": "healthy",
            "database": "postgresql",
            "error": None,
        }

    monkeypatch.setattr(
        "app.api.v1.routes.health.db_health.check_database_health",
        fake_check_database_health,
    )

    response = client.get("/api/v1/health/db")

    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["database"] == "postgresql"
    assert payload["error"] is None
    assert payload["request_id"]
    assert response.headers["X-Request-ID"] == payload["request_id"]


def test_database_health_returns_unhealthy(monkeypatch) -> None:
    def fake_check_database_health() -> dict[str, str | None]:
        return {
            "status": "unhealthy",
            "database": "postgresql",
            "error": "connection failed",
        }

    monkeypatch.setattr(
        "app.api.v1.routes.health.db_health.check_database_health",
        fake_check_database_health,
    )

    response = client.get(
        "/api/v1/health/db",
        headers={"X-Request-ID": "db-test-request"},
    )

    assert response.status_code == 503

    payload = response.json()
    assert payload["status"] == "unhealthy"
    assert payload["database"] == "postgresql"
    assert payload["error"] == "connection failed"
    assert payload["request_id"] == "db-test-request"
    assert response.headers["X-Request-ID"] == "db-test-request"
