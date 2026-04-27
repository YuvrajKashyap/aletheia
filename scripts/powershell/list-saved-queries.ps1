param(
    [string]$Source,
    [string]$DatasetId,
    [int]$Limit = 50,
    [int]$Offset = 0
)

$ErrorActionPreference = "Stop"
$Query = @{
    limit = $Limit
    offset = $Offset
}
if (-not [string]::IsNullOrWhiteSpace($Source)) {
    $Query["source"] = $Source
}
if (-not [string]::IsNullOrWhiteSpace($DatasetId)) {
    $Query["dataset_id"] = $DatasetId
}
$QueryString = ($Query.GetEnumerator() | ForEach-Object {
    "$($_.Key)=$([uri]::EscapeDataString([string]$_.Value))"
}) -join "&"

Invoke-RestMethod "http://localhost:8000/api/v1/replay/saved-queries?$QueryString"
