from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

from app.db.session import SessionLocal
from app.evaluation.runner import run_offline_evaluation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a synchronous offline benchmark evaluation.")
    parser.add_argument("--mode", choices=["bm25", "dense", "hybrid", "hybrid_rerank"])
    parser.add_argument("--experiment-config-id")
    parser.add_argument("--experiment-config-name")
    parser.add_argument("--name")
    parser.add_argument("--dataset-name", default="beir/scifact")
    parser.add_argument("--dataset-version", default="test")
    parser.add_argument("--index-version-id")
    parser.add_argument("--query-limit", type=int)
    parser.add_argument("--query-offset", type=int, default=0)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--candidate-k", type=int)
    parser.add_argument("--bm25-candidate-k", type=int)
    parser.add_argument("--dense-candidate-k", type=int)
    parser.add_argument("--hybrid-candidate-k", type=int)
    parser.add_argument("--rerank-top-n", type=int)
    parser.add_argument("--rrf-k", type=int, default=60)
    parser.add_argument("--notes")
    return parser.parse_args()


def _default_name(mode: str | None, config_name: str | None) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    label = mode or config_name or "configured"
    return f"{label} evaluation {timestamp}"


def main() -> int:
    args = parse_args()
    try:
        with SessionLocal() as db:
            summary = run_offline_evaluation(
                db,
                name=args.name or _default_name(args.mode, args.experiment_config_name),
                retrieval_mode=args.mode,
                experiment_config_id=args.experiment_config_id,
                experiment_config_name=args.experiment_config_name,
                dataset_name=args.dataset_name,
                dataset_version=args.dataset_version,
                index_version_id=args.index_version_id,
                query_limit=args.query_limit,
                query_offset=args.query_offset,
                top_k=args.top_k,
                candidate_k=args.candidate_k,
                bm25_candidate_k=args.bm25_candidate_k,
                dense_candidate_k=args.dense_candidate_k,
                hybrid_candidate_k=args.hybrid_candidate_k,
                rerank_top_n=args.rerank_top_n,
                rrf_k=args.rrf_k,
                notes=args.notes,
            )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
