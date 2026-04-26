from __future__ import annotations

import argparse
import json
import sys
from uuid import UUID

from app.db.session import SessionLocal
from app.search.dense_retriever import (
    search_dense,
    search_dense_by_collection_name,
)
from app.search.retrieval_models import DenseSearchResponse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an internal dense vector search.")
    parser.add_argument("query")
    parser.add_argument("--index-version-id")
    parser.add_argument("--collection-name")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--candidate-k", type=int)
    parser.add_argument("--text", action="store_true")
    return parser.parse_args()


def _preview(text: str, max_length: int = 240) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_length:
        return compact
    return f"{compact[: max_length - 3]}..."


def _json_payload(response: DenseSearchResponse) -> dict:
    payload = response.to_dict()
    payload["result_count"] = len(response.results)
    for result in payload["results"]:
        result["text_preview"] = _preview(result["text"])
        result.pop("text", None)
    return payload


def _print_text(response: DenseSearchResponse) -> None:
    print(f"query: {response.query}")
    print(f"collection: {response.collection_name}")
    print(f"mode: {response.retrieval_mode}")
    print(f"latency_ms: {response.latency_ms}")
    print(f"embedding_latency_ms: {response.embedding_latency_ms}")
    print(f"qdrant_latency_ms: {response.qdrant_latency_ms}")
    print()
    for result in response.results:
        label = result.title or result.document_external_id or result.document_id or "untitled"
        print(f"{result.rank}. score={result.score:.4f} doc={label} chunk={result.chunk_id}")
        print(_preview(result.text))
        print()


def main() -> int:
    args = parse_args()
    db = None
    try:
        if args.collection_name:
            response = search_dense_by_collection_name(
                query=args.query,
                collection_name=args.collection_name,
                top_k=args.top_k,
                candidate_k=args.candidate_k,
            )
        else:
            db = SessionLocal()
            response = search_dense(
                db,
                query=args.query,
                index_version_id=UUID(args.index_version_id) if args.index_version_id else None,
                top_k=args.top_k,
                candidate_k=args.candidate_k,
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
