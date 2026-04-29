from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SUPPORTED_THRESHOLD_KEYS = {
    "failed_query_count_max",
    "recall_at_10_min",
    "mrr_at_10_min",
    "ndcg_at_10_min",
}


def load_smoke_thresholds(path: str) -> dict:
    threshold_path = Path(path)
    with threshold_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Smoke threshold config must be a JSON object")

    thresholds = payload.get("thresholds", {})
    if thresholds is None:
        thresholds = {}
    if not isinstance(thresholds, dict):
        raise ValueError("Smoke threshold config field 'thresholds' must be an object")

    mode = payload.get("mode", "warn")
    if mode is not None and mode not in {"warn", "fail"}:
        raise ValueError("Smoke threshold config field 'mode' must be 'warn' or 'fail'")

    for field_name in ("description", "retrieval_mode"):
        value = payload.get(field_name)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"Smoke threshold config field '{field_name}' must be a string")

    query_limit = payload.get("query_limit")
    if query_limit is not None and not isinstance(query_limit, int):
        raise ValueError("Smoke threshold config field 'query_limit' must be an integer")

    for threshold_key, threshold_value in thresholds.items():
        if threshold_key not in SUPPORTED_THRESHOLD_KEYS:
            raise ValueError(f"Unsupported smoke threshold: {threshold_key}")
        if not isinstance(threshold_value, int | float):
            raise ValueError(f"Smoke threshold '{threshold_key}' must be numeric")

    normalized = dict(payload)
    normalized["mode"] = mode or "warn"
    normalized["thresholds"] = thresholds
    return normalized


def _metric(summary: dict, key: str) -> int | float | None:
    value = summary.get(key)
    if isinstance(value, int | float):
        return value
    return None


def _check(
    name: str,
    actual: int | float | None,
    expected: int | float,
    operator: str,
) -> dict[str, Any]:
    if actual is None:
        return {
            "name": name,
            "status": "warning",
            "actual": None,
            "expected": expected,
            "operator": operator,
            "message": f"Metric '{name}' is missing from smoke summary",
        }

    if operator == "<=":
        passed = actual <= expected
    elif operator == ">=":
        passed = actual >= expected
    else:
        raise ValueError(f"Unsupported threshold operator: {operator}")

    return {
        "name": name,
        "status": "pass" if passed else "miss",
        "actual": actual,
        "expected": expected,
        "operator": operator,
    }


def evaluate_smoke_thresholds(summary: dict, thresholds: dict) -> dict:
    mode = thresholds.get("mode", "warn")
    if mode not in {"warn", "fail"}:
        mode = "warn"
    threshold_values = thresholds.get("thresholds", {})
    if not isinstance(threshold_values, dict):
        threshold_values = {}

    checks: list[dict[str, Any]] = []
    warnings: list[str] = []
    failures: list[str] = []

    threshold_specs = [
        ("failed_query_count", "failed_query_count_max", "<="),
        ("recall_at_10", "recall_at_10_min", ">="),
        ("mrr_at_10", "mrr_at_10_min", ">="),
        ("ndcg_at_10", "ndcg_at_10_min", ">="),
    ]

    for summary_key, threshold_key, operator in threshold_specs:
        if threshold_key not in threshold_values:
            continue

        check = _check(
            summary_key,
            _metric(summary, summary_key),
            threshold_values[threshold_key],
            operator,
        )
        checks.append(check)

        if check["status"] == "warning":
            warnings.append(check["message"])
        elif check["status"] == "miss":
            message = (
                f"{summary_key}={check['actual']} missed threshold "
                f"{operator} {check['expected']}"
            )
            if mode == "fail":
                failures.append(message)
            else:
                warnings.append(message)

    if failures:
        status = "fail"
    elif warnings:
        status = "warning"
    else:
        status = "pass"

    return {
        "status": status,
        "mode": mode,
        "checks": checks,
        "warnings": warnings,
        "failures": failures,
    }


def write_smoke_report(report: dict, output_path: str) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return str(path)
