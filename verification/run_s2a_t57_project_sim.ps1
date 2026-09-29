param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("dryrun", "run", "recover")]
    [string]$Mode
)

$ErrorActionPreference = "Stop"
$RepositoryRoot = "D:\FPGA_Competition"
$ExpectedRepositoryRoot = [IO.Path]::GetFullPath("D:\FPGA_Competition")
$VivadoPath = "D:\Xilinx\2026.1\Vivado\bin\vivado.bat"
$TclPath = Join-Path $RepositoryRoot "report\evidence\S2A-T57\run_project_sim.tcl"
$XprPath = Join-Path $RepositoryRoot "vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr"
$BindingPath = Join-Path $RepositoryRoot "report\evidence\S2A-T57\project_preflight_binding.json"
$RunDirectory = Join-Path $RepositoryRoot "report\evidence\S2A-T57\run09\attempt09"
$ExpectedRunDirectory = "D:\FPGA_Competition\report\evidence\S2A-T57\run09\attempt09"
$XsimTclPath = Join-Path $RunDirectory "xsim_run.tcl"
$PrepareSummaryPath = Join-Path $RunDirectory "prepare_summary.json"
$FixtureManifestPath = Join-Path $RunDirectory "fixture\fixture_manifest.json"
$CompileSourceManifestPath = Join-Path $RunDirectory "compile_source_manifest.tsv"
$T57RunnerPath = Join-Path $RepositoryRoot "verification\test_s2a_conv_layer35_row21_all_channels_rtl.py"
$VerifyOnlyLogPath = Join-Path $RunDirectory "verify_only.log"
$RunSummaryPath = Join-Path $RunDirectory "run_summary.json"
$FinalReportPath = Join-Path $RunDirectory "layer35_row21_all_channels.json"
$PythonPath = (Get-Command python.exe -ErrorAction Stop).Source
$ExpectedT57SourceRelPaths = @(
    "src/int8_conv_tap_geometry.sv",
    "src/int8_conv_weight_address.sv",
    "src/int8_mac_accumulator.sv",
    "src/s2a_conv_engine.sv",
    "src/s2a_conv_layer35_channel_probe.sv",
    "sim/tb_s2a_conv_layer35_row21_all_channels.sv",
    "sim/s2a_t57_no_wave.tcl",
    "verification/test_s2a_conv_layer35_row21_all_channels_rtl.py",
    "verification/test_s2a_t57_attempt09_transcript.py",
    "report/evidence/S2A-T57/run_project_sim.tcl",
    "verification/run_s2a_t57_project_sim.ps1"
)
$ExpectedCompileSourceRelPaths = @(
    "src/int8_conv_tap_geometry.sv",
    "src/int8_conv_weight_address.sv",
    "src/int8_mac_accumulator.sv",
    "src/s2a_conv_engine.sv",
    "src/s2a_conv_layer35_channel_probe.sv",
    "sim/tb_s2a_conv_layer35_row21_all_channels.sv"
)
$ScratchDirectory = Join-Path $RunDirectory "isolated_project"
$ExpectedScratchDirectory = Join-Path $ExpectedRunDirectory "isolated_project"
$OwnerMarker = Join-Path $RunDirectory ".s2a_t57_isolated_project_owner"
$ExpectedProjectName = "AX7Z020_Gesture"
$ExpectedScratchProjectName = "s2a_t57_row21_isolated"
$ExpectedSimset = "sim_s2a_t57_row21"
$ExpectedTop = "tb_s2a_conv_layer35_row21_all_channels"

function Get-T57ProcessSnapshot {
    $names = @("vivado.exe", "xsim.exe", "xsimk.exe", "xelab.exe", "xvlog.exe")
    $names += @("vivado_lab.exe", "xsct.exe", "xvhdl.exe")
    $items = @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop |
        Where-Object { $names -contains $_.Name.ToLowerInvariant() } |
        Sort-Object ProcessId |
        ForEach-Object {
            [ordered]@{
                name = $_.Name
                process_id = [int]$_.ProcessId
            }
        })
    return $items
}

