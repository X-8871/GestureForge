[CmdletBinding()]
param(
    [ValidatePattern('^protocol_directed[0-9]{2}$')]
    [string]$EvidenceRunName = 'protocol_directed01'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

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

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][string[]]$Arguments
    )
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = @(& $Executable @Arguments 2>&1)
        $exitCode = $LASTEXITCODE
        return [pscustomobject]@{
            output = @($output)
            exit_code = $exitCode
        }
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
}

function Get-SourceRows {
    param([Parameter(Mandatory = $true)][string[]]$Paths)
    return @(
        foreach ($path in $Paths) {
            $item = Get-Item -LiteralPath $path -ErrorAction Stop
            [ordered]@{
                path = $item.FullName
                bytes = $item.Length
                sha256 = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            }
        }
    )
}

$repoRoot = 'D:\FPGA_Competition'
$toolchainRoot = 'D:\FPGA_S2A_MSYS2_20261001\env'
$toolBin = Join-Path $toolchainRoot 'mingw64\bin'
$makeBin = Join-Path $toolchainRoot 'usr\bin'
$verilator = Join-Path $toolBin 'verilator_bin.exe'
$makePath = Join-Path $makeBin 'make.exe'
$compilerPath = Join-Path $toolBin 'g++.exe'
$verilatorRoot = [System.IO.Path]::GetFullPath((Join-Path $toolBin '..\share\verilator'))
$env:PATH = "$makeBin;$toolBin;$env:PATH"
$env:VERILATOR_ROOT = $verilatorRoot

foreach ($directory in @($toolchainRoot, $toolBin, $makeBin, $verilatorRoot)) {
    if (-not (Test-Path -LiteralPath $directory -PathType Container)) {
        throw "缺少批准 toolchain 目录：$directory"
    }
}
foreach ($file in @($verilator, $makePath, $compilerPath)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "缺少批准 toolchain 文件：$file"
    }
}
$resolvedMake = @(Get-Command -Name 'make.exe' -CommandType Application -ErrorAction Stop)[0]
$resolvedCompiler = @(Get-Command -Name 'g++.exe' -CommandType Application -ErrorAction Stop)[0]
$resolvedMakePath = [System.IO.Path]::GetFullPath($resolvedMake.Path)
$resolvedCompilerPath = [System.IO.Path]::GetFullPath($resolvedCompiler.Path)
if ($resolvedMakePath -ine [System.IO.Path]::GetFullPath($makePath)) {
    throw "PATH 中解析到批准 toolchain 之外的 make：$resolvedMakePath"
}
if ($resolvedCompilerPath -ine [System.IO.Path]::GetFullPath($compilerPath)) {
    throw "PATH 中解析到批准 toolchain 之外的 g++：$resolvedCompilerPath"
}
if (-not (Test-Path -LiteralPath $verilatorRoot -PathType Container)) {
    throw "缺少 Verilator 数据目录：$verilatorRoot"
}

$evidenceParent = $PSScriptRoot
$evidenceDirectory = Join-Path $evidenceParent $EvidenceRunName
if (-not (Test-Path -LiteralPath $evidenceParent -PathType Container)) {
    throw "缺少已核对的证据父目录：$evidenceParent"
}
if (Test-Path -LiteralPath $evidenceDirectory) {
    throw "证据目录已存在，拒绝复用或覆盖：$evidenceDirectory"
}
$null = [System.IO.Directory]::CreateDirectory($evidenceDirectory)
$buildDirectory = Join-Path $evidenceDirectory 'build'
$null = [System.IO.Directory]::CreateDirectory($buildDirectory)

