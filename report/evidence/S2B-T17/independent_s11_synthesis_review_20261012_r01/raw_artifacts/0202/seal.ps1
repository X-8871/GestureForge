$ErrorActionPreference='Stop'
# 只冻结本审查目录，原始错误日志全部保留，不覆盖已有回执。
$reviewDir=Get-Item -LiteralPath $PSScriptRoot
if(-not $reviewDir.PSIsContainer -or $reviewDir.Name -cne 'independent_s11_synthesis_review_20261012_r01'){throw '审查目录不匹配'}
$workspace=Get-Item -LiteralPath 'C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition'
$encoding=New-Object System.Text.UTF8Encoding($false)
$resultFile=Get-Item -LiteralPath (Join-Path $reviewDir.FullName 'attempt3/review_result.json')
$result=Get-Content -LiteralPath $resultFile.FullName -Raw -Encoding utf8|ConvertFrom-Json
if($result.status -ne 'PASS' -or $result.checks.Count -ne 108){throw '审查结果未通过'}
$receiptPath=Join-Path $reviewDir.FullName 'final_review_receipt.json'
$rawPath=Join-Path $reviewDir.FullName 'raw_manifest.jsonl'
if((Test-Path -LiteralPath $receiptPath) -or (Test-Path -LiteralPath $rawPath)){throw '拒绝覆盖审查冻结'}
$inputs=Get-Content -LiteralPath (Join-Path $reviewDir.FullName 'attempt3/review_inputs.json') -Raw -Encoding utf8|ConvertFrom-Json
$sourceBinding=Get-Content -LiteralPath 'report/evidence/S2B-T17/s11_source_preflight_20261012_r01/source_before.json' -Raw -Encoding utf8|ConvertFrom-Json
$hashes=@{};foreach($s in $sourceBinding.source_files){$hashes[$s.path]=$s.sha256}
$record=@{status='PASS';scope=$result.scope;source_commit=$result.source_commit;reviewed_manifest_hash=$result.reviewed_manifest_hash;reviewer_stop='STOP_READONLY_S11_ACTUAL_REVIEW_FROZEN';reviewed_source_hashes=$hashes;checks_count=108;main_bindings=752;helper_bindings=760;resource_mapping_count=543;resource_copy_count=386;resource_reuse_count=157;result_path='tmp/2B/S2B-T17/independent_s11_synthesis_review_20261012_r01/attempt3/review_result.json';commands=$result.commands;native_review_attempts=@(@{attempt=1;native_exit_code=1;reason='审查脚本自身helper字段KeyError，原日志保留'},@{attempt=2;native_exit_code=2;reason='审查脚本误将collect:r02纳入checker FAIL2断言，且原址漂移与冻结副本未分开；原记录保留'},@{attempt=3;native_exit_code=0;reason='修正审查口径后108项通过'});elapsed_review_seconds=$result.elapsed_seconds;elapsed_native_attempt3_seconds=10.141;sampled_self_rss_bytes=$result.sampled_self_rss_bytes;absolute_self_peak_memory_bytes=$null;reviewer_process_tree_peak_bytes=$null;encoding_notes=$result.encoding_notes;limitations=$result.limitations;temporary_origin_drift=$result.temporary_origin_drift;git_write_performed=$false;real_task_process_query_performed=$false;heavy_or_hardware_performed=$false}
$record.limitations+=@('审查自身首轮脚本后来修正，未单独封存首轮脚本全文；原始stderr/stdout/native1保留，不声称恢复首轮源码字节。','ROOT确认当前PNR使用同一s11p1，5个gen_run.xml缓存原址已被重写；本次恢复消费正式saved_path，PNR及DCP实现消费不在此审查批准范围。','自有Python RSS采样最大114372608B低于128MiB，绝对峰及审查进程树峰未连续测量，保持null。')
[System.IO.File]::WriteAllText($receiptPath,($record|ConvertTo-Json -Depth 40)+"`n",$encoding)
$rows=@{};foreach($x in $inputs){$p=Get-Item -LiteralPath (Join-Path $workspace.FullName $x.path);$sha=(Get-FileHash -LiteralPath $p.FullName -Algorithm SHA256).Hash.ToLowerInvariant();if($sha -cne $x.sha256){throw "冻结前输入漂移 $($x.path)"};$rows[$x.path]=@{path=$x.path;sha256=$sha;role=$x.role}}
foreach($p in Get-ChildItem -LiteralPath $reviewDir.FullName -Recurse -File){if($p.FullName -eq $rawPath){continue};$relative=$p.FullName.Substring($workspace.FullName.Length+1).Replace('\','/');$role='result';if($p.Extension -in @('.py','.ps1')){$role='source'}elseif($p.Extension -eq '.log'){$role='log'}elseif($p.Name -like '*.native.json'){$role='diagnostic'};$rows[$relative]=@{path=$relative;sha256=(Get-FileHash -LiteralPath $p.FullName -Algorithm SHA256).Hash.ToLowerInvariant();role=$role}}
$lines=@();foreach($k in ($rows.Keys|Sort-Object)){if($k -match '\.(exe|obj|dcp|bit)$'){throw "清单禁止对象 $k"};$lines+=($rows[$k]|ConvertTo-Json -Compress)}
[System.IO.File]::WriteAllText($rawPath,($lines -join "`n")+"`n",$encoding)
Write-Output (@{status='PASS';reviewer_stop='STOP';receipt_sha256=(Get-FileHash -LiteralPath $receiptPath -Algorithm SHA256).Hash.ToLowerInvariant();raw_manifest_sha256=(Get-FileHash -LiteralPath $rawPath -Algorithm SHA256).Hash.ToLowerInvariant();raw_lines=$lines.Count;checks=108}|ConvertTo-Json -Compress)
