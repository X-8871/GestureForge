"""独立源码封包入口审查；仅读冻结输入，反例仅在本目录保存。"""
import contextlib,copy,json,sys
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).parent;ROOT=HERE.parents[3]
W=ROOT/'tmp/2B/S2B-T17/s15_source_closure_fallback_20261012_r01'
sys.path.insert(0,str(W))
import source_closure as c
checks=[]
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as stream:json.dump(v,stream,ensure_ascii=False,indent=2);stream.write('\n')
def check(name,fun):
    try:value=fun();checks.append(dict(name=name,status='PASS',value=value))
    except Exception as error:checks.append(dict(name=name,status='FAIL',error=repr(error)))
def rejects(fun):
    try:fun()
    except (ValueError,KeyError,TypeError,AttributeError):return True
    raise AssertionError('负向输入未拒绝')
def require(value):
    if not value:raise AssertionError('独立断言不符')
inventory=c.read(W/'frozen_inventory.json');g1=c.read(W/'g1_receipt.json')
def hashes():
    for row in inventory['files']:c.bound(row)
    return len(inventory['files'])
check('94_frozen_original_hashes',hashes)
check('frozen_entry_hash',lambda:require(c.binding(W/'source_closure.py')==g1['implementation']))
cfg,freeze,tools,deps=c.baseline(c.binding(c.CONFIG))
check('actual_source_config_static_46_33_14_13tools',lambda:require(len(freeze['source_files'])==46 and len(freeze['static_source_sha256'])==33 and len(freeze['frozen14'])==14 and len(tools)==13))
before_row=c.binding(Path(cfg['SOURCE_PRE'])/'source_before.json');before,snapshots=c.source_record(before_row,'before',cfg,freeze)
admission_row=c.binding(c.ROOTRUN/'source_admission_r01.json');admission=c.admission(admission_row,before_row,before,freeze)
check('actual_before_git_all46_relations_directwait48',lambda:require(len(admission['git_commands'])==48))
capture_row=admission['failed_capture'];actual=c.read(c.bound(capture_row));status,logs=c.capture(capture_row,'before',before_row,tools)
check('actual_source_capture_keeps_unknown27_wrapper2',lambda:require(status['original_status']=='BLOCKED_UNKNOWN_IDENTITY' and status['unknown_count']==27 and status['original_wrapper_exit_code']==2))
budget_row=c.binding(c.ROOTRUN/'supervision_r01/guard/guard_receipt.json')
blocked=c.budget([budget_row],'BLOCKED')
check('actual_budget_blocked_raw_bound',lambda:require(blocked['status']=='BLOCKED' and blocked['continuous_budget_pass'] is False))
check('budget_fake_PASS_rejected',lambda:rejects(lambda:c.budget([budget_row],'PASS')))
check('budget_missing_records_rejected',lambda:rejects(lambda:c.budget([],'NOT_PROVEN')))
real_read=c.read
def capture_probe(name,edit,expected_reject=True):
    value=copy.deepcopy(actual);edit(value)
    save(HERE/(name+'.json'),dict(fixture_test=True,altered_capture=value))
    with patch.object(c,'read',side_effect=lambda p:value if Path(p)==c.relative(capture_row['path']) else real_read(p)):
        if expected_reject:return rejects(lambda:c.capture(capture_row,'before',before_row,tools))
        return c.capture(capture_row,'before',before_row,tools)[0]
for name,edit in [
    ('identity_missing',lambda v:v.pop('direct_child_identity')),
    ('tools_missing',lambda v:v.pop('tool_bindings_before')),
    ('closed_logs_missing',lambda v:v.pop('closed_logs')),
    ('unknown_samples_missing',lambda v:v.pop('unknown_samples')),
    ('false_wrapper_PASS',lambda v:v.update(capture_status='CLOSED_NATIVE_SUCCESS',wrapper_exit_code=0)),
    ('budget_false_PASS',lambda v:v.update(budget_stop='TIMEOUT',capture_status='CLOSED_NATIVE_SUCCESS',wrapper_exit_code=0)),
    ('child_code_boolean',lambda v:v.update(native_exit_code=False)),
    ('wrapper_code_unknown',lambda v:v.update(wrapper_exit_code=None)),
    ('wrong_birth',lambda v:v['direct_child_identity'].update(create_time=v['launcher_identity']['create_time']-1)),
    ('wrong_full_command',lambda v:v['command'].append('EXTRA')),
    ('directwait_missing',lambda v:v.pop('direct_child_wait_returned')),
    ('source_output_missing',lambda v:v.pop('source_output')),
    ('capture_kind_missing',lambda v:v.pop('capture_target_kind')),
    ('budget_stop_missing',lambda v:v.pop('budget_stop')),
    ('known_terminal_missing',lambda v:v.pop('known_descendant_identity_terminal_observations')),
    ('known_terminal_status_missing',lambda v:v.pop('known_descendants_same_identity_absent_at_observation')),
]:check('reject_'+name,lambda name=name,edit=edit:capture_probe(name,edit))
request=dict(source_commit=c.SOURCE,config=c.binding(c.CONFIG),source_before=before_row,source_after=None,source_admission=admission_row,capture_before=capture_row,capture_after=None,budget_records=[budget_row],budget_status='BLOCKED',additional_evidence=[])
check('missing_actual_after_rejected',lambda:rejects(lambda:c.verify(request)))
# 只模拟after逻辑子项，核可选附件的契约；不生成真实SOURCE-after或新批准。
def logical_verify_missing_evidence():
    with patch.object(c,'source_record',return_value=(before,snapshots)),patch.object(c,'capture',return_value=(status,logs)):
        result=c.verify(dict(request,source_after=before_row,capture_after=capture_row))
    return dict(result_status=result['status'],additional_evidence_required=False,actual_source_after=False)
check('logical_optional_additional_evidence_result',logical_verify_missing_evidence)
result=dict(status='CHANGES_REQUIRED' if any(r['status']=='FAIL' for r in checks) else 'PASS_SOURCE_CLOSURE_TOOL_ONLY',checks=checks,entry=c.binding(W/'source_closure.py'),g1=c.binding(W/'g1_receipt.json'),inventory=c.binding(W/'frozen_inventory.json'),actual_after='NOT_REVIEWED',hardware_vivado_ross_git_executed=False)
save(HERE/'probe_result.json',result)
print(json.dumps(dict(status=result['status'],checks=len(checks),failed_checks=[r['name'] for r in checks if r['status']=='FAIL'],entry=result['entry']),ensure_ascii=False))
