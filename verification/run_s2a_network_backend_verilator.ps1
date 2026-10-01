[CmdletBinding()]
param(
    [ValidateRange(0, 108)]
    [int]$SampleIndex = 0,

    [string]$RunId = 'run01',

    [string]$EvidenceDirectory = '',

    [string]$ExpectedBackendSha256 = '',

    [long]$MaxCycles = 4294967295,

    [string]$PythonExecutable = 'python',

    [switch]$Compile,

    [switch]$RunSimulation
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-Sha256Literal {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )
    $encoding = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

function Write-CommandLog {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object[]]$Lines
    )
    $text = ($Lines | ForEach-Object { [string]$_ }) -join [Environment]::NewLine
    if (-not $text.EndsWith([Environment]::NewLine)) {
        $text += [Environment]::NewLine
    }
    Write-Utf8NoBom -Path $Path -Content $text
}

function Quote-ProcessArgument {
    param([Parameter(Mandatory = $true)][string]$Argument)
    return '"' + $Argument + '"'
}

function Test-StartedProcessIdentity {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][string]$ExpectedPath,
        [Parameter(Mandatory = $true)][string[]]$ExpectedArguments,
        [Parameter(Mandatory = $true)][datetime]$ExpectedStartTimeUtc
    )
    try {
        $Process.Refresh()
        if ($Process.HasExited) { return $false }
        $currentProcess = Get-Process -Id $Process.Id -ErrorAction Stop
        if ([string]::IsNullOrWhiteSpace($currentProcess.Path)) { return $false }
        if ([System.IO.Path]::GetFullPath($currentProcess.Path) -ine [System.IO.Path]::GetFullPath($ExpectedPath)) { return $false }
        $currentStartTimeUtc = $currentProcess.StartTime.ToUniversalTime()
        if ([Math]::Abs(($currentStartTimeUtc - $ExpectedStartTimeUtc).TotalSeconds) -gt 2) { return $false }
        $nativeProcess = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId = $($Process.Id)" -ErrorAction Stop
        if ($null -eq $nativeProcess -or [string]::IsNullOrWhiteSpace($nativeProcess.CommandLine)) { return $false }
        if ([System.IO.Path]::GetFullPath($nativeProcess.ExecutablePath) -ine [System.IO.Path]::GetFullPath($ExpectedPath)) { return $false }
        foreach ($expectedArgument in $ExpectedArguments) {
            if ($nativeProcess.CommandLine.IndexOf($expectedArgument, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
                return $false
            }
        }
        return $true
    } catch {
        return $false
    }
}

function Get-CompleteProgressMarkerLines {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return @() }
    $text = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
    if (-not $text.EndsWith("`n")) {
        $lastNewline = $text.LastIndexOf("`n")
        if ($lastNewline -lt 0) { return @() }
        $text = $text.Substring(0, $lastNewline + 1)
    }
    return @($text -split "`r?`n" | Where-Object { $_.StartsWith('S2A_PROGRESS ', [System.StringComparison]::Ordinal) })
}

