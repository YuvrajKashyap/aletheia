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


