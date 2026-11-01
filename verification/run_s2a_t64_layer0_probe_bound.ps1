[CmdletBinding()]
param(
    [switch]$PreflightOnly,
    [string]$ProcessFixturePath
)

$ErrorActionPreference = 'Stop'

$ProjectRoot = 'D:\FPGA_Competition'
$RunnerPath = 'D:\FPGA_Competition\verification\run_s2a_t64_layer0_probe_bound.ps1'
$ReferenceCommandPath = 'D:\FPGA_Competition\report\evidence\S2A-T64\sim_run11\run_layer0_probe.cmd'
$RunDirectory = 'D:\FPGA_Competition\report\evidence\S2A-T64\sim_run12'
$VivadoBin = 'D:\Xilinx\2026.1\Vivado\bin'
$VivadoExeDir = 'D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o'
$VivadoRoot = 'D:\Xilinx\2026.1\Vivado'
$VivadoRelease = '2026.1'
$XvlogPath = Join-Path $VivadoBin 'xvlog.bat'
$XelabPath = Join-Path $VivadoBin 'xelab.bat'
$XsimPath = Join-Path $VivadoBin 'xsim.bat'
$ToolBinaryPaths = @{
    xvlog = Join-Path $VivadoExeDir 'xvlog.exe'
    xelab = Join-Path $VivadoExeDir 'xelab.exe'
    xsim = Join-Path $VivadoExeDir 'xsim.exe'
}
$ExpectedRelativeSources = @(
    'src\s2a_network_descriptor_pkg.sv',
    'src\int8_conv_tap_geometry.sv',
    'src\int8_conv_weight_address.sv',
    'src\int8_mac_accumulator.sv',
    'src\int8_maxpool_geometry.sv',
    'src\int8_maxpool_window.sv',
    'src\int8_route_query.sv',
    'src\int8_upsample_query.sv',
    'src\s2a_conv_engine.sv',
    'src\s2a_maxpool_engine.sv',
    'src\s2a_route_engine.sv',
    'src\s2a_upsample_engine.sv',
    'src\s2a_control_csr.sv',
    'src\s2a_network_backend.sv',
    'sim\tb_s2a_network_backend_layer0_probe.sv'
)
$ProtectedProcessNames = @('vivado.exe', 'xsim.exe', 'xsimk.exe', 'xvlog.exe', 'xelab.exe')
$ToolFailureCodes = @{ xvlog = 91; xelab = 92; xsim = 93 }
$ResourceMinimums = @{
    free_physical_memory_mib = 2048
    d_free_space_gib = 2
}
$ProtectedProcessSpecifications = @(
    [pscustomobject]@{
        process_id = 8712
        parent_process_id = 10724
        name = 'vivado.exe'
        executable_path = 'D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\vivado.exe'
        command_line = '"D:/Xilinx/2026.1/Vivado/bin/unwrapped/win64.o/vivado.exe"   -mode tcl -source D:\FPGA_Competition\report\evidence\S2A-T60\run06\mcp_server_instance\start_mcp.tcl'
        creation_date_utc = '2026-09-29T18:07:06.1577890Z'
        executable_sha256 = '3a4e9e3f03d20cd1994dc2eff44566af7a10eaaae04429e9d460bffe3b0e86e4'
    },
    [pscustomobject]@{
        process_id = 22488
        parent_process_id = 8712
        name = 'xsimk.exe'
        executable_path = 'D:\FPGA_Competition\report\evidence\S2A-T60\run06\isolated_project\s2a_t60_run06.sim\sim_1\behav\xsim\xsim.dir\tb_s2a_conv_layer35_row24_all_channels_behav\xsimk.exe'
        command_line = 'xsim.dir/tb_s2a_conv_layer35_row24_all_channels_behav/xsimk.exe -simmode gui -wdb tb_s2a_conv_layer35_row24_all_channels_behav.wdb -simrunnum 0 -socket 8295'
        creation_date_utc = '2026-09-29T18:13:11.5972630Z'
        executable_sha256 = 'dd50783b44e1e44d89cc61080f376515db8e618a6fd96425048f26960242d0b0'
    },
    [pscustomobject]@{
        process_id = 13156
        parent_process_id = 8712
        name = 'xsimk.exe'
        executable_path = 'D:\FPGA_Competition\report\evidence\S2A-T61\run04\isolated_project\s2a_t61_run04.sim\sim_1\behav\xsim\xsim.dir\tb_s2a_conv_layer35_row25_all_channels_behav\xsimk.exe'
        command_line = 'xsim.dir/tb_s2a_conv_layer35_row25_all_channels_behav/xsimk.exe -simmode gui -wdb tb_s2a_conv_layer35_row25_all_channels_behav.wdb -simrunnum 0 -socket 12375'
        creation_date_utc = '2026-09-29T19:39:52.1132030Z'
        executable_sha256 = '5107d47f770b4c4d19c8dbf4a8066b6792cf73e844c4cb61274691faf8293905'
    }
)
$SnapshotName = 's2a_t64_layer0_snapshot'
$MutableSnapshotRelativePaths = @(
    'xsim.dir\s2a_t64_layer0_snapshot\xsim.mem',
    'xsim.dir\s2a_t64_layer0_snapshot\xsimkernel.log',
    'xsim.dir\s2a_t64_layer0_snapshot\xsimcrash.log'
)
$script:FailureExitCode = 1
$script:FailureMessage = $null
$script:PhaseResults = [ordered]@{}
$script:SourceBindings = @()
$script:ProtectedBefore = @()
$script:RunDirectoryCreated = $false
$script:ManifestWritten = $false
$script:RunManifest = $null
$script:ToolPlan = @()
$script:ReferenceBinding = $null
$script:RunnerHash = $null
$script:GitHead = $null
$script:PassLines = @()
$script:ProtectedAfter = @()
$script:ToolBinaryBindings = @()
$script:ResourceSnapshots = @()
$script:CompileArtifactBinding = $null
$script:CompileArtifactPreXsimCheck = $null
$script:CompileArtifactAfterXsim = $null
$script:ProcessFixture = $null
$script:XsimRuntimeProcesses = @()
$script:ToolVersions = [ordered]@{}
$script:XilinxLocalUserData = $null

function Get-Sha256Hex {
    param([Parameter(Mandatory = $true)][string]$Path)
    $stream = [System.IO.File]::OpenRead($Path)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $digest = $sha.ComputeHash($stream)
        return ([System.BitConverter]::ToString($digest).Replace('-', '').ToLowerInvariant())
    } finally {
        $sha.Dispose()
        $stream.Dispose()
    }
}

function Get-FileBinding {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ExpectedPath
    )
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.PSIsContainer) {
        throw "Expected a file at the exact path: $ExpectedPath"
    }
    if ($item.FullName -cne $ExpectedPath) {
        throw "Resolved path mismatch: expected $ExpectedPath; got $($item.FullName)"
    }
    $digest = Get-Sha256Hex -Path $item.FullName
    [pscustomobject]@{
        path = $item.FullName
        sha256 = $digest
        length_bytes = [int64]$item.Length
    }
}

function Get-ProcessInventory {
    return @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop |
        Select-Object ProcessId, ParentProcessId, Name, ExecutablePath, CommandLine, CreationDate)
}

function Convert-CreationDateToUtcString {
    param([Parameter(Mandatory = $true)][object]$Value)
    if ($Value -is [string]) {
        $parsed = [DateTimeOffset]::Parse(
            $Value,
            [Globalization.CultureInfo]::InvariantCulture,
            [Globalization.DateTimeStyles]::RoundtripKind)
        return $parsed.UtcDateTime.ToString('o', [Globalization.CultureInfo]::InvariantCulture)
    }
    $parsedDate = ([DateTime]$Value).ToUniversalTime()
    return $parsedDate.ToString('o', [Globalization.CultureInfo]::InvariantCulture)
}

