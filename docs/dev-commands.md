# Developer Commands

## Purpose

Aletheia is a multi-service retrieval platform. This document defines the command strategy for local development so future work uses predictable scripts instead of random one-off commands.

This is a Windows-first project during development. PowerShell scripts are the primary local command interface.

The final README will be written later, after real benchmark metrics, screenshots, and deployment details are ready. For now, use:

- PROJECT_CHARTER.md
- AGENTS.md
- docs/product-spec.md
- docs/dev-commands.md

## Current status

Step 2 only creates the reproducible command layer.

No dependencies are installed in this step.

No Docker Compose stack exists yet.

No FastAPI application exists yet.

No Next.js application exists yet.

No database schema exists yet.

Most scripts are placeholders until future steps implement the related services.

## Running scripts

Run scripts from the project root:

    C:\Users\ykyuv\dev\aletheia

Use this pattern:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/<script-name>.ps1

Examples:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/check-prereqs.ps1

    powershell -ExecutionPolicy Bypass -File scripts/powershell/doctor.ps1

## Implemented commands now

### Check prerequisites

Script:

    scripts/powershell/check-prereqs.ps1

Purpose:

Checks local availability of core developer tools.

Current checks:

- git
- python
- node
- npm
- docker
- docker compose
- gh

Notes:

- GitHub CLI is optional.
- Docker is not used yet, but it will be required soon.
- Missing tools should be reported clearly.

Run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/check-prereqs.ps1

### Python doctor

Script:

    scripts/python/doctor.py

Purpose:

Runs standard-library-only diagnostics.

Current checks:

- Python version
- Platform info
- Expected project folders
- Expected key project files

Run:

    python scripts/python/doctor.py

### PowerShell doctor wrapper

Script:

    scripts/powershell/doctor.ps1

Purpose:

Checks that Python is available, then runs:

    python scripts/python/doctor.py

Run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/doctor.ps1

## Placeholder commands

The following commands are reserved for future steps. They should not run nonexistent services yet.

### Start local stack

Script:

    scripts/powershell/dev.ps1

Future purpose:

Start the local development stack once Docker Compose exists.

Expected future services:

- PostgreSQL
- Redis
- OpenSearch
- Qdrant
- FastAPI
- RQ worker
- Next.js frontend

### Start API

Script:

    scripts/powershell/api.ps1

Future purpose:

Start the FastAPI backend once it exists.

### Start worker

Script:

    scripts/powershell/worker.ps1

Future purpose:

Start the RQ worker once backend jobs exist.

### Start frontend

Script:

    scripts/powershell/web.ps1

Future purpose:

Start the Next.js frontend once it exists.

### Run tests

Script:

    scripts/powershell/test.ps1

Future purpose:

Run backend, worker, and frontend tests once test infrastructure exists.

### Ingest SciFact

Script:

    scripts/powershell/ingest-scifact.ps1

Future purpose:

Run BEIR SciFact ingestion into PostgreSQL.

### Build index

Script:

    scripts/powershell/build-index.ps1

Future purpose:

Build versioned BM25 and dense indexes.

Expected future targets:

- OpenSearch BM25 index
- Qdrant vector collection

### Run evaluation

Script:

    scripts/powershell/run-eval.ps1

Future purpose:

Run retrieval evaluation against SciFact qrels.

Expected future metrics:

- Recall@5
- Recall@10
- MRR@10
- NDCG@10
- p50 latency
- p95 latency

### Seed demo

Script:

    scripts/powershell/seed-demo.ps1

Future purpose:

Prepare a truthful demo state using real ingested data, real indexes, real evaluation runs, and real query traces.

### Reset local state

Script:

    scripts/powershell/reset-local.ps1

Future purpose:

Reset local development state safely once Docker and database workflows exist.

### Clear local indexes

Script:

    scripts/powershell/clear-indexes.ps1

Future purpose:

Clear local OpenSearch and Qdrant indexes after those services exist.

### Export evaluation report

Script:

    scripts/powershell/export-eval-report.ps1

Future purpose:

Export evaluation metrics and comparison reports after evaluation storage exists.

## Future command list

The long-term command surface should include:

- check prerequisites
- start local stack
- start API
- start worker
- start frontend
- run tests
- ingest SciFact
- build index
- run evaluation
- seed demo
- reset local state
- clear local indexes
- export evaluation report

## Command design rules

Commands should be:

- PowerShell-friendly
- Clear
- Repeatable
- Safe by default
- Honest about missing implementation
- Easy for future agents to validate

Commands should not:

- Fake service status
- Pretend missing services exist
- Install dependencies unless the assigned step explicitly asks for it
- Start Docker before the Docker step exists
- Start FastAPI before the backend step exists
- Start Next.js before the frontend step exists
- Mutate expensive or destructive state without a clear warning

## Final note

These commands will become real as future steps add Docker, FastAPI, worker, frontend, ingestion, indexing, evaluation, and reporting.

## Step 3 local infrastructure commands

Step 3 adds the local Docker Compose infrastructure layer.

Implemented services:

- PostgreSQL
- Redis
- OpenSearch
- Qdrant

No FastAPI app, RQ worker code, or Next.js app exists yet.

### Check prerequisites

Run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/check-prereqs.ps1

This checks:

- git
- python
- node
- npm
- docker
- docker compose
- Docker daemon availability
- gh as optional

### Start local infrastructure

Run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/dev.ps1

This runs:

    docker compose up -d postgres redis opensearch qdrant

Helpful local endpoints:

- Postgres: localhost:5432
- Redis: localhost:6379
- OpenSearch: http://localhost:9200
- Qdrant: http://localhost:6333

### Inspect running containers

Run:

    docker compose ps

### Stop local infrastructure

Run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/infra-down.ps1

This runs:

    docker compose down

It stops containers but keeps local Docker volumes.

### Reset local infrastructure volumes

Warning:

This deletes local Docker volumes.

Run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/infra-reset.ps1 -ConfirmReset

This runs:

    docker compose down -v

Do not run this unless you intentionally want to delete local Postgres, Redis, OpenSearch, and Qdrant data.

### Direct health checks

Postgres:

    docker exec aletheia-postgres pg_isready -U aletheia -d aletheia

Redis:

    docker exec aletheia-redis redis-cli ping

OpenSearch:

    Invoke-WebRequest -UseBasicParsing http://localhost:9200

Qdrant:

    Invoke-WebRequest -UseBasicParsing http://localhost:6333



## Step 4 FastAPI backend commands

Step 4 adds the FastAPI backend foundation.

This step does not add database models, SQLAlchemy, Alembic, ingestion, search, OpenSearch clients, Qdrant clients, worker logic, or frontend code.

### Python 3.11 verification

Run:

    py -0p
    py -3.11 --version

Expected:

    Python 3.11.x

### Create backend virtual environment

Run from the repo root:

    py -3.11 -m venv services/api/.venv

Verify:

    .\services\api\.venv\Scripts\python.exe --version

### Install backend dependencies

Run from the repo root:

    .\services\api\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\services\api\.venv\Scripts\python.exe -m pip install -e "services/api[dev]"

### Run backend tests

Run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/test.ps1

