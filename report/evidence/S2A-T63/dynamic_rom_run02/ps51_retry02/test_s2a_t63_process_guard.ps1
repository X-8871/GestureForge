[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$RunnerPath,
    [Parameter(Mandatory = $true)][string]$BindingPath
)

$ErrorActionPreference = 'Stop'
$tokens = $null
$parseErrors = $null
$runnerAst = [System.Management.Automation.Language.Parser]::ParseFile(
    $RunnerPath,
    [ref]$tokens,
    [ref]$parseErrors
)
if ($parseErrors.Count -gt 0) {
    throw "Runner PowerShell 解析失败：$($parseErrors[0].Message)"
}

foreach ($functionName in @(
    'Get-NormalizedFullPath',
    'Assert-PathWithin',
    'Assert-NoReparsePathChain',
    'Assert-NewOutputPath',
    'Write-NewUtf8Text',
    'Get-T63FileSha256',
    'Get-T63LogArtifactBinding',
    'Invoke-LoggedNative',
    'Get-T63ProtectedProcessAllowlist',
    'Assert-T63XilinxProcessSnapshot',
    'Invoke-T63GuardedStage'
)) {
    $functionAst = $runnerAst.Find({
        param($node)
        $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
            $node.Name -ceq $functionName
    }, $true)
    if ($null -eq $functionAst) {
        throw "Runner 缺少进程保护函数：$functionName"
    }
    Invoke-Expression $functionAst.Extent.Text
}

function New-MockProcess {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$CreationDateUtc
    )
    return [pscustomobject]@{
        ProcessId = [long]$Identity.ProcessId
        ParentProcessId = [long]$Identity.ParentProcessId
        Name = [string]$Identity.Name
        ExecutablePath = [string]$Identity.ExecutablePath
        CommandLine = [string]$Identity.CommandLine
        CreationDateUtc = $CreationDateUtc
    }
}

function Assert-GuardThrows {
    param(
        [Parameter(Mandatory = $true)][string]$CaseName,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )
    $didThrow = $false
    try {
        & $Action
    }
    catch {
        $didThrow = $true
    }
    if (-not $didThrow) {
        throw "拒绝用例未失败关闭：$CaseName"
    }
}

$identities = @(Get-T63ProtectedProcessAllowlist)
$expectedIdentityLines = @(
    '8712|10724|vivado.exe|D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o\vivado.exe|"D:/Xilinx/2026.1/Vivado/bin/unwrapped/win64.o/vivado.exe"   -mode tcl -source D:\FPGA_Competition\report\evidence\S2A-T60\run06\mcp_server_instance\start_mcp.tcl|2026-09-29T18:07:06.1577890Z',
    '22488|8712|xsimk.exe|D:\FPGA_Competition\report\evidence\S2A-T60\run06\isolated_project\s2a_t60_run06.sim\sim_1\behav\xsim\xsim.dir\tb_s2a_conv_layer35_row24_all_channels_behav\xsimk.exe|xsim.dir/tb_s2a_conv_layer35_row24_all_channels_behav/xsimk.exe -simmode gui -wdb tb_s2a_conv_layer35_row24_all_channels_behav.wdb -simrunnum 0 -socket 8295|2026-09-29T18:13:11.5972630Z',
    '13156|8712|xsimk.exe|D:\FPGA_Competition\report\evidence\S2A-T61\run04\isolated_project\s2a_t61_run04.sim\sim_1\behav\xsim\xsim.dir\tb_s2a_conv_layer35_row25_all_channels_behav\xsimk.exe|xsim.dir/tb_s2a_conv_layer35_row25_all_channels_behav/xsimk.exe -simmode gui -wdb tb_s2a_conv_layer35_row25_all_channels_behav.wdb -simrunnum 0 -socket 12375|2026-09-29T19:39:52.1132030Z'
)
$actualIdentityLines = @($identities | ForEach-Object {
    '{0}|{1}|{2}|{3}|{4}|{5}' -f $_.ProcessId, $_.ParentProcessId, $_.Name, $_.ExecutablePath, $_.CommandLine, $_.CreationDateUtc
})
if ([string]::Join("`n", $actualIdentityLines) -cne [string]::Join("`n", $expectedIdentityLines)) {
    throw '受保护 Vivado/XSim allowlist 与冻结身份不一致。'
}
$binding = Get-Content -LiteralPath $BindingPath -Raw -Encoding utf8 | ConvertFrom-Json
$baseline = $binding.process_guard_baseline
if ($null -eq $baseline -or $baseline.source -cne 'Win32_Process.CreationDate -> DateTime.ToUniversalTime().ToString(o, InvariantCulture)') {
    throw 'binding 缺少可信的 Win32_Process 创建时间证据来源。'
}
$boundIdentityLines = @($baseline.identities | ForEach-Object {
    $boundCreationDate = [string]$_.creation_date_utc
    if ($_.creation_date_utc -is [DateTime]) {
        $boundCreationDate = $_.creation_date_utc.ToUniversalTime().ToString(
            'o', [System.Globalization.CultureInfo]::InvariantCulture)
    }
    '{0}|{1}|{2}|{3}|{4}|{5}' -f $_.process_id, $_.parent_process_id, $_.name, $_.executable_path, $_.command_line, $boundCreationDate
})
if ([string]::Join("`n", $boundIdentityLines) -cne [string]::Join("`n", $expectedIdentityLines)) {
    throw 'binding 中的受保护进程身份/创建时间与 runner allowlist 不一致。'
}

