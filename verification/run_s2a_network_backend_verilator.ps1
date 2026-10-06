[CmdletBinding()]
param(
    [ValidateRange(0, 108)]
    [int]$SampleIndex = 0,

    [string]$RunId = 'run01',

    [string]$EvidenceDirectory = '',

    [string]$ExpectedBackendSha256 = '',

    [long]$MaxCycles = 4294967295,

    [string]$PythonExecutable = 'python',

    [switch]$Compile,

    [switch]$RunSimulation,

    [switch]$ReuseVerifiedFixtures
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-Sha256Literal {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-S2aNetworkBackendResultSummary {
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text)

    $normalizedText = $Text.Replace("`r`n", "`n")
    return ($normalizedText -match '(?m)^status=PASS_LAYERWISE_EXACT_GOLDEN$') -and
        ($normalizedText -match '(?m)^feature_write_bytes=11382150 mismatches=0 cycles=[0-9]+$') -and
        ($normalizedText -match '(?m)^head13_bytes=5070 head26_bytes=20280$')
}

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )
    $encoding = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Path, $Content, $encoding)
}

function Write-CommandLog {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object[]]$Lines
    )
    $text = ($Lines | ForEach-Object { [string]$_ }) -join [Environment]::NewLine
    if (-not $text.EndsWith([Environment]::NewLine)) {
        $text += [Environment]::NewLine
    }
    Write-Utf8NoBom -Path $Path -Content $text
}

function Quote-ProcessArgument {
    param([Parameter(Mandatory = $true)][string]$Argument)
    return '"' + $Argument + '"'
}

function Invoke-NativeCapturedProcess {
    param(
        [Parameter(Mandatory = $true)][string]$ExecutablePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$WorkingDirectory,
        [Parameter(Mandatory = $true)][string]$StandardOutputPath,
        [Parameter(Mandatory = $true)][string]$StandardErrorPath
    )
    $process = $null
    $exitCode = 127
    $launchError = ''
    $argumentLine = ($Arguments | ForEach-Object { Quote-ProcessArgument -Argument ([string]$_) }) -join ' '
    try {
        $process = Start-Process -FilePath $ExecutablePath -ArgumentList $argumentLine `
            -WorkingDirectory $WorkingDirectory -WindowStyle Hidden -RedirectStandardOutput $StandardOutputPath `
            -RedirectStandardError $StandardErrorPath -Wait -PassThru
        if ($null -eq $process) { throw 'Start-Process 未返回 native process。' }
        $process.WaitForExit()
        $exitCode = [int]$process.ExitCode
    } catch {
        $launchError = $_.ToString()
        if ($null -ne $process) {
            try {
                $process.Refresh()
                if ($process.HasExited) { $exitCode = [int]$process.ExitCode }
            } catch { }
        }
        $encoding = [System.Text.UTF8Encoding]::new($false)
        [System.IO.File]::AppendAllText($StandardErrorPath, $launchError + [Environment]::NewLine, $encoding)
    } finally {
        if ($null -ne $process) {
            try {
                $process.Refresh()
                if ($process.HasExited) { $exitCode = [int]$process.ExitCode }
            } catch { }
        }
        if (-not (Test-Path -LiteralPath $StandardOutputPath -PathType Leaf)) {
            [System.IO.File]::WriteAllBytes($StandardOutputPath, [byte[]]@())
        }
        if (-not (Test-Path -LiteralPath $StandardErrorPath -PathType Leaf)) {
            [System.IO.File]::WriteAllBytes($StandardErrorPath, [byte[]]@())
        }
    }
    return [pscustomobject]@{
        exit_code = $exitCode
        launch_error = $launchError
        process_id = if ($null -ne $process) { $process.Id } else { $null }
        stdout_path = $StandardOutputPath
        stderr_path = $StandardErrorPath
    }
}

function Write-NativeProcessConsole {
    param(
        [Parameter(Mandatory = $true)][string]$ConsolePath,
        [Parameter(Mandatory = $true)][string]$StandardOutputPath,
        [Parameter(Mandatory = $true)][string]$StandardErrorPath
    )
    $lines = @()
    if ((Get-Item -LiteralPath $StandardOutputPath).Length -gt 0) {
        $lines += [System.IO.File]::ReadAllLines($StandardOutputPath, [System.Text.Encoding]::UTF8)
    }
    if ((Get-Item -LiteralPath $StandardErrorPath).Length -gt 0) {
        $lines += '--- STDERR ---'
        $lines += [System.IO.File]::ReadAllLines($StandardErrorPath, [System.Text.Encoding]::UTF8)
    }
    if ($lines.Count -eq 0) { $lines = @('') }
    Write-CommandLog -Path $ConsolePath -Lines $lines
}

