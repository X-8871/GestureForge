param([string]$RunName = ('s3_sensor_' + (Get-Date -Format 'yyyyMMdd_HHmmss')))
$ErrorActionPreference = 'Stop'
if ($RunName -notmatch '^[A-Za-z0-9_-]+$') { throw '运行名称只允许英文数字下划线连字符' }
$repo = (Get-Item -LiteralPath (Join-Path $PSScriptRoot '..')).FullName
$tmp = Get-Item -LiteralPath (Join-Path $repo 'tmp')
$run = Join-Path $tmp.FullName $RunName
if (Test-Path -LiteralPath $run) { throw '运行目录已存在，不覆盖' }
$gcc = (Get-Command gcc -ErrorAction Stop).Source
$driver = Get-Item -LiteralPath 'D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\iicps_v3_23\src'
$headers = @('xiicps.h','xiicps_hw.h','xiicps_master.c','xiicps_xfer.c')
$driverHashes = @()
foreach ($name in $headers) {
    $file = Get-Item -LiteralPath (Join-Path $driver.FullName $name)
    $driverHashes += @{path=$file.FullName;sha256=(Get-FileHash -LiteralPath $file.FullName).Hash}
}
New-Item -ItemType Directory -Path $run | Out-Null
$adapted = Join-Path $run 'adapted'
& (Join-Path $repo 'board/stage3/software/sensor/prepare_vendor.ps1') -OutputDirectory $adapted | Out-Null
$utf8 = [Text.UTF8Encoding]::new($false)
$original = [IO.File]::ReadAllText((Join-Path $adapted 'vendor_original/ov5640.c'),$utf8)
$modified = [IO.File]::ReadAllText((Join-Path $adapted 'ov5640.c'),$utf8)
$pattern = '(?s)struct reginfo sensor_init_data\[\]\s*=\s*\{(.*?)\n\};'
$table0 = [regex]::Match($original,$pattern)
$table1 = [regex]::Match($modified,$pattern)
if (!$table0.Success -or !$table1.Success) { throw '无法识别厂商寄存器表' }
$pair = '\{\s*(0x[0-9a-fA-F]+|SEQUENCE_END)\s*,\s*(0x[0-9a-fA-F]+)\s*\}'
$before = [regex]::Matches($table0.Groups[1].Value,$pair)
$after = [regex]::Matches($table1.Groups[1].Value,$pair)
if ($before.Count -eq 0 -or $before.Count -ne $after.Count) { throw '表长度改变' }
$expected = @()
for ($n=0; $n -lt $before.Count; $n++) {
    for ($k=1; $k -le 2; $k++) {
        if ($before[$n].Groups[$k].Value -cne $after[$n].Groups[$k].Value) { throw "第 $n 项寄存器表改变" }
    }
    $expected += "{$($before[$n].Groups[1].Value),$($before[$n].Groups[2].Value)},"
}
if ($before[$before.Count-1].Groups[1].Value -ne 'SEQUENCE_END') { throw '厂商终止符缺失' }
$golden = "static const struct reginfo expected_vendor[] = {`n" + ($expected -join "`n") + "`n};`n#define EXPECTED_WRITES $($before.Count-1)U`n"
[IO.File]::WriteAllText((Join-Path $run 'expected_vendor.h'),$golden,$utf8)
$mock = (Get-Item -LiteralPath (Join-Path $repo 'tests/stage3_sensor/mock')).FullName
$test = (Get-Item -LiteralPath (Join-Path $repo 'tests/stage3_sensor/test_sensor.c')).FullName
$results = @()
foreach ($real in @($false,$true)) {
    foreach ($sdt in @($false,$true)) {
        $tag = "header_$real-sdt_$sdt"
        $exe = Join-Path $run "$tag.exe"
        $args = @('-std=c11','-Wall','-Wextra','-Werror','-pedantic','-O0','-g','-DS3_I2C_BUSY_LIMIT=4')
        if ($sdt) { $args += '-DSDT' }
        if ($real) { $args += @('-I',$driver.FullName) }
        $args += @('-I',$mock,'-I',$adapted,'-I',$run,$test,(Join-Path $adapted 'i2c/PS_i2c.c'),(Join-Path $adapted 'ov5640.c'),'-o',$exe)
        $compile = & $gcc @args 2>&1
        $code = $LASTEXITCODE
        [IO.File]::WriteAllText((Join-Path $run "$tag.compile.log"),($compile -join "`n"),$utf8)
        if ($code -ne 0) { throw "编译失败 $tag，退出码 $code，见 $run" }
        # 只限制本次主机测试进程；不代表底层 I2C 有截止时间。
        $start = [Diagnostics.ProcessStartInfo]::new()
        $start.FileName = $exe
        $start.UseShellExecute = $false
        $start.CreateNoWindow = $true
        $start.RedirectStandardOutput = $true
        $start.RedirectStandardError = $true
        $process = [Diagnostics.Process]::Start($start)
        try {
            $stdout = $process.StandardOutput.ReadToEndAsync()
            $stderr = $process.StandardError.ReadToEndAsync()
            if (!$process.WaitForExit(30000)) {
                $process.Kill()
                $process.WaitForExit()
                [IO.File]::WriteAllText((Join-Path $run "$tag.test.log"),"TIMEOUT`n" + $stdout.Result + $stderr.Result,$utf8)
                throw "主机测试超时 $tag，已停止本次测试进程，见 $run"
            }
            $testCode = $process.ExitCode
            $output = $stdout.Result + $stderr.Result
        } finally { $process.Dispose() }
        [IO.File]::WriteAllText((Join-Path $run "$tag.test.log"),$output,$utf8)
        if ($testCode -ne 0) { throw "测试失败 $tag，退出码 $testCode，见 $run" }
        $summary = [regex]::Match($output.Trim(),'^PASS cases=(\d+) checks=(\d+) vendor_writes=(\d+)$')
        if (!$summary.Success -or [int]$summary.Groups[1].Value -le 0 -or
            [int]$summary.Groups[2].Value -le 0 -or [int]$summary.Groups[3].Value -ne $before.Count-1) {
            throw "测试终态或计数不匹配 $tag，见 $run"
        }
        $results += @{variant=$tag; compiler=$gcc; arguments=$args; compile_exit=$code; test_exit=$testCode; cases=[int]$summary.Groups[1].Value; checks=[int]$summary.Groups[2].Value; vendor_writes=[int]$summary.Groups[3].Value; output=$output}
        Write-Output "$tag $output"
    }
}
# 将实际编译输入及生成脚本绑定到证据，供独立审查核对版本。
$sourceHashes = @()
$inputs = @($PSCommandPath,$test,(Join-Path $run 'expected_vendor.h'),
    (Join-Path $adapted 'source_manifest.json'),
    (Join-Path $repo 'board/stage3/software/sensor/prepare_vendor.ps1'),
    (Join-Path $repo 'board/stage3/software/sensor/vendor_safety.patch'))
$inputs += @(Get-ChildItem -LiteralPath $mock -File | ForEach-Object { $_.FullName })
foreach ($name in @('i2c/PS_i2c.c','i2c/PS_i2c.h','ov5640.c','ov5640.h')) {
    $inputs += Join-Path $adapted $name
}
foreach ($path in $inputs) {
    $file = Get-Item -LiteralPath $path
    $sourceHashes += @{path=$file.FullName; sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash}
}
$evidence = @{table_entries=$before.Count; table_values_equal=$true; driver_files=$driverHashes; source_files=$sourceHashes; variants=$results; scope='主机 mock 故障注入与真实头签名；非 BSP 构建或板测'}
[IO.File]::WriteAllText((Join-Path $run 'result.json'),($evidence | ConvertTo-Json -Depth 8),$utf8)
Write-Output "证据：$run"
