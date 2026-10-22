#requires -Version 7.0
<#
S5-C 证据驱动脚本：按固定顺序运行检查器与自检，并把**真实退出码**逐条记录。

产出（默认 report/evidence/S5-C/<RunId>/）：
- regression_report.json / run_manifest.json / summary.md（由检查器与 finalize 写入）
- tamper/tamper_<kind>_before_after.json 等反例证据（由检查器写入）
- console/<step>.raw.txt         ：每一步的真实原始输出（UTF-8）
- console/<label>.log.txt        ：检查器自身双写的日志（UTF-8，含 SELF_REPORTED_EXIT_CODE）
- console/observed_exit_codes.json：由本脚本记录的 $LASTEXITCODE（finalize 之前写入前序步骤）
- console/exit_code_verification.json：全部步骤的退出码对照与总结论（本脚本最后写入）

说明：console/observed_exit_codes.json 在每一步执行**之前**重写，因此 finalize 步骤运行时读到的
是它之前全部步骤的真实退出码；finalize 自身的退出码只出现在 exit_code_verification.json 与
run_manifest.json 的 exit_code_verification.finalize_exit_code 中（不循环自证）。

用法：
    pwsh -File scripts/stage5_s5c/run_s5c_evidence.ps1 -RunId s5c_regression_20261021_r01
退出码：0 = 全部步骤退出码与期望一致；2 = 证据目录已存在或前置检查失败；1 = 存在不一致。
#>
[CmdletBinding()]
param(
    [string]$RunId = "s5c_regression_20261021_r01",
    [string]$OutRoot = "report/evidence/S5-C",
    [string]$Seed = "20261021",
    [int]$Limit = 8
)

$ErrorActionPreference = 'Continue'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$checker = Join-Path $PSScriptRoot 'check_s5c_stage4_regression.py'
$unittestFile = Join-Path $PSScriptRoot 'test_s5c_regression.py'
$python = (Get-Command python).Source
$out = Join-Path $repo (Join-Path $OutRoot $RunId)
$subsetRunId = "${RunId}_limit${Limit}"
$subsetOut = Join-Path $repo (Join-Path $OutRoot $subsetRunId)
$negativeOut = Join-Path $repo 'tmp/5/S5-C/negative_missing_input'
$console = Join-Path $out 'console'
New-Item -ItemType Directory -Force -Path $console | Out-Null
$env:PYTHONIOENCODING = 'utf-8'

if (Test-Path (Join-Path $out 'regression_report.json')) {
    Write-Error "证据目录已含既有运行产物，禁止覆盖：$out（请换 -RunId）"
    exit 2
}

$defs = @(
    @{ name = 'pristine'; expect = 0; args = @($checker, '--run-id', $RunId, '--out', $out) },
    @{ name = 'tamper_score_ulp'; expect = 1; args = @($checker, '--run-id', $RunId, '--out', $out, '--tamper-probe', 'score_ulp') },
    @{ name = 'tamper_score_tol'; expect = 1; args = @($checker, '--run-id', $RunId, '--out', $out, '--tamper-probe', 'score_tol') },
    @{ name = 'tamper_xyxy_ulp'; expect = 1; args = @($checker, '--run-id', $RunId, '--out', $out, '--tamper-probe', 'xyxy_ulp') },
    @{ name = 'tamper_xyxy_tol'; expect = 1; args = @($checker, '--run-id', $RunId, '--out', $out, '--tamper-probe', 'xyxy_tol') },
    @{ name = 'tamper_source_order'; expect = 1; args = @($checker, '--run-id', $RunId, '--out', $out, '--tamper-probe', 'source_order') },
    @{ name = 'tamper_frame_id'; expect = 1; args = @($checker, '--run-id', $RunId, '--out', $out, '--tamper-probe', 'frame_id') },
    @{ name = 'tamper_box_count'; expect = 1; args = @($checker, '--run-id', $RunId, '--out', $out, '--tamper-probe', 'box_count') },
    @{ name = 'tamper_identity_rebuild'; expect = 1; args = @($checker, '--run-id', $RunId, '--out', $out, '--tamper-probe', 'identity_rebuild') },
    @{ name = 'seeded_subset'; expect = 0; args = @($checker, '--run-id', $subsetRunId, '--out', $subsetOut, '--limit', "$Limit", '--seed', $Seed) },
    @{ name = 'unittest'; expect = 0; args = @($unittestFile, '-v') },
    @{ name = 'negative_missing_input'; expect = 2; args = @($checker, '--run-id', 'neg_missing', '--out', $negativeOut, '--golden', (Join-Path $repo 'tmp/5/S5-C/does_not_exist.json')) },
    @{ name = 'finalize'; expect = 0; args = @($checker, '--run-id', $RunId, '--out', $out, '--finalize-exit-codes') }
)