function Test-StartedProcessIdentity {
    param(
        [Parameter(Mandatory = $true)][System.Diagnostics.Process]$Process,
        [Parameter(Mandatory = $true)][string]$ExpectedPath,
        [Parameter(Mandatory = $true)][string[]]$ExpectedArguments,
        [Parameter(Mandatory = $true)][datetime]$ExpectedStartTimeUtc
    )
    try {
        $Process.Refresh()
        if ($Process.HasExited) { return $false }
        $currentProcess = Get-Process -Id $Process.Id -ErrorAction Stop
        if ([string]::IsNullOrWhiteSpace($currentProcess.Path)) { return $false }
        if ([System.IO.Path]::GetFullPath($currentProcess.Path) -ine [System.IO.Path]::GetFullPath($ExpectedPath)) { return $false }
        $currentStartTimeUtc = $currentProcess.StartTime.ToUniversalTime()
        if ([Math]::Abs(($currentStartTimeUtc - $ExpectedStartTimeUtc).TotalSeconds) -gt 2) { return $false }
        $nativeProcess = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId = $($Process.Id)" -ErrorAction Stop
        if ($null -eq $nativeProcess -or [string]::IsNullOrWhiteSpace($nativeProcess.CommandLine)) { return $false }
        if ([System.IO.Path]::GetFullPath($nativeProcess.ExecutablePath) -ine [System.IO.Path]::GetFullPath($ExpectedPath)) { return $false }
        foreach ($expectedArgument in $ExpectedArguments) {
            if ($nativeProcess.CommandLine.IndexOf($expectedArgument, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
                return $false
            }
        }
        return $true
    } catch {
        return $false
    }
}

function Get-CompleteProgressMarkerLines {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{ readable = $true; lines = [string[]]@() }
    }
    $sharing = [System.IO.FileShare]::ReadWrite -bor [System.IO.FileShare]::Delete
    $text = $null
    for ($attempt = 0; $attempt -lt 4; $attempt++) {
        $stream = $null
        $reader = $null
        try {
            $stream = [System.IO.FileStream]::new($Path, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, $sharing)
            $reader = [System.IO.StreamReader]::new($stream, [System.Text.Encoding]::UTF8, $true)
            $text = $reader.ReadToEnd()
            break
        } catch [System.IO.IOException] {
            if ($attempt -lt 3) { Start-Sleep -Milliseconds 25 }
        } catch [System.UnauthorizedAccessException] {
            break
        } finally {
            if ($null -ne $reader) {
                try { $reader.Dispose() } catch { }
            } elseif ($null -ne $stream) {
                try { $stream.Dispose() } catch { }
            }
        }
    }
    if ($null -eq $text) {
        return [pscustomobject]@{ readable = $false; lines = [string[]]@() }
    }
    if (-not $text.EndsWith("`n")) {
        $lastNewline = $text.LastIndexOf("`n")
        if ($lastNewline -lt 0) { return [pscustomobject]@{ readable = $true; lines = [string[]]@() } }
        $text = $text.Substring(0, $lastNewline + 1)
    }
    $lines = @($text -split "`r?`n" | Where-Object { $_.StartsWith('S2A_PROGRESS ', [System.StringComparison]::Ordinal) })
    return [pscustomobject]@{ readable = $true; lines = [string[]]$lines }
}

function ConvertFrom-ProgressMarker {
    param([Parameter(Mandatory = $true)][string]$Line)
    $pattern = '^S2A_PROGRESS sample=(?<sample>[0-9]+) layer=(?<layer>[0-9]+) cycle=(?<cycle>[0-9]+) output=(?<output>[0-9]+) conv_tile_y=(?<tile_y>[0-9]+) conv_tile_x=(?<tile_x>[0-9]+) conv_group=(?<group>[0-9]+) conv_point=(?<point>[0-9]+) conv_reduction=(?<reduction>[0-9]+) conv_feature_scan=(?<feature_scan>[0-9]+) conv_weight_reduction=(?<weight_reduction>[0-9]+) conv_output_lane=(?<output_lane>[0-9]+) conv_output_point=(?<output_point>[0-9]+) pool_tap=(?<pool_tap>[0-9]+) feature_write_bytes=(?<bytes>[0-9]+) read_transactions=(?<reads>[0-9]+) write_transactions=(?<writes>[0-9]+) phase=(?<phase>start|running|complete)$'
    if ($Line -notmatch $pattern) { return $null }
    $signature = @(
        $Matches.layer,
        $Matches.output,
        $Matches.tile_y,
        $Matches.tile_x,
        $Matches.group,
        $Matches.point,
        $Matches.reduction,
        $Matches.feature_scan,
        $Matches.weight_reduction,
        $Matches.output_lane,
        $Matches.output_point,
        $Matches.pool_tap,
        $Matches.bytes,
        $Matches.reads,
        $Matches.writes
    ) -join '|'
    return [pscustomobject]@{
        sample = [int]$Matches.sample
        layer = [int]$Matches.layer
        cycle = [long]$Matches.cycle
        phase = [string]$Matches.phase
        signature = $signature
    }
}

