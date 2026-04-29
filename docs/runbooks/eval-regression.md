# Runbook: Evaluation Regression

## Symptoms

- Recall@10 drops.
- MRR@10 drops.
- NDCG@10 drops.
- Golden smoke reports warnings.
- Evaluation run has failed queries.
- A known query retrieves different documents than before.

## Check Qrels Alignment

Confirm evaluation still maps chunk results to parent document IDs and deduplicates document IDs before scoring.

Do not hide bad metrics. A regression should remain visible until understood.

## Check Index Version

Confirm the evaluation used the intended index version:

- active index version
- lexical index name
- vector collection name
- document, chunk, and vector counts

## Check Retrieval Parameters

Compare:

- retrieval mode
- top_k
- candidate_k
- BM25 candidate depth
- dense candidate depth
- hybrid candidate depth
- rerank_top_n
- rrf_k

## Compare Traces

Use Query Trace UI to inspect:

- BM25 candidates
- dense candidates
- fusion ranks
- rerank ranks
- final ranking
- relevant documents

## Run Local Checks

Run golden smoke:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/run-golden-smoke.ps1 -Mode hybrid -QueryLimit 5 -TopK 10 -Notes "Regression check"
```

Run a limited evaluation if more context is needed.

## Inspect Reports

Open evaluation reports under `reports/evaluations` and compare query-level failures, retrieved document IDs, relevant document IDs, and trace IDs.

## Resolution

Once the cause is understood, fix the retrieval, indexing, or configuration issue and rerun a local smoke check. Do not overwrite or relabel metrics to make the dashboard look better.
