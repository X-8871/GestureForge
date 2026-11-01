[CmdletBinding()]
param(
    [switch]$RunSimulation
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding

$expectedRoot = 'D:\FPGA_Competition'
$taskRoot = (Get-Item -LiteralPath $PSScriptRoot -ErrorAction Stop).FullName
$resolvedRoot = (Resolve-Path -LiteralPath $expectedRoot -ErrorAction Stop).Path
if (-not $resolvedRoot.Equals($expectedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "工程根目录与任务卡不一致：$resolvedRoot"
}
if (-not $taskRoot.StartsWith(($expectedRoot + '\report\evidence\S2A-T63\dynamic_rom_run01'), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "任务脚本路径不在指定的 D 盘证据目录：$taskRoot"
}

$pythonVerifier = Join-Path $taskRoot 'prepare_s2a_t63_dynamic_rom.py'
$offlineTests = Join-Path $taskRoot 'test_s2a_t63_dynamic_rom.py'
$expectedTb = Join-Path $taskRoot 'tb_s2a_t63_descriptor_rom_dynamic.sv'
$fixtureManifest = Join-Path $taskRoot 'dynamic_rom_fixture_binding.json'
$passLine = 'PASS S2A-T63 dynamic descriptor ROM layers=38 fields_per_layer=104 channels=3164 fields_per_channel=6 op=21,3,11,1,2 yolo_alias=2'
$runId = [DateTime]::Now.ToString('yyyyMMdd_HHmmss') + '_' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
$workRoot = Join-Path $taskRoot ('tool_run_' + $runId)
$tempRoot = Join-Path $workRoot 'temp'
$userDataRoot = Join-Path $workRoot 'user_data'
New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null
New-Item -ItemType Directory -Path $userDataRoot -Force | Out-Null

$env:TEMP = $tempRoot
$env:TMP = $tempRoot
$env:TMPDIR = $tempRoot
$env:XILINX_LOCAL_USER_DATA = $userDataRoot
$env:PYTHONDONTWRITEBYTECODE = '1'

function Invoke-LoggedNative {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$LogPath
    )
    & $Executable @Arguments 2>&1 | Out-File -LiteralPath $LogPath -Encoding utf8
    $nativeCode = $LASTEXITCODE
    if ($nativeCode -ne 0) {
        throw "工具退出码 $nativeCode：$Executable；日志：$LogPath"
    }
}

function Resolve-VivadoTool {
    param([Parameter(Mandatory = $true)][string]$ToolName)
    if (-not [string]::IsNullOrWhiteSpace($env:XILINX_VIVADO)) {
        $candidate = Join-Path (Join-Path $env:XILINX_VIVADO 'bin') ($ToolName + '.bat')
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Get-Item -LiteralPath $candidate).FullName
        }
    }
    $command = Get-Command ($ToolName + '.bat') -ErrorAction SilentlyContinue
    if ($null -eq $command) {
        $command = Get-Command $ToolName -ErrorAction SilentlyContinue
    }
    if ($null -eq $command) {
        throw "未找到 Vivado 工具 $ToolName；没有启动任何仿真工具。"
    }
    return $command.Source
}

if (-not (Test-Path -LiteralPath $pythonVerifier -PathType Leaf)) {
    throw "独立验证器缺失：$pythonVerifier"
}
if (-not (Test-Path -LiteralPath $expectedTb -PathType Leaf)) {
    throw "动态 ROM testbench 缺失：$expectedTb"
}
if (-not (Test-Path -LiteralPath $offlineTests -PathType Leaf)) {
    throw "离线测试缺失：$offlineTests"
}
$python = Get-Command py.exe -ErrorAction Stop
Invoke-LoggedNative -Executable $python.Source -Arguments @('-3', '-B', $pythonVerifier, '--prepare') -LogPath (Join-Path $workRoot 'prepare.log')
Invoke-LoggedNative -Executable $python.Source -Arguments @('-3', '-B', $pythonVerifier, '--validate') -LogPath (Join-Path $workRoot 'validate.log')
Invoke-LoggedNative -Executable $python.Source -Arguments @('-3', '-B', $offlineTests) -LogPath (Join-Path $workRoot 'offline_tests.log')

if (-not $RunSimulation) {
    Write-Output "离线 fixture 准备与校验完成；未运行 Vivado/XVLOG/XELAB/XSim。日志：$workRoot"
    exit 0
}

