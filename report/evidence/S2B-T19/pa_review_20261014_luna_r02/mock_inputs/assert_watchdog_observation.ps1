param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('launcher_nonzero','sdk_nonzero','all_zero','sdk_fast_nonzero_unobserved')]
    [string]$Scenario,
    [Parameter(Mandatory=$true)]
    [string]$OutputPath
)
$ErrorActionPreference = 'Stop'
$raw = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $OutputPath).Path,[Text.Encoding]::UTF8)
$start = $raw.IndexOf('{')
$end = $raw.LastIndexOf('}')
if ($start -lt 0 -or $end -lt $start) { throw 'mock output lacks JSON watchdog receipt' }
$receipt = $raw.Substring($start,$end-$start+1) | ConvertFrom-Json
$exitMatch = [regex]::Match($raw,'mock_watchdog_exit=(\d+)')
if (-not $exitMatch.Success) { throw 'mock output lacks watchdog process exit' }
$watchdogExit = [int]$exitMatch.Groups[1].Value
$cleanup = @($receipt.cleanup)
switch ($Scenario) {
    'launcher_nonzero' {
        if ($receipt.native_exit_code -ne 2 -or $watchdogExit -ne 2) { throw 'launcher nonzero did not fail the watchdog' }
        if (-not ($cleanup | Where-Object {$_.action -eq 'owned_server' -and $_.status -eq 'CLOSE_SCRIPT_RETURNED'})) { throw 'owned server cleanup was not attempted' }
        if (-not ($cleanup | Where-Object {$_.action -eq 'owned_sdk' -and $_.status -eq 'TERMINATED'})) { throw 'owned SDK termination was not recorded' }
    }
    'sdk_nonzero' {
        if ($receipt.native_exit_code -ne 0 -or $receipt.sdk_native_exit_code -ne 9 -or $watchdogExit -ne 2) { throw 'sampled SDK nonzero did not fail the watchdog' }
        if (-not ($cleanup | Where-Object {$_.action -eq 'owned_server' -and $_.status -eq 'CLOSE_SCRIPT_RETURNED'})) { throw 'owned server cleanup was not attempted' }
        if (-not ($cleanup | Where-Object {$_.action -eq 'owned_sdk' -and $_.status -eq 'ALREADY_ABSENT'})) { throw 'SDK exit state was not recorded' }
    }
    'all_zero' {
        if ($receipt.native_exit_code -ne 0 -or $receipt.sdk_native_exit_code -ne 0 -or $watchdogExit -ne 0 -or $cleanup.Count -ne 0) { throw 'all-zero path did not remain successful without failure cleanup' }
    }
    'sdk_fast_nonzero_unobserved' {
        if ($receipt.native_exit_code -ne 0 -or $receipt.sdk_native_exit_code -ne $null -or $null -ne $receipt.sdk_identity -or $watchdogExit -ne 0 -or $cleanup.Count -ne 0) { throw 'fast nonzero counterexample did not reproduce the success gap' }
    }
}
[pscustomobject]@{
    scenario=$Scenario
    observation='ASSERTIONS_MATCHED'
    launcher_exit_code=$receipt.native_exit_code
    sdk_native_exit_code=$receipt.sdk_native_exit_code
    sdk_identity_captured=($null -ne $receipt.sdk_identity)
    cleanup=$cleanup
    watchdog_process_exit_code=$watchdogExit
} | ConvertTo-Json -Depth 6
