# 只释放本任务启动且PID、创建时间、父PID、映像SHA均匹配的硬件服务。
$ErrorActionPreference = 'Stop'
$taskRun = Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\tmp\2B\S2B-T19\board_run_20261013_r01'
if (-not $taskRun.PSIsContainer) { throw '运行目标不是目录' }
$taskIdentityFile = Get-Item -LiteralPath (Join-Path $taskRun.FullName 'hw_server_identity.json')
$taskIdentity = Get-Content -LiteralPath $taskIdentityFile.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
$taskDestination = Join-Path $taskRun.FullName 'server_close.json'
if (Test-Path -LiteralPath $taskDestination) { throw '拒绝覆盖释放记录' }
$taskCurrent = Get-CimInstance Win32_Process -Filter "ProcessId=$($taskIdentity.native.ProcessId)"
if ($null -eq $taskCurrent) { throw '待释放服务已不存在，不能伪造本次停止成功' }
if ($taskCurrent.ExecutablePath -cne $taskIdentity.native.ExecutablePath -or
    $taskCurrent.ParentProcessId -ne $taskIdentity.native.ParentProcessId -or
    [string]$taskCurrent.CreationDate.ToFileTimeUtc() -cne $taskIdentity.native.CreationTimeFileTimeUtc) {
    throw '待释放服务身份与本任务不一致'
}
$taskFile = Get-Item -LiteralPath $taskCurrent.ExecutablePath
$taskSha = (Get-FileHash -LiteralPath $taskFile.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
if ($taskSha -cne $taskIdentity.native_sha256) { throw '待释放服务映像SHA不同' }
$taskBound = @(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue)
if ($taskBound.Count -eq 0 -or @($taskBound | Where-Object { $_.OwningProcess -ne $taskCurrent.ProcessId }).Count -gt 0) {
    throw '待释放服务未独占3121'
}
$taskProcess = Get-Process -Id $taskCurrent.ProcessId
$null = $taskProcess.Handle
Stop-Process -Id $taskCurrent.ProcessId
if (-not $taskProcess.WaitForExit(10000)) { throw '自有服务释放超时' }
$taskLeft = @(Get-CimInstance Win32_Process -Filter "ProcessId=$($taskCurrent.ProcessId)")
$taskListeners = @(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue)
if ($taskLeft.Count -ne 0 -or $taskListeners.Count -ne 0) { throw '自有服务或3121未闭合' }
$taskLauncher = Get-CimInstance Win32_Process -Filter "ProcessId=$($taskIdentity.launcher_pid)"
$taskResult = [pscustomobject]@{
    status='OWNED_SERVER_CLOSED';checked_at_utc8=(Get-Date -Format o);identity_checked=$true
    native_pid=$taskCurrent.ProcessId;native_exit_code=$taskProcess.ExitCode
    native_absent=$true;listeners=@();launcher_current=($taskLauncher | Select-Object ProcessId,ParentProcessId,ExecutablePath,CreationDate)
    hardware_program_execution='SEE_VISIBILITY_PROBE_RESULT';target_operations='本次易失部署与缓存观测，SDK及UART闭合见独立入口运行结果'
}
$taskJson = $taskResult | ConvertTo-Json -Depth 5
[IO.File]::WriteAllText($taskDestination, $taskJson + "`n", (New-Object Text.UTF8Encoding($false)))
$taskJson
