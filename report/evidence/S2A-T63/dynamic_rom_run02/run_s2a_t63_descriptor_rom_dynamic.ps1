[CmdletBinding()]
param(
    [switch]$RunSimulation
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding

function Get-NormalizedFullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Assert-PathWithin {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$AllowedRoot
    )
    $candidate = Get-NormalizedFullPath -Path $Path
    $root = Get-NormalizedFullPath -Path $AllowedRoot
    $volumeRoot = [System.IO.Path]::GetPathRoot($root)
    if ($root.Length -gt $volumeRoot.Length) {
        $root = $root.TrimEnd('\')
    }
    $same = $candidate.Equals($root, [System.StringComparison]::OrdinalIgnoreCase)
    $prefix = $root + '\'
    $child = $candidate.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)
    if (-not ($same -or $child)) {
        throw "路径越过允许的完整目录边界：$candidate；边界：$root"
    }
}

function Assert-NoReparsePathChain {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [switch]$AllowMissingLeaf
    )
    $full = Get-NormalizedFullPath -Path $Path
    $volumeRoot = [System.IO.Path]::GetPathRoot($full)
    $volumeItem = Get-Item -LiteralPath $volumeRoot -Force -ErrorAction Stop
    if (($volumeItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "拒绝经过 reparse point：$volumeRoot"
    }
    $relative = $full.Substring($volumeRoot.Length)
    $segments = @($relative -split '[\\/]' | Where-Object { $_ -ne '' })
    $cursor = $volumeRoot
    for ($index = 0; $index -lt $segments.Count; $index++) {
        $cursor = Join-Path -Path $cursor -ChildPath $segments[$index]
        if (-not (Test-Path -LiteralPath $cursor)) {
            if ($AllowMissingLeaf -and $index -eq ($segments.Count - 1)) {
                return
            }
            throw "路径组件不存在：$cursor"
        }
        $item = Get-Item -LiteralPath $cursor -Force -ErrorAction Stop
        if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "拒绝经过 reparse point：$cursor"
        }
    }
}

function Assert-OrdinaryFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$AllowedRoot
    )
    Assert-PathWithin -Path $Path -AllowedRoot $AllowedRoot
    Assert-NoReparsePathChain -Path $Path
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($item.PSIsContainer) {
        throw "要求普通文件：$Path"
    }
}

function New-IsolatedDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$AllowedRoot
    )
    Assert-PathWithin -Path $Path -AllowedRoot $AllowedRoot
    Assert-NoReparsePathChain -Path $Path -AllowMissingLeaf
    if (Test-Path -LiteralPath $Path) {
        throw "拒绝复用已存在目录或文件：$Path"
    }
    New-Item -ItemType Directory -Path $Path | Out-Null
    Assert-NoReparsePathChain -Path $Path
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if (-not $item.PSIsContainer) {
        throw "新建目标不是目录：$Path"
    }
}

function Assert-NewOutputPath {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$AllowedRoot
    )
    Assert-PathWithin -Path $Path -AllowedRoot $AllowedRoot
    $full = Get-NormalizedFullPath -Path $Path
    $root = Get-NormalizedFullPath -Path $AllowedRoot
    if (-not [System.IO.Path]::GetDirectoryName($full).Equals($root.TrimEnd('\'), [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "输出文件必须是运行目录的直接子项：$full"
    }
    Assert-NoReparsePathChain -Path $Path -AllowMissingLeaf
    if (Test-Path -LiteralPath $Path) {
        throw "拒绝覆盖已存在输出：$Path"
    }
}

function Write-NewUtf8Text {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$AllowedRoot
    )
    Assert-NewOutputPath -Path $Path -AllowedRoot $AllowedRoot
    $encoding = [System.Text.UTF8Encoding]::new($false)
    $bytes = $encoding.GetBytes($Text)
    $stream = [System.IO.File]::Open(
        $Path,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
    )
    try {
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush()
    }
    finally {
        $stream.Dispose()
    }
}

