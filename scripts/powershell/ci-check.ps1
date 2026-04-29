$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")

function Invoke-CiSection {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )

    Write-Host ""
    Write-Host "[CI] $Name"
    & $Command
}

Push-Location $RepoRoot
try {
    Invoke-CiSection "Backend tests" {
        & ".\services\api\.venv\Scripts\python.exe" -m pytest services/api/tests
    }

    Invoke-CiSection "Backend ruff" {
        & ".\services\api\.venv\Scripts\python.exe" -m ruff check services/api/app services/api/tests
    }

    Invoke-CiSection "Frontend typecheck" {
        Push-Location apps/web
        try {
            npm run typecheck
        } finally {
            Pop-Location
        }
    }

    Invoke-CiSection "Frontend lint" {
        Push-Location apps/web
        try {
            npm run lint
        } finally {
            Pop-Location
        }
    }

    Invoke-CiSection "Frontend build" {
        Push-Location apps/web
        try {
            $env:NEXT_PUBLIC_DEMO_MODE = "snapshot"
            npm run build
        } finally {
            Remove-Item Env:NEXT_PUBLIC_DEMO_MODE -ErrorAction SilentlyContinue
            Pop-Location
        }
    }

    Invoke-CiSection "Doctor" {
        python scripts/python/doctor.py
    }

    Write-Host ""
    Write-Host "[CI] Fast quality gate passed."
} finally {
    Pop-Location
}
