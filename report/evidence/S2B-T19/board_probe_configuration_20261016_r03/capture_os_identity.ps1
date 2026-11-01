# 只读记录COM4与现有硬件服务，不连接串口或JTAG，不操作板卡。
$ErrorActionPreference = 'Stop'
$taskDirectory = Get-Item -LiteralPath $PSScriptRoot
$taskPortPath = Join-Path $taskDirectory.FullName 'uart_identity.json'
$taskServicePath = Join-Path $taskDirectory.FullName 'hw_service_inventory.json'
foreach ($taskPath in @($taskPortPath, $taskServicePath)) {
    if (Test-Path -LiteralPath $taskPath) { throw "拒绝覆盖已有身份快照：$taskPath" }
}
$taskPorts = @(Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -match '\(COM4\)$' })
if ($taskPorts.Count -ne 1) { throw "COM4设备数量不是1：$($taskPorts.Count)" }
$taskPort = $taskPorts[0]
$taskIdentity = [ordered]@{
    port='COM4';name=[string]$taskPort.Name;pnp_device_id=[string]$taskPort.PNPDeviceID
    config_manager_error_code=[int]$taskPort.ConfigManagerErrorCode
}
if ($taskIdentity.config_manager_error_code -ne 0) { throw 'COM4设备状态异常' }
$taskServices = @(Get-CimInstance Win32_Process -Filter "Name='hw_server.exe' OR Name='cs_server.exe'" |
    Select-Object ProcessId, ParentProcessId, Name, ExecutablePath)
$taskInventory = [ordered]@{
    recorded_at_utc8=[DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(8)).ToString('o')
    services=$taskServices
    scope='操作系统进程与设备只读快照，不证明板卡初始化或硬件验收。'
}
$taskEncoding = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($taskPortPath, ($taskIdentity | ConvertTo-Json -Depth 4) + "`n", $taskEncoding)
[IO.File]::WriteAllText($taskServicePath, ($taskInventory | ConvertTo-Json -Depth 5) + "`n", $taskEncoding)
[pscustomobject]@{port=$taskIdentity.port;name=$taskIdentity.name;hardware_service_count=$taskServices.Count} | ConvertTo-Json -Compress
