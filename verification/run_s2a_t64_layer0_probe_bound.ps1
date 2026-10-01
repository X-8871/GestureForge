[CmdletBinding()]
param(
    [switch]$PreflightOnly,
    [switch]$AllowConcurrentProtectedProcesses
)

$ErrorActionPreference = 'Stop'

$ProjectRoot = 'D:\FPGA_Competition'
$RunnerPath = 'D:\FPGA_Competition\verification\run_s2a_t64_layer0_probe_bound.ps1'
$ReferenceCommandPath = 'D:\FPGA_Competition\report\evidence\S2A-T64\sim_run11\run_layer0_probe.cmd'
$RunDirectory = 'D:\FPGA_Competition\report\evidence\S2A-T64\sim_run12'
$VivadoBin = 'D:\Xilinx\2026.1\Vivado\bin'
$XvlogPath = Join-Path $VivadoBin 'xvlog.bat'
$XelabPath = Join-Path $VivadoBin 'xelab.bat'
$XsimPath = Join-Path $VivadoBin 'xsim.bat'
$ExpectedRelativeSources = @(
    'src\s2a_network_descriptor_pkg.sv',
    'src\int8_conv_tap_geometry.sv',
    'src\int8_conv_weight_address.sv',
    'src\int8_mac_accumulator.sv',
    'src\int8_maxpool_geometry.sv',
    'src\int8_maxpool_window.sv',
    'src\int8_route_query.sv',
    'src\int8_upsample_query.sv',
    'src\s2a_conv_engine.sv',
    'src\s2a_maxpool_engine.sv',
    'src\s2a_route_engine.sv',
    'src\s2a_upsample_engine.sv',
    'src\s2a_control_csr.sv',
    'src\s2a_network_backend.sv',
    'sim\tb_s2a_network_backend_layer0_probe.sv'
)
$ProtectedProcessNames = @('vivado.exe', 'xsim.exe', 'xsimk.exe', 'xvlog.exe', 'xelab.exe')
$ToolFailureCodes = @{ xvlog = 91; xelab = 92; xsim = 93 }
$script:FailureExitCode = 1
$script:FailureMessage = $null
$script:PhaseResults = [ordered]@{}
$script:SourceBindings = @()
$script:ProtectedBefore = @()
$script:RunDirectoryCreated = $false
$script:ManifestWritten = $false
$script:RunManifest = $null
$script:ToolPlan = @()
$script:ReferenceBinding = $null
$script:RunnerHash = $null
$script:GitHead = $null
$script:PassLines = @()

function Get-FileBinding {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ExpectedPath
    )
    $item = Get-Item -LiteralPath $Path -Force
    if ($item.PSIsContainer) {
        throw "Expected a file at the exact path: $ExpectedPath"
    }
    if ($item.FullName -cne $ExpectedPath) {
        throw "Resolved path mismatch: expected $ExpectedPath; got $($item.FullName)"
    }
    $digest = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    [pscustomobject]@{
        path = $item.FullName
        sha256 = $digest
        length_bytes = [int64]$item.Length
    }
}

function Get-ProtectedProcessSnapshot {
    $items = @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop |
        Where-Object { $ProtectedProcessNames -ccontains ([string]$_.Name).ToLowerInvariant() } |
        Sort-Object -Property ProcessId)
    $snapshot = @()
    foreach ($item in $items) {
        $snapshot += [pscustomobject]@{
            process_id = [int]$item.ProcessId
            name = [string]$item.Name
            executable_path = [string]$item.ExecutablePath
        }
    }
    return $snapshot
}

function Get-ProcessSetKey {
    param([object[]]$Processes)
    return (@($Processes | ForEach-Object { '{0}|{1}' -f $_.process_id, $_.name } | Sort-Object) -join ';')
}

function Get-ProcessSummary {
    param([object[]]$Processes)
    if ($Processes.Count -eq 0) {
        return 'none'
    }
    return (@($Processes | ForEach-Object { '{0}#{1}' -f $_.name, $_.process_id }) -join ',')
}