function Test-ProgressSignatureChanged {
    param(
        [AllowEmptyString()][string]$PreviousSignature,
        [Parameter(Mandatory = $true)][string]$CurrentSignature
    )
    if ([string]::IsNullOrEmpty($PreviousSignature)) { return $false }
    return -not [string]::Equals($PreviousSignature, $CurrentSignature, [System.StringComparison]::Ordinal)
}

if ($RunSimulation -and -not $Compile) {
    throw 'RunSimulation 必须与 Compile 同次调用，防止运行未绑定的旧二进制。'
}
if ($MaxCycles -le 0 -or $MaxCycles -gt 4294967295) {
    throw 'MaxCycles 必须在 1..4294967295 范围内。'
}
if ($RunId -notmatch '^[A-Za-z0-9_-]+$') {
    throw 'RunId 仅允许 ASCII 字母、数字、下划线和连字符。'
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if ([string]::IsNullOrWhiteSpace($EvidenceDirectory)) {
    $EvidenceDirectory = Join-Path $repoRoot 'report\evidence\S2A-T68\run01'
}
$evidenceRoot = [System.IO.Path]::GetFullPath($EvidenceDirectory)
$prepareScript = Join-Path $PSScriptRoot 'prepare_s2a_network_backend_golden.py'
$verifyScript = Join-Path $PSScriptRoot 'verify_s2a_network_backend_golden.py'
$runnerSource = (Resolve-Path -LiteralPath $PSCommandPath).Path
$testbench = Join-Path $repoRoot 'sim\tb_s2a_network_backend_golden.sv'
$backendSource = Join-Path $repoRoot 'src\s2a_network_backend.sv'

if (-not (Test-Path -LiteralPath $prepareScript -PathType Leaf)) { throw "缺少 preparer：$prepareScript" }
if (-not (Test-Path -LiteralPath $verifyScript -PathType Leaf)) { throw "缺少只读 verifier：$verifyScript" }
if (-not (Test-Path -LiteralPath $testbench -PathType Leaf)) { throw "缺少 testbench：$testbench" }
if (-not (Test-Path -LiteralPath $backendSource -PathType Leaf)) { throw "缺少 backend：$backendSource" }

$fixtureManifest = Join-Path $evidenceRoot ("fixtures\sample_{0:D3}\fixture_manifest.json" -f $SampleIndex)
if ($ReuseVerifiedFixtures) {
    if (-not (Test-Path -LiteralPath $fixtureManifest -PathType Leaf)) {
        throw "只读复用模式要求 fixture manifest 已存在：$fixtureManifest"
    }
} else {
    $prepareArgs = @(
        $prepareScript,
        '--sample-index', [string]$SampleIndex,
        '--output-root', $evidenceRoot
    )
    & $PythonExecutable @prepareArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$verifyArgs = @($verifyScript, '--manifest', $fixtureManifest)
& $PythonExecutable @verifyArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (-not $Compile) {
    Write-Output "T68 fixture-only 完成；未编译、未启动仿真。EvidenceDirectory=$evidenceRoot"
    exit 0
}

if ($ExpectedBackendSha256 -notmatch '^[0-9a-fA-F]{64}$') {
    throw 'RTL compile/run 必须显式给出冻结 backend SHA-256。'
}
$actualBackendSha256 = Get-Sha256Literal -Path $backendSource
if ($actualBackendSha256 -ne $ExpectedBackendSha256.ToLowerInvariant()) {
    throw "当前 backend SHA 与冻结值不同；actual=$actualBackendSha256 expected=$ExpectedBackendSha256"
}

$toolchainRoot = 'D:\FPGA_S2A_MSYS2_20261001\env'
$toolBin = Join-Path $toolchainRoot 'mingw64\bin'
$makeBin = Join-Path $toolchainRoot 'usr\bin'
$verilator = Join-Path $toolBin 'verilator_bin.exe'
$makePath = Join-Path $makeBin 'make.exe'
$compilerPath = Join-Path $toolBin 'g++.exe'
$verilatorRoot = [System.IO.Path]::GetFullPath((Join-Path $toolBin '..\share\verilator'))
if (-not (Test-Path -LiteralPath $toolchainRoot -PathType Container)) { throw "缺少批准的 MSYS2 环境目录：$toolchainRoot" }
if (-not (Test-Path -LiteralPath $toolBin -PathType Container)) { throw "缺少指定 MSYS2 bin 目录：$toolBin" }
if (-not (Test-Path -LiteralPath $makeBin -PathType Container)) { throw "缺少 MSYS2 make 目录：$makeBin" }
if (-not (Test-Path -LiteralPath $verilator -PathType Leaf)) { throw "缺少 Verilator 二进制：$verilator" }
if (-not (Test-Path -LiteralPath $makePath -PathType Leaf)) { throw "缺少 MSYS2 make：$makePath" }
if (-not (Test-Path -LiteralPath $compilerPath -PathType Leaf)) { throw "缺少 MSYS2 C++ 编译器：$compilerPath" }
if (-not (Test-Path -LiteralPath $verilatorRoot -PathType Container)) { throw "缺少 Verilator 数据目录：$verilatorRoot" }
$env:PATH = "$makeBin;$toolBin;$env:PATH"
$env:VERILATOR_ROOT = $verilatorRoot
$resolvedMakeMatches = @(Get-Command -Name 'make.exe' -CommandType Application -All -ErrorAction Stop)
$resolvedCompilerMatches = @(Get-Command -Name 'g++.exe' -CommandType Application -All -ErrorAction Stop)
if (($resolvedMakeMatches.Count -lt 1) -or ($resolvedCompilerMatches.Count -lt 1)) {
    throw 'PATH 中未解析到 make.exe 或 g++.exe。'
}
$resolvedMakePath = [System.IO.Path]::GetFullPath([string]$resolvedMakeMatches[0].Path)
$resolvedCompilerPath = [System.IO.Path]::GetFullPath([string]$resolvedCompilerMatches[0].Path)
if ($resolvedMakePath -ine [System.IO.Path]::GetFullPath($makePath)) {
    throw "PATH 解析到批准 toolchain 之外的 make：$resolvedMakePath"
}
if ($resolvedCompilerPath -ine [System.IO.Path]::GetFullPath($compilerPath)) {
    throw "PATH 解析到批准 toolchain 之外的 g++：$resolvedCompilerPath"
}

$runDirectory = Join-Path $evidenceRoot ("runs\sample_{0:D3}\{1}" -f $SampleIndex, $RunId)
if (Test-Path -LiteralPath $runDirectory) {
    throw "拒绝复用已存在的运行目录：$runDirectory"
}
$null = New-Item -ItemType Directory -Path $runDirectory -Force:$false
$buildDirectory = Join-Path $runDirectory 'build'
$null = New-Item -ItemType Directory -Path $buildDirectory -Force:$false

$rtlRelativePaths = @(
    'src\s2a_network_descriptor_pkg.sv',
    'src\int8_maxpool_geometry.sv',
    'src\int8_maxpool_window.sv',
    'src\int8_route_query.sv',
    'src\int8_upsample_query.sv',
    'src\s2a_conv_tile_engine.sv',
    'src\s2a_maxpool_engine.sv',
    'src\s2a_route_engine.sv',
    'src\s2a_upsample_engine.sv',
    'src\s2a_network_backend.sv'
)
$rtlSources = @(
    foreach ($relativePath in $rtlRelativePaths) {
        $sourcePath = Join-Path $repoRoot $relativePath
        if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw "RTL source list 文件不存在：$sourcePath" }
        (Resolve-Path -LiteralPath $sourcePath).Path
    }
)
$compileSources = @($rtlSources) + @($testbench)
$toolingSourceRows = @(
    foreach ($sourcePath in @($runnerSource, $prepareScript, $verifyScript)) {
        $sourceItem = Get-Item -LiteralPath $sourcePath
        [ordered]@{
            path = $sourceItem.FullName
            bytes = $sourceItem.Length
            sha256 = Get-Sha256Literal -Path $sourceItem.FullName
        }
    }
)

$sourceSnapshotRows = @(
    foreach ($sourcePath in $compileSources) {
        $sourceItem = Get-Item -LiteralPath $sourcePath
        [ordered]@{
            path = $sourceItem.FullName
            bytes = $sourceItem.Length
            sha256 = Get-Sha256Literal -Path $sourceItem.FullName
        }
    }
)
$currentBackendRow = $sourceSnapshotRows | Where-Object { $_.path -eq $backendSource }
if ($null -eq $currentBackendRow -or $currentBackendRow.sha256 -ne $ExpectedBackendSha256.ToLowerInvariant()) {
    throw '编译源列表中的 backend SHA 与显式冻结值不匹配。'
}

$commandArgs = @(
    '--binary',
    '--timing',
    '-Wno-fatal',
    '--top-module', 'tb_s2a_network_backend_golden',
    '--Mdir', $buildDirectory,
    '-CFLAGS', '-D_GLIBCXX_USE_CXX11_ABI=0'
) + $compileSources
$snapshot = [ordered]@{
    schema_version = 'gestureforge_s2a_t68_compile_source_snapshot_v1'
    task_id = 'S2A-T68'
    sample_index = $SampleIndex
    run_id = $RunId
    top_module = 'tb_s2a_network_backend_golden'
    backend_sha256_expected = $ExpectedBackendSha256.ToLowerInvariant()
    source_count = $compileSources.Count
    verilator_path = $verilator
    make_path = $resolvedMakePath
    compiler_path = $resolvedCompilerPath
    verilator_root = $verilatorRoot
    toolchain_path_prefix = @($makeBin, $toolBin)
    command = @($commandArgs)
    sources = $sourceSnapshotRows
    tooling_sources = $toolingSourceRows
    simulator_started = $false
}
$snapshotPath = Join-Path $runDirectory 'compile_source_snapshot.json'
Write-Utf8NoBom -Path $snapshotPath -Content (($snapshot | ConvertTo-Json -Depth 8) + [Environment]::NewLine)

$versionStdoutPath = Join-Path $runDirectory 'verilator_version_stdout.txt'
$versionStderrPath = Join-Path $runDirectory 'verilator_version_stderr.txt'
$versionConsolePath = Join-Path $runDirectory 'verilator_version.txt'
$versionInvocation = Invoke-NativeCapturedProcess -ExecutablePath $verilator -Arguments @('--version') `
    -WorkingDirectory $repoRoot -StandardOutputPath $versionStdoutPath -StandardErrorPath $versionStderrPath
$versionExitCode = [int]$versionInvocation.exit_code
Write-NativeProcessConsole -ConsolePath $versionConsolePath -StandardOutputPath $versionStdoutPath -StandardErrorPath $versionStderrPath
$versionOutputText = [System.IO.File]::ReadAllText($versionStdoutPath, [System.Text.Encoding]::UTF8) + [Environment]::NewLine +
    [System.IO.File]::ReadAllText($versionStderrPath, [System.Text.Encoding]::UTF8)
$versionWarningCount = [regex]::Matches($versionOutputText, '(?m)^%Warning[^:\r\n]*:').Count
$versionErrorCount = [regex]::Matches($versionOutputText, '(?m)^%Error[^:\r\n]*:').Count
$versionAccepted = ($versionExitCode -eq 0) -and ($versionErrorCount -eq 0) -and [string]::IsNullOrEmpty($versionInvocation.launch_error)
$versionRecord = [ordered]@{
    schema_version = 'gestureforge_s2a_t68_verilator_version_v1'
    command = @($verilator, '--version')
    exit_code = $versionExitCode
    accepted = $versionAccepted
    launch_error = $versionInvocation.launch_error
    process_id = $versionInvocation.process_id
    warning_count = $versionWarningCount
    error_count = $versionErrorCount
    warning_text_retained = (Test-Path -LiteralPath $versionStderrPath -PathType Leaf)
    stdout_path = $versionStdoutPath
    stdout_sha256 = Get-Sha256Literal -Path $versionStdoutPath
    stderr_path = $versionStderrPath
    stderr_sha256 = Get-Sha256Literal -Path $versionStderrPath
    console_path = $versionConsolePath
    console_sha256 = Get-Sha256Literal -Path $versionConsolePath
}
$versionRecordPath = Join-Path $runDirectory 'verilator_version_record.json'
Write-Utf8NoBom -Path $versionRecordPath -Content (($versionRecord | ConvertTo-Json -Depth 4) + [Environment]::NewLine)
if (-not $versionAccepted) {
    if ($versionExitCode -eq 0) { $versionExitCode = 125 }
    exit $versionExitCode
}

$compileLog = Join-Path $runDirectory 'verilator_compile_console.txt'
$compileStdoutPath = Join-Path $runDirectory 'verilator_compile_stdout.txt'
$compileStderrPath = Join-Path $runDirectory 'verilator_compile_stderr.txt'
$compileWatch = [System.Diagnostics.Stopwatch]::StartNew()
$compileInvocation = Invoke-NativeCapturedProcess -ExecutablePath $verilator -Arguments $commandArgs `
    -WorkingDirectory $repoRoot -StandardOutputPath $compileStdoutPath -StandardErrorPath $compileStderrPath
$compileNativeExitCode = [int]$compileInvocation.exit_code
$compileWatch.Stop()
Write-NativeProcessConsole -ConsolePath $compileLog -StandardOutputPath $compileStdoutPath -StandardErrorPath $compileStderrPath
$compileOutputText = [System.IO.File]::ReadAllText($compileStdoutPath, [System.Text.Encoding]::UTF8) + [Environment]::NewLine +
    [System.IO.File]::ReadAllText($compileStderrPath, [System.Text.Encoding]::UTF8)
$compileWarningCount = [regex]::Matches($compileOutputText, '(?m)^%Warning[^:\r\n]*:').Count
$compileErrorCount = [regex]::Matches($compileOutputText, '(?m)^%Error[^:\r\n]*:').Count
$compileAccepted = ($compileNativeExitCode -eq 0) -and ($compileErrorCount -eq 0) -and [string]::IsNullOrEmpty($compileInvocation.launch_error)
$compileExitCode = $compileNativeExitCode
if (-not $compileAccepted -and ($compileExitCode -eq 0)) { $compileExitCode = 125 }
$postCompileSourceRows = @(
    foreach ($sourcePath in $compileSources) {
        $sourceItem = Get-Item -LiteralPath $sourcePath
        [ordered]@{
            path = $sourceItem.FullName
            bytes = $sourceItem.Length
            sha256 = Get-Sha256Literal -Path $sourceItem.FullName
        }
    }
)
$postCompileToolingSourceRows = @(
    foreach ($sourcePath in @($runnerSource, $prepareScript, $verifyScript)) {
        $sourceItem = Get-Item -LiteralPath $sourcePath
        [ordered]@{
            path = $sourceItem.FullName
            bytes = $sourceItem.Length
            sha256 = Get-Sha256Literal -Path $sourceItem.FullName
        }
    }
)
$compileRecord = [ordered]@{
    schema_version = 'gestureforge_s2a_t68_compile_execution_v1'
    sample_index = $SampleIndex
    run_id = $RunId
    backend_sha256_expected = $ExpectedBackendSha256.ToLowerInvariant()
    runner_path = $runnerSource
    runner_sha256 = Get-Sha256Literal -Path $runnerSource
    command = @($verilator) + @($commandArgs)
    verilator_path = $verilator
    make_path = $resolvedMakePath
    compiler_path = $resolvedCompilerPath
    verilator_root = $verilatorRoot
    exit_code = $compileExitCode
    native_exit_code = $compileNativeExitCode
    compile_accepted = $compileAccepted
    launch_error = $compileInvocation.launch_error
    warning_count = $compileWarningCount
    error_count = $compileErrorCount
    warning_text_retained = (Test-Path -LiteralPath $compileStderrPath -PathType Leaf)
    duration_seconds = [Math]::Round($compileWatch.Elapsed.TotalSeconds, 3)
    source_unchanged = (($sourceSnapshotRows | ConvertTo-Json -Depth 5 -Compress) -ceq ($postCompileSourceRows | ConvertTo-Json -Depth 5 -Compress))
    tooling_sources = $toolingSourceRows
    tooling_sources_after = $postCompileToolingSourceRows
    tooling_sources_unchanged = (($toolingSourceRows | ConvertTo-Json -Depth 5 -Compress) -ceq ($postCompileToolingSourceRows | ConvertTo-Json -Depth 5 -Compress))
    sources_after = $postCompileSourceRows
    console_path = $compileLog
    console_sha256 = Get-Sha256Literal -Path $compileLog
    stdout_path = $compileStdoutPath
    stdout_sha256 = Get-Sha256Literal -Path $compileStdoutPath
    stderr_path = $compileStderrPath
    stderr_sha256 = Get-Sha256Literal -Path $compileStderrPath
    warning_gate = '-Wno-fatal'
    version_record_path = $versionRecordPath
    version_record_sha256 = Get-Sha256Literal -Path $versionRecordPath
    simulator_started = $false
}
$compileRecordPath = Join-Path $runDirectory 'compile_execution_record.json'
Write-Utf8NoBom -Path $compileRecordPath -Content (($compileRecord | ConvertTo-Json -Depth 8) + [Environment]::NewLine)
if (-not $compileRecord.source_unchanged -or -not $compileRecord.tooling_sources_unchanged) {
    throw "RTL compile 期间输入源发生变化；记录已保留：$compileRecordPath"
}
if (-not $compileAccepted -or ($compileExitCode -ne 0)) { exit $compileExitCode }

if ($RunSimulation) {
    $fixtureDirectory = Join-Path $evidenceRoot ("fixtures\sample_{0:D3}" -f $SampleIndex)
    $binary = Join-Path $buildDirectory 'Vtb_s2a_network_backend_golden.exe'
    if (-not (Test-Path -LiteralPath $binary -PathType Leaf)) { throw "Verilator 未生成预期 binary：$binary" }
    $resultPath = Join-Path $runDirectory 'result_summary.txt'
    $progressMarkerPath = Join-Path $runDirectory 'progress_markers.txt'
    $head13Path = Join-Path $runDirectory 'head13_actual_int8.bin'
    $head26Path = Join-Path $runDirectory 'head26_actual_int8.bin'
    $simulationArgs = @(
        "+SAMPLE_INDEX=$SampleIndex",
        "+FIXTURE_DIR=$fixtureDirectory",
        "+MAX_CYCLES=$MaxCycles",
        "+RESULT_FILE=$resultPath",
        "+PROGRESS_FILE=$progressMarkerPath",
        "+HEAD13_FILE=$head13Path",
        "+HEAD26_FILE=$head26Path"
    )
    $simulationLog = Join-Path $runDirectory 'verilator_simulation_console.txt'
    $simulationErrorLog = Join-Path $runDirectory 'verilator_simulation_stderr.txt'
    $simulationWatch = [System.Diagnostics.Stopwatch]::StartNew()
    $quotedSimulationArguments = ($simulationArgs | ForEach-Object { Quote-ProcessArgument -Argument ([string]$_) }) -join ' '
    $simProcess = Start-Process -FilePath $binary -ArgumentList $quotedSimulationArguments `
        -WorkingDirectory $buildDirectory -WindowStyle Hidden `
        -RedirectStandardOutput $simulationLog -RedirectStandardError $simulationErrorLog -PassThru
    $processStartTimeUtc = $simProcess.StartTime.ToUniversalTime()
    $lastProgressAtUtc = $processStartTimeUtc
    $lastProgressSignature = ''
    $processedMarkerCount = 0
    $progressMarkerCount = 0
    $previousProgressCycle = -1L
    $firstProgressPhase = ''
    $lastProgressPhase = ''
    $functionalProgressObserved = $false
    $badProgressMarkerSeen = $false
    $watchdogFailure = $false
    $watchdogTerminationReason = 'PROCESS_EXITED'
    $identityVerifiedAtTimeout = $false
    $killRequested = $false
    while ($true) {
        $simProcess.Refresh()
        $processExited = $simProcess.HasExited
        $progressRead = Get-CompleteProgressMarkerLines -Path $progressMarkerPath
        if ($progressRead.readable) {
            $progressLines = @($progressRead.lines)
            if ($progressLines.Count -lt $processedMarkerCount) {
                $badProgressMarkerSeen = $true
            } else {
                for ($markerIndex = $processedMarkerCount; $markerIndex -lt $progressLines.Count; $markerIndex++) {
                    $progressMarker = ConvertFrom-ProgressMarker -Line ([string]$progressLines[$markerIndex])
                    if ($null -eq $progressMarker) {
                        $badProgressMarkerSeen = $true
                        $processedMarkerCount++
                        continue
                    }
                    $phaseSequenceValid = if ($progressMarkerCount -eq 0) {
                        $progressMarker.phase -eq 'start'
                    } else {
                        ($progressMarker.phase -ne 'start') -and ($lastProgressPhase -ne 'complete')
                    }
                    if (($progressMarker.sample -ne $SampleIndex) -or
                        ($progressMarker.layer -lt 0) -or ($progressMarker.layer -ge 38) -or
                        ($progressMarker.cycle -lt $previousProgressCycle) -or
                        ($progressMarker.cycle -gt $MaxCycles) -or (-not $phaseSequenceValid)) {
                        $badProgressMarkerSeen = $true
                        $processedMarkerCount++
                        continue
                    }
                    if ($progressMarkerCount -eq 0) {
                        $firstProgressPhase = $progressMarker.phase
                        $lastProgressSignature = $progressMarker.signature
                    } else {
                        if (Test-ProgressSignatureChanged -PreviousSignature $lastProgressSignature `
                            -CurrentSignature $progressMarker.signature) {
                            $lastProgressAtUtc = [datetime]::UtcNow
                            $functionalProgressObserved = $true
                        }
                        $lastProgressSignature = $progressMarker.signature
                    }
                    $previousProgressCycle = $progressMarker.cycle
                    $lastProgressPhase = $progressMarker.phase
                    $progressMarkerCount++
                    $processedMarkerCount++
                }
            }
        }
        if ($processExited) { break }
        if (([datetime]::UtcNow - $lastProgressAtUtc).TotalSeconds -ge 1800) {
            $watchdogFailure = $true
            $identityVerifiedAtTimeout = Test-StartedProcessIdentity -Process $simProcess `
                -ExpectedPath $binary -ExpectedArguments $simulationArgs -ExpectedStartTimeUtc $processStartTimeUtc
            if ($identityVerifiedAtTimeout) {
                $watchdogTerminationReason = 'NO_PROGRESS_30_MINUTES_IDENTITY_VERIFIED_KILLED_OWN_PROCESS'
                try {
                    $simProcess.Kill()
                    $killRequested = $true
                    $simProcess.WaitForExit()
                } catch {
                    $watchdogTerminationReason = 'NO_PROGRESS_30_MINUTES_IDENTITY_VERIFIED_KILL_FAILED'
                }
            } else {
                $watchdogTerminationReason = 'NO_PROGRESS_30_MINUTES_IDENTITY_UNVERIFIED_NOT_KILLED'
            }
            break
        }
        Start-Sleep -Seconds 5
    }
    $simProcess.Refresh()
    $simulationExitCode = if ($simProcess.HasExited) { $simProcess.ExitCode } else { $null }
    $simulationWatch.Stop()
    $progressMarkersValid = (-not $badProgressMarkerSeen) -and ($progressMarkerCount -ge 2) -and
        $functionalProgressObserved -and ($firstProgressPhase -eq 'start')
    if (-not $watchdogFailure -and ((-not $progressMarkersValid) -or ($lastProgressPhase -ne 'complete'))) {
        $watchdogTerminationReason = 'PROCESS_EXITED_WITHOUT_VALID_COMPLETE_PROGRESS'
    }
    $runnerExitCode = 0
    if ($watchdogFailure) {
        $runnerExitCode = 124
    } elseif (($simulationExitCode -ne 0) -or (-not $progressMarkersValid) -or ($lastProgressPhase -ne 'complete')) {
        $runnerExitCode = if ($simulationExitCode -and $simulationExitCode -ne 0) { $simulationExitCode } else { 125 }
    }
    $resultSummaryValid = $false
    if (($runnerExitCode -eq 0) -and (Test-Path -LiteralPath $resultPath -PathType Leaf)) {
        $resultSummary = [System.IO.File]::ReadAllText($resultPath, [System.Text.Encoding]::UTF8)
        $resultSummaryValid = Test-S2aNetworkBackendResultSummary -Text $resultSummary
        if (-not $resultSummaryValid) {
            $runnerExitCode = 125
            $watchdogTerminationReason = 'RESULT_SUMMARY_INVALID'
        }
    } elseif ($runnerExitCode -eq 0) {
        $runnerExitCode = 125
        $watchdogTerminationReason = 'RESULT_SUMMARY_MISSING'
    }
    $head13Bytes = $null
    $head13Sha256 = $null
    $head26Bytes = $null
    $head26Sha256 = $null
    $headExportsValid = $false
    if (($runnerExitCode -eq 0) -and (Test-Path -LiteralPath $head13Path -PathType Leaf) -and
        (Test-Path -LiteralPath $head26Path -PathType Leaf)) {
        $head13Bytes = (Get-Item -LiteralPath $head13Path).Length
        $head26Bytes = (Get-Item -LiteralPath $head26Path).Length
        if (($head13Bytes -eq 5070) -and ($head26Bytes -eq 20280)) {
            $head13Sha256 = Get-Sha256Literal -Path $head13Path
            $head26Sha256 = Get-Sha256Literal -Path $head26Path
            $headExportsValid = $true
        }
    }
    if (($runnerExitCode -eq 0) -and (-not $headExportsValid)) {
        $runnerExitCode = 125
        $watchdogTerminationReason = 'HEAD_EXPORT_INVALID'
    }
    $simulationRecord = [ordered]@{
        schema_version = 'gestureforge_s2a_t68_simulation_execution_v1'
        command = @($binary) + @($simulationArgs)
        exit_code = $simulationExitCode
        runner_exit_code = $runnerExitCode
        duration_seconds = [Math]::Round($simulationWatch.Elapsed.TotalSeconds, 3)
        sample_index = $SampleIndex
        run_id = $RunId
        runner_path = $runnerSource
        runner_sha256 = Get-Sha256Literal -Path $runnerSource
        tooling_sources = $toolingSourceRows
        compile_source_snapshot_path = $snapshotPath
        compile_source_snapshot_sha256 = Get-Sha256Literal -Path $snapshotPath
        compile_execution_record_path = $compileRecordPath
        compile_execution_record_sha256 = Get-Sha256Literal -Path $compileRecordPath
        result_summary_path = $resultPath
        result_summary_sha256 = if (Test-Path -LiteralPath $resultPath -PathType Leaf) { Get-Sha256Literal -Path $resultPath } else { $null }
        console_path = $simulationLog
        console_sha256 = if (Test-Path -LiteralPath $simulationLog -PathType Leaf) { Get-Sha256Literal -Path $simulationLog } else { $null }
        stderr_path = $simulationErrorLog
        stderr_sha256 = if (Test-Path -LiteralPath $simulationErrorLog -PathType Leaf) { Get-Sha256Literal -Path $simulationErrorLog } else { $null }
        progress_marker_path = $progressMarkerPath
        progress_marker_sha256 = if (Test-Path -LiteralPath $progressMarkerPath -PathType Leaf) { Get-Sha256Literal -Path $progressMarkerPath } else { $null }
        progress_marker_count = $progressMarkerCount
        progress_markers_valid = $progressMarkersValid
        functional_progress_observed = $functionalProgressObserved
        bad_progress_marker_seen = $badProgressMarkerSeen
        last_progress_phase = $lastProgressPhase
        last_progress_signature = $lastProgressSignature
        result_summary_valid = $resultSummaryValid
        head_exports_valid = $headExportsValid
        head13_export = [ordered]@{ path = $head13Path; bytes = $head13Bytes; sha256 = $head13Sha256 }
        head26_export = [ordered]@{ path = $head26Path; bytes = $head26Bytes; sha256 = $head26Sha256 }
        progress_interval_cycles = 30000000
        watchdog_no_progress_seconds = 1800
        watchdog_failure = $watchdogFailure
        watchdog_termination_reason = $watchdogTerminationReason
        identity_verified_at_timeout = $identityVerifiedAtTimeout
        kill_requested = $killRequested
        process_id = $simProcess.Id
        process_start_time_utc = $processStartTimeUtc.ToString('o')
        process_executable_path = $binary
        wave_dump_requested = $false
    }
    $simulationRecordPath = Join-Path $runDirectory 'simulation_execution_record.json'
    Write-Utf8NoBom -Path $simulationRecordPath -Content (($simulationRecord | ConvertTo-Json -Depth 5) + [Environment]::NewLine)
    Write-Output "T68 sample=$SampleIndex simulation exit_code=$simulationExitCode runner_exit_code=$runnerExitCode duration_seconds=$($simulationRecord.duration_seconds) watchdog=$watchdogTerminationReason"
    if ($runnerExitCode -ne 0) { exit $runnerExitCode }
}

Write-Output "T68 runner 完成；run_directory=$runDirectory compile_exit_code=$compileExitCode simulation_started=$RunSimulation"
exit 0
