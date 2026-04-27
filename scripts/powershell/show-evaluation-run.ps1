param(
    [Parameter(Mandatory = $true)]
    [string]$EvaluationRunId,
    [switch]$Results,
    [switch]$Report,
    [switch]$IncludeJson
)

$ErrorActionPreference = "Stop"
$BaseUri = "http://localhost:8000/api/v1/evaluations/runs/$EvaluationRunId"

if ($Results) {
    Invoke-RestMethod "$BaseUri/results"
}
elseif ($Report) {
    $Include = if ($IncludeJson) { "true" } else { "false" }
    Invoke-RestMethod "$BaseUri/report?include_json=$Include"
}
else {
    Invoke-RestMethod $BaseUri
}
