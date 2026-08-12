# Final Resume Copy

This is the direct-use resume copy package for Aletheia. It is optimized for SWE, backend, ML infrastructure, and search infrastructure roles.

## Recommended Final Resume Entry

Project: Aletheia: Hybrid Retrieval, Reranking & Evaluation Platform

Links: GitHub: https://github.com/YuvrajKashyap/aletheia | Demo: https://aletheia.yuvrajkashyap.com

Tech stack: FastAPI, Next.js, PostgreSQL, Redis/RQ, OpenSearch, Qdrant, Docker, SQLAlchemy, Alembic, TypeScript, BEIR SciFact, local embedding and reranking models.

- Built a production-style hybrid retrieval platform using FastAPI, PostgreSQL, Redis/RQ, OpenSearch, Qdrant, and Next.js to compare BM25, dense vector search, Reciprocal Rank Fusion, and cross-encoder reranking over BEIR SciFact.
- Implemented retrieval evaluation and observability with query traces, rank/score provenance, document-level qrels scoring, Recall@K/MRR/NDCG metrics, async evaluation jobs, experiment comparison, and saved-query replay workflows.
- Shipped a public Vercel snapshot demo backed by real exported traces, evaluation reports, index metadata, and replay results, with CI quality gates, Dockerized local infrastructure, deployment docs, and audit tooling.

## Ultra-Compact Two-Bullet Version

- Built Aletheia, a FastAPI/Next.js retrieval platform with PostgreSQL, Redis/RQ, OpenSearch, Qdrant, BM25, dense vectors, RRF, reranking, query tracing, evaluation dashboards, and replay tooling.
- Evaluated BEIR SciFact using document-level qrels across BM25, dense, hybrid RRF, and sampled hybrid rerank runs, producing Recall@K, MRR@10, NDCG@10, and latency reports.

## Backend-Heavy Version

- Built a FastAPI backend with PostgreSQL, SQLAlchemy, Alembic, Redis/RQ, and Docker to orchestrate ingestion, chunking, index builds, evaluation jobs, experiment comparisons, replay jobs, and system events.
- Implemented versioned index lifecycle workflows for OpenSearch and Qdrant, including index jobs, active version state, activation/rollback semantics, and UI-visible operational status.
- Added production-style quality gates with 343 backend tests in current CI, Ruff, frontend typecheck/lint/build, doctor checks, release readiness docs, and repository audit tooling.

## ML/Search-Heavy Version

- Implemented BM25, dense vector retrieval, hybrid Reciprocal Rank Fusion, and cross-encoder reranking using OpenSearch, Qdrant, `BAAI/bge-small-en-v1.5`, and `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Evaluated BEIR SciFact with 5,183 documents, 300 benchmark queries, and 339 qrels, mapping retrieved chunks back to parent documents before document-level Recall@K, MRR@10, and NDCG@10 scoring.
- Produced reproducible benchmarks showing hybrid RRF Recall@10 of 0.8429 over the full 300-query SciFact run, with hybrid rerank kept separate as a sampled 50-query CPU rerank benchmark.

## Full-Stack And Product Version

- Built a Next.js dashboard with Search Lab, Query Trace UI, Evaluation Dashboard, Experiment Matrix, Index Console, Dataset Browser, Replay Lab, and System Health views over real API or exported snapshot data.
- Created a public Vercel snapshot demo using real exported outputs from the local full stack while disabling live retrieval, reranking, indexing, evaluation, replay, and admin jobs publicly.
- Delivered a polished project repository with screenshots, Mermaid architecture diagrams, CI, benchmark docs, runbooks, release readiness checks, and interview documentation.

## One-Line Resume Summary

Built Aletheia, a FastAPI/Next.js retrieval platform for BM25, dense, hybrid RRF, reranking, tracing, evaluation, and replay over BEIR SciFact.

## What Not To Put On Resume

- Do not describe Aletheia as a chatbot.
- Do not describe it as a generic RAG app.
- Do not claim production users.
- Do not claim public live backend hosting.
- Do not claim public live arbitrary retrieval.
- Do not claim web-scale traffic or corpus scale.
- Do not claim Atlas integration is implemented.
- Do not use generic "AI-powered" wording.
- Do not present sampled hybrid rerank metrics as full 300-query benchmark metrics.
