param(
    [switch]$UseDefaults,
    [string[]]$ConfigName,
    [string[]]$ConfigId,
    [int]$QueryLimit,
    [int]$QueryOffset = 0,
    [string]$Name,
    [string]$DatasetName = "beir/scifact",
    [string]$DatasetVersion = "test",
    [string]$IndexVersionId,
    [string]$Notes
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run setup before running comparison."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    $ArgsList = @(
        "-m", "app.cli.run_comparison",
        "--dataset-name", $DatasetName,
        "--dataset-version", $DatasetVersion,
        "--query-offset", "$QueryOffset"
    )
    if ($UseDefaults) {
        $ArgsList += "--use-defaults"
    }
    foreach ($Value in $ConfigName) {
        if (-not [string]::IsNullOrWhiteSpace($Value)) {
            $ArgsList += @("--config-name", $Value)
        }
    }
    foreach ($Value in $ConfigId) {
        if (-not [string]::IsNullOrWhiteSpace($Value)) {
            $ArgsList += @("--config-id", $Value)
        }
    }
    if ($PSBoundParameters.ContainsKey("QueryLimit")) {
        $ArgsList += @("--query-limit", "$QueryLimit")
    }
    if (-not [string]::IsNullOrWhiteSpace($Name)) {
        $ArgsList += @("--name", $Name)
    }
    if (-not [string]::IsNullOrWhiteSpace($IndexVersionId)) {
        $ArgsList += @("--index-version-id", $IndexVersionId)
    }
    if (-not [string]::IsNullOrWhiteSpace($Notes)) {
        $ArgsList += @("--notes", $Notes)
    }

    & $Python @ArgsList
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
