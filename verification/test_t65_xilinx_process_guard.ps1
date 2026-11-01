[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$GuardModulePath,
    [Parameter(Mandatory = $true)][string]$AllowlistPath,
    [Parameter(Mandatory = $true)][string]$ExpectedGuardModuleSha256,
    [Parameter(Mandatory = $true)][string]$ExpectedAllowlistSha256
)

$ErrorActionPreference = 'Stop'

function Assert-T65ExpectedGuardFailure {
    param(
        [Parameter(Mandatory = $true)][string]$CaseName,
        [Parameter(Mandatory = $true)][scriptblock]$Action,
        [Parameter(Mandatory = $true)][string]$ExpectedError
    )
    try {
        & $Action | Out-Null
    }
    catch {
        if ($_.Exception.Message -notmatch $ExpectedError) {
            throw "测试 $CaseName 收到非预期错误：$($_.Exception.Message)"
        }
        return
    }
    throw "测试 $CaseName 未按预期拒绝错误身份。"
}

function Copy-T65IdentitySet {
    param([Parameter(Mandatory = $true)][object[]]$Source)
    return @($Source | ForEach-Object {
        [pscustomobject]@{
            pid = [int]$_.pid
            parent_pid = [int]$_.parent_pid
            name = [string]$_.name
            executable_path = [string]$_.executable_path
            command_line = [string]$_.command_line
            creation_date_utc = [string]$_.creation_date_utc
        }
    })
}

$moduleItem = Get-Item -LiteralPath $GuardModulePath -ErrorAction Stop
if ($moduleItem.PSIsContainer -or $moduleItem.FullName -cne $GuardModulePath) {
    throw "测试模块不是精确路径上的普通文件：$GuardModulePath"
}
$moduleSha256 = (Get-FileHash -LiteralPath $GuardModulePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($moduleSha256 -cne $ExpectedGuardModuleSha256.ToLowerInvariant()) {
    throw '测试模块 SHA-256 与绑定值不符。'
}
. $GuardModulePath
$allowlist = Read-T65XilinxProcessAllowlist -Path $AllowlistPath -ExpectedSha256 $ExpectedAllowlistSha256
$identities = @($allowlist.identities)

Assert-T65XilinxProcessIdentities -ActualProcesses $identities -AllowedIdentities $identities -Phase 'offline positive exact identities' | Out-Null

$timeMismatch = @(Copy-T65IdentitySet -Source $identities)
$timeMismatch[0].creation_date_utc = '2026-09-29T18:07:06.1577891Z'
Assert-T65ExpectedGuardFailure -CaseName 'creation time / PID reuse mismatch' -ExpectedError 'T65_PROCESS_IDENTITY_MISMATCH' -Action {
    Assert-T65XilinxProcessIdentities -ActualProcesses $timeMismatch -AllowedIdentities $identities -Phase 'negative creation time mismatch'
}

$commandMismatch = @(Copy-T65IdentitySet -Source $identities)
$commandMismatch[1].command_line = [string]$commandMismatch[1].command_line + ' altered'
Assert-T65ExpectedGuardFailure -CaseName 'command line mismatch' -ExpectedError 'T65_PROCESS_IDENTITY_MISMATCH' -Action {
    Assert-T65XilinxProcessIdentities -ActualProcesses $commandMismatch -AllowedIdentities $identities -Phase 'negative command line mismatch'
}

$newProcess = [pscustomobject]@{
    pid = 991234
    parent_pid = 8712
    name = 'xsimk.exe'
    executable_path = 'D:\FPGA_Competition\offline_validation\unexpected\xsimk.exe'
    command_line = 'unexpected xsim process'
    creation_date_utc = '2026-10-01T06:00:00.0000000Z'
}
$withNewProcess = @($identities) + @($newProcess)
Assert-T65ExpectedGuardFailure -CaseName 'new unlisted Xilinx process' -ExpectedError 'T65_ACTIVE_XILINX_PROCESS' -Action {
    Assert-T65XilinxProcessIdentities -ActualProcesses $withNewProcess -AllowedIdentities $identities -Phase 'negative new process'
}

$missingTime = @(Copy-T65IdentitySet -Source $identities)
$missingTime[2].creation_date_utc = ''
Assert-T65ExpectedGuardFailure -CaseName 'missing creation time' -ExpectedError 'T65_PROCESS_IDENTITY_INCOMPLETE' -Action {
    Assert-T65XilinxProcessIdentities -ActualProcesses $missingTime -AllowedIdentities $identities -Phase 'negative missing creation time'
}

$liveSnapshot = @(Get-T65XilinxProcessSnapshot)
Assert-T65XilinxProcessIdentities -ActualProcesses $liveSnapshot -AllowedIdentities $identities -Phase 'live read-only protected process snapshot' | Out-Null

[pscustomobject]@{
    status = 'PASS'
    powershell_version = $PSVersionTable.PSVersion.ToString()
    allowlist_sha256 = (Get-FileHash -LiteralPath $AllowlistPath -Algorithm SHA256).Hash.ToLowerInvariant()
    guard_module_sha256 = $moduleSha256
    positive_exact_identity = 'PASS'
    negative_creation_time_pid_reuse = 'PASS'
    negative_command_line_mismatch = 'PASS'
    negative_new_process = 'PASS'
    negative_missing_creation_time = 'PASS'
    live_read_only_snapshot = 'PASS'
    live_xilinx_process_count = $liveSnapshot.Count
    simulator_tool_invocations = 0
} | ConvertTo-Json -Compress
