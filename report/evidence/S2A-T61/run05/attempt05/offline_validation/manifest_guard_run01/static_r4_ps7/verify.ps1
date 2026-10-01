param([ValidateSet('PS7','PS51')][string]$RunId='PS7')
$ErrorActionPreference='Stop'
$attemptRoot='D:\FPGA_Competition\report\evidence\S2A-T61\run05\attempt05'
$runnerPath=Join-Path $attemptRoot 'run05_runner_attempt05_safe.ps1'
$fixtureRoot=Join-Path $PSScriptRoot ('fault_fixtures_r3_'+$RunId.ToLowerInvariant())
$resultPath=Join-Path $PSScriptRoot ('static_fault_injection_r4_'+$RunId.ToLowerInvariant()+'.json')
if(-not (Test-Path -LiteralPath $runnerPath -PathType Leaf)){throw "runner 缺失：$runnerPath"}
if(Test-Path -LiteralPath $fixtureRoot){throw "静态注入夹具目录已存在，拒绝覆盖：$fixtureRoot"}
New-Item -ItemType Directory -Path $fixtureRoot | Out-Null
$runnerHash=(Get-FileHash -LiteralPath $runnerPath -Algorithm SHA256).Hash.ToLowerInvariant()
$runnerText=[IO.File]::ReadAllText($runnerPath,[Text.Encoding]::UTF8)
$tokens=$null
$parseErrors=$null
$runnerAst=[Management.Automation.Language.Parser]::ParseFile($runnerPath,[ref]$tokens,[ref]$parseErrors)
$tests=[System.Collections.Generic.List[object]]::new()
function Add-TestResult([string]$name,[bool]$passed,[string]$actual,[string]$details){
    $tests.Add([pscustomobject]@{case=$name;expected='PASS';actual=$actual;assertion=$(if($passed){'PASS'}else{'FAIL'});details=$details})
}
$parserPassed=($parseErrors.Count -eq 0)
Add-TestResult 'powershell_current_parser' $parserPassed $(if($parserPassed){'PARSE_PASS'}else{'PARSE_FAIL'}) (($parseErrors | ForEach-Object Message) -join '; ')
if(-not $parserPassed){throw '当前 PowerShell 无法解析 runner'}
$functionNames=@('Assert-NoLogFault','Format-StageFailure','New-StageLauncher','Assert-GlobalPassEvidence')
$functionAsts=@($runnerAst.FindAll({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst] -and $node.Name -in $functionNames},$true))
if($functionAsts.Count -ne $functionNames.Count){throw "runner 函数提取数量异常：$($functionAsts.Count)"}
foreach($functionAst in $functionAsts){Invoke-Expression $functionAst.Extent.Text}
function New-LogSet([string]$name,[bool]$includeNative,[string]$nativeKind='file'){
    $dir=Join-Path $fixtureRoot $name
    New-Item -ItemType Directory -Path $dir | Out-Null
    $native=Join-Path $dir 'xvlog.log'
    $stdout=Join-Path $dir 'xvlog.stdout.txt'
    $stderr=Join-Path $dir 'xvlog.stderr.txt'
    if($includeNative){
        if($nativeKind -eq 'directory'){New-Item -ItemType Directory -Path $native | Out-Null}
        else{[IO.File]::WriteAllText($native,'XVLOG native log'+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))}
    }
    [IO.File]::WriteAllText($stdout,'stdout clean'+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
    [IO.File]::WriteAllText($stderr,'stderr clean'+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
    return [pscustomobject]@{directory=$dir;native=$native;stdout=$stdout;stderr=$stderr;paths=@($native,$stdout,$stderr)}
}
function New-RuntimeLogSet([string]$name){
    $dir=Join-Path $fixtureRoot $name
    New-Item -ItemType Directory -Path $dir | Out-Null
    $native=Join-Path $dir 'xsim.log'
    $stdout=Join-Path $dir 'xsim.stdout.txt'
    $stderr=Join-Path $dir 'xsim.stderr.txt'
    foreach($path in @($native,$stdout,$stderr)){[IO.File]::WriteAllText($path,'clean log'+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))}
    return [pscustomobject]@{directory=$dir;native=$native;stdout=$stdout;stderr=$stderr;paths=@($native,$stdout,$stderr)}
}
$normal=New-LogSet 'normal_three_logs' $true
try{
    $normalResult=Assert-NoLogFault -paths $normal.paths -phase 'normal' -stageExitCode 0 -nativeLog $normal.native
    $ok=($normalResult.state -eq 'PASS_SCAN' -and -not $normalResult.native_log_missing -and $normalResult.scanned_paths.Count -eq 3)
    Add-TestResult 'normal_three_regular_readable_logs' $ok $normalResult.state ($normalResult | ConvertTo-Json -Compress -Depth 5)
}catch{Add-TestResult 'normal_three_regular_readable_logs' $false 'REJECTED' $_.Exception.Message}
$missingSuccess=New-LogSet 'missing_native_on_success' $false
$missingSuccessError=''
try{Assert-NoLogFault -paths $missingSuccess.paths -phase 'missing_native_success' -stageExitCode 0 -nativeLog $missingSuccess.native | Out-Null}
catch{$missingSuccessError=$_.Exception.Message}
Add-TestResult 'successful_tool_requires_native_log' ($missingSuccessError -match '日志缺失') $(if($missingSuccessError){'REJECTED'}else{'ACCEPTED'}) $missingSuccessError
$missingFailure=New-LogSet 'missing_native_on_process_failure' $false
$failureCode=-1073741515
$failureResult=$null
$failureError=''
try{$failureResult=Assert-NoLogFault -paths $missingFailure.paths -phase 'failed_process' -stageExitCode $failureCode -nativeLog $missingFailure.native}
catch{$failureError=$_.Exception.Message}
$failureMessage=''
if($null -ne $failureResult){$failureMessage=Format-StageFailure -name 'xvlog' -stageExitCode $failureCode -finalLogScan $failureResult -nativeLog $missingFailure.native -stdout $missingFailure.stdout -stderr $missingFailure.stderr}
$failureOk=($null -ne $failureResult -and $failureResult.state -eq 'FAIL_SCAN_NONZERO_EXIT' -and $failureResult.native_log_missing -and $failureResult.scanned_paths.Count -eq 2 -and $failureMessage.Contains([string]$failureCode) -and $failureMessage.Contains($missingFailure.stdout) -and $failureMessage.Contains($missingFailure.stderr) -and $failureMessage.Contains($missingFailure.native))
Add-TestResult 'nonzero_exit_missing_native_preserves_exit_and_stream_paths' $failureOk $(if($failureOk){'FAILURE_PRESERVED'}else{'INVALID'}) $(if($failureError){$failureError}else{$failureMessage})
$directoryNative=New-LogSet 'directory_at_native_path' $false
New-Item -ItemType Directory -Path $directoryNative.native | Out-Null
$directoryError=''
try{Assert-NoLogFault -paths $directoryNative.paths -phase 'directory_native' -stageExitCode $failureCode -nativeLog $directoryNative.native | Out-Null}
catch{$directoryError=$_.Exception.Message}
Add-TestResult 'nonzero_exit_rejects_directory_native_path' ($directoryError -match '不是普通文件') $(if($directoryError){'REJECTED'}else{'ACCEPTED'}) $directoryError
$missingStdout=New-LogSet 'missing_stdout_on_failure' $false
[IO.File]::Delete($missingStdout.stdout)
$stdoutError=''
try{Assert-NoLogFault -paths $missingStdout.paths -phase 'missing_stdout' -stageExitCode $failureCode -nativeLog $missingStdout.native | Out-Null}
catch{$stdoutError=$_.Exception.Message}
Add-TestResult 'nonzero_exit_still_requires_stdout_and_stderr' ($stdoutError -match '缺失') $(if($stdoutError){'REJECTED'}else{'ACCEPTED'}) $stdoutError
$locked=New-LogSet 'unreadable_exclusive_lock' $true
$lock=$null
$lockedError=''
try{
    $lock=[IO.File]::Open($locked.native,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
    try{Assert-NoLogFault -paths $locked.paths -phase 'locked_native' -stageExitCode 0 -nativeLog $locked.native | Out-Null}
    catch{$lockedError=$_.Exception.Message}
}finally{if($null -ne $lock){$lock.Dispose()}}
Add-TestResult 'unreadable_native_log_rejected' ($lockedError -match '不可读') $(if($lockedError){'REJECTED'}else{'ACCEPTED'}) $lockedError
$tail=New-LogSet 'drain_tail_error' $true
$tailInitial=Assert-NoLogFault -paths $tail.paths -phase 'pre_drain' -stageExitCode 0 -nativeLog $tail.native
[IO.File]::AppendAllText($tail.stdout,'ERROR: injected after drain'+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
$tailError=''
try{Assert-NoLogFault -paths $tail.paths -phase 'post_drain' -stageExitCode 0 -nativeLog $tail.native | Out-Null}
catch{$tailError=$_.Exception.Message}
Add-TestResult 'post_drain_tail_error_rejected' ($null -ne $tailInitial -and $tailError -match '最终日志复扫发现错误') $(if($tailError){'REJECTED'}else{'ACCEPTED'}) $tailError
$nonzeroMarker=New-LogSet 'nonzero_with_error_marker' $false
[IO.File]::WriteAllText($nonzeroMarker.stdout,'ERROR: loader initialization failed'+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
$markerResult=Assert-NoLogFault -paths $nonzeroMarker.paths -phase 'nonzero_marker' -stageExitCode $failureCode -nativeLog $nonzeroMarker.native
$markerMessage=Format-StageFailure -name 'xvlog' -stageExitCode $failureCode -finalLogScan $markerResult -nativeLog $nonzeroMarker.native -stdout $nonzeroMarker.stdout -stderr $nonzeroMarker.stderr
$markerOk=($markerResult.faults.Count -eq 1 -and $markerMessage.Contains([string]$failureCode) -and $markerMessage.Contains('ERROR:'))
Add-TestResult 'nonzero_exit_scans_and_reports_error_marker' $markerOk $(if($markerOk){'FAILURE_AND_LOG_MARKER_PRESERVED'}else{'INVALID'}) $markerMessage
$planPath=Join-Path $attemptRoot 'run_plan.json'
$plan=Get-Content -LiteralPath $planPath -Raw -Encoding UTF8 | ConvertFrom-Json
$expectedPassLine=[string]$plan.pass_definition.pass_line
$expectedFinishTimeNs=[long]$plan.pass_definition.finish_time_ns
if($expectedFinishTimeNs -ne [long]2134685240){throw "run_plan finish_time_ns 冻结值错误：$expectedFinishTimeNs"}
$runtimePositive=New-RuntimeLogSet 'global_single_distributed_markers'
[IO.File]::WriteAllText($runtimePositive.stdout,$expectedPassLine+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($runtimePositive.stderr,('$finish called at time : '+$expectedFinishTimeNs+' ns')+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
$runtimePositiveResult=$null
$runtimePositiveError=''
try{$runtimePositiveResult=Assert-GlobalPassEvidence -paths $runtimePositive.paths -expectedPassLine $expectedPassLine -expectedFinishTimeNs $expectedFinishTimeNs}
catch{$runtimePositiveError=$_.Exception.Message}
$runtimePositiveOk=($null -ne $runtimePositiveResult -and $runtimePositiveResult.state -eq 'PASS_GLOBAL_EVIDENCE' -and $runtimePositiveResult.pass_marker_count -eq 1 -and $runtimePositiveResult.finish_marker_count -eq 1 -and $runtimePositiveResult.finish_time_ns -eq $expectedFinishTimeNs -and $runtimePositiveResult.pass_marker_path -eq $runtimePositive.stdout -and $runtimePositiveResult.finish_marker_path -eq $runtimePositive.stderr)
Add-TestResult 'global_single_pass_and_frozen_finish_distributed_across_logs' $runtimePositiveOk $(if($runtimePositiveOk){'GLOBAL_PASS'}else{'REJECTED'}) $(if($runtimePositiveError){$runtimePositiveError}else{$runtimePositiveResult | ConvertTo-Json -Compress -Depth 5})
$runtimeDuplicate=New-RuntimeLogSet 'global_duplicate_pass_across_logs'
[IO.File]::WriteAllText($runtimeDuplicate.native,$expectedPassLine+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($runtimeDuplicate.stdout,$expectedPassLine+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($runtimeDuplicate.stderr,('$finish called at time : '+$expectedFinishTimeNs+' ns')+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
$duplicateError=''
try{Assert-GlobalPassEvidence -paths $runtimeDuplicate.paths -expectedPassLine $expectedPassLine -expectedFinishTimeNs $expectedFinishTimeNs | Out-Null}
catch{$duplicateError=$_.Exception.Message}
Add-TestResult 'global_duplicate_pass_across_logs_rejected' ($duplicateError -match 'PASS 标记数量不是 1') $(if($duplicateError){'REJECTED'}else{'ACCEPTED'}) $duplicateError
$runtimeWrongTime=New-RuntimeLogSet 'global_finish_time_mismatch'
[IO.File]::WriteAllText($runtimeWrongTime.native,$expectedPassLine+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
$wrongFinishTime=$expectedFinishTimeNs-1
[IO.File]::WriteAllText($runtimeWrongTime.stdout,('$finish called at time : '+$wrongFinishTime+' ns')+[Environment]::NewLine,[Text.UTF8Encoding]::new($false))
$wrongTimeError=''
try{Assert-GlobalPassEvidence -paths $runtimeWrongTime.paths -expectedPassLine $expectedPassLine -expectedFinishTimeNs $expectedFinishTimeNs | Out-Null}
catch{$wrongTimeError=$_.Exception.Message}
Add-TestResult 'global_finish_time_mismatch_rejected' ($wrongTimeError -match 'finish_time_ns 与冻结值不匹配') $(if($wrongTimeError){'REJECTED'}else{'ACCEPTED'}) $wrongTimeError
$dummyTool=Join-Path $fixtureRoot 'dummy_tool.cmd'
$dummyWrapper=Join-Path $fixtureRoot 'dummy_stage_launcher.cmd'
$dummyObserved=Join-Path $fixtureRoot 'dummy_observed_args.txt'
$dummyText='@echo off'+[Environment]::NewLine+'> "'+$dummyObserved+'" echo %*'+[Environment]::NewLine+'exit /b 7'+[Environment]::NewLine
[IO.File]::WriteAllText($dummyTool,$dummyText,[Text.Encoding]::ASCII)
$dummyArgs=@('alpha','argument with spaces','D:\FPGA_Competition\offline path\sample.bin')
$hostArguments=New-StageLauncher -launchScript $dummyWrapper -executable $dummyTool -arguments $dummyArgs
$cmd=Join-Path $env:WINDIR 'System32\cmd.exe'
if(-not (Test-Path -LiteralPath $cmd -PathType Leaf)){throw "cmd.exe 缺失：$cmd"}
$si=New-Object System.Diagnostics.ProcessStartInfo
$si.FileName=$cmd
$si.Arguments=$hostArguments
$si.WorkingDirectory=$fixtureRoot
$si.UseShellExecute=$false
$si.CreateNoWindow=$true
$si.RedirectStandardOutput=$true
$si.RedirectStandardError=$true
$process=New-Object System.Diagnostics.Process
$process.StartInfo=$si
if(-not $process.Start()){throw '仅测试用 cmd.exe 未启动'}
$dummyStdout=$process.StandardOutput.ReadToEnd()
$dummyStderr=$process.StandardError.ReadToEnd()
$process.WaitForExit()
$dummyExit=$process.ExitCode
$observed=Get-Content -LiteralPath $dummyObserved -Raw -Encoding UTF8
$dummyOk=($dummyExit -eq 7 -and $observed.Contains('alpha') -and $observed.Contains('argument with spaces') -and $observed.Contains('offline path'))
Add-TestResult 'cmd_batch_argument_and_exit_code_transport' $dummyOk $(if($dummyOk){'PASS'}else{'FAIL'}) ([ordered]@{exit_code=$dummyExit;host_arguments=$hostArguments;observed_args=$observed;stdout=$dummyStdout;stderr=$dummyStderr} | ConvertTo-Json -Compress -Depth 4)
$ps51=Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe'
$ps51Exit=$null
$ps51Output=''
if(Test-Path -LiteralPath $ps51 -PathType Leaf){
    $parserSource='$parsePath='+[char]39+$runnerPath+[char]39+';$tk=$null;$er=$null;[Management.Automation.Language.Parser]::ParseFile($parsePath,[ref]$tk,[ref]$er)|Out-Null;if($er.Count){$er|ForEach-Object Message;exit 31};Write-Output ''PARSE_PASS'';exit 0'
    $encoded=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($parserSource))
    $ps51Output=(& $ps51 -NoLogo -NoProfile -NonInteractive -EncodedCommand $encoded 2>&1 | Out-String).Trim()
    $ps51Exit=$LASTEXITCODE
}
$ps51Ok=($ps51Exit -eq 0 -and $ps51Output -match 'PARSE_PASS')
Add-TestResult 'windows_powershell_51_parser' $ps51Ok $(if($ps51Ok){'PARSE_PASS'}else{'PARSE_FAIL'}) ([ordered]@{executable=$ps51;exit_code=$ps51Exit;output=$ps51Output} | ConvertTo-Json -Compress -Depth 4)
$failed=@($tests | Where-Object {$_.assertion -ne 'PASS'})
$status=$(if($failed.Count -eq 0){'STATIC_VALIDATION_PASS'}else{'STATIC_VALIDATION_FAIL'})
$start=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8))
$report=[ordered]@{
    schema='S2A-T61-attempt-static-fault-injection-v3'
    task_id='S2A-T61'
    run_id='run05'
    attempt='attempt05'
    status=$status
    runner_path=$runnerPath
    runner_sha256=$runnerHash
    powershell_edition=[string]$PSVersionTable.PSEdition
    powershell_version=[string]$PSVersionTable.PSVersion
    test_count=$tests.Count
    tests=@($tests.ToArray())
    execution_run_id=$RunId
    test_fixture_root=$fixtureRoot
    toolchain_invocations=@()
    mcp_used=$false
    protected_process_control_used=$false
    runner_invoked=$false
    simulation_status='NO_SIMULATION'
    started_at_utc8=$start.ToString('yyyy-MM-dd HH:mm:ss zzz')
    ended_at_utc8=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss zzz')
}
[IO.File]::WriteAllText($resultPath,($report | ConvertTo-Json -Depth 20),[Text.UTF8Encoding]::new($false))
if($failed.Count -gt 0){[Console]::Error.WriteLine("STATIC_VALIDATION_FAIL failed=$($failed.Count)");exit 1}
[Console]::WriteLine("STATIC_VALIDATION_PASS tests=$($tests.Count) simulation=NO_SIMULATION")
exit 0