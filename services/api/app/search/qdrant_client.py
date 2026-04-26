from __future__ import annotations

from typing import Any

from qdrant_client import QdrantClient

from app.core.config import get_settings


def get_qdrant_client() -> QdrantClient:
    settings = get_settings()
    return QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
        timeout=settings.QDRANT_REQUEST_TIMEOUT_SECONDS,
    )


def check_qdrant_health() -> dict[str, Any]:
    settings = get_settings()
    try:
        client = get_qdrant_client()
        collections = client.get_collections()
        collection_items = getattr(collections, "collections", []) or []
        version = None
        try:
            telemetry = client.info()
            version = getattr(telemetry, "version", None) or (
                telemetry.get("version") if isinstance(telemetry, dict) else None
            )
        except Exception:
            version = None

        return {
            "status": "healthy",
            "url": settings.QDRANT_URL,
            "version": version,
            "collections_count": len(collection_items),
            "error": None,
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "url": settings.QDRANT_URL,
            "version": None,
            "collections_count": None,
            "error": str(exc),
        }
