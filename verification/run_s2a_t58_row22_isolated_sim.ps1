[CmdletBinding()]
param(
    [ValidateSet('DryRun', 'Run', 'AuditInventory')]
    [string]$Mode = 'DryRun',
    [string]$VivadoExecutable = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = 'D:\FPGA_Competition'
$Run02 = 'D:\FPGA_Competition\report\evidence\S2A-T58\run02'
$Run03 = 'D:\FPGA_Competition\report\evidence\S2A-T58\run03'
$Run02Summary = Join-Path $Run02 'prepare_summary.json'
$Run02Binding = Join-Path $Run02 'project_preflight_binding.json'
$T56Report = 'D:\FPGA_Competition\report\evidence\S2A-T56\layer35_row20_all_channels.json'
$T56Summary = 'D:\FPGA_Competition\report\evidence\S2A-T56\mcp_project_run01\simulation_summary.json'
$Xpr = 'D:\FPGA_Competition\vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr'
$Verifier = 'D:\FPGA_Competition\verification\test_s2a_conv_layer35_row22_all_channels_rtl.py'
$AttemptTb = 'D:\FPGA_Competition\sim\tb_s2a_conv_layer35_row22_attempt03.sv'
$ProjectTcl = Join-Path $Run03 'run_project_sim.tcl'
$XsimTcl = Join-Path $Run03 'xsim_run.tcl'
$AllowedProcesses = @('vivado', 'vivado_lab', 'xsct', 'xsim', 'xsimk', 'xelab', 'xvlog', 'xvhdl')
$BaseHead = '7b8bad78a456310d2ca797a02e3a5a7f873f9c18'
$Run02SummarySha = 'f5b170ba5ec2c25fd8c7c917035ab6bb1fe46847198bd74ea0ffb27cbbdcbba6'
$Run02BindingSha = '24fd56415f60f5fe441d039d9f5458be21a4f95759244aa32e13828e9676cb4d'
$T56ReportSha = '44a25b6b5af6f8868dd2cb9780c4834bdd87860ba43a71b0c696c0b67627da12'
$T56SummarySha = 'eceb674cdc63c25bcc990885e27a81690efbd1312a095a07fd1d8c3235ac9e0b'
$XprSha = '9e637bb8a31c8c74cdb703d632282a020875f5623893665719c1bbb5035be1ec'
$Run03InventorySha = 'ae4dcbd723a3b01d6da173a9e69260224795f8db61438c06c8c574e670dc2e77'
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

function Require([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-Artifact([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force
    return [ordered]@{
        path = [IO.Path]::GetFullPath($Path)
        bytes = [int64]$item.Length
        sha256 = Get-Sha256 $Path
    }
}

function Assert-NoReparseChain([string]$Path, [string]$Boundary = $RepoRoot) {
    $full = [IO.Path]::GetFullPath($Path)
    $boundaryFull = [IO.Path]::GetFullPath($Boundary).TrimEnd([char]92)
    Require (Test-Path -LiteralPath $full) ("绑定路径不存在：" + $full)
    $cursor = $full
    while ($true) {
        $item = Get-Item -LiteralPath $cursor -Force
        Require (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) ("拒绝 reparse 路径：" + $cursor)
        if ($cursor.Equals($boundaryFull, [StringComparison]::OrdinalIgnoreCase)) { break }
        $parent = [IO.Directory]::GetParent($cursor)
        Require ($null -ne $parent) ("路径不在仓库内：" + $full)
        $cursor = $parent.FullName
        Require ($cursor.StartsWith($boundaryFull.TrimEnd([char]92) + '\', [StringComparison]::OrdinalIgnoreCase) -or
                 $cursor.Equals($boundaryFull, [StringComparison]::OrdinalIgnoreCase)) ("路径逃逸边界：" + $full)
    }
}

function Assert-ContainedPath([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    Require ($full.StartsWith($RepoRoot + '\', [StringComparison]::OrdinalIgnoreCase)) ("路径不在仓库内：" + $full)
}

function Write-NewBytes([string]$Path, [byte[]]$Bytes) {
    Require (-not (Test-Path -LiteralPath $Path)) ("拒绝覆盖已有证据：" + $Path)
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($Bytes, 0, $Bytes.Length) } finally { $stream.Dispose() }
}

function Write-NewText([string]$Path, [string]$Text) {
    $encoding = [Text.UTF8Encoding]::new($false)
    Write-NewBytes $Path $encoding.GetBytes($Text + "`n")
}

function Write-NewJson([string]$Path, $Value) {
    $json = ConvertTo-Json -InputObject $Value -Depth 64
    Write-NewText $Path $json
}

function Get-CurrentHead {
    $headText = & git.exe -C $RepoRoot rev-parse --verify HEAD
    Require ($LASTEXITCODE -eq 0) '读取 Git HEAD 失败'
    return ([string]$headText).Trim().ToLowerInvariant()
}

function Assert-BaseAncestor([string]$Head) {
    & git.exe -C $RepoRoot merge-base --is-ancestor $BaseHead $Head 2>$null
    Require ($LASTEXITCODE -eq 0) '冻结基线不是当前 HEAD 的祖先'
}

function Assert-CommitAncestor([string]$Ancestor, [string]$Head, [string]$Label) {
    & git.exe -C $RepoRoot merge-base --is-ancestor $Ancestor $Head 2>$null
    Require ($LASTEXITCODE -eq 0) ($Label + ' 不是当前 HEAD 的祖先')
}

function Get-ProcessSnapshot {
    $found = @(Get-CimInstance Win32_Process | Where-Object { $AllowedProcesses -contains ([IO.Path]::GetFileNameWithoutExtension($_.Name)).ToLowerInvariant() } |
        ForEach-Object { [ordered]@{ pid = [int]$_.ProcessId; name = $_.Name; executable = $_.ExecutablePath; command_line = $_.CommandLine; parent_pid = [int]$_.ParentProcessId } })
    return $found
}

function Assert-NoActiveXilinx([string]$Context) {
    $processes = @(Get-ProcessSnapshot)
    Require ($processes.Count -eq 0) ($Context + '检测到活动 Vivado/XSim 进程，拒绝继续：' + (ConvertTo-Json -InputObject $processes -Depth 8 -Compress))
    return $processes
}

function Read-Json([string]$Path) {
    return (Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json)
}

function Assert-FileRecord($Record, [string]$ExpectedPath, [int64]$ExpectedBytes, [string]$ExpectedSha, [string]$Label) {
    Require ([string]$Record.path -ceq $ExpectedPath) ($Label + ' 绑定路径不符')
    Require ([int64]$Record.bytes -eq $ExpectedBytes) ($Label + ' 绑定字节数不符')
    Require ([string]$Record.sha256 -ceq $ExpectedSha) ($Label + ' 绑定 SHA 不符')
    Assert-NoReparseChain $ExpectedPath
    $artifact = Get-Artifact $ExpectedPath
    Require ($artifact.bytes -eq $ExpectedBytes -and $artifact.sha256 -ceq $ExpectedSha) ($Label + ' 实际长度或 SHA 不符')
    return $artifact
}

function Get-Run02Binding {
    Assert-NoReparseChain $Run02Summary
    Assert-NoReparseChain $Run02Binding
    Require ((Get-Sha256 $Run02Summary) -ceq $Run02SummarySha) 'T58 run02 prepare_summary SHA 不匹配'
    Require ((Get-Sha256 $Run02Binding) -ceq $Run02BindingSha) 'T58 run02 project_preflight_binding SHA 不匹配'
    $summary = Read-Json $Run02Summary
    $binding = Read-Json $Run02Binding
    Require ($summary.schema -ceq 'GestureForge-S2A-T58-preparation-summary-v3' -and $summary.run_id -ceq 'run02' -and $summary.status -ceq 'PREPARED_NOT_SIMULATED') 'T58 run02 摘要身份或状态不符'
    Require ($binding.schema -ceq 'GestureForge-S2A-T58-project-preflight-v2' -and $binding.run_id -ceq 'run02' -and $binding.status -ceq 'READ_ONLY_BOUND') 'T58 run02 工程绑定身份或状态不符'
    Require ($summary.baseline_head -ceq $BaseHead -and $binding.baseline_head -ceq $BaseHead) 'T58 run02 固定基线不符'
    Require ($binding.target_xpr_sha256_before_prepare -ceq $XprSha -and $binding.target_xpr_sha256_after_prepare -ceq $XprSha -and $binding.target_xpr_unchanged -eq $true) 'T58 run02 XPR 哈希绑定不符'
    Require (@($binding.T58_source_hashes.PSObject.Properties).Count -eq $ExpectedRtl.Count + 2) 'T58 run02 源清单项目数不符'
    foreach ($relative in $ExpectedRtl.Keys) {
        $path = Join-Path $RepoRoot $relative.Replace('/', '\')
        Assert-NoReparseChain $path
        $actual = Get-Sha256 $path
        Require ($actual -ceq $ExpectedRtl[$relative]) ("共享 RTL 哈希不符：" + $relative)
        Require ([string]$binding.T58_source_hashes.$relative -ceq $ExpectedRtl[$relative]) ("run02 源绑定不符：" + $relative)
    }
    Require ([string]$binding.T58_source_hashes.'sim/tb_s2a_conv_layer35_row22_all_channels.sv' -ceq 'd66dc1f1d58e5214ddbc4739b878f3662d281d40d19b2d5c49a280a885ace688') 'run02 原 TB 历史绑定不符'
    Require ([string]$binding.T58_source_hashes.'verification/test_s2a_conv_layer35_row22_all_channels_rtl.py' -ceq 'c61c5ed246fc0568a520db58a9dfaabf8e7b3152476faf33190f52565c2f0b07') 'run02 原 runner 历史绑定不符'
    Assert-NoReparseChain $T56Report
    Assert-NoReparseChain $T56Summary
    Require ((Get-Sha256 $T56Report) -ceq $T56ReportSha) 'T56 父报告 SHA 不符'
    Require ((Get-Sha256 $T56Summary) -ceq $T56SummarySha) 'T56 simulation_summary SHA 不符'
    Require ($summary.T56_parent_report.path -ceq $T56Report -and $summary.T56_parent_report.sha256 -ceq $T56ReportSha) 'T58 摘要未精确绑定 T56 父报告'
    Require ($summary.T56_summary.path -ceq $T56Summary -and $summary.T56_summary.sha256 -ceq $T56SummarySha) 'T58 摘要未精确绑定 T56 summary'
    $manifestRecord = $summary.fixture.manifest
    $manifestPath = [string]$manifestRecord.path
    Require ($manifestPath -ceq (Join-Path (Join-Path $Run02 'fixture') 'fixture_manifest.json')) 'run02 fixture manifest 路径不符'
    Assert-NoReparseChain $manifestPath
    $manifest = Get-Artifact $manifestPath
    Require ($manifest.bytes -eq [int64]$manifestRecord.bytes -and $manifest.sha256 -ceq [string]$manifestRecord.sha256) 'run02 fixture manifest 字节或 SHA 不符'
    $fixtureFiles = [ordered]@{}
    foreach ($name in $ExpectedFixture.Keys) {
        $expectedPath = Join-Path (Join-Path $Run02 'fixture') $name
        $record = $summary.fixture.files.$name
        $fixtureFiles[$name] = Assert-FileRecord $record $expectedPath $ExpectedFixture[$name].bytes $ExpectedFixture[$name].sha256 ('run02 fixture ' + $name)
    }
    Require ([string]$summary.fixture.root -ceq (Join-Path $Run02 'fixture')) 'run02 fixture 根目录不符'
    Require ([int]$summary.fixture.golden_layout.raw_int32_le_bytes -eq 26624 -and
             [int]$summary.fixture.golden_layout.int8_bytes -eq 6656 -and
             [int]$summary.fixture.golden_layout.total_bytes -eq 33280) 'run02 golden 布局不符'
    Require ((Get-Sha256 $Xpr) -ceq $XprSha) '工程 XPR 当前 SHA 与 run02 固定值不符'
    Assert-NoReparseChain $Xpr
    return [ordered]@{
        summary = Get-Artifact $Run02Summary
        project_binding = Get-Artifact $Run02Binding
        summary_status = [string]$summary.status
        preparation_head = [string]$summary.preparation_head
        base_head = [string]$summary.baseline_head
        xpr_sha256 = Get-Sha256 $Xpr
        t56_parent_report = Get-Artifact $T56Report
        t56_summary = Get-Artifact $T56Summary
        fixture_manifest = $manifest
        fixture_files = $fixtureFiles
        shared_rtl_sha256 = $ExpectedRtl
        oracle_counts = @{ raw_int32 = 6656; int8 = 6656; d2_t23_matches = 6656 }
    }
}

function Assert-AttemptTb {
    Assert-NoReparseChain $AttemptTb
    $tbText = [IO.File]::ReadAllText($AttemptTb, [Text.Encoding]::UTF8)
    Require (-not $tbText.Contains([char]13)) 'attempt03 TB 必须使用 LF 行尾'
    Require (([regex]::Matches($tbText, 'module tb_s2a_conv_layer35_row22_attempt03;')).Count -eq 1) 'attempt03 TB 顶层模块声明不唯一'
    $oldOut = [string][char]92 + [char]92
    $run02Raw = 'D:' + $oldOut + 'FPGA_Competition' + $oldOut + 'report' + $oldOut + 'evidence' + $oldOut + 'S2A-T58' + $oldOut + 'run02' + $oldOut + 'observed_raw.bin'
    $run02Int8 = 'D:' + $oldOut + 'FPGA_Competition' + $oldOut + 'report' + $oldOut + 'evidence' + $oldOut + 'S2A-T58' + $oldOut + 'run02' + $oldOut + 'observed_output.bin'
    $run03Raw = 'D:' + $oldOut + 'FPGA_Competition' + $oldOut + 'report' + $oldOut + 'evidence' + $oldOut + 'S2A-T58' + $oldOut + 'run03' + $oldOut + 'observed_raw.bin'
    $run03Int8 = 'D:' + $oldOut + 'FPGA_Competition' + $oldOut + 'report' + $oldOut + 'evidence' + $oldOut + 'S2A-T58' + $oldOut + 'run03' + $oldOut + 'observed_output.bin'
    Require (([regex]::Matches($tbText, [regex]::Escape($run02Raw))).Count -eq 0 -and
             ([regex]::Matches($tbText, [regex]::Escape($run02Int8))).Count -eq 0) 'attempt03 TB 仍写入 run02'
    Require (([regex]::Matches($tbText, [regex]::Escape($run03Raw))).Count -eq 1 -and
             ([regex]::Matches($tbText, [regex]::Escape($run03Int8))).Count -eq 1) 'attempt03 TB 输出路径不唯一或不属于 run03'
    $fixtureNeedle = 'S2A-T58' + $oldOut + 'run02' + $oldOut + 'fixture' + $oldOut
    Require (([regex]::Matches($tbText, [regex]::Escape($fixtureNeedle))).Count -eq 4) 'attempt03 TB 的 run02 fixture 输入路径数不符'
    Require (([regex]::Matches($tbText, 'T58_XSIM_SENTINEL=PASS')).Count -eq 1) 'attempt03 TB sentinel 必须且只能有一个'
    Require (([regex]::Matches($tbText, '\$finish;')).Count -eq 1) 'attempt03 TB $finish 必须且只能有一个'
    Require (([regex]::Matches($tbText, '"PASS T58 outputs=')).Count -eq 1) 'attempt03 TB PASS 打印必须且只能有一个'
    Require (([regex]::Matches($tbText, '"PROGRESS T58 outputs=')).Count -eq 1) 'attempt03 TB 进度打印格式不符'
    return [ordered]@{ artifact = Get-Artifact $AttemptTb; fixture_input_open_count = 4; run03_output_open_count = 2; sentinel_count = 1; finish_count = 1; pass_format_count = 1; progress_format_count = 1 }
}

function Invoke-Run02PreparedContentVerify([string]$StdoutPath, [string]$StderrPath, [string]$TemporaryRoot) {
    $python = Get-Command -Name 'python.exe' -ErrorAction Stop | Select-Object -First 1
    $pythonPath = $python.Source
    Require (-not [string]::IsNullOrWhiteSpace($pythonPath)) '未找到 python.exe 可执行文件'
    $scriptPath = Join-Path $TemporaryRoot 'verify_t58_prepared_content.py'
    $script = @'
import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout

runner_path = r"D:\FPGA_Competition\verification\test_s2a_conv_layer35_row22_all_channels_rtl.py"
spec = importlib.util.spec_from_file_location("t58_prepared_verifier", runner_path)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load the frozen T58 verifier")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

def sibling_aware_runtime_gate(expect_run02_absent):
    if expect_run02_absent:
        raise RuntimeError("content verify mode never prepares or writes run02")
    return {
        "path_chain_valid": True,
        "target_absent": False,
        "existing_run01": True,
        "existing_run02": True,
        "process_names": list(module.PROCESS_NAMES),
        "processes_before_prepare": [],
        "powershell_exit_code": 0,
        "mcp_status": "NOT_QUERIED",
        "run03_sibling_allowed": True,
    }

module._runtime_preflight = sibling_aware_runtime_gate
captured = io.StringIO()
with redirect_stdout(captured):
    module._verify_prepared()
result = json.loads(captured.getvalue())
print(json.dumps({
    "result": result["result"],
    "preparation_head": result["preparation_head"],
    "current_head_at_verify": result["current_head_at_verify"],
    "prepare_summary_sha256": result["prepare_summary_sha256"],
    "fixture_manifest_sha256": result["fixture_manifest_sha256"],
    "golden_sha256": result["golden_sha256"],
    "output_counts": result["output_counts"],
    "tb_fopen_count": result["tb_fopen_count"],
    "simulation": result["simulation"],
    "verification_mode": "full T58 _verify_prepared; only runtime root-entry inventory accepts sibling run03",
    "original_cli_verify_only_mode": "not used; its exact root-entry guard rejects the required run03 sibling",
}, ensure_ascii=False, indent=2))
'@
    Write-NewText $scriptPath $script
    $arguments = '-B "' + $scriptPath + '"'
    $process = Start-Process -FilePath $pythonPath -ArgumentList $arguments -WorkingDirectory $RepoRoot -NoNewWindow -PassThru -Wait -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath
    Require ($process.HasExited) 'run02 内容核验进程尚未退出'
    $stdoutText = [Text.Encoding]::UTF8.GetString([IO.File]::ReadAllBytes($StdoutPath))
    try { $result = $stdoutText | ConvertFrom-Json } catch { throw ('run02 内容核验 stdout 不是有效 JSON：' + $_.Exception.Message) }
    Require ($process.ExitCode -eq 0) ("run02 内容核验失败，exit=" + $process.ExitCode)
    Require ($result.result -ceq 'PREPARED_NOT_SIMULATED' -and $result.simulation -ceq 'NOT_RUN') 'run02 内容核验状态不符'
    Require ([int]$result.output_counts.raw_int32 -eq 6656 -and [int]$result.output_counts.int8 -eq 6656 -and
             [int]$result.output_counts.d2_t23_matches -eq 6656) 'run02 内容核验数量不符'
    return [ordered]@{
        python = $pythonPath
        command = 'python.exe -B <TEMP>\verify_t58_prepared_content.py'
        temporary_script = Get-Artifact $scriptPath
        exit_code = [int]$process.ExitCode
        stdout = Get-Artifact $StdoutPath
        stderr = Get-Artifact $StderrPath
        verifier_source = Get-Artifact $Verifier
        result = $result
    }
}

function Get-VivadoPath {
    if (-not [string]::IsNullOrWhiteSpace($VivadoExecutable)) {
        Require (Test-Path -LiteralPath $VivadoExecutable -PathType Leaf) '指定的 Vivado executable 不存在'
        Assert-NoReparseChain $VivadoExecutable
        return [IO.Path]::GetFullPath($VivadoExecutable)
    }
    if (-not [string]::IsNullOrWhiteSpace($env:XILINX_VIVADO)) {
        $candidate = Join-Path (Join-Path $env:XILINX_VIVADO 'bin') 'vivado.bat'
        if (Test-Path -LiteralPath $candidate -PathType Leaf) { return [IO.Path]::GetFullPath($candidate) }
    }
    $found = Get-Command -Name 'vivado.exe', 'vivado.bat', 'vivado' -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -ne $found -and -not [string]::IsNullOrWhiteSpace($found.Source)) { return [IO.Path]::GetFullPath($found.Source) }
    throw '未找到 Vivado CLI；Run 模式需指定 -VivadoExecutable 或配置 XILINX_VIVADO/PATH'
}

function Get-DirectoryArtifacts([string]$Root) {
    Assert-NoReparseChain $Root
    $records = @()
    foreach ($directory in @(Get-ChildItem -LiteralPath $Root -Directory -Recurse -Force)) {
        if (($directory.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw ('输出中出现 reparse 目录：' + $directory.FullName) }
    }
    foreach ($file in @(Get-ChildItem -LiteralPath $Root -File -Recurse -Force | Sort-Object FullName)) {
        if (($file.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw ('输出中出现 reparse 文件：' + $file.FullName) }
        $records += Get-Artifact $file.FullName
    }
    return $records
}

function Assert-Run02Inventory {
    $expected = @(
        'prepare_summary.json',
        'project_preflight_binding.json',
        'fixture/feature_input.bin',
        'fixture/layer35_weights.bin',
        'fixture/golden.bin',
        'fixture/vectors.txt',
        'fixture/fixture_manifest.json'
    ) | Sort-Object
    $actual = @(Get-ChildItem -LiteralPath $Run02 -File -Recurse -Force | ForEach-Object {
        $full = [IO.Path]::GetFullPath($_.FullName)
        Assert-ContainedPath $full
        Require (($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) ("run02 中出现 reparse 文件：" + $full)
        $full.Substring(([IO.Path]::GetFullPath($Run02).TrimEnd([char]92) + '\').Length).Replace('\', '/')
    } | Sort-Object)
    foreach ($directory in @(Get-ChildItem -LiteralPath $Run02 -Directory -Recurse -Force)) {
        Require (($directory.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) ("run02 中出现 reparse 目录：" + $directory.FullName)
    }
    Require (($actual -join '|') -ceq ($expected -join '|')) ("run02 文件清单不符：actual=" + ($actual -join ',') + '; expected=' + ($expected -join ','))
    return $actual
}

function Assert-TaskDirectoryGate([string]$EvidenceRoot, [string[]]$ExpectedRootEntries, [string[]]$ExpectedRun03Nodes, [string[]]$ExpectedRun03Files, [string[]]$AllowedRun03Directories = @()) {
    $evidenceFull = [IO.Path]::GetFullPath($EvidenceRoot)
    $run03Path = Join-Path $evidenceFull 'run03'
    Require (Test-Path -LiteralPath $evidenceFull -PathType Container) ("证据根目录不存在：" + $evidenceFull)
    Require (Test-Path -LiteralPath $run03Path -PathType Container) 'run03 目录不存在'
    $rootNodes = @(Get-ChildItem -LiteralPath $evidenceFull -Force | ForEach-Object { $_.Name } | Sort-Object)
    $expectedRoot = @($ExpectedRootEntries | Sort-Object)
    Require (($rootNodes -join '|') -ceq ($expectedRoot -join '|')) ("T58 evidence 根目录节点不符：actual=" + ($rootNodes -join ',') + '; expected=' + ($expectedRoot -join ','))
    $runNodes = @(Get-ChildItem -LiteralPath $run03Path -Force | ForEach-Object { $_.Name } | Sort-Object)
    $expectedNodes = @($ExpectedRun03Nodes | Sort-Object)
    Require (($runNodes -join '|') -ceq ($expectedNodes -join '|')) ("run03 节点不符：actual=" + ($runNodes -join ',') + '; expected=' + ($expectedNodes -join ','))
    $pending = New-Object 'System.Collections.Generic.Stack[string]'
    $pending.Push($evidenceFull)
    while ($pending.Count -gt 0) {
        $directory = $pending.Pop()
        foreach ($path in [IO.Directory]::EnumerateFileSystemEntries($directory)) {
            $item = Get-Item -LiteralPath $path -Force
            Require (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) ("T58 evidence 中出现 reparse/symlink：" + $path)
            if ($item.PSIsContainer) { $pending.Push($item.FullName) }
        }
    }
    $actualRunFiles = @()
    foreach ($file in @(Get-ChildItem -LiteralPath $run03Path -File -Recurse -Force)) {
        $full = [IO.Path]::GetFullPath($file.FullName)
        $skip = $false
        foreach ($directoryName in $AllowedRun03Directories) {
            $allowedRoot = [IO.Path]::GetFullPath((Join-Path $run03Path $directoryName)).TrimEnd([char]92) + '\'
            if ($full.StartsWith($allowedRoot, [StringComparison]::OrdinalIgnoreCase)) { $skip = $true; break }
        }
        if (-not $skip) {
            $actualRunFiles += $full.Substring(([IO.Path]::GetFullPath($run03Path).TrimEnd([char]92) + '\').Length).Replace('\', '/')
        }
    }
    foreach ($directory in @(Get-ChildItem -LiteralPath $run03Path -Directory -Recurse -Force)) {
        $relative = $directory.FullName.Substring(([IO.Path]::GetFullPath($run03Path).TrimEnd([char]92) + '\').Length).Replace('\', '/')
        $topName = $relative.Split('/')[0]
        Require ($AllowedRun03Directories -contains $topName) ("run03 出现未登记目录：" + $relative)
    }
    $actualRunFiles = @($actualRunFiles | Sort-Object)
    $expectedFiles = @($ExpectedRun03Files | Sort-Object)
    Require (($actualRunFiles -join '|') -ceq ($expectedFiles -join '|')) ("run03 文件清单不符：actual=" + ($actualRunFiles -join ',') + '; expected=' + ($expectedFiles -join ','))
    return [ordered]@{ evidence_root_entries = $rootNodes; run03_nodes = $runNodes; run03_files = $actualRunFiles; reparse_points = 0 }
}

function Test-DirectoryGateNegativeCases([string]$TemporaryRoot) {
    $probe = Join-Path $TemporaryRoot 'inventory_gate_negative_tests'
    $target = Join-Path $TemporaryRoot 'inventory_gate_junction_target'
    $junction = Join-Path (Join-Path $probe 'run03') 'linked_directory'
    Require (-not (Test-Path -LiteralPath $probe)) '目录门禁负测 scratch 路径碰撞'
    Require (-not (Test-Path -LiteralPath $target)) '目录门禁 junction target 路径碰撞'
    $probeFull = [IO.Path]::GetFullPath($probe)
    $temporaryFull = [IO.Path]::GetFullPath($TemporaryRoot).TrimEnd([char]92) + '\'
    Require ($probeFull.StartsWith($temporaryFull, [StringComparison]::OrdinalIgnoreCase)) '门禁负测目录逃逸 TEMP scratch'
    $probeRun03 = Join-Path $probe 'run03'
    $junctionCreated = $false
    try {
        [IO.Directory]::CreateDirectory($probeRun03) | Out-Null
        [IO.Directory]::CreateDirectory((Join-Path $probe 'run01')) | Out-Null
        [IO.Directory]::CreateDirectory((Join-Path $probe 'run02')) | Out-Null
        Write-NewText (Join-Path $probe 'project_preflight_binding.json') '{}'
        Write-NewText (Join-Path $probeRun03 'allowed.json') '{}'
        $rootNames = @('project_preflight_binding.json', 'run01', 'run02', 'run03')
        $nodeNames = @('allowed.json')
        $fileNames = @('allowed.json')
        [void](Assert-TaskDirectoryGate $probe $rootNames $nodeNames $fileNames)

        [IO.Directory]::CreateDirectory((Join-Path $probe 'extra_sibling')) | Out-Null
        $extraSiblingRejected = $false
        try { [void](Assert-TaskDirectoryGate $probe $rootNames $nodeNames $fileNames) } catch { $extraSiblingRejected = $true }
        Require $extraSiblingRejected '目录门禁未拒绝额外 sibling'
        Remove-Item -LiteralPath (Join-Path $probe 'extra_sibling') -Recurse -Force

        Write-NewText (Join-Path $probeRun03 'unexpected.bin') 'extra'
        $extraFileRejected = $false
        try { [void](Assert-TaskDirectoryGate $probe $rootNames $nodeNames $fileNames) } catch { $extraFileRejected = $true }
        Require $extraFileRejected '目录门禁未拒绝 run03 未登记文件'
        Remove-Item -LiteralPath (Join-Path $probeRun03 'unexpected.bin') -Force

        Remove-Item -LiteralPath (Join-Path $probeRun03 'allowed.json') -Force
        [IO.Directory]::CreateDirectory($target) | Out-Null
        New-Item -ItemType Junction -Path $junction -Target $target -ErrorAction Stop | Out-Null
        $junctionCreated = $true
        $symlinkRejected = $false
        try { [void](Assert-TaskDirectoryGate $probe $rootNames @('linked_directory') @() @('linked_directory')) } catch { $symlinkRejected = $true }
        Require $symlinkRejected '目录门禁未拒绝 run03 junction/reparse'
    }
    finally {
        if ($junctionCreated -and (Test-Path -LiteralPath $junction)) {
            Remove-Item -LiteralPath $junction -Force
        }
        if (Test-Path -LiteralPath $probe) {
            foreach ($entry in @(Get-ChildItem -LiteralPath $probe -Force -Recurse)) {
                Require (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) ("负测清理前发现 reparse：" + $entry.FullName)
            }
            Remove-Item -LiteralPath $probe -Recurse -Force
        }
        if (Test-Path -LiteralPath $target) {
            Require ([IO.Path]::GetFullPath($target).StartsWith($temporaryFull, [StringComparison]::OrdinalIgnoreCase)) 'junction target 清理路径逃逸 TEMP'
            Remove-Item -LiteralPath $target -Recurse -Force
        }
    }
    Require (-not (Test-Path -LiteralPath $probe) -and -not (Test-Path -LiteralPath $target)) '目录门禁负测 scratch 清理失败'
    return [ordered]@{
        clean_gate_pass = $true
        extra_sibling_rejected = $extraSiblingRejected
        unexpected_run03_file_rejected = $extraFileRejected
        symlink_rejected = $symlinkRejected
        symlink_kind = 'Windows junction（reparse directory）'
        scratch_removed = $true
    }
}
function Assert-T58SiblingDirectoryGate([string[]]$ExpectedRun03Files, [string[]]$ExpectedRun03Directories = @()) {
    Assert-NoReparseChain $Run03
    Assert-Run02Inventory | Out-Null
    $root = Split-Path -Parent $Run03
    $expectedRootEntries = @('project_preflight_binding.json', 'run01', 'run02', 'run03')
    $expectedNodes = @($ExpectedRun03Files + $ExpectedRun03Directories)
    return Assert-TaskDirectoryGate $root $expectedRootEntries $expectedNodes $ExpectedRun03Files $ExpectedRun03Directories
}

function Get-ExpectedRun03InventoryFiles {
    return @(
        'run_project_sim.tcl',
        'xsim_run.tcl',
        'run02_verify.stdout.json',
        'run02_verify.stderr.bin',
        'run02_prepared_content_verify.stdout.json',
        'run02_prepared_content_verify.stderr.bin',
        'run02_prepared_content_verify_attempt02.stdout.json',
        'run02_prepared_content_verify_attempt02.stderr.bin',
        'isolated_sim_binding.json',
        'directory_gate_negative_tests.json',
        'dryrun_plan.json',
        'process_check.json',
        'run02_cli_verify_sibling_guard.json',
        'dryrun_summary.json'
    )
}

function Assert-Run03DryRunInventory {
    Assert-NoReparseChain $Run03
    $inventoryPath = Join-Path $Run03 'isolated_run_inventory.json'
    Assert-NoReparseChain $inventoryPath
    Require ((Get-Sha256 $inventoryPath) -ceq $Run03InventorySha) 'run03 dryrun inventory 固定 SHA 不匹配'
    $inventory = Read-Json $inventoryPath
    Require ($inventory.schema -ceq 'GestureForge-S2A-T58-isolated-run-inventory-v1' -and
             $inventory.run_id -ceq 'run03' -and
             $inventory.status -ceq 'PRE_FINAL_GATE_SNAPSHOT') 'run03 dryrun inventory 身份或状态不符'
    $expected = @(Get-ExpectedRun03InventoryFiles | Sort-Object)
    $records = @($inventory.evidence_files)
    $actual = @($records | ForEach-Object { [string]$_.relative_path } | Sort-Object)
    Require (($actual -join '|') -ceq ($expected -join '|')) 'run03 dryrun inventory 文件名清单不符'
    foreach ($record in $records) {
        $relative = [string]$record.relative_path
        Require ($expected -contains $relative) ('run03 inventory 出现未登记路径：' + $relative)
        $path = [IO.Path]::GetFullPath((Join-Path $Run03 $relative))
        Assert-ContainedPath $path
        Assert-NoReparseChain $path
        Require ([string]$record.artifact.path -ceq $path) ('run03 inventory 路径字段不符：' + $relative)
        $actualArtifact = Get-Artifact $path
        Require ([int64]$record.artifact.bytes -eq $actualArtifact.bytes -and
                 [string]$record.artifact.sha256 -ceq $actualArtifact.sha256) ('run03 inventory 文件 SHA/长度不符：' + $relative)
    }
    $expectedNodes = @($expected + 'isolated_run_inventory.json')
    $gate = Assert-T58SiblingDirectoryGate $expectedNodes
    $run02 = Get-Run02Binding
    Require ($run02.summary.sha256 -ceq $Run02SummarySha -and
             $run02.project_binding.sha256 -ceq $Run02BindingSha) '启动前 run02 summary/project binding SHA 不符'
    return [ordered]@{
        status = 'PASS_READ_ONLY_ISOLATED_RUN_INVENTORY'
        inventory = Get-Artifact $inventoryPath
        inventory_file_count = $records.Count
        directory_gate = $gate
        run02_summary = $run02.summary
        run02_project_binding = $run02.project_binding
        xpr_sha256 = $run02.xpr_sha256
    }
}

function Invoke-AuditInventory {
    $head = Get-CurrentHead
    Assert-BaseAncestor $head
    $inventory = Assert-Run03DryRunInventory
    $binding = Read-Json $Run03BindingPath
    $recordedLauncherSha = [string]$binding.source_files.'verification/run_s2a_t58_row22_isolated_sim.ps1'.sha256
    $currentLauncherSha = Get-Sha256 $PSCommandPath
    Write-Output (ConvertTo-Json -InputObject ([ordered]@{
        status = 'INVENTORY_PASS_RUN_BLOCKED_BY_STALE_LAUNCHER_BINDING'
        audit_mode = 'AuditInventory（只读，不运行 Python/Vivado/XSim）'
        current_head = $head
        current_launcher_sha256 = $currentLauncherSha
        dryrun_bound_launcher_sha256 = $recordedLauncherSha
        current_launcher_matches_dryrun_binding = ($currentLauncherSha -ceq $recordedLauncherSha)
        run_allowed = ($currentLauncherSha -ceq $recordedLauncherSha)
        inventory_gate = $inventory
        simulation = 'NOT_RUN'
    }) -Depth 16)
}

function New-Run03BaseEvidence {
    Assert-NoReparseChain $Run03
    $entries = @(Get-ChildItem -LiteralPath $Run03 -Force)
    $baseNames = @('run_project_sim.tcl', 'xsim_run.tcl', 'run02_verify.stdout.json', 'run02_verify.stderr.bin') | Sort-Object
    $attempt01Names = @($baseNames + 'run02_prepared_content_verify.stdout.json' + 'run02_prepared_content_verify.stderr.bin') | Sort-Object
    $actualNames = @($entries | ForEach-Object { $_.Name } | Sort-Object)
    Require (@($entries | Where-Object { $_.PSIsContainer }).Count -eq 0) 'run03 初始内容不得有目录'
    $joinedActual = $actualNames -join '|'
    if ($joinedActual -ceq ($baseNames -join '|')) {
        $acceptedNames = $baseNames
    }
    elseif ($joinedActual -ceq ($attempt01Names -join '|')) {
        $acceptedNames = $attempt01Names
    }
    else {
        throw ('run03 内容不匹配预期的原始四件或保留的 attempt01 六件：actual=' + $joinedActual)
    }
    Require (Test-Path -LiteralPath $ProjectTcl -PathType Leaf) 'run_project_sim.tcl 缺失'
    Require (Test-Path -LiteralPath $XsimTcl -PathType Leaf) 'xsim_run.tcl 缺失'
    [void](Assert-T58SiblingDirectoryGate $acceptedNames)
}
function Invoke-DryRun {
    New-Run03BaseEvidence
    $headBefore = Get-CurrentHead
    Assert-BaseAncestor $headBefore
    $processesBefore = Assert-NoActiveXilinx 'DryRun 开始前：'
    $binding = Get-Run02Binding
    $tbBinding = Assert-AttemptTb
    $projectTclArtifact = Get-Artifact $ProjectTcl
    $xsimTclArtifact = Get-Artifact $XsimTcl
    $launcherArtifact = Get-Artifact $PSCommandPath

    $tempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    $scratch = Join-Path $tempRoot ('s2a_t58_row22_dryrun_' + [Guid]::NewGuid().ToString('N'))
    Require (-not (Test-Path -LiteralPath $scratch)) 'dry-run scratch 路径碰撞'
    [IO.Directory]::CreateDirectory($scratch) | Out-Null
    $verify = Invoke-Run02PreparedContentVerify (Join-Path $Run03 'run02_prepared_content_verify_attempt02.stdout.json') (Join-Path $Run03 'run02_prepared_content_verify_attempt02.stderr.bin') $scratch
    $negativeCases = Test-DirectoryGateNegativeCases $scratch
    $run02After = Get-Run02Binding
    Require ($binding.xpr_sha256 -ceq $run02After.xpr_sha256) 'run02 XPR 在内容核验前后变化'
    $scratchProject = Join-Path $scratch 'isolated_project_plan.json'
    $scratchPlan = [ordered]@{
        project_name = 'T58_Row22_Attempt03'
        scratch_project_directory = Join-Path $Run03 'isolated_project'
        vivado_script = $ProjectTcl
        target_part = 'xc7z020clg400-1'
        source_files = @($ExpectedRtl.Keys | ForEach-Object { Join-Path $RepoRoot $_.Replace('/', '\') }) + @($AttemptTb)
        compile_elaborate = @('launch_simulation -mode behavioral -step all 生成并执行 compile.bat、elaborate.bat')
        simulate = @('launch_simulation -mode behavioral -step all 执行 simulate.bat；xsim_run.tcl: run all; quit')
        wave_output = $false
        executed = $false
    }
    Write-NewJson $scratchProject $scratchPlan
    $scratchArtifact = Get-Artifact $scratchProject
    $scratchRootCanonical = [IO.Path]::GetFullPath($tempRoot).TrimEnd('\') + '\'
    Require ([IO.Path]::GetFullPath($scratch).StartsWith($scratchRootCanonical, [StringComparison]::OrdinalIgnoreCase)) 'dry-run scratch 路径不在 TEMP 下'
    Assert-NoReparseChain $scratchProject $tempRoot
    foreach ($scratchEntry in @(Get-ChildItem -LiteralPath $scratch -Force -Recurse)) {
        Require (($scratchEntry.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) ("dry-run scratch 出现 reparse 项：" + $scratchEntry.FullName)
    }
    Remove-Item -LiteralPath $scratch -Recurse -Force
    Require (-not (Test-Path -LiteralPath $scratch)) 'dry-run scratch 清理失败'
    $headAfter = Get-CurrentHead
    Require ($headAfter -ceq $headBefore) 'DryRun 期间 HEAD 变化'
    $processesAfter = @(Get-ProcessSnapshot)
    Require ($processesAfter.Count -eq 0) 'DryRun 后检测到 Vivado/XSim 进程'
    $xprAfter = Get-Sha256 $Xpr
    Require ($xprAfter -ceq $XprSha) 'DryRun 后工程 XPR 哈希变化'

    $sourceFiles = [ordered]@{}
    foreach ($relative in $ExpectedRtl.Keys) { $sourceFiles[$relative] = Get-Artifact (Join-Path $RepoRoot $relative.Replace('/', '\')) }
    $sourceFiles['sim/tb_s2a_conv_layer35_row22_attempt03.sv'] = $tbBinding.artifact
    $sourceFiles['verification/test_s2a_conv_layer35_row22_all_channels_rtl.py'] = Get-Artifact $Verifier
    $sourceFiles['verification/run_s2a_t58_row22_isolated_sim.ps1'] = $launcherArtifact
    $sourceFiles['report/evidence/S2A-T58/run03/run_project_sim.tcl'] = $projectTclArtifact
    $sourceFiles['report/evidence/S2A-T58/run03/xsim_run.tcl'] = $xsimTclArtifact
    $bindingDoc = [ordered]@{
        schema = 'GestureForge-S2A-T58-isolated-sim-binding-v1'
        task_id = 'S2A-T58'
        run_id = 'run03'
        status = 'READ_ONLY_BOUND'
        run02_summary = $binding.summary
        run02_project_preflight_binding = $binding.project_binding
        T56_parent_report = $binding.t56_parent_report
        T56_summary = $binding.t56_summary
        fixture_manifest = $binding.fixture_manifest
        fixture_files = $binding.fixture_files
        source_files = $sourceFiles
        output_paths = @{ observed_raw = (Join-Path $Run03 'observed_raw.bin'); observed_int8 = (Join-Path $Run03 'observed_output.bin') }
        target_xpr = @{ path = $Xpr; sha256_before = $XprSha; sha256_after = $xprAfter; unchanged = ($xprAfter -ceq $XprSha) }
        base_head = $BaseHead
        current_head_before = $headBefore
        current_head_after = $headAfter
        scope = @{ layer = 35; y = 22; x_min = 0; x_max = 25; channels = 256; expected_points_per_output = 6656; raw_int32_bytes = 26624; int8_bytes = 6656 }
        source_snapshot_policy = '固定原始 run02 不修改；attempt03 TB 从 run02 读取输入并将输出写入 run03'
    }
    Write-NewJson (Join-Path $Run03 'isolated_sim_binding.json') $bindingDoc
    Write-NewJson (Join-Path $Run03 'directory_gate_negative_tests.json') $negativeCases
    $cliFailure = [ordered]@{
        schema = 'GestureForge-S2A-T58-existing-cli-sibling-guard-observation-v1'
        status = 'BLOCKED_BY_RUN03_SIBLING_ROOT_INVENTORY'
        invocation = 'python.exe -B verification/test_s2a_conv_layer35_row22_all_channels_rtl.py --verify-only'
        exit_code = 1
        stdout = Get-Artifact (Join-Path $Run03 'run02_verify.stdout.json')
        stderr = Get-Artifact (Join-Path $Run03 'run02_verify.stderr.bin')
        explanation = '原 runner 的只读 PowerShell 根目录门禁要求 evidenceRoot 仅包含 root binding、run01、run02；任务要求的新 sibling run03 使该 CLI 失败。run02 数据本身由上述完整 _verify_prepared 内容核验重新验证。'
        prior_cli_verify_before_run03 = @{ status = 'PASS_OBSERVED_BEFORE_RUN03_CREATION'; exit_code = 0; raw_stdout_preserved = $false; raw_artifact_path = $null; raw_artifact_sha256 = $null }
    }
    Write-NewJson (Join-Path $Run03 'run02_cli_verify_sibling_guard.json') $cliFailure
    $planDoc = [ordered]@{
        schema = 'GestureForge-S2A-T58-isolated-sim-dryrun-plan-v1'
        mode = 'DryRun'
        compile_elaborate = @{ planned = $true; executed = $false; isolated_project = (Join-Path $Run03 'isolated_project'); vivado_script = $ProjectTcl; actions = @('create_project xc7z020clg400-1', 'add 5 bound RTL sources and attempt03 testbench', 'launch_simulation -mode behavioral -step all; Vivado performs compile then elaborate before simulate') }
        simulate = @{ planned = $true; executed = $false; script = $XsimTcl; actions = @('run all', 'T58_XSIM_TCL_RUN_ALL_RETURNED', 'quit'); waves = 'disabled; no wave commands or waveform output configured' }
        invocation = @{ executable_available_in_path = ($null -ne (Get-Command -Name 'vivado.exe', 'vivado.bat', 'vivado' -ErrorAction SilentlyContinue | Select-Object -First 1)); actual_vivado_or_xsim_invoked = $false }
        scratch_plan_artifact = $scratchArtifact
        scratch_path = $scratch
        scratch_removed = $true
        run02_prepared_content_verify = $verify
        directory_gate_negative_tests = Get-Artifact (Join-Path $Run03 'directory_gate_negative_tests.json')
        process_check_before = $processesBefore
        process_check_after = $processesAfter
        XPR_sha256_before = $XprSha
        XPR_sha256_after = $xprAfter
    }
    Write-NewJson (Join-Path $Run03 'dryrun_plan.json') $planDoc
    Write-NewJson (Join-Path $Run03 'process_check.json') ([ordered]@{ before = $processesBefore; after = $processesAfter; policy = '只观察，不控制或停止现有进程' })
    $summary = [ordered]@{
        schema = 'GestureForge-S2A-T58-isolated-sim-dryrun-summary-v1'
        task_id = 'S2A-T58'
        run_id = 'run03'
        status = 'DRYRUN_READY_NOT_SIMULATED'
        simulation = 'NOT_RUN'
        head = @{ base = $BaseHead; at_start = $headBefore; at_end = $headAfter; unchanged_during_run = $true }
        verification_mode = '自建 isolated-run sibling 内容门禁；不是官方 --verify-only'
        run02_prepared_content_verification = $verify
        directory_gate_negative_tests = $negativeCases
        oracle_counts = $verify.result.output_counts
        new_tb = $tbBinding
        run02_binding_sha256 = $binding.project_binding.sha256
        run02_summary_sha256 = $binding.summary.sha256
        source_binding_path = (Join-Path $Run03 'isolated_sim_binding.json')
        compile_elaborate = @{ planned = $true; executed = $false; scratch_cleaned = $true }
        xsim = @{ planned = $true; executed = $false; pid = $null; exit_code = $null; sentinel_expected = 1; progress_expected = 256; pass_expected = 1; finish_expected = 1 }
        target_xpr = @{ before = $XprSha; after = $xprAfter; unchanged = ($xprAfter -ceq $XprSha) }
        xilinx_processes_before = $processesBefore
        xilinx_processes_after = $processesAfter
        tool_availability = @{ vivado_on_path = ($null -ne (Get-Command -Name 'vivado.exe', 'vivado.bat', 'vivado' -ErrorAction SilentlyContinue | Select-Object -First 1)); tclsh_on_path = ($null -ne (Get-Command -Name 'tclsh.exe', 'tclsh' -ErrorAction SilentlyContinue | Select-Object -First 1)) }
        launcher = $launcherArtifact
        project_tcl = $projectTclArtifact
        xsim_tcl = $xsimTclArtifact
        expected_output = @{ raw_int32_bytes = 26624; int8_bytes = 6656; compare_raw_to_golden = $true; compare_int8_to_run02_d2_t23_golden = $true }
    }
    Write-NewJson (Join-Path $Run03 'dryrun_summary.json') $summary
    $inventoryNames = @(
        'run_project_sim.tcl',
        'xsim_run.tcl',
        'run02_verify.stdout.json',
        'run02_verify.stderr.bin',
        'run02_prepared_content_verify.stdout.json',
        'run02_prepared_content_verify.stderr.bin',
        'run02_prepared_content_verify_attempt02.stdout.json',
        'run02_prepared_content_verify_attempt02.stderr.bin',
        'isolated_sim_binding.json',
        'directory_gate_negative_tests.json',
        'dryrun_plan.json',
        'process_check.json',
        'run02_cli_verify_sibling_guard.json',
        'dryrun_summary.json'
    )
    $inventoryRecords = @($inventoryNames | ForEach-Object { [ordered]@{ relative_path = $_; artifact = Get-Artifact (Join-Path $Run03 $_) } })
    Write-NewJson (Join-Path $Run03 'isolated_run_inventory.json') ([ordered]@{
        schema = 'GestureForge-S2A-T58-isolated-run-inventory-v1'
        status = 'PRE_FINAL_GATE_SNAPSHOT'
        run_id = 'run03'
        evidence_files = $inventoryRecords
        self_record = '本清单不对自身建立递归 SHA；其文件本身仍受精确清单与 reparse 门禁检查'
    })
    $expectedRun03Files = @($inventoryNames + 'isolated_run_inventory.json')
    $finalGate = Assert-T58SiblingDirectoryGate $expectedRun03Files
    $finalBinding = Get-Run02Binding
    Require ($finalBinding.summary.sha256 -ceq $Run02SummarySha -and $finalBinding.project_binding.sha256 -ceq $Run02BindingSha) 'final gate 后 run02 root binding/summary SHA 改变'
    Require ($finalBinding.xpr_sha256 -ceq $XprSha) 'final gate 后 XPR SHA 改变'
    $finalProcesses = Assert-NoActiveXilinx 'DryRun 结束后：'
    Write-Output (ConvertTo-Json -InputObject ([ordered]@{
        status = 'PASS_SELF_BUILT_ISOLATED_RUN_GATE'
        official_cli_verify_only = 'BLOCKED_BY_RUN03_SIBLING_ROOT_INVENTORY'
        content_verification_mode = '完整 T58 _verify_prepared()，仅替换 runtime root inventory gate 以容纳 run03'
        directory_gate = $finalGate
        run02_summary_sha256 = $finalBinding.summary.sha256
        run02_binding_sha256 = $finalBinding.project_binding.sha256
        xpr_sha256 = $finalBinding.xpr_sha256
        process_check_after_final_gate = $finalProcesses
        simulation = 'NOT_RUN'
        compile_elaborate = 'NOT_RUN'
    }) -Depth 16)
    Write-Output (ConvertTo-Json -InputObject $summary -Depth 20)
}

function Invoke-Run {
    $dryrunInventory = Assert-Run03DryRunInventory
    $dryrunSummaryPath = Join-Path $Run03 'dryrun_summary.json'
    $bindingPath = Join-Path $Run03 'isolated_sim_binding.json'
    Assert-NoReparseChain $dryrunSummaryPath
    Assert-NoReparseChain $bindingPath
    $dry = Read-Json $dryrunSummaryPath
    $bound = Read-Json $bindingPath
    Require ($dry.status -ceq 'DRYRUN_READY_NOT_SIMULATED' -and $dry.simulation -ceq 'NOT_RUN') 'run03 dryrun 状态不允许实际启动'
    Require ($bound.schema -ceq 'GestureForge-S2A-T58-isolated-sim-binding-v1' -and $bound.status -ceq 'READ_ONLY_BOUND') 'run03 source binding 状态不符'
    Require ((Get-Sha256 $Run02Summary) -ceq $Run02SummarySha -and (Get-Sha256 $Run02Binding) -ceq $Run02BindingSha) 'run02 固定证据发生变化'
    $headBefore = Get-CurrentHead
    Assert-BaseAncestor $headBefore
    Assert-CommitAncestor ([string]$dry.head.at_end) $headBefore 'dryrun HEAD 快照'
    $processesBefore = Assert-NoActiveXilinx 'Run 启动前：'
    $currentBinding = Get-Run02Binding
    $currentTb = Assert-AttemptTb
    Require ($currentTb.artifact.sha256 -ceq [string]$dry.new_tb.artifact.sha256) 'attempt03 TB 与 dryrun 哈希不符'
    Require ((Get-Sha256 $Verifier) -ceq [string]$bound.source_files.'verification/test_s2a_conv_layer35_row22_all_channels_rtl.py'.sha256) 'T58 verify-only runner 与 dryrun 哈希不符'
    Require ((Get-Sha256 $PSCommandPath) -ceq [string]$bound.source_files.'verification/run_s2a_t58_row22_isolated_sim.ps1'.sha256) 'isolated launcher 与 dryrun 哈希不符'
    Require ((Get-Sha256 $ProjectTcl) -ceq [string]$bound.source_files.'report/evidence/S2A-T58/run03/run_project_sim.tcl'.sha256) 'Vivado Tcl 与 dryrun 哈希不符'
    Require ((Get-Sha256 $XsimTcl) -ceq [string]$bound.source_files.'report/evidence/S2A-T58/run03/xsim_run.tcl'.sha256) 'XSim Tcl 与 dryrun 哈希不符'
    foreach ($relative in $ExpectedRtl.Keys) {
        $path = Join-Path $RepoRoot $relative.Replace('/', '\')
        Require ((Get-Sha256 $path) -ceq [string]$bound.source_files.$relative.sha256) ("共享 RTL 在 dryrun 后变化：" + $relative)
    }
    $vivado = Get-VivadoPath
    $projectDir = Join-Path $Run03 'isolated_project'
    Require (-not (Test-Path -LiteralPath $projectDir)) '隔离 Vivado 项目目录已存在，拒绝覆盖'
    $newOutputs = @(
        (Join-Path $Run03 'vivado_console.stdout.bin'),
        (Join-Path $Run03 'vivado_console.stderr.bin'),
        (Join-Path $Run03 'xsim_console_transcript.raw.bin'),
        (Join-Path $Run03 'runtime_processes.json'),
        (Join-Path $Run03 'runtime_summary.json'),
        (Join-Path $Run03 'runtime_prelaunch_content_verify.stdout.json'),
        (Join-Path $Run03 'runtime_prelaunch_content_verify.stderr.bin'),
        (Join-Path $Run03 'observed_raw.bin'),
        (Join-Path $Run03 'observed_output.bin'),
        (Join-Path $Run03 'compile.generated.bat'),
        (Join-Path $Run03 'elaborate.generated.bat'),
        (Join-Path $Run03 'simulate.generated.bat'),
        (Join-Path $Run03 'vivado.jou'),
        (Join-Path $Run03 'vivado.log'),
        (Join-Path $Run03 'runtime_gate.json'),
        (Join-Path $Run03 'NON_ACCEPTANCE_run03.json')
    )
    foreach ($path in $newOutputs) { Require (-not (Test-Path -LiteralPath $path)) ("Run 输出路径已存在，拒绝覆盖：" + $path) }
    $xprBefore = Get-Sha256 $Xpr
    Require ($xprBefore -ceq $XprSha) 'Run 启动前 XPR SHA 不符'
    $verifyTempRoot = [IO.Path]::GetFullPath([IO.Path]::GetTempPath())
    $verifyScratch = Join-Path $verifyTempRoot ('s2a_t58_row22_run_verify_' + [Guid]::NewGuid().ToString('N'))
    Require (-not (Test-Path -LiteralPath $verifyScratch)) 'Run 内容核验 scratch 路径碰撞'
    [IO.Directory]::CreateDirectory($verifyScratch) | Out-Null
    try {
        $cpuVerify = Invoke-Run02PreparedContentVerify (Join-Path $Run03 'runtime_prelaunch_content_verify.stdout.json') (Join-Path $Run03 'runtime_prelaunch_content_verify.stderr.bin') $verifyScratch
    }
    finally {
        if (Test-Path -LiteralPath $verifyScratch) {
            foreach ($scratchEntry in @(Get-ChildItem -LiteralPath $verifyScratch -Force -Recurse)) {
                Require (($scratchEntry.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) ("Run scratch 清理前出现 reparse 项：" + $scratchEntry.FullName)
            }
            Remove-Item -LiteralPath $verifyScratch -Recurse -Force
        }
    }
    Require (-not (Test-Path -LiteralPath $verifyScratch)) 'Run 内容核验 scratch 清理失败'
    Require ([int]$cpuVerify.result.output_counts.raw_int32 -eq 6656 -and
             [int]$cpuVerify.result.output_counts.int8 -eq 6656 -and
             [int]$cpuVerify.result.output_counts.d2_t23_matches -eq 6656) 'Run 启动前 CPU oracle 对照未通过'
    $processesPreVivado = Assert-NoActiveXilinx 'Vivado 启动前最终检查：'
    $arguments = '/d /s /c ""' + $vivado + '" -mode batch -source "' + $ProjectTcl + '" -tclargs "' + $Run03 + '"'
    $proc = Start-Process -FilePath $env:ComSpec -ArgumentList $arguments -WorkingDirectory $Run03 -NoNewWindow -PassThru -RedirectStandardOutput (Join-Path $Run03 'vivado_console.stdout.bin') -RedirectStandardError (Join-Path $Run03 'vivado_console.stderr.bin')
    $seen = @{}
    $seen[[string]$proc.Id] = [ordered]@{ pid = [int]$proc.Id; name = 'cmd.exe'; command_line = $arguments; parent_pid = $null }
    while (-not $proc.HasExited) {
        $all = @(Get-CimInstance Win32_Process)
        $owned = New-Object System.Collections.Generic.HashSet[int]
        [void]$owned.Add([int]$proc.Id)
        $changed = $true
        while ($changed) {
            $changed = $false
            foreach ($item in $all) {
                $name = [IO.Path]::GetFileNameWithoutExtension([string]$item.Name).ToLowerInvariant()
                if (($AllowedProcesses -contains $name) -and ($owned.Contains([int]$item.ParentProcessId) -or ([string]$item.CommandLine).Contains($Run03))) {
                    if ($owned.Add([int]$item.ProcessId)) { $changed = $true }
                    $seen[[string]$item.ProcessId] = [ordered]@{ pid = [int]$item.ProcessId; name = $item.Name; executable = $item.ExecutablePath; command_line = $item.CommandLine; parent_pid = [int]$item.ParentProcessId }
                }
            }
        }
        Start-Sleep -Seconds 5
        $proc.Refresh()
    }
    $proc.WaitForExit()
    $runtimeExit = [int]$proc.ExitCode
    $headAfter = Get-CurrentHead
    Require ($headAfter -ceq $headBefore) 'Vivado/XSim 运行期间 HEAD 变化'
    $xprAfter = Get-Sha256 $Xpr
    Require ($xprAfter -ceq $xprBefore -and $xprAfter -ceq $XprSha) 'Vivado/XSim 运行期间原 XPR 发生变化'
    $allProcessesAfter = @(Get-ProcessSnapshot)
    Require ($allProcessesAfter.Count -eq 0) 'Run 结束后仍有 Vivado/XSim 进程；不发送控制命令'

    $consolePath = Join-Path $Run03 'vivado_console.stdout.bin'
    $transcriptPath = Join-Path $Run03 'xsim_console_transcript.raw.bin'
    $consoleBytes = [IO.File]::ReadAllBytes($consolePath)
    $consoleText = [Text.Encoding]::UTF8.GetString($consoleBytes)
    Write-NewBytes $transcriptPath $consoleBytes
    $consoleArtifact = Get-Artifact $consolePath
    $transcriptArtifact = Get-Artifact $transcriptPath
    Require ($consoleArtifact.bytes -eq $transcriptArtifact.bytes -and $consoleArtifact.sha256 -ceq $transcriptArtifact.sha256) 'console/transcript 原始字节绑定不一致'
    $sentinelCount = ([regex]::Matches($consoleText, 'T58_XSIM_SENTINEL=PASS')).Count
    $progressCount = ([regex]::Matches($consoleText, '(?m)^PROGRESS T58 outputs=\d+/6656\s*$')).Count
    $passCount = ([regex]::Matches($consoleText, '(?m)^PASS T58 outputs=6656 raw=6656(?:\s|$)')).Count
    $finishCount = ([regex]::Matches($consoleText, '(?m)^T58_XSIM_TCL_RUN_ALL_RETURNED\s*$')).Count
    Require ($runtimeExit -eq 0) ("Vivado/XSim exit code 非0：" + $runtimeExit)
    Require ($sentinelCount -eq 1 -and $progressCount -eq 256 -and $passCount -eq 1 -and $finishCount -eq 1) '仿真 console sentinel/progress/PASS/run-all-return 计数不符'
    $run02GoldenPath = Join-Path (Join-Path $Run02 'fixture') 'golden.bin'
    $golden = [IO.File]::ReadAllBytes($run02GoldenPath)
    $rawPath = Join-Path $Run03 'observed_raw.bin'
    $int8Path = Join-Path $Run03 'observed_output.bin'
    Require ((Test-Path -LiteralPath $rawPath -PathType Leaf) -and (Test-Path -LiteralPath $int8Path -PathType Leaf)) '仿真输出文件缺失'
    $observedRaw = [IO.File]::ReadAllBytes($rawPath)
    $observedInt8 = [IO.File]::ReadAllBytes($int8Path)
    $expectedRaw = New-Object byte[] 26624
    $expectedInt8 = New-Object byte[] 6656
    [Array]::Copy($golden, 0, $expectedRaw, 0, $expectedRaw.Length)
    [Array]::Copy($golden, 26624, $expectedInt8, 0, $expectedInt8.Length)
    Require ($observedRaw.Length -eq 26624 -and [Convert]::ToBase64String($observedRaw) -ceq [Convert]::ToBase64String($expectedRaw)) 'run03 raw INT32 与 run02 golden 逐字节比较失败'
    Require ($observedInt8.Length -eq 6656 -and [Convert]::ToBase64String($observedInt8) -ceq [Convert]::ToBase64String($expectedInt8)) 'run03 INT8 与冻结 D2/T23 golden 逐字节比较失败'
    Require ([int]$cpuVerify.result.output_counts.d2_t23_matches -eq 6656) '冻结 D2/T23 CPU 参考计数不符'
    $projectDir = Join-Path $Run03 'isolated_project'
    $copyMap = @(@{ name = 'compile.bat'; dest = 'compile.generated.bat' }, @{ name = 'elaborate.bat'; dest = 'elaborate.generated.bat' }, @{ name = 'simulate.bat'; dest = 'simulate.generated.bat' })
    foreach ($entry in $copyMap) {
        $matches = @(Get-ChildItem -LiteralPath $projectDir -Filter $entry.name -File -Recurse -ErrorAction SilentlyContinue)
        Require ($matches.Count -eq 1) ("未找到唯一生成脚本：" + $entry.name)
        $destination = Join-Path $Run03 $entry.dest
        Require (-not (Test-Path -LiteralPath $destination)) ("脚本快照已存在：" + $destination)
        [IO.File]::Copy($matches[0].FullName, $destination, $false)
    }
    $vivadoJournalPath = Join-Path $Run03 'vivado.jou'
    $vivadoLogPath = Join-Path $Run03 'vivado.log'
    Require ((Test-Path -LiteralPath $vivadoJournalPath -PathType Leaf) -and
             (Test-Path -LiteralPath $vivadoLogPath -PathType Leaf)) 'Vivado 工作目录日志 vivado.jou/vivado.log 缺失'
    $vivadoJournalArtifact = Get-Artifact $vivadoJournalPath
    $vivadoLogArtifact = Get-Artifact $vivadoLogPath
    $runtimeProcesses = [ordered]@{ launcher_pid = [int]$proc.Id; observed_processes = @($seen.Values); before_vivado = $processesPreVivado; after = $allProcessesAfter }
    Write-NewJson (Join-Path $Run03 'runtime_processes.json') $runtimeProcesses
    $projectScripts = @(Get-DirectoryArtifacts $projectDir)
    $summary = [ordered]@{
        schema = 'GestureForge-S2A-T58-isolated-sim-runtime-summary-v1'
        task_id = 'S2A-T58'
        run_id = 'run03'
        status = 'PASS_SIMULATION_DATA_ONLY'
        simulation = 'PASS'
        head = @{ at_start = $headBefore; at_end = $headAfter; unchanged_during_run = $true }
        source_binding_sha256 = (Get-Sha256 $bindingPath)
        vivado_executable = $vivado
        invocation = @{ command_line = $arguments; launcher_pid = [int]$proc.Id; exit_code = $runtimeExit }
        console = $consoleArtifact
        console_stderr = Get-Artifact (Join-Path $Run03 'vivado_console.stderr.bin')
        vivado_journal = $vivadoJournalArtifact
        vivado_log = $vivadoLogArtifact
        transcript_mirror = $transcriptArtifact
        console_transcript_byte_identical = $true
        sentinel_count = $sentinelCount
        progress_checkpoint_count = $progressCount
        pass_count = $passCount
        finish_after_tb_finish_marker_count = $finishCount
        testbench_finish_statement_count = [int]$currentTb.finish_count
        observed_raw = Get-Artifact $rawPath
        observed_int8 = Get-Artifact $int8Path
        raw_equals_run02_golden = $true
        int8_equals_frozen_D2_T23_golden = $true
        D2_T23_reference_count = [int]$cpuVerify.result.output_counts.d2_t23_matches
        CPU_reference_status = [string]$cpuVerify.result.result
        run02_prepared_content_verify_exit_code = [int]$cpuVerify.exit_code
        run02_prepared_content_verify_stdout = $cpuVerify.stdout
        run02_prepared_content_verify_stderr = $cpuVerify.stderr
        generated_project_scripts = $projectScripts
        generated_script_snapshots = @((Get-Artifact (Join-Path $Run03 'compile.generated.bat')),(Get-Artifact (Join-Path $Run03 'elaborate.generated.bat')),(Get-Artifact (Join-Path $Run03 'simulate.generated.bat')))
        process_artifacts = Get-Artifact (Join-Path $Run03 'runtime_processes.json')
        target_xpr = @{ before = $xprBefore; after = $xprAfter; unchanged = $true }
    }
    Write-NewJson (Join-Path $Run03 'runtime_summary.json') $summary
    $postRunFiles = @((Get-ExpectedRun03InventoryFiles) + @(
        'isolated_run_inventory.json',
        'runtime_prelaunch_content_verify.stdout.json',
        'runtime_prelaunch_content_verify.stderr.bin',
        'vivado_console.stdout.bin',
        'vivado_console.stderr.bin',
        'xsim_console_transcript.raw.bin',
        'runtime_processes.json',
        'runtime_summary.json',
        'observed_raw.bin',
        'observed_output.bin',
        'compile.generated.bat',
        'elaborate.generated.bat',
        'simulate.generated.bat',
        'vivado.jou',
        'vivado.log'
    ))
    $preRecordGate = Assert-T58SiblingDirectoryGate $postRunFiles @('isolated_project')
    $gateRecord = [ordered]@{
        schema = 'GestureForge-S2A-T58-post-run-directory-gate-v1'
        status = 'PASS_BEFORE_GATE_RECORD'
        gate = $preRecordGate
        root_level_runtime_artifacts = @(
            (Get-Artifact $vivadoJournalPath),
            (Get-Artifact $vivadoLogPath),
            (Get-Artifact (Join-Path $Run03 'vivado_console.stdout.bin')),
            (Get-Artifact (Join-Path $Run03 'vivado_console.stderr.bin')),
            (Get-Artifact $transcriptPath),
            (Get-Artifact $rawPath),
            (Get-Artifact $int8Path)
        )
        isolated_project_file_count = $projectScripts.Count
        isolated_project_files = $projectScripts
        run02_summary_sha256 = $currentBinding.summary.sha256
        run02_project_binding_sha256 = $currentBinding.project_binding.sha256
        run03_binding_sha256 = Get-Sha256 $bindingPath
    }
    Write-NewJson (Join-Path $Run03 'runtime_gate.json') $gateRecord
    $finalRunFiles = @($postRunFiles + 'runtime_gate.json')
    $finalRunGate = Assert-T58SiblingDirectoryGate $finalRunFiles @('isolated_project')
    Write-Output (ConvertTo-Json -InputObject ([ordered]@{
        status = 'PASS_POST_RUN_ISOLATED_DIRECTORY_GATE'
        gate_record = Get-Artifact (Join-Path $Run03 'runtime_gate.json')
        final_gate = $finalRunGate
        process_check_after_gate = @(Get-ProcessSnapshot)
        simulation = 'PASS'
    }) -Depth 20)
    Write-Output (ConvertTo-Json -InputObject $summary -Depth 20)
}

try {
    Require (([IO.Path]::GetFullPath((Get-Location).Path)).Equals($RepoRoot, [StringComparison]::OrdinalIgnoreCase)) '必须从固定仓库根目录运行'
    Assert-NoReparseChain $RepoRoot
    if ($Mode -eq 'DryRun') {
        Invoke-DryRun
    }
    elseif ($Mode -eq 'Run') {
        Invoke-Run
    }
    else {
        Invoke-AuditInventory
    }
}
catch {
    if ($Mode -eq 'Run' -and (Test-Path -LiteralPath $Run03 -PathType Container) -and -not (Test-Path -LiteralPath (Join-Path $Run03 'NON_ACCEPTANCE_run03.json'))) {
        try {
            Write-NewJson (Join-Path $Run03 'NON_ACCEPTANCE_run03.json') ([ordered]@{
                schema = 'GestureForge-S2A-T58-isolated-sim-nonacceptance-v1'
                status = 'NON_ACCEPTANCE'
                mode = $Mode
                error = [string]$_.Exception.Message
                time_local = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss zzz')
                process_observation = Get-ProcessSnapshot
                note = '失败侧件不执行进程控制；若已启动的进程仍在运行，由调用者观察后处理。'
            })
        }
        catch { [Console]::Error.WriteLine(('失败侧件也未能写入：' + $_.Exception.Message)) }
    }
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
