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