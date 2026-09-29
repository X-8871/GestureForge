$ErrorActionPreference = 'Stop'
$root = (Get-Location).Path
$evidence = 'report/evidence/S2A-T57'
$run = Join-Path $evidence 'run08'
$reportPath = Join-Path $run 'r8_static_validation.json'
if (Test-Path -LiteralPath $reportPath) { throw 'static report already exists' }
function Get-Sha256([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
$base = '7b8bad78a456310d2ca797a02e3a5a7f873f9c18'
$head = (git rev-parse HEAD).Trim()
if ($head -cne 'decaef9ceb97befab2ff6d6ba5a72fc822905f58') { throw "unexpected current HEAD $head" }
git merge-base --is-ancestor $base $head
$ancestorExit = $LASTEXITCODE
if ($ancestorExit -ne 0) { throw 'baseline ancestry check failed' }
$prepPath = Join-Path $run 'prepare_summary.json'
$prep = Get-Content -LiteralPath $prepPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($prep.status -cne 'PREPARED_NOT_SIMULATED' -or $prep.baseline_head -cne $base -or $prep.current_head -cne $head) { throw 'prepare status or HEAD mismatch' }
$sourceHashes = [ordered]@{}
foreach ($entry in $prep.bindings.T57_source_hashes.PSObject.Properties) {
    $path = Join-Path $root $entry.Name
    $sha = Get-Sha256 $path
    if ($sha -cne [string]$entry.Value) { throw "source SHA mismatch $($entry.Name)" }
    $sourceHashes[$entry.Name] = $sha
}
$fixtureHashes = [ordered]@{}
foreach ($entry in $prep.fixture.files.PSObject.Properties) {
    $record = $entry.Value
    $path = [string]$record.path
    $item = Get-Item -LiteralPath $path
    $sha = Get-Sha256 $path
    if ($item.Length -ne [int64]$record.bytes -or $sha -cne [string]$record.sha256) { throw "fixture SHA/size mismatch $path" }
    $fixtureHashes[$entry.Name] = [ordered]@{ bytes = [int64]$item.Length; sha256 = $sha }
}
$fixtureManifestPath = Join-Path $run 'fixture\fixture_manifest.json'
$fixtureManifestSha = Get-Sha256 $fixtureManifestPath
if ($fixtureManifestSha -cne [string]$prep.fixture.manifest.sha256) { throw 'fixture manifest SHA mismatch' }
$customTclPath = Join-Path $run 'xsim_run.tcl'
$customTclSha = Get-Sha256 $customTclPath
if ($customTclSha -cne [string]$prep.bindings.xsim_custom_tcl.sha256) { throw 'custom Tcl SHA mismatch' }
$xprPath = 'vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr'
$xprSha = Get-Sha256 $xprPath
$xprBinding = Get-Content -LiteralPath (Join-Path $evidence 'project_preflight_binding.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($xprSha -cne [string]$xprBinding.xpr_sha256_before_run -or $xprSha -cne [string]$prep.project_preflight.target_xpr_sha256) { throw 'XPR preflight binding mismatch' }
$pythonAstFiles = @('verification/test_s2a_conv_layer35_row21_all_channels_rtl.py', (Join-Path $run 'r8_batch_signature_gate_test.py'))
foreach ($path in $pythonAstFiles) {
    & python -B -c "import ast,pathlib,sys; ast.parse(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8-sig'), filename=sys.argv[1])" $path
    if ($LASTEXITCODE -ne 0) { throw "Python AST failed $path" }
}
$powerShellFiles = @('verification/run_s2a_t57_project_sim.ps1', (Join-Path $run 'r8_wrapper_finalization_gate_test_retry01.ps1'), (Join-Path $run 'r8_static_validation.ps1'))
$powerShellTokens = [ordered]@{}
foreach ($path in $powerShellFiles) {
    $tokens = $null; $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path -LiteralPath $path).Path, [ref]$tokens, [ref]$errors) | Out-Null
    if ($errors.Count) { throw "PowerShell parser failed $path $($errors[0])" }
    $powerShellTokens[$path] = $tokens.Count
}
$tclFiles = @('report/evidence/S2A-T57/run_project_sim.tcl', 'sim/s2a_t57_no_wave.tcl', $customTclPath)
foreach ($path in $tclFiles) {
    & python -B -c "import pathlib,sys,tkinter; p=pathlib.Path(sys.argv[1]); text=p.read_text(encoding='utf-8'); assert int(tkinter.Tcl().call('info','complete',text)) == 1" $path
    if ($LASTEXITCODE -ne 0) { throw "Tcl info complete failed $path" }
}
$wrapperResultPath = Join-Path $run 'r8_wrapper_gate_test_results_retry01.json'
$wrapperResult = Get-Content -LiteralPath $wrapperResultPath -Raw -Encoding UTF8 | ConvertFrom-Json
$wrapperLog = Get-Content -LiteralPath (Join-Path $run 'r8_wrapper_gate_test_console_retry01.log') -Raw -Encoding UTF8
if ($wrapperResult.status -cne 'PASS_STATIC_SYNTHETIC_FIXTURES' -or @($wrapperResult.cases).Count -ne 5 -or $wrapperLog -notmatch 'exit_code=0') { throw 'wrapper finalization gate result failed' }
$batchResultPath = Join-Path $run '_r8_batch_signature_gate_unit\r8_batch_signature_gate_results.json'
$batchResult = Get-Content -LiteralPath $batchResultPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($batchResult.status -cne 'PASS_STATIC_SYNTHETIC_FIXTURES' -or @($batchResult.cases).Count -ne 5) { throw 'batch signature gate result failed' }
$prepareLog = Get-Content -LiteralPath (Join-Path $run 'run08_prepare_console.log') -Raw -Encoding UTF8
$verifyLog = Get-Content -LiteralPath (Join-Path $run 'run08_verify_only_expected_fail.log') -Raw -Encoding UTF8
if ($prepareLog -notmatch 'exit_code=0' -or $verifyLog -notmatch 'exit_code=1' -or $verifyLog -notmatch 'stage_status.json') { throw 'prepare/verify log result mismatch' }
$stagePath = Join-Path $run 'stage_status.json'
$finalPath = Join-Path $run 'layer35_row21_all_channels.json'
if ((Test-Path -LiteralPath $stagePath) -or (Test-Path -LiteralPath $finalPath)) { throw 'simulation status/result unexpectedly exists' }
$priorManifestPath = Join-Path $run 'r8_prior_runs_sha256_manifest.json'
$priorManifest = Get-Content -LiteralPath $priorManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$priorManifestSha = Get-Sha256 $priorManifestPath
$evidenceFull = (Resolve-Path -LiteralPath $evidence).Path
$rechecked = [Collections.Generic.List[object]]::new()
foreach ($n in 1..7) {
    $name = 'run{0:D2}' -f $n
    $path = Join-Path $evidence $name
    $dir = Get-Item -LiteralPath $path -Force
    if ($dir.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "old attempt reparse point $name" }
    $items = @(Get-ChildItem -LiteralPath $path -Force -Recurse)
    if (@($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) { throw "old attempt descendant reparse point $name" }
    foreach ($file in @($items | Where-Object { -not $_.PSIsContainer })) {
        $relative = $file.FullName.Substring($evidenceFull.Length).TrimStart([char]92)
        $rechecked.Add([pscustomobject]@{ relative_path = $relative; bytes = [int64]$file.Length; sha256 = (Get-Sha256 $file.FullName) })
    }
}
if ($rechecked.Count -ne [int]$priorManifest.total_files) { throw 'old attempts inventory count changed' }
$mismatches = [Collections.Generic.List[string]]::new()
foreach ($record in $priorManifest.files) {
    $matches = @($rechecked | Where-Object { $_.relative_path -ceq [string]$record.relative_path })
    if ($matches.Count -ne 1 -or [int64]$matches[0].bytes -ne [int64]$record.bytes -or [string]$matches[0].sha256 -cne [string]$record.sha256) { $mismatches.Add([string]$record.relative_path) }
}
if ($mismatches.Count) { throw "old attempts changed after capture: $($mismatches.Count)" }
$processCounts = [ordered]@{}
foreach ($name in @('vivado','xsim','xsimk','xelab','xvlog','xvhdl','vivado_lab','hw_server')) { $processCounts[$name] = @(Get-Process -Name $name -ErrorAction SilentlyContinue).Count }
if (@($processCounts.Values | Where-Object { $_ -ne 0 }).Count) { throw 'Vivado/XSim process detected' }
$r6Root = Join-Path $evidence 'run06'
$r6Stage = Get-Content -LiteralPath (Join-Path $r6Root 'stage_status.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$golden = [IO.File]::ReadAllBytes((Join-Path $r6Root 'fixture\golden.bin'))
$raw = [IO.File]::ReadAllBytes((Join-Path $r6Root 'observed_raw.bin'))
$int8 = [IO.File]::ReadAllBytes((Join-Path $r6Root 'observed_output.bin'))
$rawEqual = $raw.Length -eq 26624
if ($rawEqual) { for ($i = 0; $i -lt $raw.Length; $i++) { if ($raw[$i] -ne $golden[$i]) { $rawEqual = $false; break } } }
$int8Equal = $int8.Length -eq 6656
if ($int8Equal) { for ($i = 0; $i -lt $int8.Length; $i++) { if ($int8[$i] -ne $golden[26624 + $i]) { $int8Equal = $false; break } } }
$environment = Get-Content -LiteralPath (Join-Path $evidence 'environment_preflight.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$report = [ordered]@{
    schema = 'GestureForge-S2A-T57-R8-static-validation-v1'
    task_id = 'S2A-T57-R8'
    status = 'PASS_STATIC_PREPARED_NOT_SIMULATED'
    simulation_started = $false
    generated_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    baseline_head = $base
    current_head_at_generation = $head
    current_head_at_validation = (git rev-parse HEAD).Trim()
    baseline_is_ancestor = $true
    source_hashes = $sourceHashes
    prepare_summary = [ordered]@{ path = (Resolve-Path -LiteralPath $prepPath).Path; sha256 = (Get-Sha256 $prepPath); status = $prep.status }
    fixture = [ordered]@{ manifest_path = (Resolve-Path -LiteralPath $fixtureManifestPath).Path; manifest_sha256 = $fixtureManifestSha; custom_tcl_path = (Resolve-Path -LiteralPath $customTclPath).Path; custom_tcl_sha256 = $customTclSha; files = $fixtureHashes }
    commands = [ordered]@{
        prepare_only = [ordered]@{ command = 'python -B verification/test_s2a_conv_layer35_row21_all_channels_rtl.py --prepare-only'; exit_code = 0; result = 'PREPARED_NOT_SIMULATED' }
        verify_only = [ordered]@{ command = 'python -B verification/test_s2a_conv_layer35_row21_all_channels_rtl.py --verify-only'; exit_code = 1; expected_fail_closed = $true; reason = 'stage_status.json absent; final report absent' }
    }
    static_parsers = [ordered]@{ python_ast = 'PASS'; python_ast_files = $pythonAstFiles; powershell = 'PASS'; powershell_files = $powerShellTokens; tcl_info_complete = 'PASS'; tcl_files = $tclFiles }
    synthetic_gates = [ordered]@{
        wrapper_finalization = [ordered]@{ status = $wrapperResult.status; case_count = @($wrapperResult.cases).Count; result_sha256 = (Get-Sha256 $wrapperResultPath) }
        batch_signature = [ordered]@{ status = $batchResult.status; case_count = @($batchResult.cases).Count; cases = $batchResult.cases; result_sha256 = (Get-Sha256 $batchResultPath) }
    }
    prior_attempts = [ordered]@{
        manifest_path = (Resolve-Path -LiteralPath $priorManifestPath).Path
        manifest_sha256 = $priorManifestSha
        file_count = $priorManifest.total_files
        attempts = $priorManifest.attempts
        run01_run06_vs_r7_start = [ordered]@{ result = $priorManifest.r7_start_cross_check.result; files = $priorManifest.r7_start_cross_check.current_files; mismatches = $priorManifest.r7_start_cross_check.mismatch_count }
        final_recheck_mismatches = $mismatches.Count
    }
    historic_run06 = [ordered]@{ stage_status = $r6Stage.status; custom_tcl_executed = $r6Stage.custom_tcl_executed; simulate_log_complete = $r6Stage.simulate_log_complete; xsim_exit_code = $r6Stage.xsim_exit_code; raw_matches_golden = $rawEqual; int8_matches_golden = $int8Equal }
    vivado = [ordered]@{
        mcp_connectivity_from_preflight = $environment.vivado_mcp.status
        mcp_error = $environment.vivado_mcp.error
        project_xpr_path = (Resolve-Path -LiteralPath $xprPath).Path
        xpr_sha256 = $xprSha
        xpr_unchanged_from_preflight = $true
        process_counts_after = $processCounts
        process_total_after = (($processCounts.Values | Measure-Object -Sum).Sum)
    }
}
$json = ConvertTo-Json -InputObject $report -Depth 12
[IO.File]::WriteAllText((Join-Path (Get-Location) $reportPath), $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
$written = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($written.status -cne 'PASS_STATIC_PREPARED_NOT_SIMULATED' -or $written.prior_attempts.final_recheck_mismatches -ne 0 -or $written.vivado.process_total_after -ne 0) { throw 'static report self-check failed' }
Write-Output "R8_STATIC_VALIDATION=PASS source_count=$($sourceHashes.Count) old_attempt_files=$($priorManifest.total_files) old_mismatches=$($mismatches.Count) processes=$($written.vivado.process_total_after)"
