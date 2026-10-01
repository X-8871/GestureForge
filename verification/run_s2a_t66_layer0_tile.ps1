[CmdletBinding()]
param(
    [switch]$PrepareOnly,
    [switch]$CompileOnly,
    [string]$ApprovedPrelaunchSnapshotSha256,
    [switch]$RunSimulation,
    [string]$EvidenceDirectory = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01'
)

$ErrorActionPreference = 'Stop'

$rootPath = 'D:\FPGA_Competition'
$baselineCommit = '9fb9ab7b380430c22bf147654157858b52151dad'
$tileEvidenceRoot = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01'
$evidencePath = [System.IO.Path]::GetFullPath($EvidenceDirectory)
$fixturePath = Join-Path $evidencePath 'fixture'
$simPath = Join-Path $evidencePath 'sim'
$preparerPath = 'D:\FPGA_Competition\verification\prepare_s2a_t66_layer0_golden.py'
$offlineVerifierPath = 'D:\FPGA_Competition\verification\test_s2a_t66_layer0_tile.py'
$allowlistPath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02\process_identity_allowlist.json'
$allowlistSha256 = 'bc743da5ac3d3b2a2e493f3b1b23bf8cc0dfce3913e179062022806797aa090e'
$vivadoBinPath = 'D:\Xilinx\2026.1\Vivado\bin'
$snapshotName = 's2a_t66_layer0_tile_snapshot'
$passMarker = 'PASS: T66 sample0 layer0 full tensor matched T25; bytes=1384448 mismatches=0'
$executionPath = Join-Path $evidencePath 'execution_record.json'
$statusPath = Join-Path $evidencePath 'status.txt'
$currentPhase = 'INITIALIZE'
$execution = [ordered]@{
    schema_version = 'gestureforge_s2a_t66_tile01_execution_v1'
    task_id = 'S2A-T66-TILE01'
    status = 'PREPARING'
    baseline_commit = $baselineCommit
    cache_policy = [ordered]@{
        decision = 'A'
        tile_order = 'spatial_tile_major'
        feature_patch_capacity_bytes = 51200
        feature_patch_loads_per_spatial_tile = 1
        feature_patch_reuse_scope = 'all_output_channel_groups_in_current_tile'
        weight_group_capacity_bytes = 36864
        weight_group_output_channel_lanes = 8
        weight_group_reuse_scope = 'all_spatial_points_in_current_tile'
        weight_group_loads_per_tile_per_output_channel_group = 1
        weight_group_reloads_across_spatial_tiles = 'accepted_by_decision_A'
        output_block_capacity_bytes = 512
    }
    layer0_transfer_budget = [ordered]@{
        transaction_unit = '单次 transaction 为一条 32-bit 对齐 word 请求内 one-hot strobe 选中的 1 个字节；计数单位是 byte request'
        feature_in_bounds_byte_requests = 583443
        weight_byte_requests = 584064
        output_byte_requests = 1384448
    }
    xsim_launch_count = 0
    xsim_started = $false
    xsim_exit_code = $null
    waveforms_enabled = $false
    expected_output_bytes = 1384448
    expected_output_sha256 = '220499b6b8122c3264bef4d581967d51eedccc9e28813df3e0ff8f8716bc2ed8'
    estimated_cycles = 26003000
    watchdog_cycles = 75000000
    cycle_budget = [ordered]@{
        tile_count = 676
        feature_patch_bytes_total = 586092
        feature_in_bounds_byte_requests = 583443
        feature_zero_padding_patch_bytes = 2649
        weight_byte_requests = 584064
        output_byte_requests = 1384448
        all_single_byte_requests = 2551955
        request_latency_cycles = 7655865
        request_stall_cycles = 6635073
        response_stall_cycles = 6635073
        feature_request_stall_cycles = 1516947
        weight_request_stall_cycles = 1518566
        output_request_stall_cycles = 3599560
        feature_response_stall_cycles = 1516947
        weight_response_stall_cycles = 1518566
        output_response_stall_cycles = 3599560
        effective_mac_operations = 37380096
        parallel_mac_cycles = 4672512
        requant_cycles = 173056
        point_bias_init_cycles = 170352
        tile_group_control_cycles = 228488
        boundary_padding_scan_cycles = 2649
        estimated_total_cycles = 26002716
        stall_pattern = @(0, 1, 2, 7, 3)
    }
    estimated_wall_time = '15–25 minutes; stop at 30 minutes without a changed simulator progress line'
    xsim_working_directory = $simPath
    command_log_paths = @()
}

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )
    $encoding = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Path, $Text, $encoding)
}

function Assert-ExactDirectory {
    param([Parameter(Mandatory = $true)][string]$Path)
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if (-not $item.PSIsContainer -or $item.FullName -cne $Path -or
        ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        throw "T66_PATH_INVALID: 目录类型、精确路径或重解析属性不符：$($item.FullName)"
    }
    return $item
}

function Assert-ExactFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($item.PSIsContainer -or $item.FullName -cne $Path -or
        ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        throw "T66_PATH_INVALID: 文件类型、精确路径或重解析属性不符：$($item.FullName)"
    }
    return $item
}

function Write-ExecutionRecord {
    $json = ($execution | ConvertTo-Json -Depth 12) + [Environment]::NewLine
    Write-Utf8NoBom -Path $executionPath -Text $json
}

function ConvertTo-UtcInstantTicks {
    param([Parameter(Mandatory = $true)][object]$Value)

    if ($Value -is [DateTimeOffset]) {
        $instant = $Value.ToUniversalTime()
    } elseif ($Value -is [DateTime]) {
        $dateTime = [DateTime]$Value
        if ($dateTime.Kind -eq [DateTimeKind]::Unspecified) {
            $dateTime = [DateTime]::SpecifyKind($dateTime, [DateTimeKind]::Utc)
        }
        $instant = ([DateTimeOffset]$dateTime).ToUniversalTime()
    } else {
        $dateStyles = [System.Globalization.DateTimeStyles]::AssumeUniversal -bor
            [System.Globalization.DateTimeStyles]::AdjustToUniversal
        $instant = [DateTimeOffset]::Parse(
            [string]$Value,
            [System.Globalization.CultureInfo]::InvariantCulture,
            $dateStyles
        ).ToUniversalTime()
    }
    return [long]$instant.UtcDateTime.Ticks
}

