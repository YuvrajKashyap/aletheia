# Demo Walkthrough

## Demo Goal

This walkthrough is for recruiters and engineers reviewing Aletheia as a production-style retrieval infrastructure project. It demonstrates search and ranking infrastructure, observability, evaluation correctness, experiment comparison, and the public snapshot demo model.

The public walkthrough uses the Vercel-hosted snapshot demo at https://aletheia.yuvrajkashyap.com. The hosted demo is backed by real precomputed outputs exported from the full local Aletheia pipeline. Live retrieval, reranking, index rebuilds, evaluation jobs, replay jobs, and admin actions are disabled publicly to avoid always-on search and ML infrastructure costs.

## 60 To 90 Second Recruiter Walkthrough

0:00 to 0:10, Overview:

"This is Aletheia, a hybrid retrieval, reranking, evaluation, and search observability platform. It is not a chatbot. The public demo is snapshot-backed, using real outputs exported from the full local stack."

0:10 to 0:25, Search Lab:

"In Search Lab, I can select a curated public demo query and inspect real precomputed retrieval results. The system supports BM25, dense retrieval, hybrid RRF, and hybrid reranking."

0:25 to 0:40, Query Trace:

"The trace view shows what happened inside retrieval: stage metadata, candidate provenance, ranks, scores, and trace JSON. This is built for debugging search behavior rather than generating answers."

0:40 to 0:55, Evaluations and Experiments:

"The evaluation dashboard shows qrels-backed SciFact metrics, including Recall@10, MRR@10, NDCG@10, and latency. The experiment matrix compares retrieval configurations using real completed runs."

0:55 to 1:10, Index, Dataset, Replay, and System Health:

"The index console shows versioned index metadata, the dataset browser shows SciFact documents, benchmark queries, and qrels, and Replay Lab shows saved golden queries and replay outputs. System Health explains what is hosted publicly and what runs in the local full stack."

1:10 to 1:30, Close:

"The full live stack runs locally with FastAPI, Postgres, Redis/RQ, OpenSearch, Qdrant, embeddings, and reranking. The public snapshot architecture is a cost-aware way to show real outputs without pretending the expensive search and ML infrastructure is hosted 24/7."

## 3 To 5 Minute Technical Walkthrough

1. Architecture:
   - Start on the Overview page.
   - Explain that the frontend is Next.js and the backend is FastAPI.
   - Explain that Postgres stores metadata, OpenSearch powers BM25, Qdrant powers dense retrieval, Redis/RQ handles background jobs, and local models handle embeddings and reranking.
   - Make clear that the public site is snapshot-backed while the full live stack runs locally.

2. Public snapshot mode:
   - Point to the banner.
   - Say that the public demo uses real exported outputs from local runs.
   - Mention that public arbitrary retrieval and admin jobs are disabled to avoid always-on infrastructure costs.

3. Search Lab:
   - Open `/search`.
   - Select a public demo scenario.
   - Show ranked results, score breakdown, metadata, latency, and trace link.
   - Explain that this is retrieval output, not answer generation.

4. Query Trace:
   - Open `/traces`.
   - Select a hybrid or hybrid rerank trace.
   - Show stage metadata, ranking summary, candidate provenance, and raw trace JSON if useful.
   - Explain how this helps debug ranking behavior.

5. Evaluation methodology:
   - Open `/evaluations`.
   - Show metric cards, charts, query results, and report JSON.
   - Explain that SciFact qrels are document-level, so chunk hits are mapped back to parent document IDs before scoring.

6. Experiment Matrix:
   - Open `/experiments`.
   - Show configs, best-by-metric cards, and comparison charts.
   - Explain that winners are computed from completed real evaluation runs, not hardcoded.

7. Index Console:
   - Open `/indexes`.
   - Show active index metadata, document/chunk/vector counts, OpenSearch index name, Qdrant collection name, and index jobs.
   - Explain index versioning and why failed or partial indexes should not auto-activate.