function Get-T57VerifiedDirectoryChain {
    param([Parameter(Mandatory = $true)][string]$Path)
    $full = [IO.Path]::GetFullPath($Path)
    $root = [IO.Path]::GetPathRoot($full)
    if (-not [string]::Equals($root, "D:\", [StringComparison]::OrdinalIgnoreCase)) {
        throw "T57 路径不在固定 D:\ 卷：$full"
    }
    $chain = [Collections.Generic.List[object]]::new()
    $current = $root
    $rootItem = Get-Item -LiteralPath $current -ErrorAction Stop
    if (-not $rootItem.PSIsContainer -or
        (($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "T57 卷根不是普通目录：$current"
    }
    $chain.Add([pscustomobject]@{ path = $current; is_directory = $true; reparse_point = $false })
    $relative = $full.Substring($root.Length).TrimEnd([char[]]@([char]92, [char]47))
    foreach ($component in ($relative -split '[\\/]')) {
        if ([string]::IsNullOrWhiteSpace($component) -or $component -eq "." -or $component -eq "..") {
            throw "T57 路径包含空或相对目录组件：$full"
        }
        $current = Join-Path $current $component
        $item = Get-Item -LiteralPath $current -ErrorAction Stop
        $isReparse = (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)
        if (-not $item.PSIsContainer -or $isReparse) {
            throw "T57 路径链包含非目录或 reparse point：$current"
        }
        $chain.Add([pscustomobject]@{ path = $current; is_directory = $true; reparse_point = $false })
    }
    return $chain.ToArray()
}

function Assert-T57ScratchTreeSafe {
    param([Parameter(Mandatory = $true)][string]$Path)
    $null = @(Get-T57VerifiedDirectoryChain -Path $RunDirectory)
    if (-not [string]::Equals([IO.Path]::GetFullPath($RunDirectory), $ExpectedRunDirectory,
            [StringComparison]::OrdinalIgnoreCase)) {
        throw "run09 路径不等于固定证据目录：$RunDirectory"
    }
    $full = [IO.Path]::GetFullPath($Path)
    if (-not [string]::Equals($full, $ExpectedScratchDirectory, [StringComparison]::OrdinalIgnoreCase) -or
        -not [string]::Equals([IO.Path]::GetDirectoryName($full), $ExpectedRunDirectory,
            [StringComparison]::OrdinalIgnoreCase)) {
        throw "拒绝检查非固定 scratch 目录：$full"
    }
    if (-not (Test-Path -LiteralPath $full -PathType Container)) {
        throw "隔离工程目录不存在或类型错误：$full"
    }
    $item = Get-Item -LiteralPath $full -ErrorAction Stop
    if (-not $item.PSIsContainer -or
        (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "隔离工程根不是普通目录：$full"
    }
    $boundary = $full.TrimEnd([char[]]@([char]92, [char]47)) + [IO.Path]::DirectorySeparatorChar
    $pending = [Collections.Generic.Stack[string]]::new()
    $pending.Push($full)
    while ($pending.Count -gt 0) {
        $directory = $pending.Pop()
        foreach ($entry in [IO.Directory]::EnumerateFileSystemEntries($directory)) {
            $entryFull = [IO.Path]::GetFullPath($entry)
            if (-not $entryFull.StartsWith($boundary, [StringComparison]::OrdinalIgnoreCase)) {
                throw "隔离工程节点越出预期 workspace：$entryFull"
            }
            $attributes = [IO.File]::GetAttributes($entryFull)
            if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "隔离工程中发现 reparse point，拒绝清理：$entryFull"
            }
            if (($attributes -band [IO.FileAttributes]::Directory) -ne 0) {
                $child = Get-Item -LiteralPath $entryFull -ErrorAction Stop
                if (-not $child.PSIsContainer) {
                    throw "隔离工程目录节点类型异常：$entryFull"
                }
                $pending.Push($entryFull)
            }
        }
    }
}

function Clear-T57ScratchReadOnlyAttributes {
    param([Parameter(Mandatory = $true)][string]$Path)
    $null = @(Get-T57VerifiedDirectoryChain -Path $RunDirectory)
    $full = Test-T57ScratchPath -Path $Path
    Assert-T57ScratchTreeSafe -Path $full
    $boundary = $full.TrimEnd([char[]]@([char]92, [char]47)) + [IO.Path]::DirectorySeparatorChar
    $nodes = [Collections.Generic.List[string]]::new()
    $nodes.Add($full)
    $pending = [Collections.Generic.Stack[string]]::new()
    $pending.Push($full)
    while ($pending.Count -gt 0) {
        $directory = $pending.Pop()
        foreach ($entry in [IO.Directory]::EnumerateFileSystemEntries($directory)) {
            $entryFull = [IO.Path]::GetFullPath($entry)
            if (-not $entryFull.StartsWith($boundary, [StringComparison]::OrdinalIgnoreCase)) {
                throw "拒绝修改 scratch 边界外节点属性：$entryFull"
            }
            $attributes = [IO.File]::GetAttributes($entryFull)
            if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "scratch 节点出现 reparse point，拒绝修改属性：$entryFull"
            }
            $item = Get-Item -LiteralPath $entryFull -ErrorAction Stop
            $attributeIsDirectory = (($attributes -band [IO.FileAttributes]::Directory) -ne 0)
            if ($attributeIsDirectory -ne $item.PSIsContainer) {
                throw "scratch 节点类型变化，拒绝修改属性：$entryFull"
            }
            $nodes.Add($entryFull)
            if ($item.PSIsContainer) {
                $pending.Push($entryFull)
            }
        }
    }
    foreach ($node in $nodes) {
        if (-not [string]::Equals($node, $full, [StringComparison]::OrdinalIgnoreCase) -and
            -not $node.StartsWith($boundary, [StringComparison]::OrdinalIgnoreCase)) {
            throw "scratch 属性目标超出固定 workspace：$node"
        }
        $attributes = [IO.File]::GetAttributes($node)
        if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "scratch 属性目标变为 reparse point：$node"
        }
        if (($attributes -band [IO.FileAttributes]::ReadOnly) -ne 0) {
            $writableAttributes = $attributes -band (-bnot [IO.FileAttributes]::ReadOnly)
            [IO.File]::SetAttributes($node, $writableAttributes)
        }
    }
    Assert-T57ScratchTreeSafe -Path $full
}

function Assert-T57OwnerMarkerSafe {
    $expected = Join-Path $ExpectedRunDirectory ".s2a_t57_isolated_project_owner"
    $full = [IO.Path]::GetFullPath($OwnerMarker)
    if (-not [string]::Equals($full, $expected, [StringComparison]::OrdinalIgnoreCase) -or
        -not [string]::Equals([IO.Path]::GetDirectoryName($full), $ExpectedRunDirectory,
            [StringComparison]::OrdinalIgnoreCase)) {
        throw "owner marker 路径不是固定 run09 文件：$full"
    }
    $item = Get-Item -LiteralPath $full -ErrorAction Stop
    if ($item.PSIsContainer -or
        (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "owner marker 不是普通文件：$full"
    }
}

function Get-T57Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-T57BoundFile {
    param(
        [Parameter(Mandatory = $true)][string]$ExpectedPath,
        [Parameter(Mandatory = $true)]$Record,
        [Parameter(Mandatory = $true)][string]$Label
    )
    if ($null -eq $Record.path -or $null -eq $Record.bytes -or $null -eq $Record.sha256) {
        throw "$Label 绑定缺少 path/bytes/sha256"
    }
    $full = [IO.Path]::GetFullPath($ExpectedPath)
    $recordFull = [IO.Path]::GetFullPath([string]$Record.path)
    if (-not [string]::Equals($recordFull, $full, [StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label 路径与固定绑定不一致：$recordFull"
    }
    $null = @(Get-T57VerifiedDirectoryChain -Path ([IO.Path]::GetDirectoryName($full)))
    $item = Get-Item -LiteralPath $full -ErrorAction Stop
    if ($item.PSIsContainer -or
        (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "$Label 不是普通文件或是 reparse point：$full"
    }
    if ($item.Length -ne [int64]$Record.bytes) {
        throw "$Label 字节数变化：expected=$($Record.bytes) actual=$($item.Length)"
    }
    $actualSha = Get-T57Sha256 -Path $full
    if ($actualSha -cne ([string]$Record.sha256).ToLowerInvariant()) {
        throw "$Label SHA-256 变化：$full"
    }
    return $actualSha
}

function Assert-T57StartupSourceBindings {
    param([Parameter(Mandatory = $true)][string]$RunDirectory)
    $runFull = [IO.Path]::GetFullPath($RunDirectory)
    if (-not [string]::Equals($runFull, $ExpectedRunDirectory, [StringComparison]::OrdinalIgnoreCase)) {
        throw "启动前源码绑定门的 run 路径不匹配：$runFull"
    }
    $null = @(Get-T57VerifiedDirectoryChain -Path $runFull)
    $summaryRecord = [ordered]@{
        path = $PrepareSummaryPath
        bytes = (Get-Item -LiteralPath $PrepareSummaryPath -ErrorAction Stop).Length
        sha256 = Get-T57Sha256 -Path $PrepareSummaryPath
    }
    $null = Assert-T57BoundFile -ExpectedPath $PrepareSummaryPath -Record $summaryRecord -Label "T57 run09 prepare summary"
    $preparation = [IO.File]::ReadAllText($PrepareSummaryPath, [Text.Encoding]::UTF8) | ConvertFrom-Json -ErrorAction Stop
    if ($preparation.schema -cne "GestureForge-S2A-T57-preparation-summary-v3" -or
        $preparation.status -cne "PREPARED_NOT_SIMULATED") {
        throw "T57 run09 prepare summary schema/status 不匹配"
    }
    $fixtureRecord = $preparation.fixture.manifest
    $null = Assert-T57BoundFile -ExpectedPath $FixtureManifestPath -Record $fixtureRecord -Label "T57 fixture manifest"
    $fixture = [IO.File]::ReadAllText($FixtureManifestPath, [Text.Encoding]::UTF8) | ConvertFrom-Json -ErrorAction Stop
    if ($fixture.schema -cne "GestureForge-S2A-T57-fixture-manifest-v3" -or
        $fixture.task_id -cne "S2A-T57" -or $fixture.status -cne "PREPARED_NOT_SIMULATED") {
        throw "T57 run09 fixture manifest schema/status 不匹配"
    }

    $sourceHashes = $preparation.bindings.T57_source_hashes
    $sourceBindings = $preparation.bindings.T57_source_bindings
    $fixtureSourceHashes = $fixture.T57_source_hashes
    $fixtureSourceBindings = $fixture.T57_source_bindings
    $preflightSourceHashes = $preparation.project_preflight.T57_source_hashes
    $preflightSourceBindings = $preparation.project_preflight.T57_source_bindings
    foreach ($map in @($sourceHashes, $sourceBindings, $fixtureSourceHashes, $fixtureSourceBindings,
            $preflightSourceHashes, $preflightSourceBindings)) {
        if ($null -eq $map -or @($map.PSObject.Properties).Count -ne $ExpectedT57SourceRelPaths.Count) {
            throw "T57 prepare/fixture 源码绑定集合大小不匹配"
        }
        foreach ($relative in $ExpectedT57SourceRelPaths) {
            if (@($map.PSObject.Properties | Where-Object { $_.Name -ceq $relative }).Count -ne 1) {
                throw "T57 prepare/fixture 缺少精确源码路径绑定：$relative"
            }
        }
    }
    foreach ($relative in $ExpectedT57SourceRelPaths) {
        $expectedPath = Join-Path $RepositoryRoot ($relative.Replace('/', [IO.Path]::DirectorySeparatorChar))
        $summarySource = $sourceBindings.PSObject.Properties[$relative].Value
        $fixtureSource = $fixtureSourceBindings.PSObject.Properties[$relative].Value
        $preflightSource = $preflightSourceBindings.PSObject.Properties[$relative].Value
        if ($fixtureSource.path -cne $summarySource.path -or
            [int64]$fixtureSource.bytes -ne [int64]$summarySource.bytes -or
            ([string]$fixtureSource.sha256).ToLowerInvariant() -cne
                ([string]$summarySource.sha256).ToLowerInvariant() -or
            $preflightSource.path -cne $summarySource.path -or
            [int64]$preflightSource.bytes -ne [int64]$summarySource.bytes -or
            ([string]$preflightSource.sha256).ToLowerInvariant() -cne
                ([string]$summarySource.sha256).ToLowerInvariant() -or
            ([string]$sourceHashes.PSObject.Properties[$relative].Value).ToLowerInvariant() -cne
                ([string]$summarySource.sha256).ToLowerInvariant() -or
            ([string]$fixtureSourceHashes.PSObject.Properties[$relative].Value).ToLowerInvariant() -cne
                ([string]$summarySource.sha256).ToLowerInvariant() -or
            ([string]$preflightSourceHashes.PSObject.Properties[$relative].Value).ToLowerInvariant() -cne
                ([string]$summarySource.sha256).ToLowerInvariant()) {
            throw "T57 prepare/fixture/source-hash 三方绑定不一致：$relative"
        }
        $null = Assert-T57BoundFile -ExpectedPath $expectedPath -Record $summarySource -Label "T57 $relative"
    }

    $compileBindings = @($preparation.bindings.simulation_compile_sources)
    $fixtureCompileBindings = @($fixture.simulation_compile_sources)
    $preflightCompileBindings = @($preparation.project_preflight.simulation_compile_sources)
    if ($compileBindings.Count -ne $ExpectedCompileSourceRelPaths.Count -or
        $fixtureCompileBindings.Count -ne $ExpectedCompileSourceRelPaths.Count -or
        $preflightCompileBindings.Count -ne $ExpectedCompileSourceRelPaths.Count) {
        throw "T57 project-preflight/fixture 实际编译源数量不匹配"
    }
    for ($index = 0; $index -lt $ExpectedCompileSourceRelPaths.Count; $index++) {
        $relative = $ExpectedCompileSourceRelPaths[$index]
        $expectedPath = Join-Path $RepositoryRoot ($relative.Replace('/', [IO.Path]::DirectorySeparatorChar))
        $sourceRecord = $compileBindings[$index]
        foreach ($record in @($sourceRecord, $fixtureCompileBindings[$index], $preflightCompileBindings[$index])) {
            if ($record.path -cne $sourceRecord.path -or
                [int64]$record.bytes -ne [int64]$sourceRecord.bytes -or
                ([string]$record.sha256).ToLowerInvariant() -cne ([string]$sourceRecord.sha256).ToLowerInvariant()) {
                throw "T57 compile source bindings diverge: $relative"
            }
        }
        if ([IO.Path]::GetFullPath([string]$sourceRecord.path) -cne
            [IO.Path]::GetFullPath($expectedPath) -or
            ([string]$sourceRecord.sha256).ToLowerInvariant() -cne
                ([string]$sourceBindings.PSObject.Properties[$relative].Value.sha256).ToLowerInvariant()) {
            throw "T57 compile source path/hash is not an exact T57 source binding: $relative"
        }
        $null = Assert-T57BoundFile -ExpectedPath $expectedPath -Record $sourceRecord -Label "T57 compile source $relative"
    }

    $customTclRecord = $preparation.bindings.xsim_custom_tcl
    if ($fixture.xsim_custom_tcl.path -cne $customTclRecord.path -or
        [int64]$fixture.xsim_custom_tcl.bytes -ne [int64]$customTclRecord.bytes -or
        ([string]$fixture.xsim_custom_tcl.sha256).ToLowerInvariant() -cne
            ([string]$customTclRecord.sha256).ToLowerInvariant()) {
        throw "T57 custom XSim Tcl summary/fixture 绑定不一致"
    }
    $null = Assert-T57BoundFile -ExpectedPath $XsimTclPath -Record $customTclRecord -Label "T57 run09 custom XSim Tcl"

    $sourceManifestRecord = $preparation.bindings.compile_source_manifest
    if ($fixture.compile_source_manifest.path -cne $sourceManifestRecord.path -or
        [int64]$fixture.compile_source_manifest.bytes -ne [int64]$sourceManifestRecord.bytes -or
        ([string]$fixture.compile_source_manifest.sha256).ToLowerInvariant() -cne
            ([string]$sourceManifestRecord.sha256).ToLowerInvariant()) {
        throw "T57 compile-source manifest summary/fixture 绑定不一致"
    }
    if ($preparation.project_preflight.compile_source_manifest.path -cne $sourceManifestRecord.path -or
        [int64]$preparation.project_preflight.compile_source_manifest.bytes -ne [int64]$sourceManifestRecord.bytes -or
        ([string]$preparation.project_preflight.compile_source_manifest.sha256).ToLowerInvariant() -cne
            ([string]$sourceManifestRecord.sha256).ToLowerInvariant()) {
        throw "T57 compile-source manifest project-preflight 绑定不一致"
    }
    $sourceManifestSha = Assert-T57BoundFile -ExpectedPath $CompileSourceManifestPath `
        -Record $sourceManifestRecord -Label "T57 compile-source manifest"
    $manifestLines = [Collections.Generic.List[string]]::new()
    $manifestLines.Add("GestureForge-S2A-T57-compile-source-manifest-v1")
    foreach ($record in $compileBindings) {
        $manifestLines.Add(([string]$record.sha256).ToLowerInvariant() + "`t" +
            [string]([int64]$record.bytes) + "`t" + [string]$record.path)
    }
    $expectedManifestText = ($manifestLines -join "`n") + "`n"
    $actualManifestText = [IO.File]::ReadAllText($CompileSourceManifestPath, [Text.Encoding]::UTF8)
    if ($actualManifestText -cne $expectedManifestText) {
        throw "T57 compile-source manifest 内容与项目实际源绑定不一致"
    }

    $preflightRecord = $preparation.project_preflight.binding_file
    $preflightPath = [IO.Path]::GetFullPath([string]$preparation.project_preflight.path)
    if (-not [string]::Equals($preflightPath, [IO.Path]::GetFullPath($BindingPath), [StringComparison]::OrdinalIgnoreCase)) {
        throw "T57 project-preflight 文件路径不匹配：$preflightPath"
    }
    $null = Assert-T57BoundFile -ExpectedPath $BindingPath -Record $preflightRecord -Label "T57 project-preflight binding"
    if ((Get-T57Sha256 -Path $BindingPath) -cne ([string]$preparation.project_preflight.sha256).ToLowerInvariant()) {
        throw "T57 project-preflight SHA 与 prepare summary 不匹配"
    }
    $projectBinding = [IO.File]::ReadAllText($BindingPath, [Text.Encoding]::UTF8) | ConvertFrom-Json -ErrorAction Stop
    if ($projectBinding.project_name -cne $ExpectedProjectName -or
        [IO.Path]::GetFullPath([string]$projectBinding.project_path) -cne [IO.Path]::GetFullPath($XprPath) -or
        [string]$projectBinding.xpr_sha256_before_run -cne [string]$preparation.project_preflight.target_xpr_sha256 -or
        [int]$projectBinding.preflight_exit_code -ne 0) {
        throw "T57 project-preflight target XPR binding is invalid"
    }
    return [pscustomobject]@{
        prepare_summary_sha256 = Get-T57Sha256 -Path $PrepareSummaryPath
        fixture_manifest_sha256 = Get-T57Sha256 -Path $FixtureManifestPath
        compile_source_manifest_sha256 = $sourceManifestSha
        compile_source_count = $compileBindings.Count
        source_binding_count = $ExpectedT57SourceRelPaths.Count
        python_runner_sha256 = [string]$sourceBindings.PSObject.Properties['verification/test_s2a_conv_layer35_row21_all_channels_rtl.py'].Value.sha256
    }
}

function Set-T57JsonField {
    param(
        [Parameter(Mandatory = $true)]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter()][AllowNull()]$Value
    )
    $Object | Add-Member -MemberType NoteProperty -Name $Name -Value $Value -Force
}

function Get-T57TranscriptEvidence {
    param([Parameter(Mandatory = $true)][string]$Text)
    $sentinelCount = [regex]::Matches($Text, '(?m)^T57_CUSTOM_TCL_SENTINEL=run09_attempt09[ \t]*\r?$').Count
    $passCount = [regex]::Matches($Text, '(?m)^PASS T57 outputs=').Count
    $progressMatches = [regex]::Matches($Text, '(?m)^PROGRESS T57 outputs=(\d+)/6656[ \t]*\r?$')
    $progressValues = @($progressMatches | ForEach-Object { [int]$_.Groups[1].Value })
    $expectedProgress = @(for ($value = 26; $value -le 6656; $value += 26) { $value })
    $progressMatchesExpected = ($progressValues.Count -eq 256 -and
        (($progressValues -join ",") -ceq ($expectedProgress -join ",")))
    $finishMatches = [regex]::Matches($Text, '\$finish called at time[ \t]*:[ \t]*(\d+)[ \t]+ns')
    $finishTimeNs = $null
    if ($finishMatches.Count -eq 1) {
        $finishTimeNs = [long]$finishMatches[0].Groups[1].Value
    }
    $hasError = [regex]::IsMatch($Text, '(?im)^[ \t]*(?:ERROR|FATAL)(?:[ \t]|:)')
    return [pscustomobject]@{
        sentinel_count = $sentinelCount
        pass_line_count = $passCount
        progress_checkpoint_count = $progressValues.Count
        progress_matches_expected = $progressMatchesExpected
        finish_time_ns = $finishTimeNs
        has_error = $hasError
        complete = ($sentinelCount -eq 1 -and $passCount -eq 1 -and
            $progressMatchesExpected -and $null -ne $finishTimeNs -and
            $finishTimeNs -gt 1000 -and -not $hasError)
    }
}

function Complete-T57StageStatus {
    param(
        [Parameter(Mandatory = $true)][string]$RunDirectory,
        [Parameter(Mandatory = $true)][string]$XsimTclPath,
        [Parameter(Mandatory = $true)][string]$TranscriptRunnerPath,
        [Parameter(Mandatory = $true)][string]$PythonExecutable,
        [Parameter(Mandatory = $true)][string]$ExpectedTranscriptRunnerSha256,
        [Parameter(Mandatory = $true)][AllowNull()][object]$VivadoExitCode,
        [Parameter(Mandatory = $true)][string]$ExpectedXprSha256,
        [Parameter(Mandatory = $true)][string]$ExpectedCompileSourceManifestSha256,
        [Parameter(Mandatory = $true)][bool]$XprUnchanged,
        [Parameter(Mandatory = $true)][int]$RemainingProcessCount,
        [Parameter(Mandatory = $true)][bool]$CleanupVerified,
        [Parameter()][AllowEmptyString()][string]$RunFailure = ""
    )
    $statusPath = Join-Path $RunDirectory "stage_status.json"
    if (-not (Test-Path -LiteralPath $statusPath -PathType Leaf)) {
        return [pscustomobject]@{ exit_code = 1; status = "MISSING"; failure = "缺少 stage_status.json"; finalized = $false; stage_status_sha256 = $null }
    }
    $statusItem = Get-Item -LiteralPath $statusPath -ErrorAction Stop
    if (($statusItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        return [pscustomobject]@{ exit_code = 1; status = "INVALID"; failure = "stage_status.json 是 reparse point"; finalized = $false; stage_status_sha256 = $null }
    }
    try {
        $stage = [IO.File]::ReadAllText($statusPath, [Text.Encoding]::UTF8) | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return [pscustomobject]@{ exit_code = 1; status = "INVALID"; failure = "stage_status.json 解析失败：$($_.Exception.Message)"; finalized = $false; stage_status_sha256 = $null }
    }

    $reasons = [Collections.Generic.List[string]]::new()
    $consolePath = Join-Path $RunDirectory "vivado_batch_console.log"
    $extractedTranscriptPath = Join-Path $RunDirectory "xsim_simulate_transcript.log"
    $transcriptPath = $consolePath
    $transcriptSource = "vivado_batch_console.log"
    $transcriptText = ""
    $transcriptFacts = $null
    $transcriptExtractionExitCode = $null
    $transcriptExtractionRecord = $null
    $transcriptExtractionFailure = $null
    $transcriptOriginSha256 = $null
    if (Test-Path -LiteralPath $consolePath -PathType Leaf) {
        try {
            if ((Get-T57Sha256 -Path $TranscriptRunnerPath) -cne
                $ExpectedTranscriptRunnerSha256.ToLowerInvariant()) {
                throw "transcript extractor runner SHA 与启动前绑定不一致"
            }
            $extractArguments = @("-B", $TranscriptRunnerPath, "--extract-console-transcript")
            $extractOutput = @(& $PythonExecutable @extractArguments 2>&1)
            $transcriptExtractionExitCode = [int]$LASTEXITCODE
            if ($transcriptExtractionExitCode -ne 0) {
                throw "Python transcript extractor 返回非零：$transcriptExtractionExitCode；$($extractOutput -join ' ')"
            }
            $extractJson = [string]::Join([Environment]::NewLine, [string[]]$extractOutput)
            $transcriptExtractionRecord = $extractJson | ConvertFrom-Json -ErrorAction Stop
            $transcriptOriginSha256 = Get-T57Sha256 -Path $consolePath
            $expectedTranscriptPath = [IO.Path]::GetFullPath($extractedTranscriptPath)
            $expectedConsolePath = [IO.Path]::GetFullPath($consolePath)
            if ($transcriptExtractionRecord.schema -cne "S2A-T57-xsim-transcript-extraction-v1" -or
                $transcriptExtractionRecord.status -cne "PASS" -or
                $transcriptExtractionRecord.algorithm -cne "byte_lines_unique_sentinel_through_unique_finish_v1" -or
                -not [string]::Equals([IO.Path]::GetFullPath([string]$transcriptExtractionRecord.source.path),
                    $expectedConsolePath, [StringComparison]::OrdinalIgnoreCase) -or
                [int64]$transcriptExtractionRecord.source.bytes -ne (Get-Item -LiteralPath $consolePath).Length -or
                $transcriptExtractionRecord.source.sha256 -cne $transcriptOriginSha256 -or
                -not [string]::Equals([IO.Path]::GetFullPath([string]$transcriptExtractionRecord.transcript.path),
                    $expectedTranscriptPath, [StringComparison]::OrdinalIgnoreCase) -or
                [int64]$transcriptExtractionRecord.transcript.bytes -ne (Get-Item -LiteralPath $extractedTranscriptPath).Length -or
                $transcriptExtractionRecord.transcript.sha256 -cne (Get-T57Sha256 -Path $extractedTranscriptPath)) {
                throw "Python transcript extractor 返回值未绑定本轮 console 与 transcript 文件"
            }
            $transcriptPath = $extractedTranscriptPath
            $transcriptText = [IO.File]::ReadAllText($transcriptPath, [Text.Encoding]::UTF8)
            $transcriptFacts = Get-T57TranscriptEvidence -Text $transcriptText
            if (-not $transcriptFacts.complete) {
                throw "截取后的 XSim transcript 不完整"
            }
            $transcriptSource = "xsim_simulate_transcript.log"
        }
        catch {
            $transcriptExtractionFailure = $_.Exception.Message
            $reasons.Add("XSim transcript 提取失败：$transcriptExtractionFailure")
        }
    }
    else {
        $transcriptExtractionFailure = "缺少 vivado_batch_console.log"
        $reasons.Add($transcriptExtractionFailure)
    }
    $originalStatus = [string]$stage.status
    if ($stage.schema -cne "GestureForge-S2A-T57-isolated-simulation-status-v5") {
        $reasons.Add("stage_status schema 不匹配")
    }
    if ($originalStatus -notin @("SIMULATION_FLOW_RUNNING", "SIMULATION_FLOW_PASS")) {
        $reasons.Add("Vivado Tcl 终态不可接受：$originalStatus")
    }
    if ($stage.data_verification_status -cne "DATA_VERIFICATION_PENDING" -or
        $null -ne $stage.data_verification_report) {
        $reasons.Add("stage_status 不再保持 DATA_VERIFICATION_PENDING")
    }
    if ($stage.compile_exit_code -ne 0 -or $stage.elaboration_exit_code -ne 0) {
        $reasons.Add("compile/elaboration 状态未全部为 0")
    }
    if ($null -ne $stage.simulate_step_tcl_code -and
        [int]$stage.simulate_step_tcl_code -ne 0) {
        $reasons.Add("Vivado simulate step Tcl 返回非零")
    }
    if ($stage.source_project_xpr_sha256 -cne $ExpectedXprSha256) {
        $reasons.Add("stage_status 源 XPR 哈希不匹配")
    }
    $expectedManifestPath = [IO.Path]::GetFullPath((Join-Path $RunDirectory "compile_source_manifest.tsv"))
    if (-not [string]::Equals([IO.Path]::GetFullPath([string]$stage.compile_source_manifest_path),
            $expectedManifestPath, [StringComparison]::OrdinalIgnoreCase) -or
        $stage.compile_source_manifest_sha256 -cne $ExpectedCompileSourceManifestSha256) {
        $reasons.Add("stage_status compile-source manifest path/SHA 不匹配")
    }
    if ($stage.simset -cne "sim_s2a_t57_row21" -or
        $stage.top -cne "tb_s2a_conv_layer35_row21_all_channels") {
        $reasons.Add("stage_status 仿真集或顶层不匹配")
    }
    if ($stage.runtime_property_empty -ne $true -or
        $stage.runtime_control -cne "CUSTOM_TCL_RUN_ALL" -or
        $stage.effective_debug_level -cne "off" -or
        $stage.log_all_signals -ne 0) {
        $reasons.Add("no-wave runtime/debug 属性未满足冻结配置")
    }
    try {
        if (-not [string]::Equals([IO.Path]::GetFullPath([string]$stage.custom_tcl_path),
                [IO.Path]::GetFullPath($XsimTclPath), [StringComparison]::OrdinalIgnoreCase)) {
            $reasons.Add("stage_status custom Tcl 路径不匹配")
        }
    }
    catch {
        $reasons.Add("stage_status custom Tcl 路径无效")
    }

    $requiredNames = @(
        "vivado_batch_console.log", "xsim_simulate_transcript.log", "compile.log", "elaborate.log", "xsim_run.tcl", "compile_source_manifest.tsv",
        "observed_raw.bin", "observed_output.bin",
        "elaborate.before_compile.bat", "elaborate.after_compile.bat", "elaborate.after_elaborate.bat",
        "simulate.before_compile.bat", "simulate.after_compile.bat", "simulate.after_elaborate.bat"
    )
    $missingNames = [Collections.Generic.List[string]]::new()
    foreach ($name in $requiredNames) {
        $path = Join-Path $RunDirectory $name
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            $missingNames.Add($name)
            continue
        }
        $item = Get-Item -LiteralPath $path -ErrorAction Stop
        if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
            $reasons.Add("必需证据是 reparse point：$name")
        }
    }
    if ($missingNames.Count -gt 0) {
        $reasons.Add("缺少运行证据：$($missingNames -join ', ')")
    }

    $transcriptOriginSha256 = if ($null -ne $transcriptOriginSha256) {
        $transcriptOriginSha256
    } elseif (Test-Path -LiteralPath $consolePath -PathType Leaf) {
        Get-T57Sha256 -Path $consolePath
    } else { $null }
    $sentinelCount = $transcriptFacts.sentinel_count
    $passCount = $transcriptFacts.pass_line_count
    $progressMatchesExpected = $transcriptFacts.progress_matches_expected
    $finishTimeNs = $transcriptFacts.finish_time_ns
    $transcriptHasError = $transcriptFacts.has_error
    $progressCheckpointCount = $transcriptFacts.progress_checkpoint_count
    $transcriptComplete = $transcriptFacts.complete
    if (-not $transcriptComplete) {
        $reasons.Add("Vivado/XSim transcript 不完整：custom=$sentinelCount pass=$passCount progress=$progressCheckpointCount finish=$finishTimeNs errors=$transcriptHasError")
    }
    $elaborateLogPath = Join-Path $RunDirectory "elaborate.log"
    $elaborateHasSnapshot = $false
    if (Test-Path -LiteralPath $elaborateLogPath -PathType Leaf) {
        $elaborateHasSnapshot = [IO.File]::ReadAllText($elaborateLogPath, [Text.Encoding]::UTF8).Contains("Built simulation snapshot tb_s2a_conv_layer35_row21_all_channels_behav")
    }
    if (-not $elaborateHasSnapshot) {
        $reasons.Add("elaborate.log 未证明目标 snapshot")
    }
    if (-not [string]::IsNullOrEmpty([string]$stage.simulate_command_signature)) {
        $signature = [string]$stage.simulate_command_signature
        $expectedBatchPath = [IO.Path]::GetFullPath($XsimTclPath).Replace([char]92, [char]47)
        $expectedSnapshot = "tb_s2a_conv_layer35_row21_all_channels_behav"
        $expectedSnapshotKey = "Behavioral:sim_s2a_t57_row21:Functional:tb_s2a_conv_layer35_row21_all_channels"
        $batchMatches = [regex]::Matches($signature, '(?i)(?:^|[ \t])-tclbatch[ \t]+(?:"([^"]+)"|\{([^}]+)\}|([^ \t]+))')
        $testplusargMatches = [regex]::Matches($signature, '(?i)(?:^|[ \t])-testplusarg[ \t]+(?:"([^"]+)"|\{([^}]+)\}|([^ \t]+))')
        $batchValue = ""
        if ($batchMatches.Count -eq 1) {
            foreach ($groupIndex in 1..3) {
                if ($batchMatches[0].Groups[$groupIndex].Success) {
                    $batchValue = $batchMatches[0].Groups[$groupIndex].Value
                    break
                }
            }
        }
        $testplusargValue = ""
        if ($testplusargMatches.Count -eq 1) {
            foreach ($groupIndex in 1..3) {
                if ($testplusargMatches[0].Groups[$groupIndex].Success) {
                    $testplusargValue = $testplusargMatches[0].Groups[$groupIndex].Value
                    break
                }
            }
        }
        $expectedRunRootArgument = "T57_RUN_ROOT=" + [IO.Path]::GetFullPath($RunDirectory).Replace([char]92, [char]47)
        if ($batchMatches.Count -ne 1 -or $batchValue.Contains([char]92) -or
            -not [string]::Equals($batchValue, $expectedBatchPath, [StringComparison]::OrdinalIgnoreCase) -or
            $testplusargMatches.Count -ne 1 -or
            -not [string]::Equals($testplusargValue, $expectedRunRootArgument, [StringComparison]::Ordinal) -or
            -not $signature.Contains($expectedSnapshot) -or
            -not $signature.Contains($expectedSnapshotKey) -or
            [regex]::IsMatch($signature, '(?i)(?:^|[ \t])-wdb(?:[ \t=]|$)')) {
            $reasons.Add("唯一 xsim 签名未绑定目标 snapshot/top、run09/attempt09 custom Tcl/testplusarg 或启用了 WDB")
        }
    }
    else {
        $reasons.Add("stage_status 缺少 xsim 命令签名")
    }

    $rawPath = Join-Path $RunDirectory "observed_raw.bin"
    $int8Path = Join-Path $RunDirectory "observed_output.bin"
    $rawBytes = if (Test-Path -LiteralPath $rawPath -PathType Leaf) { (Get-Item -LiteralPath $rawPath).Length } else { $null }
    $int8Bytes = if (Test-Path -LiteralPath $int8Path -PathType Leaf) { (Get-Item -LiteralPath $int8Path).Length } else { $null }
    if ($rawBytes -ne 26624 -or $int8Bytes -ne 6656) {
        $reasons.Add("observed raw/INT8 文件缺失或长度不匹配")
    }
    $wdbFiles = @(Get-ChildItem -LiteralPath $RunDirectory -Filter "*.wdb" -File -Recurse -Force -ErrorAction SilentlyContinue)
    if ($wdbFiles.Count -gt 0 -or (Test-Path -LiteralPath (Join-Path $RunDirectory "project_simulation_errors.log"))) {
        $reasons.Add("运行目录包含 WDB 或 Vivado 仿真错误记录")
    }
    if ($null -eq $VivadoExitCode -or [int]$VivadoExitCode -ne 0) {
        $reasons.Add("Vivado batch 主进程未捕获到退出码 0")
    }
    if (-not $XprUnchanged -or $RemainingProcessCount -ne 0 -or -not $CleanupVerified) {
        $reasons.Add("XPR、进程归零或隔离工程清理门未通过")
    }
    if (-not [string]::IsNullOrWhiteSpace($RunFailure)) {
        $reasons.Add("Vivado wrapper 运行失败：$RunFailure")
    }

    $finalStatus = if ($reasons.Count -eq 0) { "SIMULATION_FLOW_PASS" } else { "SIMULATION_FLOW_FAIL" }
    Set-T57JsonField -Object $stage -Name "status" -Value $finalStatus
    Set-T57JsonField -Object $stage -Name "data_verification_status" -Value "DATA_VERIFICATION_PENDING"
    Set-T57JsonField -Object $stage -Name "data_verification_report" -Value $null
    Set-T57JsonField -Object $stage -Name "custom_tcl_executed" -Value ($sentinelCount -eq 1)
    Set-T57JsonField -Object $stage -Name "simulate_log_complete" -Value $transcriptComplete
    Set-T57JsonField -Object $stage -Name "finish_time_ns" -Value $finishTimeNs
    Set-T57JsonField -Object $stage -Name "xsim_exit_code" -Value $null
    Set-T57JsonField -Object $stage -Name "xsim_exit_code_captured" -Value $false
    Set-T57JsonField -Object $stage -Name "xsim_exit_code_source" -Value $null
    Set-T57JsonField -Object $stage -Name "vivado_process_exit_code" -Value $VivadoExitCode
    Set-T57JsonField -Object $stage -Name "simulate_log_path" -Value ([IO.Path]::GetFullPath($transcriptPath))
    Set-T57JsonField -Object $stage -Name "simulate_log_source" -Value $transcriptSource
    Set-T57JsonField -Object $stage -Name "simulate_log_sha256" -Value $(if (Test-Path -LiteralPath $transcriptPath -PathType Leaf) { (Get-FileHash -LiteralPath $transcriptPath -Algorithm SHA256).Hash.ToLowerInvariant() } else { $null })
    Set-T57JsonField -Object $stage -Name "simulate_log_bytes" -Value $(if (Test-Path -LiteralPath $transcriptPath -PathType Leaf) { (Get-Item -LiteralPath $transcriptPath).Length } else { $null })
    Set-T57JsonField -Object $stage -Name "simulate_log_origin_path" -Value ([IO.Path]::GetFullPath($consolePath))
    Set-T57JsonField -Object $stage -Name "simulate_log_origin_sha256" -Value $transcriptOriginSha256
    Set-T57JsonField -Object $stage -Name "simulate_log_origin_bytes" -Value $(if (Test-Path -LiteralPath $consolePath -PathType Leaf) { (Get-Item -LiteralPath $consolePath).Length } else { $null })
    Set-T57JsonField -Object $stage -Name "simulate_log_extraction_algorithm" -Value "byte_lines_unique_sentinel_through_unique_finish_v1"
    Set-T57JsonField -Object $stage -Name "simulate_log_extraction_status" -Value $(if ($transcriptComplete) { "PASS" } else { "FAIL" })
    Set-T57JsonField -Object $stage -Name "simulate_log_extraction_exit_code" -Value $transcriptExtractionExitCode
    Set-T57JsonField -Object $stage -Name "simulate_log_extraction_line_range" -Value $(if ($null -ne $transcriptExtractionRecord) { $transcriptExtractionRecord.line_range_1based_inclusive } else { $null })
    Set-T57JsonField -Object $stage -Name "wdb_generated" -Value ($wdbFiles.Count -gt 0)
    Set-T57JsonField -Object $stage -Name "failure" -Value ($reasons -join "; ")
    Set-T57JsonField -Object $stage -Name "wrapper_finalization" -Value ([ordered]@{
        source = "PowerShell wrapper"
        original_status = $originalStatus
        terminal_status = $finalStatus
        transcript_source = $transcriptSource
        transcript_origin = "vivado_batch_console.log"
        transcript_origin_sha256 = $transcriptOriginSha256
        transcript_extraction_algorithm = "byte_lines_unique_sentinel_through_unique_finish_v1"
        transcript_extraction_exit_code = $transcriptExtractionExitCode
        transcript_extraction_failure = $transcriptExtractionFailure
        transcript_extraction_line_range = $(if ($null -ne $transcriptExtractionRecord) { $transcriptExtractionRecord.line_range_1based_inclusive } else { $null })
        sentinel_count = $sentinelCount
        pass_line_count = $passCount
        progress_checkpoint_count = $progressCheckpointCount
        finish_time_ns = $finishTimeNs
        xsim_exit_code_captured = $false
    })
    $temporaryPath = $statusPath + ".r9tmp"
    if (Test-Path -LiteralPath $temporaryPath) {
        return [pscustomobject]@{ exit_code = 1; status = "INVALID"; failure = "stage_status 临时文件已存在"; finalized = $false; stage_status_sha256 = $null }
    }
    $json = ConvertTo-Json -InputObject $stage -Depth 10
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($json + [Environment]::NewLine)
    $stream = [IO.File]::Open($temporaryPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush($true)
    }
    finally {
        $stream.Dispose()
    }
    $backupPath = $statusPath + ".r9bak"
    if (Test-Path -LiteralPath $backupPath) {
        throw "stage_status 备份文件已存在：$backupPath"
    }
    [IO.File]::Replace($temporaryPath, $statusPath, $backupPath)
    [IO.File]::Delete($backupPath)
    $statusSha256 = (Get-FileHash -LiteralPath $statusPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $failureText = $reasons -join "; "
    return [pscustomobject]@{
        exit_code = if ($finalStatus -eq "SIMULATION_FLOW_PASS") { 0 } else { 1 }
        status = $finalStatus
        failure = $failureText
        finalized = $true
        stage_status_sha256 = $statusSha256
    }
}

function Write-T57JsonCreateNew {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)]$Value
    )
    $json = ConvertTo-Json -InputObject $Value -Depth 8
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($json + [Environment]::NewLine)
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try {
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush($true)
    }
    finally {
        $stream.Dispose()
    }
}

