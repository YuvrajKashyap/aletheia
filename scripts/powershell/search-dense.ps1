param(
    [Parameter(Mandatory = $true)]
    [string]$Query,
    [string]$IndexVersionId,
    [string]$CollectionName,
    [int]$TopK = 10,
    [int]$CandidateK,
    [switch]$Text
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run the setup commands before dense search."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    $ArgsList = @("-m", "app.cli.search_dense", $Query, "--top-k", "$TopK")
    if (-not [string]::IsNullOrWhiteSpace($IndexVersionId)) {
        $ArgsList += @("--index-version-id", $IndexVersionId)
    }
    if (-not [string]::IsNullOrWhiteSpace($CollectionName)) {
        $ArgsList += @("--collection-name", $CollectionName)
    }
    if ($PSBoundParameters.ContainsKey("CandidateK")) {
        $ArgsList += @("--candidate-k", "$CandidateK")
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
