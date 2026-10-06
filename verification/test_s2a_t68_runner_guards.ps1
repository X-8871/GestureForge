[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-TestCondition {
    param([Parameter(Mandatory = $true)][bool]$Condition, [Parameter(Mandatory = $true)][string]$Message)
    if (-not $Condition) { throw $Message }
}

function Assert-ExpectedFailure {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )
    try {
        & $Action | Out-Null
    } catch {
        return
    }
    throw "负向测试未拒绝：$Name"
}

function New-TestSummary {
    param([Parameter(Mandatory = $true)][string[]]$Lines, [Parameter(Mandatory = $true)][string]$NewLine)
    return (($Lines -join $NewLine) + $NewLine)
}

$runnerPath = Join-Path $PSScriptRoot 'run_s2a_network_backend_verilator.ps1'
$coordinatorPath = Join-Path $PSScriptRoot 'run_s2a_t68_unattended_continuation.ps1'
foreach ($functionBinding in @(
    @{ path = $runnerPath; name = 'Test-S2aNetworkBackendResultSummary' },
    @{ path = $runnerPath; name = 'Get-CompleteProgressMarkerLines' },
    @{ path = (Join-Path $PSScriptRoot 'run_s2a_t68_batch_verilator.ps1'); name = 'Get-StableWorkerLogSnapshot' },
    @{ path = $coordinatorPath; name = 'Assert-ApprovedPythonCommandResolution' }
)) {
    $tokens = $null
    $parseErrors = $null
    $ast = [System.Management.Automation.Language.Parser]::ParseFile($functionBinding.path, [ref]$tokens, [ref]$parseErrors)
    if ($parseErrors.Count -gt 0) { throw "PowerShell 解析失败：$($functionBinding.path)；$($parseErrors[0].Message)" }
    $functionName = [string]$functionBinding.name
    $functionAst = $ast.Find({
        param($node)
        ($node -is [System.Management.Automation.Language.FunctionDefinitionAst]) -and ($node.Name -ceq $functionName)
    }, $true)
    if ($null -eq $functionAst) { throw "未找到测试目标函数：$functionName ($($functionBinding.path))" }
    . ([scriptblock]::Create($functionAst.Extent.Text))
}

$validLines = @(
    'status=PASS_LAYERWISE_EXACT_GOLDEN',
    'feature_write_bytes=11382150 mismatches=0 cycles=972865374',
    'head13_bytes=5070 head26_bytes=20280'
)
$summaryCases = 0
$fixtureReuseGuardCases = 0
$recoverySchedulerGuardCases = 0
$runnerSourceText = [System.IO.File]::ReadAllText($runnerPath, [System.Text.Encoding]::UTF8)
$reuseBranch = $runnerSourceText.IndexOf('if ($ReuseVerifiedFixtures) {', [System.StringComparison]::Ordinal)
$prepareBranch = $runnerSourceText.IndexOf('$prepareArgs = @(', [System.StringComparison]::Ordinal)
$fixtureVerifierCall = $runnerSourceText.IndexOf('& $PythonExecutable @verifyArgs', [System.StringComparison]::Ordinal)
Assert-TestCondition -Condition ($runnerSourceText.Contains('[switch]$ReuseVerifiedFixtures')) -Message 'runner 必须提供显式只读 fixture 复用开关。'
Assert-TestCondition -Condition (($reuseBranch -ge 0) -and ($prepareBranch -gt $reuseBranch) -and ($fixtureVerifierCall -gt $prepareBranch)) -Message '只读复用分支必须跳过 preparer 且仍运行原 fixture verifier。'
Assert-TestCondition -Condition ($runnerSourceText.Contains('if (-not (Test-Path -LiteralPath $fixtureManifest -PathType Leaf))')) -Message '只读复用分支必须要求既有 fixture manifest。'
$fixtureReuseGuardCases++
$batchPath = Join-Path $PSScriptRoot 'run_s2a_t68_batch_verilator.ps1'
$batchSourceText = [System.IO.File]::ReadAllText($batchPath, [System.Text.Encoding]::UTF8)
$preflightIndex = $batchSourceText.IndexOf("Invoke-RecoveryManifestTool -Operation 'preflight'", [System.StringComparison]::Ordinal)
$preflightExitIndex = $batchSourceText.IndexOf('if ($PreflightOnly) {', $preflightIndex, [System.StringComparison]::Ordinal)
$launchRecoveryGateIndex = $batchSourceText.IndexOf('if ($LaunchRecovery) {', $preflightExitIndex, [System.StringComparison]::Ordinal)
$processGateIndex = $batchSourceText.IndexOf('Assert-NoCandidateT68Processes -EvidenceRoot', $preflightExitIndex, [System.StringComparison]::Ordinal)
$launchRecoveryGateEndIndex = $batchSourceText.IndexOf('}', $launchRecoveryGateIndex, [System.StringComparison]::Ordinal)
$dispatchCreateIndex = $batchSourceText.IndexOf('$null = New-Item -ItemType Directory -Path $dispatchDirectory', [System.StringComparison]::Ordinal)
$workerLaunchIndex = $batchSourceText.IndexOf('Start-Process -FilePath $pwshPath', [System.StringComparison]::Ordinal)
foreach ($requiredToken in @(
    '[switch]$ResumeCandidate109', '[switch]$PreflightOnly', '[switch]$LaunchRecovery',
    '$firstIndex -ne 25 -or $lastIndex -ne 108', '-ReuseVerifiedFixtures',
    'Get-StableWorkerLogSnapshot', 'stdout_read_error', 'stderr_read_error',
    '$Worker.process.HasExited', '$DispatchSubdirectory',
    'Get-CimInstance -ClassName Win32_Process -ErrorAction Stop'
)) {
    Assert-TestCondition -Condition ($batchSourceText.Contains($requiredToken)) -Message "batch scheduler 缺少恢复安全门：$requiredToken"
}
Assert-TestCondition -Condition (($preflightIndex -ge 0) -and ($preflightExitIndex -gt $preflightIndex) -and
    ($dispatchCreateIndex -gt $preflightExitIndex) -and ($workerLaunchIndex -gt $dispatchCreateIndex)) -Message '只读预检必须先于 dispatch 创建与任何 worker 启动。'
