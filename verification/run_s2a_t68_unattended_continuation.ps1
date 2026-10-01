[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$EvidenceDirectory,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9_-]+$')]
    [string]$RunId,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-fA-F]{64}$')]
    [string]$ExpectedBackendSha256
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:ApprovedBackendSha256 = '3910bc69d1630eff3f8740eed74e03f5328319da24abb3f9e755808afd5ec154'
$script:ApprovedPythonPath = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$script:ExpectedPowerShellVersion = '7.6.5'
$script:ExpectedT29ReportSha256 = '24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231'
$script:ExpectedT25IndexSha256 = 'cbda3f257ac626252901f978464b93c5c2e909634e30c1bcf70cd588f0f6950d'
$script:ExpectedD9DecoderSha256 = '0be8e2dc0878116b5239a20a397f4f063de7b33c2ee38e1d0aadf1ced7d365c6'
$script:Sample0WaitLimit = [TimeSpan]::FromHours(24)
$script:Sample0PollInterval = [TimeSpan]::FromSeconds(30)
$script:ExistingBatchWaitLimit = [TimeSpan]::FromHours(72)
$script:ExistingBatchPollInterval = [TimeSpan]::FromSeconds(30)
$script:CoordinatorLock = $null
$script:CoordinatorLockOwned = $false
$script:SummaryPath = $null
$script:SummaryWritable = $false
$script:Summary = [ordered]@{
    schema_version = 'gestureforge_s2a_t68_unattended_continuation_v1'
    status = 'INITIALIZING'
    stage2a_pass = $false
    evidence_directory = $null
    run_id = $null
    expected_backend_sha256 = $null
    observed_backend_sha256 = $null
    coordinator_path = $null
    coordinator_sha256 = $null
    powershell_version = $PSVersionTable.PSVersion.ToString()
    powershell_executable = $null
    pinned_python_path = $script:ApprovedPythonPath
    pinned_python_version_expected = 'Python 3.12.14'
    pinned_python_version_stdout = $null
    pinned_python_version_exit_code = $null
    pinned_python_sha256 = $null
    sample0 = $null
    batch = $null
    d9 = $null
    error = $null
    created_utc = [DateTime]::UtcNow.ToString('o')
}

function Get-Sha256Literal {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
}

function Test-PathComponentRun01 {
    param([Parameter(Mandatory = $true)][string]$Path)
    foreach ($part in ($Path -split '[\\/]+' | Where-Object { $_ -ne '' })) {
        if ($part -ieq 'run01') { return $true }
    }
    return $false
}

function Assert-NormalDirectory {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Label)
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if (-not $item.PSIsContainer -or (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "$Label 必须是普通目录：$Path"
    }
    return $item.FullName
}

function Assert-NormalFile {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Label)
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($item.PSIsContainer -or (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "$Label 必须是普通文件：$Path"
    }
    return $item.FullName
}

function Read-JsonObject {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Label)
    $normalPath = Assert-NormalFile -Path $Path -Label $Label
    $encoding = [System.Text.UTF8Encoding]::new($false, $true)
    $text = [System.IO.File]::ReadAllText($normalPath, $encoding)
    $value = ConvertFrom-Json -InputObject $text -AsHashtable -Depth 64 -ErrorAction Stop
    if ($value -isnot [System.Collections.IDictionary]) { throw "$Label 顶层必须为 JSON 对象：$normalPath" }
    return $value
}

function Write-NewUtf8File {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Text)
    $encoding = [System.Text.UTF8Encoding]::new($false)
    $bytes = $encoding.GetBytes($Text)
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
}

function Write-NewJsonFile {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][System.Collections.IDictionary]$Value)
    $encoding = [System.Text.UTF8Encoding]::new($false)
    $payload = ($Value | ConvertTo-Json -Depth 32) + "`n"
    $script:Summary.summary_payload_sha256 = [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($encoding.GetBytes($payload))).ToLowerInvariant()
    $script:Summary.summary_hash_scope = 'summary_payload_sha256 覆盖插入该字段前的 UTF-8 无 BOM JSON 文本及一个 LF。'
    $json = ($Value | ConvertTo-Json -Depth 32) + "`n"
    Write-NewUtf8File -Path $Path -Text $json
}

