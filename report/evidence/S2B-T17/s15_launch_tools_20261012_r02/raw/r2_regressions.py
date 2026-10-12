"""R2完整原生metadata及不可改gate链回归；真实子进程与逻辑fixture范围明确分列。"""
import ast
import contextlib
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch
import collector as c
import compat_pins as pins
import native_contract as contract
import native_capture as n
import guard
import selftest

W=Path(__file__).parent;ROOT=W.parents[3];RUN=os.environ.get('S15_R2_TEST_RUN','r03')
assert RUN.startswith('r') and RUN[1:].isdigit()
F=W/('r2_fixtures_'+RUN);F.mkdir()
ROWS=[];NATIVE=[]
COMMIT='b'*40

def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')

def check(name,function):
    try:function()
    except Exception as error:
        ROWS.append(dict(case=name,status='FAIL_PRESERVED',exception=repr(error)))
        raise
    ROWS.append(dict(case=name,status='PASS'))

def reject(function):
    try:function()
    except (ValueError,KeyError,TypeError):return
    raise AssertionError('错误记录被接受')

def launch(work,prefix,arguments,expected=0):
    command=[sys.executable,'-X','utf8','-B',str(work/'collector.py'),*arguments]
    wrapper=[sys.executable,'-X','utf8','-B',str(work/'native_capture.py'),prefix,*command]
    start=time.monotonic()
    with (work/(prefix+'.outer.stdout.bin')).open('xb') as out,(work/(prefix+'.outer.stderr.bin')).open('xb') as err:
        code=subprocess.run(wrapper,cwd=ROOT,stdout=out,stderr=err,creationflags=subprocess.DETACHED_PROCESS,timeout=15).returncode
    record=json.loads((work/(prefix+'.native.json')).read_text(encoding='utf-8'))
    NATIVE.append(dict(command=wrapper,outer_native_exit_code=code,child_native_exit_code=record['native_exit_code'],
                       wrapper_exit_code=record['wrapper_exit_code'],unknown_count=record['unknown_count'],
                       capture_status=record['capture_status'],elapsed_seconds=time.monotonic()-start,binding=c.binding(work/(prefix+'.native.json'))))
    assert code==expected and record['native_exit_code']==expected,record
    return record

# 正式collector的真实PENDING失败仍有完整捕获，绝不伪称SOURCE已批准。
real=launch(W,'s15_runtime_pending_prepare_'+RUN,['prepare'],1)
real_row=c.binding(W/('s15_runtime_pending_prepare_'+RUN+'.native.json'))
with patch.object(c,'CACHE',W),patch.object(c,'expected_tool_bindings',return_value=contract.capture_tools(W,ROOT)):
    check('actual_production_pending_capture_metadata_complete',lambda: c.runtime_native_records(dict(native_wrappers=[real_row])))
assert pins.SOURCE_COMMIT is None and pins.TOOLS_G2_SHA is None and pins.FUNCTIONAL_G2_SHA is None
check('production_source_g2_still_pending',lambda: reject(pins.require_ready))

# 闭合链仅用于逻辑fixture，实际subprocess身份/流/时间均从真实捕获获取。
FW=F/'tools';FW.mkdir();PRE=F/'pre';PRE.mkdir();REPORT=F/'report';REPORT.mkdir()
for name in contract.TOOL_NAMES:
    (FW/name).write_bytes((W/name).read_bytes())
