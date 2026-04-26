from __future__ import annotations

import math


def _clean_values(values: list[float]) -> list[float]:
    return [float(value) for value in values if value is not None]


def percentile(values: list[float], p: float) -> float:
    if p < 0 or p > 100:
        raise ValueError("p must be between 0 and 100")
    clean = sorted(_clean_values(values))
    if not clean:
        return 0.0
    # Nearest-rank percentile: simple, deterministic, and dependency-free.
    rank = math.ceil((p / 100.0) * len(clean))
    rank = min(max(rank, 1), len(clean))
    return clean[rank - 1]


def summarize_latencies(latencies_ms: list[float]) -> dict:
    clean = _clean_values(latencies_ms)
    if not clean:
        return {
            "count": 0,
            "avg_latency_ms": 0.0,
            "p50_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "min_latency_ms": 0.0,
            "max_latency_ms": 0.0,
        }

    return {
        "count": len(clean),
        "avg_latency_ms": sum(clean) / len(clean),
        "p50_latency_ms": percentile(clean, 50),
        "p95_latency_ms": percentile(clean, 95),
        "min_latency_ms": min(clean),
        "max_latency_ms": max(clean),
    }
