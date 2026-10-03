param(
    [string]$RunName = ('s3_vaxis01_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '_' + [guid]::NewGuid().ToString('N')),
    [ValidateRange(1, 600)]
    [int]$TimeoutSeconds = 120,
    [switch]$ValidateExitCodePolicy
)

$ErrorActionPreference = 'Stop'
$utf8 = [Text.UTF8Encoding]::new($false)
$repo = (Get-Item -LiteralPath (Join-Path $PSScriptRoot '..')).FullName
$tmp = (Get-Item -LiteralPath (Join-Path $repo 'tmp')).FullName
$result = [ordered]@{
    task = 'S3-VAXIS-01'
    status = 'RUNNING'
    run_name = $RunName
    started_local = (Get-Date).ToString('o')
    timeout_seconds_per_tool = $TimeoutSeconds
    commands = @()
    limitations = @(
        'Camera and AXI sides use the same clock; XPM asynchronous-clock CDC is not covered.',
        'Pixel format, I2C, real reset timing, sensor capture timing, and hardware behavior are not verified.'
    )
}
$run = $null
$resultPath = $null

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function ConvertTo-CmdBatchArgument([string]$Value) {
    if ([string]::IsNullOrEmpty($Value) -or
        $Value -notmatch '\A[\x20-\x7E]+\z' -or
        $Value.Contains('"') -or
        $Value.Contains('%')) {
        throw 'Batch command arguments must be non-empty printable ASCII without quotes or percent signs'
    }
    return '"' + $Value + '"'
}

function Resolve-ExitCodeCapturePolicy($LauncherExitCode, [string]$LauncherExitCodeError, $SentinelExitCode) {
    if ($null -eq $LauncherExitCode -or ![string]::IsNullOrWhiteSpace($LauncherExitCodeError)) {
        return [pscustomobject]@{
            Status = 'LAUNCHER_UNAVAILABLE'
            ExitCode = $null
            Error = 'Launcher exit code is missing or could not be retrieved'
        }
    }
    if ($null -eq $SentinelExitCode) {
        return [pscustomobject]@{
            Status = 'SENTINEL_UNAVAILABLE'
            ExitCode = $null
            Error = 'Tool exit-code sentinel value is missing'
        }
    }
    if ([int]$LauncherExitCode -ne [int]$SentinelExitCode) {
        return [pscustomobject]@{
            Status = 'MISMATCH'
            ExitCode = $null
            Error = 'Launcher exit code does not match the tool exit-code sentinel'
        }
    }
    return [pscustomobject]@{
        Status = 'CAPTURED'
        ExitCode = [int]$SentinelExitCode
        Error = $null
    }
}

function Invoke-ExitCodePolicySelfTest {
    $cases = @(
        [pscustomobject]@{
            Name = 'missing_launcher_with_read_error'
            LauncherExitCode = $null
            LauncherExitCodeError = 'simulated Process.ExitCode read error'
            SentinelExitCode = 0
            ExpectedStatus = 'LAUNCHER_UNAVAILABLE'
            ExpectedExitCode = $null
        },
        [pscustomobject]@{
            Name = 'missing_launcher_without_read_error'
            LauncherExitCode = $null
            LauncherExitCodeError = $null
            SentinelExitCode = 0
            ExpectedStatus = 'LAUNCHER_UNAVAILABLE'
            ExpectedExitCode = $null
        },
        [pscustomobject]@{
            Name = 'mismatched_exit_codes'
            LauncherExitCode = 0
            LauncherExitCodeError = $null
            SentinelExitCode = 1
            ExpectedStatus = 'MISMATCH'
            ExpectedExitCode = $null
        },
        [pscustomobject]@{
            Name = 'matching_zero_exit_codes'
            LauncherExitCode = 0
            LauncherExitCodeError = $null
            SentinelExitCode = 0
            ExpectedStatus = 'CAPTURED'
            ExpectedExitCode = 0
        },
        [pscustomobject]@{
            Name = 'matching_nonzero_exit_codes'
            LauncherExitCode = 23
            LauncherExitCodeError = $null
            SentinelExitCode = 23
            ExpectedStatus = 'CAPTURED'
            ExpectedExitCode = 23
        }
    )
    foreach ($case in $cases) {
        $decision = Resolve-ExitCodeCapturePolicy `
            $case.LauncherExitCode `
            $case.LauncherExitCodeError `
            $case.SentinelExitCode
        if ($decision.Status -cne $case.ExpectedStatus) {
            throw ('Exit-code policy self-test status mismatch: ' + $case.Name)
        }
        if ($null -eq $case.ExpectedExitCode) {
            if ($null -ne $decision.ExitCode -or $decision.Status -eq 'CAPTURED') {
                throw ('Exit-code policy self-test accepted a failure case: ' + $case.Name)
            }
        } elseif ($null -eq $decision.ExitCode -or [int]$decision.ExitCode -ne [int]$case.ExpectedExitCode) {
            throw ('Exit-code policy self-test exit-code mismatch: ' + $case.Name)
        }
        $exitCodeText = 'null'
        if ($null -ne $decision.ExitCode) { $exitCodeText = [string]$decision.ExitCode }
        Write-Output ('PASS policy_case=' + $case.Name + ' status=' + $decision.Status + ' exit_code=' + $exitCodeText)
    }
    Write-Output ('PASS exit_code_policy cases=' + $cases.Count)
}

function Invoke-TimedVivadoTool(
    [string]$Name,
    [string]$Executable,
    [string[]]$Arguments,
    [string]$WorkingDirectory,
    [int]$TimeoutSeconds,
    [string]$RunDirectory
) {
    $stdoutPath = Join-Path $RunDirectory ($Name + '.stdout.log')
    $stderrPath = Join-Path $RunDirectory ($Name + '.stderr.log')
    $killPath = Join-Path $RunDirectory ($Name + '.timeout-kill.log')
    $wrapperPath = Join-Path $RunDirectory ($Name + '.wrapper.cmd')
    $sentinelName = $Name + '.exitcode'
    $sentinelPath = Join-Path $RunDirectory $sentinelName
    if ((Test-Path -LiteralPath $stdoutPath) -or
        (Test-Path -LiteralPath $stderrPath) -or
        (Test-Path -LiteralPath $killPath) -or
        (Test-Path -LiteralPath $wrapperPath) -or
        (Test-Path -LiteralPath $sentinelPath)) {
        throw ('Tool log path already exists; refusing to overwrite: ' + $Name)
    }
    $batchTokens = @($Executable) + $Arguments
    $quotedTokens = foreach ($token in $batchTokens) {
        ConvertTo-CmdBatchArgument $token
    }
    $batchCommand = 'call ' + ($quotedTokens -join ' ')
    $wrapperLines = @(
        '@echo off',
        $batchCommand,
        'set "s3_tool_exit=%ERRORLEVEL%"',
        ('> "' + $sentinelName + '" echo %s3_tool_exit%'),
        'exit /b %s3_tool_exit%'
    )
    [IO.File]::WriteAllLines($wrapperPath, $wrapperLines, [Text.Encoding]::ASCII)
    $entry = [ordered]@{
        tool = $Name
        executable = $Executable
        arguments = $Arguments
        working_directory = $WorkingDirectory
        started_local = (Get-Date).ToString('o')
        timeout_seconds = $TimeoutSeconds
        pid = $null
        timed_out = $false
        exit_code = $null
        launcher_exit_code = $null
        launcher_exit_code_error = $null
        exit_code_capture_status = 'PENDING'
        exit_code_capture_error = $null
        batch_wrapper = $wrapperPath
        batch_wrapper_sha256 = Get-Sha256 $wrapperPath
        exit_code_sentinel = $sentinelPath
        exit_code_sentinel_sha256 = $null
        stdout = $stdoutPath
        stderr = $stderrPath
        stdout_sha256 = $null
        stderr_sha256 = $null
    }
    $commandProcessor = (Get-Command cmd.exe -CommandType Application -ErrorAction Stop).Source
    $processArguments = '/d /v:off /s /c ""' + $wrapperPath + '""'
    $entry.launcher = $commandProcessor
    $entry.launcher_arguments = $processArguments
    $process = Start-Process -FilePath $commandProcessor -ArgumentList $processArguments -WorkingDirectory $WorkingDirectory -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru -WindowStyle Hidden
    $entry.pid = $process.Id
    if (!$process.WaitForExit($TimeoutSeconds * 1000)) {
        $entry.timed_out = $true
        $taskkill = (Get-Command taskkill.exe -ErrorAction Stop).Source
        & $taskkill /PID $process.Id /T /F *> $killPath
        $entry.kill_exit_code = $LASTEXITCODE
        $process.WaitForExit(10000) | Out-Null
        if ($process.HasExited) {
            try { $entry.launcher_exit_code = [int]$process.ExitCode }
            catch { $entry.launcher_exit_code_error = $_.Exception.Message }
        }
        $process.Dispose()
        $entry.finished_local = (Get-Date).ToString('o')
        $entry.exit_code_capture_status = 'TIMED_OUT'
        if (Test-Path -LiteralPath $stdoutPath) { $entry.stdout_sha256 = Get-Sha256 $stdoutPath }
        if (Test-Path -LiteralPath $stderrPath) { $entry.stderr_sha256 = Get-Sha256 $stderrPath }
        if (Test-Path -LiteralPath $sentinelPath -PathType Leaf) { $entry.exit_code_sentinel_sha256 = Get-Sha256 $sentinelPath }
        $entry.kill_log = $killPath
        if (Test-Path -LiteralPath $killPath) { $entry.kill_log_sha256 = Get-Sha256 $killPath }
        return [pscustomobject]$entry
    }
    $process.Refresh()
    if ($process.HasExited) {
        try { $entry.launcher_exit_code = [int]$process.ExitCode }
        catch { $entry.launcher_exit_code_error = $_.Exception.Message }
    }
    $process.Dispose()
    $entry.finished_local = (Get-Date).ToString('o')
    if (Test-Path -LiteralPath $stdoutPath) { $entry.stdout_sha256 = Get-Sha256 $stdoutPath }
    if (Test-Path -LiteralPath $stderrPath) { $entry.stderr_sha256 = Get-Sha256 $stderrPath }
    if (!(Test-Path -LiteralPath $sentinelPath -PathType Leaf)) {
        $entry.exit_code_capture_status = 'MISSING'
        $entry.exit_code_capture_error = 'Tool exit-code sentinel was not created'
    } else {
        $entry.exit_code_sentinel_sha256 = Get-Sha256 $sentinelPath
        $sentinelText = [IO.File]::ReadAllText($sentinelPath, [Text.Encoding]::ASCII)
        if ($sentinelText -notmatch '\A(-?\d+)\r?\n\z') {
            $entry.exit_code_capture_status = 'INVALID'
            $entry.exit_code_capture_error = 'Tool exit-code sentinel does not contain exactly one integer line'
        } else {
            $exitCodeText = $Matches[1]
            $capturedExitCode = 0
            if (![int]::TryParse($exitCodeText, [ref]$capturedExitCode)) {
                $entry.exit_code_capture_status = 'INVALID'
                $entry.exit_code_capture_error = 'Tool exit-code sentinel is outside the Int32 range'
            } else {
                $decision = Resolve-ExitCodeCapturePolicy `
                    $entry.launcher_exit_code `
                    $entry.launcher_exit_code_error `
                    $capturedExitCode
                $entry.exit_code = $decision.ExitCode
                $entry.exit_code_capture_status = $decision.Status
                $entry.exit_code_capture_error = $decision.Error
            }
        }
    }
    return [pscustomobject]$entry
}