function ConvertFrom-ProgressMarker {
    param([Parameter(Mandatory = $true)][string]$Line)
    $pattern = '^S2A_PROGRESS sample=(?<sample>[0-9]+) layer=(?<layer>[0-9]+) cycle=(?<cycle>[0-9]+) output=(?<output>[0-9]+) conv_tile_y=(?<tile_y>[0-9]+) conv_tile_x=(?<tile_x>[0-9]+) conv_group=(?<group>[0-9]+) conv_point=(?<point>[0-9]+) conv_reduction=(?<reduction>[0-9]+) conv_feature_scan=(?<feature_scan>[0-9]+) conv_weight_reduction=(?<weight_reduction>[0-9]+) conv_output_lane=(?<output_lane>[0-9]+) conv_output_point=(?<output_point>[0-9]+) pool_tap=(?<pool_tap>[0-9]+) feature_write_bytes=(?<bytes>[0-9]+) read_transactions=(?<reads>[0-9]+) write_transactions=(?<writes>[0-9]+) phase=(?<phase>start|running|complete)$'
    if ($Line -notmatch $pattern) { return $null }
    $signature = @(
        $Matches.layer,
        $Matches.output,
        $Matches.tile_y,
        $Matches.tile_x,
        $Matches.group,
        $Matches.point,
        $Matches.reduction,
        $Matches.feature_scan,
        $Matches.weight_reduction,
        $Matches.output_lane,
        $Matches.output_point,
        $Matches.pool_tap,
        $Matches.bytes,
        $Matches.reads,
        $Matches.writes
    ) -join '|'
    return [pscustomobject]@{
        sample = [int]$Matches.sample
        layer = [int]$Matches.layer
        cycle = [long]$Matches.cycle
        phase = [string]$Matches.phase
        signature = $signature
    }
}

function Test-ProgressSignatureChanged {
    param(
        [AllowEmptyString()][string]$PreviousSignature,
        [Parameter(Mandatory = $true)][string]$CurrentSignature
    )
    if ([string]::IsNullOrEmpty($PreviousSignature)) { return $false }
    return -not [string]::Equals($PreviousSignature, $CurrentSignature, [System.StringComparison]::Ordinal)
}

if ($RunSimulation -and -not $Compile) {
    throw 'RunSimulation 必须与 Compile 同次调用，防止运行未绑定的旧二进制。'
}
if ($MaxCycles -le 0 -or $MaxCycles -gt 4294967295) {
    throw 'MaxCycles 必须在 1..4294967295 范围内。'
}
if ($RunId -notmatch '^[A-Za-z0-9_-]+$') {
    throw 'RunId 仅允许 ASCII 字母、数字、下划线和连字符。'
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if ([string]::IsNullOrWhiteSpace($EvidenceDirectory)) {
    $EvidenceDirectory = Join-Path $repoRoot 'report\evidence\S2A-T68\run01'
}
$evidenceRoot = [System.IO.Path]::GetFullPath($EvidenceDirectory)
$prepareScript = Join-Path $PSScriptRoot 'prepare_s2a_network_backend_golden.py'
$verifyScript = Join-Path $PSScriptRoot 'verify_s2a_network_backend_golden.py'
$testbench = Join-Path $repoRoot 'sim\tb_s2a_network_backend_golden.sv'
$backendSource = Join-Path $repoRoot 'src\s2a_network_backend.sv'

if (-not (Test-Path -LiteralPath $prepareScript -PathType Leaf)) { throw "缺少 preparer：$prepareScript" }
if (-not (Test-Path -LiteralPath $verifyScript -PathType Leaf)) { throw "缺少只读 verifier：$verifyScript" }
if (-not (Test-Path -LiteralPath $testbench -PathType Leaf)) { throw "缺少 testbench：$testbench" }
if (-not (Test-Path -LiteralPath $backendSource -PathType Leaf)) { throw "缺少 backend：$backendSource" }

$prepareArgs = @(
    $prepareScript,
    '--sample-index', [string]$SampleIndex,
    '--output-root', $evidenceRoot
)
& $PythonExecutable @prepareArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$fixtureManifest = Join-Path $evidenceRoot ("fixtures\sample_{0:D3}\fixture_manifest.json" -f $SampleIndex)
$verifyArgs = @($verifyScript, '--manifest', $fixtureManifest)
& $PythonExecutable @verifyArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $Compile) {
    Write-Output "T68 fixture-only 完成；未编译、未启动仿真。EvidenceDirectory=$evidenceRoot"
    exit 0
}

if ($ExpectedBackendSha256 -notmatch '^[0-9a-fA-F]{64}$') {
    throw 'RTL compile/run 必须显式给出冻结 backend SHA-256。'
}
$actualBackendSha256 = Get-Sha256Literal -Path $backendSource
if ($actualBackendSha256 -ne $ExpectedBackendSha256.ToLowerInvariant()) {
    throw "当前 backend SHA 与冻结值不同；actual=$actualBackendSha256 expected=$ExpectedBackendSha256"
}

