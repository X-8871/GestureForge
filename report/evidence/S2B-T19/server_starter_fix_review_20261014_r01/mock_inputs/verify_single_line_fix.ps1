$ErrorActionPreference = 'Stop'
$repo = (Get-Location).Path
$oldPath = Join-Path $repo 'report/evidence/S2B-T19/pa_review_20261014_luna_r03/source_snapshot/start_owned_server.ps1'
$newPath = Join-Path $repo 'tmp/2B/S2B-T19/board_run_20261014_r02/start_owned_server.ps1'
$oldHash = (Get-FileHash -LiteralPath $oldPath -Algorithm SHA256).Hash.ToLowerInvariant()
$newHash = (Get-FileHash -LiteralPath $newPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($oldHash -cne '4113e6eafa69de6a8c2049bdfdf653431b6c105730477ffc2de1bf6995c8ec79') { throw 'previous starter source hash drift' }
if ($newHash -cne '0bdf8eb0de5c9e57d22df271585c8446d02e081d93e3728074fe0afc0e76ef2d') { throw 'candidate starter source hash drift' }
$oldLines = [IO.File]::ReadAllLines($oldPath, [Text.Encoding]::UTF8)
$newLines = [IO.File]::ReadAllLines($newPath, [Text.Encoding]::UTF8)
if ($oldLines.Length -ne $newLines.Length) { throw 'line count changed' }
$changed = @()
for ($index = 0; $index -lt $oldLines.Length; $index++) {
    if ($oldLines[$index] -cne $newLines[$index]) { $changed += $index }
}
if ($changed.Count -ne 1 -or $changed[0] -ne 31) { throw "expected one change at line 32; observed $($changed -join ',')" }
$expectedOld = '$taskExpectedCommandLines = @($taskExecutable.FullName + '' -s tcp::3121'', ''"'' + $taskExecutable.FullName + ''" -s tcp::3121'')'
$expectedNew = '$taskExpectedCommandLines = @(($taskExecutable.FullName + '' -s tcp::3121''), (''"'' + $taskExecutable.FullName + ''" -s tcp::3121''))'
if ($oldLines[31] -cne $expectedOld -or $newLines[31] -cne $expectedNew) { throw 'changed line is not the exact command-line array grouping fix' }
$exe = 'D:\Xilinx\2026.1\Vitis\bin\unwrapped\win64.o\hw_server.exe'
$expected = @(($exe + ' -s tcp::3121'), ('"' + $exe + '" -s tcp::3121'))
$unquoted = $exe + ' -s tcp::3121'
$quoted = '"' + $exe + '" -s tcp::3121'
if ($expected.Count -ne 2 -or $expected[0] -cne $unquoted -or $expected[1] -cne $quoted) { throw 'fixed expression does not produce the two exact legal forms' }
$text = [IO.File]::ReadAllText($newPath, [Text.Encoding]::UTF8)
$guards = [ordered]@{
    hidden_start = $text.Contains('-WindowStyle Hidden')
    exact_start_arguments = $text.Contains("-ArgumentList @('-s','tcp::3121')")
    no_existing_service_or_listener = $text.Contains('$taskServers.Count -ne 0 -or $taskListeners.Count -ne 0')
    listener_owned_by_child = $text.Contains('$_.OwningProcess -ne $taskChild.Id')
    parent_pid_checked = $text.Contains('$taskCurrent.ParentProcessId -ne $PID')
    executable_path_checked = $text.Contains('$taskCurrent.ExecutablePath -cne $taskExecutable.FullName')
    command_line_checked = $text.Contains('$taskCurrent.CommandLine -cnotin $taskExpectedCommandLines')
    executable_hash_checked = $text.Contains("e1c90dae3564a7d63b48796a8ed9373a4a00e5e70f2312651cff77c48a6399f3")
    identity_receipt_binds_checked_command = $text.Contains('CommandLine=$taskCurrent.CommandLine')
    identity_receipt_binds_checked_hash = $text.Contains('native_sha256=$taskSha')
}
if (@($guards.Values | Where-Object { -not $_ }).Count -ne 0) { throw "an existing starter safety guard is missing: $($guards | ConvertTo-Json -Compress)" }
$tokens = $null
$parseErrors = $null
[System.Management.Automation.Language.Parser]::ParseFile($newPath, [ref]$tokens, [ref]$parseErrors) | Out-Null
if (@($parseErrors).Count -ne 0) { throw ($parseErrors | ForEach-Object Message | Out-String) }
[ordered]@{
    result = 'PASS_SINGLE_LINE_S1_FIX'
    previous_sha256 = $oldHash
    candidate_sha256 = $newHash
    changed_line = 32
    old_line = $oldLines[31]
    new_line = $newLines[31]
    changed_line_count = $changed.Count
    expected_forms_count = $expected.Count
    unquoted_expected = $expected -ccontains $unquoted
    quoted_expected = $expected -ccontains $quoted
    parser_errors = @($parseErrors).Count
    safety_guards = $guards
} | ConvertTo-Json -Depth 6
