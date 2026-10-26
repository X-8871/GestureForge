param()
$ErrorActionPreference = 'Stop'
$w = 'D:\codex-worktrees\dbdf'
$src = Join-Path $w 'tmp\stage3_reference\AX7020_2023.1\course_s2_vitis\22_ov5640_single\Vitis\auto_create_vitis\src\an5642_single'
$bspSrc = Join-Path $w 'tmp\s3r06\t04_j11cmos2_elf_v11\elf_build'
$out = Join-Path $w 'tmp\s3r06\t05_vdma_start_trace_20261026_r03'
$ev = Join-Path $w 'report\evidence\S3-T05\t05_vdma_start_trace_20261026_r03'
$log = Join-Path $ev 'make_only_build.log'
$v12 = Join-Path $w 'board\stage3\software\sensor\s3_t04_app_diag_v12.patch'
$v13 = Join-Path $w 'board\stage3\software\sensor\s3_t04_app_diag_v13_vdma_start_trace.patch'
foreach ($p in @($src, $bspSrc, $v12, $v13)) {
    if (-not (Test-Path -LiteralPath $p)) { throw "所需精确路径不存在：$p" }
}
if (Test-Path -LiteralPath $out) { throw "RunId 构建目标已存在，拒绝覆盖：$out" }
New-Item -ItemType Directory -Path $out | Out-Null
$app = Join-Path $out 'app'
New-Item -ItemType Directory -Path $app | Out-Null
Get-ChildItem -LiteralPath $src -Force | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $app -Recurse }
foreach ($name in @('bsp', '_input', '_sdtgen_cwd')) { Copy-Item -LiteralPath (Join-Path $bspSrc $name) -Destination $out -Recurse }
Copy-Item -LiteralPath (Join-Path $bspSrc 'app\empty_application_bsp') -Destination $app -Recurse
foreach ($name in @('lscript.ld', 'Makefile', 'Xilinx.spec')) { Copy-Item -LiteralPath (Join-Path $bspSrc "app\$name") -Destination $app }
Copy-Item -LiteralPath (Join-Path $w 'scripts\stage3_t04_vitis\Makefile.app') -Destination $app
$xsaHash = (Get-FileHash -LiteralPath (Join-Path $out '_input\design_1_wrapper.xsa') -Algorithm SHA256).Hash.ToLowerInvariant()
$pristineHash = (Get-FileHash -LiteralPath (Join-Path $app 'display_demo.c') -Algorithm SHA256).Hash.ToLowerInvariant()
$lib = Join-Path $app 'empty_application_bsp\ps7_cortexa9_0\lib\libxil.a'
$libHash = (Get-FileHash -LiteralPath $lib -Algorithm SHA256).Hash.ToLowerInvariant()
$lscriptHash = (Get-FileHash -LiteralPath (Join-Path $app 'lscript.ld') -Algorithm SHA256).Hash.ToLowerInvariant()
if ($xsaHash -ne '1f5b138e693065c6257e29075018f7654d4c3a6b67dcab051f0ea8ac106cb0e3') { throw "XSA 哈希不符：$xsaHash" }
if ($pristineHash -ne '1e2c74f100a77aef06fe3973c5ca40c964db403ca4621336110a6d15223da985') { throw "原始应用哈希不符：$pristineHash" }
if ($libHash -ne '8185dcb110944ab1cd687ae6b7a40aafc070725e1d1e1076c27ef1196779dd0a') { throw "libxil.a 哈希不符：$libHash" }
if ($lscriptHash -ne '7b5f5ccfdbdb47e8d931f3bbe9e15414cab763904473f29a1786a8069563ac8a') { throw "lscript.ld 哈希不符：$lscriptHash" }
$git = (Get-Command git.exe -ErrorAction Stop).Source
foreach ($patch in @($v12, $v13)) {
    & $git -C $w apply -p1 --directory='tmp/s3r06/t05_vdma_start_trace_20261026_r03/app' $patch
    if ($LASTEXITCODE -ne 0) { throw "应用补丁失败：$patch；rc=$LASTEXITCODE" }
}
$env:PATH = 'D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin;D:\Xilinx\2026.1\Vitis\gnuwin\bin;' + $env:PATH
$env:RDI_PLATFORM = 'win'
$make = 'D:\Xilinx\2026.1\Vitis\gnuwin\bin\make.exe'
$fields = @($make, "XSA_SHA256=$xsaHash", "PRISTINE_DISPLAY_DEMO_SHA256=$pristineHash", "LIBXIL_SHA256=$libHash", "LSCRIPT_SHA256=$lscriptHash")
[IO.File]::WriteAllLines($log, $fields, [Text.UTF8Encoding]::new($false))
Push-Location $app
try {
    & $make -f Makefile.app 'EXEC=an5642_j11cmos2_v13_vdma_start_trace.elf' 'OPT_FLAGS=-O2 -c' 2>&1 | Tee-Object -FilePath $log -Append
    $rc = $LASTEXITCODE
} finally { Pop-Location }
"BUILD_RC=$rc" | Add-Content -LiteralPath $log -Encoding utf8
if ($rc -ne 0) { exit $rc }
$elf = Join-Path $app 'an5642_j11cmos2_v13_vdma_start_trace.elf'
if (-not (Test-Path -LiteralPath $elf)) { throw "make 返回成功但 ELF 缺失：$elf" }
"ELF_PATH=$elf"
"ELF_SHA256=$((Get-FileHash -LiteralPath $elf -Algorithm SHA256).Hash.ToLowerInvariant())"
"BUILD_LOG=$log"
