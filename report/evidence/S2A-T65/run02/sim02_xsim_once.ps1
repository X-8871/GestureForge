[CmdletBinding()]
param(
    [switch]$PreflightOnly
)

$ErrorActionPreference = 'Stop'

function Write-NewUtf8Json {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Value
    )
    $encoding = [System.Text.UTF8Encoding]::new($false)
    $json = ($Value | ConvertTo-Json -Depth 10) + [Environment]::NewLine
    $bytes = $encoding.GetBytes($json)
    $stream = [System.IO.File]::Open(
        $Path,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
    )
    try {
        $stream.Write($bytes, 0, $bytes.Length)
        $stream.Flush()
    }
    finally {
        $stream.Dispose()
    }
}

$rootPath = 'D:\FPGA_Competition'
$runPath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02'
$simPath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02\sim02'
$vivadoBinPath = 'D:\Xilinx\2026.1\Vivado\bin'
$manifestPath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02\fixture_manifest.json'
$compileSnapshotPath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02\sim02_compile_source_snapshot.json'
$runnerPath = 'D:\FPGA_Competition\verification\run_s2a_t65_layer0_golden.ps1'
$pythonTestPath = 'D:\FPGA_Competition\verification\test_s2a_t65_layer0_golden.py'
$guardPath = 'D:\FPGA_Competition\verification\t65_xilinx_process_guard.ps1'
$guardExpectedSha256 = 'e9103032f4a61ece7e58fd8570c786cfb4ddc8be6e9029c8e7d595932a13dca9'
$allowlistPath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02\process_identity_allowlist.json'
$allowlistExpectedSha256 = 'bc743da5ac3d3b2a2e493f3b1b23bf8cc0dfce3913e179062022806797aa090e'
$snapshotName = 's2a_t65_layer0_golden_snapshot'
$inputFixturePath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02\fixture\sample0_input_chw_int8.bin'
$weightFixturePath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02\fixture\sample0_layer0_gf8_weights.bin'
$goldenFixturePath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02\fixture\sample0_layer0_output_point0.bin'
$inputPlusArg = "+T65_INPUT_PATH=$($inputFixturePath.Replace('\', '/'))"
$weightPlusArg = "+T65_WEIGHT_PATH=$($weightFixturePath.Replace('\', '/'))"
$goldenPlusArg = "+T65_GOLDEN_PATH=$($goldenFixturePath.Replace('\', '/'))"
$xsimLog = Join-Path $simPath 'xsim.log'
$xsimConsole = Join-Path $simPath 'xsim_once_console.txt'
$statusPath = Join-Path $simPath 'status.txt'
$bindingPath = Join-Path $runPath 'sim02_xsim_runtime_binding.json'
$recordPath = Join-Path $runPath 'sim02_xsim_execution_record.json'
$passMarker = 'PASS: sample0 layer0 首个输出字节 memory-read/write matched T25'

