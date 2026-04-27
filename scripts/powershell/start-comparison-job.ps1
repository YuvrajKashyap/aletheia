param(
    [switch]$UseDefaults,
    [string[]]$ConfigName,
    [string[]]$ConfigId,
    [int]$QueryLimit,
    [int]$QueryOffset = 0,
    [string]$Name,
    [string]$DatasetName = "beir/scifact",
    [string]$DatasetVersion = "test",
    [string]$IndexVersionId,
    [string]$Notes,
    [string]$AdminApiKey = "replace-me"
)

$ErrorActionPreference = "Stop"
$Body = @{
    use_defaults = [bool]$UseDefaults
    dataset_name = $DatasetName
    dataset_version = $DatasetVersion
    query_offset = $QueryOffset
}
if ($ConfigName -and $ConfigName.Count -gt 0) {
    $Body["experiment_config_names"] = @($ConfigName)
}
if ($ConfigId -and $ConfigId.Count -gt 0) {
    $Body["experiment_config_ids"] = @($ConfigId)
}
if ($PSBoundParameters.ContainsKey("QueryLimit")) {
    $Body["query_limit"] = $QueryLimit
}
foreach ($Item in @(
    @("name", $Name),
    @("index_version_id", $IndexVersionId),
    @("notes", $Notes)
)) {
    if (-not [string]::IsNullOrWhiteSpace($Item[1])) {
        $Body[$Item[0]] = $Item[1]
    }
}

$Json = $Body | ConvertTo-Json
Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8000/api/v1/experiments/comparisons" `
    -ContentType "application/json" `
    -Headers @{"X-Admin-API-Key" = $AdminApiKey} `
    -Body $Json
