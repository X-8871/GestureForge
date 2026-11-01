param(
    [Parameter(Mandatory = $true)][string]$RunnerPath,
    [Parameter(Mandatory = $true)][string]$RunRoot
)

$ErrorActionPreference = "Stop"
$expectedRunRoot = [IO.Path]::GetFullPath("D:\FPGA_Competition\report\evidence\S2A-T57\run09\attempt03")
$runRootFull = [IO.Path]::GetFullPath($RunRoot)
if (-not [string]::Equals($runRootFull, $expectedRunRoot, [StringComparison]::OrdinalIgnoreCase)) {
    throw "回归验证根目录不等于固定 attempt03：$runRootFull"
}
$runnerFull = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $RunnerPath).Path)
$unitRoot = Join-Path $runRootFull "wrapper_finalization_regression_unit"
if (Test-Path -LiteralPath $unitRoot) {
    throw "回归验证隔离目录已经存在，拒绝覆盖：$unitRoot"
}

$tokens = $null
$parseErrors = $null
$runnerAst = [System.Management.Automation.Language.Parser]::ParseFile($runnerFull, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count -ne 0) {
    throw "PowerShell runner 语法解析失败：$($parseErrors -join '; ')"
}
$wantedFunctions = @("Set-T57JsonField", "Get-T57TranscriptEvidence", "Complete-T57StageStatus")
$allFunctions = @($runnerAst.FindAll({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $true))
$functionText = [Collections.Generic.List[string]]::new()
foreach ($name in $wantedFunctions) {
    $matches = @($allFunctions | Where-Object { $_.Name -ceq $name })
    if ($matches.Count -ne 1) {
        throw "预期函数必须唯一出现：$name count=$($matches.Count)"
    }
    $functionText.Add($matches[0].Extent.Text)
}
Invoke-Expression ($functionText -join [Environment]::NewLine)

$transcriptLines = [Collections.Generic.List[string]]::new()
$transcriptLines.Add('# puts "T57_CUSTOM_TCL_SENTINEL=run09_attempt03"')
$transcriptLines.Add("T57_CUSTOM_TCL_SENTINEL=run09_attempt03")
for ($value = 26; $value -le 6656; $value += 26) {
    $transcriptLines.Add("PROGRESS T57 outputs=$value/6656")
}
$transcriptLines.Add("PASS T57 outputs=6656 raw=6656 int8=6656")
$transcriptLines.Add('$finish called at time : 2971541060 ns')
$syntheticTranscript = $transcriptLines -join [Environment]::NewLine
$transcriptFacts = Get-T57TranscriptEvidence -Text $syntheticTranscript
$commentOnlyFacts = Get-T57TranscriptEvidence -Text '# puts "T57_CUSTOM_TCL_SENTINEL=run09_attempt03"'
if ($transcriptFacts.sentinel_count -ne 1 -or
    $transcriptFacts.pass_line_count -ne 1 -or
    $transcriptFacts.progress_checkpoint_count -ne 256 -or
    -not $transcriptFacts.progress_matches_expected -or
    $transcriptFacts.finish_time_ns -ne 2971541060 -or
    -not $transcriptFacts.complete -or
    $commentOnlyFacts.sentinel_count -ne 0 -or
    $commentOnlyFacts.complete) {
    throw "锚定 transcript parser 的注释/真实标记回归失败"
}

[IO.Directory]::CreateDirectory($unitRoot) | Out-Null
$utf8 = [Text.UTF8Encoding]::new($false)
$xsimTclPath = Join-Path $unitRoot "xsim_run.tcl"
$manifestPath = Join-Path $unitRoot "compile_source_manifest.tsv"
$consolePath = Join-Path $unitRoot "vivado_batch_console.log"
$statusPath = Join-Path $unitRoot "stage_status.json"
[IO.File]::WriteAllText($xsimTclPath, "run all`nquit`n", $utf8)
[IO.File]::WriteAllText($manifestPath, "synthetic manifest`n", $utf8)
[IO.File]::WriteAllText($consolePath, $syntheticTranscript + [Environment]::NewLine, $utf8)
[IO.File]::WriteAllText((Join-Path $unitRoot "compile.log"), "synthetic compile complete`n", $utf8)
[IO.File]::WriteAllText((Join-Path $unitRoot "elaborate.log"), "Built simulation snapshot tb_s2a_conv_layer35_row21_all_channels_behav`n", $utf8)
foreach ($name in @(
        "elaborate.before_compile.bat", "elaborate.after_compile.bat", "elaborate.after_elaborate.bat",
        "simulate.before_compile.bat", "simulate.after_compile.bat", "simulate.after_elaborate.bat")) {
    [IO.File]::WriteAllText((Join-Path $unitRoot $name), "synthetic batch evidence`n", $utf8)
}
[IO.File]::WriteAllBytes((Join-Path $unitRoot "observed_raw.bin"), [byte[]]::new(26624))
[IO.File]::WriteAllBytes((Join-Path $unitRoot "observed_output.bin"), [byte[]]::new(6656))
$xprSha = "a" * 64
$manifestSha = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
$xsimTclFull = [IO.Path]::GetFullPath($xsimTclPath)
$normalizedBatchPath = $xsimTclFull.Replace([char]92, [char]47)
$expectedSnapshot = "tb_s2a_conv_layer35_row21_all_channels_behav"
$expectedSnapshotKey = "Behavioral:sim_s2a_t57_row21:Functional:tb_s2a_conv_layer35_row21_all_channels"
$stage = [ordered]@{
    schema = "GestureForge-S2A-T57-isolated-simulation-status-v5"
    status = "SIMULATION_FLOW_RUNNING"
    data_verification_status = "DATA_VERIFICATION_PENDING"
    data_verification_report = $null
    compile_exit_code = 0
    elaboration_exit_code = 0
    simulate_step_tcl_code = $null
    source_project_xpr_sha256 = $xprSha
    compile_source_manifest_path = [IO.Path]::GetFullPath($manifestPath)
    compile_source_manifest_sha256 = $manifestSha
    simset = "sim_s2a_t57_row21"
    top = "tb_s2a_conv_layer35_row21_all_channels"
    custom_tcl_path = $xsimTclFull
    simulate_command_signature = "xsim $expectedSnapshot -tclbatch `"$normalizedBatchPath`" -key $expectedSnapshotKey"
}
[IO.File]::WriteAllText($statusPath, (ConvertTo-Json -InputObject $stage -Depth 8) + [Environment]::NewLine, $utf8)
$finalization = Complete-T57StageStatus `
    -RunDirectory $unitRoot `
    -XsimTclPath $xsimTclFull `
    -VivadoExitCode 0 `
    -ExpectedXprSha256 $xprSha `
    -ExpectedCompileSourceManifestSha256 $manifestSha `
    -XprUnchanged $true `
    -RemainingProcessCount 0 `
    -CleanupVerified $true `
    -RunFailure ""
if ($finalization.exit_code -ne 0 -or
    $finalization.status -cne "SIMULATION_FLOW_PASS" -or
    -not $finalization.finalized) {
    throw "wrapper finalization 未写 SIMULATION_FLOW_PASS：$($finalization | ConvertTo-Json -Compress)"
}
$writtenStage = [IO.File]::ReadAllText($statusPath, [Text.Encoding]::UTF8) | ConvertFrom-Json -ErrorAction Stop
if ($writtenStage.status -cne "SIMULATION_FLOW_PASS" -or
    $writtenStage.custom_tcl_executed -ne $true -or
    $writtenStage.simulate_log_complete -ne $true -or
    $writtenStage.simulate_log_source -cne "vivado_batch_console.log" -or
    $writtenStage.wrapper_finalization.terminal_status -cne "SIMULATION_FLOW_PASS" -or
    $writtenStage.wrapper_finalization.sentinel_count -ne 1 -or
    $writtenStage.wrapper_finalization.progress_checkpoint_count -ne 256 -or
    $writtenStage.finish_time_ns -ne 2971541060) {
    throw "wrapper finalization 写入后的 JSON 状态与期望不一致"
}

$functionBundle = $functionText -join [Environment]::NewLine
$functionHashProvider = [Security.Cryptography.SHA256]::Create()
try {
    $functionBundleSha256 = [BitConverter]::ToString($functionHashProvider.ComputeHash($utf8.GetBytes($functionBundle))).Replace("-", "").ToLowerInvariant()
}
finally {
    $functionHashProvider.Dispose()
}
$result = [ordered]@{
    schema = "GestureForge-S2A-T57-wrapper-finalization-regression-v1"
    status = "PASS"
    test_scope = "CPU_ONLY_WRAPPER_FINALIZATION_UNIT"
    comment_sentinel_tokens = 1
    standalone_sentinel_lines = 1
    parsed_sentinel_count = $transcriptFacts.sentinel_count
    comment_only_sentinel_count = $commentOnlyFacts.sentinel_count
    progress_checkpoint_count = $transcriptFacts.progress_checkpoint_count
    progress_matches_expected = $transcriptFacts.progress_matches_expected
    finish_time_ns = $transcriptFacts.finish_time_ns
    transcript_source_fallback = "vivado_batch_console.log"
    finalization_exit_code = $finalization.exit_code
    finalization_status = $finalization.status
    written_stage_status = $writtenStage.status
    written_custom_tcl_executed = $writtenStage.custom_tcl_executed
    runner_sha256 = (Get-FileHash -LiteralPath $runnerFull -Algorithm SHA256).Hash.ToLowerInvariant()
    wrapper_sha256 = (Get-FileHash -LiteralPath $MyInvocation.MyCommand.Path -Algorithm SHA256).Hash.ToLowerInvariant()
    extracted_wrapper_functions_sha256 = $functionBundleSha256
    synthetic_console_sha256 = (Get-FileHash -LiteralPath $consolePath -Algorithm SHA256).Hash.ToLowerInvariant()
    finalized_stage_status_sha256 = (Get-FileHash -LiteralPath $statusPath -Algorithm SHA256).Hash.ToLowerInvariant()
    unit_directory = $unitRoot
}
$resultPath = Join-Path $runRootFull "wrapper_finalization_regression.json"
[IO.File]::WriteAllText($resultPath, (ConvertTo-Json -InputObject $result -Depth 8) + [Environment]::NewLine, $utf8)
ConvertTo-Json -InputObject $result -Depth 8
