$ErrorActionPreference='Stop'
$runRoot=(Get-Item -LiteralPath $PSScriptRoot -ErrorAction Stop).FullName
$expectedRoot='D:\FPGA_Competition\report\evidence\S2A-T61\run05'
$attemptRoot=Join-Path $runRoot 'attempt02'
if($runRoot -cne $expectedRoot){throw "run05 验证目录不符：$runRoot"}
$prepPath=Join-Path $runRoot 'prepare_summary.json'
$runStatusPath=Join-Path $attemptRoot 'run_status.json'
$processRunsPath=Join-Path $attemptRoot 'process_runs.json'
$preSnapshotPath=Join-Path $attemptRoot 'pre_run_process_snapshot.json'
$postSnapshotPath=Join-Path $attemptRoot 'post_run_process_snapshot.json'
$manifestPath=Join-Path (Join-Path $runRoot 'fixture') 'fixture_manifest.json'
$goldenPath=Join-Path (Join-Path $runRoot 'fixture') 'golden.bin'
$rawPath=Join-Path $runRoot 'observed_raw.bin'
$int8Path=Join-Path $runRoot 'observed_output.bin'
$runtimeLogPath=Join-Path (Join-Path $attemptRoot 'logs') 'runtime_simulate.log'
$referenceRoot=Join-Path $runRoot 'reference'
$required=@($prepPath,$runStatusPath,$processRunsPath,$preSnapshotPath,$postSnapshotPath,$manifestPath,$goldenPath,$rawPath,$int8Path,$runtimeLogPath)
foreach($p in $required){if(-not(Test-Path -LiteralPath $p -PathType Leaf)){throw "验证证据缺失：$p"}}
$prep=Get-Content -LiteralPath $prepPath -Raw -Encoding UTF8 | ConvertFrom-Json
$status=Get-Content -LiteralPath $runStatusPath -Raw -Encoding UTF8 | ConvertFrom-Json
$processRuns=@(Get-Content -LiteralPath $processRunsPath -Raw -Encoding UTF8 | ConvertFrom-Json)
$pre=Get-Content -LiteralPath $preSnapshotPath -Raw -Encoding UTF8 | ConvertFrom-Json
$post=Get-Content -LiteralPath $postSnapshotPath -Raw -Encoding UTF8 | ConvertFrom-Json
$manifest=Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$refRuntimePath=Join-Path $referenceRoot 'run04_runtime_result.json'
$refRawPath=Join-Path $referenceRoot 'run04_observed_raw.bin'
$refInt8Path=Join-Path $referenceRoot 'run04_observed_int8.bin'
$refRuntime=Get-Content -LiteralPath $refRuntimePath -Raw -Encoding UTF8 | ConvertFrom-Json
function Get-Sha256([string]$path){(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function Test-BytesEqual([byte[]]$left,[byte[]]$right){
    if($left.Length -ne $right.Length){return $false}
    for($i=0;$i -lt $left.Length;$i++){if($left[$i] -ne $right[$i]){return $false}}
    return $true
}
if($prep.task_id -cne 'S2A-T61' -or $prep.run_id -cne 'run05' -or $prep.status -cne 'PREPARED_NOT_SIMULATED'){throw '准备摘要身份或状态不符'}
if($prep.baseline_head -cne 'f7ec51b786c70822ff721fecb04660e6fcaa0a6d'){throw 'run05 基线 HEAD 不符'}
if($status.status -cne 'RUN_COMPLETED_PENDING_VERIFICATION' -or $null -ne $status.failure){throw "runner 状态未成功：$($status.status) $($status.failure)"}
if($manifest.task_id -cne 'S2A-T61' -or $manifest.run_id -cne 'run05' -or $manifest.fixture_root -cne (Join-Path $runRoot 'fixture')){throw 'run05 fixture manifest 身份或根路径不符'}
if((Get-Sha256 $manifestPath) -cne $prep.run05_fixture_manifest_sha256){throw 'run05 fixture manifest 哈希不符'}
if($manifest.scope -cne $prep.scope -or $manifest.expected_counts.output_cases -ne 6656 -or $manifest.expected_counts.raw_int32_compares -ne 6656 -or $manifest.expected_counts.quantized_int8_compares -ne 6656){throw 'run05 fixture 规格/计数不符'}
if($manifest.fixed_points_yx.Count -ne 26){throw 'run05 fixture 坐标数不符'}
for($x=0;$x -lt 26;$x++){if($manifest.fixed_points_yx[$x].Count -ne 2 -or $manifest.fixed_points_yx[$x][0] -ne 25 -or $manifest.fixed_points_yx[$x][1] -ne $x){throw "run05 fixture 坐标错误：index=$x"}}
foreach($name in @('feature_input.bin','golden.bin','layer35_weights.bin','vectors.txt')){
    $path=Join-Path (Join-Path $runRoot 'fixture') $name
    $meta=$manifest.files.PSObject.Properties[$name].Value
    $binding=$prep.fixture_bindings.PSObject.Properties[$name].Value
    if($meta.path -cne $path -or $meta.bytes -ne $binding.bytes -or (Get-Item -LiteralPath $path).Length -ne $binding.bytes){throw "run05 fixture 路径或长度不符：$name"}
    if((Get-Sha256 $path) -cne $binding.source_sha256 -or $meta.sha256 -cne $binding.source_sha256){throw "run05 fixture 哈希偏离 run04：$name"}
}
$run04TB=$prep.rtl_bindings.'rtl\tb_s2a_conv_layer35_row25_all_channels.sv'
$run05TBPath=$run04TB.destination
$run04TBPath=$run04TB.source
if((Get-Sha256 $run05TBPath) -cne $run04TB.destination_sha256){throw 'run05 TB 哈希偏离准备绑定'}
$oldSegment='S2A-T61\\run04\\'
$newSegment='S2A-T61\\run05\\'
$run05Text=[IO.File]::ReadAllText($run05TBPath,[Text.UTF8Encoding]::new($false,$true))
$run04Text=[IO.File]::ReadAllText($run04TBPath,[Text.UTF8Encoding]::new($false,$true))
if(([regex]::Matches($run05Text,[regex]::Escape($newSegment))).Count -ne 6 -or $run05Text.Contains($oldSegment)){throw 'run05 TB 路径字面量替换不符'}
if($run05Text.Replace($newSegment,$oldSegment) -cne $run04Text){throw 'run05 TB 语义回滚校验失败'}
foreach($relative in @('rtl\int8_conv_tap_geometry.sv','rtl\int8_conv_weight_address.sv','rtl\int8_mac_accumulator.sv','rtl\s2a_conv_engine.sv','rtl\s2a_conv_layer35_channel_probe.sv')){
    $binding=$prep.rtl_bindings.PSObject.Properties[$relative].Value
    if((Get-Sha256 $binding.destination) -cne $binding.source_sha256){throw "RTL 字节哈希偏离 run04：$relative"}
}
if((Get-Sha256 $refRuntimePath) -cne $prep.source_run04.runtime_result_sha256 -or $refRuntime.status -cne 'PASS_SIMULATION_DATA_ONLY'){throw 'run04 runtime reference 绑定不符'}
if((Get-Sha256 $refRawPath) -cne $prep.source_run04.raw_sha256 -or (Get-Sha256 $refInt8Path) -cne $prep.source_run04.int8_sha256){throw 'run04 参考输出哈希不符'}
$raw=[IO.File]::ReadAllBytes($rawPath)
$int8=[IO.File]::ReadAllBytes($int8Path)
$golden=[IO.File]::ReadAllBytes($goldenPath)
$refRaw=[IO.File]::ReadAllBytes($refRawPath)
$refInt8=[IO.File]::ReadAllBytes($refInt8Path)
if($raw.Length -ne 26624 -or $int8.Length -ne 6656 -or $golden.Length -ne 33280){throw "run05 输出长度错误：raw=$($raw.Length) int8=$($int8.Length) golden=$($golden.Length)"}
$goldRaw=[byte[]]::new(26624)
$goldInt8=[byte[]]::new(6656)
[Array]::Copy($golden,0,$goldRaw,0,26624)
[Array]::Copy($golden,26624,$goldInt8,0,6656)
if(-not(Test-BytesEqual $raw $goldRaw)){throw 'run05 raw INT32 输出与冻结 golden 不一致'}
if(-not(Test-BytesEqual $int8 $goldInt8)){throw 'run05 INT8 输出与冻结 golden 不一致'}
if(-not(Test-BytesEqual $raw $refRaw)){throw 'run05 raw INT32 输出与 run04 输出不一致'}
if(-not(Test-BytesEqual $int8 $refInt8)){throw 'run05 INT8 输出与 run04 输出不一致'}
$runtimeLog=[IO.File]::ReadAllText($runtimeLogPath,[Text.UTF8Encoding]::new($false,$true))
$passMatches=[regex]::Matches($runtimeLog,'(?m)^PASS T61 outputs=6656 raw=6656[^\r\n]*')
$finishMatches=[regex]::Matches($runtimeLog,'(?m)^\$finish called at time : ([0-9]+) ns')
if($passMatches.Count -ne 1){throw "PASS 行数量不为 1：$($passMatches.Count)"}
if($finishMatches.Count -ne 1){throw "正常 $finish 行数量不为 1：$($finishMatches.Count)"}
if($passMatches[0].Value -cne $refRuntime.pass_line){throw 'PASS 行事务计数与 run04 不同'}
if([long]$finishMatches[0].Groups[1].Value -ne [long]$refRuntime.finish_time_ns){throw '仿真时间与 run04 冻结运行不同'}
if($runtimeLog -match '(?im)^\s*(?:ERROR:|FATAL:|Fatal:)|\$fatal|raw INT32|INT8 result|不匹配|无法打开|截断|长度过长'){throw '仿真日志包含 error/FATAL/输出 mismatch'}
$stageExpected=@('xvlog','xelab','xsim')
if($processRuns.Count -ne 3){throw "仿真工具阶段数不为 3：$($processRuns.Count)"}
foreach($name in $stageExpected){
    $entry=@($processRuns | Where-Object {$_.stage -ceq $name})
    if($entry.Count -ne 1 -or $entry[0].exit_code -ne 0 -or $entry[0].pid -le 0){throw "工具阶段退出记录不合格：$name"}
}
foreach($run in $processRuns){
    foreach($child in @($run.child_processes)){
        if($child.active -eq $true){throw "run05 子进程仍运行：$($child.pid) $($child.name)"}
        if($null -ne $child.exit_code -and $child.exit_code -ne 0){throw "run05 子进程退出码异常：$($child.pid) $($child.exit_code)"}
    }
}
$protected=@(8712,13156,22488)
$preById=@{}
$postById=@{}
foreach($p in $pre.fpga_processes){$preById[[string]$p.pid]=$p}
foreach($p in $post.fpga_processes){$postById[[string]$p.pid]=$p}
$protectedChecks=@()
foreach($pidValue in $protected){
    $key=[string]$pidValue
    if($preById.ContainsKey($key)){
        if($postById.ContainsKey($key)){
            $before=$preById[$key];$after=$postById[$key]
            if($before.name -cne $after.name -or $before.executable_path -cne $after.executable_path -or $before.command_line -cne $after.command_line){throw "受保护进程身份变化：PID $pidValue"}
            $state='same_process_still_present'
        }else{$state='absent_after_run_process_exited_without_agent_action'}
    }else{$state='not_present_at_run_start'}
    $protectedChecks += [pscustomobject]@{pid=$pidValue;state=$state}
}
$run04Stable=@()
foreach($entry in @(
    [pscustomobject]@{path='D:\FPGA_Competition\report\evidence\S2A-T61\run04\fixture\fixture_manifest.json';sha=$prep.source_run04.fixture_manifest_sha256},
    [pscustomobject]@{path='D:\FPGA_Competition\report\evidence\S2A-T61\run04\runtime_result.json';sha=$prep.source_run04.runtime_result_sha256},
    [pscustomobject]@{path='D:\FPGA_Competition\report\evidence\S2A-T61\run04\observed_raw.bin';sha=$prep.source_run04.raw_sha256},
    [pscustomobject]@{path='D:\FPGA_Competition\report\evidence\S2A-T61\run04\observed_output.bin';sha=$prep.source_run04.int8_sha256},
    [pscustomobject]@{path='D:\FPGA_Competition\report\evidence\S2A-T61\run04\runtime_simulate.log';sha=$prep.source_run04.runtime_log_sha256}
)){
    if((Get-Sha256 $entry.path) -cne $entry.sha){throw "run04 原始证据在 run05 期间哈希改变：$($entry.path)"}
    $run04Stable += $entry.path
}
$toolLogs=@(
    (Join-Path (Join-Path $attemptRoot 'logs') 'xvlog.log'),
    (Join-Path (Join-Path $attemptRoot 'logs') 'xelab.log'),
    (Join-Path (Join-Path $attemptRoot 'logs') 'xsim.log'),
    (Join-Path (Join-Path $attemptRoot 'logs') 'xvlog.stdout.txt'),
    (Join-Path (Join-Path $attemptRoot 'logs') 'xvlog.stderr.txt'),
    (Join-Path (Join-Path $attemptRoot 'logs') 'xelab.stdout.txt'),
    (Join-Path (Join-Path $attemptRoot 'logs') 'xelab.stderr.txt'),
    (Join-Path (Join-Path $attemptRoot 'logs') 'xsim.stdout.txt'),
    (Join-Path (Join-Path $attemptRoot 'logs') 'xsim.stderr.txt')
)
foreach($p in $toolLogs){if(-not(Test-Path -LiteralPath $p -PathType Leaf)){throw "工具控制台/log 缺失：$p"}}
$verification=[ordered]@{
    task_id='S2A-T61'
    run_id='run05'
    attempt='attempt02'
    status='PASS_DATA_REPRODUCED'
    verified_at_utc8=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss zzz')
    scope=$prep.scope
    baseline_head=$prep.baseline_head
    xsim_finish_time_ns=[long]$finishMatches[0].Groups[1].Value
    raw_int32=[ordered]@{count=6656;bytes=$raw.Length;sha256=(Get-Sha256 $rawPath);golden_exact_match=$true;run04_exact_match=$true}
    int8=[ordered]@{count=6656;bytes=$int8.Length;sha256=(Get-Sha256 $int8Path);golden_exact_match=$true;run04_exact_match=$true}
    pass_line=$passMatches[0].Value
    process_runs=$processRuns
    protected_process_identity_checks=$protectedChecks
    run04_reference_unchanged_paths=$run04Stable
    limitation='T61 row25数据级重跑证据；不等于完整整网、G4或G5验收'
}
$resultPath=Join-Path $runRoot 'verification_result.json'
$attempt01=Get-Content -LiteralPath (Join-Path (Join-Path $runRoot 'attempt01') 'attempt_result.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$final=[ordered]@{task_id='S2A-T61';run_id='run05';status='PASS_DATA_REPRODUCED';successful_attempt='attempt02';failed_attempt='attempt01';attempt01_failure=$attempt01.failure;verification_result=$resultPath;scope=$prep.scope;completed_at_utc8=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss zzz')}
[IO.File]::WriteAllText((Join-Path $runRoot 'run05_final_result.json'),($final | ConvertTo-Json -Depth 20),[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($resultPath,($verification | ConvertTo-Json -Depth 40),[Text.UTF8Encoding]::new($false))
$files=@(Get-ChildItem -LiteralPath $runRoot -Force -Recurse -File | Where-Object {$_.FullName -cne (Join-Path $runRoot 'hash_manifest.json')})
$items=@()
foreach($file in $files){
    $relative=$file.FullName.Substring($runRoot.Length+1)
    $items += [pscustomobject]@{path=$relative;bytes=$file.Length;sha256=(Get-Sha256 $file.FullName)}
}
$hashManifest=[ordered]@{task_id='S2A-T61';run_id='run05';generated_at_utc8=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss zzz');file_count=$items.Count;files=$items}
$hashPath=Join-Path $runRoot 'hash_manifest.json'
[IO.File]::WriteAllText($hashPath,($hashManifest | ConvertTo-Json -Depth 10),[Text.UTF8Encoding]::new($false))
$hash=(Get-Sha256 $hashPath)
Write-Output "T61_RUN05_VERIFY=PASS raw=6656 int8=6656 raw_bytes=$($raw.Length) int8_bytes=$($int8.Length) finish_ns=$($verification.xsim_finish_time_ns)"
Write-Output "HASH_MANIFEST_SHA256=$hash FILES=$($items.Count)"