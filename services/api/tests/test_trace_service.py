from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

from app.search import trace_service


TRACE_ID = UUID("00000000-0000-0000-0000-000000000001")
QUERY_ID = UUID("00000000-0000-0000-0000-000000000002")


class FakeCandidate:
    id = UUID("00000000-0000-0000-0000-000000000003")
    source = "hybrid_rerank"
    final_rank = 1
    bm25_rank = 2
    dense_rank = 3
    fusion_rank = 2
    rerank_rank = 1
    bm25_score = 10.0
    dense_score = 0.8
    fusion_score = 0.03
    reranker_score = 9.0
    chunk_id = UUID("00000000-0000-0000-0000-000000000004")
    document_id = UUID("00000000-0000-0000-0000-000000000005")
    metadata_json = {"title": "Result"}
    created_at = datetime(2026, 4, 26, tzinfo=timezone.utc)


class FakeScalars:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class FakeDb:
    def __init__(self):
        self.trace = SimpleNamespace(
            id=TRACE_ID,
            query_id=QUERY_ID,
            created_at=datetime(2026, 4, 26, tzinfo=timezone.utc),
            trace_json={
                "trace_schema_version": "search_trace_v1",
                "ranking_summary": {"result_count": 1},
            },
        )
        self.query = SimpleNamespace(
            id=QUERY_ID,
            text="statins",
            retrieval_mode="hybrid_rerank",
            status="completed",
            total_latency_ms=12.0,
            index_version_id=None,
        )

    def scalar(self, statement):
        return 1

    def execute(self, statement):
        return SimpleNamespace(all=lambda: [(self.trace, self.query)], first=lambda: (self.trace, self.query))

    def get(self, model, object_id):
        return self.trace if object_id == TRACE_ID else None

    def scalars(self, statement):
        return FakeScalars([FakeCandidate()])


def test_list_traces_accepts_filters_and_returns_shape() -> None:
    response = trace_service.list_query_traces(
        FakeDb(),
        retrieval_mode="hybrid_rerank",
        status="completed",
        limit=10,
        offset=0,
    )

    assert response.total == 1
    assert response.items[0].retrieval_mode == "hybrid_rerank"
    assert response.items[0].result_count == 1


def test_get_detail_returns_candidates_by_source() -> None:
    detail = trace_service.get_query_trace_detail(FakeDb(), TRACE_ID)

    assert detail is not None
    assert detail.trace_schema_version == "search_trace_v1"
    assert detail.ranking_summary == {"result_count": 1}
    assert detail.candidates[0].source == "hybrid_rerank"
    assert detail.candidates_by_source["hybrid_rerank"][0]["reranker_score"] == 9.0


def test_list_trace_candidates_supports_source_filter() -> None:
    response = trace_service.list_trace_candidates(
        FakeDb(),
        trace_id=TRACE_ID,
        source="hybrid_rerank",
        limit=10,
        offset=0,
    )

    assert response is not None
    assert response.total == 1
    assert response.items[0].fusion_rank == 2
