$ErrorActionPreference='Stop'
# 仅冻结本轮隔离复审，不改候选或旧审查包。
$directory=Get-Item -LiteralPath $PSScriptRoot
$workspace=Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition'
if(-not $directory.PSIsContainer -or $directory.Name -cne 'independent_s11_impl_collector_review_20261012_r02'){throw '目录不匹配'}
$result=Get-Content -LiteralPath (Join-Path $directory.FullName 'attempt2/review_result.json') -Raw -Encoding utf8|ConvertFrom-Json
if($result.status -ne 'PASS' -or $result.checks_count -ne 51){throw '结果未通过'}
$receipt=Join-Path $directory.FullName 'final_review_receipt.json';$manifest=Join-Path $directory.FullName 'raw_manifest.jsonl'
if((Test-Path -LiteralPath $receipt) -or (Test-Path -LiteralPath $manifest)){throw '拒绝覆盖'}
$record=@{status='PASS';scope=$result.scope;source_commit=$result.source_commit;reviewer_stop='STOP_READONLY_PNR_COLLECTOR_REPAIR_REVIEW';reviewed_source_hashes=$result.reviewed_source_hashes;checks_count=51;history_mock_count=13;adapter_inmemory_mock_count=9;raw_candidate_bindings=82;original_P1='CLOSED_BY_INDEPENDENT_MOCK';findings=@();commands=$result.commands;review_native_exit_code=0;elapsed_seconds=$result.elapsed_seconds;sampled_self_rss_bytes=$result.sampled_self_rss_bytes;absolute_peak_memory_bytes=$null;actual_git_queries=0;actual_source_after_or_collect_executed=$false;real_task_process_query_performed=$false;heavy_or_hardware_performed=$false;limitations=$result.limitations;first_attempt=@{native_exit_code=1;reason='独立审查脚本误读freeze中的derived_sources字段；正确字段在board profile。首轮完整脚本和stdout/stderr/native保留。'};prepared_receipt_sha256='dc9d17810fcbbabbf51e14545b3fabe5fa3a29724fd6320bbc13fa2bd8443c04';tool_receipt_sha256='7e9217313f302ffc1d0b8fd64d6507a212e9243489741206e0e26888504d36c8';candidate_raw_manifest_sha256='5bd67dd972646252da8a0207670f449c0a1a4aa25f024916a601f93b9da5ed95'}
$encoding=New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($receipt,($record|ConvertTo-Json -Depth 30)+"`n",$encoding)
$rows=@{}
foreach($x in (Get-Content -LiteralPath (Join-Path $directory.FullName 'attempt2/review_inputs.json') -Raw -Encoding utf8|ConvertFrom-Json)){$p=Get-Item -LiteralPath (Join-Path $workspace.FullName $x.path);if((Get-FileHash -LiteralPath $p.FullName -Algorithm SHA256).Hash.ToLowerInvariant() -cne $x.sha256){throw "输入漂移 $($x.path)"};$rows[$x.path]=@{path=$x.path;sha256=$x.sha256;role=$x.role}}
$common=Get-Item -LiteralPath 'tmp/2B/S2B-T17/s11_collection_20261012_r01/collector.py';$relative=$common.FullName.Substring($workspace.FullName.Length+1).Replace('\','/');$rows[$relative]=@{path=$relative;sha256=(Get-FileHash -LiteralPath $common.FullName -Algorithm SHA256).Hash.ToLowerInvariant();role='source'}
foreach($p in Get-ChildItem -LiteralPath $directory.FullName -Recurse -File){$relative=$p.FullName.Substring($workspace.FullName.Length+1).Replace('\','/');$role='result';if($p.Extension -in @('.py','.ps1')){$role='source'}elseif($p.Extension -eq '.log'){$role='log'}elseif($p.Name -like '*.native.json'){$role='diagnostic'};$rows[$relative]=@{path=$relative;sha256=(Get-FileHash -LiteralPath $p.FullName -Algorithm SHA256).Hash.ToLowerInvariant();role=$role}}
$lines=@();foreach($k in ($rows.Keys|Sort-Object)){$lines+=($rows[$k]|ConvertTo-Json -Compress)}
[System.IO.File]::WriteAllText($manifest,($lines -join "`n")+"`n",$encoding)
Write-Output (@{status='PASS';STOP=$true;receipt_sha256=(Get-FileHash -LiteralPath $receipt -Algorithm SHA256).Hash.ToLowerInvariant();raw_sha256=(Get-FileHash -LiteralPath $manifest -Algorithm SHA256).Hash.ToLowerInvariant();raw_lines=$lines.Count;checks=51;rss=$result.sampled_self_rss_bytes;seconds=$result.elapsed_seconds}|ConvertTo-Json -Compress)
