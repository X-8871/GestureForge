Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$rootPath = 'D:\FPGA_Competition'
$evidencePath = 'D:\FPGA_Competition\report\evidence\S2A-T66\weightcap_boundary_4608_20261006_attempt02\retry05'
$buildPath = Join-Path $evidencePath 'build'
$dutPath = Join-Path $rootPath 'src\s2a_conv_tile_engine.sv'
$packagePath = Join-Path $rootPath 'src\s2a_network_descriptor_pkg.sv'
$benchPath = Join-Path $evidencePath 'tb_s2a_weightcap_boundary.sv'
$compileWrapperPath = Join-Path $evidencePath 'compile.cmd'
$simulateWrapperPath = Join-Path $evidencePath 'simulate.cmd'
$cmdPath = 'C:\Windows\System32\cmd.exe'
$utf8 = [System.Text.UTF8Encoding]::new($false)

function Write-NewText([string]$Path, [string]$Text) {
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try { $bytes = $utf8.GetBytes($Text); $stream.Write($bytes, 0, $bytes.Length); $stream.Flush() } finally { $stream.Dispose() }
}
function Write-NewJson([string]$Path, [object]$Value) {
    Write-NewText $Path (($Value | ConvertTo-Json -Depth 12) + [Environment]::NewLine)
}
function Get-Sha([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Invoke-CapturedCommand([string]$Path) {
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
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    $watch = [System.Diagnostics.Stopwatch]::StartNew()
    if (-not $process.Start()) { throw "无法启动命令包装器：$Path" }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    $process.WaitForExit()
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    $exitCode = [int]$process.ExitCode
    $watch.Stop()
    $process.Dispose()
    return [pscustomobject]@{ command = @($cmdPath, '/d', '/c', $Path); exit_code = $exitCode; stdout = $stdout; stderr = $stderr; duration_seconds = [Math]::Round($watch.Elapsed.TotalSeconds, 3) }
}
function Assert-ExactFile([string]$Path) {
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($item.PSIsContainer -or $item.FullName -cne $Path -or ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) { throw "文件路径核验失败：$Path" }
}
function Assert-ExactDirectory([string]$Path) {
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if (-not $item.PSIsContainer -or $item.FullName -cne $Path -or ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) { throw "目录路径核验失败：$Path" }
}

Assert-ExactDirectory $rootPath
Assert-ExactDirectory (Join-Path $rootPath 'src')
Assert-ExactDirectory $evidencePath
foreach ($path in @($dutPath, $packagePath, $benchPath, $compileWrapperPath, $simulateWrapperPath, $cmdPath)) { Assert-ExactFile $path }
if (Test-Path -LiteralPath $buildPath) { throw "拒绝复用已有构建目录：$buildPath" }
$outputPaths = @('compile_stdout.txt','compile_stderr.txt','compile_console.txt','compile_execution_record.json','compile_status.json','simulation_stdout.txt','simulation_stderr.txt','simulation_console.txt','simulation_execution_record.json','simulation_status.json') | ForEach-Object { Join-Path $evidencePath $_ }
$existing = @($outputPaths | Where-Object { Test-Path -LiteralPath $_ })
if ($existing.Count -gt 0) { throw "拒绝覆盖已有证据：$($existing -join ', ')" }
[void][System.IO.Directory]::CreateDirectory($buildPath)
$sourcePaths = @($packagePath,$dutPath,$benchPath,$compileWrapperPath,$simulateWrapperPath)
$sourceRowsBefore = @(
    foreach ($path in $sourcePaths) {
        [ordered]@{ path = $path; bytes = [long](Get-Item -LiteralPath $path).Length; sha256 = Get-Sha $path }
    }
)

$compile = Invoke-CapturedCommand $compileWrapperPath
$compileText = "STDOUT`r`n$($compile.stdout)`r`nSTDERR`r`n$($compile.stderr)`r`n"
Write-NewText (Join-Path $evidencePath 'compile_stdout.txt') $compile.stdout
Write-NewText (Join-Path $evidencePath 'compile_stderr.txt') $compile.stderr
Write-NewText (Join-Path $evidencePath 'compile_console.txt') $compileText
$warningRows = @(
    foreach ($match in [regex]::Matches($compileText, '%Warning-([A-Z0-9_]+):\s+([^\r\n]+)')) {
        [ordered]@{ category = $match.Groups[1].Value; detail = $match.Groups[2].Value.Trim() }
    }
)
$warningLimits = [ordered]@{ TIMESCALEMOD = 11; UNSIGNED = 1; WIDTHEXPAND = 36; WIDTHTRUNC = 16 }
$warningCounts = [ordered]@{ TIMESCALEMOD = 0; UNSIGNED = 0; WIDTHEXPAND = 0; WIDTHTRUNC = 0 }
$unknownWarnings = @{}
foreach ($warning in $warningRows) {
    $category = $warning.category
    if ($warningCounts.Contains($category)) {
        $warningCounts[$category] = [int]$warningCounts[$category] + 1
    } else {
        $unknownWarnings[$category] = 1 + [int]$unknownWarnings[$category]
    }
}
$overLimitWarnings = @(
    foreach ($category in $warningLimits.Keys) {
        if ([int]$warningCounts[$category] -gt [int]$warningLimits[$category]) { $category }
    }
)
$warningGatePassed = ($unknownWarnings.Count -eq 0) -and ($overLimitWarnings.Count -eq 0)
$sourceRowsAfterCompile = @(
    foreach ($path in $sourcePaths) {
        [ordered]@{ path = $path; bytes = [long](Get-Item -LiteralPath $path).Length; sha256 = Get-Sha $path }
    }
)
$sourceUnchanged = (($sourceRowsBefore | ConvertTo-Json -Depth 8 -Compress) -ceq ($sourceRowsAfterCompile | ConvertTo-Json -Depth 8 -Compress))
$gxxProbeMatch = [regex]::Match($compileText, '(?m)^GXX_PROBE_EXIT=(\d+)\s*$')
$verilatorExitMatch = [regex]::Match($compileText, '(?m)^VERILATOR_EXIT_CODE=(\d+)\s*$')
$gxxProbeExit = if ($gxxProbeMatch.Success) { [int]$gxxProbeMatch.Groups[1].Value } else { $null }
$verilatorExit = if ($verilatorExitMatch.Success) { [int]$verilatorExitMatch.Groups[1].Value } else { $null }
$executablePath = Join-Path $buildPath 'Vtb_s2a_weightcap_boundary.exe'
$executableSha = if (Test-Path -LiteralPath $executablePath -PathType Leaf) { Get-Sha $executablePath } else { $null }
$compilePassed = ($compile.exit_code -eq 0) -and ($gxxProbeExit -eq 0) -and ($verilatorExit -eq 0) -and $warningGatePassed -and $sourceUnchanged -and $null -ne $executableSha
$compileRecord = [ordered]@{
    schema_version = 's2a_t66_weightcap_boundary_compile_v2'
    evidence_path = $evidencePath
    candidate_dut_sha256 = Get-Sha $dutPath
    descriptor_package_sha256 = Get-Sha $packagePath
    testbench_sha256 = Get-Sha $benchPath
    wrapper_sha256 = Get-Sha $compileWrapperPath
    driver_sha256 = Get-Sha $PSCommandPath
    source_rows_before = $sourceRowsBefore
    source_rows_after = $sourceRowsAfterCompile
    source_unchanged = [bool]$sourceUnchanged
    command = $compile.command
    wrapper_exit_code = [int]$compile.exit_code
    gxx_probe_exit_code = $gxxProbeExit
    verilator_exit_code = $verilatorExit
    duration_seconds = [double]$compile.duration_seconds
    warning_rows = $warningRows
    warning_counts = $warningCounts
    warning_limits = $warningLimits
    unknown_warning_categories = @($unknownWarnings.Keys)
    over_limit_warning_categories = $overLimitWarnings
    warning_gate_passed = [bool]$warningGatePassed
    executable_path = $executablePath
    executable_sha256 = $executableSha
    stdout_path = Join-Path $evidencePath 'compile_stdout.txt'
    stderr_path = Join-Path $evidencePath 'compile_stderr.txt'
    console_path = Join-Path $evidencePath 'compile_console.txt'
    simulator_started = $false
    passed = [bool]$compilePassed
}
Write-NewJson (Join-Path $evidencePath 'compile_execution_record.json') $compileRecord
Write-NewJson (Join-Path $evidencePath 'compile_status.json') ([ordered]@{ status = if ($compilePassed) { 'COMPILE_PASS_WAITING_SIMULATION' } else { 'COMPILE_FAILED_OR_WARNING_GATE_REJECTED' }; simulator_started = $false; compile_record_sha256 = Get-Sha (Join-Path $evidencePath 'compile_execution_record.json') })
if (-not $compilePassed) { exit $(if ($compile.exit_code -ne 0) { $compile.exit_code } else { 1 }) }
Assert-ExactFile $executablePath

$simulation = Invoke-CapturedCommand $simulateWrapperPath
$simulationText = "STDOUT`r`n$($simulation.stdout)`r`nSTDERR`r`n$($simulation.stderr)`r`n"
Write-NewText (Join-Path $evidencePath 'simulation_stdout.txt') $simulation.stdout
Write-NewText (Join-Path $evidencePath 'simulation_stderr.txt') $simulation.stderr
Write-NewText (Join-Path $evidencePath 'simulation_console.txt') $simulationText
$simExitMatch = [regex]::Match($simulationText, '(?m)^SIMULATOR_EXIT_CODE=(\d+)\s*$')
$simulatorExit = if ($simExitMatch.Success) { [int]$simExitMatch.Groups[1].Value } else { $null }
$markerK4608 = $simulation.stdout.Contains('K4608_PASS')
$markerK4609 = $simulation.stdout.Contains('K4609_REJECT_PASS')
$fullMarker = $simulation.stdout.Contains('PASS: exact K boundary 4608 reaches and reads/writes lane RAM index 4607; K=4609 is rejected before memory access')
$simulationPassed = ($simulation.exit_code -eq 0) -and ($simulatorExit -eq 0) -and $markerK4608 -and $markerK4609 -and $fullMarker
$simulationRecord = [ordered]@{
    schema_version = 's2a_t66_weightcap_boundary_simulation_v2'
    evidence_path = $evidencePath
    candidate_dut_sha256 = Get-Sha $dutPath
    testbench_sha256 = Get-Sha $benchPath
    compile_record_sha256 = Get-Sha (Join-Path $evidencePath 'compile_execution_record.json')
    executable_sha256 = Get-Sha $executablePath
    command = $simulation.command
    wrapper_exit_code = [int]$simulation.exit_code
    simulator_exit_code = $simulatorExit
    duration_seconds = [double]$simulation.duration_seconds
    k4608_pass_marker = [bool]$markerK4608
    k4609_reject_marker = [bool]$markerK4609
    full_boundary_marker = [bool]$fullMarker
    stdout_path = Join-Path $evidencePath 'simulation_stdout.txt'
    stderr_path = Join-Path $evidencePath 'simulation_stderr.txt'
    console_path = Join-Path $evidencePath 'simulation_console.txt'
    simulator_started = $true
    passed = [bool]$simulationPassed
}
Write-NewJson (Join-Path $evidencePath 'simulation_execution_record.json') $simulationRecord
Write-NewJson (Join-Path $evidencePath 'simulation_status.json') ([ordered]@{ status = if ($simulationPassed) { 'PASS_K4608_AND_REJECT_K4609' } else { 'SIMULATION_FAILED' }; simulator_started = $true; simulation_record_sha256 = Get-Sha (Join-Path $evidencePath 'simulation_execution_record.json') })
if (-not $simulationPassed) { exit $(if ($simulation.exit_code -ne 0) { $simulation.exit_code } else { 1 }) }
Write-Output "PASS_WEIGHTCAP_BOUNDARY evidence=$evidencePath compile_seconds=$($compile.duration_seconds) simulation_seconds=$($simulation.duration_seconds)"