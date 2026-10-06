[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$OutputDirectory
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptVersion = '1.0.0'
$sourceDriverRoot = 'D:\Xilinx\2026.1\Vitis\data\embeddedsw\XilinxProcessorIPLib\drivers\iicps_v3_23'
$componentRelativeRoot = 'XilinxProcessorIPLib/drivers/iicps_v3_24'
$expectedCoreHashes = [ordered]@{
    'src/xiicps_master.c' = '6e002edfd94b80b0dfdd54215c0a536e5fbe06380d7a40f0418b6e52066e3b10'
    'src/xiicps_xfer.c'   = '628414e27016be423ca950af493d522556587e4e04f1eef0e1ce7b10ecffbc1f'
    'src/xiicps_xfer.h'   = '94a72a32a8c1e1a18a0506c998de88c69e9e1cb612da483cec91bccc7ef64a0b'
    'src/xiicps.c'        = 'c60c4afda63d4b6dbe09066ac67ad2883aae04f81d637b38ccd7c0b7f70b58b3'
    'src/xiicps.h'        = 'a96553e979223be1828a781f1bdeb818c61db661e154337b8cf3b4bf10b500ca'
    'src/xiicps_hw.h'     = '0013bcfc147a4c7fc1e60bba7368b5742b638661afb7fdf7efb8dab3223b3d9a'
}
$expectedPatchHashes = [ordered]@{
    'iicps_v3_23_hw_timeout.patch'    = '73083bc57385e8aeabf659db69a1a7c017db2021d5d24e0eeb8dfbdbda77f859'
    'iicps_v3_23_sw_deadline.patch'   = '803a34e29009a944b9c88c5defb4c3371feb21606882855231987f6210f6d989'
}
$expectedOverlayFiles = @(
    'src/xiicps_master.c',
    'src/xiicps_xfer.c',
    'src/xiicps_xfer.h'
)
$verifiedCoreHashes = @{}

function Get-Sha256 {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    return (Get-FileHash -LiteralPath $LiteralPath -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Assert-NotReparsePoint {
    param([Parameter(Mandatory = $true)][string]$LiteralPath)
    $item = Get-Item -LiteralPath $LiteralPath -Force
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "拒绝使用重解析点路径：$LiteralPath"
    }
    return $item
}

function Get-TreeInventory {
    param([Parameter(Mandatory = $true)][string]$Root)

    $rootItem = Assert-NotReparsePoint -LiteralPath $Root
    if (-not $rootItem.PSIsContainer) {
        throw "源驱动根不是目录：$Root"
    }

    $files = New-Object 'System.Collections.Generic.List[object]'
    $directories = New-Object 'System.Collections.Generic.List[string]'
    $pending = New-Object 'System.Collections.Generic.Stack[string]'
    foreach ($relativeRoot in @('src', 'data')) {
        $absoluteRoot = Join-Path $Root $relativeRoot
        if (-not (Test-Path -LiteralPath $absoluteRoot -PathType Container)) {
            throw "缺少驱动必需目录：$absoluteRoot"
        }
        $requiredRootItem = Assert-NotReparsePoint -LiteralPath $absoluteRoot
        if (-not $requiredRootItem.PSIsContainer) {
            throw "驱动必需路径不是目录：$absoluteRoot"
        }
        [void]$pending.Push($absoluteRoot)
        $directories.Add($relativeRoot)
    }

    while ($pending.Count -gt 0) {
        $current = $pending.Pop()
        foreach ($entry in @(Get-ChildItem -LiteralPath $current -Force)) {
            if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "驱动源含重解析点，拒绝跟随：$($entry.FullName)"
            }
            $relative = $entry.FullName.Substring($Root.TrimEnd('\').Length + 1).Replace('\', '/')
            if ($entry.PSIsContainer) {
                $directories.Add($relative)
                [void]$pending.Push($entry.FullName)
            }
            else {
                $files.Add([pscustomobject]@{
                    RelativePath = $relative
                    FullName = $entry.FullName
                    Length = [long]$entry.Length
                    SHA256 = Get-Sha256 -LiteralPath $entry.FullName
                })
            }
        }
    }

    return [pscustomobject]@{
        Files = @($files | Sort-Object -Property RelativePath)
        Directories = @($directories | Sort-Object -Property { ($_ -split '/').Count }, { $_ })
    }
}

function Assert-OutputPathSafe {
    param(
        [Parameter(Mandatory = $true)][string]$RequestedPath,
        [Parameter(Mandatory = $true)][string]$RepositoryRoot
    )

    if (-not [IO.Path]::IsPathRooted($RequestedPath)) {
        throw '输出目录必须是绝对路径。'
    }
    if ($RequestedPath -match '(^|[\\/])\.{1,2}([\\/]|$)' -or $RequestedPath -ne $RequestedPath.Trim()) {
        throw '输出目录不得包含点路径段或首尾空白。'
    }

    $repoRootFull = [IO.Path]::GetFullPath($RepositoryRoot).TrimEnd('\')
    $tmpRoot = [IO.Path]::GetFullPath((Join-Path $repoRootFull 'tmp')).TrimEnd('\')
    $outputFull = [IO.Path]::GetFullPath($RequestedPath).TrimEnd('\')
    $tmpPrefix = $tmpRoot + '\'
    if (-not $outputFull.StartsWith($tmpPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "输出目录必须位于项目 tmp 子目录内：$tmpRoot"
    }

    [void](Assert-NotReparsePoint -LiteralPath $repoRootFull)
    [void](Assert-NotReparsePoint -LiteralPath $tmpRoot)

    if ((Test-Path -LiteralPath $outputFull) -or [IO.File]::Exists($outputFull) -or [IO.Directory]::Exists($outputFull)) {
        throw "输出目标已存在，拒绝覆盖：$outputFull"
    }

    $relative = $outputFull.Substring($tmpPrefix.Length)
    $segments = @($relative -split '[\\/]')
    if ($segments.Count -lt 1 -or @($segments | Where-Object { $_ -eq '' -or $_ -eq '.' -or $_ -eq '..' -or $_.EndsWith('.') -or $_.EndsWith(' ') }).Count -gt 0) {
        throw "输出目录包含不安全路径段：$outputFull"
    }

    $cursor = $tmpRoot
    for ($index = 0; $index -lt ($segments.Count - 1); $index++) {
        $cursor = Join-Path $cursor $segments[$index]
        if (-not (Test-Path -LiteralPath $cursor -PathType Container)) {
            throw "输出目录父目录必须预先存在：$cursor"
        }
        [void](Assert-NotReparsePoint -LiteralPath $cursor)
    }

    return $outputFull
}

function Invoke-GitPatch {
    param(
        [Parameter(Mandatory = $true)][string]$GitExecutable,
        [Parameter(Mandatory = $true)][string]$DriverDirectory,
        [Parameter(Mandatory = $true)][string]$PatchPath,
        [Parameter(Mandatory = $true)][ValidateSet('check', 'apply')][string]$Operation
    )

    $driverFullPath = [IO.Path]::GetFullPath($DriverDirectory).TrimEnd('\')
    $repoFullPath = [IO.Path]::GetFullPath($script:repositoryRoot).TrimEnd('\')
    $repoPrefix = $repoFullPath + '\'
    if (-not $driverFullPath.StartsWith($repoPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "补丁目标不在项目仓库内：$driverFullPath"
    }
    $relativeApplyDirectory = $driverFullPath.Substring($repoPrefix.Length).Replace('\', '/')
    Push-Location -LiteralPath $repoFullPath
    try {
        if ($Operation -eq 'check') {
            $output = & $GitExecutable -c core.autocrlf=false apply --directory=$relativeApplyDirectory --check $PatchPath 2>&1
        }
        else {
            $output = & $GitExecutable -c core.autocrlf=false apply --directory=$relativeApplyDirectory $PatchPath 2>&1
        }
        $exitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }
    if ($exitCode -ne 0) {
        throw "git apply $Operation 失败（退出码 $exitCode）：$($output -join [Environment]::NewLine)"
    }
    return [pscustomobject]@{ Operation = $Operation; ExitCode = $exitCode; Output = @($output | ForEach-Object { [string]$_ }) }
}

function Update-MddVersionByte {
    param([Parameter(Mandatory = $true)][string]$MddPath)

    $bytes = [IO.File]::ReadAllBytes($MddPath)
    $text = [Text.Encoding]::ASCII.GetString($bytes)
    $matches = [regex]::Matches($text, '(?m)^  OPTION VERSION = 3\.23;\r?$')
    if ($matches.Count -ne 1) {
        throw "MDD 中必须且只能有一条精确的 3.23 VERSION 项：$MddPath"
    }
    $versionToken = [regex]::Matches($text, '(?m)^  OPTION VERSION = 3\.\d+;\r?$')
    if ($versionToken.Count -ne 1) {
        throw "MDD VERSION 元数据不唯一，拒绝修改：$MddPath"
    }

    $match = $matches[0]
    $lastVersionDigitOffset = $match.Index + $match.Length - 2
    if ($bytes[$lastVersionDigitOffset] -ne [byte][char]'3') {
        throw 'MDD VERSION 字节位置与预期不一致。'
    }
    $bytes[$lastVersionDigitOffset] = [byte][char]'4'
    [IO.File]::WriteAllBytes($MddPath, $bytes)
}

function Assert-MddOnlyVersionBump {
    param(
        [Parameter(Mandatory = $true)][byte[]]$OriginalBytes,
        [Parameter(Mandatory = $true)][byte[]]$CandidateBytes
    )
    if ($OriginalBytes.Length -ne $CandidateBytes.Length) {
        throw 'MDD 版本修改改变了文件长度。'
    }
    $differentOffsets = New-Object 'System.Collections.Generic.List[int]'
    for ($index = 0; $index -lt $OriginalBytes.Length; $index++) {
        if ($OriginalBytes[$index] -ne $CandidateBytes[$index]) {
            $differentOffsets.Add($index)
        }
    }
    if ($differentOffsets.Count -ne 1) {
        throw "MDD 必须只改变一个 VERSION 字节；实际差异字节数：$($differentOffsets.Count)"
    }
    $originalText = [Text.Encoding]::ASCII.GetString($OriginalBytes)
    $candidateText = [Text.Encoding]::ASCII.GetString($CandidateBytes)
    if ($originalText -notmatch '(?m)^  OPTION VERSION = 3\.23;\r?$' -or
        $candidateText -notmatch '(?m)^  OPTION VERSION = 3\.24;\r?$') {
        throw 'MDD 原始或输出 VERSION 不符合 3.23 → 3.24 的精确变更。'
    }
}

try {
    $repositoryRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
    $script:repositoryRoot = $repositoryRoot
    $outputFull = Assert-OutputPathSafe -RequestedPath $OutputDirectory -RepositoryRoot $repositoryRoot

    if (-not (Test-Path -LiteralPath $sourceDriverRoot -PathType Container)) {
        throw "固定 Vitis 驱动源目录不存在：$sourceDriverRoot"
    }

    # 先按任务卡逐项校验六个核心厂商原件，失败时不创建输出目录。
    foreach ($relativePath in $expectedCoreHashes.Keys) {
        $sourcePath = Join-Path $sourceDriverRoot ($relativePath.Replace('/', '\'))
        if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
            throw "缺少固定核心源文件：$sourcePath"
        }
        $actualHash = Get-Sha256 -LiteralPath $sourcePath
        if ($actualHash -ne $expectedCoreHashes[$relativePath]) {
            throw "固定 Vitis 原件 SHA-256 不匹配：$relativePath（$actualHash）"
        }
        $verifiedCoreHashes[$relativePath] = $actualHash
    }

    $patchRoot = Join-Path $repositoryRoot 'board\stage3\software\sensor'
    $patchFiles = @(
        [pscustomobject]@{ Name = 'iicps_v3_23_hw_timeout.patch'; Sequence = 1; Id = 'hardware_timeout'; Hash = ''; Path = '' },
        [pscustomobject]@{ Name = 'iicps_v3_23_sw_deadline.patch'; Sequence = 2; Id = 'software_poll_deadline'; Hash = ''; Path = '' }
    )
    foreach ($patch in $patchFiles) {
        $patchPath = Join-Path $patchRoot $patch.Name
        if (-not (Test-Path -LiteralPath $patchPath -PathType Leaf)) {
            throw "缺少仓库补丁：$patchPath"
        }
        $actualHash = Get-Sha256 -LiteralPath $patchPath
        if ($actualHash -ne $expectedPatchHashes[$patch.Name]) {
            throw "仓库补丁 SHA-256 不匹配：$($patch.Name)（$actualHash）"
        }
        $patch.Hash = $actualHash
        $patch.Path = $patchPath
    }

    $patchTargetSet = New-Object 'System.Collections.Generic.List[string]'
    foreach ($patch in $patchFiles) {
        $patchText = [IO.File]::ReadAllText($patch.Path)
        $headers = [regex]::Matches($patchText, '(?m)^diff --git a/([^\s]+) b/([^\s]+)\r?$')
        if ($headers.Count -eq 0) {
            throw "补丁缺少标准 git diff 文件头：$($patch.Name)"
        }
        foreach ($header in $headers) {
            $oldPath = $header.Groups[1].Value
            $newPath = $header.Groups[2].Value
            if ($oldPath -ne $newPath -or -not $newPath.StartsWith('src/', [StringComparison]::Ordinal)) {
                throw "补丁目标超出 src/ 或含重命名：$($patch.Name) -> $newPath"
            }
            $patchTargetSet.Add($newPath)
        }
        if ($patchText -match '(?m)^(new file mode|deleted file mode|rename from|rename to) ') {
            throw "补丁包含新增、删除或重命名文件，拒绝继续：$($patch.Name)"
        }
    }
    $actualPatchTargets = (@($patchTargetSet | Sort-Object -Unique) -join "`n")
    $expectedPatchTargets = (@($expectedOverlayFiles | Sort-Object -Unique) -join "`n")
    if ($actualPatchTargets -ne $expectedPatchTargets) {
        throw "两补丁的目标文件集合不符：$actualPatchTargets"
    }

    $inventory = Get-TreeInventory -Root $sourceDriverRoot
    if (@($inventory.Files | Where-Object { $_.RelativePath -eq 'data/iicps.mdd' }).Count -ne 1) {
        throw '源驱动必须且只能包含 data/iicps.mdd。'
    }

    $gitCommand = Get-Command git.exe -ErrorAction Stop
    $gitExecutable = $gitCommand.Source
    $gitVersionOutput = & $gitExecutable --version 2>&1
    $gitVersionExitCode = $LASTEXITCODE
    if ($gitVersionExitCode -ne 0) {
        throw '无法读取 Git 版本。'
    }

    # 哈希、补丁和输出路径均核验后，才创建唯一目标目录。
    if ([IO.Directory]::Exists($outputFull) -or [IO.File]::Exists($outputFull)) {
        throw "输出目标在核验期间出现，拒绝覆盖：$outputFull"
    }
    [void][IO.Directory]::CreateDirectory($outputFull)
    [void](Assert-NotReparsePoint -LiteralPath $outputFull)

    $componentRoot = Join-Path $outputFull ($componentRelativeRoot.Replace('/', '\'))
    foreach ($relativeDirectory in $inventory.Directories) {
        $destinationDirectory = Join-Path $componentRoot ($relativeDirectory.Replace('/', '\'))
        [void][IO.Directory]::CreateDirectory($destinationDirectory)
    }
    foreach ($file in $inventory.Files) {
        $destinationFile = Join-Path $componentRoot ($file.RelativePath.Replace('/', '\'))
        $destinationParent = [IO.Path]::GetDirectoryName($destinationFile)
        if (-not [IO.Directory]::Exists($destinationParent)) {
            throw "复制目标父目录未按预期创建：$destinationParent"
        }
        [IO.File]::Copy($file.FullName, $destinationFile, $false)
        $copiedAttributes = [IO.File]::GetAttributes($destinationFile)
        if (($copiedAttributes -band [IO.FileAttributes]::ReadOnly) -ne 0) {
            $writableAttributes = [IO.FileAttributes]([int]$copiedAttributes -band (-bnot [int][IO.FileAttributes]::ReadOnly))
            [IO.File]::SetAttributes($destinationFile, $writableAttributes)
        }
    }

    $mddPath = Join-Path $componentRoot 'data\iicps.mdd'
    Update-MddVersionByte -MddPath $mddPath

    $patchEvidence = New-Object 'System.Collections.Generic.List[object]'
    foreach ($patch in $patchFiles) {
        $checkResult = Invoke-GitPatch -GitExecutable $gitExecutable -DriverDirectory $componentRoot -PatchPath $patch.Path -Operation 'check'
        $applyResult = Invoke-GitPatch -GitExecutable $gitExecutable -DriverDirectory $componentRoot -PatchPath $patch.Path -Operation 'apply'
        $patchEvidence.Add([pscustomobject]@{
            Id = $patch.Id
            Sequence = $patch.Sequence
            File = $patch.Name
            SHA256 = $patch.Hash
            CheckExitCode = $checkResult.ExitCode
            ApplyExitCode = $applyResult.ExitCode
        })
    }

    $verifiedOutputInventory = Get-TreeInventory -Root $componentRoot
    $originalPathSet = (@($inventory.Files | ForEach-Object { $_.RelativePath } | Sort-Object) -join "`n")
    $outputPathSet = (@($verifiedOutputInventory.Files | ForEach-Object { $_.RelativePath } | Sort-Object) -join "`n")
    if ($originalPathSet -ne $outputPathSet) {
        throw '补丁前后源文件路径集合不同，存在新增、删除或遗漏文件。'
    }

    $overlaySet = @{}
    foreach ($relativePath in $expectedOverlayFiles) { $overlaySet[$relativePath] = $true }
    $outputFiles = New-Object 'System.Collections.Generic.List[object]'
    $changedOverlayFiles = New-Object 'System.Collections.Generic.List[string]'
    foreach ($file in $inventory.Files) {
        $destinationFile = Join-Path $componentRoot ($file.RelativePath.Replace('/', '\'))
        $destinationHash = Get-Sha256 -LiteralPath $destinationFile
        $destinationLength = (Get-Item -LiteralPath $destinationFile -Force).Length
        $outputFiles.Add([pscustomobject]@{
            Path = "$componentRelativeRoot/$($file.RelativePath)"
            Length = [long]$destinationLength
            SHA256 = $destinationHash
        })

        if ($overlaySet.ContainsKey($file.RelativePath)) {
            if ($destinationHash -eq $file.SHA256) {
                throw "预期 overlay 目标没有发生变化：$($file.RelativePath)"
            }
            $changedOverlayFiles.Add($file.RelativePath)
        }
        elseif ($file.RelativePath -eq 'data/iicps.mdd') {
            $originalBytes = [IO.File]::ReadAllBytes($file.FullName)
            $candidateBytes = [IO.File]::ReadAllBytes($destinationFile)
            Assert-MddOnlyVersionBump -OriginalBytes $originalBytes -CandidateBytes $candidateBytes
        }
        elseif ($destinationHash -ne $file.SHA256) {
            throw "非 overlay 源文件字节变化，拒绝交付：$($file.RelativePath)"
        }
    }
    $changedOverlaySet = (@($changedOverlayFiles | Sort-Object -Unique) -join "`n")
    $expectedOverlaySet = (@($expectedOverlayFiles | Sort-Object -Unique) -join "`n")
    if ($changedOverlaySet -ne $expectedOverlaySet) {
        throw 'overlay 改动文件集合与固定三文件集合不一致。'
    }

    $manifestPath = Join-Path $outputFull 'source_manifest.json'
    if ([IO.File]::Exists($manifestPath)) {
        throw "source_manifest.json 已存在，拒绝覆盖：$manifestPath"
    }
    $manifest = [ordered]@{
        schema_version = 1
        task = 'S3-SW04-REPO'
        prepared_at_utc_plus_8 = [TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTimeOffset]::UtcNow, 'China Standard Time').ToString('o')
        preparer_version = $scriptVersion
        source_driver_root = $sourceDriverRoot
        source_driver_version = '3.23'
        output_component_root = $componentRelativeRoot
        driver_name = 'iicps'
        output_driver_version = '3.24'
        source_integrity = @($expectedCoreHashes.Keys | Sort-Object | ForEach-Object {
            [pscustomobject]@{ Path = $_; ExpectedSHA256 = $expectedCoreHashes[$_]; ActualSHA256 = $verifiedCoreHashes[$_] }
        })
        original_files = @($inventory.Files | ForEach-Object {
            [pscustomobject]@{ Path = $_.RelativePath; Length = [long]$_.Length; SHA256 = $_.SHA256 }
        })
        output_files = $outputFiles.ToArray()
        overlay_modified_files = @($changedOverlayFiles | Sort-Object)
        metadata_only_change = [pscustomobject]@{
            Path = "$componentRelativeRoot/data/iicps.mdd"
            Field = 'OPTION VERSION'
            From = '3.23'
            To = '3.24'
            ByteChangeCount = 1
        }
        patches = $patchEvidence.ToArray()
        steps = @(
            '校验六个固定 Vitis 原件 SHA-256。',
            '校验两个仓库 overlay 的固定 SHA-256。',
            '逐文件复制源驱动 src 与 data 元数据到任务指定的本地仓库候选布局。',
            '仅在输出副本中将 data/iicps.mdd 的 VERSION 从 3.23 提升到 3.24。',
            '先对硬件 TO overlay 执行 git apply --check 并应用，再对软件轮询期限 overlay 执行 git apply --check 并应用。',
            'fail-closed 核验只有三个 overlay 源文件改变，其他复制源逐字节一致，且 MDD 仅改一个版本字节。'
        )
        tool_versions = [pscustomobject]@{
            PowerShell = $PSVersionTable.PSVersion.ToString()
            Git = (($gitVersionOutput | ForEach-Object { [string]$_ }) -join ' ').Trim()
        }
        limitations = @(
            '这是离线 local software repository 候选包；没有启动 Vitis 2026.1 扫描、添加、选择或生成 BSP。',
            'UG1400 2026.1 说明自建驱动仓库包含 src/data 与提升后的 MDD 版本，并说明仓库按组件目录组织；任务指定的 XilinxProcessorIPLib 前缀是否被当前 Vitis 扫描器接受仍待实测。',
            '未完成 Vitis 2026.1、XA7Z020/-1 目标平台 BSP 构建或编译。',
            '未进行板测；补丁行为测试不构成目标硬件上的 MMIO、I2C 或墙钟期限证明。',
            '厂商安装源、AppData、Registry、AX7Z020 资料库和板卡均未写入或操作。'
        )
        manifest_self_hash_excluded = 'source_manifest.json 的 SHA-256 未纳入自身清单，以避免递归哈希。'
    }
    $manifestJson = ConvertTo-Json -InputObject $manifest -Depth 20
    [IO.File]::WriteAllText($manifestPath, $manifestJson + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))

    Write-Output "候选包已生成：$outputFull"
    Write-Output "组件目录：$(Join-Path $outputFull ($componentRelativeRoot.Replace('/', '\')))"
    Write-Output "文件清单：$manifestPath"
    exit 0
}
catch {
    [Console]::Error.WriteLine("准备失败：$($_.Exception.Message)")
    if (-not [string]::IsNullOrWhiteSpace([string]$_.ScriptStackTrace)) {
        [Console]::Error.WriteLine("诊断位置：$($_.InvocationInfo.PositionMessage)")
        [Console]::Error.WriteLine("调用栈：$($_.ScriptStackTrace)")
    }
    exit 1
}
