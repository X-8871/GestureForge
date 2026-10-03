[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$EvidenceDirectory,

    [Parameter(Mandatory = $true)]
    [string]$RunId,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedBackendSha256,

    [ValidateRange(1, 108)]
    [int]$FirstIndex = 1,

    [ValidateRange(1, 108)]
    [int]$LastIndex = 108,

    [ValidateRange(1, 108)]
    [int]$MaxWorkers = 8
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-Sha256Literal {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Test-S2aNetworkBackendResultSummary {
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text)

    $normalizedText = $Text.Replace("`r`n", "`n")
    return ($normalizedText -match '(?m)^status=PASS_LAYERWISE_EXACT_GOLDEN$') -and
        ($normalizedText -match '(?m)^feature_write_bytes=11382150 mismatches=0 cycles=[0-9]+$') -and
        ($normalizedText -match '(?m)^head13_bytes=5070 head26_bytes=20280$')
}

function Add-SchedulerError {
    param([Parameter(Mandatory = $true)][string]$Message)
    if ([string]::IsNullOrWhiteSpace($script:schedulerError)) {
        $script:schedulerError = $Message
    } else {
        $script:schedulerError += [Environment]::NewLine + $Message
    }
    $script:stopLaunching = $true
}

function Test-SchedulerSourceStable {
    param([Parameter(Mandatory = $true)][string]$Checkpoint)
    $currentPath = $script:schedulerPath
    $currentBytes = $null
    $currentHash = $null
    $readError = $null
    try {
        $item = Get-Item -LiteralPath $script:schedulerPath -ErrorAction Stop
        if ($item.PSIsContainer -or (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw 'scheduler source 不是普通文件。'
        }
        $currentPath = $item.FullName
        $currentBytes = [long]$item.Length
        $currentHash = Get-Sha256Literal -Path $item.FullName
    } catch {
        $readError = $_.Exception.Message
    }
    $observation = [ordered]@{
        checkpoint = $Checkpoint
        observed_utc = [DateTime]::UtcNow.ToString('o')
        path = $currentPath
        expected_bytes = $script:schedulerFrozenBytes
        current_bytes = $currentBytes
        expected_sha256 = $script:schedulerFrozenHash
        current_sha256 = $currentHash
        unchanged = ($null -eq $readError) -and ($currentHash -ceq $script:schedulerFrozenHash) -and ($currentBytes -eq $script:schedulerFrozenBytes)
        read_error = $readError
    }
    if (-not $observation.unchanged) {
        $script:schedulerHashMismatches.Add($observation)
        Add-SchedulerError -Message ("scheduler source changed at {0}: expected sha256={1} bytes={2}; current sha256={3} bytes={4}; read_error={5}" -f `
            $Checkpoint, $script:schedulerFrozenHash, $script:schedulerFrozenBytes, $currentHash, $currentBytes, $readError)
    }
    return $observation
}

function Read-JsonObject {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label
    )
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "$Label 缺失：$Path" }
    $item = Get-Item -LiteralPath $Path
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) { throw "$Label 不能是 reparse point：$Path" }
    $value = [System.IO.File]::ReadAllText($item.FullName, [System.Text.Encoding]::UTF8) | ConvertFrom-Json -AsHashtable -Depth 64 -ErrorAction Stop
    if ($value -isnot [System.Collections.IDictionary]) { throw "$Label 顶层必须是 JSON 对象：$Path" }
    return $value
}

function Assert-NormalDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label
    )
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) { throw "$Label 目录缺失：$Path" }
    $item = Get-Item -LiteralPath $Path
    if (-not $item.PSIsContainer -or (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "$Label 必须是普通目录：$Path"
    }
    return $item.FullName
}

function Assert-PathWithin {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Parent,
        [Parameter(Mandatory = $true)][string]$Label
    )
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $fullParent = [System.IO.Path]::GetFullPath($Parent).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $prefix = $fullParent + [System.IO.Path]::DirectorySeparatorChar
    if (-not $fullPath.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "$Label 路径越出批准目录：$fullPath"
    }
    return $fullPath
}

function Get-SafeRunFile {
    param(
        [Parameter(Mandatory = $true)][string]$RunDirectory,
        [Parameter(Mandatory = $true)][object]$PathValue,
        [Parameter(Mandatory = $true)][string]$Label
    )
    if ($PathValue -isnot [string] -or [string]::IsNullOrWhiteSpace([string]$PathValue)) { throw "$Label 路径缺失" }
    if (-not [System.IO.Path]::IsPathRooted([string]$PathValue)) { throw "$Label 路径不是绝对路径：$PathValue" }
    $fullPath = Assert-PathWithin -Path ([string]$PathValue) -Parent $RunDirectory -Label $Label
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) { throw "$Label 文件缺失：$fullPath" }
    $item = Get-Item -LiteralPath $fullPath
    if ($item.PSIsContainer -or (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "$Label 必须是普通文件：$fullPath"
    }
    return $item.FullName
}

function Get-ClosureSignature {
    param(
        [Parameter(Mandatory = $true)][object[]]$Rows,
        [Parameter(Mandatory = $true)][int]$ExpectedCount,
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot
    )
    if ($Rows.Count -ne $ExpectedCount) { throw "$Label 行数应为 $ExpectedCount，实际为 $($Rows.Count)" }
    $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    $signatureRows = [System.Collections.Generic.List[string]]::new()
    foreach ($row in $Rows) {
        if ($row -isnot [System.Collections.IDictionary]) { throw "$Label 含非对象行" }
        if ($row.path -isnot [string] -or -not [System.IO.Path]::IsPathRooted([string]$row.path)) { throw "$Label 含无效 source path" }
        $fullPath = Assert-PathWithin -Path ([string]$row.path) -Parent $RepositoryRoot -Label $Label
        if (-not $seen.Add($fullPath)) { throw "$Label 含重复 source path：$fullPath" }
        if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) { throw "$Label source 缺失：$fullPath" }
        $item = Get-Item -LiteralPath $fullPath
        if ($item.PSIsContainer -or (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "$Label source 必须是普通文件：$fullPath"
        }
        $hash = Get-Sha256Literal -Path $fullPath
        if (($item.Length -ne [long]$row.bytes) -or ($hash -ne ([string]$row.sha256).ToLowerInvariant())) {
            throw "$Label source length/hash 与冻结 snapshot 不同：$fullPath"
        }
        $signatureRows.Add(($fullPath.ToLowerInvariant() + '|' + [string]$item.Length + '|' + $hash))
    }
    $sortedRows = @($signatureRows | Sort-Object -CaseSensitive)
    return ($sortedRows -join "`n")
}

function Get-ClosureDigest {
    param([Parameter(Mandatory = $true)][string]$Signature)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Signature)
    return [Convert]::ToHexString([System.Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
}

function Write-NewJsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][object]$Value
    )
    $json = ($Value | ConvertTo-Json -Depth 16) + [Environment]::NewLine
    $bytes = [System.Text.UTF8Encoding]::new($false).GetBytes($json)
    $stream = [System.IO.File]::Open($Path, [System.IO.FileMode]::CreateNew, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Dispose() }
}

function Quote-WindowsArgument {
    param([Parameter(Mandatory = $true)][AllowEmptyString()][string]$Argument)
    $builder = [System.Text.StringBuilder]::new()
    $null = $builder.Append([char]'"')
    $backslashes = 0
    foreach ($character in $Argument.ToCharArray()) {
        if ($character -eq [char]'\') {
            $backslashes++
        } elseif ($character -eq [char]'"') {
            for ($i = 0; $i -lt (2 * $backslashes + 1); $i++) { $null = $builder.Append([char]'\') }
            $null = $builder.Append([char]'"')
            $backslashes = 0
        } else {
            for ($i = 0; $i -lt $backslashes; $i++) { $null = $builder.Append([char]'\') }
            $null = $builder.Append($character)
            $backslashes = 0
        }
    }
    for ($i = 0; $i -lt (2 * $backslashes); $i++) { $null = $builder.Append([char]'\') }
    $null = $builder.Append([char]'"')
    return $builder.ToString()
}

function Get-SourceClosureFromSnapshot {
    param(
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$Snapshot,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$BackendPath,
        [Parameter(Mandatory = $true)][string]$ExpectedBackendHash
    )
    $sourceRows = @($Snapshot.sources)
    $sourceSignature = Get-ClosureSignature -Rows $sourceRows -ExpectedCount 11 -Label 'T68 compile source closure' -RepositoryRoot $RepositoryRoot
    $backendRows = @($sourceRows | Where-Object {
        [System.IO.Path]::GetFullPath([string]$_.path).Equals($BackendPath, [System.StringComparison]::OrdinalIgnoreCase)
    })
    if ($backendRows.Count -ne 1 -or ([string]$backendRows[0].sha256).ToLowerInvariant() -ne $ExpectedBackendHash) {
        throw 'sample0 compile snapshot backend 路径或 SHA 与显式冻结值不符。'
    }
    $toolRows = @($Snapshot.tooling_sources)
    $toolSignature = Get-ClosureSignature -Rows $toolRows -ExpectedCount 3 -Label 'T68 tooling source closure' -RepositoryRoot $RepositoryRoot
    return [ordered]@{
        source_rows = $sourceRows
        source_signature = $sourceSignature
        source_digest = Get-ClosureDigest -Signature $sourceSignature
        tooling_rows = $toolRows
        tooling_signature = $toolSignature
        tooling_digest = Get-ClosureDigest -Signature $toolSignature
    }
}

function Assert-CurrentSourceClosure {
    param(
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$FrozenClosure,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$Label
    )
    $sourceSignature = Get-ClosureSignature -Rows @($FrozenClosure.source_rows) -ExpectedCount 11 -Label "$Label compile closure" -RepositoryRoot $RepositoryRoot
    $toolSignature = Get-ClosureSignature -Rows @($FrozenClosure.tooling_rows) -ExpectedCount 3 -Label "$Label tooling closure" -RepositoryRoot $RepositoryRoot
    if ($sourceSignature -cne [string]$FrozenClosure.source_signature) { throw "$Label compile source closure changed after sample0 freeze" }
    if ($toolSignature -cne [string]$FrozenClosure.tooling_signature) { throw "$Label tooling source closure changed after sample0 freeze" }
}

function Assert-Sample0Passed {
    param(
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$RunId,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$BackendPath,
        [Parameter(Mandatory = $true)][string]$ExpectedBackendHash
    )
    $sampleDirectory = Join-Path $EvidenceRoot (Join-Path 'runs\sample_000' $RunId)
    $sampleDirectory = Assert-NormalDirectory -Path $sampleDirectory -Label 'sample0 run'
    $compilePath = Join-Path $sampleDirectory 'compile_execution_record.json'
    $simulationPath = Join-Path $sampleDirectory 'simulation_execution_record.json'
    $snapshotPath = Join-Path $sampleDirectory 'compile_source_snapshot.json'
    $compileRecord = Read-JsonObject -Path $compilePath -Label 'sample0 compile record'
    $simulationRecord = Read-JsonObject -Path $simulationPath -Label 'sample0 simulation record'
    $snapshot = Read-JsonObject -Path $snapshotPath -Label 'sample0 compile source snapshot'

    if ($compileRecord.exit_code -ne 0 -or $compileRecord.native_exit_code -ne 0 -or $compileRecord.compile_accepted -ne $true -or $compileRecord.simulator_started -ne $false) {
        throw 'sample0 compile record 未通过 exit/accepted/simulator_started 门。'
    }
    if ($compileRecord.sample_index -ne 0 -or $compileRecord.run_id -cne $RunId) { throw 'sample0 compile record index/run id 不匹配。' }
    if ($compileRecord.backend_sha256_expected -cne $ExpectedBackendHash) { throw 'sample0 compile record backend SHA 与期望值不符。' }
    if ($compileRecord.source_unchanged -ne $true -or $compileRecord.tooling_sources_unchanged -ne $true) { throw 'sample0 compile source closure 未保持稳定。' }
    if ($snapshot.schema_version -cne 'gestureforge_s2a_t68_compile_source_snapshot_v1' -or $snapshot.simulator_started -ne $false) {
        throw 'sample0 compile snapshot schema 或 simulator_started 不符。'
    }
    if ($simulationRecord.schema_version -cne 'gestureforge_s2a_t68_simulation_execution_v1' -or
        $simulationRecord.sample_index -ne 0 -or $simulationRecord.run_id -cne $RunId -or
        $simulationRecord.exit_code -ne 0 -or $simulationRecord.runner_exit_code -ne 0 -or
        $simulationRecord.progress_markers_valid -ne $true -or $simulationRecord.last_progress_phase -cne 'complete' -or
        $simulationRecord.result_summary_valid -ne $true -or $simulationRecord.head_exports_valid -ne $true -or
        $simulationRecord.wave_dump_requested -ne $false) {
        throw 'sample0 simulation record 未通过 progress/result/head/wave/exit 门。'
    }
    $snapshotHash = Get-Sha256Literal -Path $snapshotPath
    $compileHash = Get-Sha256Literal -Path $compilePath
    if ($simulationRecord.compile_source_snapshot_sha256 -cne $snapshotHash -or
        $simulationRecord.compile_execution_record_sha256 -cne $compileHash) {
        throw 'sample0 simulation record 未绑定当前 compile snapshot 与 compile record。'
    }
    if ($compileRecord.tooling_sources_after -isnot [System.Collections.IList]) { throw 'sample0 compile record 缺少 tooling_sources_after。' }
    $closure = Get-SourceClosureFromSnapshot -Snapshot $snapshot -RepositoryRoot $RepositoryRoot `
        -BackendPath $BackendPath -ExpectedBackendHash $ExpectedBackendHash
    $compileSourceSignature = Get-ClosureSignature -Rows @($compileRecord.sources_after) -ExpectedCount 11 `
        -Label 'sample0 compile record source closure' -RepositoryRoot $RepositoryRoot
    $compileToolSignature = Get-ClosureSignature -Rows @($compileRecord.tooling_sources) -ExpectedCount 3 `
        -Label 'sample0 compile record tooling closure' -RepositoryRoot $RepositoryRoot
    $compileToolAfterSignature = Get-ClosureSignature -Rows @($compileRecord.tooling_sources_after) -ExpectedCount 3 `
        -Label 'sample0 post-compile tooling closure' -RepositoryRoot $RepositoryRoot
    if ($compileSourceSignature -cne $closure.source_signature -or
        $compileToolSignature -cne $closure.tooling_signature -or
        $compileToolAfterSignature -cne $closure.tooling_signature) {
        throw 'sample0 compile record 与 compile snapshot 闭包不一致。'
    }
    if ($simulationRecord.tooling_sources -isnot [System.Collections.IList]) { throw 'sample0 simulation record 缺少 tooling source rows。' }
    $simulationToolSignature = Get-ClosureSignature -Rows @($simulationRecord.tooling_sources) -ExpectedCount 3 `
        -Label 'sample0 simulation tooling closure' -RepositoryRoot $RepositoryRoot
    if ($simulationToolSignature -cne $closure.tooling_signature) { throw 'sample0 simulation tooling closure 与 compile snapshot 不一致。' }

    $summaryPath = Get-SafeRunFile -RunDirectory $sampleDirectory -PathValue $simulationRecord.result_summary_path -Label 'sample0 result summary'
    if ((Get-Sha256Literal -Path $summaryPath) -cne $simulationRecord.result_summary_sha256) { throw 'sample0 result summary SHA 不匹配。' }
    $summaryText = [System.IO.File]::ReadAllText($summaryPath, [System.Text.Encoding]::UTF8)
    if (-not (Test-S2aNetworkBackendResultSummary -Text $summaryText)) {
        throw 'sample0 result summary 未包含完整 golden/head PASS 记录。'
    }
    foreach ($head in @(
        @{ key = 'head13_export'; file = 'head13_actual_int8.bin'; bytes = 5070 },
        @{ key = 'head26_export'; file = 'head26_actual_int8.bin'; bytes = 20280 }
    )) {
        $export = $simulationRecord[$head.key]
        if ($export -isnot [System.Collections.IDictionary]) { throw "sample0 $($head.key) record 缺失。" }
        $exportPath = Get-SafeRunFile -RunDirectory $sampleDirectory -PathValue $export.path -Label "sample0 $($head.key)"
        $exportItem = Get-Item -LiteralPath $exportPath
        if ($exportItem.Length -ne $head.bytes -or $export.bytes -ne $head.bytes -or
            (Get-Sha256Literal -Path $exportPath) -cne $export.sha256) {
            throw "sample0 $($head.key) 长度/SHA 不匹配。"
        }
        if ([System.IO.Path]::GetFileName($exportPath) -cne $head.file) { throw "sample0 $($head.key) 文件名不符合约定。" }
    }

    $manifestPath = Join-Path $EvidenceRoot 'fixtures\sample_000\fixture_manifest.json'
    $fixtureManifest = Read-JsonObject -Path $manifestPath -Label 'sample0 fixture manifest'
    if ($fixtureManifest.sample_index -ne 0 -or $fixtureManifest.weight_package.path -cne 'fixtures/common/weights.gf8') {
        throw 'sample0 fixture manifest 的索引或 common GF8 路径不符。'
    }
    $commonWeightPath = Join-Path $EvidenceRoot 'fixtures\common\weights.gf8'
    if (-not (Test-Path -LiteralPath $commonWeightPath -PathType Leaf)) { throw "common GF8 fixture 缺失：$commonWeightPath" }
    $weightItem = Get-Item -LiteralPath $commonWeightPath
    if ($weightItem.PSIsContainer -or (($weightItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) -or
        $weightItem.Length -ne $fixtureManifest.weight_package.bytes -or
        (Get-Sha256Literal -Path $commonWeightPath) -cne $fixtureManifest.weight_package.sha256) {
        throw 'common GF8 fixture 类型、长度或 SHA 与 sample0 manifest 不匹配。'
    }

    return [ordered]@{
        sample_directory = $sampleDirectory
        snapshot_path = $snapshotPath
        snapshot_bytes = (Get-Item -LiteralPath $snapshotPath).Length
        snapshot_sha256 = $snapshotHash
        compile_record_sha256 = $compileHash
        closure = $closure
        common_weight_path = $commonWeightPath
        common_weight_bytes = $weightItem.Length
        common_weight_sha256 = Get-Sha256Literal -Path $commonWeightPath
    }
}

function Assert-PendingRunDirectories {
    param(
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$RunId,
        [Parameter(Mandatory = $true)][int[]]$Indices
    )
    $runsDirectory = Join-Path $EvidenceRoot 'runs'
    if (Test-Path -LiteralPath $runsDirectory) {
        $null = Assert-NormalDirectory -Path $runsDirectory -Label 'runs'
    }
    foreach ($index in $Indices) {
        $sampleParent = Join-Path $runsDirectory ("sample_{0:D3}" -f $index)
        if (Test-Path -LiteralPath $sampleParent) { $null = Assert-NormalDirectory -Path $sampleParent -Label "sample_$index parent" }
        $runDirectory = Join-Path $sampleParent $RunId
        if (Test-Path -LiteralPath $runDirectory) { throw "拒绝覆盖已存在 sample/run evidence：$runDirectory" }
    }
}

function Test-CompletedSampleRecords {
    param(
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$RunId,
        [Parameter(Mandatory = $true)][int]$SampleIndex,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$BackendPath,
        [Parameter(Mandatory = $true)][string]$ExpectedBackendHash,
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$FrozenClosure
    )
    $sampleKey = "sample_{0:D3}" -f $SampleIndex
    $sampleDirectory = Assert-NormalDirectory -Path (Join-Path $EvidenceRoot (Join-Path "runs\$sampleKey" $RunId)) -Label "$sampleKey run"
    $compilePath = Join-Path $sampleDirectory 'compile_execution_record.json'
    $simulationPath = Join-Path $sampleDirectory 'simulation_execution_record.json'
    $snapshotPath = Join-Path $sampleDirectory 'compile_source_snapshot.json'
    $compileRecord = Read-JsonObject -Path $compilePath -Label "$sampleKey compile record"
    $simulationRecord = Read-JsonObject -Path $simulationPath -Label "$sampleKey simulation record"
    $snapshot = Read-JsonObject -Path $snapshotPath -Label "$sampleKey compile snapshot"

    if ($compileRecord.exit_code -ne 0 -or $compileRecord.native_exit_code -ne 0 -or
        $compileRecord.compile_accepted -ne $true -or $compileRecord.simulator_started -ne $false -or
        $compileRecord.sample_index -ne $SampleIndex -or $compileRecord.run_id -cne $RunId -or
        $compileRecord.backend_sha256_expected -cne $ExpectedBackendHash -or
        $compileRecord.source_unchanged -ne $true -or $compileRecord.tooling_sources_unchanged -ne $true) {
        throw "$sampleKey compile execution record 未通过成功门。"
    }
    if ($snapshot.schema_version -cne 'gestureforge_s2a_t68_compile_source_snapshot_v1' -or
        $snapshot.sample_index -ne $SampleIndex -or $snapshot.run_id -cne $RunId -or $snapshot.simulator_started -ne $false) {
        throw "$sampleKey compile snapshot sample/run/schema 不符。"
    }
    $sourceSignature = Get-ClosureSignature -Rows @($snapshot.sources) -ExpectedCount 11 -Label "$sampleKey snapshot" -RepositoryRoot $RepositoryRoot
    $recordSourceSignature = Get-ClosureSignature -Rows @($compileRecord.sources_after) -ExpectedCount 11 -Label "$sampleKey compile record" -RepositoryRoot $RepositoryRoot
    $toolSignature = Get-ClosureSignature -Rows @($snapshot.tooling_sources) -ExpectedCount 3 -Label "$sampleKey snapshot tooling" -RepositoryRoot $RepositoryRoot
    $recordToolSignature = Get-ClosureSignature -Rows @($compileRecord.tooling_sources) -ExpectedCount 3 -Label "$sampleKey compile tooling" -RepositoryRoot $RepositoryRoot
    $recordToolAfterSignature = Get-ClosureSignature -Rows @($compileRecord.tooling_sources_after) -ExpectedCount 3 -Label "$sampleKey post compile tooling" -RepositoryRoot $RepositoryRoot
    if ($sourceSignature -cne [string]$FrozenClosure.source_signature -or
        $recordSourceSignature -cne [string]$FrozenClosure.source_signature -or
        $toolSignature -cne [string]$FrozenClosure.tooling_signature -or
        $recordToolSignature -cne [string]$FrozenClosure.tooling_signature -or
        $recordToolAfterSignature -cne [string]$FrozenClosure.tooling_signature) {
        throw "$sampleKey compiled source/tooling closure differs from sample0."
    }
    if ($simulationRecord.schema_version -cne 'gestureforge_s2a_t68_simulation_execution_v1' -or
        $simulationRecord.sample_index -ne $SampleIndex -or $simulationRecord.run_id -cne $RunId -or
        $simulationRecord.exit_code -ne 0 -or $simulationRecord.runner_exit_code -ne 0 -or
        $simulationRecord.progress_markers_valid -ne $true -or $simulationRecord.last_progress_phase -cne 'complete' -or
        $simulationRecord.result_summary_valid -ne $true -or $simulationRecord.head_exports_valid -ne $true -or
        $simulationRecord.wave_dump_requested -ne $false) {
        throw "$sampleKey simulation execution record 未通过 progress/result/head/exit 门。"
    }
    $expectedSnapshotHash = Get-Sha256Literal -Path $snapshotPath
    $expectedCompileHash = Get-Sha256Literal -Path $compilePath
    if ($simulationRecord.compile_source_snapshot_sha256 -cne $expectedSnapshotHash -or
        $simulationRecord.compile_execution_record_sha256 -cne $expectedCompileHash) {
        throw "$sampleKey simulation record 未绑定当前 compile records。"
    }
    $simulationToolSignature = Get-ClosureSignature -Rows @($simulationRecord.tooling_sources) -ExpectedCount 3 `
        -Label "$sampleKey simulation tooling" -RepositoryRoot $RepositoryRoot
    if ($simulationToolSignature -cne [string]$FrozenClosure.tooling_signature) { throw "$sampleKey simulation tooling closure 不符。" }

    $resultPath = Get-SafeRunFile -RunDirectory $sampleDirectory -PathValue $simulationRecord.result_summary_path -Label "$sampleKey result summary"
    if ((Get-Sha256Literal -Path $resultPath) -cne $simulationRecord.result_summary_sha256) { throw "$sampleKey result summary SHA 不匹配。" }
    $resultText = [System.IO.File]::ReadAllText($resultPath, [System.Text.Encoding]::UTF8)
    if ($resultText -notmatch '(?m)^status=PASS_LAYERWISE_EXACT_GOLDEN$' -or
        $resultText -notmatch '(?m)^feature_write_bytes=11382150 mismatches=0 cycles=[0-9]+$' -or
        $resultText -notmatch '(?m)^head13_bytes=5070 head26_bytes=20280$') {
        throw "$sampleKey result summary 缺少 PASS 或字节统计。"
    }
    $headHashes = [ordered]@{}
    foreach ($head in @(
        @{ key = 'head13_export'; file = 'head13_actual_int8.bin'; bytes = 5070 },
        @{ key = 'head26_export'; file = 'head26_actual_int8.bin'; bytes = 20280 }
    )) {
        $export = $simulationRecord[$head.key]
        if ($export -isnot [System.Collections.IDictionary]) { throw "$sampleKey $($head.key) record 缺失。" }
        $exportPath = Get-SafeRunFile -RunDirectory $sampleDirectory -PathValue $export.path -Label "$sampleKey $($head.key)"
        $exportItem = Get-Item -LiteralPath $exportPath
        $hash = Get-Sha256Literal -Path $exportPath
        if ([System.IO.Path]::GetFileName($exportPath) -cne $head.file -or
            $exportItem.Length -ne $head.bytes -or $export.bytes -ne $head.bytes -or $hash -cne $export.sha256) {
            throw "$sampleKey $($head.key) export length/path/SHA 不匹配。"
        }
        $headHashes[$head.key] = $hash
    }
    $fixturePath = Join-Path $EvidenceRoot ("fixtures\$sampleKey\fixture_manifest.json")
    $fixture = Read-JsonObject -Path $fixturePath -Label "$sampleKey fixture manifest"
    if ($fixture.sample_index -ne $SampleIndex -or $fixture.weight_package.path -cne 'fixtures/common/weights.gf8' -or
        $fixture.weight_package.sha256 -cne (Get-Sha256Literal -Path (Join-Path $EvidenceRoot 'fixtures\common\weights.gf8'))) {
        throw "$sampleKey fixture manifest index/common weight binding 不匹配。"
    }

    return [ordered]@{
        sample_index = $SampleIndex
        run_id = $RunId
        compile_record_sha256 = $expectedCompileHash
        simulation_record_sha256 = Get-Sha256Literal -Path $simulationPath
        compile_snapshot_sha256 = $expectedSnapshotHash
        result_summary_sha256 = Get-Sha256Literal -Path $resultPath
        head13_sha256 = $headHashes.head13_export
        head26_sha256 = $headHashes.head26_export
    }
}

function Get-WorkerEvent {
    param(
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$Worker,
        [Parameter(Mandatory = $true)][int]$ExitCode,
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$RunId,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$BackendPath,
        [Parameter(Mandatory = $true)][string]$ExpectedBackendHash,
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$FrozenClosure
    )
    $validation = $null
    $failure = $null
    if ($ExitCode -ne 0) {
        $failure = "child_runner_exit_$ExitCode"
    } else {
        try {
            $validation = Test-CompletedSampleRecords -EvidenceRoot $EvidenceRoot -RunId $RunId `
                -SampleIndex $Worker.sample_index -RepositoryRoot $RepositoryRoot -BackendPath $BackendPath `
                -ExpectedBackendHash $ExpectedBackendHash -FrozenClosure $FrozenClosure
        } catch {
            $failure = $_.Exception.Message
        }
    }
    $stdoutHash = if (Test-Path -LiteralPath $Worker.stdout_path -PathType Leaf) { Get-Sha256Literal -Path $Worker.stdout_path } else { $null }
    $stderrHash = if (Test-Path -LiteralPath $Worker.stderr_path -PathType Leaf) { Get-Sha256Literal -Path $Worker.stderr_path } else { $null }
    return [ordered]@{
        schema_version = 'gestureforge_s2a_t68_batch_event_v1'
        sample_index = $Worker.sample_index
        run_id = $RunId
        status = if ($null -eq $failure) { 'PASS_RUNNER_AND_RECORDS' } else { 'FAIL_RUNNER_OR_RECORDS' }
        runner_exit_code = $ExitCode
        process_id = $Worker.process_id
        process_started_utc = $Worker.started_utc
        process_finished_utc = [DateTime]::UtcNow.ToString('o')
        stdout_path = $Worker.stdout_path
        stdout_sha256 = $stdoutHash
        stderr_path = $Worker.stderr_path
        stderr_sha256 = $stderrHash
        validated_records = $validation
        failure = $failure
    }
}

function Complete-OwnedWorker {
    param(
        [Parameter(Mandatory = $true)][string]$WorkerKey,
        [Parameter(Mandatory = $true)][string]$EvidenceRoot,
        [Parameter(Mandatory = $true)][string]$RunId,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot,
        [Parameter(Mandatory = $true)][string]$BackendPath,
        [Parameter(Mandatory = $true)][string]$ExpectedBackendHash,
        [Parameter(Mandatory = $true)][System.Collections.IDictionary]$FrozenClosure,
        [Parameter(Mandatory = $true)][string]$DispatchDirectory
    )
    if (-not $script:workerProcesses.ContainsKey($WorkerKey)) { return $true }
    $worker = $script:workerProcesses[$WorkerKey]
    $hasExited = $false
    $exitCode = $null
    try {
        $worker.process.Refresh()
        $hasExited = $worker.process.HasExited
        if ($hasExited) { $exitCode = [int]$worker.process.ExitCode }
    } catch {
        Add-SchedulerError -Message ("runner process refresh failed sample={0}: {1}" -f $worker.sample_index, $_.Exception.Message)
        try {
            $worker.process.WaitForExit()
            $worker.process.Refresh()
            $hasExited = $worker.process.HasExited
            if ($hasExited) { $exitCode = [int]$worker.process.ExitCode }
        } catch {
            Add-SchedulerError -Message ("runner process wait failed sample={0}: {1}" -f $worker.sample_index, $_.Exception.Message)
            return $false
        }
    }
    if (-not $hasExited) { return $false }

    $eventPath = Join-Path $DispatchDirectory ("sample_{0:D3}_event.json" -f $worker.sample_index)
    $event = $null
    $eventWriteError = $null
    $samplePassed = $false
    try {
        $event = Get-WorkerEvent -Worker $worker -ExitCode $exitCode -EvidenceRoot $EvidenceRoot `
            -RunId $RunId -RepositoryRoot $RepositoryRoot -BackendPath $BackendPath `
            -ExpectedBackendHash $ExpectedBackendHash -FrozenClosure $FrozenClosure
        if ($exitCode -eq 0 -and $event.status -eq 'PASS_RUNNER_AND_RECORDS') {
            $samplePassed = $true
        } elseif ($exitCode -eq 0) {
            Add-SchedulerError -Message ("worker evidence validation failed sample={0}: {1}" -f $worker.sample_index, $event.failure)
        }
        if ($exitCode -ne 0) { $script:stopLaunching = $true }
    } catch {
        Add-SchedulerError -Message ("worker event validation failed sample={0}: {1}" -f $worker.sample_index, $_.Exception.Message)
        $event = [ordered]@{
            schema_version = 'gestureforge_s2a_t68_batch_event_v1'
            sample_index = $worker.sample_index
            run_id = $RunId
            status = 'FAIL_RUNNER_OR_RECORDS'
            runner_exit_code = $exitCode
            process_id = $worker.process_id
            process_started_utc = $worker.started_utc
            process_finished_utc = [DateTime]::UtcNow.ToString('o')
            stdout_path = $worker.stdout_path
            stderr_path = $worker.stderr_path
            validated_records = $null
            failure = $_.Exception.Message
        }
    }

    try {
        Write-NewJsonFile -Path $eventPath -Value $event
        $script:eventRows.Add([ordered]@{
            sample_index = $worker.sample_index
            path = $eventPath
            sha256 = Get-Sha256Literal -Path $eventPath
            write_error = $null
        })
    } catch {
        $eventWriteError = $_.Exception.Message
        Add-SchedulerError -Message ("worker event write failed sample={0}: {1}" -f $worker.sample_index, $eventWriteError)
        $samplePassed = $false
        $script:eventRows.Add([ordered]@{
            sample_index = $worker.sample_index
            path = $eventPath
            sha256 = $null
            write_error = $eventWriteError
        })
    } finally {
        if ($samplePassed) {
            if (-not $script:succeededIndices.Contains([int]$worker.sample_index)) {
                $script:succeededIndices.Add([int]$worker.sample_index)
            }
        } else {
            $script:stopLaunching = $true
            if (-not $script:failedIndices.Contains([int]$worker.sample_index)) {
                $script:failedIndices.Add([int]$worker.sample_index)
            }
        }
        $script:workerProcesses.Remove($WorkerKey)
    }
    return $true
}

if ([Version]$PSVersionTable.PSVersion -lt [Version]'7.0') { throw '批次 scheduler 需要 PowerShell 7 或更新版本。' }
if ($FirstIndex -gt $LastIndex) { throw 'FirstIndex 必须小于或等于 LastIndex。' }
if ($ExpectedBackendSha256 -notmatch '^[0-9a-fA-F]{64}$') { throw 'ExpectedBackendSha256 必须是 64 位 SHA-256。' }
if ($RunId -notmatch '^[A-Za-z0-9_-]+$') { throw 'RunId 仅允许 ASCII 字母、数字、下划线和连字符。' }

$script:schedulerPath = (Resolve-Path -LiteralPath $PSCommandPath).Path
$schedulerInitialItem = Get-Item -LiteralPath $script:schedulerPath
if ($schedulerInitialItem.PSIsContainer -or (($schedulerInitialItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
    throw "scheduler source 必须是普通文件：$($script:schedulerPath)"
}
$script:schedulerFrozenBytes = [long]$schedulerInitialItem.Length
$script:schedulerFrozenHash = Get-Sha256Literal -Path $script:schedulerPath
$script:schedulerHashMismatches = [System.Collections.Generic.List[object]]::new()
$script:schedulerError = $null
$script:stopLaunching = $false

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$evidenceRoot = [System.IO.Path]::GetFullPath($EvidenceDirectory)
$evidenceRoot = Assert-NormalDirectory -Path $evidenceRoot -Label 'EvidenceDirectory'
if ($evidenceRoot -split '[\\/]' | Where-Object { $_ -ieq 'run01' }) { throw '为保护既有 run01，EvidenceDirectory 路径不能包含 run01 组件。' }
$backendPath = [System.IO.Path]::GetFullPath((Join-Path $repoRoot 'src\s2a_network_backend.sv'))
$runnerPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot 'run_s2a_network_backend_verilator.ps1')).Path
$actualBackendHash = Get-Sha256Literal -Path $backendPath
$expectedBackendHash = $ExpectedBackendSha256.ToLowerInvariant()
if ($actualBackendHash -cne $expectedBackendHash) { throw "当前 backend SHA 与显式冻结值不匹配：$actualBackendHash" }

$pwshProcess = Get-Process -Id $PID -ErrorAction Stop
$pwshPath = [System.IO.Path]::GetFullPath([string]$pwshProcess.Path)
if ([System.IO.Path]::GetFileName($pwshPath) -ine 'pwsh.exe') { throw "scheduler 必须由 pwsh.exe 运行：$pwshPath" }
$firstIndex = [int]$FirstIndex
$lastIndex = [int]$LastIndex
$maxWorkers = [int]$MaxWorkers
$targetIndices = @($firstIndex..$lastIndex)
$frozen = Assert-Sample0Passed -EvidenceRoot $evidenceRoot -RunId $RunId `
    -RepositoryRoot $repoRoot -BackendPath $backendPath -ExpectedBackendHash $expectedBackendHash
Assert-PendingRunDirectories -EvidenceRoot $evidenceRoot -RunId $RunId -Indices $targetIndices

$dispatchDirectory = Join-Path $evidenceRoot 'batch_dispatch'
if (Test-Path -LiteralPath $dispatchDirectory) { throw "拒绝复用既有 batch_dispatch：$dispatchDirectory" }
$null = New-Item -ItemType Directory -Path $dispatchDirectory -Force:$false
$dispatchDirectory = Assert-NormalDirectory -Path $dispatchDirectory -Label 'batch_dispatch'

$schedulerSnapshotPath = Join-Path $dispatchDirectory 'scheduler_source_snapshot.json'
$schedulerSnapshot = [ordered]@{
    schema_version = 'gestureforge_s2a_t68_batch_scheduler_source_v1'
    path = $script:schedulerPath
    bytes = $script:schedulerFrozenBytes
    sha256 = $script:schedulerFrozenHash
    frozen_utc = [DateTime]::UtcNow.ToString('o')
}
$schedulerSnapshotWriteError = $null
try {
    Write-NewJsonFile -Path $schedulerSnapshotPath -Value $schedulerSnapshot
} catch {
    $schedulerSnapshotWriteError = $_.Exception.Message
    Add-SchedulerError -Message ("scheduler source snapshot write failed: {0}" -f $schedulerSnapshotWriteError)
}

$startedIndices = [System.Collections.Generic.List[int]]::new()
$succeededIndices = [System.Collections.Generic.List[int]]::new()
$failedIndices = [System.Collections.Generic.List[int]]::new()
$workerProcesses = @{}
$nextPosition = 0
$eventRows = [System.Collections.Generic.List[object]]::new()
$script:startedIndices = $startedIndices
$script:succeededIndices = $succeededIndices
$script:failedIndices = $failedIndices
$script:workerProcesses = $workerProcesses
$script:eventRows = $eventRows

$mainLoopException = $null
try {
    while (($workerProcesses.Count -gt 0) -or ((-not $stopLaunching) -and ($nextPosition -lt $targetIndices.Count))) {
        foreach ($workerKey in @($workerProcesses.Keys)) {
            try {
                $null = Complete-OwnedWorker -WorkerKey ([string]$workerKey) -EvidenceRoot $evidenceRoot `
                    -RunId $RunId -RepositoryRoot $repoRoot -BackendPath $backendPath `
                    -ExpectedBackendHash $expectedBackendHash -FrozenClosure $frozen.closure `
                    -DispatchDirectory $dispatchDirectory
            } catch {
                Add-SchedulerError -Message ("main-loop worker completion exception key={0}: {1}" -f $workerKey, $_.Exception.Message)
            }
        }

        while ((-not $stopLaunching) -and ($workerProcesses.Count -lt $maxWorkers) -and ($nextPosition -lt $targetIndices.Count)) {
            $sampleIndex = [int]$targetIndices[$nextPosition]
            try {
                $schedulerObservation = Test-SchedulerSourceStable -Checkpoint ("before_sample_{0:D3}_dispatch" -f $sampleIndex)
                if (-not $schedulerObservation.unchanged) { break }
                Assert-CurrentSourceClosure -FrozenClosure $frozen.closure -RepositoryRoot $repoRoot -Label "before sample_$('{0:D3}' -f $sampleIndex) launch"
                $sampleRunDirectory = Join-Path $evidenceRoot (Join-Path ("runs\sample_{0:D3}" -f $sampleIndex) $RunId)
                if (Test-Path -LiteralPath $sampleRunDirectory) { throw "拒绝覆盖新出现的 sample/run evidence：$sampleRunDirectory" }
                $stdoutPath = Join-Path $dispatchDirectory ("sample_{0:D3}.stdout.log" -f $sampleIndex)
                $stderrPath = Join-Path $dispatchDirectory ("sample_{0:D3}.stderr.log" -f $sampleIndex)
                if ((Test-Path -LiteralPath $stdoutPath) -or (Test-Path -LiteralPath $stderrPath)) { throw "sample_$('{0:D3}' -f $sampleIndex) batch log 已存在。" }
                $arguments = @(
                    '-NoLogo',
                    '-NoProfile',
                    '-NonInteractive',
                    '-File', $runnerPath,
                    '-SampleIndex', [string]$sampleIndex,
                    '-RunId', $RunId,
                    '-EvidenceDirectory', $evidenceRoot,
                    '-ExpectedBackendSha256', $expectedBackendHash,
                    '-MaxCycles', '4294967295',
                    '-Compile',
                    '-RunSimulation'
                )
                $argumentLine = ($arguments | ForEach-Object { Quote-WindowsArgument -Argument ([string]$_) }) -join ' '
                $dispatchObservation = Test-SchedulerSourceStable -Checkpoint ("immediately_before_sample_{0:D3}_start_process" -f $sampleIndex)
                if (-not $dispatchObservation.unchanged) { throw 'scheduler source integrity check failed immediately before worker launch.' }
                $process = Start-Process -FilePath $pwshPath -ArgumentList $argumentLine -WorkingDirectory $repoRoot `
                    -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru
                $worker = [ordered]@{
                    sample_index = $sampleIndex
                    process = $process
                    process_id = $process.Id
                    started_utc = [DateTime]::UtcNow.ToString('o')
                    stdout_path = $stdoutPath
                    stderr_path = $stderrPath
                }
                $workerProcesses[[string]$sampleIndex] = $worker
                $nextPosition++
                $startedIndices.Add($sampleIndex)
                Write-Output ("T68 batch sample={0:D3} START runner_pid={1}" -f $sampleIndex, $process.Id)
            } catch {
                Add-SchedulerError -Message ("sample_$('{0:D3}' -f $sampleIndex) launch stopped: $($_.Exception.Message)")
            }
        }

        if (($workerProcesses.Count -gt 0) -or ((-not $stopLaunching) -and ($nextPosition -lt $targetIndices.Count))) {
            Start-Sleep -Seconds 2
        }
    }
} catch {
    $mainLoopException = $_.Exception.Message
    Add-SchedulerError -Message ("main scheduler loop exception: {0}" -f $mainLoopException)
}

while ($workerProcesses.Count -gt 0) {
    try {
        foreach ($workerKey in @($workerProcesses.Keys)) {
            try {
                $null = Complete-OwnedWorker -WorkerKey ([string]$workerKey) -EvidenceRoot $evidenceRoot `
                    -RunId $RunId -RepositoryRoot $repoRoot -BackendPath $backendPath `
                    -ExpectedBackendHash $expectedBackendHash -FrozenClosure $frozen.closure `
                    -DispatchDirectory $dispatchDirectory
            } catch {
                Add-SchedulerError -Message ("worker drain exception key={0}: {1}" -f $workerKey, $_.Exception.Message)
                if ($workerProcesses.ContainsKey([string]$workerKey)) {
                    $ownedWorker = $workerProcesses[[string]$workerKey]
                    try {
                        $ownedWorker.process.WaitForExit()
                        $ownedWorker.process.Refresh()
                        if ($ownedWorker.process.HasExited) {
                            $null = Complete-OwnedWorker -WorkerKey ([string]$workerKey) -EvidenceRoot $evidenceRoot `
                                -RunId $RunId -RepositoryRoot $repoRoot -BackendPath $backendPath `
                                -ExpectedBackendHash $expectedBackendHash -FrozenClosure $frozen.closure `
                                -DispatchDirectory $dispatchDirectory
                        }
                    } catch {
                        Add-SchedulerError -Message ("owned worker wait/reclaim failed key={0}: {1}" -f $workerKey, $_.Exception.Message)
                    }
                }
            }
        }
        if ($workerProcesses.Count -gt 0) { [System.Threading.Thread]::Sleep(2000) }
    } catch {
        Add-SchedulerError -Message ("worker drain loop exception: {0}" -f $_.Exception.Message)
        foreach ($workerKey in @($workerProcesses.Keys)) {
            if (-not $workerProcesses.ContainsKey([string]$workerKey)) { continue }
            $ownedWorker = $workerProcesses[[string]$workerKey]
            try {
                $ownedWorker.process.WaitForExit()
                $ownedWorker.process.Refresh()
                if ($ownedWorker.process.HasExited) {
                    $null = Complete-OwnedWorker -WorkerKey ([string]$workerKey) -EvidenceRoot $evidenceRoot `
                        -RunId $RunId -RepositoryRoot $repoRoot -BackendPath $backendPath `
                        -ExpectedBackendHash $expectedBackendHash -FrozenClosure $frozen.closure `
                        -DispatchDirectory $dispatchDirectory
                }
            } catch {
                Add-SchedulerError -Message ("owned worker emergency reclaim failed key={0}: {1}" -f $workerKey, $_.Exception.Message)
            }
        }
    }
}

$schedulerFinalObservation = Test-SchedulerSourceStable -Checkpoint 'before_summary_write'

$summaryPath = Join-Path $dispatchDirectory 'batch_summary.json'
$finalDispatched = [System.Collections.Generic.HashSet[int]]::new()
foreach ($sample in $startedIndices) { $null = $finalDispatched.Add([int]$sample) }
foreach ($sample in $succeededIndices) { $null = $finalDispatched.Add([int]$sample) }
foreach ($sample in $failedIndices) { $null = $finalDispatched.Add([int]$sample) }
foreach ($workerKey in @($workerProcesses.Keys)) { $null = $finalDispatched.Add([int]$workerKey) }
$dispatchedIndices = @($targetIndices | Where-Object { $finalDispatched.Contains([int]$_) } | Sort-Object)
$remainingIndices = @($targetIndices | Where-Object { -not $finalDispatched.Contains([int]$_) } | Sort-Object)
$allTargetSucceeded = ($succeededIndices.Count -eq $targetIndices.Count) -and ($failedIndices.Count -eq 0) -and ($workerProcesses.Count -eq 0) -and ($null -eq $schedulerError)
if ($allTargetSucceeded -and ($targetIndices.Count -eq 108) -and ($firstIndex -eq 1) -and ($lastIndex -eq 108)) {
    $batchStatus = 'PASS_108_RUNNERS'
} elseif ($allTargetSucceeded) {
    $batchStatus = "PASS_SUBSET_$($targetIndices.Count)_RUNNERS"
} else {
    $batchStatus = 'FAIL_RUNNERS'
}
$summaryFailure = $null
try {
    $schedulerSnapshotBytes = $null
    $schedulerSnapshotHash = $null
    if (Test-Path -LiteralPath $schedulerSnapshotPath -PathType Leaf) {
        $snapshotItem = Get-Item -LiteralPath $schedulerSnapshotPath -ErrorAction Stop
        $schedulerSnapshotBytes = [long]$snapshotItem.Length
        $schedulerSnapshotHash = Get-Sha256Literal -Path $schedulerSnapshotPath
    }
    $summary = [ordered]@{
        schema_version = 'gestureforge_s2a_t68_batch_summary_v1'
        status = $batchStatus
        evidence_directory = $evidenceRoot
        run_id = $RunId
        expected_backend_sha256 = $expectedBackendHash
        scheduler_path = $script:schedulerPath
        scheduler_bytes = $script:schedulerFrozenBytes
        scheduler_sha256 = $script:schedulerFrozenHash
        scheduler_source_snapshot = [ordered]@{
            path = $schedulerSnapshotPath
            bytes = $schedulerSnapshotBytes
            sha256 = $schedulerSnapshotHash
            write_error = $schedulerSnapshotWriteError
        }
        scheduler_final_observation = $schedulerFinalObservation
        scheduler_hash_mismatches = @($script:schedulerHashMismatches)
        runner_path = $runnerPath
        runner_sha256 = Get-Sha256Literal -Path $runnerPath
        pwsh_path = $pwshPath
        first_index = $firstIndex
        last_index = $lastIndex
        max_workers = $maxWorkers
        poll_interval_seconds = 2
        sample0_snapshot = [ordered]@{
            path = $frozen.snapshot_path
            bytes = $frozen.snapshot_bytes
            sha256 = $frozen.snapshot_sha256
            compile_record_sha256 = $frozen.compile_record_sha256
            source_closure_sha256 = $frozen.closure.source_digest
            tooling_closure_sha256 = $frozen.closure.tooling_digest
        }
        common_weight = [ordered]@{
            path = $frozen.common_weight_path
            bytes = $frozen.common_weight_bytes
            sha256 = $frozen.common_weight_sha256
        }
        target_indices = $targetIndices
        dispatched_indices = $dispatchedIndices
        started_indices = @($startedIndices | Sort-Object)
        succeeded_indices = @($succeededIndices | Sort-Object)
        failed_indices = @($failedIndices | Sort-Object)
        remaining_indices = $remainingIndices
        scheduler_error = $schedulerError
        events = @($eventRows)
        d9_aggregation_started = $false
        stage2a_pass = $false
        created_utc = [DateTime]::UtcNow.ToString('o')
    }
    Write-NewJsonFile -Path $summaryPath -Value $summary
} catch {
    $summaryFailure = $_.Exception.Message
    Add-SchedulerError -Message ("batch summary finalization failed: {0}" -f $summaryFailure)
    $allTargetSucceeded = $false
    $batchStatus = 'FAIL_RUNNERS'
    try {
        if (Test-Path -LiteralPath $summaryPath) { $summaryPath = Join-Path $dispatchDirectory 'batch_summary_fallback.json' }
        $emergencySummary = [ordered]@{
            schema_version = 'gestureforge_s2a_t68_batch_summary_v1'
            status = 'FAIL_RUNNERS'
            evidence_directory = $evidenceRoot
            run_id = $RunId
            scheduler_path = $script:schedulerPath
            scheduler_bytes = $script:schedulerFrozenBytes
            scheduler_sha256 = $script:schedulerFrozenHash
            scheduler_final_observation = $schedulerFinalObservation
            scheduler_hash_mismatches = @($script:schedulerHashMismatches)
            target_indices = $targetIndices
            dispatched_indices = $dispatchedIndices
            started_indices = @($startedIndices | Sort-Object)
            succeeded_indices = @($succeededIndices | Sort-Object)
            failed_indices = @($failedIndices | Sort-Object)
            remaining_indices = $remainingIndices
            scheduler_error = $schedulerError
            finalization_error = $summaryFailure
            events = @($eventRows)
            created_utc = [DateTime]::UtcNow.ToString('o')
        }
        Write-NewJsonFile -Path $summaryPath -Value $emergencySummary
    } catch {
        $fallbackWriteFailure = $_.Exception.Message
        Add-SchedulerError -Message ("batch fallback summary write failed: {0}" -f $fallbackWriteFailure)
        Write-Output ("T68 batch status=FAIL_RUNNERS; summary_finalization_error={0}; fallback_summary_error={1}" -f `
            $summaryFailure, $fallbackWriteFailure)
    }
}
Write-Output ("T68 batch status={0} succeeded={1} failed={2} remaining={3} summary={4}" -f `
    $batchStatus, $succeededIndices.Count, $failedIndices.Count, $remainingIndices.Count, $summaryPath)
if (-not $allTargetSucceeded) { exit 1 }
exit 0
