# 仅为本任务启动独占hw_server；经Vitis官方启动批处理加载环境。
$ErrorActionPreference = 'Stop'
$taskRun = Get-Item -LiteralPath 'D:\FPGA_Competition\w2b\tmp\stage2b\S2B-T19\formal_hw_server_20261018_r02'
$taskLauncher = Get-Item -LiteralPath 'D:\Xilinx\2026.1\Vitis\bin\hw_server.bat'
$taskExecutable = Get-Item -LiteralPath 'D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe'
$taskSha = (Get-FileHash -LiteralPath $taskExecutable.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
if ($taskSha -ne 'e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3') { throw '硬件服务工具版本与已核验基线不符' }
$taskServers = @(Get-Process -Name 'hw_server' -ErrorAction SilentlyContinue)
$taskListeners = @(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue)
if ($taskServers.Count -ne 0 -or $taskListeners.Count -ne 0) { throw '服务或端口已被占用' }
$taskStdout = Join-Path $taskRun.FullName 'attempt03_hw_server_stdout.log'
$taskStderr = Join-Path $taskRun.FullName 'attempt03_hw_server_stderr.log'
$taskIdentity = Join-Path $taskRun.FullName 'attempt03_hw_server_identity.json'
foreach ($taskPath in @($taskStdout, $taskStderr, $taskIdentity)) {
    if (Test-Path -LiteralPath $taskPath) { throw "拒绝覆盖已有目标：$taskPath" }
}
$taskArgs = @('/d','/c',('"' + $taskLauncher.FullName + '" -stcp::3121'))
$taskChild = Start-Process -FilePath $env:ComSpec -ArgumentList $taskArgs -WorkingDirectory $taskRun.FullName -WindowStyle Hidden -PassThru -RedirectStandardOutput $taskStdout -RedirectStandardError $taskStderr
$taskDeadline = (Get-Date).AddSeconds(25)
do {
    $taskBound = @(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue)
    if ($taskBound.Count -gt 0) { break }
    $taskParent = Get-Process -Id $taskChild.Id -ErrorAction SilentlyContinue
    if ($null -eq $taskParent) { throw '本任务hw_server启动器已退出且3121未监听' }
    Start-Sleep -Milliseconds 250
} while ((Get-Date) -lt $taskDeadline)
if ($taskBound.Count -eq 0) { throw '本任务Vitis服务未在限时内监听3121' }
if (@($taskBound | Where-Object { $_.LocalPort -ne 3121 }).Count -ne 0) { throw '监听端口检查异常' }
$taskNative = Get-Process -Id ([int]$taskBound[0].OwningProcess) -ErrorAction Stop
if ($taskNative.Path -cne $taskExecutable.FullName) { throw '3121监听进程映像路径不符' }
if (@($taskBound | Where-Object { $_.OwningProcess -ne $taskNative.Id }).Count -ne 0) { throw '3121存在非本任务监听进程' }
$taskResult = [pscustomobject]@{
    status='OWNED_SERVER_READY';checked_at_utc8=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(8)).ToString('o')
    native=[pscustomobject]@{ProcessId=$taskNative.Id;ParentProcessId=$taskChild.Id;ExecutablePath=$taskNative.Path;CommandLine=('"' + $taskExecutable.FullName + '" -stcp::3121');CreationTimeFileTimeUtc=[string]$taskNative.StartTime.ToUniversalTime().ToFileTimeUtc()}
    native_sha256=$taskSha
    launcher=[pscustomobject]@{path=$taskLauncher.FullName;sha256=(Get-FileHash -LiteralPath $taskLauncher.FullName -Algorithm SHA256).Hash.ToLowerInvariant();process_id=$taskChild.Id;arguments=$taskArgs}
    listeners=@($taskBound | Select-Object LocalAddress,LocalPort,OwningProcess)
    hardware_program_execution='NOT_RUN'
    command_line_provenance='VITIS_BATCH_LAUNCHER_AND_3121_OWNER_PID'
}
$taskJson = $taskResult | ConvertTo-Json -Depth 6
$taskEncoding = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($taskIdentity, $taskJson + "`n", $taskEncoding)
$taskJson