$protectedNames = @('vivado.exe', 'xsim.exe', 'xsimk.exe', 'xvlog.exe', 'xelab.exe')
$activeTools = Get-CimInstance -ClassName Win32_Process |
    Where-Object { $protectedNames -contains $_.Name }
if ($activeTools) {
    $details = $activeTools | ForEach-Object { "$($_.Name) PID=$($_.ProcessId)" }
    throw "检测到既有 Vivado/XSim/编译进程；为避免占用或影响其他窗口，已中止：$($details -join ', ')"
}

$freeRamMb = [math]::Floor((Get-CimInstance -ClassName Win32_OperatingSystem).FreePhysicalMemory / 1024)
$dDrive = Get-PSDrive -Name D -ErrorAction Stop
$freeDiskMb = [math]::Floor($dDrive.Free / 1MB)
if ($freeRamMb -lt 2048 -or $freeDiskMb -lt 2048) {
    throw ("资源保护门限未满足：可用 RAM={0}MB、D 盘={1}MB；未启动编译/仿真。" -f $freeRamMb, $freeDiskMb)
}

$xvlog = Resolve-VivadoTool -ToolName 'xvlog'
$xelab = Resolve-VivadoTool -ToolName 'xelab'
$xsim = Resolve-VivadoTool -ToolName 'xsim'
$packagePath = Join-Path $resolvedRoot 'src\s2a_network_descriptor_pkg.sv'
$layerFixture = Join-Path $taskRoot 'expected_layers.mem'
$channelFixture = Join-Path $taskRoot 'expected_channels.mem'
foreach ($path in @($packagePath, $layerFixture, $channelFixture, $fixtureManifest)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "运行输入缺失：$path"
    }
}

$forwardLayerFixture = $layerFixture.Replace('\', '/')
$forwardChannelFixture = $channelFixture.Replace('\', '/')
$snapshot = 's2a_t63_descriptor_rom_dynamic'
Push-Location -LiteralPath $workRoot
try {
    Invoke-LoggedNative -Executable $xvlog -Arguments @('-sv', '-work', 'work', $packagePath, $expectedTb) -LogPath (Join-Path $workRoot 'xvlog.log')
    Invoke-LoggedNative -Executable $xelab -Arguments @('work.tb_s2a_t63_descriptor_rom_dynamic', '-s', $snapshot) -LogPath (Join-Path $workRoot 'xelab.log')
    Invoke-LoggedNative -Executable $xsim -Arguments @(
        $snapshot,
        '-runall',
        '-testplusarg', "LAYER_FIXTURE=$forwardLayerFixture",
        '-testplusarg', "CHANNEL_FIXTURE=$forwardChannelFixture"
    ) -LogPath (Join-Path $workRoot 'xsim.log')
}
finally {
    Pop-Location
}

$simulationLog = Get-Content -LiteralPath (Join-Path $workRoot 'xsim.log') -Raw -Encoding utf8
$passMatches = [regex]::Matches($simulationLog, [regex]::Escape($passLine))
if ($passMatches.Count -ne 1) {
    throw "仿真日志中的精确 PASS 行数量不是 1：$($passMatches.Count)；日志：$(Join-Path $workRoot 'xsim.log')"
}
$result = [ordered]@{
    schema_version = 's2a_t63_dynamic_rom_simulation_v1'
    task_id = 'S2A-T63-DYNAMIC-ROM'
    status = 'PASS'
    exact_pass_line = $passLine
    fixture_binding_sha256 = (Get-FileHash -LiteralPath $fixtureManifest -Algorithm SHA256).Hash.ToLowerInvariant()
    xsim_log_sha256 = (Get-FileHash -LiteralPath (Join-Path $workRoot 'xsim.log') -Algorithm SHA256).Hash.ToLowerInvariant()
    xsim_pid_after_exit = @((Get-CimInstance -ClassName Win32_Process | Where-Object { $_.Name -in @('xsim.exe', 'xsimk.exe') }).ProcessId)
    resource_snapshot = @{ free_ram_mb = $freeRamMb; free_d_drive_mb = $freeDiskMb }
    execution = @{ xvlog_exit_code = 0; xelab_exit_code = 0; xsim_exit_code = 0 }
}
$resultPath = Join-Path $workRoot 'simulation_result.json'
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resultPath -Encoding utf8
Write-Output "动态 ROM 仿真通过；日志与结果：$workRoot"
