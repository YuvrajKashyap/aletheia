# Generates database chunks for loaded documents.
# Requires the backend virtual environment at services/api/.venv.

param(
    [string]$DatasetName = "beir/scifact",
    [string]$DatasetVersion = "test",
    [int]$DocumentLimit = 0,
    [string]$Strategy = "scifact_document_v1",
    [string]$ChunkingVersion = "1.0",
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

$arguments = @(
    "-m",
    "app.cli.chunk_documents",
    "--dataset-name",
    $DatasetName,
    "--dataset-version",
    $DatasetVersion,
    "--strategy",
    $Strategy,
    "--chunking-version",
    $ChunkingVersion
)

if ($DocumentLimit -gt 0) {
    $arguments += @("--document-limit", $DocumentLimit)
}

if ($DryRun) {
    $arguments += "--dry-run"
}

Push-Location $apiDir
try {
    Write-Host "Running document chunker..."
    & $pythonExe @arguments
}
finally {
    Pop-Location
}
