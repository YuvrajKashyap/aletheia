from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import app

client = TestClient(app)


def clear_overrides() -> None:
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_admin_status_missing_key_returns_401() -> None:
    clear_overrides()

    response = client.get("/api/v1/admin/status")

    assert response.status_code == 401


def test_admin_status_wrong_key_returns_403() -> None:
    clear_overrides()

    response = client.get(
        "/api/v1/admin/status",
        headers={"X-Admin-API-Key": "wrong"},
    )

    assert response.status_code == 403


def test_admin_status_accepts_x_admin_api_key() -> None:
    clear_overrides()

    response = client.get(
        "/api/v1/admin/status",
        headers={"X-Admin-API-Key": "replace-me"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["app_mode"] == "local"
    assert payload["admin_protection_enabled"] is True
    assert "replace-me" not in response.text


def test_admin_status_accepts_authorization_bearer_key() -> None:
    clear_overrides()

    response = client.get(
        "/api/v1/admin/status",
        headers={"Authorization": "Bearer replace-me"},
    )

    assert response.status_code == 200
    assert "replace-me" not in response.text


def test_public_mode_with_default_key_is_rejected_safely() -> None:
    clear_overrides()
    app.dependency_overrides[get_settings] = lambda: Settings(
        APP_MODE="demo",
        ADMIN_API_KEY="replace-me",
    )
    try:
        response = client.get(
            "/api/v1/admin/status",
            headers={"X-Admin-API-Key": "replace-me"},
        )
    finally:
        clear_overrides()

    assert response.status_code == 500
    assert "replace-me" not in response.text
