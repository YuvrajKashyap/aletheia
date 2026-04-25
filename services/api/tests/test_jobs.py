from app.jobs.health import ping_job


def test_ping_job_returns_expected_structure() -> None:
    result = ping_job("step7")

    assert result["status"] == "ok"
    assert result["message"] == "step7"
    assert result["processed_at"]
