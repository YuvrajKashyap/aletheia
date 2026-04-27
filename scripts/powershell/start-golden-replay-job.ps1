param(
    [string]$Name,
    [string]$Source = "golden_scifact",
    [ValidateSet("bm25", "dense", "hybrid", "hybrid_rerank")]
    [string]$Mode,
    [string]$ExperimentConfigId,
    [string]$ExperimentConfigName,
    [int]$Limit,
    [int]$Offset = 0,
    [int]$TopK = 10,
    [int]$CandidateK,
    [int]$Bm25CandidateK,
    [int]$DenseCandidateK,
    [int]$HybridCandidateK,
    [int]$RerankTopN,
    [int]$RrfK = 60,
    [string]$Notes,
    [string]$AdminApiKey = "replace-me"
)

$ErrorActionPreference = "Stop"
$Body = @{
    source = $Source
    offset = $Offset
    top_k = $TopK
    rrf_k = $RrfK
}
foreach ($Item in @(
    @("name", $Name),
    @("retrieval_mode", $Mode),
    @("experiment_config_id", $ExperimentConfigId),
    @("experiment_config_name", $ExperimentConfigName),
    @("notes", $Notes)
)) {
    if (-not [string]::IsNullOrWhiteSpace($Item[1])) {
        $Body[$Item[0]] = $Item[1]
    }
}
foreach ($Item in @(
    @("limit", "Limit", $Limit),
    @("candidate_k", "CandidateK", $CandidateK),
    @("bm25_candidate_k", "Bm25CandidateK", $Bm25CandidateK),
    @("dense_candidate_k", "DenseCandidateK", $DenseCandidateK),
    @("hybrid_candidate_k", "HybridCandidateK", $HybridCandidateK),
    @("rerank_top_n", "RerankTopN", $RerankTopN)
)) {
    if ($PSBoundParameters.ContainsKey($Item[1])) {
        $Body[$Item[0]] = $Item[2]
    }
}

$Json = $Body | ConvertTo-Json
Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8000/api/v1/replay/golden/run" `
    -ContentType "application/json" `
    -Headers @{"X-Admin-API-Key" = $AdminApiKey} `
    -Body $Json
