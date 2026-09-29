$ErrorActionPreference = 'Stop'
$runRoot = (Get-Item -LiteralPath $PSScriptRoot -ErrorAction Stop).FullName
$expectedRun = 'D:\FPGA_Competition\report\evidence\S2A-T60\run06'
if ($runRoot -cne $expectedRun) { throw "Unexpected verifier root: $runRoot" }
$env:TEMP = Join-Path $runRoot 'temp'
$env:TMP = $env:TEMP
$env:TMPDIR = $env:TEMP
$summary = Get-Content -LiteralPath (Join-Path $runRoot 'prepare_summary.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$binding = Get-Content -LiteralPath (Join-Path $runRoot 'project_preflight_binding.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$manifest = Get-Content -LiteralPath (Join-Path (Join-Path $runRoot 'fixture') 'fixture_manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$inventory = Get-Content -LiteralPath (Join-Path $runRoot 'run06_inventory.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if ($summary.run_id -cne 'run06' -or $summary.status -cne 'PREPARED_NOT_SIMULATED') { throw 'Run06 summary identity/status mismatch' }
if ($binding.run_id -cne 'run06' -or $binding.status -cne 'STATIC_PREPARED_NOT_SIMULATED') { throw 'Run06 binding identity/status mismatch' }
if ($manifest.run_id -cne 'run06' -or $manifest.status -cne 'PREPARED_NOT_SIMULATED') { throw 'Run06 fixture manifest identity/status mismatch' }
if ($inventory.run_id -cne 'run06' -or $inventory.status -cne 'PREPARED_NOT_SIMULATED' -or -not $inventory.inventory_excludes_itself) { throw 'Run06 inventory identity/status mismatch' }
if ($summary.geometry.y -ne 24 -or $summary.geometry.x_first -ne 0 -or $summary.geometry.x_last -ne 25 -or $summary.geometry.output_values -ne 6656 -or $summary.geometry.output_channels -ne 256) { throw 'T60 geometry mismatch' }
foreach ($name in @('TEMP','TMP','TMPDIR')) {
    $value = [Environment]::GetEnvironmentVariable($name)
    if ([IO.Path]::GetPathRoot($value) -cne 'D:\') { throw "Temporary variable is not on D: $name=$value" }
}
foreach ($entry in $manifest.copied_fixture_files) {
    $file = Get-Item -LiteralPath $entry.path -ErrorAction Stop
    if ($file.Length -ne [int64]$entry.bytes -or (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -cne $entry.sha256) { throw "Fixture mismatch: $($entry.name)" }
}
foreach ($entry in $binding.rtl_sources) {
    $file = Get-Item -LiteralPath $entry.path -ErrorAction Stop
    if ($file.Length -ne [int64]$entry.bytes -or (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -cne $entry.sha256) { throw "RTL mismatch: $($file.name)" }
}
$tb = Get-Content -LiteralPath (Join-Path (Join-Path $runRoot 'rtl') 'tb_s2a_conv_layer35_row24_all_channels.sv') -Raw -Encoding UTF8
if ($tb.Contains('S2A-T60\\run04') -or -not $tb.Contains('S2A-T60\\run06')) { throw 'Testbench path is not exclusively bound to run06' }
$setup = Get-Content -LiteralPath (Join-Path $runRoot 'prepare_isolated_project.tcl') -Raw -Encoding UTF8
if ($setup -notmatch 'set t60_project_name "s2a_t60_run06"' -or $setup -notmatch 'create_project \$t60_project_name \$t60_project_dir -part xc7z020clg400-1' -or $setup -match '(?im)^\s*launch_simulation\b') { throw 'Project Tcl static contract mismatch' }
if ($setup -notmatch 'foreach t60_env_name \{TEMP TMP TMPDIR\}' -or $setup -notmatch 'set ::env\(\$t60_env_name\)' -or $setup -notmatch 'cd \$t60_run_root') { throw 'Project Tcl D environment/cwd binding mismatch' }
$launcherPath = Join-Path $runRoot 'run_xsim_background.tcl'
$launcher = Get-Content -LiteralPath $launcherPath -Raw -Encoding UTF8
$launcherHash = (Get-FileHash -LiteralPath $launcherPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($launcher -notmatch 'T60_RUN06_ASYNC_LAUNCHER_BLOCKED' -or $launcher -match '(?im)^\s*(?:exec|launch_simulation)\b' -or $binding.simulation.launcher_status -cne 'BLOCKED_UNVERIFIED' -or $binding.simulation.blocker_sha256 -cne $launcherHash) { throw 'Launcher must stay fail-closed and match its binding' }
if ($summary.scripts.background_xsim_launcher.sha256 -cne $launcherHash -or $summary.scripts.background_xsim_launcher.status -cne 'BLOCKED_FAIL_CLOSED') { throw 'Summary launcher binding mismatch' }
if ($summary.project_binding.sha256 -cne (Get-FileHash -LiteralPath (Join-Path $runRoot 'project_preflight_binding.json') -Algorithm SHA256).Hash.ToLowerInvariant()) { throw 'Summary project binding hash mismatch' }
if ($summary.static_verification.launcher_blocked_fail_closed -ne $true -or $summary.static_verification.runner_launches_simulation -ne $false -or $summary.execution.simulation -cne 'NOT_RUN' -or $summary.execution.Vivado -cne 'NOT_STARTED') { throw 'Static-only execution state mismatch' }
if (Test-Path -LiteralPath $binding.project.xpr) { throw 'Vivado project should remain uncreated during static prep' }
foreach ($name in @('observed_raw.bin','observed_output.bin','simulate.log','xsim_console.log')) { if (Test-Path -LiteralPath (Join-Path $runRoot $name)) { throw "Unexpected simulation output: $name" } }
foreach ($entry in $inventory.files) {
    $file = Get-Item -LiteralPath $entry.path -ErrorAction Stop
    if ($file.Length -ne [int64]$entry.bytes -or (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -cne $entry.sha256) { throw "Inventory mismatch: $($entry.relative_path)" }
    if ([IO.Path]::GetPathRoot($file.FullName) -cne 'D:\') { throw "Generated inventory path is outside D: $($entry.path)" }
}
$actualFiles = @(Get-ChildItem -LiteralPath $runRoot -File -Force -Recurse | Where-Object { $_.Name -cne 'run06_inventory.json' })
if ($actualFiles.Count -ne @($inventory.files).Count) { throw 'Inventory file count mismatch' }
Write-Output "T60_RUN06_STATIC_VERIFY=PASS y=24 outputs=6656 temp=D: project=NOT_CREATED simulation=NOT_RUN launcher=BLOCKED_FAIL_CLOSED"