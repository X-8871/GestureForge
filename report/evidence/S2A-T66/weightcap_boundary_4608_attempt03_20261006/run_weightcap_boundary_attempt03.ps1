[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$rootPath = 'D:\FPGA_Competition'
$evidencePath = 'D:\FPGA_Competition\report\evidence\S2A-T66\weightcap_boundary_4608_attempt03_20261006'
$buildPath = Join-Path $evidencePath 'build'
$dutPath = Join-Path $rootPath 'src\s2a_conv_tile_engine.sv'
$packagePath = Join-Path $rootPath 'src\s2a_network_descriptor_pkg.sv'
$benchPath = Join-Path $evidencePath 'tb_s2a_weightcap_boundary_attempt03.sv'
$compileCmdPath = Join-Path $evidencePath 'compile.cmd'
$simulateCmdPath = Join-Path $evidencePath 'simulate.cmd'
$compileShPath = Join-Path $evidencePath 'compile.sh'
$simulateShPath = Join-Path $evidencePath 'simulate.sh'
$cmdPath = 'C:\Windows\System32\cmd.exe'
$expectedDutSha = '76ca735b14802e26f0a4b016989e13b43cf8bd904587ccea37651c757d089300'
$utf8 = [System.Text.UTF8Encoding]::new($false)

function Write-NewText {
    param([Parameter(Mandatory = $true)][string]$Path,
          [Parameter(Mandatory = $true)][string]$Text)
    $stream = [System.IO.File]::Open(
        $Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try {
        $bytes = $utf8.GetBytes($Text)
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush()
    }
    finally { $stream.Dispose() }
}

function Write-NewJson {
    param([Parameter(Mandatory = $true)][string]$Path,
          [Parameter(Mandatory = $true)][object]$Value)
    Write-NewText -Path $Path -Text (($Value | ConvertTo-Json -Depth 16) + [Environment]::NewLine)
}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    (Get-FileHash -LiteralPath $Path -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
}

function Assert-ExactFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($item.PSIsContainer -or $item.FullName -cne $Path -or
        ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        throw "文件类型、精确路径或重解析属性核验失败：$Path"
    }
    $item
}

function Assert-ExactDirectory {
    param([Parameter(Mandatory = $true)][string]$Path)
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if (-not $item.PSIsContainer -or $item.FullName -cne $Path -or
        ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        throw "目录类型、精确路径或重解析属性核验失败：$Path"
    }
    $item
}

function Get-FileBinding {
    param([Parameter(Mandatory = $true)][string[]]$Paths)
    @(
        foreach ($path in $Paths) {
            $item = Assert-ExactFile -Path $path
            [ordered]@{
                path = $item.FullName
                bytes = [long]$item.Length
                sha256 = Get-Sha256 -Path $item.FullName
            }
        }
    )
}

function Get-ToolProcessSnapshot {
    @(
        Get-Process -ErrorAction Stop |
            Where-Object { $_.ProcessName -match '^(verilator_bin|make|g\+\+|Vtb_s2a_weightcap_boundary)$' } |
            Sort-Object ProcessName, Id |
            ForEach-Object { [ordered]@{ process_name = $_.ProcessName; process_id = [int]$_.Id } }
    )
}

function Invoke-CapturedCommand {
    param([Parameter(Mandatory = $true)][string]$Path)
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $cmdPath
    $startInfo.ArgumentList.Add('/d')
    $startInfo.ArgumentList.Add('/c')
    $startInfo.ArgumentList.Add($Path)
    $startInfo.WorkingDirectory = $evidencePath
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.StandardOutputEncoding = $utf8
    $startInfo.StandardErrorEncoding = $utf8
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    $watch = [System.Diagnostics.Stopwatch]::StartNew()
    if (-not $process.Start()) { throw "无法启动包装器：$Path" }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.WaitForExit()
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    $exitCode = [int]$process.ExitCode
    $watch.Stop()
    $process.Dispose()
    [ordered]@{
        command = @($cmdPath, '/d', '/c', $Path)
        exit_code = $exitCode
        stdout = $stdout
        stderr = $stderr
        duration_seconds = [Math]::Round($watch.Elapsed.TotalSeconds, 3)
    }
}

Assert-ExactDirectory -Path $rootPath | Out-Null
Assert-ExactDirectory -Path (Join-Path $rootPath 'src') | Out-Null
Assert-ExactDirectory -Path $evidencePath | Out-Null
foreach ($path in @($dutPath, $packagePath, $benchPath, $compileCmdPath,
                     $simulateCmdPath, $compileShPath, $simulateShPath, $cmdPath)) {
    Assert-ExactFile -Path $path | Out-Null
}

$actualDutSha = Get-Sha256 -Path $dutPath
if ($actualDutSha -cne $expectedDutSha) {
    throw "候选 RTL hash 与指定基线不符：expected=$expectedDutSha actual=$actualDutSha"
}

$outputNames = @(
    'source_manifest.json', 'compile_stdout.txt', 'compile_stderr.txt', 'compile_console.txt',
    'compile_execution_record.json', 'compile_status.json', 'simulation_stdout.txt',
    'simulation_stderr.txt', 'simulation_console.txt', 'simulation_execution_record.json',
    'simulation_status.json', 'attempt_summary.json'
)
$existingOutputs = @($outputNames | ForEach-Object { Join-Path $evidencePath $_ } |
    Where-Object { Test-Path -LiteralPath $_ })
if ($existingOutputs.Count -gt 0) {
    throw "拒绝覆盖既有 attempt03 证据：$($existingOutputs -join ', ')"
}
if (Test-Path -LiteralPath $buildPath) { throw "拒绝复用既有构建目录：$buildPath" }

$busyBefore = @(Get-ToolProcessSnapshot)
if ($busyBefore.Count -gt 0) {
    throw "发现并行 Verilator/build/simulator 进程，未启动本次验证：$($busyBefore | ConvertTo-Json -Compress)"
}

foreach ($directory in @((Join-Path $evidencePath 'msys_home'), (Join-Path $evidencePath 'msys_temp'), $buildPath)) {
    if (Test-Path -LiteralPath $directory) { throw "拒绝复用临时目录：$directory" }
    [void][System.IO.Directory]::CreateDirectory($directory)
    Assert-ExactDirectory -Path $directory | Out-Null
}

$sourcePaths = @($packagePath, $dutPath, $benchPath, $compileCmdPath,
                 $simulateCmdPath, $compileShPath, $simulateShPath, $PSCommandPath)
$sourceRowsBefore = Get-FileBinding -Paths $sourcePaths
$manifest = [ordered]@{
    schema_version = 's2a_t66_weightcap_boundary_manifest_v1'
    evidence_path = $evidencePath
    candidate_dut_sha256 = $actualDutSha
    ram_contract = [ordered]@{
        lane_count = 8
        maximum_reduction_entries_per_lane = 4608
        maximum_weight_group_bytes = 36864
        physical_storage_bytes = 36864
    }
    test_scope = 'layer26 legal K=4608 descriptor; feature fill followed by last output group 504..511; reject K=4609 before memory requests'
    source_rows = $sourceRowsBefore
}
$manifestPath = Join-Path $evidencePath 'source_manifest.json'
Write-NewJson -Path $manifestPath -Value $manifest
$manifestSha = Get-Sha256 -Path $manifestPath

$compile = Invoke-CapturedCommand -Path $compileCmdPath
$compileText = "STDOUT`r`n$($compile.stdout)`r`nSTDERR`r`n$($compile.stderr)`r`n"
Write-NewText -Path (Join-Path $evidencePath 'compile_stdout.txt') -Text $compile.stdout
Write-NewText -Path (Join-Path $evidencePath 'compile_stderr.txt') -Text $compile.stderr
Write-NewText -Path (Join-Path $evidencePath 'compile_console.txt') -Text $compileText

$warningRows = @(
    foreach ($match in [regex]::Matches($compileText, '%Warning-([A-Z0-9_]+):\s+([^\r\n]+)')) {
        [ordered]@{ category = $match.Groups[1].Value; detail = $match.Groups[2].Value.Trim() }
    }
)
$warningLimits = [ordered]@{ TIMESCALEMOD = 11; UNSIGNED = 1; WIDTHEXPAND = 36; WIDTHTRUNC = 16 }
$warningCounts = [ordered]@{ TIMESCALEMOD = 0; UNSIGNED = 0; WIDTHEXPAND = 0; WIDTHTRUNC = 0 }
$unknownWarnings = [ordered]@{}
foreach ($warning in $warningRows) {
    $category = [string]$warning.category
    if ($warningCounts.Contains($category)) {
        $warningCounts[$category] = [int]$warningCounts[$category] + 1
    } else {
        if (-not $unknownWarnings.Contains($category)) { $unknownWarnings[$category] = 0 }
        $unknownWarnings[$category] = [int]$unknownWarnings[$category] + 1
    }
}
$overLimitWarnings = @(
    foreach ($category in $warningLimits.Keys) {
        if ([int]$warningCounts[$category] -gt [int]$warningLimits[$category]) { $category }
    }
)
$warningGatePassed = ($unknownWarnings.Count -eq 0) -and ($overLimitWarnings.Count -eq 0)
$sourceRowsAfterCompile = Get-FileBinding -Paths $sourcePaths
$sourceUnchanged = (($sourceRowsBefore | ConvertTo-Json -Depth 10 -Compress) -ceq
                    ($sourceRowsAfterCompile | ConvertTo-Json -Depth 10 -Compress))
$gxxMatch = [regex]::Match($compileText, '(?m)^GXX_PROBE_EXIT=(\d+)\s*$')
$verilatorMatch = [regex]::Match($compileText, '(?m)^VERILATOR_EXIT_CODE=(\d+)\s*$')
$gxxExit = if ($gxxMatch.Success) { [int]$gxxMatch.Groups[1].Value } else { $null }
$verilatorExit = if ($verilatorMatch.Success) { [int]$verilatorMatch.Groups[1].Value } else { $null }
$simulatorPath = Join-Path $buildPath 'Vtb_s2a_weightcap_boundary.exe'
$simulatorSha = if (Test-Path -LiteralPath $simulatorPath -PathType Leaf) { Get-Sha256 -Path $simulatorPath } else { $null }
$compilePassed = ($compile.exit_code -eq 0) -and ($gxxExit -eq 0) -and ($verilatorExit -eq 0) -and
                 $warningGatePassed -and $sourceUnchanged -and ($null -ne $simulatorSha)
$compileRecord = [ordered]@{
    schema_version = 's2a_t66_weightcap_boundary_compile_v3'
    evidence_path = $evidencePath
    source_manifest_sha256 = $manifestSha
    candidate_dut_sha256 = $actualDutSha
    descriptor_package_sha256 = Get-Sha256 -Path $packagePath
    testbench_sha256 = Get-Sha256 -Path $benchPath
    runner_sha256 = Get-Sha256 -Path $PSCommandPath
    source_rows_before = $sourceRowsBefore
    source_rows_after_compile = $sourceRowsAfterCompile
    source_unchanged = [bool]$sourceUnchanged
    command = $compile.command
    wrapper_exit_code = [int]$compile.exit_code
    gxx_probe_exit_code = $gxxExit
    verilator_exit_code = $verilatorExit
    duration_seconds = [double]$compile.duration_seconds
    warning_rows = $warningRows
    warning_counts = $warningCounts
    warning_limits = $warningLimits
    unknown_warning_categories = @($unknownWarnings.Keys)
    over_limit_warning_categories = $overLimitWarnings
    warning_gate_passed = [bool]$warningGatePassed
    simulator_path = $simulatorPath
    simulator_sha256 = $simulatorSha
    simulator_started = $false
    passed = [bool]$compilePassed
}
$compileRecordPath = Join-Path $evidencePath 'compile_execution_record.json'
Write-NewJson -Path $compileRecordPath -Value $compileRecord
Write-NewJson -Path (Join-Path $evidencePath 'compile_status.json') -Value ([ordered]@{
    status = if ($compilePassed) { 'COMPILE_PASS_WAITING_SIMULATION' } else { 'COMPILE_FAILED_OR_WARNING_GATE_REJECTED' }
    simulator_started = $false
    compile_record_sha256 = Get-Sha256 -Path $compileRecordPath
})
if (-not $compilePassed) { exit $(if ($compile.exit_code -ne 0) { $compile.exit_code } else { 1 }) }

$busyAfterCompile = @(Get-ToolProcessSnapshot)
if ($busyAfterCompile.Count -gt 0) {
    throw "编译器返回后仍有 build 进程，未启动 simulator：$($busyAfterCompile | ConvertTo-Json -Compress)"
}

$simulation = Invoke-CapturedCommand -Path $simulateCmdPath
$simulationText = "STDOUT`r`n$($simulation.stdout)`r`nSTDERR`r`n$($simulation.stderr)`r`n"
Write-NewText -Path (Join-Path $evidencePath 'simulation_stdout.txt') -Text $simulation.stdout
Write-NewText -Path (Join-Path $evidencePath 'simulation_stderr.txt') -Text $simulation.stderr
Write-NewText -Path (Join-Path $evidencePath 'simulation_console.txt') -Text $simulationText
$simulatorExitMatch = [regex]::Match($simulationText, '(?m)^SIMULATOR_EXIT_CODE=(\d+)\s*$')
$simulatorExit = if ($simulatorExitMatch.Success) { [int]$simulatorExitMatch.Groups[1].Value } else { $null }
$k4608Match = [regex]::Match($simulationText,
    'K4608_PASS requests=(\d+) feature_reads=(\d+) weight_reads=(\d+) output_writes=(\d+) lane7_index4607_fetches=(\d+) final_ram_reads=(\d+) observed_package_last_byte=([0-9a-fA-F]+) responder_word=([0-9a-fA-F]+)')
$k4609Match = [regex]::Match($simulationText,
    'K4609_REJECT_PASS result_error_code=(\d+) prevalidation_memory_requests=(\d+) input_bytes=(\d+) quantized_weight_bytes=(\d+) package_length=(\d+)')
$boundaryMarker = $simulationText.Contains('PASS: K=4608 max reduction reads lane RAM index4607; K=4609 BAD_ARGUMENT before memory access')
$countsPassed = $k4608Match.Success -and
                ([int]$k4608Match.Groups[1].Value -eq 41480) -and
                ([int]$k4608Match.Groups[2].Value -eq 4608) -and
                ([int]$k4608Match.Groups[3].Value -eq 36864) -and
                ([int]$k4608Match.Groups[4].Value -eq 8) -and
                ([int]$k4608Match.Groups[5].Value -eq 1) -and
                ([int]$k4608Match.Groups[6].Value -eq 8) -and
                ($k4608Match.Groups[8].Value.ToLowerInvariant() -eq '01010101')
$k4609Passed = $k4609Match.Success -and
               ([int]$k4609Match.Groups[1].Value -eq 1) -and
               ([int]$k4609Match.Groups[2].Value -eq 0) -and
               ([int]$k4609Match.Groups[3].Value -eq 4609) -and
               ([int]$k4609Match.Groups[4].Value -eq 2359808) -and
               ([int]$k4609Match.Groups[5].Value -eq 2359808)
$simulationPassed = ($simulation.exit_code -eq 0) -and ($simulatorExit -eq 0) -and
                    $countsPassed -and $k4609Passed -and $boundaryMarker
$busyAfterSimulation = @(Get-ToolProcessSnapshot)
$simulationRecord = [ordered]@{
    schema_version = 's2a_t66_weightcap_boundary_simulation_v3'
    evidence_path = $evidencePath
    source_manifest_sha256 = $manifestSha
    candidate_dut_sha256 = $actualDutSha
    descriptor_package_sha256 = Get-Sha256 -Path $packagePath
    testbench_sha256 = Get-Sha256 -Path $benchPath
    runner_sha256 = Get-Sha256 -Path $PSCommandPath
    compile_record_sha256 = Get-Sha256 -Path $compileRecordPath
    executable_sha256 = Get-Sha256 -Path $simulatorPath
    command = $simulation.command
    wrapper_exit_code = [int]$simulation.exit_code
    simulator_exit_code = $simulatorExit
    duration_seconds = [double]$simulation.duration_seconds
    k4608_pass_marker = [bool]$k4608Match.Success
    k4608_memory_requests = if ($k4608Match.Success) { [int]$k4608Match.Groups[1].Value } else { $null }
    k4608_feature_read_requests = if ($k4608Match.Success) { [int]$k4608Match.Groups[2].Value } else { $null }
    k4608_weight_read_requests = if ($k4608Match.Success) { [int]$k4608Match.Groups[3].Value } else { $null }
    k4608_output_write_requests = if ($k4608Match.Success) { [int]$k4608Match.Groups[4].Value } else { $null }
    k4608_lane7_index4607_fetches = if ($k4608Match.Success) { [int]$k4608Match.Groups[5].Value } else { $null }
    k4608_last_ram_reads = if ($k4608Match.Success) { [int]$k4608Match.Groups[6].Value } else { $null }
    observed_package_last_byte = if ($k4608Match.Success) { $k4608Match.Groups[7].Value.ToLowerInvariant() } else { $null }
    synthetic_memory_responder_word = if ($k4608Match.Success) { $k4608Match.Groups[8].Value.ToLowerInvariant() } else { $null }
    k4609_reject_marker = [bool]$k4609Match.Success
    k4609_result_error_code = if ($k4609Match.Success) { [int]$k4609Match.Groups[1].Value } else { $null }
    k4609_new_memory_requests = if ($k4609Match.Success) { [int]$k4609Match.Groups[2].Value } else { $null }
    k4609_shapes_and_lengths_validated = [bool]$k4609Passed
    boundary_marker = [bool]$boundaryMarker
    count_gate_passed = [bool]$countsPassed
    no_orphan_tool_processes = ($busyAfterSimulation.Count -eq 0)
    remaining_tool_processes = $busyAfterSimulation
    simulator_started = $true
    passed = [bool]$simulationPassed -and ($busyAfterSimulation.Count -eq 0)
}
$simulationRecordPath = Join-Path $evidencePath 'simulation_execution_record.json'
Write-NewJson -Path $simulationRecordPath -Value $simulationRecord
Write-NewJson -Path (Join-Path $evidencePath 'simulation_status.json') -Value ([ordered]@{
    status = if ($simulationRecord.passed) { 'PASS_K4608_AND_REJECT_K4609' } else { 'SIMULATION_FAILED' }
    simulator_started = $true
    simulation_record_sha256 = Get-Sha256 -Path $simulationRecordPath
})
$summary = [ordered]@{
    schema_version = 's2a_t66_weightcap_boundary_attempt_summary_v1'
    status = if ($compilePassed -and $simulationRecord.passed) { 'PASS' } else { 'FAIL' }
    source_manifest_sha256 = $manifestSha
    compile_record_sha256 = Get-Sha256 -Path $compileRecordPath
    simulation_record_sha256 = Get-Sha256 -Path $simulationRecordPath
    candidate_dut_sha256 = $actualDutSha
    testbench_sha256 = Get-Sha256 -Path $benchPath
    runner_sha256 = Get-Sha256 -Path $PSCommandPath
    compile_exit_code = [int]$compile.exit_code
    simulator_exit_code = $simulatorExit
    passed = [bool]$compilePassed -and [bool]$simulationRecord.passed
}
Write-NewJson -Path (Join-Path $evidencePath 'attempt_summary.json') -Value $summary
if (-not $summary.passed) { exit $(if ($simulation.exit_code -ne 0) { $simulation.exit_code } else { 1 }) }
Write-Output "PASS_WEIGHTCAP_BOUNDARY evidence=$evidencePath manifest=$manifestSha compile_seconds=$($compile.duration_seconds) simulation_seconds=$($simulation.duration_seconds)"
