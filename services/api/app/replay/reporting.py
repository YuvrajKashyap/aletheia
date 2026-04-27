from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def ensure_replay_reports_dir() -> Path:
    reports_dir = _repo_root() / "reports" / "replays"
    reports_dir.mkdir(parents=True, exist_ok=True)
    gitkeep = reports_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()
    return reports_dir


def _safe_name(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", name.strip()).strip("_")
    return slug or datetime.now().strftime("%Y%m%d_%H%M%S")


def write_replay_report(report: dict[str, Any], name: str) -> str:
    reports_dir = ensure_replay_reports_dir()
    path = reports_dir / f"replay_{_safe_name(name)}.json"
    counter = 2
    while path.exists():
        path = reports_dir / f"replay_{_safe_name(name)}_{counter}.json"
        counter += 1
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return str(path.relative_to(_repo_root()))


def load_replay_report(path: str) -> dict[str, Any]:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = _repo_root() / candidate
    with candidate.open("r", encoding="utf-8") as file:
        return json.load(file)