function Test-T57ScratchPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    $null = @(Get-T57VerifiedDirectoryChain -Path $RunDirectory)
    $full = [IO.Path]::GetFullPath($Path)
    $runFull = [IO.Path]::GetFullPath($RunDirectory)
    $parent = [IO.Path]::GetDirectoryName($full)
    $leaf = [IO.Path]::GetFileName($full)
    if (-not [string]::Equals($parent, $runFull, [StringComparison]::OrdinalIgnoreCase) -or
        $leaf -cne "isolated_project" -or
        -not [string]::Equals($full, $ExpectedScratchDirectory, [StringComparison]::OrdinalIgnoreCase)) {
        throw "隔离工程清理路径不等于固定的 run09\isolated_project：$full"
    }
    return $full
}

$RunDirectoryChainBefore = @(Get-T57VerifiedDirectoryChain -Path $RunDirectory)
if (-not [string]::Equals([IO.Path]::GetFullPath($RunDirectory), $ExpectedRunDirectory,
        [StringComparison]::OrdinalIgnoreCase)) {
    throw "run09 路径不等于固定证据目录：$RunDirectory"
}
$repositoryActual = [IO.Path]::GetFullPath($RepositoryRoot)
if (-not [string]::Equals($repositoryActual, $ExpectedRepositoryRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw "仓库根目录不匹配：$repositoryActual"
}
foreach ($requiredPath in @($VivadoPath, $TclPath, $XprPath, $BindingPath, $XsimTclPath,
        $PrepareSummaryPath, $FixtureManifestPath, $CompileSourceManifestPath,
        $T57RunnerPath, $PythonPath, $RunDirectory)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf) -and
        -not ($requiredPath -eq $RunDirectory -and (Test-Path -LiteralPath $requiredPath -PathType Container))) {
        throw "必需路径不存在或类型错误：$requiredPath"
    }
}
$ScratchFullPath = Test-T57ScratchPath -Path $ScratchDirectory
$RunFullPath = [IO.Path]::GetFullPath($RunDirectory)
if ([IO.Path]::GetFullPath((Split-Path -Parent $XprPath)) -cne
    [IO.Path]::GetFullPath((Join-Path $RepositoryRoot "vivado\AX7Z020_Gesture"))) {
    throw "真实工程路径校验失败"
}

