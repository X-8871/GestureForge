$ErrorActionPreference='Stop'
# 冻结独立模拟结果，保留两轮实际原生日志，不改作者或正式证据。
$directory=Get-Item -LiteralPath $PSScriptRoot
$workspace=Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition'
if(-not $directory.PSIsContainer -or $directory.Name -cne 'independent_s11_impl_collector_review_20261012_r01'){throw '输出目录不匹配'}
$result=Get-Content -LiteralPath (Join-Path $directory.FullName 'attempt2/review_result.json') -Raw -Encoding utf8|ConvertFrom-Json
if($result.status -ne 'CHANGES_REQUIRED' -or $result.findings.Count -ne 1){throw '结果异常'}
$receipt=Join-Path $directory.FullName 'final_review_receipt.json'
$manifest=Join-Path $directory.FullName 'raw_manifest.jsonl'
if((Test-Path -LiteralPath $receipt) -or (Test-Path -LiteralPath $manifest)){throw '拒绝覆盖'}
$record=@{status='CHANGES_REQUIRED';scope=$result.scope;source_commit=$result.source_commit;reviewer_stop='STOP_READONLY_S11_PNR_COLLECTOR_PRECHECK';reviewed_source_hashes=$result.reviewed_source_hashes;checks_count=$result.checks_count;findings=$result.findings;commands=$result.commands;review_native_exit_code=2;elapsed_seconds=$result.elapsed_seconds;sampled_self_rss_bytes=$result.sampled_self_rss_bytes;absolute_peak_memory_bytes=$null;limits=$result.limitations;simulated_not_actual_pnr=$true;actual_collect_executed=$false;real_task_process_query_performed=$false;git_write_performed=$false;prepared_receipt_sha256='b8bde0c7cb5a321dcaf29b1f6fd1383234a3e72a8a0046dbd81ce1364f4a885b';candidate_raw_manifest_path='tmp/2B/S2B-T17/s11_impl_collection_20261012_r01/raw_manifest_r02.jsonl';candidate_raw_manifest_sha256='7830a57681b8234cb9aa4baa39edf225c4d3276b02a95db737d12178e559a86f';first_review_limit='首轮误用保留的旧raw_manifest.jsonl20行，原native2及结果保留；精确r02清单43行已核SHA，最终仅history双射缺陷仍阻断。'}
$encoding=New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($receipt,($record|ConvertTo-Json -Depth 30)+"`n",$encoding)
$rows=@{}
foreach($name in @('review_inputs.json','attempt2/review_inputs.json')){foreach($x in (Get-Content -LiteralPath (Join-Path $directory.FullName $name) -Raw -Encoding utf8|ConvertFrom-Json)){$p=Get-Item -LiteralPath (Join-Path $workspace.FullName $x.path);if((Get-FileHash -LiteralPath $p.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -cne $x.sha256){throw "输入漂移 $($x.path)"};$rows[$x.path]=@{path=$x.path;sha256=$x.sha256;role=$x.role}}}
foreach($p in Get-ChildItem -LiteralPath $directory.FullName -Recurse -File){$path=$p.FullName.Substring($workspace.FullName.Length+1).Replace('\','/');$role='result';if($p.Extension -in @('.py','.ps1')){$role='source'}elseif($p.Extension -eq '.log'){$role='log'}elseif($p.Name -like '*.native.json'){$role='diagnostic'};$rows[$path]=@{path=$path;sha256=(Get-FileHash -LiteralPath $p.FullName -Algorithm SHA256).Hash.ToLowerInvariant();role=$role}}
$lines=@();foreach($k in ($rows.Keys|Sort-Object)){$lines+=($rows[$k]|ConvertTo-Json -Compress)}
[System.IO.File]::WriteAllText($manifest,($lines -join "`n")+"`n",$encoding)
Write-Output (@{status='CHANGES_REQUIRED';STOP=$true;receipt_sha256=(Get-FileHash -LiteralPath $receipt -Algorithm SHA256).Hash.ToLowerInvariant();raw_sha256=(Get-FileHash -LiteralPath $manifest -Algorithm SHA256).Hash.ToLowerInvariant();raw_lines=$lines.Count;checks=$result.checks_count;rss=$result.sampled_self_rss_bytes;seconds=$result.elapsed_seconds}|ConvertTo-Json -Compress)
