$ErrorActionPreference = 'Stop'
# 本脚本只读比对 T60 run06 的仿真观察值、冻结 golden 和终止日志。
$runRoot = (Get-Item -LiteralPath $PSScriptRoot -ErrorAction Stop).FullName
$expectedRun = 'D:\FPGA_Competition\report\evidence\S2A-T60\run06'
if ($runRoot -cne $expectedRun) { throw "证据目录不符：$runRoot" }
$fixtureRoot = Join-Path $runRoot 'fixture'
$rawPath = Join-Path $runRoot 'observed_raw.bin'
$int8Path = Join-Path $runRoot 'observed_output.bin'
$goldenPath = Join-Path $fixtureRoot 'golden.bin'
$logPath = Join-Path $runRoot 'runtime_simulate.log'
$manifest = Get-Content -LiteralPath (Join-Path $fixtureRoot 'fixture_manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$raw = [IO.File]::ReadAllBytes($rawPath)
$int8 = [IO.File]::ReadAllBytes($int8Path)
$golden = [IO.File]::ReadAllBytes($goldenPath)
if ($raw.Length -ne 26624 -or $int8.Length -ne 6656 -or $golden.Length -ne 33280) { throw "文件长度不符：raw=$($raw.Length) int8=$($int8.Length) golden=$($golden.Length)" }
if ($manifest.geometry.output_values -ne 6656 -or $manifest.geometry.y -ne 24 -or $manifest.geometry.output_channels -ne 256) { throw 'fixture 几何与 T60 run06 范围不符' }
$goldRaw = [byte[]]::new($raw.Length)
$goldInt8 = [byte[]]::new($int8.Length)
[Array]::Copy($golden,0,$goldRaw,0,$goldRaw.Length)
[Array]::Copy($golden,$goldRaw.Length,$goldInt8,0,$goldInt8.Length)
function Test-ByteArrayEqual {
    param([byte[]]$Left,[byte[]]$Right)
    if ($Left.Length -ne $Right.Length) { return $false }
    for ($index = 0; $index -lt $Left.Length; $index++) {
        if ($Left[$index] -ne $Right[$index]) { return $false }
    }
    return $true
}
if (-not (Test-ByteArrayEqual $raw $goldRaw)) { throw 'raw INT32 观察值与 golden 前段不一致' }
if (-not (Test-ByteArrayEqual $int8 $goldInt8)) { throw 'INT8 观察值与 golden 后段不一致' }
$log = Get-Content -LiteralPath $logPath -Raw -Encoding UTF8
if ($log -notmatch '(?m)^PASS T60 outputs=6656 raw=6656' -or $log -notmatch '(?m)^\$finish called at time : 2971541060 ns') { throw '仿真 PASS/$finish 日志核查失败' }
$rawHash = (Get-FileHash -LiteralPath $rawPath -Algorithm SHA256).Hash.ToLowerInvariant()
$int8Hash = (Get-FileHash -LiteralPath $int8Path -Algorithm SHA256).Hash.ToLowerInvariant()
$goldenHash = (Get-FileHash -LiteralPath $goldenPath -Algorithm SHA256).Hash.ToLowerInvariant()
$manifestGolden = $manifest.copied_fixture_files | Where-Object { $_.name -ceq 'golden.bin' } | Select-Object -First 1
if (-not $manifestGolden -or $goldenHash -cne $manifestGolden.sha256) { throw 'golden.bin 与冻结 fixture 清单哈希不符' }
Write-Output "T60_RUN06_RUNTIME_VERIFY=PASS y=24 outputs=6656 raw_exact=1 int8_exact=1 raw_sha256=$rawHash int8_sha256=$int8Hash"