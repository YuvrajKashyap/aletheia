param(
    [string]$InputPath = "data/samples/metrics-fixture.json"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run setup before evaluating metrics fixtures."
}

if ([System.IO.Path]::IsPathRooted($InputPath)) {
    $ResolvedInput = Resolve-Path $InputPath
}
else {
    $ResolvedInput = Resolve-Path (Join-Path $RepoRoot $InputPath)
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    & $Python -m app.cli.evaluate_metrics_fixture --input $ResolvedInput
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