8. Dataset Browser:
   - Open `/datasets`.
   - Show SciFact documents, chunks, benchmark queries, and qrels.
   - Explain that public mode shows a representative exported sample while preserving real data.

9. Replay Lab:
   - Open `/replay`.
   - Show saved golden queries, replay metrics, matched or missed relevant documents, and trace link.
   - Explain that replay is trace-level regression/debugging support, not the same as a full evaluation run.

10. System Health:
    - Open `/system`.
    - Show hosted snapshot status, static data status, and local-only backend services.
    - Explain that this page is honest about public hosting boundaries.

11. GitHub, CI, and docs:
    - Open the README.
    - Point to CI, benchmark table, architecture docs, screenshots, and diagrams.
    - Explain that GitHub CI stays fast while heavier golden smoke and benchmark runs are local full-stack checks.

## Page-By-Page Talking Points

### Overview

- What to show: snapshot banner, real counts, active index metadata, datasets, evaluations, traces, replay counts.
- What to say: "This page summarizes the exported state from the full local pipeline."
- What not to overclaim: do not say the public overview is checking live backend services.

### Search Lab

- What to show: public demo scenarios, real exported result cards, score breakdown, trace metadata.
- What to say: "This uses real precomputed retrieval outputs. Arbitrary live search runs locally."
- What not to overclaim: do not say public users can run arbitrary live retrieval.

### Query Traces

- What to show: hybrid or hybrid rerank trace, ranking summary, candidate provenance, raw trace JSON.
- What to say: "Trace data explains how candidates moved through the retrieval pipeline."
- What not to overclaim: do not imply traces are generated live in public mode.

### Evaluations

- What to show: metrics, latency chart, query result rows, report JSON.
- What to say: "Metrics are qrels-backed and document-level."
- What not to overclaim: do not hide failed or weak metrics.

### Experiments

- What to show: configs, latest runs, best-by-metric cards, comparison charts.
- What to say: "This compares retrieval configurations using real completed evaluation runs."
- What not to overclaim: do not say one mode is always best across all corpora.

### Index Console

- What to show: active version, counts, lexical index, vector collection, local-only service state.
- What to say: "Indexes are versioned system assets with explicit activation."
- What not to overclaim: do not say public OpenSearch or Qdrant are live.

### Dataset Browser

- What to show: SciFact stats, document samples, chunks, benchmark queries, qrels.
- What to say: "The benchmark is grounded in real SciFact corpus and qrels."
- What not to overclaim: do not say the public sample contains every row unless showing the full local stack.

### Replay Lab

- What to show: saved golden query, replay detail, metrics, matched/missed relevant document IDs, trace link.
- What to say: "Replay supports trace-level regression and debugging."
- What not to overclaim: do not present replay as a replacement for full evaluation.

### System Health

- What to show: public snapshot status, static data status, local-only backend services, events.
- What to say: "This page is explicit about what is hosted publicly versus what runs locally."
- What not to overclaim: do not call local-only services publicly healthy.

### GitHub Repo And README

- What to show: README, benchmark table, screenshots, architecture docs, CI badge.
- What to say: "The repo includes the full local backend/search/worker/ML stack plus docs, tests, and quality gates."
- What not to overclaim: do not say Atlas integration is already implemented.

## Key Phrases To Use

- "This is not a chatbot. It is a retrieval and ranking observability platform."
- "The public demo uses real exported outputs from the full local stack."
- "I intentionally use snapshot mode publicly to avoid always-on OpenSearch, Qdrant, Redis, and ML model hosting costs."
- "The full live stack runs locally through Docker Compose."
- "Evaluation is document-level because SciFact qrels are document-level."
- "Hybrid fusion uses rank-based RRF instead of mixing incomparable raw scores."

## Things Not To Say

- Do not say public demo runs live arbitrary search.
- Do not say Atlas integration is already implemented.
- Do not claim web-scale traffic.
- Do not call it a chatbot.
- Do not overstate sampled rerank benchmark.
- Do not say the hosted demo has a live backend if it does not.