Equivalent direct command:

    .\services\api\.venv\Scripts\python.exe -m pytest services/api/tests

### Start the FastAPI backend

Run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/api.ps1

The backend runs at:

    http://localhost:8000

API docs:

    http://localhost:8000/api/docs

OpenAPI schema:

    http://localhost:8000/api/openapi.json

### Test backend endpoints

In a second PowerShell window while the API is running:

    Invoke-RestMethod http://localhost:8000/
    Invoke-RestMethod http://localhost:8000/api/v1/health

Expected root response:

    service: aletheia-api
    status: ok
    docs: /api/docs

Expected health response includes:

    status
    service
    version
    app_mode
    request_id

### Request ID behavior

The API adds an X-Request-ID response header.

If the request includes X-Request-ID, the API preserves it.

If absent, the API generates a UUID request ID.

## Step 5 database and Alembic commands

Step 5 adds the SQLAlchemy and Alembic database foundation.

This step does not add application data models yet. Dataset, document, chunk, query, qrel, evaluation, trace, and job tables are added in later steps.

Database rules:

- Database access is owned by FastAPI through SQLAlchemy.
- Migrations are managed by Alembic.
- Do not use Base.metadata.create_all().
- Do not make the frontend talk directly to PostgreSQL.
- The initial migration is intentionally empty and establishes Alembic versioning only.

### Start local infrastructure

Postgres must be running before migration commands are used.

Run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/dev.ps1

Check Postgres:

    docker exec aletheia-postgres pg_isready -U aletheia -d aletheia

### Install updated backend dependencies

Run:

    .\services\api\.venv\Scripts\python.exe -m pip install -e "services/api[dev]"

Step 5 adds:

- sqlalchemy
- alembic
- psycopg[binary]
- python-dotenv

### Upgrade database

Run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/db-upgrade.ps1

This runs Alembic upgrade head from services/api.

### Check current migration

Run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/db-current.ps1

### Show migration history

Run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/db-history.ps1

### Downgrade database

Downgrade requires an explicit revision.

Example:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/db-downgrade.ps1 -Revision -1

If no revision is provided, the script exits without running a downgrade.

### Database health endpoint

Start the API:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/api.ps1

Then in a second PowerShell window:

    Invoke-RestMethod http://localhost:8000/api/v1/health/db

Expected healthy response includes:

    status: healthy
    database: postgresql
    request_id
    error: null

## Step 6 core schema commands

Step 6 adds the core SQLAlchemy ORM model metadata and the Alembic migration for the
Aletheia database schema.

Schema rules:

- Core tables are defined in `services/api/app/models`.
- Migrations are managed under `services/api/alembic/versions`.
- Apply schema changes with the database upgrade command after reviewing migrations.
- Do not use `Base.metadata.create_all()`.
- Use Alembic only for database schema changes.
- This step still does not include ingestion, search, vector indexing, reranking, worker, or frontend code.

Run database migrations:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/db-upgrade.ps1

Run backend tests:

    .\services\api\.venv\Scripts\python.exe -m pytest services/api/tests

## Step 7 worker and queue commands

Step 7 adds the Redis/RQ async worker foundation.

Worker rules:

- RQ is used for async jobs.
- Redis is the broker.
- Worker heartbeat state is stored in PostgreSQL.
- Real ingestion, indexing, evaluation, replay, and demo seed jobs come later.
- This step only validates async plumbing with a harmless test job.

Start local infrastructure:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/dev.ps1

Start the API:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/api.ps1

Start the worker:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/worker.ps1

Check the default queue:

    Invoke-RestMethod http://localhost:8000/api/v1/system/queue

Enqueue a test job:

    $body = @{ message = "step7-worker-check" } | ConvertTo-Json
    $job = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/system/jobs/test -ContentType "application/json" -Headers @{"X-Admin-API-Key"="replace-me"} -Body $body
    $job

Inspect the test job:

    Invoke-RestMethod "http://localhost:8000/api/v1/system/jobs/$($job.job_id)"

Inspect worker heartbeats:

    Invoke-RestMethod http://localhost:8000/api/v1/system/worker-heartbeats

## Step 8 admin safety commands

Step 8 adds app mode and admin API key protection for expensive or mutating backend
operations.

App modes:

- `local` is the default development mode.
- `demo` and `production` are public-like modes.
- `demo` and `production` must use a real `ADMIN_API_KEY`, not `replace-me`.

Admin protection:

- This is not a full user authentication system.
- It is a safety guard for expensive or destructive backend operations.
- Public demo viewers should not be able to trigger ingestion, indexing, evaluation, reset, or seed jobs.
- `POST /api/v1/system/jobs/test` is admin-protected as the current harmless mutation endpoint.
- Step 8 does not add real ingestion, search, indexing, evaluation, OpenSearch, Qdrant, embedding, reranking, or frontend logic.

The default local admin key is:

    replace-me

Check admin status:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/admin-status.ps1

Check admin status with an explicit key:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/admin-status.ps1 -AdminApiKey "replace-me"

Enqueue the protected test job:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/enqueue-test-job.ps1 -Message "step8-script-check"

Direct admin status request:

    Invoke-RestMethod http://localhost:8000/api/v1/admin/status -Headers @{"X-Admin-API-Key"="replace-me"}

Direct protected enqueue request:

    $body = @{ message = "step8-admin-check" } | ConvertTo-Json
    $job = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/system/jobs/test -ContentType "application/json" -Headers @{"X-Admin-API-Key"="replace-me"} -Body $body
    $job

## Step 9 SciFact dataset loader commands

Step 9 adds the BEIR SciFact dataset loader.

Loader rules:

- `ir_datasets` is used as the dataset source.
- The loader stores SciFact corpus documents, test benchmark queries, and document-level qrels.
- SciFact qrels are stored as document-level relevance judgments.
- Chunking, OpenSearch indexing, Qdrant indexing, retrieval, reranking, and evaluation metrics come later.
- This step does not add fake data or fake benchmark metrics.

Dry run with small limits:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/ingest-scifact.ps1 -DryRun -DocumentLimit 10 -QueryLimit 5 -QrelLimit 5

Limited real load:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/ingest-scifact.ps1 -DocumentLimit 10 -QueryLimit 5 -QrelLimit 5

Full load:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/ingest-scifact.ps1

Postgres count checks:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from datasets;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from documents;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from benchmark_queries;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from relevance_judgments;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from chunks;"

Read-only API endpoints:

    Invoke-RestMethod http://localhost:8000/api/v1/datasets
    Invoke-RestMethod "http://localhost:8000/api/v1/documents?limit=5&offset=0"
    Invoke-RestMethod "http://localhost:8000/api/v1/benchmark-queries?limit=5&offset=0"

## Step 10 text normalization and chunking commands

Step 10 adds conservative text normalization and database chunk generation.

Chunking rules:

- Text normalization collapses whitespace and strips leading/trailing whitespace.
- Normalization preserves case, punctuation, citations, numbers, and scientific symbols.
- SciFact uses document-level chunking by default: one chunk per document.
- SciFact qrels are document-level, so document-level chunks preserve a clean mapping back to relevance judgments.
- OpenSearch indexing, Qdrant indexing, search, embeddings, reranking, and evaluation metrics come later.

