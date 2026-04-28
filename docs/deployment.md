# Deployment Readiness

Aletheia is a retrieval, reranking, evaluation, replay, indexing, dataset inspection, and observability platform. Deployment must preserve that identity and must not replace backend data with frontend mock data.

This document describes repo readiness only. It does not create provider accounts or deploy services.

## Local Architecture

Local development uses:

- Next.js frontend in `apps/web`
- FastAPI backend in `services/api`
- RQ worker using the same backend package
- PostgreSQL through Docker Compose
- Redis through Docker Compose
- OpenSearch through Docker Compose
- Qdrant through Docker Compose

The frontend calls FastAPI through `NEXT_PUBLIC_API_BASE_URL`. It never talks directly to Postgres, Redis, OpenSearch, or Qdrant.

## Intended Hosted Architecture

The practical hosted shape is:

- Vercel for the Next.js frontend
- Neon for hosted Postgres
- A Docker-capable host for the FastAPI API service
- A separate Docker-capable worker service for RQ jobs
- Redis from the backend host or a managed Redis provider
- Qdrant Cloud or self-hosted Qdrant
- Managed OpenSearch or self-hosted OpenSearch

OpenSearch can be the most expensive part of the stack. A public demo should not claim production search readiness until real hosted search infrastructure is configured.

## Deployment Stages

1. Deploy the frontend to Vercel with `NEXT_PUBLIC_API_BASE_URL` pointing at the backend API domain.
2. Create the Neon Postgres project and configure `DATABASE_URL`.
3. Deploy the API container and validate `/api/v1/health`.
4. Deploy the worker container as a separate process or service.
5. Configure Redis for queue and worker communication.
6. Choose and configure Qdrant and OpenSearch hosting.
7. Load data, build indexes, run evaluations, and validate the full public demo.

Do not fake search, evaluation, replay, system health, or index state during partial deployment. Pages should show honest API errors or unavailable states until real services are connected.

## Required Environment Variables

Use `.env.production.example` as the placeholder checklist. Real values belong in provider dashboards or secret managers, not in the repository.

Core backend variables:

```text
APP_MODE=production
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DB?sslmode=require
REDIS_URL=redis://USER:PASSWORD@HOST:6379/0
OPENSEARCH_URL=https://OPENSEARCH_HOST
QDRANT_URL=https://QDRANT_HOST
ADMIN_API_KEY=<real secret>
CORS_ALLOWED_ORIGINS=https://aletheia.yuvrajkashyap.com
```

Core frontend variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://<backend-api-domain>
```

## Migrations

Run Alembic migrations against the hosted Postgres database before using the API:

```powershell
cd services/api
.\.venv\Scripts\python.exe -m alembic upgrade head
```

For Linux or hosted jobs:

```bash
cd services/api
python -m alembic upgrade head
```

Use the direct connection string recommended by the database provider for migrations when applicable.

## Data and Index Strategy

The local full stack remains the source of truth until hosted OpenSearch and Qdrant are configured. Hosted demo data must be loaded through existing ingestion, chunking, indexing, evaluation, and replay workflows.

Do not add fake corpus rows, fake qrels, fake metrics, fake traces, fake index jobs, or fake system events to fill deployment gaps.

## Admin Safety

Production and demo modes require a real `ADMIN_API_KEY`. Admin actions should only be used intentionally from trusted environments. Public demo deployments should restrict expensive write actions through environment and key management.

Never commit provider credentials, database URLs, API keys, or generated `.env` files.

## CORS and Domains

Set `CORS_ALLOWED_ORIGINS` to the deployed frontend origin and any approved custom domain. For example:

```text
CORS_ALLOWED_ORIGINS=https://aletheia.yuvrajkashyap.com,https://aletheia.vercel.app
```

The backend config parses comma-separated origins.
