# 独占SDK入口的父进程看门狗；仅终止本次启动且精确身份仍相同的进程。
param(
    [Parameter(Mandatory=$true)][string]$RunDirectory,
    [Parameter(Mandatory=$true)][string]$ConfigPath,
    [Parameter(Mandatory=$true)][string]$ConfigSha256,
    [Parameter(Mandatory=$true)][string]$EntrySha256,
    [Parameter(Mandatory=$true)][string]$CloseScriptSha256
)
$ErrorActionPreference = 'Stop'
$taskRun = Get-Item -LiteralPath $RunDirectory
$taskConfig = Get-Item -LiteralPath $ConfigPath
$taskEntry = Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\vitis\run_s2b_visibility_probe.py'
$taskVitis = Get-Item -LiteralPath 'D:\Xilinx\2026.1\Vitis\bin\vitis.bat'
$taskPython = Get-Item -LiteralPath 'D:\Xilinx\2026.1\Vivado\tps\win64\python-3.13.0\python.exe'
$taskCmd = Get-Item -LiteralPath 'C:\WINDOWS\system32\cmd.exe'
$taskCloser = Get-Item -LiteralPath (Join-Path $taskRun.FullName 'close_owned_server.ps1')
if (-not $taskRun.PSIsContainer -or $taskConfig.PSIsContainer -or $taskEntry.PSIsContainer -or $taskVitis.PSIsContainer -or $taskPython.PSIsContainer -or $taskCmd.PSIsContainer -or $taskCloser.PSIsContainer) {throw '路径类型错误'}
foreach ($taskPair in @(@($taskConfig,$ConfigSha256),@($taskEntry,$EntrySha256),@($taskCloser,$CloseScriptSha256),@($taskPython,'d289b7527fe1a1e18a64da085ab50d319bcbba92ab1d58fa0ac073a1c240fc75'))) {
    if ((Get-FileHash -LiteralPath $taskPair[0].FullName -Algorithm SHA256).Hash.ToLowerInvariant() -cne $taskPair[1]) {throw '已绑定文件漂移'}
}
$taskConfigData = Get-Content -LiteralPath $taskConfig.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
$taskEvidence = Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\report\evidence\S2B-T19'
$taskEvidenceRun = [string]$taskConfigData.run_dir
$taskRunName = [IO.Path]::GetFileName($taskEvidenceRun)
if ($taskRunName -notmatch '^cache_probe_[0-9]{8}_r[0-9]{2}$' -or [IO.Path]::GetDirectoryName($taskEvidenceRun) -cne $taskEvidence.FullName) {throw '运行标识或精确父目录错误'}
$taskRecord = Join-Path $taskRun.FullName 'vitis_execution.json'
$taskIdentityPath = Join-Path $taskRun.FullName 'sdk_process_identity.json'
$taskStdout = Join-Path $taskRun.FullName 'vitis_stdout.log'
$taskStderr = Join-Path $taskRun.FullName 'vitis_stderr.log'
foreach ($taskPath in @($taskRecord,$taskIdentityPath,$taskStdout,$taskStderr,$taskEvidenceRun)) {if (Test-Path -LiteralPath $taskPath) {throw '拒绝覆盖运行或日志'}}
$taskEncoding = New-Object System.Text.UTF8Encoding($false)
$taskPreviousConfig = $env:S2B_VISIBILITY_PROBE_CONFIG
$taskPreviousEncoding = $env:PYTHONIOENCODING
$taskStarted = Get-Date
$taskLastProgress = $taskStarted
$taskProgress = @{}
$taskSdkIdentity = $null
$taskSdkProcess = $null
$taskTimeoutReason = $null
$taskClosureError = $null
$taskPrimaryError = $null
$taskLauncher = $null
$taskLauncherBirth = $null
$taskCleanup = @()
$taskFailureAtExit = $false
$taskMaxWorkingSet = 0L
$taskArgument = '/d /s /c ""' + $taskVitis.FullName + '" -s ' + $taskEntry.FullName + '"'
function Stop-TaskOwnedSdk {
    # 仅使用本轮实际捕获身份；失配或未捕获时保留阻断，绝不按名称扩大终止范围。
    if ($null -eq $script:taskSdkIdentity) {
        $script:taskCleanup += [pscustomobject]@{action='owned_sdk';status='BLOCKED';reason='未采集精确SDK身份，不自动终止未知子进程'}
        return
    }
    try {
        $taskCurrent = Get-CimInstance Win32_Process -Filter "ProcessId=$($script:taskSdkIdentity.pid)"
        if ($null -eq $taskCurrent) {
            $script:taskCleanup += [pscustomobject]@{action='owned_sdk';status='ALREADY_ABSENT';terminated_by_this_watchdog=$false}
            return
        }
        if ($taskCurrent.ParentProcessId -ne $script:taskSdkIdentity.parent_pid -or $taskCurrent.CreationDate.ToFileTimeUtc().ToString() -cne $script:taskSdkIdentity.birth -or $taskCurrent.ExecutablePath -cne $script:taskSdkIdentity.image -or $taskCurrent.CommandLine -cne $script:taskSdkIdentity.command_line -or (Get-FileHash -LiteralPath $taskCurrent.ExecutablePath -Algorithm SHA256).Hash.ToLowerInvariant() -cne $script:taskSdkIdentity.image_sha256) {throw '进程精确身份改变，拒绝终止'}
        Stop-Process -Id $script:taskSdkIdentity.pid
        if (-not $script:taskSdkProcess.WaitForExit(10000)) {throw '自有SDK终止后仍未退出'}
        if ($null -ne (Get-CimInstance Win32_Process -Filter "ProcessId=$($script:taskSdkIdentity.pid)")) {throw '终止后PID仍存在，不能声称已闭合'}
        $script:taskCleanup += [pscustomobject]@{action='owned_sdk';status='TERMINATED';terminated_by_this_watchdog=$true;native_exit_code=$script:taskSdkProcess.ExitCode}
    } catch {
        $script:taskCleanup += [pscustomobject]@{action='owned_sdk';status='BLOCKED';reason=$_.Exception.Message}
    }
}
try {
    $env:S2B_VISIBILITY_PROBE_CONFIG = $taskConfig.FullName
    $env:PYTHONIOENCODING = 'utf-8'
    $taskLauncher = Start-Process -FilePath $taskCmd.FullName -ArgumentList $taskArgument -WindowStyle Hidden -PassThru -RedirectStandardOutput $taskStdout -RedirectStandardError $taskStderr
    $null = $taskLauncher.Handle
    $taskLauncherBirth = $taskLauncher.StartTime.ToFileTimeUtc().ToString()
    while (-not $taskLauncher.HasExited) {
        if ($null -eq $taskSdkIdentity) {
            $taskChildren = @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$($taskLauncher.Id) AND Name='python.exe'")
            if ($taskChildren.Count -gt 1) {throw '独占SDK父进程出现多个Python子进程'}
            if ($taskChildren.Count -eq 1) {
                $taskChild = $taskChildren[0]
                if ($taskChild.ExecutablePath -cne $taskPython.FullName -or $taskChild.CommandLine -cne ('python.exe   ' + $taskEntry.FullName)) {throw 'SDK子进程身份不符合官方入口'}
                $taskSdkProcess = Get-Process -Id $taskChild.ProcessId
                $null = $taskSdkProcess.Handle
                $taskSdkIdentity = [pscustomobject]@{pid=$taskChild.ProcessId;parent_pid=$taskChild.ParentProcessId;birth=$taskChild.CreationDate.ToFileTimeUtc().ToString();image=$taskChild.ExecutablePath;command_line=$taskChild.CommandLine;launcher_pid=$taskLauncher.Id;launcher_birth=$taskLauncherBirth;image_sha256='d289b7527fe1a1e18a64da085ab50d319bcbba92ab1d58fa0ac073a1c240fc75';observed_at_utc8=(Get-Date -Format o)}
                [IO.File]::WriteAllText($taskIdentityPath,($taskSdkIdentity | ConvertTo-Json -Depth 5)+"`n",$taskEncoding)
            }
        }
        if ($null -ne $taskSdkProcess -and -not $taskSdkProcess.HasExited) {$taskSdkProcess.Refresh(); $taskMaxWorkingSet = [Math]::Max($taskMaxWorkingSet,$taskSdkProcess.WorkingSet64)}
        foreach ($taskLog in @($taskStdout,$taskStderr,(Join-Path $taskEvidenceRun 'entry_calls.jsonl'),(Join-Path $taskEvidenceRun 'jtag_calls.jsonl'),(Join-Path $taskEvidenceRun 'sdk_unload_stack.log'))) {
            if (Test-Path -LiteralPath $taskLog -PathType Leaf) {
                $taskInfo = Get-Item -LiteralPath $taskLog
                $taskStamp = $taskInfo.Length.ToString() + ':' + $taskInfo.LastWriteTimeUtc.ToFileTimeUtc().ToString()
                if ($taskProgress[$taskLog] -cne $taskStamp) {$taskProgress[$taskLog] = $taskStamp; $taskLastProgress = Get-Date}
            }
        }
        if (((Get-Date)-$taskStarted).TotalSeconds -ge 300) {$taskTimeoutReason='HARD_TIMEOUT_300_SECONDS'; break}
        if (((Get-Date)-$taskLastProgress).TotalSeconds -ge 180) {$taskTimeoutReason='NO_PROGRESS_180_SECONDS'; break}
        Start-Sleep -Milliseconds 1000
        $taskLauncher.Refresh()
    }
    if ($null -eq $taskTimeoutReason) {$taskLauncher.WaitForExit()}
} catch {
    $taskPrimaryError=$_.Exception.Message
} finally {
    # 非零退出、启动异常与超时均触发有限闭合；成功路径保留在线服务供后续判读。
    $taskLauncherExit = $null
    if ($null -ne $taskLauncher -and $taskLauncher.HasExited) {$taskLauncher.Refresh();$taskLauncherExit=$taskLauncher.ExitCode}
    $taskSdkExit = $null
    if ($null -ne $taskSdkProcess -and $taskSdkProcess.HasExited) {$taskSdkExit=$taskSdkProcess.ExitCode}
    $taskFailureAtExit = ($null -ne $taskTimeoutReason -or $null -ne $taskPrimaryError -or $null -eq $taskLauncherExit -or $taskLauncherExit -ne 0 -or ($null -ne $taskSdkExit -and $taskSdkExit -ne 0))
    if ($taskFailureAtExit) {
        try {
            if ((Get-FileHash -LiteralPath $taskCloser.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -cne $CloseScriptSha256) {throw '服务释放脚本漂移'}
            & $taskCloser.FullName | Out-Null
            $taskCleanup += [pscustomobject]@{action='owned_server';status='CLOSE_SCRIPT_RETURNED';evidence='server_close.json'}
        } catch {
            $taskClosureError=$_.Exception.Message
            $taskCleanup += [pscustomobject]@{action='owned_server';status='BLOCKED';reason=$taskClosureError}
        }
        Stop-TaskOwnedSdk
        if ($null -ne $taskLauncher) {
            try {
                if (-not $taskLauncher.WaitForExit(10000)) {throw '启动器未退出，不自动扩大终止范围'}
            } catch {$taskCleanup += [pscustomobject]@{action='owned_launcher';status='BLOCKED';reason=$_.Exception.Message}}
        }
    }
    $taskResult = [pscustomobject]@{command=@($taskCmd.FullName,$taskArgument);config_path=$taskConfig.FullName;config_sha256=$ConfigSha256;entry_sha256=$EntrySha256;started_at_utc8=$taskStarted.ToString('o');finished_at_utc8=(Get-Date -Format o);native_exit_code=$taskLauncherExit;sdk_native_exit_code=$taskSdkExit;timeout_reason=$taskTimeoutReason;primary_error=$taskPrimaryError;server_close_error=$taskClosureError;cleanup=$taskCleanup;no_progress_seconds=180;hard_timeout_seconds=300;sdk_sampled_peak_working_set_bytes=$taskMaxWorkingSet;sdk_identity=$taskSdkIdentity;result_semantics='启动器0不代表通过；超时或SDK异常终止明确失败，未写最终入口收据时按部分运行归档。'}
    try {
        [IO.File]::WriteAllText($taskRecord,($taskResult | ConvertTo-Json -Depth 6)+"`n",$taskEncoding)
        $taskResult | ConvertTo-Json -Depth 6
    } finally {
        $env:S2B_VISIBILITY_PROBE_CONFIG = $taskPreviousConfig
        $env:PYTHONIOENCODING = $taskPreviousEncoding
    }
}
if ($taskFailureAtExit) {exit 2}
