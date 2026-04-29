from __future__ import annotations

import argparse
from pathlib import Path

from app.db.session import SessionLocal
from app.export.demo_snapshot import SnapshotLimits, export_demo_snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export real local Aletheia data for public snapshot mode.")
    parser.add_argument("--output", default="../../apps/web/public/demo-data")
    parser.add_argument("--scenario-limit", type=int, default=4)
    parser.add_argument("--trace-limit", type=int, default=20)
    parser.add_argument("--evaluation-limit", type=int, default=20)
    parser.add_argument("--document-limit", type=int, default=20)
    parser.add_argument("--chunk-limit", type=int, default=20)
    parser.add_argument("--query-limit", type=int, default=20)
    parser.add_argument("--qrel-limit", type=int, default=20)
    parser.add_argument("--replay-limit", type=int, default=20)
    parser.add_argument("--include-large-text", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    limits = SnapshotLimits(
        scenario_limit=args.scenario_limit,
        trace_limit=args.trace_limit,
        evaluation_limit=args.evaluation_limit,
        document_limit=args.document_limit,
        chunk_limit=args.chunk_limit,
        query_limit=args.query_limit,
        qrel_limit=args.qrel_limit,
        replay_limit=args.replay_limit,
        include_large_text=args.include_large_text,
    )

    output_dir = Path(args.output).resolve()
    with SessionLocal() as db:
        manifest = export_demo_snapshot(db, output_dir, limits)

    print(f"Exported Aletheia demo snapshot to {output_dir}")
    print(f"Files: {len(manifest['files'])}")
    if manifest["warnings"]:
        print("Warnings:")
        for warning in manifest["warnings"]:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
