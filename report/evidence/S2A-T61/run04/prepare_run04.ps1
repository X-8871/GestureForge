$ErrorActionPreference = 'Stop'
# 本脚本只准备 T61 run04 的隔离输入，不启动 Vivado 或 XSim。
$runRoot = (Get-Item -LiteralPath $PSScriptRoot -ErrorAction Stop).FullName
$expectedRunRoot = 'D:\FPGA_Competition\report\evidence\S2A-T61\run04'
if ($runRoot -cne $expectedRunRoot) { throw "run04 目录不符：$runRoot" }

$repoRoot = 'D:\FPGA_Competition'
$run03Root = 'D:\FPGA_Competition\report\evidence\S2A-T61\run03'
$run03FixtureRoot = Join-Path $run03Root 'fixture'
$rtlRoot = Join-Path $runRoot 'rtl'
$fixtureRoot = Join-Path $runRoot 'fixture'
$tempRoot = Join-Path $runRoot 'temp'
$targetXpr = 'D:\FPGA_Competition\vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr'
$targetPart = 'xa7z020clg400-1I'
$expectedScope = 'tiny416 cfg section36 layer35; all 256 output channels at y=25, x=0..25'
$helperFiles = @('prepare_run04.ps1', 'prepare_isolated_project.tcl', 'verify_run04_runtime.ps1')
$run04PreparePath = Join-Path $runRoot 'prepare_summary.json'
$run04RuntimePath = Join-Path $runRoot 'runtime_result.json'
$rawOutputPath = Join-Path $runRoot 'observed_raw.bin'
$int8OutputPath = Join-Path $runRoot 'observed_output.bin'
$runtimeLogPath = Join-Path $runRoot 'runtime_simulate.log'

function Get-BytesSha256 {
    param([byte[]]$Bytes)
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose() }
}
function Write-NewFile {
    param(
        [string]$Path,
        [byte[]]$Bytes,
        [System.Collections.Generic.List[string]]$CreatedFiles
    )
    $stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    $CreatedFiles.Add($Path)
    try { $stream.Write($Bytes, 0, $Bytes.Length) }
    finally { $stream.Dispose() }
}

if (-not (Test-Path -LiteralPath $repoRoot -PathType Container)) { throw '仓库根目录不存在' }
if (-not (Test-Path -LiteralPath $run03Root -PathType Container)) { throw 'T61 run03 输入目录不存在' }
if (-not (Test-Path -LiteralPath $targetXpr -PathType Leaf)) { throw '目标 XPR 不存在' }
foreach ($path in @($rtlRoot, $fixtureRoot, $tempRoot, (Join-Path $runRoot 'isolated_project'))) {
    if (Test-Path -LiteralPath $path) { throw "拒绝覆盖已有 run04 目录：$path" }
}
foreach ($path in @($run04PreparePath, $run04RuntimePath, $rawOutputPath, $int8OutputPath, $runtimeLogPath)) {
    if (Test-Path -LiteralPath $path) { throw "拒绝覆盖已有 run04 结果：$path" }
}
foreach ($helper in $helperFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $runRoot $helper) -PathType Leaf)) { throw "运行准备脚本缺失：$helper" }
}
$unexpectedEntries = @(Get-ChildItem -LiteralPath $runRoot -Force | Where-Object { $helperFiles -cnotcontains $_.Name })
if ($unexpectedEntries.Count -ne 0) { throw "run04 根目录含未预期项目：$($unexpectedEntries.Name -join ', ')" }

# 先完成全部只读绑定检查，任何失败都不创建临时或输出目录。
$xprBefore = (Get-FileHash -LiteralPath $targetXpr -Algorithm SHA256).Hash.ToLowerInvariant()
$xprText = [IO.File]::ReadAllText($targetXpr, [Text.UTF8Encoding]::new($false))
if ($xprText -notmatch '<Option Name="Part" Val="([^"]+)"') { throw '无法从目标 XPR 读取 Part' }
if ($Matches[1] -cne $targetPart) { throw "目标 XPR Part 不符：$($Matches[1])" }

