$ErrorActionPreference='Stop'
$records=@()
foreach($code in @(0,7)){
    $startInfo=New-Object System.Diagnostics.ProcessStartInfo
    $startInfo.FileName=$env:ComSpec
    $startInfo.Arguments=if($code -eq 0){'/d /c echo PROBE_OUTPUT'}else{'/d /c exit 7'}
    $startInfo.UseShellExecute=$false
    $startInfo.RedirectStandardOutput=$true
    $startInfo.RedirectStandardError=$true
    $proc=[System.Diagnostics.Process]::Start($startInfo)
    $pidValue=[int]$proc.Id
    $stdoutPath=Join-Path $PSScriptRoot "exit_code_probe_$code.stdout.txt"
    $stderrPath=Join-Path $PSScriptRoot "exit_code_probe_$code.stderr.txt"
    $stdoutStream=[IO.File]::Open($stdoutPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite)
    $stderrStream=[IO.File]::Open($stderrPath,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::ReadWrite)
    try{
        $stdoutTask=$proc.StandardOutput.BaseStream.CopyToAsync($stdoutStream)
        $stderrTask=$proc.StandardError.BaseStream.CopyToAsync($stderrStream)
        $waitResult=$proc.WaitForExit(10000)
        if(-not $waitResult){throw "Process.Start probe timeout pid=$pidValue expected=$code"}
        $proc.WaitForExit()
        $proc.Refresh()
        $hasExited=[bool]$proc.HasExited
        if(-not $hasExited){throw "Process.Start probe HasExited=false pid=$pidValue"}
        $exit=[int]$proc.ExitCode
        $stdoutTask.GetAwaiter().GetResult()
        $stderrTask.GetAwaiter().GetResult()
        $stdoutStream.Flush()
        $stderrStream.Flush()
    }finally{
        $stdoutStream.Dispose()
        $stderrStream.Dispose()
    }
    $stdout=[IO.File]::ReadAllText($stdoutPath).Trim()
    $stderr=[IO.File]::ReadAllText($stderrPath).Trim()
    $records += [pscustomobject]@{pid=$pidValue;wait_returned=$waitResult;has_exited=$hasExited;expected_exit_code=$code;captured_exit_code=$exit;stdout=$stdout;stderr=$stderr;stdout_file=$stdoutPath;stderr_file=$stderrPath}
    $proc.Dispose()
}
if($records.Count -ne 2 -or $records[0].captured_exit_code -ne 0 -or $records[1].captured_exit_code -ne 7 -or $records[0].stdout -cne 'PROBE_OUTPUT'){throw 'Process.Start exit code or redirected-output probe mismatch'}
$out=[ordered]@{test='System.Diagnostics.Process.Start with live stdout/stderr file streaming, WaitForExit, Refresh, HasExited and ExitCode';powershell_version=$PSVersionTable.PSVersion.ToString();passed=$true;results=$records;tested_at_utc8=[DateTimeOffset]::Now.ToOffset([TimeSpan]::FromHours(8)).ToString('yyyy-MM-dd HH:mm:ss zzz')}
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'exit_code_probe.json'),($out | ConvertTo-Json -Depth 10),[Text.UTF8Encoding]::new($false))
Write-Output "EXIT_CODE_PROBE=PASS pids=$($records[0].pid),$($records[1].pid) exit_codes=0,7 live_file_streaming=true"