$binding = Get-Content -LiteralPath $BindingPath -Raw -Encoding UTF8 | ConvertFrom-Json
$expectedXprPath = [IO.Path]::GetFullPath($XprPath)
if ($binding.project_name -cne $ExpectedProjectName -or
    -not [string]::Equals([IO.Path]::GetFullPath([string]$binding.project_path), $expectedXprPath, [StringComparison]::OrdinalIgnoreCase)) {
    throw "工程预检绑定没有指向精确的 AX7Z020_Gesture XPR"
}
if ([int]$binding.preflight_exit_code -ne 0) {
    throw "工程只读预检未通过"
}
$XprShaBefore = Get-T57Sha256 -Path $XprPath
if ($XprShaBefore -cne ([string]$binding.xpr_sha256_before_run).ToLowerInvariant()) {
    throw "目标 XPR SHA-256 与当前只读预检绑定不匹配"
}
if ($Mode -eq "recover") {
    if (-not [string]::Equals($RunFullPath, $ExpectedRunDirectory,
            [StringComparison]::OrdinalIgnoreCase)) {
        throw "recover 仅允许固定 attempt09 根目录：$RunFullPath"
    }
    $recoverBefore = @(Get-T57ProcessSnapshot)
    if ($recoverBefore.Count -ne 0) {
        throw "recover 启动前发现 Vivado/XSim 进程，拒绝修改 attempt09 状态"
    }
    $recoverArguments = @("-X", "utf8", "-B", $T57RunnerPath, "--recover-attempt09")
    Push-Location -LiteralPath $RepositoryRoot
    try {
        & $PythonPath @recoverArguments
        $recoverExitCode = [int]$LASTEXITCODE
    }
    finally {
        Pop-Location
    }
    $recoverAfter = @(Get-T57ProcessSnapshot)
    if ($recoverAfter.Count -ne 0) {
        throw "recover 结束后发现 Vivado/XSim 进程"
    }
    if ($recoverExitCode -ne 0) {
        throw "attempt09 recover runner 返回非零：$recoverExitCode"
    }
    Write-Output (ConvertTo-Json -InputObject ([ordered]@{
        result = "T57_ATTEMPT09_RECOVERY_PASS"
        run_directory = $RunFullPath
        python_command = @($PythonPath) + $recoverArguments
        vivado_processes_before = $recoverBefore
        vivado_processes_after = $recoverAfter
        vivado_started = $false
        xsim_started = $false
    }) -Depth 5 -Compress)
    exit 0
}
$StartupBindings = Assert-T57StartupSourceBindings -RunDirectory $RunDirectory
$CompileSourceManifestSha256 = $StartupBindings.compile_source_manifest_sha256
$SimulationTclSha = Get-T57Sha256 -Path $TclPath
$LauncherScriptSha = Get-T57Sha256 -Path $PSCommandPath
$XsimTclSha = Get-T57Sha256 -Path $XsimTclPath

