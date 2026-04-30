# Scale Plan

This document explains how Aletheia would scale beyond the current local live stack and public snapshot demo. It describes future work, not current hosted production infrastructure.

## Current Baseline

- Full live stack runs locally with Docker Compose and local processes.
- Public demo runs on Vercel in snapshot mode.
- Snapshot mode serves real exported outputs from the local pipeline.
- Public demo does not expose live retrieval, reranking, indexing, evaluation, replay, or admin jobs.

## Hosted FastAPI And Workers

- Deploy FastAPI as a dedicated API service.
- Deploy RQ workers as separate services.
- Scale API and workers independently.
- Split worker pools by job type if needed: indexing, evaluation, replay, and export.
- Keep FastAPI as the only backend boundary for official logic.

## Managed Postgres

- Use managed Postgres such as Neon for metadata.
- Keep SQLAlchemy and Alembic migrations.
- Add backup, migration, and rollback procedures.
- Monitor query latency and table growth.

## Managed Redis

- Use managed Redis for RQ queues.
- Separate queues by workload if needed.
- Add retry policy, dead-letter inspection, and queue latency dashboards.

## Managed OpenSearch

- Use managed OpenSearch for BM25 at larger scale.
- Plan shard count, analyzers, mappings, and replica strategy.
- Keep index versions explicit.
- Promote indexes through controlled activation.

## Managed Qdrant

- Use Qdrant Cloud or hosted Qdrant for vector retrieval.
- Tune collection configuration, payload indexes, and batch ingestion.
- Track vector counts and collection names per index version.

## Model Serving Optimization

- Move embedding and reranking models into warm worker or model-serving processes.
- Batch embedding requests where practical.
- Cache query embeddings for repeated benchmark or replay queries.
- Keep reranking top-N bounded.
- Consider GPU or optimized inference if latency becomes a product requirement.

## Caching

- Cache repeated query outputs for demo or benchmark scenarios.
- Cache embeddings for repeated queries.
- Cache index metadata and health summaries.
- Use cache invalidation tied to active index version changes.

## Batching

- Batch document embeddings during vector index builds.
- Batch replay and evaluation jobs.
- Keep user-facing search paths responsive by limiting synchronous heavy work.

## Index Version Promotion

- Build new lexical and vector assets under a new version.
- Validate counts and smoke checks.
- Activate only after successful build and verification.
- Roll back by reactivating a prior valid index version.

## Observability

- Add structured logs, request IDs, trace IDs, queue metrics, worker heartbeat metrics, and model latency metrics.
- Monitor OpenSearch and Qdrant latency separately.
- Track slow query system events.
- Add alerts for failed jobs, stale workers, and index build failures.

## Auth And Multi-Tenant Controls

- Add authentication before exposing admin actions.
- Separate read-only public demo actions from expensive write/admin actions.
- Add admin roles, rate limits, audit logs, and tenant boundaries if multiple users or organizations are supported.

## Larger Datasets

- Add ingestion validation and dedupe.
- Partition larger corpora by dataset, index version, and source metadata.
- Add stronger sampling and benchmark reporting for large evaluation sets.
- Track index storage and rebuild cost.

## Cost-Aware Tradeoffs

- Snapshot mode remains useful for demos because it is cheap, stable, and honest.
- Hosted live mode requires always-on search, vector, queue, worker, and model infrastructure.
- Reranking should stay bounded or async if latency and cost matter.
- Managed search/vector providers simplify operations but increase cost.

## Atlas Web Corpus Path

Atlas integration is future-facing. If Atlas feeds web-scale corpora into Aletheia:

- Atlas handles crawl frontier, robots.txt, politeness, extraction, dedupe, and freshness.
- Aletheia treats Atlas pages as a dataset such as `atlas_web_v1`.
- Documents become pages, chunks become sections or paragraphs, and metadata includes URL, domain, crawl timestamp, and content hash.
- Evaluation would require human-labeled qrels, editorial test sets, or replay-based qualitative validation.
- Search infrastructure would need stronger scaling, freshness, and abuse controls.

## What Stays The Same Conceptually

- FastAPI owns backend logic.
- PostgreSQL stores metadata.
- OpenSearch handles BM25.
- Qdrant handles vector retrieval.
- Redis/RQ handles async jobs.
- Evaluation maps retrieved chunks back to judged documents when qrels are document-level.
- Public snapshots can still be generated from real live outputs.
