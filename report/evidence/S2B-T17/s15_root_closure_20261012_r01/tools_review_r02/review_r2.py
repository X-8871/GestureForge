"""独立R2只读复审；实际捕获与逻辑门禁夹具明确分列。"""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

HERE=Path(__file__).parent;ROOT=HERE.parents[3]
W=ROOT/'tmp/2B/S2B-T17/s15_launch_prepare_20261012_r02'
PACKAGE=ROOT/'report/evidence/S2B-T17/s15_launch_tools_20261012_r02'
sys.path.insert(0,str(W))
import collector as c
import compat_pins as pins
import native_contract as contract
import native_capture as native
import supervisor

def read(path):return json.loads(c.exact(path).read_text(encoding='utf-8'))
def save(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
def row(path):return c.binding(path)
checks=[]
def check(name,function):
    try:value=function();checks.append(dict(name=name,status='PASS',details=value))
    except Exception as error:checks.append(dict(name=name,status='FAIL',error=repr(error)))
def require(value,message='独立断言失败'):
    if not value:raise AssertionError(message)
def rejects(function):
    try:function()
    except (ValueError,KeyError,TypeError):return True
    raise AssertionError('负向输入被接受')

receipt=read(PACKAGE/'g1_receipt.json');manifest=read(PACKAGE/'delivery_manifest.json')
def hashes(rows):
    bad=[r['path'] for r in rows if row(ROOT/r['path'])['sha256']!=r['sha256'] or ('bytes' in r and row(ROOT/r['path'])['bytes']!=r['bytes'])]
    require(not bad,str(bad));return dict(count=len(rows))
check('200_formal_file_hashes',lambda:hashes(manifest['files']))
check('13_production_tool_hashes',lambda:hashes(receipt['reviewed_tools']))
check('40_G1_cases_and_true_waits',lambda:require(sum(r['methods'] for r in receipt['test_results'])==40 and all(r['status']=='PASS_G1_ONLY' for r in receipt['test_results'])))
actual_tools=contract.capture_tools(W,ROOT)
check('contract_13_exact_names',lambda:require(actual_tools==receipt['reviewed_tools'] and len(actual_tools)==13))
check('still_pending_source_g2',lambda:rejects(pins.require_ready))
layout=read(PACKAGE/'runtime_pin_layout.json')
check('layout_file_available',lambda:dict(keys=list(layout)))
pending=read(W/'s15_runtime_pending_prepare_r03.native.json')
logs=[row(W/('s15_runtime_pending_prepare_r03.'+suffix)) for suffix in ('stdout.bin','stderr.bin')]
check('actual_pending_prepare_capture_child1_wrapper1',lambda:contract.validate_capture(pending,pending['command'],pending['wrapper_command'],str(ROOT),actual_tools,pending['prefix'],logs))
check('pending_prepare_not_source_success',lambda:require(pending['native_exit_code']==pending['wrapper_exit_code']==1 and pending['capture_status']=='CLOSED_NATIVE_CHILD_FAILURE'))

F=W/'r2_fixtures_r03';FW=F/'tools';PRE=F/'pre';REPORT=F/'report';COMMIT='b'*40
fixture_tools=contract.capture_tools(FW,ROOT)
gate1=read(F/'gate_r01.json');gate2=read(F/'gate_r02.json');summary=read(REPORT/'s15_collection_summary.json')
original_gate1=row(F/'gate_r01.json');original_gate2=row(F/'gate_r02.json')
with contextlib.ExitStack() as stack:
    for owner,name,value in [(c,'WORK',FW),(c,'CACHE',FW),(c,'REPORT',REPORT),(c,'PRE',PRE),(c,'FREEZE',F/'freeze.json'),(c,'FREEZE_SHA',c.sha(F/'freeze.json')),(pins,'SOURCE_COMMIT',COMMIT)]:stack.enter_context(patch.object(owner,name,value))
    stack.enter_context(patch.object(c,'expected_tool_bindings',return_value=fixture_tools))
    stack.enter_context(patch.object(pins,'require_ready'))
    stack.enter_context(patch.object(pins,'runtime_config_binding',return_value=gate1['runtime_config']))
    valid_gate=c.closed_gate(F/'gate_r02.json',COMMIT)
    records=c.runtime_native_records(valid_gate,COMMIT)
    check('real_metadata_logical_fixture_gate_chain_positive',lambda:c.validate_collect_chain(summary,valid_gate,records,COMMIT))
    before,after,collected=[record for _,record in records]
    check('fixture_actual_source_before_after_collect_native0',lambda:require(all(r['native_exit_code']==r['wrapper_exit_code']==0 and r['capture_target_kind']=='COLLECTOR' for r in (before,after,collected))))
    base=collected
    base_logs=[row(FW/(base['prefix']+'.'+suffix)) for suffix in ('stdout.bin','stderr.bin')]
    # 完整capture契约直接负向，不让路径或声明SHA提前拒绝掩盖被测字段。
    variants=[
        ('r1_missing_metadata',lambda r:[r.pop(k,None) for k in ('launcher_identity','direct_child_identity','tool_bindings_before')]),
        ('r1_wrong_parent_birth',lambda r:r['direct_child_identity'].update(ppid=999,create_time=r['launcher_identity']['create_time']-1)),
        ('r1_tools_changed',lambda r:r['tool_bindings_after'][0].update(sha256='c'*64)),
        ('r1_budget_stop_rc0',lambda r:r.update(budget_stop='ELAPSED_GT_120_SECONDS',unknown_count=1,unknown_samples=[dict(phase='UNKNOWN')])),
        ('parent_birth_only',lambda r:r['direct_child_identity'].update(create_time=r['launcher_identity']['create_time']-1)),
        ('parent_pid_only',lambda r:r['direct_child_identity'].update(ppid=999)),
        ('child_exe',lambda r:r['direct_child_identity'].update(exe=str(HERE/'other.exe'))),
        ('child_cwd',lambda r:r['direct_child_identity'].update(cwd=str(HERE))),
        ('child_argv',lambda r:r['direct_child_identity'].update(cmdline=['OTHER'])),
        ('launcher_argv',lambda r:r['launcher_identity'].update(cmdline=['OTHER'])),
        ('tool_missing',lambda r:r['tool_bindings_before'].pop()),
        ('tool_extra',lambda r:r['tool_bindings_before'].append(dict(path='OTHER',sha256='a'*64,bytes=1))),
        ('wrapper_rc0_child_failure',lambda r:r.update(native_exit_code=1,wrapper_exit_code=0)),
        ('budget_only_rc0',lambda r:r.update(budget_stop='TREE_RSS_GT_256MiB')),
        ('unknown_only_rc0',lambda r:r.update(unknown_count=1,unknown_samples=[dict(phase='UNKNOWN')])),
        ('direct_wait_false',lambda r:r.update(direct_child_wait_returned=False)),
        ('log_order_swapped',lambda r:r.update(closed_logs=list(reversed(base_logs)))),
        ('terminal_child_unbound',lambda r:r['known_descendant_identity_terminal_observations'][0].update(pid=98765)),
    ]
    for label,mutate in variants:
        bad=copy.deepcopy(base);mutate(bad)
        save(HERE/(label+'.json'),dict(fixture_test=True,record=bad))
        check('reject_'+label,lambda bad=bad:rejects(lambda:contract.validate_capture(bad,base['command'],base['wrapper_command'],str(ROOT),fixture_tools,base['prefix'],base_logs)))
    # 单独测试完整argv和commit，确保第五个R1反例由参数语义关闭。
    for label,args in [('duplicate_commit',['collect','--commit',COMMIT,'--gate',str(F/'gate_r01.json'),'--commit',COMMIT]),('extra_phase',['collect','--commit',COMMIT,'--gate',str(F/'gate_r01.json'),'--phase','after']),('missing_gate',['collect','--commit',COMMIT])]:
        check('reject_argv_'+label,lambda args=args:rejects(lambda:contract.collector_arguments(args)))
    changed=copy.deepcopy(base);changed['command']=changed['command'][:6]+['--commit','c'*40,'--gate',str(HERE/'OTHER.json')]
    original_read=c.read
    actual_record_path=FW/(base['prefix']+'.native.json')
    with patch.object(c,'read',side_effect=lambda p:changed if Path(p)==actual_record_path else original_read(p)):
        check('reject_r1_wrong_collect_commit_gate',lambda:rejects(lambda:c.runtime_native_records(valid_gate,COMMIT)))
    for field in ('source_commit','runtime_config','design_mcp_records','additional_closed_files','source_before','source_after','static_source_closed','mcp_history','immutable_session_log'):
        changed_gate=copy.deepcopy(valid_gate);changed_gate[field]='OTHER'
        check('reject_gate_change_'+field,lambda changed_gate=changed_gate:rejects(lambda:c.validate_collect_chain(summary,changed_gate,records,COMMIT)))
    for field in ('root_gate','closed_gate_inputs','source_commit'):
        changed_summary=copy.deepcopy(summary);changed_summary[field]='OTHER'
        check('reject_summary_'+field,lambda changed_summary=changed_summary:rejects(lambda:c.validate_collect_chain(changed_summary,valid_gate,records,COMMIT)))
    changed_gate=copy.deepcopy(valid_gate);changed_gate['native_wrappers']=changed_gate['native_wrappers'][1:]
    check('reject_gate_remove_original_native',lambda:rejects(lambda:c.validate_collect_chain(summary,changed_gate,records,COMMIT)))

check('fixture_gates_original_unchanged',lambda:require(row(F/'gate_r01.json')==original_gate1 and row(F/'gate_r02.json')==original_gate2))
# 自有新原生通用canary；仅输出落本目录，实际工具读取固定13生产闭包。
native_tools=contract.capture_tools
with patch.object(native,'HERE',HERE),patch.object(native,'ROOT',ROOT),patch.object(contract,'capture_tools',side_effect=lambda work,root:native_tools(W,ROOT)),patch.object(sys,'argv',[str(W/'native_capture.py'),'review_r2_native',sys.executable,'-X','utf8','-B','-c','import time; print("独立R2轻量原生"); time.sleep(0.4)']),contextlib.redirect_stdout(io.StringIO()):
    code=native.main(dict(mode='collect',prefix='review_r2_native'))
canary=read(HERE/'review_r2_native.native.json')
canary_logs=[row(HERE/('review_r2_native.'+suffix)) for suffix in ('stdout.bin','stderr.bin')]
check('independent_real_native_direct_wait',lambda:require(code==canary['native_exit_code']==canary['wrapper_exit_code']==0 and canary['direct_child_wait_returned']))
check('independent_real_native_complete_metadata',lambda:contract.validate_capture(canary,canary['command'],canary['wrapper_command'],str(ROOT),actual_tools,canary['prefix'],canary_logs))
check('generic_canary_not_actual_collector',lambda:require(canary['capture_target_kind']=='GENERIC_CANARY'))
check('stop_13_tools_hashes_unchanged',lambda:hashes(receipt['reviewed_tools']))
result=dict(status='PASS_TOOL_G2_ONLY' if all(row['status']=='PASS' for row in checks) else 'CHANGES_REQUIRED',checks=checks,baseline_commit=subprocess.check_output(['git','-c','core.longpaths=true','rev-parse','HEAD'],cwd=ROOT).decode().strip(),formal_manifest=row(PACKAGE/'delivery_manifest.json'),g1_receipt=row(PACKAGE/'g1_receipt.json'),reviewed_tools=receipt['reviewed_tools'],guard_launch_dependency=dict(supervisor_guard=str(supervisor.GUARD),pins_guard=str(pins.GUARD),same_path=supervisor.GUARD==pins.GUARD,actual_guard_hash=c.sha(supervisor.GUARD),pinned_guard_hash=pins.GUARD_SHA),native=dict(native_exit_code=canary['native_exit_code'],wrapper_exit_code=canary['wrapper_exit_code'],direct_child_wait_returned=canary['direct_child_wait_returned'],unknown_count=canary['unknown_count'],elapsed_seconds=canary['elapsed_seconds'],sampled_peak_bytes=canary['sampled_owned_tree_peak_bytes'],entire_os_tree_terminal=canary['entire_os_tree_terminal']),logical_fixture_source_success_not_actual_approval=True,production_source_actual='PENDING',hardware_vivado_ross=False)
save(HERE/'review_r2_result.json',result)
print(json.dumps(dict(status=result['status'],checks=len(checks),failures=[row for row in checks if row['status']=='FAIL'],guard_dependency=result['guard_launch_dependency'],native=result['native']),ensure_ascii=False))
