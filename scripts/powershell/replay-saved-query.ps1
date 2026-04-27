param(
    [Parameter(Mandatory = $true)]
    [string]$SavedQueryId,
    [ValidateSet("bm25", "dense", "hybrid", "hybrid_rerank")]
    [string]$Mode,
    [string]$ExperimentConfigId,
    [string]$ExperimentConfigName,
    [string]$SourceTraceId,
    [int]$TopK = 10,
    [int]$CandidateK,
    [int]$Bm25CandidateK,
    [int]$DenseCandidateK,
    [int]$HybridCandidateK,
    [int]$RerankTopN,
    [int]$RrfK = 60
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run setup before replaying saved queries."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    $ArgsList = @("-m", "app.cli.replay_saved_query", "--saved-query-id", $SavedQueryId, "--top-k", "$TopK", "--rrf-k", "$RrfK")
    foreach ($Item in @(
        @("--mode", $Mode),
        @("--experiment-config-id", $ExperimentConfigId),
        @("--experiment-config-name", $ExperimentConfigName),
        @("--source-trace-id", $SourceTraceId)
    )) {
        if (-not [string]::IsNullOrWhiteSpace($Item[1])) {
            $ArgsList += @($Item[0], $Item[1])
        }
    }
    foreach ($Item in @(
        @("--candidate-k", "CandidateK", $CandidateK),
        @("--bm25-candidate-k", "Bm25CandidateK", $Bm25CandidateK),
        @("--dense-candidate-k", "DenseCandidateK", $DenseCandidateK),
        @("--hybrid-candidate-k", "HybridCandidateK", $HybridCandidateK),
        @("--rerank-top-n", "RerankTopN", $RerankTopN)
    )) {
        if ($PSBoundParameters.ContainsKey($Item[1])) {
            $ArgsList += @($Item[0], "$($Item[2])")
        }
    }
    & $Python @ArgsList
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
