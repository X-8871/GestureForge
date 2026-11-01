$script:T65XilinxProcessNamePattern = '^(?i:vivado|vivado_lab|xsim|xsimk|xvlog|xelab|xvhdl|xsc|hw_server|cs_server|xicom|xsct|bootgen|wdbserver)\.exe$'
$script:T65ExpectedProtectedPids = @(8712, 13156, 22488)

function Get-T65XilinxProcessSnapshot {
    [CmdletBinding()]
    param()

    try {
        $processes = @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop)
    }
    catch {
        throw "T65_PROCESS_SNAPSHOT_UNAVAILABLE: 无法读取 Win32_Process：$($_.Exception.Message)"
    }

    $snapshot = @()
    foreach ($process in $processes) {
        $name = [string]$process.Name
        $path = [string]$process.ExecutablePath
        $commandLine = [string]$process.CommandLine
        $isKnownTool = $name -match $script:T65XilinxProcessNamePattern
        $hasXilinxPath = $path -match '(?i)[\\/]Xilinx[\\/]'
        if (-not ($isKnownTool -or $hasXilinxPath)) {
            continue
        }

        if ([string]::IsNullOrWhiteSpace($name) -or
            $process.ProcessId -le 0 -or
            $process.ParentProcessId -le 0 -or
            [string]::IsNullOrWhiteSpace($path) -or
            [string]::IsNullOrWhiteSpace($commandLine) -or
            $null -eq $process.CreationDate -or
            $process.CreationDate -isnot [datetime]) {
            throw "T65_PROCESS_IDENTITY_INCOMPLETE: Xilinx 进程缺少 PID、父 PID、路径、命令行或创建时间。"
        }

        $snapshot += [pscustomobject]@{
            pid = [int]$process.ProcessId
            parent_pid = [int]$process.ParentProcessId
            name = $name
            executable_path = $path
            command_line = $commandLine
            creation_date_utc = $process.CreationDate.ToUniversalTime().ToString(
                'yyyy-MM-ddTHH:mm:ss.fffffffZ',
                [Globalization.CultureInfo]::InvariantCulture
            )
        }
    }
    return @($snapshot | Sort-Object -Property pid)
}

function Read-T65XilinxProcessAllowlist {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ExpectedSha256
    )

    $item = Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($item.PSIsContainer -or $item.FullName -cne $Path) {
        throw "T65_PROCESS_ALLOWLIST_PATH_INVALID: allowlist 不是精确路径上的普通文件：$Path"
    }
    $actualSha256 = (Get-FileHash -LiteralPath $Path -Algorithm SHA256 -ErrorAction Stop).Hash.ToLowerInvariant()
    if ($actualSha256 -cne $ExpectedSha256.ToLowerInvariant()) {
        throw "T65_PROCESS_ALLOWLIST_SHA_MISMATCH: 进程身份 allowlist 摘要不匹配。"
    }

    try {
        $allowlist = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        throw "T65_PROCESS_ALLOWLIST_INVALID: 无法解析 allowlist：$($_.Exception.Message)"
    }
    if ($allowlist.schema_version -cne 'gestureforge_s2a_t65_process_allowlist_v1' -or
        $allowlist.task_id -cne 'S2A-T65' -or
        $allowlist.status -cne 'FROZEN_READ_ONLY_IDENTITIES' -or
        [string]$allowlist.source_snapshot_sha256 -cne '4e797ee7d12bf2e03c989aef2a3ce16ac610e4132fc58ae09e25799a7c2cb7b1') {
        throw 'T65_PROCESS_ALLOWLIST_SCHEMA_INVALID: schema、任务标识、状态或来源快照摘要不匹配。'
    }

    $identities = @($allowlist.identities)
    if ($identities.Count -ne 3) {
        throw "T65_PROCESS_ALLOWLIST_COUNT_INVALID: 允许身份数必须为 3，实际为 $($identities.Count)。"
    }
    $actualPids = @($identities | ForEach-Object { [int]$_.pid } | Sort-Object -Unique)
    if (($actualPids -join ',') -cne '8712,13156,22488') {
        throw 'T65_PROCESS_ALLOWLIST_PID_INVALID: 允许 PID 必须精确为 8712、13156、22488。'
    }
    foreach ($identity in $identities) {
        if ($identity.creation_date_utc -is [datetime]) {
            $identity.creation_date_utc = $identity.creation_date_utc.ToUniversalTime().ToString(
                'yyyy-MM-ddTHH:mm:ss.fffffffZ',
                [Globalization.CultureInfo]::InvariantCulture
            )
        }
        foreach ($field in @('pid', 'parent_pid', 'name', 'executable_path', 'command_line', 'creation_date_utc')) {
            if ($null -eq $identity.$field -or [string]::IsNullOrWhiteSpace([string]$identity.$field)) {
                throw "T65_PROCESS_ALLOWLIST_IDENTITY_INCOMPLETE: 缺少身份字段 $field。"
            }
        }
        if ([string]$identity.creation_date_utc -notmatch '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{7}Z$') {
            throw "T65_PROCESS_ALLOWLIST_CREATION_DATE_INVALID: PID $($identity.pid) 创建时间格式无效。"
        }
    }
    return $allowlist
}

