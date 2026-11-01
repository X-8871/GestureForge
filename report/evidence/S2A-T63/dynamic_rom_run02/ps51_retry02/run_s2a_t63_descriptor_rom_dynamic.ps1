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

function Get-T63FileSha256 {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$AllowedRoot
    )
    Assert-PathWithin -Path $Path -AllowedRoot $AllowedRoot
    $fullPath = Get-NormalizedFullPath -Path $Path
    $stream = [System.IO.File]::OpenRead($fullPath)
    $algorithm = [System.Security.Cryptography.SHA256]::Create()
    try {
        $digest = $algorithm.ComputeHash($stream)
        return [System.BitConverter]::ToString($digest).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $algorithm.Dispose()
        $stream.Dispose()
    }
}

$expectedRoot = 'D:\FPGA_Competition'
$expectedTaskRoot = Join-Path $expectedRoot 'report\evidence\S2A-T63\dynamic_rom_run02\ps51_retry02'
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
$roamingRoot = Join-Path $userDataRoot 'Roaming'
$localAppDataRoot = Join-Path $userDataRoot 'Local'
New-IsolatedDirectory -Path $workRoot -AllowedRoot $taskRoot
New-IsolatedDirectory -Path $tempRoot -AllowedRoot $workRoot
New-IsolatedDirectory -Path $userDataRoot -AllowedRoot $workRoot
New-IsolatedDirectory -Path $roamingRoot -AllowedRoot $userDataRoot
New-IsolatedDirectory -Path $localAppDataRoot -AllowedRoot $userDataRoot

$env:TEMP = $tempRoot
$env:TMP = $tempRoot
$env:TMPDIR = $tempRoot
$env:XILINX_LOCAL_USER_DATA = $userDataRoot
$env:HOME = $userDataRoot
$env:APPDATA = $roamingRoot
$env:LOCALAPPDATA = $localAppDataRoot
$env:PYTHONDONTWRITEBYTECODE = '1'
$executionLog = [System.Collections.Generic.List[object]]::new()
$processSnapshots = [System.Collections.Generic.List[object]]::new()
$resourceSnapshots = [System.Collections.Generic.List[object]]::new()
$protectedIdentities = @()
$baselineProcesses = @()

function Get-T63LogArtifactBinding {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$AllowedRoot
    )
    Assert-PathWithin -Path $Path -AllowedRoot $AllowedRoot
    $fullPath = Get-NormalizedFullPath -Path $Path
    if (-not (Test-Path -LiteralPath $fullPath)) {
        return [pscustomobject]@{
            path = $fullPath
            exists = $false
            length = $null
            sha256 = $null
        }
    }
    Assert-NoReparsePathChain -Path $fullPath
    $item = Get-Item -LiteralPath $fullPath -Force -ErrorAction Stop
    if ($item.PSIsContainer) {
        throw "日志绑定目标必须是普通文件：$fullPath"
    }
    return [pscustomobject]@{
        path = $fullPath
        exists = $true
        length = [long]$item.Length
        sha256 = Get-T63FileSha256 -Path $fullPath -AllowedRoot $AllowedRoot
    }
}

