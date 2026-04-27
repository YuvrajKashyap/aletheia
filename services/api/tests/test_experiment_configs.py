from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

import pytest

from app.experiments.defaults import get_default_experiment_configs
from app.experiments.service import (
    experiment_config_to_evaluation_params,
    seed_default_experiment_configs,
    validate_experiment_config_values,
)


def config(**overrides):
    now = datetime.now(timezone.utc)
    values = {
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "name": "bm25_baseline",
        "retrieval_mode": "bm25",
        "bm25_candidate_k": 10,
        "dense_candidate_k": 0,
        "hybrid_candidate_k": 0,
        "rerank_top_n": 0,
        "top_k_final": 10,
        "fusion_method": None,
        "fusion_params_json": {},
        "embedding_model": None,
        "reranker_model": None,
        "config_json": {},
        "is_default": True,
        "created_at": now,
        "updated_at": now,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_default_configs_exist_in_expected_order() -> None:
    defaults = get_default_experiment_configs()
    assert [item["name"] for item in defaults] == [
        "bm25_baseline",
        "dense_baseline",
        "hybrid_rrf_default",
        "hybrid_rerank_default",
    ]
    assert [item["retrieval_mode"] for item in defaults] == [
        "bm25",
        "dense",
        "hybrid",
        "hybrid_rerank",
    ]


def test_config_to_evaluation_params_for_bm25() -> None:
    params = experiment_config_to_evaluation_params(config())
    assert params == {"retrieval_mode": "bm25", "top_k": 10, "rrf_k": 60, "candidate_k": 10}


def test_config_to_evaluation_params_for_dense() -> None:
    params = experiment_config_to_evaluation_params(
        config(retrieval_mode="dense", bm25_candidate_k=0, dense_candidate_k=10)
    )
    assert params["retrieval_mode"] == "dense"
    assert params["candidate_k"] == 10
    assert "bm25_candidate_k" not in params


def test_config_to_evaluation_params_for_hybrid() -> None:
    params = experiment_config_to_evaluation_params(
        config(
            retrieval_mode="hybrid",
            bm25_candidate_k=50,
            dense_candidate_k=40,
            hybrid_candidate_k=50,
            fusion_params_json={"rrf_k": 42},
        )
    )
    assert params["retrieval_mode"] == "hybrid"
    assert params["bm25_candidate_k"] == 50
    assert params["dense_candidate_k"] == 40
    assert params["rrf_k"] == 42
    assert "hybrid_candidate_k" not in params


def test_config_to_evaluation_params_for_hybrid_rerank() -> None:
    params = experiment_config_to_evaluation_params(
        config(
            retrieval_mode="hybrid_rerank",
            bm25_candidate_k=50,
            dense_candidate_k=50,
            hybrid_candidate_k=50,
            rerank_top_n=25,
            fusion_params_json={"rrf_k": 60},
        )
    )
    assert params["retrieval_mode"] == "hybrid_rerank"
    assert params["hybrid_candidate_k"] == 50
    assert params["rerank_top_n"] == 25


def test_validation_rejects_invalid_mode() -> None:
    with pytest.raises(ValueError, match="Unsupported"):
        validate_experiment_config_values(
            name="bad",
            retrieval_mode="future",
            bm25_candidate_k=10,
            dense_candidate_k=10,
            hybrid_candidate_k=10,
            rerank_top_n=10,
            top_k_final=10,
        )


def test_validation_rejects_invalid_candidate_depths() -> None:
    with pytest.raises(ValueError, match="bm25_candidate_k"):
        validate_experiment_config_values(
            name="bad",
            retrieval_mode="bm25",
            bm25_candidate_k=5,
            dense_candidate_k=0,
            hybrid_candidate_k=0,
            rerank_top_n=0,
            top_k_final=10,
        )


def test_seed_defaults_idempotency_with_fakes(monkeypatch) -> None:
    created = []
    existing = {spec["name"]: config(**spec) for spec in get_default_experiment_configs()}

    monkeypatch.setattr(
        "app.experiments.service.get_experiment_config_by_name",
        lambda db, name: existing.get(name),
    )

    def fake_create(db, **kwargs):
        created.append(kwargs)
        return config(**kwargs)

    monkeypatch.setattr("app.experiments.service.create_experiment_config", fake_create)
    result = seed_default_experiment_configs(SimpleNamespace(commit=lambda: None, refresh=lambda c: None))

    assert result["created_count"] == 0
    assert result["existing_count"] == 4
    assert created == []
