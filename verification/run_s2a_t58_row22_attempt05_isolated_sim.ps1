[CmdletBinding()]
param(
    [ValidateSet('Prepare', 'AuditInventory')]
    [string]$Mode = 'Prepare'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$RepoRoot = 'D:\FPGA_Competition'
$EvidenceRoot = Join-Path $RepoRoot 'report\evidence\S2A-T58'
$Run02 = Join-Path $EvidenceRoot 'run02'
$Run03 = Join-Path $EvidenceRoot 'run03'
$Run04 = Join-Path $EvidenceRoot 'run04'
$Run05 = Join-Path $EvidenceRoot 'run05'
$Tb = Join-Path $RepoRoot 'sim\tb_s2a_conv_layer35_row22_attempt05.sv'
$PriorTb = Join-Path $RepoRoot 'sim\tb_s2a_conv_layer35_row22_attempt04.sv'
$Xpr = Join-Path $RepoRoot 'vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr'
$T56Report = Join-Path $RepoRoot 'report\evidence\S2A-T56\layer35_row20_all_channels.json'
$T56Summary = Join-Path $RepoRoot 'report\evidence\S2A-T56\mcp_project_run01\simulation_summary.json'
$Verifier = Join-Path $RepoRoot 'verification\test_s2a_conv_layer35_row22_all_channels_rtl.py'
$OriginalTb = Join-Path $RepoRoot 'sim\tb_s2a_conv_layer35_row22_all_channels.sv'
$ProjectTcl = Join-Path $Run05 'run_project_sim.tcl'
$XsimTcl = Join-Path $Run05 'xsim_run.tcl'
$BindingPath = Join-Path $Run05 'isolated_sim_binding.json'
$PlanPath = Join-Path $Run05 'dryrun_plan.json'
$SummaryPath = Join-Path $Run05 'dryrun_summary.json'
$InventoryPath = Join-Path $Run05 'isolated_run_inventory.json'
$BaseHead = 'a8d19fbdc3389682b888f2d8add2cdd77af4503c'
$Run02SummarySha = 'f5b170ba5ec2c25fd8c7c917035ab6bb1fe46847198bd74ea0ffb27cbbdcbba6'
$Run02BindingSha = '24fd56415f60f5fe441d039d9f5458be21a4f95759244aa32e13828e9676cb4d'
$T56ReportSha = '44a25b6b5af6f8868dd2cb9780c4834bdd87860ba43a71b0c696c0b67627da12'
$T56SummarySha = 'eceb674cdc63c25bcc990885e27a81690efbd1312a095a07fd1d8c3235ac9e0b'
$XprSha = '9e637bb8a31c8c74cdb703d632282a020875f5623893665719c1bbb5035be1ec'
$Run03ContentPath = Join-Path $Run03 'run02_prepared_content_verify.stdout.json'
$Run03ContentSha = '006ab22ab4595e30d866a5403803748afe720587beb6442bf151f17de610f51e'
$Run03ContentErrPath = Join-Path $Run03 'run02_prepared_content_verify.stderr.bin'
$Run03ContentErrSha = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
$Run03DryrunPath = Join-Path $Run03 'dryrun_summary.json'
$Run03DryrunSha = '013af49da8460fb84d35987172f7a22ab074c71423bdd3314ae305cea8bfcdbc'
$Run03CliPath = Join-Path $Run03 'run02_cli_verify_sibling_guard.json'
$Run03CliSha = 'c36a3a6bc9484b2572ec1e95afd8c088457f6400821338696b7a0edfd266a25e'
$Run03CliOutPath = Join-Path $Run03 'run02_verify.stdout.json'
$Run03CliOutSha = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
$Run03CliErrPath = Join-Path $Run03 'run02_verify.stderr.bin'
$Run03CliErrSha = '317f5b0b86f0e91b27f55c1ddeb287d3ef30b35d116a7ac5d9276d60f19e32b4'
$ProcessNames = '^(vivado|vivado_lab|xsim|xsimk|xelab|xvlog|xvhdl|xsct|hw_server)(\.exe)?$'
$ExpectedRtl = [ordered]@{
    'src/int8_conv_tap_geometry.sv' = '109b58473fa2f5d6de5c362e0c780ae2e98bce260c1d92714fde58ae706e4bbc'
    'src/int8_conv_weight_address.sv' = '0914df477c9e160d227c74f9eaf926e502069e563145e1e1f3e03673654d4592'
    'src/int8_mac_accumulator.sv' = 'b3f6a425e2db58b86c63524b9caf0019ddf7a103c5b66f8bfcc3cf86966d0a74'
    'src/s2a_conv_engine.sv' = '8656f43f510a8f7c74aaee44f809da74adeb3b8c5fed32f8f009aabecb05c994'
    'src/s2a_conv_layer35_channel_probe.sv' = '91f1e954c1a50a0047861b40df75d1f0523ae2307f03d0c7328abaf4d5469ef4'
}
$ExpectedFixture = [ordered]@{
    'feature_input.bin' = @{ bytes = 259584; sha256 = 'f7cbcdae9627c974b0210b3329be66a4264d96d0e2474d3c7f30a1b9c2f59ff1' }
    'layer35_weights.bin' = @{ bytes = 884736; sha256 = 'e7b7d6fd8511b918d0a3ee372ef9d35eb4f3a2827fac77e28cf4f9d775d85bc2' }
    'golden.bin' = @{ bytes = 33280; sha256 = '0892e785cfb724eb10c9fd39b5bdba2836fa4eb9c0374dd31e5fd2aa7ce50271' }
    'vectors.txt' = @{ bytes = 254606; sha256 = 'ba7d9a9944fe0d1a2b62b7831fea6963a0e86945e68f0feaf4c73ce55fcaffed' }
}
$InventoryNames = @('dryrun_plan.json', 'dryrun_summary.json', 'isolated_sim_binding.json', 'run_project_sim.tcl', 'xsim_run.tcl')

function Require([bool]$Condition, [string]$Message) { if (-not $Condition) { throw $Message } }
function Get-Sha([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Get-Artifact([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force
    [ordered]@{ path = [IO.Path]::GetFullPath($Path); bytes = [int64]$item.Length; sha256 = Get-Sha $Path }
}
function Read-Json([string]$Path) { Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json }
function Write-NewJson([string]$Path, [object]$Value) {
    Require (-not (Test-Path -LiteralPath $Path)) ('拒绝覆盖：' + $Path)
    $text = (ConvertTo-Json -InputObject $Value -Depth 64) + "`n"
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($text)
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
}
function Write-NewText([string]$Path, [string]$Text) {
    Require (-not (Test-Path -LiteralPath $Path)) ('拒绝覆盖：' + $Path)
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($Text)
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
}
function Assert-NoReparse([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    $boundary = [IO.Path]::GetFullPath($RepoRoot).TrimEnd([char]92)
    Require ($full.Equals($boundary, [StringComparison]::OrdinalIgnoreCase) -or $full.StartsWith($boundary + '\', [StringComparison]::OrdinalIgnoreCase)) ('仓库路径越界：' + $full)
    $cursor = $full
    while ($true) {
        $item = Get-Item -LiteralPath $cursor -Force
        Require (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) ('拒绝 reparse 路径：' + $cursor)
        if ($cursor.Equals($boundary, [StringComparison]::OrdinalIgnoreCase)) { break }
        $parent = [IO.Directory]::GetParent($cursor)
        Require ($null -ne $parent) ('仓库路径缺少父目录：' + $full)
        $cursor = $parent.FullName
    }
}
function Get-ProcessSnapshot {
    @(Get-CimInstance -ClassName Win32_Process | Where-Object { $_.Name -match $ProcessNames } | Sort-Object ProcessId | ForEach-Object { [ordered]@{ name = $_.Name; pid = [int]$_.ProcessId; command_line = $_.CommandLine } })
}
function Get-Head {
    $value = & git -C $RepoRoot rev-parse HEAD
    Require ($LASTEXITCODE -eq 0) '读取 HEAD 失败'
    ([string]$value).Trim().ToLowerInvariant()
}
function Get-Tree([string]$Path) {
    Assert-NoReparse $Path
    $root = [IO.Path]::GetFullPath($Path).TrimEnd([char]92) + '\'
    $dirs = [Collections.Generic.List[string]]::new()
    $files = [Collections.Generic.List[object]]::new()
    $stack = [Collections.Generic.Stack[string]]::new()
    $stack.Push([IO.Path]::GetFullPath($Path))
    while ($stack.Count -gt 0) {
        $dir = $stack.Pop()
        foreach ($entry in [IO.Directory]::EnumerateFileSystemEntries($dir)) {
            $attr = [IO.File]::GetAttributes($entry)
            Require (($attr -band [IO.FileAttributes]::ReparsePoint) -eq 0) ('目录快照发现 reparse：' + $entry)
            $relative = $entry.Substring($root.Length).Replace('\', '/')
            if (($attr -band [IO.FileAttributes]::Directory) -ne 0) { $dirs.Add($relative); $stack.Push($entry) }
            else { $files.Add([ordered]@{ relative_path = $relative; bytes = [int64](Get-Item -LiteralPath $entry).Length; sha256 = Get-Sha $entry }) }
        }
    }
    $dirs.Sort([StringComparer]::Ordinal)
    $sortedFiles = @($files.ToArray() | Sort-Object relative_path)
    $rows = [Collections.Generic.List[string]]::new()
    $rows.Add('ROOT|' + [IO.Path]::GetFullPath($Path))
    foreach ($dir in $dirs) { $rows.Add('D|' + $dir) }
    foreach ($file in $sortedFiles) { $rows.Add('F|' + $file.relative_path + '|' + $file.bytes + '|' + $file.sha256) }
    $payload = [Text.UTF8Encoding]::new($false).GetBytes(([string]::Join("`n", $rows.ToArray())) + "`n")
    $fingerprint = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($payload)).ToLowerInvariant()
    [ordered]@{ root = [IO.Path]::GetFullPath($Path); directories = @($dirs.ToArray()); files = $sortedFiles; fingerprint_sha256 = $fingerprint }
}
function Assert-SameTree($Before, $After, [string]$Label) {
    Require ($Before.fingerprint_sha256 -ceq $After.fingerprint_sha256) ($Label + ' 前后目录 SHA/清单变化')
}
function Assert-Hash([string]$Path, [string]$Expected, [string]$Label) {
    Assert-NoReparse $Path
    $artifact = Get-Artifact $Path
    Require ($artifact.sha256 -ceq $Expected.ToLowerInvariant()) ($Label + ' SHA 不匹配：' + $artifact.sha256)
    $artifact
}
function Get-Run02SourceBinding {
    $summaryPath = Join-Path $Run02 'prepare_summary.json'
    $bindingPath = Join-Path $Run02 'project_preflight_binding.json'
    $summaryArtifact = Assert-Hash $summaryPath $Run02SummarySha 'run02 prepare_summary'
    $bindingArtifact = Assert-Hash $bindingPath $Run02BindingSha 'run02 project binding'
    $summary = Read-Json $summaryPath
    $projectBinding = Read-Json $bindingPath
    Require ($summary.task_id -ceq 'S2A-T58' -and $summary.run_id -ceq 'run02' -and $summary.status -ceq 'PREPARED_NOT_SIMULATED') 'run02 摘要身份/状态不符'
    Require ($projectBinding.task_id -ceq 'S2A-T58' -and $projectBinding.run_id -ceq 'run02' -and $projectBinding.status -ceq 'READ_ONLY_BOUND') 'run02 工程绑定身份/状态不符'
    Require ($projectBinding.target_xpr_sha256_before_prepare -ceq $XprSha -and $projectBinding.target_xpr_sha256_after_prepare -ceq $XprSha -and $projectBinding.target_xpr_unchanged -eq $true) 'run02 XPR 绑定不符'
    Require ((Get-Sha $Xpr) -ceq $XprSha) '目标 XPR 哈希变化'
    Require ((Assert-Hash $T56Report $T56ReportSha 'T56 report').sha256 -ceq $projectBinding.preparation_inputs.T56_parent_report.sha256) 'T56 report 未绑定 run02'
    Require ((Assert-Hash $T56Summary $T56SummarySha 'T56 summary').sha256 -ceq $projectBinding.preparation_inputs.T56_summary.sha256) 'T56 summary 未绑定 run02'
    $t56 = Read-Json $T56Report
    Require ($t56.task_id -ceq 'S2A-T56' -and $t56.status -ceq 'PASS_SIMULATION_DATA_ONLY' -and $t56.acceptance_status -ceq 'PASS_INDEPENDENT_REVIEW_DATA_ONLY') 'T56 父报告状态不符'
    $sourceRecords = [ordered]@{}
    foreach ($relative in $ExpectedRtl.Keys) {
        $path = Join-Path $RepoRoot $relative.Replace('/', '\')
        $sourceRecords[$relative] = Assert-Hash $path $ExpectedRtl[$relative] ('RTL ' + $relative)
        Require ([string]$projectBinding.T58_source_hashes.$relative -ceq $ExpectedRtl[$relative] -and [string]$summary.bindings.T58_source_hashes.$relative -ceq $ExpectedRtl[$relative]) ('run02 RTL 绑定不符：' + $relative)
    }
    Require ([string]$projectBinding.T58_source_hashes.'sim/tb_s2a_conv_layer35_row22_all_channels.sv' -ceq 'd66dc1f1d58e5214ddbc4739b878f3662d281d40d19b2d5c49a280a885ace688') 'run02 原 TB 绑定不符'
    Require ([string]$projectBinding.T58_source_hashes.'verification/test_s2a_conv_layer35_row22_all_channels_rtl.py' -ceq 'c61c5ed246fc0568a520db58a9dfaabf8e7b3152476faf33190f52565c2f0b07') 'run02 官方 runner 绑定不符'
    $sourceRecords['sim/tb_s2a_conv_layer35_row22_all_channels.sv'] = Assert-Hash $OriginalTb 'd66dc1f1d58e5214ddbc4739b878f3662d281d40d19b2d5c49a280a885ace688' '原始 TB'
    $sourceRecords['verification/test_s2a_conv_layer35_row22_all_channels_rtl.py'] = Assert-Hash $Verifier 'c61c5ed246fc0568a520db58a9dfaabf8e7b3152476faf33190f52565c2f0b07' '官方 runner'
    $fixtureRoot = Join-Path $Run02 'fixture'
    foreach ($name in $ExpectedFixture.Keys) {
        $record = Assert-Hash (Join-Path $fixtureRoot $name) $ExpectedFixture[$name].sha256 ('run02 fixture ' + $name)
        Require ($record.bytes -eq $ExpectedFixture[$name].bytes) ('run02 fixture 长度错误：' + $name)
        $sourceRecords['report/evidence/S2A-T58/run02/fixture/' + $name] = $record
        Require ([string]$summary.fixture.files.$name.sha256 -ceq $record.sha256 -and [int64]$summary.fixture.files.$name.bytes -eq $record.bytes) ('run02 summary fixture 引用不符：' + $name)
    }
    Require ($summary.fixture.manifest.path -ceq (Join-Path $fixtureRoot 'fixture_manifest.json')) 'run02 manifest 路径不符'
    $manifestArtifact = Assert-Hash (Join-Path $fixtureRoot 'fixture_manifest.json') ([string]$summary.fixture.manifest.sha256) 'run02 fixture manifest'
    Require ($manifestArtifact.bytes -eq [int64]$summary.fixture.manifest.bytes) 'run02 manifest 长度不符'
    $manifest = Read-Json (Join-Path $fixtureRoot 'fixture_manifest.json')
    Require ($manifest.task_id -ceq 'S2A-T58' -and $manifest.run_id -ceq 'run02' -and $manifest.fixed_points_yx.Count -eq 26 -and $manifest.oracle.raw_int32_count -eq 6656 -and $manifest.oracle.quantized_int8_count -eq 6656) 'run02 manifest scope/count 不符'
    $sourceRecords['report/evidence/S2A-T58/run02/prepare_summary.json'] = $summaryArtifact
    $sourceRecords['report/evidence/S2A-T58/run02/project_preflight_binding.json'] = $bindingArtifact
    $sourceRecords['report/evidence/S2A-T58/run02/fixture/fixture_manifest.json'] = $manifestArtifact
    $sourceRecords['report/evidence/S2A-T56/layer35_row20_all_channels.json'] = Get-Artifact $T56Report
    $sourceRecords['report/evidence/S2A-T56/mcp_project_run01/simulation_summary.json'] = Get-Artifact $T56Summary
    $sourceRecords['vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr'] = Get-Artifact $Xpr
    [ordered]@{ summary = $summary; project_binding = $projectBinding; summary_artifact = $summaryArtifact; binding_artifact = $bindingArtifact; fixture_manifest = $manifestArtifact; sources = $sourceRecords }
}
function Assert-Run03References {
    $contentArtifact = Assert-Hash $Run03ContentPath $Run03ContentSha 'run03 内容核验 stdout'
    $contentErr = Assert-Hash $Run03ContentErrPath $Run03ContentErrSha 'run03 内容核验 stderr'
    $content = Read-Json $Run03ContentPath
    Require ($content.result -ceq 'PREPARED_NOT_SIMULATED' -and $content.simulation -ceq 'NOT_RUN' -and $content.output_counts.raw_int32 -eq 6656 -and $content.output_counts.int8 -eq 6656 -and $content.output_counts.d2_t23_matches -eq 6656) 'run03 内容核验记录失败或计数不符'
    $dryrun = Assert-Hash $Run03DryrunPath $Run03DryrunSha 'run03 dryrun summary'
    $dryrunJson = Read-Json $Run03DryrunPath
    Require ($dryrunJson.run_id -ceq 'run03' -and $dryrunJson.status -ceq 'DRYRUN_READY_NOT_SIMULATED' -and $dryrunJson.simulation -ceq 'NOT_RUN') 'run03 dryrun 状态不符'
    $cli = Assert-Hash $Run03CliPath $Run03CliSha 'run03 官方 CLI 门禁记录'
    $cliJson = Read-Json $Run03CliPath
    Require ($cliJson.status -ceq 'BLOCKED_BY_RUN03_SIBLING_ROOT_INVENTORY' -and $cliJson.exit_code -eq 1) 'run03 官方 CLI 门禁状态不符'
    $cliOut = Assert-Hash $Run03CliOutPath $Run03CliOutSha 'run03 官方 CLI stdout'
    $cliErr = Assert-Hash $Run03CliErrPath $Run03CliErrSha 'run03 官方 CLI stderr'
    Require ($cliJson.stdout.sha256 -ceq $cliOut.sha256 -and $cliJson.stderr.sha256 -ceq $cliErr.sha256 -and $cliErr.bytes -eq 315) 'run03 官方 CLI 原始输出引用不符'
    [ordered]@{ full_prepared_verify = $contentArtifact; full_prepared_verify_stderr = $contentErr; run03_summary = $dryrun; cli_guard_record = $cli; cli_stdout = $cliOut; cli_stderr = $cliErr; status = $content.result; raw_int32 = 6656; int8 = 6656; d2_t23_matches = 6656; simulation = 'NOT_RUN'; official_cli = 'BLOCKED_BY_RUN03_SIBLING_ROOT_INVENTORY' }
}
function Assert-Tb([string]$ExpectedRun) {
    $tbText = [IO.File]::ReadAllText($Tb, [Text.UTF8Encoding]::new($false, $true))
    Require (([regex]::Matches($tbText, 'D:\\\\FPGA_Competition\\\\report\\\\evidence\\\\S2A-T58\\\\run02\\\\fixture\\\\')).Count -eq 4) 'attempt05 TB run02 fixture 输入数不符'
    $outputPathCount = [regex]::Matches($tbText, ('D:\\\\FPGA_Competition\\\\report\\\\evidence\\\\S2A-T58\\\\' + $ExpectedRun + '\\\\')).Count
    Require ($outputPathCount -eq 2) 'attempt05 TB 输出根路径不符'
    Require (([regex]::Matches($tbText, 'module tb_s2a_conv_layer35_row22_attempt05;')).Count -eq 1) 'attempt05 TB 模块名不符'
    Require (([regex]::Matches($tbText, 'T58_XSIM_SENTINEL=PASS_RUN05')).Count -eq 1) 'attempt05 sentinel 不唯一'
    Require (([regex]::Matches($tbText, '\$finish;')).Count -eq 1) 'attempt05 $finish 不唯一'
    Require (-not $tbText.Contains('S2A-T58\\run04\\observed_') -and -not $tbText.Contains('S2A-T58\\run03\\observed_')) 'attempt05 TB 仍指向旧 attempt 输出'
    Get-Artifact $Tb
}
function Assert-RootNames([string[]]$Expected) {
    $actual = @(Get-ChildItem -LiteralPath $EvidenceRoot -Force | ForEach-Object { $_.Name } | Sort-Object)
    $want = @($Expected | Sort-Object)
    Require (($actual -join '|') -ceq ($want -join '|')) ('T58 evidence root 节点不符：' + ($actual -join ','))
}
function Assert-Run05Inventory {
    Assert-NoReparse $Run05
    Assert-RootNames @('project_preflight_binding.json', 'run01', 'run02', 'run03', 'run04', 'run05')
    $inventory = Read-Json $InventoryPath
    Require ($inventory.schema -ceq 'GestureForge-S2A-T58-run05-inventory-v1' -and $inventory.run_id -ceq 'run05' -and $inventory.simulation -ceq 'NOT_RUN') 'run05 inventory 身份/状态不符'
    $actualNames = @(Get-ChildItem -LiteralPath $Run05 -Force | ForEach-Object { $_.Name } | Sort-Object)
    $expectedNames = @($InventoryNames + 'isolated_run_inventory.json' | Sort-Object)
    Require (($actualNames -join '|') -ceq ($expectedNames -join '|')) 'run05 evidence 文件清单不符'
    foreach ($record in @($inventory.evidence_files)) {
        $artifact = Get-Artifact (Join-Path $Run05 ([string]$record.relative_path))
        Require ($artifact.path -ceq $record.artifact.path -and $artifact.bytes -eq [int64]$record.artifact.bytes -and $artifact.sha256 -ceq $record.artifact.sha256) ('run05 文件 SHA/长度不符：' + $record.relative_path)
    }
    $binding = Read-Json $BindingPath
    Require ($binding.launcher.sha256 -ceq (Get-Sha $PSCommandPath) -and $binding.tb.sha256 -ceq (Get-Sha $Tb)) 'run05 源码绑定变化'
    foreach ($property in $binding.sources.PSObject.Properties) {
        $actualSource = Assert-Hash ([string]$property.Value.path) ([string]$property.Value.sha256) ('run05 source ' + $property.Name)
        Require ($actualSource.bytes -eq [int64]$property.Value.bytes) ('run05 source 长度变化：' + $property.Name)
    }
    Require ((Assert-Tb 'run05').sha256 -ceq $binding.tb.sha256) 'run05 TB 重新校验失败'
    Require ((Get-Sha $ProjectTcl) -ceq $binding.project_tcl.sha256 -and (Get-Sha $XsimTcl) -ceq $binding.xsim_tcl.sha256) 'run05 Tcl 绑定变化'
    $summary = Read-Json $SummaryPath
    foreach ($key in @('run02', 'run03', 'run04')) {
        $current = Get-Tree (Join-Path $EvidenceRoot $key)
        Require ($current.fingerprint_sha256 -ceq $summary.preserved_trees.$key.fingerprint_sha256) ('旧证据目录发生变化：' + $key)
    }
    Require ((Get-Sha $Xpr) -ceq $summary.preserved_xpr.sha256 -and (Get-Sha $Xpr) -ceq $XprSha) '目标 XPR SHA 变化'
    Require ((Get-Head) -ceq $BaseHead) 'HEAD 不再等于冻结基线'
    $processes = @(Get-ProcessSnapshot)
    Require ($processes.Count -eq 0) 'AuditInventory 检测到 Vivado/XSim 进程'
    [ordered]@{ status = 'PASS_READ_ONLY_RUN05_INVENTORY'; run_id = 'run05'; file_count = $inventory.evidence_files.Count; tb_sha256 = $binding.tb.sha256; project_tcl_sha256 = $binding.project_tcl.sha256; xsim_tcl_sha256 = $binding.xsim_tcl.sha256; preserved_run02_run03_run04 = $true; xpr_sha256 = $XprSha; process_count = 0 }
}
function Invoke-Prepare {
    Require ([IO.Path]::GetFullPath((Get-Location).Path).Equals($RepoRoot, [StringComparison]::OrdinalIgnoreCase)) '必须从仓库根目录执行'
    Require ((Get-Head) -ceq $BaseHead) 'HEAD 与任务卡冻结基线不一致'
    Require (-not (Test-Path -LiteralPath $Run05)) 'run05 已存在；拒绝覆盖'
    Assert-RootNames @('project_preflight_binding.json', 'run01', 'run02', 'run03', 'run04')
    $processBefore = @(Get-ProcessSnapshot)
    Require ($processBefore.Count -eq 0) '准备前存在 Vivado/XSim 进程'
    $before = [ordered]@{ run02 = Get-Tree $Run02; run03 = Get-Tree $Run03; run04 = Get-Tree $Run04; xpr = Get-Artifact $Xpr }
    Require ($before.xpr.sha256 -ceq $XprSha) 'XPR SHA 不匹配'
    $run02 = Get-Run02SourceBinding
    $run03 = Assert-Run03References
    $tbArtifact = Assert-Tb 'run05'
    $priorText = [IO.File]::ReadAllText($PriorTb, [Text.UTF8Encoding]::new($false, $true))
    $newText = [IO.File]::ReadAllText($Tb, [Text.UTF8Encoding]::new($false, $true))
    $restored = $newText.Replace('tb_s2a_conv_layer35_row22_attempt05', 'tb_s2a_conv_layer35_row22_attempt04').Replace('\\run05\\', '\\run04\\').Replace('PASS_RUN05', 'PASS_RUN04')
    Require ($restored -ceq $priorText) 'attempt05 TB 相对 attempt04 的差异超出模块/输出目录/sentinel'
    $parent = Split-Path -Parent $Run05
    Assert-NoReparse $parent
    [void][IO.Directory]::CreateDirectory($Run05)
    $projectDir = (Join-Path $Run05 'isolated_project\T58_Row22_Attempt05').Replace('\', '/')
    $xsimPath = $XsimTcl.Replace('\', '/')
    $rtlPaths = @($ExpectedRtl.Keys | ForEach-Object { (Join-Path $RepoRoot $_.Replace('/', '\')).Replace('\', '/') })
    $lines = [Collections.Generic.List[string]]::new()
    $lines.Add('set project_dir {' + $projectDir + '}')
    $lines.Add('if {[file exists $project_dir]} { error "拒绝覆盖已存在的 run05 isolated project" }')
    $lines.Add('file mkdir [file dirname $project_dir]')
    $lines.Add('create_project T58_Row22_Attempt05 $project_dir -part xc7z020clg400-1')
    $lines.Add('set_property target_language Verilog [current_project]')
    $lines.Add('set_property simulator_language Mixed [current_project]')
    $lines.Add('set_property TARGET_SIMULATOR XSim [current_project]')
    foreach ($path in $rtlPaths) { $lines.Add('add_files -norecurse -fileset sources_1 {' + $path + '}') }
    $lines.Add('add_files -norecurse -fileset sim_1 {' + $Tb.Replace('\', '/') + '}')
    $lines.Add('set_property top tb_s2a_conv_layer35_row22_attempt05 [get_filesets sim_1]')
    $lines.Add('set_property xsim.simulate.runtime {all} [get_filesets sim_1]')
    $lines.Add('set_property xsim.simulate.custom_tcl {' + $xsimPath + '} [get_filesets sim_1]')
    $lines.Add('update_compile_order -fileset sources_1')
    $lines.Add('update_compile_order -fileset sim_1')
    $lines.Add('puts {T58_RUN_PROJECT=ISOLATED_PROJECT_CREATED}')
    $lines.Add('puts {T58_RUN_PROJECT=COMPILE_ELABORATE_SIMULATE_BEGIN}')
    $lines.Add('launch_simulation -mode behavioral -step all')
    $lines.Add('puts {T58_RUN_PROJECT=COMPILE_ELABORATE_SIMULATE_RETURNED}')
    $lines.Add('close_project')
    $lines.Add('puts {T58_RUN_PROJECT=CLOSED}')
    $projectText = [string]::Join("`n", $lines.ToArray()) + "`n"
    Require ($lines.Count -eq 24 -and -not $projectText.Contains("`r") -and $projectText.Split("`n").Length -eq 25) 'run05 project Tcl 行数/行尾错误'
    Require (([regex]::Matches($projectText, '(?m)^(?:set|if|file|create_project|set_property|add_files|update_compile_order|puts|launch_simulation|close_project)\b')).Count -eq 24) 'run05 Tcl Vivado command 数不是 24'
    Require (([regex]::Matches($projectText, '(?m)^add_files\b')).Count -eq 6 -and ([regex]::Matches($projectText, '(?m)^launch_simulation\b')).Count -eq 1 -and -not $projectText.Contains(';')) 'run05 Tcl 命令数量/连接检查失败'
    $expectedOrder = @('set project_dir', 'if {[file exists', 'file mkdir', 'create_project', 'set_property target_language', 'set_property simulator_language', 'set_property TARGET_SIMULATOR') + @('add_files') * 6 + @('set_property top', 'set_property xsim.simulate.runtime', 'set_property xsim.simulate.custom_tcl', 'update_compile_order -fileset sources_1', 'update_compile_order -fileset sim_1', 'puts {T58_RUN_PROJECT=ISOLATED_PROJECT_CREATED}', 'puts {T58_RUN_PROJECT=COMPILE_ELABORATE_SIMULATE_BEGIN}', 'launch_simulation', 'puts {T58_RUN_PROJECT=COMPILE_ELABORATE_SIMULATE_RETURNED}', 'close_project', 'puts {T58_RUN_PROJECT=CLOSED}')
    for ($i = 0; $i -lt $expectedOrder.Count; $i++) { Require ($lines[$i].StartsWith($expectedOrder[$i], [StringComparison]::Ordinal)) ('run05 Tcl 命令顺序错误，行 ' + ($i + 1)) }
    $xsimLines = [Collections.Generic.List[string]]::new()
    $xsimLines.Add('# 不创建波形，只运行至 testbench 的 $finish。')
    $xsimLines.Add('run all')
    $xsimLines.Add('puts {T58_XSIM_TCL_RUN_ALL_RETURNED}')
    $xsimLines.Add('quit')
    $xsimText = [string]::Join("`n", $xsimLines.ToArray()) + "`n"
    Require (-not $xsimText.Contains("`r") -and -not [regex]::IsMatch($xsimText, '(?i)\b(?:add_wave|log_wave|wdb)\b')) 'run05 xsim Tcl 行尾或波形配置不符'
    Write-NewText $ProjectTcl $projectText
    Write-NewText $XsimTcl $xsimText
    $launcher = Get-Artifact $PSCommandPath
    $projectArtifact = Get-Artifact $ProjectTcl
    $xsimArtifact = Get-Artifact $XsimTcl
    $sources = $run02.sources
    $sources['sim/tb_s2a_conv_layer35_row22_attempt04.sv'] = Get-Artifact $PriorTb
    $sources['sim/tb_s2a_conv_layer35_row22_attempt05.sv'] = $tbArtifact
    $sources['verification/run_s2a_t58_row22_attempt05_isolated_sim.ps1'] = $launcher
    $sources['report/evidence/S2A-T58/run05/run_project_sim.tcl'] = $projectArtifact
    $sources['report/evidence/S2A-T58/run05/xsim_run.tcl'] = $xsimArtifact
    $binding = [ordered]@{ schema = 'GestureForge-S2A-T58-attempt05-binding-v1'; task_id = 'S2A-T58'; run_id = 'run05'; status = 'PREPARED_NOT_SIMULATED'; simulation = 'NOT_RUN'; base_head = $BaseHead; prepared_on_head = Get-Head; launcher = $launcher; tb = $tbArtifact; tb_top = 'tb_s2a_conv_layer35_row22_attempt05'; sources = $sources; prior_prepared_data = $run03; preserved_trees = $before; target_xpr = @{ path = $Xpr; sha256 = $XprSha; opened = $false; modified = $false }; project_tcl = $projectArtifact; xsim_tcl = $xsimArtifact; project = @{ name = 'T58_Row22_Attempt05'; part = 'xc7z020clg400-1'; directory = $projectDir; created = $false; opened = $false }; outputs = @{ raw_int32 = (Join-Path $Run05 'observed_raw.bin'); int8 = (Join-Path $Run05 'observed_output.bin'); raw_bytes_expected = 26624; int8_bytes_expected = 6656 }; sim_gates = @{ sentinel = 'T58_XSIM_SENTINEL=PASS_RUN05'; progress_events = 256; finish = '$finish'; run_all_marker = 'T58_XSIM_TCL_RUN_ALL_RETURNED' }; process_check_before = $processBefore; vivado_xsim_started = $false }
    Write-NewJson $BindingPath $binding
    $plan = [ordered]@{ schema = 'GestureForge-S2A-T58-attempt05-plan-v1'; status = 'READY_FOR_MCP_REVIEW'; simulation = 'NOT_RUN'; powershell_starts_vivado_or_xsim = $false; source_count = $sources.Count; command_count = $lines.Count; command_order = @($lines.ToArray()); project_tcl_uses_literal_lf = $true; nested_array_join_used = $false; mcp_steps_after_review = @('run_tcl source run_project_sim.tcl', 'run_tcl source xsim_run.tcl'); observed_outputs = @{ raw = 26624; int8 = 6656 } }
    Write-NewJson $PlanPath $plan
    $after = [ordered]@{ run02 = Get-Tree $Run02; run03 = Get-Tree $Run03; run04 = Get-Tree $Run04; xpr = Get-Artifact $Xpr }
    foreach ($key in @('run02', 'run03', 'run04')) { Assert-SameTree $before[$key] $after[$key] $key }
    Require ($after.xpr.sha256 -ceq $before.xpr.sha256 -and $after.xpr.sha256 -ceq $XprSha) 'XPR 准备前后变化'
    Require ((Get-Head) -ceq $BaseHead) '准备期间 HEAD 变化'
    $processAfter = @(Get-ProcessSnapshot)
    Require ($processAfter.Count -eq 0) '准备结束时检测到 Vivado/XSim 进程'
    $summary = [ordered]@{ schema = 'GestureForge-S2A-T58-attempt05-dryrun-summary-v1'; task_id = 'S2A-T58'; run_id = 'run05'; status = 'DRYRUN_READY_NOT_SIMULATED'; simulation = 'NOT_RUN'; current_head = $BaseHead; run02_oracle = @{ raw_int32 = 6656; int8 = 6656; d2_t23_matches = 6656 }; prior_run03_evidence = $run03; preserved_trees = $after; preserved_xpr = $after.xpr; process_before = $processBefore; process_after = $processAfter; vivado_or_xsim_started = $false; tcl_static_check = @{ line_count = $lines.Count; command_count = 24; add_files_count = 6; launch_simulation_count = 1; literal_lf_only = $true; order_check = 'PASS' }; limitation = '仅完成局部仿真准备；尚未通过 MCP 执行 compile/elaborate/simulate；不代表完整 layer/network 或 G3/G4/G5。' }
    Write-NewJson $SummaryPath $summary
    $records = @($InventoryNames | Sort-Object | ForEach-Object { [ordered]@{ relative_path = $_; artifact = Get-Artifact (Join-Path $Run05 $_) } })
    Write-NewJson $InventoryPath ([ordered]@{ schema = 'GestureForge-S2A-T58-run05-inventory-v1'; run_id = 'run05'; simulation = 'NOT_RUN'; evidence_files = $records; self_record = '本清单不递归记录自身 SHA-256' })
    $audit = Assert-Run05Inventory
    Write-Output (ConvertTo-Json -InputObject ([ordered]@{ status = 'PASS_RUN05_DRYRUN_READY'; audit = $audit; simulation = 'NOT_RUN'; run04_unchanged = $true; xpr_unchanged = $true }) -Depth 12 -Compress)
}
try {
    if ($Mode -eq 'Prepare') { Invoke-Prepare }
    else { Write-Output (ConvertTo-Json -InputObject (Assert-Run05Inventory) -Depth 12 -Compress) }
}
catch {
    [Console]::Error.WriteLine(('S2A-T58 run05 ' + $Mode + ' failed: ' + $_.Exception.Message))
    exit 1
}