function Invoke-LoggedNative {
    param(
        [Parameter(Mandatory = $true)][string]$StageName,
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$ConsoleLogPath,
        [string]$NativeLogPath,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][System.Collections.Generic.List[object]]$ExecutionLog
    )
    if ($StageName -notmatch '^[a-z][a-z0-9_]*$') {
        throw "非法执行阶段名称：$StageName"
    }
    Assert-NewOutputPath -Path $ConsoleLogPath -AllowedRoot $workRoot
    if (-not [string]::IsNullOrWhiteSpace($NativeLogPath)) {
        $consoleFullPath = Get-NormalizedFullPath -Path $ConsoleLogPath
        $nativeFullPath = Get-NormalizedFullPath -Path $NativeLogPath
        if ($consoleFullPath.Equals($nativeFullPath, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "控制台捕获与工具原生日志必须使用不同路径：$consoleFullPath"
        }
        Assert-NewOutputPath -Path $NativeLogPath -AllowedRoot $workRoot
    }
    $previousErrorActionPreference = $ErrorActionPreference
    $startedAt = [DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8))
    $nativeCode = $null
    $invocationFailure = $null
    try {
        $ErrorActionPreference = 'Continue'
        & $Executable @Arguments 2>&1 | Out-File -LiteralPath $ConsoleLogPath -Encoding utf8 -NoClobber -ErrorAction Stop
        $nativeCode = $LASTEXITCODE
    }
    catch {
        $invocationFailure = $_
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    $endedAt = [DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8))
    $consoleBinding = Get-T63LogArtifactBinding -Path $ConsoleLogPath -AllowedRoot $workRoot
    $nativeBinding = $null
    if (-not [string]::IsNullOrWhiteSpace($NativeLogPath)) {
        $nativeBinding = Get-T63LogArtifactBinding -Path $NativeLogPath -AllowedRoot $workRoot
    }
    $failureMessage = $null
    if ($null -ne $invocationFailure) {
        $failureMessage = [string]$invocationFailure.Exception.Message
    }
    elseif ($null -eq $nativeCode) {
        $failureMessage = "工具没有返回退出码：$Executable"
    }
    elseif ($nativeCode -ne 0) {
        $failureMessage = "工具退出码 $nativeCode：$Executable"
    }
    elseif ($null -ne $nativeBinding -and -not $nativeBinding.exists) {
        $failureMessage = "工具返回成功但没有生成原生日志：$NativeLogPath"
    }
    $stageResultPath = Join-Path $workRoot ("stage_" + $StageName + "_result.json")
    $executionRecord = [pscustomobject]@{
        stage = $StageName
        executable = $Executable
        arguments = @($Arguments)
        started_at_utc8 = $startedAt.ToString('yyyy-MM-dd HH:mm:ss.fff zzz')
        ended_at_utc8 = $endedAt.ToString('yyyy-MM-dd HH:mm:ss.fff zzz')
        exit_code = $nativeCode
        status = if ($null -eq $failureMessage) { 'PASS' } else { 'FAIL' }
        console_log = $consoleBinding
        native_log = $nativeBinding
        stage_result_path = $stageResultPath
        error = $failureMessage
    }
    $ExecutionLog.Add($executionRecord)
    Write-NewUtf8Text -Path $stageResultPath -Text (($executionRecord | ConvertTo-Json -Depth 8) + [Environment]::NewLine) -AllowedRoot $workRoot
    if ($null -ne $failureMessage) {
        throw "$failureMessage；控制台日志：$ConsoleLogPath；原生日志：$NativeLogPath；阶段结果：$stageResultPath"
    }
    return $executionRecord
}

function Resolve-VivadoTool {
    param([Parameter(Mandatory = $true)][string]$ToolName)
    if (-not [string]::IsNullOrWhiteSpace($env:XILINX_VIVADO)) {
        $candidate = Join-Path (Join-Path $env:XILINX_VIVADO 'bin') ($ToolName + '.bat')
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Get-Item -LiteralPath $candidate -ErrorAction Stop).FullName
        }
        throw "固定 D 盘 Vivado 安装目录中缺少 $ToolName.bat：$candidate；不会回退到 PATH。"
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

function Get-T63ProtectedProcessAllowlist {
    return @(
        [pscustomobject]@{
            ProcessId = [long]8712
            ParentProcessId = [long]10724
            Name = 'vivado.exe'
            ExecutablePath = 'D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\vivado.exe'
            CommandLine = '"D:/Xilinx/2026.1/Vivado/bin/unwrapped/win64.o/vivado.exe"   -mode tcl -source D:\FPGA_Competition\report\evidence\S2A-T60\run06\mcp_server_instance\start_mcp.tcl'
            CreationDateUtc = '2026-09-29T18:07:06.1577890Z'
        },
        [pscustomobject]@{
            ProcessId = [long]22488
            ParentProcessId = [long]8712
            Name = 'xsimk.exe'
            ExecutablePath = 'D:\FPGA_Competition\report\evidence\S2A-T60\run06\isolated_project\s2a_t60_run06.sim\sim_1\behav\xsim\xsim.dir\tb_s2a_conv_layer35_row24_all_channels_behav\xsimk.exe'
            CommandLine = 'xsim.dir/tb_s2a_conv_layer35_row24_all_channels_behav/xsimk.exe -simmode gui -wdb tb_s2a_conv_layer35_row24_all_channels_behav.wdb -simrunnum 0 -socket 8295'
            CreationDateUtc = '2026-09-29T18:13:11.5972630Z'
        },
        [pscustomobject]@{
            ProcessId = [long]13156
            ParentProcessId = [long]8712
            Name = 'xsimk.exe'
            ExecutablePath = 'D:\FPGA_Competition\report\evidence\S2A-T61\run04\isolated_project\s2a_t61_run04.sim\sim_1\behav\xsim\xsim.dir\tb_s2a_conv_layer35_row25_all_channels_behav\xsimk.exe'
            CommandLine = 'xsim.dir/tb_s2a_conv_layer35_row25_all_channels_behav/xsimk.exe -simmode gui -wdb tb_s2a_conv_layer35_row25_all_channels_behav.wdb -simrunnum 0 -socket 12375'
            CreationDateUtc = '2026-09-29T19:39:52.1132030Z'
        }
    )
}

