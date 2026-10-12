"""R2 G1真实证据冻结；旧原件、失败、未知保持，不声明独立批准。"""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import ast,difflib,hashlib,json,subprocess,sys
import psutil
import compat_pins as pins
import native_contract as contract
import native_capture as native
W=Path(__file__).parent;ROOT=W.parents[3]
D=ROOT/'report/evidence/S2B-T17/s15_launch_tools_20261012_r02'
OLD=W.parent/'s15_launch_prepare_20261012_r01';REVIEW=W.parent/'independent_s15_tools_review_20261012_r01'
def bind(p):
    raw=p.read_bytes();return dict(path=p.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def save(p,value):
    with p.open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def copy(p,target):
    assert p.is_file() and not target.exists();target.parent.mkdir(parents=True,exist_ok=True)
    raw=p.read_bytes()
    with target.open('xb') as stream:stream.write(raw)
    assert bind(p)['sha256']==bind(target)['sha256']
    return dict(original=bind(p),saved=bind(target))
assert D.is_dir() and not (D/'g1_receipt.json').exists()
assert pins.SOURCE_COMMIT is None and pins.TOOLS_G2_SHA is None and pins.FUNCTIONAL_G2_SHA is None and not pins.RUNTIME_CONFIG.exists()
tests=[json.loads((W/name).read_text(encoding='utf-8')) for name in ['r2_regression_result_r03.json','extra_regression_result.json']]
assert all(row['status']=='PASS_G1_ONLY' for row in tests)
waits=json.loads((W/'r2_final_waits.json').read_text(encoding='utf-8'))['waits']
tools=contract.capture_tools(W,ROOT)
assert all(row['native_exit_code']==0 and row['direct_child_wait_returned'] is True and row['tool_bindings_before']==tools and row['tool_bindings_after']==tools for row in waits)
baseline=[];diffs=[]
for name in contract.TOOL_NAMES:
    current=W/name;ast.parse(current.read_text(encoding='utf-8'));old=OLD/name
    if old.exists():baseline.append(copy(old,D/'baseline_tools'/name))
    diff=D/'diffs'/(name+'.diff');diff.parent.mkdir(exist_ok=True)
    with diff.open('x',encoding='utf-8',newline='\n') as stream:stream.write(''.join(difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(True) if old.exists() else [],current.read_text(encoding='utf-8').splitlines(True),fromfile=str(old),tofile=str(current))))
    diffs.append(bind(diff))
    archive=D/'tools'/name
    if archive.exists():assert archive.read_bytes()==current.read_bytes()
    else:copy(current,archive)
review_inputs=[]
for name,expected in [('final_review_receipt.json','0f2d8f1d8c3150934f408673b8df2b37f7b6ef9256fb6fc93dffcc749c23e6b1'),('review_probe.py','95e0cc41baab72786829fe29e08f0bdf4d801e9bc0b8ee3c493c5c89438a50a9')]:
    p=REVIEW/name;assert bind(p)['sha256']==expected;review_inputs.append(copy(p,D/'review_inputs'/name))
native_records=[];known={}
for p in sorted(W.rglob('*.native.json')):
    row=json.loads(p.read_text(encoding='utf-8'))
    native_records.append(dict(binding=bind(p),native_exit_code=row.get('native_exit_code'),wrapper_exit_code=row.get('wrapper_exit_code'),capture_status=row.get('capture_status'),
                               direct_child_wait_returned=row.get('direct_child_wait_returned'),unknown_count=row.get('unknown_count'),budget_stop=row.get('budget_stop'),
                               elapsed_seconds=row.get('elapsed_seconds'),sampled_owned_tree_peak_bytes=row.get('sampled_owned_tree_peak_bytes')))
    identities=[row.get('launcher_identity'),row.get('direct_child_identity'),*row.get('known_descendant_identity_terminal_observations',[])]
    for identity in identities:
        if type(identity) is dict and all(key in identity for key in contract.IDENTITY_KEYS):known[(identity['pid'],identity['create_time'])]={key:identity[key] for key in contract.IDENTITY_KEYS}