Dry-run chunking:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/chunk-documents.ps1 -DryRun -DocumentLimit 10

Limited real chunking:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/chunk-documents.ps1 -DocumentLimit 10

Full chunking:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/chunk-documents.ps1

Postgres count checks:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from documents;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from chunks;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select chunking_strategy, chunking_version, count(*) from chunks group by chunking_strategy, chunking_version;"

Chunk API endpoints:

    Invoke-RestMethod "http://localhost:8000/api/v1/chunks?limit=5&offset=0"
    $chunks = Invoke-RestMethod "http://localhost:8000/api/v1/chunks?limit=1&offset=0"
    $chunkId = $chunks.items[0].id
    Invoke-RestMethod "http://localhost:8000/api/v1/chunks/$chunkId"

## Step 11 idempotent ingestion and job tracking commands

Step 11 adds tracked ingestion runs for SciFact loading.

Ingestion rules:

- Ingestion runs are tracked in PostgreSQL using `ingestion_runs`.
- CLI ingestion and API-triggered ingestion use the same orchestration service.
- The API trigger is admin-protected and enqueues an RQ job.
- The worker executes expensive ingestion work.
- Reruns are idempotent: existing datasets, documents, queries, qrels, and chunks are updated or reused instead of duplicated.
- An active-run guard prevents duplicate concurrent real SciFact ingestion jobs.
- Chunking is included by default.
- OpenSearch indexing, Qdrant indexing, retrieval, embeddings, reranking, and evaluation metrics are not part of this step.

CLI dry run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/ingest-scifact.ps1 -DryRun -DocumentLimit 10 -QueryLimit 5 -QrelLimit 5

CLI full run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/ingest-scifact.ps1

API async trigger:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/start-scifact-ingestion-job.ps1 -DocumentLimit 10 -QueryLimit 5 -QrelLimit 5

List ingestion runs:

    Invoke-RestMethod "http://localhost:8000/api/v1/ingestion/runs?limit=10&offset=0"

Get ingestion run detail:

    $runs = Invoke-RestMethod "http://localhost:8000/api/v1/ingestion/runs?limit=1&offset=0"
    $runId = $runs.items[0].id
    Invoke-RestMethod "http://localhost:8000/api/v1/ingestion/runs/$runId"

Inspect ingestion runs table:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, status, documents_loaded, chunks_created, queries_loaded, qrels_loaded, errors_count, created_at from ingestion_runs order by created_at desc limit 10;"

## Step 12 index versioning commands

Step 12 adds metadata-only index version lifecycle management.

Index version rules:

- Index versions represent future OpenSearch lexical indexes and Qdrant vector collections.
- `status` describes lifecycle: pending, building, ready, active, failed, deprecated.
- `is_active` identifies the one version that should serve search for a dataset later.
- No real OpenSearch index or Qdrant collection is created in this step.
- Never build directly into an active index. The intended future flow is create pending metadata, build resources later, validate later, mark ready, then activate.
- Activation is metadata-only until indexing steps exist.
- Rollback is metadata-only and switches `is_active` back to a ready or deprecated version.

Create an index version from the CLI:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/create-index-version.ps1

Create and mark ready for local lifecycle validation:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/create-index-version.ps1 -MarkReady

Check index status:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/index-status.ps1

List index versions:

    Invoke-RestMethod "http://localhost:8000/api/v1/indexes/versions?limit=10&offset=0"

Create index version through the API:

    $body = @{ dataset_name = "beir/scifact"; dataset_version = "test"; chunking_strategy = "scifact_document_v1"; chunking_version = "1.0" } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/indexes/versions" -ContentType "application/json" -Headers @{"X-Admin-API-Key"="replace-me"} -Body $body

Mark an index version ready:

    Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/indexes/versions/$indexVersionId/mark-ready" -Headers @{"X-Admin-API-Key"="replace-me"}

Activate an index version:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/activate-index-version.ps1 -IndexVersionId $indexVersionId

Rollback to a previous ready or deprecated version:

    Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/indexes/versions/$indexVersionId/rollback" -Headers @{"X-Admin-API-Key"="replace-me"}

## Step 13 OpenSearch lexical indexing commands

Step 13 adds OpenSearch BM25 lexical indexing for stored chunks.

Indexing rules:

- Chunks are indexed into OpenSearch.
- The target OpenSearch index name comes from `index_versions.lexical_index_name`.
- Default OpenSearch BM25 behavior is used; there is no custom analyzer yet.
- This step does not add a BM25 search endpoint or any retrieval API.
- Qdrant/vector indexing, embeddings, dense retrieval, reranking, evaluation metrics, and frontend work come later.
- `index_jobs` tracks lexical build jobs.
- `vector_count` remains `0` because Qdrant indexing is not built yet.

Check OpenSearch health through FastAPI:

    Invoke-RestMethod http://localhost:8000/api/v1/system/opensearch

Build lexical index from the CLI:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/build-lexical-index.ps1 -IndexVersionId $indexVersionId

Recreate and build with a small limit:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/build-lexical-index.ps1 -IndexVersionId $indexVersionId -Recreate -Limit 25

Build the active index version:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/build-lexical-index.ps1 -Active

Start an async lexical build job through the API:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/start-lexical-index-build-job.ps1 -IndexVersionId $indexVersionId

Direct API trigger:

    $body = @{ recreate = $false; refresh = $true } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/indexes/versions/$indexVersionId/build-lexical" -ContentType "application/json" -Headers @{"X-Admin-API-Key"="replace-me"} -Body $body

OpenSearch count validation:

    Invoke-RestMethod "http://localhost:9200/$lexicalIndexName/_count"

Inspect index jobs:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, index_version_id, job_type, status, chunks_total, chunks_completed, chunks_failed, created_at from index_jobs order by created_at desc limit 10;"

## Step 14 BM25 lexical retrieval commands

Step 14 adds the internal BM25 lexical retrieval service.

Retrieval rules:

- OpenSearch default BM25 scoring is used against indexed chunk text, with a small title match included.
- This is not the final public Search API.
- No `/api/v1/search` endpoint is added in this step.
- Retrieval does not write to `queries`, `query_traces`, or `retrieval_candidates`.
- Results are ranked chunks from the active OpenSearch lexical index unless an index version or index name is explicitly supplied.
- Qdrant/vector retrieval, embeddings, reranking, evaluation metrics, and frontend work are still not implemented.

Run BM25 search through the PowerShell helper:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-bm25.ps1 -Query "Does aspirin reduce risk of heart attack?" -TopK 5

Use a specific index name:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-bm25.ps1 -Query "Does aspirin reduce risk of heart attack?" -IndexName "aletheia-lexical-beir-scifact-test-scifact-document-v1-1-0-63195a04" -TopK 5

Human-readable output:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-bm25.ps1 -Query "statin therapy cardiovascular risk" -TopK 5 -Text

Direct CLI help:

    cd services/api
    .venv/Scripts/python.exe -m app.cli.search_bm25 --help

Expected JSON output fields:

