param(
    [string]$IndexVersionId,
    [switch]$Active,
    [switch]$Recreate,
    [int]$Limit,
    [switch]$NoRefresh
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run the setup commands before building indexes."
}

if (-not $Active -and [string]::IsNullOrWhiteSpace($IndexVersionId)) {
    Write-Error "Provide -IndexVersionId or use -Active."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    $ArgsList = @("-m", "app.cli.build_lexical_index")
    if ($Active) {
        $ArgsList += "--active"
    } else {
        $ArgsList += @("--index-version-id", $IndexVersionId)
    }
    if ($Recreate) { $ArgsList += "--recreate" }
    if ($PSBoundParameters.ContainsKey("Limit")) { $ArgsList += @("--limit", "$Limit") }
    if ($NoRefresh) { $ArgsList += "--no-refresh" }

    & $Python @ArgsList
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
