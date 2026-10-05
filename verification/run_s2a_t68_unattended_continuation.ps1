[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$EvidenceDirectory,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9_-]+$')]
    [string]$RunId,

    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[0-9a-fA-F]{64}$')]
    [string]$ExpectedBackendSha256,

    [ValidatePattern('^[0-9a-f]{64}$')]
    [string]$ResumeFailedCoordinatorSha256,

    [ValidatePattern('^[0-9a-f]{64}$')]
    [string]$ResumeFailedRecoverySha256
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script:ApprovedBackendSha256 = '3910bc69d1630eff3f8740eed74e03f5328319da24abb3f9e755808afd5ec154'
$script:ApprovedPythonPath = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$script:ApprovedPythonModulePath = 'C:\Users\22061\AppData\Local\Programs\Python\Python312\Lib\site-packages'
$script:ExpectedPowerShellVersion = '7.6.5'
$script:ExpectedT29ReportSha256 = '24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231'
$script:ExpectedT25IndexSha256 = 'cbda3f257ac626252901f978464b93c5c2e909634e30c1bcf70cd588f0f6950d'
$script:ExpectedD9DecoderSha256 = '0be8e2dc0878116b5239a20a397f4f063de7b33c2ee38e1d0aadf1ced7d365c6'
$script:ExpectedT29CanonicalSha256 = '10a4116904261ee092940e1e354bed64dbd944023f6d8fdae5cf2079ad9b4c63'
$script:ExpectedT29RegeneratedCanonicalSha256 = '1cd26b9e655a9e8faa6d9f614b4569fecda8fb236cf9237e6e72726469de8cdd'
$script:ApprovedD9RecoveryRunId = 'repair109_20261003_194620'
$script:ApprovedD9RecoveryEvidenceDirectory = 'D:\FPGA_Competition\report\evidence\S2A-T68\repair109_20261003_194620'
$script:ExpectedD9RecoverySummarySha256 = '4c187dda223209d2a4308dd7fbe210f34ff5be06bb2cce624229cc477e664cda'
$script:ExpectedD9Attempt1StdoutSha256 = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
$script:ExpectedD9Attempt1StderrSha256 = '38b3c4ec5b626ac905e23e6fdeb99090616b21afc470b4df04f257de14f87ef5'
$script:ExpectedD9FailedCoordinatorSha256 = '36f9543827e71b08907cbe10a8aef37a91388d1300c683008130935dba2f1542'
$script:ExpectedD9RecoveryBatchSummarySha256 = '93cb51989c98fdb074c5c5857acd9842ee7902c8a27d09c655ae555c41ac2e38'
$script:ExpectedD9ReplayEvidencePath = 'D:\FPGA_Competition\report\evidence\S2A-T68\repair109_20261003_194620\t29_runtime_normalization_preflight_20261005.json'
$script:ExpectedD9ReplayEvidenceSha256 = '0ad4b0fd6ffce3d2e624c8879a04f8f51daa308685352045e95d32c6e1b61e15'
$script:ExpectedD9FailureVerifierCommit = '10ef3a499a976c3005adcbed0399bfc2d7279e5c'
$script:ExpectedD9FailureVerifierBlobOid = 'c60b04c9a046a0125cf9f7a63652245c49442402'
$script:ExpectedD9FailureVerifierSha256 = 'a86ca04a5f763616030cdf774672d9e7e3808942e216f8132ba1c3f50e5b3f0e'
$script:ExpectedD9ReplayExitCode = 2
$script:ExpectedD9ReplayStdoutSha256 = 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
$script:ExpectedD9ReplayStderrSha256 = 'de34afc0edbea18e22e5e1fba101ef190fa4f9084e0ea6974b69d88f7ff41a1e'
$script:ExpectedD9FailureSummaryError = 'System.Management.Automation.RuntimeException: D9 verifier 未生成预期报告。'
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
    d9_recovery = $null
    error = $null
    created_utc = [DateTime]::UtcNow.ToString('o')
}

