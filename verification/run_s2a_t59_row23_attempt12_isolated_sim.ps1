[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('Prepare', 'AuditInventory', 'RepairCanonicalRecovery', 'ResumeCanonicalRecovery')]
    [string]$Mode
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$script:RepoRoot = 'D:\FPGA_Competition'
$script:ExpectedHead = '7278f2342de4f44d8da8e8002b3b92597b5e5050'
$script:Run10Root = 'D:\FPGA_Competition\report\evidence\S2A-T59\run10'
$script:Run11Root = 'D:\FPGA_Competition\report\evidence\S2A-T59\run11'
$script:Run11InventoryPath = 'D:\FPGA_Competition\report\evidence\S2A-T59\run11\run11_inventory.json'
$script:Run12Root = 'D:\FPGA_Competition\report\evidence\S2A-T59\run12'
$script:Run12SummaryPath = 'D:\FPGA_Competition\report\evidence\S2A-T59\run12\prepare_summary.json'
$script:Run12InventoryPath = 'D:\FPGA_Competition\report\evidence\S2A-T59\run12\run12_inventory.json'
$script:Run12StaleSummaryPath = 'D:\FPGA_Competition\report\evidence\S2A-T59\run12\prepare_summary.pre_recovery_stale.json'
$script:Run12StaleInventoryPath = 'D:\FPGA_Competition\report\evidence\S2A-T59\run12\run12_inventory.pre_recovery_stale.json'
$script:Run12ProjectRoot = 'D:\FPGA_Competition\report\evidence\S2A-T59\run12\isolated_project'
$script:Run12TempRoot = 'D:\FPGA_Competition\report\evidence\S2A-T59\run12\temp'
$script:Run12XsimBuildRoot = 'D:\FPGA_Competition\report\evidence\S2A-T59\run12\isolated_project\s2a_t59_row23_attempt12.sim\sim_1\behav\xsim'
$script:SourceTbPath = 'D:\FPGA_Competition\sim\tb_s2a_conv_layer35_row23_all_channels.sv'
$script:AttemptTbPath = 'D:\FPGA_Competition\sim\tb_s2a_conv_layer35_attempt12.sv'
$script:SourcePythonPath = 'D:\FPGA_Competition\verification\test_s2a_conv_layer35_row23_all_channels_rtl.py'
$script:Run10SummaryPath = 'D:\FPGA_Competition\report\evidence\S2A-T59\run10\prepare_summary.json'
$script:Run10BindingPath = 'D:\FPGA_Competition\report\evidence\S2A-T59\run10\project_preflight_binding.json'
$script:Run10ManifestPath = 'D:\FPGA_Competition\report\evidence\S2A-T59\run10\fixture\fixture_manifest.json'
$script:Run11FailurePath = 'D:\FPGA_Competition\report\evidence\S2A-T59\run11\simulation_failure.json'
$script:TargetXprPath = 'D:\FPGA_Competition\vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr'
$script:ExpectedRun10SummarySha = '35a816aae2167e618b9c91fef1a3f5441bc59fe27d85468f47919d87beee83c1'
$script:ExpectedRun10BindingSha = '2f7da35666c3238f1ace45ceed46ecbc9f5ab1c4bbf49919d077f73579ec6c8a'
$script:ExpectedRun10ManifestSha = '7bdb1ccc6e94b9ae7327f75facc1d0cbe5d541b8fdd9b63480598102f2e1e792'
$script:ExpectedGoldenSha = '95f93d520186a64693996fa6cf9184417539c37ea8535359a7cd1579f47fc07e'
$script:ExpectedXprSha = '9e637bb8a31c8c74cdb703d632282a020875f5623893665719c1bbb5035be1ec'
$script:ExpectedRun11FailureSha = 'e38dd93f3a1c2941f19e49a07d4b3f477b3d7afeae5fb745bffbe62901a8e4ff'
$script:ExpectedRun11InventorySha = 'c004432be9a497880560b9d128d57b2d56432ff24fe57790cce14aec7b426d9a'
$script:ExpectedStaleSummaryBytes = 10041
$script:ExpectedStaleSummarySha = '4147807a9948a4e4577da6f0d711c280f57f0d57d425707ad80b2e99c6c2700a'
$script:ExpectedStaleInventoryBytes = 1565
$script:ExpectedStaleInventorySha = '67827926bee9e28dc89f517069598f7c1b91391ec13ab5f28ae0b1fe9d805364'
$script:XvlogPath = 'D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\xvlog.exe'
$script:XelabPath = 'D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\xelab.exe'
$script:XsimPath = 'D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\xsim.exe'
$script:ExpectedXvlogSha = '00e6cc2a03f92b22306b45830ab40ceddcd7deba9d805d71d4fe2f19983675e3'
$script:ExpectedXelabSha = 'dde9fe7a39f73229293be00e78a99fc5a9051ffbd2e033171af093424d5a0d5b'
$script:ExpectedXsimSha = '7574bc25eceaabe1c3c8cbe9cd00a542223afb17ca925d4dc9a97ee4bb1152c4'
$script:KnownPartialRunnerSha = '6d3b8d6c4b5ad2b87c737f1446366ea44e43f432a0f2306c98a49a96864d7f70'
$script:ExpectedRecoveryRunnerSha = 'e7c8aeb5d7def69aa662cfb61ca1ec45f61006d45381f3ddd2fb3199d0bea783'
$script:FailedCanonicalRepairRunnerSha = 'c373f8e0ee5a62f8e39d98a2ae8585d21516b1b9ba5a9c85f50d2639bde1756d'
$script:SuccessfulCanonicalRepairRunnerSha = '9868ac5f553872c4647267acca6c479a733fc9aa5b3b7e410e42f61f833aa648'
$script:KnownPartialFileHashes = [ordered]@{
    'isolated_project\project_setup.tcl' = 'df5bfb42283dd455404666091dcd4f6b6ffe3e9f791a1ae598e4d98046e275b0'
    'run_project_sim_batch.tcl' = 'cc67188220e74047b4b7ef441844f258fc7e53f36551d8d137571845994eae25'
    'static_tcl_contract.json' = 'faf136c5912a450feb18b4ed6be6d43ae8b4c3fb4b48ce8d55e5ad8ec13db531'
    'project_preflight_binding.json' = 'c29fceefd4979bf4637300206d6b8dcdae176dabc78ec383b7b2a007982ee0fd'
    'prepare_summary.json' = '4147807a9948a4e4577da6f0d711c280f57f0d57d425707ad80b2e99c6c2700a'
}

function Assert-Equal {
    param([Parameter(Mandatory = $true)]$Actual, [Parameter(Mandatory = $true)]$Expected, [Parameter(Mandatory = $true)][string]$Name)
    if ([string]$Actual -cne [string]$Expected) { throw "$Name 不匹配：实际=$Actual 期望=$Expected" }
}

