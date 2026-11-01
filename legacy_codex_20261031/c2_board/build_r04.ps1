$ErrorActionPreference = 'Stop'
$c2Root = 'D:\codex-worktrees\w6\legacy_codex_20261031\c2_board'
$sourceRoot = Join-Path $c2Root 'src'
$testRoot = Join-Path $c2Root 'tests'
$cacheRoot = 'D:\codex-worktrees\w6\tmp\c2_real_chainb_20261101_r04'
$recordPath = Join-Path $c2Root 'build_record_r04.json'
$gccRoot = 'D:\Xilinx\2026.1\Vitis\gnu\aarch32\nt\gcc-arm-none-eabi\bin'
$gcc = Join-Path $gccRoot 'arm-none-eabi-gcc.exe'
$objcopy = Join-Path $gccRoot 'arm-none-eabi-objcopy.exe'
$nm = Join-Path $gccRoot 'arm-none-eabi-nm.exe'
$size = Join-Path $gccRoot 'arm-none-eabi-size.exe'
$hostGcc = 'D:\mingw64\bin\gcc.exe'
$bspRoot = 'D:\codex-worktrees\w4\tmp\4\S4-B-REAL-01\s4b_ps_tensor_20261023_r13\bundle_extract\bundle\workspace\ps7\export\ps7\sw\cpu0'
$linkerScript = 'D:\codex-worktrees\w4\tmp\4\S4-T34\ps_app_build\lscript_s4t34.ld'
$fixturePath = Join-Path (Join-Path $c2Root 'inputs') 'fixture_fist_000_640x480_bgr888.raw'
$originalFixtureRun = 'D:\codex-worktrees\w4\report\evidence\S4-T34\bringup_chainlite_b_20261028_r01'

if (Test-Path -LiteralPath $cacheRoot) { throw "R04 cache already exists: $cacheRoot" }
if (Test-Path -LiteralPath $recordPath) { throw "R04 record already exists: $recordPath" }
New-Item -ItemType Directory -Path $cacheRoot | Out-Null

$compileFlags = @(
    '-DSDT', '-DPREPROC_SRC=0', '-DS4D_CHAINB_SELFCHECK=1', '-DC2_REAL_FIXTURE_MODE=1',
    '-mcpu=cortex-a9', '-mfpu=vfpv3', '-mfloat-abi=hard',
    ('-specs=' + (Join-Path $bspRoot 'Xilinx.spec')),
    ('-I' + (Join-Path $bspRoot 'include')), ('-I' + $sourceRoot),
    '-Wall', '-Wextra', '-O2', '-g3', '-std=gnu11',
    '-ffunction-sections', '-fdata-sections', '-U__clang__'
)
$compileUnits = @(
    @('s4d_ps_app.c', 's4d_ps_app.o'),
    @('s4d_sw_preproc.c', 's4d_sw_preproc.o'),
    @('s2a_ps_decode_nms_reference.c', 's2a_ps_decode_nms_reference.o'),
    @('c2_s5_publish.c', 'c2_s5_publish.o'),
    @('c2_display_hook.c', 'c2_display_hook.o'),
    @('s5_display_app.c', 's5_display_app.o'),
    @('s5_real_source.c', 's5_real_source.o'),
    @('s5_timebase.c', 's5_timebase.o'),
    @('vdma_ctrl.c', 'vdma_ctrl.o'),
    @('vtc_ctrl.c', 'vtc_ctrl.o')
)
$compileResults = @()
foreach ($unit in $compileUnits) {
    $unitFlags = $compileFlags
    if ($unit[0] -eq 's5_display_app.c') { $unitFlags = $compileFlags + @('-DS5_HOST_TEST=1') }
    $objectPath = Join-Path $cacheRoot $unit[1]
    $logPath = Join-Path $cacheRoot ($unit[1] + '.log')
    $commandArgs = @($unitFlags) + @('-c', (Join-Path $sourceRoot $unit[0]), '-o', $objectPath)
    & $gcc @commandArgs *> $logPath
    $unitExit = $LASTEXITCODE
    $compileResults += [pscustomobject]@{
        source = $unit[0]
        object = $objectPath
        arguments = $commandArgs
        exit_code = $unitExit
        log = $logPath
    }
    if ($unitExit -ne 0) { throw "Compile failed: $($unit[0]) exit=$unitExit log=$logPath" }
}

