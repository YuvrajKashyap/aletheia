# Interview Package

This is the compact interview prep guide for explaining Aletheia clearly and honestly.

## 15-Second Explanation

Aletheia is a retrieval, ranking, evaluation, and search observability platform. It is not a chatbot. It uses real BEIR SciFact benchmark data, shows real traces and metrics, and has a public snapshot demo backed by outputs exported from the full local stack.

## 30-Second Explanation

Aletheia is a FastAPI and Next.js platform for comparing BM25, dense retrieval, hybrid Reciprocal Rank Fusion, and cross-encoder reranking. It uses OpenSearch for lexical search, Qdrant for vector search, PostgreSQL for metadata, Redis/RQ for jobs, and BEIR SciFact for evaluation. The UI exposes Search Lab, query traces, evaluation dashboards, experiment comparison, index status, replay, and system health.

## 2-Minute Technical Explanation

The problem Aletheia solves is that retrieval systems are hard to reason about if you only see final ranked results. You need to know where candidates came from, how they were scored, how ranks changed, whether evaluation is correct, and whether index state is trustworthy.

Aletheia has a FastAPI backend, PostgreSQL metadata store, Redis/RQ jobs, OpenSearch BM25 index, Qdrant vector collection, local embedding model, and cross-encoder reranker. The Next.js frontend is a dashboard for search, traces, evaluations, experiments, indexes, datasets, replay, and system health.

The retrieval modes are BM25, dense, hybrid RRF, and hybrid rerank. Hybrid uses rank-based Reciprocal Rank Fusion instead of mixing raw BM25 and dense scores. Reranking only applies to the top candidate set because cross-encoder scoring is more expensive.

Evaluation uses BEIR SciFact. SciFact qrels are document-level, while Aletheia retrieves chunks, so the evaluator maps chunk hits back to parent documents and deduplicates before scoring Recall@5, Recall@10, MRR@10, NDCG@10, and latency.

The public demo is snapshot-backed. It uses real exported outputs from the full local pipeline and disables live retrieval, reranking, indexing, evaluation jobs, replay jobs, and admin actions publicly. The full live stack runs locally. The main lesson is that a credible retrieval platform needs backend orchestration, evaluation correctness, traceability, and honest operational boundaries.

## 5-Minute Deep Dive

### Data Model

- Documents, chunks, benchmark queries, qrels, index versions, index jobs, queries, traces, retrieval candidates, evaluation runs, evaluation query results, experiment configs, replay runs, system events, and worker heartbeats are stored as backend-owned data.
- PostgreSQL is the system of record for metadata and run history.
- FastAPI owns all backend logic. The frontend does not compute official metrics or talk directly to database, OpenSearch, or Qdrant.

### Ingestion And Chunking

- SciFact is loaded from real BEIR data.
- The corpus has 5,183 documents, 300 benchmark queries, and 339 qrels.
- SciFact uses document-level chunking in this project because its qrels are document-level.
- This keeps evaluation alignment clear and avoids rewarding multiple chunks from the same document as multiple relevant hits.

### Index Versioning

- Indexes are versioned assets.
- Index jobs track lexical and vector build progress.
- Active index changes are explicit.
- Failed or partial builds should not silently become active.
- Rollback is based on selecting a prior valid index version.

### BM25

- BM25 uses OpenSearch.
- It is strong for exact terms, domain terminology, and short factual queries.
- In the recorded benchmark, BM25 was the fastest full-run mode.

### Dense Retrieval

- Dense retrieval uses `BAAI/bge-small-en-v1.5` embeddings and Qdrant.
- It captures semantic similarity beyond exact term overlap.
- It has higher local CPU latency because embedding calls run locally.

### Hybrid RRF

- Hybrid retrieval combines BM25 and dense candidate lists using Reciprocal Rank Fusion.
- RRF uses ranks rather than raw scores, which avoids mixing incomparable BM25 and vector similarity score scales.
- In the recorded full 300-query benchmark, hybrid RRF achieved the strongest Recall@10.

### Reranking

- Hybrid rerank takes a top candidate set and applies `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Cross-encoders score query-document pairs directly, which can improve ordering but costs more latency.
- The recorded rerank benchmark is sampled at 50 queries and is not directly comparable to the full 300-query rows.

### Query Tracing

- Each search can produce a query row, trace row, retrieval candidates, and trace JSON.
- Trace views show candidate source, ranks, scores, fusion, rerank movement, latency, and stage metadata.
- This makes relevance issues debuggable instead of opaque.

### Evaluation

- Evaluation runs queries through the real search service.
- Retrieved chunks map back to parent document IDs.
- Duplicate document IDs are removed before scoring.
- Metrics include Recall@5, Recall@10, MRR@10, NDCG@10, and latency.

### Async Jobs

- Redis/RQ supports ingestion, indexing, evaluation, comparison, and replay jobs.
- Jobs expose IDs and status.
- Worker heartbeat and system events make background execution observable.

### Frontend Product Surfaces

- Search Lab: curated or live retrieval workflows depending on mode.
- Query Traces: candidate provenance and rank movement.
- Evaluations: metrics, query results, and reports.
- Experiments: mode comparison and best-by-metric views.
- Index Console: versioned index status and jobs.
- Dataset Browser: SciFact docs, chunks, queries, and qrels.
- Replay Lab: saved query and golden query replay.
- System Health: local live stack and public snapshot state.

### Public Snapshot Demo

- Public Vercel demo uses real static JSON exported from the full local pipeline.
- It is intentionally read-only for expensive actions.
- It is not fake, but it is also not a publicly hosted live search cluster.

## What I Would Whiteboard

1. User sends a query to the Next.js UI.
2. UI calls FastAPI in live mode, or reads exported snapshot data in public demo mode.
3. FastAPI stores a query row and selects retrieval mode.
4. BM25 path queries OpenSearch.
5. Dense path embeds query text and searches Qdrant.
6. Hybrid path fuses BM25 and dense rankings with RRF.
7. Hybrid rerank path sends top candidates to the cross-encoder reranker.
8. Candidates are persisted with ranks, scores, sources, and metadata.
9. QueryTrace and trace JSON capture stage-level details.
10. Evaluation maps retrieved chunks to parent documents, deduplicates document IDs, and compares against qrels.

## Key Numbers To Remember

- 5,183 SciFact documents.
- 5,183 chunks in the document-level chunking strategy.
- 300 benchmark queries.
- 339 qrels.
- 4 retrieval modes: BM25, dense, hybrid RRF, hybrid rerank.
- BM25 was fastest in the recorded benchmark.
- Hybrid RRF had the strongest full-run Recall@10 in the recorded benchmark.
- Dense had the strongest full-run Recall@5, MRR@10, and NDCG@10 in the recorded table.
- Hybrid rerank is sampled at 50 queries and is not directly comparable to full 300-query rows.
- Current CI includes 343 backend tests. Check latest CI for the exact count.
- Public demo is snapshot-backed.
- Full live stack runs locally.

## Honest Caveats

- The public demo is snapshot-backed with real exported outputs.
- The full live stack currently runs locally.
- The hybrid rerank benchmark is sampled.
- Local CPU model latency is higher than optimized hosted inference would be.
- There is no claim of production traffic or production users.
- Atlas integration is future-facing and not implemented in this repo.
