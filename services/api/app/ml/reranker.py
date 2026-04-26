from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from app.core.config import get_settings


@dataclass(frozen=True)
class RerankerModelStatus:
    model_name: str
    device: str
    loaded: bool
    cache_dir: str
    error: str | None

    def to_dict(self) -> dict:
        return asdict(self)


_reranker_model: Any | None = None
_reranker_model_name: str | None = None
_reranker_model_error: str | None = None


def reset_reranker_model_cache() -> None:
    global _reranker_model, _reranker_model_name, _reranker_model_error
    _reranker_model = None
    _reranker_model_name = None
    _reranker_model_error = None


def get_reranker_model(model_name: str | None = None):
    global _reranker_model, _reranker_model_name, _reranker_model_error

    settings = get_settings()
    resolved_model_name = model_name or settings.RERANKER_MODEL
    if _reranker_model is not None and _reranker_model_name == resolved_model_name:
        return _reranker_model
    if _reranker_model is not None and _reranker_model_name != resolved_model_name:
        reset_reranker_model_cache()

    try:
        from sentence_transformers import CrossEncoder

        _reranker_model = CrossEncoder(
            resolved_model_name,
            max_length=512,
            device=settings.RERANKER_DEVICE,
            cache_folder=settings.MODEL_CACHE_DIR,
        )
        _reranker_model_name = resolved_model_name
        _reranker_model_error = None
        return _reranker_model
    except Exception as exc:
        _reranker_model_error = str(exc)
        raise RuntimeError(f"Failed to load reranker model {resolved_model_name}: {exc}") from exc


def get_reranker_model_status() -> dict:
    settings = get_settings()
    return RerankerModelStatus(
        model_name=_reranker_model_name or settings.RERANKER_MODEL,
        device=settings.RERANKER_DEVICE,
        loaded=_reranker_model is not None,
        cache_dir=settings.MODEL_CACHE_DIR,
        error=_reranker_model_error,
    ).to_dict()


def _validate_query(query: str) -> str:
    normalized = query.strip()
    if not normalized:
        raise ValueError("Reranker query must not be empty.")
    return normalized


def _validate_documents(documents: list[str]) -> list[str]:
    if not documents:
        raise ValueError("Reranker documents must not be empty.")
    normalized = []
    for document in documents:
        stripped = document.strip()
        if not stripped:
            raise ValueError("Reranker document text must not be empty.")
        normalized.append(stripped)
    return normalized


def _scores_to_list(scores: Any) -> list[float]:
    if hasattr(scores, "tolist"):
        scores = scores.tolist()
    return [float(score) for score in scores]


def score_query_documents(
    query: str,
    documents: list[str],
    model_name: str | None = None,
    batch_size: int | None = None,
) -> list[float]:
    settings = get_settings()
    normalized_query = _validate_query(query)
    normalized_documents = _validate_documents(documents)
    resolved_batch_size = settings.RERANKER_BATCH_SIZE if batch_size is None else batch_size
    if resolved_batch_size < 1:
        raise ValueError("Reranker batch size must be at least 1.")

    model = get_reranker_model(model_name)
    pairs = [(normalized_query, document) for document in normalized_documents]
    try:
        scores = model.predict(pairs, batch_size=resolved_batch_size)
    except TypeError:
        scores = model.predict(pairs)
    result = _scores_to_list(scores)
    if len(result) != len(normalized_documents):
        raise RuntimeError("Reranker returned an unexpected number of scores.")
    return result
