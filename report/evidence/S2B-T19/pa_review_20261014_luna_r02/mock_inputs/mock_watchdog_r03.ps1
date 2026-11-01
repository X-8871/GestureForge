param([Parameter(Mandatory=$true)][ValidateSet('launcher_nonzero','sdk_nonzero','all_zero','launcher_zero_sdk_live','sdk_fast_nonzero_unobserved')][string]$Scenario)
$ErrorActionPreference = 'Stop'
$script:Repo = (Get-Location).Path
$global:Repo = $script:Repo
$script:MockState = [ordered]@{
    Scenario = $Scenario
    LauncherId = 42420
    SdkId = 42421
    LauncherExited = $false
    SdkExited = $false
    SdkRemoved = $false
    LauncherExit = 0
    SdkExit = 0
    StartWindowStyle = $null
    StopSdkCalls = 0
    SdkCreation = [datetime]::UtcNow.AddMinutes(-3)
}
$global:MockState = $script:MockState
switch ($Scenario) {
    'launcher_nonzero' { $script:MockState.LauncherExit = 2; $script:MockState.SdkExit = 0 }
    'sdk_nonzero' { $script:MockState.LauncherExit = 0; $script:MockState.SdkExit = 9 }
    'all_zero' { $script:MockState.LauncherExit = 0; $script:MockState.SdkExit = 0 }
    'launcher_zero_sdk_live' { $script:MockState.LauncherExit = 0; $script:MockState.SdkExit = 0 }
    'sdk_fast_nonzero_unobserved' { $script:MockState.LauncherExit = 0; $script:MockState.SdkExit = 23; $script:MockState.SdkExited = $true }
}
$script:TestRoot = Join-Path $script:Repo 'tmp/2B/S2B-T19/pa_review_20261014_luna_r02/watchdog_mocks'
$script:RunDirectory = Join-Path $script:TestRoot ($Scenario + '_' + [guid]::NewGuid().ToString('N'))
$global:RunDirectory = $script:RunDirectory
$null = New-Item -ItemType Directory -Path $script:RunDirectory -Force
$script:ConfigPath = Join-Path $script:RunDirectory 'config.json'
$script:ConfigRunDir = Join-Path $script:Repo 'report/evidence/S2B-T19/cache_probe_20261014_r99'
[IO.File]::WriteAllText($script:ConfigPath,(@{run_dir=$script:ConfigRunDir} | ConvertTo-Json -Compress),[Text.UTF8Encoding]::new($false))
$script:CloserPath = Join-Path $script:RunDirectory 'close_owned_server.ps1'
$script:MarkerPath = Join-Path $script:RunDirectory 'closer_called.txt'
$script:StopMarkerPath = Join-Path $script:RunDirectory 'stop_sdk_called.txt'
$global:StopMarkerPath = $script:StopMarkerPath
[IO.File]::WriteAllText($script:CloserPath,"[IO.File]::WriteAllText('$($script:MarkerPath.Replace("'","''"))','closed',[Text.UTF8Encoding]::new(`$false))`n",[Text.UTF8Encoding]::new($false))
$env:S2B_TEST_SERVER_CLOSE_MARKER = $script:MarkerPath
$script:RealCmdGetItem = (Get-Command Get-Item -CommandType Cmdlet).Source

function Start-Process {
    param([string]$FilePath,[string]$ArgumentList,[string]$WorkingDirectory,[string]$WindowStyle,[switch]$PassThru,[string]$RedirectStandardOutput,[string]$RedirectStandardError)
    $global:MockState['StartWindowStyle'] = $WindowStyle
    if ($global:MockState.Scenario -eq 'sdk_fast_nonzero_unobserved') {$global:MockState.LauncherExited=$true}
    $launcher = [pscustomobject]@{Id=$global:MockState.LauncherId;StartTime=[datetime]::UtcNow;Handle='mock-handle'}
    $launcher | Add-Member -MemberType ScriptProperty -Name HasExited -Value { [bool]$global:MockState.LauncherExited }
    $launcher | Add-Member -MemberType ScriptProperty -Name ExitCode -Value { [int]$global:MockState.LauncherExit }
    $launcher | Add-Member -MemberType ScriptMethod -Name Refresh -Value {}
    $launcher | Add-Member -MemberType ScriptMethod -Name WaitForExit -Value { param([int]$Milliseconds) $global:MockState.LauncherExited=$true; return $true }
    return $launcher
}
function Get-CimInstance {
    param([string]$ClassName,[string]$Filter)
    if ($Filter -match "ParentProcessId=$($global:MockState.LauncherId) AND Name='python.exe'") {
        return @([pscustomobject]@{ProcessId=$global:MockState.SdkId;ParentProcessId=$global:MockState.LauncherId;CreationDate=$global:MockState.SdkCreation;ExecutablePath='D:\Xilinx\2026.1\Vivado\tps\win64\python-3.13.0\python.exe';CommandLine='python.exe   ' + (Join-Path $global:Repo 'vitis/run_s2b_visibility_probe.py')})
    }
    if ($Filter -match 'ProcessId=(\d+)') {
        if ([int]$Matches[1] -eq $global:MockState.SdkId -and -not $global:MockState.SdkRemoved -and -not $global:MockState.SdkExited) {
            return [pscustomobject]@{ProcessId=$global:MockState.SdkId;ParentProcessId=$global:MockState.LauncherId;CreationDate=$global:MockState.SdkCreation;ExecutablePath='D:\Xilinx\2026.1\Vivado\tps\win64\python-3.13.0\python.exe';CommandLine='python.exe   ' + (Join-Path $global:Repo 'vitis/run_s2b_visibility_probe.py')}
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
    $process | Add-Member -MemberType ScriptMethod -Name WaitForExit -Value { param([int]$Milliseconds) $global:MockState.SdkExited=$true; return $true }
    return $process
}
function Stop-Process {
    param([int]$Id)
    $global:MockState.StopSdkCalls++
    $global:MockState.SdkExited=$true
    $global:MockState.SdkRemoved=$true
    [IO.File]::WriteAllText($global:StopMarkerPath,[string]$Id,[Text.UTF8Encoding]::new($false))
}
function Start-Sleep {
    param([int]$Milliseconds)
    $global:MockState.LauncherExited=$true
    if ($global:MockState.Scenario -in @('sdk_nonzero','all_zero')) {$global:MockState.SdkExited=$true}
}
function Test-Path {
    param([string]$LiteralPath,[string]$Path,[string]$PathType)
    return $false
}
$scriptPath = Join-Path $script:Repo 'tmp/2B/S2B-T19/watchdog_prepare_20261013_r01/run_visibility_guarded_r03.ps1'
$configSha = (Get-FileHash -LiteralPath $script:ConfigPath -Algorithm SHA256).Hash.ToLowerInvariant()
$entryPath = Join-Path $script:Repo 'vitis/run_s2b_visibility_probe.py'
$entrySha = (Get-FileHash -LiteralPath $entryPath -Algorithm SHA256).Hash.ToLowerInvariant()
$closerSha = (Get-FileHash -LiteralPath $script:CloserPath -Algorithm SHA256).Hash.ToLowerInvariant()
& $scriptPath -RunDirectory $script:RunDirectory -ConfigPath $script:ConfigPath -ConfigSha256 $configSha -EntrySha256 $entrySha -CloseScriptSha256 $closerSha
$record = Get-Content -LiteralPath (Join-Path $script:RunDirectory 'vitis_execution.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$expectedWatchdogExit = if ($null -ne $record.timeout_reason -or $null -ne $record.primary_error -or $null -eq $record.native_exit_code -or $record.native_exit_code -ne 0 -or ($null -ne $record.sdk_native_exit_code -and $record.sdk_native_exit_code -ne 0)) { 2 } else { 0 }
Write-Output ('mock_watchdog_exit=' + $expectedWatchdogExit)
exit $expectedWatchdogExit
