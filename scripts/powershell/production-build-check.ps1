$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
Set-Location $RepoRoot

function Invoke-Section {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )

    Write-Host ""
    Write-Host "== $Name =="
    & $Command
}

Invoke-Section "Backend tests" {
    & ".\services\api\.venv\Scripts\python.exe" -m pytest services/api/tests
}

Invoke-Section "Backend ruff" {
    & ".\services\api\.venv\Scripts\python.exe" -m ruff check services/api/app services/api/tests
}

Invoke-Section "Frontend typecheck" {
    Push-Location apps/web
    try {
        npm run typecheck
    } finally {
        Pop-Location
    }
}

Invoke-Section "Frontend build" {
    Push-Location apps/web
    try {
        npm run build
    } finally {
        Pop-Location
    }
}

Invoke-Section "Frontend lint" {
    Push-Location apps/web
    try {
        npm run lint
    } finally {
        Pop-Location
    }
}

Invoke-Section "Doctor" {
    powershell -ExecutionPolicy Bypass -File scripts/powershell/doctor.ps1
}

Write-Host ""
Write-Host "Production build check passed."
