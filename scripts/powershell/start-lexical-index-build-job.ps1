param(
    [Parameter(Mandatory = $true)]
    [string]$IndexVersionId,
    [switch]$Recreate,
    [int]$Limit,
    [switch]$NoRefresh,
    [string]$AdminApiKey = "replace-me"
)

$ErrorActionPreference = "Stop"
$Body = @{
    recreate = [bool]$Recreate
    refresh = -not [bool]$NoRefresh
}
if ($PSBoundParameters.ContainsKey("Limit")) {
    $Body.limit = $Limit
}

$Json = $Body | ConvertTo-Json
$Uri = "http://localhost:8000/api/v1/indexes/versions/$IndexVersionId/build-lexical"
$Headers = @{ "X-Admin-API-Key" = $AdminApiKey }

try {
    Invoke-RestMethod -Method Post -Uri $Uri -ContentType "application/json" -Headers $Headers -Body $Json
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
