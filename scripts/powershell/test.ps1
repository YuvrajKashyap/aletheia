# Runs Aletheia backend tests for the current Step 4 API foundation.

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path "$PSScriptRoot\..\.."
$apiDir = Join-Path $repoRoot "services\api"
$pythonExe = Join-Path $apiDir ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host "ERROR backend virtual environment is missing."
    Write-Host "Run these commands from the repo root:"
    Write-Host "py -3.11 -m venv services/api/.venv"
    Write-Host ".\services\api\.venv\Scripts\python.exe -m pip install --upgrade pip"
    Write-Host ".\services\api\.venv\Scripts\python.exe -m pip install -e `"services/api[dev]`""
    exit 1
}

& $pythonExe -m pytest services/api/tests
