"""R2集中修复真实G1冻结；实际SOURCE内容闭合与原BLOCKED状态严格分列。"""
from datetime import datetime,timedelta,timezone
import ast,json,subprocess,sys,time
from pathlib import Path
import source_closure as c
HERE=Path(__file__).parent;ROOT=c.ROOT
assert not (HERE/'g1_receipt.json').exists()
entry=c.binding(HERE/'source_closure.py');result=c.read(HERE/'regression_result_r02.json');waits=c.read(HERE/'real_waits_r02.json')['waits']
assert result['status']=='PASS_G1_ONLY' and result['methods']==43
assert all(row['native_exit_code']==row['expected_exit_code'] and row['direct_child_wait_returned'] is True and row['tool_before']==row['tool_after']==entry for row in waits)
out=HERE/'s15_source_closure_actual_r02';closure=c.read(out/'source_closure_receipt.json')
assert closure['mcp9_sta_validation']=='NOT_IN_SCOPE' and closure['budget']['status']=='BLOCKED' and closure['budget']['continuous_budget_pass'] is False
assert [(row['original_wrapper_exit_code'],row['unknown_count']) for row in closure['captures']]==[(2,27),(2,26)]
for row in closure['raw_mapping']:
    c.bound(row['original']);c.bound(row['saved']);assert row['original']['sha256']==row['saved']['sha256']
command=[sys.executable,'-X','utf8','-B',str(ROOT/'verification/check_stage_delivery.py'),'--mode','evidence','--manifest',str(out/'delivery_manifest.json'),'--project-root',str(ROOT)]
start=time.monotonic()
with (HERE/'tmp_packaging.stdout.bin').open('xb') as stdout,(HERE/'tmp_packaging.stderr.bin').open('xb') as stderr:
    code=subprocess.run(command,cwd=ROOT,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW,timeout=20).returncode
checked=json.loads((HERE/'tmp_packaging.stdout.bin').read_bytes().decode('utf-8'))
assert code==2 and checked['errors']==['evidence_dir 必须精确等于 report/evidence/S2B-T17/'+out.name],checked
c.save(HERE/'tmp_packaging.wait.json',dict(command=command,native_exit_code=code,direct_child_wait_returned=True,elapsed_seconds=time.monotonic()-start,stdout=c.binding(HERE/'tmp_packaging.stdout.bin'),stderr=c.binding(HERE/'tmp_packaging.stderr.bin'),reason='实际TMP封包，严格要求未来正式report落点；其他绑定与格式无错误。'))
original_index=c.read(HERE/'copied_original_index.json')
for group in ('baseline_r01','review_r01'):
    for row in original_index[group]:c.bound(row['original']);c.bound(row['saved'])
for p in HERE.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
receipt=dict(status='STOP_G1_SOURCE_CLOSURE_R2_PENDING_INDEPENDENT_G2',stop=True,created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
 source_commit=c.SOURCE,implementation=entry,reviewed_entry_tools=[c.binding(p) for p in sorted(HERE.glob('*.py'))],methods=43,regression_result=c.binding(HERE/'regression_result_r02.json'),
 prior_review_receipt=c.binding(HERE/'review_r01/final_review_receipt.json'),copied_original_index=c.binding(HERE/'copied_original_index.json'),baseline_copied_files=len(original_index['baseline_r01']),review_copied_files=len(original_index['review_r01']),
 real_waits=waits,sampled_tree_peak_bytes=max(row['sampled_tree_peak_bytes'] for row in waits),elapsed_seconds_sum=sum(row['elapsed_seconds'] for row in waits),absolute_tree_peak_bytes=None,
 actual_request=c.binding(HERE/'actual_request_r01.json'),actual_source_content_closure=c.binding(out/'source_closure_receipt.json'),actual_tmp_manifest=c.binding(out/'delivery_manifest.json'),
 original_capture_states=closure['captures'],budget_status='BLOCKED',continuous_budget_pass=False,mcp9_sta_validation='NOT_IN_SCOPE',original_seal='NOT_CALLED_NOT_PASSED',entry_g2='PENDING',hardware='NOT_RUN',stage_g5='NOT_APPROVED',
 changes=['缺完整native_capture任何metadata字段拒绝，尤其target/budget/terminal/absence四项。',
 'strict native/wrapper int排除bool；六字段身份、每项终态合法状态与absence汇总一致、unknown类型与计数、metrics和原流均校验。',
 '实际before/after child0与SOURCE快照封包成功，原wrapper2/UNKNOWN27及26和guard BLOCKED不升级。',
 'additional_evidence可空；verify/receipt/CLI明确mcp9_sta_validation=NOT_IN_SCOPE，九MCP/五job/STA不属于本工具批准范围。'],
 future_cli=[sys.executable,'-X','utf8','-B',str(HERE/'source_closure.py'),'--request',str(HERE/'actual_request_r01.json'),'--output-dir','ROOT指定正式report/evidence/S2B-T17/s15_source_closure_新RunId绝对路径'],
 recovery_scope=['按actual closure.raw_mapping逐字节恢复到相同精确ROOT。封包包括固定config/freeze/46 RAW/92 snapshots/两SOURCE JSON/两native捕获及日志/admission/G1-G2 receipts/13原工具与额外r01guard actual和正式恢复副本。',
 'R2入口与request另逐字节保存；R1所有95文件和Reviewer20原件只读复制，原目录未写。',
 'guard/consumer BLOCKED及guard samples/events原件绑定保留；本入口无停止或设备动作。',
 'additional_evidence当前为空，MCP9/五job/STA完整包不在本工具恢复及批准范围；ROOT用现collector和独立design evidence完整清单另行关闭。'],
 limitations=['只工具G1，等待独立R2 G2；真实SOURCE内容闭合不追认capture、连续预算、STA、G3或G5。',
 '当前正向封包仅TMP。标准checker真实2仅因TMP不是正式report目录，其他格式/绑定无错误，不称CHECKS_OK。',
 '此前R2第一批实际成功包与最终批均保留，各自implementation原字节SHA真实不同，最终审核以本receipt最终entry为准。',
 '13原工具/config/SOURCE/ROOTclosure均未修改；无Git/ROSS/Vivado/重型/硬件；不提交。'])
c.save(HERE/'g1_receipt.json',receipt)
files=[c.binding(p) for p in sorted(HERE.rglob('*')) if p.is_file()]
c.save(HERE/'frozen_inventory.json',dict(status=receipt['status'],implementation=entry,files=files,source_commit=c.SOURCE,mcp9_sta_validation='NOT_IN_SCOPE',entry_g2=None))
print(json.dumps(dict(status=receipt['status'],entry=entry,receipt=c.binding(HERE/'g1_receipt.json'),inventory=c.binding(HERE/'frozen_inventory.json'),files=len(files)),ensure_ascii=False))
