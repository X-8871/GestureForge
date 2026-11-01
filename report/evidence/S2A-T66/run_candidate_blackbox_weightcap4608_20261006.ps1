[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, ParameterSetName = 'Compile')]
    [switch]$CompileOnly,
    [Parameter(Mandatory = $true, ParameterSetName = 'Run')]
    [switch]$RunSimulation,
    [Parameter(Mandatory = $true, ParameterSetName = 'Run')]
    [ValidatePattern('^[0-9a-fA-F]{64}$')]
    [string]$ApprovedCompileRecordSha256
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-NewText {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )
    $encoding = [System.Text.UTF8Encoding]::new($false)
    $bytes = $encoding.GetBytes($Text)
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

function Write-NewJson {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Value
    )
    Write-NewText -Path $Path -Text (($Value | ConvertTo-Json -Depth 16) + [Environment]::NewLine)
}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
}

function Assert-ExactFile {
    param([Parameter(Mandatory = $true)][string]$Path)
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($item.PSIsContainer -or $item.FullName -cne $Path -or
        ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        throw "T66_CANDIDATE_PATH_INVALID: 文件类型、精确路径或重解析属性不符：$($item.FullName)"
    }
    return $item
}

function Assert-ExactDirectory {
    param([Parameter(Mandatory = $true)][string]$Path)
    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if (-not $item.PSIsContainer -or $item.FullName -cne $Path -or
        ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
        throw "T66_CANDIDATE_PATH_INVALID: 目录类型、精确路径或重解析属性不符：$($item.FullName)"
    }
    return $item
}

function Get-FileBinding {
    param([Parameter(Mandatory = $true)][string[]]$Paths)
    return @(
        foreach ($path in $Paths) {
            $item = Assert-ExactFile -Path $path
            [ordered]@{
                path = $item.FullName
                bytes = [long]$item.Length
                sha256 = Get-Sha256 -Path $item.FullName
            }
        }
    )
}

