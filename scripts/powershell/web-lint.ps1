param()

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$WebRoot = Join-Path $RepoRoot "apps\web"

if (-not (Test-Path $WebRoot)) {
    Write-Error "Missing apps/web frontend directory."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "npm is required to validate the frontend."
}

$PreviousLocation = Get-Location
try {
    Set-Location $WebRoot
    npm run lint
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    npm run typecheck
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
