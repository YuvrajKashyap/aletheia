# Benchmark Reports

Generated benchmark JSON files are ignored by default.

Run the final benchmark suite locally:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/run-final-benchmark-suite.ps1
```

Dry run planned benchmark work:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/run-final-benchmark-suite.ps1 -DryRun
```

Final selected benchmark summaries can be copied into the README later after local execution and review.

Do not commit fake metrics. Do not hand-edit benchmark JSON reports to look better.