foreach ($directoryPath in @($rootPath, $runPath, $simPath)) {
    $directory = Get-Item -LiteralPath $directoryPath -ErrorAction Stop
    if (-not $directory.PSIsContainer -or $directory.FullName -cne $directoryPath -or
        ($directory.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "T65_ONCE_PATH_INVALID: $directoryPath"
    }
}
foreach ($outputPath in @($xsimLog, $xsimConsole, $statusPath, $bindingPath, $recordPath)) {
    if (Test-Path -LiteralPath $outputPath) {
        throw "T65_ONCE_OUTPUT_COLLISION: $outputPath"
    }
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$compileSnapshot = Get-Content -LiteralPath $compileSnapshotPath -Raw -Encoding UTF8 | ConvertFrom-Json
$runnerSha256 = (Get-FileHash -LiteralPath $runnerPath -Algorithm SHA256).Hash.ToLowerInvariant()
$pythonTestSha256 = (Get-FileHash -LiteralPath $pythonTestPath -Algorithm SHA256).Hash.ToLowerInvariant()
$manifestSha256 = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($manifest.source_sha256.'verification/run_s2a_t65_layer0_golden.ps1' -cne $runnerSha256 -or
    $manifest.source_sha256.'verification/test_s2a_t65_layer0_golden.py' -cne $pythonTestSha256) {
    throw 'T65_ONCE_RUNNER_BINDING_MISMATCH'
}
if (@($compileSnapshot.compiled_sv_inputs).Count -ne 15) {
    throw 'T65_ONCE_COMPILE_INPUT_COUNT_MISMATCH'
}
$compileInputs = @()
foreach ($input in $compileSnapshot.compiled_sv_inputs) {
    $inputItem = Get-Item -LiteralPath ([string]$input.path) -ErrorAction Stop
    if ($inputItem.PSIsContainer -or $inputItem.FullName -cne [string]$input.path -or
        ($inputItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "T65_ONCE_COMPILE_INPUT_PATH_INVALID: $($input.path)"
    }
    $actualSha256 = (Get-FileHash -LiteralPath $inputItem.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    $manifestKey = $inputItem.FullName.Substring($rootPath.Length + 1).Replace('\', '/')
    if ($actualSha256 -cne [string]$input.sha256 -or
        $actualSha256 -cne [string]$manifest.source_sha256.$manifestKey) {
        throw "T65_ONCE_COMPILE_INPUT_SHA_MISMATCH: $manifestKey"
    }
    $compileInputs += [ordered]@{ path = $inputItem.FullName; sha256 = $actualSha256; bytes = $inputItem.Length }
}
$fixtures = @(
    [ordered]@{ path = $inputFixturePath; expected_sha256 = [string]$manifest.sample.input_fixture_sha256 },
    [ordered]@{ path = $weightFixturePath; expected_sha256 = [string]$manifest.weights.slice_sha256 },
    [ordered]@{ path = $goldenFixturePath; expected_sha256 = [string]$manifest.golden.fixture_sha256 }
)
foreach ($fixture in $fixtures) {
    $fixtureItem = Get-Item -LiteralPath $fixture.path -ErrorAction Stop
    if ($fixtureItem.PSIsContainer -or $fixtureItem.FullName -cne $fixture.path -or
        ($fixtureItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "T65_ONCE_FIXTURE_PATH_INVALID: $($fixture.path)"
    }
    $fixture['actual_sha256'] = (Get-FileHash -LiteralPath $fixture.path -Algorithm SHA256).Hash.ToLowerInvariant()
    $fixture['bytes'] = $fixtureItem.Length
    if ($fixture['actual_sha256'] -cne $fixture.expected_sha256) {
        throw "T65_ONCE_FIXTURE_SHA_MISMATCH: $($fixture.path)"
    }
}

$xelabLog = Join-Path $simPath 'xelab.log'
$xelabItem = Get-Item -LiteralPath $xelabLog -ErrorAction Stop
if ($xelabItem.PSIsContainer -or (Select-String -LiteralPath $xelabLog -Pattern 'ERROR:|FATAL:' -Quiet) -or
    -not (Select-String -LiteralPath $xelabLog -SimpleMatch -Pattern "Built simulation snapshot $snapshotName" -Quiet)) {
    throw 'T65_ONCE_ELABORATION_EVIDENCE_INVALID'
}
$snapshotDirectoryPath = Join-Path (Join-Path $simPath 'xsim.dir') $snapshotName
$snapshotDirectory = Get-Item -LiteralPath $snapshotDirectoryPath -ErrorAction Stop
if (-not $snapshotDirectory.PSIsContainer -or
    ($snapshotDirectory.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    throw 'T65_ONCE_ELABORATED_SNAPSHOT_PATH_INVALID'
}

$guardItem = Get-Item -LiteralPath $guardPath -ErrorAction Stop
$allowlistItem = Get-Item -LiteralPath $allowlistPath -ErrorAction Stop
if ($guardItem.PSIsContainer -or $guardItem.FullName -cne $guardPath -or
    (Get-FileHash -LiteralPath $guardPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne $guardExpectedSha256 -or
    $allowlistItem.PSIsContainer -or $allowlistItem.FullName -cne $allowlistPath -or
    (Get-FileHash -LiteralPath $allowlistPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne $allowlistExpectedSha256) {
    throw 'T65_ONCE_PROCESS_GUARD_OR_ALLOWLIST_MISMATCH'
}
. $guardPath
$allowlist = Read-T65XilinxProcessAllowlist -Path $allowlistPath -ExpectedSha256 $allowlistExpectedSha256
$allowedIdentities = @($allowlist.identities)
$processBefore = Assert-T65AllowedXilinxProcessSnapshot -AllowedIdentities $allowedIdentities -Phase 'immediately before the sole XSim run'

$xsimToolPath = Join-Path $vivadoBinPath 'xsim.bat'
$xsimTool = Get-Item -LiteralPath $xsimToolPath -ErrorAction Stop
if ($xsimTool.PSIsContainer) {
    throw "T65_ONCE_XSIM_TOOL_INVALID: $xsimToolPath"
}
$arguments = @(
    '-R',
    '-testplusarg', $inputPlusArg,
    '-testplusarg', $weightPlusArg,
    '-testplusarg', $goldenPlusArg,
    '-log', 'xsim.log',
    $snapshotName
)
$binding = [ordered]@{
    schema_version = 'gestureforge_s2a_t65_sim02_xsim_binding_v1'
    task_id = 'S2A-T65-SIM02'
    status = 'BOUND_BEFORE_SOLE_XSIM_INVOCATION'
    scope = 'sample0 layer0 CONV output NCHW [0,0,0,0] only'
    command = [ordered]@{ executable = $xsimToolPath; arguments = $arguments; working_directory = $simPath }
    runner_sha256 = $runnerSha256
    python_verifier_sha256 = $pythonTestSha256
    manifest_path = $manifestPath
    manifest_sha256 = $manifestSha256
    compile_snapshot_path = $compileSnapshotPath
    compile_snapshot_sha256 = (Get-FileHash -LiteralPath $compileSnapshotPath -Algorithm SHA256).Hash.ToLowerInvariant()
    xelab_log_sha256 = (Get-FileHash -LiteralPath $xelabLog -Algorithm SHA256).Hash.ToLowerInvariant()
    elaborated_snapshot_path = $snapshotDirectoryPath
    compiled_sv_inputs = $compileInputs
    fixtures = $fixtures
    allowlist_sha256 = $allowlistExpectedSha256
    process_guard_sha256 = $guardExpectedSha256
    process_snapshot_before = $processBefore
    waveform_dump_requested = $false
}
if ($PreflightOnly) {
    Write-Output 'PREFLIGHT_PASS: source, fixture, compiled snapshot, and protected process identities are bound.'
    exit 0
}
Write-NewUtf8Json -Path $bindingPath -Value $binding

Push-Location -LiteralPath $simPath
$started = [DateTimeOffset]::Now
$xsimExit = $null
$runError = $null
$processAfter = $null
try {
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $LASTEXITCODE = $null
        & $xsimToolPath @arguments *> $xsimConsole
        $xsimExit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    $processAfter = Assert-T65AllowedXilinxProcessSnapshot -AllowedIdentities $allowedIdentities -Phase 'immediately after the sole XSim run'
}
catch {
    $runError = $_.Exception.Message
}
finally {
    Pop-Location
}
$ended = [DateTimeOffset]::Now

$runStatus = 'XSIM_FAIL'
if ($null -ne $runError) {
    $runStatus = 'PROCESS_GATE_OR_LAUNCH_ERROR'
}
elseif ($xsimExit -ne 0) {
    $runStatus = "XSIM_FAIL exit=$xsimExit"
}
elseif (-not (Test-Path -LiteralPath $xsimLog -PathType Leaf)) {
    $runStatus = 'XSIM_LOG_MISSING'
}
elseif (Select-String -LiteralPath $xsimLog -Pattern 'ERROR:|FATAL:' -Quiet) {
    $runStatus = 'XSIM_LOG_FAIL'
}
elseif (-not (Select-String -LiteralPath $xsimLog -SimpleMatch -Pattern $passMarker -Quiet)) {
    $runStatus = 'PASS_MARKER_MISSING'
}
else {
    $runStatus = 'PASS_SAMPLE0_LAYER0_POINT0_ONLY'
}
Set-Content -LiteralPath $statusPath -Value $runStatus -Encoding UTF8
$record = [ordered]@{
    schema_version = 'gestureforge_s2a_t65_sim02_xsim_execution_v1'
    task_id = 'S2A-T65-SIM02'
    scope = 'single sample0 layer0 CONV output NCHW [0,0,0,0] smoke only'
    status = $runStatus
    xsim_exit_code = $xsimExit
    error = $runError
    command = $binding.command
    binding_path = $bindingPath
    binding_sha256 = (Get-FileHash -LiteralPath $bindingPath -Algorithm SHA256).Hash.ToLowerInvariant()
    execution_script_path = $PSCommandPath
    execution_script_sha256 = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()
    runner_sha256 = $runnerSha256
    xsim_console_path = $xsimConsole
    xsim_console_sha256 = if (Test-Path -LiteralPath $xsimConsole -PathType Leaf) { (Get-FileHash -LiteralPath $xsimConsole -Algorithm SHA256).Hash.ToLowerInvariant() } else { $null }
    xsim_log_path = $xsimLog
    xsim_log_sha256 = if (Test-Path -LiteralPath $xsimLog -PathType Leaf) { (Get-FileHash -LiteralPath $xsimLog -Algorithm SHA256).Hash.ToLowerInvariant() } else { $null }
    process_snapshot_before = $processBefore
    process_snapshot_after = $processAfter
    started_utc = $started.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffffffZ', [Globalization.CultureInfo]::InvariantCulture)
    ended_utc = $ended.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffffffZ', [Globalization.CultureInfo]::InvariantCulture)
    duration_seconds = [Math]::Round(($ended - $started).TotalSeconds, 3)
    waveform_dump_requested = $false
}
Write-NewUtf8Json -Path $recordPath -Value $record
Write-Output "status=$runStatus"
Write-Output "xsim_exit_code=$xsimExit"
Write-Output "xsim_console=$xsimConsole"
Write-Output "xsim_log=$xsimLog"
Write-Output "execution_record=$recordPath"
if ($runStatus -ne 'PASS_SAMPLE0_LAYER0_POINT0_ONLY') {
    if ($null -ne $xsimExit -and $xsimExit -ne 0) {
        exit ([int]$xsimExit)
    }
    exit 1
}
Write-Output $passMarker