function Quote-WindowsArgument {
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Argument)
    $builder = [System.Text.StringBuilder]::new()
    $null = $builder.Append([char]'"')
    $backslashes = 0
    foreach ($character in $Argument.ToCharArray()) {
        if ($character -eq [char]'\') {
            $backslashes++
        } elseif ($character -eq [char]'"') {
            for ($index = 0; $index -lt (2 * $backslashes + 1); $index++) { $null = $builder.Append([char]'\') }
            $null = $builder.Append([char]'"')
            $backslashes = 0
        } else {
            for ($index = 0; $index -lt $backslashes; $index++) { $null = $builder.Append([char]'\') }
            $null = $builder.Append($character)
            $backslashes = 0
        }
    }
    for ($index = 0; $index -lt (2 * $backslashes); $index++) { $null = $builder.Append([char]'\') }
    $null = $builder.Append([char]'"')
    return $builder.ToString()
}

function Invoke-CapturedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$ExecutablePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory
    )
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $ExecutablePath
    $startInfo.WorkingDirectory = $WorkingDirectory
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.Environment['PATH'] = $env:PATH
    foreach ($argument in $Arguments) { $null = $startInfo.ArgumentList.Add([string]$argument) }

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    try {
        if (-not $process.Start()) { throw "无法启动程序：$ExecutablePath" }
        $stdoutTask = $process.StandardOutput.ReadToEndAsync()
        $stderrTask = $process.StandardError.ReadToEndAsync()
        $process.WaitForExit()
        $stdout = $stdoutTask.GetAwaiter().GetResult()
        $stderr = $stderrTask.GetAwaiter().GetResult()
        $exitCode = [int]$process.ExitCode
        return [ordered]@{ exit_code = $exitCode; stdout = $stdout; stderr = $stderr }
    } finally {
        $process.Dispose()
    }
}

function Test-Sample0Passed {
    param([Parameter(Mandatory = $true)][System.Collections.IDictionary]$Record, [Parameter(Mandatory = $true)][string]$ExpectedRunId)
    return ($Record.schema_version -ceq 'gestureforge_s2a_t68_simulation_execution_v1' -and
        $Record.sample_index -eq 0 -and $Record.run_id -ceq $ExpectedRunId -and
        $Record.exit_code -eq 0 -and $Record.runner_exit_code -eq 0 -and
        $Record.progress_markers_valid -eq $true -and $Record.last_progress_phase -ceq 'complete' -and
        $Record.result_summary_valid -eq $true -and $Record.head_exports_valid -eq $true -and
        $Record.wave_dump_requested -eq $false)
}

function Test-ExpectedIndices {
    param(
        [Parameter(Mandatory = $true)][AllowNull()][AllowEmptyCollection()][object]$Observed,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][int[]]$Expected,
        [Parameter(Mandatory = $true)][string]$Label
    )
    $actual = @($Observed | ForEach-Object { [int]$_ })
    if (($actual -join ',') -cne ($Expected -join ',')) { throw "$Label 与预期样本索引不一致。" }
}

function Assert-PassingBatchSummary {
    param(
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$BatchSummary,
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$ExpectedRunId,
        [Parameter(Mandatory = $true)][string]$ExpectedBackendHash,
        [Parameter(Mandatory = $true)][string]$ExpectedSchedulerHash,
        [Parameter(Mandatory = $true)][string]$ExpectedRunnerHash
    )
    $expectedIndices = @(1..108)
    if ($BatchSummary.schema_version -cne 'gestureforge_s2a_t68_batch_summary_v1' -or
        $BatchSummary.status -cne 'PASS_108_RUNNERS' -or
        ([string]$BatchSummary.evidence_directory).TrimEnd('\') -ine $EvidenceRoot.TrimEnd('\') -or
        $BatchSummary.run_id -cne $ExpectedRunId -or
        ([string]$BatchSummary.expected_backend_sha256).ToLowerInvariant() -cne $ExpectedBackendHash -or
        $BatchSummary.scheduler_sha256 -cne $ExpectedSchedulerHash -or
        $BatchSummary.runner_sha256 -cne $ExpectedRunnerHash -or
        $BatchSummary.sample0_snapshot.sha256 -notmatch '^[0-9a-f]{64}$' -or
        $BatchSummary.first_index -ne 1 -or $BatchSummary.last_index -ne 108 -or $BatchSummary.max_workers -ne 8 -or
        $BatchSummary.stage2a_pass -ne $false -or $BatchSummary.d9_aggregation_started -ne $false -or
        $null -ne $BatchSummary.scheduler_error) {
        throw '既有 batch_summary.json 不满足固定 T68 108 样本批次的 PASS 条件。'
    }
    foreach ($name in @('target_indices', 'dispatched_indices', 'started_indices', 'succeeded_indices')) {
        Test-ExpectedIndices -Observed $BatchSummary[$name] -Expected $expectedIndices -Label $name
    }
    Test-ExpectedIndices -Observed $BatchSummary.failed_indices -Expected @() -Label 'failed_indices'
    Test-ExpectedIndices -Observed $BatchSummary.remaining_indices -Expected @() -Label 'remaining_indices'
    if ($BatchSummary.scheduler_sha256 -notmatch '^[0-9a-f]{64}$' -or
        $BatchSummary.runner_sha256 -notmatch '^[0-9a-f]{64}$' -or
        $BatchSummary.scheduler_source_snapshot.sha256 -cne $BatchSummary.scheduler_sha256 -or
        $null -ne $BatchSummary.scheduler_source_snapshot.write_error -or
        $BatchSummary.scheduler_final_observation.unchanged -ne $true -or
        @($BatchSummary.scheduler_hash_mismatches).Count -ne 0) {
        throw 'batch_summary.json 的 scheduler 源码冻结证据不完整或不一致。'
    }
}

function Wait-Sample0TerminalRecord {
    param([Parameter(Mandatory = $true)][string]$RecordPath, [Parameter(Mandatory = $true)][TimeSpan]$MaximumWait, [Parameter(Mandatory = $true)][TimeSpan]$PollInterval)
    $deadline = [DateTime]::UtcNow + $MaximumWait
    $previousInvalidSignature = $null
    $sameInvalidCount = 0
    $lastReadError = $null
    while ([DateTime]::UtcNow -lt $deadline) {
        if (Test-Path -LiteralPath $RecordPath) {
            try {
                $normalPath = Assert-NormalFile -Path $RecordPath -Label 'sample0 终态记录'
                $record = Read-JsonObject -Path $normalPath -Label 'sample0 终态记录'
                return [ordered]@{ state = 'FOUND'; record = $record; read_error = $null }
            } catch {
                $lastReadError = $_.Exception.Message
                $signature = $null
                try {
                    $normalPath = Assert-NormalFile -Path $RecordPath -Label 'sample0 终态记录'
                    $signature = '{0}|{1}' -f (Get-Item -LiteralPath $normalPath).Length, (Get-Sha256Literal -Path $normalPath)
                } catch { $lastReadError = $_.Exception.Message }
                if ($null -ne $signature -and $signature -ceq $previousInvalidSignature) {
                    $sameInvalidCount++
                } elseif ($null -ne $signature) {
                    $previousInvalidSignature = $signature
                    $sameInvalidCount = 1
                }
                if ($sameInvalidCount -ge 2) {
                    return [ordered]@{ state = 'INVALID'; record = $null; read_error = $lastReadError }
                }
            }
        }
        $remaining = $deadline - [DateTime]::UtcNow
        if ($remaining -le [TimeSpan]::Zero) { break }
        $sleepMilliseconds = [int][Math]::Min($PollInterval.TotalMilliseconds, $remaining.TotalMilliseconds)
        if ($sleepMilliseconds -gt 0) { Start-Sleep -Milliseconds $sleepMilliseconds }
    }
    return [ordered]@{ state = 'TIMEOUT'; record = $null; read_error = $lastReadError }
}

function Get-ExistingBatchState {
    param(
        [Parameter(Mandatory = $true)][string]$DispatchDirectory,
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$ExpectedRunId,
        [Parameter(Mandatory = $true)][string]$ExpectedBackendHash,
        [Parameter(Mandatory = $true)][string]$SchedulerPath,
        [Parameter(Mandatory = $true)][string]$RunnerPath
    )
    if (-not (Test-Path -LiteralPath $DispatchDirectory)) {
        return [ordered]@{ state = 'ABSENT'; summary = $null; summary_path = $null; summary_sha256 = $null; message = $null; wait_seconds = 0 }
    }
    $null = Assert-NormalDirectory -Path $DispatchDirectory -Label 'batch_dispatch'
    $summaryPath = Join-Path $DispatchDirectory 'batch_summary.json'
    $fallbackPath = Join-Path $DispatchDirectory 'batch_summary_fallback.json'
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $deadline = [DateTime]::UtcNow + $script:ExistingBatchWaitLimit
    $lastInvalidSignature = $null
    $sameInvalidCount = 0
    $lastReadError = $null
    while ([DateTime]::UtcNow -lt $deadline) {
        $primaryExists = Test-Path -LiteralPath $summaryPath
        $fallbackExists = Test-Path -LiteralPath $fallbackPath
        if ($primaryExists -and $fallbackExists) {
            return [ordered]@{ state = 'FAILED'; summary = $null; summary_path = $summaryPath; summary_sha256 = $null; message = '主 summary 与 fallback summary 同时存在，拒绝继续。'; wait_seconds = [Math]::Round($timer.Elapsed.TotalSeconds, 3) }
        }
        if ($primaryExists -or $fallbackExists) {
            $candidatePath = if ($primaryExists) { $summaryPath } else { $fallbackPath }
            $candidateLabel = if ($primaryExists) { '既有 batch_summary.json' } else { 'scheduler fallback summary' }
            try {
                $candidateItem = Get-Item -LiteralPath $candidatePath -ErrorAction Stop
                if ($candidateItem.PSIsContainer -or (($candidateItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
                    return [ordered]@{ state = 'FAILED'; summary = $null; summary_path = $candidatePath; summary_sha256 = $null; message = '既有 scheduler summary 路径类型不安全，拒绝继续或重派。'; wait_seconds = [Math]::Round($timer.Elapsed.TotalSeconds, 3) }
                }
            } catch {
                return [ordered]@{ state = 'FAILED'; summary = $null; summary_path = $candidatePath; summary_sha256 = $null; message = $_.Exception.Message; wait_seconds = [Math]::Round($timer.Elapsed.TotalSeconds, 3) }
            }
            try {
                $candidate = Read-JsonObject -Path $candidatePath -Label $candidateLabel
                $candidateHash = Get-Sha256Literal -Path $candidatePath
                if (-not $primaryExists) {
                    return [ordered]@{ state = 'FAILED'; summary = $null; summary_path = $candidatePath; summary_sha256 = $candidateHash; message = '既有 scheduler 写入 fallback summary，批次失败，拒绝重派。'; wait_seconds = [Math]::Round($timer.Elapsed.TotalSeconds, 3) }
                }
                try {
                    Assert-PassingBatchSummary -BatchSummary $candidate -EvidenceRoot $EvidenceRoot -ExpectedRunId $ExpectedRunId -ExpectedBackendHash $ExpectedBackendHash `
                        -ExpectedSchedulerHash (Get-Sha256Literal -Path $SchedulerPath) -ExpectedRunnerHash (Get-Sha256Literal -Path $RunnerPath)
                    return [ordered]@{ state = 'PASS'; summary = $candidate; summary_path = $candidatePath; summary_sha256 = $candidateHash; message = $null; wait_seconds = [Math]::Round($timer.Elapsed.TotalSeconds, 3) }
                } catch {
                    return [ordered]@{ state = 'FAILED'; summary = $null; summary_path = $candidatePath; summary_sha256 = $candidateHash; message = $_.Exception.Message; wait_seconds = [Math]::Round($timer.Elapsed.TotalSeconds, 3) }
                }
            } catch {
                $lastReadError = $_.Exception.Message
                $signature = $null
                try {
                    $normalCandidatePath = Assert-NormalFile -Path $candidatePath -Label $candidateLabel
                    $signature = '{0}|{1}' -f (Get-Item -LiteralPath $normalCandidatePath).Length, (Get-Sha256Literal -Path $normalCandidatePath)
                } catch { $lastReadError = $_.Exception.Message }
                if ($null -ne $signature -and $signature -ceq $lastInvalidSignature) {
                    $sameInvalidCount++
                } elseif ($null -ne $signature) {
                    $lastInvalidSignature = $signature
                    $sameInvalidCount = 1
                }
                if ($sameInvalidCount -ge 2) {
                    return [ordered]@{ state = 'FAILED'; summary = $null; summary_path = $candidatePath; summary_sha256 = $signature.Split('|')[1]; message = "终态 summary 连续两次解析失败：$lastReadError"; wait_seconds = [Math]::Round($timer.Elapsed.TotalSeconds, 3) }
                }
            }
        }
        $remaining = $deadline - [DateTime]::UtcNow
        if ($remaining -le [TimeSpan]::Zero) { break }
        $sleepMilliseconds = [int][Math]::Min($script:ExistingBatchPollInterval.TotalMilliseconds, $remaining.TotalMilliseconds)
        if ($sleepMilliseconds -gt 0) { Start-Sleep -Milliseconds $sleepMilliseconds }
    }
    return [ordered]@{ state = 'TIMEOUT'; summary = $null; summary_path = $summaryPath; summary_sha256 = $null; message = '72 小时内未出现既有 scheduler 的终态 summary；不自动重启，避免重复派发。'; wait_seconds = [Math]::Round($timer.Elapsed.TotalSeconds, 3) }
}

function Assert-D9ReportBinding {
    param(
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$Report,
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$ExpectedRunId,
        [Parameter(Mandatory = $true)][string]$VerifierHash,
        [Parameter(Mandatory = $true)][string]$ExpectedBackendHash,
        [Parameter(Mandatory = $true)][string]$ExpectedSample0SnapshotHash,
        [AllowNull()][string]$ExpectedSample0SimulationHash
    )
    $resolvedRoot = [System.IO.Path]::GetFullPath($EvidenceRoot).TrimEnd('\')
    if ($Report.schema_version -cne 'gestureforge_s2a_t68_d9_actual_head_comparison_v1' -or
        $Report.status -cne 'PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9' -or
        $Report.sample_count -ne 109 -or $Report.run_id -cne $ExpectedRunId -or
        [System.IO.Path]::GetFullPath([string]$Report.evidence_root).TrimEnd('\') -ine $resolvedRoot -or
        $Report.verifier_sha256 -cne $VerifierHash -or
        $Report.cpu_d9_reference.path -cne 'report/evidence/S2A-T29/cpu_decode_nms_reference.json' -or
        $Report.cpu_d9_reference.sha256 -cne $script:ExpectedT29ReportSha256 -or
        $Report.t25_index.path -cne 'report/evidence/S2A-T25/cpu_layer_golden_index.json' -or
        $Report.t25_index.sha256 -cne $script:ExpectedT25IndexSha256 -or
        $Report.d9_decoder_sha256 -cne $script:ExpectedD9DecoderSha256 -or
        $Report.score_threshold -ne 0.25 -or $Report.score_absolute_tolerance -ne 1e-6 -or
        $Report.coordinate_absolute_tolerance -ne 1e-6 -or $Report.relative_tolerance -ne 0.0 -or
        $Report.simulator_started_by_verifier -ne $false) {
        throw 'D9 报告顶层 schema、样本范围、运行路径、verifier 或冻结基线绑定不符。'
    }
    if ($ExpectedBackendHash -cne $script:ApprovedBackendSha256 -or
        $ExpectedSample0SnapshotHash -notmatch '^[0-9a-f]{64}$') {
        throw '当前批次 backend 或 sample0 编译快照绑定无效。'
    }
    if ($Report.samples -isnot [array] -or $Report.samples.Count -ne 109) { throw 'D9 报告 samples 必须覆盖 109 个样本。' }

    $sampleIds = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
    $maxScoreError = 0.0
    $maxCoordinateError = 0.0
    for ($index = 0; $index -lt 109; $index++) {
        $sample = $Report.samples[$index]
        if ($sample -isnot [System.Collections.IDictionary] -or
            $sample.sample_index -ne $index -or $sample.frame_id -ne $index -or
            $sample.sample_id -isnot [string] -or [string]::IsNullOrWhiteSpace($sample.sample_id) -or
            -not $sampleIds.Add([string]$sample.sample_id)) {
            throw "D9 报告样本顺序、sample_id 或 frame_id 不符：$index"
        }
        foreach ($field in @('fixture_manifest_sha256', 'simulation_execution_record_sha256', 'compile_execution_record_sha256', 'compile_source_snapshot_sha256', 'input_sha256')) {
            if ($sample[$field] -isnot [string] -or $sample[$field] -notmatch '^[0-9a-f]{64}$') {
                throw "D9 报告样本 $index 缺少有效 $field。"
            }
        }
        if ($index -eq 0 -and $sample.compile_source_snapshot_sha256 -cne $ExpectedSample0SnapshotHash) {
            throw 'D9 sample_000 编译快照与通过的 batch summary 不一致。'
        }
        if ($index -eq 0 -and $null -ne $ExpectedSample0SimulationHash -and
            $sample.simulation_execution_record_sha256 -cne $ExpectedSample0SimulationHash) {
            throw 'D9 sample_000 仿真记录与已观察的终态记录不一致。'
        }
        if ($sample.head_exports -isnot [System.Collections.IDictionary] -or
            $sample.head_exports.head13 -isnot [System.Collections.IDictionary] -or
            $sample.head_exports.head26 -isnot [System.Collections.IDictionary]) {
            throw "D9 报告样本 $index 缺少 head13/head26 绑定。"
        }
        foreach ($head in @(@{ name = 'head13'; bytes = 5070 }, @{ name = 'head26'; bytes = 20280 })) {
            $headRow = $sample.head_exports[$head.name]
            if ($headRow.bytes -ne $head.bytes -or
                $headRow.sha256 -isnot [string] -or $headRow.sha256 -notmatch '^[0-9a-f]{64}$' -or
                $headRow.t25_cpu_sha256 -cne $headRow.sha256) {
                throw "D9 报告样本 $index 的 $($head.name) PL/T25 哈希或字节数不符。"
            }
        }
        $comparison = $sample.d9_comparison
        if ($comparison -isnot [System.Collections.IDictionary] -or
            $comparison.detections -isnot [array] -or $comparison.detection_count -ne $comparison.detections.Count -or
            $comparison.raw_candidate_count -lt 0 -or $comparison.relative_tolerance -ne 0.0) {
            throw "D9 报告样本 $index 的离散比较摘要缺失或不一致。"
        }
        $sampleScoreError = [double]$comparison.max_score_abs_error
        $sampleCoordinateError = [double]$comparison.max_xyxy_abs_error
        if ([double]::IsNaN($sampleScoreError) -or [double]::IsInfinity($sampleScoreError) -or
            [double]::IsNaN($sampleCoordinateError) -or [double]::IsInfinity($sampleCoordinateError) -or
            $sampleScoreError -lt 0.0 -or $sampleScoreError -gt 1e-6 -or
            $sampleCoordinateError -lt 0.0 -or $sampleCoordinateError -gt 1e-6) {
            throw "D9 报告样本 $index 的数值误差超出冻结容差。"
        }
        foreach ($detection in $comparison.detections) {
            $scoreError = [double]$detection.score_abs_error
            $coordinateError = [double]$detection.xyxy_max_abs_error
            if ($detection.class_id -lt 0 -or $detection.class_name -isnot [string] -or
                $detection.source_order -lt 0 -or [double]::IsNaN($scoreError) -or [double]::IsInfinity($scoreError) -or
                [double]::IsNaN($coordinateError) -or [double]::IsInfinity($coordinateError) -or
                $scoreError -lt 0.0 -or $scoreError -gt 1e-6 -or $coordinateError -lt 0.0 -or $coordinateError -gt 1e-6) {
                throw "D9 报告样本 $index 含无效 detection comparison。"
            }
        }
        if ($sampleScoreError -gt $maxScoreError) { $maxScoreError = $sampleScoreError }
        if ($sampleCoordinateError -gt $maxCoordinateError) { $maxCoordinateError = $sampleCoordinateError }
    }
    if ([Math]::Abs([double]$Report.max_score_abs_error - $maxScoreError) -gt 1e-15 -or
        [Math]::Abs([double]$Report.max_xyxy_abs_error - $maxCoordinateError) -gt 1e-15) {
        throw 'D9 报告聚合误差与 109 个样本摘要不一致。'
    }
}

function ConvertTo-D9CanonicalJsonValue {
    param([AllowNull()][object]$Value)
    if ($null -eq $Value) { return $null }
    if ($Value -is [System.Collections.IDictionary]) {
        $canonical = [System.Collections.Generic.SortedDictionary[string, object]]::new([System.StringComparer]::Ordinal)
        foreach ($key in $Value.Keys) {
            $canonical[[string]$key] = ConvertTo-D9CanonicalJsonValue -Value $Value[$key]
        }
        return ,$canonical
    }
    if ($Value -is [System.Array]) {
        $items = [System.Collections.Generic.List[object]]::new()
        foreach ($item in $Value) { $items.Add((ConvertTo-D9CanonicalJsonValue -Value $item)) }
        return ,$items.ToArray()
    }
    return $Value
}

function Get-D9SharedReportFields {
    param([Parameter(Mandatory = $true)][System.Collections.IDictionary]$Value)
    $shared = [System.Collections.Generic.Dictionary[string, object]]::new([System.StringComparer]::Ordinal)
    foreach ($key in $Value.Keys) {
        if ([string]$key -cnotin @('report_path', 'report_sha256')) {
            $shared[[string]$key] = $Value[$key]
        }
    }
    return ,$shared
}

function Assert-D9ReportDeepEqual {
    param(
        [Parameter(Mandatory = $true)][object]$Expected,
        [Parameter(Mandatory = $true)][object]$Observed,
        [Parameter(Mandatory = $true)][string]$Label
    )
    $expectedJson = ConvertTo-Json -InputObject (ConvertTo-D9CanonicalJsonValue -Value $Expected) -Depth 64 -Compress
    $observedJson = ConvertTo-Json -InputObject (ConvertTo-D9CanonicalJsonValue -Value $Observed) -Depth 64 -Compress
    if ($expectedJson -cne $observedJson) { throw "$Label 与重新计算的完整 D9 报告不一致。" }
}

function Assert-D9LogBundle {
    param(
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath,
        [Parameter(Mandatory = $true)][string]$ReportPath,
        [Parameter(Mandatory = $true)][string]$ReportHash,
        [Parameter(Mandatory = $true)][string]$ExpectedRunId,
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$VerifierHash,
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$ExpectedReport
    )
    $stdout = [System.IO.File]::ReadAllText((Assert-NormalFile -Path $StdoutPath -Label 'D9 stdout log'), [System.Text.UTF8Encoding]::new($false, $true))
    $stderr = [System.IO.File]::ReadAllText((Assert-NormalFile -Path $StderrPath -Label 'D9 stderr log'), [System.Text.UTF8Encoding]::new($false, $true))
    if (-not [string]::IsNullOrWhiteSpace($stderr)) { throw '已有 D9 stderr log 非空，与成功报告冲突。' }
    $printed = ConvertFrom-Json -InputObject $stdout -AsHashtable -Depth 64 -ErrorAction Stop
    if ($printed -isnot [System.Collections.IDictionary] -or
        $printed.status -cne 'PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9' -or $printed.sample_count -ne 109 -or
        $printed.run_id -cne $ExpectedRunId -or
        [System.IO.Path]::GetFullPath([string]$printed.evidence_root).TrimEnd('\') -ine [System.IO.Path]::GetFullPath($EvidenceRoot).TrimEnd('\') -or
        $printed.verifier_sha256 -cne $VerifierHash -or
        [System.IO.Path]::GetFullPath([string]$printed.report_path) -ine [System.IO.Path]::GetFullPath($ReportPath) -or
        $printed.report_sha256 -cne $ReportHash) {
        throw '既有 D9 stdout log 与报告身份或 SHA 不一致。'
    }
    Assert-D9ReportDeepEqual -Expected $ExpectedReport -Observed (Get-D9SharedReportFields -Value $printed) -Label '既有 D9 stdout log'
}

function Invoke-VerifiedD9 {
    param(
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$ExpectedRunId,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$PythonPath,
        [Parameter(Mandatory = $true)][string]$ExpectedBackendHash,
        [Parameter(Mandatory = $true)][string]$ExpectedSample0SnapshotHash,
        [AllowNull()][string]$ExpectedSample0SimulationHash
    )
    $verifierPath = Join-Path $RepositoryRoot 'verification\verify_s2a_t68_d9_outputs.py'
    $reportPath = Join-Path $EvidenceRoot 'd9_109_sample_report.json'
    $stdoutPath = Join-Path $EvidenceRoot ("unattended_d9_stdout_{0}.log" -f $ExpectedRunId)
    $stderrPath = Join-Path $EvidenceRoot ("unattended_d9_stderr_{0}.log" -f $ExpectedRunId)
    $verifierHash = Get-Sha256Literal -Path $verifierPath
    $pythonHash = Get-Sha256Literal -Path $PythonPath
    $reportExists = Test-Path -LiteralPath $reportPath
    $stdoutExists = Test-Path -LiteralPath $stdoutPath
    $stderrExists = Test-Path -LiteralPath $stderrPath
    if (-not $reportExists -and ($stdoutExists -or $stderrExists)) {
        throw '存在 D9 coordinator log 但报告缺失，拒绝覆盖或重新运行。'
    }
    if ($reportExists) {
        $report = Read-JsonObject -Path $reportPath -Label '既有 D9 报告'
        $reportHash = Get-Sha256Literal -Path $reportPath
        Assert-D9ReportBinding -Report $report -EvidenceRoot $EvidenceRoot -ExpectedRunId $ExpectedRunId -VerifierHash $verifierHash `
            -ExpectedBackendHash $ExpectedBackendHash -ExpectedSample0SnapshotHash $ExpectedSample0SnapshotHash `
            -ExpectedSample0SimulationHash $ExpectedSample0SimulationHash
        $arguments = @('-B', $verifierPath, '--evidence-root', $EvidenceRoot, '--run-id', $ExpectedRunId)
        $execution = Invoke-CapturedProcess -ExecutablePath $PythonPath -Arguments $arguments -WorkingDirectory $RepositoryRoot
        if ($execution.exit_code -ne 0) { throw "D9 只读全量重算失败，exit=$($execution.exit_code)；保留既有报告与日志。" }
        if (-not [string]::IsNullOrWhiteSpace($execution.stderr)) { throw 'D9 只读全量重算 stderr 非空；保留既有报告与日志。' }
        $recomputed = ConvertFrom-Json -InputObject $execution.stdout -AsHashtable -Depth 64 -ErrorAction Stop
        if ($recomputed -isnot [System.Collections.IDictionary]) { throw 'D9 只读全量重算 stdout 不是完整 JSON 对象。' }
        Assert-D9ReportBinding -Report (Get-D9SharedReportFields -Value $recomputed) -EvidenceRoot $EvidenceRoot -ExpectedRunId $ExpectedRunId -VerifierHash $verifierHash `
            -ExpectedBackendHash $ExpectedBackendHash -ExpectedSample0SnapshotHash $ExpectedSample0SnapshotHash `
            -ExpectedSample0SimulationHash $ExpectedSample0SimulationHash
        Assert-D9ReportDeepEqual -Expected $report -Observed (Get-D9SharedReportFields -Value $recomputed) -Label '既有 D9 report'
        if ($stdoutExists -xor $stderrExists) { throw 'D9 报告存在但 coordinator stdout/stderr log 不成对，保留现场并终止。' }
        if ($stdoutExists) {
            Assert-D9LogBundle -StdoutPath $stdoutPath -StderrPath $stderrPath -ReportPath $reportPath -ReportHash $reportHash `
                -ExpectedRunId $ExpectedRunId -EvidenceRoot $EvidenceRoot -VerifierHash $verifierHash -ExpectedReport $report
        }
        return [ordered]@{
            passed = $true
            status = 'PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9'
            reused_existing_report = $true
            process_exit_code = $execution.exit_code
            process_exit_observed = $true
            verifier_path = $verifierPath
            verifier_sha256 = $verifierHash
            python_path = $PythonPath
            python_sha256 = $pythonHash
            report_path = $reportPath
            report_sha256 = $reportHash
            revalidation_stdout_sha256 = [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes($execution.stdout))).ToLowerInvariant()
            revalidation_stderr_sha256 = [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes($execution.stderr))).ToLowerInvariant()
            report_status = $report.status
            sample_count = $report.sample_count
            stdout_path = if ($stdoutExists) { $stdoutPath } else { $null }
            stdout_sha256 = if ($stdoutExists) { Get-Sha256Literal -Path $stdoutPath } else { $null }
            stderr_path = if ($stderrExists) { $stderrPath } else { $null }
            stderr_sha256 = if ($stderrExists) { Get-Sha256Literal -Path $stderrPath } else { $null }
        }
    }
    foreach ($path in @($stdoutPath, $stderrPath)) {
        if (Test-Path -LiteralPath $path) { throw "拒绝覆盖已有 D9 coordinator log：$path" }
    }
    $arguments = @('-B', $verifierPath, '--evidence-root', $EvidenceRoot, '--run-id', $ExpectedRunId, '--report', $reportPath)
    $execution = Invoke-CapturedProcess -ExecutablePath $PythonPath -Arguments $arguments -WorkingDirectory $RepositoryRoot
    Write-NewUtf8File -Path $stdoutPath -Text $execution.stdout
    Write-NewUtf8File -Path $stderrPath -Text $execution.stderr
    if (-not (Test-Path -LiteralPath $reportPath -PathType Leaf)) { throw 'D9 verifier 未生成预期报告。' }
    $report = Read-JsonObject -Path $reportPath -Label 'D9 报告'
    $reportHash = Get-Sha256Literal -Path $reportPath
    Assert-D9ReportBinding -Report $report -EvidenceRoot $EvidenceRoot -ExpectedRunId $ExpectedRunId -VerifierHash $verifierHash `
        -ExpectedBackendHash $ExpectedBackendHash -ExpectedSample0SnapshotHash $ExpectedSample0SnapshotHash `
        -ExpectedSample0SimulationHash $ExpectedSample0SimulationHash
    Assert-D9LogBundle -StdoutPath $stdoutPath -StderrPath $stderrPath -ReportPath $reportPath -ReportHash $reportHash `
        -ExpectedRunId $ExpectedRunId -EvidenceRoot $EvidenceRoot -VerifierHash $verifierHash -ExpectedReport $report
    $pass = ($execution.exit_code -eq 0)
    return [ordered]@{
        passed = $pass
        status = if ($pass) { 'PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9' } else { 'FAIL_D9_VERIFICATION' }
        reused_existing_report = $false
        process_exit_code = $execution.exit_code
        process_exit_observed = $true
        verifier_path = $verifierPath
        verifier_sha256 = $verifierHash
        python_path = $PythonPath
        python_sha256 = $pythonHash
        report_path = $reportPath
        report_sha256 = $reportHash
        report_status = $report.status
        sample_count = $report.sample_count
        stdout_path = $stdoutPath
        stdout_sha256 = Get-Sha256Literal -Path $stdoutPath
        stderr_path = $stderrPath
        stderr_sha256 = Get-Sha256Literal -Path $stderrPath
    }
}

try {
    if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { throw '该 continuation 仅支持 Windows。' }
    if ($PSVersionTable.PSVersion.ToString() -cne $script:ExpectedPowerShellVersion) {
        throw "必须使用 PowerShell $($script:ExpectedPowerShellVersion)，当前为 $($PSVersionTable.PSVersion)。"
    }
    if ($RunId -notmatch '^[A-Za-z0-9_-]+$') { throw 'RunId 仅允许 ASCII 字母、数字、下划线和连字符。' }
    $expectedBackendHash = $ExpectedBackendSha256.ToLowerInvariant()
    if ($expectedBackendHash -cne $script:ApprovedBackendSha256) { throw 'ExpectedBackendSha256 与已冻结的 8×8/8-lane backend SHA 不符。' }

    $repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..') -ErrorAction Stop).Path
    $approvedEvidenceParent = (Resolve-Path -LiteralPath (Join-Path $repositoryRoot 'report\evidence\S2A-T68') -ErrorAction Stop).Path.TrimEnd('\')
    $evidenceRoot = [System.IO.Path]::GetFullPath((Resolve-Path -LiteralPath $EvidenceDirectory -ErrorAction Stop).Path)
    $null = Assert-NormalDirectory -Path $evidenceRoot -Label 'EvidenceDirectory'
    if ((Test-PathComponentRun01 -Path $evidenceRoot) -or (Test-PathComponentRun01 -Path $RunId)) {
        throw '路径或 RunId 含 run01 组件，拒绝访问。'
    }
    $evidencePrefix = $approvedEvidenceParent + [System.IO.Path]::DirectorySeparatorChar
    if (-not $evidenceRoot.StartsWith($evidencePrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "EvidenceDirectory 必须位于固定 S2A-T68 evidence 父目录内：$approvedEvidenceParent"
    }

    $script:Summary.evidence_directory = $evidenceRoot
    $script:Summary.run_id = $RunId
    $script:Summary.expected_backend_sha256 = $expectedBackendHash
    $script:Summary.coordinator_path = (Resolve-Path -LiteralPath $PSCommandPath -ErrorAction Stop).Path
    $script:Summary.coordinator_sha256 = Get-Sha256Literal -Path $script:Summary.coordinator_path
    $pwshPath = Join-Path $PSHOME 'pwsh.exe'
    $null = Assert-NormalFile -Path $pwshPath -Label 'PowerShell executable'
    $script:Summary.powershell_executable = $pwshPath

    $backendPath = Join-Path $repositoryRoot 'src\s2a_network_backend.sv'
    $observedBackendHash = Get-Sha256Literal -Path $backendPath
    $script:Summary.observed_backend_sha256 = $observedBackendHash
    if ($observedBackendHash -cne $expectedBackendHash) { throw "当前 backend SHA 与传入冻结值不一致：$observedBackendHash" }

    $pythonPath = $script:ApprovedPythonPath
    $null = Assert-NormalFile -Path $pythonPath -Label '固定 Python'
    $pythonVersionCheck = Invoke-CapturedProcess -ExecutablePath $pythonPath -Arguments @('--version') -WorkingDirectory $repositoryRoot
    $pythonVersionStdout = ([string]$pythonVersionCheck.stdout).Trim()
    $script:Summary.pinned_python_version_stdout = $pythonVersionStdout
    $script:Summary.pinned_python_version_exit_code = $pythonVersionCheck.exit_code
    if ($pythonVersionCheck.exit_code -ne 0 -or $pythonVersionStdout -cne $script:Summary.pinned_python_version_expected) {
        throw "固定 Python 版本断言失败：exit=$($pythonVersionCheck.exit_code)，stdout='$pythonVersionStdout'。"
    }
    $pythonDirectory = Split-Path -Parent $pythonPath
    $env:PATH = $pythonDirectory + [System.IO.Path]::PathSeparator + $env:PATH
    $resolvedPython = (Get-Command -Name 'python.exe' -CommandType Application -ErrorAction Stop).Path
    if ([System.IO.Path]::GetFullPath($resolvedPython) -ine [System.IO.Path]::GetFullPath($pythonPath)) {
        throw "批 worker 的 python.exe 未解析到固定 Python：$resolvedPython"
    }
    $script:Summary.pinned_python_sha256 = Get-Sha256Literal -Path $pythonPath

    $script:SummaryPath = Join-Path $evidenceRoot ("unattended_continuation_{0}.json" -f $RunId)
    if (Test-Path -LiteralPath $script:SummaryPath) { throw "拒绝覆盖既有 coordinator summary：$($script:SummaryPath)" }

    $mutexKey = [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData([System.Text.Encoding]::UTF8.GetBytes(($evidenceRoot.ToLowerInvariant() + '|' + $RunId.ToLowerInvariant()))))
    $script:CoordinatorLock = [System.Threading.Mutex]::new($false, ('Local\FPGA_S2A_T68_' + $mutexKey))
    try {
        $script:CoordinatorLockOwned = $script:CoordinatorLock.WaitOne(0)
    } catch [System.Threading.AbandonedMutexException] {
        $script:CoordinatorLockOwned = $true
    }
    if (-not $script:CoordinatorLockOwned) { throw '同一 EvidenceDirectory/RunId 已有 continuation 在运行，拒绝并发执行。' }
    if (Test-Path -LiteralPath $script:SummaryPath) { throw "已有 continuation 已先写入终态 summary：$($script:SummaryPath)" }
    $script:SummaryWritable = $true

    $dispatchDirectory = Join-Path $evidenceRoot 'batch_dispatch'
    $schedulerPath = Join-Path $repositoryRoot 'verification\run_s2a_t68_batch_verilator.ps1'
    $runnerPath = Join-Path $repositoryRoot 'verification\run_s2a_network_backend_verilator.ps1'
    $existingBatch = Get-ExistingBatchState -DispatchDirectory $dispatchDirectory -EvidenceRoot $evidenceRoot -ExpectedRunId $RunId `
        -ExpectedBackendHash $expectedBackendHash -SchedulerPath $schedulerPath -RunnerPath $runnerPath
    $batchSummaryPath = Join-Path $dispatchDirectory 'batch_summary.json'
    $script:Summary.batch = [ordered]@{
        status = $null
        scheduler_path = $schedulerPath
        scheduler_sha256 = $null
        process_exit_code = $null
        summary_path = $null
        summary_sha256 = $null
        stdout_path = $null
        stdout_sha256 = $null
        stderr_path = $null
        stderr_sha256 = $null
        sample0_snapshot_sha256 = $null
        existing_dispatch_wait_limit_hours = 72
        existing_dispatch_poll_interval_seconds = 30
        existing_dispatch_wait_seconds = $existingBatch.wait_seconds
        message = $null
    }

    $continueToD9 = $false
    $launchScheduler = $false
    if ($existingBatch.state -eq 'PASS') {
        $script:Summary.batch.status = 'EXISTING_PASS'
        $script:Summary.batch.summary_path = $existingBatch.summary_path
        $script:Summary.batch.summary_sha256 = $existingBatch.summary_sha256
        $script:Summary.batch.scheduler_sha256 = $existingBatch.summary.scheduler_sha256
        $script:Summary.batch.sample0_snapshot_sha256 = $existingBatch.summary.sample0_snapshot.sha256
        $continueToD9 = $true
    } elseif ($existingBatch.state -eq 'TIMEOUT') {
        $script:Summary.batch.status = 'WAIT_TIMEOUT_NO_RESTART'
        $script:Summary.batch.summary_path = $existingBatch.summary_path
        $script:Summary.batch.summary_sha256 = $existingBatch.summary_sha256
        $script:Summary.batch.message = $existingBatch.message
        $script:Summary.status = 'EXISTING_BATCH_WAIT_TIMEOUT_NO_RESTART'
    } elseif ($existingBatch.state -eq 'FAILED') {
        $script:Summary.batch.status = 'STOP_EXISTING_BATCH_NOT_PASS'
        $script:Summary.batch.summary_path = $existingBatch.summary_path
        $script:Summary.batch.summary_sha256 = $existingBatch.summary_sha256
        $script:Summary.batch.message = $existingBatch.message
        $script:Summary.status = 'STOP_EXISTING_BATCH_NO_DUPLICATE'
    } else {
        $launchScheduler = $true
    }

    if ($launchScheduler) {
        $sample0Directory = Join-Path $evidenceRoot (Join-Path 'runs\sample_000' $RunId)
        $sample0RecordPath = Join-Path $sample0Directory 'simulation_execution_record.json'
        $script:Summary.sample0 = [ordered]@{
            terminal_record_path = $sample0RecordPath
            terminal_record_sha256 = $null
            terminal_record_status = $null
            exit_code = $null
            runner_exit_code = $null
            wait_limit_hours = 24
            poll_interval_seconds = 30
            read_error = $null
        }
        $script:Summary.status = 'WAITING_SAMPLE0_TERMINAL'
        $waitResult = Wait-Sample0TerminalRecord -RecordPath $sample0RecordPath -MaximumWait $script:Sample0WaitLimit -PollInterval $script:Sample0PollInterval
        if ($waitResult.state -eq 'TIMEOUT') {
            $script:Summary.status = 'SAMPLE0_WAIT_TIMEOUT_24H'
            $script:Summary.sample0.terminal_record_status = 'NOT_OBSERVED'
            $script:Summary.sample0.read_error = $waitResult.read_error
        } elseif ($waitResult.state -eq 'INVALID') {
            $script:Summary.status = 'SAMPLE0_TERMINAL_RECORD_INVALID'
            $script:Summary.sample0.terminal_record_status = 'INVALID'
            $script:Summary.sample0.read_error = $waitResult.read_error
        } else {
            $sample0Record = $waitResult.record
            $script:Summary.sample0.terminal_record_sha256 = Get-Sha256Literal -Path $sample0RecordPath
            $script:Summary.sample0.exit_code = $sample0Record.exit_code
            $script:Summary.sample0.runner_exit_code = $sample0Record.runner_exit_code
            $sample0Passed = Test-Sample0Passed -Record $sample0Record -ExpectedRunId $RunId
            $script:Summary.sample0.terminal_record_status = if ($sample0Passed) { 'PASS_SAMPLE0_TERMINAL' } else { 'FAIL_SAMPLE0_TERMINAL' }
            if (-not $sample0Passed) {
                $script:Summary.status = 'STOP_SAMPLE0_FAILED'
            } else {
                $batchRunnerPath = $schedulerPath
                $batchRunnerHash = Get-Sha256Literal -Path $batchRunnerPath
                $script:Summary.batch.scheduler_sha256 = $batchRunnerHash

                $recheckedBatch = Get-ExistingBatchState -DispatchDirectory $dispatchDirectory -EvidenceRoot $evidenceRoot -ExpectedRunId $RunId `
                    -ExpectedBackendHash $expectedBackendHash -SchedulerPath $schedulerPath -RunnerPath $runnerPath
                if ($recheckedBatch.state -eq 'PASS') {
                    $script:Summary.batch.status = 'EXISTING_PASS'
                    $script:Summary.batch.summary_path = $recheckedBatch.summary_path
                    $script:Summary.batch.summary_sha256 = $recheckedBatch.summary_sha256
                    $script:Summary.batch.scheduler_sha256 = $recheckedBatch.summary.scheduler_sha256
                    $script:Summary.batch.sample0_snapshot_sha256 = $recheckedBatch.summary.sample0_snapshot.sha256
                    $continueToD9 = $true
                } elseif ($recheckedBatch.state -ne 'ABSENT') {
                    $script:Summary.batch.status = if ($recheckedBatch.state -eq 'TIMEOUT') { 'WAIT_TIMEOUT_NO_RESTART' } else { 'STOP_EXISTING_BATCH_NOT_PASS' }
                    $script:Summary.batch.summary_path = $recheckedBatch.summary_path
                    $script:Summary.batch.summary_sha256 = $recheckedBatch.summary_sha256
                    $script:Summary.batch.message = $recheckedBatch.message
                    $script:Summary.batch.existing_dispatch_wait_seconds = $recheckedBatch.wait_seconds
                    $script:Summary.status = if ($recheckedBatch.state -eq 'TIMEOUT') { 'EXISTING_BATCH_WAIT_TIMEOUT_NO_RESTART' } else { 'STOP_EXISTING_BATCH_NO_DUPLICATE' }
                } else {
                    $batchStdoutPath = Join-Path $evidenceRoot ("unattended_batch_stdout_{0}.log" -f $RunId)
                    $batchStderrPath = Join-Path $evidenceRoot ("unattended_batch_stderr_{0}.log" -f $RunId)
                    foreach ($path in @($batchSummaryPath, $batchStdoutPath, $batchStderrPath)) {
                        if (Test-Path -LiteralPath $path) { throw "启动前发现已有批次 summary/log，拒绝覆盖：$path" }
                    }
                    $arguments = @(
                        '-NoLogo', '-NoProfile', '-NonInteractive', '-File', $batchRunnerPath,
                        '-EvidenceDirectory', $evidenceRoot,
                        '-RunId', $RunId,
                        '-ExpectedBackendSha256', $expectedBackendHash,
                        '-FirstIndex', '1', '-LastIndex', '108', '-MaxWorkers', '8'
                    )
                    $script:Summary.batch.status = 'RUNNING_EXISTING_SCHEDULER'
                    $execution = Invoke-CapturedProcess -ExecutablePath $pwshPath -Arguments $arguments -WorkingDirectory $repositoryRoot
                    Write-NewUtf8File -Path $batchStdoutPath -Text $execution.stdout
                    Write-NewUtf8File -Path $batchStderrPath -Text $execution.stderr
                    $script:Summary.batch.process_exit_code = $execution.exit_code
                    $script:Summary.batch.stdout_path = $batchStdoutPath
                    $script:Summary.batch.stdout_sha256 = Get-Sha256Literal -Path $batchStdoutPath
                    $script:Summary.batch.stderr_path = $batchStderrPath
                    $script:Summary.batch.stderr_sha256 = Get-Sha256Literal -Path $batchStderrPath

                    if (Test-Path -LiteralPath $batchSummaryPath -PathType Leaf) {
                        $batchSummary = Read-JsonObject -Path $batchSummaryPath -Label 'scheduler batch_summary.json'
                        $script:Summary.batch.summary_path = $batchSummaryPath
                        $script:Summary.batch.summary_sha256 = Get-Sha256Literal -Path $batchSummaryPath
                        try {
                            Assert-PassingBatchSummary -BatchSummary $batchSummary -EvidenceRoot $evidenceRoot -ExpectedRunId $RunId `
                                -ExpectedBackendHash $expectedBackendHash -ExpectedSchedulerHash (Get-Sha256Literal -Path $schedulerPath) `
                                -ExpectedRunnerHash (Get-Sha256Literal -Path $runnerPath)
                            if ($execution.exit_code -ne 0) { throw "scheduler exit code 为 $($execution.exit_code)，即使 summary 显示 PASS 也拒绝继续。" }
                            $script:Summary.batch.status = 'PASS_108_RUNNERS'
                            $script:Summary.batch.scheduler_sha256 = $batchSummary.scheduler_sha256
                            $script:Summary.batch.sample0_snapshot_sha256 = $batchSummary.sample0_snapshot.sha256
                            $continueToD9 = $true
                        } catch {
                            $script:Summary.batch.status = 'FAIL_BATCH_NOT_PASS'
                            $script:Summary.batch.message = $_.Exception.Message
                            $script:Summary.status = 'STOP_BATCH_FAILED'
                        }
                    } else {
                        $script:Summary.batch.status = 'FAIL_BATCH_SUMMARY_MISSING'
                        $script:Summary.batch.message = 'scheduler 结束但没有 batch_summary.json；不重启、不重试。'
                        $script:Summary.status = 'STOP_BATCH_FAILED'
                    }
                }
            }
        }
    }

    if ($continueToD9) {
        $sample0SimulationHash = if ($null -ne $script:Summary.sample0) { [string]$script:Summary.sample0.terminal_record_sha256 } else { $null }
        $script:Summary.d9 = Invoke-VerifiedD9 -EvidenceRoot $evidenceRoot -ExpectedRunId $RunId -RepositoryRoot $repositoryRoot `
            -PythonPath $pythonPath -ExpectedBackendHash $expectedBackendHash `
            -ExpectedSample0SnapshotHash $script:Summary.batch.sample0_snapshot_sha256 `
            -ExpectedSample0SimulationHash $sample0SimulationHash
        if ($script:Summary.d9.passed) {
            $script:Summary.status = 'PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9'
            $script:Summary.stage2a_pass = $false
        } else {
            $script:Summary.status = 'STOP_D9_FAILED'
        }
    }
} catch {
    $script:Summary.status = 'COORDINATOR_ERROR'
    $script:Summary.error = $_.Exception.ToString()
    Write-Output ("T68 unattended continuation error: {0}" -f $_.Exception.Message)
} finally {
    if ($script:SummaryWritable -and $null -ne $script:SummaryPath) {
        try {
            if (-not (Test-Path -LiteralPath $script:SummaryPath)) {
                Write-NewJsonFile -Path $script:SummaryPath -Value $script:Summary
                Write-Output ("T68 unattended continuation terminal status={0} summary={1}" -f $script:Summary.status, $script:SummaryPath)
            } else {
                Write-Output ("拒绝覆盖已出现的 coordinator summary：{0}" -f $script:SummaryPath)
                $script:Summary.status = 'COORDINATOR_SUMMARY_PATH_COLLISION'
            }
        } catch {
            Write-Output ("无法写入 coordinator terminal summary：{0}" -f $_.Exception.Message)
            $script:Summary.status = 'COORDINATOR_SUMMARY_WRITE_FAILED'
        }
    }
    if ($script:CoordinatorLockOwned -and $null -ne $script:CoordinatorLock) {
        try { $script:CoordinatorLock.ReleaseMutex() } catch { }
    }
    if ($null -ne $script:CoordinatorLock) { $script:CoordinatorLock.Dispose() }
}

if ($script:Summary.status -ceq 'PASS_109_ACTUAL_PL_HEADS_VS_FROZEN_CPU_D9') { exit 0 }
exit 1
