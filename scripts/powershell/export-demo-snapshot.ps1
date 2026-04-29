param(
    [string]$Output = "../../apps/web/public/demo-data",
    [int]$ScenarioLimit = 4,
    [int]$TraceLimit = 20,
    [int]$EvaluationLimit = 20,
    [int]$DocumentLimit = 20,
    [int]$ChunkLimit = 20,
    [int]$QueryLimit = 20,
    [int]$QrelLimit = 20,
    [int]$ReplayLimit = 20,
    [switch]$IncludeLargeText
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..")
$ApiDir = Join-Path $RepoRoot "services\api"
$Python = Join-Path $ApiDir ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    throw "Backend virtual environment not found at $Python"
}

$PreviousLocation = Get-Location
try {
    Set-Location $ApiDir
    $Args = @(
        "-m", "app.cli.export_demo_snapshot",
        "--output", $Output,
        "--scenario-limit", $ScenarioLimit,
        "--trace-limit", $TraceLimit,
        "--evaluation-limit", $EvaluationLimit,
        "--document-limit", $DocumentLimit,
        "--chunk-limit", $ChunkLimit,
        "--query-limit", $QueryLimit,
        "--qrel-limit", $QrelLimit,
        "--replay-limit", $ReplayLimit
    )

    if ($IncludeLargeText) {
        $Args += "--include-large-text"
    }

    & $Python @Args
} finally {
    Set-Location $PreviousLocation
}
