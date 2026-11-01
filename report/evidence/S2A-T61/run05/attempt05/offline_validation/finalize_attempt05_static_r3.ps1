$ErrorActionPreference='Stop'
$attemptRoot='D:\FPGA_Competition\report\evidence\S2A-T61\run05\attempt05'
$runnerPath=Join-Path $attemptRoot 'run05_runner_attempt05_safe.ps1'
$verifierPath=Join-Path (Join-Path $attemptRoot 'offline_validation') 'verify_attempt05_static_r3.ps1'
$reportPath=Join-Path $attemptRoot 'static_fault_injection_r3.json'
$runDefinitions=@(
    [pscustomobject]@{run_id='PS7';report_path=(Join-Path $attemptRoot 'static_fault_injection_r3_ps7.json')},
    [pscustomobject]@{run_id='PS51';report_path=(Join-Path $attemptRoot 'static_fault_injection_r3_ps51.json')}
)
$runnerHash=(Get-FileHash -LiteralPath $runnerPath -Algorithm SHA256).Hash.ToLowerInvariant()
$verifierHash=(Get-FileHash -LiteralPath $verifierPath -Algorithm SHA256).Hash.ToLowerInvariant()
$reports=@()
$tests=[System.Collections.Generic.List[object]]::new()
foreach($definition in $runDefinitions){
    if(-not(Test-Path -LiteralPath $definition.report_path -PathType Leaf)){throw "静态验证结果缺失：$($definition.report_path)"}
    $report=Get-Content -LiteralPath $definition.report_path -Raw -Encoding UTF8 | ConvertFrom-Json
    if($report.status -ne 'STATIC_VALIDATION_PASS'){throw "静态验证未通过：$($definition.run_id) status=$($report.status)"}
    if($report.simulation_status -ne 'NO_SIMULATION' -or $report.runner_invoked -ne $false -or @($report.toolchain_invocations).Count -ne 0){throw "静态验证报告声明了仿真或工具调用：$($definition.run_id)"}
    if($report.runner_sha256 -cne $runnerHash){throw "静态验证报告绑定了不同 runner：$($definition.run_id)"}
    if($report.test_count -ne @($report.tests).Count -or $report.test_count -lt 14){throw "静态验证测试数量异常：$($definition.run_id)"}
    $reports+=([pscustomobject]@{
        run_id=$definition.run_id
        report_path=$definition.report_path
        report_sha256=(Get-FileHash -LiteralPath $definition.report_path -Algorithm SHA256).Hash.ToLowerInvariant()
        status=$report.status
        powershell_edition=$report.powershell_edition
        powershell_version=$report.powershell_version
        test_count=$report.test_count
        fixture_root=$report.test_fixture_root
    })
    foreach($test in $report.tests){$tests.Add([pscustomobject]@{run_id=$definition.run_id;case=$test.case;assertion=$test.assertion;actual=$test.actual;details=$test.details})}
}
$planPath=Join-Path $attemptRoot 'run_plan.json'
$plan=Get-Content -LiteralPath $planPath -Raw -Encoding UTF8 | ConvertFrom-Json
if([long]$plan.pass_definition.finish_time_ns -ne [long]2134685240){throw 'run_plan finish_time_ns 不等于冻结值 2134685240'}
$failures=@($tests | Where-Object {$_.assertion -ne 'PASS'})
$status=if($failures.Count -eq 0){'STATIC_VALIDATION_PASS'}else{'STATIC_VALIDATION_FAIL'}
$now=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8))
$object=[ordered]@{
    schema='S2A-T61-attempt-static-fault-injection-v3'
    task_id='S2A-T61'
    run_id='run05'
    attempt='attempt05'
    status=$status
    runner_path=$runnerPath
    runner_sha256=$runnerHash
    verifier_path=$verifierPath
    verifier_sha256=$verifierHash
    frozen_finish_time_ns=[long]$plan.pass_definition.finish_time_ns
    pass_marker_count_required=1
    finish_marker_count_required=1
    execution_reports=@($reports)
    test_count=$tests.Count
    tests=@($tests.ToArray())
    toolchain_invocations=@()
    mcp_used=$false
    protected_process_control_used=$false
    runner_invoked=$false
    simulation_status='NO_SIMULATION'
    generated_at_utc8=$now.ToString('yyyy-MM-dd HH:mm:ss zzz')
}
[IO.File]::WriteAllText($reportPath,($object | ConvertTo-Json -Depth 30),[Text.UTF8Encoding]::new($false))
$reportHash=(Get-FileHash -LiteralPath $reportPath -Algorithm SHA256).Hash.ToLowerInvariant()
'STATIC_R3_AGGREGATE='+$status
'STATIC_R3_TESTS='+$tests.Count
'STATIC_R3_REPORT_SHA256='+$reportHash
if($failures.Count -gt 0){exit 1}
exit 0