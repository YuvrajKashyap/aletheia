from __future__ import annotations

import argparse
import json
import sys

from app.db.session import SessionLocal
from app.experiments.service import seed_default_experiment_configs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed default experiment configs.")
    return parser.parse_args()


def _config_payload(config) -> dict:
    return {
        "id": str(config.id),
        "name": config.name,
        "retrieval_mode": config.retrieval_mode,
        "bm25_candidate_k": config.bm25_candidate_k,
        "dense_candidate_k": config.dense_candidate_k,
        "hybrid_candidate_k": config.hybrid_candidate_k,
        "rerank_top_n": config.rerank_top_n,
        "top_k_final": config.top_k_final,
        "fusion_method": config.fusion_method,
        "fusion_params_json": config.fusion_params_json,
        "embedding_model": config.embedding_model,
        "reranker_model": config.reranker_model,
        "is_default": config.is_default,
    }


def main() -> int:
    parse_args()
    try:
        with SessionLocal() as db:
            result = seed_default_experiment_configs(db)
            payload = {
                "created_count": result["created_count"],
                "updated_count": result["updated_count"],
                "existing_count": result["existing_count"],
                "configs": [_config_payload(config) for config in result["configs"]],
            }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
