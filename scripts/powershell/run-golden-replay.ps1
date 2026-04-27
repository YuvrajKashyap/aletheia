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
    [string]$Notes
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run setup before running golden replay."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    $ArgsList = @("-m", "app.cli.run_golden_replay", "--source", $Source, "--offset", "$Offset", "--top-k", "$TopK", "--rrf-k", "$RrfK")
    foreach ($Item in @(
        @("--name", $Name),
        @("--mode", $Mode),
        @("--experiment-config-id", $ExperimentConfigId),
        @("--experiment-config-name", $ExperimentConfigName),
        @("--notes", $Notes)
    )) {
        if (-not [string]::IsNullOrWhiteSpace($Item[1])) {
            $ArgsList += @($Item[0], $Item[1])
        }
    }
    foreach ($Item in @(
        @("--limit", "Limit", $Limit),
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
