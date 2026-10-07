[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
# 仅加载函数定义，不执行主流程、真实证据路径或互斥锁。
$runner = Join-Path $PSScriptRoot 'run_s2a_t66_candidate_blackbox.ps1'
$tokens = $null
$errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($runner, [ref]$tokens, [ref]$errors)
if ($errors.Count) { throw 'runner 解析失败。' }
foreach ($node in $ast.EndBlock.Statements) {
    if ($node -is [System.Management.Automation.Language.FunctionDefinitionAst]) {
        . ([scriptblock]::Create($node.Extent.Text))
    }
}
$script:CompileTimeoutMilliseconds = 200
$script:CleanupTimeoutMilliseconds = 3000
$script:DrainTimeoutMilliseconds = 500
$script:ActiveStdoutWriter = $null
$script:ActiveStderrWriter = $null
$script:ActiveStdoutTask = $null
$script:ActiveStderrTask = $null
$script:ActiveOutputMode = $null
$script:ActiveProcess = $null
$tempParent = [System.IO.Path]::GetTempPath()
$tempRoot = Join-Path $tempParent ('t66-offline-' + [guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $tempRoot
$passes = 0
$testProcessIds = [System.Collections.Generic.List[int]]::new()
function Expect-Failure {
    param([scriptblock]$Action, [string]$Expected)
    $failed = $false
    try { & $Action | Out-Null } catch {
        if ($_.Exception.Message -notmatch $Expected) { throw }
        $failed = $true
    }
    if (-not $failed) { throw "应拒绝：$Expected" }
    $script:passes++
}
try {
    foreach ($set in @(@{ prefix='T66_READ_LANE_PASS'; field='lane'; ids=@(0,1,2,3) },
                       @{ prefix='T66_CLASS_STALL'; field='class'; ids=@(0,1,2) })) {
        $valid = @($set.ids | ForEach-Object { "$($set.prefix) $($set.field)=$_ ok" })
        $null = Assert-UniqueMarkerSet ($valid -join "`n") $set.prefix $set.field $set.ids
        $passes++
        foreach ($id in $set.ids) {
            Expect-Failure { Assert-UniqueMarkerSet (($valid + "$($set.prefix) $($set.field)=$id ok") -join "`n") $set.prefix $set.field $set.ids } 'DUPLICATE'
            Expect-Failure { Assert-UniqueMarkerSet (($valid | Where-Object { $_ -notmatch "=$id " }) -join "`n") $set.prefix $set.field $set.ids } 'MISSING'
        }
        foreach ($bad in @('-1','99','x','00','99999999999999999999')) {
            Expect-Failure { Assert-UniqueMarkerSet (($valid + "$($set.prefix) $($set.field)=$bad ok") -join "`n") $set.prefix $set.field $set.ids } 'INVALID'
        }
    }
    $pwsh = (Get-Process -Id $PID).Path
    $watch = [System.Diagnostics.Stopwatch]::StartNew()
    Expect-Failure { Invoke-CapturedChild -FileName $pwsh -Arguments '-NoLogo -NoProfile -Command "Start-Sleep -Seconds 30"' -WorkingDirectory $tempRoot -StdoutPath (Join-Path $tempRoot 'out.txt') -StderrPath (Join-Path $tempRoot 'err.txt') } 'COMPILE_TIMEOUT'
    if ($watch.Elapsed.TotalSeconds -gt 15) { throw '超时清理超出离线总预算。' }
    if ($null -ne $script:ActiveProcess -and -not $script:ActiveProcess.HasExited) { throw '测试子进程残留。' }
    if (-not $script:CleanupDiagnostics.process_exited) { throw '测试子进程退出未确认。' }
    $testProcessIds.Add($script:ActiveProcessId)
    $passes++
    # 测试树终止：子脚本再派生一个睡眠进程，所有 PID 只来自本次脚本。
    $childPidFile = Join-Path $tempRoot 'child_pid.txt'
    $spawnScript = Join-Path $tempRoot 'spawn.ps1'
    Write-NewText $spawnScript ('param($exe,$pidFile)' + "`n" + '$p=Start-Process -FilePath $exe -ArgumentList ''-NoLogo -NoProfile -Command "Start-Sleep -Seconds 30"'' -WindowStyle Hidden -PassThru; [IO.File]::WriteAllText($pidFile,[string]$p.Id); Start-Sleep -Seconds 30')
    $script:CompileTimeoutMilliseconds = 1500
    Expect-Failure { Invoke-CapturedChild -FileName $pwsh -Arguments "-NoLogo -NoProfile -File `"$spawnScript`" `"$pwsh`" `"$childPidFile`"" -WorkingDirectory $tempRoot -StdoutPath (Join-Path $tempRoot 'tree_out.txt') -StderrPath (Join-Path $tempRoot 'tree_err.txt') } 'COMPILE_TIMEOUT'
    $testProcessIds.Add($script:ActiveProcessId)
    if (-not (Test-Path -LiteralPath $childPidFile)) { throw '派生进程测试未实际启动。' }
    $testProcessIds.Add([int][IO.File]::ReadAllText($childPidFile))
    foreach ($processId in $testProcessIds) {
        if (Get-Process -Id $processId -ErrorAction SilentlyContinue) { throw "树终止残留 PID=$processId" }
    }
    $passes++
    # 模拟 lines 模式永不返回 EOF，验证截止后仍明确输出不完整。
    $script:ActiveOutputMode = 'lines'
    $script:ActiveStdoutTask = [System.Threading.Tasks.TaskCompletionSource[string]]::new().Task
    $script:ActiveStderrTask = [System.Threading.Tasks.TaskCompletionSource[string]]::new().Task
    $watch.Restart()
    Stop-ActiveProcessAndCapture
    if ($script:CleanupDiagnostics.output_complete -or $watch.ElapsedMilliseconds -gt 2500) { throw 'lines 输出截止失效。' }
    $passes++
    # 模拟永不完成的输出读取，确认清理截止时间及 incomplete 状态。
    $script:ActiveProcess = $null
    $script:ActiveOutputMode = 'read_all'
    $script:ActiveStdoutTask = [System.Threading.Tasks.TaskCompletionSource[string]]::new().Task
    $script:ActiveStderrTask = [System.Threading.Tasks.TaskCompletionSource[string]]::new().Task
    $watch.Restart()
    Stop-ActiveProcessAndCapture
    if ($script:CleanupDiagnostics.output_complete -or $watch.ElapsedMilliseconds -gt 2500) { throw '读取收尾未按预算失败。' }
    $passes++
    $record = @{ reason='离线注入' }
    $status = @{ failure_record_sha256=$null }
    $r = Save-FailureEvidence (Join-Path $tempRoot 'record.json') (Join-Path $tempRoot 'status.json') $record $status
    if (-not $r.record_saved -or -not $r.status_saved) { throw '正常持久化失败。' }
    $passes++
    # 不存在的父目录及独占创建冲突分别注入 record/status 写失败。
    $r = Save-FailureEvidence (Join-Path $tempRoot 'missing/record.json') (Join-Path $tempRoot 'status2.json') $record @{failure_record_sha256=$null}
    if ($r.record_saved -or -not $r.status_saved -or $r.errors.Count -eq 0) { throw 'record 写失败未暴露。' }
    $passes++
    $r = Save-FailureEvidence (Join-Path $tempRoot 'record2.json') (Join-Path $tempRoot 'status.json') $record @{failure_record_sha256=$null}
    if (-not $r.record_saved -or $r.status_saved -or $r.errors.Count -eq 0) { throw 'status 写失败未暴露。' }
    $passes++
    foreach ($processId in $testProcessIds) {
        if (Get-Process -Id $processId -ErrorAction SilentlyContinue) { throw '最终枚举发现测试子进程仍存活。' }
    }
    Write-Output "PASS_OFFLINE_T66_RUNNER cases=$passes residual_children=0"
} finally {
    if ($null -ne $script:ActiveProcess) { $null = Stop-ProcessTreeBounded $script:ActiveProcess 3000 }
    foreach ($processId in $testProcessIds) {
        $leftover = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($null -ne $leftover) {
            if (-not (Stop-ProcessTreeBounded $leftover 3000)) { throw "测试进程无法回收 PID=$processId" }
        }
    }
    # 仅删除本次独占的临时目录，目标必须仍位于原临时父目录。
    $item = Get-Item -LiteralPath $tempRoot
    if (-not $item.FullName.StartsWith((Get-Item -LiteralPath $tempParent).FullName, [StringComparison]::OrdinalIgnoreCase) -or
        $item.Name -notmatch '^t66-offline-[0-9a-f]{32}$') { throw '临时清理边界不符。' }
    Remove-Item -LiteralPath $item.FullName -Recurse -Force
}
