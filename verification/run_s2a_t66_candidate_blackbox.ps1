[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, ParameterSetName = 'Compile')]
    [switch]$CompileOnly,
    [Parameter(Mandatory = $true, ParameterSetName = 'Run')]
    [switch]$RunSimulation,
    [Parameter(Mandatory = $true, ParameterSetName = 'Compile')]
    [Parameter(Mandatory = $true, ParameterSetName = 'Run')]
    [ValidatePattern('^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,78}[A-Za-z0-9_-])?$')]
    [string]$EvidenceDirectoryName,
    [Parameter(Mandatory = $true, ParameterSetName = 'Run')]
    [ValidatePattern('^[0-9a-fA-F]{64}$')]
    [string]$ApprovedCompileRecordSha256
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$script:EvidenceCreatedByInvocation = $false
$script:EvidenceMutex = $null
$script:EvidenceMutexName = $null
$script:EvidenceMutexOwned = $false
$script:FailureDirectoryCreatedByInvocation = $false
$script:FailureDirectoryPath = $null
$script:RunnerStage = 'parameter_validation'
$script:ActiveProcess = $null
$script:ActiveProcessId = $null
$script:ActiveExitCode = $null
$script:SimulatorStarted = $false
$script:ActiveStdoutTask = $null
$script:ActiveStderrTask = $null
$script:ActiveStdoutWriter = $null
$script:ActiveStderrWriter = $null
$script:ActiveOutputMode = $null
$script:ActiveStdoutPath = $null
$script:ActiveStderrPath = $null
$script:LastProgressUtcTicks = [DateTime]::UtcNow.Ticks
$script:CompileTimeoutMilliseconds = 1800000
$script:CleanupTimeoutMilliseconds = 10000
$script:DrainTimeoutMilliseconds = 10000
$script:CleanupDiagnostics = $null

function Initialize-BoundedProcessSupport {
    # 在无 PowerShell runspace 的线程执行系统调用，调用及退出等待共享截止时间。
    if (-not ('T66BoundedProcessStop' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Diagnostics;
using System.Threading.Tasks;
public static class T66BoundedProcessStop {
    public static bool CloseWriter(System.IO.StreamWriter writer, int milliseconds) {
        var task = Task.Run(() => writer.Dispose());
        if (!task.Wait(milliseconds)) return false;
        task.GetAwaiter().GetResult();
        return true;
    }
    public static bool Stop(Process process, int milliseconds) {
        var watch = Stopwatch.StartNew();
        var task = Task.Run(() => { if (!process.HasExited) process.Kill(true); });
        if (!task.Wait(milliseconds)) return false;
        task.GetAwaiter().GetResult();
        int remaining = Math.Max(0, milliseconds - (int)watch.ElapsedMilliseconds);
        return process.WaitForExit(remaining);
    }
}
'@
    }
}

function Stop-ProcessTreeBounded {
    param([Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
          [int]$BudgetMilliseconds = 10000)
    Initialize-BoundedProcessSupport
    if ($BudgetMilliseconds -le 0) { throw '终止预算必须为正。' }
    return [T66BoundedProcessStop]::Stop($Process, $BudgetMilliseconds)
}

function Assert-UniqueMarkerSet {
    param([string]$Text, [string]$Prefix, [string]$Field, [int[]]$Expected)
    # 所有以该 marker 开头的行均纳入检查，非法值及重复不能隐藏在计数之外。
    $rows = @($Text -split '\r?\n' | Where-Object { $_ -match ('^' + [regex]::Escape($Prefix) + '\b') })
    $observed = [System.Collections.Generic.HashSet[int]]::new()
    foreach ($row in $rows) {
        $pattern = '^' + [regex]::Escape($Prefix) + ' ' + [regex]::Escape($Field) + '=([0-9]+) '
        $match = [regex]::Match($row, $pattern)
        if (-not $match.Success) { throw "T66_MARKER_INVALID: $row" }
        $value = 0
        if (-not [int]::TryParse($match.Groups[1].Value, [ref]$value) -or $value -notin $Expected -or
            $match.Groups[1].Value -cne $value.ToString()) {
            throw "T66_MARKER_INVALID: $row"
        }
        if (-not $observed.Add($value)) { throw "T66_MARKER_DUPLICATE: $row" }
    }
    if ($observed.Count -ne $Expected.Count) { throw "T66_MARKER_MISSING: $Prefix" }
    return $rows.Count
}

function Save-FailureEvidence {
    param([string]$RecordPath, [string]$StatusPath, [object]$Record, [object]$Status)
    $result = [ordered]@{ record_saved = $false; status_saved = $false; errors = @() }
    try {
        Write-NewJson -Path $RecordPath -Value $Record
        $Status.failure_record_sha256 = Get-Sha256 -Path $RecordPath
        $result.record_saved = $true
    } catch { $result.errors += "record: $($_.Exception.Message)" }
    $Status.failure_record_saved = $result.record_saved
    try {
        Write-NewJson -Path $StatusPath -Value $Status
        $result.status_saved = $true
    } catch { $result.errors += "status: $($_.Exception.Message)" }
    [Console]::Error.WriteLine(('T66_FAILURE_PERSISTENCE: ' + ($result | ConvertTo-Json -Compress)))
    return [pscustomobject]$result
}

function Write-NewText {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text
    )
    $encoding = [System.Text.UTF8Encoding]::new($false)
    $bytes = $encoding.GetBytes($Text)
    $stream = [System.IO.File]::Open(
        $Path,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
    )
    try {
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush()
    }
    finally {
        $stream.Dispose()
    }
}

function Write-NewJson {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Value
    )
    Write-NewText -Path $Path -Text (($Value | ConvertTo-Json -Depth 16) + [Environment]::NewLine)
}

function New-CreateNewWriter {
    param([Parameter(Mandatory = $true)][string]$Path)
    $stream = [System.IO.File]::Open(
        $Path,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::Read
    )
    return [System.IO.StreamWriter]::new($stream, [System.Text.UTF8Encoding]::new($false))
}

