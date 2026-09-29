[CmdletBinding()]
param(
    [ValidateSet('Prepare', 'RepairPrepared', 'AuditInventory')]
    [string]$Mode = 'Prepare'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = 'D:\FPGA_Competition'
$Run02 = Join-Path $RepoRoot 'report\evidence\S2A-T58\run02'
$Run03 = Join-Path $RepoRoot 'report\evidence\S2A-T58\run03'
$Run04 = Join-Path $RepoRoot 'report\evidence\S2A-T58\run04'
$Tb = Join-Path $RepoRoot 'sim\tb_s2a_conv_layer35_row22_attempt04.sv'
$Xpr = Join-Path $RepoRoot 'vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr'
$T56Report = Join-Path $RepoRoot 'report\evidence\S2A-T56\layer35_row20_all_channels.json'
$T56Summary = Join-Path $RepoRoot 'report\evidence\S2A-T56\mcp_project_run01\simulation_summary.json'
$Verifier = Join-Path $RepoRoot 'verification\test_s2a_conv_layer35_row22_all_channels_rtl.py'
$BaseHead = 'a8d19fbdc3389682b888f2d8add2cdd77af4503c'
$Run02SummarySha = 'f5b170ba5ec2c25fd8c7c917035ab6bb1fe46847198bd74ea0ffb27cbbdcbba6'
$Run02BindingSha = '24fd56415f60f5fe441d039d9f5458be21a4f95759244aa32e13828e9676cb4d'
$T56ReportSha = '44a25b6b5af6f8868dd2cb9780c4834bdd87860ba43a71b0c696c0b67627da12'
$T56SummarySha = 'eceb674cdc63c25bcc990885e27a81690efbd1312a095a07fd1d8c3235ac9e0b'
$XprSha = '9e637bb8a31c8c74cdb703d632282a020875f5623893665719c1bbb5035be1ec'
$Run03PreparedSha = '006ab22ab4595e30d866a5403803748afe720587beb6442bf151f17de610f51e'
$Run03DryrunSha = '013af49da8460fb84d35987172f7a22ab074c71423bdd3314ae305cea8bfcdbc'
$Run03BindingSha = '174008f3c08f6424382be4a805997b40f1d466d16962ddeb6a41e1524c954279'
$Run03CliGuardSha = 'c36a3a6bc9484b2572ec1e95afd8c088457f6400821338696b7a0edfd266a25e'
$Run03CliStderrSha = '317f5b0b86f0e91b27f55c1ddeb287d3ef30b35d116a7ac5d9276d60f19e32b4'
$Attempt01ArchiveSha = '2759a7125ea9bf9f3f3ed14db509123bb3927303057c8047fa9be18d0b84d090'
$Run03ContentVerifyPath = Join-Path $Run03 'run02_prepared_content_verify_attempt02.stdout.json'
$Run03DryrunPath = Join-Path $Run03 'dryrun_summary.json'
$Run03BindingPath = Join-Path $Run03 'isolated_sim_binding.json'
$Run03CliGuardPath = Join-Path $Run03 'run02_cli_verify_sibling_guard.json'
$Run03CliStderrPath = Join-Path $Run03 'run02_verify.stderr.bin'
$ProjectTcl = Join-Path $Run04 'run_project_sim.tcl'
$XsimTcl = Join-Path $Run04 'xsim_run.tcl'
$BindingPath = Join-Path $Run04 'isolated_sim_binding.json'
$SummaryPath = Join-Path $Run04 'dryrun_summary.json'
$InventoryPath = Join-Path $Run04 'isolated_run_inventory.json'
$ProcessNames = '^(vivado|vivado_lab|xsim|xsimk|xelab|xvlog|xvhdl|hw_server)(\.exe)?$'
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
$ExpectedInventoryNames = @('dryrun_plan.json', 'dryrun_summary.json', 'isolated_sim_binding.json', 'prepare_attempt01_failure_archive.json', 'repair_record.json', 'run_project_sim.tcl', 'xsim_run.tcl')

function Require([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-Artifact([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force
    return [ordered]@{ path = [IO.Path]::GetFullPath($Path); bytes = [int64]$item.Length; sha256 = Get-Sha256 $Path }
}

function Assert-NoReparseChain([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    $boundary = [IO.Path]::GetFullPath($RepoRoot).TrimEnd([char]92)
    Require ($full.Equals($boundary, [StringComparison]::OrdinalIgnoreCase) -or
        $full.StartsWith($boundary + '\', [StringComparison]::OrdinalIgnoreCase)) ('路径超出仓库：' + $full)
    $cursor = $full
    while ($true) {
        $item = Get-Item -LiteralPath $cursor -Force
        Require (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) ('拒绝 reparse 路径：' + $cursor)
        if ($cursor.Equals($boundary, [StringComparison]::OrdinalIgnoreCase)) { break }
        $parent = [IO.Directory]::GetParent($cursor)
        Require ($null -ne $parent) ('路径缺少仓库内父目录：' + $full)
        $cursor = $parent.FullName
    }
}

function Get-ProcessSnapshot {
    return @(Get-CimInstance Win32_Process | Where-Object { $_.Name -match $ProcessNames } |
        Sort-Object ProcessId | ForEach-Object { [ordered]@{ name = $_.Name; pid = [int]$_.ProcessId } })
}

function Get-CurrentHead {
    $head = & git -C $RepoRoot rev-parse HEAD
    Require ($LASTEXITCODE -eq 0) '读取 Git HEAD 失败'
    return [string]$head
}

function Assert-BaseAncestor([string]$Head) {
    & git -C $RepoRoot merge-base --is-ancestor $BaseHead $Head *> $null
    Require ($LASTEXITCODE -eq 0) ('当前 HEAD 不包含冻结基线：' + $BaseHead)
}

function Assert-Hash([string]$Path, [string]$Expected, [string]$Label) {
    Assert-NoReparseChain $Path
    $actual = Get-Sha256 $Path
    $normalizedExpected = ([string]$Expected).ToLowerInvariant()
    Require ($actual -ceq $normalizedExpected) ($Label + ' SHA256 不符：expected=' + $normalizedExpected + ' actual=' + $actual)
    return Get-Artifact $Path
}

function Write-NewJson([string]$Path, [object]$Value) {
    Require (-not (Test-Path -LiteralPath $Path)) ('拒绝覆盖已有证据：' + $Path)
    $json = ConvertTo-Json -InputObject $Value -Depth 32
    [IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
}

function Write-ReplaceJson([string]$Path, [object]$Value) {
    Assert-NoReparseChain $Path
    $json = ConvertTo-Json -InputObject $Value -Depth 32
    [IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
}

function Get-SourceBinding {
    $sources = [ordered]@{}
    foreach ($relative in $ExpectedRtl.Keys) {
        $path = Join-Path $RepoRoot $relative.Replace('/', '\')
        $sources[$relative] = Assert-Hash $path $ExpectedRtl[$relative] ('RTL ' + $relative)
    }
    $fixtureRoot = Join-Path $Run02 'fixture'
    foreach ($name in $ExpectedFixture.Keys) {
        $path = Join-Path $fixtureRoot $name
        $artifact = Assert-Hash $path $ExpectedFixture[$name].sha256 ('run02 fixture ' + $name)
        Require ($artifact.bytes -eq $ExpectedFixture[$name].bytes) ('run02 fixture 长度不符：' + $name)
        $sources['report/evidence/S2A-T58/run02/fixture/' + $name] = $artifact
    }
    $sources['report/evidence/S2A-T58/run02/prepare_summary.json'] = Assert-Hash (Join-Path $Run02 'prepare_summary.json') $Run02SummarySha 'run02 prepare_summary'
    $sources['report/evidence/S2A-T58/run02/project_preflight_binding.json'] = Assert-Hash (Join-Path $Run02 'project_preflight_binding.json') $Run02BindingSha 'run02 project binding'
    $sources['report/evidence/S2A-T56/layer35_row20_all_channels.json'] = Assert-Hash $T56Report $T56ReportSha 'T56 report'
    $sources['report/evidence/S2A-T56/mcp_project_run01/simulation_summary.json'] = Assert-Hash $T56Summary $T56SummarySha 'T56 summary'
    $sources['vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr'] = Assert-Hash $Xpr $XprSha 'target XPR'
    $sources['verification/test_s2a_conv_layer35_row22_all_channels_rtl.py'] = Get-Artifact $Verifier

    Assert-NoReparseChain $Tb
    $tbText = [IO.File]::ReadAllText($Tb, [Text.Encoding]::UTF8)
    $run02OutputPath = 'D:\\FPGA_Competition\\report\\evidence\\S2A-T58\\run02\\fixture\\'
    $run04OutputPath = 'D:\\FPGA_Competition\\report\\evidence\\S2A-T58\\run04\\'
    Require (([regex]::Matches($tbText, [regex]::Escape($run02OutputPath))).Count -eq 4) 'attempt04 TB 必须且只能从 run02 读取四个 fixture 文件'
    Require (([regex]::Matches($tbText, [regex]::Escape($run04OutputPath))).Count -eq 2) 'attempt04 TB 必须且只能向 run04 写两个输出文件'
    Require (([regex]::Matches($tbText, 'T58_XSIM_SENTINEL=PASS_RUN04')).Count -eq 1) 'attempt04 TB sentinel 缺失或重复'
    Require (-not $tbText.Contains('\\run03\\observed_')) 'attempt04 TB 不得向 run03 写输出'
    $module = [regex]::Match($tbText, '(?m)^\s*module\s+([A-Za-z_][A-Za-z0-9_$]*)')
    Require ($module.Success) 'attempt04 TB 未找到顶层 module'
    $sources['sim/tb_s2a_conv_layer35_row22_attempt04.sv'] = Get-Artifact $Tb
    return [ordered]@{ sources = $sources; tb_top = $module.Groups[1].Value }
}

function Assert-PreservedRun03References {
    $preparedArtifact = Assert-Hash $Run03ContentVerifyPath $Run03PreparedSha 'run03 prepared-content verifier record'
    $prepared = Get-Content -LiteralPath $Run03ContentVerifyPath -Encoding utf8 -Raw | ConvertFrom-Json
    Require ($prepared.result -ceq 'PREPARED_NOT_SIMULATED' -and $prepared.simulation -ceq 'NOT_RUN') 'run03 prepared-content 状态不符'
    Require ($prepared.output_counts.raw_int32 -eq 6656 -and $prepared.output_counts.int8 -eq 6656 -and $prepared.output_counts.d2_t23_matches -eq 6656) 'run03 prepared-content 项数不符'
    $dryrunArtifact = Assert-Hash $Run03DryrunPath $Run03DryrunSha 'run03 dryrun summary'
    $dryrun = Get-Content -LiteralPath $Run03DryrunPath -Encoding utf8 -Raw | ConvertFrom-Json
    Require ($dryrun.status -ceq 'DRYRUN_READY_NOT_SIMULATED' -and $dryrun.simulation -ceq 'NOT_RUN') 'run03 dryrun 状态不符'
    [void](Assert-Hash $Run03BindingPath $Run03BindingSha 'run03 isolated binding')
    [void](Assert-Hash $Run03CliGuardPath $Run03CliGuardSha 'run03 official CLI guard record')
    $cliGuard = Get-Content -LiteralPath $Run03CliGuardPath -Encoding utf8 -Raw | ConvertFrom-Json
    Require ($cliGuard.status -ceq 'BLOCKED_BY_RUN03_SIBLING_ROOT_INVENTORY' -and $cliGuard.exit_code -eq 1) 'run03 official CLI guard 观察状态不符'
    $stderrArtifact = Assert-Hash $Run03CliStderrPath $Run03CliStderrSha 'run03 official CLI stderr'
    Require ($stderrArtifact.bytes -eq 315 -and $cliGuard.stderr.sha256 -ceq $stderrArtifact.sha256) 'run03 official CLI stderr 引用不符'
    return [ordered]@{
        prepared_content_record = $preparedArtifact
        prepared_content_status = $prepared.result
        prepared_content_simulation = $prepared.simulation
        output_counts = $prepared.output_counts
        run03_dryrun_record = $dryrunArtifact
        run03_binding = Get-Artifact $Run03BindingPath
        official_cli_guard = Get-Artifact $Run03CliGuardPath
        official_cli_failure_stderr = $stderrArtifact
        explanation = '沿用已审查的 run02 完整 _verify_prepared 结果；官方 --verify-only 失败仅因 run03 sibling root inventory 门禁。'
    }
}

function Get-RootEntryNames {
    return @((Get-ChildItem -LiteralPath (Join-Path $RepoRoot 'report\evidence\S2A-T58') -Force |
        ForEach-Object { $_.Name } | Sort-Object))
}

function Assert-Run04Inventory {
    Assert-NoReparseChain $Run04
    $actualEntries = @(Get-ChildItem -LiteralPath $Run04 -Force | ForEach-Object { $_.Name } | Sort-Object)
    $expectedEntries = @($ExpectedInventoryNames + 'isolated_run_inventory.json' | Sort-Object)
    Require (($actualEntries -join '|') -ceq ($expectedEntries -join '|')) 'run04 evidence 目录含额外或缺失项目'
    $inventory = Get-Content -LiteralPath $InventoryPath -Encoding utf8 -Raw | ConvertFrom-Json
    Require ($inventory.schema -ceq 'GestureForge-S2A-T58-run04-inventory-v1' -and
        $inventory.run_id -ceq 'run04' -and $inventory.simulation -ceq 'NOT_RUN') 'run04 inventory 身份/状态不符'
    $expected = @($ExpectedInventoryNames | Sort-Object)
    $records = @($inventory.evidence_files)
    $actual = @($records | ForEach-Object { [string]$_.relative_path } | Sort-Object)
    Require (($actual -join '|') -ceq ($expected -join '|')) 'run04 inventory 文件列表不符'
    foreach ($record in $records) {
        $relative = [string]$record.relative_path
        $path = Join-Path $Run04 $relative
        Assert-NoReparseChain $path
        $artifact = Get-Artifact $path
        Require ([string]$record.artifact.path -ceq $artifact.path -and [int64]$record.artifact.bytes -eq $artifact.bytes -and
            [string]$record.artifact.sha256 -ceq $artifact.sha256) ('run04 artifact 哈希或长度变化：' + $relative)
    }
    $binding = Get-Content -LiteralPath $BindingPath -Encoding utf8 -Raw | ConvertFrom-Json
    Require ($binding.launcher.sha256 -ceq (Get-Sha256 $PSCommandPath)) 'run04 launcher 与 binding 哈希不符'
    $sourceBinding = Get-SourceBinding
    [void](Assert-PreservedRun03References)
    Require ($binding.tb_top -ceq $sourceBinding.tb_top) 'run04 TB 顶层发生变化'
    foreach ($key in $sourceBinding.sources.Keys) {
        $boundProperty = $binding.sources.PSObject.Properties[$key]
        Require ($null -ne $boundProperty) ('run04 source binding 缺少路径：' + $key)
        Require ($boundProperty.Value.sha256 -ceq $sourceBinding.sources[$key].sha256) ('run04 source 绑定变化：' + $key)
    }
    Require ((Get-Sha256 $ProjectTcl) -ceq $binding.project_tcl.sha256) 'run04 project Tcl 哈希不符'
    Require ((Get-Sha256 $XsimTcl) -ceq $binding.xsim_tcl.sha256) 'run04 xsim Tcl 哈希不符'
    $archivePath = Join-Path $Run04 'prepare_attempt01_failure_archive.json'
    $archiveArtifact = Assert-Hash $archivePath $Attempt01ArchiveSha 'attempt01 失败准备快照'
    $repair = Get-Content -LiteralPath (Join-Path $Run04 'repair_record.json') -Encoding utf8 -Raw | ConvertFrom-Json
    Require ($repair.status -ceq 'PREPARATION_REBOUND_WITH_ARCHIVED_ATTEMPT01' -and
        $repair.archive.sha256 -ceq $archiveArtifact.sha256 -and
        $repair.launcher.sha256 -ceq (Get-Sha256 $PSCommandPath)) 'run04 repair record 身份或来源哈希不符'
    $rootNames = Get-RootEntryNames
    $expectedRoot = @('project_preflight_binding.json', 'run01', 'run02', 'run03', 'run04') | Sort-Object
    Require (($rootNames -join '|') -ceq ($expectedRoot -join '|')) 'T58 evidence root 出现非预期 sibling'
    return [ordered]@{ status = 'PASS_READ_ONLY_RUN04_INVENTORY'; inventory_sha256 = Get-Sha256 $InventoryPath; file_count = $records.Count; run02_xpr_sha256 = $binding.target_xpr.sha256; sources_rechecked = $sourceBinding.sources.Count }
}

function Invoke-RepairPrepared {
    Require (([IO.Path]::GetFullPath((Get-Location).Path)).Equals($RepoRoot, [StringComparison]::OrdinalIgnoreCase)) '必须从仓库根目录运行'
    Assert-NoReparseChain $Run04
    $legacyNames = @('dryrun_plan.json', 'dryrun_summary.json', 'isolated_sim_binding.json', 'isolated_run_inventory.json', 'prepare_attempt01_failure_archive.json', 'run_project_sim.tcl', 'xsim_run.tcl') | Sort-Object
    $actualNames = @(Get-ChildItem -LiteralPath $Run04 -Force | ForEach-Object { $_.Name } | Sort-Object)
    Require (($actualNames -join '|') -ceq ($legacyNames -join '|')) 'run04 初始准备快照目录含非预期项目'
    $archivePath = Join-Path $Run04 'prepare_attempt01_failure_archive.json'
    [void](Assert-Hash $archivePath $Attempt01ArchiveSha 'attempt01 失败准备快照')
    $archive = Get-Content -LiteralPath $archivePath -Encoding utf8 -Raw | ConvertFrom-Json
    Require ($archive.status -ceq 'NON_ACCEPTANCE_PREPARE_EXIT1_POSTCHECK_EMPTY_ARRAY_COUNT' -and
        $archive.simulation -ceq 'NOT_RUN' -and $archive.exit_code -eq 1) 'attempt01 failure archive 状态不符'
    Require (@($archive.captured_files).Count -eq 6) 'attempt01 failure archive 捕获项目数不符'
    foreach ($item in @($archive.captured_files)) {
        $path = Join-Path $Run04 ([string]$item.relative_path)
        Assert-NoReparseChain $path
        $archivedBytes = [Convert]::FromBase64String([string]$item.base64)
        Require ($archivedBytes.Length -eq [int64]$item.bytes) ('attempt01 快照长度不符：' + $item.relative_path)
        $archivedSha = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($archivedBytes)).ToLowerInvariant()
        Require ($archivedSha -ceq [string]$item.sha256 -and
            [Convert]::ToBase64String([IO.File]::ReadAllBytes($path)) -ceq [string]$item.base64) ('attempt01 快照与现存文件不一致：' + $item.relative_path)
    }
    Require (-not (Test-Path -LiteralPath (Join-Path $Run04 'isolated_project'))) 'run04 已有隔离 Vivado 工程，拒绝准备重绑'
    Require (-not (Test-Path -LiteralPath (Join-Path $Run04 'observed_raw.bin')) -and
        -not (Test-Path -LiteralPath (Join-Path $Run04 'observed_output.bin'))) 'run04 已有仿真输出，拒绝准备重绑'
    $oldBinding = Get-Content -LiteralPath $BindingPath -Encoding utf8 -Raw | ConvertFrom-Json
    Require ($oldBinding.launcher.sha256 -ceq $archive.launcher_sha256_at_attempt) 'attempt01 launcher 绑定与归档不符'
    Require ((Get-Sha256 $ProjectTcl) -ceq $oldBinding.project_tcl.sha256 -and
        (Get-Sha256 $XsimTcl) -ceq $oldBinding.xsim_tcl.sha256) 'attempt01 Tcl 与绑定哈希不符'
    $head = Get-CurrentHead
    Assert-BaseAncestor $head
    $processes = @(Get-ProcessSnapshot)
    Require ($processes.Count -eq 0) 'RepairPrepared 前检测到 Vivado/XSim 进程'
    $sourceBinding = Get-SourceBinding
    $priorReferences = Assert-PreservedRun03References
    Require ((Get-Sha256 $Xpr) -ceq $XprSha) 'RepairPrepared 前目标 XPR 哈希变化'
    $launcher = Get-Artifact $PSCommandPath
    $archiveArtifact = Get-Artifact $archivePath
    $repairRecord = [ordered]@{
        schema = 'GestureForge-S2A-T58-attempt04-repair-record-v1'
        status = 'PREPARATION_REBOUND_WITH_ARCHIVED_ATTEMPT01'
        prior_attempt_status = $archive.status
        prior_attempt_exit_code = $archive.exit_code
        prior_attempt_error = $archive.error
        prior_launcher_sha256 = $archive.launcher_sha256_at_attempt
        launcher = $launcher
        archive = $archiveArtifact
        simulation = 'NOT_RUN'
        vivado_or_xsim_invoked = $false
        source_recheck_count = $sourceBinding.sources.Count
        xpr_sha256_unchanged = (Get-Sha256 $Xpr)
        process_count_before = $processes.Count
    }
    $repairPath = Join-Path $Run04 'repair_record.json'
    Write-NewJson $repairPath $repairRecord
    $projectTclArtifact = Get-Artifact $ProjectTcl
    $xsimTclArtifact = Get-Artifact $XsimTcl
    $bindingDoc = [ordered]@{
        schema = 'GestureForge-S2A-T58-attempt04-binding-v1'
        task_id = 'S2A-T58'
        run_id = 'run04'
        status = 'PREPARED_NOT_SIMULATED'
        simulation = 'NOT_RUN'
        base_head = $BaseHead
        prepared_on_head = $head
        launcher = $launcher
        tb_top = $sourceBinding.tb_top
        sources = $sourceBinding.sources
        prior_prepared_data_evidence = $priorReferences
        project_tcl = $projectTclArtifact
        xsim_tcl = $xsimTclArtifact
        repair_record = Get-Artifact $repairPath
        target_xpr = @{ path = $Xpr; sha256 = $XprSha; opened = $false; modified = $false }
        project = @{ name = 'T58_Row22_Attempt04'; part = 'xc7z020clg400-1'; directory = (Join-Path $Run04 'isolated_project\T58_Row22_Attempt04').Replace('\', '/'); created = $false; opened = $false }
        outputs = @{ raw_int32 = (Join-Path $Run04 'observed_raw.bin'); int8 = (Join-Path $Run04 'observed_output.bin'); raw_bytes_expected = 26624; int8_bytes_expected = 6656 }
        sim_gates = @{ pass_sentinel = 'T58_XSIM_SENTINEL=PASS_RUN04'; progress_events = 256; finish = '$finish'; run_all_marker = 'T58_XSIM_TCL_RUN_ALL_RETURNED' }
        prior_failure_archive = $archiveArtifact
        process_check_before = $processes
    }
    $plan = [ordered]@{
        schema = 'GestureForge-S2A-T58-attempt04-plan-v1'
        status = 'PREPARED_AWAITING_MCP_CONNECTION_CHECK'
        simulation = 'NOT_RUN'
        mcp_actions_when_connection_is_available = @('check_connection', 'get_project_info', 'run_tcl source run_project_sim.tcl', 'run_tcl source xsim_run.tcl')
        powershell_launches_vivado = $false
        isolated_project = $bindingDoc.project.directory
        target_project_xpr_opened = $false
        source_count = $sourceBinding.sources.Count
    }
    $summary = [ordered]@{
        schema = 'GestureForge-S2A-T58-attempt04-dryrun-summary-v1'
        task_id = 'S2A-T58'
        run_id = 'run04'
        status = 'DRYRUN_READY_NOT_SIMULATED'
        simulation = 'NOT_RUN'
        current_head = $head
        source_count = $sourceBinding.sources.Count
        tb_top = $sourceBinding.tb_top
        run02_oracle_counts = $priorReferences.output_counts
        xpr_unchanged_sha256 = Get-Sha256 $Xpr
        process_count_before = $processes.Count
        process_count_after = 0
        vivado_or_xsim_invoked = $false
        repair_record = Get-Artifact $repairPath
        prior_prepare_attempt = @{ status = $archive.status; exit_code = $archive.exit_code; archive_sha256 = $archiveArtifact.sha256 }
    }
    Write-ReplaceJson $BindingPath $bindingDoc
    Write-ReplaceJson (Join-Path $Run04 'dryrun_plan.json') $plan
    Write-ReplaceJson $SummaryPath $summary
    $records = @($ExpectedInventoryNames | Sort-Object | ForEach-Object { [ordered]@{ relative_path = $_; artifact = Get-Artifact (Join-Path $Run04 $_) } })
    Write-ReplaceJson $InventoryPath ([ordered]@{ schema = 'GestureForge-S2A-T58-run04-inventory-v1'; run_id = 'run04'; simulation = 'NOT_RUN'; evidence_files = $records; self_record = '本清单不递归记录自身 SHA' })
    $audit = Assert-Run04Inventory
    $finalProcesses = @(Get-ProcessSnapshot)
    Require ($finalProcesses.Count -eq 0) 'RepairPrepared 结束时检测到 Vivado/XSim 进程'
    Require ((Get-Sha256 $Xpr) -ceq $XprSha) 'RepairPrepared 结束时目标 XPR 哈希变化'
    Write-Output (ConvertTo-Json -InputObject ([ordered]@{ status = 'PASS_RUN04_REPAIR_AND_DRYRUN'; audit = $audit; simulation = 'NOT_RUN'; prior_failure_preserved = $true }) -Depth 12 -Compress)
}

function Invoke-Prepare {
    Require (([IO.Path]::GetFullPath((Get-Location).Path)).Equals($RepoRoot, [StringComparison]::OrdinalIgnoreCase)) '必须从仓库根目录运行'
    Assert-NoReparseChain $RepoRoot
    Require (-not (Test-Path -LiteralPath $Run04)) 'run04 已存在；拒绝覆盖'
    $initialRootNames = @('project_preflight_binding.json', 'run01', 'run02', 'run03') | Sort-Object
    Require (((Get-RootEntryNames) -join '|') -ceq ($initialRootNames -join '|')) 'T58 evidence root 初始清单不符'
    $processes = @(Get-ProcessSnapshot)
    Require ($processes.Count -eq 0) ('准备前存在 Vivado/XSim 进程，拒绝继续：' + (ConvertTo-Json $processes -Compress))
    $head = Get-CurrentHead
    Assert-BaseAncestor $head
    $sourceBinding = Get-SourceBinding
    $run03References = Assert-PreservedRun03References

    $parent = Split-Path -Parent $Run04
    Assert-NoReparseChain $parent
    [void][IO.Directory]::CreateDirectory($Run04)
    $rtlPaths = @($ExpectedRtl.Keys | ForEach-Object { (Join-Path $RepoRoot $_.Replace('/', '\')).Replace('\', '/') })
    $tbPath = $Tb.Replace('\', '/')
    $projectDir = (Join-Path $Run04 'isolated_project\T58_Row22_Attempt04').Replace('\', '/')
    $projectTclLines = @(
        'set project_dir {' + $projectDir + '}',
        'if {[file exists $project_dir]} { error "拒绝覆盖已存在的 run04 isolated project" }',
        'file mkdir [file dirname $project_dir]',
        'create_project T58_Row22_Attempt04 $project_dir -part xc7z020clg400-1',
        'set_property target_language Verilog [current_project]'
    )
    foreach ($rtlPath in $rtlPaths) { $projectTclLines += 'add_files -fileset sources_1 -norecurse {' + $rtlPath + '}' }
    $projectTclLines += @(
        'add_files -fileset sim_1 -norecurse {' + $tbPath + '}',
        'set_property top ' + $sourceBinding.tb_top + ' [get_filesets sim_1]',
        'update_compile_order -fileset sim_1',
        'launch_simulation -mode behavioral -simset sim_1'
    )
    [IO.File]::WriteAllText($ProjectTcl, ($projectTclLines -join [Environment]::NewLine) + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
    $xsimTclLines = @('run all', 'puts "T58_XSIM_TCL_RUN_ALL_RETURNED"')
    [IO.File]::WriteAllText($XsimTcl, ($xsimTclLines -join [Environment]::NewLine) + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))

    $launcher = Get-Artifact $PSCommandPath
    $bindingDoc = [ordered]@{
        schema = 'GestureForge-S2A-T58-attempt04-binding-v1'
        task_id = 'S2A-T58'
        run_id = 'run04'
        status = 'PREPARED_NOT_SIMULATED'
        simulation = 'NOT_RUN'
        base_head = $BaseHead
        prepared_on_head = $head
        launcher = $launcher
        tb_top = $sourceBinding.tb_top
        sources = $sourceBinding.sources
        prior_prepared_data_evidence = $run03References
        project_tcl = Get-Artifact $ProjectTcl
        xsim_tcl = Get-Artifact $XsimTcl
        target_xpr = @{ path = $Xpr; sha256 = $XprSha; opened = $false; modified = $false }
        project = @{ name = 'T58_Row22_Attempt04'; part = 'xc7z020clg400-1'; directory = $projectDir; created = $false; opened = $false }
        outputs = @{ raw_int32 = (Join-Path $Run04 'observed_raw.bin'); int8 = (Join-Path $Run04 'observed_output.bin'); raw_bytes_expected = 26624; int8_bytes_expected = 6656 }
        sim_gates = @{ pass_sentinel = 'T58_XSIM_SENTINEL=PASS_RUN04'; progress_events = 256; finish = '$finish'; run_all_marker = 'T58_XSIM_TCL_RUN_ALL_RETURNED' }
        process_check_before = $processes
        note = 'DryRun/AuditInventory 不启动 Vivado/XSim。实际 create_project、compile/elaborate 和 run all 仅允许通过已确认实例的 Vivado MCP run_tcl 执行。'
    }
    Write-NewJson $BindingPath $bindingDoc
    $planDoc = [ordered]@{
        schema = 'GestureForge-S2A-T58-attempt04-plan-v1'
        status = 'READY_FOR_MCP_SIMULATION'
        simulation = 'NOT_RUN'
        mcp_actions_when_connection_is_available = @('check_connection', 'get_project_info', 'run_tcl source run_project_sim.tcl', 'run_tcl source xsim_run.tcl')
        powershell_launches_vivado = $false
        isolated_project = $projectDir
        target_project_xpr_opened = $false
        sources_sha256 = $sourceBinding.sources
        prior_prepared_data = $run03References
    }
    Write-NewJson (Join-Path $Run04 'dryrun_plan.json') $planDoc
    $summary = [ordered]@{
        schema = 'GestureForge-S2A-T58-attempt04-dryrun-summary-v1'
        task_id = 'S2A-T58'
        run_id = 'run04'
        status = 'DRYRUN_READY_NOT_SIMULATED'
        simulation = 'NOT_RUN'
        current_head = $head
        source_count = $sourceBinding.sources.Count
        tb_top = $sourceBinding.tb_top
        run02_oracle_counts = $run03References.output_counts
        xpr_unchanged_sha256 = Get-Sha256 $Xpr
        process_count_before = $processes.Count
        vivado_or_xsim_invoked = $false
    }
    Write-NewJson $SummaryPath $summary
    $records = @($ExpectedInventoryNames | Sort-Object | ForEach-Object { [ordered]@{ relative_path = $_; artifact = Get-Artifact (Join-Path $Run04 $_) } })
    Write-NewJson $InventoryPath ([ordered]@{ schema = 'GestureForge-S2A-T58-run04-inventory-v1'; run_id = 'run04'; simulation = 'NOT_RUN'; evidence_files = $records; self_record = '本清单不递归记录自身 SHA' })
    $audit = Assert-Run04Inventory
    Require ((Get-Sha256 $Xpr) -ceq $XprSha) '准备结束时目标 XPR 哈希变化'
    $processesAfter = @(Get-ProcessSnapshot)
    Require ($processesAfter.Count -eq 0) '准备结束时检测到 Vivado/XSim 进程'
    Write-Output (ConvertTo-Json -InputObject ([ordered]@{ status = 'PASS_RUN04_DRYRUN'; audit = $audit; simulation = 'NOT_RUN'; xpr_unchanged = $true }) -Depth 12 -Compress)
}

try {
    if ($Mode -eq 'Prepare') { Invoke-Prepare }
    elseif ($Mode -eq 'RepairPrepared') { Invoke-RepairPrepared }
    else { Write-Output (ConvertTo-Json -InputObject (Assert-Run04Inventory) -Depth 12 -Compress) }
}
catch {
    [Console]::Error.WriteLine(('S2A-T58 run04 ' + $Mode + ' failed: ' + $_.Exception.Message))
    exit 1
}