function Assert-UtcTimestampNormalizationRegression {
    $jsonTimestamp = '{"creation_date_utc":"2026-09-29T18:07:06.157789Z"}' |
        ConvertFrom-Json
    $parsedDateTime = $jsonTimestamp.creation_date_utc
    if ($parsedDateTime -isnot [DateTime]) {
        throw 'T66_TIMESTAMP_REGRESSION_FAIL: ConvertFrom-Json 没有产生 DateTime。'
    }

    $parsedTicks = ConvertTo-UtcInstantTicks -Value $parsedDateTime
    $equalIsoTicks = ConvertTo-UtcInstantTicks -Value '2026-09-29T18:07:06.157789Z'
    $oneTickLater = ConvertTo-UtcInstantTicks -Value '2026-09-29T18:07:06.1577891Z'
    $differentInstant = ConvertTo-UtcInstantTicks -Value '2026-09-29T18:07:07.157789Z'
    if ($parsedTicks -ne $equalIsoTicks) {
        throw 'T66_TIMESTAMP_REGRESSION_FAIL: DateTime 与等值 ISO UTC 字符串没有匹配。'
    }
    if ($oneTickLater -ne ($parsedTicks + 1)) {
        throw 'T66_TIMESTAMP_REGRESSION_FAIL: +1 tick 用例没有保持精确差异。'
    }
    if (($parsedTicks -eq $oneTickLater) -or ($parsedTicks -eq $differentInstant)) {
        throw 'T66_TIMESTAMP_REGRESSION_FAIL: 不同 UTC 时刻被错误视为相等。'
    }

    return [ordered]@{
        status = 'PASS'
        normalization = 'UTC_DateTimeOffset_100ns_ticks'
        parsed_json_type = $parsedDateTime.GetType().FullName
        equivalent_iso_utc_matched = $true
        plus_one_tick_rejected = $true
        different_instant_rejected = $true
        test_timestamp_utc = '2026-09-29T18:07:06.157789Z'
        plus_one_tick_utc = '2026-09-29T18:07:06.1577891Z'
        different_instant_utc = '2026-09-29T18:07:07.157789Z'
    }
}

function Test-PreviousAttemptFailureSemantics {
    param(
        [Parameter(Mandatory = $true)][object]$Record,
        [Parameter(Mandatory = $true)][string]$StatusLine,
        [Parameter(Mandatory = $true)][string]$ExpectedFailure
    )

    $invocationProperty = $Record.PSObject.Properties['xsim_invocation_attempt_count']
    $invocationCountIsNullOrMissing = ($null -eq $invocationProperty) -or
        ($null -eq $invocationProperty.Value)
    $startedIsBooleanFalse = ($Record.xsim_started -is [bool]) -and
        ($Record.xsim_started -eq $false)
    $launchCount = $Record.xsim_launch_count
    $launchCountIsInteger = ($launchCount -is [sbyte]) -or ($launchCount -is [byte]) -or
        ($launchCount -is [int16]) -or ($launchCount -is [uint16]) -or
        ($launchCount -is [int32]) -or ($launchCount -is [uint32]) -or
        ($launchCount -is [int64]) -or ($launchCount -is [uint64])
    $launchCountIsZero = $launchCountIsInteger -and ($launchCount -eq 0)
    return [bool](
        ($Record.status -ceq 'FAIL_XSIM') -and
        $startedIsBooleanFalse -and
        $launchCountIsZero -and
        $invocationCountIsNullOrMissing -and
        ($StatusLine -ceq 'FAIL_XSIM') -and
        ($Record.failure -ceq $ExpectedFailure)
    )
}

function Assert-PreviousAttemptFailureSemanticsRegression {
    $expectedFailure = 'T66_PROCESS_SNAPSHOT_CHANGED: 批准快照之后出现新的或变化的 Xilinx 进程：pid=8712 name=vivado.exe'
    $missingPropertyRecord = [pscustomobject]@{
        status = 'FAIL_XSIM'
        xsim_started = $false
        xsim_launch_count = 0
        failure = $expectedFailure
    }
    $explicitNullRecord = $missingPropertyRecord | Select-Object *
    $explicitNullRecord | Add-Member -MemberType NoteProperty -Name 'xsim_invocation_attempt_count' -Value $null
    $nonNullRecord = $explicitNullRecord | Select-Object *
    $nonNullRecord.xsim_invocation_attempt_count = 0
    $wrongStatusRecord = $missingPropertyRecord | Select-Object *
    $wrongStatusRecord.status = 'PASS_FULL_LAYER0'
    $wrongStartedRecord = $missingPropertyRecord | Select-Object *
    $wrongStartedRecord.xsim_started = $true
    $wrongLaunchRecord = $missingPropertyRecord | Select-Object *
    $wrongLaunchRecord.xsim_launch_count = 1
    $wrongStartedTypeRecord = $missingPropertyRecord | Select-Object *
    $wrongStartedTypeRecord.xsim_started = 'false'
    $wrongLaunchTypeRecord = $missingPropertyRecord | Select-Object *
    $wrongLaunchTypeRecord.xsim_launch_count = '0'
    $wrongFailureRecord = $missingPropertyRecord | Select-Object *
    $wrongFailureRecord.failure = 'T66_OTHER_FAILURE'

    $missingAccepted = Test-PreviousAttemptFailureSemantics -Record $missingPropertyRecord -StatusLine 'FAIL_XSIM' -ExpectedFailure $expectedFailure
    $nullAccepted = Test-PreviousAttemptFailureSemantics -Record $explicitNullRecord -StatusLine 'FAIL_XSIM' -ExpectedFailure $expectedFailure
    $nonNullRejected = -not (Test-PreviousAttemptFailureSemantics -Record $nonNullRecord -StatusLine 'FAIL_XSIM' -ExpectedFailure $expectedFailure)
    $wrongStatusRejected = -not (Test-PreviousAttemptFailureSemantics -Record $wrongStatusRecord -StatusLine 'FAIL_XSIM' -ExpectedFailure $expectedFailure)
    $wrongStartedRejected = -not (Test-PreviousAttemptFailureSemantics -Record $wrongStartedRecord -StatusLine 'FAIL_XSIM' -ExpectedFailure $expectedFailure)
    $wrongLaunchRejected = -not (Test-PreviousAttemptFailureSemantics -Record $wrongLaunchRecord -StatusLine 'FAIL_XSIM' -ExpectedFailure $expectedFailure)
    $wrongStartedTypeRejected = -not (Test-PreviousAttemptFailureSemantics -Record $wrongStartedTypeRecord -StatusLine 'FAIL_XSIM' -ExpectedFailure $expectedFailure)
    $wrongLaunchTypeRejected = -not (Test-PreviousAttemptFailureSemantics -Record $wrongLaunchTypeRecord -StatusLine 'FAIL_XSIM' -ExpectedFailure $expectedFailure)
    $wrongFailureRejected = -not (Test-PreviousAttemptFailureSemantics -Record $wrongFailureRecord -StatusLine 'FAIL_XSIM' -ExpectedFailure $expectedFailure)
    $wrongStatusLineRejected = -not (Test-PreviousAttemptFailureSemantics -Record $missingPropertyRecord -StatusLine 'COMPILED_WAITING_PARENT_REVIEW' -ExpectedFailure $expectedFailure)
    if (-not ($missingAccepted -and $nullAccepted -and $nonNullRejected -and
              $wrongStatusRejected -and $wrongStartedRejected -and $wrongLaunchRejected -and
              $wrongStartedTypeRejected -and $wrongLaunchTypeRejected -and
              $wrongFailureRejected -and $wrongStatusLineRejected)) {
        throw 'T66_PREVIOUS_FAILURE_SEMANTICS_REGRESSION_FAIL: missing/null 或严格字段检查错误。'
    }
    return [ordered]@{
        status = 'PASS'
        missing_invocation_count_accepted = $missingAccepted
        explicit_null_invocation_count_accepted = $nullAccepted
        non_null_invocation_count_rejected = $nonNullRejected
        wrong_status_rejected = $wrongStatusRejected
        wrong_started_flag_rejected = $wrongStartedRejected
        wrong_launch_count_rejected = $wrongLaunchRejected
        wrong_started_type_rejected = $wrongStartedTypeRejected
        wrong_launch_type_rejected = $wrongLaunchTypeRejected
        wrong_failure_text_rejected = $wrongFailureRejected
        wrong_status_file_rejected = $wrongStatusLineRejected
    }
}

