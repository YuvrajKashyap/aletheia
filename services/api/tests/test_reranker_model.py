import pytest

from app.ml import reranker


class FakeRerankerModel:
    def __init__(self):
        self.calls = []

    def predict(self, pairs, batch_size=None):
        self.calls.append({"pairs": pairs, "batch_size": batch_size})
        return [float(index) for index, _ in enumerate(pairs, start=1)]


def test_empty_query_rejected() -> None:
    with pytest.raises(ValueError):
        reranker.score_query_documents("", ["document"])


def test_empty_documents_rejected() -> None:
    with pytest.raises(ValueError):
        reranker.score_query_documents("query", [])


def test_empty_document_text_rejected() -> None:
    with pytest.raises(ValueError):
        reranker.score_query_documents("query", ["document", " "])


def test_batch_scoring_preserves_order_and_returns_floats(monkeypatch) -> None:
    fake_model = FakeRerankerModel()
    monkeypatch.setattr(reranker, "get_reranker_model", lambda model_name=None: fake_model)

    scores = reranker.score_query_documents(" query ", [" first ", " second "], batch_size=8)

    assert scores == [1.0, 2.0]
    assert fake_model.calls == [
        {
            "pairs": [("query", "first"), ("query", "second")],
            "batch_size": 8,
        }
    ]


def test_model_status_does_not_force_load(monkeypatch) -> None:
    reranker.reset_reranker_model_cache()

    def fail_load(*args, **kwargs):
        raise AssertionError("status must not load the model")

    monkeypatch.setattr(reranker, "get_reranker_model", fail_load)

    status = reranker.get_reranker_model_status()

    assert status["model_name"] == "cross-encoder/ms-marco-MiniLM-L-6-v2"
    assert status["device"] == "cpu"
    assert status["loaded"] is False
