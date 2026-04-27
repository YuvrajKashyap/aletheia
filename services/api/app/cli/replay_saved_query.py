from __future__ import annotations

import argparse
import json
import sys

from app.db.session import SessionLocal
from app.replay.service import run_saved_query_replay


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay one saved query synchronously.")
    parser.add_argument("--saved-query-id", required=True)
    parser.add_argument("--mode", choices=["bm25", "dense", "hybrid", "hybrid_rerank"])
    parser.add_argument("--experiment-config-id")
    parser.add_argument("--experiment-config-name")
    parser.add_argument("--source-trace-id")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--candidate-k", type=int)
    parser.add_argument("--bm25-candidate-k", type=int)
    parser.add_argument("--dense-candidate-k", type=int)
    parser.add_argument("--hybrid-candidate-k", type=int)
    parser.add_argument("--rerank-top-n", type=int)
    parser.add_argument("--rrf-k", type=int, default=60)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        with SessionLocal() as db:
            summary = run_saved_query_replay(
                db,
                saved_query_id=args.saved_query_id,
                retrieval_mode=args.mode,
                experiment_config_id=args.experiment_config_id,
                experiment_config_name=args.experiment_config_name,
                source_trace_id=args.source_trace_id,
                top_k=args.top_k,
                candidate_k=args.candidate_k,
                bm25_candidate_k=args.bm25_candidate_k,
                dense_candidate_k=args.dense_candidate_k,
                hybrid_candidate_k=args.hybrid_candidate_k,
                rerank_top_n=args.rerank_top_n,
                rrf_k=args.rrf_k,
            )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
