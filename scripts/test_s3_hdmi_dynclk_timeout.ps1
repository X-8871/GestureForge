param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot
)

$ErrorActionPreference = 'Stop'

function Add-EvidenceLine {
    param([string]$Line)
    $script:EvidenceLines.Add($Line)
    Write-Output $Line
}

function Get-CFunctionText {
    param(
        [string]$Source,
        [string]$FunctionName
    )

    $signaturePattern = '(?m)\bint\s+' + [regex]::Escape($FunctionName) + '\s*\(\s*u32\s+dynClkAddr\s*\)\s*\{'
    $match = [regex]::Match($Source, $signaturePattern)
    if (!$match.Success) {
        throw "无法在补丁后的源码中定位函数：$FunctionName"
    }

    $start = $match.Index
    $openBrace = $Source.IndexOf('{', $match.Index, $match.Length)
    if ($openBrace -lt 0) {
        throw "函数缺少左花括号：$FunctionName"
    }

    $depth = 0
    $state = 'code'
    $index = $openBrace
    while ($index -lt $Source.Length) {
        $character = $Source[$index]
        $nextCharacter = if ($index + 1 -lt $Source.Length) { $Source[$index + 1] } else { [char]0 }

        switch ($state) {
            'code' {
                if ($character -eq '/' -and $nextCharacter -eq '/') {
                    $state = 'line-comment'
                    $index++
                }
                elseif ($character -eq '/' -and $nextCharacter -eq '*') {
                    $state = 'block-comment'
                    $index++
                }
                elseif ($character -eq '"') {
                    $state = 'string'
                }
                elseif ($character -eq "'") {
                    $state = 'character'
                }
                elseif ($character -eq '{') {
                    $depth++
                }
                elseif ($character -eq '}') {
                    $depth--
                    if ($depth -eq 0) {
                        return $Source.Substring($start, $index - $start + 1)
                    }
                }
            }
            'line-comment' {
                if ($character -eq [char]10) {
                    $state = 'code'
                }
            }
            'block-comment' {
                if ($character -eq '*' -and $nextCharacter -eq '/') {
                    $state = 'code'
                    $index++
                }
            }
            'string' {
                if ($character -eq '\') {
                    $index++
                }
                elseif ($character -eq '"') {
                    $state = 'code'
                }
            }
            'character' {
                if ($character -eq '\') {
                    $index++
                }
                elseif ($character -eq "'") {
                    $state = 'code'
                }
            }
        }
        $index++
    }

    throw "函数花括号不匹配：$FunctionName"
}

$repoPath = [IO.Path]::GetFullPath($RepoRoot)
$vendorRoot = Join-Path $repoPath 'tmp/stage3_reference/AX7020_2023.1'
$patchPath = Join-Path $repoPath 'board/stage3/software/hdmi_test/hdmi_display_bringup.patch'
$gccPath = 'D:\mingw64\bin\gcc.exe'
$expectedVendorCommit = 'fcf1e4a239b0f47e8ee95dfde7c2eedc5685c327'
$expectedFiles = [ordered]@{
    'course_s2_vitis/14_vdma_hdmi_out/Vitis/auto_create_vitis/src/vdma_hdmi/dynclk/dynclk.c' = 'BE827313363BAAD59D1693C8E7B1894AB6C0AACC569934EA85919ABE73846E14'
    'course_s2_vitis/14_vdma_hdmi_out/Vitis/auto_create_vitis/src/vdma_hdmi/dynclk/dynclk.h' = '62D8815CE504EA1BDA24B23AA404A860D59B6BF96D98A91A2519B16EDE437ED3'
    'course_s2_vitis/14_vdma_hdmi_out/Vitis/auto_create_vitis/src/vdma_hdmi/display_ctrl/display_ctrl.c' = '3E9E02D815CC6CA1D6D4A457467ECD26EC4A1126F6696C038C2EEE1E6D4CF29C'
}
$expectedPatchPaths = @(
    'course_s2_vitis/14_vdma_hdmi_out/Vitis/auto_create_vitis/src/vdma_hdmi/main.c',
    'course_s2_vitis/14_vdma_hdmi_out/Vitis/auto_create_vitis/src/vdma_hdmi/dynclk/dynclk.c',
    'course_s2_vitis/14_vdma_hdmi_out/Vitis/auto_create_vitis/src/vdma_hdmi/dynclk/dynclk.h',
    'course_s2_vitis/14_vdma_hdmi_out/Vitis/auto_create_vitis/src/vdma_hdmi/display_ctrl/display_ctrl.c'
)
$EvidenceRoot = Join-Path ([IO.Path]::GetTempPath()) ('s3-dclk-host-' + [guid]::NewGuid().ToString('N'))
[void][IO.Directory]::CreateDirectory($EvidenceRoot)
$script:EvidenceLines = [System.Collections.Generic.List[string]]::new()

