# Benchmark Results

This document defines the final benchmark methodology and where generated results should be placed. It does not contain final metrics until the benchmark suite is run locally and reviewed.

## Methodology

The benchmark suite uses BEIR SciFact with:

- 5,183 documents
- 300 benchmark queries
- 339 qrels
- document-level relevance judgments

Aletheia retrieves chunks, maps chunk hits back to parent document IDs, deduplicates document IDs, then scores against qrels.

## Benchmark Modes

The default suite includes:

- BM25 full SciFact benchmark
- Dense full SciFact benchmark
- Hybrid RRF full SciFact benchmark
- Hybrid rerank sampled SciFact benchmark

Hybrid rerank is sampled by default because local CPU reranking can be slow. Sampled and full results must not be presented as equivalent.

## Metrics

The suite records:

- Recall@5
- Recall@10
- MRR@10
- NDCG@10
- average latency
- p50 latency
- p95 latency
- failed query count

## Latency Caveats

Latency depends on:

- local CPU performance
- model warmup
- candidate depth
- `rerank_top_n`
- OpenSearch and Qdrant state
- whether dense and rerank models are already cached

Latency should be reported as measured local runtime, not a hosted SLA.

## Final Selected Results

Populate after running:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/run-final-benchmark-suite.ps1
```

Copy the generated Markdown table from the benchmark report or CLI output.

Do not invent metrics. Do not hide weak metrics. Do not mix full and sampled results without labeling scope.
