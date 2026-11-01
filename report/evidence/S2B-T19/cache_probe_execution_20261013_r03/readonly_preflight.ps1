# 只读采集现场端口、进程及内存，不打开串口、不下载或复位板卡。
$ErrorActionPreference = 'Stop'
$taskRun = Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\tmp\2B\S2B-T19\board_run_20261013_r03'
if (-not $taskRun.PSIsContainer) { throw '运行路径不是目录' }
$taskPorts = @(Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -match '\(COM[0-9]+\)$' } | Select-Object Name,PNPDeviceID,ConfigManagerErrorCode)
$taskServers = @(Get-CimInstance Win32_Process -Filter "Name='hw_server.exe'" | Select-Object ProcessId,ParentProcessId,ExecutablePath,CreationDate)
$taskHeavy = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(vivado|vitis|python)(\.exe|\.bat)$' } | Select-Object ProcessId,ParentProcessId,Name,CreationDate,CommandLine)
$taskListeners = @(Get-NetTCPConnection -LocalPort 3121 -State Listen -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess)
$taskOs = Get-CimInstance Win32_OperatingSystem
$taskRecord = [pscustomobject]@{checked_at_utc8=(Get-Date -Format o);ports=$taskPorts;servers=$taskServers;heavy_processes=$taskHeavy;listeners=$taskListeners;free_physical_bytes=([int64]$taskOs.FreePhysicalMemory*1024);total_physical_bytes=([int64]$taskOs.TotalVisibleMemorySize*1024);hardware_execution='NOT_RUN'}
$taskEncoding = New-Object System.Text.UTF8Encoding($false)
$taskFile = Join-Path $taskRun.FullName 'readonly_preflight.json'
if (Test-Path -LiteralPath $taskFile) { throw '拒绝覆盖现场记录' }
[IO.File]::WriteAllText($taskFile, ($taskRecord | ConvertTo-Json -Depth 6)+"`n", $taskEncoding)
if ($taskServers.Count -ne 0 -or $taskListeners.Count -ne 0) { throw '硬件服务或3121已被占用' }
$taskUart = @($taskPorts | Where-Object { $_.Name -match '\(COM4\)$' })
if ($taskUart.Count -ne 1 -or $taskUart[0].ConfigManagerErrorCode -ne 0 -or $taskUart[0].PNPDeviceID -cne 'USB\VID_10C4&PID_EA60\D02E61162787ED11A536569F9D1CC348') { throw 'COM4实际身份不符合既有板卡' }
$taskUartFile = Join-Path $taskRun.FullName 'uart_identity.json'
if (Test-Path -LiteralPath $taskUartFile) { throw '拒绝覆盖UART身份' }
$taskIdentity = [pscustomobject]@{port='COM4';name=$taskUart[0].Name;pnp_device_id=$taskUart[0].PNPDeviceID;config_manager_error_code=[int]$taskUart[0].ConfigManagerErrorCode}
[IO.File]::WriteAllText($taskUartFile, ($taskIdentity | ConvertTo-Json -Depth 4)+"`n", $taskEncoding)
$taskRecord | ConvertTo-Json -Depth 6
