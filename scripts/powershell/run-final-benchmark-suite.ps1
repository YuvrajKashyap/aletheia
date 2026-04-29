param(
    [string]$Config = "configs/final-benchmark-suite.json",
    [string]$OutputDir = "reports/benchmarks",
    [switch]$DryRun,
    [switch]$SkipRerank,
    [switch]$RerankFull,
    [string]$OnlyMode
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
$Python = Join-Path $RepoRoot "services\api\.venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Backend virtual environment not found at $Python"
}

$ArgsList = @(
    "-m", "app.cli.run_benchmark_suite",
    "--config", $Config,
    "--output-dir", $OutputDir
)

if ($DryRun) {
    $ArgsList += "--dry-run"
}
if ($SkipRerank) {
    $ArgsList += "--skip-rerank"
}
if ($RerankFull) {
    $ArgsList += "--rerank-full"
}
if ($OnlyMode) {
    $ArgsList += @("--only-mode", $OnlyMode)
}

Write-Host ""
Write-Host "[Benchmark] Final benchmark suite"
Write-Host "[Benchmark] Config: $Config"
Write-Host "[Benchmark] Output directory: $OutputDir"
if ($DryRun) {
    Write-Host "[Benchmark] Dry run only. No evaluation rows will be written."
}

Push-Location (Join-Path $RepoRoot "services\api")
try {
    & $Python @ArgsList
} finally {
    Pop-Location
}
