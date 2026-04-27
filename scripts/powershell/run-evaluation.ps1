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
    [string]$Notes
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run setup before running evaluation."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    $ArgsList = @(
        "-m", "app.cli.run_evaluation",
        "--dataset-name", $DatasetName,
        "--dataset-version", $DatasetVersion,
        "--query-offset", "$QueryOffset",
        "--top-k", "$TopK",
        "--rrf-k", "$RrfK"
    )
    if (-not [string]::IsNullOrWhiteSpace($Mode)) {
        $ArgsList += @("--mode", $Mode)
    }
    if (-not [string]::IsNullOrWhiteSpace($ExperimentConfigId)) {
        $ArgsList += @("--experiment-config-id", $ExperimentConfigId)
    }
    if (-not [string]::IsNullOrWhiteSpace($ExperimentConfigName)) {
        $ArgsList += @("--experiment-config-name", $ExperimentConfigName)
    }
    if (-not [string]::IsNullOrWhiteSpace($Name)) {
        $ArgsList += @("--name", $Name)
    }
    if (-not [string]::IsNullOrWhiteSpace($IndexVersionId)) {
        $ArgsList += @("--index-version-id", $IndexVersionId)
    }
    if ($PSBoundParameters.ContainsKey("QueryLimit")) {
        $ArgsList += @("--query-limit", "$QueryLimit")
    }
    if ($PSBoundParameters.ContainsKey("CandidateK")) {
        $ArgsList += @("--candidate-k", "$CandidateK")
    }
    if ($PSBoundParameters.ContainsKey("Bm25CandidateK")) {
        $ArgsList += @("--bm25-candidate-k", "$Bm25CandidateK")
    }
    if ($PSBoundParameters.ContainsKey("DenseCandidateK")) {
        $ArgsList += @("--dense-candidate-k", "$DenseCandidateK")
    }
    if ($PSBoundParameters.ContainsKey("HybridCandidateK")) {
        $ArgsList += @("--hybrid-candidate-k", "$HybridCandidateK")
    }
    if ($PSBoundParameters.ContainsKey("RerankTopN")) {
        $ArgsList += @("--rerank-top-n", "$RerankTopN")
    }
    if (-not [string]::IsNullOrWhiteSpace($Notes)) {
        $ArgsList += @("--notes", $Notes)
    }

    & $Python @ArgsList
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
