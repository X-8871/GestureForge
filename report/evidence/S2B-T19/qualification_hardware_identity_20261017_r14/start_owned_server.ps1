# 仅为单样本资格准备启动本任务独占hw_server；不连接XSDB或发目标命令。
$ErrorActionPreference = 'Stop'
$taskRun = Get-Item -LiteralPath 'D:\FPGA_Competition\w2b\tmp\2B\S2B-T19\qualification_board_session_20261017_r14'
if (-not $taskRun.PSIsContainer) { throw '运行目标不是目录' }
$taskExecutable = Get-Item -LiteralPath 'D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe'
if ($taskExecutable.PSIsContainer) { throw '工具目标不是文件' }
$taskSha = (Get-FileHash -LiteralPath $taskExecutable.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
if ($taskSha -ne 'e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3') { throw '硬件服务工具版本与已核验基线不符' }
$taskServers = @(Get-CimInstance Win32_Process -Filter "Name='hw_server.exe'")
$taskListeners = @(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue)
if ($taskServers.Count -ne 0 -or $taskListeners.Count -ne 0) { throw '服务或端口已被占用' }
$taskStdout = Join-Path $taskRun.FullName 'hw_server_stdout.log'
$taskStderr = Join-Path $taskRun.FullName 'hw_server_stderr.log'
$taskIdentity = Join-Path $taskRun.FullName 'hw_server_identity.json'
foreach ($taskPath in @($taskStdout, $taskStderr, $taskIdentity)) {
    if (Test-Path -LiteralPath $taskPath) { throw "拒绝覆盖已有目标：$taskPath" }
}
$taskChild = Start-Process -FilePath $taskExecutable.FullName -ArgumentList @('-s','tcp::3121') -WorkingDirectory $taskRun.FullName -WindowStyle Hidden -PassThru -RedirectStandardOutput $taskStdout -RedirectStandardError $taskStderr
$taskDeadline = (Get-Date).AddSeconds(20)
do {
    $taskCurrent = Get-CimInstance Win32_Process -Filter "ProcessId=$($taskChild.Id)"
    $taskBound = @(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue)
    if ($null -eq $taskCurrent) { throw '本任务硬件服务启动后已退出' }
    if ($taskBound.Count -gt 0) { break }
    Start-Sleep -Milliseconds 250
} while ((Get-Date) -lt $taskDeadline)
if ($taskBound.Count -eq 0 -or @($taskBound | Where-Object { $_.OwningProcess -ne $taskChild.Id }).Count -ne 0) { throw '本任务服务未独占监听3121' }
$taskExpectedCommandLines = @(($taskExecutable.FullName + ' -s tcp::3121'), ('"' + $taskExecutable.FullName + '" -s tcp::3121'))
if ($taskCurrent.ExecutablePath -cne $taskExecutable.FullName -or $taskCurrent.CommandLine -cnotin $taskExpectedCommandLines) { throw '子进程身份或命令行不一致' }
$taskResult = [pscustomobject]@{
    status='OWNED_SERVER_READY';checked_at_utc8=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(8)).ToString('o')
    native=[pscustomobject]@{ProcessId=$taskCurrent.ProcessId;ParentProcessId=$taskCurrent.ParentProcessId;ExecutablePath=$taskCurrent.ExecutablePath;CommandLine=$taskCurrent.CommandLine;CreationTimeFileTimeUtc=[string]$taskCurrent.CreationDate.ToFileTimeUtc()}
    native_sha256=$taskSha
    listeners=@($taskBound | Select-Object LocalAddress,LocalPort,OwningProcess)
    hardware_program_execution='NOT_RUN'
}
$taskJson = $taskResult | ConvertTo-Json -Depth 5
$taskEncoding = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($taskIdentity, $taskJson + "`n", $taskEncoding)
$taskJson
