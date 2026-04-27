import json

from app.cli import replay_saved_query, run_golden_replay, seed_golden_queries


class FakeSession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def test_seed_golden_queries_cli(monkeypatch, capsys) -> None:
    monkeypatch.setattr(seed_golden_queries, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(
        seed_golden_queries,
        "seed_golden_queries_from_scifact",
        lambda db, **kwargs: {
            "created_count": 1,
            "existing_count": 0,
            "total_selected": 1,
            "items": [
                type(
                    "Saved",
                    (),
                    {
                        "id": "sq1",
                        "name": "SciFact q1",
                        "text": "query",
                        "source": "golden_scifact",
                        "dataset_id": None,
                        "metadata_json": {},
                    },
                )()
            ],
        },
    )
    monkeypatch.setattr("sys.argv", ["seed_golden_queries.py", "--limit", "1"])

    assert seed_golden_queries.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["created_count"] == 1


def test_replay_saved_query_cli(monkeypatch, capsys) -> None:
    calls = []
    monkeypatch.setattr(replay_saved_query, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(
        replay_saved_query,
        "run_saved_query_replay",
        lambda db, **kwargs: calls.append(kwargs)
        or {"query_replay_id": "qr1", "status": "completed"},
    )
    monkeypatch.setattr(
        "sys.argv",
        ["replay_saved_query.py", "--saved-query-id", "sq1", "--mode", "bm25"],
    )

    assert replay_saved_query.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["query_replay_id"] == "qr1"
    assert calls[0]["retrieval_mode"] == "bm25"


def test_run_golden_replay_cli(monkeypatch, capsys) -> None:
    calls = []
    monkeypatch.setattr(run_golden_replay, "SessionLocal", lambda: FakeSession())
    monkeypatch.setattr(
        run_golden_replay,
        "run_golden_query_replay",
        lambda db, **kwargs: calls.append(kwargs)
        or {"name": kwargs["name"], "report_path": "reports/replays/test.json"},
    )
    monkeypatch.setattr(
        "sys.argv",
        ["run_golden_replay.py", "--name", "test", "--mode", "bm25", "--limit", "1"],
    )

    assert run_golden_replay.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["report_path"] == "reports/replays/test.json"
    assert calls[0]["retrieval_mode"] == "bm25"
