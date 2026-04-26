# Reads metadata-only index version status from the running FastAPI backend.

$ErrorActionPreference = "Stop"

Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/v1/indexes/status"
