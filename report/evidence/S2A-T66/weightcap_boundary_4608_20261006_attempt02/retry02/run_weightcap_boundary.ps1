Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$evidence = 'D:\FPGA_Competition\report\evidence\S2A-T66\weightcap_boundary_4608_20261006_attempt02\retry02'
$dut = 'D:\FPGA_Competition\src\s2a_conv_tile_engine.sv'
$package = 'D:\FPGA_Competition\src\s2a_network_descriptor_pkg.sv'
$bench = 'D:\FPGA_Competition\report\evidence\S2A-T66\weightcap_boundary_4608_20261006_attempt02\retry02\tb_s2a_weightcap_boundary.sv'
$verilator = 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin\verilator_bin.exe'
$toolBin = 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\bin'
$makeBin = 'D:\FPGA_S2A_MSYS2_20261001\env\usr\bin'
$verilatorRoot = 'D:\FPGA_S2A_MSYS2_20261001\env\mingw64\share\verilator'
$python = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$build = Join-Path $evidence 'build'
$utf8 = [System.Text.UTF8Encoding]::new($false)
function Write-NewText([string]$Path, [string]$Text) {
    $s = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try { $b = $utf8.GetBytes($Text); $s.Write($b, 0, $b.Length); $s.Flush() } finally { $s.Dispose() }
}
function Write-NewJson([string]$Path, [object]$Value) {
    Write-NewText $Path (($Value | ConvertTo-Json -Depth 12) + [Environment]::NewLine)
}
function Get-Sha([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
foreach ($p in @($evidence, (Split-Path -Parent $dut), (Split-Path -Parent $package),
                  (Split-Path -Parent $bench), $toolBin, $makeBin, $verilatorRoot)) {
    $i = Get-Item -LiteralPath $p
    if (-not $i.PSIsContainer -or $i.FullName -cne $p) { throw "目录路径核验失败：$p" }
}
foreach ($p in @($dut, $package, $bench, $verilator, (Join-Path $makeBin 'make.exe'),
                  (Join-Path $toolBin 'g++.exe'), $python)) {
    $i = Get-Item -LiteralPath $p
    if ($i.PSIsContainer -or $i.FullName -cne $p) { throw "文件路径核验失败：$p" }
}
if (Test-Path -LiteralPath $build) { throw "拒绝复用已有构建目录：$build" }
$null = [System.IO.Directory]::CreateDirectory($build)
$env:PATH = "$makeBin;$toolBin;$env:PATH"
$env:VERILATOR_ROOT = $verilatorRoot
$pythonMakeFlag = "PYTHON3='/c/Users/22061/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'"
$compileArgs = @('--binary','--timing','-Wno-fatal','-j','1','--threads','1',
                 '--top-module','tb_s2a_weightcap_boundary','--Mdir',$build,
                 '-MAKEFLAGS',$pythonMakeFlag,'-CFLAGS','-D_GLIBCXX_USE_CXX11_ABI=0',
                 $package,$dut,$bench)
$compileLog = Join-Path $evidence 'compile_console.txt'
$compileWatch = [System.Diagnostics.Stopwatch]::StartNew()
$previousPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = 'Continue'
    $compileOutput = @(& $verilator @compileArgs 2>&1 | ForEach-Object { [string]$_ })
    $compileExit = [int]$LASTEXITCODE
}
finally { $ErrorActionPreference = $previousPreference }
$compileWatch.Stop()
$compileText = $compileOutput -join [Environment]::NewLine
$warningRows = @(
    foreach ($match in [regex]::Matches($compileText, '%Warning-([A-Z0-9_]+):\s+([^\r\n]+)')) {
        [PSCustomObject]@{ category = $match.Groups[1].Value; detail = $match.Groups[2].Value.Trim() }
    }
)
$expectedTimescaleWarning = ($warningRows.Count -eq 1) -and
    ($warningRows[0].category -ceq 'TIMESCALEMOD') -and
    ($warningRows[0].detail -match '^D:\\FPGA_Competition\\src\\s2a_network_descriptor_pkg\.sv:\d+:\d+:\s+Timescale missing on this module as other modules have it')
$warningGatePassed = ($warningRows.Count -eq 0) -or $expectedTimescaleWarning
Write-NewText $compileLog (($compileOutput -join [Environment]::NewLine) + [Environment]::NewLine)
$compileRecord = [ordered]@{
    schema_version = 's2a_t66_weightcap_boundary_compile_v1'
    dut_sha256 = Get-Sha $dut
    package_sha256 = Get-Sha $package
    testbench_sha256 = Get-Sha $bench
    command = @($verilator) + $compileArgs
    exit_code = $compileExit
    duration_seconds = [Math]::Round($compileWatch.Elapsed.TotalSeconds, 3)
    warning_rows = $warningRows
    warning_gate_passed = [bool]$warningGatePassed
    console_path = $compileLog
    simulator_started = $false
}
$compileRecordPath = Join-Path $evidence 'compile_execution_record.json'
Write-NewJson $compileRecordPath $compileRecord
if ($compileExit -ne 0) { exit $compileExit }
if (-not $warningGatePassed) { exit 1 }
$simulator = Join-Path $build 'Vtb_s2a_weightcap_boundary.exe'
if (-not (Test-Path -LiteralPath $simulator -PathType Leaf)) { throw "仿真程序未生成：$simulator" }
$simLog = Join-Path $evidence 'simulation_console.txt'
$simWatch = [System.Diagnostics.Stopwatch]::StartNew()
$simOutput = @(& $simulator 2>&1 | ForEach-Object { [string]$_ })
$simExit = [int]$LASTEXITCODE
$simWatch.Stop()
Write-NewText $simLog (($simOutput -join [Environment]::NewLine) + [Environment]::NewLine)
$simText = $simOutput -join [Environment]::NewLine
$pass = ($simExit -eq 0) -and
        $simText.Contains('K4608_PASS') -and
        $simText.Contains('K4609_REJECT_PASS') -and
        $simText.Contains('PASS: exact K boundary 4608 reaches and reads/writes lane RAM index 4607; K=4609 is rejected before memory access')
$simRecord = [ordered]@{
    schema_version = 's2a_t66_weightcap_boundary_simulation_v1'
    dut_sha256 = Get-Sha $dut
    package_sha256 = Get-Sha $package
    testbench_sha256 = Get-Sha $bench
    compile_record_sha256 = Get-Sha $compileRecordPath
    command = @($simulator)
    exit_code = $simExit
    duration_seconds = [Math]::Round($simWatch.Elapsed.TotalSeconds, 3)
    k4608_pass_marker = [bool]$simText.Contains('K4608_PASS')
    k4609_reject_marker = [bool]$simText.Contains('K4609_REJECT_PASS')
    boundary_passed = [bool]$pass
    console_path = $simLog
}
$simRecordPath = Join-Path $evidence 'simulation_execution_record.json'
Write-NewJson $simRecordPath $simRecord
if (-not $pass) { exit $(if ($simExit -ne 0) { $simExit } else { 1 }) }
Write-Output "PASS_WEIGHTCAP_BOUNDARY evidence=$evidence duration_seconds=$($simRecord.duration_seconds)"