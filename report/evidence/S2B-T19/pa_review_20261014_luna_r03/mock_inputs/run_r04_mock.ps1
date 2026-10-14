param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('fast_missing','sdk_live_missing_exit','sdk_nonzero_valid','launcher_nonzero_valid','malformed','schema_missing','schema_wrong','status_failed','status_wrong','native_missing','native_nonzero','source_missing','source_mismatch','config_missing','config_mismatch','hardware_missing','hardware_wrong','cold_true','cleanup_missing','cleanup_nonempty','serial_open','final_csr_missing','cache_probe_missing','uart_empty','all_zero_valid')]
    [string]$Scenario
)
$ErrorActionPreference = 'Stop'
$script:Repo = (Get-Location).Path
$global:Repo = $script:Repo
$script:EntryPath = Join-Path $script:Repo 'vitis/run_s2b_visibility_probe.py'
$script:EntrySha = 'e2cf60f08a0de90b40eb38599c2b3ed5eb809c7d35b6b16a8de6efd4fe94ec1a'
$script:MockState = [ordered]@{
    Scenario = $Scenario
    LauncherId = 52420
    SdkId = 52421
    LauncherExited = $false
    SdkExited = $false
    SdkRemoved = $false
    LauncherExit = 0
    SdkExit = 0
    CaptureSdk = $true
    SdkExitOnSleep = $true
    StopSdkCalls = 0
    StartWindowStyle = $null
    PriorConfig = 'prior-config-sentinel'
    PriorEncoding = 'prior-encoding-sentinel'
}
$global:MockState = $script:MockState
switch ($Scenario) {
    'fast_missing' { $script:MockState.LauncherExited = $true; $script:MockState.CaptureSdk = $false }
    'sdk_live_missing_exit' { $script:MockState.SdkExitOnSleep = $false }
    'sdk_nonzero_valid' { $script:MockState.SdkExit = 9 }
    'launcher_nonzero_valid' { $script:MockState.LauncherExit = 2; $script:MockState.SdkExitOnSleep = $false }
}
$script:MockRoot = Join-Path $script:Repo 'tmp/2B/S2B-T19/pa_review_20261014_luna_r03/cases'
$script:RunDirectory = Join-Path $script:MockRoot ($Scenario + '_' + [guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $script:RunDirectory -Force
$script:ConfigPath = Join-Path $script:RunDirectory 'config.json'
$script:EntryRun = Join-Path $script:Repo 'report/evidence/S2B-T19/cache_probe_20261014_r90'
[IO.File]::WriteAllText($script:ConfigPath,(@{run_dir=$script:EntryRun} | ConvertTo-Json -Compress),[Text.UTF8Encoding]::new($false))
$script:ConfigSha = (Get-FileHash -LiteralPath $script:ConfigPath -Algorithm SHA256).Hash.ToLowerInvariant()
$script:CloserPath = Join-Path $script:RunDirectory 'close_owned_server.ps1'
$script:CloseMarker = Join-Path $script:RunDirectory 'server_close_mock.marker'
$script:StopMarker = Join-Path $script:RunDirectory 'sdk_stop_mock.marker'
$global:MockState['StopMarker'] = $script:StopMarker
[IO.File]::WriteAllText($script:CloserPath,"[IO.File]::WriteAllText('$($script:CloseMarker.Replace("'","''"))','closed',[Text.UTF8Encoding]::new(`$false))`n",[Text.UTF8Encoding]::new($false))
$script:CloserSha = (Get-FileHash -LiteralPath $script:CloserPath -Algorithm SHA256).Hash.ToLowerInvariant()
$script:ReceiptPath = Join-Path $script:EntryRun 'visibility_probe_result.json'
$script:Birth = [datetime]::UtcNow.AddMinutes(-2)
$script:ValidReceipt = [ordered]@{
    schema_version=1
    status='API_OBSERVATIONS_SAVED_ACCEPTANCE_PENDING'
    native_exit_code=0
    source_sha256=$script:EntrySha
    config_sha256=$script:ConfigSha
    hardware_execution='REQUESTED_BY_ROOT_CALL'
    cold_lifecycle_proven=$false
    cleanup_errors=@()
    serial_closed=$true
    final_csr=@{status='PASS';state='COLD_IDLE'}
    cache_probe=@{status='PASS'}
    uart_events=@(@{epoch=0;last_sequence=2;abort_pending=$null;failed=$false})
}
$script:ReceiptPresent = $Scenario -notin @('fast_missing','sdk_live_missing_exit')
$script:ReceiptContent = $null
if ($script:ReceiptPresent) {
    switch ($Scenario) {
        'malformed' { $script:ReceiptContent = '{ malformed json' }
        'schema_missing' { $script:ValidReceipt.Remove('schema_version') }
        'schema_wrong' { $script:ValidReceipt.schema_version = 2 }
        'status_failed' { $script:ValidReceipt.status = 'FAILED' }
        'status_wrong' { $script:ValidReceipt.status = 'API_OBSERVATIONS_SAVED' }
        'native_missing' { $script:ValidReceipt.Remove('native_exit_code') }
        'native_nonzero' { $script:ValidReceipt.native_exit_code = 2 }
        'source_missing' { $script:ValidReceipt.Remove('source_sha256') }
        'source_mismatch' { $script:ValidReceipt.source_sha256 = ('0' * 64) }
        'config_missing' { $script:ValidReceipt.Remove('config_sha256') }
        'config_mismatch' { $script:ValidReceipt.config_sha256 = ('0' * 64) }
        'hardware_missing' { $script:ValidReceipt.Remove('hardware_execution') }
        'hardware_wrong' { $script:ValidReceipt.hardware_execution = 'NOT_RUN' }
        'cold_true' { $script:ValidReceipt.cold_lifecycle_proven = $true }
        'cleanup_missing' { $script:ValidReceipt.Remove('cleanup_errors') }
        'cleanup_nonempty' { $script:ValidReceipt.cleanup_errors = @(@{action='mock';error='failure'}) }
        'serial_open' { $script:ValidReceipt.serial_closed = $false }
        'final_csr_missing' { $script:ValidReceipt.Remove('final_csr') }
        'cache_probe_missing' { $script:ValidReceipt.Remove('cache_probe') }
        'uart_empty' { $script:ValidReceipt.uart_events = @() }
    }
    if ($null -eq $script:ReceiptContent) { $script:ReceiptContent = $script:ValidReceipt | ConvertTo-Json -Depth 8 -Compress }
}
$global:MockState['ReceiptPath'] = $script:ReceiptPath
$global:MockState['ReceiptPresent'] = $script:ReceiptPresent
$global:MockState['ReceiptContent'] = $script:ReceiptContent
$global:MockState['Birth'] = $script:Birth
$env:S2B_VISIBILITY_PROBE_CONFIG = $global:MockState.PriorConfig
$env:PYTHONIOENCODING = $global:MockState.PriorEncoding

function Start-Process {
    param([string]$FilePath,[string]$ArgumentList,[string]$WorkingDirectory,[string]$WindowStyle,[switch]$PassThru,[string]$RedirectStandardOutput,[string]$RedirectStandardError)
    $global:MockState.StartWindowStyle = $WindowStyle
    $launcher = [pscustomobject]@{Id=$global:MockState.LauncherId;StartTime=[datetime]::UtcNow;Handle='mock-launcher-handle'}
    $launcher | Add-Member -MemberType ScriptProperty -Name HasExited -Value { [bool]$global:MockState.LauncherExited }
    $launcher | Add-Member -MemberType ScriptProperty -Name ExitCode -Value { [int]$global:MockState.LauncherExit }
    $launcher | Add-Member -MemberType ScriptMethod -Name Refresh -Value {}
    $launcher | Add-Member -MemberType ScriptMethod -Name WaitForExit -Value { param([int]$Milliseconds) $global:MockState.LauncherExited=$true; return $true }
    return $launcher
}
function Get-CimInstance {
    param([string]$ClassName,[string]$Filter)
    if ($Filter -match "ParentProcessId=$($global:MockState.LauncherId) AND Name='python.exe'") {
        if (-not $global:MockState.CaptureSdk) { return @() }
        return @([pscustomobject]@{ProcessId=$global:MockState.SdkId;ParentProcessId=$global:MockState.LauncherId;CreationDate=$global:MockState.Birth;ExecutablePath='D:\Xilinx\2026.1\Vivado\tps\win64\python-3.13.0\python.exe';CommandLine='python.exe   ' + $global:Repo + '\vitis\run_s2b_visibility_probe.py'})
    }
    if ($Filter -match 'ProcessId=(\d+)') {
        $id = [int]$Matches[1]
        if ($id -eq $global:MockState.SdkId -and -not $global:MockState.SdkRemoved -and -not $global:MockState.SdkExited) {
            return [pscustomobject]@{ProcessId=$global:MockState.SdkId;ParentProcessId=$global:MockState.LauncherId;CreationDate=$global:MockState.Birth;ExecutablePath='D:\Xilinx\2026.1\Vivado\tps\win64\python-3.13.0\python.exe';CommandLine='python.exe   ' + $global:Repo + '\vitis\run_s2b_visibility_probe.py'}
        }
    }
    return $null
}
function Get-Process {
    param([int]$Id)
    $process = [pscustomobject]@{Id=$Id;Handle='mock-sdk-handle';WorkingSet64=123456L}
    $process | Add-Member -MemberType ScriptProperty -Name HasExited -Value { [bool]$global:MockState.SdkExited }
    $process | Add-Member -MemberType ScriptProperty -Name ExitCode -Value { [int]$global:MockState.SdkExit }
    $process | Add-Member -MemberType ScriptMethod -Name Refresh -Value {}
    $process | Add-Member -MemberType ScriptMethod -Name WaitForExit -Value { param([int]$Milliseconds) $global:MockState.SdkExited=$true;$global:MockState.SdkRemoved=$true;return $true }
    return $process
}
function Stop-Process {
    param([int]$Id)
    $global:MockState.StopSdkCalls++
    $global:MockState.SdkExited=$true
    $global:MockState.SdkRemoved=$true
    [IO.File]::WriteAllText($global:MockState.StopMarker,[string]$Id,[Text.UTF8Encoding]::new($false))
}
function Start-Sleep {
    param([int]$Milliseconds)
    $global:MockState.LauncherExited=$true
    if ($global:MockState.SdkExitOnSleep) { $global:MockState.SdkExited=$true }
}
function Test-Path {
    param([string]$LiteralPath,[string]$Path,[string]$PathType,[switch]$IsValid)
    $candidate = if ($null -ne $LiteralPath) {$LiteralPath} else {$Path}
    if ($candidate -ieq $global:MockState.ReceiptPath) { return [bool]$global:MockState.ReceiptPresent }
    return $false
}
function Get-Content {
    param([string]$LiteralPath,[string]$Path,[switch]$Raw,[string]$Encoding,[int]$Depth)
    $candidate = if ($null -ne $LiteralPath) {$LiteralPath} else {$Path}
    if ($candidate -ieq $global:MockState.ReceiptPath) { return [string]$global:MockState.ReceiptContent }
    return Microsoft.PowerShell.Management\Get-Content @PSBoundParameters
}

$scriptPath = Join-Path $script:Repo 'tmp/2B/S2B-T19/watchdog_prepare_20261013_r01/run_visibility_guarded_r04.ps1'
$closeSha = (Get-FileHash -LiteralPath $scriptPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($closeSha -ne '0aa0e95a7014db2357aa5fd2b0bcf4db2a4dc1fe126ae79d2e097441eecff3b4') { throw 'r04 candidate changed during test' }
$candidateError = $null
try {
    & $scriptPath -RunDirectory $script:RunDirectory -ConfigPath $script:ConfigPath -ConfigSha256 $script:ConfigSha -EntrySha256 $script:EntrySha -CloseScriptSha256 $script:CloserSha
} catch { $candidateError = $_.Exception.Message }
$record = Get-Content -LiteralPath (Join-Path $script:RunDirectory 'vitis_execution.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$failureExpected = $Scenario -notin @('all_zero_valid')
$serverMarkerExists = Microsoft.PowerShell.Management\Test-Path -LiteralPath $script:CloseMarker -PathType Leaf
$sdkMarkerExists = Microsoft.PowerShell.Management\Test-Path -LiteralPath $script:StopMarker -PathType Leaf
$expectedReceiptError = $Scenario -notin @('all_zero_valid','sdk_nonzero_valid','launcher_nonzero_valid')
$assertions = [ordered]@{
    scenario=$Scenario
    observed=''
    entry_receipt_error=$record.entry_receipt_error
    entry_result_status=$record.entry_result_status
    entry_native_exit_code=$record.entry_native_exit_code
    launcher_exit_code=$record.native_exit_code
    sdk_native_exit_code=$record.sdk_native_exit_code
    sdk_exit_code_missing=$record.sdk_exit_code_missing
    sdk_identity_captured=($null -ne $record.sdk_identity)
    cleanup=$record.cleanup
    server_cleanup_invoked=$serverMarkerExists
    sdk_stop_invoked=$sdkMarkerExists
    environment_restored=($env:S2B_VISIBILITY_PROBE_CONFIG -ceq $global:MockState.PriorConfig -and $env:PYTHONIOENCODING -ceq $global:MockState.PriorEncoding)
    candidate_error=$candidateError
}
if ($failureExpected) {
    if (-not $serverMarkerExists -or $record.cleanup.Count -eq 0) { throw "failure case $Scenario did not invoke bounded server cleanup" }
} else {
    if ($serverMarkerExists -or $record.cleanup.Count -ne 0 -or $null -ne $record.entry_receipt_error) { throw 'valid all-zero case incorrectly ran failure cleanup or rejected the entry receipt' }
}
if ($expectedReceiptError -and $null -eq $record.entry_receipt_error) { throw "receipt rejection not recorded for $Scenario" }
if (-not $expectedReceiptError -and $Scenario -in @('all_zero_valid','sdk_nonzero_valid','launcher_nonzero_valid') -and $null -ne $record.entry_receipt_error) { throw "valid receipt rejected in $Scenario" }
if ($Scenario -eq 'sdk_live_missing_exit' -and (-not $record.sdk_exit_code_missing -or -not $sdkMarkerExists -or $record.sdk_native_exit_code -ne $null)) { throw 'sampled SDK missing-exit case did not record and stop exact SDK' }
if ($Scenario -eq 'fast_missing' -and ($record.sdk_identity -ne $null -or $record.sdk_native_exit_code -ne $null -or $record.entry_receipt_error -ne '入口最终结果收据缺失')) { throw 'fast unsampled missing-receipt case did not fail closed' }
if ($Scenario -eq 'sdk_nonzero_valid' -and ($record.sdk_native_exit_code -ne 9 -or -not $serverMarkerExists)) { throw 'SDK nonzero did not cause failure cleanup despite valid inner receipt' }
if ($Scenario -eq 'launcher_nonzero_valid' -and ($record.native_exit_code -ne 2 -or -not $sdkMarkerExists)) { throw 'launcher nonzero did not cause bounded failure cleanup' }
if (-not $assertions.environment_restored) { throw 'environment variables were not restored' }
$assertions.observed = if ($failureExpected) {'FAILURE_CLOSED_AS_EXPECTED'} else {'VALID_SUCCESS_NO_FAILURE_CLEANUP'}
$assertions | ConvertTo-Json -Depth 8
