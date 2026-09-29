$ErrorActionPreference = "Stop"
$root = "D:\FPGA_Competition"
$runRoot = Join-Path $root "report\evidence\S2A-T57\run09\attempt02"
$wrapperPath = Join-Path $root "verification\run_s2a_t57_project_sim.ps1"
$preparePath = Join-Path $runRoot "prepare_summary.json"
$resultPath = Join-Path $runRoot "r9_prelaunch_source_hash_gate_test.json"
if (-not (Test-Path -LiteralPath $runRoot -PathType Container) -or
    (Test-Path -LiteralPath $resultPath)) { throw "R9 source gate test path unavailable or already exists" }
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($wrapperPath, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw "wrapper parse failed: $($parseErrors[0].Message)" }
foreach ($functionName in @("Get-T57ProcessSnapshot", "Get-T57VerifiedDirectoryChain", "Get-T57Sha256", "Assert-T57BoundFile")) {
    $node = $ast.Find({ param($item) $item -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $item.Name -ceq $functionName }, $true)
    if ($null -eq $node) { throw "wrapper missing source gate function: $functionName" }
    Invoke-Expression $node.Extent.Text
}
$wrapperText = [IO.File]::ReadAllText($wrapperPath, [Text.Encoding]::UTF8)
$gateIndex = $wrapperText.IndexOf("`$StartupBindings = Assert-T57StartupSourceBindings -RunDirectory `$RunDirectory", [StringComparison]::Ordinal)
$launchIndex = $wrapperText.IndexOf("& `$VivadoPath @tclArgs", [StringComparison]::Ordinal)
if ($gateIndex -lt 0 -or $launchIndex -lt 0 -or $gateIndex -ge $launchIndex) {
    throw "prelaunch source gate is not textually ordered before Vivado invocation"
}
$summary = [IO.File]::ReadAllText($preparePath, [Text.Encoding]::UTF8) | ConvertFrom-Json
$processNames = @(Get-T57ProcessSnapshot)
if ($processNames.Count -ne 0) { throw "test requires zero Vivado/XSim processes before negative cases" }
$cases = [Collections.Generic.List[object]]::new()
foreach ($relative in @("src/int8_conv_tap_geometry.sv", "sim/tb_s2a_conv_layer35_row21_all_channels.sv")) {
    $record = $summary.bindings.T57_source_bindings.PSObject.Properties[$relative].Value
    if ($null -eq $record) { throw "prepare summary does not bind $relative" }
    $badHash = ([string]$record.sha256).ToLowerInvariant()
    $replacement = if ($badHash.Substring(0,1) -ceq "0") { "1" } else { "0" }
    $badHash = $replacement + $badHash.Substring(1)
    $tampered = [pscustomobject]@{ path = $record.path; bytes = [int64]$record.bytes; sha256 = $badHash }
    $before = @(Get-T57ProcessSnapshot).Count
    $rejected = $false
    try { $null = Assert-T57BoundFile -ExpectedPath $record.path -Record $tampered -Label "synthetic $relative" }
    catch { $rejected = $true }
    $after = @(Get-T57ProcessSnapshot).Count
    if (-not $rejected -or $before -ne 0 -or $after -ne 0) {
        throw "tampered source hash was not rejected before Vivado launch: $relative"
    }
    $cases.Add([ordered]@{ source = $relative; tampered_sha_rejected = $true; before_process_count = $before; after_process_count = $after })
}
$result = [ordered]@{
    schema = "GestureForge-S2A-T57-R9-prelaunch-source-hash-gate-test-v1"
    status = "PASS_STATIC_SYNTHETIC_FIXTURES"
    simulator_started = $false
    gate_precedes_vivado_call = $true
    test_scope = "Invoked the exact wrapper bound-file validator used by Assert-T57StartupSourceBindings with in-memory mutated design and TB SHA records."
    cases = $cases.ToArray()
}
$json = ConvertTo-Json -InputObject $result -Depth 8
$bytes = [Text.UTF8Encoding]::new($false).GetBytes($json + [Environment]::NewLine)
$stream = [IO.File]::Open($resultPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
try { $stream.Write($bytes, 0, $bytes.Length); $stream.Flush($true) } finally { $stream.Dispose() }
Write-Output "R9_PRELAUNCH_SOURCE_HASH_GATE=PASS cases=$($cases.Count) simulator_started=false"