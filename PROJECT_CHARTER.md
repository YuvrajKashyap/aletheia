# Aletheia Project Charter

## Project name

Aletheia

## One-line definition

Aletheia is a production-style hybrid retrieval, reranking, evaluation, and search observability platform built on real benchmark data and real retrieval metrics.

## What Aletheia is

Aletheia is a technical platform for building, running, evaluating, and observing retrieval systems.

The final system will ingest a real benchmark corpus, index the corpus through both lexical and dense retrieval systems, combine results through hybrid retrieval, rerank candidates with a cross-encoder, evaluate search quality against ground truth relevance judgments, and expose the results through a polished dashboard.

Aletheia must demonstrate the full retrieval lifecycle:

1. Ingest a real corpus.
2. Store documents, chunks, queries, and qrels in PostgreSQL.
3. Build a BM25 lexical index with OpenSearch.
4. Build a dense vector index with Qdrant.
5. Retrieve candidates through BM25, dense retrieval, hybrid RRF, and hybrid plus reranker modes.
6. Rerank top candidates with a cross-encoder.
7. Evaluate retrieval quality with real metrics.
8. Store query traces and latency measurements.
9. Compare experiments across retrieval configurations.
10. Present the system through a serious, technical dashboard.

## What Aletheia is not

Aletheia is not:

- A chatbot
- A RAG wrapper
- A vector database demo
- A fake dashboard
- A notebook project
- A frontend-only portfolio project
- An OpenAI API wrapper
- A toy search bar with hardcoded results
- A demo that invents metrics
- A UI shell without backend substance

## North star

The north star for Aletheia is correctness and observability across a real retrieval pipeline.

Every visible result, metric, trace, and comparison in the final demo must come from real data, real retrieval runs, real relevance judgments, and real system measurements.

The project should prove that the builder understands production retrieval systems, not just frontend presentation.

## Final system capabilities

The final Aletheia system must support:

- BEIR SciFact ingestion
- Document and chunk storage in PostgreSQL
- Query and qrel storage in PostgreSQL
- BM25 retrieval through OpenSearch
- Dense retrieval through Qdrant
- Embeddings generated with BAAI/bge-small-en-v1.5
- Hybrid retrieval through Reciprocal Rank Fusion
- Cross-encoder reranking with cross-encoder/ms-marco-MiniLM-L-6-v2
- Search execution through FastAPI
- Evaluation runs against SciFact qrels
- Recall@5
- Recall@10
- MRR@10
- NDCG@10
- p50 latency
- p95 latency
- Query trace storage
- Experiment comparison
- Index versioning
- Index activation controls
- Worker-based background jobs
- System health visibility
- A polished dashboard with real data only

## Final stack

The stack is locked unless the project owner explicitly changes it.

### Frontend

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Recharts

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Database

- PostgreSQL
- Docker Postgres for local development
- Neon Postgres for hosted database

### Queue and worker

- Redis
- RQ

### Retrieval infrastructure

- OpenSearch for BM25 lexical retrieval
- Qdrant for dense vector retrieval

### Models

- BAAI/bge-small-en-v1.5 for embeddings
- cross-encoder/ms-marco-MiniLM-L-6-v2 for reranking

### Dataset

- BEIR SciFact

### Local development

- Docker Compose

### Testing

- pytest

### Later deployment

- GitHub Actions for CI
- Vercel for public frontend
- Hosted backend option to be decided later
- Neon Postgres for hosted PostgreSQL
- Public domain later: aletheia.yuvrajkashyap.com

## Architecture rule

FastAPI owns all backend logic.

Correct architecture:

- Frontend calls FastAPI.
- FastAPI uses SQLAlchemy to access PostgreSQL.
- FastAPI talks to OpenSearch.
- FastAPI talks to Qdrant.
- FastAPI talks to Redis and RQ.

Incorrect architecture:

- Frontend talks directly to PostgreSQL.
- Frontend uses Supabase client to access database tables directly.
- Frontend talks directly to OpenSearch.
- Frontend talks directly to Qdrant.
- Frontend owns backend logic.

The frontend must never bypass FastAPI for backend logic.

This project is not using Supabase-specific backend magic. If hosted Postgres is needed, use Neon.

## Core retrieval modes

Aletheia must preserve four retrieval modes:

1. BM25

   Lexical search using OpenSearch BM25.

2. Dense

   Vector search using Qdrant and BAAI/bge-small-en-v1.5 embeddings.

3. Hybrid RRF

   BM25 and dense results combined using Reciprocal Rank Fusion.

4. Hybrid plus reranker

   Hybrid RRF candidates reranked with cross-encoder/ms-marco-MiniLM-L-6-v2.

These modes must be comparable through the same query set and evaluation metrics.