Assert-TestCondition -Condition (($launchRecoveryGateIndex -gt $preflightExitIndex) -and
    ($processGateIndex -gt $launchRecoveryGateIndex) -and ($processGateIndex -lt $launchRecoveryGateEndIndex) -and
    ($processGateIndex -lt $dispatchCreateIndex)) -Message '进程 fail-closed 门只能在静态预检退出后、LaunchRecovery 分支内且 dispatch 创建前执行。'
Assert-TestCondition -Condition ($batchSourceText.Contains('process_check_performed -ne $false') -and
    $batchSourceText.Contains('process_check=not_performed')) -Message '静态预检必须明确不执行进程检查且不得声称进程空闲。'
$recoverySchedulerGuardCases++
foreach ($newLine in @("`n", "`r`n")) {
    $validSummary = New-TestSummary -Lines $validLines -NewLine $newLine
    Assert-TestCondition -Condition (Test-S2aNetworkBackendResultSummary -Text $validSummary) -Message '有效 LF/CRLF 摘要应被接受。'
    $summaryCases++

    $badCases = @(
        @{ name = 'wrong status'; lines = @('status=FAIL', $validLines[1], $validLines[2]) },
        @{ name = 'nonzero mismatch'; lines = @($validLines[0], 'feature_write_bytes=11382150 mismatches=1 cycles=972865374', $validLines[2]) },
        @{ name = 'wrong feature bytes'; lines = @($validLines[0], 'feature_write_bytes=11382149 mismatches=0 cycles=972865374', $validLines[2]) },
        @{ name = 'missing output field'; lines = @($validLines[0], $validLines[1]) },
        @{ name = 'wrong head bytes'; lines = @($validLines[0], $validLines[1], 'head13_bytes=5070 head26_bytes=20281') }
    )
    foreach ($badCase in $badCases) {
        $badSummary = New-TestSummary -Lines $badCase.lines -NewLine $newLine
        Assert-TestCondition -Condition (-not (Test-S2aNetworkBackendResultSummary -Text $badSummary)) -Message "错误摘要被接受：$($badCase.name)"
        $summaryCases++
    }
}

$temporaryRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('s2a-t68-runner-guards-' + [guid]::NewGuid().ToString('N'))
$temporaryRoot = [System.IO.Path]::GetFullPath($temporaryRoot)
$approvedDirectory = Join-Path $temporaryRoot 'approved'
$otherDirectories = @(
    (Join-Path $temporaryRoot 'other-a'),
    (Join-Path $temporaryRoot 'other-b'),
    (Join-Path $temporaryRoot 'other-c')
)
$approvedPython = Join-Path $approvedDirectory 'python.exe'
$originalPath = $env:PATH
$pythonPathCases = 0
$progressMarkerReadCases = 0
$workerLogSnapshotCases = 0
try {
    $null = [System.IO.Directory]::CreateDirectory($approvedDirectory)
    foreach ($directory in $otherDirectories) { $null = [System.IO.Directory]::CreateDirectory($directory) }

    $progressMarkerPath = Join-Path $temporaryRoot 'progress_markers.txt'
    $firstProgressMarker = 'S2A_PROGRESS sample=7 layer=0 cycle=10 output=0 conv_tile_y=0 conv_tile_x=0 conv_group=0 conv_point=0 conv_reduction=0 conv_feature_scan=0 conv_weight_reduction=0 conv_output_lane=0 conv_output_point=0 pool_tap=0 feature_write_bytes=0 read_transactions=0 write_transactions=0 phase=start'
    $secondProgressMarker = 'S2A_PROGRESS sample=7 layer=1 cycle=20 output=1 conv_tile_y=0 conv_tile_x=0 conv_group=0 conv_point=1 conv_reduction=0 conv_feature_scan=0 conv_weight_reduction=0 conv_output_lane=0 conv_output_point=0 pool_tap=0 feature_write_bytes=4 read_transactions=1 write_transactions=1 phase=running'
    $partialProgressMarker = 'S2A_PROGRESS sample=7 layer=2 cycle=30'
    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($progressMarkerPath, $firstProgressMarker + "`n", $utf8NoBom)

    $exclusiveWriter = [System.IO.FileStream]::new($progressMarkerPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    try {
        $blockedProgressRead = Get-CompleteProgressMarkerLines -Path $progressMarkerPath
        Assert-TestCondition -Condition (-not $blockedProgressRead.readable) -Message '排他写入期间应安全报告进度文件暂不可读。'
        Assert-TestCondition -Condition ($blockedProgressRead.lines.Count -eq 0) -Message '排他写入期间不得返回伪造进度行。'
        $progressMarkerReadCases++
    } finally {
        $exclusiveWriter.Dispose()
    }

    $recoveredProgressRead = Get-CompleteProgressMarkerLines -Path $progressMarkerPath
    Assert-TestCondition -Condition $recoveredProgressRead.readable -Message '释放写入锁后进度文件应可恢复读取。'
    Assert-TestCondition -Condition ($recoveredProgressRead.lines.Count -eq 1) -Message '恢复读取应只返回完整进度行。'
    Assert-TestCondition -Condition ($recoveredProgressRead.lines[0] -ceq $firstProgressMarker) -Message '恢复读取的完整进度行内容不匹配。'
    $progressMarkerReadCases++

    $workerLogPath = Join-Path $temporaryRoot 'worker.stdout.log'
    $workerLogBytes = [System.Text.Encoding]::UTF8.GetBytes("worker output`n")
    [System.IO.File]::WriteAllBytes($workerLogPath, $workerLogBytes)
    $exclusiveWorkerLog = [System.IO.FileStream]::new($workerLogPath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::None)
    try {
        Assert-ExpectedFailure -Name '持久 worker log 文件锁' -Action {
            Get-StableWorkerLogSnapshot -Path $workerLogPath -MaxAttempts 2 -RetryDelayMilliseconds 10
        }
        $workerLogSnapshotCases++
    } finally {
        $exclusiveWorkerLog.Dispose()
    }
    $workerLogSnapshot = Get-StableWorkerLogSnapshot -Path $workerLogPath -MaxAttempts 2 -RetryDelayMilliseconds 10
    Assert-TestCondition -Condition ($workerLogSnapshot.bytes -eq $workerLogBytes.Length) -Message '共享读取的 worker log byte length 不符。'
    Assert-TestCondition -Condition ($workerLogSnapshot.sha256 -ceq [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($workerLogBytes)).ToLowerInvariant()) -Message '共享读取的 worker log SHA 不符。'
    Assert-TestCondition -Condition ($workerLogSnapshot.attempts -eq 1) -Message '可读 worker log 不应无故重试。'
    $workerLogSnapshotCases++

    $sharedWriter = [System.IO.FileStream]::new($progressMarkerPath, [System.IO.FileMode]::Append, [System.IO.FileAccess]::Write,
        ([System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete))
    try {
        $appendBytes = $utf8NoBom.GetBytes("`n" + $secondProgressMarker + "`n" + $partialProgressMarker)
        $sharedWriter.Write($appendBytes, 0, $appendBytes.Length)
        $sharedWriter.Flush()
        $concurrentProgressRead = Get-CompleteProgressMarkerLines -Path $progressMarkerPath
        Assert-TestCondition -Condition $concurrentProgressRead.readable -Message '共享写入期间进度文件应可并发读取。'
        Assert-TestCondition -Condition ($concurrentProgressRead.lines.Count -eq 2) -Message '并发读取应排除末尾未完成行。'
        Assert-TestCondition -Condition ($concurrentProgressRead.lines[1] -ceq $secondProgressMarker) -Message '并发读取的第二条完整进度行内容不匹配。'
        $progressMarkerReadCases++
    } finally {
        $sharedWriter.Dispose()
    }

    [System.IO.File]::WriteAllBytes($approvedPython, [byte[]]@())
    foreach ($directory in $otherDirectories) {
        [System.IO.File]::WriteAllBytes((Join-Path $directory 'python.exe'), [byte[]]@())
    }

    $env:PATH = (@($approvedDirectory) + $otherDirectories + @($originalPath)) -join [System.IO.Path]::PathSeparator
    $preferredCommands = @(Get-Command -Name 'python.exe' -CommandType Application -All -ErrorAction Stop)
    Assert-TestCondition -Condition ($preferredCommands.Count -ge 4) -Message '测试 PATH 未解析到多个 python.exe 候选。'
    $selectedPython = Assert-ApprovedPythonCommandResolution -ApprovedPath $approvedPython -ResolvedCommands $preferredCommands
    Assert-TestCondition -Condition ($selectedPython -ieq [System.IO.Path]::GetFullPath($approvedPython)) -Message '固定路径首选解析未被接受。'
    $pythonPathCases++

    $env:PATH = (@($otherDirectories[0], $approvedDirectory) + $otherDirectories[1..2] + @($originalPath)) -join [System.IO.Path]::PathSeparator
    $wrongFirstCommands = @(Get-Command -Name 'python.exe' -CommandType Application -All -ErrorAction Stop)
    Assert-TestCondition -Condition ($wrongFirstCommands.Count -ge 4) -Message '首选不一致用例缺少多个 python.exe 候选。'
    Assert-ExpectedFailure -Name '首选解析不一致' -Action {
        Assert-ApprovedPythonCommandResolution -ApprovedPath $approvedPython -ResolvedCommands $wrongFirstCommands
    }
    $pythonPathCases++

    Remove-Item -LiteralPath $approvedPython -Force
    $env:PATH = (@($approvedDirectory) + $otherDirectories + @($originalPath)) -join [System.IO.Path]::PathSeparator
    $withoutApprovedFile = @(Get-Command -Name 'python.exe' -CommandType Application -All -ErrorAction Stop)
    Assert-ExpectedFailure -Name '固定 Python 文件不可用' -Action {
        Assert-ApprovedPythonCommandResolution -ApprovedPath $approvedPython -ResolvedCommands $withoutApprovedFile
    }
    $pythonPathCases++
} finally {
    $env:PATH = $originalPath
    $tempParent = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $temporaryRoot.StartsWith($tempParent, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "合成测试临时目录超出系统 Temp：$temporaryRoot"
    }
    if (Test-Path -LiteralPath $temporaryRoot) {
        $temporaryItem = Get-Item -LiteralPath $temporaryRoot -ErrorAction Stop
        if (-not $temporaryItem.PSIsContainer -or (($temporaryItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "拒绝清理非普通临时目录：$temporaryRoot"
        }
        Remove-Item -LiteralPath $temporaryRoot -Recurse -Force
    }
}

[pscustomobject]@{
    status = 'PASS'
    powershell_version = $PSVersionTable.PSVersion.ToString()
    powershell_executable = Join-Path $PSHOME 'pwsh.exe'
    summary_cases = $summaryCases
    fixture_reuse_guard_cases = $fixtureReuseGuardCases
    recovery_scheduler_guard_cases = $recoverySchedulerGuardCases
    python_path_resolution_cases = $pythonPathCases
    progress_marker_read_cases = $progressMarkerReadCases
    worker_log_snapshot_cases = $workerLogSnapshotCases
    python_interpreter_invocations = 0
    simulation_invocations = 0
} | ConvertTo-Json -Compress