function Get-ObservedXilinxProcesses {
    if ($null -ne $script:ProcessFixture) {
        return @($script:ProcessFixture)
    }
    $items = @(Get-ProcessInventory | Where-Object {
        $ProtectedProcessNames -ccontains ([string]$_.Name).ToLowerInvariant()
    } | Sort-Object -Property ProcessId)
    $snapshot = @()
    foreach ($item in $items) {
        $path = [string]$item.ExecutablePath
        if ([string]::IsNullOrWhiteSpace($path) -or -not (Test-Path -LiteralPath $path -PathType Leaf)) {
            $script:FailureExitCode = 96
            throw "无法只读核验 Xilinx 进程 PID=$($item.ProcessId) 的映像路径。"
        }
        $snapshot += [pscustomobject]@{
            process_id = [int]$item.ProcessId
            parent_process_id = [int]$item.ParentProcessId
            name = ([string]$item.Name).ToLowerInvariant()
            executable_path = $path
            command_line = [string]$item.CommandLine
            creation_date_utc = Convert-CreationDateToUtcString -Value $item.CreationDate
            executable_sha256 = Get-Sha256Hex -Path $path
        }
    }
    return $snapshot
}

function Get-ProtectedProcessSpecification {
    param([int]$ProcessId)
    return @($ProtectedProcessSpecifications | Where-Object { $_.process_id -eq $ProcessId } | Select-Object -First 1)[0]
}

function Assert-ProtectedIdentity {
    param([Parameter(Mandatory = $true)][object]$Process)
    $expected = Get-ProtectedProcessSpecification -ProcessId ([int]$Process.process_id)
    if ($null -eq $expected) {
        $script:FailureExitCode = 96
        throw "发现未授权的 Vivado/XSim/XVLOG/XELAB 进程：$($Process.name) PID=$($Process.process_id)。"
    }
    $matches = ([int]$Process.parent_process_id -eq [int]$expected.parent_process_id) -and
        ([string]$Process.name -ceq [string]$expected.name) -and
        ([string]$Process.executable_path -ceq [string]$expected.executable_path) -and
        ([string]$Process.command_line -ceq [string]$expected.command_line) -and
        ([string]$Process.executable_sha256 -ceq [string]$expected.executable_sha256)
    try {
        $actualCreation = [DateTimeOffset]::Parse(
            (Convert-CreationDateToUtcString -Value $Process.creation_date_utc),
            [Globalization.CultureInfo]::InvariantCulture,
            [Globalization.DateTimeStyles]::RoundtripKind).UtcDateTime.Ticks
        $expectedCreation = [DateTimeOffset]::Parse(
            [string]$expected.creation_date_utc,
            [Globalization.CultureInfo]::InvariantCulture,
            [Globalization.DateTimeStyles]::RoundtripKind).UtcDateTime.Ticks
        $matches = $matches -and ($actualCreation -eq $expectedCreation)
    } catch {
        $matches = $false
    }
    if (-not $matches) {
        $script:FailureExitCode = 96
        throw "受保护 PID=$($Process.process_id) 的创建时间/父 PID/路径/命令行/映像哈希与固定身份不符，按 PID 重用或身份变化拒绝启动。"
    }
}

function Assert-NoUnexpectedXilinxProcesses {
    param(
        [Parameter(Mandatory = $true)][string]$StageName,
        [object[]]$Processes = @()
    )
    if ($Processes.Count -eq 0) {
        $Processes = @(Get-ObservedXilinxProcesses)
    }
    foreach ($process in $Processes) {
        Assert-ProtectedIdentity -Process $process
    }
    return @($Processes)
}

function Get-ProcessSetKey {
    param([object[]]$Processes)
    return (@($Processes | ForEach-Object {
        '{0}|{1}|{2}|{3}' -f $_.process_id, $_.creation_date_utc, $_.executable_path, $_.executable_sha256
    } | Sort-Object) -join ';')
}

function Get-ProcessSummary {
    param([object[]]$Processes)
    if ($Processes.Count -eq 0) {
        return 'none'
    }
    return (@($Processes | ForEach-Object { '{0}#{1}' -f $_.name, $_.process_id }) -join ',')
}

function Get-ResourceSnapshot {
    $operatingSystem = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction Stop
    $drive = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='D:'" -ErrorAction Stop
    if ($null -eq $drive -or $null -eq $operatingSystem) {
        throw '无法读取 D: 可用空间或物理内存；资源门限失败关闭。'
    }
    $freeMemoryMiB = [math]::Floor(([double]$operatingSystem.FreePhysicalMemory * 1KB) / 1MB)
    $freeDriveGiB = [math]::Floor(([double]$drive.FreeSpace) / 1GB)
    $snapshot = [pscustomobject]@{
        captured_utc = [DateTime]::UtcNow.ToString('o')
        free_physical_memory_mib = [int64]$freeMemoryMiB
        d_free_space_gib = [int64]$freeDriveGiB
        thresholds = $ResourceMinimums
        passed = ($freeMemoryMiB -ge $ResourceMinimums.free_physical_memory_mib) -and
            ($freeDriveGiB -ge $ResourceMinimums.d_free_space_gib)
    }
    $script:ResourceSnapshots += $snapshot
    if (-not $snapshot.passed) {
        $script:FailureExitCode = 99
        throw "资源门限失败：Free RAM=$freeMemoryMiB MiB，D: free=$freeDriveGiB GiB。"
    }
    return $snapshot
}

function Get-ToolBinaryBindings {
    $bindings = @()
    foreach ($name in @('xvlog', 'xelab', 'xsim')) {
        $path = [string]$ToolBinaryPaths[$name]
        $bindings += [pscustomobject]@{
            name = $name
            release = $VivadoRelease
            installation_root = $VivadoRoot
            binary = Get-FileBinding -Path $path -ExpectedPath $path
        }
    }
    return $bindings
}

function Assert-ToolBinariesUnchanged {
    param([string]$StageName)
    foreach ($before in $script:ToolBinaryBindings) {
        $path = [string]$before.binary.path
        $after = Get-FileBinding -Path $path -ExpectedPath $path
        if ($after.sha256 -cne $before.binary.sha256 -or
            $after.length_bytes -ne $before.binary.length_bytes) {
            $script:FailureExitCode = 96
            throw "Vivado 2026.1 tool binary changed before/after ${StageName}: $path"
        }
    }
}

