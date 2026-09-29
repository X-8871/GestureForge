[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$RepoRoot = 'D:\FPGA_Competition'
$EvidenceRoot = Join-Path $RepoRoot 'report\evidence\S2A-T58'
$Run02 = Join-Path $EvidenceRoot 'run02'
$Run06 = Join-Path $EvidenceRoot 'run06'
$CaptureRoot = Join-Path $Run06 'simulation_logs'
$SimSource = Join-Path $Run06 'isolated_project\T58_Row22_Attempt06\T58_Row22_Attempt06.sim\sim_1\behav\xsim\simulate.log'
$XvlogSource = Join-Path $Run06 'isolated_project\T58_Row22_Attempt06\T58_Row22_Attempt06.sim\sim_1\behav\xsim\xvlog.log'
$SimCapture = Join-Path $CaptureRoot 'simulate.log'
$XvlogCapture = Join-Path $CaptureRoot 'xvlog.log'
$ResultPath = Join-Path $Run06 'simulation_result.json'
$InventoryPath = Join-Path $Run06 'simulation_inventory.json'
$DryrunPlan = Join-Path $Run06 'dryrun_plan.json'
$DryrunSummary = Join-Path $Run06 'dryrun_summary.json'
$BindingPath = Join-Path $Run06 'isolated_sim_binding.json'
$PreparedInventory = Join-Path $Run06 'isolated_run_inventory.json'
$ProjectTcl = Join-Path $Run06 'run_project_sim.tcl'
$XsimTcl = Join-Path $Run06 'xsim_run.tcl'
$TbPath = Join-Path $RepoRoot 'sim\tb_s2a_conv_layer35_row22_attempt06.sv'
$LauncherPath = Join-Path $RepoRoot 'verification\run_s2a_t58_row22_attempt06_isolated_sim.ps1'
$PriorAttemptSources = [ordered]@{
    'sim/tb_s2a_conv_layer35_row22_attempt04.sv' = @{ path = (Join-Path $RepoRoot 'sim\tb_s2a_conv_layer35_row22_attempt04.sv'); bytes = 37642; sha256 = '33acf2b5181e2b5fa1b26dd58bc58448719b4bf17cd07a736be93238d8257125' }
    'verification/run_s2a_t58_row22_attempt04_isolated_sim.ps1' = @{ path = (Join-Path $RepoRoot 'verification\run_s2a_t58_row22_attempt04_isolated_sim.ps1'); bytes = 28815; sha256 = '6b8da9580cf587fdea3a94f94d6e0851a8105c6a189fdf006d44677608f1bda3' }
    'sim/tb_s2a_conv_layer35_row22_attempt05.sv' = @{ path = (Join-Path $RepoRoot 'sim\tb_s2a_conv_layer35_row22_attempt05.sv'); bytes = 37642; sha256 = '9b5c3c8c26b856e2fea6c061ba670d15eabaddc866eda7ee28be38d194138513' }
    'verification/run_s2a_t58_row22_attempt05_isolated_sim.ps1' = @{ path = (Join-Path $RepoRoot 'verification\run_s2a_t58_row22_attempt05_isolated_sim.ps1'); bytes = 29602; sha256 = '94b45242ed322ed0988229b1c6834a0c2291048b7ec7dc77fa48c90a1b14e0e8' }
    'sim/tb_s2a_conv_layer35_row22_attempt06.sv' = @{ path = $TbPath; bytes = 37642; sha256 = 'b1f53f31d0a061b80038ca60225f84b0c639da97a33cc9e232929b47210f5c0a' }
    'verification/run_s2a_t58_row22_attempt06_isolated_sim.ps1' = @{ path = $LauncherPath; bytes = 36387; sha256 = '7269d3c948eb0a7cbeeb76c6c16103fa8ff4e00a2cd1ba699b9e0936b6363c40' }
}
$GoldenPath = Join-Path $Run02 'fixture\golden.bin'
$RawPath = Join-Path $Run06 'observed_raw.bin'
$OutputPath = Join-Path $Run06 'observed_output.bin'
$TargetXpr = Join-Path $RepoRoot 'vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr'
$BaseHead = 'a8d19fbdc3389682b888f2d8add2cdd77af4503c'
$ExpectedHashes = [ordered]@{
    'dryrun_plan.json' = '5526924c1ecefcecc3e51eb15bee2ff31e536c90e730d0f85e2d6cefb41fc4e6'
    'dryrun_summary.json' = '60001abf623bc7004e2b2c1305f3c3dad81a98c790d5c0fdf6f1a08c6a673bc5'
    'isolated_sim_binding.json' = 'f85bc71bd2b2b56d662056dcaed079ddb9582facae5a67714f60436ef6273067'
    'isolated_run_inventory.json' = '4a7497861fb8d1697114890fdc73ac8808b7f4d26f8b6b47fa70db39c4053fe2'
    'run_project_sim.tcl' = 'f932d9a6b3ca920364b2378396fa9248224e3ed8d0f7dc2d4f5c5138c236aa0b'
    'xsim_run.tcl' = '1968c19a24629b2182b6063c563a4f0f632397621057ae05de14e02e277f868b'
}
$ExpectedTbSha = 'b1f53f31d0a061b80038ca60225f84b0c639da97a33cc9e232929b47210f5c0a'
$ExpectedLauncherSha = '7269d3c948eb0a7cbeeb76c6c16103fa8ff4e00a2cd1ba699b9e0936b6363c40'
$ExpectedXprSha = '9e637bb8a31c8c74cdb703d632282a020875f5623893665719c1bbb5035be1ec'
$ExpectedGoldenSha = '0892e785cfb724eb10c9fd39b5bdba2836fa4eb9c0374dd31e5fd2aa7ce50271'
$ExpectedRawBytes = 26624
$ExpectedOutputBytes = 6656
$ExpectedGoldenBytes = 33280
$ProcessNames = '^(vivado|vivado_lab|xsim|xsimk|xelab|xvlog|xvhdl|xsct|hw_server)(\.exe)?$'

function Require([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
}

function Get-Sha([string]$Path) {
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-BytesSha([byte[]]$Bytes) {
    [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)).ToLowerInvariant()
}

function Get-Artifact([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force
    Require ($item -is [IO.FileInfo]) ('要求普通文件：' + $Path)
    [ordered]@{ path = [IO.Path]::GetFullPath($Path); bytes = [int64]$item.Length; sha256 = Get-Sha $Path }
}

function Read-Json([string]$Path) {
    Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
}

function Write-NewJson([string]$Path, [object]$Value) {
    Require (-not (Test-Path -LiteralPath $Path)) ('拒绝覆盖：' + $Path)
    $text = (ConvertTo-Json -InputObject $Value -Depth 64) + "`n"
    $bytes = [Text.UTF8Encoding]::new($false).GetBytes($text)
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
}

function Assert-RepoFile([string]$Path) {
    $full = [IO.Path]::GetFullPath($Path)
    $boundary = [IO.Path]::GetFullPath($RepoRoot).TrimEnd([char]92)
    Require ($full.StartsWith($boundary + '\', [StringComparison]::OrdinalIgnoreCase)) ('源文件路径越界：' + $full)
    $cursor = $full
    while ($true) {
        $item = Get-Item -LiteralPath $cursor -Force
        Require (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) ('拒绝 reparse 路径：' + $cursor)
        if ($cursor.Equals($boundary, [StringComparison]::OrdinalIgnoreCase)) { break }
        $parent = [IO.Directory]::GetParent($cursor)
        Require ($null -ne $parent) ('源文件父目录缺失：' + $full)
        $cursor = $parent.FullName
    }
    $item = Get-Item -LiteralPath $full -Force
    Require ($item -is [IO.FileInfo]) ('要求普通文件：' + $full)
    $full
}

function Assert-Hash([string]$Path, [string]$ExpectedSha, [string]$Label, [int64]$ExpectedBytes = -1) {
    [void](Assert-RepoFile $Path)
    $artifact = Get-Artifact $Path
    Require ($artifact.sha256 -ceq $ExpectedSha.ToLowerInvariant()) ($Label + ' SHA 不符：' + $artifact.sha256)
    if ($ExpectedBytes -ge 0) { Require ($artifact.bytes -eq $ExpectedBytes) ($Label + ' 字节数不符：' + $artifact.bytes) }
    $artifact
}

function Get-ProcessSnapshot {
    @(Get-CimInstance -ClassName Win32_Process | Where-Object { $_.Name -match $ProcessNames } | Sort-Object ProcessId | ForEach-Object { [ordered]@{ name = $_.Name; pid = [int]$_.ProcessId; command_line = $_.CommandLine } })
}

function Copy-NewFile([string]$Source, [string]$Destination) {
    Require (-not (Test-Path -LiteralPath $Destination)) ('拒绝覆盖日志副本：' + $Destination)
    $inputStream = [IO.File]::Open($Source, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    $outputStream = [IO.File]::Open($Destination, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $inputStream.CopyTo($outputStream); $outputStream.Flush($true) }
    finally { $outputStream.Dispose(); $inputStream.Dispose() }
}

function Compare-Bytes([byte[]]$Observed, [byte[]]$Golden, [int]$GoldenOffset) {
    $mismatchCount = 0
    for ($index = 0; $index -lt $Observed.Length; $index++) {
        if ($Observed[$index] -ne $Golden[$GoldenOffset + $index]) { $mismatchCount++ }
    }
    $mismatchCount
}

function Get-ProgressValues([string]$Text) {
    $pattern = '(?m)^PROGRESS T58 outputs=(\d+)/6656\r?$'
    $progressMatches = [regex]::Matches($Text, $pattern)
    $occurrences = [regex]::Matches($Text, 'PROGRESS T58 outputs=').Count
    Require ($progressMatches.Count -eq 256 -and $occurrences -eq $progressMatches.Count) ('progress 记录数量/形状不符：matches=' + $progressMatches.Count + '; occurrences=' + $occurrences)
    $values = [Collections.Generic.List[int]]::new()
    for ($index = 0; $index -lt $progressMatches.Count; $index++) {
        $value = [int]$progressMatches[$index].Groups[1].Value
        Require ($value -eq (($index + 1) * 26)) ('progress 顺序或值不符，序号=' + ($index + 1) + '; 值=' + $value)
        $values.Add($value)
    }
    @($values.ToArray())
}

function Get-LogContract([string]$SimText, [string]$CompileText) {
    $passMatches = [regex]::Matches($SimText, '(?m)^PASS T58 outputs=6656 raw=6656(?: .*)?\r?$')
    $sentinelMatches = [regex]::Matches($SimText, '(?m)^T58_XSIM_SENTINEL=PASS_RUN06\r?$')
    $finishMatches = [regex]::Matches($SimText, '(?m)^\$finish called at time : (\d+) ns : File ".*tb_s2a_conv_layer35_row22_attempt06\.sv" Line 517\r?$')
    Require ($passMatches.Count -eq 1) ('T58 PASS 行数量不符：' + $passMatches.Count)
    Require ($sentinelMatches.Count -eq 1) ('PASS_RUN06 sentinel 数量不符：' + $sentinelMatches.Count)
    Require ($finishMatches.Count -eq 1) ('$finish 行数量不符：' + $finishMatches.Count)
    Require ([int64]$finishMatches[0].Groups[1].Value -eq 2971541060) ('$finish 时间不符：' + $finishMatches[0].Groups[1].Value)
    $progress = Get-ProgressValues $SimText
    $errorPattern = '(?im)^\s*(?:ERROR|FATAL)(?:\s|:|\[)'
    $errorMatches = [regex]::Matches($SimText + "`n" + $CompileText, $errorPattern)
    Require ($errorMatches.Count -eq 0) ('simulate/xvlog 日志包含 ERROR/FATAL 行：' + $errorMatches.Count)
    $runAllMarker = 'T58_XSIM_TCL_RUN_ALL_RETURNED'
    Require (-not $SimText.Contains($runAllMarker) -and -not $CompileText.Contains($runAllMarker)) '发现不应出现的 run-all marker'
    [ordered]@{
        progress_count = $progress.Count
        progress_values = $progress
        pass_line_count = $passMatches.Count
        pass_line = $passMatches[0].Value.TrimEnd("`r")
        sentinel_count = $sentinelMatches.Count
        sentinel = $sentinelMatches[0].Value.TrimEnd("`r")
        finish_count = $finishMatches.Count
        finish_time_ns = [int64]$finishMatches[0].Groups[1].Value
        error_fatal_line_count = $errorMatches.Count
        xsim_run_all_marker = $runAllMarker
        xsim_run_all_marker_present = $false
    }
}

function Add-InventoryArtifact([Collections.Generic.List[object]]$List, [string]$RelativePath, [string]$Path) {
    $artifact = Get-Artifact $Path
    $List.Add([ordered]@{ relative_path = $RelativePath; artifact = $artifact })
}

try {
    Require ([IO.Path]::GetFullPath((Get-Location).Path).Equals($RepoRoot, [StringComparison]::OrdinalIgnoreCase)) '必须从仓库根目录执行'
    Require ((& git -C $RepoRoot rev-parse HEAD).Trim().ToLowerInvariant() -ceq $BaseHead) 'HEAD 与 run06 冻结基线不符'

    $scriptTokens = $null
    $scriptParseErrors = $null
    $scriptAst = [System.Management.Automation.Language.Parser]::ParseFile($PSCommandPath, [ref]$scriptTokens, [ref]$scriptParseErrors)
    Require ($scriptParseErrors.Count -eq 0) 'finalizer PowerShell AST 解析失败'
    $forbiddenCommands = @('Start-Process', 'Start-Job', 'Invoke-Expression', 'vivado', 'vivado.exe', 'xsim', 'xsim.exe', 'xvlog', 'xvlog.exe', 'xelab', 'xelab.exe')
    $commandNodes = @($scriptAst.FindAll({ param($node) $node -is [System.Management.Automation.Language.CommandAst] }, $true))
    foreach ($commandNode in $commandNodes) {
        $commandName = $commandNode.GetCommandName()
        if ($null -ne $commandName) { Require ($forbiddenCommands -notcontains $commandName.ToLowerInvariant()) ('finalizer 含有禁止的外部执行命令：' + $commandName) }
    }
    $pathVariableNames = @('RepoRoot', 'EvidenceRoot', 'Run02', 'Run06', 'CaptureRoot', 'SimSource', 'XvlogSource', 'SimCapture', 'XvlogCapture', 'ResultPath', 'InventoryPath', 'DryrunPlan', 'DryrunSummary', 'BindingPath', 'PreparedInventory', 'ProjectTcl', 'XsimTcl', 'TbPath', 'LauncherPath', 'GoldenPath', 'RawPath', 'OutputPath', 'TargetXpr')
    $pathAssignmentCounts = @{}
    $assignmentNodes = @($scriptAst.FindAll({ param($node) $node -is [System.Management.Automation.Language.AssignmentStatementAst] }, $true))
    foreach ($assignmentNode in $assignmentNodes) {
        if ($assignmentNode.Left -is [System.Management.Automation.Language.VariableExpressionAst]) {
            $assignedName = $assignmentNode.Left.VariablePath.UserPath
            if ($pathVariableNames -contains $assignedName) {
                $normalizedName = $assignedName.ToLowerInvariant()
                if (-not $pathAssignmentCounts.ContainsKey($normalizedName)) { $pathAssignmentCounts[$normalizedName] = 0 }
                $pathAssignmentCounts[$normalizedName]++
            }
        }
    }
    foreach ($pathVariableName in $pathVariableNames) {
        $normalizedName = $pathVariableName.ToLowerInvariant()
        Require ($pathAssignmentCounts.ContainsKey($normalizedName) -and $pathAssignmentCounts[$normalizedName] -eq 1) ('' + $pathVariableName + ' 路径变量存在重复或缺失赋值')
    }

    Require (-not (Test-Path -LiteralPath $CaptureRoot) -and -not (Test-Path -LiteralPath $ResultPath) -and -not (Test-Path -LiteralPath $InventoryPath)) '发现已有 simulation capture/result/inventory，拒绝覆盖'
    $processBefore = @(Get-ProcessSnapshot)
    Require ($processBefore.Count -eq 0) '后处理开始前存在 Vivado/XSim 进程'

    $frozenArtifacts = [ordered]@{}
    foreach ($name in $ExpectedHashes.Keys) {
        $path = Join-Path $Run06 $name
        $frozenArtifacts[$name] = Assert-Hash $path $ExpectedHashes[$name] ('run06 frozen ' + $name)
    }
    $tbArtifact = Assert-Hash $TbPath $ExpectedTbSha 'attempt06 TB'
    $launcherArtifact = Assert-Hash $LauncherPath $ExpectedLauncherSha 'attempt06 launcher'
    $attemptSourceArtifacts = [Collections.Generic.List[object]]::new()
    foreach ($sourceName in $PriorAttemptSources.Keys) {
        $priorSource = $PriorAttemptSources[$sourceName]
        $priorArtifact = Assert-Hash $priorSource.path $priorSource.sha256 ('frozen attempt source ' + $sourceName) $priorSource.bytes
        $attemptSourceArtifacts.Add([ordered]@{ name = $sourceName; artifact = $priorArtifact })
    }
    $binding = Read-Json $BindingPath
    Require ($binding.schema -ceq 'GestureForge-S2A-T58-attempt06-binding-v1' -and $binding.task_id -ceq 'S2A-T58' -and $binding.run_id -ceq 'run06' -and $binding.status -ceq 'PREPARED_NOT_SIMULATED' -and $binding.simulation -ceq 'NOT_RUN') 'run06 frozen binding identity/status mismatch'
    Require ($binding.base_head -ceq $BaseHead -and $binding.tb.sha256 -ceq $ExpectedTbSha -and $binding.launcher.sha256 -ceq $ExpectedLauncherSha) 'run06 frozen binding HEAD/TB/launcher mismatch'
    Require ($binding.tb.path -ceq $tbArtifact.path -and [int64]$binding.tb.bytes -eq $tbArtifact.bytes -and $binding.launcher.path -ceq $launcherArtifact.path -and [int64]$binding.launcher.bytes -eq $launcherArtifact.bytes) 'run06 frozen binding path/size mismatch'
    Require ($binding.target_xpr.path -ceq $TargetXpr -and $binding.target_xpr.sha256 -ceq $ExpectedXprSha -and $binding.target_xpr.opened -eq $false -and $binding.target_xpr.modified -eq $false) 'target XPR binding mismatch'
    [void](Assert-Hash $TargetXpr $ExpectedXprSha 'target XPR' 23010)

    $dryrunSummaryRecord = Read-Json $DryrunSummary
    Require ($dryrunSummaryRecord.status -ceq 'DRYRUN_READY_NOT_SIMULATED' -and $dryrunSummaryRecord.simulation -ceq 'NOT_RUN' -and $dryrunSummaryRecord.current_head -ceq $BaseHead) 'dryrun summary 必须保持原始 NOT_RUN 状态'
    Require ($binding.project_tcl.sha256 -ceq $ExpectedHashes['run_project_sim.tcl'] -and $binding.xsim_tcl.sha256 -ceq $ExpectedHashes['xsim_run.tcl']) 'run06 Tcl binding mismatch'
    Require ($binding.project_tcl.path -ceq [IO.Path]::GetFullPath($ProjectTcl) -and $binding.xsim_tcl.path -ceq [IO.Path]::GetFullPath($XsimTcl)) 'run06 Tcl binding path mismatch'

    $sourceRecords = [Collections.Generic.List[object]]::new()
    foreach ($sourceProperty in $binding.sources.PSObject.Properties) {
        $sourcePath = [string]$sourceProperty.Value.path
        $sourceArtifact = Assert-Hash $sourcePath ([string]$sourceProperty.Value.sha256) ('bound source ' + $sourceProperty.Name) ([int64]$sourceProperty.Value.bytes)
        $sourceRecords.Add([ordered]@{ name = $sourceProperty.Name; artifact = $sourceArtifact })
    }
    Require ($sourceRecords.Count -ge 20) ('run06 binding source 数量异常：' + $sourceRecords.Count)
    $goldenArtifact = Assert-Hash $GoldenPath $ExpectedGoldenSha 'run02 golden' $ExpectedGoldenBytes
    Require ($binding.sources.'report/evidence/S2A-T58/run02/fixture/golden.bin'.sha256 -ceq $goldenArtifact.sha256) 'golden 未在 run06 sources 中绑定'

    $preparedInventoryArtifact = Assert-Hash $PreparedInventory $ExpectedHashes['isolated_run_inventory.json'] 'original prepare inventory'
    $preparedInventoryRecord = Read-Json $PreparedInventory
    Require ($preparedInventoryRecord.run_id -ceq 'run06' -and $preparedInventoryRecord.simulation -ceq 'NOT_RUN') '原 isolated_run_inventory 内容变化'

    $simSourceArtifact = Get-Artifact (Assert-RepoFile $SimSource)
    $xvlogSourceArtifact = Get-Artifact (Assert-RepoFile $XvlogSource)
    Require ($simSourceArtifact.bytes -gt 0 -and $xvlogSourceArtifact.bytes -gt 0) '源 simulate/xvlog 日志为空'
    $rawBytes = [IO.File]::ReadAllBytes((Assert-RepoFile $RawPath))
    $outputBytes = [IO.File]::ReadAllBytes((Assert-RepoFile $OutputPath))
    Require ($rawBytes.Length -eq $ExpectedRawBytes) ('observed_raw 长度错误：' + $rawBytes.Length)
    Require ($outputBytes.Length -eq $ExpectedOutputBytes) ('observed_output 长度错误：' + $outputBytes.Length)
    $goldenBytes = [IO.File]::ReadAllBytes((Assert-RepoFile $GoldenPath))
    Require ($goldenBytes.Length -eq $ExpectedGoldenBytes) ('golden 长度错误：' + $goldenBytes.Length)
    $rawMismatchCount = Compare-Bytes $rawBytes $goldenBytes 0
    $outputMismatchCount = Compare-Bytes $outputBytes $goldenBytes ($goldenBytes.Length - $ExpectedOutputBytes)

    [void][IO.Directory]::CreateDirectory($CaptureRoot)
    Copy-NewFile $SimSource $SimCapture
    Copy-NewFile $XvlogSource $XvlogCapture
    $simCaptureArtifact = Get-Artifact (Assert-RepoFile $SimCapture)
    $xvlogCaptureArtifact = Get-Artifact (Assert-RepoFile $XvlogCapture)
    Require ($simCaptureArtifact.bytes -eq $simSourceArtifact.bytes -and $simCaptureArtifact.sha256 -ceq $simSourceArtifact.sha256) 'simulate.log 副本与源不一致'
    Require ($xvlogCaptureArtifact.bytes -eq $xvlogSourceArtifact.bytes -and $xvlogCaptureArtifact.sha256 -ceq $xvlogSourceArtifact.sha256) 'xvlog.log 副本与源不一致'
    $simText = [Text.UTF8Encoding]::new($false, $true).GetString([IO.File]::ReadAllBytes($SimCapture))
    $xvlogText = [Text.UTF8Encoding]::new($false, $true).GetString([IO.File]::ReadAllBytes($XvlogCapture))
    $logContract = Get-LogContract $simText $xvlogText

    Require ($rawMismatchCount -eq 0) ('raw 与 golden 首段 mismatch=' + $rawMismatchCount)
    Require ($outputMismatchCount -eq 0) ('INT8 与 golden 末段 mismatch=' + $outputMismatchCount)
    Require ((Get-Sha $RawPath) -ceq (Get-BytesSha $rawBytes) -and (Get-Sha $OutputPath) -ceq (Get-BytesSha $outputBytes)) 'observed 输出在比对期间变化'
    foreach ($sourceProperty in $binding.sources.PSObject.Properties) {
        [void](Assert-Hash ([string]$sourceProperty.Value.path) ([string]$sourceProperty.Value.sha256) ('postcheck bound source ' + $sourceProperty.Name) ([int64]$sourceProperty.Value.bytes))
    }
    $processAfter = @(Get-ProcessSnapshot)
    Require ($processAfter.Count -eq 0) '后处理结束前检测到 Vivado/XSim 进程'

    $verifierArtifact = Get-Artifact (Assert-RepoFile $PSCommandPath)
    $result = [ordered]@{
        schema = 'GestureForge-S2A-T58-run06-simulation-result-v1'
        task_id = 'S2A-T58'
        run_id = 'run06'
        status = 'PASS_SIMULATION_DATA_ONLY'
        scope = 'layer35 row22 local PL simulation data; not a full layer/network acceptance'
        simulation = 'COMPLETED_WITH_PASS_SENTINEL_AND_FINISH'
        base_head = $BaseHead
        finalizer_attempt_number = 2
        prior_finalizer_attempts = @(@{ attempt = 1; status = 'FAILED_BEFORE_CAPTURE'; command = 'pwsh.exe -NoLogo -NoProfile -File D:\FPGA_Competition\verification\verify_s2a_t58_row22_run06_simulation.ps1'; exit_code = 1; error = 'Cannot find path System.Collections.Specialized.OrderedDictionary because it does not exist.'; root_cause = 'PowerShell case-insensitive variable name collision: $preparedInventory record overwrote the $PreparedInventory path before Read-Json.'; capture_files_created = $false; prior_run06_files_changed = $false })
        frozen_prepare = @{ status = $dryrunSummaryRecord.status; simulation = $dryrunSummaryRecord.simulation; dryrun_summary_sha256 = $ExpectedHashes['dryrun_summary.json']; binding_sha256 = $ExpectedHashes['isolated_sim_binding.json']; original_inventory_sha256 = $ExpectedHashes['isolated_run_inventory.json'] }
        verifier = $verifierArtifact
        static_bindings = @{ attempt06_tb = $tbArtifact; attempt06_runner = $launcherArtifact; preserved_attempt04_05_06_sources = @($attemptSourceArtifacts.ToArray()); target_xpr = (Get-Artifact $TargetXpr); bound_source_count = $sourceRecords.Count; bound_sources = @($sourceRecords.ToArray()) }
        logs = @{ simulate_source = $simSourceArtifact; simulate_copy = $simCaptureArtifact; xvlog_source = $xvlogSourceArtifact; xvlog_copy = $xvlogCaptureArtifact; contract = $logContract; xvlog_exit_code_captured = $false }
        outputs = @{
            raw_int32 = @{ artifact = Get-Artifact $RawPath; expected_bytes = $ExpectedRawBytes; golden_segment = 'first 26,624 bytes'; golden_segment_sha256 = Get-BytesSha ([byte[]]$goldenBytes[0..($ExpectedRawBytes - 1)]); mismatch_count = $rawMismatchCount }
            int8 = @{ artifact = Get-Artifact $OutputPath; expected_bytes = $ExpectedOutputBytes; golden_segment = 'last 6,656 bytes'; golden_segment_sha256 = Get-BytesSha ([byte[]]$goldenBytes[($goldenBytes.Length - $ExpectedOutputBytes)..($goldenBytes.Length - 1)]); mismatch_count = $outputMismatchCount }
            golden = $goldenArtifact
        }
        mcp_observations = @{
            evidence_source = '本任务卡提供的会话观察；run06 中没有原始 MCP 收据文件'
            check_connection_before_project_create = 'SUCCEEDED'
            get_project_info_independent_instance = 'NO_PROJECT'
            run_tcl_source_run_project_sim = @{ outcome = 'CLIENT_TIMEOUT'; timeout_seconds = 300; later_simulate_log_contains_complete_pass_and_finish = $true }
            post_run_check_connection = @{ outcome = 'FAILED'; error = 'WinError 1225'; timing = 'Vivado process had exited' }
            xsim_run_tcl_separately_sourced = $false
            xsim_run_all_marker = $logContract.xsim_run_all_marker
            xsim_run_all_marker_present = $logContract.xsim_run_all_marker_present
        }
        process_before = $processBefore
        process_after = $processAfter
        interpretation_limits = @('run_project_sim.tcl MCP client call timed out after 300 seconds even though the later captured simulate.log completed with PASS and $finish.', 'xsim_run.tcl was not separately sourced; its T58_XSIM_TCL_RUN_ALL_RETURNED marker is absent, so no claim is made that this marker executed.', 'This is simulation data-only evidence. It does not claim full layer/network acceptance, board validation, G3, G4, or G5.')
    }
    Write-NewJson $ResultPath $result

    $inventoryArtifacts = [Collections.Generic.List[object]]::new()
    foreach ($name in $ExpectedHashes.Keys) { Add-InventoryArtifact $inventoryArtifacts ('report/evidence/S2A-T58/run06/' + $name) (Join-Path $Run06 $name) }
    Add-InventoryArtifact $inventoryArtifacts 'report/evidence/S2A-T58/run06/observed_raw.bin' $RawPath
    Add-InventoryArtifact $inventoryArtifacts 'report/evidence/S2A-T58/run06/observed_output.bin' $OutputPath
    Add-InventoryArtifact $inventoryArtifacts 'report/evidence/S2A-T58/run06/simulation_logs/simulate.log' $SimCapture
    Add-InventoryArtifact $inventoryArtifacts 'report/evidence/S2A-T58/run06/simulation_logs/xvlog.log' $XvlogCapture
    Add-InventoryArtifact $inventoryArtifacts 'report/evidence/S2A-T58/run06/simulation_result.json' $ResultPath
    Add-InventoryArtifact $inventoryArtifacts 'sim/tb_s2a_conv_layer35_row22_attempt06.sv' $TbPath
    Add-InventoryArtifact $inventoryArtifacts 'verification/run_s2a_t58_row22_attempt06_isolated_sim.ps1' $LauncherPath
    Add-InventoryArtifact $inventoryArtifacts 'verification/verify_s2a_t58_row22_run06_simulation.ps1' $PSCommandPath
    foreach ($sourceName in $PriorAttemptSources.Keys) { Add-InventoryArtifact ('preserved_attempt_source/' + $sourceName) $PriorAttemptSources[$sourceName].path }
    foreach ($sourceProperty in $binding.sources.PSObject.Properties) {
        $inventoryArtifacts.Add([ordered]@{ relative_path = 'bound_source/' + $sourceProperty.Name; artifact = Get-Artifact ([string]$sourceProperty.Value.path) })
    }
    $inventoryResult = [ordered]@{
        schema = 'GestureForge-S2A-T58-run06-simulation-inventory-v1'
        task_id = 'S2A-T58'
        run_id = 'run06'
        status = 'PASS_SIMULATION_DATA_ONLY'
        simulation = 'COMPLETED_WITH_PASS_SENTINEL_AND_FINISH'
        evidence_files = @($inventoryArtifacts.ToArray())
        excluded = @('report/evidence/S2A-T58/run06/simulation_inventory.json (self)', 'report/evidence/S2A-T58/run06/isolated_project/** (generated build directory)')
        existing_isolated_run_inventory = @{ path = [IO.Path]::GetFullPath($PreparedInventory); sha256 = $ExpectedHashes['isolated_run_inventory.json']; preserved = $true }
    }
    Write-NewJson $InventoryPath $inventoryResult

    $finalProcess = @(Get-ProcessSnapshot)
    Require ($finalProcess.Count -eq 0) 'simulation inventory 写入后检测到 Vivado/XSim 进程'
    Write-Output (ConvertTo-Json -InputObject ([ordered]@{ status = 'PASS_SIMULATION_DATA_ONLY'; run_id = 'run06'; raw_bytes = $ExpectedRawBytes; int8_bytes = $ExpectedOutputBytes; raw_mismatches = $rawMismatchCount; int8_mismatches = $outputMismatchCount; progress_events = $logContract.progress_count; simulation_inventory_files = $inventoryArtifacts.Count; vivado_xsim_process_count = 0 }) -Depth 8 -Compress)
}
catch {
    [Console]::Error.WriteLine(('S2A-T58 run06 simulation finalizer failed: ' + $_.Exception.Message))
    exit 1
}
