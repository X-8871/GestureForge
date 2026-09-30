[CmdletBinding()]
param(
    [switch]$PrepareOnly,
    [switch]$RunSimulation
)

$ErrorActionPreference = 'Stop'

$rootPath = 'D:\FPGA_Competition'
$t64BaselineCommit = 'ec686741e0553ebc4a8701129e381526e0b06974'
$evidenceRootPath = 'D:\FPGA_Competition\report\evidence\S2A-T65'
$runPath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02'
$pythonTestPath = 'D:\FPGA_Competition\verification\test_s2a_t65_layer0_golden.py'
$vivadoBinPath = 'D:\Xilinx\2026.1\Vivado\bin'
$passMarker = 'PASS: sample0 layer0 首个输出字节 memory-read/write matched T25'

if ($PrepareOnly -and $RunSimulation) {
    throw 'PrepareOnly 与 RunSimulation 不能同时指定。'
}

$rootItem = Get-Item -LiteralPath $rootPath -ErrorAction Stop
if (-not $rootItem.PSIsContainer -or $rootItem.FullName -cne $rootPath) {
    throw "项目根目录与任务卡精确路径不匹配：$($rootItem.FullName)"
}
$evidenceRootItem = Get-Item -LiteralPath $evidenceRootPath -ErrorAction Stop
if (-not $evidenceRootItem.PSIsContainer -or $evidenceRootItem.FullName -cne $evidenceRootPath) {
    throw "T65 evidence 目录类型或完整路径不匹配：$($evidenceRootItem.FullName)"
}
$actualHead = (git -C $rootPath rev-parse HEAD).Trim()
$headReadExit = $LASTEXITCODE
if ($headReadExit -ne 0 -or $actualHead -notmatch '^[0-9a-f]{40}$') {
    throw "无法读取当前项目 HEAD：exit=$headReadExit actual=$actualHead"
}
git -C $rootPath merge-base --is-ancestor $t64BaselineCommit $actualHead
$baselineAncestorExit = $LASTEXITCODE
if ($baselineAncestorExit -ne 0) {
    throw "当前 HEAD 不包含冻结 T64 基线：baseline=$t64BaselineCommit actual=$actualHead exit=$baselineAncestorExit"
}
$runItem = Get-Item -LiteralPath $runPath -ErrorAction SilentlyContinue
if ($runItem -and (-not $runItem.PSIsContainer -or $runItem.FullName -cne $runPath)) {
    throw "T65 runPath 类型或完整路径不匹配：$($runItem.FullName)"
}
if (-not $runItem) {
    New-Item -ItemType Directory -Path $runPath | Out-Null
}
$runItem = Get-Item -LiteralPath $runPath -ErrorAction Stop
if (-not $runItem.PSIsContainer -or $runItem.FullName -cne $runPath) {
    throw "T65 runPath 类型或完整路径不匹配：$($runItem.FullName)"
}
$simPath = Join-Path $runPath 'sim01'
if ($RunSimulation -and (Test-Path -LiteralPath $simPath)) {
    throw "T65_SIM_PATH_COLLISION: 仿真证据目录已存在，拒绝覆盖：$simPath"
}
$tempPath = Join-Path $runPath 'temp'
if (-not (Test-Path -LiteralPath $tempPath -PathType Container)) {
    New-Item -ItemType Directory -Path $tempPath | Out-Null
}
$env:TEMP = $tempPath
$env:TMP = $tempPath
$env:TMPDIR = $tempPath
$env:PYTHONDONTWRITEBYTECODE = '1'

$pythonCommand = Get-Command -Name 'python' -CommandType Application -ErrorAction Stop |
    Where-Object { $_.Source -notlike '*\WindowsApps\python.exe' } |
    Select-Object -First 1
if (-not $pythonCommand) {
    throw '未找到可执行的 Python 3.12 环境。'
}
Write-Output "冻结 T64 基线：$t64BaselineCommit"
Write-Output "执行 HEAD：$actualHead"
Write-Output "临时目录：$tempPath"
Write-Output '运行 sample0 输入重建、GF8 layer0 切片、T25 golden 映射及离线逐点复算。'
& $pythonCommand.Source -B $pythonTestPath --evidence-dir $runPath
if ($LASTEXITCODE -ne 0) {
    throw "T65 离线夹具检查失败，Python exit=$LASTEXITCODE"
}

if (-not $RunSimulation) {
    Write-Output 'PREPARE_ONLY：未调用 Vivado/XSim。'
    exit 0
}

$toolPaths = @(
    (Join-Path $vivadoBinPath 'xvlog.bat'),
    (Join-Path $vivadoBinPath 'xelab.bat'),
    (Join-Path $vivadoBinPath 'xsim.bat')
)
foreach ($toolPath in $toolPaths) {
    $toolItem = Get-Item -LiteralPath $toolPath -ErrorAction Stop
    if ($toolItem.PSIsContainer) {
        throw "Vivado 工具路径不是文件：$($toolItem.FullName)"
    }
}

if (Test-Path -LiteralPath $simPath) {
    throw "T65_SIM_PATH_COLLISION: 仿真证据目录已存在，拒绝覆盖：$simPath"
}
New-Item -ItemType Directory -Path $simPath -ErrorAction Stop | Out-Null
$simDirectory = Get-Item -LiteralPath $simPath -ErrorAction Stop
if (-not $simDirectory.PSIsContainer -or $simDirectory.FullName -cne $simPath) {
    throw "T65_SIM_PATH_MISMATCH: 新建仿真目录类型或完整路径不匹配：$($simDirectory.FullName)"
}

