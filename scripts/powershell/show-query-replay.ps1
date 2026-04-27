param(
    [Parameter(Mandatory = $true)]
    [string]$QueryReplayId
)

$ErrorActionPreference = "Stop"
Invoke-RestMethod "http://localhost:8000/api/v1/replay/runs/$QueryReplayId"
