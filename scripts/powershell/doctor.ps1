# Runs the standard-library-only Python doctor for Aletheia.

$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "WARN python is not available on PATH. Cannot run scripts/python/doctor.py."
    exit 0
}

python scripts/python/doctor.py
exit $LASTEXITCODE
