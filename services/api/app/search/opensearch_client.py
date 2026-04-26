from __future__ import annotations

from typing import Any

from opensearchpy import OpenSearch

from app.core.config import get_settings


def get_opensearch_client() -> OpenSearch:
    settings = get_settings()
    auth = None
    if settings.OPENSEARCH_USERNAME and settings.OPENSEARCH_PASSWORD:
        auth = (settings.OPENSEARCH_USERNAME, settings.OPENSEARCH_PASSWORD)

    return OpenSearch(
        hosts=[settings.OPENSEARCH_URL],
        http_auth=auth,
        verify_certs=settings.OPENSEARCH_VERIFY_CERTS,
        timeout=settings.OPENSEARCH_REQUEST_TIMEOUT_SECONDS,
    )


def check_opensearch_health() -> dict[str, Any]:
    settings = get_settings()
    try:
        client = get_opensearch_client()
        info = client.info()
        health = client.cluster.health()
        return {
            "status": "healthy",
            "url": settings.OPENSEARCH_URL,
            "cluster_name": info.get("cluster_name") or health.get("cluster_name"),
            "version": (info.get("version") or {}).get("number"),
            "error": None,
        }
    except Exception as exc:
        return {
            "status": "unhealthy",
            "url": settings.OPENSEARCH_URL,
            "cluster_name": None,
            "version": None,
            "error": str(exc),
        }
