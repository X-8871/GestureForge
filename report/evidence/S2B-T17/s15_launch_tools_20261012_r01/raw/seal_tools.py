"""冻结新S15工具G1与全部原生失败原件；生产SOURCE和独审G2保持待冻结。"""
from datetime import datetime,timedelta,timezone
from pathlib import Path
import difflib
import hashlib
import json
import shutil
import subprocess
import sys
import psutil
import compat_pins as pins

W=Path(__file__).parent;ROOT=W.parents[3]
D=ROOT/'report/evidence/S2B-T17/s15_launch_tools_20261012_r01'
OLD=W.parent/'s14_launch_prepare_20261012_r01'
RUN=W.parent/'s14_physical_launch_root_20261012_r01'
BASE='0700c33e6faba8861cc2e7646a8981e424a69c45'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def binding(p):return dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),bytes=p.stat().st_size)
def save(p,value):
    with p.open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def copy(p,target):
    assert p.is_file() and not target.exists()
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as stream:stream.write(p.read_bytes())
    assert sha(p)==sha(target)
    return dict(original=binding(p),saved=binding(target))

assert D.is_dir() and not (D/'g1_receipt.json').exists()
assert pins.SOURCE_COMMIT is None and pins.FUNCTIONAL_G2_SHA is None and pins.TOOLS_G2_SHA is None and not pins.RUNTIME_CONFIG.exists()
tests={name:json.loads((W/name).read_text(encoding='utf-8')) for name in [
    'boundary_regression_result.json','selftest_result_r03.json','monitor_fixture_result.json',
    'collector_fixture_result_r03.json','s15_regression_result_r03.json','final_checks_result_r02.json']}
assert all(value['status'].startswith('PASS') for value in tests.values())
tools=[binding(p) for p in sorted(W.glob('*.py'))]
baseline=json.loads((W/'s14_diagnostic.json').read_text(encoding='utf-8'))
oldcopies=[];diffs=[]
for row in baseline['original_tools']:
    original=ROOT/row['original']['path'];assert binding(original)==row['original']
    oldcopies.append(copy(original,D/'baseline_tools'/original.name))
    current=W/('s15_regressions.py' if original.name=='s14_regressions.py' else original.name)
    path=D/'diffs'/(current.name+'.diff');path.parent.mkdir(exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(''.join(difflib.unified_diff(original.read_text(encoding='utf-8').splitlines(True),current.read_text(encoding='utf-8').splitlines(True),fromfile=str(original),tofile=str(current))))
    diffs.append(binding(path))
oldruntime=[]
for r in ('01','02','03'):
    for sub in ('guard/samples.jsonl','guard/events.jsonl','guard/guard_receipt.json','supervisor_receipt.json'):
        p=RUN/('supervision_r'+r)/sub;oldruntime.append(copy(p,D/'s14_original_runtime'/('supervision_r'+r)/sub))
    p=RUN/('native_consumer_r'+r)/'consumer_receipt.json';oldruntime.append(copy(p,D/'s14_original_runtime'/('native_consumer_r'+r)/p.name))
for prefix in ('s14_collect_r01','s14_collect_r02','s14_collect_r03','s14_seal_r01'):
    for suffix in ('.native.json','.stdout.bin','.stderr.bin'):
        p=OLD/(prefix+suffix);oldruntime.append(copy(p,D/'s14_collector_failures'/p.name))
for name in ('closed_inputs_gate.json','closed_inputs_gate_r02.json','gate_identifier_correction.json'):
    p=RUN/name;oldruntime.append(copy(p,D/'s14_collector_failures'/p.name))
raw=[copy(p,D/'raw'/p.relative_to(W)) for p in sorted(W.rglob('*')) if p.is_file()]
native=[]
for p in sorted(W.glob('*.native.json')):
    r=json.loads(p.read_text(encoding='utf-8'))
    native.append(dict(binding=binding(p),native_exit_code=r.get('native_exit_code'),elapsed_seconds=r.get('elapsed_seconds'),
                       sampled_owned_tree_peak_bytes=r.get('sampled_owned_tree_peak_bytes'),unknown_count=r.get('unknown_count'),
                       direct_child_wait_returned=r.get('direct_child_wait_returned'),tool_prepost_bound='tool_bindings_before' in r,
                       tools_prepost_equal=r.get('tool_bindings_before')==r.get('tool_bindings_after') if 'tool_bindings_before' in r else None))
receipt=dict(status='STOP_G1_TOOLS_PENDING_INDEPENDENT_G2',created_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
    baseline_commit=BASE,actual_production_source_commit=None,expected_profile='s2b-inference-platform/0.1.15',
    functional_g2=None,tools_g2=None,actual_runtime='NOT_RUN',actual_continuous_budget='NOT_RUN',
    tools=tools,diffs=diffs,test_results=tests,unique_methods=77,native=native,
    mapping=binding(D/'archive_mapping.json'),recovery=binding(D/'recovery_entry.json'),
    sampled_owned_tree_peak_bytes=max(r['sampled_owned_tree_peak_bytes'] or 0 for r in native),
    wrapper_elapsed_seconds_sum=sum(r['elapsed_seconds'] or 0 for r in native),tool_call_count=None,
    baseline_bindings=oldcopies,s14_raw_bindings=oldruntime,raw_bindings=raw,
    source_before='PENDING',source_count='ROOT_ACTUAL_FREEZE_REQUIRED',static_count=33,active_rtl_count=18,frozen_original_count=14,
    changes=['活集合只比较连续两轮pid/birth完全相等，退出原件单列不再额外veto；max3和unknown阻断保持。',
             '每个重扫保存活集合、unknown与退出原件；真实持续出生仍BLOCKED。',
             '末表父ABSENT窗口再核子；确认原对象退出则删除活集合项，未知与漂移阻断。',
             '停止准备确认退出只列ALREADY_EXITED；动作前完整现时祖先链复查仍保留。',
             'collector只接收显式native_wrappers、专用s15_runtime_标签、完整schema/mode/命令/闭合流。',
             '仅approved_evidence相对identifier转换为POSIX，真实FS路径不规范化。',
             'native采集记录真实直接wait/原流与工具集合前后哈希，预算停止前重核launcher及子六字段/birth父关系。',
             '新profile/SOURCE/功能G2/工具G2严格绑定，未知SOURCE/G2仍PENDING。'],
    failures_preserved=['S14 collect误--closed-gate native2、approved_evidence反斜杠绑定native1、旧G1无mode混收seal native1全部原件复制。',
                        'S15 selftest r01 hidden CREATE_NO_WINDOW创建conhost并被严格cwd门禁阻断；r02旧diff名称冲突；r03 DETACHED_PROCESS自有canary成功。',
                        'S15 monitor r01缺fixture helper，r02旧guard静态SHA，r03补齐后真实0。'],
    limitations=['G1不等于独立G2/真实运行监护通过；S14 351raw/348valid/3unclosed保持失败，不追认连续预算PASS。',
                 'S14坏样本未保存逐轮中间活集合；新增逐轮证据不能回填过去，r01持续扩张仍可能阻断。',
                 '首次原生记录未捕获完整tool_prepost时明确null；不得用最终工具SHA冒充当时字节。',
                 '17已知自有身份最终ABSENT仅只读观察；整OS树、未采短命对象和连续绝对峰NOT_PROVEN。',
                 '没有Vivado/ROSS/综合/PNR/JTAG/串口/设备访问；仅自有隐藏轻量canary。',
                 'Tclnamespace0.1.12保持，JSON0.1.15候选只由ROOT最终真实源码冻结。'],stop=True)
save(D/'g1_receipt.json',receipt)
files=[]
for p in sorted(D.rglob('*')):
    if p.is_file():files.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),role='source' if p.suffix=='.py' else 'log' if p.suffix in ('.bin','.log','.diff') else 'result'))