function Write-Observed {
    param($Steps, [int]$Complete)
    # 注意：必须显式物化为 [object[]]；直接把 List[object] 放进有序哈希会把 Add 的参数类型搞坏
    $stepArray = [object[]]$Steps
    $payload = [ordered]@{
        run_id        = $RunId
        generated_utc8 = (Get-Date).ToUniversalTime().AddHours(8).ToString('yyyy-MM-ddTHH:mm:ss+08:00')
        generator     = 'scripts/stage5_s5c/run_s5c_evidence.ps1'
        python        = $python
        note          = 'exit_code 为真实 $LASTEXITCODE；本文件在每一步执行前重写，故 finalize 步骤自身不在本文件内'
        steps_complete = $Complete
        steps         = $stepArray
    }
    $payload | ConvertTo-Json -Depth 6 | Set-Content -Path (Join-Path $console 'observed_exit_codes.json') -Encoding utf8
}

$steps = New-Object System.Collections.Generic.List[object]
$finalizeCode = $null
foreach ($def in $defs) {
    Write-Observed -Steps $steps -Complete $steps.Count
    if ($def.name -eq 'finalize') {
        # 防止「写坏了 observed_exit_codes.json 却继续 finalize」的静默失败
        $observedFile = Join-Path $console 'observed_exit_codes.json'
        try {
            $probe = Get-Content -Raw -Path $observedFile -Encoding utf8 | ConvertFrom-Json
        } catch {
            Write-Error "observed_exit_codes.json 无法解析：$($_.Exception.Message)"
            exit 2
        }
        if ($null -eq $probe.steps -or @($probe.steps).Count -ne $steps.Count) {
            Write-Error ("observed_exit_codes.json 步骤数不一致（{0} != {1}），停止 finalize" -f @($probe.steps).Count, $steps.Count)
            exit 2
        }
    }
    $raw = Join-Path $console ($def.name + '.raw.txt')
    & $python -B @($def.args) *> $raw
    $code = $LASTEXITCODE
    $scriptLog = $null
    if ($def.name -eq 'pristine') { $scriptLog = 'console/pristine.log.txt' }
    elseif ($def.name -eq 'seeded_subset') { $scriptLog = "console/seeded_subset.log.txt" }
    elseif ($def.name -like 'tamper_*') { $scriptLog = "console/checker_$($def.name).log.txt" }
    $steps.Add([pscustomobject]@{
        name               = $def.name
        command            = ('python -B ' + ($def.args -join ' '))
        exit_code          = $code
        expected_exit_code = $def.expect
        matched            = ($code -eq $def.expect)
        console_raw        = ('console/' + $def.name + '.raw.txt')
        console_script_log = $scriptLog
    })
    Write-Host ('[step] {0,-26} exit={1} expected={2} {3}' -f $def.name, $code, $def.expect, $(if ($code -eq $def.expect) { 'MATCH' } else { 'MISMATCH' }))
    if ($def.name -eq 'finalize') { $finalizeCode = $code }
}
Write-Observed -Steps $steps -Complete $steps.Count

$mismatches = @($steps | Where-Object { -not $_.matched })
$allMatched = ($mismatches.Count -eq 0)
$verification = [ordered]@{
    run_id           = $RunId
    generated_utc8   = (Get-Date).ToUniversalTime().AddHours(8).ToString('yyyy-MM-ddTHH:mm:ss+08:00')
    all_matched      = $allMatched
    step_count       = $steps.Count
    mismatch_count   = $mismatches.Count
    mismatches       = [object[]]$mismatches
    finalize_exit_code = $finalizeCode
    steps            = [object[]]$steps
    note             = '本文件由驱动脚本最后写入，含 finalize 自身退出码；observed_exit_codes.json 不含 finalize'
}
$verification | ConvertTo-Json -Depth 6 | Set-Content -Path (Join-Path $console 'exit_code_verification.json') -Encoding utf8

Write-Host ''
Write-Host ("[S5-C] 步骤 {0}，退出码与期望不符 {1}；finalize 退出码 {2}" -f $steps.Count, $mismatches.Count, $finalizeCode)
Write-Host ("[S5-C] 证据目录 {0}" -f $out)
if ($allMatched) { exit 0 } else { exit 1 }