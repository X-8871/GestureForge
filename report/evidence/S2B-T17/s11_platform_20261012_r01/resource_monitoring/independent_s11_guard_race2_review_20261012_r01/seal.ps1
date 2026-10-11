$ErrorActionPreference = 'Stop'
$reviewBase = Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition\tmp\2B\S2B-T17\independent_s11_guard_race2_review_20261012_r01'
$projectRoot = Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition'
if (!$reviewBase.PSIsContainer -or !$projectRoot.PSIsContainer) { throw '精确目录类型错误' }
$reviewResult = Get-Content -LiteralPath (Join-Path $reviewBase.FullName 'attempt2\review_result.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$firstNative = Get-Content -LiteralPath (Join-Path $reviewBase.FullName 'review.native.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$finalNative = Get-Content -LiteralPath (Join-Path $reviewBase.FullName 'review_attempt2.native.json') -Encoding UTF8 -Raw | ConvertFrom-Json
$headNative = Get-Content -LiteralPath (Join-Path $reviewBase.FullName 'attempt2\head.native.json') -Encoding UTF8 -Raw | ConvertFrom-Json
if ($reviewResult.status -ne 'PASS' -or $firstNative.native_exit_code -ne 1 -or $finalNative.native_exit_code -ne 0 -or $headNative.native_exit_code -ne 0) { throw '实际原生结果不符' }
$entryMap = @{}
$inputRows = Get-Content -LiteralPath (Join-Path $reviewBase.FullName 'attempt2\review_inputs.json') -Encoding UTF8 -Raw | ConvertFrom-Json
foreach ($row in $inputRows) {
    $entryMap[$row.path] = [ordered]@{ path=$row.path; sha256=$row.sha256; role=$row.role }
}
foreach ($reviewFile in (Get-ChildItem -LiteralPath $reviewBase.FullName -Recurse -File)) {
    if ($reviewFile.Extension.ToLowerInvariant() -in @('.exe','.obj','.dcp','.bit','.pyc')) { throw '不得纳入缓存产物' }
    $relativePath = $reviewFile.FullName.Substring($projectRoot.FullName.Length + 1).Replace('\','/')
    $fileRole = if ($reviewFile.Extension -in @('.py','.ps1')) { 'source' } elseif ($reviewFile.Extension -eq '.log') { 'log' } elseif ($reviewFile.Name -match 'timeout') { 'diagnostic' } else { 'result' }
    $entryMap[$relativePath] = [ordered]@{ path=$relativePath; sha256=(Get-FileHash -LiteralPath $reviewFile.FullName -Algorithm SHA256).Hash.ToLowerInvariant(); role=$fileRole }
}
$rawPath = Join-Path $reviewBase.FullName 'raw_manifest.jsonl'
$receiptPath = Join-Path $reviewBase.FullName 'final_review_receipt.json'
if ((Test-Path -LiteralPath $rawPath) -or (Test-Path -LiteralPath $receiptPath)) { throw '新冻结目标已存在，拒绝覆盖' }
$utf8 = New-Object System.Text.UTF8Encoding($false)
$rawLines = foreach ($key in ($entryMap.Keys | Sort-Object)) { $entryMap[$key] | ConvertTo-Json -Compress }
[System.IO.File]::WriteAllText($rawPath, ($rawLines -join "`n") + "`n", $utf8)
$rawHash = (Get-FileHash -LiteralPath $rawPath -Algorithm SHA256).Hash.ToLowerInvariant()
$reviewResult | Add-Member -NotePropertyName commands -NotePropertyValue @($firstNative,$finalNative,$headNative) -Force
$reviewResult | Add-Member -NotePropertyName reviewer_auxiliary_failure -NotePropertyValue ([ordered]@{ native_exit_code=1; cause='首轮独立mock命名空间缺少psutil.__version__；仅修正审查包装，在新attempt2执行'; evidence='review.stderr.log'; candidate_changed=$false }) -Force
$reviewResult | Add-Member -NotePropertyName approval_timeouts -NotePropertyValue @([ordered]@{ evidence='launch_initial_timeout.json'; execution_started=$false; native_exit_code=$null },[ordered]@{ evidence='launch_attempt2_timeout.json'; execution_started=$false; native_exit_code=$null }) -Force
$reviewResult | Add-Member -NotePropertyName raw_manifest_sha256 -NotePropertyValue $rawHash -Force
$reviewResult | Add-Member -NotePropertyName raw_manifest_lines -NotePropertyValue $entryMap.Count -Force
$reviewResult.reviewer_stop = 'STOP_READONLY_S11_G_RACE2_REVIEW_FROZEN'
[System.IO.File]::WriteAllText($receiptPath, ($reviewResult | ConvertTo-Json -Depth 30) + "`n", $utf8)
Write-Output ([ordered]@{ status='PASS'; STOP=$true; receipt_sha256=(Get-FileHash -LiteralPath $receiptPath -Algorithm SHA256).Hash.ToLowerInvariant(); raw_manifest_sha256=$rawHash; raw_manifest_lines=$entryMap.Count } | ConvertTo-Json -Compress)
