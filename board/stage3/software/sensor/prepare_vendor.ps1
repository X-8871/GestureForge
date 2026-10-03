param([Parameter(Mandatory=$true)][string]$OutputDirectory)
$ErrorActionPreference = 'Stop'
$repo = (Get-Item -LiteralPath (Join-Path $PSScriptRoot '../../../..')).FullName
$reference = Get-Item -LiteralPath (Join-Path $repo 'tmp/stage3_reference/AX7020_2023.1')
$prefix = 'course_s2_vitis/22_ov5640_single/Vitis/auto_create_vitis/src/an5642_single'
$source = Get-Item -LiteralPath (Join-Path $reference.FullName $prefix)
$pin = 'fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327'
if ((& git -C $reference.FullName rev-parse HEAD) -ne $pin) { throw '参考提交不匹配' }
$tmp = (Get-Item -LiteralPath (Join-Path $repo 'tmp')).FullName
$target = [IO.Path]::GetFullPath($OutputDirectory)
if (!$target.StartsWith($tmp + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw '输出必须在项目 tmp 内' }
if (Test-Path -LiteralPath $target) { throw '输出目录已存在，禁止覆盖' }
$parent = Get-Item -LiteralPath ([IO.Path]::GetDirectoryName($target))
if (!$parent.PSIsContainer) { throw '父目录不是目录' }
$utf8 = [Text.UTF8Encoding]::new($false)
$files = @('i2c/PS_i2c.c','i2c/PS_i2c.h','ov5640.c','ov5640.h')
$texts = @{}
$manifest = @()
foreach ($name in $files) {
    $item = Get-Item -LiteralPath (Join-Path $source.FullName $name)
    if ($item.PSIsContainer) { throw '源不是普通文件' }
    $expected = & git -C $reference.FullName rev-parse "$pin`:$prefix/$name"
    $actual = & git -C $reference.FullName hash-object -- $item.FullName
    if ($LASTEXITCODE -ne 0 -or $actual -ne $expected) { throw "参考文件被修改：$name" }
    # 厂商表的非 ASCII 注释含旧编码；原始字节另存，适配副本统一 UTF-8。
    $texts[$name] = [IO.File]::ReadAllText($item.FullName, $utf8).Replace("`r", '').TrimEnd("`n").Split("`n")
    $manifest += @{path=$name; git_blob=$actual; sha256=(Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash}
}
$patch = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'vendor_safety.patch') -Encoding UTF8
$p = 0
while ($p -lt $patch.Count) {
    if ($patch[$p] -notmatch '^--- a/(.+)$') { throw '补丁格式错误' }
    $name = $Matches[1]; $p++
    if ($patch[$p] -ne "+++ b/$name") { throw '补丁目标错误' }; $p++
    if ($patch[$p] -notmatch '^@@ -(\d+),(\d+) \+(\d+),(\d+) @@$') { throw '补丁范围错误' }
    $start = [int]$Matches[1] - 1; $oldCount = [int]$Matches[2]; $newCount = [int]$Matches[4]; $p++
    $old = @(); $new = @()
    while ($p -lt $patch.Count -and !$patch[$p].StartsWith('--- a/')) {
        $row = $patch[$p]; $p++
        if ($row.StartsWith('-')) { $old += $row.Substring(1) }
        elseif ($row.StartsWith('+')) { $new += $row.Substring(1) }
        else { throw '只接受无上下文精确差异' }
    }
    if ($old.Count -ne $oldCount -or $new.Count -ne $newCount) { throw '补丁计数错误' }
    $lines = [Collections.Generic.List[string]]::new()
    $lines.AddRange([string[]]$texts[$name])
    for ($n=0; $n -lt $oldCount; $n++) {
        if ($start+$n -ge $lines.Count -or $lines[$start+$n] -cne $old[$n]) { throw "补丁上下文不匹配：$name" }
    }
    $lines.RemoveRange($start,$oldCount); $lines.InsertRange($start,[string[]]$new)
    $texts[$name] = $lines.ToArray()
}
New-Item -ItemType Directory -Path $target | Out-Null
New-Item -ItemType Directory -Path (Join-Path $target 'i2c'),(Join-Path $target 'vendor_original/i2c') | Out-Null
foreach ($name in $files) {
    Copy-Item -LiteralPath (Join-Path $source.FullName $name) -Destination (Join-Path $target "vendor_original/$name")
    [IO.File]::WriteAllText((Join-Path $target $name), ($texts[$name] -join "`n") + "`n", $utf8)
}
$data = @{reference_commit=$pin; source=$source.FullName; files=$manifest; license='厂商四文件未见许可声明；不据此授予再分发权'}
[IO.File]::WriteAllText((Join-Path $target 'source_manifest.json'), ($data | ConvertTo-Json -Depth 6), $utf8)
Write-Output $target