$manifestPath = Join-Path $run03FixtureRoot 'fixture_manifest.json'
$rowReportPath = 'D:\FPGA_Competition\report\evidence\S2A-T61\layer35_row25_all_channels_run03.json'
$prepareSummaryPath = Join-Path $run03Root 'prepare_summary.json'
foreach ($path in @($manifestPath, $rowReportPath, $prepareSummaryPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "冻结准备证据缺失：$path" }
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$rowReport = Get-Content -LiteralPath $rowReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
$run03Summary = Get-Content -LiteralPath $prepareSummaryPath -Raw -Encoding UTF8 | ConvertFrom-Json
$manifestFullPath = (Get-Item -LiteralPath $manifestPath).FullName
$manifestBytes = (Get-Item -LiteralPath $manifestPath).Length
$manifestHash = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($manifest.task_id -cne 'S2A-T61' -or $manifest.run_id -cne 'run03') { throw 'run03 fixture manifest 身份不符' }
if ($manifest.fixture_root -cne $run03FixtureRoot -or $manifest.scope -cne $expectedScope) { throw 'run03 fixture root 或范围不符' }
if ($run03Summary.task_id -cne 'S2A-T61' -or $run03Summary.run_id -cne 'run03' -or $run03Summary.status -cne 'PREPARED_NOT_SIMULATED' -or $run03Summary.simulation.status -cne 'NOT_RUN') { throw 'run03 准备证据身份或状态不符' }
if ($rowReport.task_id -cne 'S2A-T61' -or $rowReport.run_id -cne 'run03' -or $rowReport.scope -cne $expectedScope -or $rowReport.source_hashes -eq $null) { throw 'T61 run03 主报告身份、范围或源码绑定不符' }
foreach ($binding in @($rowReport.fixture_manifest, $run03Summary.fixture.manifest)) {
    if ($binding.path -cne $manifestFullPath -or $binding.bytes -ne $manifestBytes -or $binding.sha256 -cne $manifestHash) { throw 'run03 fixture manifest 未通过报告路径、字节数和 SHA-256 绑定' }
}
if ($run03Summary.fixture.root -cne $run03FixtureRoot) { throw 'run03 summary fixture root 不符' }
if ($manifest.expected_counts.output_cases -ne 6656 -or $manifest.expected_counts.raw_int32_compares -ne 6656 -or $manifest.expected_counts.quantized_int8_compares -ne 6656) { throw 'T61 冻结输出计数不符' }
if ($manifest.fixed_points_yx.Count -ne 26) { throw 'T61 冻结坐标数不符' }
for ($x = 0; $x -lt 26; $x++) {
    if ($manifest.fixed_points_yx[$x].Count -ne 2 -or $manifest.fixed_points_yx[$x][0] -ne 25 -or $manifest.fixed_points_yx[$x][1] -ne $x) { throw "T61 冻结坐标不符：index=$x" }
}

$expectedFixtureNames = @('feature_input.bin', 'golden.bin', 'layer35_weights.bin', 'vectors.txt')
if ((@($manifest.files.PSObject.Properties.Name | Sort-Object) -join "`n") -cne (@($expectedFixtureNames | Sort-Object) -join "`n")) { throw 'run03 fixture 文件清单不符' }
$fixturePreflight = [ordered]@{}
foreach ($name in $expectedFixtureNames) {
    $source = Join-Path $run03FixtureRoot $name
    $metadata = $manifest.files.$name
    if ((Get-Item -LiteralPath $source).FullName -cne $metadata.path) { throw "fixture 源路径不符：$name" }
    if ((Get-Item -LiteralPath $source).Length -ne $metadata.bytes) { throw "fixture 长度不符：$name" }
    $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($sourceHash -cne $metadata.sha256) { throw "run03 fixture 哈希不符：$name" }
    $fixturePreflight[$name] = [pscustomobject]@{source=$source;metadata=$metadata;sha256=$sourceHash}
}

$sourceFiles = @(
    'src/int8_conv_tap_geometry.sv',
    'src/int8_conv_weight_address.sv',
    'src/int8_mac_accumulator.sv',
    'src/s2a_conv_engine.sv',
    'src/s2a_conv_layer35_channel_probe.sv',
    'sim/tb_s2a_conv_layer35_row25_all_channels.sv'
)
$sourcePreflight = [ordered]@{}
foreach ($relative in $sourceFiles) {
    $expectedHash = $rowReport.source_hashes.$relative
    if ([string]::IsNullOrWhiteSpace($expectedHash)) { throw "主报告没有源码哈希：$relative" }
    $source = Join-Path $repoRoot ($relative -replace '/', '\')
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "冻结源码不存在：$source" }
    $sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($sourceHash -cne $expectedHash) { throw "冻结源码哈希漂移：$relative" }
    $entry = [ordered]@{source=$source;source_sha256=$sourceHash;contents=$null;path_replacements=0;run04_sha256=$sourceHash}
    if ($relative -ceq 'sim/tb_s2a_conv_layer35_row25_all_channels.sv') {
        $text = [IO.File]::ReadAllText($source, [Text.UTF8Encoding]::new($false, $true))
        $oldSegment = 'S2A-T61\\run03\\'
        $newSegment = 'S2A-T61\\run04\\'
        $replaceCount = ([regex]::Matches($text, [regex]::Escape($oldSegment))).Count
        if ($replaceCount -ne 6) { throw "TB run03 路径段计数不符：$replaceCount" }
        $text = $text.Replace($oldSegment, $newSegment)
        if ($text.Contains($oldSegment) -or ([regex]::Matches($text, [regex]::Escape($newSegment))).Count -ne 6) { throw 'TB 运行目录路径替换校验失败' }
        $entry.contents = $text
        $entry.path_replacements = $replaceCount
        $entry.run04_sha256 = Get-BytesSha256 ([Text.UTF8Encoding]::new($false).GetBytes($text))
    }
    $sourcePreflight[$relative] = [pscustomobject]$entry
}

# 只读预检全部通过后，才在 D 盘创建本任务自己的运行目录。
$createdDirectories = [System.Collections.Generic.List[string]]::new()
$createdFiles = [System.Collections.Generic.List[string]]::new()
try {
    foreach ($directory in @($tempRoot, $fixtureRoot, $rtlRoot)) {
        [void][IO.Directory]::CreateDirectory($directory)
        $createdDirectories.Add($directory)
    }
    $env:TEMP = $tempRoot
    $env:TMP = $tempRoot
    $env:TMPDIR = $tempRoot
    foreach ($name in @('TEMP','TMP','TMPDIR')) {
        $value = [Environment]::GetEnvironmentVariable($name)
        if ($value -notlike 'D:\*') { throw "临时目录没有绑定到 D 盘：$name=$value" }
    }

    foreach ($name in $expectedFixtureNames) {
        $preflight = $fixturePreflight[$name]
        $destination = Join-Path $fixtureRoot $name
        Write-NewFile -Path $destination -Bytes ([IO.File]::ReadAllBytes($preflight.source)) -CreatedFiles $createdFiles
        if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -cne $preflight.sha256) { throw "run04 fixture 复制校验失败：$name" }
        $preflight.metadata.path = $destination
    }
    $manifest.run_id = 'run04'
    $manifest.fixture_root = $fixtureRoot
    $manifestOutput = $manifest | ConvertTo-Json -Depth 30
    $manifestOutputPath = Join-Path $fixtureRoot 'fixture_manifest.json'
    $manifestOutputBytes = [Text.UTF8Encoding]::new($false).GetBytes($manifestOutput)
    $manifestOutputHash = Get-BytesSha256 $manifestOutputBytes
    Write-NewFile -Path $manifestOutputPath -Bytes $manifestOutputBytes -CreatedFiles $createdFiles
    if ((Get-FileHash -LiteralPath $manifestOutputPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne $manifestOutputHash) { throw 'run04 fixture manifest 写入校验失败' }

    $sourceBindings = [ordered]@{}
    foreach ($relative in $sourceFiles) {
        $preflight = $sourcePreflight[$relative]
        $name = Split-Path -Leaf $relative
        $destination = Join-Path $rtlRoot $name
        if ($null -ne $preflight.contents) {
            $sourceBytes = [Text.UTF8Encoding]::new($false).GetBytes($preflight.contents)
        } else {
            $sourceBytes = [IO.File]::ReadAllBytes($preflight.source)
        }
        Write-NewFile -Path $destination -Bytes $sourceBytes -CreatedFiles $createdFiles
        $destinationHash = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($destinationHash -cne $preflight.run04_sha256) { throw "run04 源文件复制校验失败：$relative" }
        $sourceBindings[$relative] = [pscustomobject]@{source_sha256=$preflight.source_sha256;run04_sha256=$destinationHash;path_replacements=$preflight.path_replacements}
    }

    $xprAfter = (Get-FileHash -LiteralPath $targetXpr -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($xprAfter -cne $xprBefore) { throw '目标工程 XPR 在准备过程中发生变化' }
    $head = (git -C $repoRoot rev-parse HEAD).Trim()
    $fixtureBindings = [ordered]@{}
    foreach ($name in $expectedFixtureNames) {
        $path = Join-Path $fixtureRoot $name
        $fixtureBindings[$name] = [pscustomobject]@{path=$path;bytes=(Get-Item -LiteralPath $path).Length;sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
    }
    $summary = [ordered]@{
        task_id = 'S2A-T61'
        run_id = 'run04'
        status = 'PREPARED_NOT_SIMULATED'
        prepared_at_utc8 = [DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss zzz')
        baseline_head = $run03Summary.baseline_head
        current_head = $head
        scope = $expectedScope
        expected_counts = [ordered]@{raw_int32_compares=6656;quantized_int8_compares=6656;golden_bytes=33280}
        target_project_binding = [ordered]@{xpr=$targetXpr;xpr_sha256=$xprBefore;part=$targetPart;opened_or_modified=$false}
        source_bindings = $sourceBindings
        fixture_bindings = $fixtureBindings
        source_fixture_manifest = [ordered]@{path=$manifestFullPath;bytes=$manifestBytes;sha256=$manifestHash}
        fixture_manifest_sha256 = (Get-FileHash -LiteralPath $manifestOutputPath -Algorithm SHA256).Hash.ToLowerInvariant()
        testbench_path_replacements = 6
        temp_roots = [ordered]@{TEMP=$env:TEMP;TMP=$env:TMP;TMPDIR=$env:TMPDIR}
        vivado_invoked = $false
        xsim_invoked = $false
        simulation = 'NOT_RUN'
        review = [ordered]@{G2='NOT_REVIEWED';G3='NOT_CLAIMED';G4='NOT_CLAIMED';G5='NOT_CLAIMED'}
    }
    $summaryJson = $summary | ConvertTo-Json -Depth 30
    $summaryHash = Get-BytesSha256 ([Text.UTF8Encoding]::new($false).GetBytes($summaryJson))
    Write-NewFile -Path $run04PreparePath -Bytes ([Text.UTF8Encoding]::new($false).GetBytes($summaryJson)) -CreatedFiles $createdFiles
    if ((Get-FileHash -LiteralPath $run04PreparePath -Algorithm SHA256).Hash.ToLowerInvariant() -cne $summaryHash) { throw 'run04 prepare summary 写入校验失败' }
    Write-Output "T61_RUN04_PREPARE=PASS files=$($sourceFiles.Count) fixture_files=$($expectedFixtureNames.Count) tb_path_replacements=6 part=$targetPart xpr_unchanged=1 temp=D"
} catch {
    for ($index = $createdFiles.Count - 1; $index -ge 0; $index--) {
        $createdPath = $createdFiles[$index]
        if (Test-Path -LiteralPath $createdPath -PathType Leaf) {
            $createdFullPath = (Get-Item -LiteralPath $createdPath).FullName
            $runRootPrefix = $runRoot.TrimEnd('\') + '\'
            if ($createdFullPath.StartsWith($runRootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
                Remove-Item -LiteralPath $createdPath -Force
            } else {
                Write-Warning "拒绝清理 run04 根目录以外的文件：$createdFullPath"
            }
        }
    }
    for ($index = $createdDirectories.Count - 1; $index -ge 0; $index--) {
        $directory = $createdDirectories[$index]
        if (Test-Path -LiteralPath $directory -PathType Container) {
            if (@(Get-ChildItem -LiteralPath $directory -Force).Count -eq 0) { Remove-Item -LiteralPath $directory -Force }
            else { Write-Warning "保留非空的本轮准备目录以保护其中数据：$directory" }
        }
    }
    throw
}