- `query`
- `index_version_id`
- `index_name`
- `retrieval_mode`
- `top_k`
- `total_hits`
- `latency_ms`
- `results`, including rank, OpenSearch score, chunk/document IDs, title, text, chunking metadata, and source metadata.

## Step 15 BM25 Search API and trace commands

Step 15 adds the formal backend Search API for BM25 retrieval.

Search API rules:

- `POST /api/v1/search` is public/read-oriented and does not require an admin key.
- `bm25` is currently the only supported retrieval mode.
- Every successful search writes a `queries` row, a `query_traces` row, and BM25 `retrieval_candidates` rows.
- The trace is a BM25-only skeleton for now.
- Dense retrieval, Qdrant retrieval, hybrid RRF, reranking, evaluation metrics, and frontend work come later.
- The response returns ranked chunks, not generated answers.

PowerShell helper:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-api.ps1 -Query "Do statins lower cholesterol?" -TopK 5

Direct API call:

    $body = @{ query = "Do statins lower cholesterol?"; retrieval_mode = "bm25"; top_k = 5 } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/search" -ContentType "application/json" -Body $body

List traces:

    Invoke-RestMethod "http://localhost:8000/api/v1/search/traces?limit=10&offset=0"

Get trace detail:

    $traces = Invoke-RestMethod "http://localhost:8000/api/v1/search/traces?limit=1&offset=0"
    $traceId = $traces.items[0].trace_id
    Invoke-RestMethod "http://localhost:8000/api/v1/search/traces/$traceId"

Validate database writes:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, retrieval_mode, status, total_latency_ms, created_at from queries order by created_at desc limit 5;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, query_id, created_at from query_traces order by created_at desc limit 5;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select query_id, source, bm25_rank, final_rank, bm25_score from retrieval_candidates order by created_at desc limit 10;"

## Step 16 local embedding model commands

Step 16 adds the local embedding model service.

Embedding rules:

- The locked embedding model is `BAAI/bge-small-en-v1.5`.
- The expected embedding dimension is `384`.
- The model loads lazily only when embedding functionality is called.
- FastAPI startup and normal health checks do not load or download the model.
- The model cache directory is `data/models`.
- The first CLI run may download the model and take time.
- This step does not write embeddings to Qdrant.
- This step does not add dense retrieval or modify `/api/v1/search`.
- Hybrid retrieval, reranking, evaluation metrics, and frontend work come later.

Check API embedding model status without loading the model:

    Invoke-RestMethod http://localhost:8000/api/v1/system/models/embedding

Embed text from PowerShell:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/embed-text.ps1 -Text "Do statins lower cholesterol?"

Show a larger vector preview:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/embed-text.ps1 -Text "Do statins lower cholesterol?" -PreviewDimensions 16

Print the full vector:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/embed-text.ps1 -Text "Do statins lower cholesterol?" -ShowVector

Note: the CLI runs in its own Python process. If the CLI loads the model, the API status route may still report `loaded=false` until the API process itself uses embedding functionality.

## Step 17 Qdrant vector indexing commands

Step 17 adds Qdrant vector indexing for stored chunks.

Vector indexing rules:

- Chunk text is embedded with `BAAI/bge-small-en-v1.5`.
- Expected vector dimension is `384`.
- Vectors are stored in Qdrant with chunk, document, dataset, and index-version payload metadata.
- The target collection name comes from `index_versions.vector_collection_name`.
- A full local build should make `index_versions.vector_count` become `5183`.
- This step does not add dense retrieval or modify `/api/v1/search`.
- Hybrid RRF, reranking, evaluation metrics, and frontend work come later.
- First run may load or download the embedding model and take time on CPU.

Check Qdrant health:

    Invoke-RestMethod http://localhost:8000/api/v1/system/qdrant

Build vector index from the CLI:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/build-vector-index.ps1 -IndexVersionId $indexVersionId

Limited build for validation:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/build-vector-index.ps1 -IndexVersionId $indexVersionId -Recreate -Limit 25 -BatchSize 8

Build the active index version:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/build-vector-index.ps1 -Active

Start an async vector build job through the API:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/start-vector-index-build-job.ps1 -IndexVersionId $indexVersionId

Direct API trigger:

    $body = @{ recreate = $false; batch_size = 64 } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/indexes/versions/$indexVersionId/build-vector" -ContentType "application/json" -Headers @{"X-Admin-API-Key"="replace-me"} -Body $body

Qdrant count validation:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, vector_collection_name, vector_count, embedding_model, embedding_dimension from index_versions order by created_at desc limit 5;"

Inspect vector index jobs:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, index_version_id, job_type, status, chunks_total, chunks_completed, chunks_failed, created_at from index_jobs where job_type = 'vector_index_build' order by created_at desc limit 10;"

## Step 18 dense retrieval commands

Step 18 adds dense vector retrieval from Qdrant and enables `retrieval_mode=dense` in the Search API.

Dense retrieval rules:

- The query is embedded with `BAAI/bge-small-en-v1.5`.
- Qdrant vector similarity search is used against the active index version collection.
- Dense retrieval is semantic retrieval, not keyword retrieval.
- `/api/v1/search` now supports `bm25` and `dense`.
- Dense searches write `queries`, `query_traces`, and `retrieval_candidates` rows with dense stage metadata.
- Hybrid RRF, reranking, evaluation metrics, and frontend work come later.

Dense CLI:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-dense.ps1 -Query "Can animals transmit coronaviruses to humans?" -TopK 5

Dense CLI with text output:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-dense.ps1 -Query "Do statins lower cholesterol?" -TopK 5 -Text

Dense Search API body:

    $body = @{
      query = "Can animals transmit coronaviruses to humans?"
      retrieval_mode = "dense"
      top_k = 5
    } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/search" -ContentType "application/json" -Body $body

Trace and candidate checks:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from queries;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from query_traces;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select source, count(*) from retrieval_candidates group by source order by source;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, retrieval_mode, status, total_latency_ms, created_at from queries where retrieval_mode = 'dense' order by created_at desc limit 5;"

## Step 19 hybrid retrieval commands

Step 19 adds hybrid retrieval with Reciprocal Rank Fusion.

Hybrid retrieval rules:

- BM25 and dense raw scores are not directly comparable, so they are not added or averaged.
- Reciprocal Rank Fusion combines ranked lists using `sum(1 / (rrf_k + rank))`.
- The default `rrf_k` is `60`.
- `/api/v1/search` now supports `bm25`, `dense`, and `hybrid`.
- Hybrid traces store BM25, dense, and fusion stages.
- Reranking, evaluation metrics, and frontend work come later.

Compare BM25:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-bm25.ps1 -Query "Can animals transmit coronaviruses to humans?" -TopK 5

Compare dense:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-dense.ps1 -Query "Can animals transmit coronaviruses to humans?" -TopK 5

Hybrid CLI:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-hybrid.ps1 -Query "Can animals transmit coronaviruses to humans?" -TopK 5 -Bm25CandidateK 50 -DenseCandidateK 50 -RrfK 60

Hybrid CLI with text output:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-hybrid.ps1 -Query "Do statins lower cholesterol?" -TopK 5 -Text

