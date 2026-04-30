# Interview Q&A

## Architecture

### What is Aletheia?

Aletheia is a production-style retrieval, reranking, evaluation, and search observability platform. It compares BM25, dense vector retrieval, hybrid RRF, and cross-encoder reranking over BEIR SciFact with real traces, metrics, index metadata, replay outputs, and dashboards.

### Why not just build a chatbot?

The goal is to build retrieval infrastructure, not answer generation. Aletheia focuses on what documents are retrieved, why they were ranked, how retrieval modes compare, and whether results match qrels. That is the foundation behind many search and retrieval systems.

### Why FastAPI?

FastAPI gives a clear API boundary, typed request and response schemas, async-friendly endpoints, and a practical Python backend for retrieval and ML model integration.

### Why PostgreSQL?

PostgreSQL is the metadata source of truth. It stores documents, chunks, queries, qrels, traces, candidates, index versions, jobs, evaluation runs, replay runs, and system events.

### Why SQLAlchemy and Alembic?

SQLAlchemy keeps database access explicit and testable. Alembic provides reproducible schema migrations, which matters because the project has many linked entities and run histories.

### Why Redis/RQ?

Redis/RQ gives a simple production-style background job model for ingestion, indexing, evaluation, comparison, and replay. It is lighter than Celery for this project while still demonstrating async orchestration.

### Why OpenSearch and Qdrant separately?

They solve different retrieval problems. OpenSearch is strong for BM25 lexical retrieval. Qdrant is built for vector similarity search. Keeping them separate makes retrieval behavior and infrastructure tradeoffs clearer.

### Why not only vector search?

Vector search can miss exact lexical signals, citations, terminology, or rare entities. BM25 remains strong for exact-match and domain-specific language. Hybrid retrieval can combine strengths from both.

## Retrieval

### What is BM25?

BM25 is a lexical ranking function based on term frequency, inverse document frequency, and document length normalization. In Aletheia it runs through OpenSearch.

### What is dense retrieval?

Dense retrieval embeds queries and documents into vector space, then ranks by vector similarity. Aletheia uses `BAAI/bge-small-en-v1.5` embeddings and Qdrant.

### Why RRF?

Reciprocal Rank Fusion combines ranked lists using rank positions. It is robust when sources have different score scales, such as BM25 scores and vector similarity scores.

### Why not combine raw scores?

BM25 and dense scores are not directly comparable. A raw weighted sum can be unstable unless scores are carefully calibrated. RRF avoids that by using rank.

### What does the reranker do?

The reranker uses a cross-encoder to score query-candidate pairs directly. It can improve ordering because it sees the query and candidate text together rather than relying only on independent embeddings or lexical matching.

### Why rerank only top-N?

Cross-encoder scoring is expensive because each query-document pair is evaluated separately. Reranking top-N candidates is the practical tradeoff between quality and latency.

### Why does reranker cost more?

The cross-encoder runs model inference for candidate pairs. On local CPU this is much slower than BM25 and usually slower than vector search.

## Evaluation

### How did you evaluate?

Aletheia evaluates BEIR SciFact queries against real qrels. The evaluator runs retrieval, maps returned chunks to parent document IDs, deduplicates document IDs, and computes Recall@5, Recall@10, MRR@10, NDCG@10, and latency.

### What are Recall@K, MRR, and NDCG?

Recall@K measures whether relevant documents appear in the top K. MRR measures how early the first relevant result appears. NDCG rewards relevant documents appearing higher in the ranked list.

### Why map chunks back to documents?

SciFact qrels are document-level. Aletheia retrieves chunks. To score correctly, chunk hits must map back to parent document IDs, and duplicates must be removed before metrics are computed.

### What does qrels mean?

Qrels are relevance judgments. They define which documents are relevant for each benchmark query.

### Why are some metrics low or different by mode?

Different modes optimize different signals. BM25 can excel at exact term overlap. Dense retrieval can capture semantic similarity. Hybrid can improve recall by combining sources. Reranking can improve order but is latency-sensitive and in the recorded table was sampled.

## Production

### How do you track jobs?

Jobs have backend-visible state through Redis/RQ and persisted job metadata. The UI shows job status for indexing, evaluation, comparison, and replay workflows.

### How does index versioning work?

Indexes are treated as versioned assets. Builds create or update index versions and jobs. Activation is explicit, and failed or partial builds should not silently become active.

### How would rollback work?

Rollback means reactivating a prior valid index version and ensuring dependent metadata points to that version. The important invariant is that only one intended active version is used.

### How do query traces help debugging?

Traces show candidate source, scores, ranks, latency, fusion, rerank movement, and trace JSON. They make it possible to debug whether a miss came from retrieval, fusion, reranking, or evaluation mapping.

### How do you detect slow queries?

Aletheia records latency fields and system events. Slow queries can be diagnosed through trace stage timings, model paths, candidate counts, and system health views.

### How would you scale it?

Keep FastAPI as the API boundary, move Postgres, Redis, OpenSearch, and Qdrant to managed services, run separate API and worker pools, add model-serving optimization, add caching and batching, improve observability, and introduce auth and tenant controls.

## Public Demo

### Why snapshot mode?

The public demo should be affordable and honest. Hosting OpenSearch, Qdrant, Redis, workers, and ML models continuously is costly. Snapshot mode serves real exported outputs from the full local pipeline without pretending the public site is a live search cluster.

### Is the public demo fake?

No. It uses real traces, evaluations, index metadata, replay results, and dataset samples exported from the local full stack. It is precomputed and read-only publicly.

### What runs locally vs publicly?

Locally, the full stack runs: FastAPI, Postgres, Redis/RQ, OpenSearch, Qdrant, embeddings, reranker, worker, and Next.js. Publicly, Vercel serves the frontend and static snapshot JSON.

### How would you host full live mode if budget allowed?

Deploy FastAPI and workers as separate services, use managed Postgres and Redis, host OpenSearch and Qdrant through managed providers, use persistent model-serving workers, configure CORS/auth/admin controls, and add production observability.

## Atlas

### How would Atlas integrate?

Atlas would crawl and clean web documents. Aletheia would ingest those documents as a dataset, chunk and index them, run BM25/dense/hybrid/rerank retrieval, trace results, and evaluate with human-labeled qrels or replay-based validation.

### What changes for web-scale search?

The corpus becomes larger and noisier. The system would need stronger ingestion pipelines, dedupe, freshness, shard/partition strategy, managed search/vector infrastructure, more workers, caching, stronger auth, and better observability.
