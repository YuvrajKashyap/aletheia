# Resume Positioning

This document translates Aletheia into concise resume, recruiter, LinkedIn, and project-card language. It preserves the project's actual scope: a retrieval, ranking, evaluation, and search observability platform with a public snapshot demo and a full local live stack.

## One-Line Project Description

1. Resume style: Built Aletheia, a production-style hybrid retrieval and search observability platform comparing BM25, dense vector retrieval, hybrid RRF, and cross-encoder reranking over BEIR SciFact with real traces and evaluation metrics.
2. GitHub style: Hybrid retrieval, reranking, evaluation, and search observability platform using FastAPI, Next.js, PostgreSQL, Redis/RQ, OpenSearch, Qdrant, and BEIR SciFact.
3. Recruiter style: Aletheia is a full-stack search infrastructure project that shows how retrieval systems are indexed, traced, evaluated, compared, and debugged.
4. ML systems style: Aletheia evaluates lexical, dense, hybrid, and reranked retrieval using document-level SciFact qrels, rank fusion, query traces, and reproducible benchmark reports.
5. Backend/search infrastructure style: Aletheia is a FastAPI-backed retrieval platform with versioned indexes, async jobs, search traces, evaluation runs, replay tooling, and a public snapshot demo.

## Resume Bullets

### Set 1: SWE And Backend Focused

- Built a FastAPI retrieval platform with PostgreSQL metadata, SQLAlchemy/Alembic migrations, Redis/RQ background jobs, and admin-safe workflows for ingestion, indexing, evaluation, experiment comparison, and replay.
- Implemented production-style index orchestration with versioned OpenSearch and Qdrant assets, explicit activation/rollback state, job tracking, system events, and failure-visible UI surfaces.
- Added CI and local quality gates covering 343 backend tests, Ruff, frontend typecheck/lint/build, doctor checks, release readiness docs, and repo audit tooling.

### Set 2: ML And Search Focused

