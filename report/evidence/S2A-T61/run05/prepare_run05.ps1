$ErrorActionPreference='Stop'
$runRoot=(Get-Item -LiteralPath $PSScriptRoot -ErrorAction Stop).FullName
$expectedRunRoot='D:\FPGA_Competition\report\evidence\S2A-T61\run05'
if ($runRoot -cne $expectedRunRoot) { throw "run05 目录不符：$runRoot" }
$repoRoot='D:\FPGA_Competition'
$sourceRoot='D:\FPGA_Competition\report\evidence\S2A-T61\run04'
$fixtureRoot=Join-Path $runRoot 'fixture'
$rtlRoot=Join-Path $runRoot 'rtl'
$referenceRoot=Join-Path $runRoot 'reference'
$workRoot=Join-Path $runRoot 'work'
$tempRoot=Join-Path $runRoot 'temp'
$logsRoot=Join-Path $runRoot 'logs'
$expectedScope='tiny416 cfg section36 layer35; all 256 output channels at y=25, x=0..25'
$sourceFixtureManifestPath=Join-Path $sourceRoot 'fixture\fixture_manifest.json'
$sourcePreparePath=Join-Path $sourceRoot 'prepare_summary.json'
$sourceRuntimePath=Join-Path $sourceRoot 'runtime_result.json'
$sourceRawPath=Join-Path $sourceRoot 'observed_raw.bin'
$sourceInt8Path=Join-Path $sourceRoot 'observed_output.bin'
$sourceLogPath=Join-Path $sourceRoot 'runtime_simulate.log'
$sourceRowReportPath='D:\FPGA_Competition\report\evidence\S2A-T61\layer35_row25_all_channels_run03.json'
$expectedHead='f7ec51b786c70822ff721fecb04660e6fcaa0a6d'
$fixtureNames=@('feature_input.bin','golden.bin','layer35_weights.bin','vectors.txt')
$sourceFiles=@(
    'rtl\int8_conv_tap_geometry.sv',
    'rtl\int8_conv_weight_address.sv',
    'rtl\int8_mac_accumulator.sv',
    'rtl\s2a_conv_engine.sv',
    'rtl\s2a_conv_layer35_channel_probe.sv',
    'rtl\tb_s2a_conv_layer35_row25_all_channels.sv'
)
$requiredFiles=@($sourceFixtureManifestPath,$sourcePreparePath,$sourceRuntimePath,$sourceRawPath,$sourceInt8Path,$sourceLogPath,$sourceRowReportPath)
foreach($path in $requiredFiles){if(-not(Test-Path -LiteralPath $path -PathType Leaf)){throw "run04 证据缺失：$path"}}
$sourceManifest=Get-Content -LiteralPath $sourceFixtureManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$sourcePrepare=Get-Content -LiteralPath $sourcePreparePath -Raw -Encoding UTF8 | ConvertFrom-Json
$sourceRuntime=Get-Content -LiteralPath $sourceRuntimePath -Raw -Encoding UTF8 | ConvertFrom-Json
$rowReport=Get-Content -LiteralPath $sourceRowReportPath -Raw -Encoding UTF8 | ConvertFrom-Json
if($sourceManifest.task_id -cne 'S2A-T61' -or $sourceManifest.run_id -cne 'run04' -or $sourceManifest.fixture_root -cne (Join-Path $sourceRoot 'fixture')){throw 'run04 fixture manifest 身份或根目录不符'}
if($sourcePrepare.task_id -cne 'S2A-T61' -or $sourcePrepare.run_id -cne 'run04' -or $sourcePrepare.status -cne 'PREPARED_NOT_SIMULATED'){throw 'run04 preparation 身份不符'}
if($sourceRuntime.task_id -cne 'S2A-T61' -or $sourceRuntime.run_id -cne 'run04' -or $sourceRuntime.status -cne 'PASS_SIMULATION_DATA_ONLY'){throw 'run04 runtime 不是已记录 PASS'}
if($sourceRuntime.raw_exact_match -ne $true -or $sourceRuntime.int8_exact_match -ne $true -or $sourceRuntime.result_count -ne 6656){throw 'run04 PASS 摘要数据范围不符'}
if($rowReport.task_id -cne 'S2A-T61' -or $rowReport.run_id -cne 'run03' -or $rowReport.scope -cne $expectedScope){throw 'run03 冻结报告身份或范围不符'}
if($sourceManifest.scope -cne $expectedScope -or $sourceManifest.expected_counts.output_cases -ne 6656 -or $sourceManifest.expected_counts.raw_int32_compares -ne 6656 -or $sourceManifest.expected_counts.quantized_int8_compares -ne 6656){throw '冻结输出范围/计数不符'}
if($sourceManifest.fixed_points_yx.Count -ne 26){throw '冻结坐标数不符'}
for($x=0;$x -lt 26;$x++){if($sourceManifest.fixed_points_yx[$x].Count -ne 2 -or $sourceManifest.fixed_points_yx[$x][0] -ne 25 -or $sourceManifest.fixed_points_yx[$x][1] -ne $x){throw "冻结坐标不符：index=$x"}}
$head=(git -C $repoRoot rev-parse HEAD).Trim()
if($head -cne $expectedHead){throw "基线 HEAD 改变：expected=$expectedHead actual=$head"}
function Get-Sha256([string]$path){(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()}
function Get-BytesSha256([byte[]]$bytes){$sha=[Security.Cryptography.SHA256]::Create();try{([BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-','').ToLowerInvariant()}finally{$sha.Dispose()}}
$sourceManifestHash=Get-Sha256 $sourceFixtureManifestPath
$sourceRuntimeHash=Get-Sha256 $sourceRuntimePath
if($sourceRuntime.hashes.fixture_manifest_sha256 -cne $sourceManifestHash){throw 'run04 runtime 摘要绑定的 fixture manifest 哈希不符'}
$sourceOutputHashes=[ordered]@{
    observed_raw=(Get-Sha256 $sourceRawPath)
    observed_int8=(Get-Sha256 $sourceInt8Path)
    runtime_log=(Get-Sha256 $sourceLogPath)
}
if($sourceOutputHashes.observed_raw -cne $sourceRuntime.hashes.observed_raw_sha256 -or $sourceOutputHashes.observed_int8 -cne $sourceRuntime.hashes.observed_int8_sha256 -or $sourceOutputHashes.runtime_log -cne $sourceRuntime.hashes.runtime_log_sha256){throw 'run04 输出或仿真日志与 PASS 摘要哈希不符'}
if((Get-Item -LiteralPath $sourceRawPath).Length -ne 26624 -or (Get-Item -LiteralPath $sourceInt8Path).Length -ne 6656){throw 'run04 输出字节数不符'}
$fixtureBindings=[ordered]@{}
foreach($name in $fixtureNames){
    $source=Join-Path (Join-Path $sourceRoot 'fixture') $name
    $metadata=$sourceManifest.files.PSObject.Properties[$name].Value
    if((Get-Item -LiteralPath $source).Length -ne $metadata.bytes -or (Get-Sha256 $source) -cne $metadata.sha256){throw "run04 fixture 长度或哈希不符：$name"}
    $fixtureBindings[$name]=[ordered]@{source=$source;source_sha256=(Get-Sha256 $source);bytes=$metadata.bytes}
}
$rtlBindings=[ordered]@{}
foreach($relative in $sourceFiles){
    $source=Join-Path $sourceRoot $relative
    if(-not(Test-Path -LiteralPath $source -PathType Leaf)){throw "run04 RTL 副本缺失：$source"}
    $sourceHash=Get-Sha256 $source
    $baseName=Split-Path -Leaf $relative
    if($baseName -ceq 'tb_s2a_conv_layer35_row25_all_channels.sv'){
        $text=[IO.File]::ReadAllText($source,[Text.UTF8Encoding]::new($false,$true))
        $oldSegment='S2A-T61\\run04\\'
        $newSegment='S2A-T61\\run05\\'
        $replacementCount=([regex]::Matches($text,[regex]::Escape($oldSegment))).Count
        if($replacementCount -ne 6){throw "run04 TB 路径段计数不符：$replacementCount"}
        $destinationText=$text.Replace($oldSegment,$newSegment)
        if($destinationText.Contains($oldSegment) -or ([regex]::Matches($destinationText,[regex]::Escape($newSegment))).Count -ne 6){throw 'TB run05 路径替换计数不符'}
        if($destinationText.Replace($newSegment,$oldSegment) -cne $text){throw 'TB 除运行目录字符串外存在语义差异'}
        $destinationBytes=[Text.UTF8Encoding]::new($false).GetBytes($destinationText)
    }else{
        $replacementCount=0
        $destinationBytes=[IO.File]::ReadAllBytes($source)
    }
    $rtlBindings[$relative]=[ordered]@{source=$source;source_sha256=$sourceHash;destination=Join-Path $rtlRoot $baseName;destination_sha256=(Get-BytesSha256 $destinationBytes);path_replacements=$replacementCount}
}
foreach($directory in @($fixtureRoot,$rtlRoot,$referenceRoot,$workRoot,$tempRoot,$logsRoot)){
    if(Test-Path -LiteralPath $directory){throw "run05 子目录已存在，拒绝覆盖：$directory"}
}
$referenceFiles=@(
    [pscustomobject]@{name='run04_observed_raw.bin';source=$sourceRawPath;expected_sha256=$sourceOutputHashes.observed_raw},
    [pscustomobject]@{name='run04_observed_int8.bin';source=$sourceInt8Path;expected_sha256=$sourceOutputHashes.observed_int8},
    [pscustomobject]@{name='run04_runtime_result.json';source=$sourceRuntimePath;expected_sha256=$sourceRuntimeHash},
    [pscustomobject]@{name='run04_runtime_simulate.log';source=$sourceLogPath;expected_sha256=$sourceOutputHashes.runtime_log}
)
foreach($directory in @($fixtureRoot,$rtlRoot,$referenceRoot,$workRoot,$tempRoot,$logsRoot)){[void][IO.Directory]::CreateDirectory($directory)}
function Write-NewBytes([string]$path,[byte[]]$bytes){
    $stream=[IO.File]::Open($path,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
    try{$stream.Write($bytes,0,$bytes.Length)}finally{$stream.Dispose()}
}
foreach($name in $fixtureNames){
    $source=Join-Path (Join-Path $sourceRoot 'fixture') $name
    $dest=Join-Path $fixtureRoot $name
    Write-NewBytes $dest ([IO.File]::ReadAllBytes($source))
    if((Get-Sha256 $dest) -cne $fixtureBindings[$name].source_sha256){throw "run05 fixture 复制校验失败：$name"}
}
$runManifest=ConvertFrom-Json ($sourceManifest | ConvertTo-Json -Depth 40)
$runManifest.run_id='run05'
$runManifest.fixture_root=$fixtureRoot
foreach($name in $fixtureNames){$runManifest.files.PSObject.Properties[$name].Value.path=(Join-Path $fixtureRoot $name)}
$manifestBytes=[Text.UTF8Encoding]::new($false).GetBytes(($runManifest | ConvertTo-Json -Depth 40))
Write-NewBytes (Join-Path $fixtureRoot 'fixture_manifest.json') $manifestBytes
foreach($relative in $sourceFiles){
    $binding=$rtlBindings[$relative]
    $source=Join-Path $sourceRoot $relative
    $dest=$binding.destination
    if((Split-Path -Leaf $relative) -ceq 'tb_s2a_conv_layer35_row25_all_channels.sv'){
        $text=[IO.File]::ReadAllText($source,[Text.UTF8Encoding]::new($false,$true)).Replace('S2A-T61\\run04\\','S2A-T61\\run05\\')
        $bytes=[Text.UTF8Encoding]::new($false).GetBytes($text)
    }else{$bytes=[IO.File]::ReadAllBytes($source)}
    Write-NewBytes $dest $bytes
    if((Get-Sha256 $dest) -cne $binding.destination_sha256){throw "run05 RTL 复制校验失败：$relative"}
}
foreach($item in $referenceFiles){
    $dest=Join-Path $referenceRoot $item.name
    Write-NewBytes $dest ([IO.File]::ReadAllBytes($item.source))
    if((Get-Sha256 $dest) -cne $item.expected_sha256){throw "run04 参考证据复制校验失败：$($item.name)"}
}
$vendorGlbl='D:\Xilinx\2026.1\Vivado\data\verilog\src\glbl.v'
if(-not(Test-Path -LiteralPath $vendorGlbl -PathType Leaf)){throw "Vivado glbl.v 缺失：$vendorGlbl"}
$glblDest=Join-Path $workRoot 'glbl.v'
Write-NewBytes $glblDest ([IO.File]::ReadAllBytes($vendorGlbl))
$prjPath=Join-Path $workRoot 'tb_s2a_conv_layer35_row25_all_channels_vlog.prj'
$prjLines=[string[]]@(
    ('sv xil_defaultlib "'+((Join-Path $rtlRoot 'int8_conv_tap_geometry.sv').Replace('\','/'))+'"'),
    ('sv xil_defaultlib "'+((Join-Path $rtlRoot 'int8_conv_weight_address.sv').Replace('\','/'))+'"'),
    ('sv xil_defaultlib "'+((Join-Path $rtlRoot 'int8_mac_accumulator.sv').Replace('\','/'))+'"'),
    ('sv xil_defaultlib "'+((Join-Path $rtlRoot 's2a_conv_engine.sv').Replace('\','/'))+'"'),
    ('sv xil_defaultlib "'+((Join-Path $rtlRoot 's2a_conv_layer35_channel_probe.sv').Replace('\','/'))+'"'),
    ('sv xil_defaultlib "'+((Join-Path $rtlRoot 'tb_s2a_conv_layer35_row25_all_channels.sv').Replace('\','/'))+'"'),
    ('verilog xil_defaultlib "'+($glblDest.Replace('\','/'))+'"')
)
$prjText=($prjLines -join [Environment]::NewLine)+[Environment]::NewLine
[IO.File]::WriteAllText($prjPath,$prjText,[Text.UTF8Encoding]::new($false))
$batchPath=Join-Path $workRoot 'run05_batch.tcl'
$batch='run all'+[Environment]::NewLine+'quit'+[Environment]::NewLine
[IO.File]::WriteAllText($batchPath,$batch,[Text.UTF8Encoding]::new($false))
$referenceBinding=[ordered]@{}
foreach($item in $referenceFiles){
    $dest=Join-Path $referenceRoot $item.name
    $referenceBinding[$item.name]=[ordered]@{path=$dest;bytes=(Get-Item -LiteralPath $dest).Length;sha256=(Get-Sha256 $dest);source=$item.source;source_sha256=$item.expected_sha256}
}
$fixtureManifestHash=Get-Sha256 (Join-Path $fixtureRoot 'fixture_manifest.json')
$summary=[ordered]@{
    task_id='S2A-T61'
    run_id='run05'
    status='PREPARED_NOT_SIMULATED'
    prepared_at_utc8=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss zzz')
    baseline_head=$head
    scope=$expectedScope
    expected_counts=[ordered]@{raw_int32_compares=6656;int8_compares=6656;raw_bytes=26624;int8_bytes=6656;golden_bytes=33280}
    mcp_preflight=[ordered]@{
        check_connection='Vivado plugin is healthy; version 2026.1'
        connected_instance='s2a_t61_run04'
        connected_directory='D:/FPGA_Competition/report/evidence/S2A-T61/run04/isolated_project'
        connected_xpr=''
        connected_top=''
        project_state='isolated instance has no XPR/top; no project/simulation-state commands sent'
        run05_invocation='MCP run_tcl with Tcl exec to run05_runner.ps1'
    }
    source_run04=[ordered]@{
        prepare_summary=Join-Path $sourceRoot 'prepare_summary.json'
        prepare_summary_sha256=(Get-Sha256 $sourcePreparePath)
        fixture_manifest=$sourceFixtureManifestPath
        fixture_manifest_sha256=$sourceManifestHash
        runtime_result=$sourceRuntimePath
        runtime_result_sha256=$sourceRuntimeHash
        raw_sha256=$sourceOutputHashes.observed_raw
        int8_sha256=$sourceOutputHashes.observed_int8
        runtime_log_sha256=$sourceOutputHashes.runtime_log
    }
    fixture_bindings=$fixtureBindings
    rtl_bindings=$rtlBindings
    references=$referenceBinding
    run05_fixture_manifest_sha256=$fixtureManifestHash
    testbench_path_replacements=6
    reference_semantic_check='run05 TB path rollback equals run04 TB byte text'
    temp_roots=[ordered]@{TEMP=$tempRoot;TMP=$tempRoot;TMPDIR=$tempRoot}
    vivado_project_opened=$false
    simulation='NOT_RUN'
}
$summaryPath=Join-Path $runRoot 'prepare_summary.json'
Write-NewBytes $summaryPath ([Text.UTF8Encoding]::new($false).GetBytes(($summary | ConvertTo-Json -Depth 40)))
$plan=[ordered]@{
    task_id='S2A-T61'
    run_id='run05'
    command='MCP vivado-mcp run_tcl -> Tcl exec powershell.exe -NoProfile -ExecutionPolicy Bypass -File run05_runner.ps1'
    working_directory=$workRoot
    estimated_elapsed_minutes=12
    stop_conditions=@('error/FATAL/$fatal/output mismatch','free physical RAM below 2048 MiB','simulation log has no new PROGRESS output for 15 minutes')
    protected_existing_process_ids=@(8712,13156,22488)
    logs=@('pre_run_process_snapshot.json','process_runs.json','logs\xvlog.stdout.txt','logs\xvlog.stderr.txt','logs\xvlog.log','logs\xelab.stdout.txt','logs\xelab.stderr.txt','logs\xelab.log','logs\xsim.stdout.txt','logs\xsim.stderr.txt','logs\xsim.log','logs\runtime_simulate.log')
    expected_results=@{raw_compares=6656;int8_compares=6656;raw_bytes=26624;int8_bytes=6656;unique_PASS_lines=1;unique_finish_lines=1}
}
Write-NewBytes (Join-Path $runRoot 'run_plan.json') ([Text.UTF8Encoding]::new($false).GetBytes(($plan | ConvertTo-Json -Depth 20)))
Write-Output 'T61_RUN05_PREPARE=PASS run04_fixture_and_RTL_bound=1 tb_path_replacements=6 semantics_restored=1 references_bound=1 all_generated_paths=D:'