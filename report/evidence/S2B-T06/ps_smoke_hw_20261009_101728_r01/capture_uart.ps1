[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Port,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$RawPath,

    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$StopFlagPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

# 按真实目录项逐分量核对大小写，不展开通配符，不修正输入路径。
function Get-NewLiteralFileTarget {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)

    if ($LiteralPath -cnotmatch '\A[A-Z]:\\[^\\]') {
        throw '目标必须是盘符大写、反斜杠分隔的完整 Windows 绝对文件路径。'
    }
    $parts = @($LiteralPath.Substring(3).Split([char]'\'))
    foreach ($part in $parts) {
        if ([string]::IsNullOrEmpty($part) -or $part -eq '.' -or $part -eq '..' -or
            $part -match '[<>:"/\\|?*\[\]\x00-\x1f]' -or $part -match '[. ]\z' -or
            $part -match '\A(?:CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|\z)') {
            throw "路径分量无效或存在隐式解释：$part"
        }
    }

    $current = $LiteralPath.Substring(0, 3)
    if (-not [System.IO.Directory]::Exists($current)) {
        throw "目标盘符目录不存在：$current"
    }
    for ($index = 0; $index -lt ($parts.Length - 1); $index++) {
        $expected = $parts[$index]
        $parentEntries = @([System.IO.Directory]::EnumerateFileSystemEntries($current) | Where-Object {
            [string]::Equals([System.IO.Path]::GetFileName($_), $expected, [System.StringComparison]::OrdinalIgnoreCase)
        })
        if ($parentEntries.Count -ne 1) {
            throw "父目录不存在或名称有冲突：$current\$expected"
        }
        if (-not [string]::Equals([System.IO.Path]::GetFileName($parentEntries[0]), $expected, [System.StringComparison]::Ordinal)) {
            throw "父目录字符不一致，输入为 $expected，实际为 $([System.IO.Path]::GetFileName($parentEntries[0]))"
        }
        $attributes = [System.IO.File]::GetAttributes($parentEntries[0])
        if (($attributes -band [System.IO.FileAttributes]::Directory) -eq 0 -or
            ($attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            throw "父路径必须是真实目录，不能是文件或重解析点：$($parentEntries[0])"
        }
        $current = $parentEntries[0]
    }

    $leaf = $parts[$parts.Length - 1]
    $existing = @([System.IO.Directory]::EnumerateFileSystemEntries($current) | Where-Object {
        [string]::Equals([System.IO.Path]::GetFileName($_), $leaf, [System.StringComparison]::OrdinalIgnoreCase)
    })
    if ($existing.Count -ne 0) {
        throw "目标已存在或存在大小写冲突，拒绝覆盖：$LiteralPath"
    }
    $fullPath = [System.IO.Path]::Combine($current, $leaf)
    if (-not [string]::Equals($fullPath, $LiteralPath, [System.StringComparison]::Ordinal)) {
        throw '核验后的完整路径与输入字符不一致。'
    }
    return [pscustomobject]@{ FullPath = $fullPath; ParentDirectory = $current; Name = $leaf }
}

# 只读取操作员随后创建的精确停止文件；本脚本不创建、改写或删除它。
function Test-ExactStopFlag {
    param([Parameter(Mandatory = $true)]$Target)

    $entries = @([System.IO.Directory]::EnumerateFileSystemEntries($Target.ParentDirectory) | Where-Object {
        [string]::Equals([System.IO.Path]::GetFileName($_), $Target.Name, [System.StringComparison]::OrdinalIgnoreCase)
    })
    if ($entries.Count -eq 0) { return $false }
    if ($entries.Count -ne 1 -or
        -not [string]::Equals($entries[0], $Target.FullPath, [System.StringComparison]::Ordinal)) {
        throw '停止文件名称有字符差异或大小写冲突。'
    }
    $attributes = [System.IO.File]::GetAttributes($entries[0])
    if (($attributes -band [System.IO.FileAttributes]::Directory) -ne 0 -or
        ($attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw '停止标记必须是精确路径上的普通文件。'
    }
    return $true
}

$serial = $null
$raw = $null
$captureClock = $null
$rawTarget = $null
$stopTarget = $null
$opened = $false
$rawCreated = $false
$limitReached = $false
$stopSeen = $false
$capturedBytes = [long]0
$reason = 'not_started'
$exitCode = 1
$failureMessage = $null
$closeErrors = [System.Collections.Generic.List[string]]::new()

try {
    if (-not [System.Text.RegularExpressions.Regex]::IsMatch($Port, '\ACOM[1-9][0-9]*\z')) {
        throw '串口参数必须精确填写实际 COM 端口，例如 COM3；不能为空或使用占位值。'
    }
    $rawTarget = Get-NewLiteralFileTarget -LiteralPath $RawPath
    if ($PSBoundParameters.ContainsKey('StopFlagPath')) {
        $stopTarget = Get-NewLiteralFileTarget -LiteralPath $StopFlagPath
        if (-not [string]::Equals($stopTarget.Name, 'stop_capture.flag', [System.StringComparison]::Ordinal) -or
            -not [string]::Equals($stopTarget.ParentDirectory, $rawTarget.ParentDirectory, [System.StringComparison]::Ordinal) -or
            [string]::Equals($stopTarget.FullPath, $rawTarget.FullPath, [System.StringComparison]::Ordinal)) {
            throw '停止标记必须是与原始文件同一人工 Run 目录下的全新 stop_capture.flag。'
        }
    }

    # 串口参数及原始字节写入方式忠实使用固定操作包的步骤2。
    $serial = [System.IO.Ports.SerialPort]::new($Port, 115200, [System.IO.Ports.Parity]::None, 8, [System.IO.Ports.StopBits]::One)
    $serial.Handshake = [System.IO.Ports.Handshake]::None
    $serial.DtrEnable = $false
    $serial.RtsEnable = $false
    $serial.ReadTimeout = 200
    $bytes = [byte[]]::new(4096)
    $raw = [System.IO.File]::Open($rawTarget.FullPath, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::Read)
    $rawCreated = $true
    $captureClock = [System.Diagnostics.Stopwatch]::StartNew()
    $serial.Open()
    $opened = $true
    $reason = 'interrupted'
    $exitCode = 130
    [Console]::WriteLine('CAPTURE_OPEN ' + (ConvertTo-Json -Compress -InputObject ([ordered]@{
        time = [DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(8)).ToString('o')
        port = $Port
        raw_path = $rawTarget.FullPath
        stop_flag_path = $StopFlagPath
        baud = 115200
        format = '8N1'
        flow_control = 'None'
        dtr = $false
        rts = $false
        read_timeout_ms = 200
        limit_seconds = 600
    })))

    while ($captureClock.Elapsed.TotalSeconds -lt 600) {
        if ($null -ne $stopTarget -and (Test-ExactStopFlag -Target $stopTarget)) {
            $stopSeen = $true
            $reason = 'stop_flag'
            $exitCode = 0
            break
        }
        try { $count = $serial.Read($bytes, 0, $bytes.Length) }
        catch [System.TimeoutException] { continue }
        $raw.Write($bytes, 0, $count)
        $raw.Flush()
        $capturedBytes += $count
        # ASCII 仅供屏幕观察；原始文件只写入串口返回的字节。
        [Console]::Write([System.Text.Encoding]::ASCII.GetString($bytes, 0, $count))
    }
    if (-not $stopSeen) {
        $limitReached = $true
        $reason = 'limit_600s'
        $exitCode = 2
    }
}
catch {
    $failureMessage = $_.Exception.Message
    $reason = 'error'
    $exitCode = 1
    [Console]::Error.WriteLine('CAPTURE_ERROR ' + (ConvertTo-Json -Compress -InputObject ([ordered]@{
        time = [DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(8)).ToString('o')
        message = $failureMessage
    })))
}
finally {
    # 打开失败也保留已创建的原始文件；各对象清理失败不能跳过其他清理。
    if ($null -ne $serial) {
        try { $serial.Close() }
        catch { $closeErrors.Add("串口关闭失败：$($_.Exception.Message)") }
        finally {
            try { $serial.Dispose() }
            catch { $closeErrors.Add("串口释放失败：$($_.Exception.Message)") }
        }
    }
    if ($null -ne $raw) {
        try { $raw.Flush() }
        catch { $closeErrors.Add("原始文件刷新失败：$($_.Exception.Message)") }
        finally {
            try { $raw.Dispose() }
            catch { $closeErrors.Add("原始文件释放失败：$($_.Exception.Message)") }
        }
    }
    $elapsedSeconds = 0.0
    if ($null -ne $captureClock) {
        $captureClock.Stop()
        $elapsedSeconds = $captureClock.Elapsed.TotalSeconds
    }
    if ($closeErrors.Count -gt 0) { $exitCode = 1 }
    # 完成状态写入 UTF-8 控制台文本，不向原始串口文件加入任何标记。
    [Console]::WriteLine()
    [Console]::WriteLine('CAPTURE_CLOSED ' + (ConvertTo-Json -Compress -InputObject ([ordered]@{
        time = [DateTimeOffset]::UtcNow.ToOffset([TimeSpan]::FromHours(8)).ToString('o')
        port = $Port
        raw_path = $RawPath
        opened = $opened
        raw_created = $rawCreated
        captured_bytes = $capturedBytes
        reason = $reason
        limit_600s_reached = $limitReached
        stop_flag_seen = $stopSeen
        elapsed_seconds = $elapsedSeconds
        failure_message = $failureMessage
        cleanup_errors = $closeErrors.ToArray()
        exit_code = $exitCode
    })))
}

exit $exitCode