function Stop-ActiveProcessAndCapture {
    $script:CleanupDiagnostics = [ordered]@{ process_exited = $null; output_complete = $true; errors = @() }
    if ($null -ne $script:ActiveProcess) {
        try {
            $script:CleanupDiagnostics.process_exited = Stop-ProcessTreeBounded -Process $script:ActiveProcess -BudgetMilliseconds $script:CleanupTimeoutMilliseconds
            if ($script:ActiveProcess.HasExited) { $script:ActiveExitCode = [int]$script:ActiveProcess.ExitCode }
        }
        catch { $script:CleanupDiagnostics.process_exited = $false; $script:CleanupDiagnostics.errors += $_.Exception.Message }
    }
    $drainWatch = [System.Diagnostics.Stopwatch]::StartNew()
    if ($script:ActiveOutputMode -eq 'read_all') {
        foreach ($taskName in @('ActiveStdoutTask', 'ActiveStderrTask')) {
            $task = Get-Variable -Name $taskName -Scope Script -ValueOnly -ErrorAction SilentlyContinue
            if ($null -eq $task) { continue }
            try {
                $remaining = [Math]::Max(0, $script:DrainTimeoutMilliseconds - [int]$drainWatch.ElapsedMilliseconds)
                if (-not $task.IsCompleted) { [void]$task.Wait($remaining) }
                if ($task.IsCompleted -and -not $task.IsFaulted) {
                    $text = $task.GetAwaiter().GetResult()
                    $pathVariable = if ($taskName -eq 'ActiveStdoutTask') { 'ActiveStdoutPath' } else { 'ActiveStderrPath' }
                    $path = Get-Variable -Name $pathVariable -Scope Script -ValueOnly
                    if ($path -and -not (Test-Path -LiteralPath $path)) { Write-NewText -Path $path -Text ([string]$text) }
                }
                else { $script:CleanupDiagnostics.output_complete = $false }
            }
            catch { $script:CleanupDiagnostics.output_complete = $false; $script:CleanupDiagnostics.errors += $_.Exception.Message }
        }
    }
    elseif ($script:ActiveOutputMode -eq 'lines' -and $null -ne $script:ActiveProcess) {
        while ($null -ne $script:ActiveStdoutTask -or $null -ne $script:ActiveStderrTask) {
            if ($drainWatch.ElapsedMilliseconds -ge $script:DrainTimeoutMilliseconds) {
                $script:CleanupDiagnostics.output_complete = $false
                break
            }
            $pending = @()
            if ($null -ne $script:ActiveStdoutTask) { $pending += $script:ActiveStdoutTask }
            if ($null -ne $script:ActiveStderrTask) { $pending += $script:ActiveStderrTask }
            if ($pending.Count -gt 0) {
                try { [void][System.Threading.Tasks.Task]::WaitAny([System.Threading.Tasks.Task[]]$pending, 250) }
                catch { $script:CleanupDiagnostics.output_complete = $false; $script:CleanupDiagnostics.errors += $_.Exception.Message; break }
            }
            foreach ($streamName in @('stdout', 'stderr')) {
                $taskName = if ($streamName -eq 'stdout') { 'ActiveStdoutTask' } else { 'ActiveStderrTask' }
                $readerName = if ($streamName -eq 'stdout') { 'StandardOutput' } else { 'StandardError' }
                $writerName = if ($streamName -eq 'stdout') { 'ActiveStdoutWriter' } else { 'ActiveStderrWriter' }
                $task = Get-Variable -Name $taskName -Scope Script -ValueOnly
                if ($null -eq $task -or -not $task.IsCompleted) { continue }
                try {
                    $line = $task.GetAwaiter().GetResult()
                    if ($null -eq $line) {
                        Set-Variable -Name $taskName -Scope Script -Value $null
                    } else {
                        $writer = Get-Variable -Name $writerName -Scope Script -ValueOnly
                        if ($null -ne $writer) { $writer.WriteLine([string]$line) }
                        $next = $script:ActiveProcess.$readerName.ReadLineAsync()
                        Set-Variable -Name $taskName -Scope Script -Value $next
                    }
                }
                catch {
                    $script:CleanupDiagnostics.output_complete = $false
                    $script:CleanupDiagnostics.errors += $_.Exception.Message
                    Set-Variable -Name $taskName -Scope Script -Value $null
                }
            }
        }
    }

    if ($null -ne $script:ActiveStdoutWriter) {
        Initialize-BoundedProcessSupport
        try {
            if (-not [T66BoundedProcessStop]::CloseWriter($script:ActiveStdoutWriter, $script:DrainTimeoutMilliseconds)) { throw 'stdout writer 收尾超时。' }
        } catch { $script:CleanupDiagnostics.output_complete = $false; $script:CleanupDiagnostics.errors += $_.Exception.Message }
        $script:ActiveStdoutWriter = $null
    }
    if ($null -ne $script:ActiveStderrWriter) {
        Initialize-BoundedProcessSupport
        try {
            if (-not [T66BoundedProcessStop]::CloseWriter($script:ActiveStderrWriter, $script:DrainTimeoutMilliseconds)) { throw 'stderr writer 收尾超时。' }
        } catch { $script:CleanupDiagnostics.output_complete = $false; $script:CleanupDiagnostics.errors += $_.Exception.Message }
        $script:ActiveStderrWriter = $null
    }
    [Console]::Error.WriteLine(('T66_CLEANUP: ' + ($script:CleanupDiagnostics | ConvertTo-Json -Compress)))
}

function Release-EvidenceMutex {
    if ($script:EvidenceMutexOwned -and $null -ne $script:EvidenceMutex) {
        try { $script:EvidenceMutex.ReleaseMutex() } catch {}
        $script:EvidenceMutexOwned = $false
    }
    if ($null -ne $script:EvidenceMutex) {
        try { $script:EvidenceMutex.Dispose() } catch {}
        $script:EvidenceMutex = $null
    }
}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
}

function Convert-ToMsysPath {
    param([Parameter(Mandatory = $true)][string]$WindowsPath)
    if ($WindowsPath -notmatch '^([A-Za-z]):\\(.*)$') {
        throw "T66_CANDIDATE_MSYS_PATH_INVALID: 不是驱动器绝对路径：$WindowsPath"
    }
    $drive = $Matches[1].ToLowerInvariant()
    $tail = $Matches[2].Replace('\', '/')
    return "/$drive/$tail"
}

function Convert-ToBashLiteral {
    param([Parameter(Mandatory = $true)][string]$Value)
    if ($Value.Contains('"')) { throw 'T66_CANDIDATE_BASH_LITERAL_UNSUPPORTED: 路径包含双引号。' }
    if ($Value.Contains("'")) { return '"' + $Value + '"' }
    return "'" + $Value + "'"
}

function Assert-ExactFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($item.PSIsContainer -or $item.FullName -cne $Path -or
        ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        throw "T66_CANDIDATE_PATH_INVALID: 文件类型、精确路径或重解析属性不符：$($item.FullName)"
    }
    return $item
}

function Assert-ExactDirectory {
    param([Parameter(Mandatory = $true)][string]$Path)
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if (-not $item.PSIsContainer -or $item.FullName -cne $Path -or
        ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        throw "T66_CANDIDATE_PATH_INVALID: 目录类型、精确路径或重解析属性不符：$($item.FullName)"
    }
    return $item
}

