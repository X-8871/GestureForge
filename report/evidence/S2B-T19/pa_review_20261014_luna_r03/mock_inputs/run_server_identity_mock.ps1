param(
    [Parameter(Mandatory=$true)][ValidateSet('start_unquoted','start_quoted','start_bad_arg','close_match','close_commandline_drift','close_parent_drift')][string]$Scenario
)
$ErrorActionPreference='Stop'
$script:Repo=(Get-Location).Path
$global:Repo=$script:Repo
$script:RunDirectory=Join-Path $script:Repo ('tmp/2B/S2B-T19/pa_review_20261014_luna_r03/server_cases/'+$Scenario+'_'+[guid]::NewGuid().ToString('N'))
$null=New-Item -ItemType Directory -Path $script:RunDirectory -Force
$script:ServerPath='D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe'
$script:ServerSha='e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3'
$script:CandidateStart=Join-Path $script:Repo 'tmp/2B/S2B-T19/board_run_20261014_r02/start_owned_server.ps1'
$script:CandidateClose=Join-Path $script:Repo 'tmp/2B/S2B-T19/board_run_20261014_r02/close_owned_server.ps1'
$global:MockState=[ordered]@{
    Scenario=$Scenario
    RunDirectory=$script:RunDirectory
    ServerPath=$script:ServerPath
    ServerSha=$script:ServerSha
    ServerPid=64001
    ParentPid=[int]$PID
    Birth=[datetime]::UtcNow.AddMinutes(-1)
    PortCalls=0
    Removed=$false
    StopCalls=0
    StartFilePath=$null
    StartArguments=$null
    StartWindowStyle=$null
    CommandLine=$null
    ExecutablePath=$script:ServerPath
    ParentDrift=$false
}
if ($Scenario -in @('start_unquoted','start_quoted','start_bad_arg')) {
    $global:MockState.CommandLine = switch ($Scenario) {
        'start_unquoted' { $script:ServerPath+' -s tcp::3121' }
        'start_quoted' { '"'+$script:ServerPath+'" -s tcp::3121' }
        'start_bad_arg' { $script:ServerPath+' -s tcp::9999' }
    }
    $script:Candidate=$script:CandidateStart
} else {
    $script:Candidate=$script:CandidateClose
    $commandLine=$script:ServerPath+' -s tcp::3121'
    $parentPid=[int]$PID
    if ($Scenario -eq 'close_commandline_drift') { $global:MockState.CommandLine=$commandLine+' --unexpected';$commandLine=$commandLine }
    else { $global:MockState.CommandLine=$commandLine }
    if ($Scenario -eq 'close_parent_drift') {$global:MockState.ParentDrift=$true}
    $native=[ordered]@{ProcessId=$global:MockState.ServerPid;ParentProcessId=$parentPid;ExecutablePath=$script:ServerPath;CommandLine=$commandLine;CreationTimeFileTimeUtc=[string]$global:MockState.Birth.ToFileTimeUtc()}
    $identity=[ordered]@{launcher_pid=[int]$PID;native=$native;native_sha256=$script:ServerSha}
    [IO.File]::WriteAllText((Join-Path $script:RunDirectory 'hw_server_identity.json'),($identity|ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
}
function Get-Item {
    param([string]$LiteralPath,[string]$Path)
    $p=if($null -ne $LiteralPath){$LiteralPath}else{$Path}
    if ($p -ieq 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\tmp\2B\S2B-T19\board_run_20261014_r02') {
        return Microsoft.PowerShell.Management\Get-Item -LiteralPath $global:MockState.RunDirectory
    }
    return Microsoft.PowerShell.Management\Get-Item @PSBoundParameters
}
function Get-Content {
    param([string]$LiteralPath,[string]$Path,[switch]$Raw,[string]$Encoding)
    return Microsoft.PowerShell.Management\Get-Content @PSBoundParameters
}
function Test-Path {
    param([string]$LiteralPath,[string]$Path,[string]$PathType,[switch]$IsValid)
    return $false
}
function Get-CimInstance {
    param([string]$ClassName,[string]$Filter)
    $global:MockState.LastFilter=$Filter
    if ($Filter -eq "Name='hw_server.exe'") { return @() }
    if ($Filter -match 'ParentProcessId=(\d+) AND Name=') { return @() }
    if ($Filter -match 'ProcessId=(\d+)') {
        $id=[int]$Matches[1]
        if ($id -eq [int]$PID) { return [pscustomobject]@{ProcessId=[int]$PID;ParentProcessId=0;CreationDate=$global:MockState.Birth;ExecutablePath='C:\WINDOWS\system32\WindowsPowerShell\v1.0\powershell.exe';CommandLine='mock launcher'} }
        if ($id -eq $global:MockState.ServerPid -and -not $global:MockState.Removed) {
            $parent=if($global:MockState.ParentDrift){$global:MockState.ParentPid+1}else{$global:MockState.ParentPid}
            $row=[pscustomobject]@{ProcessId=$global:MockState.ServerPid;ParentProcessId=$parent;CreationDate=$global:MockState.Birth;ExecutablePath=$global:MockState.ExecutablePath;CommandLine=$global:MockState.CommandLine}
            $global:MockState.LastReturnedProcess=$row
            return $row
        }
    }
    return @()
}
function Get-NetTCPConnection {
    [CmdletBinding()]
    param([int]$LocalPort,[string]$State)
    $global:MockState.PortCalls++
    $global:MockState.LastNetState=$State
    if ($global:MockState.Removed) { return @() }
    if ($global:MockState.Scenario -like 'start_*' -and $global:MockState.PortCalls -eq 1) { return @() }
    return @([pscustomobject]@{LocalAddress='127.0.0.1';LocalPort=3121;OwningProcess=$global:MockState.ServerPid})
}
function Start-Process {
    param([string]$FilePath,[object]$ArgumentList,[string]$WorkingDirectory,[string]$WindowStyle,[switch]$PassThru,[string]$RedirectStandardOutput,[string]$RedirectStandardError)
    $global:MockState.StartFilePath=$FilePath
    $global:MockState.StartArguments=@($ArgumentList)
    $global:MockState.StartWindowStyle=$WindowStyle
    return [pscustomobject]@{Id=$global:MockState.ServerPid}
}
function Start-Sleep { param([int]$Milliseconds) }
function Get-Process {
    param([int]$Id)
    $proc=[pscustomobject]@{Id=$Id;Handle='mock-server-handle';ExitCode=0}
    $proc | Add-Member -MemberType ScriptMethod -Name WaitForExit -Value {param([int]$Milliseconds)$global:MockState.Removed=$true;return $true}
    return $proc
}
function Stop-Process {
    param([int]$Id)
    $global:MockState.StopCalls++
    $global:MockState.Removed=$true
}
$caught=$null
try { & $script:Candidate } catch { $caught=$_.Exception.Message }
$postProcessCount=@(Get-CimInstance Win32_Process -Filter "ProcessId=$($global:MockState.ServerPid)").Count
$postListenerCount=@(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue).Count
if ($Scenario -like 'start_*') {
    $identityPath=Join-Path $script:RunDirectory 'hw_server_identity.json'
    $identityExists=Microsoft.PowerShell.Management\Test-Path -LiteralPath $identityPath -PathType Leaf
    $accepted=$Scenario -in @('start_unquoted','start_quoted')
    if ($accepted) {
        if ($null -ne $caught -or -not $identityExists) { throw "valid server command-line form rejected: $Scenario; $caught; pid=$PID; row=$($global:MockState.LastReturnedProcess|ConvertTo-Json -Compress) expected=$($global:MockState.CommandLine) start=$($global:MockState.StartFilePath)" }
        $saved=Microsoft.PowerShell.Management\Get-Content -LiteralPath $identityPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($saved.status -cne 'OWNED_SERVER_READY' -or $saved.native.CommandLine -cne $global:MockState.CommandLine -or $saved.native.ParentProcessId -ne $PID -or $saved.native_sha256 -cne $script:ServerSha) { throw 'starter did not preserve checked server command-line identity' }
        if ($global:MockState.StartWindowStyle -cne 'Hidden' -or $global:MockState.StartFilePath -cne $script:ServerPath -or ($global:MockState.StartArguments -join ' ') -cne '-s tcp::3121') { throw 'starter invocation properties changed' }
    } else {
        if ($null -eq $caught -or -not ($caught -like '*命令行不一致*') -or $identityExists) { throw 'starter accepted a near-match command line' }
    }
    [pscustomobject]@{scenario=$Scenario;result=if($accepted){'ACCEPTED_EXACT_VARIANT'}else{'REJECTED_NEAR_MATCH'};command_line=$global:MockState.CommandLine;receipt_written=$identityExists;window_style=$global:MockState.StartWindowStyle;error=$caught} | ConvertTo-Json -Depth 5
} else {
    $closeRecord=Join-Path $script:RunDirectory 'server_close.json'
    $recordExists=Microsoft.PowerShell.Management\Test-Path -LiteralPath $closeRecord -PathType Leaf
    $good=$Scenario -eq 'close_match'
    if ($good) {
        if ($null -ne $caught -or $global:MockState.StopCalls -ne 1 -or -not $recordExists) { throw "exact identity failed to close: $caught; removed=$($global:MockState.Removed); post_process_count=$postProcessCount; post_listener_count=$postListenerCount; port_calls=$($global:MockState.PortCalls); last_filter=$($global:MockState.LastFilter); last_net_state=$($global:MockState.LastNetState); stop_calls=$($global:MockState.StopCalls); record=$recordExists" }
        $saved=Microsoft.PowerShell.Management\Get-Content -LiteralPath $closeRecord -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($saved.status -cne 'OWNED_SERVER_CLOSED' -or $saved.identity_checked -ne $true -or $saved.native_absent -ne $true) { throw 'valid server close receipt not produced' }
    } else {
        if ($null -eq $caught -or $global:MockState.StopCalls -ne 0 -or $recordExists) { throw "drifted identity reached Stop-Process or wrote success receipt: $Scenario" }
    }
    [pscustomobject]@{scenario=$Scenario;result=if($good){'STOPPED_MATCHING_OWNED_PROCESS'}else{'REFUSED_DRIFT_BEFORE_STOP'};stop_calls=$global:MockState.StopCalls;server_close_receipt=$recordExists;error=$caught;command_line=$global:MockState.CommandLine} | ConvertTo-Json -Depth 5
}
