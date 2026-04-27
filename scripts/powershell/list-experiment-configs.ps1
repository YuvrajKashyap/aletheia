param(
    [ValidateSet("bm25", "dense", "hybrid", "hybrid_rerank")]
    [string]$RetrievalMode,
    [bool]$IsDefault,
    [int]$Limit = 50,
    [int]$Offset = 0
)

$ErrorActionPreference = "Stop"
$Query = @{
    limit = $Limit
    offset = $Offset
}
if (-not [string]::IsNullOrWhiteSpace($RetrievalMode)) {
    $Query["retrieval_mode"] = $RetrievalMode
}
if ($PSBoundParameters.ContainsKey("IsDefault")) {
    $Query["is_default"] = $IsDefault
}

$QueryString = ($Query.GetEnumerator() | ForEach-Object {
    "$($_.Key)=$([uri]::EscapeDataString([string]$_.Value))"
}) -join "&"

Invoke-RestMethod "http://localhost:8000/api/v1/experiments/configs?$QueryString"
