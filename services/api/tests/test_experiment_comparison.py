from types import SimpleNamespace
from uuid import UUID

from app.experiments import comparison
from app.experiments import jobs as comparison_jobs


def cfg(config_id: str, name: str, mode: str):
    return SimpleNamespace(id=UUID(config_id), name=name, retrieval_mode=mode)


def test_comparison_resolves_defaults_in_expected_order(monkeypatch) -> None:
    configs = {
        "bm25_baseline": cfg("00000000-0000-0000-0000-000000000001", "bm25_baseline", "bm25"),
        "dense_baseline": cfg("00000000-0000-0000-0000-000000000002", "dense_baseline", "dense"),
        "hybrid_rrf_default": cfg(
            "00000000-0000-0000-0000-000000000003",
            "hybrid_rrf_default",
            "hybrid",
        ),
        "hybrid_rerank_default": cfg(
            "00000000-0000-0000-0000-000000000004",
            "hybrid_rerank_default",
            "hybrid_rerank",
        ),
    }
    monkeypatch.setattr(comparison, "seed_default_experiment_configs", lambda db: {})
    monkeypatch.setattr(comparison, "get_experiment_config_by_name", lambda db, name: configs[name])

    resolved = comparison._resolve_configs(object(), None, None, True)

    assert [item.name for item in resolved] == [
        "bm25_baseline",
        "dense_baseline",
        "hybrid_rrf_default",
        "hybrid_rerank_default",
    ]


def test_comparison_calls_runner_and_writes_report(monkeypatch) -> None:
    configs = [
        cfg("00000000-0000-0000-0000-000000000001", "bm25_baseline", "bm25"),
        cfg("00000000-0000-0000-0000-000000000002", "dense_baseline", "dense"),
    ]
    calls = []
    monkeypatch.setattr(comparison, "_resolve_configs", lambda *args, **kwargs: configs)

    def fake_run(db, **kwargs):
        calls.append(kwargs)
        index = len(calls)
        return {
            "evaluation_run_id": f"run-{index}",
            "query_count": 5,
            "failed_query_count": 0,
            "aggregate_metrics": {
                "recall_at_5": 0.1 * index,
                "recall_at_10": 0.2 * index,
                "mrr_at_10": 0.3 * index,
                "ndcg_at_10": 0.4 * index,
            },
            "latency_summary": {
                "avg_latency_ms": 20.0 / index,
                "p50_latency_ms": 10.0,
                "p95_latency_ms": 30.0,
            },
            "report_path": f"reports/evaluations/evaluation_run-{index}.json",
        }

    monkeypatch.setattr(comparison, "run_offline_evaluation", fake_run)
    monkeypatch.setattr(
        comparison,
        "write_comparison_report",
        lambda report, name: "reports/evaluations/comparisons/comparison_test.json",
    )

    summary = comparison.run_evaluation_comparison(object(), name="test")

    assert [call["experiment_config_id"] for call in calls] == [str(config.id) for config in configs]
    assert summary["best_by_metric"]["recall_at_10"]["experiment_config_name"] == "dense_baseline"
    assert summary["best_by_metric"]["avg_latency_ms"]["experiment_config_name"] == "dense_baseline"
    assert summary["report_path"].endswith("comparison_test.json")


def test_duplicate_configs_are_deduped_preserving_order(monkeypatch) -> None:
    first = cfg("00000000-0000-0000-0000-000000000001", "one", "bm25")
    second = cfg("00000000-0000-0000-0000-000000000002", "two", "dense")
    monkeypatch.setattr(comparison, "get_experiment_config", lambda db, config_id: first)
    monkeypatch.setattr(comparison, "get_experiment_config_by_name", lambda db, name: second)

    resolved = comparison._resolve_configs(object(), [str(first.id), str(first.id)], ["two"], False)

    assert [item.name for item in resolved] == ["one", "two"]


def test_comparison_job_opens_session_calls_runner_and_closes(monkeypatch) -> None:
    class FakeSession:
        closed = False

        def close(self):
            self.closed = True

    session = FakeSession()
    calls = []

    def fake_runner(db, **kwargs):
        calls.append({"db": db, **kwargs})
        return {"comparison_name": kwargs["name"], "report_path": "reports/comparison.json"}

    monkeypatch.setattr(comparison_jobs, "SessionLocal", lambda: session)
    monkeypatch.setattr(comparison_jobs, "run_evaluation_comparison", fake_runner)

    result = comparison_jobs.run_evaluation_comparison_job(
        name="comparison",
        use_defaults=True,
        query_limit=3,
    )

    assert result["comparison_name"] == "comparison"
    assert calls[0]["db"] is session
    assert calls[0]["use_defaults"] is True
    assert calls[0]["query_limit"] == 3
    assert session.closed is True