$sourcePaths = @(
    'D:\FPGA_Competition\src\s2a_network_descriptor_pkg.sv',
    'D:\FPGA_Competition\src\int8_conv_tap_geometry.sv',
    'D:\FPGA_Competition\src\int8_conv_weight_address.sv',
    'D:\FPGA_Competition\src\int8_mac_accumulator.sv',
    'D:\FPGA_Competition\src\int8_maxpool_geometry.sv',
    'D:\FPGA_Competition\src\int8_maxpool_window.sv',
    'D:\FPGA_Competition\src\int8_route_query.sv',
    'D:\FPGA_Competition\src\int8_upsample_query.sv',
    'D:\FPGA_Competition\src\s2a_conv_engine.sv',
    'D:\FPGA_Competition\src\s2a_maxpool_engine.sv',
    'D:\FPGA_Competition\src\s2a_route_engine.sv',
    'D:\FPGA_Competition\src\s2a_upsample_engine.sv',
    'D:\FPGA_Competition\src\s2a_control_csr.sv',
    'D:\FPGA_Competition\src\s2a_network_backend.sv',
    'D:\FPGA_Competition\sim\tb_s2a_t65_layer0_golden.sv'
)
foreach ($sourcePath in $sourcePaths) {
    $sourceItem = Get-Item -LiteralPath $sourcePath -ErrorAction Stop
    if ($sourceItem.PSIsContainer) {
        throw "仿真输入不是普通文件：$($sourceItem.FullName)"
    }
}

$xvlogConsole = Join-Path $simPath 'xvlog_console.txt'
$xelabConsole = Join-Path $simPath 'xelab_console.txt'
$xsimConsole = Join-Path $simPath 'xsim_console.txt'
$xvlogLog = Join-Path $simPath 'xvlog.log'
$xelabLog = Join-Path $simPath 'xelab.log'
$xsimLog = Join-Path $simPath 'xsim.log'
$snapshotName = 's2a_t65_layer0_golden_snapshot'
$statusPath = Join-Path $simPath 'status.txt'

Push-Location -LiteralPath $simPath
try {
    Write-Output '在独立 T65 evidence 工作目录编译冻结 T64 backend 和 T65 bench。'
    & (Join-Path $vivadoBinPath 'xvlog.bat') -sv -work xil_defaultlib @sourcePaths *> $xvlogConsole
    $xvlogExit = $LASTEXITCODE
    if ($xvlogExit -ne 0 -or -not (Test-Path -LiteralPath $xvlogLog -PathType Leaf)) {
        Set-Content -LiteralPath $statusPath -Value "XVLOG_FAIL exit=$xvlogExit" -Encoding utf8
        throw "xvlog 失败，exit=$xvlogExit；日志：$xvlogConsole"
    }
    if (Select-String -LiteralPath $xvlogLog -Pattern 'ERROR:|FATAL:' -Quiet) {
        Set-Content -LiteralPath $statusPath -Value 'XVLOG_LOG_FAIL' -Encoding utf8
        throw "xvlog 日志存在 ERROR/FATAL：$xvlogLog"
    }

    Write-Output '在独立 snapshot 中 elaboration。'
    & (Join-Path $vivadoBinPath 'xelab.bat') -mt off -debug typical xil_defaultlib.tb_s2a_t65_layer0_golden -s $snapshotName -log $xelabLog *> $xelabConsole
    $xelabExit = $LASTEXITCODE
    if ($xelabExit -ne 0 -or -not (Test-Path -LiteralPath $xelabLog -PathType Leaf)) {
        Set-Content -LiteralPath $statusPath -Value "XELAB_FAIL exit=$xelabExit" -Encoding utf8
        throw "xelab 失败，exit=$xelabExit；日志：$xelabConsole"
    }
    if (Select-String -LiteralPath $xelabLog -Pattern 'ERROR:|FATAL:' -Quiet) {
        Set-Content -LiteralPath $statusPath -Value 'XELAB_LOG_FAIL' -Encoding utf8
        throw "xelab 日志存在 ERROR/FATAL：$xelabLog"
    }

    Write-Output '运行 sample0 layer0 首个输出点；bench 有界结束，不推进整层。'
    & (Join-Path $vivadoBinPath 'xsim.bat') $snapshotName -R -log $xsimLog *> $xsimConsole
    $xsimExit = $LASTEXITCODE
    if ($xsimExit -ne 0 -or -not (Test-Path -LiteralPath $xsimLog -PathType Leaf)) {
        Set-Content -LiteralPath $statusPath -Value "XSIM_FAIL exit=$xsimExit" -Encoding utf8
        throw "xsim 失败，exit=$xsimExit；日志：$xsimConsole"
    }
    if (Select-String -LiteralPath $xsimLog -Pattern 'ERROR:|FATAL:' -Quiet) {
        Set-Content -LiteralPath $statusPath -Value 'XSIM_LOG_FAIL' -Encoding utf8
        throw "xsim 日志存在 ERROR/FATAL：$xsimLog"
    }
    if (-not (Select-String -LiteralPath $xsimLog -SimpleMatch -Pattern $passMarker -Quiet)) {
        Set-Content -LiteralPath $statusPath -Value 'PASS_MARKER_MISSING' -Encoding utf8
        throw "xsim 未输出预期 PASS 标记：$xsimLog"
    }
    Set-Content -LiteralPath $statusPath -Value 'PASS_SAMPLE0_LAYER0_POINT0_ONLY' -Encoding utf8
    Write-Output "PASS：$passMarker"
    Write-Output "运行日志：$simPath"
}
finally {
    Pop-Location
}