function Get-T63XilinxProcessSnapshot {
    $toolNames = @('vivado.exe', 'vivado_lab.exe', 'xsim.exe', 'xsimk.exe', 'xvlog.exe', 'xelab.exe', 'xvhdl.exe')
    $protectedIds = @((Get-T63ProtectedProcessAllowlist | ForEach-Object { [long]$_.ProcessId }))
    $processes = @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop |
        Where-Object { $toolNames -contains ([string]$_.Name).ToLowerInvariant() -or
            $protectedIds -contains [long]$_.ProcessId })
    return @($processes | Sort-Object -Property ProcessId | ForEach-Object {
        $creationDateUtc = ''
        if ($null -ne $_.CreationDate) {
            $creationDateUtc = ([DateTime]$_.CreationDate).ToUniversalTime().ToString(
                'o', [System.Globalization.CultureInfo]::InvariantCulture)
        }
        [pscustomobject]@{
            ProcessId = [long]$_.ProcessId
            ParentProcessId = [long]$_.ParentProcessId
            Name = [string]$_.Name
            ExecutablePath = [string]$_.ExecutablePath
            CommandLine = [string]$_.CommandLine
            CreationDateUtc = $creationDateUtc
        }
    })
}

function Assert-T63XilinxProcessSnapshot {
    param(
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$Processes,
        [Parameter(Mandatory = $true)][object[]]$ProtectedIdentities,
        [AllowEmptyCollection()][object[]]$BaselineProcesses = @(),
        [switch]$InitialSnapshot
    )
    $expectedByPid = @{}
    foreach ($identity in $ProtectedIdentities) {
        $identityPid = [long]$identity.ProcessId
        if ([string]::IsNullOrWhiteSpace([string]$identity.CreationDateUtc)) {
            throw "受保护身份 PID $identityPid 缺少可信 CreationDateUtc；拒绝运行。"
        }
        if ($expectedByPid.ContainsKey($identityPid)) {
            throw "保护身份表含重复 PID：$identityPid"
        }
        $expectedByPid[$identityPid] = $identity
    }
    if (-not $InitialSnapshot) {
        if ($null -eq $BaselineProcesses) {
            throw '后续进程快照缺少启动前身份基线。'
        }
    }
    $baselineByPid = @{}
    foreach ($baseline in $BaselineProcesses) {
        $baselineByPid[[long]$baseline.ProcessId] = $baseline
    }
    $seenPids = @{}
    foreach ($process in $Processes) {
        $processId = [long]$process.ProcessId
        if ($seenPids.ContainsKey($processId)) {
            throw "进程快照含重复 PID：$processId"
        }
        $seenPids[$processId] = $true
        if (-not $expectedByPid.ContainsKey($processId)) {
            throw "发现未授权 Vivado/XSim/XVLOG/XELAB 进程：$($process.Name) PID=$processId"
        }
        $expected = $expectedByPid[$processId]
        foreach ($field in @('Name', 'ExecutablePath', 'CommandLine')) {
            if (-not [string]::Equals([string]$process.$field, [string]$expected.$field,
                    [System.StringComparison]::Ordinal)) {
                throw "保护 PID $processId 身份变化：$field 不匹配。"
            }
        }
        if ([long]$process.ParentProcessId -ne [long]$expected.ParentProcessId) {
            throw "保护 PID $processId 身份变化：ParentProcessId 不匹配。"
        }
        if ([string]::IsNullOrWhiteSpace([string]$process.CreationDateUtc)) {
            throw "保护 PID $processId 缺少进程创建时间，无法排除 PID 重用。"
        }
        if (-not [string]::Equals([string]$process.CreationDateUtc,
                [string]$expected.CreationDateUtc, [System.StringComparison]::Ordinal)) {
            throw "保护 PID $processId 创建时间与可信身份绑定不匹配；检测到 PID 重用或身份变化。"
        }
        if (-not $InitialSnapshot) {
            if (-not $baselineByPid.ContainsKey($processId)) {
                throw "保护 PID $processId 在启动快照中不存在，当前出现视为 PID 重用或新进程。"
            }
            $baseline = $baselineByPid[$processId]
            if (-not [string]::Equals([string]$process.CreationDateUtc,
                    [string]$baseline.CreationDateUtc, [System.StringComparison]::Ordinal)) {
                throw "保护 PID $processId 创建时间变化，检测到 PID 重用。"
            }
        }
    }
    return [pscustomobject]@{
        captured_at_utc8 = [DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss.fff zzz')
        process_count = @($Processes).Count
        processes = @($Processes)
        protected_process_ids_present = @($Processes | ForEach-Object { [long]$_.ProcessId })
    }
}

function Invoke-T63GuardedStage {
    param(
        [Parameter(Mandatory = $true)][string]$Phase,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$Processes,
        [Parameter(Mandatory = $true)][object[]]$ProtectedIdentities,
        [AllowEmptyCollection()][object[]]$BaselineProcesses = @(),
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][System.Collections.Generic.List[object]]$ProcessSnapshots,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )
    $checkedSnapshot = Assert-T63XilinxProcessSnapshot `
        -Processes $Processes `
        -ProtectedIdentities $ProtectedIdentities `
        -BaselineProcesses $BaselineProcesses
    $checkedSnapshot | Add-Member -MemberType NoteProperty -Name phase -Value $Phase
    $ProcessSnapshots.Add($checkedSnapshot)
    & $Action | Out-Null
}

function Get-T63ResourceSnapshot {
    param([Parameter(Mandatory = $true)][string]$Phase)
    $freeRamMb = [math]::Floor((Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction Stop).FreePhysicalMemory / 1024)
    $dDrive = Get-PSDrive -Name D -ErrorAction Stop
    if (-not [string]::Equals([string]$dDrive.Root, 'D:\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "D: 空间查询返回的卷根不正确：$($dDrive.Root)"
    }
    $freeDiskMb = [math]::Floor($dDrive.Free / 1MB)
    if ($freeRamMb -lt 2048 -or $freeDiskMb -lt 2048) {
        throw ("资源保护门限未满足（{0}）：可用 RAM={1}MB、D 盘={2}MB；未启动或继续仿真。" -f $Phase, $freeRamMb, $freeDiskMb)
    }
    return [pscustomobject]@{
        phase = $Phase
        captured_at_utc8 = [DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss.fff zzz')
        free_ram_mb = $freeRamMb
        free_d_drive_mb = $freeDiskMb
        minimum_free_ram_mb = 2048
        minimum_free_d_drive_mb = 2048
    }
}

if ($RunSimulation) {
    $env:XILINX_VIVADO = 'D:\Xilinx\2026.1\Vivado'
    $vivadoRoot = Get-NormalizedFullPath -Path $env:XILINX_VIVADO
    if (-not $vivadoRoot.StartsWith('D:\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Vivado 安装路径不在 D 盘：$vivadoRoot"
    }
    Assert-NoReparsePathChain -Path $vivadoRoot
    if (-not (Test-Path -LiteralPath $vivadoRoot -PathType Container)) {
        throw "固定 Vivado 安装目录不存在：$vivadoRoot"
    }
    $protectedIdentities = @(Get-T63ProtectedProcessAllowlist)
    $initialProcessList = @(Get-T63XilinxProcessSnapshot)
    $initialProcessSnapshot = Assert-T63XilinxProcessSnapshot `
        -Processes $initialProcessList `
        -ProtectedIdentities $protectedIdentities `
        -InitialSnapshot
    $initialProcessSnapshot | Add-Member -MemberType NoteProperty -Name phase -Value 'before_offline_validation'
    $processSnapshots.Add($initialProcessSnapshot)
    $baselineProcesses = $initialProcessList
    $resourceSnapshots.Add((Get-T63ResourceSnapshot -Phase 'before_offline_validation'))
}

