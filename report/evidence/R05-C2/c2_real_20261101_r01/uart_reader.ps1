$ErrorActionPreference = 'Stop'
$run = 'D:\codex-worktrees\w6\report\evidence\R05-C2\c2_real_20261101_r01'
$raw = Join-Path $run 'uart.bin'
$ready = Join-Path $run 'uart_ready.txt'
if ((Test-Path -LiteralPath $raw) -or (Test-Path -LiteralPath $ready)) { throw 'UART outputs already exist' }
$port = New-Object System.IO.Ports.SerialPort 'COM4',115200,'None',8,'One'
$port.ReadTimeout = 200
$stream = $null
$text = ''
$bytes = 0
$saw = $false
$errorText = $null
$timer = [Diagnostics.Stopwatch]::StartNew()
try {
    # 先打开串口再启动应用；保存原始字节，不以主机时间替代板上GT。
    $port.Open()
    $port.DiscardInBuffer()
    $stream = [IO.File]::Open($raw,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)
    [IO.File]::WriteAllText($ready,'COM4 115200 8N1 opened',[Text.Encoding]::UTF8)
    [byte[]]$buffer = New-Object byte[] 4096
    while ($timer.Elapsed.TotalSeconds -lt 160) {
        try {
            $n = $port.Read($buffer,0,$buffer.Length)
            if ($n -gt 0) {
                $stream.Write($buffer,0,$n)
                $stream.Flush()
                $bytes += $n
                $text += [Text.Encoding]::ASCII.GetString($buffer,0,$n)
                if ($text -match 'CHAINB RESULT=\{[^\r\n]+\}\r?\n') { $saw = $true; break }
            }
        } catch {
            if (($_.Exception -is [TimeoutException]) -or ($_.Exception.InnerException -is [TimeoutException])) { continue }
            throw
        }
    }
} catch {
    $errorText = $_.Exception.ToString()
} finally {
    if ($stream) { $stream.Dispose() }
    if ($port.IsOpen) { $port.Close() }
    $port.Dispose()
    $summary = @{ bytes=$bytes; saw_final_result=$saw; elapsed_seconds=$timer.Elapsed.TotalSeconds; error=$errorText; closed=$true }
    [IO.File]::WriteAllText((Join-Path $run 'uart_capture.json'),($summary | ConvertTo-Json -Compress),[Text.Encoding]::UTF8)
}
if ($errorText -or (-not $saw)) { exit 2 }
exit 0
