import pytest

from app.ml import embeddings


class FakeModel:
    def __init__(self):
        self.calls = []

    def encode(self, texts_or_text, **kwargs):
        self.calls.append({"input": texts_or_text, "kwargs": kwargs})
        if isinstance(texts_or_text, list):
            return [[float(index), float(index + 1), float(index + 2)] for index, _ in enumerate(texts_or_text)]
        return [0.1, 0.2, 0.3]

    def get_sentence_embedding_dimension(self):
        return 3


@pytest.fixture(autouse=True)
def reset_embedding_cache():
    embeddings.reset_embedding_model_cache()
    yield
    embeddings.reset_embedding_model_cache()


def test_empty_text_rejected() -> None:
    with pytest.raises(ValueError):
        embeddings.embed_text("")


def test_whitespace_text_rejected() -> None:
    with pytest.raises(ValueError):
        embeddings.embed_text("   ")


def test_empty_batch_rejected() -> None:
    with pytest.raises(ValueError):
        embeddings.embed_texts([])


def test_batch_with_empty_text_rejected() -> None:
    with pytest.raises(ValueError):
        embeddings.embed_texts(["valid", "   "])


def test_embed_text_returns_list_of_floats_with_fake_model(monkeypatch) -> None:
    fake_model = FakeModel()
    monkeypatch.setattr(embeddings, "get_embedding_model", lambda model_name=None: fake_model)

    vector = embeddings.embed_text("hello", normalize=False)

    assert vector == [0.1, 0.2, 0.3]
    assert fake_model.calls[0]["input"] == "hello"
    assert fake_model.calls[0]["kwargs"]["normalize_embeddings"] is False


def test_embed_texts_preserves_order_with_fake_model(monkeypatch) -> None:
    fake_model = FakeModel()
    monkeypatch.setattr(embeddings, "get_embedding_model", lambda model_name=None: fake_model)

    vectors = embeddings.embed_texts(["first", "second"], batch_size=2, normalize=True)

    assert vectors == [[0.0, 1.0, 2.0], [1.0, 2.0, 3.0]]
    assert fake_model.calls[0]["input"] == ["first", "second"]
    assert fake_model.calls[0]["kwargs"]["batch_size"] == 2
    assert fake_model.calls[0]["kwargs"]["normalize_embeddings"] is True


def test_embedding_model_status_does_not_force_load(monkeypatch) -> None:
    def fail_if_loaded(model_name=None):
        raise AssertionError("status must not load the model")

    monkeypatch.setattr(embeddings, "get_embedding_model", fail_if_loaded)

    status = embeddings.get_embedding_model_status()

    assert status["model_name"] == "BAAI/bge-small-en-v1.5"
    assert status["loaded"] is False
    assert status["embedding_dimension"] == 384
    assert status["cache_dir"] == "data/models"


def test_dimension_helper_uses_fake_loaded_model() -> None:
    embeddings._embedding_model = FakeModel()
    embeddings._embedding_model_name = "BAAI/bge-small-en-v1.5"

    assert embeddings.get_embedding_dimension() == 3


def test_batch_size_argument_is_validated(monkeypatch) -> None:
    fake_model = FakeModel()
    monkeypatch.setattr(embeddings, "get_embedding_model", lambda model_name=None: fake_model)

    with pytest.raises(ValueError):
        embeddings.embed_texts(["hello"], batch_size=0)
