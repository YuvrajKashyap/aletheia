# Final Portfolio Card Copy

## Title

Aletheia

## Subtitle

Hybrid Retrieval, Reranking & Evaluation Platform

## Short Description

Aletheia is a production-style search infrastructure platform for comparing BM25, dense vector retrieval, hybrid RRF, and cross-encoder reranking over BEIR SciFact with real traces, evaluation metrics, and index observability.

## Long Description

Aletheia is a full-stack retrieval and ranking platform built with FastAPI, Next.js, PostgreSQL, Redis/RQ, OpenSearch, and Qdrant. It supports BM25, dense vector search, hybrid Reciprocal Rank Fusion, and hybrid rerank modes, then exposes query traces, evaluation reports, experiment comparisons, index metadata, dataset inspection, replay workflows, and system health through a polished dashboard. The public demo runs in snapshot mode using real outputs exported from the full local pipeline.

## Problem

Retrieval systems are hard to debug if you only see final ranked results. Engineers need to know where candidates came from, how ranks changed, whether metrics align with qrels, which index version served the query, and how different retrieval modes compare.

## Solution

Aletheia compares BM25, dense retrieval, hybrid RRF, and reranking while exposing the internal retrieval pipeline. It includes Search Lab, Query Traces, Evaluation Dashboard, Experiment Matrix, Index Console, Dataset Browser, Replay Lab, and System Health.

## Technical Highlights

- FastAPI backend with typed API schemas.
- PostgreSQL metadata store through SQLAlchemy and Alembic.
- Redis/RQ async jobs for ingestion, indexing, evaluation, comparison, and replay.
- OpenSearch BM25 lexical retrieval.
- Qdrant dense vector retrieval.
- Local embeddings and reranking models.
- Next.js dashboard for traces, metrics, indexes, datasets, replay, and health.
- Docker-based local live stack.
- Vercel public snapshot demo using real exported outputs.
- CI, doctor checks, benchmark docs, diagrams, screenshots, and release readiness docs.

## Metrics And Evaluation

- Dataset: BEIR SciFact.
- Corpus: 5,183 documents.
- Benchmark queries: 300.
- Qrels: 339.
- Evaluation maps retrieved chunks back to parent documents for document-level scoring.
- Hybrid RRF full-run Recall@10: 0.8429.
- Dense full-run Recall@10: 0.8386.
- BM25 average latency: 54.8 ms.
- Hybrid rerank is a sampled 50-query benchmark and is not directly comparable to the full 300-query rows.

## Demo Mode Explanation

The public demo is snapshot-backed. It uses real exported traces, evaluations, index metadata, replay outputs, and dataset samples from the full local Aletheia pipeline. Live arbitrary search and admin jobs are disabled publicly to avoid always-on OpenSearch, Qdrant, Redis, worker, and model hosting costs. The full live stack runs locally.

## Tech Stack

FastAPI, Next.js, TypeScript, PostgreSQL, SQLAlchemy, Alembic, Redis/RQ, OpenSearch, Qdrant, Docker, Recharts, BEIR SciFact, `BAAI/bge-small-en-v1.5`, `cross-encoder/ms-marco-MiniLM-L-6-v2`.

## Links

- Demo: https://aletheia.yuvrajkashyap.com
- GitHub: https://github.com/YuvrajKashyap/aletheia
- Docs: `docs/docs-index.md`

## Suggested Screenshots

- Overview.
- Search Lab.
- Query Trace.
- Evaluation Dashboard.
- Experiment Matrix.

## Short Hover Or Preview Copy

1. Search infrastructure dashboard for hybrid retrieval, reranking, tracing, and SciFact evaluation.
2. Full-stack retrieval platform comparing BM25, dense vectors, RRF, and reranking with real qrels-backed metrics.
3. Production-style search observability project with FastAPI, Next.js, OpenSearch, Qdrant, Redis/RQ, and public snapshot demo.

## CTA Labels

- View Demo
- View GitHub
- Read Technical Docs