$hostTest = Join-Path $testRoot 'test_c2_rev4_profile.c'
$hostTestExe = Join-Path $cacheRoot 'test_c2_rev4_profile.exe'
$hostTestLog = Join-Path $cacheRoot 'host_test.log'
$hostTestArgs = @('-std=c11', '-Wall', '-Wextra', '-Werror', '-pedantic',
    ('-I' + $sourceRoot), (Join-Path $sourceRoot 'c2_s5_publish.c'), $hostTest,
    '-lm', '-o', $hostTestExe)
& $hostGcc @hostTestArgs *> $hostTestLog
$hostCompileExit = $LASTEXITCODE
if ($hostCompileExit -ne 0) { throw "Host test compile failed: exit=$hostCompileExit log=$hostTestLog" }
& $hostTestExe *> $hostTestLog
$hostTestExit = $LASTEXITCODE
if ($hostTestExit -ne 0) { throw "Host test failed: exit=$hostTestExit log=$hostTestLog" }

Copy-Item -LiteralPath $fixturePath -Destination (Join-Path $cacheRoot 'fixture.bin')
$fixtureObject = Join-Path $cacheRoot 'fixture_blob.o'
Push-Location -LiteralPath $cacheRoot
try {
    & $objcopy '-I' 'binary' '-O' 'elf32-littlearm' '-B' 'arm' `
        '--rename-section' '.data=.rodata,alloc,load,readonly,data,contents' `
        'fixture.bin' 'fixture_blob.o'
    $objcopyExit = $LASTEXITCODE
} finally {
    Pop-Location
}
if ($objcopyExit -ne 0) { throw "Fixture objcopy failed: exit=$objcopyExit" }

$elf = Join-Path $cacheRoot 'c2_real_chainb_display.elf'
$map = Join-Path $cacheRoot 'c2_real_chainb_display.map'
$linkLog = Join-Path $cacheRoot 'link.log'
$libraryRoot = Join-Path $bspRoot 'lib'
$linkArgs = @(
    $compileFlags,
    ('-Wl,-Map=' + $map + ',--cref,--gc-sections')
)
foreach ($unit in $compileUnits) { $linkArgs += Join-Path $cacheRoot $unit[1] }
$linkArgs += $fixtureObject
$linkArgs += @('-o', $elf, ('-L' + $libraryRoot), '-Wl,-T', ('-Wl,' + $linkerScript),
    '-Wl,--start-group', '-lxilstandalone', '-lxiltimer', '-lxil', '-lgcc', '-lc', '-lm', '-Wl,--end-group')
& $gcc @linkArgs *> $linkLog
$linkExit = $LASTEXITCODE
if ($linkExit -ne 0) { throw "Target link failed: exit=$linkExit log=$linkLog" }

$sizeLog = Join-Path $cacheRoot 'size.log'
& $size '--format=berkeley' $elf *> $sizeLog
$sizeExit = $LASTEXITCODE
if ($sizeExit -ne 0) { throw "Target size failed: exit=$sizeExit log=$sizeLog" }
$nmLog = Join-Path $cacheRoot 'nm.log'
& $nm '-n' '--defined-only' $elf *> $nmLog
$nmExit = $LASTEXITCODE
if ($nmExit -ne 0) { throw "Target nm failed: exit=$nmExit log=$nmLog" }
$nmText = [System.IO.File]::ReadAllText($nmLog, [System.Text.Encoding]::UTF8)
$requiredSymbols = @('main', 'C2Publisher_InitRev4Session', 'C2Publisher_PublishRev4', 'C2_DisplayOneFrame', '_binary_fixture_bin_start', '_binary_fixture_bin_end')
$missingSymbols = @($requiredSymbols | Where-Object { $nmText -notmatch [regex]::Escape($_) })
if ($missingSymbols.Count -ne 0) { throw ('Required ELF symbols missing: ' + ($missingSymbols -join ', ')) }

