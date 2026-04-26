from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

from app.models.queries import Query, QueryTrace, RetrievalCandidate
from app.schemas.search import SearchRequest
from app.search import service as search_service
from app.search.retrieval_models import LexicalSearchResponse, LexicalSearchResult


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
