# Creates a metadata-only index version record.

param(
    [string]$DatasetName = "beir/scifact",
    [string]$DatasetVersion = "test",
    [string]$ChunkingStrategy = "scifact_document_v1",
    [string]$ChunkingVersion = "1.0",
    [string]$EmbeddingModel = "",
    [int]$EmbeddingDimension = 0,
    [string]$Notes = "",
    [switch]$MarkReady
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path "$PSScriptRoot\..\.."
$apiDir = Join-Path $repoRoot "services\api"
$pythonExe = Join-Path $apiDir ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR backend virtual environment is missing."
    Write-Host "Run from repo root: .\services\api\.venv\Scripts\python.exe -m pip install -e `"services/api[dev]`""
    exit 1
}

$arguments = @(
    "-m",
    "app.cli.create_index_version",
    "--dataset-name",
    $DatasetName,
    "--dataset-version",
    $DatasetVersion,
    "--chunking-strategy",
    $ChunkingStrategy,
    "--chunking-version",
    $ChunkingVersion
)

if ($EmbeddingModel) {
    $arguments += @("--embedding-model", $EmbeddingModel)
}

if ($EmbeddingDimension -gt 0) {
    $arguments += @("--embedding-dimension", $EmbeddingDimension)
}

if ($Notes) {
    $arguments += @("--notes", $Notes)
}

if ($MarkReady) {
    $arguments += "--mark-ready"
}

Push-Location $apiDir
try {
    & $pythonExe @arguments
}
finally {
    Pop-Location
}
