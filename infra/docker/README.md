# Aletheia Local Docker Infrastructure

This folder documents the local Docker infrastructure for Aletheia.

Aletheia uses Docker Compose for local infrastructure services only. This layer does not include FastAPI, the RQ worker, or the Next.js frontend yet.

## Services

### PostgreSQL

Purpose:

Stores Aletheia application data later, including documents, chunks, queries, qrels, indexes, traces, jobs, experiments, and evaluation runs.

Local connection:

- Host: localhost
- Port: 5432
- Database: aletheia
- User: aletheia
- Password: aletheia

Container:

- aletheia-postgres

### Redis

Purpose:

Provides queue and job infrastructure later for RQ workers.

Local connection:

- Host: localhost
- Port: 6379

Container:

- aletheia-redis

### OpenSearch

Purpose:

Provides BM25 lexical retrieval later.

Local connection:

- URL: http://localhost:9200

Container:

- aletheia-opensearch

Warning:

OpenSearch security is disabled in this local setup only. Do not use this configuration for production.

### Qdrant

Purpose:

Provides dense vector retrieval later.

Local connection:

- URL: http://localhost:6333

Container:

- aletheia-qdrant

## Start local infrastructure

From the project root:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/dev.ps1

Equivalent direct command:

    docker compose up -d postgres redis opensearch qdrant

## Stop local infrastructure

From the project root:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/infra-down.ps1

Equivalent direct command:

    docker compose down

This stops containers without deleting volumes.

## Inspect running containers

From the project root:

    docker compose ps

## Health checks

### PostgreSQL

    docker exec aletheia-postgres pg_isready -U aletheia -d aletheia

### Redis

    docker exec aletheia-redis redis-cli ping

Expected result:

    PONG

### OpenSearch

    Invoke-WebRequest -UseBasicParsing http://localhost:9200

or:

    curl http://localhost:9200

### Qdrant

    Invoke-WebRequest -UseBasicParsing http://localhost:6333

or:

    curl http://localhost:6333

## Reset local infrastructure volumes

Warning:

This deletes local Docker volumes for the Aletheia infrastructure stack.

From the project root:

    powershell -ExecutionPolicy Bypass -File scripts/powershell/infra-reset.ps1 -ConfirmReset

Equivalent direct command:

    docker compose down -v

Only run this when you intentionally want to delete local infrastructure data.


