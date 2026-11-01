[CmdletBinding()]
param(
    [switch]$PrepareOnly,
    [switch]$RunSimulation
)

$ErrorActionPreference = 'Stop'

function Write-NewOrVerifyUtf8 {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )
    $encoding = [System.Text.UTF8Encoding]::new($false)
    if (Test-Path -LiteralPath $Path) {
        $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
        if ($item.PSIsContainer) {
            throw "准备证据目标不是文件：$Path"
        }
        $existingText = [System.IO.File]::ReadAllText($Path, $encoding)
        if ($existingText -cne $Text) {
            throw "SIM02_PREPARATION_COLLISION: 已有准备证据内容不同，拒绝覆盖：$Path"
        }
        return
    }
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

$rootPath = 'D:\FPGA_Competition'
$t64BaselineCommit = 'ec686741e0553ebc4a8701129e381526e0b06974'
$evidenceRootPath = 'D:\FPGA_Competition\report\evidence\S2A-T65'
$runPath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02'
$pythonTestPath = 'D:\FPGA_Competition\verification\test_s2a_t65_layer0_golden.py'
$vivadoBinPath = 'D:\Xilinx\2026.1\Vivado\bin'
$processGuardModulePath = 'D:\FPGA_Competition\verification\t65_xilinx_process_guard.ps1'
$processAllowlistPath = 'D:\FPGA_Competition\report\evidence\S2A-T65\run02\process_identity_allowlist.json'
$processGuardModuleExpectedSha256 = 'e9103032f4a61ece7e58fd8570c786cfb4ddc8be6e9029c8e7d595932a13dca9'
$processAllowlistExpectedSha256 = 'bc743da5ac3d3b2a2e493f3b1b23bf8cc0dfce3913e179062022806797aa090e'
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
$simPath = Join-Path $runPath 'sim02'
if ($RunSimulation -and (Test-Path -LiteralPath $simPath)) {
    throw "T65_SIM_PATH_COLLISION: 仿真证据目录已存在，拒绝覆盖：$simPath"
}
$preparationEvidencePath = Join-Path $runPath 'sim02_preparation_process_guarded.json'
if ($RunSimulation) {
    New-Item -ItemType Directory -Path $simPath -ErrorAction Stop | Out-Null
    $simCreatedDirectory = Get-Item -LiteralPath $simPath -ErrorAction Stop
    if (-not $simCreatedDirectory.PSIsContainer -or $simCreatedDirectory.FullName -cne $simPath -or
        ($simCreatedDirectory.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "T65_SIM_PATH_MISMATCH: 新建仿真目录类型、完整路径或重解析状态不符合要求：$($simCreatedDirectory.FullName)"
    }
    $tempPath = Join-Path $simPath 'temp'
}
else {
    $tempPath = Join-Path $runPath 'temp'
}
if (-not (Test-Path -LiteralPath $tempPath -PathType Container)) {
    New-Item -ItemType Directory -Path $tempPath | Out-Null
}
$xilinxLocalUserDataPath = Join-Path $tempPath 'xilinx_local_user_data'
$homePath = Join-Path $tempPath 'home'
$appDataPath = Join-Path $tempPath 'appdata'
$localAppDataPath = Join-Path $tempPath 'localappdata'
foreach ($directoryPath in @($tempPath, $xilinxLocalUserDataPath, $homePath, $appDataPath, $localAppDataPath)) {
    if (-not (Test-Path -LiteralPath $directoryPath -PathType Container)) {
        New-Item -ItemType Directory -Path $directoryPath -ErrorAction Stop | Out-Null
    }
    $directoryItem = Get-Item -LiteralPath $directoryPath -ErrorAction Stop
    $directoryFullPath = [IO.Path]::GetFullPath($directoryItem.FullName)
    $tempFullPath = [IO.Path]::GetFullPath($tempPath)
    $tempFullPathPrefix = [IO.Path]::GetFullPath($tempPath).TrimEnd('\') + '\'
    $isTempRoot = $directoryFullPath.Equals($tempFullPath, [StringComparison]::OrdinalIgnoreCase)
    $isTempChild = $directoryFullPath.StartsWith($tempFullPathPrefix, [StringComparison]::OrdinalIgnoreCase)
    if (-not $directoryItem.PSIsContainer -or $directoryItem.FullName -cne $directoryPath -or
        ($directoryItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -or
        -not ($directoryFullPath.StartsWith('D:\', [StringComparison]::OrdinalIgnoreCase) -and ($isTempRoot -or $isTempChild))) {
        throw "T65_TEMP_PATH_INVALID: 临时目录必须是 D 盘 temp 根目录下的普通目录：$directoryPath"
    }
}
$env:TEMP = $tempPath
$env:TMP = $tempPath
$env:TMPDIR = $tempPath
$env:HOME = $homePath
$env:APPDATA = $appDataPath
$env:LOCALAPPDATA = $localAppDataPath
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:XILINX_LOCAL_USER_DATA = $xilinxLocalUserDataPath

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

$fixtureRootPath = Join-Path $runPath 'fixture'
$fixtureManifestPath = Join-Path $runPath 'fixture_manifest.json'
$inputFixturePath = Join-Path $fixtureRootPath 'sample0_input_chw_int8.bin'
$weightFixturePath = Join-Path $fixtureRootPath 'sample0_layer0_gf8_weights.bin'
$goldenFixturePath = Join-Path $fixtureRootPath 'sample0_layer0_output_point0.bin'
foreach ($fixturePath in @($fixtureManifestPath, $inputFixturePath, $weightFixturePath, $goldenFixturePath)) {
    $fixtureItem = Get-Item -LiteralPath $fixturePath -ErrorAction Stop
    if ($fixtureItem.PSIsContainer) {
        throw "T65 fixture 不是普通文件：$($fixtureItem.FullName)"
    }
}
$fixtureBinding = Get-Content -LiteralPath $fixtureManifestPath -Raw -Encoding utf8 | ConvertFrom-Json
$fixtureBindings = @(
    [pscustomobject]@{
        Name = 'input'; Path = $inputFixturePath
        BoundPath = [string]$fixtureBinding.sample.input_fixture_path
        BoundSha256 = [string]$fixtureBinding.sample.input_fixture_sha256
    },
    [pscustomobject]@{
        Name = 'weights'; Path = $weightFixturePath
        BoundPath = [string]$fixtureBinding.weights.slice_path
        BoundSha256 = [string]$fixtureBinding.weights.slice_sha256
    },
    [pscustomobject]@{
        Name = 'golden'; Path = $goldenFixturePath
        BoundPath = [string]$fixtureBinding.golden.fixture_path
        BoundSha256 = [string]$fixtureBinding.golden.fixture_sha256
    }
)
foreach ($fixture in $fixtureBindings) {
    $actualFixturePath = [System.IO.Path]::GetFullPath($fixture.Path)
    $boundFixturePath = [System.IO.Path]::GetFullPath($fixture.BoundPath)
    if (-not $actualFixturePath.Equals($boundFixturePath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "T65_FIXTURE_PATH_BINDING_MISMATCH: $($fixture.Name) 路径与 fixture manifest 不一致。"
    }
    $actualFixtureSha256 = (Get-FileHash -LiteralPath $fixture.Path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualFixtureSha256 -cne $fixture.BoundSha256) {
        throw "T65_FIXTURE_SHA_MISMATCH: $($fixture.Name) 夹具摘要与 fixture manifest 不一致。"
    }
}
$forwardInputFixturePath = $inputFixturePath.Replace('\', '/')
$forwardWeightFixturePath = $weightFixturePath.Replace('\', '/')
$forwardGoldenFixturePath = $goldenFixturePath.Replace('\', '/')
$inputPlusArg = "+T65_INPUT_PATH=$forwardInputFixturePath"
$weightPlusArg = "+T65_WEIGHT_PATH=$forwardWeightFixturePath"
$goldenPlusArg = "+T65_GOLDEN_PATH=$forwardGoldenFixturePath"
$preparationEvidence = [ordered]@{
    schema_version = 'gestureforge_s2a_t65_sim02_preparation_v1'
    task_id = 'S2A-T65-SIM02-PREP'
    status = 'SIM02_INPUTS_BOUND_BEFORE_TOOL_LAUNCH'
    scope = 'sample0 layer0 CONV output NCHW index [0,0,0,0] only'
    run_path = $runPath
    simulation_path = $simPath
    fixture_manifest_path = $fixtureManifestPath
    fixture_manifest_sha256 = (Get-FileHash -LiteralPath $fixtureManifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
    fixtures = [ordered]@{
        input = [ordered]@{ path = $inputFixturePath; sha256 = $fixtureBindings[0].BoundSha256 }
        weights = [ordered]@{ path = $weightFixturePath; sha256 = $fixtureBindings[1].BoundSha256 }
        golden = [ordered]@{ path = $goldenFixturePath; sha256 = $fixtureBindings[2].BoundSha256 }
    }
    xsim_testplusargs = @($inputPlusArg, $weightPlusArg, $goldenPlusArg)
    tool_environment = [ordered]@{
        temp = $tempPath
        tmp = $tempPath
        tmpdir = $tempPath
        home = $homePath
        appdata = $appDataPath
        localappdata = $localAppDataPath
        xilinx_local_user_data = $xilinxLocalUserDataPath
    }
    source_sha256 = [ordered]@{
        runner = (Get-FileHash -LiteralPath (Join-Path $rootPath 'verification\run_s2a_t65_layer0_golden.ps1') -Algorithm SHA256).Hash.ToLowerInvariant()
        testbench = (Get-FileHash -LiteralPath (Join-Path $rootPath 'sim\tb_s2a_t65_layer0_golden.sv') -Algorithm SHA256).Hash.ToLowerInvariant()
        offline_test = (Get-FileHash -LiteralPath $pythonTestPath -Algorithm SHA256).Hash.ToLowerInvariant()
        process_guard = (Get-FileHash -LiteralPath $processGuardModulePath -Algorithm SHA256).Hash.ToLowerInvariant()
        process_allowlist = (Get-FileHash -LiteralPath $processAllowlistPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    execution_at_record_time = [ordered]@{ xvlog_started = $false; xelab_started = $false; xsim_started = $false }
}
$preparationJson = ($preparationEvidence | ConvertTo-Json -Depth 10) + [Environment]::NewLine
Write-NewOrVerifyUtf8 -Path $preparationEvidencePath -Text $preparationJson

if (-not $RunSimulation) {
    Write-Output "PREPARE_ONLY：fixture 路径已绑定到 sim02；未调用 Vivado/XSim。证据：$preparationEvidencePath"
    exit 0
}

$processGuardItem = Get-Item -LiteralPath $processGuardModulePath -ErrorAction Stop
if ($processGuardItem.PSIsContainer -or $processGuardItem.FullName -cne $processGuardModulePath -or
    ($processGuardItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    throw "T65_PROCESS_GUARD_PATH_INVALID: process guard 不是 D 盘精确路径上的普通文件：$processGuardModulePath"
}
$processGuardActualSha256 = (Get-FileHash -LiteralPath $processGuardModulePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($processGuardActualSha256 -cne $processGuardModuleExpectedSha256) {
    throw 'T65_PROCESS_GUARD_SHA_MISMATCH: process guard 源码摘要不匹配。'
}
. $processGuardModulePath
$t65ProcessAllowlist = Read-T65XilinxProcessAllowlist -Path $processAllowlistPath -ExpectedSha256 $processAllowlistExpectedSha256
$t65AllowedProcessIdentities = @($t65ProcessAllowlist.identities)

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
    Assert-T65AllowedXilinxProcessSnapshot -AllowedIdentities $t65AllowedProcessIdentities -Phase 'immediately before xvlog' | Out-Null
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & (Join-Path $vivadoBinPath 'xvlog.bat') -sv -work xil_defaultlib @sourcePaths *> $xvlogConsole
        $xvlogExit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    Assert-T65AllowedXilinxProcessSnapshot -AllowedIdentities $t65AllowedProcessIdentities -Phase 'immediately after xvlog' | Out-Null
    if ($xvlogExit -ne 0 -or -not (Test-Path -LiteralPath $xvlogLog -PathType Leaf)) {
        Set-Content -LiteralPath $statusPath -Value "XVLOG_FAIL exit=$xvlogExit" -Encoding utf8
        throw "xvlog 失败，exit=$xvlogExit；日志：$xvlogConsole"
    }
    if (Select-String -LiteralPath $xvlogLog -Pattern 'ERROR:|FATAL:' -Quiet) {
        Set-Content -LiteralPath $statusPath -Value 'XVLOG_LOG_FAIL' -Encoding utf8
        throw "xvlog 日志存在 ERROR/FATAL：$xvlogLog"
    }

    Write-Output '在独立 snapshot 中 elaboration。'
    Assert-T65AllowedXilinxProcessSnapshot -AllowedIdentities $t65AllowedProcessIdentities -Phase 'immediately before xelab' | Out-Null
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & (Join-Path $vivadoBinPath 'xelab.bat') -mt off -debug typical xil_defaultlib.tb_s2a_t65_layer0_golden -s $snapshotName -log $xelabLog *> $xelabConsole
        $xelabExit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    Assert-T65AllowedXilinxProcessSnapshot -AllowedIdentities $t65AllowedProcessIdentities -Phase 'immediately after xelab' | Out-Null
    if ($xelabExit -ne 0 -or -not (Test-Path -LiteralPath $xelabLog -PathType Leaf)) {
        Set-Content -LiteralPath $statusPath -Value "XELAB_FAIL exit=$xelabExit" -Encoding utf8
        throw "xelab 失败，exit=$xelabExit；日志：$xelabConsole"
    }
    if (Select-String -LiteralPath $xelabLog -Pattern 'ERROR:|FATAL:' -Quiet) {
        Set-Content -LiteralPath $statusPath -Value 'XELAB_LOG_FAIL' -Encoding utf8
        throw "xelab 日志存在 ERROR/FATAL：$xelabLog"
    }

    Write-Output '运行 sample0 layer0 首个输出点；bench 有界结束，不推进整层。'
    Assert-T65AllowedXilinxProcessSnapshot -AllowedIdentities $t65AllowedProcessIdentities -Phase 'immediately before xsim' | Out-Null
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & (Join-Path $vivadoBinPath 'xsim.bat') -R -testplusarg $inputPlusArg -testplusarg $weightPlusArg -testplusarg $goldenPlusArg -log $xsimLog $snapshotName *> $xsimConsole
        $xsimExit = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    Assert-T65AllowedXilinxProcessSnapshot -AllowedIdentities $t65AllowedProcessIdentities -Phase 'immediately after xsim' | Out-Null
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
