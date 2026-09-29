$ErrorActionPreference = 'Stop'
# 本脚本核验 T61 run04 仿真观察值、冻结 golden 和终止日志，并只新建 runtime_result.json。
$runRoot = (Get-Item -LiteralPath $PSScriptRoot -ErrorAction Stop).FullName
$expectedRun = 'D:\FPGA_Competition\report\evidence\S2A-T61\run04'
if ($runRoot -cne $expectedRun) { throw "证据目录不符：$runRoot" }
$fixtureRoot = Join-Path $runRoot 'fixture'
$rawPath = Join-Path $runRoot 'observed_raw.bin'
$int8Path = Join-Path $runRoot 'observed_output.bin'
$goldenPath = Join-Path $fixtureRoot 'golden.bin'
$manifestPath = Join-Path $fixtureRoot 'fixture_manifest.json'
$preparePath = Join-Path $runRoot 'prepare_summary.json'
$logPath = Join-Path $runRoot 'runtime_simulate.log'
$runtimePath = Join-Path $runRoot 'runtime_result.json'
$runtimeTempPath = Join-Path (Join-Path $runRoot 'temp') 'runtime_result.json.tmp'
if (Test-Path -LiteralPath $runtimePath) { throw "拒绝覆盖已有运行摘要：$runtimePath" }
if (Test-Path -LiteralPath $runtimeTempPath) { throw "拒绝覆盖已有临时摘要：$runtimeTempPath" }
foreach ($path in @($rawPath, $int8Path, $goldenPath, $manifestPath, $preparePath, $logPath)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "运行证据缺失：$path" }
}
$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$prepare = Get-Content -LiteralPath $preparePath -Raw -Encoding UTF8 | ConvertFrom-Json
$raw = [IO.File]::ReadAllBytes($rawPath)
$int8 = [IO.File]::ReadAllBytes($int8Path)
$golden = [IO.File]::ReadAllBytes($goldenPath)
if ($manifest.task_id -cne 'S2A-T61' -or $manifest.run_id -cne 'run04') { throw 'fixture 身份不符' }
if ($manifest.fixture.bytes -ne 259584 -or $manifest.fixture.sha256 -cne 'f7cbcdae9627c974b0210b3329be66a4264d96d0e2474d3c7f30a1b9c2f59ff1') { throw 'feature fixture 绑定不符' }
if ($manifest.expected_counts.output_cases -ne 6656 -or $manifest.fixed_points_yx.Count -ne 26) { throw '输出几何或计数不符' }
for ($x = 0; $x -lt 26; $x++) {
    if ($manifest.fixed_points_yx[$x].Count -ne 2 -or $manifest.fixed_points_yx[$x][0] -ne 25 -or $manifest.fixed_points_yx[$x][1] -ne $x) { throw "fixture 坐标不符：index=$x" }
}
if ($raw.Length -ne 26624 -or $int8.Length -ne 6656 -or $golden.Length -ne 33280) { throw "文件长度不符：raw=$($raw.Length) int8=$($int8.Length) golden=$($golden.Length)" }
foreach ($name in @('feature_input.bin', 'golden.bin', 'layer35_weights.bin', 'vectors.txt')) {
    $path = Join-Path $fixtureRoot $name
    $metadata = $manifest.files.$name
    if ($metadata.path -cne $path -or (Get-Item -LiteralPath $path).Length -ne $metadata.bytes) { throw "fixture 路径或长度不符：$name" }
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $metadata.sha256) { throw "fixture 哈希不符：$name" }
}
if ((Get-FileHash -LiteralPath $goldenPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne '7dc57c7f59c8580797951bd034346b85096dd469c4aad75b569647c1b083d015') { throw 'golden.bin 哈希不符' }
$goldRaw = [byte[]]::new($raw.Length)
$goldInt8 = [byte[]]::new($int8.Length)
[Array]::Copy($golden, 0, $goldRaw, 0, $goldRaw.Length)
[Array]::Copy($golden, $goldRaw.Length, $goldInt8, 0, $goldInt8.Length)
function Test-ByteArrayEqual {
    param([byte[]]$Left, [byte[]]$Right)
    if ($Left.Length -ne $Right.Length) { return $false }
    for ($index = 0; $index -lt $Left.Length; $index++) {
        if ($Left[$index] -ne $Right[$index]) { return $false }
    }
    return $true
}
function Get-BytesSha256 {
    param([byte[]]$Bytes)
    $sha = [Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-', '').ToLowerInvariant() }
    finally { $sha.Dispose() }
}
if (-not (Test-ByteArrayEqual $raw $goldRaw)) { throw 'raw INT32 观察值与 golden 前段不一致' }
if (-not (Test-ByteArrayEqual $int8 $goldInt8)) { throw 'INT8 观察值与 golden 后段不一致' }
$log = Get-Content -LiteralPath $logPath -Raw -Encoding UTF8
$passLines = @([regex]::Matches($log, '(?m)^PASS T61 outputs=6656 raw=6656[^\r\n]*') | ForEach-Object { $_.Value })
if ($passLines.Count -ne 1) { throw "PASS T61 行数量不为 1：$($passLines.Count)" }
$finishMatches = [regex]::Matches($log, '(?m)^\$finish called at time : ([0-9]+) ns')
if ($finishMatches.Count -ne 1) { throw "仿真正常 $finish 日志数量不为 1：$($finishMatches.Count)" }
$finishMatch = $finishMatches[0]
if ($log -match '(?im)^\s*(ERROR|FATAL)\b') { throw '仿真日志含 ERROR/FATAL 行' }
if ($prepare.task_id -cne 'S2A-T61' -or $prepare.run_id -cne 'run04' -or $prepare.target_project_binding.part -cne 'xa7z020clg400-1I') { throw '准备绑定不符' }
if (@($prepare.source_bindings.PSObject.Properties).Count -ne 6) { throw '准备源码清单数量不符' }
foreach ($item in $prepare.source_bindings.PSObject.Properties) {
    $rtlPath = Join-Path (Join-Path $runRoot 'rtl') (Split-Path -Leaf $item.Name)
    if ((Get-FileHash -LiteralPath $rtlPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne $item.Value.run04_sha256) { throw "run04 RTL 源码哈希不符：$($item.Name)" }
}
$runtime = [ordered]@{
    task_id = 'S2A-T61'
    run_id = 'run04'
    status = 'PASS_SIMULATION_DATA_ONLY'
    scope = 'tiny416 cfg section36 layer35; all 256 output channels at y=25, x=0..25'
    result_count = 6656
    raw_int32_bytes = $raw.Length
    int8_bytes = $int8.Length
    raw_exact_match = $true
    int8_exact_match = $true
    finish_time_ns = [UInt64]::Parse($finishMatch.Groups[1].Value)
    pass_line = $passLines[0]
    hashes = [ordered]@{
        observed_raw_sha256 = (Get-FileHash -LiteralPath $rawPath -Algorithm SHA256).Hash.ToLowerInvariant()
        observed_int8_sha256 = (Get-FileHash -LiteralPath $int8Path -Algorithm SHA256).Hash.ToLowerInvariant()
        golden_sha256 = (Get-FileHash -LiteralPath $goldenPath -Algorithm SHA256).Hash.ToLowerInvariant()
        runtime_log_sha256 = (Get-FileHash -LiteralPath $logPath -Algorithm SHA256).Hash.ToLowerInvariant()
        fixture_manifest_sha256 = (Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant()
    }
    prepare_summary_sha256 = (Get-FileHash -LiteralPath $preparePath -Algorithm SHA256).Hash.ToLowerInvariant()
    verified_at_utc8 = [DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss zzz')
    review = [ordered]@{G2='NOT_REVIEWED';G3='NOT_CLAIMED';G4='NOT_CLAIMED';G5='NOT_CLAIMED'}
}
$runtimeJson = $runtime | ConvertTo-Json -Depth 12
$runtimeBytes = [Text.UTF8Encoding]::new($false).GetBytes($runtimeJson)
$runtimeTempCreated = $false
try {
    $runtimeStream = [IO.File]::Open($runtimeTempPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)
    $runtimeTempCreated = $true
    try { $runtimeStream.Write($runtimeBytes, 0, $runtimeBytes.Length) }
    finally { $runtimeStream.Dispose() }
    if ((Get-FileHash -LiteralPath $runtimeTempPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne (Get-BytesSha256 $runtimeBytes)) { throw '临时运行摘要哈希校验失败' }
    [IO.File]::Move($runtimeTempPath, $runtimePath)
} catch {
    if ($runtimeTempCreated -and (Test-Path -LiteralPath $runtimeTempPath -PathType Leaf)) { Remove-Item -LiteralPath $runtimeTempPath -Force }
    throw
}
Write-Output "T61_RUN04_RUNTIME_VERIFY=PASS y=25 outputs=6656 raw_exact=1 int8_exact=1 finish_ns=$($runtime.finish_time_ns) raw_sha256=$($runtime.hashes.observed_raw_sha256) int8_sha256=$($runtime.hashes.observed_int8_sha256)"