function Assert-ProtectedProcessesUnchanged {
    param([string]$StageName)
    $current = @(Get-ProtectedProcessSnapshot)
    if ((Get-ProcessSetKey $current) -cne (Get-ProcessSetKey $script:ProtectedBefore)) {
        $script:FailureExitCode = 96
        throw "Protected process set changed before stage $StageName; refusing to continue."
    }
}

function Write-JsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Value
    )
    $json = ConvertTo-Json -InputObject $Value -Depth 16
    $encoding = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, $encoding)
}

function Get-CurrentGitHead {
    $head = & git -C $ProjectRoot rev-parse HEAD
    if ($LASTEXITCODE -ne 0) {
        throw 'git rev-parse HEAD failed.'
    }
    $head = [string]$head
    if ($head -notmatch '^[0-9a-fA-F]{40}$') {
        throw "Unexpected Git HEAD value: $head"
    }
    return $head.ToLowerInvariant()
}

function Get-ReferenceCommandLines {
    param([string[]]$SourcePaths)
    $content = Get-Content -LiteralPath $ReferenceCommandPath -Raw -Encoding UTF8
    $lines = @([regex]::Split($content, '\r?\n'))
    $xvlogLine = @($lines | Where-Object { $_ -match '^call "[^"]*\\xvlog\.bat"' })
    $xelabLine = @($lines | Where-Object { $_ -match '^call "[^"]*\\xelab\.bat"' })
    $xsimLine = @($lines | Where-Object { $_ -match '^call "[^"]*\\xsim\.bat"' })
    if ($xvlogLine.Count -ne 1 -or $xelabLine.Count -ne 1 -or $xsimLine.Count -ne 1) {
        throw 'The reference command must contain exactly one xvlog, xelab, and xsim invocation.'
    }

    $sourcePattern = '"(?<source>D:\\FPGA_Competition\\[^"]+\.sv)"'
    $matches = [regex]::Matches($xvlogLine[0], $sourcePattern)
    if ($matches.Count -ne 15) {
        throw "The reference xvlog command must bind exactly 15 SystemVerilog sources; found $($matches.Count)."
    }
    for ($index = 0; $index -lt $SourcePaths.Count; $index++) {
        if ($matches[$index].Groups['source'].Value -cne $SourcePaths[$index]) {
            throw "Reference source order/path mismatch at item $index."
        }
    }

    $quotedSources = @($SourcePaths | ForEach-Object { '"' + $_ + '"' }) -join ' '
    $expectedXvlog = 'call "' + $XvlogPath + '" -sv -work xil_defaultlib ' +
        $quotedSources + ' > xvlog_console.txt 2>&1'
    $expectedXelab = 'call "' + $XelabPath +
        '" -mt off -debug typical xil_defaultlib.tb_s2a_network_backend_layer0_probe -s s2a_t64_layer0_snapshot -log xelab.log > xelab_console.txt 2>&1'
    $expectedXsim = 'call "' + $XsimPath +
        '" s2a_t64_layer0_snapshot -R -log xsim.log > xsim_console.txt 2>&1'
    if ($xvlogLine[0] -cne $expectedXvlog -or
        $xelabLine[0] -cne $expectedXelab -or
        $xsimLine[0] -cne $expectedXsim) {
        throw 'The reference tool command arguments differ from the frozen runner plan.'
    }
    return [pscustomobject]@{
        xvlog = $xvlogLine[0]
        xelab = $xelabLine[0]
        xsim = $xsimLine[0]
    }
}

function Get-SourceBindings {
    $bindings = @()
    foreach ($relativePath in $ExpectedRelativeSources) {
        $absolutePath = Join-Path $ProjectRoot $relativePath
        $bindings += Get-FileBinding -Path $absolutePath -ExpectedPath $absolutePath
    }
    return $bindings
}