Hybrid Search API body:

    $body = @{
      query = "Do statins lower cholesterol?"
      retrieval_mode = "hybrid"
      top_k = 5
      bm25_candidate_k = 50
      dense_candidate_k = 50
      rrf_k = 60
    } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/search" -ContentType "application/json" -Body $body

Trace and candidate checks:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select source, count(*) from retrieval_candidates group by source order by source;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, retrieval_mode, status, total_latency_ms, created_at from queries order by created_at desc limit 10;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select source, bm25_rank, dense_rank, fusion_rank, final_rank, bm25_score, dense_score, fusion_score from retrieval_candidates where source = 'hybrid_rrf' order by created_at desc limit 10;"

## Step 20 cross-encoder reranking commands

Step 20 adds cross-encoder reranking for hybrid retrieval candidates.

Reranking rules:

- Hybrid retrieval still runs first with BM25, dense retrieval, and Reciprocal Rank Fusion.
- The cross-encoder scores only the top-N hybrid candidates because pairwise query-document scoring is expensive.
- The default reranker model is `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- The default `rerank_top_n` is `25`.
- `/api/v1/search` now supports `bm25`, `dense`, `hybrid`, and `hybrid_rerank`.
- `hybrid_rerank` traces store BM25, dense, fusion, and reranker stages.
- Evaluation metrics and frontend work come later.
- The first reranker call may download or load the model and be slower.

Check reranker model status without loading the model:

    Invoke-RestMethod http://localhost:8000/api/v1/system/models/reranker

Rerank CLI:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-hybrid-rerank.ps1 -Query "Can animals transmit coronaviruses to humans?" -TopK 5 -Bm25CandidateK 50 -DenseCandidateK 50 -HybridCandidateK 50 -RerankTopN 25 -RrfK 60

Rerank CLI with text output:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-hybrid-rerank.ps1 -Query "Do statins lower cholesterol?" -TopK 5 -RerankTopN 25 -Text

Rerank Search API body:

    $body = @{
      query = "Do statins lower cholesterol?"
      retrieval_mode = "hybrid_rerank"
      top_k = 5
      bm25_candidate_k = 50
      dense_candidate_k = 50
      hybrid_candidate_k = 50
      rerank_top_n = 25
      rrf_k = 60
    } | ConvertTo-Json
    Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/search" -ContentType "application/json" -Body $body

Trace and candidate checks:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select source, count(*) from retrieval_candidates group by source order by source;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, retrieval_mode, status, total_latency_ms, created_at from queries order by created_at desc limit 10;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select source, bm25_rank, dense_rank, fusion_rank, rerank_rank, final_rank, bm25_score, dense_score, fusion_score, reranker_score from retrieval_candidates where source = 'hybrid_rerank' order by created_at desc limit 10;"

## Step 21 query tracing and observability commands

Step 21 standardizes search traces under `trace_schema_version = search_trace_v1`.

Trace rules:

- Every completed search trace records query metadata, request ID, query ID, trace ID, index version snapshot, parameters, stages, warnings, errors, ranking summary, and total latency.
- Stage traces include BM25, dense, fusion, and reranker latency and resource names where relevant.
- Candidate provenance is persisted in `retrieval_candidates` and exposed by trace detail/candidate endpoints.
- `hybrid_rerank` traces include rank movement summaries comparing fusion rank to rerank rank.
- Slow searches create best-effort `SLOW_SEARCH_QUERY` system events.
- Failed searches create failed query traces and best-effort `SEARCH_QUERY_FAILED` system events when possible.
- Evaluation metrics, experiment configs, query replay, and frontend work still come later.

Run one search in each mode:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-api.ps1 -Query "Can animals transmit coronaviruses to humans?" -RetrievalMode bm25 -TopK 5
    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-api.ps1 -Query "Can animals transmit coronaviruses to humans?" -RetrievalMode dense -TopK 5
    powershell -ExecutionPolicy Bypass -File scripts/powershell/search-api.ps1 -Query "Can animals transmit coronaviruses to humans?" -RetrievalMode hybrid -TopK 5

List traces:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/list-traces.ps1 -Limit 5

List rerank traces:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/list-traces.ps1 -RetrievalMode hybrid_rerank -Limit 5

Inspect trace detail:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/inspect-trace.ps1 -TraceId <trace_id>

Inspect trace as text:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/inspect-trace.ps1 -TraceId <trace_id> -Text

Inspect candidates through the API:

    Invoke-RestMethod "http://localhost:8000/api/v1/search/traces/<trace_id>/candidates?limit=25&offset=0"
    Invoke-RestMethod "http://localhost:8000/api/v1/search/traces/<trace_id>/candidates?source=hybrid_rerank&limit=25&offset=0"

DB checks:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select retrieval_mode, status, count(*) from queries group by retrieval_mode, status order by retrieval_mode, status;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select source, count(*) from retrieval_candidates group by source order by source;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select event_type, severity, count(*) from system_events group by event_type, severity order by event_type, severity;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select trace_json->>'trace_schema_version' as version, count(*) from query_traces group by version;"

## Step 22 benchmark metrics engine commands

Step 22 adds the pure benchmark metrics engine. It does not run SciFact retrieval, create an evaluation runner, expose evaluation API routes, enqueue jobs, or write evaluation database rows.

Metric rules:

- Metrics operate on document IDs, not chunk IDs.
- Aletheia retrieves chunks, so the full evaluation runner must later map chunk results back to parent document IDs before scoring.
- Duplicate document IDs are deduplicated before scoring so multiple chunks from the same document cannot count as multiple hits.
- Recall@K is the fraction of relevant documents retrieved in the top K deduplicated document IDs.
- MRR@10 is the mean of per-query reciprocal rank at 10.
- NDCG@10 uses DCG divided by ideal DCG with binary or graded relevance.
- Latency summaries include count, average, p50, p95, min, and max using deterministic nearest-rank percentiles.
- The fixture output is deterministic and only validates metric math; it is not a benchmark result.
- Full SciFact evaluation and evaluation DB writes come later.

Run the fixture through PowerShell:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/evaluate-metrics-fixture.ps1

Run the fixture directly:

    cd services/api
    .\.venv\Scripts\python.exe -m app.cli.evaluate_metrics_fixture --input ..\..\data\samples\metrics-fixture.json
    cd ..\..

Expected output shape:

    {
      "per_query": [
        {
          "query_id": "q_perfect",
          "metrics": {
            "recall_at_5": 1.0,
            "recall_at_10": 1.0,
            "reciprocal_rank_at_10": 1.0,
            "ndcg_at_10": 1.0,
            "retrieved_count": 3,
            "relevant_count": 1,
            "hit_at_5": 1.0,
            "hit_at_10": 1.0
          }
        }
      ],
      "aggregate": {
        "query_count": 3,
        "recall_at_5": 0.6666666666666666,
        "recall_at_10": 0.6666666666666666,
        "mrr_at_10": 0.4444444444444444,
        "ndcg_at_10": 0.5,
        "hit_rate_at_5": 0.6666666666666666,
        "hit_rate_at_10": 0.6666666666666666
      },
      "latency_summary": {
        "count": 3,
        "avg_latency_ms": 43.333333333333336,
        "p50_latency_ms": 20.0,
        "p95_latency_ms": 100.0,
        "min_latency_ms": 10.0,
        "max_latency_ms": 100.0
      }
    }

Evaluation DB non-mutation checks:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from evaluation_runs;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from evaluation_query_results;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from evaluation_reports;"

Expected counts should remain 0 unless prior manual testing inserted rows. Step 22 does not write evaluation DB rows.

## Step 23 evaluation correctness commands

Step 23 adds the correctness layer that connects stored Aletheia traces and retrieval candidates to document-level SciFact relevance judgments.

Correctness rules:

- SciFact qrels are document-level, while Aletheia retrieves chunks.
- Chunks and retrieval candidates must be mapped back to parent `document_id` values before scoring.
- Ranked document IDs are deduplicated before metrics so multiple chunks from the same document count once.
- Trace-level evaluation uses real stored candidates and real relevance judgments.
- This step is read-only: it does not create `evaluation_runs`, `evaluation_query_results`, or `evaluation_reports`.
- This is not the full evaluation runner. Batch evaluation, jobs, reports, and persisted evaluation rows come later.

Check qrels alignment:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/check-eval-alignment.ps1

Manual benchmark query lookup:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select external_id, text from benchmark_queries order by external_id limit 5;"

Run search for exact benchmark query text:

    $body = @{
      query = "<PASTE_EXACT_BENCHMARK_QUERY_TEXT>"
      retrieval_mode = "hybrid_rerank"
      top_k = 10
      bm25_candidate_k = 50
      dense_candidate_k = 50
      hybrid_candidate_k = 50
      rerank_top_n = 25
      rrf_k = 60
    } | ConvertTo-Json

    $result = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/search -ContentType "application/json" -Body $body

Evaluate trace:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/evaluate-trace.ps1 -TraceId $result.trace_id -QueryExternalId "<PASTE_QUERY_EXTERNAL_ID>"

Evaluate trace with text output:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/evaluate-trace.ps1 -TraceId $result.trace_id -QueryExternalId "<PASTE_QUERY_EXTERNAL_ID>" -Text

Direct CLI help:

    cd services/api
    .\.venv\Scripts\python.exe -m app.cli.check_eval_alignment --help
    .\.venv\Scripts\python.exe -m app.cli.evaluate_trace --help
    cd ..\..

Verify no evaluation DB rows:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from evaluation_runs;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from evaluation_query_results;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from evaluation_reports;"

## Step 24 offline evaluation runner commands

Step 24 adds the synchronous offline evaluation runner. This is the first step that writes evaluation DB rows.

Runner rules:

- The runner writes `evaluation_runs`, `evaluation_query_results`, and `evaluation_reports`.
- It uses real benchmark query text, the existing Search API service layer, real retrieval, stored traces/candidates, and real qrels.
- Normal `queries`, `query_traces`, and `retrieval_candidates` rows are created as side effects because evaluation calls the existing search service.
- Retrieved chunks are scored only after mapping to parent document IDs.
- Duplicate document IDs are deduplicated before metrics.
- Metrics are honest and may be low or zero.
- Reports are written to `reports/evaluations/`.
- The runner is synchronous in Step 24. RQ jobs and evaluation API routes come later.

Run qrels alignment first:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/check-eval-alignment.ps1

Limited BM25:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/run-evaluation.ps1 -Mode bm25 -Name "BM25 limited Step 24 eval" -QueryLimit 10 -TopK 10 -CandidateK 10 -Notes "Step 24 limited BM25 validation"

Limited dense:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/run-evaluation.ps1 -Mode dense -Name "Dense limited Step 24 eval" -QueryLimit 10 -TopK 10 -CandidateK 10 -Notes "Step 24 limited dense validation"

Limited hybrid:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/run-evaluation.ps1 -Mode hybrid -Name "Hybrid limited Step 24 eval" -QueryLimit 10 -TopK 10 -Bm25CandidateK 50 -DenseCandidateK 50 -RrfK 60 -Notes "Step 24 limited hybrid validation"

Tiny hybrid rerank:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/run-evaluation.ps1 -Mode hybrid_rerank -Name "Hybrid rerank tiny Step 24 eval" -QueryLimit 3 -TopK 10 -Bm25CandidateK 50 -DenseCandidateK 50 -HybridCandidateK 50 -RerankTopN 25 -RrfK 60 -Notes "Step 24 tiny rerank validation"

The legacy `run-eval.ps1` delegates to `run-evaluation.ps1`:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/run-eval.ps1 -Mode bm25 -QueryLimit 10

Evaluation DB inspection:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, name, status, query_count, failed_query_count, recall_at_5, recall_at_10, mrr_at_10, ndcg_at_10, avg_latency_ms, p50_latency_ms, p95_latency_ms, report_path, created_at from evaluation_runs order by created_at desc limit 10;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from evaluation_query_results;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select report_format, report_path, created_at from evaluation_reports order by created_at desc limit 5;"

## Step 28 frontend foundation commands

Step 28 initializes the frontend foundation under `apps/web`.

Frontend scope:

- Next.js App Router with TypeScript and Tailwind CSS.
- Real API client using `NEXT_PUBLIC_API_BASE_URL`.
- Default backend URL is `http://localhost:8000`.
- Overview uses real FastAPI data only.
- Route skeletons are intentionally not fake dashboards.
- No frontend metrics are invented.

