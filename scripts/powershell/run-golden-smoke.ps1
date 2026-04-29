param(
    [string]$Mode = "hybrid",
    [int]$QueryLimit = 5,
    [int]$TopK = 10,
    [string]$Thresholds = "configs/golden-smoke-thresholds.json",
    [string]$Output = "reports/smoke/golden-smoke-latest.json",
    [switch]$FailOnThreshold,
    [string]$Notes
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
$Python = Join-Path $RepoRoot "services\api\.venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Backend virtual environment not found at $Python"
}

$ArgsList = @(
    "-m", "app.cli.run_golden_smoke",
    "--mode", $Mode,
    "--query-limit", $QueryLimit,
    "--top-k", $TopK,
    "--thresholds", $Thresholds,
    "--output", $Output
)

if ($FailOnThreshold) {
    $ArgsList += "--fail-on-threshold"
}

if ($Notes) {
    $ArgsList += @("--notes", $Notes)
}

Write-Host ""
Write-Host "[Golden Smoke] Local qrels-backed retrieval smoke"
Write-Host "[Golden Smoke] Mode: $Mode"
Write-Host "[Golden Smoke] Query limit: $QueryLimit"
Write-Host "[Golden Smoke] Top K: $TopK"
Write-Host "[Golden Smoke] Thresholds: $Thresholds"
Write-Host "[Golden Smoke] Output: $Output"

Push-Location (Join-Path $RepoRoot "services\api")
try {
    & $Python @ArgsList
} finally {
    Pop-Location
}