function Assert-SourcesUnchanged {
    param([string]$StageName)
    $currentBindings = @(Get-SourceBindings)
    if ($currentBindings.Count -ne $script:SourceBindings.Count) {
        $script:FailureExitCode = 95
        throw "Source count changed after stage $StageName."
    }
    for ($index = 0; $index -lt $currentBindings.Count; $index++) {
        if ($currentBindings[$index].path -cne $script:SourceBindings[$index].path -or
            $currentBindings[$index].sha256 -cne $script:SourceBindings[$index].sha256 -or
            $currentBindings[$index].length_bytes -ne $script:SourceBindings[$index].length_bytes) {
            $script:FailureExitCode = 95
            throw "Source binding changed after stage $($StageName): $($currentBindings[$index].path)"
        }
    }
}

function Get-LogBindings {
    $logNames = @(
        'xvlog.log', 'xvlog_console.txt',
        'xelab.log', 'xelab_console.txt',
        'xsim.log', 'xsim_console.txt'
    )
    $logs = @()
    foreach ($name in $logNames) {
        $path = Join-Path $RunDirectory $name
        if (Test-Path -LiteralPath $path -PathType Leaf) {
            $file = Get-Item -LiteralPath $path
            $logs += [pscustomobject]@{
                path = $file.FullName
                present = $true
                sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                length_bytes = [int64]$file.Length
            }
        } else {
            $logs += [pscustomobject]@{
                path = $path
                present = $false
                sha256 = $null
                length_bytes = $null
            }
        }
    }
    return $logs
}

function Write-RunStatus {
    param(
        [string]$Status,
        [int]$RunnerExitCode,
        [object[]]$ProtectedAfter,
        [string]$ProtectedSnapshotError
    )
    $sourceAfter = @()
    $sourceError = $null
    try {
        $sourceAfter = @(Get-SourceBindings)
    } catch {
        $sourceError = $_.Exception.Message
    }
    $sourceChecks = @()
    for ($index = 0; $index -lt $script:SourceBindings.Count; $index++) {
        $before = $script:SourceBindings[$index]
        $after = $null
        if ($index -lt $sourceAfter.Count) {
            $after = $sourceAfter[$index]
        }
        $same = $null -ne $after -and
            $before.path -ceq $after.path -and
            $before.sha256 -ceq $after.sha256 -and
            $before.length_bytes -eq $after.length_bytes
        $sourceChecks += [pscustomobject]@{
            path = $before.path
            before_sha256 = $before.sha256
            after_sha256 = if ($null -ne $after) { $after.sha256 } else { $null }
            before_length_bytes = $before.length_bytes
            after_length_bytes = if ($null -ne $after) { $after.length_bytes } else { $null }
            unchanged = $same
        }
    }
    if ($sourceError) {
        $Status = 'FAIL_SOURCE_HASH_CHECK'
        if ($RunnerExitCode -eq 0) {
            $RunnerExitCode = 95
        }
    } elseif (@($sourceChecks | Where-Object { -not $_.unchanged }).Count -gt 0) {
        $Status = 'FAIL_SOURCE_HASH_CHECK'
        if ($RunnerExitCode -eq 0) {
            $RunnerExitCode = 95
        }
    }
    $logBindings = @(Get-LogBindings)
    $statusObject = [ordered]@{
        status = $Status
        runner_exit_code = $RunnerExitCode
        failure = $script:FailureMessage
        git_head = $script:GitHead
        runner_sha256 = $script:RunnerHash
        manifest_written_before_tools = $script:ManifestWritten
        phase_exit_codes = $script:PhaseResults
        source_hashes_unchanged = $null -eq $sourceError -and
            @($sourceChecks | Where-Object { -not $_.unchanged }).Count -eq 0
        source_hash_check_error = $sourceError
        source_hash_checks = $sourceChecks
        logs = $logBindings
        unique_pass_line_count = $script:PassLines.Count
        unique_pass_line = if ($script:PassLines.Count -eq 1) { $script:PassLines[0] } else { $null }
        protected_processes_before = @($script:ProtectedBefore)
        protected_processes_after = @($ProtectedAfter)
        protected_process_snapshot_error = $ProtectedSnapshotError
        protected_process_set_changed = (Get-ProcessSetKey @($script:ProtectedBefore)) -cne
            (Get-ProcessSetKey @($ProtectedAfter))
    }
    Write-JsonFile -Path (Join-Path $RunDirectory 'run_status.json') -Value $statusObject
}