function Get-PreviousAttemptFailureEvidence {
    if ([System.IO.Path]::GetFileName($evidencePath) -cne 'compile_attempt03') {
        return $null
    }

    $previousPath = Join-Path ([System.IO.Directory]::GetParent($evidencePath).FullName) 'compile_attempt02'
    $null = Assert-ExactDirectory -Path $previousPath
    $expectedHashes = [ordered]@{
        runner_log = '03a6445b00dcd38e8350d1328cdc282ed39fc40aaec4d85e6722f71cf790b736'
        offline_resume_preflight = 'fac7ed9962012310439ea3d7be50f7dae3c418936398a7a044b1c554ee161841'
        status = 'c7dfcffdf90e38f167ea849f9ef5696f2cbcf eea615ed6846d3c72df313794aa'.Replace(' ', '')
        execution_record = 'd49780d7032e2211812ee0d661e65215ad6b3055f11d4f9493107ff274b63041'
        compile_snapshot = '0fc684b60d0107314f9172cb2474bde326d091bf328f52df0e324bdb7c382f2f'
    }
    $previousFiles = [ordered]@{
        runner_log = Join-Path $previousPath 'run_simulation_runner_round4.txt'
        offline_resume_preflight = Join-Path $previousPath 'offline_resume_preflight_console.txt'
        status = Join-Path $previousPath 'status.txt'
        execution_record = Join-Path $previousPath 'execution_record.json'
        compile_snapshot = Join-Path $previousPath 'compile_pre_xsim_process_snapshot.json'
    }
    foreach ($name in $previousFiles.Keys) {
        $null = Assert-ExactFile -Path $previousFiles[$name]
        $actualHash = (Get-FileHash -LiteralPath $previousFiles[$name] -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actualHash -cne $expectedHashes[$name]) {
            throw "T66_PREVIOUS_FAILURE_EVIDENCE_CHANGED: $($previousFiles[$name])"
        }
    }

    $previousRecord = Get-Content -LiteralPath $previousFiles.execution_record -Raw -Encoding UTF8 |
        ConvertFrom-Json
    $previousStatus = (Get-Content -LiteralPath $previousFiles.status -Raw -Encoding UTF8 -ErrorAction Stop).Split("`n")[0].Trim()
    $semanticRegression = Assert-PreviousAttemptFailureSemanticsRegression
    if (-not (Test-PreviousAttemptFailureSemantics -Record $previousRecord -StatusLine $previousStatus `
            -ExpectedFailure 'T66_PROCESS_SNAPSHOT_CHANGED: 批准快照之后出现新的或变化的 Xilinx 进程：pid=8712 name=vivado.exe')) {
        throw 'T66_PREVIOUS_FAILURE_EVIDENCE_INVALID: attempt02 未记录为未启动 XSim 的快照前失败。'
    }

    return [ordered]@{
        evidence_directory = $previousPath
        status = $previousRecord.status
        failure = $previousRecord.failure
        xsim_started = $previousRecord.xsim_started
        xsim_launch_count = $previousRecord.xsim_launch_count
        xsim_invocation_attempt_count = $previousRecord.xsim_invocation_attempt_count
        compile_snapshot_path = $previousFiles.compile_snapshot
        compile_snapshot_sha256 = $expectedHashes.compile_snapshot
        files_sha256 = $expectedHashes
        semantics_regression = $semanticRegression
    }
}

function Get-XilinxProcessSnapshot {
    param([Parameter(Mandatory = $true)][string]$Phase)
    $items = @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop |
        Where-Object { $_.Name -match '^(vivado|vivado_lab|xsim|xsimk|xvlog|xelab|xvhdl|xsc|hw_server|cs_server|xicom|xsct|bootgen|wdbserver)(\.exe)?$' } |
        Sort-Object ProcessId)
    $rows = @(
        foreach ($process in $items) {
            $createdUtc = $null
            if ($process.CreationDate) {
                $createdAt = $process.CreationDate
                if ($createdAt -isnot [DateTime]) {
                    $createdAt = [System.Management.ManagementDateTimeConverter]::ToDateTime(
                        [string]$createdAt
                    )
                }
                $createdUtc = $createdAt.ToUniversalTime().ToString("yyyy-MM-dd'T'HH:mm:ss.ffffff'Z'")
            }
            [ordered]@{
                pid = [int]$process.ProcessId
                parent_pid = [int]$process.ParentProcessId
                name = [string]$process.Name
                executable_path = [string]$process.ExecutablePath
                command_line = [string]$process.CommandLine
                creation_date_utc = $createdUtc
            }
        }
    )
    return [ordered]@{
        phase = $Phase
        captured_at_utc = [DateTime]::UtcNow.ToString('o')
        processes = $rows
    }
}

function Assert-ProtectedXilinxIdentities {
    param(
        [Parameter(Mandatory = $true)][string]$Phase,
        [switch]$AllowThisSimulation
    )
    $snapshot = Get-XilinxProcessSnapshot -Phase $Phase
    foreach ($process in $snapshot.processes) {
        $matched = $false
        foreach ($expected in $protectedIdentities) {
            if ($process.pid -eq [int]$expected.pid) {
                if ($process.name -cne $expected.name -or
                    $process.executable_path -cne $expected.executable_path -or
                    $process.command_line -cne $expected.command_line) {
                    throw "T66_PROCESS_IDENTITY_CHANGED: PID=$($process.pid) 阶段=$Phase"
                }
                $matched = $true
                break
            }
        }
        if (-not $matched -and $AllowThisSimulation) {
            $exePath = [string]$process.executable_path
            $commandLine = [string]$process.command_line
            $runLocal = $exePath.StartsWith($simPath + '\', [StringComparison]::OrdinalIgnoreCase)
            $runCommand = $commandLine -and $commandLine.Contains($snapshotName)
            if (($runLocal -or $runCommand) -and
                $process.name -match '^(xsim|xsimk|xelab|xvlog)(\.exe)?$') {
                $matched = $true
            }
        }
        if (-not $matched) {
            throw "T66_UNEXPECTED_XILINX_PROCESS: phase=$Phase pid=$($process.pid) name=$($process.name) path=$($process.executable_path)"
        }
    }
    return $snapshot
}

function Invoke-XilinxTool {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$ConsolePath,
        [Parameter(Mandatory = $true)][string]$Phase
    )
    $beforeSnapshot = Assert-ProtectedXilinxIdentities -Phase "before $Phase"
    $beforeSnapshotPath = Join-Path $evidencePath "${Phase}_pre_process_snapshot.json"
    if (Test-Path -LiteralPath $beforeSnapshotPath) {
        throw "T66_PROCESS_SNAPSHOT_COLLISION: 拒绝覆盖工具前快照：$beforeSnapshotPath"
    }
    Write-Utf8NoBom -Path $beforeSnapshotPath -Text (($beforeSnapshot | ConvertTo-Json -Depth 8) + [Environment]::NewLine)
    $execution["${Phase}_pre_process_snapshot_path"] = $beforeSnapshotPath
    $execution["${Phase}_pre_process_snapshot_sha256"] = (
        (Get-FileHash -LiteralPath $beforeSnapshotPath -Algorithm SHA256).Hash.ToLowerInvariant()
    )
    $startUtc = [DateTime]::UtcNow.ToString('o')
    $execution["${Phase}_command"] = @($Executable) + @($Arguments)
    $execution["${Phase}_working_directory"] = (Get-Location).Path
    $execution["${Phase}_console_path"] = $ConsolePath
    $execution["${Phase}_started"] = $true
    $execution["${Phase}_launch_count"] = 1
    $execution["${Phase}_started_at_utc"] = $startUtc
    Write-ExecutionRecord
    $savedPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & $Executable @Arguments *> $ConsolePath
        $toolExit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $savedPreference
    }
    $afterSnapshot = Assert-ProtectedXilinxIdentities -Phase "after $Phase"
    $afterSnapshotPath = Join-Path $evidencePath "${Phase}_post_process_snapshot.json"
    if (Test-Path -LiteralPath $afterSnapshotPath) {
        throw "T66_PROCESS_SNAPSHOT_COLLISION: 拒绝覆盖工具后快照：$afterSnapshotPath"
    }
    Write-Utf8NoBom -Path $afterSnapshotPath -Text (($afterSnapshot | ConvertTo-Json -Depth 8) + [Environment]::NewLine)
    $execution["${Phase}_post_process_snapshot_path"] = $afterSnapshotPath
    $execution["${Phase}_post_process_snapshot_sha256"] = (
        (Get-FileHash -LiteralPath $afterSnapshotPath -Algorithm SHA256).Hash.ToLowerInvariant()
    )
    $execution.command_log_paths += $ConsolePath
    $execution["${Phase}_exit_code"] = $toolExit
    $execution["${Phase}_console_sha256"] = (
        (Get-FileHash -LiteralPath $ConsolePath -Algorithm SHA256).Hash.ToLowerInvariant()
    )
    Write-ExecutionRecord
    if ($toolExit -ne 0) {
        throw "T66_${Phase}_FAIL: exit=$toolExit console=$ConsolePath"
    }
}

try {
    $selectedModes = @()
    if ($PrepareOnly) { $selectedModes += 'PrepareOnly' }
    if ($CompileOnly) { $selectedModes += 'CompileOnly' }
    if ($RunSimulation) { $selectedModes += 'RunSimulation' }
    $modeCount = $selectedModes.Count
    if ($modeCount -ne 1) {
        throw '必须且只能指定 PrepareOnly、CompileOnly 或 RunSimulation。'
    }
    $tileEvidencePrefix = $tileEvidenceRoot.TrimEnd('\') + '\'
    if (($evidencePath -cne $tileEvidenceRoot) -and
        -not $evidencePath.StartsWith($tileEvidencePrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "T66_EVIDENCE_SCOPE_INVALID: 证据目录必须位于 tile01 内：$evidencePath"
    }
    $null = Assert-ExactDirectory -Path $rootPath
    $null = Assert-ExactDirectory -Path (Join-Path $rootPath 'report')
    $null = Assert-ExactDirectory -Path (Join-Path $rootPath 'report\evidence')
    $null = Assert-ExactDirectory -Path (Join-Path $rootPath 'report\evidence\S2A-T66')
    $null = Assert-ExactDirectory -Path $evidencePath
    if (Test-Path -LiteralPath $fixturePath) {
        $null = Assert-ExactDirectory -Path $fixturePath
    }
    if ($CompileOnly -and ((Test-Path -LiteralPath $simPath) -or
                           (Test-Path -LiteralPath $executionPath))) {
        throw "T66_COMPILE_PATH_COLLISION: 隔离编译路径已存在：$simPath 或 $executionPath"
    }
    if ($RunSimulation) {
        $null = Assert-ExactDirectory -Path $simPath
        $null = Assert-ExactFile -Path $executionPath
        if ($ApprovedPrelaunchSnapshotSha256 -notmatch '^[0-9a-fA-F]{64}$') {
            throw 'T66_APPROVED_SNAPSHOT_REQUIRED: RunSimulation 必须带父级核对过的 64 位 snapshot SHA-256。'
        }
        $loadedExecution = Get-Content -LiteralPath $executionPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $execution = [ordered]@{}
        foreach ($property in $loadedExecution.PSObject.Properties) {
            $execution[$property.Name] = $property.Value
        }
        if ($execution.status -cne 'COMPILED_WAITING_PARENT_REVIEW' -or
            $execution.xsim_launch_count -ne 0 -or $execution.xsim_started -ne $false) {
            throw 'T66_RUN_STATE_INVALID: 仿真只能从编译完成且未启动的待复核状态继续。'
        }
        if ($execution.compile_pre_xsim_process_snapshot_sha256 -cne
            $ApprovedPrelaunchSnapshotSha256.ToLowerInvariant()) {
            throw 'T66_APPROVED_SNAPSHOT_MISMATCH: 父级核对摘要与编译后快照不同。'
        }
        $savedSnapshotPath = [string]$execution.compile_pre_xsim_process_snapshot_path
        $null = Assert-ExactFile -Path $savedSnapshotPath
        $savedSnapshotSha256 = (Get-FileHash -LiteralPath $savedSnapshotPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($savedSnapshotSha256 -cne $ApprovedPrelaunchSnapshotSha256.ToLowerInvariant()) {
            throw 'T66_APPROVED_SNAPSHOT_FILE_MISMATCH: 编译后进程快照文件摘要已变化。'
        }
    } elseif (Test-Path -LiteralPath $executionPath) {
        throw "T66_EXECUTION_RECORD_COLLISION: 执行记录已存在，拒绝覆盖：$executionPath"
    }

    $head = (git -C $rootPath rev-parse HEAD).Trim()
    $gitExit = $LASTEXITCODE
    if ($gitExit -ne 0 -or $head -notmatch '^[0-9a-f]{40}$') {
        throw "T66_BASELINE_READ_FAIL: 无法读取当前 HEAD：exit=$gitExit head=$head"
    }
    git -C $rootPath merge-base --is-ancestor $baselineCommit $head
    $ancestorExit = $LASTEXITCODE
    if ($ancestorExit -ne 0) {
        throw "T66_BASELINE_MISMATCH: 基线不是当前 HEAD 祖先：baseline=$baselineCommit head=$head"
    }
    $execution.actual_head = $head
    if (-not $RunSimulation) {
        $execution.status = 'VERIFYING_FIXTURES'
        $execution.started_at_utc = [DateTime]::UtcNow.ToString('o')
        Write-ExecutionRecord
    }
    $execution.runtime_timestamp_regression = Assert-UtcTimestampNormalizationRegression
    $previousAttemptEvidence = Get-PreviousAttemptFailureEvidence
    if ($null -ne $previousAttemptEvidence) {
        $execution.previous_attempt_failure_evidence = $previousAttemptEvidence
    }
    Write-ExecutionRecord

    $pythonCommand = Get-Command -Name 'python' -CommandType Application -ErrorAction Stop |
        Where-Object { $_.Source -notlike '*\WindowsApps\python.exe' } |
        Select-Object -First 1
    if (-not $pythonCommand) {
        throw 'T66_PYTHON_NOT_FOUND: 未找到 Python 可执行文件。'
    }
    if (-not $RunSimulation) {
        $currentPhase = 'PREPARE_FIXTURES'
        $prepConsoleName = if ($CompileOnly) { 'fixture_prepare_compile_console.txt' } else { 'fixture_prepare_prepare_console.txt' }
        $prepConsolePath = Join-Path $evidencePath $prepConsoleName
        if (Test-Path -LiteralPath $prepConsolePath) {
            throw "T66_PREP_LOG_COLLISION: 拒绝覆盖既有准备日志：$prepConsolePath"
        }
        & $pythonCommand.Source -B $preparerPath --evidence-dir $evidencePath *> $prepConsolePath
        $prepExit = $LASTEXITCODE
        $execution.preparer_exit_code = $prepExit
        $execution.preparer_console_sha256 = (Get-FileHash -LiteralPath $prepConsolePath -Algorithm SHA256).Hash.ToLowerInvariant()
        $execution.command_log_paths += $prepConsolePath
        Write-ExecutionRecord
        if ($prepExit -ne 0) {
            throw "T66_FIXTURE_PREPARE_FAIL: exit=$prepExit console=$prepConsolePath"
        }
        $fixtureManifestPath = Join-Path $evidencePath 'fixture_manifest.json'
        $fixtureManifest = Get-Content -LiteralPath $fixtureManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $execution.cache_policy = $fixtureManifest.cache_policy
        $execution.layer0_transfer_budget = $fixtureManifest.layer0_transfer_budget
        $execution.cache_policy_summary_path = $fixtureManifest.cache_policy_summary.path
        $execution.cache_policy_summary_sha256 = $fixtureManifest.cache_policy_summary.sha256
        $execution.source_sha256 = $fixtureManifest.source_sha256
        Write-ExecutionRecord
    }

    $currentPhase = 'OFFLINE_PREFLIGHT'
    $preflightConsoleName = if ($RunSimulation) {
        'offline_resume_preflight_console.txt'
    } elseif ($CompileOnly) {
        'offline_compile_preflight_console.txt'
    } else {
        'offline_prepare_preflight_console.txt'
    }
    $preflightConsolePath = Join-Path $evidencePath $preflightConsoleName
    if (Test-Path -LiteralPath $preflightConsolePath) {
        throw "T66_PREFLIGHT_LOG_COLLISION: 拒绝覆盖既有离线核验日志：$preflightConsolePath"
    }
    & $pythonCommand.Source -B $offlineVerifierPath --evidence-dir $evidencePath *> $preflightConsolePath
    $preflightExit = $LASTEXITCODE
    $execution.preflight_exit_code = $preflightExit
    $execution.preflight_console_sha256 = (Get-FileHash -LiteralPath $preflightConsolePath -Algorithm SHA256).Hash.ToLowerInvariant()
    $execution.command_log_paths += $preflightConsolePath
    Write-ExecutionRecord
    if ($preflightExit -ne 0) {
        throw "T66_PREFLIGHT_FAIL: exit=$preflightExit console=$preflightConsolePath"
    }

    if ($PrepareOnly) {
        $execution.status = 'PREPARE_ONLY_SIMULATION_NOT_RUN'
        $execution.completed_at_utc = [DateTime]::UtcNow.ToString('o')
        Write-ExecutionRecord
        Write-Utf8NoBom -Path $statusPath -Text "PREPARE_ONLY_SIMULATION_NOT_RUN`n"
        Write-Output "PASS: T66 fixture preparation only; no Vivado/XSim invocation. Evidence: $evidencePath"
        exit 0
    }

    $null = Assert-ExactFile -Path $allowlistPath
    $allowlistHash = (Get-FileHash -LiteralPath $allowlistPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($allowlistHash -cne $allowlistSha256) {
        throw "T66_PROCESS_ALLOWLIST_SHA_MISMATCH: actual=$allowlistHash"
    }
    $allowlist = Get-Content -LiteralPath $allowlistPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($allowlist.schema_version -cne 'gestureforge_s2a_t65_process_allowlist_v1' -or
        $allowlist.status -cne 'FROZEN_READ_ONLY_IDENTITIES' -or
        $allowlist.identities.Count -ne 3) {
        throw 'T66_PROCESS_ALLOWLIST_INVALID: allowlist schema/status/identity count changed.'
    }
    $script:protectedIdentities = @($allowlist.identities)

    if (-not $RunSimulation) {
        $null = New-Item -ItemType Directory -Path $simPath -ErrorAction Stop
    }
    $simItem = Assert-ExactDirectory -Path $simPath
    $tempPath = Join-Path $simPath 'temp'
    foreach ($path in @(
        $tempPath,
        (Join-Path $tempPath 'xilinx_local_user_data'),
        (Join-Path $tempPath 'home'),
        (Join-Path $tempPath 'appdata'),
        (Join-Path $tempPath 'localappdata')
    )) {
        if (-not (Test-Path -LiteralPath $path) -and -not $RunSimulation) {
            New-Item -ItemType Directory -Path $path -ErrorAction Stop | Out-Null
        }
        $null = Assert-ExactDirectory -Path $path
        if (-not ([System.IO.Path]::GetFullPath($path).StartsWith(
                [System.IO.Path]::GetFullPath($simPath).TrimEnd('\') + '\',
                [StringComparison]::OrdinalIgnoreCase))) {
            throw "T66_TEMP_PATH_INVALID: 临时路径必须留在隔离 sim 目录：$path"
        }
    }
    $env:TEMP = $tempPath
    $env:TMP = $tempPath
    $env:TMPDIR = $tempPath
    $env:HOME = Join-Path $tempPath 'home'
    $env:APPDATA = Join-Path $tempPath 'appdata'
    $env:LOCALAPPDATA = Join-Path $tempPath 'localappdata'
    $env:PYTHONDONTWRITEBYTECODE = '1'
    $env:XILINX_LOCAL_USER_DATA = Join-Path $tempPath 'xilinx_local_user_data'
    $execution.sim_path = $simItem.FullName
    if (-not $RunSimulation) { $execution.status = 'PREPARED_FOR_XSIM' }
    $execution.expected_runtime_process_guard_sha256 = $allowlistHash
    $execution.expected_output_fixture_sha256 = '220499b6b8122c3264bef4d581967d51eedccc9e28813df3e0ff8f8716bc2ed8'
    $execution.xsim_command = @(
        (Join-Path $vivadoBinPath 'xsim.bat'), '-R', '-log', 'xsim.log', $snapshotName
    )
    $execution.command_working_directory = $simPath
    $execution.stop_conditions = @(
        'SV watchdog at 75000000 simulation cycles',
        'wall time exceeds 30 minutes without a changed output progress line',
        'any missing/duplicate/mismatching output byte or memory protocol violation'
    )
    if (-not $RunSimulation) { Write-ExecutionRecord }

    $toolPaths = @(
        (Join-Path $vivadoBinPath 'xvlog.bat'),
        (Join-Path $vivadoBinPath 'xelab.bat'),
        (Join-Path $vivadoBinPath 'xsim.bat')
    )
    foreach ($path in $toolPaths) { $null = Assert-ExactFile -Path $path }
    $sourcePaths = @(
        'D:\FPGA_Competition\src\s2a_network_descriptor_pkg.sv',
        'D:\FPGA_Competition\src\s2a_conv_tile_engine.sv',
        'D:\FPGA_Competition\sim\tb_s2a_t66_layer0_tile.sv'
    )
    foreach ($path in $sourcePaths) { $null = Assert-ExactFile -Path $path }

    Push-Location -LiteralPath $simPath
    try {
        if (-not $RunSimulation) {
            $currentPhase = 'XVLOG'
            $execution.status = 'COMPILING'
            $xvlogConsole = Join-Path $simPath 'xvlog_console.txt'
            Invoke-XilinxTool -Executable (Join-Path $vivadoBinPath 'xvlog.bat') `
                -Arguments (@('-sv', '-work', 'xil_defaultlib') + $sourcePaths) `
                -ConsolePath $xvlogConsole -Phase 'xvlog'
            $xvlogLog = Join-Path $simPath 'xvlog.log'
            $null = Assert-ExactFile -Path $xvlogLog
            if (Select-String -LiteralPath $xvlogLog -Pattern 'ERROR:|FATAL:' -Quiet) {
                throw "T66_XVLOG_LOG_ERROR: $xvlogLog"
            }

            $currentPhase = 'XELAB'
            $xelabConsole = Join-Path $simPath 'xelab_console.txt'
            Invoke-XilinxTool -Executable (Join-Path $vivadoBinPath 'xelab.bat') `
                -Arguments @('-mt', 'off', '-debug', 'off', 'xil_defaultlib.tb_s2a_t66_layer0_tile', '-s', $snapshotName, '-log', 'xelab.log') `
                -ConsolePath $xelabConsole -Phase 'xelab'
            $xelabLog = Join-Path $simPath 'xelab.log'
            $null = Assert-ExactFile -Path $xelabLog
            if (Select-String -LiteralPath $xelabLog -Pattern 'ERROR:|FATAL:' -Quiet) {
                throw "T66_XELAB_LOG_ERROR: $xelabLog"
            }
        }

        $currentPhase = 'XSIM'
        if ($RunSimulation) {
            $approvedSnapshotPath = [string]$execution.compile_pre_xsim_process_snapshot_path
            $approvedSnapshot = Get-Content -LiteralPath $approvedSnapshotPath -Raw -Encoding UTF8 | ConvertFrom-Json
            $approvedRows = @($approvedSnapshot.processes)
            $liveSnapshot = Assert-ProtectedXilinxIdentities -Phase 'immediately_before_xsim'
            foreach ($process in $liveSnapshot.processes) {
                $found = $false
                foreach ($known in $approvedRows) {
                    if (($process.pid -eq $known.pid) -and ($process.parent_pid -eq $known.parent_pid) -and
                        ($process.name -ceq $known.name) -and
                        ($process.executable_path -ceq $known.executable_path) -and
                        ($process.command_line -ceq $known.command_line) -and
                        ((ConvertTo-UtcInstantTicks -Value $process.creation_date_utc) -eq
                            (ConvertTo-UtcInstantTicks -Value $known.creation_date_utc))) {
                        $found = $true
                        break
                    }
                }
                if (-not $found) {
                    throw "T66_PROCESS_SNAPSHOT_CHANGED: 批准快照之后出现新的或变化的 Xilinx 进程：pid=$($process.pid) name=$($process.name)"
                }
            }
            $preSnapshot = $liveSnapshot
            $execution.approved_compile_prelaunch_snapshot_sha256 = $ApprovedPrelaunchSnapshotSha256.ToLowerInvariant()
        } else {
            $preSnapshot = Assert-ProtectedXilinxIdentities -Phase 'compile_complete_prelaunch_snapshot'
        }
        $preSnapshotName = if ($RunSimulation) { 'pre_xsim_process_snapshot.json' } else { 'compile_pre_xsim_process_snapshot.json' }
        $preSnapshotPath = Join-Path $evidencePath $preSnapshotName
        Write-Utf8NoBom -Path $preSnapshotPath -Text (($preSnapshot | ConvertTo-Json -Depth 8) + [Environment]::NewLine)
        $preSnapshotHash = (Get-FileHash -LiteralPath $preSnapshotPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($RunSimulation) {
            $execution.pre_xsim_process_snapshot_sha256 = $preSnapshotHash
            $execution.pre_xsim_process_snapshot_path = $preSnapshotPath
        } else {
            $execution.compile_pre_xsim_process_snapshot_sha256 = $preSnapshotHash
            $execution.compile_pre_xsim_process_snapshot_path = $preSnapshotPath
            $execution.status = 'COMPILED_WAITING_PARENT_REVIEW'
            $execution.xsim_started = $false
            $execution.xsim_launch_count = 0
            $execution.compiled_at_utc = [DateTime]::UtcNow.ToString('o')
            Write-ExecutionRecord
            Write-Utf8NoBom -Path $statusPath -Text "COMPILED_WAITING_PARENT_REVIEW`n"
            if ($CompileOnly) {
                Write-Output "PASS: T66 fixture, xvlog, xelab complete; XSim not started. snapshot_sha256=$preSnapshotHash snapshot=$preSnapshotPath"
                exit 0
            }
        }
        $execution.status = 'XSIM_RUNNING'
        $execution.xsim_started = $false
        $execution.xsim_launch_count = 0
        $execution.xsim_invocation_attempt_count = 1
        $execution.xsim_started_at_utc = [DateTime]::UtcNow.ToString('o')
        $execution.expected_pass_marker = $passMarker
        $execution.xsim_estimated_runtime = '15–25 minutes; simulator watchdog 75000000 cycles; external no-progress stop at 30 minutes'
        $xsimConsole = Join-Path $simPath 'xsim_console.txt'
        $xsimErrorConsole = Join-Path $simPath 'xsim_stderr.txt'
        foreach ($newLogPath in @($xsimConsole, $xsimErrorConsole, (Join-Path $simPath 'xsim.log'))) {
            if (Test-Path -LiteralPath $newLogPath) {
                throw "T66_XSIM_LOG_COLLISION: 拒绝覆盖既有仿真日志：$newLogPath"
            }
        }
        $execution.xsim_console_path = $xsimConsole
        Write-ExecutionRecord
        Write-Utf8NoBom -Path $statusPath -Text "XSIM_RUNNING`n"

        $xsimProcess = Start-Process -FilePath (Join-Path $vivadoBinPath 'xsim.bat') `
            -ArgumentList @('-R', '-log', 'xsim.log', $snapshotName) `
            -WorkingDirectory $simPath -RedirectStandardOutput $xsimConsole `
            -RedirectStandardError $xsimErrorConsole -PassThru -WindowStyle Hidden
        $execution.xsim_started = $true
        $execution.xsim_launch_count = 1
        $execution.xsim_process_id = $xsimProcess.Id
        $execution.xsim_progress_interval_seconds = 5
        $execution.xsim_no_progress_timeout_seconds = 1800
        $execution.xsim_no_progress_source = 'xsim_console.txt and xsim.log lines beginning T66_CYCLE_PROGRESS or T66_PROGRESS'
        Write-ExecutionRecord
        $lastProgressUtc = [DateTime]::UtcNow
        $lastProgressCount = 0
        while (-not $xsimProcess.HasExited) {
            Start-Sleep -Seconds 5
            $progressCount = 0
            foreach ($progressPath in @($xsimConsole, (Join-Path $simPath 'xsim.log'))) {
                if (Test-Path -LiteralPath $progressPath -PathType Leaf) {
                    $progressCount += @(Select-String -LiteralPath $progressPath `
                        -Pattern '^T66_(CYCLE_)?PROGRESS\b' -AllMatches -ErrorAction SilentlyContinue).Count
                }
            }
            if ($progressCount -gt $lastProgressCount) {
                $lastProgressCount = $progressCount
                $lastProgressUtc = [DateTime]::UtcNow
                $execution.last_progress_count = $progressCount
                $execution.last_progress_seen_at_utc = $lastProgressUtc.ToString('o')
                Write-ExecutionRecord
            }
            if (([DateTime]::UtcNow - $lastProgressUtc).TotalSeconds -ge 1800) {
                $execution.no_progress_stop_triggered = $true
                $execution.no_progress_stop_triggered_at_utc = [DateTime]::UtcNow.ToString('o')
                $execution.no_progress_stop_last_count = $lastProgressCount
                Write-ExecutionRecord
                if (-not $xsimProcess.HasExited) {
                    if (@($protectedIdentities | Where-Object { [int]$_.pid -eq [int]$xsimProcess.Id }).Count -eq 0) {
                        Stop-Process -Id $xsimProcess.Id -Force -ErrorAction SilentlyContinue
                    }
                }
                foreach ($process in @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop |
                    Where-Object { $_.Name -match '^(xsim|xsimk|cmd)(\.exe)?$' -and
                        (([string]$_.CommandLine).Contains($snapshotName) -or
                         ([string]$_.ExecutablePath).StartsWith($simPath + '\', [StringComparison]::OrdinalIgnoreCase)) })) {
                    if (@($protectedIdentities | Where-Object { [int]$_.pid -eq [int]$process.ProcessId }).Count -eq 0) {
                        Stop-Process -Id ([int]$process.ProcessId) -Force -ErrorAction SilentlyContinue
                    }
                }
                throw "T66_XSIM_NO_PROGRESS_STOP: 30 分钟没有 T66 progress 行；日志=$xsimConsole; $($execution.xsim_no_progress_source)"
            }
            $xsimProcess.Refresh()
        }
        $xsimProcess.WaitForExit()
        $xsimExit = $xsimProcess.ExitCode
        $postSnapshot = Assert-ProtectedXilinxIdentities -Phase 'immediately_after_xsim' -AllowThisSimulation
        $postSnapshotPath = Join-Path $evidencePath 'post_xsim_process_snapshot.json'
        Write-Utf8NoBom -Path $postSnapshotPath -Text (($postSnapshot | ConvertTo-Json -Depth 8) + [Environment]::NewLine)
        $execution.post_xsim_process_snapshot_sha256 = (Get-FileHash -LiteralPath $postSnapshotPath -Algorithm SHA256).Hash.ToLowerInvariant()
        $execution.post_xsim_process_snapshot_path = $postSnapshotPath
        $execution.xsim_exit_code = $xsimExit
        $execution.xsim_completed_at_utc = [DateTime]::UtcNow.ToString('o')
        $execution.xsim_console_sha256 = (Get-FileHash -LiteralPath $xsimConsole -Algorithm SHA256).Hash.ToLowerInvariant()
        $execution.xsim_stderr_sha256 = (Get-FileHash -LiteralPath $xsimErrorConsole -Algorithm SHA256).Hash.ToLowerInvariant()
        $xsimLog = Join-Path $simPath 'xsim.log'
        if (Test-Path -LiteralPath $xsimLog -PathType Leaf) {
            $execution.xsim_log_sha256 = (Get-FileHash -LiteralPath $xsimLog -Algorithm SHA256).Hash.ToLowerInvariant()
        }
        Write-ExecutionRecord
        if ($xsimExit -ne 0) {
            throw "T66_XSIM_FAIL: exit=$xsimExit console=$xsimConsole"
        }
        if (-not (Test-Path -LiteralPath $xsimLog -PathType Leaf) -or
            -not (Select-String -LiteralPath $xsimLog -SimpleMatch -Pattern $passMarker -Quiet)) {
            throw "T66_PASS_MARKER_MISSING: required=$passMarker log=$xsimLog"
        }
        if (-not (Select-String -LiteralPath $xsimLog -Pattern 'ERROR:|FATAL:' -Quiet)) {
            $execution.status = 'PASS_FULL_LAYER0'
        } else {
            throw "T66_XSIM_LOG_ERROR: $xsimLog"
        }
        Write-Utf8NoBom -Path $statusPath -Text "PASS_FULL_SAMPLE0_LAYER0_ZERO_MISMATCH`n"
        Write-ExecutionRecord

        $currentPhase = 'OFFLINE_FINAL_VERIFY'
        $finalConsole = Join-Path $evidencePath 'offline_final_verify_console.txt'
        & $pythonCommand.Source -B $offlineVerifierPath --evidence-dir $evidencePath --require-simulation *> $finalConsole
        $finalExit = $LASTEXITCODE
        $execution.final_verifier_exit_code = $finalExit
        $execution.final_verifier_console_sha256 = (Get-FileHash -LiteralPath $finalConsole -Algorithm SHA256).Hash.ToLowerInvariant()
        $execution.command_log_paths += $finalConsole
        if ($finalExit -ne 0) {
            throw "T66_FINAL_OFFLINE_VERIFY_FAIL: exit=$finalExit console=$finalConsole"
        }
        Write-ExecutionRecord
        Write-Output "PASS: sample0 layer0 full tensor matched T25 with zero mismatches. Logs: $simPath"
    }
    finally {
        Pop-Location
    }
}
catch {
    $execution.status = "FAIL_$currentPhase"
    $execution.failure = $_.Exception.Message
    $execution.failed_at_utc = [DateTime]::UtcNow.ToString('o')
    if (Test-Path -LiteralPath $evidencePath -PathType Container) {
        if (-not (Test-Path -LiteralPath $executionPath -PathType Leaf)) {
            try { Write-ExecutionRecord } catch { }
        } else {
            try { Write-ExecutionRecord } catch { }
        }
        if (Test-Path -LiteralPath $statusPath -PathType Leaf) {
            try { Write-Utf8NoBom -Path $statusPath -Text ("FAIL_$currentPhase`n" + $_.Exception.Message + "`n") } catch { }
        } elseif ($RunSimulation) {
            try { Write-Utf8NoBom -Path $statusPath -Text ("FAIL_$currentPhase`n" + $_.Exception.Message + "`n") } catch { }
        }
    }
    throw
}
