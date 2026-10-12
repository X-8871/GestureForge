"""固定R2工具独审结果；明确保留实际r01守卫运行及恢复依赖。"""
import hashlib
import json
from pathlib import Path
from datetime import datetime,timezone,timedelta
HERE=Path(__file__).parent;ROOT=HERE.parents[3]
W=ROOT/'tmp/2B/S2B-T17/s15_launch_prepare_20261012_r02'
PACKAGE=ROOT/'report/evidence/S2B-T17/s15_launch_tools_20261012_r02'
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def row(path):
    assert path.is_file()
    return dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
result=read(HERE/'review_r2_result.json');layout=read(HERE/'source_layout_probe_result.json');g1=read(PACKAGE/'g1_receipt.json')
assert result['status']=='PASS_TOOL_G2_ONLY' and len(result['checks'])==50 and all(r['status']=='PASS' for r in result['checks'])
assert len(layout['checks'])==4 and all(r['passed'] for r in layout['checks'])
assert len(g1['reviewed_tools'])==13 and all(row(ROOT/r['path'])==r for r in g1['reviewed_tools'])
guard=ROOT/'tmp/2B/S2B-T17/s15_launch_prepare_20261012_r01/guard.py'
artifact=ROOT/'report/evidence/S2B-T17/s15_launch_tools_20261012_r01/tools/guard.py'
expected='e055276318f6e215981bdceadb437ebe2bf50ec160b8d93c2d11c33bc89f886f'
assert row(guard)['sha256']==row(artifact)['sha256']==row(W/'guard.py')['sha256']==expected
assert guard.read_bytes()==artifact.read_bytes()==(W/'guard.py').read_bytes()
runtime_dependency=dict(actual_run_path=row(guard),formal_recovery_copy=row(artifact),r02_reviewed_copy=row(W/'guard.py'),same_bytes_verified=True,
    root_decision='ROOT明确保留r01运行依赖而不修改已审13工具；不声明仅13对象可独立恢复。',
    root_required_binding='ROOT已承诺source_freeze新增tool_runtime_dependencies，并在SOURCE-before/after及closed_gate绑定实际r01守卫和正式副本；ROOT ready检查SUP实际GUARD与r02副本同字节和固定SHA，argv使用真实r01路径。',
    actual_source_freeze_binding='PENDING_ROOT_REAL_SOURCE_FREEZE_NOT_CREATED_BY_REVIEWER')
receipt=dict(status='PASS_TOOL_G2_ONLY',stop=True,created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),baseline_commit=result['baseline_commit'],
    reviewed_manifest=result['formal_manifest'],reviewed_g1_receipt=result['g1_receipt'],reviewed_tools=g1['reviewed_tools'],production_tool_count=13,
    tool_runtime_dependencies=[runtime_dependency],independent_checks=55,checks_summary=dict(r2_schema_gate_native_checks=50,source_layout_fixture_checks=4,r01_runtime_recovery_dependency_bytes=1),
    g1_reviewed_cases=40,g1_formal_files_hash_checked=200,r1_p1_closed=True,r1_five_counterexamples_rejected=True,
    valid_gate_chain='PASS_LOGICAL_FIXTURE_WITH_TRUE_NATIVE_CAPTURE_METADATA: immutable gate_r01 -> collect -> new gate_r02 explicit native_wrappers extension; oldgate unchanged',
    actual_production_pending_prepare=dict(child_native_exit_code=1,wrapper_exit_code=1,capture_status='CLOSED_NATIVE_CHILD_FAILURE',not_source_approval=True),
    fixture_source_before_after_collect=dict(real_child_native_exit_codes=[0,0,0],real_wrapper_exit_codes=[0,0,0],source_gate_semantics='EXPLICIT_FIXTURE_ONLY'),
    independent_native=result['native'],tool_source_hashes_unchanged_at_stop=True,
    production_source_actual='PENDING',actual_s15_sta='NOT_RUN',actual_continuous_budget='NOT_PROVEN',actual_hardware_g3_g4_g5='NOT_RUN',
    functional_g2='ROOT_SEPARATELY_APPROVED_NOT_REVIEWED_HERE',
    evidence=[row(HERE/name) for name in ('review_r2.py','review_r2_result.json','source_layout_probe.py','source_layout_probe_result.json','review_r2_native.native.json')],
    limits=dict(tree_rss_limit_bytes=6*1024**3,available_ram_stop_bytes=512*1024**2,c_free_minimum_bytes=8*1024**3,sample_seconds=1,supervisor_seconds=5,consumer_seconds=5,consumer_hard_freshness_seconds=10,closure_same_alive_rounds=2,closure_max_rounds=3),
    findings=[],
    limitations=['G2仅批准冻结工具软件行为；未执行Vivado/ROSS、综合、PNR、串口/JTAG或大型编译，未证明实际S15预算/STA/部署/G3-G5。',
                '本次独立真实canary只输出并退出，child和wrapper0、直接wait、unknown0及离散峰52,793,344B；整OS树和绝对连续峰仍NOT_PROVEN。',
                '工具SOURCE/功能G2/工具G2运行pin仍待ROOT真实冻结，不能把prepare PENDING1或fixture SOURCE0改称生产SOURCE批准。',
                '保留R1原失败和R2真实UNKNOWN失败；旧S14 351raw/348valid/3unclosed与FAIL_TIMING不后验重分类。',
                'SOURCE-before创建PRE/REPORT和防覆盖独立测试仅逻辑fixture；实际PRE/REPORT尚未由Reviewer创建。',
                '监督器实际执行r01 guard，而13工具映射恢复r02 copy；ROOT明确绑定并保留额外r01依赖，恢复必须一起恢复所声明路径。',
                '未修改被审13工具、ROOT closure、共享分支或提交。'])
save(HERE/'final_review_receipt.json',receipt)
files=[row(path) for path in sorted(HERE.rglob('*')) if path.is_file()]
save(HERE/'original_file_index.json',dict(status='STOP_REVIEW_ORIGINALS_INDEXED',files=files,root=str(HERE)))
print(json.dumps(dict(status=receipt['status'],receipt=row(HERE/'final_review_receipt.json'),index=row(HERE/'original_file_index.json'),original_files=len(files),independent_checks=55),ensure_ascii=False))
