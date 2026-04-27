from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app

client = TestClient(app)


class FakeDb:
    pass


def fake_db():
    return FakeDb()


def fake_run(run_id: str = "00000000-0000-0000-0000-000000000001"):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=UUID(run_id),
        name="BM25 eval",
        dataset_id=UUID("00000000-0000-0000-0000-000000000002"),
        index_version_id=UUID("00000000-0000-0000-0000-000000000003"),
        experiment_config_id=None,
        status="completed",
        query_count=5,
        failed_query_count=0,
        recall_at_5=0.2,
        recall_at_10=0.4,
        mrr_at_10=0.3,
        ndcg_at_10=0.25,
        avg_latency_ms=12.0,
        p50_latency_ms=10.0,
        p95_latency_ms=20.0,
        report_path="reports/evaluations/evaluation_1.json",
        created_at=now,
        started_at=now,
        completed_at=now,
        config_json={"retrieval_mode": "bm25"},
        notes="notes",
    )


def fake_result():
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000010"),
        evaluation_run_id=UUID("00000000-0000-0000-0000-000000000001"),
        benchmark_query_id=UUID("00000000-0000-0000-0000-000000000011"),
        query_external_id="q1",
        query_text="query text",
        recall_at_5=1.0,
        recall_at_10=1.0,
        mrr_at_10=1.0,
        ndcg_at_10=1.0,
        latency_ms=5.0,
        trace_id=UUID("00000000-0000-0000-0000-000000000012"),
        error_message=None,
        created_at=now,
    )


def fake_report():
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=UUID("00000000-0000-0000-0000-000000000020"),
        evaluation_run_id=UUID("00000000-0000-0000-0000-000000000001"),
        report_format="json",
        report_path="reports/evaluations/evaluation_1.json",
        summary_json={"aggregate_metrics": {"recall_at_5": 1.0}},
        created_at=now,
    )


def test_start_evaluation_requires_admin_key() -> None:
    response = client.post("/api/v1/evaluations/runs", json={"retrieval_mode": "bm25"})
    assert response.status_code == 401


def test_start_evaluation_wrong_admin_key_fails() -> None:
    response = client.post(
        "/api/v1/evaluations/runs",
        json={"retrieval_mode": "bm25"},
        headers={"X-Admin-API-Key": "wrong"},
    )
    assert response.status_code == 403


def test_start_evaluation_with_admin_key_enqueues(monkeypatch) -> None:
    calls = []

    def fake_enqueue(**kwargs):
        calls.append(kwargs)
        return {
            "job_id": "job-1",
            "queue": "default",
            "status": "queued",
            "retrieval_mode": kwargs.get("retrieval_mode"),
            "message": "Evaluation job enqueued.",
        }

    monkeypatch.setattr("app.api.v1.routes.evaluations.job_queue.enqueue_evaluation_job", fake_enqueue)
    response = client.post(
        "/api/v1/evaluations/runs",
        json={"retrieval_mode": "bm25", "query_limit": 5, "top_k": 10, "candidate_k": 10},
        headers={"X-Admin-API-Key": "replace-me"},
    )

    assert response.status_code == 200
    assert response.json()["job_id"] == "job-1"
    assert calls[0]["retrieval_mode"] == "bm25"
    assert calls[0]["query_limit"] == 5


def test_start_evaluation_with_experiment_config_without_mode(monkeypatch) -> None:
    calls = []

    def fake_enqueue(**kwargs):
        calls.append(kwargs)
        return {
            "job_id": "job-1",
            "queue": "default",
            "status": "queued",
            "retrieval_mode": None,
            "message": "Evaluation job enqueued.",
        }

    monkeypatch.setattr("app.api.v1.routes.evaluations.job_queue.enqueue_evaluation_job", fake_enqueue)
    response = client.post(
        "/api/v1/evaluations/runs",
        json={"experiment_config_name": "bm25_baseline", "query_limit": 5},
        headers={"X-Admin-API-Key": "replace-me"},
    )

    assert response.status_code == 200
    assert calls[0]["retrieval_mode"] is None
    assert calls[0]["experiment_config_name"] == "bm25_baseline"


def test_start_evaluation_unsupported_mode_fails_validation() -> None:
    response = client.post(
        "/api/v1/evaluations/runs",
        json={"retrieval_mode": "future"},
        headers={"X-Admin-API-Key": "replace-me"},
    )
    assert response.status_code == 422


def test_list_evaluation_runs_read_only(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.evaluations.list_evaluation_runs_query",
        lambda db, retrieval_mode=None, status_filter=None, limit=50, offset=0: ([fake_run()], 1),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/evaluations/runs?limit=5")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["status"] == "completed"


def test_get_evaluation_run_detail_read_only(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.evaluations.get_evaluation_run_query",
        lambda db, evaluation_run_id: fake_run(str(evaluation_run_id)),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get("/api/v1/evaluations/runs/00000000-0000-0000-0000-000000000001")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["config_json"]["retrieval_mode"] == "bm25"


def test_list_evaluation_results_read_only(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.evaluations.get_evaluation_run_query",
        lambda db, evaluation_run_id: fake_run(str(evaluation_run_id)),
    )
    monkeypatch.setattr(
        "app.api.v1.routes.evaluations.list_evaluation_results_query",
        lambda db, evaluation_run_id, failed_only=False, limit=50, offset=0: ([fake_result()], 1),
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get(
            "/api/v1/evaluations/runs/00000000-0000-0000-0000-000000000001/results"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["items"][0]["query_external_id"] == "q1"


def test_get_evaluation_report_read_only(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.api.v1.routes.evaluations.get_evaluation_run_query",
        lambda db, evaluation_run_id: fake_run(str(evaluation_run_id)),
    )
    monkeypatch.setattr(
        "app.api.v1.routes.evaluations.get_evaluation_report_query",
        lambda db, evaluation_run_id: fake_report(),
    )
    monkeypatch.setattr(
        "app.api.v1.routes.evaluations.load_evaluation_report",
        lambda path: {"evaluation_run_id": "00000000-0000-0000-0000-000000000001"},
    )
    app.dependency_overrides[get_db] = fake_db
    try:
        response = client.get(
            "/api/v1/evaluations/runs/00000000-0000-0000-0000-000000000001/report"
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["report_format"] == "json"
    assert response.json()["report_json"]["evaluation_run_id"].endswith("0001")
