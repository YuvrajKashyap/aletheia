param()

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run setup before seeding experiment configs."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    & $Python -m app.cli.seed_experiment_configs
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
