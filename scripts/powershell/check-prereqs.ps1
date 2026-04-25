# Checks local developer prerequisites for Aletheia.
# This script is intentionally simple and Windows PowerShell friendly.

$ErrorActionPreference = "Continue"

function Test-Tool {
    param(
        [string]$Name,
        [string]$Command,
        [scriptblock]$VersionCommand,
        [string]$Required = "Required",
        [string]$Note = ""
    )

    $exists = Get-Command $Command -ErrorAction SilentlyContinue

    if ($exists) {
        $version = "available"
        if ($VersionCommand) {
            try {
                $output = & $VersionCommand 2>$null
                if ($output) {
                    $version = ($output | Select-Object -First 1).ToString()
                }
            } catch {
                $version = "available, version check failed"
            }
        }

        Write-Host ("PASS  {0,-18} {1}" -f $Name, $version)
        return $true
    }

    if ($Required -eq "Optional") {
        Write-Host ("WARN  {0,-18} missing. Optional. {1}" -f $Name, $Note)
    } else {
        Write-Host ("WARN  {0,-18} missing. {1}" -f $Name, $Note)
    }

    return $false
}

Write-Host ""
Write-Host "Aletheia prerequisite check"
Write-Host "==========================="
Write-Host ("Current directory: {0}" -f (Get-Location))

if (Get-Command git -ErrorAction SilentlyContinue) {
    try {
        $branch = git branch --show-current 2>$null
        if ($branch) {
            Write-Host ("Git branch: {0}" -f $branch)
        } else {
            Write-Host "Git branch: unavailable"
        }
    } catch {
        Write-Host "Git branch: unavailable"
    }
} else {
    Write-Host "Git branch: unavailable because git is missing"
}

Write-Host ""
Write-Host "Tool status"
Write-Host "-----------"

$hasGit = Test-Tool -Name "git" -Command "git" -VersionCommand { git --version } -Note "Git is required for source control."
$hasPython = Test-Tool -Name "python" -Command "python" -VersionCommand { python --version } -Note "Python 3.11 is the target version."
$hasNode = Test-Tool -Name "node" -Command "node" -VersionCommand { node --version } -Note "Node 22 is the target version."
$hasNpm = Test-Tool -Name "npm" -Command "npm" -VersionCommand { npm --version } -Note "npm is required for the future frontend."
$hasDocker = Test-Tool -Name "docker" -Command "docker" -VersionCommand { docker --version } -Note "Docker is required for local infrastructure."

if ($hasDocker) {
    try {
        $composeVersion = docker compose version 2>$null
        if ($LASTEXITCODE -eq 0 -and $composeVersion) {
            Write-Host ("PASS  {0,-18} {1}" -f "docker compose", ($composeVersion | Select-Object -First 1).ToString())
        } else {
            Write-Host ("WARN  {0,-18} missing or unavailable. Docker Compose is required for local infrastructure." -f "docker compose")
        }
    } catch {
        Write-Host ("WARN  {0,-18} missing or unavailable. Docker Compose is required for local infrastructure." -f "docker compose")
    }

    try {
        docker info *> $null
        if ($LASTEXITCODE -eq 0) {
            Write-Host ("PASS  {0,-18} Docker daemon is running." -f "docker daemon")
        } else {
            Write-Host ("WARN  {0,-18} Docker daemon is not available. Start Docker Desktop." -f "docker daemon")
        }
    } catch {
        Write-Host ("WARN  {0,-18} Docker daemon check failed. Start Docker Desktop." -f "docker daemon")
    }
} else {
    Write-Host ("WARN  {0,-18} skipped because docker is missing. Docker Compose is required for local infrastructure." -f "docker compose")
    Write-Host ("WARN  {0,-18} skipped because docker is missing. Start/install Docker Desktop." -f "docker daemon")
}

$hasGh = Test-Tool -Name "gh" -Command "gh" -VersionCommand { gh --version } -Required "Optional" -Note "GitHub CLI is optional but useful." | Out-Null

Write-Host ""
Write-Host "Expected versions"
Write-Host "-----------------"
Write-Host "Python target: 3.11"
Write-Host "Node target: 22"
Write-Host ""
Write-Host "Done."

