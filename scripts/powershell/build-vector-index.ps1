param(
    [string]$IndexVersionId,
    [switch]$Active,
    [switch]$Recreate,
    [int]$Limit,
    [int]$BatchSize
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run setup before building vector indexes."
}

if (-not $Active -and [string]::IsNullOrWhiteSpace($IndexVersionId)) {
    Write-Error "Provide -IndexVersionId or use -Active."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    $ArgsList = @("-m", "app.cli.build_vector_index")
    if ($Active) {
        $ArgsList += "--active"
    } else {
        $ArgsList += @("--index-version-id", $IndexVersionId)
    }
    if ($Recreate) { $ArgsList += "--recreate" }
    if ($PSBoundParameters.ContainsKey("Limit")) { $ArgsList += @("--limit", "$Limit") }
    if ($PSBoundParameters.ContainsKey("BatchSize")) { $ArgsList += @("--batch-size", "$BatchSize") }

    & $Python @ArgsList
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
