param(
    [Parameter(Mandatory = $true)]
    [string]$TraceId,
    [string]$BenchmarkQueryId,
    [string]$QueryExternalId,
    [string]$DatasetName = "beir/scifact",
    [string]$DatasetVersion = "test",
    [switch]$Text
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run setup before evaluating traces."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    $ArgsList = @(
        "-m", "app.cli.evaluate_trace",
        "--trace-id", $TraceId,
        "--dataset-name", $DatasetName,
        "--dataset-version", $DatasetVersion
    )
    if (-not [string]::IsNullOrWhiteSpace($BenchmarkQueryId)) {
        $ArgsList += @("--benchmark-query-id", $BenchmarkQueryId)
    }
    if (-not [string]::IsNullOrWhiteSpace($QueryExternalId)) {
        $ArgsList += @("--query-external-id", $QueryExternalId)
    }
    if ($Text) {
        $ArgsList += "--text"
    }
    & $Python @ArgsList
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
