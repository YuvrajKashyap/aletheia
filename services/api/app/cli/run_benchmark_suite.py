from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.benchmarks.reporting import format_markdown_benchmark_table
from app.benchmarks.suite import build_planned_runs, load_benchmark_suite_config, run_benchmark_suite
from app.db.session import SessionLocal


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def service_root() -> Path:
    return repo_root() / "services" / "api"


def resolve_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    candidates = [
        Path.cwd() / path,
        repo_root() / path,
        service_root() / path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return (repo_root() / path).resolve()


def parse_modes(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local final Aletheia benchmark suite.")
    parser.add_argument("--config", default="../../configs/final-benchmark-suite.json")
    parser.add_argument("--output-dir", default="../../reports/benchmarks")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--only-mode")
    parser.add_argument("--skip-rerank", action="store_true")
    parser.add_argument("--rerank-full", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config_path = resolve_path(args.config)
        output_dir = resolve_path(args.output_dir)
        config = load_benchmark_suite_config(str(config_path))
        only_modes = parse_modes(args.only_mode)
        planned_runs = build_planned_runs(
            config,
            skip_rerank=args.skip_rerank,
            only_modes=only_modes,
            rerank_full=args.rerank_full,
        )

        if args.dry_run:
            print(
                json.dumps(
                    {
                        "status": "dry_run",
                        "config_path": str(config_path),
                        "output_dir": str(output_dir),
                        "planned_runs": planned_runs,
                        "message": "No evaluation rows written.",
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        run_config = dict(config)
        run_config["runs"] = planned_runs
        with SessionLocal() as db:
            report = run_benchmark_suite(db, run_config, str(output_dir))

        print(json.dumps(report, indent=2, sort_keys=True))
        print()
        print(format_markdown_benchmark_table(report))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