function Get-RelativeRunPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    $resolvedRun = (Resolve-Path -LiteralPath $RunDirectory).Path.TrimEnd('\')
    $resolvedPath = (Resolve-Path -LiteralPath $Path).Path
    if (-not $resolvedPath.StartsWith($resolvedRun + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Generated artifact is outside the D: run directory: $resolvedPath"
    }
    return $resolvedPath.Substring($resolvedRun.Length + 1).Replace('/', '\')
}

function Get-CompileArtifactBinding {
    $snapshotDirectory = Join-Path $RunDirectory ("xsim.dir\" + $SnapshotName)
    if (-not (Test-Path -LiteralPath $snapshotDirectory -PathType Container)) {
        throw "Elaborated snapshot directory is missing: $snapshotDirectory"
    }
    $requiredRelativePaths = @(
        "xsim.dir\$SnapshotName\xsimk.exe",
        "xsim.dir\$SnapshotName\Compile_Options.txt",
        "xsim.dir\$SnapshotName\xsim.version",
        "xsim.dir\$SnapshotName\xsim.mem"
    )
    foreach ($relativePath in $requiredRelativePaths) {
        $requiredPath = Join-Path $RunDirectory $relativePath
        if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
            throw "Required elaboration artifact is missing: $relativePath"
        }
    }
    $versionFile = Join-Path $RunDirectory "xsim.dir\$SnapshotName\xsim.version"
    $versionText = (Get-Content -LiteralPath $versionFile -Raw -Encoding UTF8).Trim()
    if ($versionText -cne $VivadoRelease) {
        throw "Snapshot release mismatch: expected $VivadoRelease; got $versionText"
    }
    $allFiles = @(Get-ChildItem -LiteralPath (Join-Path $RunDirectory 'xsim.dir') -Recurse -File -Force)
    if ($allFiles.Count -eq 0) {
        throw 'xsim.dir contains no elaboration artifacts.'
    }
    $staticFiles = @()
    $mutableFiles = @()
    foreach ($file in $allFiles) {
        if (($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "Reparse-point artifact is not allowed in xsim.dir: $($file.FullName)"
        }
        $relativePath = Get-RelativeRunPath -Path $file.FullName
        $binding = [pscustomobject]@{
            relative_path = $relativePath
            length_bytes = [int64]$file.Length
            sha256 = Get-Sha256Hex -Path $file.FullName
        }
        if ($MutableSnapshotRelativePaths -ccontains $relativePath) {
            $mutableFiles += $binding
        } else {
            $staticFiles += $binding
        }
    }
    $snapshotExecutable = @($staticFiles | Where-Object {
        $_.relative_path -ceq "xsim.dir\$SnapshotName\xsimk.exe"
    })
    $compileOptions = @($staticFiles | Where-Object {
        $_.relative_path -ceq "xsim.dir\$SnapshotName\Compile_Options.txt"
    })
    $sdbFiles = @($staticFiles | Where-Object { $_.relative_path -match '\.sdb$' })
    if ($snapshotExecutable.Count -ne 1 -or $compileOptions.Count -ne 1 -or $sdbFiles.Count -eq 0) {
        throw "Static snapshot binding incomplete: xsimk=$($snapshotExecutable.Count), options=$($compileOptions.Count), sdb=$($sdbFiles.Count)."
    }
    $mutableByName = @{}
    foreach ($relativePath in $MutableSnapshotRelativePaths) {
        $match = @($mutableFiles | Where-Object { $_.relative_path -ceq $relativePath })
        if ($match.Count -gt 0) {
            $mutableByName[$relativePath] = $match[0]
        }
    }
    if (-not $mutableByName.ContainsKey("xsim.dir\$SnapshotName\xsim.mem")) {
        throw 'The pre-xsim xsim.mem binding is missing.'
    }
    return [pscustomobject]@{
        captured_utc = [DateTime]::UtcNow.ToString('o')
        snapshot_name = $SnapshotName
        snapshot_directory = "xsim.dir\$SnapshotName"
        snapshot_executable = $snapshotExecutable[0]
        compile_options = $compileOptions[0]
        sdb_file_count = $sdbFiles.Count
        static_files = @($staticFiles | Sort-Object -Property relative_path)
        mutable_files = @($mutableFiles | Sort-Object -Property relative_path)
        mutable_file_policy = 'xsim.mem、xsimkernel.log、xsimcrash.log 属于工具运行期可变文件；不纳入静态锁，保存运行前后长度和 SHA256。'
        snapshot_release = $versionText
    }
}

function Compare-StaticCompileArtifacts {
    param(
        [Parameter(Mandatory = $true)][object]$Before,
        [Parameter(Mandatory = $true)][object]$After
    )
    $beforeFiles = @($Before.static_files | Sort-Object -Property relative_path)
    $afterFiles = @($After.static_files | Sort-Object -Property relative_path)
    if ($beforeFiles.Count -ne $afterFiles.Count) {
        return [pscustomobject]@{ passed = $false; reason = 'static file count changed'; changed_paths = @() }
    }
    $changed = @()
    for ($index = 0; $index -lt $beforeFiles.Count; $index++) {
        if ($beforeFiles[$index].relative_path -cne $afterFiles[$index].relative_path -or
            $beforeFiles[$index].length_bytes -ne $afterFiles[$index].length_bytes -or
            $beforeFiles[$index].sha256 -cne $afterFiles[$index].sha256) {
            $changed += [string]$beforeFiles[$index].relative_path
            if ($afterFiles[$index].relative_path -cne $beforeFiles[$index].relative_path) {
                $changed += [string]$afterFiles[$index].relative_path
            }
        }
    }
    return [pscustomobject]@{
        passed = ($changed.Count -eq 0)
        reason = if ($changed.Count -eq 0) { $null } else { 'static compile artifact path/length/hash changed' }
        changed_paths = @($changed | Sort-Object -Unique)
    }
}

function Get-ToolReportedVersion {
    param([Parameter(Mandatory = $true)][string]$Name)
    if ($Name -eq 'xvlog') {
        return [pscustomobject]@{
            name = 'xvlog'
            release = $VivadoRelease
            reported_in_log = $false
            evidence = '2026.1 安装根路径、实际 xvlog.exe 路径与 SHA256 已绑定；xvlog 日志不含版本 banner。'
        }
    }
    if ($Name -eq 'xelab') {
        $log = Join-Path $RunDirectory 'xelab.log'
        $matches = @(Select-String -LiteralPath $log -Pattern '^Vivado Simulator v(?<version>[0-9.]+)$' -AllMatches)
        if ($matches.Count -ne 1 -or $matches[0].Matches[0].Groups['version'].Value -cne $VivadoRelease) {
            throw 'xelab log did not report the expected single Vivado Simulator 2026.1 banner.'
        }
        return [pscustomobject]@{ name = 'xelab'; release = $matches[0].Matches[0].Groups['version'].Value; reported_in_log = $true }
    }
    if ($Name -eq 'xsim') {
        $consoleLog = Join-Path $RunDirectory 'xsim_console.txt'
        $matches = @(Select-String -LiteralPath $consoleLog -Pattern '^\s*\*{0,6}\s*xsim v(?<version>[0-9.]+) \(64-bit\)$' -AllMatches)
        if ($matches.Count -ne 1 -or $matches[0].Matches[0].Groups['version'].Value -cne $VivadoRelease) {
            throw 'xsim console did not report the expected single xsim 2026.1 banner.'
        }
        return [pscustomobject]@{ name = 'xsim'; release = $matches[0].Matches[0].Groups['version'].Value; reported_in_log = $true }
    }
    throw "Unknown tool-version key: $Name"
}

function Normalize-ProcessToken {
    param([string]$Value)
    return $Value.Trim('"').Replace('/', '\').ToLowerInvariant()
}

function Get-CommandTokens {
    param([string]$CommandLine)
    $tokens = @()
    foreach ($match in [regex]::Matches($CommandLine, '"(?<quoted>[^"]*)"|(?<plain>\S+)')) {
        if ($match.Groups['quoted'].Success) {
            $tokens += $match.Groups['quoted'].Value
        } else {
            $tokens += $match.Groups['plain'].Value
        }
    }
    return $tokens
}

function Test-DescendsFromLauncher {
    param(
        [Parameter(Mandatory = $true)][object]$Process,
        [Parameter(Mandatory = $true)][object[]]$Inventory,
        [Parameter(Mandatory = $true)][int]$LauncherProcessId
    )
    $parentId = [int]$Process.ParentProcessId
    $visited = @{}
    for ($depth = 0; $depth -lt 16; $depth++) {
        if ($parentId -eq $LauncherProcessId) {
            return $true
        }
        if ($parentId -le 0 -or $visited.ContainsKey($parentId)) {
            return $false
        }
        $visited[$parentId] = $true
        $parent = @($Inventory | Where-Object { [int]$_.ProcessId -eq $parentId } | Select-Object -First 1)
        if ($parent.Count -ne 1) {
            return $false
        }
        $parentId = [int]$parent[0].ParentProcessId
    }
    return $false
}

function Convert-ProcessToIdentity {
    param([Parameter(Mandatory = $true)][object]$Process)
    $path = [string]$Process.ExecutablePath
    if ([string]::IsNullOrWhiteSpace($path) -or -not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Runner-owned Xilinx process has no readable image path: PID=$($Process.ProcessId)"
    }
    [pscustomobject]@{
        process_id = [int]$Process.ProcessId
        parent_process_id = [int]$Process.ParentProcessId
        name = ([string]$Process.Name).ToLowerInvariant()
        executable_path = $path
        command_line = [string]$Process.CommandLine
        creation_date_utc = Convert-CreationDateToUtcString -Value $Process.CreationDate
        executable_sha256 = Get-Sha256Hex -Path $path
    }
}

function Assert-CommandMatchesToolPlan {
    param(
        [Parameter(Mandatory = $true)][object]$Process,
        [Parameter(Mandatory = $true)][object]$Tool
    )
    $expectedTokens = @([string]$ToolBinaryPaths[$Tool.name]) + @($Tool.arguments)
    $actualTokens = @(Get-CommandTokens -CommandLine ([string]$Process.CommandLine))
    if ($actualTokens.Count -ne $expectedTokens.Count) {
        throw "$($Tool.name) process argv count differs from the frozen run plan."
    }
    for ($index = 0; $index -lt $expectedTokens.Count; $index++) {
        if ((Normalize-ProcessToken $actualTokens[$index]) -cne
            (Normalize-ProcessToken ([string]$expectedTokens[$index]))) {
            throw "$($Tool.name) process argv differs from the frozen run plan at token $index."
        }
    }
}

function Assert-RunnerOwnedProcessPolicy {
    param(
        [Parameter(Mandatory = $true)][string]$StageName,
        [Parameter(Mandatory = $true)][int]$LauncherProcessId,
        [Parameter(Mandatory = $true)][string]$LaunchCommand,
        [Parameter(Mandatory = $true)][object]$Tool
    )
    $inventory = @(Get-ProcessInventory)
    $launcher = @($inventory | Where-Object { [int]$_.ProcessId -eq $LauncherProcessId } | Select-Object -First 1)
    if ($launcher.Count -ne 1) {
        throw "Runner command shell PID=$LauncherProcessId is not visible in the process inventory."
    }
    if ([string]$launcher[0].Name -ine 'cmd.exe' -or
        [string]$launcher[0].ExecutablePath -ine [string]$env:ComSpec -or
        [int]$launcher[0].ParentProcessId -ne $PID -or
        -not ([string]$launcher[0].CommandLine).Contains($LaunchCommand)) {
        throw "Runner command shell PID=$LauncherProcessId parent/path/command does not match the launch binding."
    }
    $observedOwned = @()
    $expectedProcessName = "$($Tool.name).exe"
    foreach ($item in $inventory | Where-Object {
        $ProtectedProcessNames -ccontains ([string]$_.Name).ToLowerInvariant()
    }) {
        $identity = Convert-ProcessToIdentity -Process $item
        $protected = Get-ProtectedProcessSpecification -ProcessId $identity.process_id
        if ($null -ne $protected) {
            Assert-ProtectedIdentity -Process $identity
            continue
        }
        if (-not (Test-DescendsFromLauncher -Process $item -Inventory $inventory -LauncherProcessId $LauncherProcessId)) {
            throw "发现不属于 runner 的 Xilinx 进程：$($identity.name) PID=$($identity.process_id)。"
        }
        if ($identity.name -ceq 'xsimk.exe') {
            if ($StageName -cne 'xsim') {
                throw "xsimk.exe is not permitted during $StageName."
            }
            $expectedSnapshotPath = Join-Path $RunDirectory "xsim.dir\$SnapshotName\xsimk.exe"
            if ($identity.executable_path -cne $expectedSnapshotPath -or
                $identity.executable_sha256 -cne $script:CompileArtifactBinding.snapshot_executable.sha256) {
                throw 'Runner-owned xsimk.exe path or SHA256 differs from the elaborated snapshot lock.'
            }
            $normalizedCommand = Normalize-ProcessToken ([string]$identity.command_line)
            $expectedPrefix = 'xsim.dir\' + $SnapshotName + '\xsimk.exe'
            if (-not $normalizedCommand.StartsWith($expectedPrefix, [System.StringComparison]::OrdinalIgnoreCase) -or
                $normalizedCommand -notmatch '\s-simmode\s+batch(?:\s|$)' -or
                $normalizedCommand -match '(?:^|\s)\+|\-testplusarg|\-simmode\s+gui') {
                throw 'Runner-owned xsimk.exe command is not bound to the batch snapshot invocation.'
            }
        } else {
            if ($identity.name -cne $expectedProcessName -or
                $identity.executable_path -cne [string]$ToolBinaryPaths[$Tool.name]) {
                throw "Unexpected runner-owned Xilinx process during ${StageName}: $($identity.name) $($identity.executable_path)"
            }
            $expectedBinary = @($script:ToolBinaryBindings | Where-Object { $_.name -ceq $Tool.name })[0]
            if ($identity.executable_sha256 -cne $expectedBinary.binary.sha256) {
                throw "Runner-owned $($Tool.name).exe SHA256 differs from the preflight tool binary."
            }
            Assert-CommandMatchesToolPlan -Process $item -Tool $Tool
        }
        $observedOwned += $identity
    }
    return [pscustomobject]@{
        captured_utc = [DateTime]::UtcNow.ToString('o')
        stage = $StageName
        launcher_process_id = $LauncherProcessId
        runner_owned_xilinx_processes = @($observedOwned)
    }
}

function Update-RunManifest {
    param([string]$Status = 'RUNNING')
    if ($script:RunManifest) {
        $script:RunManifest.status = $Status
        $script:RunManifest.phase_results = $script:PhaseResults
        $script:RunManifest.resource_snapshots = @($script:ResourceSnapshots)
        $script:RunManifest.tool_versions = $script:ToolVersions
        $script:RunManifest.compile_artifacts_before_xsim = $script:CompileArtifactBinding
        $script:RunManifest.compile_artifacts_reverified_before_xsim = $script:CompileArtifactPreXsimCheck
        $script:RunManifest.compile_artifacts_after_xsim = $script:CompileArtifactAfterXsim
        $script:RunManifest.xsim_runtime_processes = @($script:XsimRuntimeProcesses)
        $script:RunManifest.protected_processes_after = @($script:ProtectedAfter)
        $script:RunManifest.failure = $script:FailureMessage
        $script:RunManifest.run_scope = '仅绑定本次新建的 S2A-T64 sim_run12；不回填 sim_run10 或 sim_run11。'
        Write-JsonFile -Path (Join-Path $RunDirectory 'run_manifest.json') -Value $script:RunManifest
    }
}

function Get-DRunDirectories {
    return [ordered]@{
        temporary_directory = Join-Path $RunDirectory 'temp'
        xilinx_local_user_data = Join-Path $RunDirectory 'xilinx_local_user_data'
        home = Join-Path $RunDirectory 'home'
        appdata = Join-Path $RunDirectory 'appdata\roaming'
        localappdata = Join-Path $RunDirectory 'appdata\local'
    }
}

function Assert-DOnlyGeneratedPaths {
    param([Parameter(Mandatory = $true)][System.Collections.IDictionary]$Directories)
    $candidatePaths = @($RunDirectory) + @($Directories.Values)
    foreach ($candidate in $candidatePaths) {
        $fullPath = [IO.Path]::GetFullPath([string]$candidate)
        if ([IO.Path]::GetPathRoot($fullPath) -cne 'D:\') {
            throw "仿真输出或环境目录未规范化到 D:：$fullPath"
        }
    }
}

function Set-ToolEnvironment {
    param([Parameter(Mandatory = $true)][System.Collections.IDictionary]$Directories)
    $names = @('TEMP', 'TMP', 'TMPDIR', 'XILINX_LOCAL_USER_DATA', 'HOME', 'APPDATA', 'LOCALAPPDATA')
    $previous = @{}
    foreach ($name in $names) {
        $previous[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
    }
    $env:TEMP = [string]$Directories.temporary_directory
    $env:TMP = [string]$Directories.temporary_directory
    $env:TMPDIR = [string]$Directories.temporary_directory
    $env:XILINX_LOCAL_USER_DATA = [string]$Directories.xilinx_local_user_data
    $env:HOME = [string]$Directories.home
    $env:APPDATA = [string]$Directories.appdata
    $env:LOCALAPPDATA = [string]$Directories.localappdata
    Assert-DOnlyGeneratedPaths -Directories $Directories
    return $previous
}

function Restore-ToolEnvironment {
    param([System.Collections.IDictionary]$Previous)
    if ($null -eq $Previous) {
        return
    }
    foreach ($name in @('TEMP', 'TMP', 'TMPDIR', 'XILINX_LOCAL_USER_DATA', 'HOME', 'APPDATA', 'LOCALAPPDATA')) {
        [Environment]::SetEnvironmentVariable($name, [string]$Previous[$name], 'Process')
    }
}

function Write-JsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Value
    )
    $json = ConvertTo-Json -InputObject $Value -Depth 16
    $encoding = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, $encoding)
}

function Get-CurrentGitHead {
    $head = & git -C $ProjectRoot rev-parse HEAD
    if ($LASTEXITCODE -ne 0) {
        throw 'git rev-parse HEAD failed.'
    }
    $head = [string]$head
    if ($head -notmatch '^[0-9a-fA-F]{40}$') {
        throw "Unexpected Git HEAD value: $head"
    }
    return $head.ToLowerInvariant()
}

function Get-ReferenceCommandLines {
    param([string[]]$SourcePaths)
    $content = Get-Content -LiteralPath $ReferenceCommandPath -Raw -Encoding UTF8
    $lines = @([regex]::Split($content, '\r?\n'))
    $xvlogLine = @($lines | Where-Object { $_ -match '^call "[^"]*\\xvlog\.bat"' })
    $xelabLine = @($lines | Where-Object { $_ -match '^call "[^"]*\\xelab\.bat"' })
    $xsimLine = @($lines | Where-Object { $_ -match '^call "[^"]*\\xsim\.bat"' })
    if ($xvlogLine.Count -ne 1 -or $xelabLine.Count -ne 1 -or $xsimLine.Count -ne 1) {
        throw 'The reference command must contain exactly one xvlog, xelab, and xsim invocation.'
    }

    $sourcePattern = '"(?<source>D:\\FPGA_Competition\\[^"]+\.sv)"'
    $matches = [regex]::Matches($xvlogLine[0], $sourcePattern)
    if ($matches.Count -ne 15) {
        throw "The reference xvlog command must bind exactly 15 SystemVerilog sources; found $($matches.Count)."
    }
    for ($index = 0; $index -lt $SourcePaths.Count; $index++) {
        if ($matches[$index].Groups['source'].Value -cne $SourcePaths[$index]) {
            throw "Reference source order/path mismatch at item $index."
        }
    }

    $quotedSources = @($SourcePaths | ForEach-Object { '"' + $_ + '"' }) -join ' '
    $expectedXvlog = 'call "' + $XvlogPath + '" -sv -work xil_defaultlib ' +
        $quotedSources + ' > xvlog_console.txt 2>&1'
    $expectedXelab = 'call "' + $XelabPath +
        '" -mt off -debug typical xil_defaultlib.tb_s2a_network_backend_layer0_probe -s s2a_t64_layer0_snapshot -log xelab.log > xelab_console.txt 2>&1'
    $expectedXsim = 'call "' + $XsimPath +
        '" s2a_t64_layer0_snapshot -R -log xsim.log > xsim_console.txt 2>&1'
    if ($xvlogLine[0] -cne $expectedXvlog -or
        $xelabLine[0] -cne $expectedXelab -or
        $xsimLine[0] -cne $expectedXsim) {
        throw 'The reference tool command arguments differ from the frozen runner plan.'
    }
    return [pscustomobject]@{
        xvlog = $xvlogLine[0]
        xelab = $xelabLine[0]
        xsim = $xsimLine[0]
    }
}

function Get-SourceBindings {
    $bindings = @()
    foreach ($relativePath in $ExpectedRelativeSources) {
        $absolutePath = Join-Path $ProjectRoot $relativePath
        $bindings += Get-FileBinding -Path $absolutePath -ExpectedPath $absolutePath
    }
    return $bindings
}

function Assert-SourcesUnchanged {
    param([string]$StageName)
    $currentBindings = @(Get-SourceBindings)
    if ($currentBindings.Count -ne $script:SourceBindings.Count) {
        $script:FailureExitCode = 95
        throw "Source count changed after stage $StageName."
    }
    for ($index = 0; $index -lt $currentBindings.Count; $index++) {
        if ($currentBindings[$index].path -cne $script:SourceBindings[$index].path -or
            $currentBindings[$index].sha256 -cne $script:SourceBindings[$index].sha256 -or
            $currentBindings[$index].length_bytes -ne $script:SourceBindings[$index].length_bytes) {
            $script:FailureExitCode = 95
            throw "Source binding changed after stage $($StageName): $($currentBindings[$index].path)"
        }
    }
}

function Get-LogBindings {
    $logNames = @(
        'xvlog.log', 'xvlog_console.txt',
        'xelab.log', 'xelab_console.txt',
        'xsim.log', 'xsim_console.txt'
    )
    $logs = @()
    foreach ($name in $logNames) {
        $path = Join-Path $RunDirectory $name
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            $file = Get-Item -LiteralPath $path
            $logs += [pscustomobject]@{
                path = $file.FullName
                present = $true
                sha256 = Get-Sha256Hex -Path $file.FullName
                length_bytes = [int64]$file.Length
            }
        } else {
            $logs += [pscustomobject]@{
                path = $path
                present = $false
                sha256 = $null
                length_bytes = $null
            }
        }
    }
    return $logs
}

function Write-RunStatus {
    param(
        [string]$Status,
        [int]$RunnerExitCode,
        [object[]]$ProtectedAfter,
        [string]$ProtectedSnapshotError
    )
    $sourceAfter = @()
    $sourceError = $null
    try {
        $sourceAfter = @(Get-SourceBindings)
    } catch {
        $sourceError = $_.Exception.Message
    }
    $sourceChecks = @()
    for ($index = 0; $index -lt $script:SourceBindings.Count; $index++) {
        $before = $script:SourceBindings[$index]
        $after = $null
        if ($index -lt $sourceAfter.Count) {
            $after = $sourceAfter[$index]
        }
        $same = $null -ne $after -and
            $before.path -ceq $after.path -and
            $before.sha256 -ceq $after.sha256 -and
            $before.length_bytes -eq $after.length_bytes
        $sourceChecks += [pscustomobject]@{
            path = $before.path
            before_sha256 = $before.sha256
            after_sha256 = if ($null -ne $after) { $after.sha256 } else { $null }
            before_length_bytes = $before.length_bytes
            after_length_bytes = if ($null -ne $after) { $after.length_bytes } else { $null }
            unchanged = $same
        }
    }
    if ($sourceError) {
        $Status = 'FAIL_SOURCE_HASH_CHECK'
        if ($RunnerExitCode -eq 0) {
            $RunnerExitCode = 95
        }
    } elseif (@($sourceChecks | Where-Object { -not $_.unchanged }).Count -gt 0) {
        $Status = 'FAIL_SOURCE_HASH_CHECK'
        if ($RunnerExitCode -eq 0) {
            $RunnerExitCode = 95
        }
    }
    $logBindings = @(Get-LogBindings)
    $statusObject = [ordered]@{
        status = $Status
        runner_exit_code = $RunnerExitCode
        failure = $script:FailureMessage
        git_head = $script:GitHead
        runner_sha256 = $script:RunnerHash
        manifest_written_before_tools = $script:ManifestWritten
        phase_exit_codes = $script:PhaseResults
        source_hashes_unchanged = $null -eq $sourceError -and
            @($sourceChecks | Where-Object { -not $_.unchanged }).Count -eq 0
        source_hash_check_error = $sourceError
        source_hash_checks = $sourceChecks
        logs = $logBindings
        unique_pass_line_count = $script:PassLines.Count
        unique_pass_line = if ($script:PassLines.Count -eq 1) { $script:PassLines[0] } else { $null }
        protected_processes_before = @($script:ProtectedBefore)
        protected_processes_after = @($ProtectedAfter)
        protected_process_snapshot_error = $ProtectedSnapshotError
        protected_process_policy = '仅容忍固定 PID 的完整创建时间/父 PID/名称/路径/命令行/映像 SHA256 元组；自然缺席可接受；不向其发送命令。'
        resource_snapshots = @($script:ResourceSnapshots)
        tool_versions = $script:ToolVersions
        compile_artifacts_before_xsim = $script:CompileArtifactBinding
        compile_artifacts_reverified_before_xsim = $script:CompileArtifactPreXsimCheck
        compile_artifacts_after_xsim = $script:CompileArtifactAfterXsim
        xsim_runtime_processes = @($script:XsimRuntimeProcesses)
        run_scope = '仅为本次新运行 sim_run12；不回填历史 sim_run10 或 sim_run11。'
        protected_process_set_changed = (Get-ProcessSetKey @($script:ProtectedBefore)) -cne
            (Get-ProcessSetKey @($ProtectedAfter))
    }
    Write-JsonFile -Path (Join-Path $RunDirectory 'run_status.json') -Value $statusObject
}

function Invoke-ToolStage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$ToolPath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$ConsoleLog,
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$Directories
    )
    Get-ResourceSnapshot | Out-Null
    Assert-NoUnexpectedXilinxProcesses -StageName "before $Name" | Out-Null
    Assert-ToolBinariesUnchanged -StageName "before $Name"
    $renderedArguments = @()
    foreach ($argument in $Arguments) {
        if ($argument.EndsWith('.sv', [System.StringComparison]::OrdinalIgnoreCase)) {
            $renderedArguments += '"' + $argument + '"'
        } else {
            $renderedArguments += $argument
        }
    }
    $commandLine = 'call "' + $ToolPath + '" ' + ($renderedArguments -join ' ') +
        ' > ' + $ConsoleLog + ' 2>&1'
    $phase = $script:PhaseResults[$Name]
    $phase.launch_command = $commandLine
    $phase.working_directory = $RunDirectory
    $phase.exact_arguments = @($Arguments)
    $phase.started_utc = [DateTime]::UtcNow.ToString('o')
    $previousEnvironment = Set-ToolEnvironment -Directories $Directories
    Push-Location -LiteralPath $RunDirectory
    $process = $null
    $toolExitCode = $null
    $monitorFailure = $null
    try {
        $startInfo = New-Object System.Diagnostics.ProcessStartInfo
        $startInfo.FileName = [string]$env:ComSpec
        $startInfo.Arguments = '/d /c ' + $commandLine
        $startInfo.WorkingDirectory = $RunDirectory
        $startInfo.UseShellExecute = $false
        $startInfo.CreateNoWindow = $true
        $process = [System.Diagnostics.Process]::Start($startInfo)
        if ($null -eq $process) {
            throw "Failed to start the bound command shell for $Name."
        }
        $phase.launcher_process_id = [int]$process.Id
        $phase.launcher_parent_process_id = $PID
        $phase.launcher_executable = [string]$env:ComSpec
        $phase.process_samples = @()
        $tool = @($script:ToolPlan | Where-Object { $_.name -ceq $Name } | Select-Object -First 1)[0]
        if ($null -eq $tool) {
            throw "Tool plan entry is missing for $Name."
        }
        while (-not $process.HasExited) {
            try {
                $sample = Assert-RunnerOwnedProcessPolicy -StageName $Name `
                    -LauncherProcessId ([int]$process.Id) -LaunchCommand $commandLine -Tool $tool
                $phase.process_samples += $sample
                if ($Name -eq 'xsim') {
                    $script:XsimRuntimeProcesses += $sample
                }
            } catch {
                if ($null -eq $monitorFailure) {
                    $monitorFailure = $_.Exception.Message
                }
            }
            Start-Sleep -Milliseconds 200
            $process.Refresh()
        }
        $process.WaitForExit()
        $toolExitCode = [int]$process.ExitCode
        $phase.finished_utc = [DateTime]::UtcNow.ToString('o')
        $phase.process_id = [int]$process.Id
    } finally {
        if ($null -ne $process) {
            $process.Dispose()
        }
        Pop-Location
        Restore-ToolEnvironment -Previous $previousEnvironment
    }
    $phase.tool_exit_code = [int]$toolExitCode
    if ($null -ne $monitorFailure) {
        $script:FailureExitCode = 96
        throw "Process isolation check failed during ${Name}: $monitorFailure"
    }
    if ($toolExitCode -ne 0) {
        $script:FailureExitCode = $ToolFailureCodes[$Name]
        throw "$Name exited with code $toolExitCode."
    }
    Assert-NoUnexpectedXilinxProcesses -StageName "after $Name" | Out-Null
    Assert-SourcesUnchanged -StageName $Name
    Assert-ToolBinariesUnchanged -StageName "after $Name"
    $toolLog = Join-Path $RunDirectory "$Name.log"
    if (-not (Test-Path -LiteralPath $toolLog -PathType Leaf)) {
        $script:FailureExitCode = $ToolFailureCodes[$Name]
        throw "$Name log is missing."
    }
    $errorLines = @(Select-String -LiteralPath $toolLog -Pattern 'ERROR:|FATAL:' -AllMatches)
    if ($errorLines.Count -gt 0) {
        $script:FailureExitCode = $ToolFailureCodes[$Name]
        throw "$Name log contains ERROR or FATAL."
    }
    $script:ToolVersions[$Name] = Get-ToolReportedVersion -Name $Name
    $phase.runner_exit_code = 0
    Update-RunManifest
}

function Invoke-BoundRunner {
    if ($ProcessFixturePath -and -not $PreflightOnly) {
        $script:FailureExitCode = 96
        throw 'Process fixtures are accepted only with -PreflightOnly; simulation mode cannot use injected process data.'
    }
    if ((Resolve-Path -LiteralPath $PSCommandPath).Path -cne $RunnerPath) {
        throw "Runner must be invoked from the exact path $RunnerPath"
    }
    if ((Resolve-Path -LiteralPath $PSScriptRoot).Path -cne 'D:\FPGA_Competition\verification') {
        throw 'Runner is not located in the expected project verification directory.'
    }
    if (Test-Path -LiteralPath $RunDirectory) {
        throw "Refusing to reuse or overwrite existing result path: $RunDirectory"
    }

    $script:RunnerHash = Get-Sha256Hex -Path $RunnerPath
    $script:GitHead = Get-CurrentGitHead
    $sourcePaths = @($ExpectedRelativeSources | ForEach-Object { Join-Path $ProjectRoot $_ })
    if ($sourcePaths.Count -ne 15) {
        throw "Internal compile list count is not 15: $($sourcePaths.Count)"
    }
    $referenceCommands = Get-ReferenceCommandLines -SourcePaths $sourcePaths
    $script:ReferenceBinding = Get-FileBinding -Path $ReferenceCommandPath -ExpectedPath $ReferenceCommandPath
    $script:SourceBindings = @(Get-SourceBindings)

    foreach ($toolPath in @($XvlogPath, $XelabPath, $XsimPath)) {
        if (-not (Test-Path -LiteralPath $toolPath -PathType Leaf)) {
            throw "Required Xilinx batch file is missing: $toolPath"
        }
    }
    foreach ($toolPath in $ToolBinaryPaths.Values) {
        if (-not (Test-Path -LiteralPath $toolPath -PathType Leaf)) {
            throw "Required Vivado $VivadoRelease binary is missing: $toolPath"
        }
    }
    $script:ToolBinaryBindings = @(Get-ToolBinaryBindings)
    $script:ToolPlan = @(
        [pscustomobject]@{
            name = 'xvlog'
            executable = $XvlogPath
            arguments = @('-sv', '-work', 'xil_defaultlib') + $sourcePaths
            console_log = 'xvlog_console.txt'
            tool_log = 'xvlog.log'
            runner_failure_code = 91
        },
        [pscustomobject]@{
            name = 'xelab'
            executable = $XelabPath
            arguments = @('-mt', 'off', '-debug', 'typical', 'xil_defaultlib.tb_s2a_network_backend_layer0_probe',
                '-s', $SnapshotName, '-log', 'xelab.log')
            console_log = 'xelab_console.txt'
            tool_log = 'xelab.log'
            runner_failure_code = 92
        },
        [pscustomobject]@{
            name = 'xsim'
            executable = $XsimPath
            arguments = @($SnapshotName, '-R', '-log', 'xsim.log')
            console_log = 'xsim_console.txt'
            tool_log = 'xsim.log'
            runner_failure_code = 93
        }
    )

    if ($ProcessFixturePath) {
        $fixtureFullPath = [IO.Path]::GetFullPath($ProcessFixturePath)
        if ([IO.Path]::GetPathRoot($fixtureFullPath) -cne 'D:\' -or
            -not (Test-Path -LiteralPath $fixtureFullPath -PathType Leaf)) {
            $script:FailureExitCode = 96
            throw 'Process fixture must be an existing file under D: and is valid only for no-launch preflight tests.'
        }
        $fixtureData = Get-Content -LiteralPath $fixtureFullPath -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($null -eq $fixtureData.processes) {
            $script:FailureExitCode = 96
            throw 'Process fixture JSON must contain a processes array.'
        }
        $script:ProcessFixture = @($fixtureData.processes)
    }
    Assert-DOnlyGeneratedPaths -Directories (Get-DRunDirectories)
    $script:ProtectedBefore = @(Get-ObservedXilinxProcesses)
    Assert-NoUnexpectedXilinxProcesses -StageName 'preflight' -Processes $script:ProtectedBefore | Out-Null
    $initialResources = Get-ResourceSnapshot
    if ($PreflightOnly) {
        $message = 'PREFLIGHT: run12 path, 15 source hashes, exact reference argv/no plusargs, tool version/binary hashes, Git HEAD, runner hash, D: paths/resources, and protected process identities checked; no Xilinx process started; output_directory_created=false.'
        Write-Host $message
        Write-Host ("PROTECTED_PROCESSES: " + (Get-ProcessSummary $script:ProtectedBefore))
        Write-Host ("RESOURCES: free_ram_mib={0}; d_free_gib={1}" -f $initialResources.free_physical_memory_mib, $initialResources.d_free_space_gib)
        Write-Host 'PREFLIGHT_READY: only exact known protected process identities may remain active; no tool was started.'
        return 0
    }

    [System.IO.Directory]::CreateDirectory($RunDirectory) | Out-Null
    $script:RunDirectoryCreated = $true
    $directories = Get-DRunDirectories
    foreach ($directory in $directories.Values) {
        [System.IO.Directory]::CreateDirectory([string]$directory) | Out-Null
    }
    Assert-DOnlyGeneratedPaths -Directories $directories
    foreach ($directory in @($RunDirectory) + @($directories.Values)) {
        if ((Resolve-Path -LiteralPath $directory).Path -notmatch '^[D]:\\') {
            throw "Resolved simulation/output path is not on D: $directory"
        }
    }
    $script:XilinxLocalUserData = [string]$directories.xilinx_local_user_data

    foreach ($tool in $script:ToolPlan) {
        $script:PhaseResults[$tool.name] = [ordered]@{
            executable = $tool.executable
            arguments = @($tool.arguments)
            launch_command = $null
            tool_exit_code = $null
            runner_exit_code = $null
            working_directory = $RunDirectory
        }
    }
    $script:RunManifest = [ordered]@{
        schema = 's2a_t64_bound_probe_run_v2'
        task_id = 'S2A-T64-DYN11-PROVENANCE-RUN12'
        run_id = 'S2A-T64-sim_run12'
        run_scope = '仅绑定本次新运行 sim_run12；不回填或改写 sim_run10、sim_run11。'
        status = 'PREPARED'
        git_head = $script:GitHead
        runner_path = $RunnerPath
        runner_sha256 = $script:RunnerHash
        reference_command = $script:ReferenceBinding
        reference_tool_commands = $referenceCommands
        result_directory = $RunDirectory
        working_directory = $RunDirectory
        generated_path_root = 'D:\'
        tool_environment_directories = $directories
        sources = @($script:SourceBindings)
        tools = @($script:ToolPlan)
        tool_binary_bindings = @($script:ToolBinaryBindings)
        expected_vivado_release = $VivadoRelease
        expected_snapshot_name = $SnapshotName
        protected_processes_before = @($script:ProtectedBefore)
        protected_process_policy = '只读容忍固定 PID 完整身份匹配的 8712/22488/13156；任一身份不符、PID 重用或额外 Xilinx 工具进程均 fail-closed。'
        resource_snapshots = @($script:ResourceSnapshots)
        created_utc = [DateTime]::UtcNow.ToString('o')
    }
    Write-JsonFile -Path (Join-Path $RunDirectory 'run_manifest.json') -Value $script:RunManifest
    $script:ManifestWritten = $true

    $status = 'FAIL'
    $runnerExitCode = 1
    $protectedAfter = @()
    $protectedSnapshotError = $null
    try {
        Assert-SourcesUnchanged -StageName 'before xvlog'
        Invoke-ToolStage -Name 'xvlog' -ToolPath $XvlogPath -Arguments $script:ToolPlan[0].arguments `
            -ConsoleLog $script:ToolPlan[0].console_log -Directories $directories
        $script:PhaseResults['xvlog'].runner_exit_code = 0

        Invoke-ToolStage -Name 'xelab' -ToolPath $XelabPath -Arguments $script:ToolPlan[1].arguments `
            -ConsoleLog $script:ToolPlan[1].console_log -Directories $directories
        $script:PhaseResults['xelab'].runner_exit_code = 0
        $script:CompileArtifactBinding = Get-CompileArtifactBinding
        $script:RunManifest.xsim_consumed_snapshot = [ordered]@{
            name = $SnapshotName
            relative_path = "xsim.dir\$SnapshotName"
            executable = $script:CompileArtifactBinding.snapshot_executable
            compile_options = $script:CompileArtifactBinding.compile_options
            sdb_file_count = $script:CompileArtifactBinding.sdb_file_count
            xsim_command = $script:ToolPlan[2].executable + ' ' + ($script:ToolPlan[2].arguments -join ' ')
            xsim_working_directory = $RunDirectory
            xsim_launch_command = 'call "' + $XsimPath + '" ' + ($script:ToolPlan[2].arguments -join ' ') +
                ' > xsim_console.txt 2>&1'
        }
        Update-RunManifest -Status 'ELABORATED_PRE_XSIM_LOCKED'

        Assert-SourcesUnchanged -StageName 'immediately before xsim'
        Assert-ToolBinariesUnchanged -StageName 'immediately before xsim'
        $preXsimArtifacts = Get-CompileArtifactBinding
        $staticComparison = Compare-StaticCompileArtifacts -Before $script:CompileArtifactBinding -After $preXsimArtifacts
        $memBefore = @($script:CompileArtifactBinding.mutable_files | Where-Object {
            $_.relative_path -ceq "xsim.dir\$SnapshotName\xsim.mem"
        } | Select-Object -First 1)[0]
        $memAtLaunch = @($preXsimArtifacts.mutable_files | Where-Object {
            $_.relative_path -ceq "xsim.dir\$SnapshotName\xsim.mem"
        } | Select-Object -First 1)[0]
        $memUnchangedBeforeLaunch = $null -ne $memBefore -and $null -ne $memAtLaunch -and
            $memBefore.length_bytes -eq $memAtLaunch.length_bytes -and $memBefore.sha256 -ceq $memAtLaunch.sha256
        $script:CompileArtifactPreXsimCheck = [pscustomobject]@{
            captured_utc = [DateTime]::UtcNow.ToString('o')
            static_artifacts = $staticComparison
            xsim_mem_before_xsim = $memAtLaunch
            xsim_mem_unchanged_since_xelab = $memUnchangedBeforeLaunch
            passed = $staticComparison.passed -and $memUnchangedBeforeLaunch
        }
        if (-not $script:CompileArtifactPreXsimCheck.passed) {
            $script:FailureExitCode = 96
            throw 'Compile artifacts or xsim.mem changed between xelab and the bound xsim launch.'
        }
        $script:RunManifest.xsim_consumed_snapshot.pre_xsim_artifact_revalidation = $script:CompileArtifactPreXsimCheck
        Update-RunManifest -Status 'PRE_XSIM_STATIC_ARTIFACTS_REVERIFIED'

        Invoke-ToolStage -Name 'xsim' -ToolPath $XsimPath -Arguments $script:ToolPlan[2].arguments `
            -ConsoleLog $script:ToolPlan[2].console_log -Directories $directories
        $script:CompileArtifactAfterXsim = Get-CompileArtifactBinding
        $staticAfterRun = Compare-StaticCompileArtifacts -Before $script:CompileArtifactBinding -After $script:CompileArtifactAfterXsim
        if (-not $staticAfterRun.passed) {
            $script:FailureExitCode = 96
            throw "Static compiled snapshot artifact changed during xsim: $($staticAfterRun.changed_paths -join ', ')"
        }
        $memAfterRun = @($script:CompileArtifactAfterXsim.mutable_files | Where-Object {
            $_.relative_path -ceq "xsim.dir\$SnapshotName\xsim.mem"
        } | Select-Object -First 1)[0]
        $script:RunManifest.xsim_mem_runtime_delta = [pscustomobject]@{
            before_xsim = $memAtLaunch
            after_xsim = $memAfterRun
            changed = ($null -eq $memAfterRun -or $memAtLaunch.length_bytes -ne $memAfterRun.length_bytes -or
                $memAtLaunch.sha256 -cne $memAfterRun.sha256)
            explanation = 'xsim.mem 可能是运行期 memory backing 文件；按任务要求记录运行前后，不作为静态 compile lock。'
        }
        $script:RunManifest.static_artifacts_unchanged_during_xsim = $staticAfterRun
        Update-RunManifest -Status 'XSIM_COMPLETED_ARTIFACTS_RECHECKED'
        $xsimLog = Join-Path $RunDirectory 'xsim.log'
        $script:PassLines = @(Get-Content -LiteralPath $xsimLog -Encoding UTF8 |
            Where-Object { $_.StartsWith('PASS: layer0', [System.StringComparison]::Ordinal) })
        if ($script:PassLines.Count -ne 1) {
            $script:FailureExitCode = 94
            throw "Expected exactly one PASS: layer0 line; found $($script:PassLines.Count)."
        }
        $script:PhaseResults['xsim'].runner_exit_code = 0

        Assert-SourcesUnchanged -StageName 'after xsim'
        $status = 'PASS'
        $runnerExitCode = 0
    } catch {
        $script:FailureMessage = $_.Exception.Message
        $runnerExitCode = $script:FailureExitCode
        foreach ($name in @('xvlog', 'xelab', 'xsim')) {
            if ($null -eq $script:PhaseResults[$name].runner_exit_code -and
                $null -ne $script:PhaseResults[$name].tool_exit_code) {
                $script:PhaseResults[$name].runner_exit_code = $runnerExitCode
            }
        }
        Write-Host ("RUN_FAILED: " + $script:FailureMessage)
    } finally {
        try {
            $protectedAfter = @(Get-ObservedXilinxProcesses)
            Assert-NoUnexpectedXilinxProcesses -StageName 'final' -Processes $protectedAfter | Out-Null
        } catch {
            $protectedSnapshotError = $_.Exception.Message
            $status = 'FAIL_PROTECTED_PROCESS_POLICY'
            $runnerExitCode = 96
            $script:FailureMessage = $protectedSnapshotError
        }
        try {
            $script:ProtectedAfter = @($protectedAfter)
            Update-RunManifest -Status $status
            Write-RunStatus -Status $status -RunnerExitCode $runnerExitCode -ProtectedAfter $protectedAfter -ProtectedSnapshotError $protectedSnapshotError
        } catch {
            Write-Host ("STATUS_WRITE_FAILED: " + $_.Exception.Message)
            if ($runnerExitCode -eq 0) {
                $runnerExitCode = 98
            }
        }
    }
    Write-Host ("RUN_STATUS={0}; RUNNER_EXIT_CODE={1}; PASS_LINES={2}; PROTECTED_BEFORE={3}; PROTECTED_AFTER={4}" -f
        $status, $runnerExitCode, $script:PassLines.Count,
        (Get-ProcessSummary $script:ProtectedBefore), (Get-ProcessSummary $protectedAfter))
    return $runnerExitCode
}

try {
    $exitCode = Invoke-BoundRunner
} catch {
    Write-Host ("PREFLIGHT_FAILED: " + $_.Exception.Message)
    $exitCode = $script:FailureExitCode
}
exit $exitCode
