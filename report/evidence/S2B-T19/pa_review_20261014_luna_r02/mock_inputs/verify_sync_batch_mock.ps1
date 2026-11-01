$ErrorActionPreference = 'Stop'
$repo = (Get-Location).Path
$run = Join-Path $repo 'tmp/2B/S2B-T19/pa_review_20261014_luna_r02/sync_batch_mock'
$null = New-Item -ItemType Directory -Path $run -Force
$python = 'C:\Users\22061\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$childScript = Join-Path $run 'sync_child.py'
$entry = Join-Path $run 'entry_stub.py'
$mockBatch = Join-Path $run 'mock_vitis.bat'
$resultPath = Join-Path $run 'result.json'
[IO.File]::WriteAllText($childScript,"import sys,time`ntime.sleep(3)`nsys.exit(23)`n",[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($entry,"pass`n",[Text.UTF8Encoding]::new($false))
$batchText = "@echo off`r`n`"$python`" -X utf8 -B `"$childScript`" %*`r`ngoto :EOF`r`n"
[IO.File]::WriteAllText($mockBatch,$batchText,[Text.Encoding]::ASCII)
$argument = '/d /s /c ""' + $mockBatch + '" -s ' + $entry + '"'
$launcher = Start-Process -FilePath $env:ComSpec -ArgumentList $argument -WindowStyle Hidden -PassThru
$deadline = (Get-Date).AddSeconds(5)
$child = $null
do {
    $rows = @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$($launcher.Id)")
    $child = @($rows | Where-Object { $_.CommandLine -like "*$childScript*" }) | Select-Object -First 1
    if ($null -ne $child) { break }
    Start-Sleep -Milliseconds 50
    $launcher.Refresh()
} while (-not $launcher.HasExited -and (Get-Date) -lt $deadline)
$launcherAliveWhileChildObserved = -not $launcher.HasExited
$childAliveWhileObserved = $false
if ($null -ne $child) {
    $current = Get-CimInstance Win32_Process -Filter "ProcessId=$($child.ProcessId)"
    $childAliveWhileObserved = $null -ne $current
}
$launcher.WaitForExit()
$result = [pscustomobject]@{
    command=@($env:ComSpec,$argument)
    official_vitis_bat_sha256=(Get-FileHash -LiteralPath 'D:/Xilinx/2026.1/Vitis/bin/vitis.bat' -Algorithm SHA256).Hash.ToLowerInvariant()
    official_source_line=433
    official_source_text='python.exe %args_for_source%'
    mock_child_seen=($null -ne $child)
    mock_child_live_when_seen=$childAliveWhileObserved
    launcher_live_while_child_observed=$launcherAliveWhileChildObserved
    launcher_exit_code=$launcher.ExitCode
    expected_exit_code=23
}
$result | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $resultPath -Encoding UTF8
$result | ConvertTo-Json -Depth 4
if (-not $result.mock_child_seen -or -not $result.mock_child_live_when_seen -or -not $result.launcher_live_while_child_observed -or $result.launcher_exit_code -ne 23) { exit 1 }
exit 0
