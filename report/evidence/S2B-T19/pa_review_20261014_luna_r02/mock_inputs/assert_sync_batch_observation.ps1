param([Parameter(Mandatory=$true)][string]$ResultPath)
$ErrorActionPreference = 'Stop'
$result = Get-Content -LiteralPath $ResultPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $result.mock_child_seen -or -not $result.mock_child_live_when_seen -or -not $result.launcher_live_while_child_observed) {
    throw 'mock did not establish synchronous child execution'
}
if ($result.expected_exit_code -ne 23 -or $result.launcher_exit_code -ne 0) {
    throw 'mock did not reproduce child nonzero exit masking by cmd/batch'
}
[pscustomobject]@{
    observation='SYNCHRONOUS_CHILD_AND_EXIT_MASKING_CONFIRMED'
    child_exit_code=$result.expected_exit_code
    launcher_exit_code=$result.launcher_exit_code
    child_live_when_seen=$result.mock_child_live_when_seen
    launcher_live_while_child_observed=$result.launcher_live_while_child_observed
    official_vitis_bat_sha256=$result.official_vitis_bat_sha256
    official_source_line=$result.official_source_line
    official_source_text=$result.official_source_text
} | ConvertTo-Json -Depth 4