$expectedRoot = 'D:\FPGA_Competition'
$expectedTaskRoot = Join-Path $expectedRoot 'report\evidence\S2A-T63\dynamic_rom_run02'
$resolvedRoot = Get-NormalizedFullPath -Path $expectedRoot
$taskRoot = Get-NormalizedFullPath -Path $PSScriptRoot
if (-not $resolvedRoot.Equals($expectedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "工程根目录与任务卡不一致：$resolvedRoot"
}
if (-not $taskRoot.Equals((Get-NormalizedFullPath -Path $expectedTaskRoot), [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "任务脚本必须位于独立 run02 目录：$taskRoot"
}
Assert-NoReparsePathChain -Path $resolvedRoot
Assert-NoReparsePathChain -Path $taskRoot

$pythonVerifier = Join-Path $taskRoot 'prepare_s2a_t63_dynamic_rom.py'
$offlineTests = Join-Path $taskRoot 'test_s2a_t63_dynamic_rom.py'
$expectedTb = Join-Path $taskRoot 'tb_s2a_t63_descriptor_rom_dynamic.sv'
$fixtureManifest = Join-Path $taskRoot 'dynamic_rom_fixture_binding.json'
$passLine = 'PASS S2A-T63 dynamic descriptor ROM layers=38 fields_per_layer=104 channels=3164 fields_per_channel=6 op=21,3,11,1,2 yolo_alias=2'
foreach ($path in @($pythonVerifier, $offlineTests, $expectedTb)) {
    Assert-OrdinaryFile -Path $path -AllowedRoot $taskRoot
}

$runId = [DateTime]::Now.ToString('yyyyMMdd_HHmmss') + '_' + [Guid]::NewGuid().ToString('N')
$workRoot = Join-Path $taskRoot ('tool_run_' + $runId)
$tempRoot = Join-Path $workRoot 'temp'
$userDataRoot = Join-Path $workRoot 'user_data'
New-IsolatedDirectory -Path $workRoot -AllowedRoot $taskRoot
New-IsolatedDirectory -Path $tempRoot -AllowedRoot $workRoot
New-IsolatedDirectory -Path $userDataRoot -AllowedRoot $workRoot

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
    Assert-NewOutputPath -Path $LogPath -AllowedRoot $workRoot
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & $Executable @Arguments 2>&1 | Out-File -LiteralPath $LogPath -Encoding utf8 -NoClobber -ErrorAction Stop
        $nativeCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    if ($nativeCode -ne 0) {
        throw "工具退出码 $nativeCode：$Executable；日志：$LogPath"
    }
}

function Resolve-VivadoTool {
    param([Parameter(Mandatory = $true)][string]$ToolName)
    if (-not [string]::IsNullOrWhiteSpace($env:XILINX_VIVADO)) {
        $candidate = Join-Path (Join-Path $env:XILINX_VIVADO 'bin') ($ToolName + '.bat')
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Get-Item -LiteralPath $candidate -ErrorAction Stop).FullName
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

$python = Get-Command py.exe -ErrorAction Stop
Invoke-LoggedNative -Executable $python.Source -Arguments @('-3', '-B', $pythonVerifier, '--validate') -LogPath (Join-Path $workRoot 'validate.log')
Invoke-LoggedNative -Executable $python.Source -Arguments @('-3', '-B', $offlineTests) -LogPath (Join-Path $workRoot 'offline_tests.log')

if (-not $RunSimulation) {
    Write-Output "离线 fixture 校验与测试完成；未运行 Vivado/XVLOG/XELAB/XSim。日志：$workRoot"
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
    $allowedRoot = if ($path.Equals($packagePath, [System.StringComparison]::OrdinalIgnoreCase)) { $resolvedRoot } else { $taskRoot }
    Assert-OrdinaryFile -Path $path -AllowedRoot $allowedRoot
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

$xsimLogPath = Join-Path $workRoot 'xsim.log'
Assert-OrdinaryFile -Path $xsimLogPath -AllowedRoot $workRoot
$simulationLog = Get-Content -LiteralPath $xsimLogPath -Raw -Encoding utf8
$passMatches = [regex]::Matches($simulationLog, [regex]::Escape($passLine))
if ($passMatches.Count -ne 1) {
    throw "仿真日志中的精确 PASS 行数量不是 1：$($passMatches.Count)；日志：$xsimLogPath"
}
$result = [ordered]@{
    schema_version = 's2a_t63_dynamic_rom_simulation_v1'
    task_id = 'S2A-T63-DYNAMIC-ROM'
    status = 'PASS'
    exact_pass_line = $passLine
    fixture_binding_sha256 = (Get-FileHash -LiteralPath $fixtureManifest -Algorithm SHA256).Hash.ToLowerInvariant()
    xsim_log_sha256 = (Get-FileHash -LiteralPath $xsimLogPath -Algorithm SHA256).Hash.ToLowerInvariant()
    xsim_pid_after_exit = @((Get-CimInstance -ClassName Win32_Process | Where-Object { $_.Name -in @('xsim.exe', 'xsimk.exe') }).ProcessId)
    resource_snapshot = @{ free_ram_mb = $freeRamMb; free_d_drive_mb = $freeDiskMb }
    execution = @{ xvlog_exit_code = 0; xelab_exit_code = 0; xsim_exit_code = 0 }
}
$resultPath = Join-Path $workRoot 'simulation_result.json'
Write-NewUtf8Text -Path $resultPath -Text (($result | ConvertTo-Json -Depth 8) + [Environment]::NewLine) -AllowedRoot $workRoot
Write-Output "动态 ROM 仿真通过；日志与结果：$workRoot"
