param(
    [ValidateSet("bm25", "dense", "hybrid", "hybrid_rerank")]
    [string]$Mode,
    [string]$ExperimentConfigId,
    [string]$ExperimentConfigName,
    [string]$Name,
    [string]$DatasetName = "beir/scifact",
    [string]$DatasetVersion = "test",
    [string]$IndexVersionId,
    [int]$QueryLimit,
    [int]$QueryOffset = 0,
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
    dataset_name = $DatasetName
    dataset_version = $DatasetVersion
    query_offset = $QueryOffset
    top_k = $TopK
    rrf_k = $RrfK
}
if (-not [string]::IsNullOrWhiteSpace($Mode)) {
    $Body["retrieval_mode"] = $Mode
}

foreach ($Item in @(
    @("name", $Name),
    @("index_version_id", $IndexVersionId),
    @("experiment_config_id", $ExperimentConfigId),
    @("experiment_config_name", $ExperimentConfigName),
    @("notes", $Notes)
)) {
    if (-not [string]::IsNullOrWhiteSpace($Item[1])) {
        $Body[$Item[0]] = $Item[1]
    }
}

foreach ($Item in @(
    @("query_limit", "QueryLimit", $QueryLimit),
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
    -Uri "http://localhost:8000/api/v1/evaluations/runs" `
    -ContentType "application/json" `
    -Headers @{"X-Admin-API-Key" = $AdminApiKey} `
    -Body $Json
