from types import SimpleNamespace

from app.replay.comparison import (
    build_replay_comparison_json,
    compare_ranked_lists,
    extract_ranked_document_ids_from_search_response,
)


def test_ranked_document_extraction_dedupes_objects_and_dicts() -> None:
    response = {
        "results": [
            {"document_id": "d1"},
            {"document_id": "d1"},
            SimpleNamespace(document_id="d2"),
            {"document_id": ""},
        ]
    }
    assert extract_ranked_document_ids_from_search_response(response) == ["d1", "d2"]


def test_compare_ranked_lists_overlap_and_added_removed() -> None:
    result = compare_ranked_lists(["d1", "d2", "d3"], ["d2", "d4", "d1"], top_k=3)
    assert result["overlap_at_k"] == 2
    assert result["added_document_ids"] == ["d4"]
    assert result["removed_document_ids"] == ["d3"]


def test_compare_ranked_lists_rank_movement() -> None:
    result = compare_ranked_lists(["d1", "d2", "d3"], ["d3", "d1", "d2"], top_k=3)
    movements = {item["document_id"]: item["movement"] for item in result["rank_changes"]}
    assert movements["d3"] == 2
    assert movements["d1"] == -1
    assert result["largest_upward_move"] == 2
    assert result["largest_downward_move"] == -1


def test_comparison_json_shape_includes_metrics() -> None:
    saved_query = SimpleNamespace(id="sq1", text="query")
    response = SimpleNamespace(
        query_id="q1",
        trace_id="t1",
        latency_ms=12.5,
        results=[SimpleNamespace(document_id="d1")],
    )
    trace = SimpleNamespace(id="source-trace", trace_json={"ranked_document_ids": ["d2", "d1"]})
    payload = build_replay_comparison_json(
        saved_query,
        response,
        "bm25",
        source_trace=trace,
        metrics={"recall_at_10": 1.0},
        top_k=10,
    )
    assert payload["ranked_document_ids"] == ["d1"]
    assert payload["metrics"]["recall_at_10"] == 1.0
    assert payload["rank_comparison"]["overlap_at_k"] == 1