The backend API should be running before testing the Overview page in a browser.

Direct frontend commands:

    cd apps/web
    npm install
    npm run typecheck
    npm run build
    cd ../..

PowerShell helpers:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/web.ps1
    powershell -ExecutionPolicy Bypass -File scripts/powershell/web-build.ps1
    powershell -ExecutionPolicy Bypass -File scripts/powershell/web-lint.ps1

Environment:

    copy apps\web\.env.example apps\web\.env.local

Then edit `apps/web/.env.local` only if your backend is not running on `http://localhost:8000`.

Overview data sources:

- `GET /api/v1/health`
- `GET /api/v1/health/db`
- `GET /api/v1/system/opensearch`
- `GET /api/v1/system/qdrant`
- `GET /api/v1/indexes/status`
- `GET /api/v1/evaluations/runs`
- `GET /api/v1/experiments/configs`
- `GET /api/v1/search/traces`
- `GET /api/v1/datasets`
- `GET /api/v1/replay/saved-queries`

## Step 26 experiment configs and comparison matrix

Step 26 adds reusable experiment configs and a comparison matrix built from real evaluation runs.

Experiment configs define retrieval parameters for repeatable evaluations:

- `bm25_baseline`
- `dense_baseline`
- `hybrid_rrf_default`
- `hybrid_rerank_default`

Comparison rules:

- Comparison rows come from real `evaluation_runs`.
- Evaluation runs launched from a config store `experiment_config_id`.
- Metrics are not tuned or faked; if a mode misses relevant documents, the metrics remain low or zero.
- Comparison reports are written to `reports/evaluations/comparisons`.
- Sync comparison is available through CLI; async comparison is available through API/RQ.
- Query replay, frontend work, chatbot behavior, and fake benchmark results are not part of this step.

Seed default configs:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/seed-experiment-configs.ps1

