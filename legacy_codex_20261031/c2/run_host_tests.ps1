param(
    [string]$TwoBRoot = 'D:\FPGA_Competition\w2b',
    [string]$FrozenS5Source = 'D:\codex-worktrees\w4\report\evidence\S5-T01\s5_p3b_sw_20261030_r01\src'
)

$ErrorActionPreference = 'Stop'
$scriptRoot = (Get-Item -LiteralPath $PSScriptRoot).FullName
$decoderHeader = Join-Path $TwoBRoot 'verification\s2a_ps_decode_nms_reference.h'
$decoderSource = Join-Path $TwoBRoot 'verification\s2a_ps_decode_nms_reference.c'
$abiHeader = Join-Path $FrozenS5Source 's5_result_abi.h'
$compiler = Get-Command gcc -ErrorAction Stop
$testSource = Join-Path $scriptRoot 'test_c2_s5_publish.c'
$publisherSource = Join-Path $scriptRoot 'c2_s5_publish.c'
$tempRoot = [IO.Path]::GetTempPath()
$outputDirectory = Join-Path $tempRoot ('c2-host-' + [Guid]::NewGuid().ToString('N'))
$executable = Join-Path $outputDirectory 'c2_s5_publish_test.exe'
$separator = [IO.Path]::DirectorySeparatorChar
$resolvedTempRoot = [IO.Path]::GetFullPath($tempRoot).TrimEnd($separator) + $separator
$resolvedOutputDirectory = [IO.Path]::GetFullPath($outputDirectory)

if (-not (Test-Path -LiteralPath $decoderHeader -PathType Leaf) -or
    -not (Test-Path -LiteralPath $decoderSource -PathType Leaf) -or
    -not (Test-Path -LiteralPath $abiHeader -PathType Leaf)) {
    throw 'Required pinned decoder or ABI header was not found.'
}
if (-not $resolvedOutputDirectory.StartsWith($resolvedTempRoot, [StringComparison]::OrdinalIgnoreCase) -or
    (Split-Path -Leaf $resolvedOutputDirectory) -notmatch '^c2-host-[0-9a-f]{32}$') {
    throw 'Generated build directory is outside the system temporary directory.'
}
if (Test-Path -LiteralPath $resolvedOutputDirectory) {
    throw 'Generated build directory already exists.'
}

New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
try {
    & $compiler.Source -std=c11 -Wall -Wextra -Werror -pedantic `
        -I (Split-Path -Parent $decoderHeader) `
        -I $FrozenS5Source `
        $publisherSource $testSource $decoderSource -lm -o $executable
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
    & $executable
    exit $LASTEXITCODE
}
finally {
    if (Test-Path -LiteralPath $resolvedOutputDirectory -PathType Container) {
        $actualOutputDirectory = (Get-Item -LiteralPath $resolvedOutputDirectory).FullName
        if ($actualOutputDirectory -ieq $resolvedOutputDirectory -and
            $actualOutputDirectory.StartsWith($resolvedTempRoot, [StringComparison]::OrdinalIgnoreCase) -and
            (Split-Path -Leaf $actualOutputDirectory) -match '^c2-host-[0-9a-f]{32}$') {
            Remove-Item -LiteralPath $actualOutputDirectory -Recurse -Force
        } else {
            throw 'Refusing to remove a build directory outside the generated temporary path.'
        }
    }
}
