from __future__ import annotations

import json
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.export.demo_snapshot import build_manifest, json_safe, truncate_text, write_json


def test_json_safe_serializes_common_snapshot_values() -> None:
    value = {
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "created_at": datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc),
        "day": date(2026, 1, 2),
        "score": Decimal("0.75"),
    }

    assert json_safe(value) == {
        "id": "00000000-0000-0000-0000-000000000001",
        "created_at": "2026-01-02T03:04:00+00:00",
        "day": "2026-01-02",
        "score": 0.75,
    }


def test_truncate_text_respects_large_text_flag() -> None:
    text = "x" * 20

    assert truncate_text(text, include_large_text=False, max_chars=5) == "xxxxx..."
    assert truncate_text(text, include_large_text=True, max_chars=5) == text


def test_build_manifest_uses_real_snapshot_shape() -> None:
    manifest = build_manifest(
        counts={"datasets": 1, "documents": 2},
        warnings=["missing dense trace"],
        generated_at=datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc),
        files=["manifest.json"],
    )

    assert manifest["generated"] is True
    assert manifest["source"] == "local_full_stack_export"
    assert manifest["demo_mode"] == "snapshot"
    assert manifest["counts"] == {"datasets": 1, "documents": 2}
    assert manifest["warnings"] == ["missing dense trace"]
    assert manifest["files"] == ["manifest.json"]


def test_write_json_writes_stable_file(tmp_path) -> None:
    write_json(tmp_path, "snapshot.json", {"b": 2, "a": UUID("00000000-0000-0000-0000-000000000002")})

    payload = json.loads((tmp_path / "snapshot.json").read_text(encoding="utf-8"))
    assert payload == {"a": "00000000-0000-0000-0000-000000000002", "b": 2}
