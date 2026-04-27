from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.experiments.defaults import get_default_experiment_configs
from app.models.evaluation import EvaluationRun
from app.models.experiments import ExperimentConfig


SUPPORTED_RETRIEVAL_MODES = {"bm25", "dense", "hybrid", "hybrid_rerank"}
VALIDATION_FIELDS = {
    "name",
    "retrieval_mode",
    "bm25_candidate_k",
    "dense_candidate_k",
    "hybrid_candidate_k",
    "rerank_top_n",
    "top_k_final",
}


def _normalize_name(name: str | None) -> str:
    normalized = (name or "").strip()
    if not normalized:
        raise ValueError("Experiment config name is required")
    return normalized


def _positive(value: int, field_name: str) -> None:
    if value <= 0:
        raise ValueError(f"{field_name} must be greater than 0")


def validate_experiment_config_values(
    *,
    name: str,
    retrieval_mode: str,
    bm25_candidate_k: int,
    dense_candidate_k: int,
    hybrid_candidate_k: int,
    rerank_top_n: int,
    top_k_final: int,
) -> None:
    _normalize_name(name)
    if retrieval_mode not in SUPPORTED_RETRIEVAL_MODES:
        raise ValueError(f"Unsupported retrieval mode: {retrieval_mode}")
    _positive(top_k_final, "top_k_final")
    for field_name, value in (
        ("bm25_candidate_k", bm25_candidate_k),
        ("dense_candidate_k", dense_candidate_k),
        ("hybrid_candidate_k", hybrid_candidate_k),
        ("rerank_top_n", rerank_top_n),
    ):
        if value < 0:
            raise ValueError(f"{field_name} must be greater than or equal to 0")

    if retrieval_mode == "bm25" and bm25_candidate_k < top_k_final:
        raise ValueError("bm25_candidate_k must be greater than or equal to top_k_final")
    if retrieval_mode == "dense" and dense_candidate_k < top_k_final:
        raise ValueError("dense_candidate_k must be greater than or equal to top_k_final")
    if retrieval_mode == "hybrid":
        if bm25_candidate_k < top_k_final:
            raise ValueError("bm25_candidate_k must be greater than or equal to top_k_final")
        if dense_candidate_k < top_k_final:
            raise ValueError("dense_candidate_k must be greater than or equal to top_k_final")
    if retrieval_mode == "hybrid_rerank":
        if bm25_candidate_k < top_k_final:
            raise ValueError("bm25_candidate_k must be greater than or equal to top_k_final")
        if dense_candidate_k < top_k_final:
            raise ValueError("dense_candidate_k must be greater than or equal to top_k_final")
        if hybrid_candidate_k < top_k_final:
            raise ValueError("hybrid_candidate_k must be greater than or equal to top_k_final")
        if rerank_top_n < top_k_final:
            raise ValueError("rerank_top_n must be greater than or equal to top_k_final")
        if hybrid_candidate_k < rerank_top_n:
            raise ValueError("hybrid_candidate_k must be greater than or equal to rerank_top_n")


def _ensure_unique_name(
    db: Session,
    name: str,
    existing_id: UUID | None = None,
) -> None:
    existing = get_experiment_config_by_name(db, name)
    if existing is not None and (existing_id is None or existing.id != existing_id):
        raise ValueError(f"Experiment config already exists: {name}")


def create_experiment_config(
    db: Session,
    name: str,
    retrieval_mode: str,
    bm25_candidate_k: int = 50,
    dense_candidate_k: int = 50,
    hybrid_candidate_k: int = 50,
    rerank_top_n: int = 25,
    top_k_final: int = 10,
    fusion_method: str | None = None,
    fusion_params_json: dict[str, Any] | None = None,
    embedding_model: str | None = None,
    reranker_model: str | None = None,
    config_json: dict[str, Any] | None = None,
    is_default: bool = False,
) -> ExperimentConfig:
    normalized_name = _normalize_name(name)
    validate_experiment_config_values(
        name=normalized_name,
        retrieval_mode=retrieval_mode,
        bm25_candidate_k=bm25_candidate_k,
        dense_candidate_k=dense_candidate_k,
        hybrid_candidate_k=hybrid_candidate_k,
        rerank_top_n=rerank_top_n,
        top_k_final=top_k_final,
    )
    _ensure_unique_name(db, normalized_name)
    config = ExperimentConfig(
        name=normalized_name,
        retrieval_mode=retrieval_mode,
        bm25_candidate_k=bm25_candidate_k,
        dense_candidate_k=dense_candidate_k,
        hybrid_candidate_k=hybrid_candidate_k,
        rerank_top_n=rerank_top_n,
        top_k_final=top_k_final,
        fusion_method=fusion_method,
        fusion_params_json=fusion_params_json or {},
        embedding_model=embedding_model,
        reranker_model=reranker_model,
        config_json=config_json or {},
        is_default=is_default,
    )
    db.add(config)
    db.flush()
    if fusion_method is None:
        config.fusion_method = None
    db.commit()
    db.refresh(config)
    return config