## Evaluation correctness rules

Evaluation must be correct before it is impressive.

Rules:

- Evaluation must use real SciFact relevance judgments.
- Evaluation must map chunk-level retrieval results back to document IDs before scoring.
- Evaluation must deduplicate document IDs before computing metrics.
- Evaluation must not count multiple chunks from the same document as multiple relevant document hits.
- Evaluation must compute metrics from stored retrieval results, not from hardcoded numbers.
- Evaluation must store the retrieval mode, index version, reranker setting, timestamp, and latency context for each run.
- Evaluation must distinguish between candidate retrieval latency, reranking latency, and total latency where possible.
- Evaluation must support Recall@5, Recall@10, MRR@10, and NDCG@10.
- Evaluation must include p50 and p95 latency.
- Evaluation must make failed or partial runs visibly different from successful completed runs.

## Production-grade rules

Aletheia should be built like a real internal search platform.

Rules:

- No fake metrics.
- No fake dashboard data in the final demo.
- No placeholder results presented as real.
- No hardcoded evaluation numbers.
- No invented latency measurements.
- No pretending that indexes exist before they are built.
- Failed indexes must never auto-activate.
- Indexes must be versioned.
- Jobs must be idempotent where practical.
- Jobs must be retry-safe where practical.
- Expensive and administrative actions must later be protected by ADMIN_API_KEY.
- App modes must later support local, demo, and production.
- All list endpoints must later support pagination and filtering.
- Backend responses should use structured errors.
- Backend logs should include request IDs, trace IDs, and job IDs where relevant.
- Query traces must be persisted for observability.
- Worker heartbeat and system events should be tracked later.
- Windows 11 friendly setup matters.

## Public demo and admin safety rules

The public demo must be safe, controlled, and truthful.

Rules:

- Public users should be able to explore real results without being able to mutate expensive system state.
- Admin actions must be separated from public demo actions.
- Index building, ingestion, reindexing, and expensive evaluation jobs must be protected later.
- ADMIN_API_KEY or equivalent protection must be added before exposing admin actions.
- Demo mode may restrict write actions.
- Demo mode must not fake system state.
- Demo mode may use precomputed real indexes and real evaluation runs.
- Production mode must not expose secrets or internal admin endpoints.

## Required final product pages

The final product should include these pages:

1. Search Lab

   Run queries across BM25, dense, hybrid RRF, and hybrid plus reranker modes.

2. Query Trace

   Inspect retrieval stages, candidate rankings, scores, reranker changes, document mapping, and latency.

3. Evaluation Dashboard

   View Recall@5, Recall@10, MRR@10, NDCG@10, p50 latency, and p95 latency from real evaluation runs.

4. Experiment Comparison

   Compare retrieval modes, index versions, reranker settings, and evaluation runs.

5. Index Console

   Inspect ingestion status, index versions, active indexes, failed indexes, and background jobs.

6. Document Explorer

   Browse documents, chunks, metadata, and query relevance where available.

7. System Health

   Inspect backend, database, OpenSearch, Qdrant, Redis, worker heartbeat, and recent system events.

## Final acceptance criteria

Aletheia is complete only when:

- The system ingests real BEIR SciFact data.
- PostgreSQL stores documents, chunks, queries, qrels, experiments, evaluation runs, and query traces.
- OpenSearch serves a real BM25 index.
- Qdrant serves a real dense vector index.
- The backend supports BM25, dense, hybrid RRF, and hybrid plus reranker search modes.
- The reranker is actually applied to candidate results.
- Evaluation uses real SciFact qrels.
- Chunk results are mapped back to document IDs before scoring.
- Document-level deduplication happens before metric computation.
- Recall@5, Recall@10, MRR@10, NDCG@10, p50 latency, and p95 latency are computed from real runs.
- Query traces show actual retrieval stages and timing.
- Experiment comparison uses stored experiment data.
- Index versions are tracked.
- Failed indexes do not become active.
- The frontend shows real backend data.
- The final dashboard contains no fake metrics.
- The project can be run locally on Windows 11 with clear instructions.
- The codebase is suitable for a serious portfolio review by a software engineer, ML infrastructure engineer, or search engineer.

## Strong warning to future agents

Do not turn Aletheia into a chatbot.

Do not turn Aletheia into a generic RAG wrapper.

Do not turn Aletheia into a fake analytics dashboard.

Do not replace the retrieval system with a simple OpenAI API call.

Do not remove evaluation correctness for speed.

Do not create fake metrics to make the UI look finished.

Do not bypass FastAPI.

Do not let the frontend talk directly to the database.

Do not change the stack unless explicitly instructed by the project owner.

Aletheia exists to demonstrate real retrieval, real ranking, real evaluation, and real observability.