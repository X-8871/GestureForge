# 仅为本任务启动独占hw_server；通过Process对象、启动参数及端口PID绑定身份。
$ErrorActionPreference = 'Stop'
$taskRun = Get-Item -LiteralPath 'D:\FPGA_Competition\w2b\tmp\2B\S2B-T19\qualification_board_session_20261017_r14'
$taskExecutable = Get-Item -LiteralPath 'D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe'
$taskSha = (Get-FileHash -LiteralPath $taskExecutable.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
if ($taskSha -ne 'e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3') { throw '硬件服务工具版本与已核验基线不符' }
$taskServers = @(Get-Process -Name 'hw_server' -ErrorAction SilentlyContinue)
$taskListeners = @(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue)
if ($taskServers.Count -ne 0 -or $taskListeners.Count -ne 0) { throw '服务或端口已被占用' }
$taskStdout = Join-Path $taskRun.FullName 'attempt02_hw_server_stdout.log'
$taskStderr = Join-Path $taskRun.FullName 'attempt02_hw_server_stderr.log'
$taskIdentity = Join-Path $taskRun.FullName 'attempt02_hw_server_identity.json'
foreach ($taskPath in @($taskStdout, $taskStderr, $taskIdentity)) {
    if (Test-Path -LiteralPath $taskPath) { throw "拒绝覆盖已有目标：$taskPath" }
}
$taskChild = Start-Process -FilePath $taskExecutable.FullName -ArgumentList @('-s','tcp::3121') -WorkingDirectory $taskRun.FullName -WindowStyle Hidden -PassThru -RedirectStandardOutput $taskStdout -RedirectStandardError $taskStderr
$taskDeadline = (Get-Date).AddSeconds(20)
do {
    $taskCurrent = Get-Process -Id $taskChild.Id -ErrorAction SilentlyContinue
    $taskBound = @(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue)
    if ($null -eq $taskCurrent) { throw '本任务硬件服务启动后已退出' }
    if ($taskBound.Count -gt 0) { break }
    Start-Sleep -Milliseconds 250
} while ((Get-Date) -lt $taskDeadline)
if ($taskBound.Count -eq 0 -or @($taskBound | Where-Object { $_.OwningProcess -ne $taskChild.Id }).Count -ne 0) { throw '本任务服务未独占监听3121' }
if ($taskCurrent.Path -cne $taskExecutable.FullName) { throw '子进程映像路径不一致' }
$taskCommandLine = '"' + $taskExecutable.FullName + '" -s tcp::3121'
$taskResult = [pscustomobject]@{
    status='OWNED_SERVER_READY';checked_at_utc8=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(8)).ToString('o')
    native=[pscustomobject]@{ProcessId=$taskCurrent.Id;ParentProcessId=$PID;ExecutablePath=$taskCurrent.Path;CommandLine=$taskCommandLine;CreationTimeFileTimeUtc=[string]$taskCurrent.StartTime.ToUniversalTime().ToFileTimeUtc()}
    native_sha256=$taskSha
    listeners=@($taskBound | Select-Object LocalAddress,LocalPort,OwningProcess)
    hardware_program_execution='NOT_RUN'
    command_line_provenance='START_PROCESS_FILEPATH_AND_ARGUMENTLIST_IN_THIS_SCRIPT'
}
$taskJson = $taskResult | ConvertTo-Json -Depth 5
$taskEncoding = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($taskIdentity, $taskJson + "`n", $taskEncoding)
$taskJson
