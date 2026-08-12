# Review Notes

This guide explains how to review Aletheia quickly without needing to run the local stack.

## What To Click In The Public Demo

Public demo: https://aletheia.yuvrajkashyap.com

Suggested path:

1. Open `/` for the Overview.
2. Open `/search` for curated retrieval scenarios.
3. Open `/traces` to inspect a query trace.
4. Open `/evaluations` to view real benchmark metrics.
5. Open `/experiments` to compare retrieval modes.
6. Open `/indexes` to see index metadata.
7. Open `/datasets` to inspect SciFact documents, chunks, queries, and qrels.
8. Open `/replay` to inspect saved query replay outputs.
9. Open `/system` to see public snapshot versus local live stack status.

## What To Notice

- This is not a chatbot and not a thin RAG wrapper.
- The project focuses on retrieval, ranking, evaluation, tracing, and observability.
- The UI is backed by real local outputs exported into public snapshot mode.
- The benchmark table uses real SciFact evaluation results.
- The dashboard shows internal retrieval details, not just a final answer.
- The repository includes docs, diagrams, tests, CI, screenshots, and audit tooling.

## What Is Intentionally Disabled Publicly

The public demo does not run live arbitrary retrieval. It does not expose live reranking, index rebuilds, evaluation jobs, replay jobs, or admin actions. Those actions are disabled publicly to avoid always-on OpenSearch, Qdrant, Redis, worker, and ML model hosting costs.

This is intentional. The hosted demo is snapshot-backed with real exported outputs, while the full live stack runs locally.

## What The Full Local System Includes

- FastAPI backend.
- PostgreSQL metadata store.
- Redis/RQ background jobs.
- OpenSearch BM25 retrieval.
- Qdrant vector retrieval.
- Local embedding model: `BAAI/bge-small-en-v1.5`.
- Local reranker: `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- Next.js dashboard.
- BEIR SciFact corpus, benchmark queries, and qrels.
- Offline and async evaluation flows.
- Experiment comparison, replay, tracing, and system health views.

## Why It Is A Serious Project

Aletheia demonstrates backend systems, ML/search integration, evaluation correctness, and product-quality dashboard work in one repository. It uses real retrieval infrastructure instead of mocked search results, and it treats evaluation metrics as generated artifacts from real runs.

Relevant role signals:

- SWE/backend: FastAPI, PostgreSQL, SQLAlchemy, Alembic, Redis/RQ, job orchestration, CI, audit scripts.
- ML/search infrastructure: OpenSearch, Qdrant, embeddings, reranking, RRF, BEIR SciFact, document-level qrels.
- Full-stack/platform: Next.js dashboards, trace UI, system health, Vercel public demo, screenshots, docs.

## Review In 3 Minutes

1. Read the top of `README.md`.
2. Open the public demo Overview.
3. Visit Search Lab and Query Traces.
4. Scan the benchmark table.
5. Open the screenshots section.

This should show that the project is a real retrieval platform with a polished public demo and honest caveats.

## Review Technically

1. Read `docs/architecture.md`.
2. Read `docs/retrieval-design.md`.
3. Read `docs/evaluation.md`.
4. Review `docs/benchmark-results.md`.
5. Inspect `docs/diagrams/README.md`.
6. Check `.github/workflows/ci.yml`.
7. Review `scripts/powershell/repo-audit.ps1`.

## Caveats To Preserve

- Public demo is snapshot-backed.
- No public live arbitrary retrieval is claimed.
- No fake data is used.
- Full live stack runs locally.
- Hybrid rerank benchmark is sampled and not directly comparable to full 300-query rows.
- Atlas integration is future-facing and not implemented in this repo.