function Assert-NoReparseChain {
    param([Parameter(Mandatory = $true)][string]$Path, [switch]$AllowMissingLeaf)
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $driveRoot = [System.IO.Path]::GetPathRoot($fullPath)
    $relative = $fullPath.Substring($driveRoot.Length).Trim('\')
    $parts = @($relative.Split('\', [System.StringSplitOptions]::RemoveEmptyEntries))
    $current = $driveRoot
    for ($index = 0; $index -lt $parts.Count; $index++) {
        $current = Join-Path -Path $current -ChildPath $parts[$index]
        if (-not (Test-Path -LiteralPath $current)) {
            if ($AllowMissingLeaf -and ($index -eq ($parts.Count - 1))) { return }
            throw "路径组件不存在：$current"
        }
        $entry = Get-Item -LiteralPath $current -Force
        if (($entry.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) { throw "拒绝重解析路径：$current" }
    }
}

function Get-FileRecord {
    param([Parameter(Mandatory = $true)][string]$Path)
    Assert-NoReparseChain $Path
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.PSIsContainer) { throw "预期文件却得到目录：$Path" }
    return [ordered]@{ path = $Path; bytes = [long]$item.Length; sha256 = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
}

function Get-HostGate {
    $repoFromScript = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
    Assert-Equal $repoFromScript $script:RepoRoot '仓库根路径'
    $headOutput = & git -C $script:RepoRoot rev-parse HEAD
    $gitExit = $LASTEXITCODE
    if ($gitExit -ne 0) { throw "git rev-parse 退出码=$gitExit" }
    $head = ([string]$headOutput).Trim()
    Assert-Equal $head $script:ExpectedHead '基线 HEAD'
    $blockedNames = @('vivado', 'vivado_lab', 'xsim', 'xsimk', 'xelab', 'xvlog', 'xvhdl', 'xsct')
    $active = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $blockedNames -contains $_.ProcessName.ToLowerInvariant() })
    if ($active.Count -ne 0) { throw "检测到 Xilinx 进程：$($active.ProcessName -join ',')" }
    $listeners = @()
    try { $listeners = @(Get-NetTCPConnection -State Listen -LocalPort 7654 -ErrorAction SilentlyContinue) } catch { $listeners = @() }
    if ($listeners.Count -ne 0) { throw '检测到 7654 监听端口' }
    return [ordered]@{ repo_root = $repoFromScript; head = $head; git_exit_code = [int]$gitExit; xilinx_processes = @(); listener_7654 = @(); vivado_or_xsim_invoked_by_runner = $false }
}

function ConvertTo-Utf8Json {
    param([Parameter(Mandatory = $true)]$Object)
    return ((ConvertTo-Json -InputObject $Object -Depth 32) -replace "`r`n", "`n") + "`n"
}

function Get-TextRecord {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Text)
    $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($Text)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { $digest = [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-', '').ToLowerInvariant() } finally { $sha.Dispose() }
    return [ordered]@{ path = $Path; bytes = [long]$bytes.Length; sha256 = $digest }
}

function Write-NewUtf8 {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Text)
    if (Test-Path -LiteralPath $Path) { throw "拒绝覆盖已有路径：$Path" }
    Assert-NoReparseChain (Split-Path -Parent $Path)
    $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($Text)
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
}

function Assert-ExistingText {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Text)
    $actual = [System.IO.File]::ReadAllBytes($Path)
    $expected = [System.Text.UTF8Encoding]::new($false).GetBytes($Text)
    if ($actual.Length -ne $expected.Length) { throw "文本长度不符：$Path" }
    for ($index = 0; $index -lt $actual.Length; $index++) { if ($actual[$index] -ne $expected[$index]) { throw "文本字节不符：$Path offset=$index" } }
}

function Get-ParentBinding {
    param([switch]$RequireRun12Absent)
    foreach ($path in @($script:Run10Root, (Join-Path $script:Run10Root 'fixture'), $script:Run10SummaryPath, $script:Run10BindingPath, $script:Run10ManifestPath, $script:Run11Root, $script:Run11InventoryPath, $script:Run11FailurePath, $script:TargetXprPath, $script:SourceTbPath, $script:SourcePythonPath, $script:AttemptTbPath)) { Assert-NoReparseChain $path }
    if ($RequireRun12Absent) {
        if (Test-Path -LiteralPath $script:Run12Root) { throw "run12 已存在，拒绝覆盖：$script:Run12Root" }
        Assert-NoReparseChain $script:Run12Root -AllowMissingLeaf
    } else {
        Assert-NoReparseChain $script:Run12Root
    }
    Assert-Equal (Get-FileRecord $script:Run10SummaryPath).sha256 $script:ExpectedRun10SummarySha 'run10 summary SHA256'
    Assert-Equal (Get-FileRecord $script:Run10BindingPath).sha256 $script:ExpectedRun10BindingSha 'run10 project binding SHA256'
    Assert-Equal (Get-FileRecord $script:Run10ManifestPath).sha256 $script:ExpectedRun10ManifestSha 'run10 fixture manifest SHA256'
    Assert-Equal (Get-FileRecord $script:Run11FailurePath).sha256 $script:ExpectedRun11FailureSha 'run11 failure record SHA256'
    Assert-Equal (Get-FileRecord $script:Run11InventoryPath).sha256 $script:ExpectedRun11InventorySha 'run11 original inventory SHA256'
    $summary = Get-Content -LiteralPath $script:Run10SummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $binding = Get-Content -LiteralPath $script:Run10BindingPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $manifest = Get-Content -LiteralPath $script:Run10ManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $failure = Get-Content -LiteralPath $script:Run11FailurePath -Raw -Encoding UTF8 | ConvertFrom-Json
    $run11Inventory = Get-Content -LiteralPath $script:Run11InventoryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $summary.task_id 'S2A-T59' 'run10 task id'
    Assert-Equal $summary.run_id 'run10' 'run10 run id'
    Assert-Equal $summary.status 'PREPARED_NOT_SIMULATED' 'run10 status'
    Assert-Equal $summary.scope 'tiny416 cfg section36 layer35; all 256 output channels at y=23, x=0..25' 'run10 scope'
    Assert-Equal $binding.task_id 'S2A-T59' 'run10 project binding task id'
    Assert-Equal $binding.run_id 'run10' 'run10 project binding run id'
    Assert-Equal $binding.project_xpr_path $script:TargetXprPath 'run10 project XPR path'
    Assert-Equal $binding.target_xpr_sha256_before_prepare $script:ExpectedXprSha 'run10 XPR before SHA256'
    Assert-Equal $binding.target_xpr_sha256_after_prepare $script:ExpectedXprSha 'run10 XPR after SHA256'
    Assert-Equal $binding.target_xpr_unchanged $true 'run10 target XPR unchanged'
    Assert-Equal $manifest.task_id 'S2A-T59' 'run10 manifest task id'
    Assert-Equal $manifest.run_id 'run10' 'run10 manifest run id'
    Assert-Equal $manifest.status 'PREPARED_NOT_SIMULATED' 'run10 manifest status'
    Assert-Equal $failure.task_id 'S2A-T59' 'run11 failure task id'
    Assert-Equal $failure.run_id 'run11' 'run11 failure run id'
    Assert-Equal $failure.status 'NON_ACCEPTANCE' 'run11 failure status'
    Assert-Equal $failure.failure_class 'INCOMPLETE_C_TEMP_EXHAUSTION_INFERRED' 'run11 failure class'
    Assert-Equal $run11Inventory.task_id 'S2A-T59' 'run11 original inventory task id'
    Assert-Equal $run11Inventory.run_id 'run11' 'run11 original inventory run id'
    Assert-Equal $run11Inventory.file_count $run11Inventory.files.Count 'run11 original inventory count'
    $run11Records = @()
    $run11RootPrefix = $script:Run11Root.TrimEnd('\') + '\'
    foreach ($entry in $run11Inventory.files) {
        $candidate = [System.IO.Path]::GetFullPath((Join-Path $script:Run11Root ([string]$entry.path)))
        if (-not $candidate.StartsWith($run11RootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) { throw "run11 inventory 路径越界：$($entry.path)" }
        $record = Get-FileRecord $candidate
        Assert-Equal $record.bytes $entry.bytes "run11 original inventory bytes $($entry.path)"
        Assert-Equal $record.sha256 $entry.sha256 "run11 original inventory SHA $($entry.path)"
        $run11Records += $record
    }
    $actualXpr = Get-FileRecord $script:TargetXprPath
    Assert-Equal $actualXpr.sha256 $script:ExpectedXprSha '目标 XPR SHA256'
    $simulator = [ordered]@{}
    foreach ($tool in @(
        [ordered]@{ name = 'xvlog'; path = $script:XvlogPath; sha256 = $script:ExpectedXvlogSha },
        [ordered]@{ name = 'xelab'; path = $script:XelabPath; sha256 = $script:ExpectedXelabSha },
        [ordered]@{ name = 'xsim'; path = $script:XsimPath; sha256 = $script:ExpectedXsimSha }
    )) {
        $toolRecord = Get-FileRecord $tool.path
        Assert-Equal $toolRecord.sha256 $tool.sha256 "本地 Vivado 2026.1 $($tool.name) SHA256"
        $simulator[$tool.name] = $toolRecord
    }
    $fixtureFiles = [ordered]@{}
    foreach ($name in @('feature_input.bin', 'layer35_weights.bin', 'golden.bin', 'vectors.txt')) {
        $summaryFile = $summary.fixture.files.$name
        $manifestFile = $manifest.files.$name
        if ($null -eq $summaryFile -or $null -eq $manifestFile) { throw "run10 缺少 fixture 条目：$name" }
        $expectedPath = Join-Path (Join-Path $script:Run10Root 'fixture') $name
        Assert-Equal $summaryFile.path $expectedPath "run10 fixture path $name"
        Assert-Equal $manifestFile.path $expectedPath "manifest fixture path $name"
        Assert-Equal $manifestFile.bytes $summaryFile.bytes "manifest fixture bytes $name"
        Assert-Equal $manifestFile.sha256 $summaryFile.sha256 "manifest fixture SHA $name"
        $actualFile = Get-FileRecord $expectedPath
        Assert-Equal $actualFile.bytes $summaryFile.bytes "fixture bytes $name"
        Assert-Equal $actualFile.sha256 $summaryFile.sha256 "fixture SHA $name"
        $fixtureFiles[$name] = $actualFile
    }
    Assert-Equal $fixtureFiles['golden.bin'].sha256 $script:ExpectedGoldenSha 'run10 golden SHA256'
    Assert-Equal $summary.fixture.golden_layout.raw_int32_le_bytes 26624 'raw golden bytes'
    Assert-Equal $summary.fixture.golden_layout.int8_bytes 6656 'INT8 golden bytes'
    Assert-Equal $summary.expected_counts.output_cases 6656 'run10 output count'
    Assert-Equal $summary.oracle.raw_int32_count 6656 'run10 raw oracle count'
    Assert-Equal $summary.oracle.quantized_int8_count 6656 'run10 INT8 oracle count'
    Assert-Equal $summary.oracle.d2_t23_match_count 6656 'run10 D2/T23 count'
    $sourceRecords = [ordered]@{}
    foreach ($source in $summary.bindings.T59_source_hashes.PSObject.Properties) {
        $fullPath = Join-Path $script:RepoRoot $source.Name
        $record = Get-FileRecord $fullPath
        Assert-Equal $record.sha256 $source.Value "T59 source SHA $($source.Name)"
        $sourceRecords[$source.Name] = $record
    }
    foreach ($required in @('sim/tb_s2a_conv_layer35_row23_all_channels.sv', 'verification/test_s2a_conv_layer35_row23_all_channels_rtl.py', 'src/int8_conv_tap_geometry.sv', 'src/int8_conv_weight_address.sv', 'src/int8_mac_accumulator.sv', 'src/s2a_conv_engine.sv', 'src/s2a_conv_layer35_channel_probe.sv')) {
        if (-not $sourceRecords.Contains($required)) { throw "父摘要未绑定来源：$required" }
    }
    $rawRecord = Get-FileRecord $failure.partial_outputs.raw_int32_le.path
    $int8Record = Get-FileRecord $failure.partial_outputs.quantized_int8.path
    Assert-Equal $rawRecord.bytes 15768 'run11 raw partial bytes'
    Assert-Equal $rawRecord.sha256 $failure.partial_outputs.raw_int32_le.sha256 'run11 raw partial SHA'
    Assert-Equal $int8Record.bytes 3942 'run11 INT8 partial bytes'
    Assert-Equal $int8Record.sha256 $failure.partial_outputs.quantized_int8.sha256 'run11 INT8 partial SHA'
    return [ordered]@{ summary_record = Get-FileRecord $script:Run10SummaryPath; binding_record = Get-FileRecord $script:Run10BindingPath; manifest_record = Get-FileRecord $script:Run10ManifestPath; failure_record = Get-FileRecord $script:Run11FailurePath; run11_inventory_record = Get-FileRecord $script:Run11InventoryPath; run11_original_inventory_files = @($run11Records); xpr = $actualXpr; simulator = $simulator; fixture_files = $fixtureFiles; T59_source_hashes = $sourceRecords; failure = $failure }
}

function New-TbCloneText {
    $original = [System.IO.File]::ReadAllText($script:SourceTbPath, [System.Text.Encoding]::UTF8)
    $newline = if ($original.Contains("`r`n")) { "`r`n" } else { "`n" }
    $updated = $original
    $pairs = @(
        [ordered]@{ old = 'D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run10\\observed_raw.bin'; new = 'D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run12\\observed_raw.bin' },
        [ordered]@{ old = 'D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run10\\observed_output.bin'; new = 'D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run12\\observed_output.bin' }
    )
    foreach ($pair in $pairs) {
        $count = ([regex]::Matches($updated, [regex]::Escape($pair.old))).Count
        Assert-Equal $count 1 "TB 输出路径出现次数 $($pair.old)"
        $updated = $updated.Replace($pair.old, $pair.new)
    }
    $regions = [regex]::Matches($updated, '(?s)\$display\("PASS T59 outputs=.*?\);\s*\$finish;')
    Assert-Equal $regions.Count 1 'PASS/$finish 区域数量'
    if ($updated.Contains('T59_XSIM_SENTINEL')) { throw '源 TB 已存在 T59 sentinel' }
    $finishIndex = $updated.IndexOf('$finish;', $regions[0].Index, [System.StringComparison]::Ordinal)
    if ($finishIndex -lt 0) { throw 'PASS 后没有 $finish' }
    $updated = $updated.Insert($finishIndex, '$display("T59_XSIM_SENTINEL=PASS_RUN12");' + $newline + '        ')
    foreach ($name in @('feature_input.bin', 'layer35_weights.bin', 'golden.bin', 'vectors.txt')) {
        if (-not $updated.Contains('D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run10\\fixture\\' + $name)) { throw "run10 输入路径缺失：$name" }
    }
    if ($updated.Contains('run10\\observed_raw.bin') -or $updated.Contains('run10\\observed_output.bin')) { throw 'TB 仍将输出写入 run10' }
    Assert-Equal ([regex]::Matches($updated, 'T59_XSIM_SENTINEL=PASS_RUN12').Count) 1 'run12 sentinel 唯一性'
    $reverse = $updated.Replace('$display("T59_XSIM_SENTINEL=PASS_RUN12");' + $newline + '        ', '')
    foreach ($pair in $pairs) { $reverse = $reverse.Replace($pair.new, $pair.old) }
    if ($reverse -cne $original) { throw 'attempt12 TB 除两条输出路径和 sentinel 外存在改动' }
    return [ordered]@{ text = $updated; newline = if ($newline -eq "`r`n") { 'CRLF' } else { 'LF' } }
}

function New-TclPlan {
    $projectPath = Join-Path $script:Run12ProjectRoot 's2a_t59_row23_attempt12.xpr'
    $projectSetupPath = Join-Path $script:Run12ProjectRoot 'project_setup.tcl'
    $simulationPath = Join-Path $script:Run12Root 'run_project_sim_batch.tcl'
    $snapshot = 'tb_s2a_conv_layer35_row23_all_channels_behav'
    $projectLines = [System.Collections.Generic.List[string]]::new()
    $projectLines.Add("create_project s2a_t59_row23_attempt12 {$script:Run12ProjectRoot} -part xc7z020clg400-1")
    $projectLines.Add('set_property target_language Verilog [current_project]')
    $projectLines.Add('set_property simulator_language Mixed [current_project]')
    $projectLines.Add('set_property TARGET_SIMULATOR XSim [current_project]')
    foreach ($relative in @('src/int8_conv_tap_geometry.sv', 'src/int8_conv_weight_address.sv', 'src/int8_mac_accumulator.sv', 'src/s2a_conv_engine.sv', 'src/s2a_conv_layer35_channel_probe.sv')) {
        $projectLines.Add("add_files -fileset sources_1 -norecurse {$(Join-Path $script:RepoRoot $relative)}")
    }
    $projectLines.Add("add_files -fileset sim_1 -norecurse {$script:AttemptTbPath}")
    $projectLines.Add('set_property top tb_s2a_conv_layer35_row23_all_channels [get_filesets sim_1]')
    $projectLines.Add('update_compile_order -fileset sources_1')
    $projectLines.Add('update_compile_order -fileset sim_1')
    $projectText = [string]::Join("`n", $projectLines.ToArray()) + "`n"
    $simLines = [System.Collections.Generic.List[string]]::new()
    $simLines.Add("set t59_run12_temp {$script:Run12TempRoot}")
    $simLines.Add('file mkdir $t59_run12_temp')
    $simLines.Add('set ::env(TEMP) $t59_run12_temp')
    $simLines.Add('set ::env(TMP) $t59_run12_temp')
    $simLines.Add('set ::env(TMPDIR) $t59_run12_temp')
    $simLines.Add("source {$projectSetupPath}")
    $simLines.Add('launch_simulation -simset sim_1 -mode behavioral -step compile')
    $simLines.Add('launch_simulation -simset sim_1 -mode behavioral -step elaborate')
    $simLines.Add("xsim $snapshot -R -onfinish quit -log {$script:Run12Root\simulate.log}")
    $simLines.Add('close_project')
    $simText = [string]::Join("`n", $simLines.ToArray()) + "`n"
    foreach ($pair in @(@{ text = $projectText; lines = $projectLines; name = 'project' }, @{ text = $simText; lines = $simLines; name = 'simulation' })) {
        if ($pair.text.Contains("`r")) { throw "$($pair.name) Tcl 不是 LF" }
        $actualLines = @($pair.text -split "`n" | Where-Object { $_.Length -gt 0 })
        Assert-Equal $actualLines.Count $pair.lines.Count "$($pair.name) Tcl 命令数"
        for ($index = 0; $index -lt $pair.lines.Count; $index++) {
            Assert-Equal $actualLines[$index] $pair.lines[$index] "$($pair.name) Tcl 命令顺序 $index"
            if ($actualLines[$index].Contains(';')) { throw "$($pair.name) Tcl 行包含拼接命令：$($actualLines[$index])" }
        }
    }
    if (($projectText + $simText).Contains($script:TargetXprPath)) { throw 'Tcl 意外引用主工程 XPR' }
    if ($simText -match '(?i)(?:^|\s)-gui(?:\s|$)|(?:^|\s)-wdb(?:\s|$)|\b(?:add_wave|log_wave|save_wave_config|open_wave_config)\b') { throw 'batch Tcl 含 GUI/WDB/波形命令' }
    if (-not $simText.Contains("xsim $snapshot -R")) { throw 'batch Tcl 缺少 xsim -R' }
    if (-not $simText.Contains('set ::env(TEMP) $t59_run12_temp') -or -not $simText.Contains('set ::env(TMP) $t59_run12_temp') -or -not $simText.Contains('set ::env(TMPDIR) $t59_run12_temp')) { throw 'TEMP/TMP/TMPDIR 未同时绑定到 run12 D 盘目录' }
    return [ordered]@{ project_path = $projectPath; project_setup_path = $projectSetupPath; project_text = $projectText; project_lines = @($projectLines.ToArray()); simulation_path = $simulationPath; simulation_text = $simText; simulation_lines = @($simLines.ToArray()); snapshot = $snapshot }
}

function Get-Run12FileRecords {
    $files = @(Get-ChildItem -LiteralPath $script:Run12Root -File -Recurse -Force)
    $records = @()
    foreach ($file in $files) {
        Assert-NoReparseChain $file.FullName
        $relative = $file.FullName.Substring($script:Run12Root.Length + 1)
        if ($relative -ieq 'run12_inventory.json') { continue }
        $records += [ordered]@{ path = $relative; bytes = [long]$file.Length; sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
    }
    return @($records | Sort-Object -Property path)
}

function Invoke-ResumeKnownPartial {
    $hostBefore = Get-HostGate
    $parent = Get-ParentBinding
    Assert-Run12Shape
    $expectedRelatives = @($script:KnownPartialFileHashes.Keys | Sort-Object)
    $existingFiles = @(Get-ChildItem -LiteralPath $script:Run12Root -File -Recurse -Force | ForEach-Object { Assert-NoReparseChain $_.FullName; $_.FullName.Substring($script:Run12Root.Length + 1) } | Sort-Object)
    if (($existingFiles -join "`n") -cne ($expectedRelatives -join "`n")) { throw "run12 partial file set 与冻结快照不符：$($existingFiles -join ',')" }
    foreach ($relative in $expectedRelatives) {
        $record = Get-FileRecord (Join-Path $script:Run12Root $relative)
        Assert-Equal $record.sha256 $script:KnownPartialFileHashes[$relative] "run12 partial SHA $relative"
    }
    $prepareLogPath = Join-Path $script:Run12Root 'prepare.log'
    $inventoryPath = Join-Path $script:Run12Root 'run12_inventory.json'
    if (Test-Path -LiteralPath $prepareLogPath) { throw 'partial recovery 拒绝覆盖已有 prepare.log' }
    if (Test-Path -LiteralPath $inventoryPath) { throw 'partial recovery 拒绝覆盖已有 inventory' }
    $tb = New-TbCloneText
    Assert-ExistingText $script:AttemptTbPath $tb.text
    $tcl = New-TclPlan
    $projectRecord = Get-TextRecord $tcl.project_setup_path $tcl.project_text
    $simulationRecord = Get-TextRecord $tcl.simulation_path $tcl.simulation_text
    Assert-ExistingText $tcl.project_setup_path $tcl.project_text
    Assert-ExistingText $tcl.simulation_path $tcl.simulation_text
    $contractPath = Join-Path $script:Run12Root 'static_tcl_contract.json'
    $contract = Get-Content -LiteralPath $contractPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $contract.status 'PASS_STATIC_ONLY' 'partial static Tcl contract status'
    Assert-Equal $contract.project_setup.sha256 $projectRecord.sha256 'partial project Tcl contract SHA'
    Assert-Equal $contract.simulation_tcl.sha256 $simulationRecord.sha256 'partial batch Tcl contract SHA'
    Assert-Equal $contract.project_command_count $tcl.project_lines.Count 'partial project command count'
    Assert-Equal $contract.simulation_command_count $tcl.simulation_lines.Count 'partial batch command count'
    if (($contract.project_commands -join "`n") -cne ($tcl.project_lines -join "`n")) { throw 'partial project Tcl command array differs' }
    if (($contract.simulation_commands -join "`n") -cne ($tcl.simulation_lines -join "`n")) { throw 'partial batch Tcl command array differs' }
    $bindingPath = Join-Path $script:Run12Root 'project_preflight_binding.json'
    $summaryPath = Join-Path $script:Run12Root 'prepare_summary.json'
    $binding = Get-Content -LiteralPath $bindingPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $summary = Get-Content -LiteralPath $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $binding.status 'DRYRUN_READY_NOT_SIMULATED' 'partial binding status'
    Assert-Equal $summary.status 'DRYRUN_READY_NOT_SIMULATED' 'partial summary status'
    Assert-Equal $binding.run_id 'run12' 'partial binding run id'
    Assert-Equal $summary.run_id 'run12' 'partial summary run id'
    Assert-Equal $binding.current_head $hostBefore.head 'partial binding HEAD'
    Assert-Equal $summary.current_head $hostBefore.head 'partial summary HEAD'
    Assert-Equal $binding.runner.sha256 $script:KnownPartialRunnerSha 'partial binding original runner SHA'
    Assert-Equal $summary.runner.sha256 $script:KnownPartialRunnerSha 'partial summary original runner SHA'
    Assert-Equal $binding.runner.sha256 $summary.runner.sha256 'partial runner binding consistency'
    Assert-Equal $binding.attempt12_testbench.sha256 (Get-FileRecord $script:AttemptTbPath).sha256 'partial attempt TB SHA'
    Assert-Equal $binding.static_tcl_contract.sha256 (Get-FileRecord $contractPath).sha256 'partial static contract file SHA'
    Assert-Equal $binding.project_setup_tcl.sha256 (Get-FileRecord $tcl.project_setup_path).sha256 'partial project Tcl file SHA'
    Assert-Equal $binding.batch_simulation_tcl.sha256 (Get-FileRecord $tcl.simulation_path).sha256 'partial batch Tcl file SHA'
    Assert-Equal $binding.run11_failure_record.sha256 $parent.failure_record.sha256 'partial run11 failure binding'
    Assert-Equal $binding.run11_original_inventory.sha256 $parent.run11_inventory_record.sha256 'partial original run11 inventory binding'
    Assert-Equal $binding.target_xpr.sha256 $parent.xpr.sha256 'partial XPR binding'
    Assert-Equal $summary.project_preflight_binding.sha256 (Get-FileRecord $bindingPath).sha256 'partial summary binding SHA'
    Assert-Equal $summary.static_tcl_contract.sha256 (Get-FileRecord $contractPath).sha256 'partial summary contract SHA'
    Assert-Equal $summary.project_setup_tcl.sha256 (Get-FileRecord $tcl.project_setup_path).sha256 'partial summary project Tcl SHA'
    Assert-Equal $summary.batch_simulation_tcl.sha256 (Get-FileRecord $tcl.simulation_path).sha256 'partial summary batch Tcl SHA'
    Assert-Equal (Get-FileRecord $script:TargetXprPath).sha256 $parent.xpr.sha256 'partial recovery target XPR SHA'
    $recoveryRunner = Get-FileRecord $PSCommandPath
    $logText = @(
        'task=S2A-T59 run=run12 mode=Prepare recovery=verified_partial attempt=3'
        "command=pwsh -NoLogo -NoProfile -File `"$PSCommandPath`" -Mode Prepare"
        "cwd=$script:RepoRoot"
        "head=$($hostBefore.head)"
        "prior_attempt_1=FAIL exit_code=1 writes=false cause=run10_source_hashes_nested_under_bindings"
        'prior_attempt_2=FAIL exit_code=1 partial_files_created=true cause=StrictMode_null_output_count_in_Assert_Run12Shape'
        'partial_files_hash_verified=true; existing_files_overwritten=false'
        "original_bound_runner_sha256=$($binding.runner.sha256)"
        "recovery_runner_sha256=$($recoveryRunner.sha256)"
        'summary_attempt_2_claimed_exit_code=0 but observed command exit_code=1; this log records the actual failure and does not alter the summary bytes'
        "expected_TEMP=$script:Run12TempRoot"
        "expected_TMP=$script:Run12TempRoot"
        "expected_TMPDIR=$script:Run12TempRoot"
        'vivado_cli_invoked=false'
        'xsim_cli_invoked=false'
        'status=DRYRUN_READY_NOT_SIMULATED'
        'recovery_exit_code=0'
    ) -join "`n"
    $logText += "`n"
    $logRecord = Get-TextRecord $prepareLogPath $logText
    $records = @(Get-Run12FileRecords)
    $records += [ordered]@{ path = 'prepare.log'; bytes = $logRecord.bytes; sha256 = $logRecord.sha256 }
    $records = @($records | Sort-Object -Property path)
    $inventory = [ordered]@{ schema = 'GestureForge-S2A-T59-run12-inventory-v1'; task_id = 'S2A-T59'; run_id = 'run12'; status = 'DRYRUN_READY_NOT_SIMULATED'; baseline_head = $script:ExpectedHead; file_count = $records.Count; files = $records; directories = @('isolated_project', 'temp'); recovery = [ordered]@{ status = 'VERIFIED_PARTIAL_NO_OVERWRITE'; original_runner_sha256 = $binding.runner.sha256; recovery_runner_sha256 = $recoveryRunner.sha256; prior_prepare_attempt_2_exit_code = 1 } }
    $inventoryText = ConvertTo-Utf8Json $inventory
    Write-NewUtf8 $prepareLogPath $logText
    Write-NewUtf8 $inventoryPath $inventoryText
    Assert-ExistingText $prepareLogPath $logText
    Assert-ExistingText $inventoryPath $inventoryText
    Assert-Run12Shape
    $hostAfter = Get-HostGate
    Assert-Equal $hostAfter.head $hostBefore.head 'partial recovery 后 HEAD'
    Assert-Equal (Get-FileRecord $script:TargetXprPath).sha256 $parent.xpr.sha256 'partial recovery 后主 XPR SHA'
    Write-Output 'PREPARE=PASS status=DRYRUN_READY_NOT_SIMULATED recovery=VERIFIED_PARTIAL_NO_OVERWRITE simulation=NOT_RUN'
    Write-Output "RECOVERY_RUNNER_SHA256=$($recoveryRunner.sha256)"
    Write-Output "INVENTORY_SHA256=$((Get-FileRecord $inventoryPath).sha256)"
    Write-Output "INVENTORY_FILES=$($records.Count)"
}

function Assert-Run12Shape {
    $expectedDirectories = @('isolated_project', 'temp')
    $actualDirectories = @(Get-ChildItem -LiteralPath $script:Run12Root -Directory -Recurse -Force | ForEach-Object { Assert-NoReparseChain $_.FullName; $_.FullName.Substring($script:Run12Root.Length + 1) } | Sort-Object)
    if (($actualDirectories -join "`n") -cne ($expectedDirectories -join "`n")) { throw "run12 目录集合不符：$($actualDirectories -join ',')" }
    foreach ($dir in $expectedDirectories) { if (-not (Test-Path -LiteralPath (Join-Path $script:Run12Root $dir) -PathType Container)) { throw "run12 缺少目录：$dir" } }
    $unexpectedOutput = @(@('observed_raw.bin', 'observed_output.bin', 'simulate.log') | Where-Object { Test-Path -LiteralPath (Join-Path $script:Run12Root $_) })
    if ($unexpectedOutput.Count -ne 0) { throw "准备阶段出现仿真输出：$($unexpectedOutput -join ',')" }
}

function Invoke-Prepare {
    if (Test-Path -LiteralPath $script:Run12Root) {
        Invoke-ResumeKnownPartial
        return
    }
    $hostBefore = Get-HostGate
    if (Test-Path -LiteralPath $script:Run12Root) { throw "run12 已存在，拒绝覆盖或续写：$script:Run12Root" }
    Assert-NoReparseChain $script:Run12Root -AllowMissingLeaf
    $parent = Get-ParentBinding -RequireRun12Absent
    $tb = New-TbCloneText
    Assert-ExistingText $script:AttemptTbPath $tb.text
    $tcl = New-TclPlan
    $tbRecord = Get-FileRecord $script:AttemptTbPath
    $runnerRecord = Get-FileRecord $PSCommandPath
    $projectRecord = Get-TextRecord $tcl.project_setup_path $tcl.project_text
    $simulationRecord = Get-TextRecord $tcl.simulation_path $tcl.simulation_text
    $contractPath = Join-Path $script:Run12Root 'static_tcl_contract.json'
    $contract = [ordered]@{ schema = 'GestureForge-S2A-T59-run12-batch-tcl-contract-v1'; status = 'PASS_STATIC_ONLY'; target_xpr_opened = $false; independent_project = $true; project_setup = $projectRecord; project_command_count = $tcl.project_lines.Count; project_commands = $tcl.project_lines; simulation_tcl = $simulationRecord; simulation_command_count = $tcl.simulation_lines.Count; simulation_commands = $tcl.simulation_lines; separators = 'literal LF; one Tcl command per line'; batch_mode = 'xsim snapshot -R'; gui_option_present = $false; wdb_option_present = $false; waveform_commands_present = $false; expected_child_temp_environment = [ordered]@{ TEMP = $script:Run12TempRoot; TMP = $script:Run12TempRoot; TMPDIR = $script:Run12TempRoot } }
    $contractText = ConvertTo-Utf8Json $contract
    $contractRecord = Get-TextRecord $contractPath $contractText
    $prepareLogPath = Join-Path $script:Run12Root 'prepare.log'
    $prepareLogText = @('task=S2A-T59 run=run12 mode=Prepare attempt=2', "command=pwsh -NoProfile -File `"$PSCommandPath`" -Mode Prepare", "cwd=$script:RepoRoot", "head=$($hostBefore.head)", 'prior_attempt_1=FAIL exit_code=1 writes=false cause=run10_source_hashes_nested_under_bindings', "expected_TEMP=$script:Run12TempRoot", "expected_TMP=$script:Run12TempRoot", "expected_TMPDIR=$script:Run12TempRoot", 'vivado_cli_invoked=false', 'xsim_cli_invoked=false', 'status=DRYRUN_READY_NOT_SIMULATED', 'exit_code=0') -join "`n"
    $prepareLogText += "`n"
    [System.IO.Directory]::CreateDirectory($script:Run12Root) | Out-Null
    [System.IO.Directory]::CreateDirectory($script:Run12ProjectRoot) | Out-Null
    [System.IO.Directory]::CreateDirectory($script:Run12TempRoot) | Out-Null
    Write-NewUtf8 $tcl.project_setup_path $tcl.project_text
    Write-NewUtf8 $tcl.simulation_path $tcl.simulation_text
    Write-NewUtf8 $contractPath $contractText
    $bindingPath = Join-Path $script:Run12Root 'project_preflight_binding.json'
    $binding = [ordered]@{ schema = 'GestureForge-S2A-T59-run12-project-preflight-binding-v1'; task_id = 'S2A-T59'; run_id = 'run12'; status = 'DRYRUN_READY_NOT_SIMULATED'; baseline_head = $script:ExpectedHead; current_head = $hostBefore.head; run10_parent = [ordered]@{ summary = $parent.summary_record; project_preflight_binding = $parent.binding_record; fixture_manifest = $parent.manifest_record; fixture_files = $parent.fixture_files; verification_status = 'run10 --verify-only PASS 来自任务卡；本 runner 未重跑' }; run11_failure_record = $parent.failure_record; run11_failure_status = 'NON_ACCEPTANCE'; run11_original_inventory = $parent.run11_inventory_record; run11_original_inventory_files = $parent.run11_original_inventory_files; target_xpr = $parent.xpr; local_vivado_2026_1 = $parent.simulator; T59_source_hashes = $parent.T59_source_hashes; attempt12_testbench = $tbRecord; runner = $runnerRecord; project_setup_tcl = $projectRecord; batch_simulation_tcl = $simulationRecord; static_tcl_contract = $contractRecord; tb_io_paths = [ordered]@{ fixture_inputs = @($parent.fixture_files['feature_input.bin'].path, $parent.fixture_files['layer35_weights.bin'].path, $parent.fixture_files['golden.bin'].path, $parent.fixture_files['vectors.txt'].path); observed_outputs = @((Join-Path $script:Run12Root 'observed_raw.bin'), (Join-Path $script:Run12Root 'observed_output.bin')) }; simulation_log_paths = [ordered]@{ compile = Join-Path $script:Run12XsimBuildRoot 'compile.log'; elaborate = Join-Path $script:Run12XsimBuildRoot 'elaborate.log'; xsim = Join-Path $script:Run12Root 'simulate.log' }; temp_environment = [ordered]@{ TEMP = $script:Run12TempRoot; TMP = $script:Run12TempRoot; TMPDIR = $script:Run12TempRoot }; xsim_snapshot = $tcl.snapshot; xsim_invocation = 'xsim <snapshot> -R -onfinish quit -log <run12 simulate.log>'; gui = $false; wdb = $false; waveforms = $false; target_main_xpr_opened = $false; vivado_or_xsim_invoked_by_prepare = $false }
    $bindingText = ConvertTo-Utf8Json $binding
    Write-NewUtf8 $bindingPath $bindingText
    $bindingRecord = Get-FileRecord $bindingPath
    $summaryPath = Join-Path $script:Run12Root 'prepare_summary.json'
    $summary = [ordered]@{ schema = 'GestureForge-S2A-T59-run12-preparation-summary-v1'; task_id = 'S2A-T59'; run_id = 'run12'; status = 'DRYRUN_READY_NOT_SIMULATED'; baseline_head = $script:ExpectedHead; current_head = $hostBefore.head; scope = 'tiny416 cfg section36 layer35; y=23, x=0..25, all 256 output channels'; expected_counts = [ordered]@{ outputs = 6656; raw_int32_bytes = 26624; quantized_int8_bytes = 6656 }; prepare_attempt_history = @([ordered]@{ attempt = 1; actual_exit_code = 1; files_written = $false; failure_reason = 'run10 T59_source_hashes 位于 summary.bindings 而非顶层；失败发生在创建 run12 前' }, [ordered]@{ attempt = 2; actual_exit_code = 0; files_written = $true; status = 'DRYRUN_READY_NOT_SIMULATED' }); parent_run10_summary = $parent.summary_record; parent_run10_manifest = $parent.manifest_record; parent_run10_binding = $parent.binding_record; run11_failure_record = $parent.failure_record; run11_original_inventory = $parent.run11_inventory_record; run11_original_inventory_files = $parent.run11_original_inventory_files; run10_four_fixture_inputs = $parent.fixture_files; T59_source_hashes = $parent.T59_source_hashes; target_xpr = $parent.xpr; local_vivado_2026_1 = $parent.simulator; attempt12_testbench = $tbRecord; runner = $runnerRecord; project_preflight_binding = $bindingRecord; static_tcl_contract = $contractRecord; project_setup_tcl = $projectRecord; batch_simulation_tcl = $simulationRecord; isolated_project_xpr_future_path = $tcl.project_path; future_log_paths = [ordered]@{ compile = Join-Path $script:Run12XsimBuildRoot 'compile.log'; elaborate = Join-Path $script:Run12XsimBuildRoot 'elaborate.log'; xsim = Join-Path $script:Run12Root 'simulate.log' }; temp_directory = $script:Run12TempRoot; temp_environment_required = [ordered]@{ TEMP = $script:Run12TempRoot; TMP = $script:Run12TempRoot; TMPDIR = $script:Run12TempRoot }; simulation = [ordered]@{ status = 'NOT_RUN'; vivado_cli_invoked = $false; xsim_cli_invoked = $false; mcp_run_tcl_not_called = $true }; limitations = @('此证据仅为 run12 静态准备，不是 RTL 仿真结果。','运行模拟时须由总控通过 MCP 执行生成的 run_project_sim_batch.tcl，并确认 TEMP/TMP/TMPDIR 位于 run12 D 盘 temp 目录。','使用 xsim -R batch 路径，没有 -gui、-wdb 或 waveform 命令；此前 run11 的 GUI/WDB 失败证据保留。','run10 --verify-only PASS 来自任务卡，本 runner 未重跑。','不得推及整层/整网、G3、G4 或 G5。') }
    Write-NewUtf8 $summaryPath (ConvertTo-Utf8Json $summary)
    Assert-Run12Shape
    $hostAfter = Get-HostGate
    Assert-Equal $hostAfter.head $hostBefore.head 'Prepare 后 HEAD'
    Assert-Equal (Get-FileRecord $script:TargetXprPath).sha256 $parent.xpr.sha256 'Prepare 后主 XPR SHA'
    Write-NewUtf8 $prepareLogPath $prepareLogText
    $records = Get-Run12FileRecords
    $inventoryPath = Join-Path $script:Run12Root 'run12_inventory.json'
    $inventory = [ordered]@{ schema = 'GestureForge-S2A-T59-run12-inventory-v1'; task_id = 'S2A-T59'; run_id = 'run12'; status = 'DRYRUN_READY_NOT_SIMULATED'; baseline_head = $script:ExpectedHead; file_count = $records.Count; files = $records; directories = @('isolated_project', 'temp') }
    Write-NewUtf8 $inventoryPath (ConvertTo-Utf8Json $inventory)
    Write-Output 'PREPARE=PASS status=DRYRUN_READY_NOT_SIMULATED simulation=NOT_RUN outputs=run12_only'
    Write-Output "TB_SHA256=$($tbRecord.sha256)"
    Write-Output "RUNNER_SHA256=$($runnerRecord.sha256)"
    Write-Output "INVENTORY_SHA256=$((Get-FileRecord $inventoryPath).sha256)"
    Write-Output "TCL_COMMANDS=project:$($tcl.project_lines.Count),batch:$($tcl.simulation_lines.Count)"
}

function Invoke-RepairCanonicalRecovery {
    throw '原始归档动作已执行并失败；不得重搬原件，请使用 ResumeCanonicalRecovery。'
}

function Invoke-ResumeCanonicalRecovery {
    $hostBefore = Get-HostGate
    $parent = Get-ParentBinding
    Assert-Run12Shape
    $runnerRecord = Get-FileRecord $PSCommandPath
    $expectedExisting = @(
        'isolated_project\project_setup.tcl',
        'prepare.log',
        'prepare_summary.pre_recovery_stale.json',
        'project_preflight_binding.json',
        'run12_inventory.pre_recovery_stale.json',
        'run_project_sim_batch.tcl',
        'static_tcl_contract.json'
    ) | Sort-Object
    $existingFiles = @(Get-ChildItem -LiteralPath $script:Run12Root -File -Recurse -Force | ForEach-Object {
        Assert-NoReparseChain $_.FullName
        $_.FullName.Substring($script:Run12Root.Length + 1)
    } | Sort-Object)
    if (($existingFiles -join "`n") -cne ($expectedExisting -join "`n")) {
        throw "归档续写文件集合不符合冻结状态：$($existingFiles -join ',')"
    }

    foreach ($path in @($script:Run12SummaryPath, $script:Run12InventoryPath, (Join-Path $script:Run12Root 'canonical_recovery.log'))) {
        Assert-NoReparseChain $path -AllowMissingLeaf
        if ([System.IO.File]::Exists($path) -or [System.IO.Directory]::Exists($path)) { throw "续写目标已存在，拒绝覆盖：$path" }
    }
    foreach ($relative in @('isolated_project\project_setup.tcl', 'run_project_sim_batch.tcl', 'static_tcl_contract.json', 'project_preflight_binding.json')) {
        $record = Get-FileRecord (Join-Path $script:Run12Root $relative)
        Assert-Equal $record.sha256 $script:KnownPartialFileHashes[$relative] "续写静态文件 SHA $relative"
    }
    $staleSummaryRecord = Get-FileRecord $script:Run12StaleSummaryPath
    Assert-Equal $staleSummaryRecord.bytes $script:ExpectedStaleSummaryBytes '归档 stale summary bytes'
    Assert-Equal $staleSummaryRecord.sha256 $script:ExpectedStaleSummarySha '归档 stale summary SHA'
    $staleInventoryRecord = Get-FileRecord $script:Run12StaleInventoryPath
    Assert-Equal $staleInventoryRecord.bytes $script:ExpectedStaleInventoryBytes '归档 stale inventory bytes'
    Assert-Equal $staleInventoryRecord.sha256 $script:ExpectedStaleInventorySha '归档 stale inventory SHA'
    $prepareLogPath = Join-Path $script:Run12Root 'prepare.log'
    $prepareLogRecord = Get-FileRecord $prepareLogPath
    Assert-Equal $prepareLogRecord.bytes 1189 'Prepare 日志 bytes'
    Assert-Equal $prepareLogRecord.sha256 '72c0c87ce0dfc851a04870a618d907e36645f70ad9a7a7051f4019be10c1dc89' 'Prepare 日志 SHA'
    $prepareLogText = Get-Content -LiteralPath $prepareLogPath -Raw -Encoding UTF8
    foreach ($requiredText in @(
        'prior_attempt_1=FAIL exit_code=1 writes=false',
        'prior_attempt_2=FAIL exit_code=1 partial_files_created=true',
        'recovery_exit_code=0',
        "original_bound_runner_sha256=$($script:KnownPartialRunnerSha)",
        "recovery_runner_sha256=$($script:ExpectedRecoveryRunnerSha)"
    )) {
        if (-not $prepareLogText.Contains($requiredText)) { throw "Prepare 日志缺少恢复事实：$requiredText" }
    }
    $staleSummary = Get-Content -LiteralPath $script:Run12StaleSummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
    Assert-Equal $staleSummary.task_id 'S2A-T59' 'stale summary task'
    Assert-Equal $staleSummary.run_id 'run12' 'stale summary run'
    $staleHistory = @($staleSummary.prepare_attempt_history)
    $staleAttempt2 = @($staleHistory | Where-Object { [int]$_.attempt -eq 2 })
    Assert-Equal $staleAttempt2.Count 1 'stale summary attempt2 count'
    Assert-Equal $staleAttempt2[0].actual_exit_code 0 'stale summary original claim'
    $staleInventory = Get-Content -LiteralPath $script:Run12StaleInventoryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $staleInventory.recovery.status 'VERIFIED_PARTIAL_NO_OVERWRITE' 'stale inventory status'
    Assert-Equal $staleInventory.recovery.prior_prepare_attempt_2_exit_code 1 'stale inventory observed attempt2'
    Assert-Equal $staleInventory.recovery.original_runner_sha256 $script:KnownPartialRunnerSha 'stale inventory original runner'
    Assert-Equal $staleInventory.recovery.recovery_runner_sha256 $script:ExpectedRecoveryRunnerSha 'stale inventory recovery runner'

    $tb = New-TbCloneText
    Assert-ExistingText $script:AttemptTbPath $tb.text
    $tcl = New-TclPlan
    Assert-ExistingText $tcl.project_setup_path $tcl.project_text
    Assert-ExistingText $tcl.simulation_path $tcl.simulation_text
    $contractPath = Join-Path $script:Run12Root 'static_tcl_contract.json'
    $contract = Get-Content -LiteralPath $contractPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $contract.status 'PASS_STATIC_ONLY' '归档续写 TCL 合同状态'
    Assert-Equal $contract.project_setup.sha256 (Get-FileRecord $tcl.project_setup_path).sha256 '归档续写项目 Tcl SHA'
    Assert-Equal $contract.simulation_tcl.sha256 (Get-FileRecord $tcl.simulation_path).sha256 '归档续写 batch Tcl SHA'
    if ($contract.gui_option_present -or $contract.wdb_option_present -or $contract.waveform_commands_present) { throw '归档续写 batch Tcl 含 GUI/WDB/waveform' }
    $bindingPath = Join-Path $script:Run12Root 'project_preflight_binding.json'
    $binding = Get-Content -LiteralPath $bindingPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $binding.status 'DRYRUN_READY_NOT_SIMULATED' '归档续写 binding 状态'
    Assert-Equal $binding.runner.sha256 $script:KnownPartialRunnerSha '原始准备 runner SHA'
    Assert-Equal $binding.target_xpr.sha256 $parent.xpr.sha256 '归档续写 XPR SHA'
    Assert-Equal $binding.run11_failure_record.sha256 $parent.failure_record.sha256 '归档续写 run11 失败绑定'
    Assert-Equal $binding.attempt12_testbench.sha256 (Get-FileRecord $script:AttemptTbPath).sha256 '归档续写 attempt12 TB SHA'
    Assert-Equal $binding.temp_environment.TEMP $script:Run12TempRoot '归档续写 TEMP 路径'
    Assert-Equal $binding.temp_environment.TMP $script:Run12TempRoot '归档续写 TMP 路径'
    Assert-Equal $binding.temp_environment.TMPDIR $script:Run12TempRoot '归档续写 TMPDIR 路径'
    Assert-Equal (Get-FileRecord $script:TargetXprPath).sha256 $parent.xpr.sha256 '归档续写主 XPR SHA'

    $repairLogPath = Join-Path $script:Run12Root 'canonical_recovery.log'
    $repairLog = @(
        'task=S2A-T59 run=run12 mode=ResumeCanonicalRecovery',
        'prepare_attempt_1=FAIL exit_code=1 writes=false',
        'prepare_attempt_2=FAIL exit_code=1 partial_files_created=true',
        'prepare_attempt_3=PASS exit_code=0 runner_sha256=' + $script:ExpectedRecoveryRunnerSha,
        'evidence_repair_attempt_1=FAIL exit_code=1 cause=missing_PSCustomObject_property_after_archive_move',
        'evidence_repair_attempt_1_runner_sha256=' + $script:FailedCanonicalRepairRunnerSha,
        'evidence_repair_attempt_2=PASS exit_code=0 canonical_files_written_with_CreateNew=true',
        'evidence_repair_attempt_2_runner_sha256=' + $runnerRecord.sha256,
        'stale_prepare_summary_bytes=' + $staleSummaryRecord.bytes,
        'stale_prepare_summary_sha256=' + $staleSummaryRecord.sha256,
        'stale_inventory_bytes=' + $staleInventoryRecord.bytes,
        'stale_inventory_sha256=' + $staleInventoryRecord.sha256,
        'original_bound_runner_sha256=' + $script:KnownPartialRunnerSha,
        'prepare_recovery_runner_sha256=' + $script:ExpectedRecoveryRunnerSha,
        'TEMP=' + $script:Run12TempRoot,
        'TMP=' + $script:Run12TempRoot,
        'TMPDIR=' + $script:Run12TempRoot,
        'vivado_cli_invoked=false',
        'xsim_cli_invoked=false',
        'simulation=NOT_RUN'
    ) -join "`n"
    $repairLog += "`n"
    Write-NewUtf8 $repairLogPath $repairLog
    $repairLogRecord = Get-FileRecord $repairLogPath

    $canonicalSummary = Get-Content -LiteralPath $script:Run12StaleSummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json -AsHashtable
    $prepareHistory = @($canonicalSummary.prepare_attempt_history)
    $attempt2 = @($prepareHistory | Where-Object { [int]$_.attempt -eq 2 })
    Assert-Equal $attempt2.Count 1 'canonical attempt2 count'
    $attempt2[0].actual_exit_code = 1
    $attempt2[0].failure_reason = 'StrictMode 在 Assert-Run12Shape 中对空仿真输出集合访问 Count，Prepare 实际退出码为 1。'
    $attempt2[0].status = 'FAIL_AFTER_PARTIAL_ARTIFACT_CREATION'
    $prepareHistory += [ordered]@{
        attempt = 3
        actual_exit_code = 0
        files_written = $true
        recovery = $true
        failure_reason = '按五个冻结 partial SHA 核验后，以 CreateNew 补齐 prepare.log 和 inventory，未覆盖已有文件。'
        original_bound_runner_sha256 = $script:KnownPartialRunnerSha
        recovery_runner_sha256 = $script:ExpectedRecoveryRunnerSha
        status = 'DRYRUN_READY_NOT_SIMULATED'
    }
    $canonicalSummary.prepare_attempt_history = $prepareHistory
    $canonicalSummary.pre_recovery_stale_snapshot = [ordered]@{
        status = 'ARCHIVED_STALE_NOT_CANONICAL'
        prepare_summary = [ordered]@{ original_path = $script:Run12SummaryPath; archived_path = $script:Run12StaleSummaryPath; bytes = $staleSummaryRecord.bytes; sha256 = $staleSummaryRecord.sha256 }
        inventory = [ordered]@{ original_path = $script:Run12InventoryPath; archived_path = $script:Run12StaleInventoryPath; bytes = $staleInventoryRecord.bytes; sha256 = $staleInventoryRecord.sha256 }
    }
    $canonicalSummary.evidence_correction = [ordered]@{
        status = 'CANONICAL_RECOVERY_SUMMARY'
        actual_attempt2_exit_code = 1
        recovery_attempt3_exit_code = 0
        original_bound_runner_sha256 = $script:KnownPartialRunnerSha
        prepare_recovery_runner_sha256 = $script:ExpectedRecoveryRunnerSha
        recovery_runner_sha256 = $script:ExpectedRecoveryRunnerSha
        original_summary_archive_sha256 = $staleSummaryRecord.sha256
        original_inventory_archive_sha256 = $staleInventoryRecord.sha256
        repair_log = $repairLogRecord
        repair_attempt_history = @(
            [ordered]@{ attempt = 1; actual_exit_code = 1; runner_sha256 = $script:FailedCanonicalRepairRunnerSha; event = '旧文件已归档；添加缺失 PSCustomObject 属性时失败，canonical 文件尚未创建。' },
            [ordered]@{ attempt = 2; actual_exit_code = 0; runner_sha256 = $runnerRecord.sha256; event = '从已核验 stale 归档 CreateNew 创建 canonical recovery 证据。' }
        )
    }
    $summaryText = ConvertTo-Utf8Json $canonicalSummary
    Write-NewUtf8 $script:Run12SummaryPath $summaryText
    $summaryRecord = Get-FileRecord $script:Run12SummaryPath
    $records = @(Get-Run12FileRecords)
    $inventory = [ordered]@{
        schema = 'GestureForge-S2A-T59-run12-inventory-v1'
        task_id = 'S2A-T59'
        run_id = 'run12'
        status = 'DRYRUN_READY_NOT_SIMULATED'
        baseline_head = $script:ExpectedHead
        file_count = $records.Count
        files = $records
        directories = @('isolated_project', 'temp')
        recovery = [ordered]@{
            status = 'CANONICAL_RECOVERY_AFTER_STALE_ARCHIVE'
            original_prepare_summary = [ordered]@{ original_path = $script:Run12SummaryPath; archived_path = $script:Run12StaleSummaryPath; bytes = $staleSummaryRecord.bytes; sha256 = $staleSummaryRecord.sha256 }
            original_inventory = [ordered]@{ original_path = $script:Run12InventoryPath; archived_path = $script:Run12StaleInventoryPath; bytes = $staleInventoryRecord.bytes; sha256 = $staleInventoryRecord.sha256 }
            attempt2_actual_exit_code = 1
            recovery_attempt3_actual_exit_code = 0
            original_bound_runner_sha256 = $script:KnownPartialRunnerSha
            prepare_recovery_runner_sha256 = $script:ExpectedRecoveryRunnerSha
            recovery_runner_sha256 = $script:ExpectedRecoveryRunnerSha
            evidence_repair_attempt1_actual_exit_code = 1
            evidence_repair_attempt1_runner_sha256 = $script:FailedCanonicalRepairRunnerSha
            evidence_repair_attempt2_actual_exit_code = 0
            evidence_repair_attempt2_runner_sha256 = $runnerRecord.sha256
            repair_log = $repairLogRecord
        }
    }
    Write-NewUtf8 $script:Run12InventoryPath (ConvertTo-Utf8Json $inventory)
    Assert-Equal (Get-FileRecord $script:Run12SummaryPath).sha256 $summaryRecord.sha256 'canonical summary post-write SHA'
    Write-Output 'CANONICAL_RECOVERY=PASS stale_archives_verified=true canonical_create_new=true simulation=NOT_RUN'
    Write-Output "FAILED_REPAIR_RUNNER_SHA256=$($script:FailedCanonicalRepairRunnerSha)"
    Write-Output "SUCCESSFUL_REPAIR_RUNNER_SHA256=$($runnerRecord.sha256)"
    Write-Output "STALE_SUMMARY_SHA256=$($staleSummaryRecord.sha256)"
    Write-Output "STALE_INVENTORY_SHA256=$($staleInventoryRecord.sha256)"
    Write-Output "CANONICAL_SUMMARY_SHA256=$((Get-FileRecord $script:Run12SummaryPath).sha256)"
    Write-Output "CANONICAL_INVENTORY_SHA256=$((Get-FileRecord $script:Run12InventoryPath).sha256)"
}

function Invoke-AuditInventory {
    $hostGate = Get-HostGate
    $parent = Get-ParentBinding
    Assert-Run12Shape
    $inventoryPath = $script:Run12InventoryPath
    $inventoryRecord = Get-FileRecord $inventoryPath
    $inventory = Get-Content -LiteralPath $inventoryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $inventory.task_id 'S2A-T59' 'run12 inventory task'
    Assert-Equal $inventory.run_id 'run12' 'run12 inventory run'
    Assert-Equal $inventory.status 'DRYRUN_READY_NOT_SIMULATED' 'run12 inventory status'
    Assert-Equal $inventory.baseline_head $script:ExpectedHead 'run12 inventory HEAD'
    Assert-Equal $inventory.recovery.status 'CANONICAL_RECOVERY_AFTER_STALE_ARCHIVE' 'run12 recovery provenance'
    Assert-Equal $inventory.recovery.original_bound_runner_sha256 $script:KnownPartialRunnerSha 'inventory original runner SHA'
    Assert-Equal $inventory.recovery.recovery_runner_sha256 $script:ExpectedRecoveryRunnerSha 'inventory recovery runner SHA'
    Assert-Equal $inventory.recovery.attempt2_actual_exit_code 1 'inventory attempt2 actual exit code'
    Assert-Equal $inventory.recovery.recovery_attempt3_actual_exit_code 0 'inventory recovery attempt3 actual exit code'
    $staleSummaryRecord = Get-FileRecord $script:Run12StaleSummaryPath
    $staleInventoryRecord = Get-FileRecord $script:Run12StaleInventoryPath
    Assert-Equal $staleSummaryRecord.bytes $script:ExpectedStaleSummaryBytes 'archived stale summary bytes'
    Assert-Equal $staleSummaryRecord.sha256 $script:ExpectedStaleSummarySha 'archived stale summary SHA'
    Assert-Equal $staleInventoryRecord.bytes $script:ExpectedStaleInventoryBytes 'archived stale inventory bytes'
    Assert-Equal $staleInventoryRecord.sha256 $script:ExpectedStaleInventorySha 'archived stale inventory SHA'
    Assert-Equal $inventory.recovery.original_prepare_summary.original_path $script:Run12SummaryPath 'stale summary original path'
    Assert-Equal $inventory.recovery.original_prepare_summary.archived_path $script:Run12StaleSummaryPath 'stale summary archive path'
    Assert-Equal $inventory.recovery.original_prepare_summary.bytes $staleSummaryRecord.bytes 'inventory stale summary bytes'
    Assert-Equal $inventory.recovery.original_prepare_summary.sha256 $staleSummaryRecord.sha256 'inventory stale summary SHA'
    Assert-Equal $inventory.recovery.original_inventory.original_path $script:Run12InventoryPath 'stale inventory original path'
    Assert-Equal $inventory.recovery.original_inventory.archived_path $script:Run12StaleInventoryPath 'stale inventory archive path'
    Assert-Equal $inventory.recovery.original_inventory.bytes $staleInventoryRecord.bytes 'inventory stale inventory bytes'
    Assert-Equal $inventory.recovery.original_inventory.sha256 $staleInventoryRecord.sha256 'inventory stale inventory SHA'
    $prepareLogPath = Join-Path $script:Run12Root 'prepare.log'
    $prepareLogText = Get-Content -LiteralPath $prepareLogPath -Raw -Encoding UTF8
    Assert-Equal (Get-FileRecord $prepareLogPath).sha256 '72c0c87ce0dfc851a04870a618d907e36645f70ad9a7a7051f4019be10c1dc89' 'prepare.log original SHA'
    if (-not $prepareLogText.Contains("original_bound_runner_sha256=$($script:KnownPartialRunnerSha)")) { throw 'prepare.log 缺失旧 runner hash' }
    if (-not $prepareLogText.Contains("recovery_runner_sha256=$($script:ExpectedRecoveryRunnerSha)")) { throw 'prepare.log recovery runner hash 不符' }
    if (-not $prepareLogText.Contains('prior_attempt_2=FAIL exit_code=1')) { throw 'prepare.log 未保留第二次失败' }
    if (-not $prepareLogText.Contains('summary_attempt_2_claimed_exit_code=0 but observed command exit_code=1')) { throw 'prepare.log 未说明 summary/实际退出码差异' }
    $summaryPath = $script:Run12SummaryPath
    $summaryRecord = Get-FileRecord $summaryPath
    if ($summaryRecord.sha256 -ceq $script:ExpectedStaleSummarySha) { throw 'canonical summary 仍是 stale snapshot SHA' }
    $staleSummary = Get-Content -LiteralPath $script:Run12StaleSummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $staleSummaryAttempt2 = @($staleSummary.prepare_attempt_history | Where-Object { [int]$_.attempt -eq 2 })
    Assert-Equal $staleSummaryAttempt2.Count 1 'archived stale summary attempt2 count'
    Assert-Equal $staleSummaryAttempt2[0].actual_exit_code 0 'archived stale summary retained claim'
    $staleInventory = Get-Content -LiteralPath $script:Run12StaleInventoryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $staleInventory.recovery.status 'VERIFIED_PARTIAL_NO_OVERWRITE' 'archived stale inventory retained status'
    Assert-Equal $staleInventory.recovery.prior_prepare_attempt_2_exit_code 1 'archived stale inventory actual attempt2'
    if ($inventoryRecord.sha256 -ceq $script:ExpectedStaleInventorySha) { throw 'canonical inventory 仍是 stale snapshot SHA' }
    $summary = Get-Content -LiteralPath $summaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $summary.status 'DRYRUN_READY_NOT_SIMULATED' 'run12 summary status'
    $history = @($summary.prepare_attempt_history)
    $attempt2History = @($history | Where-Object { [int]$_.attempt -eq 2 })
    $attempt3History = @($history | Where-Object { [int]$_.attempt -eq 3 })
    Assert-Equal $attempt2History.Count 1 'canonical summary attempt2 count'
    Assert-Equal $attempt2History[0].actual_exit_code 1 'canonical summary attempt2 actual exit code'
    Assert-Equal $attempt2History[0].status 'FAIL_AFTER_PARTIAL_ARTIFACT_CREATION' 'canonical summary attempt2 status'
    Assert-Equal $attempt3History.Count 1 'canonical summary recovery attempt3 count'
    Assert-Equal $attempt3History[0].actual_exit_code 0 'canonical summary recovery attempt3 actual exit code'
    Assert-Equal $attempt3History[0].recovery_runner_sha256 $script:ExpectedRecoveryRunnerSha 'canonical summary recovery runner SHA'
    Assert-Equal $summary.runner.sha256 $script:KnownPartialRunnerSha 'canonical summary original bound runner SHA'
    Assert-Equal $summary.evidence_correction.status 'CANONICAL_RECOVERY_SUMMARY' 'summary recovery correction status'
    Assert-Equal $summary.evidence_correction.actual_attempt2_exit_code 1 'summary correction attempt2 exit code'
    Assert-Equal $summary.evidence_correction.recovery_attempt3_exit_code 0 'summary correction attempt3 exit code'
    Assert-Equal $summary.evidence_correction.original_bound_runner_sha256 $script:KnownPartialRunnerSha 'summary correction original runner SHA'
    Assert-Equal $summary.evidence_correction.recovery_runner_sha256 $script:ExpectedRecoveryRunnerSha 'summary correction recovery runner SHA'
    Assert-Equal $summary.pre_recovery_stale_snapshot.status 'ARCHIVED_STALE_NOT_CANONICAL' 'summary stale archive status'
    Assert-Equal $summary.pre_recovery_stale_snapshot.prepare_summary.sha256 $staleSummaryRecord.sha256 'summary stale archive SHA'
    Assert-Equal $summary.pre_recovery_stale_snapshot.inventory.sha256 $staleInventoryRecord.sha256 'summary stale inventory SHA'
    Assert-Equal $summary.evidence_correction.original_summary_archive_sha256 $staleSummaryRecord.sha256 'summary correction archived summary SHA'
    Assert-Equal $summary.evidence_correction.original_inventory_archive_sha256 $staleInventoryRecord.sha256 'summary correction archived inventory SHA'
    $repairHistory = @($summary.evidence_correction.repair_attempt_history)
    Assert-Equal $repairHistory.Count 2 'evidence repair history count'
    $failedRepair = @($repairHistory | Where-Object { [int]$_.attempt -eq 1 })
    $successfulRepair = @($repairHistory | Where-Object { [int]$_.attempt -eq 2 })
    Assert-Equal $failedRepair.Count 1 'failed evidence repair count'
    Assert-Equal $failedRepair[0].actual_exit_code 1 'failed evidence repair exit code'
    Assert-Equal $failedRepair[0].runner_sha256 $script:FailedCanonicalRepairRunnerSha 'failed evidence repair runner SHA'
    Assert-Equal $successfulRepair.Count 1 'successful evidence repair count'
    Assert-Equal $successfulRepair[0].actual_exit_code 0 'successful evidence repair exit code'
    Assert-Equal $successfulRepair[0].runner_sha256 $script:SuccessfulCanonicalRepairRunnerSha 'successful evidence repair runner SHA'
    $repairLogPath = Join-Path $script:Run12Root 'canonical_recovery.log'
    $repairLogRecord = Get-FileRecord $repairLogPath
    Assert-Equal $repairLogRecord.sha256 $summary.evidence_correction.repair_log.sha256 'canonical repair log SHA'
    Assert-Equal $repairLogRecord.bytes $summary.evidence_correction.repair_log.bytes 'canonical repair log bytes'
    $repairLogText = Get-Content -LiteralPath $repairLogPath -Raw -Encoding UTF8
    if ($repairLogText -notmatch ('evidence_repair_attempt_1_runner_sha256=\s*' + [regex]::Escape($script:FailedCanonicalRepairRunnerSha))) { throw 'canonical repair log missing failed runner SHA' }
    if ($repairLogText -notmatch ('evidence_repair_attempt_2_runner_sha256=\s*' + [regex]::Escape($script:SuccessfulCanonicalRepairRunnerSha))) { throw 'canonical repair log missing successful runner SHA' }
    Assert-Equal $inventory.recovery.evidence_repair_attempt1_actual_exit_code 1 'inventory failed evidence repair exit code'
    Assert-Equal $inventory.recovery.evidence_repair_attempt1_runner_sha256 $script:FailedCanonicalRepairRunnerSha 'inventory failed repair runner SHA'
    Assert-Equal $inventory.recovery.evidence_repair_attempt2_actual_exit_code 0 'inventory successful evidence repair exit code'
    Assert-Equal $inventory.recovery.evidence_repair_attempt2_runner_sha256 $script:SuccessfulCanonicalRepairRunnerSha 'inventory successful repair runner SHA'
    Assert-Equal $inventory.recovery.repair_log.sha256 $repairLogRecord.sha256 'inventory repair log SHA'
    $actual = Get-Run12FileRecords
    Assert-Equal $inventory.file_count $actual.Count 'run12 inventory file count'
    $expected = @{}
    foreach ($entry in $inventory.files) { $expected[[string]$entry.path] = $entry }
    Assert-Equal $expected.Count $actual.Count 'run12 inventory unique file count'
    foreach ($entry in $actual) {
        if (-not $expected.ContainsKey([string]$entry.path)) { throw "inventory 缺少文件：$($entry.path)" }
        Assert-Equal $entry.bytes $expected[[string]$entry.path].bytes "inventory bytes $($entry.path)"
        Assert-Equal $entry.sha256 $expected[[string]$entry.path].sha256 "inventory SHA $($entry.path)"
    }
    $tbClone = New-TbCloneText
    Assert-ExistingText $script:AttemptTbPath $tbClone.text
    $bindingPath = Join-Path $script:Run12Root 'project_preflight_binding.json'
    $contractPath = Join-Path $script:Run12Root 'static_tcl_contract.json'
    $binding = Get-Content -LiteralPath $bindingPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $contract = Get-Content -LiteralPath $contractPath -Raw -Encoding UTF8 | ConvertFrom-Json
    Assert-Equal $summary.current_head $hostGate.head 'run12 summary HEAD'
    Assert-Equal $binding.status 'DRYRUN_READY_NOT_SIMULATED' 'run12 binding status'
    Assert-Equal $binding.run11_failure_record.sha256 $parent.failure_record.sha256 'run11 failure binding'
    Assert-Equal $binding.run11_original_inventory.sha256 $parent.run11_inventory_record.sha256 'run11 original inventory binding'
    Assert-Equal $binding.target_xpr.sha256 $parent.xpr.sha256 'run12 XPR binding'
    Assert-Equal $binding.attempt12_testbench.sha256 (Get-FileRecord $script:AttemptTbPath).sha256 'run12 TB binding'
    Assert-Equal $binding.runner.sha256 $script:KnownPartialRunnerSha 'run12 original prepare runner binding'
    Assert-Equal $summary.runner.sha256 $script:KnownPartialRunnerSha 'run12 summary original prepare runner binding'
    Assert-Equal $binding.temp_environment.TEMP $script:Run12TempRoot 'TEMP binding'
    Assert-Equal $binding.temp_environment.TMP $script:Run12TempRoot 'TMP binding'
    Assert-Equal $binding.temp_environment.TMPDIR $script:Run12TempRoot 'TMPDIR binding'
    Assert-Equal $contract.status 'PASS_STATIC_ONLY' 'run12 static Tcl status'
    if ($contract.gui_option_present -or $contract.wdb_option_present -or $contract.waveform_commands_present) { throw 'run12 静态 Tcl 合同意外声明 GUI/WDB/waveform' }
    foreach ($record in @($contract.project_setup, $contract.simulation_tcl)) { Assert-Equal (Get-FileRecord $record.path).sha256 $record.sha256 "Tcl SHA $($record.path)" }
    Assert-Equal (Get-FileRecord $script:TargetXprPath).sha256 $parent.xpr.sha256 'Audit 主 XPR SHA'
    Write-Output 'AUDIT_INVENTORY=PASS status=DRYRUN_READY_NOT_SIMULATED recovery=CANONICAL_RECOVERY_AFTER_STALE_ARCHIVE simulation=NOT_RUN'
    Write-Output "INVENTORY_SHA256=$($inventoryRecord.sha256)"
    Write-Output "INVENTORY_FILES=$($inventory.file_count)"
    Write-Output "ARCHIVED_STALE_SUMMARY_SHA256=$($staleSummaryRecord.sha256)"
    Write-Output "ARCHIVED_STALE_INVENTORY_SHA256=$($staleInventoryRecord.sha256)"
    Write-Output "CANONICAL_SUMMARY_SHA256=$($summaryRecord.sha256)"
    Write-Output "CURRENT_HEAD=$($hostGate.head)"
}

if ($Mode -eq 'Prepare') {
    Invoke-Prepare
} elseif ($Mode -eq 'RepairCanonicalRecovery') {
    Invoke-RepairCanonicalRecovery
} elseif ($Mode -eq 'ResumeCanonicalRecovery') {
    Invoke-ResumeCanonicalRecovery
} else {
    Invoke-AuditInventory
}