fixture_collector='''"""轻量逻辑fixture；不表示真实SOURCE、MCP或G2。"""
import hashlib,json,sys,time
from pathlib import Path
arguments=sys.argv[1:];mode=arguments[0];options=dict(zip(arguments[1::2],arguments[2::2]))
root=Path(ROOT_VALUE);pre=Path(PRE_VALUE);report=Path(REPORT_VALUE)
def binding(path):
 raw=path.read_bytes();return dict(path=path.relative_to(root).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
if mode=='source':
 value=dict(source_commit=options['--commit'],fixture_test=True,source_files=[])
 path=pre/('source_'+options['--phase']+'.json')
elif mode=='collect':
 gate=Path(options['--gate']);raw=gate.read_bytes()
 value=dict(source_commit=options['--commit'],root_gate=binding(gate),closed_gate_inputs=json.loads(raw),fixture_test=True,limitations=['逻辑fixture'],timing=dict(status='FIXTURE_ONLY'))
 path=report/'s15_collection_summary.json'
else:raise ValueError('fixture模式不同')
with path.open('x',encoding='utf-8') as stream:json.dump(value,stream,ensure_ascii=False)
print('仅逻辑fixture实际捕获');time.sleep(.25)
'''.replace('ROOT_VALUE',repr(str(ROOT))).replace('PRE_VALUE',repr(str(PRE))).replace('REPORT_VALUE',repr(str(REPORT)))
(FW/'collector.py').write_text(fixture_collector,encoding='utf-8')
fixture_wrapper='''"""真实捕获轻量逻辑fixture；工具批准仅由独立审查给出。"""
from pathlib import Path
import sys
sys.path.insert(0,WORK_VALUE)
import native_capture as n
import compat_pins as pins
n.HERE=Path(__file__).parent;n.ROOT=Path(ROOT_VALUE)
pins.SOURCE_PRE=Path(PRE_VALUE);pins.SYNTH_REPORT=Path(REPORT_VALUE)
raise SystemExit(n.main())
'''.replace('WORK_VALUE',repr(str(W))).replace('ROOT_VALUE',repr(str(ROOT))).replace('PRE_VALUE',repr(str(PRE))).replace('REPORT_VALUE',repr(str(REPORT)))
(FW/'native_capture.py').write_text(fixture_wrapper,encoding='utf-8')
before=launch(FW,'s15_runtime_before_r01',['source','--commit',COMMIT,'--phase','before'])
after=launch(FW,'s15_runtime_after_r01',['source','--commit',COMMIT,'--phase','after'])
freeze=F/'freeze.json';save(freeze,dict(source_commit=COMMIT,profile='s2b-inference-platform/0.1.15',fixture_test=True))
common=[]
for name in ['preparation_receipt','static_source_closed','immutable_session_log','mcp_history','runtime_config']:
    path=F/(name+'.json');save(path,dict(fixture_test=True));common.append((name,c.binding(path)))
gate=dict(common,root_explicit_signal='CLOSED_INPUTS_READY',project_closed=True,source_commit=COMMIT,
          root_declared_products_execution_count=1,root_declared_synthesis_execution_count=1,
          source_before=c.binding(PRE/'source_before.json'),source_after=c.binding(PRE/'source_after.json'),
          design_mcp_records=[],additional_closed_files=[],approved_evidence=[],fixture_test=True,
          native_wrappers=[c.binding(FW/(prefix+'.native.json')) for prefix in ('s15_runtime_before_r01','s15_runtime_after_r01')])
for label in c.LABELS:
    path=F/('mcp_'+label+'.json');save(path,dict(fixture_test=True,label=label))
    gate['design_mcp_records'].append(dict(c.binding(path),label=label))
