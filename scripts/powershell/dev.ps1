# Starts the local Aletheia infrastructure stack.
# This starts infrastructure services only:
# - PostgreSQL
# - Redis
# - OpenSearch
# - Qdrant
#
# It does not start FastAPI, the RQ worker, or the Next.js frontend yet.

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Starting Aletheia local infrastructure..."
Write-Host "Services: postgres, redis, opensearch, qdrant"
Write-Host ""

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR docker is not available on PATH. Install/start Docker Desktop first."
    exit 1
}

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR Docker daemon is not available. Start Docker Desktop and try again."
    exit 1
}

docker compose up -d postgres redis opensearch qdrant

Write-Host ""
Write-Host "Current Docker Compose status:"
docker compose ps

Write-Host ""
Write-Host "Helpful local endpoints:"
Write-Host "Postgres:   localhost:5432"
Write-Host "Redis:      localhost:6379"
Write-Host "OpenSearch: http://localhost:9200"
Write-Host "Qdrant:     http://localhost:6333"
Write-Host ""
Write-Host "Note: API, worker, and web are not started in Step 3."
