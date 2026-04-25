# Checks the admin safety status endpoint on the running FastAPI backend.

param(
    [string]$AdminApiKey = "replace-me"
)

$ErrorActionPreference = "Stop"

$headers = @{
    "X-Admin-API-Key" = $AdminApiKey
}

try {
    Invoke-RestMethod `
        -Method Get `
        -Uri "http://localhost:8000/api/v1/admin/status" `
        -Headers $headers
}
catch {
    Write-Host "ERROR admin status request failed."
    Write-Host $_.Exception.Message
    if ($_.Exception.Response) {
        Write-Host "Status:" $_.Exception.Response.StatusCode.value__
        Write-Host "Description:" $_.Exception.Response.StatusDescription
    }
    exit 1
}
