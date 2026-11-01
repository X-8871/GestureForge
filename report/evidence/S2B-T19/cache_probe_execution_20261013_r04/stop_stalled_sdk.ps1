# 只停止本轮超过三分钟无进度、释放独占服务后仍未返回的SDK子进程。
$ErrorActionPreference = 'Stop'
$taskRun = Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\tmp\2B\S2B-T19\board_run_20261013_r04'
if (-not $taskRun.PSIsContainer) { throw '运行目标不是目录' }
$taskDestination = Join-Path $taskRun.FullName 'sdk_timeout_stop.json'
if (Test-Path -LiteralPath $taskDestination) { throw '拒绝覆盖超时停止记录' }
$taskClosed = Get-Content -LiteralPath (Join-Path $taskRun.FullName 'server_close.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($taskClosed.status -cne 'OWNED_SERVER_CLOSED' -or -not $taskClosed.native_absent) { throw '自有服务尚未闭合' }
$taskChild = Get-CimInstance Win32_Process -Filter 'ProcessId=26300'
$taskParent = Get-CimInstance Win32_Process -Filter 'ProcessId=3420'
if ($null -eq $taskChild -or $null -eq $taskParent) { throw '待停止进程已不存在，不伪造本次终止' }
if ($taskChild.ParentProcessId -ne 3420 -or $taskParent.ParentProcessId -ne 23424 -or
    [string]$taskChild.CreationDate.ToFileTimeUtc() -cne '134363790152687010' -or
    [string]$taskParent.CreationDate.ToFileTimeUtc() -cne '134363790138466810' -or
    $taskChild.ExecutablePath -cne 'D:\Xilinx\2026.1\Vivado\tps\win64\python-3.13.0\python.exe' -or
    $taskChild.CommandLine -cne 'python.exe   C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\vitis\run_s2b_visibility_probe.py' -or
    $taskParent.CommandLine -cne 'C:\WINDOWS\system32\cmd.exe /c ""D:\Xilinx\2026.1\Vitis\bin\vitis.bat" -s C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\vitis\run_s2b_visibility_probe.py"') { throw '子进程或父进程精确身份不符' }
$taskImage = Get-Item -LiteralPath $taskChild.ExecutablePath
$taskSha = (Get-FileHash -LiteralPath $taskImage.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
$taskProcess = Get-Process -Id $taskChild.ProcessId
$null = $taskProcess.Handle
$taskStarted = Get-Date -Format o
Stop-Process -Id $taskChild.ProcessId
if (-not $taskProcess.WaitForExit(10000)) { throw '自有SDK停止后未退出' }
if (@(Get-CimInstance Win32_Process -Filter 'ProcessId=26300').Count -ne 0) { throw '自有SDK仍存在' }
$taskResult = [pscustomobject]@{status='OWNED_SDK_TERMINATED_AFTER_UNLOAD_NO_PROGRESS';started_at_utc8=$taskStarted;finished_at_utc8=(Get-Date -Format o);native_pid=26300;native_parent_pid=3420;native_birth='134363790152687010';native_image=$taskImage.FullName;native_sha256=$taskSha;native_exit_code=$taskProcess.ExitCode;native_absent=$true;last_completed_call='runtime.verify_map_cleanup_target';last_completed_at_utc8='2026-10-13T23:31:01.946587+08:00';limitation='public unloadhw未返回，具体内部卡点未知；串口close及controller.close已返回，SDK正常unload/disconnect/dispose未完成，不伪造入口最终结果。'}
[IO.File]::WriteAllText($taskDestination,($taskResult | ConvertTo-Json -Depth 5)+"`n",(New-Object Text.UTF8Encoding($false)))
$taskResult | ConvertTo-Json -Depth 5
