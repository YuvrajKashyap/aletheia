param(
    [Parameter(Mandatory = $true)]
    [string]$Query,
    [string]$RetrievalMode = "bm25",
    [int]$TopK = 10,
    [int]$CandidateK,
    [string]$IndexVersionId
)

$ErrorActionPreference = "Stop"
$Body = @{
    query = $Query
    retrieval_mode = $RetrievalMode
    top_k = $TopK
}
if ($PSBoundParameters.ContainsKey("CandidateK")) {
    $Body.candidate_k = $CandidateK
}
if (-not [string]::IsNullOrWhiteSpace($IndexVersionId)) {
    $Body.index_version_id = $IndexVersionId
}

$Json = $Body | ConvertTo-Json

try {
    Invoke-RestMethod `
        -Method Post `
        -Uri "http://localhost:8000/api/v1/search" `
        -ContentType "application/json" `
        -Body $Json
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