$before = @(Get-T57ProcessSnapshot)
$after = @()
$vivadoExitCode = $null
$scriptExitCode = 0
$runError = $null
$cleanupError = $null
$scratchCreated = $false
$scratchRemoved = $false
$ownerCreated = $false
$ownerRemoved = $false
$xprShaAfter = $null
$xprShaUnchanged = $false
$stageFinalization = $null
$consoleLog = $null
$batchLog = $null
$batchJournal = $null
$statusPath = $null
$commandDisplay = $null

if ($Mode -eq "run") {
    $consoleLog = Join-Path $RunDirectory "vivado_batch_console.log"
    $batchLog = Join-Path $RunDirectory "vivado_batch.log"
    $batchJournal = Join-Path $RunDirectory "vivado_batch.jou"
    $statusPath = Join-Path $RunDirectory "process_status.json"
}
else {
    $consoleLog = Join-Path $RunDirectory "t57_dryrun_vivado_batch_console.log"
    $batchLog = Join-Path $RunDirectory "t57_dryrun_vivado_batch.log"
    $batchJournal = Join-Path $RunDirectory "t57_dryrun_vivado_batch.jou"
    $statusPath = Join-Path $RunDirectory "t57_dryrun_process_status.json"
}
$guardPaths = @($OwnerMarker, $ScratchFullPath, $consoleLog, $batchLog, $batchJournal, $statusPath)
if ($Mode -eq "run") {
    $guardPaths += @(
        (Join-Path $RunDirectory "stage_status.json"),
        (Join-Path $RunDirectory "project_simulation_errors.log"),
        (Join-Path $RunDirectory "compile.log"),
        (Join-Path $RunDirectory "elaborate.log"),
        (Join-Path $RunDirectory "simulate.log"),
        (Join-Path $RunDirectory "observed_raw.bin"),
        (Join-Path $RunDirectory "observed_output.bin"),
        (Join-Path $RunDirectory "stage_status.json.r9tmp"),
        (Join-Path $RunDirectory "stage_status.json.r9bak"),
        $VerifyOnlyLogPath,
        $RunSummaryPath,
        $FinalReportPath,
        (Join-Path $RunDirectory "elaborate.before_compile.bat"),
        (Join-Path $RunDirectory "simulate.before_compile.bat"),
        (Join-Path $RunDirectory "elaborate.after_compile.bat"),
        (Join-Path $RunDirectory "simulate.after_compile.bat"),
        (Join-Path $RunDirectory "elaborate.after_elaborate.bat"),
        (Join-Path $RunDirectory "simulate.after_elaborate.bat")
    )
}
foreach ($path in $guardPaths) {
    if (Test-Path -LiteralPath $path) {
        throw "拒绝复用或覆盖已有路径：$path"
    }
}
if ($before.Count -ne 0) {
    $after = @(Get-T57ProcessSnapshot)
    $processStatus = [ordered]@{
        schema = "GestureForge-S2A-T57-isolated-process-status-v1"
        mode = $Mode
        vivado_process_exit_code = $null
        xpr_sha256_before = $XprShaBefore
        xpr_sha256_after = (Get-T57Sha256 -Path $XprPath)
        xpr_unchanged = ((Get-T57Sha256 -Path $XprPath) -ceq $XprShaBefore)
        unrelated_processes_before = $before
        unrelated_processes_after = $after
        source_project_name = $ExpectedProjectName
        source_project_xpr_path = $expectedXprPath
        scratch_project_name = $ExpectedScratchProjectName
        scratch_project_path = $ScratchFullPath
        scratch_project_xpr_path = Join-Path $ScratchFullPath "$ExpectedScratchProjectName.xpr"
        simulation_tcl_sha256 = $SimulationTclSha
        launcher_script_sha256 = $LauncherScriptSha
        xsim_tcl_sha256 = $XsimTclSha
        scratch_project_removed = $false
        owner_marker_removed = $false
        cleanup_verified = $false
        command = @()
        failure = "启动前发现未绑定 Vivado/XSim 进程，未启动仿真。"
    }
    Write-T57JsonCreateNew -Path $statusPath -Value $processStatus
    throw "启动门禁失败：已有 Vivado/XSim 进程；已记录 $statusPath"
}