$timestamps = @(
    '2026-09-29T18:07:06.1577890Z',
    '2026-09-29T18:13:11.5972630Z',
    '2026-09-29T19:39:52.1132030Z'
)
$testCaseCount = 0
$initialProcesses = @(
    (New-MockProcess -Identity $identities[0] -CreationDateUtc $timestamps[0]),
    (New-MockProcess -Identity $identities[1] -CreationDateUtc $timestamps[1]),
    (New-MockProcess -Identity $identities[2] -CreationDateUtc $timestamps[2])
)
$initial = Assert-T63XilinxProcessSnapshot -Processes $initialProcesses -ProtectedIdentities $identities -InitialSnapshot
if ($initial.process_count -ne 3) {
    throw '精确三进程初始快照没有通过。'
}
$testCaseCount++

$emptyInitial = Assert-T63XilinxProcessSnapshot -Processes @() -ProtectedIdentities $identities -InitialSnapshot
if ($emptyInitial.process_count -ne 0) {
    throw '无受保护进程的空闲实例快照没有通过。'
}
$testCaseCount++

$reducedProcesses = @($initialProcesses[0], $initialProcesses[2])
$reduced = Assert-T63XilinxProcessSnapshot -Processes $reducedProcesses -ProtectedIdentities $identities -BaselineProcesses $initialProcesses
if ($reduced.process_count -ne 2) {
    throw '自然退出受保护进程的快照没有通过。'
}
$testCaseCount++
Assert-GuardThrows -CaseName '自然退出后相同 PID 再出现' -Action {
    Assert-T63XilinxProcessSnapshot -Processes $initialProcesses -ProtectedIdentities $identities -BaselineProcesses $reducedProcesses
}
$testCaseCount++

$unexpected = [pscustomobject]@{
    ProcessId = [long]49000
    ParentProcessId = [long]1
    Name = 'xvlog.exe'
    ExecutablePath = 'D:\Xilinx\2026.1\Vivado\bin\xvlog.exe'
    CommandLine = 'xvlog.exe -version'
    CreationDateUtc = '2026-09-30T01:03:00.0000000Z'
}
Assert-GuardThrows -CaseName '新出现的 XVLOG' -Action {
    Assert-T63XilinxProcessSnapshot -Processes @($initialProcesses + $unexpected) -ProtectedIdentities $identities -BaselineProcesses $initialProcesses
}
$testCaseCount++

$changedCommandLine = New-MockProcess -Identity $identities[0] -CreationDateUtc $timestamps[0]
$changedCommandLine.CommandLine = $changedCommandLine.CommandLine + ' -unexpected'
Assert-GuardThrows -CaseName '受保护 PID 命令行变化' -Action {
    Assert-T63XilinxProcessSnapshot -Processes @($changedCommandLine) -ProtectedIdentities $identities -BaselineProcesses @($initialProcesses[0])
}
$testCaseCount++