- Implemented BM25, dense vector retrieval, hybrid Reciprocal Rank Fusion, and cross-encoder reranking with OpenSearch, Qdrant, `BAAI/bge-small-en-v1.5`, and `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Evaluated BEIR SciFact retrieval over 5,183 documents, 300 benchmark queries, and 339 qrels, mapping chunk hits back to parent document IDs before Recall@5, Recall@10, MRR@10, and NDCG@10 scoring.
- Built query tracing and candidate provenance views that expose BM25 rank/score, dense rank/score, fusion rank/score, reranker rank/score, latency, and trace-linked evaluation results.

### Set 3: Full-Stack And Platform Focused

- Built a Next.js dashboard for Search Lab, Query Traces, Evaluations, Experiments, Index Console, Dataset Browser, Replay Lab, and System Health using real API or exported snapshot data.
- Shipped a public Vercel snapshot demo using real outputs exported from the full local pipeline while disabling live retrieval, reranking, rebuilds, evaluation jobs, replay jobs, and admin actions publicly.
- Created technical docs, Mermaid architecture diagrams, screenshot assets, demo scripts, benchmark methodology, runbooks, and release-readiness checks for a recruiter-readable portfolio project.

### Set 4: Ultra-Compact Resume Version

- Built Aletheia, a FastAPI/Next.js hybrid retrieval platform with PostgreSQL, Redis/RQ, OpenSearch, Qdrant, BM25, dense vectors, RRF, reranking, query tracing, evaluation dashboards, and replay tooling.
- Evaluated BEIR SciFact with document-level qrels across BM25, dense, hybrid RRF, and sampled hybrid rerank runs, producing reproducible Recall@5/10, MRR@10, NDCG@10, and latency reports.

### Set 5: Aggressive Tier-One Version

- Designed and implemented a production-style search infrastructure platform that compares lexical, vector, hybrid, and reranked retrieval with versioned indexes, async jobs, trace-level observability, and qrels-backed evaluation.
- Built an end-to-end retrieval evaluation stack using FastAPI, PostgreSQL, Redis/RQ, OpenSearch, Qdrant, local embedding/reranking models, Next.js dashboards, CI quality gates, and a public snapshot demo backed by real exported pipeline outputs.
- Benchmarked BEIR SciFact over full 300-query BM25, dense, and hybrid runs, with hybrid RRF achieving the strongest full-run Recall@10; kept hybrid rerank labeled as a 50-query sampled CPU rerank benchmark.

## Recommended Final Resume Version

Recommended for SWE/backend/ML infrastructure internship or new grad roles:

- Built Aletheia, a FastAPI/Next.js hybrid retrieval platform with PostgreSQL, Redis/RQ, OpenSearch, Qdrant, BM25, dense vectors, RRF, reranking, query tracing, evaluation dashboards, and replay tooling.
- Evaluated BEIR SciFact with document-level qrels across BM25, dense, hybrid RRF, and sampled hybrid rerank runs, producing reproducible Recall@5/10, MRR@10, NDCG@10, and latency reports.
- Shipped a public Vercel snapshot demo using real outputs exported from the full local pipeline while disabling live retrieval, reranking, rebuilds, evaluation jobs, replay jobs, and admin actions publicly.

Why these work: they cover backend depth, search/ML correctness, full-stack product work, public demo maturity, and honest infrastructure tradeoffs without claiming production users or public live backend hosting.

## Short Project Card

Title: Aletheia

Subtitle: Hybrid Retrieval, Reranking & Evaluation Platform

Description: Aletheia is a production-style search infrastructure project for comparing BM25, dense retrieval, hybrid RRF, and cross-encoder reranking over BEIR SciFact. It includes query tracing, evaluation dashboards, experiment comparison, replay tooling, index observability, and a public snapshot demo backed by real exported local outputs.

Tech stack: FastAPI, Next.js, PostgreSQL, Redis/RQ, OpenSearch, Qdrant, SQLAlchemy, Alembic, TypeScript, Tailwind CSS, BEIR SciFact, sentence-transformers.

Links:

- Demo: https://aletheia.yuvrajkashyap.com
- GitHub: https://github.com/YuvrajKashyap/aletheia
- Docs: `docs/docs-index.md`

## GitHub Repo Description

Production-style hybrid retrieval, reranking, evaluation, and search observability platform using FastAPI, Next.js, PostgreSQL, Redis/RQ, OpenSearch, Qdrant, and BEIR SciFact.

Suggested topics:

- `fastapi`
- `nextjs`
- `opensearch`
- `qdrant`
- `redis`
- `information-retrieval`
- `search`
- `evaluation`
- `machine-learning`
- `retrieval`
- `reranking`

## LinkedIn Project Entry

Title: Aletheia: Hybrid Retrieval, Reranking & Evaluation Platform

Date range: Month YYYY to Month YYYY

Description: Built a production-style search infrastructure platform for comparing BM25, dense retrieval, hybrid Reciprocal Rank Fusion, and cross-encoder reranking over BEIR SciFact. The system includes a FastAPI backend, Next.js dashboard, PostgreSQL metadata store, Redis/RQ async jobs, OpenSearch lexical search, Qdrant vector search, query tracing, evaluation reports, experiment comparison, replay tooling, and a public snapshot demo using real exported local outputs.

Highlights:

- Evaluates document-level SciFact qrels by mapping chunk hits back to parent documents before scoring.
- Supports Recall@5, Recall@10, MRR@10, NDCG@10, latency metrics, and query-level reports.
- Provides trace-level candidate provenance across lexical, dense, fusion, and rerank stages.
- Uses public snapshot mode for a cost-aware hosted demo while preserving a full local live stack.

Links:

- Demo: https://aletheia.yuvrajkashyap.com
- GitHub: https://github.com/YuvrajKashyap/aletheia
- Technical docs: `docs/docs-index.md`

## Recruiter Pitch

### 15-Second Pitch

Aletheia is a search infrastructure project, not a chatbot. It compares BM25, dense retrieval, hybrid RRF, and reranking over SciFact with real traces, evaluation metrics, dashboards, and a public snapshot demo.

### 30-Second Pitch

Aletheia is a production-style retrieval and evaluation platform built with FastAPI, Next.js, PostgreSQL, Redis/RQ, OpenSearch, and Qdrant. It indexes SciFact, runs BM25, dense, hybrid, and reranked retrieval, records query traces, evaluates against document-level qrels, and exposes the results through dashboards. The public demo is snapshot-backed from real local outputs so it is affordable to host without faking data.

### 60-Second Pitch

Aletheia is a full-stack search infrastructure project that focuses on retrieval quality and observability instead of answer generation. The backend uses FastAPI, PostgreSQL, Redis/RQ, OpenSearch, Qdrant, local embeddings, and a cross-encoder reranker. The system supports BM25, dense retrieval, hybrid Reciprocal Rank Fusion, and hybrid rerank modes. It evaluates BEIR SciFact with real document-level qrels, mapping retrieved chunks back to parent documents before computing Recall@5, Recall@10, MRR@10, NDCG@10, and latency. The frontend provides Search Lab, Query Traces, Evaluation Dashboard, Experiment Matrix, Index Console, Dataset Browser, Replay Lab, and System Health. The public demo is a Vercel snapshot mode using real exported local outputs, while the full live stack runs locally through Docker Compose.

## Caveats And Honesty Language

- Public snapshot demo: "The public demo uses real precomputed outputs exported from the full local Aletheia pipeline. It does not run public live arbitrary retrieval."
- Local full live stack: "The full live stack runs locally with FastAPI, Postgres, Redis/RQ, OpenSearch, Qdrant, embeddings, and reranking."
- Sampled rerank benchmark: "The hybrid rerank benchmark is a 50-query sampled CPU rerank run and is not directly comparable to full 300-query runs."
- Atlas future integration: "Atlas integration is future-facing. Atlas can later provide web corpora that Aletheia indexes, ranks, evaluates, and observes."
