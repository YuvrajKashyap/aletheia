from __future__ import annotations

import json
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def ensure_reports_dir() -> Path:
    reports_dir = _repo_root() / "reports" / "evaluations"
    reports_dir.mkdir(parents=True, exist_ok=True)
    gitkeep = reports_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")
    return reports_dir


def write_evaluation_report(report: dict, evaluation_run_id: str) -> str:
    reports_dir = ensure_reports_dir()
    report_path = reports_dir / f"evaluation_{evaluation_run_id}.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return str(report_path.relative_to(_repo_root()))


def load_evaluation_report(path: str) -> dict:
    report_path = Path(path)
    if not report_path.is_absolute():
        report_path = _repo_root() / report_path
    with report_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