closedfile=F/'closed_file.json';save(closedfile,dict(fixture_test=True));gate['additional_closed_files'].append(c.binding(closedfile))
gate1=F/'gate_r01.json';save(gate1,gate);gate1_original=c.binding(gate1)
collected=launch(FW,'s15_runtime_collect_r01',['collect','--commit',COMMIT,'--gate',str(gate1)])
gate2_data=copy.deepcopy(gate);gate2_data['native_wrappers'].append(c.binding(FW/'s15_runtime_collect_r01.native.json'))
gate2=F/'gate_r02.json';save(gate2,gate2_data)
summary=json.loads((REPORT/'s15_collection_summary.json').read_text(encoding='utf-8'))
expected_tools=contract.capture_tools(FW,ROOT)
with contextlib.ExitStack() as stack:
    for owner,name,value in [(c,'WORK',FW),(c,'CACHE',FW),(c,'REPORT',REPORT),(c,'PRE',PRE),(c,'FREEZE',freeze),(c,'FREEZE_SHA',c.sha(freeze)),(pins,'SOURCE_COMMIT',COMMIT)]:stack.enter_context(patch.object(owner,name,value))
    stack.enter_context(patch.object(c,'expected_tool_bindings',return_value=expected_tools))
    stack.enter_context(patch.object(pins,'require_ready'))
    stack.enter_context(patch.object(pins,'runtime_config_binding',return_value=gate['runtime_config']))
    gate_read=c.closed_gate(gate2,COMMIT)
    records=c.runtime_native_records(gate_read,COMMIT)
    check('valid_actual_capture_immutable_gate_r01_to_r02_chain_fixture',lambda: c.validate_collect_chain(summary,gate_read,records,COMMIT))
    assert c.binding(gate1)==gate1_original
    base=copy.deepcopy(collected)
    variants=[('missing_identity_and_tool_metadata',lambda r:[r.pop(k,None) for k in ('launcher_identity','direct_child_identity','tool_bindings_before')]),
              ('wrong_parent_birth',lambda r:r['direct_child_identity'].update(ppid=999,create_time=r['launcher_identity']['create_time']-1)),
              ('tool_hash_changed',lambda r:r['tool_bindings_after'][0].update(sha256='c'*64)),
              ('budget_stop_with_child_rc0',lambda r:r.update(budget_stop='ELAPSED_GT_120_SECONDS',unknown_count=1,unknown_samples=[dict(phase='UNKNOWN')])),
              ('wrong_collect_commit_gate',lambda r:r.update(command=r['command'][:6]+['--commit','c'*40,'--gate',str(F/'other_gate.json')]))]
    def reject_record(label,change):
        r=copy.deepcopy(base);change(r)
        p=FW/(r['prefix']+'.native.json')
        original_read=c.read
        with patch.object(c,'read',side_effect=lambda path:r if Path(path)==p else original_read(path)):
            reject(lambda:c.runtime_native_records(gate_read,COMMIT))
    for label,change in variants:check('reviewer_reject_'+label,lambda label=label,change=change:reject_record(label,change))
    for label,change in [
        ('duplicate_commit',lambda r:r['command'].extend(['--commit',COMMIT])),
        ('extra_phase_on_collect',lambda r:r['command'].extend(['--phase','after'])),
        ('wrapper_extra_argument',lambda r:r['wrapper_command'].append('EXTRA')),
        ('wrong_cwd',lambda r:r.update(cwd=str(F))),
        ('wrong_child_exe',lambda r:r['direct_child_identity'].update(exe=str(F/'other.exe'))),
        ('wrong_child_cmdline',lambda r:r['direct_child_identity'].update(cmdline=['other'])),
        ('tool_missing_member',lambda r:r['tool_bindings_before'].pop()),
        ('unknown_count_only',lambda r:r.update(unknown_count=1,unknown_samples=[dict(phase='UNKNOWN')]))]:
        check('reject_'+label,lambda label=label,change=change:reject_record(label,change))
    for field in ('source_commit','runtime_config','design_mcp_records','additional_closed_files','source_before'):
        bad=copy.deepcopy(gate_read);bad[field]='other'
        check('seal_gate_reject_changed_'+field,lambda bad=bad:reject(lambda:c.validate_collect_chain(summary,bad,records,COMMIT)))
    for field in ('root_gate','closed_gate_inputs','source_commit'):
        bad=copy.deepcopy(summary);bad[field]='other'
        check('summary_reject_changed_'+field,lambda bad=bad:reject(lambda:c.validate_collect_chain(bad,gate_read,records,COMMIT)))
    bad=copy.deepcopy(gate_read);bad['native_wrappers']=bad['native_wrappers'][1:]
    check('seal_gate_reject_removed_prior_native',lambda:reject(lambda:c.validate_collect_chain(summary,bad,records,COMMIT)))
    # 日志内容篡改后不恢复或覆盖；反例原件仍单独存在。
    altered=F/'wrong_log.json';save(altered,dict(fixture_test=True))
    bad=copy.deepcopy(base);bad['stdout']=c.binding(altered);bad['closed_logs'][0]=bad['stdout']
    check('reject_log_actual_path_and_bytes',lambda:reject_record('wrong_log',lambda r:r.update(bad)))

check('ast_all_production_tools',lambda:[ast.parse((W/name).read_text(encoding='utf-8')) for name in contract.TOOL_NAMES])
check('guard_original_hash_unchanged',lambda: (_ for _ in ()).throw(AssertionError('guard漂移')) if hashlib.sha256((W/'guard.py').read_bytes()).hexdigest()!=pins.GUARD_SHA else None)
check('pending_source_not_mutated_after_fixture',lambda:reject(pins.require_ready))
assert pins.SOURCE_COMMIT is None
save(W/('r2_regression_result_'+RUN+'.json'),dict(status='PASS_G1_ONLY',methods=len(ROWS),cases=ROWS,native=NATIVE,
    actual_source_commit=None,tools_g2=None,functional_g2=None,fixture_gate_chain=True,
    real_production_capture='PENDING_PREPARE_NATIVE1_COMPLETE_METADATA',real_capture_count=len(NATIVE),
    independent_review='NOT_RUN',hardware_vivado_ross=False,limitations=['实际subprocess metadata与流是真实原件；source/collect成功门禁链是显式逻辑fixture，未批准真实SOURCE/G2。']))
print(json.dumps(dict(status='PASS_G1_ONLY',methods=len(ROWS),actual_captures=len(NATIVE),native=NATIVE),ensure_ascii=False))
