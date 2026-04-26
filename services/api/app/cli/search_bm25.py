from __future__ import annotations

import argparse
import json
import sys
from uuid import UUID

from app.db.session import SessionLocal
from app.search.lexical_retriever import (
    search_bm25,
    search_bm25_by_index_name,
)
from app.search.retrieval_models import LexicalSearchResponse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an internal BM25 lexical search.")
    parser.add_argument("query")
    parser.add_argument("--index-version-id")
    parser.add_argument("--index-name")
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--candidate-k", type=int)
    parser.add_argument("--json", action="store_true", default=True)
    parser.add_argument("--text", action="store_true")
    return parser.parse_args()


def _preview(text: str, max_length: int = 240) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_length:
        return compact
    return f"{compact[: max_length - 3]}..."


def _print_text(response: LexicalSearchResponse) -> None:
    print(f"query: {response.query}")
    print(f"index: {response.index_name}")
    print(f"mode: {response.retrieval_mode}")
    print(f"latency_ms: {response.latency_ms}")
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
        if args.index_name:
            response = search_bm25_by_index_name(
                query=args.query,
                index_name=args.index_name,
                top_k=args.top_k,
                candidate_k=args.candidate_k,
            )
        else:
            db = SessionLocal()
            response = search_bm25(
                db,
                query=args.query,
                index_version_id=UUID(args.index_version_id) if args.index_version_id else None,
                top_k=args.top_k,
                candidate_k=args.candidate_k,
            )

        if args.text:
            _print_text(response)
        else:
            print(json.dumps(response.to_dict(), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    sys.exit(main())