$runDirectory = Join-Path $evidenceRoot ("runs\sample_{0:D3}\{1}" -f $SampleIndex, $RunId)
if (Test-Path -LiteralPath $runDirectory) {
    throw "拒绝复用已存在的运行目录：$runDirectory"
}
$null = New-Item -ItemType Directory -Path $runDirectory -Force:$false
$buildDirectory = Join-Path $runDirectory 'build'
$null = New-Item -ItemType Directory -Path $buildDirectory -Force:$false

$toolBin = 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin'
$verilator = Join-Path $toolBin 'verilator.exe'
if (-not (Test-Path -LiteralPath $toolBin -PathType Container)) { throw "缺少指定 MSYS2 bin 目录：$toolBin" }
if (-not (Test-Path -LiteralPath $verilator -PathType Leaf)) { throw "缺少 Verilator：$verilator" }
$env:PATH = "$toolBin;$env:PATH"

$rtlRelativePaths = @(
    'src\s2a_network_descriptor_pkg.sv',
    'src\int8_maxpool_geometry.sv',
    'src\int8_maxpool_window.sv',
    'src\int8_route_query.sv',
    'src\int8_upsample_query.sv',
    'src\s2a_conv_tile_engine.sv',
    'src\s2a_maxpool_engine.sv',
    'src\s2a_route_engine.sv',
    'src\s2a_upsample_engine.sv',
    'src\s2a_network_backend.sv'
)
$rtlSources = @(
    foreach ($relativePath in $rtlRelativePaths) {
        $sourcePath = Join-Path $repoRoot $relativePath
        if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw "RTL source list 文件不存在：$sourcePath" }
        (Resolve-Path -LiteralPath $sourcePath).Path
    }
)
$compileSources = @($rtlSources) + @($testbench)

$sourceSnapshotRows = @(
    foreach ($sourcePath in $compileSources) {
        $sourceItem = Get-Item -LiteralPath $sourcePath
        [ordered]@{
            path = $sourceItem.FullName
            bytes = $sourceItem.Length
            sha256 = Get-Sha256Literal -Path $sourceItem.FullName
        }
    }
)
$currentBackendRow = $sourceSnapshotRows | Where-Object { $_.path -eq $backendSource }
if ($null -eq $currentBackendRow -or $currentBackendRow.sha256 -ne $ExpectedBackendSha256.ToLowerInvariant()) {
    throw '编译源列表中的 backend SHA 与显式冻结值不匹配。'
}

$commandArgs = @(
    '--binary',
    '--timing',
    '--top-module', 'tb_s2a_network_backend_golden',
    '--Mdir', $buildDirectory,
    '-CFLAGS', '-D_GLIBCXX_USE_CXX11_ABI=0'
) + $compileSources
$snapshot = [ordered]@{
    schema_version = 'gestureforge_s2a_t68_compile_source_snapshot_v1'
    task_id = 'S2A-T68'
    sample_index = $SampleIndex
    run_id = $RunId
    top_module = 'tb_s2a_network_backend_golden'
    backend_sha256_expected = $ExpectedBackendSha256.ToLowerInvariant()
    source_count = $compileSources.Count
    verilator_path = $verilator
    command = @($commandArgs)
    sources = $sourceSnapshotRows
    simulator_started = $false
}
$snapshotPath = Join-Path $runDirectory 'compile_source_snapshot.json'
Write-Utf8NoBom -Path $snapshotPath -Content (($snapshot | ConvertTo-Json -Depth 8) + [Environment]::NewLine)

