param(
    [string]$RetrievalMode,
    [string]$Status,
    [int]$Limit = 50,
    [int]$Offset = 0
)

$ErrorActionPreference = "Stop"
$Query = @{
    limit = $Limit
    offset = $Offset
}
if (-not [string]::IsNullOrWhiteSpace($RetrievalMode)) {
    $Query.retrieval_mode = $RetrievalMode
}
if (-not [string]::IsNullOrWhiteSpace($Status)) {
    $Query.status = $Status
}

$QueryString = ($Query.GetEnumerator() | ForEach-Object {
    "$([System.Uri]::EscapeDataString($_.Key))=$([System.Uri]::EscapeDataString([string]$_.Value))"
}) -join "&"

try {
    Invoke-RestMethod "http://localhost:8000/api/v1/search/traces?$QueryString"
}
catch {
    Write-Host "Request failed."
    if ($_.Exception.Response) {
        Write-Host "Status: $([int]$_.Exception.Response.StatusCode)"
        $Reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host $Reader.ReadToEnd()
    } else {
        Write-Host $_.Exception.Message
    }
    exit 1
}
