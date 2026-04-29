# Experiment Comparison Flow

This diagram shows how experiment configs connect to evaluation runs and the Experiment Matrix UI.

```mermaid
flowchart TD
  Configs[Experiment configs] --> BM25[bm25_baseline]
  Configs --> Dense[dense_baseline]
  Configs --> Hybrid[hybrid_rrf_default]
  Configs --> Rerank[hybrid_rerank_default]

  BM25 --> EvalBM25[Run evaluation]
  Dense --> EvalDense[Run evaluation]
  Hybrid --> EvalHybrid[Run evaluation]
  Rerank --> EvalRerank[Run evaluation]

  EvalBM25 --> Runs[EvaluationRun rows]
  EvalDense --> Runs
  EvalHybrid --> Runs
  EvalRerank --> Runs

  Runs --> Report[Comparison report]
  Runs --> Matrix[Experiment Matrix UI]
  Report --> Matrix
```

## Notes

- Best-by-metric indicators are computed from real evaluation runs.
- Aletheia does not hardcode winners.
- Missing metrics remain unavailable.