Inspect configs:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, name, retrieval_mode, bm25_candidate_k, dense_candidate_k, hybrid_candidate_k, rerank_top_n, top_k_final, fusion_method, is_default from experiment_configs order by name;"

Run limited sync comparison:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/run-comparison.ps1 -UseDefaults -QueryLimit 5 -Name "Step 26 default comparison" -Notes "Step 26 sync comparison validation"

Inspect evaluation runs with configs:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select er.name, er.status, er.query_count, er.failed_query_count, er.recall_at_10, er.mrr_at_10, er.ndcg_at_10, ec.name as config_name, ec.retrieval_mode from evaluation_runs er left join experiment_configs ec on er.experiment_config_id = ec.id order by er.created_at desc limit 12;"

Comparison reports:

    dir reports\evaluations\comparisons

API list configs:

    Invoke-RestMethod "http://localhost:8000/api/v1/experiments/configs?limit=10&offset=0"

API seed defaults:

    Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/experiments/configs/seed-defaults -Headers @{"X-Admin-API-Key"="replace-me"}

Async comparison:

    $body = @{
      name = "Step 26 async default comparison"
      use_defaults = $true
      query_limit = 3
      notes = "Step 26 async comparison validation"
    } | ConvertTo-Json

    $job = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/experiments/comparisons -ContentType "application/json" -Headers @{"X-Admin-API-Key"="replace-me"} -Body $body

Job status:

    Invoke-RestMethod "http://localhost:8000/api/v1/system/jobs/$($job.job_id)"

PowerShell helpers:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/list-experiment-configs.ps1
    powershell -ExecutionPolicy Bypass -File scripts/powershell/start-comparison-job.ps1 -UseDefaults -QueryLimit 3 -Name "Step 26 helper async comparison" -Notes "helper validation"

Final DB checks:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from experiment_configs;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from evaluation_runs where experiment_config_id is not null;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select name, status, query_count, failed_query_count, recall_at_10, mrr_at_10, ndcg_at_10 from evaluation_runs order by created_at desc limit 10;"

## Step 27 saved queries and query replay

Step 27 adds saved queries, a deterministic golden query set, and a query replay harness.

Replay is different from full evaluation:

- Evaluation runs benchmark many queries and store aggregate evaluation rows.
- Query replay focuses on individual saved queries or a small golden set for trace-level debugging and regression analysis.
- Replay uses the existing search service, so normal `queries`, `query_traces`, and `retrieval_candidates` are still created.
- Replay writes `query_replays` rows and JSON reports under `reports/replays`.
- Golden queries are sourced from real SciFact benchmark queries with real qrels.
- Replay metrics are document-level when qrels are available.
- Source trace vs target trace comparison is used for rank movement and overlap debugging.
- No fake golden labels, fake benchmark results, frontend behavior, or chatbot/RAG behavior is included.

Seed golden queries:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/seed-golden-queries.ps1 -Limit 10

Inspect saved queries:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, name, source, text, metadata_json->>'query_external_id' as query_external_id, created_at from saved_queries order by created_at desc limit 12;"

Replay one saved query:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/replay-saved-query.ps1 -SavedQueryId "<saved_query_id>" -Mode hybrid_rerank -TopK 10 -Bm25CandidateK 50 -DenseCandidateK 50 -HybridCandidateK 50 -RerankTopN 25 -RrfK 60

Run limited golden replay:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/run-golden-replay.ps1 -Name "Step 27 golden replay validation" -Mode hybrid_rerank -Limit 3 -TopK 10 -Bm25CandidateK 50 -DenseCandidateK 50 -HybridCandidateK 50 -RerankTopN 25 -RrfK 60 -Notes "Step 27 sync golden replay validation"

Inspect query replays:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, saved_query_id, status, source_trace_id, target_trace_id, experiment_config_id, index_version_id, error_message, created_at from query_replays order by created_at desc limit 10;"

Reports:

    dir reports\replays

API list saved queries:

    Invoke-RestMethod "http://localhost:8000/api/v1/replay/saved-queries?limit=10&offset=0"

API seed golden:

    $seedBody = @{
      dataset_name = "beir/scifact"
      dataset_version = "test"
      limit = 10
    } | ConvertTo-Json

    Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/replay/saved-queries/seed-golden -ContentType "application/json" -Headers @{"X-Admin-API-Key"="replace-me"} -Body $seedBody

Async golden replay:

    $body = @{
      name = "Step 27 async golden replay validation"
      source = "golden_scifact"
      retrieval_mode = "hybrid"
      limit = 3
      top_k = 10
      bm25_candidate_k = 50
      dense_candidate_k = 50
      rrf_k = 60
      notes = "Step 27 async golden replay validation"
    } | ConvertTo-Json

    $job = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/replay/golden/run -ContentType "application/json" -Headers @{"X-Admin-API-Key"="replace-me"} -Body $body

Job status:

    Invoke-RestMethod "http://localhost:8000/api/v1/system/jobs/$($job.job_id)"

PowerShell helpers:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/list-saved-queries.ps1 -Limit 5
    powershell -ExecutionPolicy Bypass -File scripts/powershell/start-golden-replay-job.ps1 -Name "Step 27 helper async replay" -Mode hybrid -Limit 3 -TopK 10 -Bm25CandidateK 50 -DenseCandidateK 50 -RrfK 60
    powershell -ExecutionPolicy Bypass -File scripts/powershell/list-query-replays.ps1 -Limit 5

Final DB checks:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from saved_queries;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select status, count(*) from query_replays group by status order by status;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select source, count(*) from saved_queries group by source order by source;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select retrieval_mode, count(*) from queries group by retrieval_mode order by retrieval_mode;"

Report files:

    dir reports\evaluations
    Get-Content reports\evaluations\<REPORT_FILE_NAME>.json | Select-Object -First 40

Trace side effects:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select retrieval_mode, count(*) from queries group by retrieval_mode order by retrieval_mode;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select source, count(*) from retrieval_candidates group by source order by source;"

## Step 25 evaluation API and async job commands

Step 25 exposes evaluation runs through FastAPI and wraps the Step 24 synchronous runner in an RQ job.

Evaluation API rules:

- `POST /api/v1/evaluations/runs` enqueues an async evaluation job and requires the admin API key.
- Read-only endpoints do not require an admin key.
- The worker job calls the existing offline runner, so real `evaluation_runs`, `evaluation_query_results`, `evaluation_reports`, query traces, and candidate rows are created.
- Triggering dense, hybrid, or hybrid rerank evaluation can be expensive.
- Experiment config management, comparison matrices, query replay, frontend work, and fake benchmark results are not implemented here.

Start infra:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/dev.ps1

Start API:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/api.ps1

Start worker:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/worker.ps1

Health:

    Invoke-RestMethod http://localhost:8000/api/v1/health
    Invoke-RestMethod http://localhost:8000/api/v1/health/db
    Invoke-RestMethod http://localhost:8000/api/v1/system/queue
    Invoke-RestMethod http://localhost:8000/api/v1/indexes/status

