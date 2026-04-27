param(
    [string]$DatasetName = "beir/scifact",
    [string]$DatasetVersion = "test",
    [int]$Limit = 20,
    [int]$Offset = 0
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run setup before seeding golden queries."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    & $Python -m app.cli.seed_golden_queries --dataset-name $DatasetName --dataset-version $DatasetVersion --limit "$Limit" --offset "$Offset"
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
