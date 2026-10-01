param([switch]$ValidateManifestOnly)
$ErrorActionPreference='Stop'
$runRoot=(Get-Item -LiteralPath $PSScriptRoot -ErrorAction Stop).FullName
$expectedRoot='D:\FPGA_Competition\report\evidence\S2A-T61\run05\attempt05'
if(-not $ValidateManifestOnly -and $runRoot -cne $expectedRoot){throw "run05 runner 目录不符：$runRoot"}
$attemptRoot=$runRoot
$manifestPath=Join-Path $attemptRoot 'input_manifest.json'
function Get-ManifestFileSha256([string]$path){
    $stream=$null
    $sha=$null
    try{
        $stream=[IO.File]::OpenRead($path)
        $sha=[Security.Cryptography.SHA256]::Create()
        return ([BitConverter]::ToString($sha.ComputeHash($stream)).Replace('-','').ToLowerInvariant())
    }finally{
        if($null -ne $stream){$stream.Dispose()}
        if($null -ne $sha){$sha.Dispose()}
    }
}
function Test-JsonInteger($value){return ($value -is [int] -or $value -is [long])}
function Get-ManifestRegularFile([string]$rootPath,[string]$pathText,[string]$field){
    if([string]::IsNullOrWhiteSpace($pathText)){throw "$field 路径为空"}
    if(-not [IO.Path]::IsPathRooted($pathText)){throw "$field 路径不是绝对路径：$pathText"}
    if($pathText.Contains('/')){throw "$field 路径必须使用规范 Windows 分隔符：$pathText"}
    $fullPath=[IO.Path]::GetFullPath($pathText)
    if(-not [string]::Equals($pathText,$fullPath,[StringComparison]::Ordinal)){throw "$field 路径不是规范完整路径：$pathText"}
    $rootPrefix=$rootPath.TrimEnd([char[]]@('\','/'))+'\'
    if(-not $fullPath.StartsWith($rootPrefix,[StringComparison]::OrdinalIgnoreCase)){throw "$field 路径越出 attempt05 根目录：$pathText"}
    $relativePath=$fullPath.Substring($rootPrefix.Length)
    if([string]::IsNullOrWhiteSpace($relativePath)){throw "$field 路径指向 attempt05 根目录而不是文件：$pathText"}
    $rootItem=Get-Item -LiteralPath $rootPath -Force -ErrorAction Stop
    if(-not $rootItem.PSIsContainer -or (($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) -or (($rootItem.Attributes -band [IO.FileAttributes]::Device) -ne 0)){throw "attempt05 根目录不是普通目录：$rootPath"}
    $parts=$relativePath.Split([char[]]@('\'),[StringSplitOptions]::RemoveEmptyEntries)
    if($parts.Count -eq 0){throw "$field 路径没有文件名：$pathText"}
    $cursor=$rootPath
    $item=$null
    for($index=0;$index -lt $parts.Count;$index++){
        $cursor=Join-Path $cursor $parts[$index]
        $item=Get-Item -LiteralPath $cursor -Force -ErrorAction Stop
        if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw "$field 路径包含重解析点：$cursor"}
        if($index -lt ($parts.Count-1) -and -not $item.PSIsContainer){throw "$field 父路径组件不是目录：$cursor"}
        if($index -eq ($parts.Count-1) -and ($item.PSIsContainer -or (($item.Attributes -band [IO.FileAttributes]::Device) -ne 0))){throw "$field 不是普通文件：$cursor"}
    }
    return $item
}
function Assert-InputManifest([string]$rootPath,[string]$executingRunnerPath){
    $rootFull=[IO.Path]::GetFullPath($rootPath)
    $runnerFull=[IO.Path]::GetFullPath($executingRunnerPath)
    $manifestFull=Join-Path $rootFull 'input_manifest.json'
    $null=Get-ManifestRegularFile $rootFull $manifestFull 'input_manifest'
    try{$manifest=Get-Content -LiteralPath $manifestFull -Raw -Encoding UTF8 | ConvertFrom-Json -ErrorAction Stop}catch{throw "input_manifest.json 不是有效 UTF-8 JSON：$($_.Exception.Message)"}
    foreach($binding in @(
        @{name='schema';value='S2A-T61-attempt-input-manifest-v2'},
        @{name='task_id';value='S2A-T61'},
        @{name='run_id';value='run05'},
        @{name='attempt';value='attempt05'},
        @{name='status';value='PREPARED_NOT_RUN'}
    )){
        $bindingProperty=$manifest.PSObject.Properties[[string]$binding.name]
        if($null -eq $bindingProperty){throw "input_manifest 缺少字段：$($binding.name)"}
        if(-not [string]::Equals([string]$bindingProperty.Value,[string]$binding.value,[StringComparison]::Ordinal)){throw ('input_manifest '+$binding.name+' 不匹配：'+$bindingProperty.Value)}
    }
    $fileCountIsInteger=Test-JsonInteger -value $manifest.file_count
    if($fileCountIsInteger -ne $true -or [long]$manifest.file_count -ne 22){throw 'input_manifest file_count 必须是整数 22'}
    $files=@($manifest.files)
    if($null -eq $manifest.files -or $files.Count -ne 22){throw 'input_manifest files 必须恰有 22 个条目'}
    if(-not [string]::Equals([string]$manifest.execution_runner,$runnerFull,[StringComparison]::Ordinal)){throw "执行 runner 完整路径与 execution_runner 不一致：$runnerFull"}
    $runnerBytesAreInteger=Test-JsonInteger -value $manifest.execution_runner_bytes
    if($runnerBytesAreInteger -ne $true){throw 'input_manifest execution_runner_bytes 必须是整数'}
    if([long]$manifest.execution_runner_bytes -le 0){throw 'input_manifest execution_runner_bytes 必须是正整数'}
    if(([string]$manifest.execution_runner_sha256) -notmatch '^[0-9a-f]{64}$'){throw 'input_manifest execution_runner_sha256 格式错误'}
    $seen=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $runnerEntryCount=0
    foreach($entry in $files){
        if($null -eq $entry -or [string]::IsNullOrWhiteSpace([string]$entry.path)){throw 'input_manifest 含空文件条目或路径'}
        $entryPath=[string]$entry.path
        $file=(Get-ManifestRegularFile -rootPath $rootFull -pathText $entryPath -field 'manifest-file')
        $normalizedPath=[IO.Path]::GetFullPath([string]$entry.path)
        if(-not $seen.Add($normalizedPath)){throw "input_manifest files 存在重复路径：$normalizedPath"}
        $entryBytesAreInteger=Test-JsonInteger -value $entry.bytes
        if($entryBytesAreInteger -ne $true -or [long]$entry.bytes -le 0){throw "input_manifest 文件长度必须为正整数：$normalizedPath"}
        if(([string]$entry.sha256) -notmatch '^[0-9a-f]{64}$'){throw "input_manifest 文件 SHA-256 格式错误：$normalizedPath"}
        if([long]$file.Length -ne [long]$entry.bytes){throw "input_manifest 文件长度不匹配：$normalizedPath"}
        $actualHash=Get-ManifestFileSha256 $normalizedPath
        if(-not [string]::Equals($actualHash,[string]$entry.sha256,[StringComparison]::Ordinal)){throw "input_manifest 文件 SHA-256 不匹配：$normalizedPath"}
        if([string]::Equals($normalizedPath,$runnerFull,[StringComparison]::Ordinal)){$runnerEntryCount++}
    }
    if($runnerEntryCount -ne 1){throw "执行 runner 必须在 files 中恰有一个对应条目：count=$runnerEntryCount"}
    $runnerItem=Get-ManifestRegularFile $rootFull $runnerFull 'execution_runner'
    $runnerHash=Get-ManifestFileSha256 $runnerFull
    if([long]$runnerItem.Length -ne [long]$manifest.execution_runner_bytes){throw '执行 runner 长度与顶层绑定不匹配'}
    if(-not [string]::Equals($runnerHash,[string]$manifest.execution_runner_sha256,[StringComparison]::Ordinal)){throw '执行 runner SHA-256 与顶层绑定不匹配'}
    return [pscustomobject]@{state='PASS';checked_at_utc8=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss zzz');file_count=$files.Count;runner_path=$runnerFull;runner_bytes=[long]$runnerItem.Length;runner_sha256=$runnerHash}
}
$initialManifestValidation=Assert-InputManifest $attemptRoot $PSCommandPath
if($ValidateManifestOnly){
    Write-Output "T61_MANIFEST_VALIDATION_PASS files=$($initialManifestValidation.file_count) runner_bytes=$($initialManifestValidation.runner_bytes) runner_sha256=$($initialManifestValidation.runner_sha256) simulation_status=NO_SIMULATION"
    return
}
$workRoot=Join-Path $attemptRoot 'work'
$tempRoot=Join-Path $attemptRoot 'temp'
$logsRoot=Join-Path $attemptRoot 'logs'
$planPath=Join-Path $attemptRoot 'run_plan.json'
$required=@($planPath,(Join-Path $runRoot 'prepare_summary.json'),(Join-Path $workRoot 'tb_s2a_conv_layer35_row25_all_channels_vlog.prj'),(Join-Path $workRoot 'run05_batch.tcl'))
foreach($p in $required){if(-not(Test-Path -LiteralPath $p -PathType Leaf)){throw "运行输入缺失：$p"}}
$plan=Get-Content -LiteralPath $planPath -Raw -Encoding UTF8 | ConvertFrom-Json
if([int]$plan.pass_definition.pass_marker_count -ne 1){throw 'run_plan 冻结 PASS 标记数量必须为 1'}
if([int]$plan.pass_definition.finish_marker_count -ne 1){throw 'run_plan 冻结 finish 标记数量必须为 1'}
if([long]$plan.pass_definition.finish_time_ns -ne [long]2134685240){throw 'run_plan 冻结 finish_time_ns 必须为 2134685240'}
$toolRoot='D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o'
$binRoot='D:\Xilinx\2026.1\Vivado\bin'
$commandProcessor=Join-Path $env:WINDIR 'System32\cmd.exe'
$toolMap=[ordered]@{
    xvlog=Join-Path $binRoot 'xvlog.bat'
    xelab=Join-Path $binRoot 'xelab.bat'
    xsim=Join-Path $binRoot 'xsim.bat'
}
foreach($name in @('xvlog','xelab','xsim')){if(-not(Test-Path -LiteralPath $toolMap[$name] -PathType Leaf)){throw "Vivado CLI 工具缺失：$($toolMap[$name])"}}
if(-not(Test-Path -LiteralPath $commandProcessor -PathType Leaf)){throw "Windows 命令处理器缺失：$commandProcessor"}

$env:TEMP=$tempRoot
$env:TMP=$tempRoot
$env:TMPDIR=$tempRoot
$env:XILINX_VIVADO='D:\Xilinx\2026.1\Vivado'
$env:PATH=$toolRoot+';'+$binRoot+';'+$env:PATH
$utf8=[Text.UTF8Encoding]::new($false)
function Write-JsonFile([string]$path,$value){[IO.File]::WriteAllText($path,($value | ConvertTo-Json -Depth 40),$utf8)}
function Get-FpgaProcesses{
    $all=Get-CimInstance Win32_Process
    $result=@()
    foreach($p in $all){
        if($p.Name -match '^(vivado|xsim|xsimk|xelab|xvlog)\.exe$'){
            $ws=0
            try{$ws=(Get-Process -Id $p.ProcessId -ErrorAction Stop).WorkingSet64}catch{}
            $result += [pscustomobject]@{pid=[int]$p.ProcessId;parent_pid=[int]$p.ParentProcessId;name=$p.Name;executable_path=$p.ExecutablePath;command_line=$p.CommandLine;working_set_bytes=$ws}
        }
    }
    return @($result | Sort-Object pid)
}
function Get-ResourceSnapshot{
    $os=Get-CimInstance Win32_OperatingSystem
    $drive=[IO.DriveInfo]::new('D:\')
    [pscustomobject]@{captured_at_utc8=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss zzz');d_free_bytes=$drive.AvailableFreeSpace;d_total_bytes=$drive.TotalSize;free_physical_mib=[Math]::Round(($os.FreePhysicalMemory*1KB)/1MB,0);total_physical_mib=[Math]::Round(($os.TotalVisibleMemorySize*1KB)/1MB,0)}
}
function Get-ProcessTree([int]$rootPid){
    $all=@(Get-CimInstance Win32_Process)
    $seen=[System.Collections.Generic.HashSet[int]]::new()
    [void]$seen.Add($rootPid)
    $changed=$true
    while($changed){
        $changed=$false
        foreach($p in $all){
            if($seen.Contains([int]$p.ParentProcessId) -and -not $seen.Contains([int]$p.ProcessId)){
                [void]$seen.Add([int]$p.ProcessId)
                $changed=$true
            }
        }
    }
    return @($all | Where-Object {$seen.Contains([int]$_.ProcessId)})
}
$processRuns=[System.Collections.Generic.List[object]]::new()
$trackedChildren=@{}
$runStarted=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8))
$prePath=Join-Path $attemptRoot 'pre_run_process_snapshot.json'
$beforeXsimPath=Join-Path $attemptRoot 'before_xsim_process_snapshot.json'
$postPath=Join-Path $attemptRoot 'post_run_process_snapshot.json'
$statusPath=Join-Path $attemptRoot 'run_status.json'
$processRunsPath=Join-Path $attemptRoot 'process_runs.json'
$consoleStatusPath=Join-Path $attemptRoot 'status.txt'
foreach($p in @($prePath,$beforeXsimPath,$postPath,$statusPath,$processRunsPath,$consoleStatusPath)){if(Test-Path -LiteralPath $p){throw "拒绝覆盖已有 run05 运行结果：$p"}}
$preResources=Get-ResourceSnapshot
$preProcesses=Get-FpgaProcesses
$existingRun05=@($preProcesses | Where-Object {$_.command_line -like '*S2A-T61\run05*'})
$preSnapshot=[ordered]@{task_id='S2A-T61';run_id='run05';attempt='attempt05';captured_at_utc8=$preResources.captured_at_utc8;runner_pid=$PID;resources=$preResources;fpga_processes=$preProcesses;existing_run05_processes=$existingRun05;protected_pids=$plan.protected_existing_process_ids;input_manifest_validation=$initialManifestValidation}
Write-JsonFile $prePath $preSnapshot
$status='RUN_FAILED'
$failure=$null
$lastStage=$null
function Add-TrackedTree([int]$rootPid){
    foreach($p in (Get-ProcessTree $rootPid)){
        $id=[int]$p.ProcessId
        if($id -eq $rootPid){continue}
        if(-not $script:trackedChildren.ContainsKey([string]$id)){
            $handle=$null
            try{$handle=[Diagnostics.Process]::GetProcessById($id)}catch{}
            $script:trackedChildren[[string]$id]=[pscustomobject]@{pid=$id;parent_pid=[int]$p.ParentProcessId;name=$p.Name;executable_path=$p.ExecutablePath;command_line=$p.CommandLine;process_handle=$handle;first_seen_utc8=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss zzz')}
        }
    }
}
function Stop-OwnedTree([int]$rootPid,[string]$reason){
    Add-TrackedTree $rootPid
    $owned=@(Get-ProcessTree $rootPid | Sort-Object ProcessId -Descending)
    foreach($p in $owned){
        try{Stop-Process -Id ([int]$p.ProcessId) -Force -ErrorAction Stop}catch{}
    }
}
function Find-LogFault([string[]]$paths){
    foreach($path in $paths){
        if(-not(Test-Path -LiteralPath $path -PathType Leaf)){continue}
        try{$text=[IO.File]::ReadAllText($path)}catch{continue}
        $match=[regex]::Match($text,'(?im)^\s*(?:ERROR:|FATAL:|Fatal:)|\$fatal|raw INT32|INT8 result|不匹配|无法打开|截断|长度过长')
        if($match.Success){return [pscustomobject]@{path=$path;match=$match.Value}}
    }
    return $null
}
function Assert-NoLogFault([string[]]$paths,[string]$phase,[int]$stageExitCode,[string]$nativeLog){
    if($null -eq $paths -or $paths.Count -ne 3){throw "$phase 必须验证恰好三份阶段日志"}
    if([string]::IsNullOrWhiteSpace($nativeLog)){throw "$phase native log 路径为空"}
    $uniquePaths=@()
    $scannedPaths=@()
    $faults=@()
    $nativeSeen=$false
    $nativeMissing=$false
    foreach($path in $paths){
        if([string]::IsNullOrWhiteSpace($path)){throw "$phase 阶段日志路径为空"}
        if($uniquePaths -contains $path){throw "$phase 阶段日志路径重复：$path"}
        $uniquePaths+=([string]$path)
        $isNative=[string]::Equals([string]$path,$nativeLog,[StringComparison]::OrdinalIgnoreCase)
        if($isNative){$nativeSeen=$true}
        if(-not(Test-Path -LiteralPath $path)){
            if($isNative -and $stageExitCode -ne 0){$nativeMissing=$true;continue}
            throw "$phase 所需日志缺失或不是普通文件：$path"
        }
        $item=Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if($item.PSIsContainer -or (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)){throw "$phase 所需日志不是普通文件：$path"}
        try{$text=[IO.File]::ReadAllText($path,[Text.Encoding]::UTF8)}catch{throw "$phase 所需日志不可读：$path :: $($_.Exception.Message)"}
        $scannedPaths+=([string]$path)
        $match=[regex]::Match($text,'(?im)^\s*(?:ERROR:|FATAL:|Fatal:)|\$fatal|raw INT32|INT8 result|不匹配|无法打开|截断|长度过长')
        if($match.Success){$faults += [pscustomobject]@{path=$path;match=$match.Value}}
    }
    if(-not $nativeSeen){throw "$phase 日志集合不含指定 native log：$nativeLog"}
    if($stageExitCode -eq 0 -and $nativeMissing){throw "$phase 成功进程缺少 native log：$nativeLog"}
    if($stageExitCode -eq 0 -and $faults.Count -gt 0){
        $faultSummary=($faults | ConvertTo-Json -Compress -Depth 4)
        throw "$phase 最终日志复扫发现错误：$faultSummary"
    }
    $scanState=if($stageExitCode -eq 0){'PASS_SCAN'}else{'FAIL_SCAN_NONZERO_EXIT'}
    return [pscustomobject]@{state=$scanState;stage_exit_code=$stageExitCode;native_log=$nativeLog;native_log_missing=$nativeMissing;scanned_paths=@($scannedPaths);faults=@($faults)}
}
function Format-StageFailure([string]$name,[int]$stageExitCode,[object]$finalLogScan,[string]$nativeLog,[string]$stdout,[string]$stderr,[string]$logReadError=''){
    $scanSummary=if($null -ne $finalLogScan){$finalLogScan | ConvertTo-Json -Compress -Depth 6}else{'unavailable'}
    $message="$name 工具进程退出码非 0：$stageExitCode；native_log=$nativeLog；stdout=$stdout；stderr=$stderr；最终日志扫描=$scanSummary"
    if(-not [string]::IsNullOrWhiteSpace($logReadError)){$message+='；最终日志读取错误='+$logReadError}
    return $message
}
function Get-LogStamp([string[]]$paths){
    $items=@()
    foreach($path in $paths){
        if(Test-Path -LiteralPath $path -PathType Leaf){
            try{$i=Get-Item -LiteralPath $path -ErrorAction Stop;$items+=($path+'|'+$i.Length+'|'+$i.LastWriteTimeUtc.Ticks)}catch{}
        }
    }
    return ($items -join ';')
}
function Assert-GlobalPassEvidence([string[]]$paths,[string]$expectedPassLine,[long]$expectedFinishTimeNs){
    if($null -eq $paths -or $paths.Count -ne 3){throw 'XSIM 全局证据必须聚合 native/stdout/stderr 恰好三份日志'}
    if([string]::IsNullOrWhiteSpace($expectedPassLine)){throw 'XSIM 冻结 PASS 行为空'}
    $uniquePaths=[System.Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $passMarkers=[System.Collections.Generic.List[object]]::new()
    $finishMarkers=[System.Collections.Generic.List[object]]::new()
    foreach($path in $paths){
        if([string]::IsNullOrWhiteSpace($path)){throw 'XSIM 全局证据日志路径为空'}
        if(-not $uniquePaths.Add([string]$path)){throw "XSIM 全局证据日志路径重复：$path"}
        if(-not(Test-Path -LiteralPath $path -PathType Leaf)){throw "XSIM 全局证据日志缺失或不是普通文件：$path"}
        $item=Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if(($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0){throw "XSIM 全局证据日志不能是重解析点：$path"}
        try{$lines=[IO.File]::ReadAllLines($path,[Text.Encoding]::UTF8)}catch{throw "XSIM 全局证据日志不可读：$path :: $($_.Exception.Message)"}
        foreach($line in $lines){
            if($line -match '^\s*PASS(?:\s|$)'){$passMarkers.Add([pscustomobject]@{path=$path;line=[string]$line})}
            $finishMatch=[regex]::Match($line,'^\$finish called at time : ([0-9]+) ns$')
            if($finishMatch.Success){
                $finishValue=[long]0
                $parsed=[long]::TryParse($finishMatch.Groups[1].Value,[Globalization.NumberStyles]::None,[Globalization.CultureInfo]::InvariantCulture,[ref]$finishValue)
                if(-not $parsed){throw "XSIM finish 时间无法解析：$($finishMatch.Groups[1].Value)"}
                $finishMarkers.Add([pscustomobject]@{path=$path;time_ns=$finishValue;line=[string]$line})
            }
        }
    }
    if($passMarkers.Count -ne 1){throw "XSIM 三份日志全局 PASS 标记数量不是 1：$($passMarkers.Count)"}
    if(-not [string]::Equals([string]$passMarkers[0].line,$expectedPassLine,[StringComparison]::Ordinal)){throw "XSIM 全局 PASS 行与冻结 run_plan pass_line 不完全一致：$($passMarkers[0].path)"}
    if($finishMarkers.Count -ne 1){throw "XSIM 三份日志全局 finish 标记数量不是 1：$($finishMarkers.Count)"}
    if([long]$finishMarkers[0].time_ns -ne $expectedFinishTimeNs){throw "XSIM finish_time_ns 与冻结值不匹配：actual=$($finishMarkers[0].time_ns) expected=$expectedFinishTimeNs"}
    return [pscustomobject]@{
        state='PASS_GLOBAL_EVIDENCE'
        log_paths=@($paths)
        pass_marker_count=$passMarkers.Count
        pass_marker_path=[string]$passMarkers[0].path
        pass_line=[string]$passMarkers[0].line
        finish_marker_count=$finishMarkers.Count
        finish_marker_path=[string]$finishMarkers[0].path
        finish_time_ns=[long]$finishMarkers[0].time_ns
        expected_finish_time_ns=$expectedFinishTimeNs
    }
}
function New-StageLauncher([string]$launchScript,[string]$executable,[string[]]$arguments){
    if([string]::IsNullOrWhiteSpace($launchScript) -or [string]::IsNullOrWhiteSpace($executable)){throw '命令包装器路径为空'}
    $quote=[string][char]34
    $unsafeChars=[char[]]@(13,10,34,37,38,124,60,62,94,33)
    foreach($value in @($launchScript,$executable)+@($arguments)){
        if($value.IndexOfAny($unsafeChars) -ge 0){throw "命令包装器参数含不安全字符：$value"}
    }
    $quotedArguments=@()
    foreach($argument in $arguments){$quotedArguments+=($quote+[string]$argument+$quote)}
    $crlf=[Environment]::NewLine
    $launchText='@echo off'+$crlf+'call '+$quote+$executable+$quote+' '+($quotedArguments -join ' ')+$crlf+'set "stage_exit=%ERRORLEVEL%"'+$crlf+'exit /b %stage_exit%'+$crlf
    [IO.File]::WriteAllText($launchScript,$launchText,[Text.Encoding]::ASCII)
    return '/d /s /c '+$quote+$launchScript+$quote
}
function Invoke-Stage([string]$name,[string]$executable,[string[]]$arguments,[string]$nativeLog,[bool]$watchSimulation=$false){
    $manifestBefore=Assert-InputManifest $attemptRoot $PSCommandPath
    $stdout=Join-Path $logsRoot ($name+'.stdout.txt')
    $stderr=Join-Path $logsRoot ($name+'.stderr.txt')
    foreach($p in @($stdout,$stderr,$nativeLog)){if(Test-Path -LiteralPath $p){throw "拒绝覆盖已有日志：$p"}}
    $launchScript=Join-Path $tempRoot ($name+'_launcher.cmd')
    if(Test-Path -LiteralPath $launchScript){throw "拒绝覆盖已有命令包装器：$launchScript"}
    $cmdArguments=New-StageLauncher -launchScript $launchScript -executable $executable -arguments $arguments

    $trackedBefore=@($script:trackedChildren.Keys)
    $start=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8))
    $record=[ordered]@{stage=$name;executable=$executable;arguments=@($arguments);command_line=($executable+' '+($arguments -join ' '));host_executable=$commandProcessor;host_arguments=$cmdArguments;launch_script=$launchScript;pid=$null;parent_pid=$PID;started_at_utc8=$start.ToString('yyyy-MM-dd HH:mm:ss zzz');ended_at_utc8=$null;elapsed_seconds=$null;exit_code=$null;stdout=$stdout;stderr=$stderr;native_log=$nativeLog;final_log_scan=$null;stop_reason=$null;child_processes=@();input_manifest_validation=[ordered]@{before_stage=$manifestBefore;after_stage=$null;after_stage_error=$null}}
    $script:processRuns.Add([pscustomobject]$record)
    $current=$script:processRuns[$script:processRuns.Count-1]
    $script:lastStage=$name
    $startInfo=New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName=$commandProcessor
    $startInfo.Arguments=$cmdArguments
    $startInfo.WorkingDirectory=$workRoot
    $startInfo.UseShellExecute=$false
    $startInfo.CreateNoWindow=$true
    $startInfo.RedirectStandardOutput=$true
    $startInfo.RedirectStandardError=$true
    $proc=New-Object System.Diagnostics.Process
    $proc.StartInfo=$startInfo
    $outStream=$null
    $errStream=$null
    $stdoutTask=$null
    $stderrTask=$null
    $lastProgressAt=[DateTimeOffset]::Now
    $logPaths=@($nativeLog,$stdout,$stderr)
    $lastLogStamp=Get-LogStamp $logPaths
    try{
        $outStream=[IO.File]::Open($stdout,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite)
        $errStream=[IO.File]::Open($stderr,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite)
        if(-not $proc.Start()){throw "$name 无法启动：$executable"}
        $current.pid=[int]$proc.Id
        $stdoutTask=$proc.StandardOutput.BaseStream.CopyToAsync($outStream)
        $stderrTask=$proc.StandardError.BaseStream.CopyToAsync($errStream)
        $done=$false
        while(-not $done){
            $mainDone=$proc.WaitForExit(5000)
            Add-TrackedTree $proc.Id
            $resource=Get-ResourceSnapshot
            if($resource.free_physical_mib -lt 2048){
                $current.stop_reason="可用 RAM 低于 2048 MiB：$($resource.free_physical_mib) MiB"
                Stop-OwnedTree $proc.Id $current.stop_reason
                try{[void]$proc.WaitForExit(15000);$proc.Refresh();if($proc.HasExited){$code=$proc.ExitCode;if($null -ne $code){$current.exit_code=[int]$code}}}catch{}
                try{[void]$stdoutTask.GetAwaiter().GetResult()}catch{}
                try{[void]$stderrTask.GetAwaiter().GetResult()}catch{}
                throw $current.stop_reason
            }
            $fault=Find-LogFault $logPaths
            if($null -ne $fault){
                $current.stop_reason="检测到仿真/编译错误：$($fault.path) :: $($fault.match)"
                Stop-OwnedTree $proc.Id $current.stop_reason
                try{[void]$proc.WaitForExit(15000);$proc.Refresh();if($proc.HasExited){$code=$proc.ExitCode;if($null -ne $code){$current.exit_code=[int]$code}}}catch{}
                try{[void]$stdoutTask.GetAwaiter().GetResult()}catch{}
                try{[void]$stderrTask.GetAwaiter().GetResult()}catch{}
                throw $current.stop_reason
            }
            if($watchSimulation){
                $logStamp=Get-LogStamp $logPaths
                if($logStamp -cne $lastLogStamp){$lastLogStamp=$logStamp;$lastProgressAt=[DateTimeOffset]::Now}
                if(([DateTimeOffset]::Now-$lastProgressAt).TotalMinutes -ge 15){
                    $current.stop_reason="仿真日志连续 15 分钟没有变化：$lastLogStamp"
                    Stop-OwnedTree $proc.Id $current.stop_reason
                    try{[void]$proc.WaitForExit(15000);$proc.Refresh();if($proc.HasExited){$code=$proc.ExitCode;if($null -ne $code){$current.exit_code=[int]$code}}}catch{}
                    try{[void]$stdoutTask.GetAwaiter().GetResult()}catch{}
                    try{[void]$stderrTask.GetAwaiter().GetResult()}catch{}
                    throw $current.stop_reason
                }
            }
            if($mainDone){
                [void]$proc.WaitForExit()
                $proc.Refresh()
                if(-not $proc.HasExited){throw "$name WaitForExit 返回后进程仍运行：PID=$($proc.Id)"}
                $nativeExitCode=$proc.ExitCode
                if($null -eq $nativeExitCode){throw "$name PID=$($proc.Id) 已退出但 ExitCode 仍为 null"}
                $current.exit_code=[int]$nativeExitCode
                $activeChildren=@()
                foreach($entry in $script:trackedChildren.Values){
                    $handle=$entry.process_handle
                    if($null -ne $handle){
                        try{$handle.Refresh();if(-not $handle.HasExited){$activeChildren += $entry}}catch{}
                    }
                }
                if($activeChildren.Count -eq 0){
                    [void]$stdoutTask.GetAwaiter().GetResult()
                    [void]$stderrTask.GetAwaiter().GetResult()
                    $outStream.Flush()
                    $errStream.Flush()
                    try{
                        $current.final_log_scan=Assert-NoLogFault $logPaths "$name 排空后的最终阶段日志复扫" ([int]$current.exit_code) $nativeLog
                    }catch{
                        $scanFailure=$_.Exception.Message
                        if($current.exit_code -ne 0){
                            $current.final_log_scan=[ordered]@{state='FAILED';stage_exit_code=[int]$current.exit_code;error=$scanFailure;stdout=$stdout;stderr=$stderr;native_log=$nativeLog}
                            throw (Format-StageFailure -name $name -stageExitCode ([int]$current.exit_code) -finalLogScan $current.final_log_scan -nativeLog $nativeLog -stdout $stdout -stderr $stderr -logReadError $scanFailure)
                        }
                        throw
                    }
                    $done=$true
                }else{Start-Sleep -Seconds 5}
            }
        }
        $proc.Refresh()
        if(-not $proc.HasExited){throw "$name 进程未结束：PID=$($proc.Id)"}
        $nativeExitCode=$proc.ExitCode
        if($null -eq $nativeExitCode){throw "$name PID=$($proc.Id) 已退出但 ExitCode 仍为 null"}
        $current.exit_code=[int]$nativeExitCode
        $end=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8))
        $current.ended_at_utc8=$end.ToString('yyyy-MM-dd HH:mm:ss zzz')
        $current.elapsed_seconds=[Math]::Round(($end-$start).TotalSeconds,3)
        $current.child_processes=@($script:trackedChildren.Values | Where-Object {$trackedBefore -notcontains [string]$_.pid} | ForEach-Object {
            $h=$_.process_handle;$exit=$null;$active=$null
            if($null -ne $h){try{$h.Refresh();$active=(-not $h.HasExited);if($h.HasExited){$childCode=$h.ExitCode;if($null -ne $childCode){$exit=[int]$childCode}}}catch{}}
            [pscustomobject]@{pid=$_.pid;parent_pid=$_.parent_pid;name=$_.name;executable_path=$_.executable_path;command_line=$_.command_line;active=$active;exit_code=$exit;first_seen_utc8=$_.first_seen_utc8}
        })
        if($current.exit_code -ne 0){
            throw (Format-StageFailure -name $name -stageExitCode ([int]$current.exit_code) -finalLogScan $current.final_log_scan -nativeLog $nativeLog -stdout $stdout -stderr $stderr)
        }
        return $current
    }finally{
        if($null -ne $outStream){try{$outStream.Flush();$outStream.Dispose()}catch{}}
        if($null -ne $errStream){try{$errStream.Flush();$errStream.Dispose()}catch{}}
        if($null -ne $proc){try{$proc.Dispose()}catch{}}
        try{$current.input_manifest_validation.after_stage=Assert-InputManifest $attemptRoot $PSCommandPath}catch{$manifestPostError=$_.Exception.Message;$current.input_manifest_validation.after_stage_error=$manifestPostError}
        if($manifestPostError){throw "工具阶段完成后 input_manifest 只读输入复核失败：$manifestPostError"}
    }
}
if($existingRun05.Count -ne 0){$failure='运行前已存在命令行指向 run05 的 FPGA 进程，拒绝重复启动'}
elseif($preResources.free_physical_mib -lt 2048){$failure="运行前 RAM 低于 2048 MiB：$($preResources.free_physical_mib) MiB"}
else{
    try{
        $run05Prj='tb_s2a_conv_layer35_row25_all_channels_vlog.prj'
        $xvlogLog=Join-Path $logsRoot 'xvlog.log'
        $xelabLog=Join-Path $logsRoot 'xelab.log'
        $xsimLog=Join-Path $logsRoot 'xsim.log'
        [void](Invoke-Stage 'xvlog' $toolMap.xvlog @('--incr','--relax','-L','uvm','-prj',$run05Prj,'-log',$xvlogLog) $xvlogLog)
        $snapshot='tb_s2a_conv_layer35_row25_all_channels_behav'
        [void](Invoke-Stage 'xelab' $toolMap.xelab @('--incr','--debug','off','--relax','--mt','2','-L','xil_defaultlib','-L','uvm','-L','unisims_ver','-L','unimacro_ver','-L','secureip','--snapshot',$snapshot,'xil_defaultlib.tb_s2a_conv_layer35_row25_all_channels','xil_defaultlib.glbl','-log',$xelabLog) $xelabLog)
        $beforeXsimResources=Get-ResourceSnapshot
$beforeXsimProcesses=Get-FpgaProcesses
$preById=@{}
foreach($p in $preProcesses){$preById[[string]$p.pid]=$p}
$protectedChecks=@()
$protectedIdentityFailures=@()
foreach($id in @($plan.protected_existing_process_ids)){
    $baseline=$preById[[string]$id]
    $now=@($beforeXsimProcesses | Where-Object {$_.pid -eq [int]$id})
    if($null -ne $baseline){
        if($now.Count -eq 0){$protectedChecks += [pscustomobject]@{pid=[int]$id;state='naturally_absent_before_xsim';identity_match=$null;valid=$true}}
        elseif($now.Count -eq 1){
            $match=($baseline.name -ceq $now[0].name -and $baseline.executable_path -ceq $now[0].executable_path -and $baseline.command_line -ceq $now[0].command_line -and $baseline.parent_pid -eq $now[0].parent_pid)
            $protectedChecks += [pscustomobject]@{pid=[int]$id;state=$(if($match){'same_process_still_present'}else{'pid_identity_changed'});identity_match=$match;valid=$match}
            if(-not $match){$protectedIdentityFailures += [int]$id}
        }else{$protectedChecks += [pscustomobject]@{pid=[int]$id;state='duplicate_pid_records';identity_match=$false;valid=$false};$protectedIdentityFailures += [int]$id}
    }elseif($now.Count -eq 0){$protectedChecks += [pscustomobject]@{pid=[int]$id;state='absent_at_both_snapshots';identity_match=$null;valid=$true}}
    else{$protectedChecks += [pscustomobject]@{pid=[int]$id;state='pid_appeared_after_start';identity_match=$false;valid=$false};$protectedIdentityFailures += [int]$id}
}
$ramOk=($beforeXsimResources.free_physical_mib -ge 2048)
$dSpaceOk=($beforeXsimResources.d_free_bytes -ge 2GB)
$beforeXsimObject=[ordered]@{task_id='S2A-T61';run_id='run05';attempt='attempt05';captured_at_utc8=$beforeXsimResources.captured_at_utc8;resource=$beforeXsimResources;ram_at_least_2_gib=$ramOk;d_free_at_least_2_gib=$dSpaceOk;protected_process_checks=$protectedChecks;protected_identities_valid=($protectedIdentityFailures.Count -eq 0);passed=($ramOk -and $dSpaceOk -and $protectedIdentityFailures.Count -eq 0);fpga_processes=$beforeXsimProcesses}
Write-JsonFile $beforeXsimPath $beforeXsimObject
if(-not $ramOk){throw "xsim 启动前可用 RAM 低于 2048 MiB：$($beforeXsimResources.free_physical_mib) MiB"}
if(-not $dSpaceOk){throw "xsim 启动前 D 盘可用空间低于 2 GiB：$($beforeXsimResources.d_free_bytes) bytes"}
if($protectedIdentityFailures.Count -ne 0){throw "xsim 启动前保护 PID 身份改变：$($protectedIdentityFailures -join ',')"}
$batch=Join-Path $workRoot 'run05_batch.tcl'
        $pathSeparator=[string][char]92
        $batchArgument=$batch.Replace($pathSeparator,'/')
        $xsimLogArgument=$xsimLog.Replace($pathSeparator,'/')
        if($batchArgument.IndexOf($pathSeparator) -ge 0 -or $xsimLogArgument.IndexOf($pathSeparator) -ge 0){throw 'xsim CLI path argument still contains a backslash'}
        if(-not(Test-Path -LiteralPath $batch -PathType Leaf)){throw "xsim Tcl batch file missing: $batch"}
        $xsimArguments=@($snapshot,'-tclbatch',$batchArgument,'-log',$xsimLogArgument)
        [void](Invoke-Stage 'xsim' $toolMap.xsim $xsimArguments $xsimLog $true)
        $runtimeCandidates=@($xsimLog,(Join-Path $logsRoot 'xsim.stdout.txt'),(Join-Path $logsRoot 'xsim.stderr.txt'))
        $expectedPassLine=[string]$plan.pass_definition.pass_line
        $expectedFinishTimeNs=[long]$plan.pass_definition.finish_time_ns
        $runtimeEvidence=Assert-GlobalPassEvidence -paths $runtimeCandidates -expectedPassLine $expectedPassLine -expectedFinishTimeNs $expectedFinishTimeNs
        $runtimeLines=[System.Collections.Generic.List[string]]::new()
        foreach($candidate in $runtimeCandidates){
            $runtimeLines.Add("===== SOURCE LOG $candidate =====")
            foreach($line in [IO.File]::ReadAllLines($candidate,[Text.Encoding]::UTF8)){$runtimeLines.Add([string]$line)}
        }
        $runtimeLog=Join-Path $logsRoot 'runtime_simulate.log'
        [IO.File]::WriteAllLines($runtimeLog,$runtimeLines.ToArray(),$utf8)
        $status='RUN_COMPLETED_PENDING_VERIFICATION'
    }catch{$failure=$_.Exception.Message;$status='RUN_FAILED'}
}
try{$finalManifestValidation=Assert-InputManifest $attemptRoot $PSCommandPath}catch{$finalManifestValidation=[pscustomobject]@{state='FAIL';error=$_.Exception.Message};$failure="整次执行结束后 input_manifest 复核失败：$($_.Exception.Message)";$status='RUN_FAILED'}
$endTime=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8))
foreach($entry in $trackedChildren.Values){
    $h=$entry.process_handle
    if($null -ne $h){try{$h.Refresh()}catch{}}
}
try{
    Write-JsonFile $processRunsPath @($processRuns)
    $postResources=Get-ResourceSnapshot
    $postProcesses=Get-FpgaProcesses
    Write-JsonFile $postPath ([ordered]@{task_id='S2A-T61';run_id='run05';attempt='attempt05';captured_at_utc8=$postResources.captured_at_utc8;resources=$postResources;fpga_processes=$postProcesses;protected_pids=$plan.protected_existing_process_ids})
    $statusObject=[ordered]@{task_id='S2A-T61';run_id='run05';attempt='attempt05';status=$status;failure=$failure;last_stage=$lastStage;started_at_utc8=$runStarted.ToString('yyyy-MM-dd HH:mm:ss zzz');ended_at_utc8=$endTime.ToString('yyyy-MM-dd HH:mm:ss zzz');elapsed_seconds=[Math]::Round(($endTime-$runStarted).TotalSeconds,3);pre_run_snapshot=$prePath;before_xsim_snapshot=$beforeXsimPath;post_run_snapshot=$postPath;process_runs=$processRunsPath;temp_roots=[ordered]@{TEMP=$env:TEMP;TMP=$env:TMP;TMPDIR=$env:TMPDIR};input_manifest_validation=[ordered]@{before_run=$initialManifestValidation;after_run=$finalManifestValidation}}
    Write-JsonFile $statusPath $statusObject
    [IO.File]::WriteAllText($consoleStatusPath,($status+[Environment]::NewLine)+$(if($failure){$failure+[Environment]::NewLine}else{''}),$utf8)
}finally{
    foreach($entry in $trackedChildren.Values){if($null -ne $entry.process_handle){try{$entry.process_handle.Dispose()}catch{}}}
}
if($failure){[Console]::Error.WriteLine("T61_RUN05=$status :: $failure");exit 2}
[Console]::WriteLine("T61_RUN05=$status stages=$($processRuns.Count) elapsed_seconds=$([Math]::Round(($endTime-$runStarted).TotalSeconds,1))")
exit 0
