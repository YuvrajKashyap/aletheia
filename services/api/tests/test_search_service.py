from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

from app.models.queries import Query, QueryTrace, RetrievalCandidate
from app.schemas.search import SearchRequest
from app.search import service as search_service
from app.search.retrieval_models import (
    DenseSearchResponse,
    DenseSearchResult,
    LexicalSearchResponse,
    LexicalSearchResult,
)


class FakeSearchDb:
    def __init__(self):
        self.added = []
        self.commits = 0
        self.flushes = 0

    def add(self, value):
        if getattr(value, "id", None) is None:
            value.id = uuid4()
        self.added.append(value)

    def commit(self):
        self.commits += 1

    def refresh(self, value):
        if getattr(value, "id", None) is None:
            value.id = uuid4()

    def flush(self):
        self.flushes += 1
        for value in self.added:
            if getattr(value, "id", None) is None:
                value.id = uuid4()

    def rollback(self):
        return None

    def get(self, model, object_id):
        for value in self.added:
            if isinstance(value, model) and value.id == object_id:
                return value
        return None


def fake_lexical_response() -> LexicalSearchResponse:
    return LexicalSearchResponse(
        query="Do statins lower cholesterol?",
        index_version_id="00000000-0000-0000-0000-000000000001",
        index_name="aletheia-lexical-test",
        top_k=1,
        total_hits=5,
        results=[
            LexicalSearchResult(
                rank=1,
                chunk_id="00000000-0000-0000-0000-000000000002",
                document_id="00000000-0000-0000-0000-000000000003",
                dataset_id="00000000-0000-0000-0000-000000000004",
                document_external_id="doc-1",
                chunk_external_id="doc-1:0",
                title="Statin result",
                text="Statins lower cholesterol in many studies.",
                score=12.3,
                token_count=6,
                content_hash="hash",
                chunking_strategy="scifact_document_v1",
                chunking_version="1.0",
                metadata_json={"source_document_external_id": "doc-1"},
            )
        ],
        latency_ms=4.5,
    )


def fake_dense_response() -> DenseSearchResponse:
    return DenseSearchResponse(
        query="Do statins lower cholesterol?",
        index_version_id="00000000-0000-0000-0000-000000000001",
        collection_name="aletheia-vector-test",
        top_k=1,
        total_hits=4,
        query_embedding_dimension=384,
        results=[
            DenseSearchResult(
                rank=1,
                chunk_id="00000000-0000-0000-0000-000000000002",
                document_id="00000000-0000-0000-0000-000000000003",
                dataset_id="00000000-0000-0000-0000-000000000004",
                index_version_id="00000000-0000-0000-0000-000000000001",
                document_external_id="doc-1",
                chunk_external_id="doc-1:0",
                title="Dense statin result",
                text="Statins lower cholesterol in many semantic matches.",
                score=0.87,
                token_count=7,
                content_hash="hash",
                chunking_strategy="scifact_document_v1",
                chunking_version="1.0",
                metadata_json={"source_document_external_id": "doc-1"},
            )
        ],
        latency_ms=8.5,
        embedding_latency_ms=2.0,
        qdrant_latency_ms=3.0,
    )


def test_run_search_calls_bm25_and_persists_trace_skeleton(monkeypatch) -> None:
    calls = []

    def fake_search_bm25(db, query, index_version_id=None, top_k=10, candidate_k=None):
        calls.append(
            {
                "query": query,
                "index_version_id": index_version_id,
                "top_k": top_k,
                "candidate_k": candidate_k,
            }
        )
        return fake_lexical_response()

    monkeypatch.setattr(search_service, "search_bm25", fake_search_bm25)
    db = FakeSearchDb()
    request = SearchRequest(query="Do statins lower cholesterol?", top_k=1, candidate_k=3)

    response = search_service.run_search(db, request, request_id="request-1")

    assert calls == [
        {
            "query": "Do statins lower cholesterol?",
            "index_version_id": None,
            "top_k": 1,
            "candidate_k": 3,
        }
    ]
    assert response.retrieval_mode == "bm25"
    assert response.result_count == 1
    assert response.results[0].score_breakdown == {"bm25": 12.3}

    query_rows = [value for value in db.added if isinstance(value, Query)]
    trace_rows = [value for value in db.added if isinstance(value, QueryTrace)]
    candidate_rows = [value for value in db.added if isinstance(value, RetrievalCandidate)]

    assert len(query_rows) == 1
    assert query_rows[0].status == "completed"
    assert query_rows[0].request_id == "request-1"
    assert len(trace_rows) == 1
    assert trace_rows[0].trace_json["stages"]["bm25"]["index_name"] == "aletheia-lexical-test"
    assert trace_rows[0].trace_json["notes"]
    assert len(candidate_rows) == 1
    assert candidate_rows[0].source == "bm25"
    assert candidate_rows[0].bm25_rank == 1
    assert candidate_rows[0].final_rank == 1
    assert candidate_rows[0].bm25_score == 12.3
    assert candidate_rows[0].metadata_json["score_breakdown"] == {"bm25": 12.3}


