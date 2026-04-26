from datetime import datetime, timezone
from uuid import UUID

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app
from app.schemas.search import (
    SearchResponse,
    SearchResultItem,
    TraceDetailResponse,
    TraceListItem,
    TraceListResponse,
)

client = TestClient(app)


class FakeDb:
    pass


def fake_db():
    return FakeDb()


def fake_search_response() -> SearchResponse:
    return SearchResponse(
        query_id=UUID("00000000-0000-0000-0000-000000000001"),
        trace_id=UUID("00000000-0000-0000-0000-000000000002"),
        request_id="request-1",
        query="Do statins lower cholesterol?",
        retrieval_mode="bm25",
        index_version_id=UUID("00000000-0000-0000-0000-000000000003"),
        index_name="aletheia-lexical-test",
        top_k=1,
        candidate_k=1,
        latency_ms=5.0,
        result_count=1,
        results=[
            SearchResultItem(
                rank=1,
                chunk_id=UUID("00000000-0000-0000-0000-000000000004"),
                document_id=UUID("00000000-0000-0000-0000-000000000005"),
                dataset_id=UUID("00000000-0000-0000-0000-000000000006"),
                document_external_id="doc-1",
                chunk_external_id="doc-1:0",
                title="Statin result",
                text="Statins lower cholesterol.",
                score=12.3,
                score_breakdown={"bm25": 12.3},
                token_count=3,
                chunking_strategy="scifact_document_v1",
                chunking_version="1.0",
                metadata_json={},
            )
        ],
    )


def fake_dense_search_response() -> SearchResponse:
    return SearchResponse(
        query_id=UUID("00000000-0000-0000-0000-000000000001"),
        trace_id=UUID("00000000-0000-0000-0000-000000000002"),
        request_id="request-1",
        query="Do statins lower cholesterol?",
        retrieval_mode="dense",
        index_version_id=UUID("00000000-0000-0000-0000-000000000003"),
        index_name=None,
        collection_name="aletheia-vector-test",
        top_k=1,
        candidate_k=1,
        latency_ms=8.0,
        embedding_latency_ms=2.0,
        qdrant_latency_ms=3.0,
        result_count=1,
        results=[
            SearchResultItem(
                rank=1,
                chunk_id=UUID("00000000-0000-0000-0000-000000000004"),
                document_id=UUID("00000000-0000-0000-0000-000000000005"),
                dataset_id=UUID("00000000-0000-0000-0000-000000000006"),
                document_external_id="doc-1",
                chunk_external_id="doc-1:0",
                title="Dense statin result",
                text="Statins lower cholesterol.",
                score=0.87,
                score_breakdown={"dense": 0.87},
                token_count=3,
                chunking_strategy="scifact_document_v1",
                chunking_version="1.0",
                metadata_json={},
            )
        ],
    )


def test_search_post_works_without_admin_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.search.search_service.run_search",
        lambda db, request, request_id=None: fake_search_response(),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/search",
            json={"query": "Do statins lower cholesterol?", "top_k": 1},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["retrieval_mode"] == "bm25"
    assert payload["results"][0]["score_breakdown"] == {"bm25": 12.3}


def test_dense_search_post_works_without_admin_key(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.search.search_service.run_search",
        lambda db, request, request_id=None: fake_dense_search_response(),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.post(
            "/api/v1/search",
            json={
                "query": "Do statins lower cholesterol?",
                "retrieval_mode": "dense",
                "top_k": 1,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["retrieval_mode"] == "dense"
    assert payload["collection_name"] == "aletheia-vector-test"
    assert payload["results"][0]["score_breakdown"] == {"dense": 0.87}


def test_search_post_unsupported_retrieval_mode_returns_validation_error() -> None:
    response = client.post(
        "/api/v1/search",
        json={"query": "Do statins lower cholesterol?", "retrieval_mode": "hybrid"},
    )

    assert response.status_code == 422


def test_search_traces_list_works_without_admin_key(monkeypatch) -> None:
    now = datetime(2026, 4, 25, tzinfo=timezone.utc)
    monkeypatch.setattr(
        "app.api.v1.routes.search.search_service.list_query_traces",
        lambda db, limit=50, offset=0: TraceListResponse(
            total=1,
            limit=limit,
            offset=offset,
            items=[
                TraceListItem(
                    trace_id=UUID("00000000-0000-0000-0000-000000000002"),
                    query_id=UUID("00000000-0000-0000-0000-000000000001"),
                    query_text="statins",
                    retrieval_mode="bm25",
                    status="completed",
                    total_latency_ms=5.0,
                    created_at=now,
                )
            ],
        ),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/search/traces?limit=10&offset=0")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["items"][0]["retrieval_mode"] == "bm25"


def test_search_trace_detail_works_without_admin_key(monkeypatch) -> None:
    now = datetime(2026, 4, 25, tzinfo=timezone.utc)
    monkeypatch.setattr(
        "app.api.v1.routes.search.search_service.get_query_trace_detail",
        lambda db, trace_id: TraceDetailResponse(
            trace_id=trace_id,
            query_id=UUID("00000000-0000-0000-0000-000000000001"),
            query_text="statins",
            retrieval_mode="bm25",
            index_version_id=UUID("00000000-0000-0000-0000-000000000003"),
            status="completed",
            total_latency_ms=5.0,
            trace_json={"stages": {"bm25": {"result_count": 1}}},
            candidates=[],
            created_at=now,
        ),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/search/traces/00000000-0000-0000-0000-000000000002")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["trace_json"]["stages"]["bm25"]["result_count"] == 1


def test_missing_search_trace_returns_404(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.search.search_service.get_query_trace_detail",
        lambda db, trace_id: None,
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/search/traces/00000000-0000-0000-0000-000000000002")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