$python = Get-Command py.exe -ErrorAction Stop
Invoke-LoggedNative -StageName 'offline_validate' -Executable $python.Source -Arguments @('-3', '-B', $pythonVerifier, '--validate') -ConsoleLogPath (Join-Path $workRoot 'validate.console.log') -ExecutionLog $executionLog | Out-Null
Invoke-LoggedNative -StageName 'offline_tests' -Executable $python.Source -Arguments @('-3', '-B', $offlineTests) -ConsoleLogPath (Join-Path $workRoot 'offline_tests.console.log') -ExecutionLog $executionLog | Out-Null

if (-not $RunSimulation) {
    Write-Output "离线 fixture 校验与测试完成；未运行 Vivado/XVLOG/XELAB/XSim。日志：$workRoot"
    exit 0
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
    $resourceSnapshots.Add((Get-T63ResourceSnapshot -Phase 'immediately_before_xvlog'))
    $processList = @(Get-T63XilinxProcessSnapshot)
    $beforeXvlog = Assert-T63XilinxProcessSnapshot -Processes $processList -ProtectedIdentities $protectedIdentities -BaselineProcesses $baselineProcesses
    $beforeXvlog | Add-Member -MemberType NoteProperty -Name phase -Value 'before_xvlog'
    $processSnapshots.Add($beforeXvlog)
    $baselineProcesses = $processList

    Invoke-LoggedNative -StageName 'xvlog' -Executable $xvlog -Arguments @('-sv', '-work', 'work', $packagePath, $expectedTb) -ConsoleLogPath (Join-Path $workRoot 'xvlog.console.log') -NativeLogPath (Join-Path $workRoot 'xvlog.log') -ExecutionLog $executionLog | Out-Null
    $processList = @(Get-T63XilinxProcessSnapshot)
    $afterXvlog = Assert-T63XilinxProcessSnapshot -Processes $processList -ProtectedIdentities $protectedIdentities -BaselineProcesses $baselineProcesses
    $afterXvlog | Add-Member -MemberType NoteProperty -Name phase -Value 'after_xvlog'
    $processSnapshots.Add($afterXvlog)
    $baselineProcesses = $processList

    $resourceSnapshots.Add((Get-T63ResourceSnapshot -Phase 'immediately_before_xelab'))
    $processList = @(Get-T63XilinxProcessSnapshot)
    Invoke-T63GuardedStage -Phase 'immediately_before_xelab' `
        -Processes $processList `
        -ProtectedIdentities $protectedIdentities `
        -BaselineProcesses $baselineProcesses `
        -ProcessSnapshots $processSnapshots `
        -Action {
            Invoke-LoggedNative -StageName 'xelab' -Executable $xelab -Arguments @('work.tb_s2a_t63_descriptor_rom_dynamic', '-s', $snapshot) -ConsoleLogPath (Join-Path $workRoot 'xelab.console.log') -NativeLogPath (Join-Path $workRoot 'xelab.log') -ExecutionLog $executionLog | Out-Null
        }
    $baselineProcesses = $processList
    $processList = @(Get-T63XilinxProcessSnapshot)
    $afterXelab = Assert-T63XilinxProcessSnapshot -Processes $processList -ProtectedIdentities $protectedIdentities -BaselineProcesses $baselineProcesses
    $afterXelab | Add-Member -MemberType NoteProperty -Name phase -Value 'after_xelab'
    $processSnapshots.Add($afterXelab)
    $baselineProcesses = $processList

    $resourceSnapshots.Add((Get-T63ResourceSnapshot -Phase 'immediately_before_xsim'))
    $processList = @(Get-T63XilinxProcessSnapshot)
    $beforeXsim = Assert-T63XilinxProcessSnapshot -Processes $processList -ProtectedIdentities $protectedIdentities -BaselineProcesses $baselineProcesses
    $beforeXsim | Add-Member -MemberType NoteProperty -Name phase -Value 'immediately_before_xsim'
    $processSnapshots.Add($beforeXsim)
    $baselineProcesses = $processList

    Invoke-LoggedNative -StageName 'xsim' -Executable $xsim -Arguments @(
        $snapshot,
        '-runall',
        '-testplusarg', "LAYER_FIXTURE=$forwardLayerFixture",
        '-testplusarg', "CHANNEL_FIXTURE=$forwardChannelFixture"
    ) -ConsoleLogPath (Join-Path $workRoot 'xsim.console.log') -NativeLogPath (Join-Path $workRoot 'xsim.log') -ExecutionLog $executionLog | Out-Null
    $processList = @(Get-T63XilinxProcessSnapshot)
    $afterXsim = Assert-T63XilinxProcessSnapshot -Processes $processList -ProtectedIdentities $protectedIdentities -BaselineProcesses $baselineProcesses
    $afterXsim | Add-Member -MemberType NoteProperty -Name phase -Value 'after_xsim'
    $processSnapshots.Add($afterXsim)
    $baselineProcesses = $processList
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
    fixture_binding_sha256 = Get-T63FileSha256 -Path $fixtureManifest -AllowedRoot $taskRoot
    xsim_log_sha256 = Get-T63FileSha256 -Path $xsimLogPath -AllowedRoot $workRoot
    xsim_pid_after_exit = @($afterXsim.processes | Where-Object { $_.Name -in @('xsim.exe', 'xsimk.exe') } | ForEach-Object { $_.ProcessId })
    process_snapshots = @($processSnapshots)
    resource_snapshots = @($resourceSnapshots)
    execution = @($executionLog)
}
$resultPath = Join-Path $workRoot 'simulation_result.json'
Write-NewUtf8Text -Path $resultPath -Text (($result | ConvertTo-Json -Depth 8) + [Environment]::NewLine) -AllowedRoot $workRoot
Write-Output "动态 ROM 仿真通过；日志与结果：$workRoot"
