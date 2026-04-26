param(
    [Parameter(Mandatory = $true)]
    [string]$Text,
    [string]$Model,
    [switch]$NoNormalize,
    [switch]$ShowVector,
    [int]$PreviewDimensions = 8
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ApiRoot = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    Write-Error "Missing services/api/.venv. Run the setup commands before embedding text."
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiRoot
    $ArgsList = @("-m", "app.cli.embed_text", $Text, "--preview-dimensions", "$PreviewDimensions")
    if (-not [string]::IsNullOrWhiteSpace($Model)) {
        $ArgsList += @("--model", $Model)
    }
    if ($NoNormalize) {
        $ArgsList += "--no-normalize"
    }
    if ($ShowVector) {
        $ArgsList += "--show-vector"
    }

    & $Python @ArgsList
    exit $LASTEXITCODE
}
finally {
    Set-Location $PreviousLocation
}
