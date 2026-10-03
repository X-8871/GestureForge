param(
    [Parameter(Mandatory=$true)]
    [string]$OutputDirectory
)

$ErrorActionPreference = 'Stop'
$utf8 = [Text.UTF8Encoding]::new($false, $true)
$repo = (Get-Item -LiteralPath (Join-Path $PSScriptRoot '../../../..')).FullName
$tmp = (Get-Item -LiteralPath (Join-Path $repo 'tmp')).FullName
$reference = Get-Item -LiteralPath (Join-Path $tmp 'stage3_reference/AX7020_2023.1')
if (!$reference.PSIsContainer) { throw 'Pinned reference cache path is not a directory' }

$pin = 'fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327'
$expectedAlinxBlob = '1c43d5a28bc1904b452dec80e5eab5803ba9cdab'
$expectedCmosBlob = 'abb847ba794884f8e25216d520f24f46f37309cf'
$singleAlinx = 'course_s2_vitis/22_ov5640_single/Vivado/auto_create_project/my_ip/ov5640_ip/src/alinx_ov5640.v'
$dualAlinx = 'course_s2_vitis/23_ov5640_dual/Vivado/auto_create_project/my_ip/ov5640_ip/src/alinx_ov5640.v'
$singleCmos = 'course_s2_vitis/22_ov5640_single/Vivado/auto_create_project/my_ip/ov5640_ip/src/cmos_8_16bit.v'
$dualCmos = 'course_s2_vitis/23_ov5640_dual/Vivado/auto_create_project/my_ip/ov5640_ip/src/cmos_8_16bit.v'

$actualHead = (& git -C $reference.FullName rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0 -or $actualHead -cne $pin) { throw 'Pinned reference cache HEAD mismatch' }

