from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app

client = TestClient(app)


class EmptyScalars:
    def all(self) -> list:
        return []


class EmptyDb:
    def scalar(self, statement) -> int:
        return 0

    def scalars(self, statement) -> EmptyScalars:
        return EmptyScalars()

    def get(self, model, item_id):
        return None


def override_empty_db():
    return EmptyDb()


def test_datasets_route_returns_empty_list_with_mocked_db() -> None:
    app.dependency_overrides[get_db] = override_empty_db
    try:
        response = client.get("/api/v1/datasets")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == []


def test_documents_route_returns_paginated_empty_response_with_mocked_db() -> None:
    app.dependency_overrides[get_db] = override_empty_db
    try:
        response = client.get("/api/v1/documents?limit=5&offset=0")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"total": 0, "limit": 5, "offset": 0, "items": []}


def test_documents_limit_max_validation() -> None:
    response = client.get("/api/v1/documents?limit=201")

    assert response.status_code == 422


def test_benchmark_queries_route_returns_paginated_empty_response_with_mocked_db() -> None:
    app.dependency_overrides[get_db] = override_empty_db
    try:
        response = client.get("/api/v1/benchmark-queries?limit=5&offset=0")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"total": 0, "limit": 5, "offset": 0, "items": []}


def test_chunks_route_returns_paginated_empty_response_with_mocked_db() -> None:
    app.dependency_overrides[get_db] = override_empty_db
    try:
        response = client.get("/api/v1/chunks?limit=5&offset=0")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"total": 0, "limit": 5, "offset": 0, "items": []}


def test_chunks_limit_max_validation() -> None:
    response = client.get("/api/v1/chunks?limit=201")

    assert response.status_code == 422


def test_missing_chunk_detail_returns_404_with_mocked_db() -> None:
    app.dependency_overrides[get_db] = override_empty_db
    try:
        response = client.get("/api/v1/chunks/00000000-0000-0000-0000-000000000001")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404


def test_missing_dataset_stats_returns_404_with_mocked_db() -> None:
    app.dependency_overrides[get_db] = override_empty_db
    try:
        response = client.get("/api/v1/datasets/00000000-0000-0000-0000-000000000001/stats")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
