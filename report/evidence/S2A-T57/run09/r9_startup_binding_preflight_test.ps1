$ErrorActionPreference = "Stop"
$RepositoryRoot = "D:\FPGA_Competition"
$ExpectedRunDirectory = "D:\FPGA_Competition\report\evidence\S2A-T57\run09"
$PrepareSummaryPath = Join-Path $ExpectedRunDirectory "prepare_summary.json"
$FixtureManifestPath = Join-Path $ExpectedRunDirectory "fixture\fixture_manifest.json"
$CompileSourceManifestPath = Join-Path $ExpectedRunDirectory "compile_source_manifest.tsv"
$XsimTclPath = Join-Path $ExpectedRunDirectory "xsim_run.tcl"
$BindingPath = Join-Path $RepositoryRoot "report\evidence\S2A-T57\project_preflight_binding.json"
$XprPath = Join-Path $RepositoryRoot "vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr"
$ExpectedProjectName = "AX7Z020_Gesture"
$ExpectedT57SourceRelPaths = @(
    "src/int8_conv_tap_geometry.sv",
    "src/int8_conv_weight_address.sv",
    "src/int8_mac_accumulator.sv",
    "src/s2a_conv_engine.sv",
    "src/s2a_conv_layer35_channel_probe.sv",
    "sim/tb_s2a_conv_layer35_row21_all_channels.sv",
    "sim/s2a_t57_no_wave.tcl",
    "verification/test_s2a_conv_layer35_row21_all_channels_rtl.py",
    "report/evidence/S2A-T57/run_project_sim.tcl",
    "verification/run_s2a_t57_project_sim.ps1"
)
$ExpectedCompileSourceRelPaths = @(
    "src/int8_conv_tap_geometry.sv",
    "src/int8_conv_weight_address.sv",
    "src/int8_mac_accumulator.sv",
    "src/s2a_conv_engine.sv",
    "src/s2a_conv_layer35_channel_probe.sv",
    "sim/tb_s2a_conv_layer35_row21_all_channels.sv"
)
$WrapperPath = Join-Path $RepositoryRoot "verification\run_s2a_t57_project_sim.ps1"
$ResultPath = Join-Path $ExpectedRunDirectory "r9_startup_binding_preflight_test.json"
if ((Test-Path -LiteralPath $ResultPath) -or
    -not (Test-Path -LiteralPath $ExpectedRunDirectory -PathType Container)) {
    throw "run09 startup binding preflight evidence path unavailable"
}
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($WrapperPath, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw "PowerShell wrapper parse failed: $($parseErrors[0].Message)" }
foreach ($functionName in @("Get-T57Sha256", "Get-T57VerifiedDirectoryChain", "Assert-T57BoundFile", "Assert-T57StartupSourceBindings")) {
    $node = $ast.Find({ param($item) $item -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $item.Name -ceq $functionName }, $true)
    if ($null -eq $node) { throw "wrapper missing startup-binding function: $functionName" }
    Invoke-Expression $node.Extent.Text
}
$result = Assert-T57StartupSourceBindings -RunDirectory $ExpectedRunDirectory
if ($result.source_binding_count -ne 10 -or $result.compile_source_count -ne 6) {
    throw "startup binding counts did not cover all fixed sources"
}
$record = [ordered]@{
    schema = "GestureForge-S2A-T57-R9-startup-binding-preflight-v1"
    status = "PASS_STATIC_BOUND_INPUTS"
    simulator_started = $false
    run_directory = $ExpectedRunDirectory
    source_binding_count = $result.source_binding_count
    compile_source_count = $result.compile_source_count
    prepare_summary_sha256 = $result.prepare_summary_sha256
    fixture_manifest_sha256 = $result.fixture_manifest_sha256
    compile_source_manifest_sha256 = $result.compile_source_manifest_sha256
    python_runner_sha256 = $result.python_runner_sha256
}
$json = ConvertTo-Json -InputObject $record -Depth 6
$bytes = [Text.UTF8Encoding]::new($false).GetBytes($json + [Environment]::NewLine)
$stream = [IO.File]::Open($ResultPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
Write-Output "R9_STARTUP_BINDING_PREFLIGHT=PASS source_count=$($result.source_binding_count) compile_source_count=$($result.compile_source_count)"