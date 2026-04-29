# Golden Regression Smoke

Golden smoke is a local qrels-backed regression check for retrieval quality sanity. It runs a small SciFact evaluation through the real Aletheia retrieval stack and writes a structured smoke report.

This is not a benchmark target. The default thresholds are conservative, warn-only smoke thresholds intended to catch obvious local regressions.

## CI vs Golden Smoke

GitHub CI is fast, unit/mocked, and deterministic. It does not start services or download models.

Golden smoke is a local full-stack check. It may require Docker Desktop, Postgres, OpenSearch, Qdrant, Redis, loaded SciFact data, active indexes, and a local model cache depending on retrieval mode.

## Why It Is Not In Default GitHub CI

The golden smoke check depends on local infrastructure and real retrieval. Running it in default CI would require service startup, indexes, model cache behavior, and additional runtime cost. The default CI remains a fast correctness gate.

## Prerequisites

- Docker Desktop running
- Local Postgres, OpenSearch, Qdrant, and Redis stack available
- SciFact data loaded
- Active index version available
- BM25 and vector indexes built for modes that need them
- Local model cache available for dense or rerank modes if needed

## Commands

Hybrid smoke:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/run-golden-smoke.ps1 -Mode hybrid -QueryLimit 5 -TopK 10 -Notes "Local validation"
```

Dense smoke:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/run-golden-smoke.ps1 -Mode dense -QueryLimit 5 -TopK 10 -Notes "Dense smoke"
```

Tiny rerank smoke:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/run-golden-smoke.ps1 -Mode hybrid_rerank -QueryLimit 2 -TopK 10 -Notes "Tiny rerank smoke"
```

Fail on threshold:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/run-golden-smoke.ps1 -Mode hybrid -QueryLimit 5 -TopK 10 -FailOnThreshold -Notes "Fail-on-threshold smoke"
```

## Report Path

The default report path is:

```text
reports/smoke/golden-smoke-latest.json
```

Generated smoke reports are local artifacts. The tracked file in `reports/smoke` is only `.gitkeep`.

## How To Interpret Results

- `pass` means every configured smoke threshold was satisfied.
- `warning` means a metric was missing or a warn-only threshold was missed.
- `fail` only appears when the threshold config mode is `fail`.
- Missing metrics are warnings because the smoke helper does not invent data.
- Default mode is warn-only.

## DB Side Effects

The smoke CLI uses the real offline evaluation runner. It may create rows in:

- `evaluation_runs`
- `evaluation_query_results`
- `evaluation_reports`

This is expected and acceptable for a local full-stack smoke check.