function Invoke-ToolStage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$ToolPath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$ConsoleLog
    )
    Assert-ProtectedProcessesUnchanged -StageName $Name
    $renderedArguments = @()
    foreach ($argument in $Arguments) {
        if ($argument.EndsWith('.sv', [System.StringComparison]::OrdinalIgnoreCase)) {
            $renderedArguments += '"' + $argument + '"'
        } else {
            $renderedArguments += $argument
        }
    }
    $commandLine = 'call "' + $ToolPath + '" ' + ($renderedArguments -join ' ') +
        ' > ' + $ConsoleLog + ' 2>&1'
    $phase = $script:PhaseResults[$Name]
    $phase.launch_command = $commandLine
    $previousTemp = $env:TEMP
    $previousTmp = $env:TMP
    $previousTmpdir = $env:TMPDIR
    $env:TEMP = Join-Path $RunDirectory 'temp'
    $env:TMP = $env:TEMP
    $env:TMPDIR = $env:TEMP
    Push-Location -LiteralPath $RunDirectory
    try {
        & $env:ComSpec /d /c $commandLine
        $toolExitCode = $LASTEXITCODE
    } finally {
        Pop-Location
        $env:TEMP = $previousTemp
        $env:TMP = $previousTmp
        $env:TMPDIR = $previousTmpdir
    }
    $phase.tool_exit_code = [int]$toolExitCode
    if ($toolExitCode -ne 0) {
        $script:FailureExitCode = $ToolFailureCodes[$Name]
        throw "$Name exited with code $toolExitCode."
    }
    Assert-SourcesUnchanged -StageName $Name
    $toolLog = Join-Path $RunDirectory "$Name.log"
    if (-not (Test-Path -LiteralPath $toolLog -PathType Leaf)) {
        $script:FailureExitCode = $ToolFailureCodes[$Name]
        throw "$Name log is missing."
    }
    $errorLines = @(Select-String -LiteralPath $toolLog -Pattern 'ERROR:|FATAL:' -AllMatches)
    if ($errorLines.Count -gt 0) {
        $script:FailureExitCode = $ToolFailureCodes[$Name]
        throw "$Name log contains ERROR or FATAL."
    }
    $phase.runner_exit_code = 0
}