$changedPath = New-MockProcess -Identity $identities[0] -CreationDateUtc $timestamps[0]
$changedPath.ExecutablePath = $changedPath.ExecutablePath + '.changed'
Assert-GuardThrows -CaseName '受保护 PID 可执行文件路径变化' -Action {
    Assert-T63XilinxProcessSnapshot -Processes @($changedPath) -ProtectedIdentities $identities -BaselineProcesses @($initialProcesses[0])
}
$testCaseCount++

$changedParent = New-MockProcess -Identity $identities[1] -CreationDateUtc $timestamps[1]
$changedParent.ParentProcessId = [long]99999
Assert-GuardThrows -CaseName '受保护 PID 父进程变化' -Action {
    Assert-T63XilinxProcessSnapshot -Processes @($changedParent) -ProtectedIdentities $identities -BaselineProcesses @($initialProcesses[1])
}
$testCaseCount++

$reusedPid = New-MockProcess -Identity $identities[1] -CreationDateUtc '2026-09-30T01:04:00.0000000Z'
Assert-GuardThrows -CaseName 'PID 重用创建时间变化' -Action {
    Assert-T63XilinxProcessSnapshot -Processes @($reusedPid) -ProtectedIdentities $identities -BaselineProcesses @($initialProcesses[1])
}
$testCaseCount++

Assert-GuardThrows -CaseName '启动时缺席的保护 PID 后续出现' -Action {
    Assert-T63XilinxProcessSnapshot -Processes @($initialProcesses[0]) -ProtectedIdentities $identities -BaselineProcesses @()
}
$testCaseCount++

$changedName = New-MockProcess -Identity $identities[0] -CreationDateUtc $timestamps[0]
$changedName.Name = 'python.exe'
Assert-GuardThrows -CaseName '保护 PID 被其他程序复用' -Action {
    Assert-T63XilinxProcessSnapshot -Processes @($changedName) -ProtectedIdentities $identities -BaselineProcesses @($initialProcesses[0])
}
$testCaseCount++

$missingTrustedIdentity = $identities[0] | Select-Object *
$missingTrustedIdentity.CreationDateUtc = ''
Assert-GuardThrows -CaseName '可信创建时间缺失' -Action {
    Assert-T63XilinxProcessSnapshot -Processes @() -ProtectedIdentities @($missingTrustedIdentity) -InitialSnapshot
}
$testCaseCount++

$script:toolInvocationCount = 0
$gateSnapshots = [System.Collections.Generic.List[object]]::new()
Invoke-T63GuardedStage -Phase 'mock_before_xelab' `
    -Processes $initialProcesses `
    -ProtectedIdentities $identities `
    -BaselineProcesses $initialProcesses `
    -ProcessSnapshots $gateSnapshots `
    -Action { $script:toolInvocationCount++ }
if ($script:toolInvocationCount -ne 1 -or $gateSnapshots.Count -ne 1 -or $gateSnapshots[0].phase -cne 'mock_before_xelab') {
    throw '允许的进程快照没有按预期调用工具替身并记录 gate。'
}
$testCaseCount++

$script:toolInvocationCount = 0
Assert-GuardThrows -CaseName 'xelab gate 检测额外进程后不调用工具' -Action {
    Invoke-T63GuardedStage -Phase 'mock_before_xelab' `
        -Processes @($initialProcesses + $unexpected) `
        -ProtectedIdentities $identities `
        -BaselineProcesses $initialProcesses `
        -ProcessSnapshots $gateSnapshots `
        -Action { $script:toolInvocationCount++ }
}
if ($script:toolInvocationCount -ne 0) {
    throw '发现未授权进程后仍调用了工具替身。'
}
$testCaseCount++

