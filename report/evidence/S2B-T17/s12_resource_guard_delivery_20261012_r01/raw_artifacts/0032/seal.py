"""冻结工具G2回执及严格三字段清单，不修改候选和旧审原件。"""
import hashlib,json,time
from pathlib import Path
ROOT=Path(__file__).parents[4];W=Path(__file__).parent;D=ROOT/'tmp/2B/S2B-T17/s12_resource_guard_20261012_r02'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
result=json.loads((W/'review_result.json').read_text(encoding='utf-8'));native=json.loads((W/'native_receipt.json').read_text(encoding='utf-8'));assert result['status']=='PASS' and native['native_exit_code']==0
receipt=dict(status='PASS',scope='S12_guard_r04与固定supervisor工具G2；首次观测出生时间P1关闭，轻量独立mock与自有监督替身验证；不批准真实heavy预算/STA/G3/G4/G5。',source_commit='932051cdacdf02f729d6a7554b07118d05e96aa4',reviewer_stop='STOP_NO_FURTHER_WRITES',reviewed_source_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in (D/'guard.py',D/'supervisor.py')},reviewed_tool_receipt_hash=sha(D/'tool_receipt_r04_r02.json'),reviewed_author_raw_hash=sha(D/'raw_manifest_r04_r02.jsonl'),author_bindings_verified=203,checks_count=len(result['checks']),checks=result['checks'],closed_issue=dict(priority='P1',location='guard.py:267–268',condition='候选至ROOT每条实际父子边必须parent.create_time<=child.create_time，首次观测/collect/停止四复核窗口使用同一verified_chain门禁；根以上launcher不检查。',independent_old_and_removed_gate_mutant_counterexamples_reproduced=True),command_receipts=[native],observed_child_native_code=7,observed_supervisor_return_code=2,actual_canary_scope='自有Python ROOT与import注入监督替身；所有自有进程退出且出生时间复核清理。',elapsed_seconds=native['elapsed_seconds'],sampled_owned_tree_peak_bytes=native['sampled_owned_tree_peak_bytes'],absolute_peak_memory_bytes=None,cache_budget_bytes=33554432,old_s11_budget_status='BLOCKED',production_thresholds=dict(tree_rss_bytes=6442450944,available_ram_bytes=536870912,c_disk_free_bytes=8589934592,sample_interval_seconds=1,supervision_seconds=5),limitations=result['limitations']+['r03、原PASS和首次观测CHANGES_REQUIRED原件完整保留，不覆盖旧记录。','作者首轮外层native1、成功native0及flags/sys.executable澄清分别读取，不把命令转录当执行时完整shell argv捕获。','活UNKNOWN/AccessDenied/复用/历史停止范围未扩大；工具只支持规定节拍的非原子离散监测，未采短命对象与连续峰未知。','ROOT下一轮heavy前仍须实际验证首样本/guard身份准入、每5秒并行消费终态、异常关闭后续派发及已知对象终态闭合。'])
with (W/'final_review_receipt.json').open('x',encoding='utf-8') as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write('\n')
inputs=[ROOT/p for p in result['used_inputs']]
inputs.extend([D/'guard_regression.stderr.log',D/'guard_regression.r02.stderr.log',D/'r04_run.py',D/'r04_run_r02.py',ROOT/'tmp/2B/S2B-T17/independent_s12_resource_guard_first_observation_review_20261012_r01/final_review_receipt.json',ROOT/'tmp/2B/S2B-T17/independent_s12_resource_guard_first_observation_review_20261012_r01/raw_manifest_r02.jsonl'])
files=inputs+[p for p in W.rglob('*') if p.is_file()]; unique={p.relative_to(ROOT).as_posix():p for p in files}
assert sum(p.stat().st_size for p in W.rglob('*') if p.is_file())<33554432
rows=[dict(path=k,sha256=sha(p),role='source' if p.suffix=='.py' else 'log' if p.suffix in ('.log','.jsonl') else 'result') for k,p in sorted(unique.items())]
with (W/'raw_manifest.jsonl').open('x',encoding='utf-8',newline='\n') as f:
    for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
print(json.dumps(dict(status='PASS',receipt_sha256=sha(W/'final_review_receipt.json'),raw_sha256=sha(W/'raw_manifest.jsonl'),raw_lines=len(rows)),ensure_ascii=False))
