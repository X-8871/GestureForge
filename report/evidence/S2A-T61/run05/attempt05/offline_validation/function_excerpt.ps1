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