from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.core.config import get_settings


@dataclass(frozen=True)
class EmbeddingModelStatus:
    model_name: str
    device: str
    loaded: bool
    embedding_dimension: int | None
    cache_dir: str
    error: str | None

    def to_dict(self) -> dict:
        return asdict(self)


_embedding_model: Any | None = None
_embedding_model_name: str | None = None
_embedding_model_error: str | None = None


def _vector_to_list(vector: Any) -> list[float]:
    if hasattr(vector, "tolist"):
        vector = vector.tolist()
    return [float(value) for value in vector]


def _model_dimension(model: Any) -> int | None:
    if hasattr(model, "get_sentence_embedding_dimension"):
        dimension = model.get_sentence_embedding_dimension()
        return int(dimension) if dimension is not None else None
    return None


def reset_embedding_model_cache() -> None:
    global _embedding_model, _embedding_model_name, _embedding_model_error
    _embedding_model = None
    _embedding_model_name = None
    _embedding_model_error = None


def get_embedding_model(model_name: str | None = None):
    global _embedding_model, _embedding_model_name, _embedding_model_error

    settings = get_settings()
    resolved_model_name = model_name or settings.EMBEDDING_MODEL
    if _embedding_model is not None and _embedding_model_name == resolved_model_name:
        return _embedding_model
    if _embedding_model is not None and _embedding_model_name != resolved_model_name:
        # Loading multiple local embedding models in one process can consume a lot of memory.
        # For now, reload explicitly when a different model is requested.
        reset_embedding_model_cache()

    try:
        from sentence_transformers import SentenceTransformer

        _embedding_model = SentenceTransformer(
            resolved_model_name,
            cache_folder=settings.MODEL_CACHE_DIR,
            device=settings.EMBEDDING_DEVICE,
        )
        _embedding_model_name = resolved_model_name
        _embedding_model_error = None
        return _embedding_model
    except Exception as exc:
        _embedding_model_error = str(exc)
        raise RuntimeError(f"Failed to load embedding model {resolved_model_name}: {exc}") from exc


def get_embedding_model_status() -> dict:
    settings = get_settings()
    loaded_dimension = _model_dimension(_embedding_model) if _embedding_model is not None else None
    return EmbeddingModelStatus(
        model_name=_embedding_model_name or settings.EMBEDDING_MODEL,
        device=settings.EMBEDDING_DEVICE,
        loaded=_embedding_model is not None,
        embedding_dimension=loaded_dimension or settings.EMBEDDING_DIMENSION,
        cache_dir=settings.MODEL_CACHE_DIR,
        error=_embedding_model_error,
    ).to_dict()


def get_embedding_dimension(
    model_name: str | None = None,
    load_if_needed: bool = False,
) -> int | None:
    settings = get_settings()
    if _embedding_model is not None and (model_name is None or model_name == _embedding_model_name):
        return _model_dimension(_embedding_model) or settings.EMBEDDING_DIMENSION
    if load_if_needed:
        return _model_dimension(get_embedding_model(model_name)) or settings.EMBEDDING_DIMENSION
    return settings.EMBEDDING_DIMENSION


def _validate_text(text: str) -> str:
    normalized = text.strip()
    if not normalized:
        raise ValueError("Text must not be empty.")
    return normalized


def embed_text(
    text: str,
    model_name: str | None = None,
    normalize: bool | None = None,
) -> list[float]:
    settings = get_settings()
    normalized_text = _validate_text(text)
    model = get_embedding_model(model_name)
    normalize_embeddings = settings.EMBEDDING_NORMALIZE if normalize is None else normalize
    vector = _vector_to_list(
        model.encode(
            normalized_text,
            normalize_embeddings=normalize_embeddings,
        )
    )
    if not vector:
        raise RuntimeError("Embedding model returned an empty vector.")
    return vector


def embed_texts(
    texts: list[str],
    model_name: str | None = None,
    batch_size: int | None = None,
    normalize: bool | None = None,
) -> list[list[float]]:
    settings = get_settings()
    if not texts:
        raise ValueError("Texts must not be empty.")
    normalized_texts = [_validate_text(text) for text in texts]
    resolved_batch_size = settings.EMBEDDING_BATCH_SIZE if batch_size is None else batch_size
    if resolved_batch_size < 1:
        raise ValueError("Batch size must be at least 1.")

    model = get_embedding_model(model_name)
    normalize_embeddings = settings.EMBEDDING_NORMALIZE if normalize is None else normalize
    vectors = model.encode(
        normalized_texts,
        batch_size=resolved_batch_size,
        normalize_embeddings=normalize_embeddings,
    )
    result = [_vector_to_list(vector) for vector in vectors]
    if any(not vector for vector in result):
        raise RuntimeError("Embedding model returned an empty vector.")
    return result
