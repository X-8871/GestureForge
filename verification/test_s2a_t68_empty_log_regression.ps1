[CmdletBinding()]
param(
    [string]$ManualEvidenceDirectory = 'report/evidence/S2A-T68/manual_20261002_140325'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-TestCondition {
    param([Parameter(Mandatory = $true)][bool]$Condition, [Parameter(Mandatory = $true)][string]$Message)
    if (-not $Condition) { throw $Message }
}

$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$coordinatorPath = Join-Path $PSScriptRoot 'run_s2a_t68_unattended_continuation.ps1'
$schedulerPath = Join-Path $PSScriptRoot 'run_s2a_t68_batch_verilator.ps1'
$runnerPath = Join-Path $PSScriptRoot 'run_s2a_network_backend_verilator.ps1'
foreach ($binding in @(
    @{ path = $coordinatorPath; names = @('Write-NewUtf8File', 'Invoke-CapturedProcess') },
    @{ path = $schedulerPath; names = @(
        'Get-Sha256Literal', 'Read-JsonObject', 'Assert-NormalDirectory', 'Assert-PathWithin',
        'Get-SafeRunFile', 'Get-ClosureSignature', 'Get-ClosureDigest',
        'Get-SourceClosureFromSnapshot', 'Test-S2aNetworkBackendResultSummary', 'Assert-Sample0Passed'
    ) }
)) {
    $tokens = $null
    $parseErrors = $null
    $sourceAst = [System.Management.Automation.Language.Parser]::ParseFile($binding.path, [ref]$tokens, [ref]$parseErrors)
    if ($parseErrors.Count -gt 0) { throw "PowerShell 解析失败：$($binding.path)；$($parseErrors[0].Message)" }
    foreach ($name in $binding.names) {
        $functionName = [string]$name
        $functionAst = $sourceAst.Find({
            param($node)
            ($node -is [System.Management.Automation.Language.FunctionDefinitionAst]) -and ($node.Name -ceq $functionName)
        }, $true)
        if ($null -eq $functionAst) { throw "未找到 AST 函数：$functionName ($($binding.path))" }
        . ([scriptblock]::Create($functionAst.Extent.Text))
    }
}

$temporaryRoot = [System.IO.Path]::GetFullPath((Join-Path ([System.IO.Path]::GetTempPath()) ('s2a-t68-empty-log-' + [guid]::NewGuid().ToString('N'))))
$successDirectory = Join-Path $temporaryRoot 'success'
$failureDirectory = Join-Path $temporaryRoot 'failure'
$protectedDirectory = Join-Path $temporaryRoot 'protected'
$null = [System.IO.Directory]::CreateDirectory($successDirectory)
$null = [System.IO.Directory]::CreateDirectory($failureDirectory)
$null = [System.IO.Directory]::CreateDirectory($protectedDirectory)
$pwshPath = Join-Path $PSHOME 'pwsh.exe'
try {
    $successRun = Invoke-CapturedProcess -ExecutablePath $pwshPath `
        -Arguments @('-NoLogo', '-NoProfile', '-NonInteractive', '-Command', 'exit 0') -WorkingDirectory $repositoryRoot
    Assert-TestCondition -Condition ($successRun.exit_code -eq 0) -Message '合成成功子进程 exit code 应为 0。'
    Assert-TestCondition -Condition ([string]$successRun.stdout -ceq '') -Message '合成成功子进程 stdout 应为空。'
    Assert-TestCondition -Condition ([string]$successRun.stderr -ceq '') -Message '合成成功子进程 stderr 应为空。'
    $successStdoutPath = Join-Path $successDirectory 'stdout.log'
    $successStderrPath = Join-Path $successDirectory 'stderr.log'
    Write-NewUtf8File -Path $successStdoutPath -Text $successRun.stdout
    Write-NewUtf8File -Path $successStderrPath -Text $successRun.stderr
    Assert-TestCondition -Condition ((Get-Item -LiteralPath $successStdoutPath).Length -eq 0) -Message '空 stdout 应创建空文件。'
    Assert-TestCondition -Condition ((Get-Item -LiteralPath $successStderrPath).Length -eq 0) -Message '空 stderr 应创建空文件。'

    $failureRun = Invoke-CapturedProcess -ExecutablePath $pwshPath `
        -Arguments @('-NoLogo', '-NoProfile', '-NonInteractive', '-Command', '[Console]::Out.Write("synthetic stdout"); [Console]::Error.Write("synthetic stderr"); exit 17') `
        -WorkingDirectory $repositoryRoot
    Assert-TestCondition -Condition ($failureRun.exit_code -eq 17) -Message '合成失败子进程 exit code 应保留为 17。'
    Assert-TestCondition -Condition ([string]$failureRun.stdout -ceq 'synthetic stdout') -Message '合成失败子进程 stdout 不符。'
    Assert-TestCondition -Condition ([string]$failureRun.stderr -ceq 'synthetic stderr') -Message '合成失败子进程 stderr 不符。'
    $failureStdoutPath = Join-Path $failureDirectory 'stdout.log'
    $failureStderrPath = Join-Path $failureDirectory 'stderr.log'
    Write-NewUtf8File -Path $failureStdoutPath -Text $failureRun.stdout
    Write-NewUtf8File -Path $failureStderrPath -Text $failureRun.stderr
    Assert-TestCondition -Condition ([System.IO.File]::ReadAllText($failureStdoutPath) -ceq 'synthetic stdout') -Message '非零子进程 stdout 日志未保留。'
    Assert-TestCondition -Condition ([System.IO.File]::ReadAllText($failureStderrPath) -ceq 'synthetic stderr') -Message '非零子进程 stderr 日志未保留。'

    $protectedPath = Join-Path $protectedDirectory 'stdout.log'
    [System.IO.File]::WriteAllText($protectedPath, 'preserve-existing')
    $overwriteRejected = $false
    try {
        Write-NewUtf8File -Path $protectedPath -Text ([string]$failureRun.stdout)
    } catch {
        $overwriteRejected = $true
    }
    Assert-TestCondition -Condition $overwriteRejected -Message 'CreateNew 日志写入应拒绝覆盖既有文件。'
    Assert-TestCondition -Condition ([System.IO.File]::ReadAllText($protectedPath) -ceq 'preserve-existing') -Message '覆盖拒绝后既有日志内容发生变化。'
} finally {
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

$newlineCases = 0
$goodLines = @(
    'status=PASS_LAYERWISE_EXACT_GOLDEN',
    'feature_write_bytes=11382150 mismatches=0 cycles=972865374',
    'head13_bytes=5070 head26_bytes=20280'
)
$validTexts = @(
    ($goodLines -join "`n"),
    ($goodLines -join "`r`n"),
    ($goodLines[0] + "`r`n" + $goodLines[1] + "`n" + $goodLines[2] + "`r`n")
)
foreach ($validText in $validTexts) {
    Assert-TestCondition -Condition (Test-S2aNetworkBackendResultSummary -Text $validText) -Message 'LF、CRLF、混合换行有效摘要应通过。'
    $newlineCases++
}
$badTexts = @(
    (($goodLines[0..0] + @('feature_write_bytes=11382150 mismatches=1 cycles=972865374', $goodLines[2])) -join "`r`n"),
    (($goodLines[0..0] + @('feature_write_bytes=11382149 mismatches=0 cycles=972865374', $goodLines[2])) -join "`n"),
    (($goodLines[0..1]) -join "`r`n"),
    (('status=PASS_LAYERWISE_EXACT_GOLDEN trailing' + "`r`n" + $goodLines[1] + "`n" + $goodLines[2])),
    (($goodLines[0] + "`r`n" + $goodLines[1] + "`nhead13_bytes=5070 head26_bytes=20280 extra"))
)
foreach ($badText in $badTexts) {
    Assert-TestCondition -Condition (-not (Test-S2aNetworkBackendResultSummary -Text $badText)) -Message '错误、缺失或尾随内容摘要被接受。'
    $newlineCases++
}

$manualPath = if ([System.IO.Path]::IsPathRooted($ManualEvidenceDirectory)) { $ManualEvidenceDirectory } else { Join-Path $repositoryRoot $ManualEvidenceDirectory }
$manualRoot = (Resolve-Path -LiteralPath $manualPath -ErrorAction Stop).Path
$manualRunId = Split-Path -Leaf $manualRoot
$compileRecordPath = Join-Path $manualRoot ("runs\sample_000\{0}\compile_execution_record.json" -f $manualRunId)
$compileRecord = Read-JsonObject -Path $compileRecordPath -Label '授权manual sample0 compile record'
$backendPath = Join-Path $repositoryRoot 'src\s2a_network_backend.sv'
$preflight = Assert-Sample0Passed -EvidenceRoot $manualRoot -RunId $manualRunId -RepositoryRoot $repositoryRoot `
    -BackendPath $backendPath -ExpectedBackendHash $compileRecord.backend_sha256_expected
$simulationPath = Join-Path $preflight.sample_directory 'simulation_execution_record.json'
$simulationRecord = Read-JsonObject -Path $simulationPath -Label '授权manual sample0 simulation record'
$evidenceRoot = Join-Path $repositoryRoot 'report\evidence\S2A-T68\fix_empty_log_20261003'
if (Test-Path -LiteralPath $evidenceRoot) {
    $evidenceItem = Get-Item -LiteralPath $evidenceRoot -ErrorAction Stop
    if (-not $evidenceItem.PSIsContainer -or (($evidenceItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "新验证证据目录必须是普通目录：$evidenceRoot"
    }
} else {
    $null = [System.IO.Directory]::CreateDirectory($evidenceRoot)
}
$evidencePath = Join-Path $evidenceRoot ('offline_regression_' + [guid]::NewGuid().ToString('N') + '.json')
$evidence = [ordered]@{
    schema_version = 'gestureforge_s2a_t68_empty_log_offline_regression_v1'
    status = 'PASS'
    powershell_version = $PSVersionTable.PSVersion.ToString()
    powershell_executable = $pwshPath
    coordinator_sha256 = (Get-FileHash -LiteralPath $coordinatorPath -Algorithm SHA256).Hash.ToLowerInvariant()
    scheduler_sha256 = (Get-FileHash -LiteralPath $schedulerPath -Algorithm SHA256).Hash.ToLowerInvariant()
    empty_stdout_stderr_exit0 = 'PASS'
    nonzero_stdout_stderr_exit17 = 'PASS'
    create_new_overwrite_protection = 'PASS'
    result_summary_line_ending_cases = $newlineCases
    python_interpreter_invocations = 0
    scheduler_main_invocations = 0
    simulator_invocations = 0
    sample0_preflight = [ordered]@{
        run_id = $manualRunId
        status = 'PASS_SAMPLE0_PREFLIGHT'
        recorded_result_summary_sha256 = $simulationRecord.result_summary_sha256
        sample0_snapshot_sha256 = $preflight.snapshot_sha256
        compile_record_sha256 = $preflight.compile_record_sha256
        compile_source_rows = @($preflight.closure.source_rows).Count
        tooling_source_rows = @($preflight.closure.tooling_rows).Count
        common_weight_bytes = $preflight.common_weight_bytes
        common_weight_sha256 = $preflight.common_weight_sha256
        head13_sha256 = $simulationRecord.head13_export.sha256
        head26_sha256 = $simulationRecord.head26_export.sha256
    }
    evidence_created_utc = [DateTime]::UtcNow.ToString('o')
}
$evidence.evidence_path = $evidencePath
$json = ($evidence | ConvertTo-Json -Depth 12) + "`n"
$stream = [System.IO.File]::Open($evidencePath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
try {
    $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($json)
    $stream.Write($bytes, 0, $bytes.Length)
} finally {
    $stream.Dispose()
}
$evidence.evidence_sha256 = (Get-FileHash -LiteralPath $evidencePath -Algorithm SHA256).Hash.ToLowerInvariant()
$evidence | ConvertTo-Json -Depth 12 -Compress