terminal=[native.read_identity(identity) for identity in known.values()]
assert terminal and all(row['same_identity_exists'] is False for row in terminal),terminal
save(W/'known_owned_terminal_readback.json',dict(status='ALL_KNOWN_ORIGINAL_IDENTITIES_ABSENT',identities=terminal,actions=[],entire_os_tree='NOT_PROVEN',short_lived_unsampled='NOT_PROVEN'))
raw=[copy(p,D/'raw'/p.relative_to(W)) for p in sorted(W.rglob('*')) if p.is_file()]
head=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,check=True).stdout.decode('ascii').strip()
receipt=dict(status='STOP_G1_TOOLS_PENDING_INDEPENDENT_G2',stop=True,created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
 baseline_commit='0700c33e6faba8861cc2e7646a8981e424a69c45',observed_current_head=head,actual_production_source_freeze=None,tools_g2=None,
 functional_g2_pin=None,expected_profile='s2b-inference-platform/0.1.15',production_tool_count=len(tools),reviewed_tools=tools,
 additional_check_tools=[bind(p) for p in sorted(W.glob('*.py')) if p.name not in contract.TOOL_NAMES],test_results=tests,
 unique_methods=sum(row['methods'] for row in tests),real_waits=waits,native=native_records,
 sampled_owned_tree_peak_bytes=max(row['sampled_tree_peak_bytes'] for row in waits),wrapper_elapsed_seconds_sum=sum(row['elapsed_seconds'] for row in waits),
 known_owned_original_identities_absent=len(terminal),terminal_readback=bind(W/'known_owned_terminal_readback.json'),
 mapping=bind(D/'archive_mapping.json'),recovery=bind(D/'recovery_entry.json'),layout=bind(D/'runtime_pin_layout.json'),
 prior_independent_review=review_inputs,baseline_bindings=baseline,diffs=diffs,raw_bindings=raw,
 runtime_cli=['python -X utf8 -B WORK/native.py --prefix s15_runtime_prepare_rN -- prepare',
 'python -X utf8 -B WORK/native.py --prefix s15_runtime_source_before_rN -- source --commit SOURCE --phase before',
 'python -X utf8 -B WORK/native.py --prefix s15_runtime_source_after_rN -- source --commit SOURCE --phase after',
 'python -X utf8 -B WORK/native.py --prefix s15_runtime_collect_rN -- collect --commit SOURCE --gate OLD_GATE_ABSOLUTE',
 'python -X utf8 -B WORK/native.py --prefix s15_runtime_seal_rN -- seal --commit SOURCE --gate NEW_GATE_ABSOLUTE'],
 metadata_changes=['原生结果增加wrapper_exit_code/capture_status/capture_target_kind；工具集合固定13，不再glob。',
 'collect绑定consumed_gate/consumed_gate_after/collection_summary；source成功绑定source_output；identity、wait、unknown、budget、完整argv、日志实际字节均必须一致。',
 '旧门禁原字节不改。新seal门禁全部字段相同仅显式扩展native_wrappers，summary中closed_gate_inputs绑定实际消费旧门禁。',
 'ROOT自有capture_owned_run/check_ready/phase CLI未改；runtime source/collect/seal沿用同CLI，生产metadata由native.py本身实际生成。'],
 failures_preserved=['r02首轮pending prepare native1/wrapper2 UNKNOWN；conhost活至wrapper结束和身份漂移未被追认成功。',
 '两个先前完整成功逻辑fixture批次和当前批次全部保留，早期工具SHA与最终工具不同按实际记录，不将其作为最终tool closure PASS。'],
 limitations=['本轮40项仅工具G1；独审工具G2、真实SOURCE冻结、实际综合监护、连续预算及硬件均未执行。',
 '真实production prepare PENDING native1/wrapper1且unknown0仅表示错误被完整捕获；成功source/collect链是显式fixture。',
 '实际进程身份/原流/直接wait是真实原件，fixture状态不能授予生产SOURCE或G2。',
 '峰值仅离散采样；已知原身份ABSENT不证明整个OS树或未采短命对象闭合。',
 'S14原351raw/348valid/3unclosed保留失败；没有放宽guard/SUP预算、max3或UNKNOWN规则。',
 'Parent已报告功能提交及独审通过，本工具compat pin尚未绑定正式功能receipt；SOURCE只待ROOT真实冻结。',
 '仅自有隐藏轻量进程与只读状态，没有Vivado/ROSS/MCP/大型编译/JTAG/串口/实物访问；不提交。'])
save(D/'g1_receipt.json',receipt)
files=[]
for p in sorted(D.rglob('*')):
    if p.is_file():files.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=bind(p)['sha256'],role='source' if p.suffix=='.py' else 'log' if p.suffix in ('.bin','.diff') else 'result'))
checks=[dict(name='r2_metadata_29_and_layout_tools_11',status='PASS',command=subprocess.list2cmdline([sys.executable,'-X','utf8','-B',str(W/'run_checks.py')]),exit_code=0,reason='真实direct wait0；40项轻量G1，fixture与production PENDING失败分列。')]
checks += [dict(name=name,status='NOT_RUN',command=None,exit_code=None,reason='工具G1不能替代ROOT实际SOURCE、独审、综合或硬件。') for name in ['独立工具G2','实际SOURCE冻结与综合监护','G3实物及G5']]
manifest=dict(schema_version=1,stage='2B',task_id='S2B-T17',run_id=D.name,source_commit=head,evidence_dir=D.relative_to(ROOT).as_posix(),
 interfaces=[],interfaces_not_applicable_reason='隔离工具G1未改生产模型或硬件接口；完整身份及资源预算由本轮任务授权固定。',tool_versions=dict(python=sys.version,psutil=psutil.__version__),
 files=files,checks=checks,limitations=receipt['limitations']+['source_commit为冻结时观察到的仓库HEAD，生产SOURCE清单尚未绑定，不声明已消费真实源码冻结。'])
save(D/'delivery_manifest.json',manifest)
print(json.dumps(dict(status=receipt['status'],files=len(files),bytes=sum(p.stat().st_size for p in D.rglob('*') if p.is_file()),receipt=bind(D/'g1_receipt.json'),manifest=bind(D/'delivery_manifest.json'),tools=tools,known_original_absent=len(terminal)),ensure_ascii=False))