$logBindingTestCount = 0
$simulationRoot = Join-Path (Split-Path -Parent $RunnerPath) ('native_log_contract_test_' + [Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $simulationRoot -ErrorAction Stop | Out-Null
try {
    Assert-PathWithin -Path $simulationRoot -AllowedRoot (Split-Path -Parent $RunnerPath)
    Assert-NoReparsePathChain -Path $simulationRoot
    $workRoot = $simulationRoot
    $mockToolPath = Join-Path $simulationRoot 'mock_native_tool.ps1'
    $mockToolSource = @'
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$NativeLogPath,
    [Parameter(Mandatory = $true)][string]$ConsoleLogPath,
    [Parameter(Mandatory = $true)][string]$MarkerPath,
    [Parameter(Mandatory = $true)][int]$ExitCode
)
if ([System.IO.Path]::GetFullPath($NativeLogPath).Equals(
        [System.IO.Path]::GetFullPath($ConsoleLogPath),
        [System.StringComparison]::OrdinalIgnoreCase)) {
    throw 'mock native and console paths collide'
}
if (Test-Path -LiteralPath $NativeLogPath) {
    throw 'native log target was occupied before mock tool launch'
}
[System.IO.File]::WriteAllText($NativeLogPath, 'native-log-sentinel', [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText($MarkerPath, 'invoked', [System.Text.UTF8Encoding]::new($false))
Write-Output 'console-output-sentinel'
exit $ExitCode
'@
    Write-NewUtf8Text -Path $mockToolPath -Text $mockToolSource -AllowedRoot $workRoot
    $childPowerShell = [string](Get-Process -Id $PID -ErrorAction Stop).Path
    if ([string]::IsNullOrWhiteSpace($childPowerShell) -or -not (Test-Path -LiteralPath $childPowerShell -PathType Leaf)) {
        throw '无法定位当前 PowerShell 可执行文件以运行日志模拟替身。'
    }
    $logExecution = [System.Collections.Generic.List[object]]::new()
    $successNative = Join-Path $simulationRoot 'mock_success.log'
    $successConsole = Join-Path $simulationRoot 'mock_success.console.log'
    $successMarker = Join-Path $simulationRoot 'mock_success.marker'
    $successRecord = Invoke-LoggedNative -StageName 'mock_success' -Executable $childPowerShell -Arguments @(
        '-NoLogo',
        '-NoProfile',
        '-NonInteractive',
        '-ExecutionPolicy',
        'Bypass',
        '-File',
        $mockToolPath,
        '-NativeLogPath',
        $successNative,
        '-ConsoleLogPath',
        $successConsole,
        '-MarkerPath',
        $successMarker,
        '-ExitCode',
        '0'
    ) -ConsoleLogPath $successConsole -NativeLogPath $successNative -ExecutionLog $logExecution
    $expectedNativeHash = Get-T63FileSha256 -Path $successNative -AllowedRoot $simulationRoot
    $expectedConsoleHash = Get-T63FileSha256 -Path $successConsole -AllowedRoot $simulationRoot
    $successResultPath = Join-Path $simulationRoot 'stage_mock_success_result.json'
    $successResult = Get-Content -LiteralPath $successResultPath -Raw -Encoding utf8 | ConvertFrom-Json
    if (-not (Test-Path -LiteralPath $successMarker -PathType Leaf) -or
        $successRecord.exit_code -ne 0 -or $successRecord.status -cne 'PASS' -or
        $successRecord.native_log.path -cne $successNative -or
        $successRecord.native_log.sha256 -cne $expectedNativeHash -or
        $successRecord.console_log.path -cne $successConsole -or
        $successRecord.console_log.sha256 -cne $expectedConsoleHash -or
        $successResult.native_log.sha256 -cne $expectedNativeHash -or
        $successResult.console_log.sha256 -cne $expectedConsoleHash) {
        throw '成功模拟阶段没有分别绑定控制台/原生日志路径、SHA 和退出码。'
    }
    if ((Get-Content -LiteralPath $successNative -Raw -Encoding utf8) -cne 'native-log-sentinel' -or
        -not (Get-Content -LiteralPath $successConsole -Raw -Encoding utf8).Contains('console-output-sentinel')) {
        throw '控制台捕获覆盖了原生日志或日志内容不符。'
    }
    $logBindingTestCount++

    $collisionPath = Join-Path $simulationRoot 'mock_collision.log'
    $collisionMarker = Join-Path $simulationRoot 'mock_collision.marker'
    Assert-GuardThrows -CaseName '模拟工具控制台/原生日志同路径' -Action {
        Invoke-LoggedNative -StageName 'mock_collision' -Executable $childPowerShell -Arguments @(
            '-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', $mockToolPath,
            '-NativeLogPath', $collisionPath, '-ConsoleLogPath', $collisionPath, '-MarkerPath', $collisionMarker, '-ExitCode', '0'
        ) -ConsoleLogPath $collisionPath -NativeLogPath $collisionPath -ExecutionLog $logExecution
    }
    if (Test-Path -LiteralPath $collisionMarker) {
        throw '控制台/原生日志同路径时仍启动了模拟工具。'
    }
    $logBindingTestCount++

    $preexistingNative = Join-Path $simulationRoot 'mock_preexisting.log'
    $preexistingConsole = Join-Path $simulationRoot 'mock_preexisting.console.log'
    $preexistingMarker = Join-Path $simulationRoot 'mock_preexisting.marker'
    [System.IO.File]::WriteAllText($preexistingNative, 'preserve-native-sentinel', [System.Text.UTF8Encoding]::new($false))
    Assert-GuardThrows -CaseName '拒绝覆盖预先存在的原生日志目标' -Action {
        Invoke-LoggedNative -StageName 'mock_preexisting' -Executable $childPowerShell -Arguments @(
            '-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', $mockToolPath,
            '-NativeLogPath', $preexistingNative, '-ConsoleLogPath', $preexistingConsole, '-MarkerPath', $preexistingMarker, '-ExitCode', '0'
        ) -ConsoleLogPath $preexistingConsole -NativeLogPath $preexistingNative -ExecutionLog $logExecution
    }
    if ((Get-Content -LiteralPath $preexistingNative -Raw -Encoding utf8) -cne 'preserve-native-sentinel' -or
        (Test-Path -LiteralPath $preexistingMarker)) {
        throw '预先存在的原生日志被覆盖或模拟工具仍被启动。'
    }
    $logBindingTestCount++

    $failureNative = Join-Path $simulationRoot 'mock_failure.log'
    $failureConsole = Join-Path $simulationRoot 'mock_failure.console.log'
    $failureMarker = Join-Path $simulationRoot 'mock_failure.marker'
    Assert-GuardThrows -CaseName '失败阶段仍保存双日志与退出码' -Action {
        Invoke-LoggedNative -StageName 'mock_failure' -Executable $childPowerShell -Arguments @(
            '-NoLogo', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', $mockToolPath,
            '-NativeLogPath', $failureNative, '-ConsoleLogPath', $failureConsole, '-MarkerPath', $failureMarker, '-ExitCode', '7'
        ) -ConsoleLogPath $failureConsole -NativeLogPath $failureNative -ExecutionLog $logExecution
    }
    $failureResultPath = Join-Path $simulationRoot 'stage_mock_failure_result.json'
    $failureResult = Get-Content -LiteralPath $failureResultPath -Raw -Encoding utf8 | ConvertFrom-Json
    if ($failureResult.status -cne 'FAIL' -or $failureResult.exit_code -ne 7 -or
        $failureResult.native_log.sha256 -cne (Get-T63FileSha256 -Path $failureNative -AllowedRoot $simulationRoot) -or
        $failureResult.console_log.sha256 -cne (Get-T63FileSha256 -Path $failureConsole -AllowedRoot $simulationRoot)) {
        throw '失败阶段没有持久绑定原生日志/控制台日志 SHA 与真实退出码。'
    }
    $logBindingTestCount++
}
finally {
    Assert-PathWithin -Path $simulationRoot -AllowedRoot (Split-Path -Parent $RunnerPath)
    Assert-NoReparsePathChain -Path $simulationRoot
    Remove-Item -LiteralPath $simulationRoot -Recurse -Force -ErrorAction Stop
}

Write-Output "PASS process_guard_tests=$testCaseCount native_log_binding_tests=$logBindingTestCount powershell=$($PSVersionTable.PSVersion)"