def test_run_search_routes_dense_and_persists_dense_trace(monkeypatch) -> None:
    dense_calls = []

    def fake_search_dense(db, query, index_version_id=None, top_k=10, candidate_k=None):
        dense_calls.append(
            {
                "query": query,
                "index_version_id": index_version_id,
                "top_k": top_k,
                "candidate_k": candidate_k,
            }
        )
        return fake_dense_response()

    def fail_bm25(*args, **kwargs):
        raise AssertionError("BM25 should not be called for dense search")

    monkeypatch.setattr(search_service, "search_dense", fake_search_dense)
    monkeypatch.setattr(search_service, "search_bm25", fail_bm25)
    db = FakeSearchDb()
    request = SearchRequest(
        query="Do statins lower cholesterol?",
        retrieval_mode="dense",
        top_k=1,
        candidate_k=3,
    )

    response = search_service.run_search(db, request, request_id="request-2")

    assert dense_calls == [
        {
            "query": "Do statins lower cholesterol?",
            "index_version_id": None,
            "top_k": 1,
            "candidate_k": 3,
        }
    ]
    assert response.retrieval_mode == "dense"
    assert response.index_name is None
    assert response.collection_name == "aletheia-vector-test"
    assert response.embedding_latency_ms == 2.0
    assert response.qdrant_latency_ms == 3.0
    assert response.results[0].score_breakdown == {"dense": 0.87}

    trace_rows = [value for value in db.added if isinstance(value, QueryTrace)]
    candidate_rows = [value for value in db.added if isinstance(value, RetrievalCandidate)]

    assert trace_rows[0].trace_json["stages"]["dense"]["collection_name"] == "aletheia-vector-test"
    assert trace_rows[0].trace_json["stages"]["dense"]["query_embedding_dimension"] == 384
    assert "hybrid" not in trace_rows[0].trace_json["stages"]
    assert candidate_rows[0].source == "dense"
    assert candidate_rows[0].dense_rank == 1
    assert candidate_rows[0].final_rank == 1
    assert candidate_rows[0].dense_score == 0.87
    assert candidate_rows[0].bm25_rank is None
    assert candidate_rows[0].bm25_score is None
    assert candidate_rows[0].metadata_json["score_breakdown"] == {"dense": 0.87}
    assert candidate_rows[0].metadata_json["collection_name"] == "aletheia-vector-test"


def test_trace_json_helper_contains_bm25_stage() -> None:
    request = SearchRequest(query="statins", top_k=5)

    payload = search_service._trace_json(
        request=request,
        index_name="index-name",
        index_version_id="version-id",
        candidate_k=5,
        bm25_latency_ms=3.2,
        result_count=2,
    )

    assert payload["retrieval_mode"] == "bm25"
    assert payload["stages"]["bm25"] == {
        "latency_ms": 3.2,
        "result_count": 2,
        "index_name": "index-name",
    }
    assert "Dense, hybrid, and reranker stages are not implemented yet" in payload["notes"][0]


def test_candidate_metadata_includes_bm25_score_breakdown() -> None:
    result = fake_lexical_response().results[0]

    metadata = search_service._candidate_metadata(result)

    assert metadata["document_external_id"] == "doc-1"
    assert metadata["chunk_external_id"] == "doc-1:0"
    assert metadata["title"] == "Statin result"
    assert metadata["score_breakdown"] == {"bm25": 12.3}


def test_list_query_traces_response_shape() -> None:
    now = datetime(2026, 4, 25, tzinfo=timezone.utc)
    trace_id = UUID("00000000-0000-0000-0000-000000000010")
    query_id = UUID("00000000-0000-0000-0000-000000000011")
    trace = SimpleNamespace(id=trace_id, query_id=query_id, created_at=now)
    query = SimpleNamespace(
        id=query_id,
        text="statins",
        retrieval_mode="bm25",
        status="completed",
        total_latency_ms=5.0,
    )

    class FakeRowsDb:
        def scalar(self, statement):
            return 1

        def execute(self, statement):
            return SimpleNamespace(all=lambda: [(trace, query)])

    response = search_service.list_query_traces(FakeRowsDb(), limit=10, offset=0)

    assert response.total == 1
    assert response.items[0].query_text == "statins"