function Assert-ApprovedPythonCommandResolution {
    param(
        [Parameter(Mandatory = $true)][string]$ApprovedPath,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$ResolvedCommands
    )

    $approvedItem = Get-Item -LiteralPath $ApprovedPath -ErrorAction Stop
    if ($approvedItem.PSIsContainer -or (($approvedItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "固定 Python 必须是普通文件：$ApprovedPath"
    }
    if ($ResolvedCommands.Count -lt 1) {
        throw 'PATH 中未解析到 python.exe。'
    }

    $resolvedPath = [string]$ResolvedCommands[0].Path
    if ([string]::IsNullOrWhiteSpace($resolvedPath)) {
        throw 'PATH 首选 python.exe 没有可验证的文件路径。'
    }
    $approvedFullPath = [System.IO.Path]::GetFullPath($approvedItem.FullName)
    if ([System.IO.Path]::GetFullPath($resolvedPath) -ine $approvedFullPath) {
        throw "批 worker 的 python.exe 首选解析不等于固定 Python：$resolvedPath"
    }
    return $approvedFullPath
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

function Assert-RecoveryBoundFile {
    param(
        [Parameter(Mandatory = $true)][string]$RecordedPath,
        [Parameter(Mandatory = $true)][string]$ExpectedPath,
        [Parameter(Mandatory = $true)][string]$RecordedSha256,
        [Parameter(Mandatory = $true)][string]$Label
    )
    if (-not [System.IO.Path]::IsPathRooted($RecordedPath) -or
        [System.IO.Path]::GetFullPath($RecordedPath) -ine [System.IO.Path]::GetFullPath($ExpectedPath) -or
        $RecordedSha256 -notmatch '^[0-9a-f]{64}$') {
        throw "$Label 的记录路径或 SHA-256 未绑定到本次证据。"
    }
    $normalPath = Assert-NormalFile -Path $ExpectedPath -Label $Label
    if ((Get-Sha256Literal -Path $normalPath) -cne $RecordedSha256) {
        throw "$Label 的实际 SHA-256 与原 coordinator 终态记录不符。"
    }
    return $normalPath
}

function Assert-FailedBatchValidationRecovery {
    param(
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$Prior,
        [Parameter(Mandatory = $true)][string]$SummaryPath,
        [Parameter(Mandatory = $true)][string]$ExpectedSummaryHash,
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$ExpectedRunId,
        [Parameter(Mandatory = $true)][string]$ExpectedBackendHash,
        [Parameter(Mandatory = $true)][string]$SchedulerPath,
        [Parameter(Mandatory = $true)][string]$RunnerPath
    )
    if ($Prior.schema_version -isnot [string] -or $Prior.schema_version -cne 'gestureforge_s2a_t68_unattended_continuation_v1' -or
        $Prior.status -isnot [string] -or $Prior.status -cne 'STOP_BATCH_FAILED' -or
        $Prior.stage2a_pass -isnot [bool] -or $Prior.stage2a_pass -ne $false -or
        $Prior.run_id -isnot [string] -or $Prior.run_id -cne $ExpectedRunId -or
        $Prior.evidence_directory -isnot [string] -or $Prior.evidence_directory -cne $EvidenceRoot -or
        $Prior.expected_backend_sha256 -isnot [string] -or
        $Prior.expected_backend_sha256 -cne $ExpectedBackendHash -or $Prior.observed_backend_sha256 -cne $ExpectedBackendHash -or
        -not $Prior.Contains('d9') -or $null -ne $Prior.d9 -or
        -not $Prior.Contains('error') -or $null -ne $Prior.error -or
        $Prior.sample0 -isnot [System.Collections.IDictionary] -or
        $Prior.batch -isnot [System.Collections.IDictionary]) {
        throw '旧 STOP_BATCH_FAILED summary 不符合 false-stop 白名单。'
    }

    $expectedSummaryPath = Join-Path $EvidenceRoot ("unattended_continuation_{0}.json" -f $ExpectedRunId)
    if ([System.IO.Path]::GetFullPath($SummaryPath) -ine [System.IO.Path]::GetFullPath($expectedSummaryPath)) {
        throw '旧 coordinator summary 路径与本次 RunId 不匹配。'
    }
    $null = Assert-RecoveryBoundFile -RecordedPath $SummaryPath -ExpectedPath $expectedSummaryPath `
        -RecordedSha256 $ExpectedSummaryHash -Label '旧 coordinator summary'

    $sample0 = $Prior.sample0
    $batch = $Prior.batch
    if ($sample0.terminal_record_status -isnot [string] -or $sample0.terminal_record_status -cne 'PASS_SAMPLE0_TERMINAL' -or
        $sample0.exit_code -isnot [long] -or
        $sample0.runner_exit_code -isnot [long] -or $sample0.exit_code -ne 0 -or $sample0.runner_exit_code -ne 0 -or
        -not $sample0.Contains('read_error') -or $null -ne $sample0.read_error -or
        $sample0.terminal_record_sha256 -isnot [string] -or
        $sample0.terminal_record_sha256 -notmatch '^[0-9a-f]{64}$' -or
        $batch.status -isnot [string] -or $batch.status -cne 'FAIL_BATCH_NOT_PASS' -or
        $batch.process_exit_code -isnot [long] -or $batch.process_exit_code -ne 0 -or
        $batch.message -isnot [string] -or
        $batch.message -cne 'batch_summary.json 的 scheduler 源码冻结证据不完整或不一致。') {
        throw '旧 STOP_BATCH_FAILED 的 sample0 或批次失败特征不符合 false-stop 白名单。'
    }

    $runsDirectory = Assert-NormalDirectory -Path (Join-Path $EvidenceRoot 'runs') -Label 'sample000 runs 目录'
    $sample0ParentDirectory = Assert-NormalDirectory -Path (Join-Path $runsDirectory 'sample_000') -Label 'sample000 目录'
    $sample0RunDirectory = Assert-NormalDirectory -Path (Join-Path $sample0ParentDirectory $ExpectedRunId) -Label 'sample000 RunId 目录'
    $sample0RecordPath = Join-Path $sample0RunDirectory 'simulation_execution_record.json'
    $normalSample0RecordPath = Assert-RecoveryBoundFile -RecordedPath ([string]$sample0.terminal_record_path) `
        -ExpectedPath $sample0RecordPath -RecordedSha256 ([string]$sample0.terminal_record_sha256) `
        -Label 'sample000 仿真终态记录'
    $sample0Record = Read-JsonObject -Path $normalSample0RecordPath -Label 'sample000 仿真终态记录'
    if (-not (Test-Sample0Passed -Record $sample0Record -ExpectedRunId $ExpectedRunId)) {
        throw 'sample000 仿真终态记录内容不通过冻结 PASS 条件。'
    }

    $dispatchDirectory = Join-Path $EvidenceRoot 'batch_dispatch'
    $dispatchDirectory = Assert-NormalDirectory -Path $dispatchDirectory -Label 'batch_dispatch 目录'
    $expectedBatchSummaryPath = Join-Path $dispatchDirectory 'batch_summary.json'
    $expectedStdoutPath = Join-Path $EvidenceRoot ("unattended_batch_stdout_{0}.log" -f $ExpectedRunId)
    $expectedStderrPath = Join-Path $EvidenceRoot ("unattended_batch_stderr_{0}.log" -f $ExpectedRunId)
    $normalBatchSummaryPath = Assert-RecoveryBoundFile -RecordedPath ([string]$batch.summary_path) `
        -ExpectedPath $expectedBatchSummaryPath -RecordedSha256 ([string]$batch.summary_sha256) `
        -Label 'batch_summary.json'
    $null = Assert-RecoveryBoundFile -RecordedPath ([string]$batch.stdout_path) -ExpectedPath $expectedStdoutPath `
        -RecordedSha256 ([string]$batch.stdout_sha256) -Label 'batch stdout log'
    $null = Assert-RecoveryBoundFile -RecordedPath ([string]$batch.stderr_path) -ExpectedPath $expectedStderrPath `
        -RecordedSha256 ([string]$batch.stderr_sha256) -Label 'batch stderr log'

    $batchSummary = Read-JsonObject -Path $normalBatchSummaryPath -Label '失败前已完成的 batch summary'
    if ($batchSummary.scheduler_path -isnot [string] -or
        [System.IO.Path]::GetFullPath($batchSummary.scheduler_path) -ine [System.IO.Path]::GetFullPath($SchedulerPath)) {
        throw 'batch_summary.json 的 scheduler 路径不匹配当前仓库。'
    }
    $normalSchedulerPath = Assert-NormalFile -Path $SchedulerPath -Label '固定 batch scheduler 源码'
    $normalRunnerPath = Assert-NormalFile -Path $RunnerPath -Label '固定 batch worker 源码'
    $schedulerHash = Get-Sha256Literal -Path $normalSchedulerPath
    if ($batch.scheduler_path -isnot [string] -or
        [System.IO.Path]::GetFullPath($batch.scheduler_path) -ine [System.IO.Path]::GetFullPath($normalSchedulerPath) -or
        $batch.scheduler_sha256 -cne $schedulerHash) {
        throw '旧 coordinator 记录中的 scheduler 源码绑定与当前仓库不符。'
    }
    Assert-PassingBatchSummary -BatchSummary $batchSummary -EvidenceRoot $EvidenceRoot -ExpectedRunId $ExpectedRunId `
        -ExpectedBackendHash $ExpectedBackendHash -ExpectedSchedulerHash $schedulerHash `
        -ExpectedRunnerHash (Get-Sha256Literal -Path $normalRunnerPath)
}

function Assert-FailedCoordinatorRecovery {
    param(
        [string]$SummaryPath, [string]$ExpectedSummaryHash, [string]$EvidenceRoot,
        [string]$ExpectedRunId, [string]$ExpectedBackendHash,
        [string]$SchedulerPath, [string]$RunnerPath
    )
    $null = Assert-NormalFile -Path $SummaryPath -Label '原失败 coordinator summary'
    if ((Get-Sha256Literal -Path $SummaryPath) -cne $ExpectedSummaryHash) { throw '原失败 coordinator summary SHA 不匹配。' }
    $prior = Read-JsonObject -Path $SummaryPath -Label '原失败 coordinator summary'
    if ($prior.status -ceq 'COORDINATOR_ERROR') {
        if ($prior.schema_version -cne 'gestureforge_s2a_t68_unattended_continuation_v1' -or
            $prior.stage2a_pass -ne $false -or
            $prior.run_id -cne $ExpectedRunId -or $prior.evidence_directory -cne $EvidenceRoot -or
            $prior.expected_backend_sha256 -cne $ExpectedBackendHash -or $prior.observed_backend_sha256 -cne $ExpectedBackendHash -or
            $prior.sample0.terminal_record_status -cne 'PASS_SAMPLE0_TERMINAL' -or
            $prior.sample0.exit_code -ne 0 -or $prior.sample0.runner_exit_code -ne 0 -or
            $prior.batch.status -cne 'RUNNING_EXISTING_SCHEDULER' -or $null -ne $prior.batch.process_exit_code -or
            $null -ne $prior.d9 -or $prior.error -notlike '*Cannot bind argument to parameter ''Text'' because it is an empty string.*') {
            throw '原失败 summary 不符合空日志故障的单次恢复条件。'
        }
        $recordPath = Join-Path $EvidenceRoot ("runs\sample_000\{0}\simulation_execution_record.json" -f $ExpectedRunId)
        if ($prior.sample0.terminal_record_path -cne $recordPath -or
            (Get-Sha256Literal -Path $recordPath) -cne $prior.sample0.terminal_record_sha256) { throw '原 sample0 终态绑定不匹配。' }
        if (Test-Path -LiteralPath (Join-Path $EvidenceRoot 'batch_dispatch')) { throw '单次恢复要求尚无 batch_dispatch；拒绝重复派发。' }
        return [ordered]@{ kind = 'SAMPLE0_EMPTY_LOG'; sample0 = $null }
    }

    if ($prior.status -ceq 'STOP_BATCH_FAILED') {
        Assert-FailedBatchValidationRecovery -Prior $prior -SummaryPath $SummaryPath -ExpectedSummaryHash $ExpectedSummaryHash `
            -EvidenceRoot $EvidenceRoot -ExpectedRunId $ExpectedRunId -ExpectedBackendHash $ExpectedBackendHash `
            -SchedulerPath $SchedulerPath -RunnerPath $RunnerPath
        return [ordered]@{
            kind = 'BATCH_FALSE_STOP_VALIDATION'
            sample0 = $prior.sample0
            batch_summary_sha256 = $prior.batch.summary_sha256
        }
    }
    throw '原 coordinator summary 状态不在允许的单次恢复白名单中。'
}

function Assert-FailedD9Recovery {
    param(
        [Parameter(Mandatory = $true)][string]$SummaryPath,
        [Parameter(Mandatory = $true)][string]$ExpectedSummaryHash,
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$ExpectedRunId,
        [Parameter(Mandatory = $true)][string]$ExpectedBackendHash,
        [Parameter(Mandatory = $true)][string]$SchedulerPath,
        [Parameter(Mandatory = $true)][string]$RunnerPath
    )
    if ($ExpectedRunId -cne $script:ApprovedD9RecoveryRunId -or
        [System.IO.Path]::GetFullPath($EvidenceRoot) -cne $script:ApprovedD9RecoveryEvidenceDirectory -or
        $ExpectedSummaryHash -cne $script:ExpectedD9RecoverySummarySha256) {
        throw 'D9 attempt2 恢复仅允许固定 RunId、evidence 目录与首次 recovery summary SHA。'
    }
    $expectedPriorPath = Join-Path $EvidenceRoot ("unattended_continuation_{0}_recovery.json" -f $ExpectedRunId)
    if ([System.IO.Path]::GetFullPath($SummaryPath) -cne [System.IO.Path]::GetFullPath($expectedPriorPath)) {
        throw 'D9 恢复输入路径必须精确匹配固定 RunId 的 recovery.json。'
    }
    $normalPriorPath = Assert-RecoveryBoundFile -RecordedPath $SummaryPath -ExpectedPath $expectedPriorPath `
        -RecordedSha256 $ExpectedSummaryHash -Label '首次 D9 失败 recovery summary'
    $prior = Read-JsonObject -Path $normalPriorPath -Label '首次 D9 失败 recovery summary'
    $replayEvidencePath = Assert-NormalFile -Path $script:ExpectedD9ReplayEvidencePath -Label 'T29 固定输入只读复放证据'
    if ([System.IO.Path]::GetFullPath($replayEvidencePath) -cne [System.IO.Path]::GetFullPath($script:ExpectedD9ReplayEvidencePath) -or
        (Get-Sha256Literal -Path $replayEvidencePath) -cne $script:ExpectedD9ReplayEvidenceSha256) {
        throw 'T29 固定输入只读复放证据路径或 SHA-256 与白名单不符。'
    }
    $replayEvidence = Read-JsonObject -Path $replayEvidencePath -Label 'T29 固定输入只读复放证据'
    if ($replayEvidence.schema_version -isnot [string] -or
        $replayEvidence.schema_version -cne 'gestureforge_s2a_t68_t29_recovery_preflight_v1' -or
        $replayEvidence.run_id -isnot [string] -or $replayEvidence.run_id -cne $script:ApprovedD9RecoveryRunId -or
        $replayEvidence.evidence_root -isnot [string] -or $replayEvidence.evidence_root -cne $script:ApprovedD9RecoveryEvidenceDirectory -or
        $replayEvidence.fixed_environment -isnot [System.Collections.IDictionary] -or
        $replayEvidence.t29_readonly_preflight -isnot [System.Collections.IDictionary] -or
        $replayEvidence.original_failure_replay -isnot [System.Collections.IDictionary] -or
        $replayEvidence.original_attempt1_artifacts -isnot [System.Collections.IDictionary]) {
        throw 'T29 固定输入只读复放证据 schema、RunId、evidence root 或嵌套结构不符。'
    }
    $replayEnvironment = $replayEvidence.fixed_environment
    $t29Preflight = $replayEvidence.t29_readonly_preflight
    $replay = $replayEvidence.original_failure_replay
    $attempt1Artifacts = $replayEvidence.original_attempt1_artifacts
    $replayRecoveryPath = Join-Path $script:ApprovedD9RecoveryEvidenceDirectory 'unattended_continuation_repair109_20261003_194620_recovery.json'
    $replayStdoutPath = Join-Path $script:ApprovedD9RecoveryEvidenceDirectory 'unattended_d9_stdout_repair109_20261003_194620.log'
    $replayStderrPath = Join-Path $script:ApprovedD9RecoveryEvidenceDirectory 'unattended_d9_stderr_repair109_20261003_194620.log'
    $preflightRuntime = $t29Preflight.runtime_versions
    if ($preflightRuntime -isnot [System.Collections.IDictionary] -or
        $preflightRuntime.python -isnot [System.Collections.IDictionary] -or
        $preflightRuntime.zlib_compile -isnot [System.Collections.IDictionary] -or
        $preflightRuntime.zlib_runtime -isnot [System.Collections.IDictionary]) {
        throw 'T29 runtime normalization 字段必须是对象。'
    }
    if ($replayEnvironment.python_path -isnot [string] -or
        $replayEnvironment.python_path -cne $script:ApprovedPythonPath -or
        $replayEnvironment.python_version -isnot [string] -or $replayEnvironment.python_version -cne '3.12.14' -or
        $replayEnvironment.pythonpath -isnot [string] -or $replayEnvironment.pythonpath -cne $script:ApprovedPythonModulePath -or
        $t29Preflight.status -isnot [string] -or $t29Preflight.status -cne 'PASS_T29_REGENERATION_EXCEPT_RUNTIME_VERSION_FIELDS' -or
        $t29Preflight.exit_code -isnot [long] -or $t29Preflight.exit_code -ne 0 -or
        $t29Preflight.sample_count -isnot [long] -or $t29Preflight.sample_count -ne 109 -or
        $t29Preflight.frozen_canonical_sha256 -isnot [string] -or $t29Preflight.frozen_canonical_sha256 -cne $script:ExpectedT29CanonicalSha256 -or
        $t29Preflight.regenerated_canonical_sha256 -isnot [string] -or $t29Preflight.regenerated_canonical_sha256 -cne $script:ExpectedT29RegeneratedCanonicalSha256 -or
        $preflightRuntime -isnot [System.Collections.IDictionary] -or
        $preflightRuntime.python.frozen -cne '3.12.10' -or $preflightRuntime.python.regenerated -cne '3.12.14' -or
        $preflightRuntime.zlib_compile.frozen -cne '1.3.1' -or $preflightRuntime.zlib_compile.regenerated -cne '1.3.2' -or
        $preflightRuntime.zlib_runtime.frozen -cne '1.3.1' -or $preflightRuntime.zlib_runtime.regenerated -cne '1.3.2') {
        throw 'T29 只读预检结果与固定 runtime normalization 证据不符。'
    }
    if ($replay.mode -isnot [string] -or $replay.mode -cne 'memory_exec_of_git_source_with___main__' -or
        $replay.source_commit -isnot [string] -or $replay.source_commit -cne $script:ExpectedD9FailureVerifierCommit -or
        $replay.source_file -isnot [string] -or $replay.source_file -cne 'verification/verify_s2a_t68_d9_outputs.py' -or
        $replay.source_bytes -isnot [long] -or $replay.source_bytes -ne 32602 -or
        $replay.source_sha256 -isnot [string] -or $replay.source_sha256 -cne $script:ExpectedD9FailureVerifierSha256 -or
        $replay.git_blob_oid -isnot [string] -or $replay.git_blob_oid -cne $script:ExpectedD9FailureVerifierBlobOid -or
        $replay.evidence_root -isnot [string] -or $replay.evidence_root -cne $script:ApprovedD9RecoveryEvidenceDirectory -or
        $replay.run_id -isnot [string] -or $replay.run_id -cne $script:ApprovedD9RecoveryRunId -or
        $replay.report_argument_supplied -isnot [bool] -or $replay.report_argument_supplied -ne $false -or
        $replay.exit_code -isnot [long] -or $replay.exit_code -ne $script:ExpectedD9ReplayExitCode -or
        $replay.stdout_sha256 -isnot [string] -or $replay.stdout_sha256 -cne $script:ExpectedD9ReplayStdoutSha256 -or
        $replay.stderr_sha256 -isnot [string] -or $replay.stderr_sha256 -cne $script:ExpectedD9ReplayStderrSha256 -or
        $replay.failure_class -isnot [string] -or $replay.failure_class -cne 'T29 CPU canonical regeneration mismatch') {
        throw '旧 D9 verifier 同固定输入复放的 commit、源码、输入、输出或退出码不符。'
    }
    if ([System.IO.Path]::GetFullPath([string]$attempt1Artifacts.recovery_path) -cne [System.IO.Path]::GetFullPath($replayRecoveryPath) -or
        $attempt1Artifacts.recovery_sha256 -isnot [string] -or $attempt1Artifacts.recovery_sha256 -cne $script:ExpectedD9RecoverySummarySha256 -or
        [System.IO.Path]::GetFullPath([string]$attempt1Artifacts.stdout_path) -cne [System.IO.Path]::GetFullPath($replayStdoutPath) -or
        $attempt1Artifacts.stdout_bytes -isnot [long] -or $attempt1Artifacts.stdout_bytes -ne 0 -or
        $attempt1Artifacts.stdout_sha256 -isnot [string] -or $attempt1Artifacts.stdout_sha256 -cne $script:ExpectedD9Attempt1StdoutSha256 -or
        [System.IO.Path]::GetFullPath([string]$attempt1Artifacts.stderr_path) -cne [System.IO.Path]::GetFullPath($replayStderrPath) -or
        $attempt1Artifacts.stderr_bytes -isnot [long] -or $attempt1Artifacts.stderr_bytes -ne 118 -or
        $attempt1Artifacts.stderr_sha256 -isnot [string] -or $attempt1Artifacts.stderr_sha256 -cne $script:ExpectedD9Attempt1StderrSha256) {
        throw '首轮 D9 日志与 recovery 的固定路径或字节哈希不符。'
    }
    $expectedCoordinatorPath = Join-Path (Split-Path -Parent $SchedulerPath) 'run_s2a_t68_unattended_continuation.ps1'
    if ($prior.schema_version -isnot [string] -or $prior.schema_version -cne 'gestureforge_s2a_t68_unattended_continuation_v1' -or
        $prior.status -isnot [string] -or $prior.status -cne 'COORDINATOR_ERROR' -or
        $prior.stage2a_pass -isnot [bool] -or $prior.stage2a_pass -ne $false -or
        $prior.run_id -isnot [string] -or $prior.run_id -cne $ExpectedRunId -or
        $prior.evidence_directory -isnot [string] -or $prior.evidence_directory -cne $EvidenceRoot -or
        $prior.expected_backend_sha256 -isnot [string] -or $prior.expected_backend_sha256 -cne $ExpectedBackendHash -or
        $prior.observed_backend_sha256 -isnot [string] -or $prior.observed_backend_sha256 -cne $ExpectedBackendHash -or
        $prior.coordinator_path -isnot [string] -or [System.IO.Path]::GetFullPath($prior.coordinator_path) -ine [System.IO.Path]::GetFullPath($expectedCoordinatorPath) -or
        $prior.coordinator_sha256 -isnot [string] -or $prior.coordinator_sha256 -cne $script:ExpectedD9FailedCoordinatorSha256 -or
        $prior.pinned_python_version_stdout -isnot [string] -or $prior.pinned_python_version_stdout -cne 'Python 3.12.14' -or
        $prior.pinned_python_sha256 -isnot [string] -or $prior.pinned_python_sha256 -cne '4278cf2a296f31737cae77cafeeb3dc71683094cf3b8fd6f3f02c968687e771c' -or
        $prior.python_dependency_versions -isnot [string] -or $prior.python_dependency_versions -cne '2.4.6|4.13.0' -or
        $prior.recovery_mode -isnot [string] -or $prior.recovery_mode -cne 'BATCH_FALSE_STOP_VALIDATION' -or
        -not $prior.Contains('error') -or $prior.error -isnot [string] -or
        $prior.error -cne $script:ExpectedD9FailureSummaryError -or
        -not $prior.Contains('d9') -or $null -ne $prior.d9 -or
        $prior.sample0 -isnot [System.Collections.IDictionary] -or
        $prior.batch -isnot [System.Collections.IDictionary]) {
        throw '首次 D9 失败 recovery summary 不符合严格单次恢复白名单。'
    }
    if ($prior.sample0.terminal_record_status -isnot [string] -or $prior.sample0.terminal_record_status -cne 'PASS_SAMPLE0_TERMINAL' -or
        $prior.sample0.exit_code -isnot [long] -or $prior.sample0.exit_code -ne 0 -or
        $prior.sample0.runner_exit_code -isnot [long] -or $prior.sample0.runner_exit_code -ne 0 -or
        -not $prior.sample0.Contains('read_error') -or $null -ne $prior.sample0.read_error -or
        $prior.sample0.terminal_record_sha256 -isnot [string] -or $prior.sample0.terminal_record_sha256 -notmatch '^[0-9a-f]{64}$' -or
        $prior.batch.status -isnot [string] -or $prior.batch.status -cne 'EXISTING_PASS' -or
        $prior.batch.summary_sha256 -isnot [string] -or $prior.batch.summary_sha256 -cne $script:ExpectedD9RecoveryBatchSummarySha256 -or
        $prior.batch.scheduler_sha256 -isnot [string] -or $prior.batch.sample0_snapshot_sha256 -isnot [string] -or
        $prior.batch.sample0_snapshot_sha256 -notmatch '^[0-9a-f]{64}$') {
        throw '首次 D9 失败 recovery 中 sample000 或 PASS batch 绑定无效。'
    }

    $sample0Path = Join-Path $EvidenceRoot (Join-Path 'runs\sample_000' (Join-Path $ExpectedRunId 'simulation_execution_record.json'))
    $normalSample0Path = Assert-RecoveryBoundFile -RecordedPath ([string]$prior.sample0.terminal_record_path) `
        -ExpectedPath $sample0Path -RecordedSha256 ([string]$prior.sample0.terminal_record_sha256) -Label 'sample000 终态记录'
    $sample0 = Read-JsonObject -Path $normalSample0Path -Label 'sample000 终态记录'
    if (-not (Test-Sample0Passed -Record $sample0 -ExpectedRunId $ExpectedRunId)) { throw 'sample000 终态记录不再满足 PASS。' }

    $dispatchDirectory = Assert-NormalDirectory -Path (Join-Path $EvidenceRoot 'batch_dispatch') -Label 'batch_dispatch 目录'
    $batchSummaryPath = Join-Path $dispatchDirectory 'batch_summary.json'
    $normalBatchSummaryPath = Assert-RecoveryBoundFile -RecordedPath ([string]$prior.batch.summary_path) `
        -ExpectedPath $batchSummaryPath -RecordedSha256 ([string]$prior.batch.summary_sha256) -Label 'PASS batch_summary.json'
    $batchSummary = Read-JsonObject -Path $normalBatchSummaryPath -Label 'PASS batch_summary.json'
    $normalSchedulerPath = Assert-NormalFile -Path $SchedulerPath -Label '固定 scheduler 源码'
    $normalRunnerPath = Assert-NormalFile -Path $RunnerPath -Label '固定 runner 源码'
    $schedulerHash = Get-Sha256Literal -Path $normalSchedulerPath
    if ($prior.batch.scheduler_path -isnot [string] -or
        [System.IO.Path]::GetFullPath($prior.batch.scheduler_path) -ine [System.IO.Path]::GetFullPath($normalSchedulerPath) -or
        $prior.batch.scheduler_sha256 -cne $schedulerHash -or
        $prior.batch.summary_path -cne $batchSummaryPath) {
        throw '首次 D9 失败 recovery 的 PASS batch 路径或 scheduler 绑定不符。'
    }
    Assert-PassingBatchSummary -BatchSummary $batchSummary -EvidenceRoot $EvidenceRoot -ExpectedRunId $ExpectedRunId `
        -ExpectedBackendHash $ExpectedBackendHash -ExpectedSchedulerHash $schedulerHash `
        -ExpectedRunnerHash (Get-Sha256Literal -Path $normalRunnerPath)
    if ($batchSummary.sample0_snapshot.sha256 -cne $prior.batch.sample0_snapshot_sha256) {
        throw '首次 D9 失败 recovery 中 batch sample000 snapshot hash 不符。'
    }

    $reportPath = Join-Path $EvidenceRoot 'd9_109_sample_report.json'
    if (Test-Path -LiteralPath $reportPath) { throw '首次 D9 失败 recovery 要求 D9 报告缺失。' }
    $attempt1StdoutPath = Join-Path $EvidenceRoot ("unattended_d9_stdout_{0}.log" -f $ExpectedRunId)
    $attempt1StderrPath = Join-Path $EvidenceRoot ("unattended_d9_stderr_{0}.log" -f $ExpectedRunId)
    $normalAttempt1StdoutPath = Assert-NormalFile -Path $attempt1StdoutPath -Label 'D9 attempt1 stdout'
        $normalAttempt1StderrPath = Assert-NormalFile -Path $attempt1StderrPath -Label 'D9 attempt1 stderr'
        $expectedAttempt1StdoutPath = Join-Path $script:ApprovedD9RecoveryEvidenceDirectory 'unattended_d9_stdout_repair109_20261003_194620.log'
    $expectedAttempt1StderrPath = Join-Path $script:ApprovedD9RecoveryEvidenceDirectory 'unattended_d9_stderr_repair109_20261003_194620.log'
    if ($normalAttempt1StdoutPath -cne $expectedAttempt1StdoutPath -or
        $normalAttempt1StderrPath -cne $expectedAttempt1StderrPath -or
        (Get-Sha256Literal -Path $normalAttempt1StdoutPath) -cne $script:ExpectedD9Attempt1StdoutSha256 -or
        (Get-Sha256Literal -Path $normalAttempt1StderrPath) -cne $script:ExpectedD9Attempt1StderrSha256) {
        throw 'D9 attempt1 stdout/stderr 路径或精确字节 SHA 与固定失败证据不符。'
    }
    return [ordered]@{
        kind = 'D9_FIRST_ATTEMPT_NO_REPORT'
        sample0 = $prior.sample0
        batch_summary_sha256 = [string]$prior.batch.summary_sha256
        attempt1_stdout_path = $normalAttempt1StdoutPath
        attempt1_stdout_sha256 = $script:ExpectedD9Attempt1StdoutSha256
        attempt1_stderr_path = $normalAttempt1StderrPath
        attempt1_stderr_sha256 = $script:ExpectedD9Attempt1StderrSha256
        attempt1_exit_code = $null
        attempt1_exit_code_observed = $false
        attempt1_error_summary = [string]$prior.error
        failure_verifier_commit = $script:ExpectedD9FailureVerifierCommit
        failure_verifier_blob_oid = $script:ExpectedD9FailureVerifierBlobOid
        failure_verifier_sha256 = $script:ExpectedD9FailureVerifierSha256
        failure_verifier_path = 'verification/verify_s2a_t68_d9_outputs.py'
        replay_exit_code = $script:ExpectedD9ReplayExitCode
        replay_exit_code_source = 'READ_ONLY_FIXED_VERIFIER_REPLAY_NOT_FIRST_ATTEMPT'
        replay_stdout_sha256 = $script:ExpectedD9ReplayStdoutSha256
        replay_stderr_sha256 = $script:ExpectedD9ReplayStderrSha256
        replay_failure_class = [string]$replay.failure_class
        replay_evidence_path = $replayEvidencePath
        replay_evidence_sha256 = $script:ExpectedD9ReplayEvidenceSha256
    }
}

function Get-D9AttemptLogPaths {
    param(
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$ExpectedRunId,
        [switch]$Attempt2
    )
    $attemptSuffix = if ($Attempt2) { '_attempt2' } else { '' }
    return [ordered]@{
        stdout_path = Join-Path $EvidenceRoot ("unattended_d9_stdout_{0}{1}.log" -f $ExpectedRunId, $attemptSuffix)
        stderr_path = Join-Path $EvidenceRoot ("unattended_d9_stderr_{0}{1}.log" -f $ExpectedRunId, $attemptSuffix)
    }
}

function Write-NewUtf8File {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text
    )
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
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [switch]$PythonUtf8
    )
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $ExecutablePath
    $startInfo.WorkingDirectory = $WorkingDirectory
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.Environment['PATH'] = $env:PATH
    if ($PythonUtf8) {
        $null = Assert-NormalDirectory -Path $script:ApprovedPythonModulePath -Label '固定 Python 模块目录'
        $startInfo.Environment['PYTHONIOENCODING'] = 'UTF-8'
        $startInfo.Environment['PYTHONPATH'] = $script:ApprovedPythonModulePath
        $startInfo.StandardOutputEncoding = [System.Text.UTF8Encoding]::new($false)
        $startInfo.StandardErrorEncoding = [System.Text.UTF8Encoding]::new($false)
    }
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
    $sourceSnapshot = $BatchSummary.scheduler_source_snapshot
    if ($BatchSummary.scheduler_sha256 -notmatch '^[0-9a-f]{64}$' -or
        $BatchSummary.runner_sha256 -notmatch '^[0-9a-f]{64}$' -or
        $BatchSummary.scheduler_path -isnot [string] -or [string]::IsNullOrWhiteSpace($BatchSummary.scheduler_path) -or
        $BatchSummary.scheduler_bytes -isnot [long] -or $BatchSummary.scheduler_bytes -le 0 -or
        $sourceSnapshot -isnot [System.Collections.IDictionary] -or
        -not $sourceSnapshot.Contains('path') -or -not $sourceSnapshot.Contains('bytes') -or
        -not $sourceSnapshot.Contains('sha256') -or -not $sourceSnapshot.Contains('write_error') -or
        $sourceSnapshot.path -isnot [string] -or [string]::IsNullOrWhiteSpace($sourceSnapshot.path) -or
        $sourceSnapshot.bytes -isnot [long] -or $sourceSnapshot.bytes -le 0 -or
        $sourceSnapshot.sha256 -isnot [string] -or $sourceSnapshot.sha256 -notmatch '^[0-9a-f]{64}$' -or
        $null -ne $sourceSnapshot.write_error) {
        throw 'batch_summary.json 的 scheduler 源码冻结证据不完整或不一致。'
    }

    $dispatchDirectory = Assert-NormalDirectory -Path (Join-Path $EvidenceRoot 'batch_dispatch') -Label 'scheduler dispatch 目录'
    $expectedSnapshotPath = [System.IO.Path]::GetFullPath((Join-Path $dispatchDirectory 'scheduler_source_snapshot.json'))
    if (-not [System.IO.Path]::IsPathRooted([string]$sourceSnapshot.path) -or
        [System.IO.Path]::GetFullPath([string]$sourceSnapshot.path) -ine $expectedSnapshotPath) {
        throw 'scheduler_source_snapshot.path 未绑定到本次 batch_dispatch 清单。'
    }
    $snapshotPath = Assert-NormalFile -Path $expectedSnapshotPath -Label 'scheduler 源码快照清单'
    $snapshotItem = Get-Item -LiteralPath $snapshotPath -ErrorAction Stop
    if ($snapshotItem.Length -ne [long]$sourceSnapshot.bytes -or
        (Get-Sha256Literal -Path $snapshotPath) -cne [string]$sourceSnapshot.sha256) {
        throw 'scheduler_source_snapshot.json 的长度或 SHA-256 与批次记录不符。'
    }

    $sourceManifest = Read-JsonObject -Path $snapshotPath -Label 'scheduler 源码快照清单'
    if (-not $sourceManifest.Contains('schema_version') -or -not $sourceManifest.Contains('path') -or
        -not $sourceManifest.Contains('bytes') -or -not $sourceManifest.Contains('sha256') -or
        $sourceManifest.schema_version -cne 'gestureforge_s2a_t68_batch_scheduler_source_v1' -or
        $sourceManifest.path -isnot [string] -or [string]::IsNullOrWhiteSpace($sourceManifest.path) -or
        -not [System.IO.Path]::IsPathRooted([string]$sourceManifest.path) -or
        $sourceManifest.bytes -isnot [long] -or $sourceManifest.bytes -le 0 -or
        $sourceManifest.sha256 -isnot [string] -or $sourceManifest.sha256 -notmatch '^[0-9a-f]{64}$' -or
        [System.IO.Path]::GetFullPath([string]$sourceManifest.path) -ine [System.IO.Path]::GetFullPath([string]$BatchSummary.scheduler_path) -or
        $sourceManifest.bytes -ne $BatchSummary.scheduler_bytes -or
        $sourceManifest.sha256 -cne $BatchSummary.scheduler_sha256) {
        throw 'scheduler_source_snapshot.json 未将冻结源码路径、长度与 SHA-256 绑定到 batch_summary.json。'
    }

    $finalObservation = $BatchSummary.scheduler_final_observation
    if ($finalObservation -isnot [System.Collections.IDictionary] -or
        $finalObservation.unchanged -ne $true -or
        $finalObservation.path -isnot [string] -or
        [System.IO.Path]::GetFullPath([string]$finalObservation.path) -ine [System.IO.Path]::GetFullPath([string]$BatchSummary.scheduler_path) -or
        $finalObservation.expected_bytes -ne $BatchSummary.scheduler_bytes -or
        $finalObservation.current_bytes -ne $BatchSummary.scheduler_bytes -or
        $finalObservation.expected_sha256 -cne $BatchSummary.scheduler_sha256 -or
        $finalObservation.current_sha256 -cne $BatchSummary.scheduler_sha256 -or
        -not $finalObservation.Contains('read_error') -or
        $null -ne $finalObservation.read_error -or
        -not $BatchSummary.Contains('scheduler_hash_mismatches') -or
        $BatchSummary.scheduler_hash_mismatches -isnot [array] -or
        $BatchSummary.scheduler_hash_mismatches.Count -ne 0) {
        throw 'batch_summary.json 的 scheduler 最终观察或哈希差异记录不完整。'
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
        [AllowNull()][object]$ExpectedSample0SimulationHash
    )
    $resolvedRoot = [System.IO.Path]::GetFullPath($EvidenceRoot).TrimEnd('\')
    $reconstruction = $Report.cpu_d9_reconstruction
    $runtimeVersions = if ($reconstruction -is [System.Collections.IDictionary]) { $reconstruction.runtime_versions } else { $null }
    $ignoredFields = @('runtime.python', 'runtime.zlib_compile', 'runtime.zlib_runtime')
    if ($Report.schema_version -cne 'gestureforge_s2a_t68_d9_actual_head_comparison_v2' -or
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
        $Report.simulator_started_by_verifier -ne $false -or
        $reconstruction -isnot [System.Collections.IDictionary] -or
        $reconstruction.Count -ne 9 -or
        $reconstruction.schema_version -cne 'gestureforge_s2a_t68_cpu_d9_reconstruction_v1' -or
        $reconstruction.status -cne 'PASS_T29_REGENERATION_EXCEPT_RUNTIME_VERSION_FIELDS' -or
        $reconstruction.frozen_canonical_sha256 -cne $script:ExpectedT29CanonicalSha256 -or
        $reconstruction.regenerated_canonical_sha256 -cne $script:ExpectedT29RegeneratedCanonicalSha256 -or
        $reconstruction.exact_outputs_status -cne 'PASS_ALL_109_SAMPLES_EXACT' -or
        $reconstruction.exact_outputs_match -isnot [bool] -or $reconstruction.exact_outputs_match -ne $true -or
        $reconstruction.normalized_canonical_match -isnot [bool] -or $reconstruction.normalized_canonical_match -ne $true -or
        $reconstruction.ignored_fields -isnot [array] -or
        (@($reconstruction.ignored_fields) -join '|') -cne ($ignoredFields -join '|')) {
        throw 'D9 报告顶层 schema、样本范围、运行路径、verifier 或冻结基线绑定不符。'
    }
    $expectedRuntimeVersions = @{
        python = @{ frozen = '3.12.10'; regenerated = '3.12.14' }
        zlib_compile = @{ frozen = '1.3.1'; regenerated = '1.3.2' }
        zlib_runtime = @{ frozen = '1.3.1'; regenerated = '1.3.2' }
    }
    if ($runtimeVersions -isnot [System.Collections.IDictionary] -or $runtimeVersions.Count -ne $expectedRuntimeVersions.Count) {
        throw 'D9 T29 重建 runtime_versions 字段集合不符。'
    }
    foreach ($field in $expectedRuntimeVersions.Keys) {
        $observed = $runtimeVersions[$field]
        if ($observed -isnot [System.Collections.IDictionary] -or $observed.Count -ne 2 -or
            $observed.frozen -isnot [string] -or $observed.frozen -cne $expectedRuntimeVersions[$field].frozen -or
            $observed.regenerated -isnot [string] -or $observed.regenerated -cne $expectedRuntimeVersions[$field].regenerated) {
            throw "D9 T29 重建 runtime_versions.$field 不符。"
        }
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
        [AllowNull()][object]$ExpectedSample0SimulationHash,
        [switch]$RecoveryAttempt2,
        [AllowNull()][System.Collections.IDictionary]$PreservedFirstAttempt
    )
    $verifierPath = Join-Path $RepositoryRoot 'verification\verify_s2a_t68_d9_outputs.py'
    $reportPath = Join-Path $EvidenceRoot 'd9_109_sample_report.json'
    $logPaths = Get-D9AttemptLogPaths -EvidenceRoot $EvidenceRoot -ExpectedRunId $ExpectedRunId -Attempt2:$RecoveryAttempt2
    if ($RecoveryAttempt2) {
        if ($PreservedFirstAttempt -isnot [System.Collections.IDictionary]) { throw 'D9 attempt2 缺少 attempt1 保留哈希。' }
        $stdoutPath = [string]$logPaths.stdout_path
        $stderrPath = [string]$logPaths.stderr_path
        if (Test-Path -LiteralPath $reportPath) { throw 'D9 recovery attempt2 要求报告仍缺失，拒绝复用或覆盖。' }
        foreach ($path in @($stdoutPath, $stderrPath)) {
            if (Test-Path -LiteralPath $path) { throw "拒绝覆盖既有 D9 attempt2 日志：$path" }
        }
    } else {
        $stdoutPath = [string]$logPaths.stdout_path
        $stderrPath = [string]$logPaths.stderr_path
    }
    $attempt1StdoutPath = Join-Path $EvidenceRoot ("unattended_d9_stdout_{0}.log" -f $ExpectedRunId)
    $attempt1StderrPath = Join-Path $EvidenceRoot ("unattended_d9_stderr_{0}.log" -f $ExpectedRunId)
    if ($RecoveryAttempt2 -and
        ($ExpectedRunId -cne $script:ApprovedD9RecoveryRunId -or
        [System.IO.Path]::GetFullPath($EvidenceRoot) -cne [System.IO.Path]::GetFullPath($script:ApprovedD9RecoveryEvidenceDirectory) -or
        $PreservedFirstAttempt.stdout_path -cne $attempt1StdoutPath -or
        $PreservedFirstAttempt.stderr_path -cne $attempt1StderrPath -or
        [string]$PreservedFirstAttempt.stdout_sha256 -cne $script:ExpectedD9Attempt1StdoutSha256 -or
        [string]$PreservedFirstAttempt.stderr_sha256 -cne $script:ExpectedD9Attempt1StderrSha256 -or
        -not (Test-Path -LiteralPath $attempt1StdoutPath -PathType Leaf) -or
        -not (Test-Path -LiteralPath $attempt1StderrPath -PathType Leaf) -or
        (Get-Sha256Literal -Path $attempt1StdoutPath) -cne [string]$PreservedFirstAttempt.stdout_sha256 -or
        (Get-Sha256Literal -Path $attempt1StderrPath) -cne [string]$PreservedFirstAttempt.stderr_sha256)) {
        throw 'D9 attempt2 启动前 attempt1 stdout/stderr 路径或 SHA-256 已变化。'
    }
    if ($RecoveryAttempt2) {
        $priorRecoveryPath = Join-Path $script:ApprovedD9RecoveryEvidenceDirectory 'unattended_continuation_repair109_20261003_194620_recovery.json'
        $replayEvidencePath = $script:ExpectedD9ReplayEvidencePath
        $priorRecoveryPath = Assert-NormalFile -Path $priorRecoveryPath -Label 'attempt2 前旧 recovery summary 固定路径'
        $replayEvidencePath = Assert-NormalFile -Path $replayEvidencePath -Label 'attempt2 前 replay evidence 固定路径'
        if ([string]$PreservedFirstAttempt.recovery_summary_path -cne $priorRecoveryPath -or
            [string]$PreservedFirstAttempt.recovery_summary_sha256 -cne $script:ExpectedD9RecoverySummarySha256 -or
            [string]$PreservedFirstAttempt.replay_evidence_path -cne $replayEvidencePath -or
            [string]$PreservedFirstAttempt.replay_evidence_sha256 -cne $script:ExpectedD9ReplayEvidenceSha256 -or
            (Get-Sha256Literal -Path $priorRecoveryPath) -cne $script:ExpectedD9RecoverySummarySha256 -or
            (Read-JsonObject -Path $priorRecoveryPath -Label 'attempt2 前旧 recovery summary').run_id -cne $script:ApprovedD9RecoveryRunId -or
            (Get-Sha256Literal -Path $replayEvidencePath) -cne $script:ExpectedD9ReplayEvidenceSha256) {
            throw 'D9 attempt2 启动前旧 recovery summary 或固定复放证据身份、SHA 已变化。'
        }
    }
    $verifierHash = Get-Sha256Literal -Path $verifierPath
    $pythonHash = Get-Sha256Literal -Path $PythonPath
    $reportExists = Test-Path -LiteralPath $reportPath
    $stdoutExists = Test-Path -LiteralPath $stdoutPath
    $stderrExists = Test-Path -LiteralPath $stderrPath
    if ($RecoveryAttempt2 -and ($reportExists -or $stdoutExists -or $stderrExists)) {
        throw 'D9 recovery attempt2 的报告或独立日志路径已存在，拒绝重用。'
    }
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
        $execution = Invoke-CapturedProcess -ExecutablePath $PythonPath -Arguments $arguments -WorkingDirectory $RepositoryRoot -PythonUtf8
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
    $execution = Invoke-CapturedProcess -ExecutablePath $PythonPath -Arguments $arguments -WorkingDirectory $RepositoryRoot -PythonUtf8
    Write-NewUtf8File -Path $stdoutPath -Text $execution.stdout
    Write-NewUtf8File -Path $stderrPath -Text $execution.stderr
    if ($RecoveryAttempt2) {
        if (-not (Test-Path -LiteralPath $attempt1StdoutPath -PathType Leaf) -or
            -not (Test-Path -LiteralPath $attempt1StderrPath -PathType Leaf) -or
            [string]$PreservedFirstAttempt.stdout_sha256 -cne $script:ExpectedD9Attempt1StdoutSha256 -or
            [string]$PreservedFirstAttempt.stderr_sha256 -cne $script:ExpectedD9Attempt1StderrSha256 -or
            (Get-Sha256Literal -Path $attempt1StdoutPath) -cne [string]$PreservedFirstAttempt.stdout_sha256 -or
            (Get-Sha256Literal -Path $attempt1StderrPath) -cne [string]$PreservedFirstAttempt.stderr_sha256) {
            throw 'D9 attempt2 后 attempt1 stdout/stderr 未保持原路径与原哈希。'
        }
        $priorRecoveryPath = Join-Path $script:ApprovedD9RecoveryEvidenceDirectory 'unattended_continuation_repair109_20261003_194620_recovery.json'
        $replayEvidencePath = $script:ExpectedD9ReplayEvidencePath
        if ((Get-Sha256Literal -Path $priorRecoveryPath) -cne $script:ExpectedD9RecoverySummarySha256 -or
            (Read-JsonObject -Path $priorRecoveryPath -Label 'attempt2 后旧 recovery summary').run_id -cne $script:ApprovedD9RecoveryRunId -or
            (Get-Sha256Literal -Path $replayEvidencePath) -cne $script:ExpectedD9ReplayEvidenceSha256) {
            throw 'D9 attempt2 后旧 recovery summary 或固定复放证据身份、SHA 已变化。'
        }
    }
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
    $pythonVersionCheck = Invoke-CapturedProcess -ExecutablePath $pythonPath -Arguments @('--version') -WorkingDirectory $repositoryRoot -PythonUtf8
    $pythonVersionStdout = ([string]$pythonVersionCheck.stdout).Trim()
    $script:Summary.pinned_python_version_stdout = $pythonVersionStdout
    $script:Summary.pinned_python_version_exit_code = $pythonVersionCheck.exit_code
    if ($pythonVersionCheck.exit_code -ne 0 -or $pythonVersionStdout -cne $script:Summary.pinned_python_version_expected) {
        throw "固定 Python 版本断言失败：exit=$($pythonVersionCheck.exit_code)，stdout='$pythonVersionStdout'。"
    }
    $dependencyCheck = Invoke-CapturedProcess -ExecutablePath $pythonPath `
        -Arguments @('-B', '-c', 'import numpy,cv2; print(numpy.__version__ + "|" + cv2.__version__)') -WorkingDirectory $repositoryRoot -PythonUtf8
    $script:Summary.python_dependency_versions = ([string]$dependencyCheck.stdout).Trim()
    $script:Summary.python_dependency_exit_code = $dependencyCheck.exit_code
    if ($dependencyCheck.exit_code -ne 0 -or $script:Summary.python_dependency_versions -cne '2.4.6|4.13.0') {
        throw "固定 NumPy/OpenCV 预检失败：exit=$($dependencyCheck.exit_code)，stderr=$($dependencyCheck.stderr)"
    }
    $pythonDirectory = Split-Path -Parent $pythonPath
    $env:PATH = $pythonDirectory + [System.IO.Path]::PathSeparator + $env:PATH
    $resolvedPythonCommands = @(Get-Command -Name 'python.exe' -CommandType Application -All -ErrorAction Stop)
    $resolvedPython = Assert-ApprovedPythonCommandResolution -ApprovedPath $pythonPath -ResolvedCommands $resolvedPythonCommands
    $script:Summary.pinned_python_sha256 = Get-Sha256Literal -Path $pythonPath

    $originalSummaryPath = Join-Path $evidenceRoot ("unattended_continuation_{0}.json" -f $RunId)
    $script:SummaryPath = $originalSummaryPath
    $falseStopBatchRecovery = $false
    $falseStopExpectedBatchSummarySha256 = $null
    $d9FirstAttemptRecovery = $false
    $d9RecoveryExpectedBatchSummarySha256 = $null
    $preservedFirstD9Attempt = $null
    if ($ResumeFailedCoordinatorSha256 -and $ResumeFailedRecoverySha256) {
        throw 'ResumeFailedCoordinatorSha256 与 ResumeFailedRecoverySha256 不能同时使用。'
    }
    if ($ResumeFailedRecoverySha256) {
        $recoveryResult = Assert-FailedD9Recovery -SummaryPath (Join-Path $evidenceRoot ("unattended_continuation_{0}_recovery.json" -f $RunId)) `
            -ExpectedSummaryHash $ResumeFailedRecoverySha256 -EvidenceRoot $evidenceRoot -ExpectedRunId $RunId `
            -ExpectedBackendHash $expectedBackendHash `
            -SchedulerPath (Join-Path $repositoryRoot 'verification\run_s2a_t68_batch_verilator.ps1') `
            -RunnerPath (Join-Path $repositoryRoot 'verification\run_s2a_network_backend_verilator.ps1')
        $d9FirstAttemptRecovery = $true
        $d9RecoveryExpectedBatchSummarySha256 = [string]$recoveryResult.batch_summary_sha256
        $preservedFirstD9Attempt = [ordered]@{
            stdout_path = [string]$recoveryResult.attempt1_stdout_path
            stdout_sha256 = [string]$recoveryResult.attempt1_stdout_sha256
            stderr_path = [string]$recoveryResult.attempt1_stderr_path
            stderr_sha256 = [string]$recoveryResult.attempt1_stderr_sha256
            recovery_summary_path = Join-Path $script:ApprovedD9RecoveryEvidenceDirectory 'unattended_continuation_repair109_20261003_194620_recovery.json'
            recovery_summary_sha256 = $ResumeFailedRecoverySha256
            replay_evidence_path = [string]$recoveryResult.replay_evidence_path
            replay_evidence_sha256 = [string]$recoveryResult.replay_evidence_sha256
        }
        $script:Summary.recovery_mode = $recoveryResult.kind
        $script:Summary.sample0 = $recoveryResult.sample0
        $script:Summary.d9_recovery = [ordered]@{
            prior_stdout_path = $preservedFirstD9Attempt.stdout_path
            prior_stdout_sha256 = $preservedFirstD9Attempt.stdout_sha256
            prior_stderr_path = $preservedFirstD9Attempt.stderr_path
            prior_stderr_sha256 = $preservedFirstD9Attempt.stderr_sha256
            retry_stdout_path = (Get-D9AttemptLogPaths -EvidenceRoot $evidenceRoot -ExpectedRunId $RunId -Attempt2).stdout_path
            retry_stderr_path = (Get-D9AttemptLogPaths -EvidenceRoot $evidenceRoot -ExpectedRunId $RunId -Attempt2).stderr_path
            batch_summary_sha256 = $d9RecoveryExpectedBatchSummarySha256
            prior_recovery_summary_path = $preservedFirstD9Attempt.recovery_summary_path
            prior_recovery_summary_sha256 = $preservedFirstD9Attempt.recovery_summary_sha256
            first_attempt_exit_code = $recoveryResult.attempt1_exit_code
            first_attempt_exit_code_observed = $recoveryResult.attempt1_exit_code_observed
            first_attempt_exit_code_recording = 'NOT_RECORDED_IN_PRIOR_RECOVERY_SUMMARY'
            first_attempt_exit_code_note = '旧 recovery summary 未记录 attempt1 进程退出码；null 表示未观察，不代表 0 或 2。'
            first_attempt_error_summary = $recoveryResult.attempt1_error_summary
            failure_verifier_commit = $recoveryResult.failure_verifier_commit
            failure_verifier_blob_oid = $recoveryResult.failure_verifier_blob_oid
            failure_verifier_sha256 = $recoveryResult.failure_verifier_sha256
            failure_verifier_path = $recoveryResult.failure_verifier_path
            first_attempt_stderr_sha256 = $recoveryResult.attempt1_stderr_sha256
            first_attempt_stderr_interpretation = 'HASH_ONLY_NO_TEXT_DECODE'
            replay_exit_code = $recoveryResult.replay_exit_code
            replay_exit_code_source = $recoveryResult.replay_exit_code_source
            replay_stdout_sha256 = $recoveryResult.replay_stdout_sha256
            replay_stderr_sha256 = $recoveryResult.replay_stderr_sha256
            replay_failure_class = $recoveryResult.replay_failure_class
            replay_evidence_path = $preservedFirstD9Attempt.replay_evidence_path
            replay_evidence_sha256 = $preservedFirstD9Attempt.replay_evidence_sha256
            replay_exit_code_note = 'exit 2 来自固定旧 verifier 对同一输入的只读复放，不是首轮 coordinator 直接记录的退出码。'
            retry_count = 0
        }
        $script:SummaryPath = Join-Path $evidenceRoot ("unattended_continuation_{0}_recovery2.json" -f $RunId)
        $script:Summary.recovered_from_summary_path = Join-Path $evidenceRoot ("unattended_continuation_{0}_recovery.json" -f $RunId)
        $script:Summary.recovered_from_summary_sha256 = $ResumeFailedRecoverySha256
    } elseif ($ResumeFailedCoordinatorSha256) {
        $recoveryResult = Assert-FailedCoordinatorRecovery -SummaryPath $originalSummaryPath -ExpectedSummaryHash $ResumeFailedCoordinatorSha256 `
            -EvidenceRoot $evidenceRoot -ExpectedRunId $RunId -ExpectedBackendHash $expectedBackendHash `
            -SchedulerPath (Join-Path $repositoryRoot 'verification\run_s2a_t68_batch_verilator.ps1') `
            -RunnerPath (Join-Path $repositoryRoot 'verification\run_s2a_network_backend_verilator.ps1')
        $script:Summary.recovery_mode = $recoveryResult.kind
        if ($recoveryResult.kind -ceq 'BATCH_FALSE_STOP_VALIDATION') {
            $falseStopBatchRecovery = $true
            $falseStopExpectedBatchSummarySha256 = [string]$recoveryResult.batch_summary_sha256
            $script:Summary.sample0 = $recoveryResult.sample0
        }
        $script:SummaryPath = Join-Path $evidenceRoot ("unattended_continuation_{0}_recovery.json" -f $RunId)
        $script:Summary.recovered_from_summary_path = $originalSummaryPath
        $script:Summary.recovered_from_summary_sha256 = $ResumeFailedCoordinatorSha256
    }
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
    if (($falseStopBatchRecovery -and
        ($existingBatch.state -ne 'PASS' -or $existingBatch.summary_sha256 -cne $falseStopExpectedBatchSummarySha256)) -or
        ($d9FirstAttemptRecovery -and
        ($existingBatch.state -ne 'PASS' -or $existingBatch.summary_sha256 -cne $d9RecoveryExpectedBatchSummarySha256))) {
        $script:Summary.batch.status = if ($d9FirstAttemptRecovery) { 'STOP_D9_RECOVERY_BATCH_NOT_PASS_NO_DISPATCH' } else { 'STOP_RECOVERY_BATCH_NOT_PASS_NO_DISPATCH' }
        $script:Summary.batch.summary_path = $existingBatch.summary_path
        $script:Summary.batch.summary_sha256 = $existingBatch.summary_sha256
        $script:Summary.batch.message = "严格恢复要求现有 batch_summary.json 复验为 PASS 且 SHA-256 与先前终态记录一致；observed state=$($existingBatch.state)，observed SHA=$($existingBatch.summary_sha256)，拒绝重新调度 108 个样本。 $($existingBatch.message)"
        $script:Summary.status = 'STOP_EXISTING_BATCH_NO_DUPLICATE'
    } elseif ($existingBatch.state -eq 'PASS') {
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
                    $script:Summary.batch.process_exit_code = [int]$execution.exit_code
                    $script:Summary.batch.status = 'SCHEDULER_PROCESS_EXITED'
                    $script:Summary.batch.stdout_path = $batchStdoutPath
                    $script:Summary.batch.stderr_path = $batchStderrPath
                    Write-NewUtf8File -Path $batchStdoutPath -Text $execution.stdout
                    Write-NewUtf8File -Path $batchStderrPath -Text $execution.stderr
                    $script:Summary.batch.stdout_sha256 = Get-Sha256Literal -Path $batchStdoutPath
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
                        $script:Summary.batch.status = if ($execution.exit_code -ne 0) { 'FAIL_SCHEDULER_EXITED_WITHOUT_SUMMARY' } else { 'FAIL_BATCH_SUMMARY_MISSING' }
                        $script:Summary.batch.message = "scheduler exit_code=$($execution.exit_code); 未生成 batch_summary.json；stdout=$batchStdoutPath；stderr=$batchStderrPath；不重启、不重试。"
                        $script:Summary.status = 'STOP_BATCH_FAILED'
                    }
                }
            }
        }
    }

    if ($continueToD9) {
        $sample0SimulationHash = if ($null -ne $script:Summary.sample0) { [string]$script:Summary.sample0.terminal_record_sha256 } else { $null }
        $d9Arguments = @{
            EvidenceRoot = $evidenceRoot
            ExpectedRunId = $RunId
            RepositoryRoot = $repositoryRoot
            PythonPath = $pythonPath
            ExpectedBackendHash = $expectedBackendHash
            ExpectedSample0SnapshotHash = $script:Summary.batch.sample0_snapshot_sha256
            ExpectedSample0SimulationHash = $sample0SimulationHash
        }
        if ($d9FirstAttemptRecovery) {
            $d9Arguments.RecoveryAttempt2 = $true
            $d9Arguments.PreservedFirstAttempt = $preservedFirstD9Attempt
            $script:Summary.d9_recovery.retry_count = 1
        }
        $script:Summary.d9 = Invoke-VerifiedD9 @d9Arguments
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
