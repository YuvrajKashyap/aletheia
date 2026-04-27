from app.evaluation import jobs


class FakeSession:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


def test_evaluation_job_opens_session_calls_runner_and_closes(monkeypatch) -> None:
    session = FakeSession()
    calls = []

    def fake_runner(db, **kwargs):
        calls.append({"db": db, **kwargs})
        return {"status": "completed", "retrieval_mode": kwargs["retrieval_mode"]}

    monkeypatch.setattr(jobs, "SessionLocal", lambda: session)
    monkeypatch.setattr(jobs, "run_offline_evaluation", fake_runner)

    result = jobs.run_evaluation_job(
        name="BM25 eval",
        retrieval_mode="bm25",
        query_limit=5,
        top_k=10,
        candidate_k=10,
        rq_job_id="rq-1",
    )

    assert result == {"status": "completed", "retrieval_mode": "bm25"}
    assert calls[0]["db"] is session
    assert calls[0]["name"] == "BM25 eval"
    assert calls[0]["retrieval_mode"] == "bm25"
    assert calls[0]["query_limit"] == 5
    assert calls[0]["candidate_k"] == 10
    assert session.closed is True