$versionLines = @(& $verilator '--version' 2>&1)
$versionExitCode = $LASTEXITCODE
Write-CommandLog -Path (Join-Path $runDirectory 'verilator_version.txt') -Lines $versionLines
if ($versionExitCode -ne 0) {
    $versionRecord = [ordered]@{ exit_code = $versionExitCode; output = @($versionLines) }
    Write-Utf8NoBom -Path (Join-Path $runDirectory 'verilator_version_record.json') -Content (($versionRecord | ConvertTo-Json -Depth 4) + [Environment]::NewLine)
    exit $versionExitCode
}

$compileLog = Join-Path $runDirectory 'verilator_compile_console.txt'
$compileWatch = [System.Diagnostics.Stopwatch]::StartNew()
$compileOutput = @(& $verilator @commandArgs 2>&1)
$compileExitCode = $LASTEXITCODE
$compileWatch.Stop()
Write-CommandLog -Path $compileLog -Lines $compileOutput
$postCompileSourceRows = @(
    foreach ($sourcePath in $compileSources) {
        $sourceItem = Get-Item -LiteralPath $sourcePath
        [ordered]@{
            path = $sourceItem.FullName
            bytes = $sourceItem.Length
            sha256 = Get-Sha256Literal -Path $sourceItem.FullName
        }
    }
)
$compileRecord = [ordered]@{
    schema_version = 'gestureforge_s2a_t68_compile_execution_v1'
    command = @($verilator) + @($commandArgs)
    exit_code = $compileExitCode
    duration_seconds = [Math]::Round($compileWatch.Elapsed.TotalSeconds, 3)
    source_unchanged = (($sourceSnapshotRows | ConvertTo-Json -Depth 5 -Compress) -ceq ($postCompileSourceRows | ConvertTo-Json -Depth 5 -Compress))
    sources_after = $postCompileSourceRows
    console_path = $compileLog
    simulator_started = $false
}
$compileRecordPath = Join-Path $runDirectory 'compile_execution_record.json'
Write-Utf8NoBom -Path $compileRecordPath -Content (($compileRecord | ConvertTo-Json -Depth 8) + [Environment]::NewLine)
if (-not $compileRecord.source_unchanged) {
    throw "RTL compile 期间输入源发生变化；记录已保留：$compileRecordPath"
}
if ($compileExitCode -ne 0) { exit $compileExitCode }