Trigger eval with API:

    $body = @{
      retrieval_mode = "bm25"
      name = "BM25 async Step 25 validation"
      query_limit = 5
      top_k = 10
      candidate_k = 10
      notes = "Step 25 async BM25 validation"
    } | ConvertTo-Json

    Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/evaluations/runs -ContentType "application/json" -Headers @{"X-Admin-API-Key"="replace-me"} -Body $body

PowerShell helper:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/start-evaluation-job.ps1 -Mode bm25 -Name "BM25 async Step 25 validation" -QueryLimit 5 -TopK 10 -CandidateK 10 -Notes "Step 25 async BM25 validation"

List runs:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/list-evaluation-runs.ps1 -Limit 5

Show run:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/show-evaluation-run.ps1 -EvaluationRunId "<run_id>"

Show results:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/show-evaluation-run.ps1 -EvaluationRunId "<run_id>" -Results

Show report:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/show-evaluation-run.ps1 -EvaluationRunId "<run_id>" -Report

DB inspection:

    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select id, name, status, query_count, failed_query_count, recall_at_5, recall_at_10, mrr_at_10, ndcg_at_10, avg_latency_ms, report_path, created_at from evaluation_runs order by created_at desc limit 10;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select count(*) from evaluation_query_results;"
    docker exec aletheia-postgres psql -U aletheia -d aletheia -c "select report_format, report_path, created_at from evaluation_reports order by created_at desc limit 5;"

## Step 29 Search Lab UI

The `/search` route is now a real Search Lab UI connected to the FastAPI search endpoint. It runs real retrieval requests only and does not show fake search results, generated answers, invented relevance labels, or local JSON fallback data.

Supported modes:

- BM25
- Dense
- Hybrid RRF
- Hybrid Rerank

The backend API must be running before browser validation. Hybrid rerank may be slower on first run because the backend loads and runs the cross-encoder model.

Start infrastructure:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/dev.ps1

Start API:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/api.ps1

Start web:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/web.ps1

Frontend validation:

    cd apps/web
    npm run typecheck
    npm run build
    npm run lint
    cd ../..

Scripted frontend validation:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/web-build.ps1
    powershell -ExecutionPolicy Bypass -File scripts/powershell/web-lint.ps1

Doctor:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/doctor.ps1

Manual Search Lab checks:

- Open `http://localhost:3000/search`.
- Run a BM25 query with `top_k=5` and `candidate_k=10`.
- Run a dense query with `top_k=5` and `candidate_k=10`.
- Run a hybrid query with `bm25_candidate_k=50`, `dense_candidate_k=50`, and `rrf_k=60`.
- Run a hybrid rerank query with `hybrid_candidate_k=50`, `rerank_top_n=25`, and `rrf_k=60`.
- Confirm `query_id`, `trace_id`, latency fields, ranked chunks, and score breakdowns are shown from the backend response.

## Step 30 Query Trace UI

The `/traces` route is now a real Query Trace UI for search observability. It lists real traces from FastAPI only and supports retrieval mode and status filters. It can deep-link to a trace with `?traceId=<trace_id>`.

The trace UI shows:

- trace list with mode, status, latency, query ID, and trace ID
- trace detail metadata and index version information
- request parameters
- pipeline stage latency for BM25, dense, fusion, and reranker stages when present
- candidate provenance grouped by source
- rank movement for hybrid rerank traces when present
- raw trace JSON for debugging

Search Lab trace links use `/traces?traceId=<trace_id>`. Backend API must be running before browser validation.

Start infrastructure:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/dev.ps1

Start API:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/api.ps1

Start web:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/web.ps1

Frontend validation:

    cd apps/web
    npm run typecheck
    npm run build
    npm run lint
    cd ../..

Scripted frontend validation:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/web-build.ps1
    powershell -ExecutionPolicy Bypass -File scripts/powershell/web-lint.ps1

Doctor:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/doctor.ps1

Manual trace checks:

- Open `http://localhost:3000/traces`.
- Filter by `hybrid_rerank` and `completed` if rerank traces exist.
- Open a trace from the list.
- Confirm stages, ranking summary, candidates, rank movement, and raw JSON render from backend trace data.
- Open `http://localhost:3000/traces?traceId=<trace_id>` with a real trace ID.

## Step 31 Evaluation Dashboard UI

The `/evaluations` route is now a real Evaluation Dashboard UI. It reads real evaluation API data and does not display fake benchmark results, fake reports, or invented chart entries.

The dashboard shows:

- recent real evaluation runs
- status filtering
- metric cards for Recall@5, Recall@10, MRR@10, NDCG@10, latency, and failed queries
- charts built only from real run metric and latency fields
- selected run metadata and config JSON
- first 50 per-query evaluation results
- trace links from query results to `/traces?traceId=<trace_id>`
- report metadata, summary JSON, and optional full report JSON

Backend API must be running before browser validation.

Start infrastructure:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/dev.ps1

Start API:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/api.ps1

Start web:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/web.ps1

Frontend validation:

    cd apps/web
    npm install
    npm run typecheck
    npm run build
    npm run lint
    cd ../..

Scripted frontend validation:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/web-build.ps1
    powershell -ExecutionPolicy Bypass -File scripts/powershell/web-lint.ps1

Doctor:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/doctor.ps1

Manual evaluation checks:

- Open `http://localhost:3000/evaluations`.
- Confirm the run table contains real backend evaluation runs.
- Select completed BM25, dense, hybrid, or hybrid rerank runs if available.
- Confirm metric cards and charts only render real numeric fields.
- Confirm per-query result trace links open the Query Trace UI.
- Confirm missing reports show an unavailable state rather than invented report content.

## Step 32 Experiment Matrix UI

The `/experiments` route is now a real Experiment Matrix UI. It reads real experiment configs and real evaluation runs from FastAPI, groups completed evaluation runs by `experiment_config_id`, and shows the latest completed run per config.

The matrix shows:

- default and custom experiment configs
- retrieval mode and config parameters
- latest completed run metrics per config
- best-by-metric indicators computed from real numeric values only
- quality and latency charts built only from real evaluation run fields
- config details including candidate sizes, fusion method, model names, and RRF parameters
- local admin actions for seeding defaults and starting default comparison jobs

Best-by-metric indicators are not shown unless at least two configs have comparable real values. The UI does not create fake winners, fake metrics, fake configs, or fake chart entries.

Backend API must be running before browser validation. Async comparison jobs require Redis and an RQ worker.

Start infrastructure:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/dev.ps1

Start API:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/api.ps1

Start worker for comparison jobs:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/worker.ps1

Start web:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/web.ps1

Frontend validation:

    cd apps/web
    npm run typecheck
    npm run build
    npm run lint
    cd ../..

Scripted frontend validation:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/web-build.ps1
    powershell -ExecutionPolicy Bypass -File scripts/powershell/web-lint.ps1

Doctor:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/doctor.ps1

Manual experiment checks:

- Open `http://localhost:3000/experiments`.
- Confirm configs are loaded from `GET /api/v1/experiments/configs`.
- Confirm metrics come from real `GET /api/v1/evaluations/runs` rows.
- Confirm configs without completed runs show unavailable metrics.
- Confirm best badges appear only when comparable real values exist.
- Confirm admin comparison trigger requires an admin API key and reports queued job status honestly.
