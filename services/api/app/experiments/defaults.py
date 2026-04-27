from __future__ import annotations

from copy import deepcopy
from typing import Any


DEFAULT_EXPERIMENT_CONFIGS: list[dict[str, Any]] = [
    {
        "name": "bm25_baseline",
        "retrieval_mode": "bm25",
        "top_k_final": 10,
        "bm25_candidate_k": 10,
        "dense_candidate_k": 0,
        "hybrid_candidate_k": 0,
        "rerank_top_n": 0,
        "fusion_method": None,
        "fusion_params_json": {},
        "embedding_model": None,
        "reranker_model": None,
        "is_default": True,
    },
    {
        "name": "dense_baseline",
        "retrieval_mode": "dense",
        "top_k_final": 10,
        "bm25_candidate_k": 0,
        "dense_candidate_k": 10,
        "hybrid_candidate_k": 0,
        "rerank_top_n": 0,
        "fusion_method": None,
        "fusion_params_json": {},
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "reranker_model": None,
        "is_default": True,
    },
    {
        "name": "hybrid_rrf_default",
        "retrieval_mode": "hybrid",
        "top_k_final": 10,
        "bm25_candidate_k": 50,
        "dense_candidate_k": 50,
        "hybrid_candidate_k": 50,
        "rerank_top_n": 0,
        "fusion_method": "reciprocal_rank_fusion",
        "fusion_params_json": {"rrf_k": 60},
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "reranker_model": None,
        "is_default": True,
    },
    {
        "name": "hybrid_rerank_default",
        "retrieval_mode": "hybrid_rerank",
        "top_k_final": 10,
        "bm25_candidate_k": 50,
        "dense_candidate_k": 50,
        "hybrid_candidate_k": 50,
        "rerank_top_n": 25,
        "fusion_method": "reciprocal_rank_fusion",
        "fusion_params_json": {"rrf_k": 60},
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "reranker_model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "is_default": True,
    },
]


def get_default_experiment_configs() -> list[dict[str, Any]]:
    return deepcopy(DEFAULT_EXPERIMENT_CONFIGS)
