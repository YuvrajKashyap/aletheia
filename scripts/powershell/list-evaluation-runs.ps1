param(
    [string]$Status,
    [string]$RetrievalMode,
    [int]$Limit = 50,
    [int]$Offset = 0
)

$ErrorActionPreference = "Stop"
$Query = @("limit=$Limit", "offset=$Offset")
if (-not [string]::IsNullOrWhiteSpace($Status)) {
    $Query += "status=$([uri]::EscapeDataString($Status))"
}
if (-not [string]::IsNullOrWhiteSpace($RetrievalMode)) {
    $Query += "retrieval_mode=$([uri]::EscapeDataString($RetrievalMode))"
}

$Uri = "http://localhost:8000/api/v1/evaluations/runs?" + ($Query -join "&")
Invoke-RestMethod $Uri