$sourceNames = @(
    's4d_ps_app.c', 's4d_sw_preproc.c', 's4d_sw_preproc.h', 's4d_geometry.h',
    's2a_ps_decode_nms_reference.c', 's2a_ps_decode_nms_reference.h',
    'c2_s5_publish.c', 'c2_s5_publish.h', 'c2_integration_status.h', 'c2_display_hook.c',
    's5_display_app.c', 's5_display_app.h', 's5_real_source.c', 's5_real_source.h',
    's5_result_abi.h', 's5_timebase.c', 's5_timebase.h', 's5_font8x16.h',
    'vdma_ctrl.c', 'vdma_ctrl.h', 'vtc_ctrl.c', 'vtc_ctrl.h'
)
$hashItems = @()
foreach ($name in $sourceNames) {
    $path = Join-Path $sourceRoot $name
    $hashItems += [pscustomobject]@{ path = $path; sha256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash; hash_basis = 'worktree_disk' }
}
$hashItems += [pscustomobject]@{ path = $fixturePath; sha256 = (Get-FileHash -LiteralPath $fixturePath -Algorithm SHA256).Hash; hash_basis = 'worktree_disk' }
foreach ($path in @((Join-Path $bspRoot 'Xilinx.spec'), (Join-Path $bspRoot 'include\xparameters.h'),
                    (Join-Path $bspRoot 'include\bspconfig.h'), (Join-Path $bspRoot 'lib\libxilstandalone.a'),
                    (Join-Path $bspRoot 'lib\libxiltimer.a'), (Join-Path $bspRoot 'lib\libxil.a'), $linkerScript)) {
    $hashItems += [pscustomobject]@{ path = $path; sha256 = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash; hash_basis = 'worktree_disk' }
}
$historyFixture = Join-Path $originalFixtureRun 'W2_pre_fixture_padded.bin'
$historyLog = Join-Path $originalFixtureRun 'chainb_uart.log'
$historyMeta = Join-Path $originalFixtureRun 'offline_reference_meta.json'
$history = [pscustomobject]@{
    raw_sha256 = (Get-FileHash -LiteralPath $fixturePath -Algorithm SHA256).Hash
    historical_raw_sha256 = (Get-FileHash -LiteralPath $historyFixture -Algorithm SHA256).Hash
    expected_decode_count = 1
    board_uart_log = $historyLog
    board_uart_log_sha256 = (Get-FileHash -LiteralPath $historyLog -Algorithm SHA256).Hash
    offline_reference_meta = $historyMeta
    offline_reference_meta_sha256 = (Get-FileHash -LiteralPath $historyMeta -Algorithm SHA256).Hash
    note = '相同RAW的既有chain-lite-B实板记录为count=1/raw=2；不据此改变解码器或safe14阈值。'
}
$toolVersion = (& $gcc '--version' | Select-Object -First 1)
$elfHash = (Get-FileHash -LiteralPath $elf -Algorithm SHA256).Hash
$elfBytes = (Get-Item -LiteralPath $elf).Length
$record = [pscustomobject]@{
    task_id = 'C2-REAL-CHAINB'
    run_id = 'c2_real_chainb_20261101_r04'
    built_utc8 = [DateTimeOffset]::Now.ToString('yyyy-MM-ddTHH:mm:sszzz')
    source_root = $c2Root
    build_script = $MyInvocation.MyCommand.Path
    build_script_sha256 = (Get-FileHash -LiteralPath $MyInvocation.MyCommand.Path -Algorithm SHA256).Hash
    toolchain = [pscustomobject]@{ compiler = $gcc; version = $toolVersion; host_compiler = $hostGcc }
    flags = $compileFlags
    compile = $compileResults
    host_test = [pscustomobject]@{ arguments = $hostTestArgs; compile_exit = $hostCompileExit; test_exit = $hostTestExit; log = $hostTestLog }
    fixture_object = [pscustomobject]@{ command = 'arm-none-eabi-objcopy -I binary -O elf32-littlearm -B arm --rename-section .data=.rodata,alloc,load,readonly,data,contents fixture.bin fixture_blob.o'; exit_code = $objcopyExit }
    link = [pscustomobject]@{ arguments = $linkArgs; exit_code = $linkExit; log = $linkLog; map = $map }
    size = [pscustomobject]@{ arguments = @('--format=berkeley', $elf); exit_code = $sizeExit; log = $sizeLog }
    symbols = [pscustomobject]@{ arguments = @('-n', '--defined-only', $elf); exit_code = $nmExit; required = $requiredSymbols; missing = $missingSymbols; log = $nmLog }
    fixture_history = $history
    inputs = $hashItems
    output = [pscustomobject]@{ path = $elf; bytes = $elfBytes; sha256 = $elfHash; hash_basis = 'worktree_disk' }
    status = [pscustomobject]@{ host_and_build = 'PASS'; board_deployment = 'NOT_RUN'; hdmi_physical_scanout = 'NOT_VERIFIED'; p3q_xsa_512m_metadata_mismatch = 'UNRESOLVED' }
}
$json = $record | ConvertTo-Json -Depth 10
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)
[System.IO.File]::WriteAllText($recordPath, $json, $utf8NoBom)
Write-Output ('R04_ELF=' + $elf)
Write-Output ('R04_SHA256=' + $elfHash)
Write-Output ('R04_BYTES=' + $elfBytes)
Write-Output ('R04_RECORD=' + $recordPath)
