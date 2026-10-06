[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$task = 'S3-SW04-REPO'
$baseline = 'dfd890e5a8448a07d2d5ee8868b510c9de38ea7b'
$sourceDriverRoot = 'D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\iicps_v3_23'
$componentRelativeRoot = 'XilinxProcessorIPLib/drivers/iicps_v3_24'
$fixedCoreHashes = [ordered]@{
    'src/xiicps_master.c' = '6e002edfd94b80b0dfdd54215c0a536e5fbe06380d7a40f0418b6e52066e3b10'
    'src/xiicps_xfer.c'   = '628414e27016be423ca950af493d522556587e4e04f1eef0e1ce7b10ecffbc1f'
    'src/xiicps_xfer.h'   = '94a72a32a8c1e1a18a0506c998de88c69e9e1cb612da483cec91bccc7ef64a0b'
    'src/xiicps.c'        = 'c60c4afda63d4b6dbe09066ac67ad2883aae04f81d637b38ccd7c0b7f70b58b3'
    'src/xiicps.h'        = 'a96553e979223be1828a781f1bdeb818c61db661e154337b8cf3b4bf10b500ca'
    'src/xiicps_hw.h'     = '0013bcfc147a4c7fc1e60bba7368b5742b638661afb7fdf7efb8dab3223b3d9a'
}
$fixedPatchHashes = [ordered]@{
    'iicps_v3_23_hw_timeout.patch'  = '73083bc57385e8aeabf659db69a1a7c017db2021d5d24e0eeb8dfbdbda77f859'
    'iicps_v3_23_sw_deadline.patch' = '803a34e29009a944b9c88c5defb4c3371feb21606882855231987f6210f6d989'
}
$expectedOverlayFiles = @('src/xiicps_master.c', 'src/xiicps_xfer.c', 'src/xiicps_xfer.h')
$patchNamesInOrder = @('iicps_v3_23_hw_timeout.patch', 'iicps_v3_23_sw_deadline.patch')
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$tmpRoot = [IO.Path]::GetFullPath((Join-Path $repoRoot 'tmp'))
$prepareScript = Join-Path $PSScriptRoot 's3_prepare_iicps_repository.ps1'
$patchRoot = Join-Path $repoRoot 'board\stage3\software\sensor'
$checks = New-Object 'System.Collections.Generic.List[object]'
$prepareLog = New-Object 'System.Collections.Generic.List[string]'
$gitLog = New-Object 'System.Collections.Generic.List[string]'
$runRoot = $null
$result = 'FAIL'

function Add-Check {
    param([string]$Name, [string]$Status, [string]$Detail)
    $checks.Add([pscustomobject]@{ Name = $Name; Result = $Status; Detail = $Detail })
}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    return (Get-FileHash -LiteralPath $LiteralPath -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-NotReparsePoint {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    $item = Get-Item -LiteralPath $LiteralPath -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "测试路径含重解析点：$LiteralPath"
    }
    return $item
}

function Get-FlatFileMap {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [switch]$DriverSubtreesOnly
    )
    [void](Assert-NotReparsePoint -LiteralPath $Root)
    $map = @{}
    $stack = New-Object 'System.Collections.Generic.Stack[string]'
    if ($DriverSubtreesOnly) {
        foreach ($relativeRoot in @('src', 'data')) {
            $absoluteRoot = Join-Path $Root $relativeRoot
            [void](Assert-NotReparsePoint -LiteralPath $absoluteRoot)
            [void]$stack.Push($absoluteRoot)
        }
    }
    else {
        [void]$stack.Push($Root)
    }
    while ($stack.Count -gt 0) {
        $current = $stack.Pop()
        foreach ($entry in @(Get-ChildItem -LiteralPath $current -Force)) {
            if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "测试发现重解析点：$($entry.FullName)"
            }
            if ($entry.PSIsContainer) {
                [void]$stack.Push($entry.FullName)
            }
            else {
                $relative = $entry.FullName.Substring($Root.TrimEnd('\').Length + 1).Replace('\', '/')
                $map[$relative] = [pscustomobject]@{
                    FullName = $entry.FullName
                    Length = [long]$entry.Length
                    SHA256 = Get-Sha256 -LiteralPath $entry.FullName
                }
            }
        }
    }
    return $map
}

function Copy-SourceTree {
    param(
        [Parameter(Mandatory = $true)][string]$SourceRoot,
        [Parameter(Mandatory = $true)][string]$DestinationRoot
    )
    foreach ($requiredRoot in @('src', 'data')) {
        $sourcePath = Join-Path $SourceRoot $requiredRoot
        [void](Assert-NotReparsePoint -LiteralPath $sourcePath)
        [void][IO.Directory]::CreateDirectory((Join-Path $DestinationRoot $requiredRoot))
    }
    $stack = New-Object 'System.Collections.Generic.Stack[string]'
    foreach ($requiredRoot in @('src', 'data')) {
        [void]$stack.Push((Join-Path $SourceRoot $requiredRoot))
    }
    while ($stack.Count -gt 0) {
        $current = $stack.Pop()
        foreach ($entry in @(Get-ChildItem -LiteralPath $current -Force)) {
            if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "独立重放源树含重解析点：$($entry.FullName)"
            }
            $relative = $entry.FullName.Substring($SourceRoot.TrimEnd('\').Length + 1)
            $destination = Join-Path $DestinationRoot $relative
            if ($entry.PSIsContainer) {
                [void][IO.Directory]::CreateDirectory($destination)
                [void]$stack.Push($entry.FullName)
            }
            else {
                [IO.File]::Copy($entry.FullName, $destination, $false)
                $copiedAttributes = [IO.File]::GetAttributes($destination)
                if (($copiedAttributes -band [IO.FileAttributes]::ReadOnly) -ne 0) {
                    $writableAttributes = [IO.FileAttributes]([int]$copiedAttributes -band (-bnot [int][IO.FileAttributes]::ReadOnly))
                    [IO.File]::SetAttributes($destination, $writableAttributes)
                }
            }
        }
    }
}

function Invoke-SourceRootReparsePointTest {
    param(
        [Parameter(Mandatory = $true)][string]$SourceRootName,
        [Parameter(Mandatory = $true)][string]$SourceDriverRoot,
        [Parameter(Mandatory = $true)][string]$ParentDirectory,
        [Parameter(Mandatory = $true)][string]$PreparerScript,
        [Parameter(Mandatory = $true)][string]$PowerShellExecutable
    )

    if ($SourceRootName -notin @('src', 'data')) {
        throw "不支持的重解析点测试目录：$SourceRootName"
    }

    $fixtureRoot = Join-Path $ParentDirectory ("reparse_root_$SourceRootName")
    [void][IO.Directory]::CreateDirectory($fixtureRoot)
    [void](Assert-NotReparsePoint -LiteralPath $fixtureRoot)

    $fixtureDriver = Join-Path $fixtureRoot 'vendor\iicps_v3_23'
    [void][IO.Directory]::CreateDirectory((Split-Path -Parent $fixtureDriver))
    Copy-SourceTree -SourceRoot $SourceDriverRoot -DestinationRoot $fixtureDriver

    $linkedDirectory = Join-Path $fixtureDriver $SourceRootName
    $parkedDirectory = Join-Path $fixtureRoot ("parked_$SourceRootName")
    Move-Item -LiteralPath $linkedDirectory -Destination $parkedDirectory
    $junctionTarget = Join-Path $SourceDriverRoot $SourceRootName
    [void](New-Item -ItemType Junction -Path $linkedDirectory -Target $junctionTarget -ErrorAction Stop)
    [void](Assert-NotReparsePoint -LiteralPath $fixtureDriver)
    $junctionItem = Get-Item -LiteralPath $linkedDirectory -Force
    if (($junctionItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -eq 0) {
        throw "测试夹具没有创建出预期 junction：$linkedDirectory"
    }

    $fixtureRepo = Join-Path $fixtureRoot 'mini_repo'
    $fixtureScripts = Join-Path $fixtureRepo 'scripts'
    $fixturePatchRoot = Join-Path $fixtureRepo 'board\stage3\software\sensor'
    $fixtureTmp = Join-Path $fixtureRepo 'tmp'
    [void][IO.Directory]::CreateDirectory($fixtureScripts)
    [void][IO.Directory]::CreateDirectory($fixturePatchRoot)
    [void][IO.Directory]::CreateDirectory($fixtureTmp)

    $sourceText = [IO.File]::ReadAllText($PreparerScript)
    $sourceVariable = '$' + 'sourceDriverRoot'
    $sourceDeclaration = $sourceVariable + " = '$SourceDriverRoot'"
    $fixtureSourceLiteral = "'" + $fixtureDriver.Replace("'", "''") + "'"
    $fixtureDeclaration = $sourceVariable + ' = ' + $fixtureSourceLiteral
    if ($sourceText.IndexOf($sourceDeclaration, [StringComparison]::Ordinal) -lt 0 -or
        $sourceText.LastIndexOf($sourceDeclaration, [StringComparison]::Ordinal) -ne
        $sourceText.IndexOf($sourceDeclaration, [StringComparison]::Ordinal)) {
        throw '隔离测试副本无法唯一定位固定源根声明。'
    }
    $fixtureScriptText = $sourceText.Replace($sourceDeclaration, $fixtureDeclaration)
    $fixtureScript = Join-Path $fixtureScripts 's3_prepare_iicps_repository.ps1'
    [IO.File]::WriteAllText($fixtureScript, $fixtureScriptText, [System.Text.UTF8Encoding]::new($true))

    foreach ($patchName in $patchNamesInOrder) {
        $sourcePatch = Join-Path $patchRoot $patchName
        $fixturePatch = Join-Path $fixturePatchRoot $patchName
        [IO.File]::Copy($sourcePatch, $fixturePatch, $false)
    }

    $candidatePath = Join-Path $fixtureTmp 'reparse_candidate'
    $result = Invoke-ExpectedFailure -PowerShellExecutable $PowerShellExecutable -Script $fixtureScript -Target $candidatePath
    $combinedOutput = $result.Output -join [Environment]::NewLine
    if ($result.ExitCode -eq 0 -or
        $combinedOutput -notmatch '拒绝使用重解析点路径' -or
        [IO.Directory]::Exists($candidatePath) -or [IO.File]::Exists($candidatePath)) {
        throw "准备器未在 $SourceRootName 顶层重解析点处安全失败：exit=$($result.ExitCode)；$combinedOutput"
    }

    return "exit=$($result.ExitCode)，$SourceRootName junction 在输出目录创建前被拒绝。"
}

function Invoke-ExpectedFailure {
    param(
        [Parameter(Mandatory = $true)][string]$PowerShellExecutable,
        [Parameter(Mandatory = $true)][string]$Script,
        [Parameter(Mandatory = $true)][string]$Target
    )
    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = & $PowerShellExecutable -NoProfile -ExecutionPolicy Bypass -File $Script -OutputDirectory $Target 2>&1
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    return [pscustomobject]@{ ExitCode = $exitCode; Output = @($output | ForEach-Object { [string]$_ }) }
}

try {
    if (-not (Test-Path -LiteralPath $repoRoot -PathType Container) -or
        -not (Test-Path -LiteralPath $tmpRoot -PathType Container)) {
        throw '项目根目录或项目 tmp 目录不存在。'
    }
    [void](Assert-NotReparsePoint -LiteralPath $repoRoot)
    [void](Assert-NotReparsePoint -LiteralPath $tmpRoot)
    if (-not (Test-Path -LiteralPath $sourceDriverRoot -PathType Container)) {
        throw "固定 Vitis 源目录不存在：$sourceDriverRoot"
    }
    if (-not (Test-Path -LiteralPath $prepareScript -PathType Leaf)) {
        throw "缺少准备脚本：$prepareScript"
    }

    $gitCommand = Get-Command git.exe -ErrorAction Stop
    $gitExecutable = $gitCommand.Source
    & $gitExecutable merge-base --is-ancestor $baseline HEAD 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "固定基线不是当前 HEAD 的祖先：$baseline"
    }
    Add-Check '固定基线祖先关系' 'PASS' $baseline

    foreach ($relativePath in $fixedCoreHashes.Keys) {
        $sourcePath = Join-Path $sourceDriverRoot ($relativePath.Replace('/', '\'))
        $actualHash = Get-Sha256 -LiteralPath $sourcePath
        if ($actualHash -ne $fixedCoreHashes[$relativePath]) {
            throw "原厂核心源哈希不匹配：$relativePath：$actualHash"
        }
    }
    Add-Check '六个固定原厂核心 SHA-256' 'PASS' '六个源文件逐一匹配任务卡固定值。'

    foreach ($patchName in $patchNamesInOrder) {
        $patchPath = Join-Path $patchRoot $patchName
        $actualHash = Get-Sha256 -LiteralPath $patchPath
        if ($actualHash -ne $fixedPatchHashes[$patchName]) {
            throw "仓库补丁哈希不匹配：$patchName：$actualHash"
        }
    }
    Add-Check '两份 overlay 固定 SHA-256' 'PASS' '硬件 TO 在前，软件期限在后。'

    $runName = 's3_iicps_repository_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '_' + [Guid]::NewGuid().ToString('N')
    $runRoot = Join-Path $tmpRoot $runName
    if (Test-Path -LiteralPath $runRoot) { throw "唯一测试目录意外已存在：$runRoot" }
    [void][IO.Directory]::CreateDirectory($runRoot)
    [void](Assert-NotReparsePoint -LiteralPath $runRoot)
    $packageRoot = Join-Path $runRoot 'repository'
    $componentPrefix = "$componentRelativeRoot/"
    $componentRoot = Join-Path $packageRoot ($componentRelativeRoot.Replace('/', '\'))

    $powershellCommand = Get-Command powershell.exe -ErrorAction Stop
    $powershellExecutable = $powershellCommand.Source
    $psVersionOutput = & $powershellExecutable -NoProfile -Command '$PSVersionTable.PSVersion.ToString()' 2>&1
    $psVersionText = ($psVersionOutput -join '').Trim()
    if ($LASTEXITCODE -ne 0 -or $psVersionText -notmatch '^5\.1\.') {
        throw "准备器必须使用 Windows PowerShell 5.1；检测结果：$psVersionText"
    }
    Add-Check 'Windows PowerShell 5.1 子进程' 'PASS' $psVersionText

    foreach ($requiredRoot in @('src', 'data')) {
        $reparseDetail = Invoke-SourceRootReparsePointTest `
            -SourceRootName $requiredRoot `
            -SourceDriverRoot $sourceDriverRoot `
            -ParentDirectory $runRoot `
            -PreparerScript $prepareScript `
            -PowerShellExecutable $powershellExecutable
        Add-Check "源驱动顶层 $requiredRoot junction 拒绝" 'PASS' $reparseDetail
    }

    $prepareOutput = & $powershellExecutable -NoProfile -ExecutionPolicy Bypass -File $prepareScript -OutputDirectory $packageRoot 2>&1
    $prepareExitCode = $LASTEXITCODE
    foreach ($line in $prepareOutput) { $prepareLog.Add([string]$line) }
    if ($prepareExitCode -ne 0) {
        throw "准备器退出码为 $prepareExitCode：$($prepareOutput -join [Environment]::NewLine)"
    }
    Add-Check '准备器调用' 'PASS' "exit=$prepareExitCode; $packageRoot"

    foreach ($relativeDirectory in @('src', 'data')) {
        if (-not (Test-Path -LiteralPath (Join-Path $componentRoot $relativeDirectory) -PathType Container)) {
            throw "候选包缺少目录：$relativeDirectory"
        }
    }
    $mddPath = Join-Path $componentRoot 'data\iicps.mdd'
    $mddText = [IO.File]::ReadAllText($mddPath)
    if ($mddText -notmatch '(?m)^  OPTION NAME = iicps;\r?$' -or
        $mddText -notmatch '(?m)^  OPTION VERSION = 3\.24;\r?$') {
        throw '候选 MDD 的 driver name 或 VERSION 不正确。'
    }
    Add-Check '候选目录与 MDD 标识/版本' 'PASS' "$componentRelativeRoot; iicps 3.24"

    $manifestPath = Join-Path $packageRoot 'source_manifest.json'
    if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { throw '候选包缺少 source_manifest.json。' }
    $manifest = [IO.File]::ReadAllText($manifestPath) | ConvertFrom-Json
    if ($manifest.task -ne $task -or $manifest.driver_name -ne 'iicps' -or
        $manifest.source_driver_version -ne '3.23' -or $manifest.output_driver_version -ne '3.24' -or
        $manifest.output_component_root -ne $componentRelativeRoot -or
        $manifest.source_driver_root -ne $sourceDriverRoot) {
        throw 'manifest 的任务、原厂根、组件路径或版本字段与固定预期不一致。'
    }
    if ($manifest.patches.Count -ne 2 -or
        $manifest.patches[0].Sequence -ne 1 -or $manifest.patches[0].File -ne $patchNamesInOrder[0] -or
        $manifest.patches[1].Sequence -ne 2 -or $manifest.patches[1].File -ne $patchNamesInOrder[1] -or
        $manifest.patches[0].CheckExitCode -ne 0 -or $manifest.patches[0].ApplyExitCode -ne 0 -or
        $manifest.patches[1].CheckExitCode -ne 0 -or $manifest.patches[1].ApplyExitCode -ne 0) {
        throw 'manifest 未证明补丁按指定顺序完成 check/apply。'
    }
    foreach ($patchName in $patchNamesInOrder) {
        $patchEntry = @($manifest.patches | Where-Object { $_.File -eq $patchName })[0]
        if ($patchEntry.SHA256 -ne $fixedPatchHashes[$patchName]) { throw "manifest 补丁 SHA 不匹配：$patchName" }
    }
    if ($manifest.source_integrity.Count -ne $fixedCoreHashes.Count) {
        throw 'manifest 核心源完整性清单数量不正确。'
    }
    foreach ($relativePath in $fixedCoreHashes.Keys) {
        $sourceIntegrityEntry = @($manifest.source_integrity | Where-Object { $_.Path -eq $relativePath })[0]
        $actualHash = Get-Sha256 -LiteralPath (Join-Path $sourceDriverRoot ($relativePath.Replace('/', '\')))
        if ($sourceIntegrityEntry.ExpectedSHA256 -ne $fixedCoreHashes[$relativePath] -or
            $sourceIntegrityEntry.ActualSHA256 -ne $actualHash) {
            throw "manifest 核心源原件哈希与实际文件不符：$relativePath"
        }
    }
    $manifestOverlaySet = (@($manifest.overlay_modified_files | Sort-Object) -join [Environment]::NewLine)
    $expectedOverlaySet = (@($expectedOverlayFiles | Sort-Object) -join [Environment]::NewLine)
    if ($manifestOverlaySet -ne $expectedOverlaySet) { throw 'manifest 的 overlay 修改集合不是精确三文件。' }
    if ($manifest.metadata_only_change.Path -ne "$componentRelativeRoot/data/iicps.mdd" -or
        $manifest.metadata_only_change.Field -ne 'OPTION VERSION' -or
        $manifest.metadata_only_change.From -ne '3.23' -or $manifest.metadata_only_change.To -ne '3.24' -or
        $manifest.metadata_only_change.ByteChangeCount -ne 1) {
        throw 'manifest 对 MDD 元数据改动的声明不正确。'
    }
    if ([string]::IsNullOrWhiteSpace([string]$manifest.tool_versions.PowerShell) -or
        [string]::IsNullOrWhiteSpace([string]$manifest.tool_versions.Git) -or
        $manifest.steps.Count -lt 5 -or $manifest.limitations.Count -lt 4) {
        throw 'manifest 缺少工具版本、步骤或限制信息。'
    }
    Add-Check 'manifest 字段、补丁序、工具版本与限制' 'PASS' 'manifest JSON 可解析且与实际任务常量相符。'

    $sourceMap = Get-FlatFileMap -Root $sourceDriverRoot -DriverSubtreesOnly
    $packageMap = Get-FlatFileMap -Root $packageRoot
    $packagePaths = @($packageMap.Keys | Sort-Object)
    $manifestSourcePaths = (@($manifest.original_files | ForEach-Object { $_.Path } | Sort-Object) -join [Environment]::NewLine)
    $actualSourcePaths = (@($sourceMap.Keys | Sort-Object) -join [Environment]::NewLine)
    if ($manifest.original_files.Count -ne $sourceMap.Count -or $manifestSourcePaths -ne $actualSourcePaths) {
        throw 'manifest 原始文件清单与固定源树路径集合/数量不一致。'
    }
    if ($packagePaths.Count -ne ($sourceMap.Count + 1) -or
        -not $packageMap.ContainsKey('source_manifest.json') -or
        $manifest.output_files.Count -ne $sourceMap.Count) {
        throw '候选包文件数量、manifest 清单或自排除 manifest 约定不一致。'
    }
    $manifestOriginalMap = @{}
    foreach ($entry in $manifest.original_files) { $manifestOriginalMap[$entry.Path] = $entry }
    foreach ($relativePath in $sourceMap.Keys) {
        $sourceEntry = $sourceMap[$relativePath]
        $manifestEntry = $manifestOriginalMap[$relativePath]
        if ($manifestEntry.SHA256 -ne $sourceEntry.SHA256 -or $manifestEntry.Length -ne $sourceEntry.Length) {
            throw "manifest 原件哈希/长度与实际 Vitis 源不符：$relativePath"
        }
    }
    $manifestOutputMap = @{}
    foreach ($entry in $manifest.output_files) { $manifestOutputMap[$entry.Path] = $entry }
    foreach ($relativePath in $sourceMap.Keys) {
        $candidateRelative = "$componentPrefix$relativePath"
        if (-not $packageMap.ContainsKey($candidateRelative) -or -not $manifestOutputMap.ContainsKey($candidateRelative)) {
            throw "候选包或 manifest 缺少输出文件：$candidateRelative"
        }
        $candidateEntry = $packageMap[$candidateRelative]
        $manifestEntry = $manifestOutputMap[$candidateRelative]
        if ($candidateEntry.SHA256 -ne $manifestEntry.SHA256 -or $candidateEntry.Length -ne $manifestEntry.Length) {
            throw "manifest 输出 SHA/长度与实际候选文件不一致：$candidateRelative"
        }
    }
    Add-Check 'manifest 原件/输出逐文件 SHA 与长度' 'PASS' "$($sourceMap.Count) 个源文件，候选另含 manifest。"

    $changedSourcePaths = New-Object 'System.Collections.Generic.List[string]'
    foreach ($relativePath in $sourceMap.Keys) {
        $candidateRelative = "$componentPrefix$relativePath"
        if ($sourceMap[$relativePath].SHA256 -ne $packageMap[$candidateRelative].SHA256) {
            $changedSourcePaths.Add($relativePath)
        }
    }
    $expectedChangedSet = (@($expectedOverlayFiles + @('data/iicps.mdd') | Sort-Object -Unique) -join [Environment]::NewLine)
    $actualChangedSet = (@($changedSourcePaths | Sort-Object -Unique) -join [Environment]::NewLine)
    if ($actualChangedSet -ne $expectedChangedSet) {
        throw "复制源变更集合超出三个 overlay 源和 MDD：$actualChangedSet"
    }
    Add-Check 'fail-closed 源文件变更范围' 'PASS' ($actualChangedSet -replace [regex]::Escape([Environment]::NewLine), ', ')

    $originalMddBytes = [IO.File]::ReadAllBytes($sourceMap['data/iicps.mdd'].FullName)
    $candidateMddBytes = [IO.File]::ReadAllBytes($packageMap[($componentPrefix + 'data/iicps.mdd')].FullName)
    if ($originalMddBytes.Length -ne $candidateMddBytes.Length) { throw '候选 MDD 长度与原件不同。' }
    $mddDifferenceCount = 0
    for ($index = 0; $index -lt $originalMddBytes.Length; $index++) {
        if ($originalMddBytes[$index] -ne $candidateMddBytes[$index]) { $mddDifferenceCount++ }
    }
    if ($mddDifferenceCount -ne 1) { throw "MDD 除 VERSION 单字节外还存在差异：$mddDifferenceCount 个字节。" }
    Add-Check 'MDD 仅 VERSION 单字节提升' 'PASS' '3.23 → 3.24，文件其他字节不变。'

    $verificationRoot = Join-Path $runRoot 'independent_replay'
    [void][IO.Directory]::CreateDirectory($verificationRoot)
    $verificationDriver = Join-Path $verificationRoot ($componentRelativeRoot.Replace('/', '\'))
    [void][IO.Directory]::CreateDirectory($verificationDriver)
    Copy-SourceTree -SourceRoot $sourceDriverRoot -DestinationRoot $verificationDriver
    $verificationMdd = Join-Path $verificationDriver 'data\iicps.mdd'
    $mddBytes = [IO.File]::ReadAllBytes($verificationMdd)
    $mddText = [Text.Encoding]::ASCII.GetString($mddBytes)
    $versionMatches = [regex]::Matches($mddText, '(?m)^  OPTION VERSION = 3\.23;\r?$')
    if ($versionMatches.Count -ne 1) { throw '独立重放原 MDD VERSION 项不唯一。' }
    $versionByteOffset = $versionMatches[0].Index + $versionMatches[0].Length - 2
    if ($mddBytes[$versionByteOffset] -ne [byte][char]'3') { throw '独立重放 MDD 版本字节位置错误。' }
    $mddBytes[$versionByteOffset] = [byte][char]'4'
    [IO.File]::WriteAllBytes($verificationMdd, $mddBytes)

    foreach ($patchName in $patchNamesInOrder) {
        $patchPath = Join-Path $patchRoot $patchName
        $verificationPrefix = [IO.Path]::GetFullPath($repoRoot).TrimEnd('\') + '\'
        $verificationFull = [IO.Path]::GetFullPath($verificationDriver).TrimEnd('\')
        if (-not $verificationFull.StartsWith($verificationPrefix, [StringComparison]::OrdinalIgnoreCase)) {
            throw "独立重放目标不在项目仓库内：$verificationFull"
        }
        $relativeApplyDirectory = $verificationFull.Substring($verificationPrefix.Length).Replace('\', '/')
        Push-Location -LiteralPath $repoRoot
        try {
            $checkOutput = & $gitExecutable -c core.autocrlf=false apply --directory=$relativeApplyDirectory --check $patchPath 2>&1
            $checkCode = $LASTEXITCODE
            foreach ($line in $checkOutput) { $gitLog.Add("$patchName check: $line") }
            if ($checkCode -ne 0) { throw "独立重放 git apply --check 失败：$patchName；$($checkOutput -join ' ')" }
            $applyOutput = & $gitExecutable -c core.autocrlf=false apply --directory=$relativeApplyDirectory $patchPath 2>&1
            $applyCode = $LASTEXITCODE
            foreach ($line in $applyOutput) { $gitLog.Add("$patchName apply: $line") }
            if ($applyCode -ne 0) { throw "独立重放 git apply 失败：$patchName；$($applyOutput -join ' ')" }
        }
        finally {
            Pop-Location
        }
    }

    $independentMap = Get-FlatFileMap -Root $verificationDriver
    if ($independentMap.Count -ne $sourceMap.Count -or
        (@($independentMap.Keys | Sort-Object) -join [Environment]::NewLine) -ne
        (@($sourceMap.Keys | Sort-Object) -join [Environment]::NewLine)) {
        throw '独立重放副本出现额外或缺失源文件。'
    }
    $independentChanged = New-Object 'System.Collections.Generic.List[string]'
    foreach ($relativePath in $sourceMap.Keys) {
        if ($sourceMap[$relativePath].SHA256 -ne $independentMap[$relativePath].SHA256) {
            $independentChanged.Add($relativePath)
        }
        $candidateRelative = "$componentPrefix$relativePath"
        if ($independentMap[$relativePath].SHA256 -ne $packageMap[$candidateRelative].SHA256) {
            throw "独立顺序重放与候选包字节不一致：$relativePath"
        }
    }
    $independentChangedSet = (@($independentChanged | Sort-Object -Unique) -join [Environment]::NewLine)
    if ($independentChangedSet -ne $expectedChangedSet) { throw "独立重放变更集合错误：$independentChangedSet" }
    Add-Check '隔离目录补丁顺序 check/apply 与字节对照' 'PASS' '两份补丁均在独立副本通过 check/apply，源与候选逐文件一致。'

    $beforeExistingCheck = Get-FlatFileMap -Root $packageRoot
    $existingResult = Invoke-ExpectedFailure -PowerShellExecutable $powershellExecutable -Script $prepareScript -Target $packageRoot
    if ($existingResult.ExitCode -eq 0) { throw '准备器接受了已存在输出目录。' }
    $afterExistingCheck = Get-FlatFileMap -Root $packageRoot
    foreach ($path in $beforeExistingCheck.Keys) {
        if (-not $afterExistingCheck.ContainsKey($path) -or
            $beforeExistingCheck[$path].SHA256 -ne $afterExistingCheck[$path].SHA256) {
            throw "已存在目标拒绝测试造成候选包变化：$path"
        }
    }
    Add-Check '已存在输出目标拒绝覆盖' 'PASS' "exit=$($existingResult.ExitCode)，候选文件哈希保持不变。"

    $outsideTarget = Join-Path $repoRoot ('outside_tmp_s3_repo_' + [Guid]::NewGuid().ToString('N'))
    $outsideResult = Invoke-ExpectedFailure -PowerShellExecutable $powershellExecutable -Script $prepareScript -Target $outsideTarget
    if ($outsideResult.ExitCode -eq 0 -or (Test-Path -LiteralPath $outsideTarget)) {
        throw '准备器未拒绝项目 tmp 外的新目标，或产生了越界目录。'
    }
    Add-Check '项目 tmp 外路径拒绝' 'PASS' "exit=$($outsideResult.ExitCode)，未创建目标。"

    $tmpRootResult = Invoke-ExpectedFailure -PowerShellExecutable $powershellExecutable -Script $prepareScript -Target $tmpRoot
    if ($tmpRootResult.ExitCode -eq 0) { throw '准备器接受了 tmp 根目录作为输出目标。' }
    Add-Check 'tmp 根本身拒绝作为目标' 'PASS' "exit=$($tmpRootResult.ExitCode)"

    foreach ($relativePath in $fixedCoreHashes.Keys) {
        $sourcePath = Join-Path $sourceDriverRoot ($relativePath.Replace('/', '\'))
        $actualHash = Get-Sha256 -LiteralPath $sourcePath
        if ($actualHash -ne $fixedCoreHashes[$relativePath]) {
            throw "测试结束时原厂源 SHA 发生变化：$relativePath：$actualHash"
        }
    }
    Add-Check '结束时原厂六文件 SHA 未变化' 'PASS' '只读安装源前后固定哈希一致。'
    $result = 'PASS'
}
catch {
    $result = 'FAIL'
    Add-Check '异常' 'FAIL' $_.Exception.Message
}
finally {
    if ($null -ne $runRoot -and [IO.Directory]::Exists($runRoot)) {
        $summary = [ordered]@{
            task = $task
            result = $result
            run_directory = $runRoot
            evidence_retained = $true
            checks = $checks.ToArray()
            preparation_output = $prepareLog.ToArray()
            independent_git_output = $gitLog.ToArray()
            generated_package = Join-Path $runRoot 'repository'
        }
        $summaryPath = Join-Path $runRoot 'summary.json'
        [IO.File]::WriteAllText($summaryPath, (ConvertTo-Json -InputObject $summary -Depth 12) + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
        Write-Output "结果：$result"
        Write-Output "证据：$summaryPath"
        Write-Output "候选包：$(Join-Path $runRoot 'repository')"
    }
}

if ($result -ne 'PASS') { exit 1 }
exit 0
