$ErrorActionPreference='Stop'
$runRoot=(Get-Item -LiteralPath $PSScriptRoot -ErrorAction Stop).FullName
$expectedRoot='D:\FPGA_Competition\report\evidence\S2A-T61\run05\attempt04'
if($runRoot -cne $expectedRoot){throw "run05 runner 目录不符：$runRoot"}
`$attemptRoot=$runRoot
$workRoot=Join-Path $attemptRoot 'work'
$tempRoot=Join-Path $attemptRoot 'temp'
$logsRoot=Join-Path $attemptRoot 'logs'
$planPath=Join-Path $attemptRoot 'run_plan.json'
$required=@($planPath,(Join-Path $runRoot 'prepare_summary.json'),(Join-Path $workRoot 'tb_s2a_conv_layer35_row25_all_channels_vlog.prj'),(Join-Path $workRoot 'run05_batch.tcl'))
foreach($p in $required){if(-not(Test-Path -LiteralPath $p -PathType Leaf)){throw "运行输入缺失：$p"}}
$plan=Get-Content -LiteralPath $planPath -Raw -Encoding UTF8 | ConvertFrom-Json
$toolRoot='D:\Xilinx\2026.1\Vivado\bin\unwrapped\win64.o'
$binRoot='D:\Xilinx\2026.1\Vivado\bin'
$toolMap=[ordered]@{
    xvlog=Join-Path $toolRoot 'xvlog.exe'
    xelab=Join-Path $toolRoot 'xelab.exe'
    xsim=Join-Path $toolRoot 'xsim.exe'
}
foreach($name in @('xvlog','xelab','xsim')){if(-not(Test-Path -LiteralPath $toolMap[$name] -PathType Leaf)){throw "Vivado CLI 工具缺失：$($toolMap[$name])"}}
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
$preSnapshot=[ordered]@{task_id='S2A-T61';run_id='run05';attempt='attempt04';captured_at_utc8=$preResources.captured_at_utc8;runner_pid=$PID;resources=$preResources;fpga_processes=$preProcesses;existing_run05_processes=$existingRun05;protected_pids=$plan.protected_existing_process_ids}
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
function Get-LogStamp([string[]]$paths){
    $items=@()
    foreach($path in $paths){
        if(Test-Path -LiteralPath $path -PathType Leaf){
            try{$i=Get-Item -LiteralPath $path -ErrorAction Stop;$items+=($path+'|'+$i.Length+'|'+$i.LastWriteTimeUtc.Ticks)}catch{}
        }
    }
    return ($items -join ';')
}function Invoke-Stage([string]$name,[string]$executable,[string[]]$arguments,[string]$nativeLog,[bool]$watchSimulation=$false){
    $stdout=Join-Path $logsRoot ($name+'.stdout.txt')
    $stderr=Join-Path $logsRoot ($name+'.stderr.txt')
    foreach($p in @($stdout,$stderr,$nativeLog)){if(Test-Path -LiteralPath $p){throw "拒绝覆盖已有日志：$p"}}
    $trackedBefore=@($script:trackedChildren.Keys)
    $start=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8))
    $record=[ordered]@{stage=$name;executable=$executable;arguments=@($arguments);command_line=($executable+' '+($arguments -join ' '));pid=$null;parent_pid=$PID;started_at_utc8=$start.ToString('yyyy-MM-dd HH:mm:ss zzz');ended_at_utc8=$null;elapsed_seconds=$null;exit_code=$null;stdout=$stdout;stderr=$stderr;native_log=$nativeLog;stop_reason=$null;child_processes=@()}
    $script:processRuns.Add([pscustomobject]$record)
    $current=$script:processRuns[$script:processRuns.Count-1]
    $script:lastStage=$name
    $startInfo=New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName=$executable
    $startInfo.Arguments=($arguments -join ' ')
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
        if($current.exit_code -ne 0){throw "$name 退出码非 0：$($current.exit_code)"}
        return $current
    }finally{
        if($null -ne $outStream){try{$outStream.Flush();$outStream.Dispose()}catch{}}
        if($null -ne $errStream){try{$errStream.Flush();$errStream.Dispose()}catch{}}
        if($null -ne $proc){try{$proc.Dispose()}catch{}}
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
$beforeXsimObject=[ordered]@{task_id='S2A-T61';run_id='run05';attempt='attempt04';captured_at_utc8=$beforeXsimResources.captured_at_utc8;resource=$beforeXsimResources;ram_at_least_2_gib=$ramOk;d_free_at_least_2_gib=$dSpaceOk;protected_process_checks=$protectedChecks;protected_identities_valid=($protectedIdentityFailures.Count -eq 0);passed=($ramOk -and $dSpaceOk -and $protectedIdentityFailures.Count -eq 0);fpga_processes=$beforeXsimProcesses}
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
        $selected=$null
        foreach($candidate in $runtimeCandidates){
            if(-not(Test-Path -LiteralPath $candidate -PathType Leaf)){continue}
            $text=[IO.File]::ReadAllText($candidate)
            $passCount=[regex]::Matches($text,'(?m)^PASS T61 outputs=6656 raw=6656[^\r\n]*').Count
            $finishCount=[regex]::Matches($text,'(?m)^\$finish called at time : [0-9]+ ns').Count
            if($passCount -eq 1 -and $finishCount -eq 1){$selected=$candidate;break}
        }
        if($null -eq $selected){throw 'XSIM 没有单一 PASS/$finish 证据日志'}
        $runtimeLog=Join-Path $logsRoot 'runtime_simulate.log'
        [IO.File]::WriteAllText($runtimeLog,[IO.File]::ReadAllText($selected),$utf8)
        $status='RUN_COMPLETED_PENDING_VERIFICATION'
    }catch{$failure=$_.Exception.Message;$status='RUN_FAILED'}
}
$endTime=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8))
foreach($entry in $trackedChildren.Values){
    $h=$entry.process_handle
    if($null -ne $h){try{$h.Refresh()}catch{}}
}
try{
    Write-JsonFile $processRunsPath @($processRuns)
    $postResources=Get-ResourceSnapshot
    $postProcesses=Get-FpgaProcesses
    Write-JsonFile $postPath ([ordered]@{task_id='S2A-T61';run_id='run05';attempt='attempt04';captured_at_utc8=$postResources.captured_at_utc8;resources=$postResources;fpga_processes=$postProcesses;protected_pids=$plan.protected_existing_process_ids})
    $statusObject=[ordered]@{task_id='S2A-T61';run_id='run05';attempt='attempt04';status=$status;failure=$failure;last_stage=$lastStage;started_at_utc8=$runStarted.ToString('yyyy-MM-dd HH:mm:ss zzz');ended_at_utc8=$endTime.ToString('yyyy-MM-dd HH:mm:ss zzz');elapsed_seconds=[Math]::Round(($endTime-$runStarted).TotalSeconds,3);pre_run_snapshot=$prePath;before_xsim_snapshot=$beforeXsimPath;post_run_snapshot=$postPath;process_runs=$processRunsPath;temp_roots=[ordered]@{TEMP=$env:TEMP;TMP=$env:TMP;TMPDIR=$env:TMPDIR}}
    Write-JsonFile $statusPath $statusObject
    [IO.File]::WriteAllText($consoleStatusPath,($status+[Environment]::NewLine)+$(if($failure){$failure+[Environment]::NewLine}else{''}),$utf8)
}finally{
    foreach($entry in $trackedChildren.Values){if($null -ne $entry.process_handle){try{$entry.process_handle.Dispose()}catch{}}}
}
if($failure){[Console]::Error.WriteLine("T61_RUN05=$status :: $failure");exit 2}
[Console]::WriteLine("T61_RUN05=$status stages=$($processRuns.Count) elapsed_seconds=$([Math]::Round(($endTime-$runStarted).TotalSeconds,1))")
exit 0