try {
    Add-EvidenceLine "证据目录：$EvidenceRoot"
    Add-EvidenceLine "仓库：$repoPath"

    if (!(Test-Path -LiteralPath $vendorRoot -PathType Container)) {
        throw "未找到固定官方源码目录：$vendorRoot"
    }
    if (!(Test-Path -LiteralPath $patchPath -PathType Leaf)) {
        throw "未找到目标补丁：$patchPath"
    }
    if (!(Test-Path -LiteralPath $gccPath -PathType Leaf)) {
        throw "未找到指定 GCC：$gccPath"
    }

    $actualVendorCommit = (& git -C $vendorRoot rev-parse HEAD 2>&1 | Out-String).Trim()
    $vendorCommitExit = $LASTEXITCODE
    Add-EvidenceLine "COMMAND: git -C $vendorRoot rev-parse HEAD"
    Add-EvidenceLine "EXIT: $vendorCommitExit"
    Add-EvidenceLine "VENDOR_COMMIT: $actualVendorCommit"
    if ($vendorCommitExit -ne 0 -or $actualVendorCommit -ne $expectedVendorCommit) {
        throw "官方源码提交与固定基线不符。"
    }

    foreach ($relativePath in $expectedFiles.Keys) {
        $sourcePath = Join-Path $vendorRoot $relativePath
        if (!(Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
            throw "官方源码文件缺失：$sourcePath"
        }
        $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourcePath).Hash
        Add-EvidenceLine "SHA256 $relativePath $actualHash"
        if ($actualHash -ne $expectedFiles[$relativePath]) {
            throw "官方源码哈希不符：$relativePath"
        }
    }

    $patchLines = [IO.File]::ReadAllLines($patchPath, [Text.Encoding]::UTF8)
    $actualPatchPaths = [System.Collections.Generic.List[string]]::new()
    foreach ($line in $patchLines) {
        if ($line -match '^diff --git a/(.+) b/(.+)$') {
            $actualPatchPaths.Add($Matches[1])
            if ($Matches[1] -ne $Matches[2]) {
                throw "补丁两侧路径不一致：$line"
            }
        }
    }
    if ([string]::Join('|', $actualPatchPaths) -ne [string]::Join('|', $expectedPatchPaths)) {
        throw "补丁修改路径超出预期集合：$([string]::Join(', ', $actualPatchPaths))"
    }
    Add-EvidenceLine "PATCH_PATHS: $([string]::Join(', ', $actualPatchPaths))"

    Add-EvidenceLine "COMMAND: git -C $vendorRoot apply --check --whitespace=error $patchPath"
    $vendorApplyOutput = & git -C $vendorRoot apply --check --whitespace=error $patchPath 2>&1
    $vendorApplyExit = $LASTEXITCODE
    foreach ($line in $vendorApplyOutput) {
        Add-EvidenceLine "$line"
    }
    Add-EvidenceLine "EXIT: $vendorApplyExit"
    if ($vendorApplyExit -ne 0) {
        throw "官方源码只读补丁应用检查失败。"
    }

    $scratchRoot = Join-Path $EvidenceRoot 'patched-source'
    foreach ($relativePath in $actualPatchPaths) {
        $sourcePath = Join-Path $vendorRoot $relativePath
        $destinationPath = Join-Path $scratchRoot $relativePath
        $destinationDirectory = Split-Path -Parent $destinationPath
        [void][IO.Directory]::CreateDirectory($destinationDirectory)
        Copy-Item -LiteralPath $sourcePath -Destination $destinationPath
    }

    Add-EvidenceLine "COMMAND: git -C $scratchRoot apply --check --whitespace=error $patchPath"
    $scratchCheckOutput = & git -C $scratchRoot apply --check --whitespace=error $patchPath 2>&1
    $scratchCheckExit = $LASTEXITCODE
    foreach ($line in $scratchCheckOutput) {
        Add-EvidenceLine "$line"
    }
    Add-EvidenceLine "EXIT: $scratchCheckExit"
    if ($scratchCheckExit -ne 0) {
        throw "隔离副本补丁应用检查失败。"
    }

    $scratchApplyArguments = @('-C', $scratchRoot, 'apply', '--whitespace=error', $patchPath)
    Add-EvidenceLine "COMMAND: git $([string]::Join(' ', $scratchApplyArguments))"
    $scratchApplyOutput = & git @scratchApplyArguments 2>&1
    $scratchApplyExit = $LASTEXITCODE
    foreach ($line in $scratchApplyOutput) {
        Add-EvidenceLine "$line"
    }
    Add-EvidenceLine "EXIT: $scratchApplyExit"
    if ($scratchApplyExit -ne 0) {
        throw "隔离副本补丁实际应用失败。"
    }

    $dynclkPath = Join-Path $scratchRoot 'course_s2_vitis/14_vdma_hdmi_out/Vitis/auto_create_vitis/src/vdma_hdmi/dynclk/dynclk.c'
    $patchedSource = [IO.File]::ReadAllText($dynclkPath, [Text.Encoding]::UTF8)
    $startFunction = Get-CFunctionText -Source $patchedSource -FunctionName 'ClkStart'
    $stopFunction = Get-CFunctionText -Source $patchedSource -FunctionName 'ClkStop'

    $harness = @'
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint32_t u32;
typedef uint64_t XTime;
#define COUNTS_PER_SECOND 1000ULL
#define DYNCLK_TIMEOUT_TICKS ((XTime)COUNTS_PER_SECOND)
#define XST_SUCCESS 0
#define XST_FAILURE 1
#define OFST_DYNCLK_CTRL 0u
#define OFST_DYNCLK_STATUS 4u
#define BIT_DYNCLK_START 0
#define BIT_DYNCLK_RUNNING 0
static XTime mock_time;
static XTime mock_step;
static XTime transition_after;
static XTime operation_start_time;
static unsigned int status_reads;
static unsigned int write_count;
static u32 write_values[4];
static u32 write_addresses[4];
static int operation_is_start;
static int clock_running;
void XTime_GetTime(XTime *value)
{
    *value = mock_time;
    mock_time += mock_step;
}
void Xil_Out32(u32 address, u32 value)
{
    if (write_count < 4u) {
        write_values[write_count] = value;
        write_addresses[write_count] = address;
    }
    write_count++;
    operation_is_start = (value & (1u << BIT_DYNCLK_START)) != 0u;
    operation_start_time = mock_time;
    if (operation_is_start) {
        clock_running = 0;
    }
}
u32 Xil_In32(u32 address)
{
    (void)address;
    status_reads++;
    if ((XTime)(mock_time - operation_start_time) >= transition_after) {
        clock_running = operation_is_start;
    }
    return clock_running ? (1u << BIT_DYNCLK_RUNNING) : 0u;
}
static void setup_case(XTime initial_time, XTime step, XTime transition, int initially_running)
{
    mock_time = initial_time;
    mock_step = step;
    transition_after = transition;
    operation_start_time = initial_time;
    status_reads = 0u;
    write_count = 0u;
    memset(write_values, 0, sizeof(write_values));
    memset(write_addresses, 0, sizeof(write_addresses));
    operation_is_start = 0;
    clock_running = initially_running;
}
static int report_case(const char *name, int passed)
{
    printf("%s %s\n", passed ? "PASS" : "FAIL", name);
    return passed ? 0 : 1;
}
static int failed_start_was_stopped_once(int result)
{
    return result == XST_FAILURE && write_count == 2u &&
        write_values[0] == 1u && write_values[1] == 0u &&
        write_addresses[0] == 0x1000u && write_addresses[1] == 0x1000u;
}
__START_FUNCTION__
__STOP_FUNCTION__
int main(void)
{
    int failures = 0;
    int result;

    setup_case(0u, 100u, 0u, 0);
    result = ClkStart(0x1000u);
    failures += report_case("start_immediate_success", result == XST_SUCCESS && status_reads == 1u && write_count == 1u);

    setup_case(0u, 100u, 0u, 1);
    result = ClkStop(0x1000u);
    failures += report_case("stop_immediate_success", result == XST_SUCCESS && status_reads == 1u && write_count == 1u);

    setup_case(0u, 100u, 250u, 0);
    result = ClkStart(0x1000u);
    failures += report_case("start_delayed_success", result == XST_SUCCESS && write_count == 1u);

    setup_case(0u, 100u, 250u, 1);
    result = ClkStop(0x1000u);
    failures += report_case("stop_delayed_success", result == XST_SUCCESS && write_count == 1u);

    setup_case(0u, 600u, UINT64_MAX, 0);
    result = ClkStart(0x1000u);
    failures += report_case("start_timeout_single_best_effort_stop", failed_start_was_stopped_once(result) && status_reads == 2u);

    setup_case(0u, 600u, UINT64_MAX, 1);
    result = ClkStop(0x1000u);
    failures += report_case("stop_timeout", result == XST_FAILURE && status_reads == 2u && write_count == 1u);

    setup_case(0u, 500u, 500u, 0);
    result = ClkStart(0x1000u);
    failures += report_case("start_terminal_at_deadline_rejected", failed_start_was_stopped_once(result) && status_reads == 2u);

    setup_case(0u, 500u, 1000u, 1);
    result = ClkStop(0x1000u);
    failures += report_case("stop_terminal_at_deadline_rejected", result == XST_FAILURE && status_reads == 2u && write_count == 1u);

    setup_case(0u, 600u, 500u, 0);
    result = ClkStart(0x1000u);
    failures += report_case("start_terminal_after_deadline_rejected", failed_start_was_stopped_once(result) && status_reads == 2u);

    setup_case(0u, 600u, 1100u, 1);
    result = ClkStop(0x1000u);
    failures += report_case("stop_terminal_after_deadline_rejected", result == XST_FAILURE && status_reads == 2u && write_count == 1u);

    setup_case(UINT64_MAX - 200u, 100u, 250u, 0);
    result = ClkStart(0x1000u);
    failures += report_case("start_success_across_timer_wrap", result == XST_SUCCESS && write_count == 1u);

    setup_case(UINT64_MAX - 200u, 100u, 250u, 1);
    result = ClkStop(0x1000u);
    failures += report_case("stop_success_across_timer_wrap", result == XST_SUCCESS && write_count == 1u);

    setup_case(UINT64_MAX - 200u, 600u, UINT64_MAX, 0);
    result = ClkStart(0x1000u);
    failures += report_case("start_timeout_across_timer_wrap", failed_start_was_stopped_once(result) && status_reads == 2u);

    setup_case(UINT64_MAX - 200u, 600u, UINT64_MAX, 1);
    result = ClkStop(0x1000u);
    failures += report_case("stop_timeout_across_timer_wrap", result == XST_FAILURE && status_reads == 2u && write_count == 1u);

    printf("RESULT cases=14 passed=%d failed=%d\n", 14 - failures, failures);
    return failures == 0 ? 0 : 1;
}
'@
    $harness = $harness.Replace('__START_FUNCTION__', $startFunction).Replace('__STOP_FUNCTION__', $stopFunction)
    $harnessPath = Join-Path $EvidenceRoot 'dynclk_timeout_harness.c'
    $executablePath = Join-Path $EvidenceRoot 'dynclk_timeout_harness.exe'
    [IO.File]::WriteAllText($harnessPath, $harness, [Text.UTF8Encoding]::new($false))

    $compileArguments = @('-std=c99', '-Wall', '-Wextra', '-Werror', '-pedantic', '-o', $executablePath, $harnessPath)
    Add-EvidenceLine "COMMAND: $gccPath $([string]::Join(' ', $compileArguments))"
    $compileOutput = & $gccPath @compileArguments 2>&1
    $compileExit = $LASTEXITCODE
    foreach ($line in $compileOutput) {
        Add-EvidenceLine "$line"
    }
    Add-EvidenceLine "EXIT: $compileExit"
    if ($compileExit -ne 0) {
        throw "GCC 主机回归编译失败。"
    }

    Add-EvidenceLine "COMMAND: $executablePath"
    $testOutput = & $executablePath 2>&1
    $testExit = $LASTEXITCODE
    foreach ($line in $testOutput) {
        Add-EvidenceLine "$line"
    }
    Add-EvidenceLine "EXIT: $testExit"
    if ($testExit -ne 0 -or !($testOutput -match 'RESULT cases=14 passed=14 failed=0')) {
        throw "GCC 主机行为回归未全部通过。"
    }

    Add-EvidenceLine 'FINAL: PASS; 14 个主机行为用例全部通过。'
    [IO.File]::WriteAllLines((Join-Path $EvidenceRoot 'test-results.txt'), $script:EvidenceLines, [Text.UTF8Encoding]::new($false))
    Write-Output "EVIDENCE_RESULTS=$(Join-Path $EvidenceRoot 'test-results.txt')"
    Write-Output "EVIDENCE_HARNESS=$harnessPath"
}
catch {
    $script:EvidenceLines.Add("FINAL: FAIL; $($_.Exception.Message)")
    [IO.File]::WriteAllLines((Join-Path $EvidenceRoot 'test-results.txt'), $script:EvidenceLines, [Text.UTF8Encoding]::new($false))
    Write-Output "EVIDENCE_RESULTS=$(Join-Path $EvidenceRoot 'test-results.txt')"
    throw
}