function Get-AllowedProcessSnapshot {
    param(
        [Parameter(Mandatory = $true)][object]$AllowedIdentities,
        [Parameter(Mandatory = $true)][string]$Phase
    )
    $snapshot = @(Get-T65XilinxProcessSnapshot)
    $guardResult = Assert-T65XilinxProcessIdentities `
        -ActualProcesses $snapshot `
        -AllowedIdentities @($AllowedIdentities.identities) `
        -Phase $Phase
    return [ordered]@{
        phase = $Phase
        guard = $guardResult
        processes = $snapshot
    }
}

function Invoke-NativeCapture {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )
    $previous = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = @(& $Executable @Arguments 2>&1 | ForEach-Object { [string]$_ })
        $exitCode = [int]$LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previous
    }
    return [pscustomobject]@{ output = $output; exit_code = $exitCode }
}

$rootPath = 'D:\FPGA_Competition'
$evidenceParentPath = 'D:\FPGA_Competition\report\evidence\S2A-T66'
$evidencePath = 'D:\FPGA_Competition\report\evidence\S2A-T66\candidate_blackbox_weightcap4608_20261006'
$fixturePath = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01\fixture'
$manifestPath = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01\fixture_manifest.json'
$inputFixture = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01\fixture\sample0_input_chw_int8.bin'
$weightFixture = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01\fixture\sample0_layer0_gf8_weights.bin'
$goldenFixture = 'D:\FPGA_Competition\report\evidence\S2A-T66\tile01\fixture\sample0_layer0_expected_nchw_int8.bin'
$descriptorPath = 'D:\FPGA_Competition\src\s2a_network_descriptor_pkg.sv'
$dutPath = 'D:\FPGA_Competition\src\s2a_conv_tile_engine.sv'
$benchPath = 'D:\FPGA_Competition\sim\tb_s2a_t66_candidate_blackbox.sv'
$runnerPath = 'D:\FPGA_Competition\report\evidence\S2A-T66\run_candidate_blackbox_weightcap4608_20261006.ps1'
$processGuardPath = 'D:\FPGA_Competition\verification\t65_xilinx_process_guard.ps1'
$processAllowlistPath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02\process_identity_allowlist.json'
$warningGateReferencePath = 'D:\FPGA_Competition\verification\run_s2a_backend_fault_recovery.ps1'
$verilatorPath = 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin\verilator_bin.exe'
$toolBinPath = 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin'
$makeBinPath = 'D:\FPGA_S2A_MSYS2_20261001\env\usr\bin'
$verilatorRootPath = 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\share\verilator'
$pythonPath = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$expectedCandidateSha256 = '76ca735b14802e26f0a4b016989e13b43cf8bd904587ccea37651c757d089300'
$expectedDescriptorSha256 = '295df973188878388ff8ef48c50dfacb1fe3d23a169369d737d1babe0507dc14'
$expectedFixtureManifestSha256 = '99477aa6e0dacda328151844545bd9268e707459313004ca3aaed22d9a324640'
$expectedInputSha256 = 'da26d3850d23d6f8cb466416799358e77fbeceaa8ee27696ebf7ab365248ab9e'
$expectedWeightSha256 = 'df49b5d3aeaebd6b4107b99d83ffa791d7a7e24bd7b26df0815c246e5717e633'
$expectedGoldenSha256 = '220499b6b8122c3264bef4d581967d51eedccc9e28813df3e0ff8f8716bc2ed8'
$expectedGuardSha256 = 'e9103032f4a61ece7e58fd8570c786cfb4ddc8be6e9029c8e7d595932a13dca9'
$expectedAllowlistSha256 = 'bc743da5ac3d3b2a2e493f3b1b23bf8cc0dfce3913e179062022806797aa090e'
$expectedWarningGateReferenceSha256 = '3fc902e0b74969e6735667dc90ad0e2d6da329a6189a3050fd69e7c3312b6432'
$expectedInputBytes = 519168
$expectedWeightBytes = 864
$expectedOutputBytes = 1384448
$compileRecordPath = Join-Path $evidencePath 'compile_execution_record.json'
$compileSnapshotPath = Join-Path $evidencePath 'compile_source_snapshot.json'
$compileConsolePath = Join-Path $evidencePath 'compile_console.txt'
$buildPath = Join-Path $evidencePath 'build'
$simulatorPath = Join-Path $buildPath 'Vtb_s2a_t66_candidate_blackbox.exe'
$utf8 = [System.Text.UTF8Encoding]::new($false)

try {
    $null = Assert-ExactDirectory -Path $rootPath
    $null = Assert-ExactDirectory -Path $evidenceParentPath
    $null = Assert-ExactDirectory -Path $fixturePath
    foreach ($path in @($descriptorPath, $dutPath, $benchPath, $runnerPath, $manifestPath,
                         $inputFixture, $weightFixture, $goldenFixture, $processGuardPath,
                         $processAllowlistPath, $warningGateReferencePath, $verilatorPath, $pythonPath)) {
        $null = Assert-ExactFile -Path $path
    }

    if ((Get-Sha256 -Path $dutPath) -cne $expectedCandidateSha256) {
        throw 'T66_CANDIDATE_DUT_SHA_MISMATCH: 冻结 DUT 哈希变化。'
    }
    if ((Get-Sha256 -Path $descriptorPath) -cne $expectedDescriptorSha256) {
        throw 'T66_CANDIDATE_DESCRIPTOR_SHA_MISMATCH: descriptor package 哈希变化。'
    }
    if ((Get-Sha256 -Path $manifestPath) -cne $expectedFixtureManifestSha256) {
        throw 'T66_CANDIDATE_FIXTURE_MANIFEST_SHA_MISMATCH: 原始 fixture manifest 哈希变化。'
    }
    if ((Get-Sha256 -Path $processGuardPath) -cne $expectedGuardSha256 -or
        (Get-Sha256 -Path $processAllowlistPath) -cne $expectedAllowlistSha256) {
        throw 'T66_CANDIDATE_PROCESS_GUARD_SHA_MISMATCH: 冻结 T65 process guard 或 allowlist 哈希变化。'
    }
    if ((Get-Sha256 -Path $warningGateReferencePath) -cne $expectedWarningGateReferenceSha256) {
        throw 'T66_CANDIDATE_WARNING_GATE_REFERENCE_SHA_MISMATCH: T68 warning gate 参考 runner 哈希变化。'
    }

    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $fixtureRows = Get-FileBinding -Paths @($inputFixture, $weightFixture, $goldenFixture)
    $expectedFixtureHashes = @($expectedInputSha256, $expectedWeightSha256, $expectedGoldenSha256)
    $expectedFixtureLengths = @($expectedInputBytes, $expectedWeightBytes, $expectedOutputBytes)
    for ($index = 0; $index -lt $fixtureRows.Count; $index++) {
        if ($fixtureRows[$index].sha256 -cne $expectedFixtureHashes[$index] -or
            [long]$fixtureRows[$index].bytes -ne [long]$expectedFixtureLengths[$index]) {
            throw "T66_CANDIDATE_FIXTURE_MISMATCH: 原始 fixture 字节数或哈希不符：$($fixtureRows[$index].path)"
        }
    }
    if ($manifest.sample.input_fixture_path -cne $inputFixture -or
        $manifest.weights.fixture_path -cne $weightFixture -or
        $manifest.golden.fixture_path -cne $goldenFixture -or
        $manifest.sample.input_fixture_sha256 -cne $expectedInputSha256 -or
        $manifest.weights.fixture_sha256 -cne $expectedWeightSha256 -or
        $manifest.golden.fixture_sha256 -cne $expectedGoldenSha256 -or
        [long]$manifest.golden.tensor_byte_length -ne $expectedOutputBytes -or
        (($manifest.golden.shape_nchw -join ',') -cne '1,32,208,208')) {
        throw 'T66_CANDIDATE_FIXTURE_MANIFEST_BINDING_MISMATCH: manifest 与原始 fixture/完整输出范围不匹配。'
    }

    . $processGuardPath
    $allowedProcesses = Read-T65XilinxProcessAllowlist `
        -Path $processAllowlistPath `
        -ExpectedSha256 $expectedAllowlistSha256

    $toolchain = @($toolBinPath, $makeBinPath, $verilatorRootPath)
    foreach ($directory in $toolchain) {
        $null = Assert-ExactDirectory -Path $directory
    }
    $makePath = Join-Path $makeBinPath 'make.exe'
    $compilerPath = Join-Path $toolBinPath 'g++.exe'
    foreach ($file in @($makePath, $compilerPath)) { $null = Assert-ExactFile -Path $file }
    $env:PATH = "$makeBinPath;$toolBinPath;$env:PATH"
    $env:VERILATOR_ROOT = $verilatorRootPath
    $resolvedMake = (Get-Command -Name 'make.exe' -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
    $resolvedCompiler = (Get-Command -Name 'g++.exe' -CommandType Application -ErrorAction Stop | Select-Object -First 1).Source
    if ([System.IO.Path]::GetFullPath($resolvedMake) -ine [System.IO.Path]::GetFullPath($makePath) -or
        [System.IO.Path]::GetFullPath($resolvedCompiler) -ine [System.IO.Path]::GetFullPath($compilerPath)) {
        throw 'T66_CANDIDATE_TOOLCHAIN_PATH_MISMATCH: make 或 g++ 解析到批准 MSYS2 toolchain 之外。'
    }

    $sourcePaths = @($descriptorPath, $dutPath, $benchPath)
    $sourceRows = Get-FileBinding -Paths $sourcePaths
    $bindingRows = Get-FileBinding -Paths @($runnerPath, $warningGateReferencePath, $pythonPath,
        $processGuardPath, $processAllowlistPath, $manifestPath, $inputFixture, $weightFixture, $goldenFixture)
    $runnerSha = Get-Sha256 -Path $runnerPath
    $pythonMakeFlag = "PYTHON3='/c/Users/22061/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'"
    $compileArguments = @(
        '--binary', '--timing', '-Wno-fatal', '-j', '1', '--threads', '1',
        '--top-module', 'tb_s2a_t66_candidate_blackbox', '--Mdir', $buildPath,
        '-MAKEFLAGS', $pythonMakeFlag, '-CFLAGS', '-D_GLIBCXX_USE_CXX11_ABI=0'
    ) + $sourcePaths
    $compileCommand = @($verilatorPath) + $compileArguments
    $version = Invoke-NativeCapture -Executable $verilatorPath -Arguments @('--version')
    if ($version.exit_code -ne 0) { throw "T66_CANDIDATE_VERILATOR_VERSION_FAILED: exit=$($version.exit_code)" }

    if ($CompileOnly) {
        if (Test-Path -LiteralPath $evidencePath) {
            throw "T66_CANDIDATE_EVIDENCE_EXISTS: 拒绝覆盖现有证据目录：$evidencePath"
        }
        $null = [System.IO.Directory]::CreateDirectory($evidencePath)
        $null = Assert-ExactDirectory -Path $evidencePath
        $null = [System.IO.Directory]::CreateDirectory($buildPath)
        $null = Assert-ExactDirectory -Path $buildPath
        Write-NewText -Path (Join-Path $evidencePath 'verilator_version_console.txt') `
            -Text (($version.output -join [Environment]::NewLine) + [Environment]::NewLine)

        $preCompileGuard = Get-AllowedProcessSnapshot -AllowedIdentities $allowedProcesses -Phase 'candidate_compile_before'
        Write-NewJson -Path (Join-Path $evidencePath 'compile_prelaunch_process_snapshot.json') -Value $preCompileGuard
        $snapshot = [ordered]@{
            schema_version = 'gestureforge_s2a_t66_candidate_blackbox_compile_snapshot_v1'
            task_id = 'S2A-T66-CANDIDATE-BLACKBOX'
            top_module = 'tb_s2a_t66_candidate_blackbox'
            candidate_dut_sha256 = $expectedCandidateSha256
            fixture_manifest_sha256 = $expectedFixtureManifestSha256
            fixture_rows = $fixtureRows
            source_rows = $sourceRows
            supporting_binding_rows = $bindingRows
            warning_gate = [ordered]@{
                reference_runner = $warningGateReferencePath
                reference_runner_sha256 = $expectedWarningGateReferenceSha256
                limits = [ordered]@{ TIMESCALEMOD = 11; UNSIGNED = 1; WIDTHEXPAND = 36; WIDTHTRUNC = 16 }
                unknown_categories_allowed = $false
            }
            process_guard = [ordered]@{
                module_path = $processGuardPath
                module_sha256 = $expectedGuardSha256
                allowlist_path = $processAllowlistPath
                allowlist_sha256 = $expectedAllowlistSha256
            }
            verilator_path = $verilatorPath
            verilator_version = @($version.output)
            verilator_root = $verilatorRootPath
            python_path = $pythonPath
            python_make_flag = $pythonMakeFlag
            python_sha256 = Get-Sha256 -Path $pythonPath
            python_version = @((Invoke-NativeCapture -Executable $pythonPath -Arguments @('--version')).output)
            make_path = $resolvedMake
            compiler_path = $resolvedCompiler
            command = $compileCommand
            runner_sha256 = $runnerSha
            simulator_started = $false
        }
        Write-NewJson -Path $compileSnapshotPath -Value $snapshot

        $compileWatch = [System.Diagnostics.Stopwatch]::StartNew()
        $compileResult = Invoke-NativeCapture -Executable $verilatorPath -Arguments $compileArguments
        $compileWatch.Stop()
        Write-NewText -Path $compileConsolePath `
            -Text (($compileResult.output -join [Environment]::NewLine) + [Environment]::NewLine)
        $sourceRowsAfter = Get-FileBinding -Paths $sourcePaths
        $bindingRowsAfter = Get-FileBinding -Paths @($runnerPath, $warningGateReferencePath, $pythonPath,
            $processGuardPath, $processAllowlistPath, $manifestPath, $inputFixture, $weightFixture, $goldenFixture)
        $sourceUnchanged = (($sourceRows | ConvertTo-Json -Depth 8 -Compress) -ceq
            ($sourceRowsAfter | ConvertTo-Json -Depth 8 -Compress))
        $bindingUnchanged = (($bindingRows | ConvertTo-Json -Depth 8 -Compress) -ceq
            ($bindingRowsAfter | ConvertTo-Json -Depth 8 -Compress))

        $warningLimits = [ordered]@{ TIMESCALEMOD = 11; UNSIGNED = 1; WIDTHEXPAND = 36; WIDTHTRUNC = 16 }
        $warningCounts = [ordered]@{ TIMESCALEMOD = 0; UNSIGNED = 0; WIDTHEXPAND = 0; WIDTHTRUNC = 0 }
        $unknownWarnings = @{}
        foreach ($line in $compileResult.output) {
            if ([string]$line -match '%Warning-([A-Z0-9_]+):') {
                $category = $Matches[1]
                if ($warningCounts.Contains($category)) {
                    $warningCounts[$category] = [int]$warningCounts[$category] + 1
                } else {
                    $unknownWarnings[$category] = 1 + [int]$unknownWarnings[$category]
                }
            }
        }
        $overLimitWarnings = @(
            foreach ($category in $warningLimits.Keys) {
                if ([int]$warningCounts[$category] -gt [int]$warningLimits[$category]) { $category }
            }
        )
        $warningGatePassed = ($unknownWarnings.Count -eq 0) -and ($overLimitWarnings.Count -eq 0)
        $compileText = $compileResult.output -join [Environment]::NewLine
        $compileErrors = $compileText.Contains('%Error:')
        $postCompileGuard = Get-AllowedProcessSnapshot -AllowedIdentities $allowedProcesses -Phase 'candidate_compile_after'
        Write-NewJson -Path (Join-Path $evidencePath 'compile_postlaunch_process_snapshot.json') -Value $postCompileGuard
        $compileExeSha = $null
        if (Test-Path -LiteralPath $simulatorPath -PathType Leaf) { $compileExeSha = Get-Sha256 -Path $simulatorPath }
        $compileRecord = [ordered]@{
            schema_version = 'gestureforge_s2a_t66_candidate_blackbox_compile_record_v1'
            task_id = 'S2A-T66-CANDIDATE-BLACKBOX'
            candidate_dut_sha256 = $expectedCandidateSha256
            fixture_manifest_sha256 = $expectedFixtureManifestSha256
            testbench_sha256 = Get-Sha256 -Path $benchPath
            command = $compileCommand
            exit_code = [int]$compileResult.exit_code
            warning_counts = $warningCounts
            warning_limits = $warningLimits
            unknown_warning_categories = @($unknownWarnings.Keys)
            over_limit_warning_categories = $overLimitWarnings
            warning_gate_passed = [bool]$warningGatePassed
            errors_detected = [bool]$compileErrors
            source_unchanged = [bool]$sourceUnchanged
            supporting_bindings_unchanged = [bool]$bindingUnchanged
            sources_after = $sourceRowsAfter
            bindings_after = $bindingRowsAfter
            executable_path = $simulatorPath
            executable_sha256 = $compileExeSha
            duration_seconds = [Math]::Round($compileWatch.Elapsed.TotalSeconds, 3)
            console_path = $compileConsolePath
            process_guard_passed_before_and_after = $true
            simulator_started = $false
            next_status = 'COMPILED_WAITING_PARENT_REVIEW'
        }
        Write-NewJson -Path $compileRecordPath -Value $compileRecord
        $compileRecordSha = Get-Sha256 -Path $compileRecordPath
        $status = [ordered]@{
            schema_version = 'gestureforge_s2a_t66_candidate_blackbox_compile_status_v1'
            status = if ($compileResult.exit_code -eq 0 -and $warningGatePassed -and -not $compileErrors -and
                         $sourceUnchanged -and $bindingUnchanged -and $null -ne $compileExeSha) {
                'COMPILED_WAITING_PARENT_REVIEW'
            } else { 'COMPILE_FAILED_OR_WARNING_GATE_REJECTED' }
            compile_record_sha256 = $compileRecordSha
            candidate_dut_sha256 = $expectedCandidateSha256
            warning_gate_passed = [bool]$warningGatePassed
            simulator_started = $false
        }
        Write-NewJson -Path (Join-Path $evidencePath 'compile_status.json') -Value $status
        if ($status.status -cne 'COMPILED_WAITING_PARENT_REVIEW') {
            exit $(if ($compileResult.exit_code -ne 0) { $compileResult.exit_code } else { 1 })
        }
        Write-Output "COMPILED_WAITING_PARENT_REVIEW evidence=$evidencePath compile_record_sha256=$compileRecordSha warnings=$($warningCounts | ConvertTo-Json -Compress)"
        exit 0
    }

    $null = Assert-ExactDirectory -Path $evidencePath
    $null = Assert-ExactDirectory -Path $buildPath
    $null = Assert-ExactFile -Path $compileRecordPath
    $null = Assert-ExactFile -Path $compileSnapshotPath
    if ((Get-Sha256 -Path $compileRecordPath) -cne $ApprovedCompileRecordSha256.ToLowerInvariant()) {
        throw 'T66_CANDIDATE_APPROVAL_SHA_MISMATCH: compile record 与 parent 批准哈希不一致。'
    }
    $compileRecord = Get-Content -LiteralPath $compileRecordPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $snapshot = Get-Content -LiteralPath $compileSnapshotPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if ($compileRecord.candidate_dut_sha256 -and
        $compileRecord.candidate_dut_sha256 -cne $expectedCandidateSha256) {
        throw 'T66_CANDIDATE_COMPILE_DUT_SHA_MISMATCH: compile record 未绑定当前候选。'
    }
    if ($compileRecord.exit_code -ne 0 -or -not $compileRecord.warning_gate_passed -or
        $compileRecord.errors_detected -or -not $compileRecord.source_unchanged -or
        -not $compileRecord.supporting_bindings_unchanged -or -not $compileRecord.executable_sha256) {
        throw 'T66_CANDIDATE_COMPILE_GATE_FAILED: 编译、warning gate、绑定或可执行程序不满足运行条件。'
    }
    if ($snapshot.candidate_dut_sha256 -cne $expectedCandidateSha256 -or
        $snapshot.runner_sha256 -cne (Get-Sha256 -Path $runnerPath) -or
        $snapshot.warning_gate.reference_runner_sha256 -cne $expectedWarningGateReferenceSha256) {
        throw 'T66_CANDIDATE_SNAPSHOT_BINDING_MISMATCH: frozen compile snapshot 绑定变化。'
    }
    $currentSources = Get-FileBinding -Paths @($descriptorPath, $dutPath, $benchPath)
    $currentBindings = Get-FileBinding -Paths @($runnerPath, $warningGateReferencePath,
        $pythonPath, $processGuardPath, $processAllowlistPath, $manifestPath,
        $inputFixture, $weightFixture, $goldenFixture)
    if (($currentSources | ConvertTo-Json -Depth 8 -Compress) -cne
        ($snapshot.source_rows | ConvertTo-Json -Depth 8 -Compress) -or
        ($currentBindings | ConvertTo-Json -Depth 8 -Compress) -cne
        ($snapshot.supporting_binding_rows | ConvertTo-Json -Depth 8 -Compress)) {
        throw 'T66_CANDIDATE_SOURCE_OR_FIXTURE_CHANGED: compile 后候选源码、guard 或 fixture 已变化。'
    }
    $null = Assert-ExactFile -Path $simulatorPath
    if ((Get-Sha256 -Path $simulatorPath) -cne $compileRecord.executable_sha256) {
        throw 'T66_CANDIDATE_EXECUTABLE_SHA_MISMATCH: 仿真程序在 compile 后发生变化。'
    }

    $preRunGuard = Get-AllowedProcessSnapshot -AllowedIdentities $allowedProcesses -Phase 'candidate_run_before'
    $preRunGuardPath = Join-Path $evidencePath 'simulation_prelaunch_process_snapshot.json'
    Write-NewJson -Path $preRunGuardPath -Value $preRunGuard
    $simulationArguments = @(
        "+T66_INPUT_PATH=$inputFixture",
        "+T66_WEIGHT_PATH=$weightFixture",
        "+T66_GOLDEN_PATH=$goldenFixture"
    )
    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $simulatorPath
    $startInfo.Arguments = $simulationArguments -join ' '
    $startInfo.WorkingDirectory = $buildPath
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    $stdoutPath = Join-Path $evidencePath 'simulation_stdout.txt'
    $stderrPath = Join-Path $evidencePath 'simulation_stderr.txt'
    $stdoutWriter = [System.IO.StreamWriter]::new($stdoutPath, $false, $utf8)
    $stderrWriter = [System.IO.StreamWriter]::new($stderrPath, $false, $utf8)
    $stdoutWriter.AutoFlush = $true
    $stderrWriter.AutoFlush = $true
    $simulationWatch = [System.Diagnostics.Stopwatch]::StartNew()
    $lastProgress = [DateTime]::UtcNow
    $nextGuardCheck = [TimeSpan]::FromSeconds(30)
    $guardSnapshots = [System.Collections.Generic.List[object]]::new()
    $stdoutTask = $null
    $stderrTask = $null
    $guardFailure = $null
    $watchdogFailure = $null
    $stdoutLines = [System.Collections.Generic.List[string]]::new()
    $stderrLines = [System.Collections.Generic.List[string]]::new()
    if (-not $process.Start()) { throw 'T66_CANDIDATE_SIM_START_FAILED: 无法启动仿真程序。' }
    $stdoutTask = $process.StandardOutput.ReadLineAsync()
    $stderrTask = $process.StandardError.ReadLineAsync()
    try {
        while ($true) {
            $pendingTasks = @()
            if ($null -ne $stdoutTask) { $pendingTasks += $stdoutTask }
            if ($null -ne $stderrTask) { $pendingTasks += $stderrTask }
            if ($pendingTasks.Count -gt 0) {
                [void][System.Threading.Tasks.Task]::WaitAny([System.Threading.Tasks.Task[]]$pendingTasks, 1000)
            } else {
                Start-Sleep -Milliseconds 1000
            }

            if ($null -ne $stdoutTask -and $stdoutTask.IsCompleted) {
                $line = $stdoutTask.GetAwaiter().GetResult()
                if ($null -eq $line) { $stdoutTask = $null }
                else {
                    $stdoutLines.Add($line)
                    $stdoutWriter.WriteLine($line)
                    if ($line -match '^T66_(CYCLE_)?PROGRESS\b') {
                        $lastProgress = [DateTime]::UtcNow
                        Write-Output $line
                    }
                    $stdoutTask = $process.StandardOutput.ReadLineAsync()
                }
            }
            if ($null -ne $stderrTask -and $stderrTask.IsCompleted) {
                $line = $stderrTask.GetAwaiter().GetResult()
                if ($null -eq $line) { $stderrTask = $null }
                else {
                    $stderrLines.Add($line)
                    $stderrWriter.WriteLine($line)
                    $stderrTask = $process.StandardError.ReadLineAsync()
                }
            }

            if ($simulationWatch.Elapsed -ge [TimeSpan]::FromMinutes(30)) {
                $watchdogFailure = 'T66_CANDIDATE_WALL_TIMEOUT: 仿真超过30分钟。'
                if (-not $process.HasExited) { $process.Kill() }
            } elseif ((([DateTime]::UtcNow - $lastProgress).TotalSeconds) -ge 180 -and
                      -not $process.HasExited) {
                $watchdogFailure = 'T66_CANDIDATE_NO_PROGRESS_TIMEOUT: 连续180秒没有仿真进度标记。'
                $process.Kill()
            }

            if ($null -eq $guardFailure -and -not $process.HasExited -and
                $simulationWatch.Elapsed -ge $nextGuardCheck) {
                try {
                    $guardSnapshot = Get-AllowedProcessSnapshot `
                        -AllowedIdentities $allowedProcesses `
                        -Phase "candidate_run_elapsed_$([int]$simulationWatch.Elapsed.TotalSeconds)s"
                    $guardSnapshots.Add($guardSnapshot)
                    $nextGuardCheck = $simulationWatch.Elapsed + [TimeSpan]::FromSeconds(30)
                }
                catch {
                    $guardFailure = $_.Exception.Message
                    if (-not $process.HasExited) { $process.Kill() }
                }
            }
            if ($process.HasExited -and $null -eq $stdoutTask -and $null -eq $stderrTask) { break }
        }
        $process.WaitForExit()
    }
    finally {
        $stdoutWriter.Dispose()
        $stderrWriter.Dispose()
    }
    $simulationWatch.Stop()
    $simulationExitCode = [int]$process.ExitCode
    $postRunGuard = $null
    if ($null -eq $guardFailure) {
        try {
            $postRunGuard = Get-AllowedProcessSnapshot -AllowedIdentities $allowedProcesses -Phase 'candidate_run_after'
        }
        catch {
            $guardFailure = $_.Exception.Message
        }
    }
    if ($null -ne $postRunGuard) { $guardSnapshots.Add($postRunGuard) }
    Write-NewJson -Path (Join-Path $evidencePath 'simulation_process_guard_samples.json') -Value @($guardSnapshots)

    $outputText = $stdoutLines -join [Environment]::NewLine
    $passRegex = '(?m)^PASS: T66 candidate blackbox sample0 layer0 full tensor matched T25; bytes=1384448 mismatches=0 input_reads=583443 weight_reads=584064 output_writes=1384448 requests=2551955 responses=2551955 request_stalls=6635073 response_stalls=6635073 cycles=[0-9]+\r?$'
    $passObserved = [bool]($outputText -match $passRegex)
    $lanePassCount = [regex]::Matches($outputText, '(?m)^T66_READ_LANE_PASS lane=[0-3] ').Count
    $stallClassCount = [regex]::Matches($outputText, '(?m)^T66_CLASS_STALL class=[0-2] ').Count
    $fixtureMarkerObserved = [bool]($outputText -match '(?m)^T66_FIXTURES input=519168 weight=864 expected=1384448 shape=\[1,32,208,208\] layout=NCHW\r?$')
    $memoryMarkerObserved = [bool]($outputText -match '(?m)^T66_MEMORY byte-strobes=one-hot aligned=32-bit outstanding=1 stall-pattern=\[0,1,2,7,3\]\r?$')
    $cycleLimitMarkerObserved = [bool]($outputText -match '(?m)^T66_PLAN cycle_limit=75000000 lanes=8 waveforms=disabled mq_bias=normal_descriptor_prefetch\r?$')
    $simulationPassed = ($simulationExitCode -eq 0) -and $passObserved -and
        ($lanePassCount -eq 4) -and ($stallClassCount -eq 3) -and
        $fixtureMarkerObserved -and $memoryMarkerObserved -and $cycleLimitMarkerObserved -and
        [string]::IsNullOrWhiteSpace($guardFailure) -and [string]::IsNullOrWhiteSpace($watchdogFailure)
    $simulationRecord = [ordered]@{
        schema_version = 'gestureforge_s2a_t66_candidate_blackbox_simulation_record_v1'
        task_id = 'S2A-T66-CANDIDATE-BLACKBOX'
        candidate_dut_sha256 = $expectedCandidateSha256
        approved_compile_record_sha256 = $ApprovedCompileRecordSha256.ToLowerInvariant()
        command = @($simulatorPath) + $simulationArguments
        exit_code = $simulationExitCode
        simulator_started = $true
        duration_seconds = [Math]::Round($simulationWatch.Elapsed.TotalSeconds, 3)
        pass_marker_observed = $passObserved
        fixture_marker_observed = $fixtureMarkerObserved
        memory_protocol_marker_observed = $memoryMarkerObserved
        cycle_limit_marker_observed = $cycleLimitMarkerObserved
        normal_mq_bias_descriptor_prefetch_marker_observed = $cycleLimitMarkerObserved
        read_lane_pass_marker_count = $lanePassCount
        transfer_stall_class_marker_count = $stallClassCount
        expected_full_output_bytes = $expectedOutputBytes
        expected_input_read_requests = 583443
        expected_weight_read_requests = 584064
        expected_output_write_requests = $expectedOutputBytes
        expected_total_requests_and_responses = 2551955
        expected_request_and_response_stall_cycles = 6635073
        stdout_path = $stdoutPath
        stderr_path = $stderrPath
        process_guard_snapshot_path = Join-Path $evidencePath 'simulation_process_guard_samples.json'
        process_guard_failure = $guardFailure
        watchdog_failure = $watchdogFailure
        result = if ($simulationPassed) { 'PASS_FULL_LAYER0_BLACKBOX' } else { 'FAIL_OR_GUARD_REJECTED' }
    }
    Write-NewJson -Path (Join-Path $evidencePath 'simulation_execution_record.json') -Value $simulationRecord
    $simulationStatus = [ordered]@{
        schema_version = 'gestureforge_s2a_t66_candidate_blackbox_simulation_status_v1'
        status = $simulationRecord.result
        candidate_dut_sha256 = $expectedCandidateSha256
        simulation_record_sha256 = Get-Sha256 -Path (Join-Path $evidencePath 'simulation_execution_record.json')
    }
    Write-NewJson -Path (Join-Path $evidencePath 'simulation_status.json') -Value $simulationStatus
    if (-not $simulationPassed) { exit $(if ($simulationExitCode -ne 0) { $simulationExitCode } else { 1 }) }
    Write-Output "PASS_FULL_LAYER0_BLACKBOX evidence=$evidencePath duration_seconds=$($simulationRecord.duration_seconds)"
    exit 0
}
catch {
    $errorText = $_.Exception.Message
    if (Test-Path -LiteralPath $evidencePath -PathType Container) {
        $failurePath = Join-Path $evidencePath 'runner_failure.txt'
        if (-not (Test-Path -LiteralPath $failurePath)) {
            try { Write-NewText -Path $failurePath -Text ($errorText + [Environment]::NewLine) } catch {}
        }
    }
    [Console]::Error.WriteLine($errorText)
    exit 1
}
