# Resets the local Aletheia Docker infrastructure and deletes volumes.
# This is destructive and requires -ConfirmReset.

param(
    [switch]$ConfirmReset
)

$ErrorActionPreference = "Stop"

if (-not $ConfirmReset) {
    Write-Host ""
    Write-Host "WARNING: This command deletes local Aletheia Docker volumes."
    Write-Host "It will remove local Postgres, Redis, OpenSearch, and Qdrant data."
    Write-Host ""
    Write-Host "To confirm, run:"
    Write-Host "powershell -ExecutionPolicy Bypass -File scripts/powershell/infra-reset.ps1 -ConfirmReset"
    Write-Host ""
    exit 0
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR docker is not available on PATH. Install/start Docker Desktop first."
    exit 1
}

Write-Host ""
Write-Host "Resetting Aletheia local infrastructure and deleting Docker volumes..."
Write-Host ""

docker compose down -v

Write-Host ""
Write-Host "Aletheia local infrastructure reset complete. Docker volumes were deleted."
