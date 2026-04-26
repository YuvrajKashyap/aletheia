# Loads BEIR SciFact documents, benchmark queries, and qrels into PostgreSQL.
# Requires the backend virtual environment at services/api/.venv.

param(
    [int]$DocumentLimit = 0,
    [int]$QueryLimit = 0,
    [int]$QrelLimit = 0,
    [string]$Split = "test",
    [switch]$NoChunk,
    [int]$ChunkDocumentLimit = 0,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path "$PSScriptRoot\..\.."
$apiDir = Join-Path $repoRoot "services\api"
$pythonExe = Join-Path $apiDir ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR backend virtual environment is missing."
    Write-Host "Run these commands from the repo root:"
    Write-Host "py -3.11 -m venv services/api/.venv"
    Write-Host ".\services\api\.venv\Scripts\python.exe -m pip install --upgrade pip"
    Write-Host ".\services\api\.venv\Scripts\python.exe -m pip install -e `"services/api[dev]`""
    exit 1
}

$arguments = @("-m", "app.cli.load_scifact", "--split", $Split)

if ($DocumentLimit -gt 0) {
    $arguments += @("--document-limit", $DocumentLimit)
}

if ($QueryLimit -gt 0) {
    $arguments += @("--query-limit", $QueryLimit)
}

if ($QrelLimit -gt 0) {
    $arguments += @("--qrel-limit", $QrelLimit)
}

if ($NoChunk) {
    $arguments += "--no-chunk"
}

if ($ChunkDocumentLimit -gt 0) {
    $arguments += @("--chunk-document-limit", $ChunkDocumentLimit)
}

if ($DryRun) {
    $arguments += "--dry-run"
}

Push-Location $apiDir
try {
    Write-Host "Running SciFact loader..."
    & $pythonExe @arguments
}
finally {
    Pop-Location
}