function Get-FileBinding {
    param([Parameter(Mandatory = $true)][string[]]$Paths)
    return @(
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

function Get-AllowedProcessSnapshot {
    param(
        [Parameter(Mandatory = $true)][object]$AllowedIdentities,
        [Parameter(Mandatory = $true)][string]$Phase
    )
    $snapshot = @(Get-T65XilinxProcessSnapshot)
    $guardResult = Assert-T65XilinxProcessIdentities `
        -ActualProcesses $snapshot `
        -AllowedIdentities @($AllowedIdentities.identities) `
        -Phase $Phase
    return [ordered]@{
        phase = $Phase
        guard = $guardResult
        processes = $snapshot
    }
}

function Invoke-CapturedChild {
    param(
        [Parameter(Mandatory = $true)][string]$FileName,
        [Parameter(Mandatory = $true)][string]$Arguments,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string]$StdoutPath,
        [Parameter(Mandatory = $true)][string]$StderrPath
    )
    foreach ($path in @($StdoutPath, $StderrPath)) {
        if (Test-Path -LiteralPath $path) { throw "T66_CANDIDATE_OUTPUT_EXISTS: 拒绝覆盖输出文件：$path" }
    }
    $info = [System.Diagnostics.ProcessStartInfo]::new()
    $info.FileName = $FileName
    $info.Arguments = $Arguments
    $info.WorkingDirectory = $WorkingDirectory
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $info.StandardOutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $info.StandardErrorEncoding = [System.Text.UTF8Encoding]::new($false)
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $info
    $watch = [System.Diagnostics.Stopwatch]::StartNew()
    $script:ActiveProcess = $process
    $script:ActiveProcessId = $null
    $script:ActiveExitCode = $null
    $script:ActiveStdoutPath = $StdoutPath
    $script:ActiveStderrPath = $StderrPath
    $script:ActiveOutputMode = 'read_all'
    $captureSucceeded = $false
    try {
        if (-not $process.Start()) { throw 'T66_CANDIDATE_CHILD_START_FAILED: Native child did not start.' }
        $script:ActiveProcessId = [int]$process.Id
        $script:ActiveStdoutTask = $process.StandardOutput.ReadToEndAsync()
        $script:ActiveStderrTask = $process.StandardError.ReadToEndAsync()
        while (-not $process.WaitForExit(1000)) {
            if ($watch.ElapsedMilliseconds -ge $script:CompileTimeoutMilliseconds) {
                throw 'T66_CANDIDATE_COMPILE_TIMEOUT: 编译子进程超过有限预算。'
            }
        }
        $drain = [System.Diagnostics.Stopwatch]::StartNew()
        foreach ($task in @($script:ActiveStdoutTask, $script:ActiveStderrTask)) {
            $remaining = [Math]::Max(0, $script:DrainTimeoutMilliseconds - [int]$drain.ElapsedMilliseconds)
            if (-not $task.Wait($remaining)) { throw 'T66_CANDIDATE_CAPTURE_TIMEOUT: 子进程已退出但输出未完整收尾。' }
        }
        $stdoutText = $script:ActiveStdoutTask.GetAwaiter().GetResult()
        $stderrText = $script:ActiveStderrTask.GetAwaiter().GetResult()
        $script:ActiveExitCode = [int]$process.ExitCode
        Write-NewText -Path $StdoutPath -Text ([string]$stdoutText)
        Write-NewText -Path $StderrPath -Text ([string]$stderrText)
        $captureSucceeded = $true
        $watch.Stop()
        return [pscustomobject]@{
            output = @(([string]$stdoutText + [Environment]::NewLine + [string]$stderrText) -split '\r?\n')
            stdout = [string]$stdoutText
            stderr = [string]$stderrText
            exit_code = [int]$process.ExitCode
            process_id = [int]$process.Id
            duration_seconds = [Math]::Round($watch.Elapsed.TotalSeconds, 3)
        }
    }
    catch {
        Stop-ActiveProcessAndCapture
        throw
    }
    finally {
        $watch.Stop()
        if ($captureSucceeded -and $null -ne $script:ActiveProcessId -and $null -ne $script:ActiveProcess -and $script:ActiveProcess.HasExited -and
            $null -ne $script:ActiveStdoutTask -and $null -ne $script:ActiveStderrTask -and
            $script:ActiveStdoutTask.IsCompleted -and $script:ActiveStderrTask.IsCompleted) {
            $script:ActiveExitCode = [int]$script:ActiveProcess.ExitCode
            $script:ActiveProcess = $null
            $script:ActiveStdoutTask = $null
            $script:ActiveStderrTask = $null
            $script:ActiveOutputMode = $null
        }
    }
}

$rootPath = 'D:\FPGA_Competition'
$evidenceParentPath = 'D:\FPGA_Competition\report\evidence\S2A-T66'
$evidencePath = Join-Path $evidenceParentPath $EvidenceDirectoryName
$fixturePath = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01\fixture'
$manifestPath = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01\fixture_manifest.json'
$inputFixture = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01\fixture\sample0_input_chw_int8.bin'
$weightFixture = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01\fixture\sample0_layer0_gf8_weights.bin'
$goldenFixture = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01\fixture\sample0_layer0_expected_nchw_int8.bin'
$descriptorPath = 'D:\FPGA_Competition\src\s2a_network_descriptor_pkg.sv'
$dutPath = 'D:\FPGA_Competition\src\s2a_conv_tile_engine.sv'
$benchPath = 'D:\FPGA_Competition\sim\tb_s2a_t66_candidate_blackbox.sv'
$runnerPath = 'D:\FPGA_Competition\verification\run_s2a_t66_candidate_blackbox.ps1'
$processGuardPath = 'D:\FPGA_Competition\verification\t65_xilinx_process_guard.ps1'
$processAllowlistPath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02\process_identity_allowlist.json'
$warningGateReferencePath = 'D:\FPGA_Competition\verification\run_s2a_backend_fault_recovery.ps1'
$verilatorPath = 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin\verilator_bin.exe'
$toolBinPath = 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin'
$makeBinPath = 'D:\FPGA_S2A_MSYS2_20261001\env\usr\bin'
$msysShellPath = 'D:\FPGA_S2A_MSYS2_20261001\env\msys2_shell.cmd'
$verilatorRootPath = 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\share\verilator'
$makePath = Join-Path $makeBinPath 'make.exe'
$compilerPath = Join-Path $toolBinPath 'g++.exe'
$unamePath = 'D:\FPGA_S2A_MSYS2_20261001\env\usr\bin\uname.exe'
$pythonPath = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$expectedCandidateSha256 = '76ca735b14802e26f0a4b016989e13b43cf8bd904587ccea37651c757d089300'
$expectedDescriptorSha256 = '295df973188878388ff8ef48c50dfacb1fe3d23a169369d737d1babe0507dc14'
$expectedFixtureManifestSha256 = '99477aa6e0dacda328151844545bd9268e707459313004ca3aaed22d9a324640'
$expectedInputSha256 = 'da26d3850d23d6f8cb466416799358e77fbeceaa8ee27696ebf7ab365248ab9e'
$expectedWeightSha256 = 'df49b5d3aeaebd6b4107b99d83ffa791d7a7e24bd7b26df0815c246e5717e633'
$expectedGoldenSha256 = '220499b6b8122c3264bef4d581967d51eedccc9e28813df3e0ff8f8716bc2ed8'
$expectedGuardSha256 = 'e9103032f4a61ece7e58fd8570c786cfb4ddc8be6e9029c8e7d595932a13dca9'
$expectedAllowlistSha256 = 'bc743da5ac3d3b2a2e493f3b1b23bf8cc0dfce3913e179062022806797aa090e'
$expectedWarningGateReferenceSha256 = '3fc902e0b74969e6735667dc90ad0e2d6da329a6189a3050fd69e7c3312b6432'
$expectedInputBytes = 519168
$expectedWeightBytes = 864
$expectedOutputBytes = 1384448
$compileRecordPath = Join-Path $evidencePath 'compile_execution_record.json'
$compileSnapshotPath = Join-Path $evidencePath 'compile_source_snapshot.json'
$compileConsolePath = Join-Path $evidencePath 'compile_console.txt'
$compileStdoutPath = Join-Path $evidencePath 'compile_stdout.txt'
$compileStderrPath = Join-Path $evidencePath 'compile_stderr.txt'
$compileWrapperPath = Join-Path $evidencePath 'compile.cmd'
$compileShellPath = Join-Path $evidencePath 'compile.sh'
$compileHomePath = Join-Path $evidencePath 'msys_home'
$compileTempPath = Join-Path $evidencePath 'msys_temp'
$buildPath = Join-Path $evidencePath 'build'
$simulatorPath = Join-Path $buildPath 'Vtb_s2a_t66_candidate_blackbox.exe'
$utf8 = [System.Text.UTF8Encoding]::new($false)

try {
    $script:RunnerStage = 'evidence_mutex_acquire'
    $mutexLeaf = $EvidenceDirectoryName.ToLowerInvariant()
    $script:EvidenceMutexName = 'Local\GestureForge_S2A_T66_' + $mutexLeaf
    $script:EvidenceMutex = [System.Threading.Mutex]::new($false, $script:EvidenceMutexName)
    $mutexAcquired = $false
    try {
        $mutexAcquired = $script:EvidenceMutex.WaitOne(0)
    }
    catch [System.Threading.AbandonedMutexException] {
        $mutexAcquired = $true
        $script:EvidenceMutexWasAbandoned = $true
    }
    if (-not $mutexAcquired) {
        $script:EvidenceMutex.Dispose()
        $script:EvidenceMutex = $null
        throw "T66_EVIDENCE_MUTEX_BUSY: 已有 invocation 持有 evidence 所有权：$evidencePath"
    }
    $script:EvidenceMutexOwned = $true

    $null = Assert-ExactDirectory -Path $rootPath
    $null = Assert-ExactDirectory -Path $evidenceParentPath
    $null = Assert-ExactDirectory -Path $fixturePath
    foreach ($path in @($descriptorPath, $dutPath, $benchPath, $runnerPath, $manifestPath,
                         $inputFixture, $weightFixture, $goldenFixture, $processGuardPath,
                         $processAllowlistPath, $warningGateReferencePath, $verilatorPath, $pythonPath,
                         $msysShellPath, $makePath, $compilerPath, $unamePath)) {
        $null = Assert-ExactFile -Path $path
    }

    if ((Get-Sha256 -Path $dutPath) -cne $expectedCandidateSha256) {
        throw 'T66_CANDIDATE_DUT_SHA_MISMATCH: 冻结 DUT 哈希变化。'
    }
    if ((Get-Sha256 -Path $descriptorPath) -cne $expectedDescriptorSha256) {
        throw 'T66_CANDIDATE_DESCRIPTOR_SHA_MISMATCH: descriptor package 哈希变化。'
    }
    if ((Get-Sha256 -Path $manifestPath) -cne $expectedFixtureManifestSha256) {
        throw 'T66_CANDIDATE_FIXTURE_MANIFEST_SHA_MISMATCH: 原始 fixture manifest 哈希变化。'
    }
    if ((Get-Sha256 -Path $processGuardPath) -cne $expectedGuardSha256 -or
        (Get-Sha256 -Path $processAllowlistPath) -cne $expectedAllowlistSha256) {
        throw 'T66_CANDIDATE_PROCESS_GUARD_SHA_MISMATCH: 冻结 T65 process guard 或 allowlist 哈希变化。'
    }
    if ((Get-Sha256 -Path $warningGateReferencePath) -cne $expectedWarningGateReferenceSha256) {
        throw 'T66_CANDIDATE_WARNING_GATE_REFERENCE_SHA_MISMATCH: T68 warning gate 参考 runner 哈希变化。'
    }

    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $fixtureRows = Get-FileBinding -Paths @($inputFixture, $weightFixture, $goldenFixture)
    $expectedFixtureHashes = @($expectedInputSha256, $expectedWeightSha256, $expectedGoldenSha256)
    $expectedFixtureLengths = @($expectedInputBytes, $expectedWeightBytes, $expectedOutputBytes)
    for ($index = 0; $index -lt $fixtureRows.Count; $index++) {
        if ($fixtureRows[$index].sha256 -cne $expectedFixtureHashes[$index] -or
            [long]$fixtureRows[$index].bytes -ne [long]$expectedFixtureLengths[$index]) {
            throw "T66_CANDIDATE_FIXTURE_MISMATCH: 原始 fixture 字节数或哈希不符：$($fixtureRows[$index].path)"
        }
    }
    if ($manifest.sample.input_fixture_path -cne $inputFixture -or
        $manifest.weights.fixture_path -cne $weightFixture -or
        $manifest.golden.fixture_path -cne $goldenFixture -or
        $manifest.sample.input_fixture_sha256 -cne $expectedInputSha256 -or
        $manifest.weights.fixture_sha256 -cne $expectedWeightSha256 -or
        $manifest.golden.fixture_sha256 -cne $expectedGoldenSha256 -or
        [long]$manifest.golden.tensor_byte_length -ne $expectedOutputBytes -or
        (($manifest.golden.shape_nchw -join ',') -cne '1,32,208,208')) {
        throw 'T66_CANDIDATE_FIXTURE_MANIFEST_BINDING_MISMATCH: manifest 与原始 fixture/完整输出范围不匹配。'
    }

    . $processGuardPath
    $allowedProcesses = Read-T65XilinxProcessAllowlist `
        -Path $processAllowlistPath `
        -ExpectedSha256 $expectedAllowlistSha256

    $toolchain = @($toolBinPath, $makeBinPath, $verilatorRootPath)
    foreach ($directory in $toolchain) {
        $null = Assert-ExactDirectory -Path $directory
    }
    foreach ($file in @($makePath, $compilerPath, $unamePath)) { $null = Assert-ExactFile -Path $file }

    $sourcePaths = @($descriptorPath, $dutPath, $benchPath)
    $sourceRows = Get-FileBinding -Paths $sourcePaths
    $baseBindingPaths = @($runnerPath, $warningGateReferencePath, $pythonPath,
        $processGuardPath, $processAllowlistPath, $manifestPath, $inputFixture, $weightFixture, $goldenFixture)
    $toolchainBindingPaths = @($msysShellPath, $verilatorPath, $makePath, $compilerPath, $unamePath)
    $pythonUnixPath = Convert-ToMsysPath -WindowsPath $pythonPath
    $verilatorUnixPath = Convert-ToMsysPath -WindowsPath $verilatorPath
    $verilatorRootUnixPath = Convert-ToMsysPath -WindowsPath $verilatorRootPath
    $evidenceUnixPath = Convert-ToMsysPath -WindowsPath $evidencePath
    $buildUnixPath = Convert-ToMsysPath -WindowsPath $buildPath
    $pythonMakeFlag = "PYTHON3='/c/Users/22061/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'"
    $compileArguments = @(
        '--binary', '--timing', '-Wno-fatal', '-j', '1', '--threads', '1',
        '--top-module', 'tb_s2a_t66_candidate_blackbox', '--Mdir', $buildPath,
        '-MAKEFLAGS', $pythonMakeFlag, '-CFLAGS', '-D_GLIBCXX_USE_CXX11_ABI=0'
    ) + $sourcePaths
    $compileCommand = @($msysShellPath, '-mingw64', '-defterm', '-no-start', '-use-full-path', '-c',
        "bash $(Convert-ToMsysPath -WindowsPath $compileShellPath)")

    if ($CompileOnly) {
        if (Test-Path -LiteralPath $evidencePath) {
            throw "T66_CANDIDATE_EVIDENCE_EXISTS: 拒绝覆盖现有证据目录：$evidencePath"
        }
        $null = [System.IO.Directory]::CreateDirectory($evidencePath)
        $null = Assert-ExactDirectory -Path $evidencePath
        $script:EvidenceCreatedByInvocation = $true
        $script:FailureDirectoryCreatedByInvocation = $true
        $script:FailureDirectoryPath = $evidencePath
        $script:RunnerStage = 'compile_prepare'
        $null = [System.IO.Directory]::CreateDirectory($compileHomePath)
        $null = [System.IO.Directory]::CreateDirectory($compileTempPath)
        $null = [System.IO.Directory]::CreateDirectory($buildPath)
        $null = Assert-ExactDirectory -Path $buildPath

        $compileSourceUnixPaths = @($sourcePaths | ForEach-Object { Convert-ToMsysPath -WindowsPath $_ })
        $compileArgsUnix = @(
            '--binary', '--timing', '-Wno-fatal', '-j', '1', '--threads', '1',
            '--top-module', 'tb_s2a_t66_candidate_blackbox', '--Mdir', $buildUnixPath,
            '-MAKEFLAGS', $pythonMakeFlag, '-CFLAGS', '-D_GLIBCXX_USE_CXX11_ABI=0'
        ) + $compileSourceUnixPaths
        $compileArgLiterals = @($compileArgsUnix | ForEach-Object { Convert-ToBashLiteral -Value $_ })
        $verilatorInvocationLine = '"$verilator_path" ' + ($compileArgLiterals -join ' ')
        $compileShellText = @(
            '#!/usr/bin/env bash',
            'set -euo pipefail',
            'export HOME="$(cygpath -u "$HOME")"',
            'export TMP="$(cygpath -w "$TMPDIR")"',
            'export TEMP="$TMP"',
            'export TMPDIR="$(cygpath -u "$TMPDIR")"',
            "export VERILATOR_ROOT=$(Convert-ToBashLiteral -Value $verilatorRootUnixPath)",
            "python_path=$(Convert-ToBashLiteral -Value $pythonUnixPath)",
            "verilator_path=$(Convert-ToBashLiteral -Value $verilatorUnixPath)",
            'printf "T66_ENV_MSYSTEM=%s\n" "$MSYSTEM"',
            'printf "T66_ENV_MINGW_PREFIX=%s\n" "$MINGW_PREFIX"',
            'printf "T66_ENV_HOME=%s\nT66_ENV_TMP=%s\nT66_ENV_TEMP=%s\nT66_ENV_TMPDIR=%s\n" "$HOME" "$TMP" "$TEMP" "$TMPDIR"',
            'printf "T66_ENV_RESOLVED_UNAME=%s\nT66_ENV_RESOLVED_GXX=%s\nT66_ENV_RESOLVED_MAKE=%s\nT66_ENV_RESOLVED_PYTHON=%s\nT66_ENV_RESOLVED_VERILATOR=%s\n" "$(command -v uname)" "$(command -v g++)" "$(command -v make)" "$python_path" "$verilator_path"',
            'uname -a',
            'g++ --version',
            'make --version',
            '"$python_path" --version',
            '"$verilator_path" --version',
            'set +e',
            $verilatorInvocationLine,
            'verilator_exit=$?',
            'set -e',
            'printf "VERILATOR_EXIT_CODE=%s\\n" "$verilator_exit"',
            'exit "$verilator_exit"'
        ) -join [Environment]::NewLine
        Write-NewText -Path $compileShellPath -Text ($compileShellText + [Environment]::NewLine)
        $shellUnixScript = Convert-ToMsysPath -WindowsPath $compileShellPath
        $compileWrapperText = @(
            '@echo off',
            'setlocal',
            ('set "HOME=' + $compileHomePath + '"'),
            ('set "TMP=' + $compileTempPath + '"'),
            ('set "TEMP=' + $compileTempPath + '"'),
            ('set "TMPDIR=' + $compileTempPath + '"'),
            ('set "PATH=' + $makeBinPath + ';' + $toolBinPath + ';%PATH%"'),
            'set "SHELL="',
            ('call "' + $msysShellPath + '" -mingw64 -defterm -no-start -use-full-path -c "bash ' + $shellUnixScript + '"'),
            'exit /b %ERRORLEVEL%'
        ) -join "`r`n"
        Write-NewText -Path $compileWrapperPath -Text ($compileWrapperText + "`r`n")
        $bindingPaths = $baseBindingPaths + @($compileWrapperPath, $compileShellPath) + $toolchainBindingPaths
        $bindingRows = Get-FileBinding -Paths $bindingPaths
        $runnerSha = Get-Sha256 -Path $runnerPath

        $script:RunnerStage = 'compile_prelaunch_guard'
        $preCompileGuard = Get-AllowedProcessSnapshot -AllowedIdentities $allowedProcesses -Phase 'candidate_compile_before'
        Write-NewJson -Path (Join-Path $evidencePath 'compile_prelaunch_process_snapshot.json') -Value $preCompileGuard
        $script:RunnerStage = 'compile_running'
        $compileWatch = [System.Diagnostics.Stopwatch]::StartNew()
        $cmdArguments = '/d /s /c ""' + $compileWrapperPath + '""'
        $compileResult = Invoke-CapturedChild -FileName $env:ComSpec -Arguments $cmdArguments `
            -WorkingDirectory $evidencePath -StdoutPath $compileStdoutPath -StderrPath $compileStderrPath
        $compileWatch.Stop()
        $compileConsoleText = "[STDOUT]`r`n$($compileResult.stdout)`r`n[STDERR]`r`n$($compileResult.stderr)"
        Write-NewText -Path $compileConsolePath -Text ($compileConsoleText + [Environment]::NewLine)
        $sourceRowsAfter = Get-FileBinding -Paths $sourcePaths
        $bindingRowsAfter = Get-FileBinding -Paths $bindingPaths
        $sourceUnchanged = (($sourceRows | ConvertTo-Json -Depth 8 -Compress) -ceq
            ($sourceRowsAfter | ConvertTo-Json -Depth 8 -Compress))
        $bindingUnchanged = (($bindingRows | ConvertTo-Json -Depth 8 -Compress) -ceq
            ($bindingRowsAfter | ConvertTo-Json -Depth 8 -Compress))

        $warningLimits = [ordered]@{ TIMESCALEMOD = 11; UNSIGNED = 1; WIDTHEXPAND = 36; WIDTHTRUNC = 16 }
        $warningCounts = [ordered]@{ TIMESCALEMOD = 0; UNSIGNED = 0; WIDTHEXPAND = 0; WIDTHTRUNC = 0 }
        $unknownWarnings = @{}
        foreach ($line in $compileResult.output) {
            if ([string]$line -match '%Warning-([A-Z0-9_]+):') {
                $category = $Matches[1]
                if ($warningCounts.Contains($category)) {
                    $warningCounts[$category] = [int]$warningCounts[$category] + 1
                } else {
                    $unknownWarnings[$category] = 1 + [int]$unknownWarnings[$category]
                }
            }
        }
        $overLimitWarnings = @(
            foreach ($category in $warningLimits.Keys) {
                if ([int]$warningCounts[$category] -gt [int]$warningLimits[$category]) { $category }
            }
        )
        $warningGatePassed = ($unknownWarnings.Count -eq 0) -and ($overLimitWarnings.Count -eq 0)
        $compileText = $compileResult.output -join [Environment]::NewLine
        $compileErrors = $compileText.Contains('%Error:')
        $postCompileGuard = Get-AllowedProcessSnapshot -AllowedIdentities $allowedProcesses -Phase 'candidate_compile_after'
        Write-NewJson -Path (Join-Path $evidencePath 'compile_postlaunch_process_snapshot.json') -Value $postCompileGuard
        $compileExeSha = $null
        if (Test-Path -LiteralPath $simulatorPath -PathType Leaf) { $compileExeSha = Get-Sha256 -Path $simulatorPath }
        $environmentLines = @($compileResult.output | Where-Object { [string]$_ -match '^(T66_ENV_|Linux |MINGW|VERILATOR v|Python |GNU Make|g\+\+|VERILATOR_EXIT_CODE=)' })
        $snapshot = [ordered]@{
            schema_version = 'gestureforge_s2a_t66_candidate_blackbox_compile_snapshot_v1'
            task_id = 'S2A-T66-CANDIDATE-BLACKBOX'
            top_module = 'tb_s2a_t66_candidate_blackbox'
            candidate_dut_sha256 = $expectedCandidateSha256
            evidence_mutex_name = $script:EvidenceMutexName
            fixture_manifest_sha256 = $expectedFixtureManifestSha256
            fixture_rows = $fixtureRows
            source_rows = $sourceRows
            supporting_binding_rows = $bindingRows
            toolchain_binding_rows = Get-FileBinding -Paths $toolchainBindingPaths
            warning_gate = [ordered]@{
                reference_runner = $warningGateReferencePath
                reference_runner_sha256 = $expectedWarningGateReferenceSha256
                limits = [ordered]@{ TIMESCALEMOD = 11; UNSIGNED = 1; WIDTHEXPAND = 36; WIDTHTRUNC = 16 }
                unknown_categories_allowed = $false
            }
            process_guard = [ordered]@{
                module_path = $processGuardPath
                module_sha256 = $expectedGuardSha256
                allowlist_path = $processAllowlistPath
                allowlist_sha256 = $expectedAllowlistSha256
            }
            msys2_shell_path = $msysShellPath
            msys2_shell_arguments = @('-mingw64', '-defterm', '-no-start', '-use-full-path')
            msys2_environment_capture = $environmentLines
            verilator_path = $verilatorPath
            verilator_root = $verilatorRootPath
            python_path = $pythonPath
            python_make_flag = $pythonMakeFlag
            python_sha256 = Get-Sha256 -Path $pythonPath
            make_path = $makePath
            compiler_path = $compilerPath
            uname_path = $unamePath
            home_path = $compileHomePath
            temp_path = $compileTempPath
            command = $compileCommand
            verilator_arguments = $compileArguments
            runner_sha256 = $runnerSha
            executable_path = $simulatorPath
            executable_sha256 = $compileExeSha
            simulator_started = $false
        }
        Write-NewJson -Path $compileSnapshotPath -Value $snapshot
        $compileSnapshotSha = Get-Sha256 -Path $compileSnapshotPath
        $compileRecord = [ordered]@{
            schema_version = 'gestureforge_s2a_t66_candidate_blackbox_compile_record_v1'
            task_id = 'S2A-T66-CANDIDATE-BLACKBOX'
            candidate_dut_sha256 = $expectedCandidateSha256
            evidence_mutex_name = $script:EvidenceMutexName
            fixture_manifest_sha256 = $expectedFixtureManifestSha256
            testbench_sha256 = Get-Sha256 -Path $benchPath
            compile_snapshot_sha256 = $compileSnapshotSha
            fixture_rows = $fixtureRows
            source_rows = $sourceRows
            supporting_binding_rows = $bindingRows
            toolchain_binding_rows = Get-FileBinding -Paths $toolchainBindingPaths
            command = $compileCommand
            exit_code = [int]$compileResult.exit_code
            process_id = $compileResult.process_id
            warning_counts = $warningCounts
            warning_limits = $warningLimits
            unknown_warning_categories = @($unknownWarnings.Keys)
            over_limit_warning_categories = $overLimitWarnings
            warning_gate_passed = [bool]$warningGatePassed
            errors_detected = [bool]$compileErrors
            source_unchanged = [bool]$sourceUnchanged
            supporting_bindings_unchanged = [bool]$bindingUnchanged
            toolchain_environment_capture = $environmentLines
            msys2_wrapper_path = $compileWrapperPath
            msys2_shell_script_path = $compileShellPath
            stdout_path = $compileStdoutPath
            stderr_path = $compileStderrPath
            sources_after = $sourceRowsAfter
            bindings_after = $bindingRowsAfter
            executable_path = $simulatorPath
            executable_sha256 = $compileExeSha
            duration_seconds = [Math]::Round($compileResult.duration_seconds, 3)
            console_path = $compileConsolePath
            process_guard_passed_before_and_after = $true
            simulator_started = $false
            next_status = 'COMPILED_WAITING_PARENT_REVIEW'
        }
        Write-NewJson -Path $compileRecordPath -Value $compileRecord
        $compileRecordSha = Get-Sha256 -Path $compileRecordPath
        $status = [ordered]@{
            schema_version = 'gestureforge_s2a_t66_candidate_blackbox_compile_status_v1'
            status = if ($compileResult.exit_code -eq 0 -and $warningGatePassed -and -not $compileErrors -and
                         $sourceUnchanged -and $bindingUnchanged -and $null -ne $compileExeSha) {
                'COMPILED_WAITING_PARENT_REVIEW'
            } else { 'COMPILE_FAILED_OR_WARNING_GATE_REJECTED' }
            compile_record_sha256 = $compileRecordSha
            candidate_dut_sha256 = $expectedCandidateSha256
            warning_gate_passed = [bool]$warningGatePassed
            simulator_started = $false
        }
        Write-NewJson -Path (Join-Path $evidencePath 'compile_status.json') -Value $status
        if ($status.status -cne 'COMPILED_WAITING_PARENT_REVIEW') {
            $script:ActiveExitCode = if ($compileResult.exit_code -ne 0) { $compileResult.exit_code } else { 1 }
            throw 'T66_CANDIDATE_COMPILE_GATE_FAILED: 编译退出码或 warning gate 未通过。'
        }
        Write-Output "COMPILED_WAITING_PARENT_REVIEW evidence=$evidencePath compile_record_sha256=$compileRecordSha warnings=$($warningCounts | ConvertTo-Json -Compress)"
        Release-EvidenceMutex
        return
    }

    $script:RunnerStage = 'run_prepare'
    $null = Assert-ExactDirectory -Path $evidencePath
    $null = Assert-ExactDirectory -Path $buildPath
    $null = Assert-ExactFile -Path $compileRecordPath
    $null = Assert-ExactFile -Path $compileSnapshotPath
    $simulationPath = Join-Path $evidencePath 'simulation'
    if (Test-Path -LiteralPath $simulationPath) {
        throw "T66_CANDIDATE_SIMULATION_OUTPUT_EXISTS: 拒绝覆盖既有仿真证据目录：$simulationPath"
    }
    $null = [System.IO.Directory]::CreateDirectory($simulationPath)
    $null = Assert-ExactDirectory -Path $simulationPath
    $script:FailureDirectoryCreatedByInvocation = $true
    $script:FailureDirectoryPath = $simulationPath
    $simulationPrelaunchGuardPath = Join-Path $simulationPath 'simulation_prelaunch_process_snapshot.json'
    $simulationStdoutPath = Join-Path $simulationPath 'simulation_stdout.txt'
    $simulationStderrPath = Join-Path $simulationPath 'simulation_stderr.txt'
    $simulationRecordPath = Join-Path $simulationPath 'simulation_execution_record.json'
    $simulationStatusPath = Join-Path $simulationPath 'simulation_status.json'
    $simulationGuardSamplesPath = Join-Path $simulationPath 'simulation_process_guard_samples.json'
    if ((Get-Sha256 -Path $compileRecordPath) -cne $ApprovedCompileRecordSha256.ToLowerInvariant()) {
        throw 'T66_CANDIDATE_APPROVAL_SHA_MISMATCH: compile record 与 parent 批准哈希不一致。'
    }
    $compileRecord = Get-Content -LiteralPath $compileRecordPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $snapshot = Get-Content -LiteralPath $compileSnapshotPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $currentSnapshotSha = Get-Sha256 -Path $compileSnapshotPath
    if ($compileRecord.compile_snapshot_sha256 -cne $currentSnapshotSha) {
        throw 'T66_CANDIDATE_SNAPSHOT_SHA_MISMATCH: compile record 未固定当前 source snapshot 的 SHA-256。'
    }
    if ($compileRecord.candidate_dut_sha256 -cne $expectedCandidateSha256) {
        throw 'T66_CANDIDATE_COMPILE_DUT_SHA_MISMATCH: compile record 未绑定当前候选。'
    }
    if ($compileRecord.exit_code -ne 0 -or -not $compileRecord.warning_gate_passed -or
        $compileRecord.errors_detected -or -not $compileRecord.source_unchanged -or
        -not $compileRecord.supporting_bindings_unchanged -or -not $compileRecord.executable_sha256) {
        throw 'T66_CANDIDATE_COMPILE_GATE_FAILED: 编译、warning gate、绑定或可执行程序不满足运行条件。'
    }
    if ($snapshot.candidate_dut_sha256 -cne $expectedCandidateSha256 -or
        $snapshot.runner_sha256 -cne (Get-Sha256 -Path $runnerPath) -or
        $snapshot.warning_gate.reference_runner_sha256 -cne $expectedWarningGateReferenceSha256) {
        throw 'T66_CANDIDATE_SNAPSHOT_BINDING_MISMATCH: frozen compile snapshot 绑定变化。'
    }
    foreach ($field in @('fixture_rows', 'source_rows', 'supporting_binding_rows', 'toolchain_binding_rows')) {
        if (($compileRecord.$field | ConvertTo-Json -Depth 10 -Compress) -cne
            ($snapshot.$field | ConvertTo-Json -Depth 10 -Compress)) {
            throw "T66_CANDIDATE_SNAPSHOT_RECORD_MISMATCH: compile record 与 source snapshot 的 $field 不一致。"
        }
    }
    if (($compileRecord.sources_after | ConvertTo-Json -Depth 10 -Compress) -cne
        ($snapshot.source_rows | ConvertTo-Json -Depth 10 -Compress) -or
        ($compileRecord.bindings_after | ConvertTo-Json -Depth 10 -Compress) -cne
        ($snapshot.supporting_binding_rows | ConvertTo-Json -Depth 10 -Compress)) {
        throw 'T66_CANDIDATE_POSTCOMPILE_ROW_MISMATCH: compile record 的编译后行与 snapshot 不一致。'
    }
    if ($compileRecord.testbench_sha256 -cne $snapshot.source_rows[2].sha256 -or
        $compileRecord.candidate_dut_sha256 -cne $snapshot.source_rows[1].sha256 -or
        $compileRecord.executable_sha256 -cne $snapshot.executable_sha256 -or
        $compileRecord.executable_path -cne $snapshot.executable_path) {
        throw 'T66_CANDIDATE_SNAPSHOT_SUMMARY_MISMATCH: DUT/TB/executable 摘要与 snapshot 不一致。'
    }
    $currentSources = Get-FileBinding -Paths @($descriptorPath, $dutPath, $benchPath)
    $currentBindings = Get-FileBinding -Paths ($baseBindingPaths + @($compileWrapperPath, $compileShellPath) + $toolchainBindingPaths)
    $currentToolchainBindings = Get-FileBinding -Paths $toolchainBindingPaths
    if (($currentSources | ConvertTo-Json -Depth 8 -Compress) -cne
        ($snapshot.source_rows | ConvertTo-Json -Depth 8 -Compress) -or
        ($currentSources | ConvertTo-Json -Depth 8 -Compress) -cne
        ($compileRecord.source_rows | ConvertTo-Json -Depth 8 -Compress) -or
        ($currentBindings | ConvertTo-Json -Depth 8 -Compress) -cne
        ($snapshot.supporting_binding_rows | ConvertTo-Json -Depth 8 -Compress) -or
        ($currentBindings | ConvertTo-Json -Depth 8 -Compress) -cne
        ($compileRecord.supporting_binding_rows | ConvertTo-Json -Depth 8 -Compress) -or
        ($currentToolchainBindings | ConvertTo-Json -Depth 8 -Compress) -cne
        ($snapshot.toolchain_binding_rows | ConvertTo-Json -Depth 8 -Compress) -or
        ($currentToolchainBindings | ConvertTo-Json -Depth 8 -Compress) -cne
        ($compileRecord.toolchain_binding_rows | ConvertTo-Json -Depth 8 -Compress) -or
        ($fixtureRows | ConvertTo-Json -Depth 8 -Compress) -cne
        ($snapshot.fixture_rows | ConvertTo-Json -Depth 8 -Compress) -or
        ($fixtureRows | ConvertTo-Json -Depth 8 -Compress) -cne
        ($compileRecord.fixture_rows | ConvertTo-Json -Depth 8 -Compress)) {
        throw 'T66_CANDIDATE_SOURCE_OR_FIXTURE_CHANGED: compile 后候选源码、guard 或 fixture 已变化。'
    }
    $null = Assert-ExactFile -Path $simulatorPath
    if ((Get-Sha256 -Path $simulatorPath) -cne $compileRecord.executable_sha256) {
        throw 'T66_CANDIDATE_EXECUTABLE_SHA_MISMATCH: 仿真程序在 compile 后发生变化。'
    }

    $script:RunnerStage = 'simulation_prelaunch_guard'
    $preRunGuard = Get-AllowedProcessSnapshot -AllowedIdentities $allowedProcesses -Phase 'candidate_run_before'
    Write-NewJson -Path $simulationPrelaunchGuardPath -Value $preRunGuard
    $simulationArguments = @(
        "+T66_INPUT_PATH=$inputFixture",
        "+T66_WEIGHT_PATH=$weightFixture",
        "+T66_GOLDEN_PATH=$goldenFixture"
    )
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $simulatorPath
    $startInfo.Arguments = $simulationArguments -join ' '
    $startInfo.WorkingDirectory = $buildPath
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.EnvironmentVariables['PATH'] = "$toolBinPath;$makeBinPath;$env:PATH"
    $startInfo.EnvironmentVariables['VERILATOR_ROOT'] = $verilatorRootPath
    $startInfo.StandardOutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $startInfo.StandardErrorEncoding = [System.Text.UTF8Encoding]::new($false)
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    $stdoutPath = $simulationStdoutPath
    $stderrPath = $simulationStderrPath
    $stdoutWriter = New-CreateNewWriter -Path $stdoutPath
    $stderrWriter = New-CreateNewWriter -Path $stderrPath
    $stdoutWriter.AutoFlush = $true
    $stderrWriter.AutoFlush = $true
    $script:ActiveProcess = $process
    $script:ActiveProcessId = $null
    $script:ActiveExitCode = $null
    $script:SimulatorStarted = $false
    $script:ActiveStdoutWriter = $stdoutWriter
    $script:ActiveStderrWriter = $stderrWriter
    $script:ActiveStdoutPath = $stdoutPath
    $script:ActiveStderrPath = $stderrPath
    $script:ActiveOutputMode = 'lines'
    $script:RunnerStage = 'simulation_start'
    $simulationWatch = [System.Diagnostics.Stopwatch]::StartNew()
    $lastProgress = [DateTime]::UtcNow
    $nextGuardCheck = [TimeSpan]::FromSeconds(30)
    $guardSnapshots = [System.Collections.Generic.List[object]]::new()
    $stdoutTask = $null
    $stderrTask = $null
    $guardFailure = $null
    $watchdogFailure = $null
    $stdoutLines = [System.Collections.Generic.List[string]]::new()
    $stderrLines = [System.Collections.Generic.List[string]]::new()
    $exitDrainStarted = $null
    if (-not $process.Start()) { throw 'T66_CANDIDATE_SIM_START_FAILED: 无法启动仿真程序。' }
    $script:SimulatorStarted = $true
    $script:ActiveProcessId = [int]$process.Id
    $stdoutTask = $process.StandardOutput.ReadLineAsync()
    $stderrTask = $process.StandardError.ReadLineAsync()
    $script:ActiveStdoutTask = $stdoutTask
    $script:ActiveStderrTask = $stderrTask
    while ($true) {
            if ($process.HasExited) {
                if ($null -eq $exitDrainStarted) { $exitDrainStarted = [System.Diagnostics.Stopwatch]::StartNew() }
                if ($exitDrainStarted.ElapsedMilliseconds -ge $script:DrainTimeoutMilliseconds) {
                    throw 'T66_CANDIDATE_CAPTURE_TIMEOUT: 仿真退出后输出管道未收尾。'
                }
            }
            $pendingTasks = @()
            if ($null -ne $stdoutTask) { $pendingTasks += $stdoutTask }
            if ($null -ne $stderrTask) { $pendingTasks += $stderrTask }
            if ($pendingTasks.Count -gt 0) {
                [void][System.Threading.Tasks.Task]::WaitAny([System.Threading.Tasks.Task[]]$pendingTasks, 1000)
            } else {
                Start-Sleep -Milliseconds 1000
            }

            if ($null -ne $stdoutTask -and $stdoutTask.IsCompleted) {
                $line = $stdoutTask.GetAwaiter().GetResult()
                if ($null -eq $line) { $stdoutTask = $null }
                else {
                    $stdoutLines.Add($line)
                    $stdoutWriter.WriteLine($line)
                    if ($line -match '^T66_(CYCLE_)?PROGRESS\b') {
                        $lastProgress = [DateTime]::UtcNow
                        Write-Output $line
                    }
                    $stdoutTask = $process.StandardOutput.ReadLineAsync()
                }
                $script:ActiveStdoutTask = $stdoutTask
            }
            if ($null -ne $stderrTask -and $stderrTask.IsCompleted) {
                $line = $stderrTask.GetAwaiter().GetResult()
                if ($null -eq $line) { $stderrTask = $null }
                else {
                    $stderrLines.Add($line)
                    $stderrWriter.WriteLine($line)
                    $stderrTask = $process.StandardError.ReadLineAsync()
                }
                $script:ActiveStderrTask = $stderrTask
            }

            if ($simulationWatch.Elapsed -ge [TimeSpan]::FromMinutes(30)) {
                $watchdogFailure = 'T66_CANDIDATE_WALL_TIMEOUT: 仿真超过30分钟。'
                throw $watchdogFailure
            } elseif ((([DateTime]::UtcNow - $lastProgress).TotalSeconds) -ge 180 -and
                      -not $process.HasExited) {
                $watchdogFailure = 'T66_CANDIDATE_NO_PROGRESS_TIMEOUT: 连续180秒没有仿真进度标记。'
                throw $watchdogFailure
            }

            if ($null -eq $guardFailure -and -not $process.HasExited -and
                $simulationWatch.Elapsed -ge $nextGuardCheck) {
                try {
                    $guardSnapshot = Get-AllowedProcessSnapshot `
                        -AllowedIdentities $allowedProcesses `
                        -Phase "candidate_run_elapsed_$([int]$simulationWatch.Elapsed.TotalSeconds)s"
                    $guardSnapshots.Add($guardSnapshot)
                    $nextGuardCheck = $simulationWatch.Elapsed + [TimeSpan]::FromSeconds(30)
                }
                catch {
                    $guardFailure = $_.Exception.Message
                    throw
                }
            }
            if ($process.HasExited -and $null -eq $stdoutTask -and $null -eq $stderrTask) { break }
    }
    if (-not $process.WaitForExit($script:CleanupTimeoutMilliseconds)) { throw 'T66_CANDIDATE_EXIT_TIMEOUT: 仿真进程未退出。' }
    $simulationWatch.Stop()
    $simulationExitCode = [int]$process.ExitCode
    $script:ActiveExitCode = $simulationExitCode
    Initialize-BoundedProcessSupport
    if (-not [T66BoundedProcessStop]::CloseWriter($stdoutWriter, $script:DrainTimeoutMilliseconds) -or
        -not [T66BoundedProcessStop]::CloseWriter($stderrWriter, $script:DrainTimeoutMilliseconds)) {
        throw 'T66_CANDIDATE_WRITER_TIMEOUT: 输出 writer 收尾超时。'
    }
    $script:ActiveStdoutWriter = $null
    $script:ActiveStderrWriter = $null
    $script:ActiveOutputMode = $null
    $script:RunnerStage = 'simulation_postflight_guard'
    $postRunGuard = $null
    if ($null -eq $guardFailure) {
        try {
            $postRunGuard = Get-AllowedProcessSnapshot -AllowedIdentities $allowedProcesses -Phase 'candidate_run_after'
        }
        catch {
            $guardFailure = $_.Exception.Message
        }
    }
    if ($null -ne $postRunGuard) { $guardSnapshots.Add($postRunGuard) }
    Write-NewJson -Path $simulationGuardSamplesPath -Value @($guardSnapshots)

    $outputText = $stdoutLines -join [Environment]::NewLine
    $passRegex = '(?m)^PASS: T66 candidate blackbox sample0 layer0 full tensor matched T25; bytes=1384448 mismatches=0 input_reads=583443 weight_reads=584064 output_writes=1384448 requests=2551955 responses=2551955 request_stalls=6635073 response_stalls=6635073 cycles=[0-9]+\r?$'
    $passObserved = [bool]($outputText -match $passRegex)
    $lanePassCount = Assert-UniqueMarkerSet -Text $outputText -Prefix 'T66_READ_LANE_PASS' -Field 'lane' -Expected @(0,1,2,3)
    $stallClassCount = Assert-UniqueMarkerSet -Text $outputText -Prefix 'T66_CLASS_STALL' -Field 'class' -Expected @(0,1,2)
    $fixtureMarkerObserved = [bool]($outputText -match '(?m)^T66_FIXTURES input=519168 weight=864 expected=1384448 shape=\[1,32,208,208\] layout=NCHW\r?$')
    $memoryMarkerObserved = [bool]($outputText -match '(?m)^T66_MEMORY byte-strobes=one-hot aligned=32-bit outstanding=1 stall-pattern=\[0,1,2,7,3\]\r?$')
    $cycleLimitMarkerObserved = [bool]($outputText -match '(?m)^T66_PLAN cycle_limit=75000000 lanes=8 waveforms=disabled mq_bias=normal_descriptor_prefetch\r?$')
    $simulationPassed = ($simulationExitCode -eq 0) -and $passObserved -and
        ($lanePassCount -eq 4) -and ($stallClassCount -eq 3) -and
        $fixtureMarkerObserved -and $memoryMarkerObserved -and $cycleLimitMarkerObserved -and
        [string]::IsNullOrWhiteSpace($guardFailure) -and [string]::IsNullOrWhiteSpace($watchdogFailure)
    $simulationRecord = [ordered]@{
        schema_version = 'gestureforge_s2a_t66_candidate_blackbox_simulation_record_v1'
        task_id = 'S2A-T66-CANDIDATE-BLACKBOX'
        candidate_dut_sha256 = $expectedCandidateSha256
        evidence_mutex_name = $script:EvidenceMutexName
        approved_compile_record_sha256 = $ApprovedCompileRecordSha256.ToLowerInvariant()
        command = @($simulatorPath) + $simulationArguments
        environment = [ordered]@{
            PATH_prefix = @($toolBinPath, $makeBinPath)
            VERILATOR_ROOT = $verilatorRootPath
        }
        exit_code = $simulationExitCode
        simulator_started = $true
        duration_seconds = [Math]::Round($simulationWatch.Elapsed.TotalSeconds, 3)
        pass_marker_observed = $passObserved
        fixture_marker_observed = $fixtureMarkerObserved
        memory_protocol_marker_observed = $memoryMarkerObserved
        cycle_limit_marker_observed = $cycleLimitMarkerObserved
        normal_mq_bias_descriptor_prefetch_marker_observed = $cycleLimitMarkerObserved
        read_lane_pass_marker_count = $lanePassCount
        transfer_stall_class_marker_count = $stallClassCount
        expected_full_output_bytes = $expectedOutputBytes
        expected_input_read_requests = 583443
        expected_weight_read_requests = 584064
        expected_output_write_requests = $expectedOutputBytes
        expected_total_requests_and_responses = 2551955
        expected_request_and_response_stall_cycles = 6635073
        stdout_path = $stdoutPath
        stderr_path = $stderrPath
        process_guard_snapshot_path = $simulationGuardSamplesPath
        process_guard_failure = $guardFailure
        watchdog_failure = $watchdogFailure
        result = if ($simulationPassed) { 'PASS_FULL_LAYER0_BLACKBOX' } else { 'FAIL_OR_GUARD_REJECTED' }
    }
    Write-NewJson -Path $simulationRecordPath -Value $simulationRecord
    $simulationStatus = [ordered]@{
        schema_version = 'gestureforge_s2a_t66_candidate_blackbox_simulation_status_v1'
        status = $simulationRecord.result
        candidate_dut_sha256 = $expectedCandidateSha256
        simulation_record_sha256 = Get-Sha256 -Path $simulationRecordPath
    }
    Write-NewJson -Path $simulationStatusPath -Value $simulationStatus
    if (-not $simulationPassed) {
        $script:ActiveExitCode = if ($simulationExitCode -ne 0) { $simulationExitCode } else { 1 }
        throw 'T66_CANDIDATE_SIMULATION_GATE_FAILED: layer0 golden 比较、marker、watchdog 或 process guard 未通过。'
    }
    Write-Output "PASS_FULL_LAYER0_BLACKBOX evidence=$evidencePath duration_seconds=$($simulationRecord.duration_seconds)"
    Release-EvidenceMutex
    return
}
catch {
    $originalFailure = $_
    Stop-ActiveProcessAndCapture
    $errorText = $originalFailure.Exception.Message
    if ($script:FailureDirectoryCreatedByInvocation -and
        $null -ne $script:FailureDirectoryPath -and
        (Test-Path -LiteralPath $script:FailureDirectoryPath -PathType Container)) {
        $failureRecordPath = Join-Path $script:FailureDirectoryPath 'runner_failure_record.json'
        $failureStatusPath = Join-Path $script:FailureDirectoryPath 'runner_failure_status.json'
        $failureRecord = [ordered]@{
            schema_version = 'gestureforge_s2a_t66_candidate_runner_failure_v1'
            stage = $script:RunnerStage
            error_category = $originalFailure.Exception.GetType().FullName
            error_message = $errorText
            exit_code = $script:ActiveExitCode
            process_id = $script:ActiveProcessId
            candidate_dut_sha256 = $expectedCandidateSha256
            simulator_started = [bool]$script:SimulatorStarted
            partial_stdout_path = $script:ActiveStdoutPath
            partial_stderr_path = $script:ActiveStderrPath
            timestamp_utc = [DateTime]::UtcNow.ToString('o')
            cleanup = $script:CleanupDiagnostics
        }
        $failureStatus = [ordered]@{
            schema_version = 'gestureforge_s2a_t66_candidate_runner_failure_status_v1'
            status = 'FAILED'
            stage = $script:RunnerStage
            candidate_dut_sha256 = $expectedCandidateSha256
            failure_record_path = $failureRecordPath
            failure_record_sha256 = $null
        }
        $null = Save-FailureEvidence -RecordPath $failureRecordPath -StatusPath $failureStatusPath -Record $failureRecord -Status $failureStatus
    }
    else { [Console]::Error.WriteLine('T66_FAILURE_PERSISTENCE: record_saved=false status_saved=false; invocation 未创建可写证据目录。') }
    Release-EvidenceMutex
    [Console]::Error.WriteLine($errorText)
    exit 1
}
