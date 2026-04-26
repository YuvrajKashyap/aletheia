param(
    [Parameter(Mandatory = $true)]
    [string]$Query,
    [string]$IndexVersionId,
    [int]$TopK = 10,
    [int]$Bm25CandidateK = 50,
    [int]$DenseCandidateK = 50,
    [int]$RrfK = 60,
    [switch]$Text
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run the setup commands before hybrid search."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    $ArgsList = @(
        "-m", "app.cli.search_hybrid",
        $Query,
        "--top-k", "$TopK",
        "--bm25-candidate-k", "$Bm25CandidateK",
        "--dense-candidate-k", "$DenseCandidateK",
        "--rrf-k", "$RrfK"
    )
    if (-not [string]::IsNullOrWhiteSpace($IndexVersionId)) {
        $ArgsList += @("--index-version-id", $IndexVersionId)
    }
    if ($Text) {
        $ArgsList += "--text"
    }

    & $Python @ArgsList
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