$relativeSources = @(
    'src\s2a_network_descriptor_pkg.sv',
    'src\int8_maxpool_geometry.sv',
    'src\int8_maxpool_window.sv',
    'src\int8_route_query.sv',
    'src\int8_upsample_query.sv',
    'src\s2a_control_csr.sv',
    'src\s2a_conv_tile_engine.sv',
    'src\s2a_maxpool_engine.sv',
    'src\s2a_route_engine.sv',
    'src\s2a_upsample_engine.sv',
    'src\s2a_network_backend.sv',
    'sim\tb_s2a_backend_fault_recovery.sv'
)
$sources = @(
    foreach ($relativePath in $relativeSources) {
        $path = Join-Path $repoRoot $relativePath
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "缺少编译源：$path" }
        (Resolve-Path -LiteralPath $path).Path
    }
)
$sourceRows = Get-SourceRows -Paths $sources
$compileArguments = @(
    '--binary',
    '--timing',
    '--trace',
    '-Wno-fatal',
    '--top-module', 'tb_s2a_backend_fault_recovery',
    '--Mdir', $buildDirectory,
    '-CFLAGS', '-D_GLIBCXX_USE_CXX11_ABI=0'
) + $sources
$versionResult = Invoke-NativeCommand -Executable $verilator -Arguments @('--version')
$versionOutput = @($versionResult.output)
$versionExitCode = [int]$versionResult.exit_code
Write-CommandLog -Path (Join-Path $evidenceDirectory 'verilator_version_console.txt') -Lines $versionOutput
if ($versionExitCode -ne 0) {
    $versionRecord = [ordered]@{
        command = @($verilator, '--version')
        exit_code = $versionExitCode
        output = @($versionOutput)
        simulator_started = $false
    }
    Write-Utf8NoBom -Path (Join-Path $evidenceDirectory 'verilator_version_record.json') `
        -Content (($versionRecord | ConvertTo-Json -Depth 5) + [Environment]::NewLine)
    exit $versionExitCode
}

$snapshot = [ordered]@{
    schema_version = 'gestureforge_s2a_t68_backend_fault_compile_snapshot_v1'
    task_id = 'S2A-T68-PROTOCOL-DIRECTED-01'
    top_module = 'tb_s2a_backend_fault_recovery'
    compile_source_count = $sources.Count
    verilator_path = $verilator
    verilator_root = $verilatorRoot
    make_path = $resolvedMakePath
    compiler_path = $resolvedCompilerPath
    toolchain_path_prefix = @($makeBin, $toolBin)
    command = @($verilator) + @($compileArguments)
    sources = $sourceRows
    simulator_started = $false
}
Write-Utf8NoBom -Path (Join-Path $evidenceDirectory 'compile_source_snapshot.json') `
    -Content (($snapshot | ConvertTo-Json -Depth 8) + [Environment]::NewLine)

$compileWatch = [System.Diagnostics.Stopwatch]::StartNew()
$compileResult = Invoke-NativeCommand -Executable $verilator -Arguments $compileArguments
$compileOutput = @($compileResult.output)
$compileExitCode = [int]$compileResult.exit_code
$compileWatch.Stop()
Write-CommandLog -Path (Join-Path $evidenceDirectory 'compile_console.txt') -Lines $compileOutput
$sourceRowsAfterCompile = Get-SourceRows -Paths $sources
$sourceUnchanged = (($sourceRows | ConvertTo-Json -Depth 5 -Compress) -ceq
    ($sourceRowsAfterCompile | ConvertTo-Json -Depth 5 -Compress))
$warningLimits = [ordered]@{
    TIMESCALEMOD = 11
    UNSIGNED = 1
    WIDTHEXPAND = 36
    WIDTHTRUNC = 16
}
$warningCounts = [ordered]@{
    TIMESCALEMOD = 0
    UNSIGNED = 0
    WIDTHEXPAND = 0
    WIDTHTRUNC = 0
}
$unknownWarningCategories = @{}
foreach ($line in $compileOutput) {
    if (([string]$line) -match '%Warning-([A-Z0-9_]+):') {
        $category = $Matches[1]
        if ($warningCounts.Contains($category)) {
            $warningCounts[$category] = [int]$warningCounts[$category] + 1
        } else {
            $unknownWarningCategories[$category] = 1 + [int]$unknownWarningCategories[$category]
        }
    }
}
$overLimitWarningCategories = @(
    foreach ($category in $warningLimits.Keys) {
        if ([int]$warningCounts[$category] -gt [int]$warningLimits[$category]) {
            $category
        }
    }
)
$warningGatePassed = ($unknownWarningCategories.Count -eq 0) -and
    ($overLimitWarningCategories.Count -eq 0)
$warningTotal = 0
foreach ($category in $warningCounts.Keys) {
    $warningTotal += [int]$warningCounts[$category]
}
$compileText = ($compileOutput | ForEach-Object { [string]$_ }) -join [Environment]::NewLine
$compileErrorsDetected = $compileText.Contains('%Error:')
$compileRecord = [ordered]@{
    schema_version = 'gestureforge_s2a_t68_backend_fault_compile_record_v1'
    command = @($verilator) + @($compileArguments)
    exit_code = $compileExitCode
    warning_count = $warningTotal
    warning_counts = $warningCounts
    warning_limits = $warningLimits
    unknown_warning_categories = @($unknownWarningCategories.Keys)
    over_limit_warning_categories = $overLimitWarningCategories
    warning_gate_passed = [bool]$warningGatePassed
    errors_detected = [bool]$compileErrorsDetected
    duration_seconds = [Math]::Round($compileWatch.Elapsed.TotalSeconds, 3)
    source_unchanged = $sourceUnchanged
    sources_after = $sourceRowsAfterCompile
    verilator_path = $verilator
    verilator_root = $verilatorRoot
    make_path = $resolvedMakePath
    compiler_path = $resolvedCompilerPath
    console_path = Join-Path $evidenceDirectory 'compile_console.txt'
    simulator_started = $false
}
Write-Utf8NoBom -Path (Join-Path $evidenceDirectory 'compile_execution_record.json') `
    -Content (($compileRecord | ConvertTo-Json -Depth 8) + [Environment]::NewLine)
if (-not $sourceUnchanged) { throw '编译期间源文件发生变化；保留快照与编译记录，停止运行。' }
if ($compileExitCode -ne 0) { exit $compileExitCode }
if ($compileErrorsDetected -or -not $warningGatePassed) { exit 1 }

$simulationExecutable = Join-Path $buildDirectory 'Vtb_s2a_backend_fault_recovery.exe'
if (-not (Test-Path -LiteralPath $simulationExecutable -PathType Leaf)) {
    throw "Verilator 未生成预期短仿真程序：$simulationExecutable"
}
$waveformPath = Join-Path $evidenceDirectory 'backend_fault_recovery.vcd'
$simulationWatch = [System.Diagnostics.Stopwatch]::StartNew()
$simulationResult = Invoke-NativeCommand -Executable $simulationExecutable `
    -Arguments @("+WAVEFORM_PATH=$waveformPath")
$simulationOutput = @($simulationResult.output)
$simulationExitCode = [int]$simulationResult.exit_code
$simulationWatch.Stop()
Write-CommandLog -Path (Join-Path $evidenceDirectory 'simulation_console.txt') -Lines $simulationOutput
$simulationLines = @($simulationOutput | ForEach-Object { [string]$_ })
$simulationText = $simulationLines -join [Environment]::NewLine
$passObserved = ($simulationText -match '(?m)^PASS_S2A_BACKEND_FAULT_CANCEL_RECOVERY ')
$pendingOutputWriteMarkerCounts = [ordered]@{
    soft_reset = 0
    hard_reset = 0
    csr_timeout = 0
}
$outputWriteCancelMarkerCounts = [ordered]@{
    soft_reset = 0
    hard_reset = 0
    csr_timeout = 0
}
$cancelCaseMarkerCounts = [ordered]@{
    soft_reset_pending_output_write = 0
    hard_reset_pending_output_write = 0
    csr_timeout_pending_output_write = 0
    soft_reset_pending_read = 0
}
$retryCaseMarkerCounts = [ordered]@{
    after_soft_reset = 0
    after_hard_reset = 0
    after_csr_timeout_ack = 0
}
$unexpectedCancelCaseMarkers = @()
$unexpectedRetryCaseMarkers = @()
foreach ($line in $simulationLines) {
    if ($line -match '^S2A_PENDING_OUTPUT_WRITE case=(soft_reset|hard_reset|csr_timeout) layer=0 ') {
        $caseName = $Matches[1]
        $pendingOutputWriteMarkerCounts[$caseName] = [int]$pendingOutputWriteMarkerCounts[$caseName] + 1
    }
    if ($line -match '^S2A_OUTPUT_WRITE_CANCEL kind=(soft_reset|hard_reset|csr_timeout) layer=0 ') {
        $caseName = $Matches[1]
        $outputWriteCancelMarkerCounts[$caseName] = [int]$outputWriteCancelMarkerCounts[$caseName] + 1
    }
    if ($line -match '^S2A_CANCEL_CASE\b') {
        if ($line -match '^S2A_CANCEL_CASE kind=(soft_reset|hard_reset|csr_timeout) request=pending_output_write cancelled=1 writes_before=([0-9]+) writes_after=([0-9]+)$') {
            $caseName = $Matches[1]
            $markerKey = "${caseName}_pending_output_write"
            if ($Matches[2] -ne '0' -or $Matches[3] -ne '0') {
                $unexpectedCancelCaseMarkers += $line
            }
            $cancelCaseMarkerCounts[$markerKey] = [int]$cancelCaseMarkerCounts[$markerKey] + 1
        } elseif ($line -match '^S2A_CANCEL_CASE kind=soft_reset request=pending_read cancelled=1 ack_restart=ready$') {
            $cancelCaseMarkerCounts['soft_reset_pending_read'] = [int]$cancelCaseMarkerCounts['soft_reset_pending_read'] + 1
        } else {
            $unexpectedCancelCaseMarkers += $line
        }
    }
    if ($line -match '^S2A_RETRY_CASE\b') {
        if ($line -match '^S2A_RETRY_CASE after=soft_reset request=pending_output_write next=hard_reset start_accepted=1$') {
            $retryCaseMarkerCounts['after_soft_reset'] = [int]$retryCaseMarkerCounts['after_soft_reset'] + 1
        } elseif ($line -match '^S2A_RETRY_CASE after=hard_reset request=pending_output_write next=csr_timeout start_accepted=1$') {
            $retryCaseMarkerCounts['after_hard_reset'] = [int]$retryCaseMarkerCounts['after_hard_reset'] + 1
        } elseif ($line -match '^S2A_RETRY_CASE after=csr_timeout_ack request=pending_read next=soft_reset start_accepted=1$') {
            $retryCaseMarkerCounts['after_csr_timeout_ack'] = [int]$retryCaseMarkerCounts['after_csr_timeout_ack'] + 1
        } else {
            $unexpectedRetryCaseMarkers += $line
        }
    }
}
$outputWriteMarkersPassed = $true
foreach ($caseName in $pendingOutputWriteMarkerCounts.Keys) {
    if ([int]$pendingOutputWriteMarkerCounts[$caseName] -ne 1 -or
        [int]$outputWriteCancelMarkerCounts[$caseName] -ne 1) {
        $outputWriteMarkersPassed = $false
    }
}
$cancelCaseMarkersPassed = ($unexpectedCancelCaseMarkers.Count -eq 0)
foreach ($markerName in $cancelCaseMarkerCounts.Keys) {
    if ([int]$cancelCaseMarkerCounts[$markerName] -ne 1) {
        $cancelCaseMarkersPassed = $false
    }
}
$retryCaseMarkersPassed = ($unexpectedRetryCaseMarkers.Count -eq 0)
foreach ($markerName in $retryCaseMarkerCounts.Keys) {
    if ([int]$retryCaseMarkerCounts[$markerName] -ne 1) {
        $retryCaseMarkersPassed = $false
    }
}
$waveformExists = Test-Path -LiteralPath $waveformPath -PathType Leaf
$waveformBytes = 0
$waveformSha256 = $null
$waveformValid = $false
if ($waveformExists) {
    $waveformItem = Get-Item -LiteralPath $waveformPath -ErrorAction Stop
    $waveformBytes = [long]$waveformItem.Length
    if ($waveformBytes -gt 0) {
        $waveformSha256 = (Get-FileHash -LiteralPath $waveformPath -Algorithm SHA256).Hash.ToLowerInvariant()
        $waveformValid = ($waveformSha256 -match '^[0-9a-f]{64}$')
    }
}
$simulationGatePassed = ($simulationExitCode -eq 0) -and $passObserved -and
    $outputWriteMarkersPassed -and $cancelCaseMarkersPassed -and $retryCaseMarkersPassed -and
    $waveformValid
$simulationRecord = [ordered]@{
    schema_version = 'gestureforge_s2a_t68_backend_fault_simulation_record_v1'
    command = @($simulationExecutable)
    exit_code = $simulationExitCode
    pass_marker_observed = [bool]$passObserved
    pending_output_write_marker_counts = $pendingOutputWriteMarkerCounts
    output_write_cancel_marker_counts = $outputWriteCancelMarkerCounts
    output_write_markers_passed = [bool]$outputWriteMarkersPassed
    cancel_case_marker_counts = $cancelCaseMarkerCounts
    unexpected_cancel_case_markers = @($unexpectedCancelCaseMarkers)
    cancel_case_markers_passed = [bool]$cancelCaseMarkersPassed
    retry_case_marker_counts = $retryCaseMarkerCounts
    unexpected_retry_case_markers = @($unexpectedRetryCaseMarkers)
    retry_case_markers_passed = [bool]$retryCaseMarkersPassed
    waveform_path = $waveformPath
    waveform_exists = [bool]$waveformExists
    waveform_bytes = $waveformBytes
    waveform_sha256 = $waveformSha256
    waveform_valid = [bool]$waveformValid
    simulator_started = $true
    duration_seconds = [Math]::Round($simulationWatch.Elapsed.TotalSeconds, 3)
    compile_source_snapshot = Join-Path $evidenceDirectory 'compile_source_snapshot.json'
    source_count = $sources.Count
    error_responses = @(6, 7)
    cancellation_cases = @('soft_reset', 'hard_reset', 'csr_timeout')
    console_path = Join-Path $evidenceDirectory 'simulation_console.txt'
    simulator_scope = '真实 backend + CSR layer0 首笔 output write reset/timeout 取消定向测试'
}
Write-Utf8NoBom -Path (Join-Path $evidenceDirectory 'simulation_execution_record.json') `
    -Content (($simulationRecord | ConvertTo-Json -Depth 6) + [Environment]::NewLine)
if ($simulationExitCode -ne 0) { exit $simulationExitCode }
if (-not $simulationGatePassed) { exit 1 }
Write-Output "PASS_S2A_BACKEND_FAULT_CANCEL_RECOVERY evidence=$evidenceDirectory duration_seconds=$($simulationRecord.duration_seconds)"
exit 0
