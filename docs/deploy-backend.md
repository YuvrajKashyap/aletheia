# Backend Deployment

This is a provider-neutral readiness guide. Suitable targets include Render Docker deploy, Railway Docker/runtime deploy, Fly.io Docker deploy, or a DigitalOcean VPS running Docker.

## Images

Build the API image from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/docker-build-api.ps1
```

Equivalent Docker command:

```powershell
docker build -f services/api/Dockerfile -t aletheia-api:local .
```

Build the worker image from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/powershell/docker-build-worker.ps1
```

Equivalent Docker command:

```powershell
docker build -f services/api/Dockerfile.worker -t aletheia-worker:local .
```

## Processes

API process:

```text
python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

Worker process:

```text
python -m app.worker.runner
```

Run the API and worker as separate services or processes. Do not run them inside the same process.

## Health Check

Use:

```text
/api/v1/health
```

## Required Environment

Set the backend variables from `.env.production.example` in the provider dashboard or secret manager. Required external services include Postgres, Redis, OpenSearch, and Qdrant.

`ADMIN_API_KEY` must be a real secret in production. Do not use `replace-me`.

## Model Cache

The embedding and reranker models may download at runtime. Configure `MODEL_CACHE_DIR` to a persistent or sufficiently large cache path when the backend host supports it.

## CORS

Set `CORS_ALLOWED_ORIGINS` to the deployed frontend origin and custom domain. The backend accepts comma-separated values.

## Secrets

Never bake secrets into the Docker image. Never commit provider `.env` files.
