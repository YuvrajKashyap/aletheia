param()

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$WebRoot = Join-Path $RepoRoot "apps\web"

if (-not (Test-Path $WebRoot)) {
    Write-Error "Missing apps/web frontend directory."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "npm is required to build the frontend."
}

$PreviousLocation = Get-Location
try {
    Set-Location $WebRoot
    npm run build
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
