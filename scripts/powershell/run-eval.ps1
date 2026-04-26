param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("bm25", "dense", "hybrid", "hybrid_rerank")]
    [string]$Mode,
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

$ArgsList = @("-File", (Join-Path $PSScriptRoot "run-evaluation.ps1"), "-Mode", $Mode)

foreach ($NameValue in @(
    @("Name", $Name),
    @("DatasetName", $DatasetName),
    @("DatasetVersion", $DatasetVersion),
    @("IndexVersionId", $IndexVersionId),
    @("Notes", $Notes)
)) {
    if (-not [string]::IsNullOrWhiteSpace($NameValue[1])) {
        $ArgsList += @("-$($NameValue[0])", $NameValue[1])
    }
}

$ArgsList += @("-QueryOffset", "$QueryOffset", "-TopK", "$TopK", "-RrfK", "$RrfK")

foreach ($NameValue in @(
    @("QueryLimit", $QueryLimit),
    @("CandidateK", $CandidateK),
    @("Bm25CandidateK", $Bm25CandidateK),
    @("DenseCandidateK", $DenseCandidateK),
    @("HybridCandidateK", $HybridCandidateK),
    @("RerankTopN", $RerankTopN)
)) {
    if ($PSBoundParameters.ContainsKey($NameValue[0])) {
        $ArgsList += @("-$($NameValue[0])", "$($NameValue[1])")
    }
}

powershell -ExecutionPolicy Bypass @ArgsList
exit $LASTEXITCODE
