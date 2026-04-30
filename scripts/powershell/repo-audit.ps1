$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
Set-Location $RepoRoot

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "[AUDIT] $Title"
}

function Test-AnyTracked {
    param(
        [string[]]$Files,
        [string]$Pattern
    )

    foreach ($file in $Files) {
        if ($file -like $Pattern) {
            return $true
        }
    }
    return $false
}

Write-Section "Git status"
git status --short

Write-Section "Common local artifacts"
$localChecks = @(
    ".env",
    ".env.local",
    "apps/web/.env.local",
    "services/api/.venv",
    "apps/web/node_modules",
    "apps/web/.next",
    "data/models",
    "data/raw/ir_datasets"
)

foreach ($path in $localChecks) {
    if (Test-Path $path) {
        Write-Host "FOUND local artifact: $path"
    } else {
        Write-Host "OK missing local artifact: $path"
    }
}

$benchmarkReports = @(Get-ChildItem -Path "reports/benchmarks" -Filter "*.json" -File -ErrorAction SilentlyContinue)
$smokeReports = @(Get-ChildItem -Path "reports/smoke" -Filter "*.json" -File -ErrorAction SilentlyContinue)
Write-Host "Local benchmark JSON reports: $($benchmarkReports.Count)"
Write-Host "Local smoke JSON reports: $($smokeReports.Count)"

Write-Section "Tracked dangerous patterns"
$tracked = @(git ls-files)
$dangerousPatterns = @(
    ".env",
    ".env.local",
    "apps/web/.env.local",
    "*.env.local",
    "*node_modules*",
    "*.next*",
    "services/api/.venv*",
    "data/models*",
    "data/raw/ir_datasets*",
    "reports/benchmarks/*.json",
    "reports/smoke/*.json"
)

$foundDanger = $false
foreach ($pattern in $dangerousPatterns) {
    if (Test-AnyTracked -Files $tracked -Pattern $pattern) {
        Write-Host "FAIL tracked dangerous pattern: $pattern"
        $foundDanger = $true
    } else {
        Write-Host "PASS no tracked files for: $pattern"
    }
}

Write-Section "Tracked secret keyword review"
Write-Host "Review these tracked filenames manually. Docs may mention password or secret without containing secrets."
$tracked | Select-String -Pattern "\.env|connection|password|secret" -CaseSensitive:$false

Write-Section "Doctor"
powershell -ExecutionPolicy Bypass -File scripts/powershell/doctor.ps1

Write-Section "Manual reminders"
Write-Host "Manually check the latest GitHub Actions run."
Write-Host "Manually open the public demo: https://aletheia.yuvrajkashyap.com"
Write-Host "Manually review any secret keyword output above."

if ($foundDanger) {
    throw "Tracked dangerous files were found. Remove them before release readiness."
}

Write-Host ""
Write-Host "[AUDIT] Repository audit passed."