def get_experiment_config(db: Session, experiment_config_id: str | UUID) -> ExperimentConfig | None:
    return db.get(ExperimentConfig, UUID(str(experiment_config_id)))


def get_experiment_config_by_name(db: Session, name: str) -> ExperimentConfig | None:
    normalized_name = _normalize_name(name)
    return db.scalar(select(ExperimentConfig).where(ExperimentConfig.name == normalized_name))


def list_experiment_configs(
    db: Session,
    retrieval_mode: str | None = None,
    is_default: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict[str, Any]:
    statement = select(ExperimentConfig)
    count_statement = select(func.count()).select_from(ExperimentConfig)
    filters = []
    if retrieval_mode:
        filters.append(ExperimentConfig.retrieval_mode == retrieval_mode)
    if is_default is not None:
        filters.append(ExperimentConfig.is_default == is_default)
    if filters:
        statement = statement.where(*filters)
        count_statement = count_statement.where(*filters)
    total = int(db.scalar(count_statement) or 0)
    configs = list(
        db.scalars(
            statement.order_by(ExperimentConfig.name.asc(), ExperimentConfig.id.asc())
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return {"total": total, "limit": limit, "offset": offset, "items": configs}


def update_experiment_config(
    db: Session,
    experiment_config_id: str | UUID,
    **fields: Any,
) -> ExperimentConfig:
    config = get_experiment_config(db, experiment_config_id)
    if config is None:
        raise LookupError(f"Experiment config not found: {experiment_config_id}")

    values = {
        "name": config.name,
        "retrieval_mode": config.retrieval_mode,
        "bm25_candidate_k": config.bm25_candidate_k,
        "dense_candidate_k": config.dense_candidate_k,
        "hybrid_candidate_k": config.hybrid_candidate_k,
        "rerank_top_n": config.rerank_top_n,
        "top_k_final": config.top_k_final,
    }
    for key, value in fields.items():
        if key in VALIDATION_FIELDS and value is not None:
            values[key] = value
    values["name"] = _normalize_name(values["name"])
    validate_experiment_config_values(**values)
    if values["name"] != config.name:
        _ensure_unique_name(db, values["name"], existing_id=config.id)

    for key, value in fields.items():
        if value is not None or key not in VALIDATION_FIELDS:
            setattr(config, key, value)
    config.name = values["name"]
    db.commit()
    db.refresh(config)
    return config


def delete_experiment_config(db: Session, experiment_config_id: str | UUID) -> None:
    config = get_experiment_config(db, experiment_config_id)
    if config is None:
        raise LookupError(f"Experiment config not found: {experiment_config_id}")
    run_count = int(
        db.scalar(
            select(func.count())
            .select_from(EvaluationRun)
            .where(EvaluationRun.experiment_config_id == config.id)
        )
        or 0
    )
    if run_count > 0:
        raise ValueError("Experiment config is used by evaluation runs and cannot be deleted")
    db.delete(config)
    db.commit()


def seed_default_experiment_configs(db: Session) -> dict[str, Any]:
    created = 0
    updated = 0
    existing = 0
    configs: list[ExperimentConfig] = []
    for spec in get_default_experiment_configs():
        config = get_experiment_config_by_name(db, spec["name"])
        if config is None:
            config = create_experiment_config(db, **spec)
            created += 1
        else:
            changed = False
            for key, value in spec.items():
                if getattr(config, key) != value:
                    setattr(config, key, value)
                    changed = True
            if changed:
                validate_experiment_config_values(
                    name=config.name,
                    retrieval_mode=config.retrieval_mode,
                    bm25_candidate_k=config.bm25_candidate_k,
                    dense_candidate_k=config.dense_candidate_k,
                    hybrid_candidate_k=config.hybrid_candidate_k,
                    rerank_top_n=config.rerank_top_n,
                    top_k_final=config.top_k_final,
                )
                db.commit()
                db.refresh(config)
                updated += 1
            else:
                existing += 1
        configs.append(config)
    return {
        "created_count": created,
        "updated_count": updated,
        "existing_count": existing,
        "configs": configs,
    }


def experiment_config_to_evaluation_params(config: ExperimentConfig) -> dict[str, Any]:
    rrf_k = (config.fusion_params_json or {}).get("rrf_k", 60)
    params: dict[str, Any] = {
        "retrieval_mode": config.retrieval_mode,
        "top_k": config.top_k_final,
        "rrf_k": rrf_k,
    }
    if config.retrieval_mode == "bm25":
        params["candidate_k"] = config.bm25_candidate_k
    elif config.retrieval_mode == "dense":
        params["candidate_k"] = config.dense_candidate_k
    elif config.retrieval_mode == "hybrid":
        params["bm25_candidate_k"] = config.bm25_candidate_k
        params["dense_candidate_k"] = config.dense_candidate_k
    elif config.retrieval_mode == "hybrid_rerank":
        params["bm25_candidate_k"] = config.bm25_candidate_k
        params["dense_candidate_k"] = config.dense_candidate_k
        params["hybrid_candidate_k"] = config.hybrid_candidate_k
        params["rerank_top_n"] = config.rerank_top_n
    return params
