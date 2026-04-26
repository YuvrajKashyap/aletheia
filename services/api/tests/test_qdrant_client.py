from types import SimpleNamespace

from app.search import qdrant_client


def test_qdrant_health_handles_mocked_healthy_client(monkeypatch) -> None:
    class FakeClient:
        def get_collections(self):
            return SimpleNamespace(collections=[SimpleNamespace(name="one")])

        def info(self):
            return SimpleNamespace(version="1.13.0")

    monkeypatch.setattr(qdrant_client, "get_qdrant_client", lambda: FakeClient())

    result = qdrant_client.check_qdrant_health()

    assert result["status"] == "healthy"
    assert result["collections_count"] == 1
    assert result["version"] == "1.13.0"


def test_qdrant_health_handles_exception_as_unhealthy(monkeypatch) -> None:
    def fail():
        raise RuntimeError("qdrant unavailable")

    monkeypatch.setattr(qdrant_client, "get_qdrant_client", fail)

    result = qdrant_client.check_qdrant_health()

    assert result["status"] == "unhealthy"
    assert result["error"] == "qdrant unavailable"
