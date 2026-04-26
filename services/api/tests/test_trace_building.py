from datetime import datetime, timezone
from types import SimpleNamespace

from app.search import tracing


def test_base_trace_includes_standard_fields() -> None:
    trace = tracing.build_base_trace(
        query="statins",
        retrieval_mode="bm25",
        request_id="request-1",
        query_id="query-1",
        trace_id="trace-1",
        index_version=None,
        parameters={"top_k": 5},
    )

    assert trace["trace_schema_version"] == "search_trace_v1"
    assert trace["parameters"] == {"top_k": 5}
    assert trace["stages"] == {}
    assert trace["warnings"] == []
    assert trace["errors"] == []


def test_stage_shapes() -> None:
    assert tracing.build_bm25_stage(1.0, "index", 50, 5)["index_name"] == "index"
    assert tracing.build_dense_stage(2.0, "collection", 50, 5, 1.0, 1.0, 384)[
        "query_embedding_dimension"
    ] == 384
    assert tracing.build_fusion_stage(0.5, 60, 25, 5)["method"] == "reciprocal_rank_fusion"
    assert tracing.build_reranker_stage(3.0, "model", 25, 25, 5)["model_name"] == "model"


def test_candidate_preview_truncates() -> None:
    assert tracing.candidate_preview(None, 10) == ""
    assert tracing.candidate_preview("short", 10) == "short"
    assert tracing.candidate_preview("1234567890", 6) == "123..."


def test_candidate_serialization_and_grouping() -> None:
    candidate = SimpleNamespace(
        id="candidate-1",
        source="bm25",
        final_rank=1,
        bm25_rank=1,
        dense_rank=None,
        fusion_rank=None,
        rerank_rank=None,
        bm25_score=10.0,
        dense_score=None,
        fusion_score=None,
        reranker_score=None,
        chunk_id="chunk-1",
        document_id="doc-1",
        metadata_json={"title": "Title"},
        created_at=datetime(2026, 4, 26, tzinfo=timezone.utc),
    )

    serialized = tracing.serialize_candidate_for_trace(candidate)
    grouped = tracing.group_candidates_by_source([candidate])

    assert serialized["id"] == "candidate-1"
    assert serialized["bm25_score"] == 10.0
    assert grouped["bm25"][0]["chunk_id"] == "chunk-1"


def test_hybrid_ranking_summary_counts_sources() -> None:
    results = [
        SimpleNamespace(rank=1, chunk_id="a", document_id="d1", bm25_rank=1, dense_rank=1, fusion_score=0.1),
        SimpleNamespace(rank=2, chunk_id="b", document_id="d2", bm25_rank=2, dense_rank=None, fusion_score=0.2),
        SimpleNamespace(rank=3, chunk_id="c", document_id="d3", bm25_rank=None, dense_rank=2, fusion_score=0.3),
    ]

    summary = tracing.build_ranking_summary(results, "hybrid")

    assert summary["both_sources_count"] == 1
    assert summary["bm25_only_count"] == 1
    assert summary["dense_only_count"] == 1


def test_hybrid_rerank_ranking_summary_computes_movements() -> None:
    results = [
        SimpleNamespace(rank=1, chunk_id="a", document_id="d1", fusion_rank=3, rerank_rank=1, reranker_score=2.0),
        SimpleNamespace(rank=2, chunk_id="b", document_id="d2", fusion_rank=1, rerank_rank=2, reranker_score=1.0),
        SimpleNamespace(rank=3, chunk_id="c", document_id="d3", fusion_rank=3, rerank_rank=3, reranker_score=0.5),
    ]

    summary = tracing.build_ranking_summary(results, "hybrid_rerank")

    assert summary["moved_up"] == 1
    assert summary["moved_down"] == 1
    assert summary["unchanged"] == 1
    assert summary["largest_upward_move"] == 2
    assert summary["largest_downward_move"] == -1


def test_invalid_preview_length_is_safe() -> None:
    assert tracing.candidate_preview("abcdef", 2) == ".."
