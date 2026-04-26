# Enqueues a tracked SciFact ingestion job through the running FastAPI backend.

param(
    [int]$DocumentLimit = 0,
    [int]$QueryLimit = 0,
    [int]$QrelLimit = 0,
    [string]$Split = "test",
    [switch]$NoChunk,
    [int]$ChunkDocumentLimit = 0,
    [switch]$DryRun,
    [string]$AdminApiKey = "replace-me"
)

$ErrorActionPreference = "Stop"

$bodyMap = @{
    split = $Split
    chunk_after_load = -not $NoChunk
    dry_run = [bool]$DryRun
}

if ($DocumentLimit -gt 0) {
    $bodyMap.document_limit = $DocumentLimit
}

if ($QueryLimit -gt 0) {
    $bodyMap.query_limit = $QueryLimit
}

if ($QrelLimit -gt 0) {
    $bodyMap.qrel_limit = $QrelLimit
}

if ($ChunkDocumentLimit -gt 0) {
    $bodyMap.chunk_document_limit = $ChunkDocumentLimit
}

$headers = @{
    "X-Admin-API-Key" = $AdminApiKey
}

$body = $bodyMap | ConvertTo-Json

try {
    Invoke-RestMethod `
        -Method Post `
        -Uri "http://localhost:8000/api/v1/ingestion/datasets/scifact" `
        -ContentType "application/json" `
        -Headers $headers `
        -Body $body
}
catch {
    Write-Host "ERROR SciFact ingestion job request failed."
    Write-Host $_.Exception.Message
    if ($_.Exception.Response) {
        Write-Host "Status:" $_.Exception.Response.StatusCode.value__
        Write-Host "Description:" $_.Exception.Response.StatusDescription
    }
    exit 1
}