function Assert-T65XilinxProcessIdentities {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$ActualProcesses,
        [Parameter(Mandatory = $true)][object[]]$AllowedIdentities,
        [Parameter(Mandatory = $true)][string]$Phase
    )

    $allowedByPid = @{}
    foreach ($allowed in $AllowedIdentities) {
        $pidValue = [int]$allowed.pid
        if ($pidValue -le 0 -or $allowedByPid.ContainsKey([string]$pidValue)) {
            throw "T65_PROCESS_ALLOWLIST_DUPLICATE_PID: allowlist 的 PID 无效或重复：$pidValue"
        }
        $allowedByPid[[string]$pidValue] = $allowed
    }

    $seenPids = @{}
    foreach ($actual in $ActualProcesses) {
        foreach ($field in @('pid', 'parent_pid', 'name', 'executable_path', 'command_line', 'creation_date_utc')) {
            if ($null -eq $actual.$field -or [string]::IsNullOrWhiteSpace([string]$actual.$field)) {
                throw "T65_PROCESS_IDENTITY_INCOMPLETE: $Phase 快照缺少身份字段 $field。"
            }
        }
        $pidValue = [int]$actual.pid
        $pidKey = [string]$pidValue
        if ($pidValue -le 0 -or $seenPids.ContainsKey($pidKey)) {
            throw "T65_PROCESS_DUPLICATE_PID: $Phase 快照中的 PID 无效或重复：$pidKey"
        }
        $seenPids[$pidKey] = $true
        if (-not $allowedByPid.ContainsKey($pidKey)) {
            throw "T65_ACTIVE_XILINX_PROCESS: $Phase 出现未授权 Xilinx 进程 PID=$pidKey name=$($actual.name)。"
        }

        $allowed = $allowedByPid[$pidKey]
        $matches = ([int]$actual.parent_pid -eq [int]$allowed.parent_pid) -and
            ([string]$actual.name).Equals([string]$allowed.name, [StringComparison]::OrdinalIgnoreCase) -and
            ([string]$actual.executable_path).Equals([string]$allowed.executable_path, [StringComparison]::OrdinalIgnoreCase) -and
            ([string]$actual.command_line).Equals([string]$allowed.command_line, [StringComparison]::Ordinal) -and
            ([string]$actual.creation_date_utc).Equals([string]$allowed.creation_date_utc, [StringComparison]::Ordinal)
        if (-not $matches) {
            throw "T65_PROCESS_IDENTITY_MISMATCH: $Phase 的 PID=$pidKey 身份与冻结创建时间 allowlist 不完全一致。"
        }
    }
    return [pscustomobject]@{
        phase = $Phase
        observed_xilinx_processes = $ActualProcesses.Count
        only_frozen_identities = $true
    }
}

function Assert-T65AllowedXilinxProcessSnapshot {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)][object[]]$AllowedIdentities,
        [Parameter(Mandatory = $true)][string]$Phase
    )

    $snapshot = @(Get-T65XilinxProcessSnapshot)
    return Assert-T65XilinxProcessIdentities -ActualProcesses $snapshot -AllowedIdentities $AllowedIdentities -Phase $Phase
}