function Invoke-BoundRunner {
    if ((Resolve-Path -LiteralPath $PSCommandPath).Path -cne $RunnerPath) {
        throw "Runner must be invoked from the exact path $RunnerPath"
    }
    if ((Resolve-Path -LiteralPath $PSScriptRoot).Path -cne 'D:\FPGA_Competition\verification') {
        throw 'Runner is not located in the expected project verification directory.'
    }
    if (Test-Path -LiteralPath $RunDirectory) {
        throw "Refusing to reuse or overwrite existing result path: $RunDirectory"
    }

    $script:RunnerHash = (Get-FileHash -LiteralPath $RunnerPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $script:GitHead = Get-CurrentGitHead
    $sourcePaths = @($ExpectedRelativeSources | ForEach-Object { Join-Path $ProjectRoot $_ })
    if ($sourcePaths.Count -ne 15) {
        throw "Internal compile list count is not 15: $($sourcePaths.Count)"
    }
    $referenceCommands = Get-ReferenceCommandLines -SourcePaths $sourcePaths
    $script:ReferenceBinding = Get-FileBinding -Path $ReferenceCommandPath -ExpectedPath $ReferenceCommandPath
    $script:SourceBindings = @(Get-SourceBindings)

    foreach ($toolPath in @($XvlogPath, $XelabPath, $XsimPath)) {
        if (-not (Test-Path -LiteralPath $toolPath -PathType Leaf)) {
            throw "Required Xilinx batch file is missing: $toolPath"
        }
    }
    $script:ToolPlan = @(
        [pscustomobject]@{
            name = 'xvlog'
            executable = $XvlogPath
            arguments = @('-sv', '-work', 'xil_defaultlib') + $sourcePaths
            console_log = 'xvlog_console.txt'
            tool_log = 'xvlog.log'
            runner_failure_code = 91
        },
        [pscustomobject]@{
            name = 'xelab'
            executable = $XelabPath
            arguments = @('-mt', 'off', '-debug', 'typical', 'xil_defaultlib.tb_s2a_network_backend_layer0_probe',
                '-s', 's2a_t64_layer0_snapshot', '-log', 'xelab.log')
            console_log = 'xelab_console.txt'
            tool_log = 'xelab.log'
            runner_failure_code = 92
        },
        [pscustomobject]@{
            name = 'xsim'
            executable = $XsimPath
            arguments = @('s2a_t64_layer0_snapshot', '-R', '-log', 'xsim.log')
            console_log = 'xsim_console.txt'
            tool_log = 'xsim.log'
            runner_failure_code = 93
        }
    )

    $script:ProtectedBefore = @(Get-ProtectedProcessSnapshot)
    if ($PreflightOnly) {
        $message = 'PREFLIGHT: exact paths, 15 source bindings, reference arguments, tools, Git HEAD, and runner hash checked; output_directory_created=false.'
        Write-Host $message
        Write-Host ("PROTECTED_PROCESSES: " + (Get-ProcessSummary $script:ProtectedBefore))
        if ($script:ProtectedBefore.Count -gt 0 -and -not $AllowConcurrentProtectedProcesses) {
            Write-Host 'BLOCKED: protected Vivado/XSim processes are active; sim_run12 was not created and no tool was started.'
            return 2
        }
        if ($script:ProtectedBefore.Count -gt 0) {
            Write-Host 'PREFLIGHT_READY_WITH_EXPLICIT_CONCURRENCY_OPT_IN: no tool was started.'
        } else {
            Write-Host 'PREFLIGHT_READY: no protected processes are active; no tool was started.'
        }
        return 0
    }

    if ($script:ProtectedBefore.Count -gt 0 -and -not $AllowConcurrentProtectedProcesses) {
        Write-Host ("BLOCKED: protected Vivado/XSim processes are active: " +
            (Get-ProcessSummary $script:ProtectedBefore) +
            '; sim_run12 was not created and no tool was started.')
        return 2
    }

    [System.IO.Directory]::CreateDirectory($RunDirectory) | Out-Null
    $script:RunDirectoryCreated = $true
    $tempDirectory = Join-Path $RunDirectory 'temp'
    [System.IO.Directory]::CreateDirectory($tempDirectory) | Out-Null

    foreach ($tool in $script:ToolPlan) {
        $script:PhaseResults[$tool.name] = [ordered]@{
            executable = $tool.executable
            arguments = @($tool.arguments)
            launch_command = $null
            tool_exit_code = $null
            runner_exit_code = $null
        }
    }
    $script:RunManifest = [ordered]@{
        schema = 's2a_t64_bound_probe_run_v1'
        status = 'PREPARED'
        git_head = $script:GitHead
        runner_path = $RunnerPath
        runner_sha256 = $script:RunnerHash
        reference_command = $script:ReferenceBinding
        reference_tool_commands = $referenceCommands
        result_directory = $RunDirectory
        working_directory = $RunDirectory
        temporary_directory = $tempDirectory
        sources = @($script:SourceBindings)
        tools = @($script:ToolPlan)
        protected_processes_before = @($script:ProtectedBefore)
        created_utc = [DateTime]::UtcNow.ToString('o')
    }
    Write-JsonFile -Path (Join-Path $RunDirectory 'run_manifest.json') -Value $script:RunManifest
    $script:ManifestWritten = $true

    $status = 'FAIL'
    $runnerExitCode = 1
    $protectedAfter = @()
    $protectedSnapshotError = $null
    try {
        Assert-SourcesUnchanged -StageName 'before xvlog'
        Invoke-ToolStage -Name 'xvlog' -ToolPath $XvlogPath -Arguments $script:ToolPlan[0].arguments -ConsoleLog $script:ToolPlan[0].console_log
        $script:PhaseResults['xvlog'].runner_exit_code = 0

        Invoke-ToolStage -Name 'xelab' -ToolPath $XelabPath -Arguments $script:ToolPlan[1].arguments -ConsoleLog $script:ToolPlan[1].console_log
        $snapshotPath = Join-Path $RunDirectory 'xsim.dir\s2a_t64_layer0_snapshot\xsimk.exe'
        if (-not (Test-Path -LiteralPath $snapshotPath -PathType Leaf)) {
            $script:FailureExitCode = 92
            throw 'Elaborated xsim snapshot executable is missing.'
        }
        $script:PhaseResults['xelab'].runner_exit_code = 0

        Invoke-ToolStage -Name 'xsim' -ToolPath $XsimPath -Arguments $script:ToolPlan[2].arguments -ConsoleLog $script:ToolPlan[2].console_log
        $xsimLog = Join-Path $RunDirectory 'xsim.log'
        $script:PassLines = @(Get-Content -LiteralPath $xsimLog -Encoding UTF8 |
            Where-Object { $_.StartsWith('PASS: layer0', [System.StringComparison]::Ordinal) })
        if ($script:PassLines.Count -ne 1) {
            $script:FailureExitCode = 94
            throw "Expected exactly one PASS: layer0 line; found $($script:PassLines.Count)."
        }
        $script:PhaseResults['xsim'].runner_exit_code = 0

        Assert-SourcesUnchanged -StageName 'after xsim'
        $status = 'PASS'
        $runnerExitCode = 0
    } catch {
        $script:FailureMessage = $_.Exception.Message
        $runnerExitCode = $script:FailureExitCode
        foreach ($name in @('xvlog', 'xelab', 'xsim')) {
            if ($null -eq $script:PhaseResults[$name].runner_exit_code -and
                $null -ne $script:PhaseResults[$name].tool_exit_code) {
                $script:PhaseResults[$name].runner_exit_code = $runnerExitCode
            }
        }
        Write-Host ("RUN_FAILED: " + $script:FailureMessage)
    } finally {
        try {
            $protectedAfter = @(Get-ProtectedProcessSnapshot)
        } catch {
            $protectedSnapshotError = $_.Exception.Message
            if ($status -eq 'PASS') {
                $status = 'FAIL_PROTECTED_PROCESS_SNAPSHOT'
                $runnerExitCode = 97
            }
        }
        if ($status -eq 'PASS' -and -not $protectedSnapshotError -and
            (Get-ProcessSetKey @($script:ProtectedBefore)) -cne
            (Get-ProcessSetKey @($protectedAfter))) {
            $status = 'FAIL_PROTECTED_PROCESS_SET_CHANGED'
            $runnerExitCode = 96
            $script:FailureMessage = 'Protected process set differs between the initial and final snapshots.'
        }
        try {
            Write-RunStatus -Status $status -RunnerExitCode $runnerExitCode -ProtectedAfter $protectedAfter -ProtectedSnapshotError $protectedSnapshotError
        } catch {
            Write-Host ("STATUS_WRITE_FAILED: " + $_.Exception.Message)
            if ($runnerExitCode -eq 0) {
                $runnerExitCode = 98
            }
        }
    }
    Write-Host ("RUN_STATUS={0}; RUNNER_EXIT_CODE={1}; PASS_LINES={2}; PROTECTED_BEFORE={3}; PROTECTED_AFTER={4}" -f
        $status, $runnerExitCode, $script:PassLines.Count,
        (Get-ProcessSummary $script:ProtectedBefore), (Get-ProcessSummary $protectedAfter))
    return $runnerExitCode
}

try {
    $exitCode = Invoke-BoundRunner
} catch {
    Write-Host ("PREFLIGHT_FAILED: " + $_.Exception.Message)
    $exitCode = 1
}
exit $exitCode
