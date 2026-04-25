# Runs Alembic downgrade for the Aletheia API database.
# Requires an explicit -Revision argument.

param(
    [string]$Revision
)

$ErrorActionPreference = "Stop"

if (-not $Revision) {
    Write-Host "Usage:"
    Write-Host "powershell -ExecutionPolicy Bypass -File scripts/powershell/db-downgrade.ps1 -Revision -1"
    Write-Host ""
    Write-Host "No downgrade was run."
    exit 0
}

$repoRoot = Resolve-Path "$PSScriptRoot\..\.."
$apiDir = Join-Path $repoRoot "services\api"
$pythonExe = Join-Path $apiDir ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR backend virtual environment is missing."
    exit 1
}

Push-Location $apiDir
try {
    & $pythonExe -m alembic downgrade $Revision
}
finally {
    Pop-Location
}
