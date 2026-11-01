Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$evidenceRoot = 'D:\FPGA_Competition\report\evidence\S2A-T66\weightcap_boundary_4608_20261006_attempt02'
$runnerPath = 'D:\FPGA_Competition\verification\run_s2a_t66_candidate_blackbox.ps1'
$dutPath = 'D:\FPGA_Competition\src\s2a_conv_tile_engine.sv'
$candidateEvidencePath = 'D:\FPGA_Competition\report\evidence\S2A-T66\candidate_blackbox_weightcap4608_20261006'
$wrapperPath = Join-Path $evidenceRoot 'standard_t66_compile.cmd'
$shellPath = Join-Path $evidenceRoot 'standard_t66_compile.sh'
$cmdPath = 'C:\Windows\System32\cmd.exe'
$stdoutPath = Join-Path $evidenceRoot 'standard_t66_compile_stdout.txt'
$stderrPath = Join-Path $evidenceRoot 'standard_t66_compile_stderr.txt'
$consolePath = Join-Path $evidenceRoot 'standard_t66_compile_console.txt'
$recordPath = Join-Path $evidenceRoot 'standard_t66_compile_execution_record.json'
$encoding = [System.Text.UTF8Encoding]::new($false)

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Write-NewText([string]$Path, [string]$Text) {
    $bytes = $encoding.GetBytes($Text)
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try {
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush()
    }
    finally {
        $stream.Dispose()
    }
}

foreach ($path in @($evidenceRoot, (Split-Path -Parent $runnerPath), (Split-Path -Parent $dutPath))) {
    $item = Get-Item -LiteralPath $path -ErrorAction Stop
    if (-not $item.PSIsContainer -or $item.FullName -cne $path) {
        throw "目录路径校验失败：$path"
    }
}
foreach ($path in @($runnerPath, $dutPath, $wrapperPath, $shellPath, $cmdPath)) {
    $item = Get-Item -LiteralPath $path -ErrorAction Stop
    if ($item.PSIsContainer -or $item.FullName -cne $path) {
        throw "文件路径校验失败：$path"
    }
}
if (Test-Path -LiteralPath $candidateEvidencePath) {
    throw "标准 runner 证据目录已存在：$candidateEvidencePath"
}
foreach ($path in @($stdoutPath, $stderrPath, $consolePath, $recordPath)) {
    if (Test-Path -LiteralPath $path) {
        throw "拒绝覆盖启动证据：$path"
    }
}

$verilatorPath = 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin\verilator_bin.exe'
$activeProcesses = @(
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.ExecutablePath -ieq $verilatorPath -or
            $_.Name -in @('make.exe', 'g++.exe', 'Vtb_s2a_t66_candidate_blackbox.exe')
        }
)
if ($activeProcesses.Count -gt 0) {
    throw "发现已有编译或仿真进程，拒绝重复启动：$($activeProcesses | ConvertTo-Json -Compress)"
}

$processInfo = [System.Diagnostics.ProcessStartInfo]::new()
$processInfo.FileName = $cmdPath
$processInfo.ArgumentList.Add('/d')
$processInfo.ArgumentList.Add('/c')
$processInfo.ArgumentList.Add($wrapperPath)
$processInfo.WorkingDirectory = $evidenceRoot
$processInfo.UseShellExecute = $false
$processInfo.CreateNoWindow = $true
$processInfo.RedirectStandardOutput = $true
$processInfo.RedirectStandardError = $true
$process = [System.Diagnostics.Process]::new()
$process.StartInfo = $processInfo
$watch = [System.Diagnostics.Stopwatch]::StartNew()
if (-not $process.Start()) {
    throw '无法启动标准 T66 compile-only launcher。'
}
$stdoutTask = $process.StandardOutput.ReadToEndAsync()
$stderrTask = $process.StandardError.ReadToEndAsync()
$process.WaitForExit()
$stdout = $stdoutTask.GetAwaiter().GetResult()
$stderr = $stderrTask.GetAwaiter().GetResult()
$exitCode = [int]$process.ExitCode
$watch.Stop()
$process.Dispose()

Write-NewText $stdoutPath $stdout
Write-NewText $stderrPath $stderr
Write-NewText $consolePath ("STDOUT`r`n$stdout`r`nSTDERR`r`n$stderr`r`n")
$innerRecordPath = Join-Path $candidateEvidencePath 'compile_execution_record.json'
$innerStatusPath = Join-Path $candidateEvidencePath 'compile_status.json'
$record = [ordered]@{
    schema_version = 's2a_t66_standard_runner_launch_v1'
    runner_path = $runnerPath
    runner_sha256 = Get-Sha256 $runnerPath
    candidate_dut_sha256 = Get-Sha256 $dutPath
    launcher_cmd_sha256 = Get-Sha256 $wrapperPath
    launcher_shell_sha256 = Get-Sha256 $shellPath
    command = @($cmdPath, '/d', '/c', $wrapperPath)
    exit_code = $exitCode
    duration_seconds = [Math]::Round($watch.Elapsed.TotalSeconds, 3)
    stdout_path = $stdoutPath
    stderr_path = $stderrPath
    console_path = $consolePath
    runner_evidence_path = $candidateEvidencePath
    runner_compile_record_path = if (Test-Path -LiteralPath $innerRecordPath) { $innerRecordPath } else { $null }
    runner_compile_record_sha256 = if (Test-Path -LiteralPath $innerRecordPath) { Get-Sha256 $innerRecordPath } else { $null }
    runner_compile_status_path = if (Test-Path -LiteralPath $innerStatusPath) { $innerStatusPath } else { $null }
    simulator_started = $false
}
Write-NewText $recordPath (($record | ConvertTo-Json -Depth 12) + [Environment]::NewLine)
Write-Output "standard_t66_compile_exit_code=$exitCode duration_seconds=$($record.duration_seconds)"
exit $exitCode
