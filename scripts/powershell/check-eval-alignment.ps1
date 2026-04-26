param(
    [string]$DatasetName = "beir/scifact",
    [string]$DatasetVersion = "test"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run setup before checking evaluation alignment."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    & $Python -m app.cli.check_eval_alignment --dataset-name $DatasetName --dataset-version $DatasetVersion
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
