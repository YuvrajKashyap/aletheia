param(
    [string]$SavedQueryId,
    [string]$Status,
    [int]$Limit = 50,
    [int]$Offset = 0
)

$ErrorActionPreference = "Stop"
$Query = @{
    limit = $Limit
    offset = $Offset
}
if (-not [string]::IsNullOrWhiteSpace($SavedQueryId)) {
    $Query["saved_query_id"] = $SavedQueryId
}
if (-not [string]::IsNullOrWhiteSpace($Status)) {
    $Query["status"] = $Status
}
$QueryString = ($Query.GetEnumerator() | ForEach-Object {
    "$($_.Key)=$([uri]::EscapeDataString([string]$_.Value))"
}) -join "&"

Invoke-RestMethod "http://localhost:8000/api/v1/replay/runs?$QueryString"