function Save-RunResult {
    if ($null -ne $script:resultPath -and $null -ne $script:run) {
        $script:result.finished_local = (Get-Date).ToString('o')
        [IO.File]::WriteAllText(
            $script:resultPath,
            ($script:result | ConvertTo-Json -Depth 12),
            $script:utf8
        )
    }
}

if ($ValidateExitCodePolicy) {
    try {
        Invoke-ExitCodePolicySelfTest
        exit 0
    } catch {
        [Console]::Error.WriteLine(('FAIL exit_code_policy ' + $_.Exception.Message))
        exit 1
    }
}

try {
    if ($RunName -notmatch '^[A-Za-z0-9_-]+$') { throw 'Run name may contain only ASCII letters, digits, underscores, and hyphens' }
    $run = Join-Path $tmp $RunName
    if (Test-Path -LiteralPath $run) { throw 'Run directory already exists; refusing to overwrite' }
    New-Item -ItemType Directory -Path $run | Out-Null
    $result.run_directory = $run
    $resultPath = Join-Path $run 'result.json'
    $result.result_path = $resultPath

    $toolRoot = 'D:\Xilinx\2026.1\Vivado\bin'
    $toolPaths = [ordered]@{
        xvlog = Join-Path $toolRoot 'xvlog.bat'
        xelab = Join-Path $toolRoot 'xelab.bat'
        xsim = Join-Path $toolRoot 'xsim.bat'
    }
    $result.tool_wrappers = @()
    foreach ($name in @('xvlog', 'xelab', 'xsim')) {
        $expectedPath = Join-Path $toolRoot ($name + '.bat')
        $toolFile = Get-Item -LiteralPath $toolPaths[$name]
        if ($toolFile.PSIsContainer -or
            [string]::Compare(
                [IO.Path]::GetFullPath($toolFile.FullName),
                [IO.Path]::GetFullPath($expectedPath),
                [StringComparison]::OrdinalIgnoreCase
            ) -ne 0) {
            throw ('Vivado tool path does not match the required path: ' + $name)
        }
        $result.tool_wrappers += [ordered]@{
            name = $name
            path = $toolFile.FullName
            sha256 = Get-Sha256 $toolFile.FullName
        }
    }

    $prepared = Join-Path $run 'prepared'
    $prepareScript = Join-Path $repo 'board/stage3/software/video/prepare_vendor.ps1'
    $prepareLog = Join-Path $run 'prepare_vendor.log'
    if (Test-Path -LiteralPath $prepareLog) { throw 'Prepare script log already exists; refusing to overwrite' }
    & $prepareScript -OutputDirectory $prepared *> $prepareLog
    if (!$?) { throw 'Pinned vendor RTL preparation script failed' }

    $manifestPath = Join-Path $prepared 'source_manifest.json'
    $manifest = Get-Content -Raw -LiteralPath $manifestPath -Encoding UTF8 | ConvertFrom-Json
    if ($manifest.reference_commit -cne 'fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327' -or
        $manifest.primary_git_blob -cne '1c43d5a28bc1904b452dec80e5eab5803ba9cdab') {
        throw 'Pinned commit or top-level Git blob mismatch in preparation manifest'
    }
    $adaptedTop = (Get-Item -LiteralPath (Join-Path $prepared 'adapted/single/alinx_ov5640.v')).FullName
    $adaptedConverter = (Get-Item -LiteralPath (Join-Path $prepared 'adapted/single/cmos_8_16bit.v')).FullName
    if ([string]::Compare(
        [IO.Path]::GetFullPath($manifest.compiled_top.path),
        [IO.Path]::GetFullPath($adaptedTop),
        [StringComparison]::OrdinalIgnoreCase
    ) -ne 0) { throw 'Manifest top-level path is not the RTL file generated by this run preparation script' }
    if ([string]::Compare(
        [IO.Path]::GetFullPath($manifest.compiled_converter.path),
        [IO.Path]::GetFullPath($adaptedConverter),
        [StringComparison]::OrdinalIgnoreCase
    ) -ne 0) { throw 'Manifest pixel-converter path is not the file generated by this run preparation script' }
    if ((Get-Sha256 $adaptedTop) -cne $manifest.compiled_top.adapted_sha256) {
        throw 'SHA-256 mismatch between compiled alinx_ov5640.v and preparation manifest'
    }
    if ((Get-Sha256 $adaptedConverter) -cne $manifest.compiled_converter.adapted_sha256) {
        throw 'SHA-256 mismatch between compiled cmos_8_16bit.v and preparation manifest'
    }
    $singleEntry = @($manifest.verified_sources | Where-Object { $_.variant -eq 'single' })
    $dualEntry = @($manifest.verified_sources | Where-Object { $_.variant -eq 'dual' })
    if ($singleEntry.Count -ne 1 -or $dualEntry.Count -ne 1 -or
        $singleEntry[0].git_blob -cne $dualEntry[0].git_blob -or
        $singleEntry[0].sha256 -cne $dualEntry[0].sha256) {
        throw 'Manifest does not establish that single- and dual-camera RTL are identical'
    }
    $result.preparation = [ordered]@{
        script = $prepareScript
        script_sha256 = Get-Sha256 $prepareScript
        log = $prepareLog
        log_sha256 = Get-Sha256 $prepareLog
        manifest = $manifestPath
        manifest_sha256 = Get-Sha256 $manifestPath
        compiled_top = $adaptedTop
        compiled_top_sha256 = Get-Sha256 $adaptedTop
        compiled_converter = $adaptedConverter
        compiled_converter_sha256 = Get-Sha256 $adaptedConverter
        patch = (Join-Path $repo 'board/stage3/software/video/vendor_axis.patch')
        patch_sha256 = Get-Sha256 (Join-Path $repo 'board/stage3/software/video/vendor_axis.patch')
    }

    $mock = (Get-Item -LiteralPath (Join-Path $repo 'tests/stage3_video/mock/xpm_fifo_async.v')).FullName
    $testbench = (Get-Item -LiteralPath (Join-Path $repo 'tests/stage3_video/test_axis_backpressure.sv')).FullName
    $result.test_inputs = @(
        [ordered]@{ path = $mock; sha256 = Get-Sha256 $mock },
        [ordered]@{ path = $testbench; sha256 = Get-Sha256 $testbench }
    )
    $compileArguments = @(
        '--sv',
        '--work', 'work',
        $mock,
        $adaptedConverter,
        $adaptedTop,
        $testbench
    )
    $compileResult = Invoke-TimedVivadoTool 'xvlog' $toolPaths.xvlog $compileArguments $run $TimeoutSeconds $run
    $result.commands += $compileResult
    if ($compileResult.timed_out) { throw 'xvlog compile timed out; its process tree was terminated' }
    if ($null -eq $compileResult.exit_code) { throw 'xvlog exit code could not be retrieved; compile result is unverified' }
    if ($compileResult.exit_code -ne 0) { throw ('xvlog compile failed with exit code: ' + $compileResult.exit_code) }

    $elaborateArguments = @(
        '--debug', 'typical',
        '--snapshot', 's3_vaxis01_snapshot',
        'work.test_axis_backpressure'
    )
    $elaborateResult = Invoke-TimedVivadoTool 'xelab' $toolPaths.xelab $elaborateArguments $run $TimeoutSeconds $run
    $result.commands += $elaborateResult
    if ($elaborateResult.timed_out) { throw 'xelab elaboration timed out; its process tree was terminated' }
    if ($null -eq $elaborateResult.exit_code) { throw 'xelab exit code could not be retrieved; elaboration result is unverified' }
    if ($elaborateResult.exit_code -ne 0) { throw ('xelab elaboration failed with exit code: ' + $elaborateResult.exit_code) }

    $simulateArguments = @('--R', 's3_vaxis01_snapshot')
    $simulateResult = Invoke-TimedVivadoTool 'xsim' $toolPaths.xsim $simulateArguments $run $TimeoutSeconds $run
    $result.commands += $simulateResult
    if ($simulateResult.timed_out) { throw 'xsim simulation timed out; its process tree was terminated' }
    if ($null -eq $simulateResult.exit_code) { throw 'xsim exit code could not be retrieved; simulation result is unverified' }
    if ($simulateResult.exit_code -ne 0) { throw ('xsim simulation failed with exit code: ' + $simulateResult.exit_code) }
    $simulationText = ''
    if (Test-Path -LiteralPath $simulateResult.stdout) {
        $simulationText += [IO.File]::ReadAllText($simulateResult.stdout)
    }
    if (Test-Path -LiteralPath $simulateResult.stderr) {
        $simulationText += [IO.File]::ReadAllText($simulateResult.stderr)
    }
    if ($simulationText -notmatch 'PASS beats=(\d+) stalled_cycles=6 fifo_pops=\1 tuser=(\d+) tlast=(\d+)') {
        throw 'xsim exited with code 0 but did not report a PASS terminal status with matching counts'
    }
    if ([int]$Matches[1] -lt 8 -or [int]$Matches[2] -lt 1 -or [int]$Matches[3] -lt 1) {
        throw 'xsim PASS counts do not meet the testbench minimum requirements'
    }
    $result.simulation_summary = [ordered]@{
        beats = [int]$Matches[1]
        stalled_cycles = 6
        fifo_pops = [int]$Matches[1]
        tuser_count = [int]$Matches[2]
        tlast_count = [int]$Matches[3]
    }
    $result.status = 'PASS'
} catch {
    $result.status = 'FAIL'
    $result.failure = $_.Exception.Message
}

if ($null -ne $resultPath -and $null -ne $run) {
    try {
        $result.input_sha256 = [ordered]@{
            test_runner = Get-Sha256 $PSCommandPath
            prepare_script = Get-Sha256 (Join-Path $repo 'board/stage3/software/video/prepare_vendor.ps1')
            patch = Get-Sha256 (Join-Path $repo 'board/stage3/software/video/vendor_axis.patch')
            testbench = Get-Sha256 (Join-Path $repo 'tests/stage3_video/test_axis_backpressure.sv')
            fifo_model = Get-Sha256 (Join-Path $repo 'tests/stage3_video/mock/xpm_fifo_async.v')
        }
        Save-RunResult
    } catch {
        $result.status = 'FAIL'
        $result.failure = 'Failed to write run evidence: ' + $_.Exception.Message
    }
}

if ($result.status -ne 'PASS') {
    [Console]::Error.WriteLine(('FAIL ' + $result.failure))
    if ($null -ne $resultPath) { [Console]::Error.WriteLine(('evidence=' + $resultPath)) }
    exit 1
}
Write-Output ('PASS task=S3-VAXIS-01 evidence=' + $resultPath)
exit 0
