# Stops the local Aletheia Docker infrastructure without deleting volumes.

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Stopping Aletheia local infrastructure..."
Write-Host "This will stop containers but keep Docker volumes."
Write-Host ""

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR docker is not available on PATH. Install/start Docker Desktop first."
    exit 1
}

docker compose down

Write-Host ""
Write-Host "Aletheia local infrastructure stopped. Volumes were kept."
