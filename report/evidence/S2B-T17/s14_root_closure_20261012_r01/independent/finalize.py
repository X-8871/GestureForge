import datetime
import hashlib
import json
import pathlib
import subprocess

# 固定独审回执，只写本次隔离目录并停止写入。
root = pathlib.Path.cwd()
out = pathlib.Path(__file__).parent
r = root / 'report/evidence/S2B-T17/s14_root_closure_20261012_r01'
p = root / 'report/evidence/S2B-T17/s14_platform_20261012_r01'
c = p / 'mcp_closed'
base = '53772ae581ff3ccfb3a9d411cdc66fc67c3e2161'
def read(x):
    return json.loads(x.read_text(encoding='utf-8'))
def sha(x):
    return hashlib.sha256(x.read_bytes()).hexdigest()
def save(name, data):
    (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

manifest = read(r / 'delivery_manifest.json')
before = read(out / 'original449_hash_index.json')
after = {x['path']:sha(root / x['path']) for x in manifest['files']}
assert before == after
head = subprocess.check_output(['C:/Program Files/Git/cmd/git.exe', 'rev-parse', 'HEAD'], text=True).strip()
assert head == base
details = []
for path, want in read(c / 'source_before.json')['source_sha256'].items():
    raw = subprocess.check_output(['C:/Program Files/Git/cmd/git.exe', 'show', base + ':' + path])
    actual = (root / path).read_bytes()
    assert hashlib.sha256(actual).hexdigest() == want
    assert raw == actual or raw.replace(b'\r\n', b'\n') == actual.replace(b'\r\n', b'\n')
    details.append({'path':path, 'sha256':want, 'git_raw_sha256':hashlib.sha256(raw).hexdigest(), 'mode':'RAW_EXACT' if raw == actual else 'EOL_ONLY_EXACT'})
assert sum(x['mode'] == 'RAW_EXACT' for x in details) == 39
h = read(out / 'mcp_independent.json')
assert h['raw_history']['history'] == [x['native_history'] for x in read(p / 's14_mcp_binding.json')['paired_calls']]
assert [x['label'] for x in h['paired_summary']] == ['source','builder','setup','launch','wait','open_run','reports','query_xdc','close']
comp = read(r / 'host_execution_receipts.json')
assert [comp[x]['exit_code'] for x in ['source_after','collect_r01','collect_r02','collect_r03_terminal','seal_r01']] == [0,1,1,0,1]
assert comp['collect_r03_initial']['session_id'] == 23770
products = (p / 'products.tcldict').read_text(encoding='utf-8')
assert 'native_counts_before {WARNING 9' in products and 'native_counts_after {WARNING 1' in products
assert (p / 'constraints_synth.xdc').read_text(encoding='utf-8').count('set_false_path') == 2
native_tcl = (p / 'native_jobs/s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl').read_text(encoding='utf-8', errors='replace')
save('source_final_independent.json', {'source_commit':base,'details':details,'descriptor_package_reference_in_native_tcl':'s2a_network_descriptor_pkg.sv' in native_tcl,'original449_final_equal':True})
save('review_artifact_index.json', {x.relative_to(root).as_posix():sha(x) for x in out.iterdir() if x.is_file() and x.name not in ['review_artifact_index.json','final_review_receipt.json']})
summary = read(p / 's14_collection_summary.json')
receipt = {
    'status':'PASS_EVIDENCE_INTEGRITY_ONLY',
    'review_task':'S14-ACTUAL-G2',
    'reviewer_stop':True,
    'created_at_utc8':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
    'source_commit':base,
    'actual_head':head,
    'original_manifest_sha256':sha(r / 'delivery_manifest.json'),
    'canonical_manifest_sha256':sha(r / 'delivery_manifest_r02.json'),
    'original449_before_after_equal':True,
    'canonical453_additional_four_verified':True,
    'actual_final_receipt_sha256':sha(r / 'final_actual_receipt.json'),
    'host_execution_receipts_sha256':sha(r / 'host_execution_receipts.json'),
    'source_counts':{'all':45,'static':33,'original_frozen_rtl':14,'active_compiled_rtl':18,'git_raw_exact':39,'git_eol_only_exact':6},
    'history_calls':[{'label':x['label'],'id':x['native_id'],'code':x['native_code'],'elapsed_seconds':x['elapsed']} for x in h['paired_summary']],
    'products_count':1,'synth_launch_count':1,'wait_count':1,'wait_native_exit_code':0,
    'native_jobs_log_marker_count':5,'native_job_raw_os_exit_codes':None,
    'timing':summary['timing'],'resources':summary['resources'],'worst_path':summary['worst_path'],
    'false_path_count':2,
    'monitor':read(out / 'monitor_independent.json'),
    'monitor_raw_sample_count':351,'monitor_unclosed_sample_count':3,'monitor_valid_sample_count':348,
    'sampled_valid_tree_peak_bytes':5223079936,'absolute_tree_peak_bytes':None,
    'continuous_budget_status':'NOT_PROVEN_THREE_BLOCKED_GUARD_ROUNDS_AND_GAPS',
    'root_identity':{'pid':19192,'create_time':1791777476.053502,'status':'ABSENT'},
    'known_identities':{'count':30,'status':'ALL_ABSENT_DISCRETE_OBSERVATION_ONLY'},
    'entire_os_tree_terminal':'NOT_PROVEN',
    'xsa_member_comparison':read(out / 'xsa_members_independent.json'),
    'runtime_elf_bsp_compatibility':'NOT_APPROVED',
    'packing_child_exit_codes':{'collect_r01':2,'collect_r02':1,'collect_r03':0,'sta_classifier':2,'seal_r01':1},
    'packing_host_exit_codes':{'source_after':0,'collect_r01':1,'collect_r02':1,'collect_r03_terminal':0,'seal_r01':1},
    'collector_r03_running_session':23770,
    'observer_initial_failure':'TypeError: None > 1；native1；原始脚本与修正后的只读观察均保存。',
    'seal_initial_failure':'KeyError mode；旧G1 native metadata缺mode/prefix；固定工具未改，不宣称seal成功。',
    'canonical_evidence_check':read(out / 'canonical_evidence_actual.json'),
    'original_manifest_checks':read(out / 'checker_unsandboxed_actual.json'),
    'sandbox_original_checks':read(out / 'checker_actual.json'),
    'products_count_verification':{
        'location':'report/evidence/S2B-T17/s14_platform_20261012_r01/s14_mcp_binding.json/products_warning_before',
        'summary_before':read(p / 's14_mcp_binding.json')['products_warning_before'],
        'summary_after':read(p / 's14_mcp_binding.json')['products_warning_after'],
        'summary_sha256':sha(p / 's14_mcp_binding.json'),
        'raw_before':9,'raw_after':1,
        'primary':'report/evidence/S2B-T17/s14_platform_20261012_r01/products.tcldict',
        'disposition':'摘要实际为单元素列表[9]与[1]，与原件9→1一致；先前Reviewer预览误将列表长度1当作值，本回执撤回错误发现；不需正式更正addendum。'
    },
    'stage2b_g3_g4_g5':'NOT_PASSED','implementation':'NOT_RUN','postroute':'NOT_RUN','hardware':'NOT_RUN',
    'scope_limits':[
        '仅审查SOURCE53772的S14失败证据真实性；不批准STA、连续预算、ELF/BSP、部署或G3-G5。',
        '历史审计追加绑定只核对精确hash，不重新执行或扩大为项目终身综合统计。',
        '实际evidence包装0仅针对453files canonical；原manifest含未列companion时实际为2。',
        '单进程/完整OS退出码和峰值未捕获字段均为null。'
    ],
    'artifact_index_sha256':sha(out / 'review_artifact_index.json'),
    'final_packaging_conditions':[
        'ROOT追加独审原件时须列入最终canonical，并再次只读evidence检查；保持原449件/r01manifest hash不变。'
    ]
}
save('final_review_receipt.json',receipt)
print('RECEIPT_SHA256',sha(out / 'final_review_receipt.json'))
print('INDEX_SHA256',sha(out / 'review_artifact_index.json'))
print('STOP')
