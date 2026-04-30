# System Design Walkthrough

This document frames Aletheia as a system-design interview answer.

## Requirements

- Support BM25, dense, hybrid RRF, and hybrid rerank retrieval modes.
- Store documents, chunks, benchmark queries, qrels, traces, candidates, indexes, jobs, evaluations, experiments, replay runs, and system events.
- Expose a dashboard for search, traces, evaluations, experiments, indexes, datasets, replay, and system health.
- Evaluate retrieval against real document-level qrels.
- Keep expensive jobs out of synchronous request paths.
- Preserve public demo honesty through snapshot mode.

## Constraints

- FastAPI owns backend logic.
- PostgreSQL is the metadata source of truth.
- OpenSearch handles BM25.
- Qdrant handles vector search.
- Redis/RQ handles async jobs.
- Next.js is the dashboard, not the owner of backend metrics.
- Public hosted demo is snapshot-backed and does not run live retrieval jobs.

## Architecture

- Browser uses the Next.js frontend.
- In live mode, Next.js calls FastAPI under `/api/v1`.
- FastAPI reads/writes PostgreSQL and calls OpenSearch, Qdrant, Redis/RQ, embedding model, and reranker.
- RQ workers run ingestion, indexing, evaluation, comparison, and replay jobs.
- In public snapshot mode, Next.js reads static JSON under `/demo-data`.

## Data Model

- `Document` and `Chunk` represent corpus content.
- `BenchmarkQuery` and qrels represent evaluation inputs.
- `IndexVersion` and `IndexJob` represent index lifecycle.
- `Query`, `QueryTrace`, and `RetrievalCandidate` represent search execution.
- `EvaluationRun`, `EvaluationQueryResult`, and `EvaluationReport` represent scoring.
- `ExperimentConfig` and comparison reports represent mode comparisons.
- `SavedQuery` and `QueryReplay` represent replay workflows.
- `SystemEvent` and worker heartbeat rows represent operational visibility.

## Indexing Pipeline

- Load SciFact documents, queries, and qrels.
- Normalize text.
- Create document-level chunks for SciFact qrels alignment.
- Create index version.
- Build OpenSearch lexical index.
- Generate embeddings.
- Build Qdrant vector collection.
- Update index job and index version metadata.
- Explicitly activate the version.

## Serving Path

- Query arrives at FastAPI.
- Request selects retrieval mode.
- BM25 queries OpenSearch.
- Dense retrieval embeds the query and searches Qdrant.
- Hybrid RRF fuses BM25 and dense ranked lists.
- Hybrid rerank reranks top candidates with a cross-encoder.
- Results and candidate provenance are persisted.
- Query trace captures stage metadata and latency.

## Async Job Model

- Redis/RQ runs expensive tasks outside normal API request handling.
- Jobs include ingestion, lexical indexing, vector indexing, evaluation, experiment comparison, and replay.
- Job IDs and statuses are visible to the UI.
- Worker heartbeat and system events help distinguish queued, running, failed, and stale work.

## Observability

- Query traces show candidates, sources, ranks, scores, and rank movement.
- System events capture slow queries and operational conditions.
- Index console shows index versions, active state, counts, and jobs.
- Replay Lab supports regression-style inspection of saved queries.

## Evaluation

- BEIR SciFact has document-level qrels.
- Aletheia retrieves chunks.
- Evaluation maps chunk hits to parent document IDs.
- Duplicate document IDs are removed before scoring.
- Metrics include Recall@5, Recall@10, MRR@10, NDCG@10, and latency.

## Deployment Model

- Local live stack runs FastAPI, Next.js, Postgres, Redis/RQ, OpenSearch, Qdrant, embedding model, reranker, and worker.
- Public demo runs on Vercel in snapshot mode using real exported JSON.
- Neon has hosted schema, but the full search/worker/model stack is not hosted publicly.

## Scaling Plan

- Use managed Postgres, Redis, OpenSearch, and Qdrant.
- Run API and workers as separate services.
- Add worker pools by job type.
- Add model-serving processes with warm caches.
- Add request caching for common queries and scenario demos.
- Add authentication, admin roles, rate limits, and tenant boundaries.
- Add observability for traces, logs, metrics, queues, and model latency.

## Failure Modes

- OpenSearch unavailable: BM25 and hybrid retrieval degrade or fail clearly.
- Qdrant unavailable: dense and hybrid retrieval degrade or fail clearly.
- Redis unavailable: async jobs cannot enqueue or run.
- Model cold start: dense or rerank latency spikes.
- Partial index build: version should not auto-activate.
- Evaluation mismatch: qrels mapping must be inspected before trusting metrics.

## Tradeoffs

- RQ is simpler than Celery for this project, but Celery may fit larger distributed workloads.
- RRF avoids raw score calibration, but it does not learn query-specific weights.
- Local models avoid paid APIs, but local CPU latency is higher.
- Snapshot demo avoids always-on infra cost, but public users cannot run arbitrary live retrieval.