checks=[]
for label in ['s15_g1_boundary_r01','s15_g1_selftest_r03','s15_g1_monitor_r03','s15_g1_collector_r02','s15_g1_regressions_r03','s15_g1_final_checks_r02']:
    r=json.loads((W/(label+'.native.json')).read_text(encoding='utf-8'));assert r['native_exit_code']==0
    checks.append(dict(name=label,status='PASS',command=subprocess.list2cmdline(r['command']),exit_code=r['native_exit_code'],reason='真实直接wait轻量G1；mock与自有canary范围见g1_receipt。'))
for name in ('独立工具G2','真实SOURCE/source-before','真实综合及预算/STA','G3实物及G5'):
    checks.append(dict(name=name,status='NOT_RUN',command=None,exit_code=None,reason='本轮仅工具G1；此项由ROOT后续在真实pin及独审门禁通过后处理。'))
manifest=dict(schema_version=1,stage='2B',task_id='S2B-T17',run_id=D.name,source_commit=BASE,evidence_dir=D.relative_to(ROOT).as_posix(),
    interfaces=[],interfaces_not_applicable_reason='本交付仅隔离的进程监护和证据采集工具G1，未消费或改写硬件模型总线接口；资源与完整身份规则由任务授权固定。',
    tool_versions=dict(python=sys.version,psutil=psutil.__version__,expected_profile='s2b-inference-platform/0.1.15'),
    files=files,checks=checks,limitations=receipt['limitations']+['source_commit为工具派生仓库基线；本轮生产SOURCE未知且不宣称该基线已覆盖待改源码。'])
save(D/'delivery_manifest.json',manifest)
print(json.dumps(dict(status=receipt['status'],files=len(files),bytes=sum(p.stat().st_size for p in D.rglob('*') if p.is_file()),
                      receipt=binding(D/'g1_receipt.json'),manifest=binding(D/'delivery_manifest.json'),tools=tools),ensure_ascii=False))
