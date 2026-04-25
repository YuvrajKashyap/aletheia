# Enqueues a harmless Step 7 worker test job through the running FastAPI backend.

param(
    [string]$Message = "pong"
)

$ErrorActionPreference = "Stop"

$body = @{
    message = $Message
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8000/api/v1/system/jobs/test" `
    -ContentType "application/json" `
    -Body $body
