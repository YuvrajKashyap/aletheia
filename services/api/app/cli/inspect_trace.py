from __future__ import annotations

import argparse
import json
import sys
from uuid import UUID

from app.db.session import SessionLocal
from app.search.trace_service import get_query_trace_detail, list_trace_candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a stored Aletheia search trace.")
    parser.add_argument("--trace-id", required=True)
    parser.add_argument("--candidates", action="store_true")
    parser.add_argument("--source")
    parser.add_argument("--json", action="store_true", default=True)
    parser.add_argument("--text", action="store_true")
    return parser.parse_args()


def _json_default(value):
    return str(value)


def _print_text(payload: dict) -> None:
    print(f"trace_id: {payload['trace_id']}")
    print(f"query_id: {payload['query_id']}")
    print(f"mode: {payload['retrieval_mode']}")
    print(f"status: {payload['status']}")
    print(f"latency_ms: {payload['total_latency_ms']}")
    print(f"schema: {payload.get('trace_schema_version')}")
    print("stages:", ", ".join((payload.get("trace_json") or {}).get("stages", {}).keys()))
    print("ranking_summary:")
    print(json.dumps(payload.get("ranking_summary") or {}, indent=2, default=_json_default))
    if payload.get("candidates"):
        print("candidates:")
        for candidate in payload["candidates"]:
            print(
                f"- {candidate.get('source')} final={candidate.get('final_rank')} "
                f"chunk={candidate.get('chunk_id')} doc={candidate.get('document_id')}"
            )


def main() -> int:
    args = parse_args()
    db = None
    try:
        db = SessionLocal()
        detail = get_query_trace_detail(db, UUID(args.trace_id))
        if detail is None:
            print(json.dumps({"status": "failed", "error": f"Trace not found: {args.trace_id}"}))
            return 1
        payload = detail.model_dump(mode="json")
        if args.candidates:
            candidates = list_trace_candidates(
                db,
                trace_id=UUID(args.trace_id),
                source=args.source,
                limit=500,
                offset=0,
            )
            payload["candidates"] = candidates.model_dump(mode="json")["items"] if candidates else []
        elif args.source:
            payload["candidates"] = [
                candidate
                for candidate in payload.get("candidates", [])
                if candidate.get("source") == args.source
            ]

        if args.text:
            _print_text(payload)
        else:
            print(json.dumps(payload, indent=2, sort_keys=True, default=_json_default))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    finally:
        if db is not None:
            db.close()


if __name__ == "__main__":
    sys.exit(main())
