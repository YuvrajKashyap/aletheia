# Shows the current Alembic migration revision for the Aletheia API database.

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path "$PSScriptRoot\..\.."
$apiDir = Join-Path $repoRoot "services\api"
$pythonExe = Join-Path $apiDir ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR backend virtual environment is missing."
    exit 1
}

Push-Location $apiDir
try {
    & $pythonExe -m alembic current
}
finally {
    Pop-Location
}
