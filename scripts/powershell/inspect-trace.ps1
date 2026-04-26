param(
    [Parameter(Mandatory = $true)]
    [string]$TraceId,
    [string]$Source,
    [switch]$Candidates,
    [switch]$Text
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run setup before inspecting traces."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    $ArgsList = @("-m", "app.cli.inspect_trace", "--trace-id", $TraceId)
    if (-not [string]::IsNullOrWhiteSpace($Source)) {
        $ArgsList += @("--source", $Source)
    }
    if ($Candidates) {
        $ArgsList += "--candidates"
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
