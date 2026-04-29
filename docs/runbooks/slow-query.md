# Runbook: Slow Query

## Symptoms

- Search Lab query takes longer than expected.
- Query Trace UI shows high latency.
- System events include `SLOW_SEARCH_QUERY`.
- Hybrid rerank mode is much slower than BM25 or hybrid.

## Likely Causes

- Cold embedding model
- Cold reranker model
- Large `rerank_top_n`
- OpenSearch latency
- Qdrant latency
- CPU-only local model inference
- Large candidate depth

## How To Inspect

1. Open Query Trace UI.
2. Find the trace for the slow query.
3. Inspect stage latency and candidate counts.
4. Check whether the mode was `dense`, `hybrid`, or `hybrid_rerank`.
5. Check system events for `SLOW_SEARCH_QUERY`.
6. Compare the same query across retrieval modes if real traces exist.

## Mitigation

- Warm the embedding model before dense or hybrid tests.
- Warm the reranker before hybrid rerank tests.
- Reduce `rerank_top_n`.
- Use `hybrid` instead of `hybrid_rerank` when latency matters.
- Reduce candidate depth for local debugging.
- Confirm OpenSearch and Qdrant are healthy.
- Run the full local stack rather than public snapshot mode for live timing work.

## Notes

Public snapshot mode shows exported timings from real local runs. It does not execute live queries.
