# Activates a metadata-only index version through the running FastAPI backend.

param(
    [Parameter(Mandatory=$true)]
    [string]$IndexVersionId,
    [string]$AdminApiKey = "replace-me"
)

$ErrorActionPreference = "Stop"

$headers = @{
    "X-Admin-API-Key" = $AdminApiKey
}

Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8000/api/v1/indexes/versions/$IndexVersionId/activate" `
    -Headers $headers