if ($RunSimulation) {
    $fixtureDirectory = Join-Path $evidenceRoot ("fixtures\sample_{0:D3}" -f $SampleIndex)
    $binary = Join-Path $buildDirectory 'Vtb_s2a_network_backend_golden.exe'
    if (-not (Test-Path -LiteralPath $binary -PathType Leaf)) { throw "Verilator 未生成预期 binary：$binary" }
    $resultPath = Join-Path $runDirectory 'result_summary.txt'
    $progressMarkerPath = Join-Path $runDirectory 'progress_markers.txt'
    $simulationArgs = @(
        "+SAMPLE_INDEX=$SampleIndex",
        "+FIXTURE_DIR=$fixtureDirectory",
        "+MAX_CYCLES=$MaxCycles",
        "+RESULT_FILE=$resultPath",
        "+PROGRESS_FILE=$progressMarkerPath"
    )
    $simulationLog = Join-Path $runDirectory 'verilator_simulation_console.txt'
    $simulationErrorLog = Join-Path $runDirectory 'verilator_simulation_stderr.txt'
    $simulationWatch = [System.Diagnostics.Stopwatch]::StartNew()
    $quotedSimulationArguments = ($simulationArgs | ForEach-Object { Quote-ProcessArgument -Argument ([string]$_) }) -join ' '
    $simProcess = Start-Process -FilePath $binary -ArgumentList $quotedSimulationArguments `
        -WorkingDirectory $buildDirectory -WindowStyle Hidden `
        -RedirectStandardOutput $simulationLog -RedirectStandardError $simulationErrorLog -PassThru
    $processStartTimeUtc = $simProcess.StartTime.ToUniversalTime()
    $lastProgressAtUtc = $processStartTimeUtc
    $lastProgressSignature = ''
    $processedMarkerCount = 0
    $progressMarkerCount = 0
    $previousProgressCycle = -1L
    $firstProgressPhase = ''
    $lastProgressPhase = ''
    $functionalProgressObserved = $false
    $badProgressMarkerSeen = $false
    $watchdogFailure = $false
    $watchdogTerminationReason = 'PROCESS_EXITED'
    $identityVerifiedAtTimeout = $false
    $killRequested = $false
    while ($true) {
        $simProcess.Refresh()
        $processExited = $simProcess.HasExited
        $progressLines = @(Get-CompleteProgressMarkerLines -Path $progressMarkerPath)
        if ($progressLines.Count -lt $processedMarkerCount) {
            $badProgressMarkerSeen = $true
        } else {
            for ($markerIndex = $processedMarkerCount; $markerIndex -lt $progressLines.Count; $markerIndex++) {
                $progressMarker = ConvertFrom-ProgressMarker -Line ([string]$progressLines[$markerIndex])
                if ($null -eq $progressMarker) {
                    $badProgressMarkerSeen = $true
                    $processedMarkerCount++
                    continue
                }
                $phaseSequenceValid = if ($progressMarkerCount -eq 0) {
                    $progressMarker.phase -eq 'start'
                } else {
                    ($progressMarker.phase -ne 'start') -and ($lastProgressPhase -ne 'complete')
                }
                if (($progressMarker.sample -ne $SampleIndex) -or
                    ($progressMarker.layer -lt 0) -or ($progressMarker.layer -ge 38) -or
                    ($progressMarker.cycle -lt $previousProgressCycle) -or
                    ($progressMarker.cycle -gt $MaxCycles) -or (-not $phaseSequenceValid)) {
                    $badProgressMarkerSeen = $true
                    $processedMarkerCount++
                    continue
                }
                if ($progressMarkerCount -eq 0) {
                    $firstProgressPhase = $progressMarker.phase
                    $lastProgressSignature = $progressMarker.signature
                } else {
                    if (Test-ProgressSignatureChanged -PreviousSignature $lastProgressSignature `
                        -CurrentSignature $progressMarker.signature) {
                        $lastProgressAtUtc = [datetime]::UtcNow
                        $functionalProgressObserved = $true
                    }
                    $lastProgressSignature = $progressMarker.signature
                }
                $previousProgressCycle = $progressMarker.cycle
                $lastProgressPhase = $progressMarker.phase
                $progressMarkerCount++
                $processedMarkerCount++
            }
        }
        if ($processExited) { break }
        if (([datetime]::UtcNow - $lastProgressAtUtc).TotalSeconds -ge 1800) {
            $watchdogFailure = $true
            $identityVerifiedAtTimeout = Test-StartedProcessIdentity -Process $simProcess `
                -ExpectedPath $binary -ExpectedArguments $simulationArgs -ExpectedStartTimeUtc $processStartTimeUtc
            if ($identityVerifiedAtTimeout) {
                $watchdogTerminationReason = 'NO_PROGRESS_30_MINUTES_IDENTITY_VERIFIED_KILLED_OWN_PROCESS'
                try {
                    $simProcess.Kill()
                    $killRequested = $true
                    $simProcess.WaitForExit()
                } catch {
                    $watchdogTerminationReason = 'NO_PROGRESS_30_MINUTES_IDENTITY_VERIFIED_KILL_FAILED'
                }
            } else {
                $watchdogTerminationReason = 'NO_PROGRESS_30_MINUTES_IDENTITY_UNVERIFIED_NOT_KILLED'
            }
            break
        }
        Start-Sleep -Seconds 5
    }
    $simProcess.Refresh()
    $simulationExitCode = if ($simProcess.HasExited) { $simProcess.ExitCode } else { $null }
    $simulationWatch.Stop()
    $progressMarkersValid = (-not $badProgressMarkerSeen) -and ($progressMarkerCount -ge 2) -and
        $functionalProgressObserved -and ($firstProgressPhase -eq 'start')
    if (-not $watchdogFailure -and ((-not $progressMarkersValid) -or ($lastProgressPhase -ne 'complete'))) {
        $watchdogTerminationReason = 'PROCESS_EXITED_WITHOUT_VALID_COMPLETE_PROGRESS'
    }
    $runnerExitCode = 0
    if ($watchdogFailure) {
        $runnerExitCode = 124
    } elseif (($simulationExitCode -ne 0) -or (-not $progressMarkersValid) -or ($lastProgressPhase -ne 'complete')) {
        $runnerExitCode = if ($simulationExitCode -and $simulationExitCode -ne 0) { $simulationExitCode } else { 125 }
    }
    $resultSummaryValid = $false
    if (($runnerExitCode -eq 0) -and (Test-Path -LiteralPath $resultPath -PathType Leaf)) {
        $resultSummary = [System.IO.File]::ReadAllText($resultPath, [System.Text.Encoding]::UTF8)
        $resultSummaryValid = ($resultSummary -match '(?m)^status=PASS_LAYERWISE_EXACT_GOLDEN$') -and
            ($resultSummary -match '(?m)^feature_write_bytes=11382150 mismatches=0 cycles=[0-9]+$')
        if (-not $resultSummaryValid) {
            $runnerExitCode = 125
            $watchdogTerminationReason = 'RESULT_SUMMARY_INVALID'
        }
    } elseif ($runnerExitCode -eq 0) {
        $runnerExitCode = 125
        $watchdogTerminationReason = 'RESULT_SUMMARY_MISSING'
    }
    $simulationRecord = [ordered]@{
        schema_version = 'gestureforge_s2a_t68_simulation_execution_v1'
        command = @($binary) + @($simulationArgs)
        exit_code = $simulationExitCode
        runner_exit_code = $runnerExitCode
        duration_seconds = [Math]::Round($simulationWatch.Elapsed.TotalSeconds, 3)
        sample_index = $SampleIndex
        result_summary_path = $resultPath
        result_summary_sha256 = if (Test-Path -LiteralPath $resultPath -PathType Leaf) { Get-Sha256Literal -Path $resultPath } else { $null }
        console_path = $simulationLog
        stderr_path = $simulationErrorLog
        progress_marker_path = $progressMarkerPath
        progress_marker_count = $progressMarkerCount
        progress_markers_valid = $progressMarkersValid
        functional_progress_observed = $functionalProgressObserved
        bad_progress_marker_seen = $badProgressMarkerSeen
        last_progress_phase = $lastProgressPhase
        last_progress_signature = $lastProgressSignature
        result_summary_valid = $resultSummaryValid
        progress_interval_cycles = 30000000
        watchdog_no_progress_seconds = 1800
        watchdog_failure = $watchdogFailure
        watchdog_termination_reason = $watchdogTerminationReason
        identity_verified_at_timeout = $identityVerifiedAtTimeout
        kill_requested = $killRequested
        process_id = $simProcess.Id
        process_start_time_utc = $processStartTimeUtc.ToString('o')
        process_executable_path = $binary
        wave_dump_requested = $false
    }
    $simulationRecordPath = Join-Path $runDirectory 'simulation_execution_record.json'
    Write-Utf8NoBom -Path $simulationRecordPath -Content (($simulationRecord | ConvertTo-Json -Depth 5) + [Environment]::NewLine)
    Write-Output "T68 sample=$SampleIndex simulation exit_code=$simulationExitCode runner_exit_code=$runnerExitCode duration_seconds=$($simulationRecord.duration_seconds) watchdog=$watchdogTerminationReason"
    if ($runnerExitCode -ne 0) { exit $runnerExitCode }
}

Write-Output "T68 runner 完成；run_directory=$runDirectory compile_exit_code=$compileExitCode simulation_started=$RunSimulation"
exit 0
