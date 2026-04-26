from __future__ import annotations

import argparse
import json
import sys
from uuid import UUID

from app.db.session import SessionLocal
from app.search.reranker import search_hybrid_rerank
from app.search.retrieval_models import RerankedSearchResponse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an internal hybrid RRF search with cross-encoder reranking.")
    parser.add_argument("query")
    parser.add_argument("--index-version-id")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--bm25-candidate-k", type=int, default=50)
    parser.add_argument("--dense-candidate-k", type=int, default=50)
    parser.add_argument("--hybrid-candidate-k", type=int, default=50)
    parser.add_argument("--rerank-top-n", type=int, default=25)
    parser.add_argument("--rrf-k", type=int, default=60)
    parser.add_argument("--text", action="store_true")
    return parser.parse_args()


def _preview(text: str, max_length: int = 240) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_length:
        return compact
    return f"{compact[: max_length - 3]}..."


def _json_payload(response: RerankedSearchResponse) -> dict:
    payload = response.to_dict()
    for result in payload["results"]:
        result["text_preview"] = _preview(result["text"])
        result.pop("text", None)
    return payload


def _print_text(response: RerankedSearchResponse) -> None:
    print(f"query: {response.query}")
    print(f"lexical_index: {response.lexical_index_name}")
    print(f"vector_collection: {response.vector_collection_name}")
    print(f"mode: {response.retrieval_mode}")
    print(f"latency_ms: {response.latency_ms}")
    print(f"reranker_latency_ms: {response.reranker_latency_ms}")
    print()
    for result in response.results:
        label = result.title or result.document_external_id or result.document_id or "untitled"
        print(
            f"{result.rank}. reranker={result.reranker_score:.6f} "
            f"rerank_rank={result.rerank_rank} fusion_rank={result.fusion_rank} "
            f"fusion={result.fusion_score} bm25_rank={result.bm25_rank} dense_rank={result.dense_rank} "
            f"bm25_score={result.bm25_score} dense_score={result.dense_score} "
            f"doc={label} chunk={result.chunk_id}"
        )
        print(_preview(result.text))
        print()


def main() -> int:
    args = parse_args()
    db = None
    try:
        db = SessionLocal()
        response = search_hybrid_rerank(
            db,
            query=args.query,
            index_version_id=UUID(args.index_version_id) if args.index_version_id else None,
            top_k=args.top_k,
            bm25_candidate_k=args.bm25_candidate_k,
            dense_candidate_k=args.dense_candidate_k,
            hybrid_candidate_k=args.hybrid_candidate_k,
            rerank_top_n=args.rerank_top_n,
            rrf_k=args.rrf_k,
        )
        if args.text:
            _print_text(response)
        else:
            print(json.dumps(_json_payload(response), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    sys.exit(main())
