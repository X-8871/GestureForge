$ErrorActionPreference = "Stop"
$RunRoot = [IO.Path]::GetFullPath("D:\FPGA_Competition\report\evidence\S2A-T57\run08")
$ExpectedRunRoot = "D:\FPGA_Competition\report\evidence\S2A-T57\run08"
$WrapperPath = [IO.Path]::GetFullPath("D:\FPGA_Competition\verification\run_s2a_t57_project_sim.ps1")
$XprPath = [IO.Path]::GetFullPath("D:\FPGA_Competition\vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr")
$UnitRoot = Join-Path $RunRoot "_r8_wrapper_gate_unit"
$ResultsPath = Join-Path $RunRoot "r8_wrapper_gate_test_results.json"

if (-not [string]::Equals($RunRoot, $ExpectedRunRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw "R8 合成夹具目录不等于固定 run08 路径：$RunRoot"
}
if (-not (Test-Path -LiteralPath $RunRoot -PathType Container)) {
    throw "run08 目录不存在：$RunRoot"
}
$runItem = Get-Item -LiteralPath $RunRoot -ErrorAction Stop
if (($runItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
    throw "run08 是 reparse point：$RunRoot"
}
if (Test-Path -LiteralPath $UnitRoot) {
    throw "拒绝复用已有 R8 合成夹具目录：$UnitRoot"
}
if (Test-Path -LiteralPath $ResultsPath) {
    throw "拒绝覆盖已有 R8 合成夹具结果：$ResultsPath"
}

$tokens = $null
$parseErrors = $null
$wrapperAst = [System.Management.Automation.Language.Parser]::ParseFile($WrapperPath, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count -gt 0) {
    throw "PowerShell wrapper 语法错误：$($parseErrors[0].Message)"
}
foreach ($functionName in @("Set-T57JsonField", "Get-T57TranscriptEvidence", "Complete-T57StageStatus")) {
    $node = $wrapperAst.Find({ param($item) $item -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $item.Name -ceq $functionName }, $true)
    if ($null -eq $node) {
        throw "wrapper 缺少终态门函数：$functionName"
    }
    Invoke-Expression $node.Extent.Text
}

function Write-T57TestText {
    param([string]$Path, [string]$Text)
    [IO.File]::WriteAllText($Path, $Text, [Text.UTF8Encoding]::new($false))
}

function New-T57SyntheticCase {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][bool]$CompleteConsole,
        [Parameter(Mandatory = $true)][AllowNull()][object]$VivadoExitCode,
        [Parameter()][switch]$OmitCompileLog,
        [Parameter()][switch]$ShortSimulateLog
    )
    $casePath = Join-Path $UnitRoot $Name
    [IO.Directory]::CreateDirectory($casePath) | Out-Null
    $customTcl = Join-Path $casePath "xsim_run.tcl"
    Write-T57TestText -Path $customTcl -Text "run all`nquit`n"
    $customTclToken = [IO.Path]::GetFullPath($customTcl).Replace([char]92, [char]47)
    $snapshot = "tb_s2a_conv_layer35_row21_all_channels_behav"
    $snapshotKey = "Behavioral:sim_s2a_t57_row21:Functional:tb_s2a_conv_layer35_row21_all_channels"
    $signature = "$snapshot -key {$snapshotKey} -tclbatch $customTclToken -log simulate.log"
    $xprHash = (Get-FileHash -LiteralPath $XprPath -Algorithm SHA256).Hash.ToLowerInvariant()
    $stage = [ordered]@{
        schema = "GestureForge-S2A-T57-isolated-simulation-status-v4"
        status = "RUNNING"
        simset = "sim_s2a_t57_row21"
        top = "tb_s2a_conv_layer35_row21_all_channels"
        compile_exit_code = 0
        elaboration_exit_code = 0
        simulate_step_tcl_code = $null
        source_project_xpr_sha256 = $xprHash
        custom_tcl_path = [IO.Path]::GetFullPath($customTcl)
        simulate_command_signature = $signature
    }
    Write-T57TestText -Path (Join-Path $casePath "stage_status.json") -Text ((ConvertTo-Json -InputObject $stage -Depth 8) + "`n")
    if (-not $OmitCompileLog) {
        Write-T57TestText -Path (Join-Path $casePath "compile.log") -Text "synthetic compile complete`n"
    }
    Write-T57TestText -Path (Join-Path $casePath "elaborate.log") -Text "Built simulation snapshot tb_s2a_conv_layer35_row21_all_channels_behav`n"
    foreach ($name in @(
        "elaborate.before_compile.bat", "elaborate.after_compile.bat", "elaborate.after_elaborate.bat",
        "simulate.before_compile.bat", "simulate.after_compile.bat", "simulate.after_elaborate.bat"
    )) {
        Write-T57TestText -Path (Join-Path $casePath $name) -Text "synthetic wrapper batch evidence`n"
    }
    Write-T57TestText -Path (Join-Path $casePath "xsim_run.tcl") -Text "run all`nquit`n"
    $console = [Collections.Generic.List[string]]::new()
    $console.Add("T57_CUSTOM_TCL_SENTINEL=run08")
    if ($CompleteConsole) {
        for ($value = 26; $value -le 6656; $value += 26) {
            $console.Add("PROGRESS T57 outputs=$value/6656")
        }
        $console.Add("PASS T57 outputs=6656")
        $console.Add('$finish called at time : 2971541060 ns')
    }
    else {
        $console.Add("PROGRESS T57 outputs=26/6656")
    }
    Write-T57TestText -Path (Join-Path $casePath "vivado_batch_console.log") -Text (($console -join "`n") + "`n")
    if ($ShortSimulateLog) {
        [IO.File]::WriteAllBytes((Join-Path $casePath "simulate.log"), [Text.Encoding]::ASCII.GetBytes("Short xsim transcript 25B"))
    }
    $rawStream = [IO.File]::Open((Join-Path $casePath "observed_raw.bin"), [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $rawStream.SetLength(26624) } finally { $rawStream.Dispose() }
    $int8Stream = [IO.File]::Open((Join-Path $casePath "observed_output.bin"), [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    try { $int8Stream.SetLength(6656) } finally { $int8Stream.Dispose() }
    return $casePath
}

[IO.Directory]::CreateDirectory($UnitRoot) | Out-Null
$xprHash = (Get-FileHash -LiteralPath $XprPath -Algorithm SHA256).Hash.ToLowerInvariant()
$caseResults = [Collections.Generic.List[object]]::new()

$passPath = New-T57SyntheticCase -Name "pass_console_fallback" -CompleteConsole $true -VivadoExitCode 0 -ShortSimulateLog
$passResult = Complete-T57StageStatus -RunDirectory $passPath -XsimTclPath (Join-Path $passPath "xsim_run.tcl") -VivadoExitCode 0 -ExpectedXprSha256 $xprHash -XprUnchanged $true -RemainingProcessCount 0 -CleanupVerified $true -RunFailure ""
$passStage = Get-Content -LiteralPath (Join-Path $passPath "stage_status.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$passOk = ($passResult.exit_code -eq 0 -and $passResult.finalized -and $passStage.status -ceq "PASS" -and
    $passStage.simulate_log_source -ceq "vivado_batch_console.log" -and $passStage.simulate_log_complete -eq $true -and
    $passStage.custom_tcl_executed -eq $true -and $null -eq $passStage.xsim_exit_code -and
    $passStage.xsim_exit_code_captured -eq $false -and $passStage.vivado_process_exit_code -eq 0 -and
    $passResult.stage_status_sha256 -ceq (Get-FileHash -LiteralPath (Join-Path $passPath "stage_status.json") -Algorithm SHA256).Hash.ToLowerInvariant())
if (-not $passOk) { throw "合成通过态或 25B simulate.log -> Vivado console 回退测试失败：$($passResult.failure)" }
$caseResults.Add([ordered]@{case="pass_console_fallback";passed=$true;status=$passStage.status;transcript_source=$passStage.simulate_log_source;xsim_exit_code=$passStage.xsim_exit_code;xsim_exit_code_captured=$passStage.xsim_exit_code_captured})

$incompletePath = New-T57SyntheticCase -Name "incomplete_running" -CompleteConsole $false -VivadoExitCode 0 -ShortSimulateLog
$incompleteResult = Complete-T57StageStatus -RunDirectory $incompletePath -XsimTclPath (Join-Path $incompletePath "xsim_run.tcl") -VivadoExitCode 0 -ExpectedXprSha256 $xprHash -XprUnchanged $true -RemainingProcessCount 0 -CleanupVerified $true -RunFailure ""
$incompleteStage = Get-Content -LiteralPath (Join-Path $incompletePath "stage_status.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($incompleteResult.exit_code -ne 1 -or -not $incompleteResult.finalized -or $incompleteStage.status -cne "FAIL" -or $incompleteStage.simulate_log_complete -ne $false) {
    throw "RUNNING + 不完整 transcript 没有 fail-closed：$($incompleteResult.failure)"
}
$caseResults.Add([ordered]@{case="incomplete_running";passed=$true;status=$incompleteStage.status;exit_code=$incompleteResult.exit_code})

$badVivadoPath = New-T57SyntheticCase -Name "vivado_nonzero" -CompleteConsole $true -VivadoExitCode 1 -ShortSimulateLog
$badVivadoResult = Complete-T57StageStatus -RunDirectory $badVivadoPath -XsimTclPath (Join-Path $badVivadoPath "xsim_run.tcl") -VivadoExitCode 1 -ExpectedXprSha256 $xprHash -XprUnchanged $true -RemainingProcessCount 0 -CleanupVerified $true -RunFailure ""
$badVivadoStage = Get-Content -LiteralPath (Join-Path $badVivadoPath "stage_status.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($badVivadoResult.exit_code -ne 1 -or $badVivadoStage.status -cne "FAIL" -or $badVivadoStage.vivado_process_exit_code -ne 1 -or $null -ne $badVivadoStage.xsim_exit_code) {
    throw "Vivado 非零退出码未 fail-closed 或 XSim 退出码被伪造"
}
$caseResults.Add([ordered]@{case="vivado_nonzero";passed=$true;status=$badVivadoStage.status;vivado_process_exit_code=$badVivadoStage.vivado_process_exit_code;xsim_exit_code=$badVivadoStage.xsim_exit_code})

$missingLogPath = New-T57SyntheticCase -Name "missing_compile_log" -CompleteConsole $true -VivadoExitCode 0 -OmitCompileLog -ShortSimulateLog
$missingLogResult = Complete-T57StageStatus -RunDirectory $missingLogPath -XsimTclPath (Join-Path $missingLogPath "xsim_run.tcl") -VivadoExitCode 0 -ExpectedXprSha256 $xprHash -XprUnchanged $true -RemainingProcessCount 0 -CleanupVerified $true -RunFailure ""
$missingLogStage = Get-Content -LiteralPath (Join-Path $missingLogPath "stage_status.json") -Raw -Encoding UTF8 | ConvertFrom-Json
if ($missingLogResult.exit_code -ne 1 -or $missingLogStage.status -cne "FAIL" -or $missingLogStage.failure -notmatch "compile.log") {
    throw "缺失必需阶段日志没有 fail-closed"
}
$caseResults.Add([ordered]@{case="missing_compile_log";passed=$true;status=$missingLogStage.status;exit_code=$missingLogResult.exit_code})

$missingStagePath = Join-Path $UnitRoot "missing_stage_status"
[IO.Directory]::CreateDirectory($missingStagePath) | Out-Null
$missingStageResult = Complete-T57StageStatus -RunDirectory $missingStagePath -XsimTclPath (Join-Path $missingStagePath "xsim_run.tcl") -VivadoExitCode 0 -ExpectedXprSha256 $xprHash -XprUnchanged $true -RemainingProcessCount 0 -CleanupVerified $true -RunFailure ""
if ($missingStageResult.exit_code -ne 1 -or $missingStageResult.status -cne "MISSING" -or $missingStageResult.finalized) {
    throw "缺失 stage_status 没有 fail-closed"
}
$caseResults.Add([ordered]@{case="missing_stage_status";passed=$true;status=$missingStageResult.status;exit_code=$missingStageResult.exit_code})

$summary = [ordered]@{
    schema = "GestureForge-S2A-T57-R8-wrapper-finalization-gate-test-v1"
    status = "PASS_STATIC_SYNTHETIC_FIXTURES"
    simulator_started = $false
    source_wrapper = $WrapperPath
    source_wrapper_sha256 = (Get-FileHash -LiteralPath $WrapperPath -Algorithm SHA256).Hash.ToLowerInvariant()
    previous_test_attempt = "首轮夹具发现 File.Replace 不能使用空 backup path；已修复，原部分合成夹具保留在 run08\\_r7_wrapper_gate_unit。"
    cases = $caseResults.ToArray()
}
$summaryJson = ConvertTo-Json -InputObject $summary -Depth 8
[IO.File]::WriteAllText($ResultsPath, $summaryJson + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
Write-Output "R8_WRAPPER_FINALIZATION_GATE_TEST=PASS cases=$($caseResults.Count)"