try {
    $null = @(Get-T57VerifiedDirectoryChain -Path $RunDirectory)
    $ownerToken = [Guid]::NewGuid().ToString("N")
    $ownerContent = $ownerToken + [char]10 + $ScratchFullPath + [char]10
    $ownerBytes = [Text.UTF8Encoding]::new($false).GetBytes($ownerContent)
    $ownerStream = [IO.File]::Open($OwnerMarker, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    $ownerCreated = $true
    try {
        $ownerStream.Write($ownerBytes, 0, $ownerBytes.Length)
        $ownerStream.Flush($true)
    }
    finally {
        $ownerStream.Dispose()
    }
    if (Test-Path -LiteralPath $ScratchFullPath) {
        throw "隔离工程目录在启动前已出现：$ScratchFullPath"
    }
    [IO.Directory]::CreateDirectory($ScratchFullPath) | Out-Null
    $scratchCreated = $true
    $scratchItem = Get-Item -LiteralPath $ScratchFullPath -ErrorAction Stop
    if (-not $scratchItem.PSIsContainer -or
        (($scratchItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "隔离工程目标不是普通目录：$ScratchFullPath"
    }
    Assert-T57ScratchTreeSafe -Path $ScratchFullPath

    $tclArgs = @(
        "-mode", "batch",
        "-log", $batchLog,
        "-journal", $batchJournal,
        "-source", $TclPath,
        "-tclargs", $Mode, $XprShaBefore, $OwnerMarker, $ownerToken,
        $CompileSourceManifestPath, $CompileSourceManifestSha256
    )
    $displayArgs = @($tclArgs | ForEach-Object { '"' + ($_ -replace '"', '\"') + '"' }) -join " "
    $commandDisplay = '"' + $VivadoPath + '" ' + $displayArgs
    Push-Location -LiteralPath $ScratchFullPath
    try {
        & $VivadoPath @tclArgs *> $consoleLog
        $vivadoExitCode = [int]$LASTEXITCODE
    }
    finally {
        Pop-Location
    }
    if ($vivadoExitCode -ne 0) {
        throw "Vivado batch 返回非零退出码：$vivadoExitCode"
    }
}
catch {
    $runError = $_.Exception.Message
    if ($null -eq $vivadoExitCode -or $vivadoExitCode -eq 0) {
        $scriptExitCode = 1
    }
    else {
        $scriptExitCode = $vivadoExitCode
    }
}
finally {
    try {
        $after = @(Get-T57ProcessSnapshot)
        $xprShaAfter = Get-T57Sha256 -Path $XprPath
        if ($after.Count -ne 0) {
            throw "结束后仍有 Vivado/XSim 进程，保留隔离目录供诊断"
        }
        $xprShaUnchanged = $xprShaAfter -ceq $XprShaBefore
        if (-not $xprShaUnchanged) {
            if ($scriptExitCode -eq 0) {
                $scriptExitCode = 1
            }
            if ($null -eq $runError) {
                $runError = "目标 XPR SHA-256 在 T57 wrapper 运行期间发生变化"
            }
        }
        if ($ownerCreated) {
            if ($scratchCreated) {
                $null = @(Get-T57VerifiedDirectoryChain -Path $RunDirectory)
                $scratchRevalidated = Test-T57ScratchPath -Path $ScratchDirectory
                if (-not [string]::Equals($scratchRevalidated, $ScratchFullPath,
                        [StringComparison]::OrdinalIgnoreCase)) {
                    throw "清理前 scratch 路径发生变化，拒绝清理"
                }
                Assert-T57OwnerMarkerSafe
                $newline = [char]10
                $markerText = [IO.File]::ReadAllText($OwnerMarker, [Text.UTF8Encoding]::new($false)).TrimEnd([char[]]@([char]10))
                $markerParts = $markerText -split ([regex]::Escape([string]$newline)), 2
                if ($markerParts.Count -ne 2 -or
                    $markerParts[0] -cne $ownerToken -or
                    -not [string]::Equals([IO.Path]::GetFullPath($markerParts[1]), $ScratchFullPath, [StringComparison]::OrdinalIgnoreCase)) {
                    throw "隔离工程 owner 标记不匹配，拒绝清理"
                }
                if (Test-Path -LiteralPath $ScratchFullPath -PathType Container) {
                    $cleanupProcesses = @(Get-T57ProcessSnapshot)
                    if ($cleanupProcesses.Count -ne 0) {
                        throw "清理前发现 Vivado/XSim 进程，保留隔离工程目录"
                    }
                    Assert-T57ScratchTreeSafe -Path $ScratchFullPath
                    Clear-T57ScratchReadOnlyAttributes -Path $ScratchFullPath
                    $cleanupProcesses = @(Get-T57ProcessSnapshot)
                    if ($cleanupProcesses.Count -ne 0) {
                        throw "scratch 属性复核后发现 Vivado/XSim 进程，保留隔离工程目录"
                    }
                    $null = @(Get-T57VerifiedDirectoryChain -Path $RunDirectory)
                    $scratchRevalidated = Test-T57ScratchPath -Path $ScratchFullPath
                    if (-not [string]::Equals($scratchRevalidated, $ScratchFullPath,
                            [StringComparison]::OrdinalIgnoreCase)) {
                        throw "scratch 清理目标复核失败，拒绝递归删除"
                    }
                    Assert-T57OwnerMarkerSafe
                    Assert-T57ScratchTreeSafe -Path $ScratchFullPath
                    [IO.Directory]::Delete($ScratchFullPath, $true)
                }
                $scratchRemoved = -not (Test-Path -LiteralPath $ScratchFullPath)
                if (-not $scratchRemoved) {
                    throw "Vivado scratch 工程清理后仍存在：$ScratchFullPath"
                }
            }
            [IO.File]::Delete($OwnerMarker)
            $ownerRemoved = -not (Test-Path -LiteralPath $OwnerMarker)
        }
    }
    catch {
        $cleanupError = $_.Exception.Message
        if ($scriptExitCode -eq 0) {
            $scriptExitCode = 1
        }
        if ($null -eq $runError) {
            $runError = $cleanupError
        }
    }
    if ($null -eq $xprShaAfter) {
        try {
            $xprShaAfter = Get-T57Sha256 -Path $XprPath
        }
        catch {
            $xprShaAfter = $null
            if ($null -eq $runError) {
                $runError = $_.Exception.Message
            }
        }
    }
    if ($null -eq $after -or $after.Count -eq 0) {
        try {
            $after = @(Get-T57ProcessSnapshot)
        }
        catch {
            $after = @()
            if ($null -eq $runError) {
                $runError = $_.Exception.Message
            }
        }
    }
    $stageStatusPath = $null
    $stageStatusSha256 = $null
    $stageStatusTerminal = $null
    $stageStatusFinalized = $null
    if ($Mode -eq "run") {
        $stageStatusPath = [IO.Path]::GetFullPath((Join-Path $RunDirectory "stage_status.json"))
        try {
            $cleanupVerified = ($scratchRemoved -and $ownerRemoved -and $after.Count -eq 0 -and $null -eq $cleanupError)
            $stageFinalization = Complete-T57StageStatus `
                -RunDirectory $RunDirectory `
                -XsimTclPath $XsimTclPath `
                -TranscriptRunnerPath $T57RunnerPath `
                -PythonExecutable $PythonPath `
                -ExpectedTranscriptRunnerSha256 ([string]$StartupBindings.python_runner_sha256) `
                -VivadoExitCode $vivadoExitCode `
                -ExpectedXprSha256 $XprShaBefore `
                -ExpectedCompileSourceManifestSha256 $CompileSourceManifestSha256 `
                -XprUnchanged $xprShaUnchanged `
                -RemainingProcessCount $after.Count `
                -CleanupVerified $cleanupVerified `
                -RunFailure ([string]$runError)
            $stageStatusSha256 = $stageFinalization.stage_status_sha256
            $stageStatusTerminal = $stageFinalization.status
            $stageStatusFinalized = [bool]$stageFinalization.finalized
            if ($stageFinalization.exit_code -ne 0 -or
                $stageStatusTerminal -eq "SIMULATION_FLOW_RUNNING" -or -not $stageStatusFinalized) {
                $scriptExitCode = 1
                if ([string]::IsNullOrWhiteSpace([string]$runError)) {
                    $runError = [string]$stageFinalization.failure
                }
            }
        }
        catch {
            $stageFinalization = [pscustomobject]@{
                exit_code = 1
                status = "INVALID"
                failure = "T57 stage_status 归档失败：$($_.Exception.Message)"
                finalized = $false
                stage_status_sha256 = $null
            }
            $stageStatusTerminal = "INVALID"
            $stageStatusFinalized = $false
            $scriptExitCode = 1
            if ([string]::IsNullOrWhiteSpace([string]$runError)) {
                $runError = [string]$stageFinalization.failure
            }
        }
    }
    $processStatus = [ordered]@{
        schema = "GestureForge-S2A-T57-isolated-process-status-v1"
        mode = $Mode
        vivado_process_exit_code = $vivadoExitCode
        xpr_sha256_before = $XprShaBefore
        xpr_sha256_after = $xprShaAfter
        xpr_unchanged = $xprShaUnchanged
        unrelated_processes_before = $before
        unrelated_processes_after = $after
        source_project_name = $ExpectedProjectName
        source_project_xpr_path = $expectedXprPath
        scratch_project_name = $ExpectedScratchProjectName
        scratch_project_path = $ScratchFullPath
        scratch_project_xpr_path = Join-Path $ScratchFullPath "$ExpectedScratchProjectName.xpr"
        simulation_tcl_sha256 = $SimulationTclSha
        launcher_script_sha256 = $LauncherScriptSha
        xsim_tcl_sha256 = $XsimTclSha
        compile_source_manifest_sha256 = $CompileSourceManifestSha256
        startup_source_bindings = $StartupBindings
        data_verification_status = "DATA_VERIFICATION_PENDING"
        stage_status_path = $stageStatusPath
        stage_status_sha256 = $stageStatusSha256
        stage_status_terminal_status = $stageStatusTerminal
        stage_status_finalized = $stageStatusFinalized
        scratch_project_created = $scratchCreated
        scratch_project_removed = $scratchRemoved
        owner_marker_removed = $ownerRemoved
        cleanup_verified = ($scratchRemoved -and $ownerRemoved -and $after.Count -eq 0)
        command = $(if ($null -eq $commandDisplay) { @() } else { $commandDisplay })
        failure = $runError
        cleanup_failure = $cleanupError
    }
    try {
        Write-T57JsonCreateNew -Path $statusPath -Value $processStatus
    }
    catch {
        if ($scriptExitCode -eq 0) {
            $scriptExitCode = 1
        }
        Write-Error "无法新建 T57 process_status.json：$($_.Exception.Message)"
    }
}

if ($Mode -eq "run") {
    $overallStatus = "FAIL"
    $verificationStatus = "NOT_RUN"
    $verificationExitCode = $null
    $verificationFailure = $null
    $verificationReportSummary = $null
    if ($scriptExitCode -eq 0 -and $stageStatusTerminal -ceq "SIMULATION_FLOW_PASS" -and
        $stageStatusFinalized -eq $true -and $after.Count -eq 0 -and $xprShaUnchanged) {
        try {
            $runnerShaBeforeVerify = Get-T57Sha256 -Path $T57RunnerPath
            if ($runnerShaBeforeVerify -cne ([string]$StartupBindings.python_runner_sha256).ToLowerInvariant()) {
                throw "verify-only runner SHA 与启动前绑定不一致"
            }
            $verifyArguments = @("-B", $T57RunnerPath, "--verify-only")
            & $PythonPath @verifyArguments *> $VerifyOnlyLogPath
            $verificationExitCode = [int]$LASTEXITCODE
            if ($verificationExitCode -ne 0) {
                throw "同版本 Python runner --verify-only 返回非零：$verificationExitCode"
            }
            if (-not (Test-Path -LiteralPath $FinalReportPath -PathType Leaf)) {
                throw "verify-only 返回 0，但未生成最终数据报告"
            }
            $finalReportItem = Get-Item -LiteralPath $FinalReportPath -ErrorAction Stop
            if ($finalReportItem.PSIsContainer -or
                (($finalReportItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
                throw "verify-only 最终数据报告不是普通文件"
            }
            $dataReport = [IO.File]::ReadAllText($FinalReportPath, [Text.Encoding]::UTF8) | ConvertFrom-Json -ErrorAction Stop
            $rawMismatchBytes = [int64]$dataReport.simulation.raw_mismatch_bytes
            $int8MismatchBytes = [int64]$dataReport.simulation.int8_mismatch_bytes
            $d2MatchCount = [int64]$dataReport.oracle.d2_t23_match_count
            if ($dataReport.schema -cne "GestureForge-S2A-T57-layer35-row21-simulation-data-v2" -or
                $dataReport.task_id -cne "S2A-T57" -or
                $dataReport.status -cne "PASS_SIMULATION_DATA_ONLY" -or
                $dataReport.acceptance_status -cne "NOT_REVIEWED" -or
                [int64]$dataReport.simulation.raw_int32_compares -ne 6656 -or
                [int64]$dataReport.simulation.int8_compares -ne 6656 -or
                $rawMismatchBytes -ne 0 -or $int8MismatchBytes -ne 0 -or
                $d2MatchCount -ne 6656 -or
                $dataReport.simulation.raw_byte_identical_to_independent_golden -ne $true -or
                $dataReport.simulation.int8_byte_identical_to_independent_golden -ne $true -or
                $dataReport.simulation.custom_tcl_executed -ne $true -or
                $dataReport.simulation.wdb_generated -ne $false) {
                throw "verify-only 最终报告未满足 raw/INT8/D2 与仿真数据证据条件"
            }
            $reportArtifacts = $dataReport.simulation.artifacts
            if ($reportArtifacts.'stage_status.json'.sha256 -cne $stageStatusSha256 -or
                $reportArtifacts.'process_status.json'.sha256 -cne (Get-T57Sha256 -Path $statusPath)) {
                throw "verify-only 最终报告未绑定当前 stage/process 状态文件"
            }
            $verificationStatus = "PASS"
            $overallStatus = "PASS"
            $verificationReportSummary = [ordered]@{
                path = [IO.Path]::GetFullPath($FinalReportPath)
                bytes = $finalReportItem.Length
                sha256 = Get-T57Sha256 -Path $FinalReportPath
                status = $dataReport.status
                acceptance_status = $dataReport.acceptance_status
                raw_int32_compares = [int64]$dataReport.simulation.raw_int32_compares
                int8_compares = [int64]$dataReport.simulation.int8_compares
                raw_mismatch_bytes = $rawMismatchBytes
                int8_mismatch_bytes = $int8MismatchBytes
                d2_t23_match_count = $d2MatchCount
            }
        }
        catch {
            $verificationFailure = $_.Exception.Message
            $verificationStatus = "FAIL"
            $overallStatus = "FAIL"
            if ($scriptExitCode -eq 0) { $scriptExitCode = 1 }
        }
    }
    else {
        $verificationFailure = "Simulation-flow gate 未通过；未执行 data verify-only。"
        $verificationStatus = "NOT_RUN"
        $overallStatus = "FAIL"
        if ($scriptExitCode -eq 0) { $scriptExitCode = 1 }
    }
    $verifyLogSummary = $null
    if (Test-Path -LiteralPath $VerifyOnlyLogPath -PathType Leaf) {
        $verifyLogItem = Get-Item -LiteralPath $VerifyOnlyLogPath -ErrorAction Stop
        if ($verifyLogItem.PSIsContainer -or
            (($verifyLogItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            $verificationFailure = "verify-only log 不是普通文件"
            $verificationStatus = "FAIL"
            $overallStatus = "FAIL"
            if ($scriptExitCode -eq 0) { $scriptExitCode = 1 }
        }
        else {
            $verifyLogSummary = [ordered]@{
                path = [IO.Path]::GetFullPath($VerifyOnlyLogPath)
                bytes = $verifyLogItem.Length
                sha256 = Get-T57Sha256 -Path $VerifyOnlyLogPath
            }
        }
    }
    $runSummary = [ordered]@{
        schema = "GestureForge-S2A-T57-run-summary-v1"
        task_id = "S2A-T57"
        mode = "run"
        overall_status = $overallStatus
        simulation_flow_status = $stageStatusTerminal
        data_verification_status = $verificationStatus
        vivado_process_exit_code = $vivadoExitCode
        verify_only = [ordered]@{
            command = @($PythonPath, "-B", $T57RunnerPath, "--verify-only")
            runner_sha256 = [string]$StartupBindings.python_runner_sha256
            exit_code = $verificationExitCode
            log = $verifyLogSummary
            report = $verificationReportSummary
            failure = $verificationFailure
        }
        stage_status = [ordered]@{
            path = $stageStatusPath
            sha256 = $stageStatusSha256
            terminal_status = $stageStatusTerminal
        }
        process_status = [ordered]@{
            path = $statusPath
            sha256 = $(if (Test-Path -LiteralPath $statusPath -PathType Leaf) { Get-T57Sha256 -Path $statusPath } else { $null })
        }
        failure = $(if ($null -ne $verificationFailure) { $verificationFailure } else { $runError })
    }
    try {
        Write-T57JsonCreateNew -Path $RunSummaryPath -Value $runSummary
    }
    catch {
        $scriptExitCode = 1
        Write-Error "无法新建 T57 run_summary.json：$($_.Exception.Message)"
    }
    if ($overallStatus -eq "PASS" -and $verificationExitCode -eq 0) {
        Write-Output "T57_SIMULATION_FLOW_AND_DATA_VERIFY_PASS"
    }
    else {
        Write-Error "T57 run failed: $verificationFailure; flow=$stageStatusTerminal; verify_exit=$verificationExitCode"
    }
}
elseif ($Mode -eq "dryrun" -and $scriptExitCode -eq 0) {
    Write-Output "T57_ISOLATED_DRYRUN_AND_XPR_HASH_CHECK_PASS"
}
else {
    Write-Error "T57 isolated project failed: $runError"
}
exit $scriptExitCode
