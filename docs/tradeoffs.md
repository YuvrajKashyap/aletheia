# Tradeoffs

Aletheia is designed as a serious retrieval infrastructure project. The choices below favor correctness, inspectability, and realistic local operation over a simpler demo.

## FastAPI Backend

FastAPI owns backend logic. The frontend calls the API and does not talk directly to PostgreSQL, OpenSearch, Qdrant, or Redis.

This keeps retrieval, evaluation, indexing, and replay behavior centralized and testable.

## PostgreSQL With SQLAlchemy And Alembic

PostgreSQL stores metadata and evaluation records. SQLAlchemy provides explicit models and transactions. Alembic provides schema history.

Neon is used as hosted Postgres schema infrastructure, not as a platform-specific shortcut around the backend.

## Redis/RQ Instead Of Celery

RQ is sufficient for local async evaluation, indexing, replay, and comparison jobs. It is simpler to operate than Celery for this project size while still demonstrating production-style job boundaries.

At larger scale, a more advanced queue could be considered if scheduling, routing, retries, and observability needs outgrow RQ.

## OpenSearch For BM25

OpenSearch provides a real lexical retrieval engine with BM25 scoring and operational behavior closer to production search than in-memory matching.

## Qdrant For Dense Retrieval

Qdrant provides vector indexing and similarity search. Keeping dense retrieval separate from lexical retrieval makes score behavior and hybrid fusion easier to inspect.

## Local Models Instead Of Paid APIs

Embeddings use `BAAI/bge-small-en-v1.5`. Reranking uses `cross-encoder/ms-marco-MiniLM-L-6-v2`.

This keeps the system reproducible locally and avoids paid API dependencies for core retrieval.

## RRF Over Raw Score Fusion

BM25 and dense scores are not directly comparable. Reciprocal Rank Fusion combines ranked lists without pretending the raw score scales are equivalent.

## Rerank Top-N Only

Cross-encoder reranking is expensive relative to retrieval. Aletheia reranks only a bounded candidate set to expose the quality and latency tradeoff clearly.

## Document-Level Chunking For SciFact

SciFact qrels are document-level, and SciFact documents are short enough that document-level chunking is defensible. This reduces evaluation alignment risk.

For larger corpora, chunking should become more granular while preserving document-level evaluation mapping where qrels require it.

## Snapshot Public Demo

The public demo uses real exported outputs from the local full stack rather than always-on hosted search infrastructure.

This is intentional:

- avoids hosting OpenSearch, Qdrant, Redis, workers, and ML models full time
- keeps public data honest
- demonstrates real traces and metrics
- preserves the local full-stack path for live operation

## CI Scope

GitHub CI avoids Docker, search services, Redis, workers, model downloads, ingestion, indexing, and evaluation jobs. It remains a fast unit and build gate.

Full integration checks remain local through documented scripts.

## Larger Scale Changes

At larger scale, likely changes include:

- managed OpenSearch or equivalent lexical search
- hosted Qdrant or managed vector storage
- larger worker pool
- query and embedding cache
- authenticated admin controls
- multi-tenant boundaries
- centralized logs and traces
- stronger evaluation datasets
- scheduled regression evaluations