$target = [IO.Path]::GetFullPath($OutputDirectory)
$separator = [IO.Path]::DirectorySeparatorChar
if (!$target.StartsWith(($tmp + $separator), [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Output directory must be a new directory inside project tmp'
}
if (Test-Path -LiteralPath $target) { throw 'Output directory already exists; refusing to overwrite' }
$parentPath = [IO.Path]::GetDirectoryName($target)
$parent = Get-Item -LiteralPath $parentPath
if (!$parent.PSIsContainer) { throw 'Output directory parent path is not a directory' }

function Get-PinnedSource([string]$RelativePath, [string]$ExpectedBlob) {
    $spec = $pin + ':' + $RelativePath
    $treeBlob = (& git -C $reference.FullName rev-parse $spec).Trim()
    if ($LASTEXITCODE -ne 0 -or $treeBlob -cne $ExpectedBlob) {
        throw ('Git blob mismatch in pinned commit: ' + $RelativePath)
    }
    $source = Get-Item -LiteralPath (Join-Path $reference.FullName $RelativePath)
    if ($source.PSIsContainer) { throw ('Source is not a regular file: ' + $RelativePath) }
    $workBlob = (& git -C $reference.FullName hash-object -- $source.FullName).Trim()
    if ($LASTEXITCODE -ne 0 -or $workBlob -cne $ExpectedBlob) {
        throw ('Source file in reference cache differs from pinned Git blob: ' + $RelativePath)
    }
    return [ordered]@{
        path = $RelativePath
        full_path = $source.FullName
        git_blob = $workBlob
        sha256 = (Get-FileHash -LiteralPath $source.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        bytes = [IO.File]::ReadAllBytes($source.FullName)
    }
}

$single = Get-PinnedSource $singleAlinx $expectedAlinxBlob
$dual = Get-PinnedSource $dualAlinx $expectedAlinxBlob
$singleConverter = Get-PinnedSource $singleCmos $expectedCmosBlob
$dualConverter = Get-PinnedSource $dualCmos $expectedCmosBlob
if ($single.sha256 -cne $dual.sha256 -or
    [Convert]::ToBase64String($single.bytes) -cne [Convert]::ToBase64String($dual.bytes)) {
    throw 'Single and dual alinx_ov5640.v contents are not identical'
}
if ($singleConverter.sha256 -cne $dualConverter.sha256 -or
    [Convert]::ToBase64String($singleConverter.bytes) -cne [Convert]::ToBase64String($dualConverter.bytes)) {
    throw 'Single and dual cmos_8_16bit.v contents are not identical'
}

$patchPath = Join-Path $PSScriptRoot 'vendor_axis.patch'
$actualPatch = [IO.File]::ReadAllText($patchPath, $utf8).Replace([string][char]13 + [char]10, [string][char]10)
$expectedPatch = @'
--- a/alinx_ov5640.v
+++ b/alinx_ov5640.v
@@ -162,1 +162,1 @@
-assign m_axis_video_tvalid = ~empty & m_axis_video_tready;
+assign m_axis_video_tvalid = ~empty & fifo_ready_maxis;
@@ -198,1 +198,1 @@
-      .rd_en            (m_axis_video_tready & ~empty & fifo_ready_maxis),
+      .rd_en            (m_axis_video_tvalid & m_axis_video_tready),
'@
if ($actualPatch -cne ($expectedPatch + [char]10)) { throw 'Adaptation patch does not match the approved exact diff' }

$originalText = $utf8.GetString($single.bytes).Replace([string][char]13 + [char]10, [string][char]10).Replace([string][char]13, [string][char]10)
$oldValid = 'assign m_axis_video_tvalid = ~empty & m_axis_video_tready;'
$newValid = 'assign m_axis_video_tvalid = ~empty & fifo_ready_maxis;'
$oldRead = '      .rd_en            (m_axis_video_tready & ~empty & fifo_ready_maxis),'
$newRead = '      .rd_en            (m_axis_video_tvalid & m_axis_video_tready),'
foreach ($statement in @($oldValid, $newValid, $oldRead, $newRead)) {
    if ([regex]::Matches($originalText, [regex]::Escape($statement)).Count -gt 1) {
        throw ('Exact-diff statement occurs more than once; refusing adaptation: ' + $statement)
    }
}
if (!$originalText.Contains($oldValid) -or !$originalText.Contains($oldRead) -or
    $originalText.Contains($newValid) -or $originalText.Contains($newRead)) {
    throw 'Pinned RTL does not contain exactly the two original statements to replace'
}
$adaptedText = $originalText.Replace($oldValid, $newValid).Replace($oldRead, $newRead)
if (!$adaptedText.Contains($newValid) -or !$adaptedText.Contains($newRead) -or
    $adaptedText.Contains($oldValid) -or $adaptedText.Contains($oldRead)) {
    throw 'Content validation failed after applying the exact diff'
}

$patchHash = (Get-FileHash -LiteralPath $patchPath -Algorithm SHA256).Hash.ToLowerInvariant()
New-Item -ItemType Directory -Path $target | Out-Null
$directories = @(
    'vendor_original/single',
    'vendor_original/dual',
    'vendor_original/converter',
    'adapted/single'
)
foreach ($directory in $directories) {
    New-Item -ItemType Directory -Path (Join-Path $target $directory) | Out-Null
}
[IO.File]::WriteAllBytes((Join-Path $target 'vendor_original/single/alinx_ov5640.v'), $single.bytes)
[IO.File]::WriteAllBytes((Join-Path $target 'vendor_original/dual/alinx_ov5640.v'), $dual.bytes)
[IO.File]::WriteAllBytes((Join-Path $target 'vendor_original/converter/cmos_8_16bit.v'), $singleConverter.bytes)
[IO.File]::WriteAllBytes((Join-Path $target 'adapted/single/cmos_8_16bit.v'), $singleConverter.bytes)
[IO.File]::WriteAllText((Join-Path $target 'adapted/single/alinx_ov5640.v'), $adaptedText, $utf8)

$adaptedTop = Join-Path $target 'adapted/single/alinx_ov5640.v'
$adaptedTopHash = (Get-FileHash -LiteralPath $adaptedTop -Algorithm SHA256).Hash.ToLowerInvariant()
$converterPath = Join-Path $target 'adapted/single/cmos_8_16bit.v'
$converterHash = (Get-FileHash -LiteralPath $converterPath -Algorithm SHA256).Hash.ToLowerInvariant()
$manifest = [ordered]@{
    reference_commit = $pin
    primary_git_blob = $expectedAlinxBlob
    patch_sha256 = $patchHash
    compiled_top = [ordered]@{
        path = $adaptedTop
        source_git_blob = $single.git_blob
        original_sha256 = $single.sha256
        adapted_sha256 = $adaptedTopHash
    }
    compiled_converter = [ordered]@{
        path = $converterPath
        source_git_blob = $singleConverter.git_blob
        original_sha256 = $singleConverter.sha256
        adapted_sha256 = $converterHash
    }
    verified_sources = @(
        [ordered]@{ variant = 'single'; path = $single.path; git_blob = $single.git_blob; sha256 = $single.sha256 },
        [ordered]@{ variant = 'dual'; path = $dual.path; git_blob = $dual.git_blob; sha256 = $dual.sha256 },
        [ordered]@{ variant = 'single_converter'; path = $singleConverter.path; git_blob = $singleConverter.git_blob; sha256 = $singleConverter.sha256 },
        [ordered]@{ variant = 'dual_converter'; path = $dualConverter.path; git_blob = $dualConverter.git_blob; sha256 = $dualConverter.sha256 }
    )
    originals_directory = (Join-Path $target 'vendor_original')
    license_note = 'Runtime original bytes remain only in tmp; vendor source files and register tables are not added to Git.'
}
$manifestPath = Join-Path $target 'source_manifest.json'
[IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json -Depth 8), $utf8)
Write-Output $target
