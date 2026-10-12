"""SOURCE独立封包窄回归；真实before只读正向，after缺失不伪造生产闭合。"""
import ast,copy,json,subprocess,sys,time
from pathlib import Path
from unittest.mock import patch
import source_closure as c
HERE=Path(__file__).parent;ROOT=c.ROOT;ROWS=[]
F=HERE/'regression_fixtures_r01';F.mkdir()
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as stream:json.dump(v,stream,ensure_ascii=False,indent=2);stream.write('\n')
def check(name,fun):
    try:fun()
    except Exception as error:save(F/(name+'.failed.json'),dict(case=name,error=repr(error)));raise
    ROWS.append(dict(case=name,status='PASS'))
def reject(fun):
    try:fun()
    except (ValueError,KeyError,TypeError,AttributeError):return
    raise AssertionError('拒绝反例被放行')
cfg,freeze,tools,dependencies=c.baseline(c.binding(c.CONFIG))
before_row=c.binding(Path(cfg['SOURCE_PRE'])/'source_before.json')
before,snapshots=c.source_record(before_row,'before',cfg,freeze)
admission_row=c.binding(c.ROOTRUN/'source_admission_r01.json')
admission=c.admission(admission_row,before_row,before,freeze)
capture_row=admission['failed_capture'];original=c.read(c.bound(capture_row))
capture_status,logs=c.capture(capture_row,'before',before_row,tools)
budget_row=c.binding(c.ROOTRUN/'supervision_r01/guard/guard_receipt.json')
budget=c.budget([budget_row],'BLOCKED')
request=dict(source_commit=c.SOURCE,config=c.binding(c.CONFIG),source_before=before_row,source_after=None,
 source_admission=admission_row,capture_before=capture_row,capture_after=None,budget_records=[budget_row],budget_status='BLOCKED',additional_evidence=[])
save(HERE/'request_pending_after.json',request)
check('actual_baseline_46_33_14_and_13_tools_guard_dependency',lambda:c.baseline(request['config']))
check('actual_before_all_raw_snapshot_git_relation',lambda:c.admission(admission_row,before_row,before,freeze))
check('actual_before_child0_unknown27_wrapper2_preserved',lambda:c.capture(capture_row,'before',before_row,tools))
assert capture_status['original_status']=='BLOCKED_UNKNOWN_IDENTITY' and capture_status['unknown_count']==27 and capture_status['original_wrapper_exit_code']==2
check('actual_guard_blocked_original_raw_preserved',lambda:c.budget([budget_row],'BLOCKED'))
assert budget['continuous_budget_pass'] is False and budget['status']=='BLOCKED'
check('reject_missing_source_commit',lambda:reject(lambda:c.verify(dict(request,source_commit=None))))
check('reject_wrong_config_hash',lambda:reject(lambda:c.baseline(dict(request['config'],sha256='f'*64))))
check('reject_missing_after_snapshot',lambda:reject(lambda:c.verify(request)))
native_read=c.read
def altered_capture(label,edit):
    value=copy.deepcopy(original);edit(value);save(F/(label+'.probe.json'),dict(fixture_test=True,altered_capture=value))
    with patch.object(c,'read',side_effect=lambda p:value if Path(p)==c.relative(capture_row['path']) else native_read(p)):
        reject(lambda:c.capture(capture_row,'before',before_row,tools))
for label,edit in [('false_child0_boolean',lambda v:v.update(native_exit_code=False)),
                   ('child_nonzero',lambda v:v.update(native_exit_code=1)),
                   ('missing_directwait',lambda v:v.update(direct_child_wait_returned=False)),
                   ('wrong_source_phase_command',lambda v:v['command'].append('EXTRA')),
                   ('lost_unknown_originals',lambda v:v.update(unknown_samples=[])),
                   ('unknown_promoted_pass',lambda v:v.update(capture_status='CLOSED_NATIVE_SUCCESS',wrapper_exit_code=0)),
                   ('budget_stop_promoted_pass',lambda v:v.update(budget_stop='TREE_RSS_GT_256MiB',capture_status='CLOSED_NATIVE_SUCCESS',wrapper_exit_code=0)),
                   ('wrong_tool_hash',lambda v:v['tool_bindings_after'][0].update(sha256='d'*64)),
                   ('wrong_parent_birth',lambda v:v['direct_child_identity'].update(create_time=v['launcher_identity']['create_time']-1)),
                   ('missing_identity',lambda v:v.pop('direct_child_identity'))]:
    check('reject_'+label,lambda label=label,edit=edit:altered_capture(label,edit))
def missing_snapshot():
    value=copy.deepcopy(before);value['source_files'][0]['snapshot']='tmp/2B/S2B-T17/nonexistent_snapshot'
    with patch.object(c,'read',side_effect=lambda p:value if Path(p)==c.relative(before_row['path']) else native_read(p)):
        reject(lambda:c.source_record(before_row,'before',cfg,freeze))
check('reject_snapshot_path_missing_or_wrong',missing_snapshot)
check('reject_budget_fake_pass',lambda:reject(lambda:c.budget([budget_row],'PASS')))
check('reject_budget_original_missing',lambda:reject(lambda:c.budget([],'NOT_PROVEN')))
def lost_original():
    req=dict(request,capture_before=dict(capture_row,sha256='0'*64))
    # 后半阶段由显式fixture绕过，仍要求admission绑定的原UNKNOWN记录不能替换。
    with patch.object(c,'source_record',return_value=(before,snapshots)):
        reject(lambda:c.verify(req))
check('reject_replaced_unknown_native_binding',lost_original)
check('ast_entry_and_regressions',lambda:[ast.parse(p.read_text(encoding='utf-8')) for p in HERE.glob('*.py')])
assert c.binding(c.relative(capture_row['path']))==capture_row
assert all(c.binding(c.relative(row['path']))==row for row in tools)
# 封包mechanics只使用显式fixture；不伪造尚不存在的after实际SOURCE。
fixture_request=F/'request_fixture.json';save(fixture_request,dict(fixture_test=True))
fixture_result=dict(status='PACKAGE_FIXTURE_ONLY_NOT_ACTUAL_SOURCE_CLOSURE',source_commit=c.SOURCE,captures=[capture_status],budget=budget,inputs=[request['config'],capture_row,*logs,budget_row],fixture_test=True)
out=HERE/'s15_source_closure_package_fixture_r01'
with patch.object(c,'verify',return_value=fixture_result):
    check('package_fixture_new_directory_all_raw_preserved',lambda:c.package(fixture_request,out))
    saved=c.binding(out/'source_closure_receipt.json')
    check('reject_package_existing_output_without_overwrite',lambda:reject(lambda:c.package(fixture_request,out)))
    assert c.binding(out/'source_closure_receipt.json')==saved
command=[sys.executable,'-X','utf8','-B',str(ROOT/'verification/check_stage_delivery.py'),'--mode','evidence','--manifest',str(out/'delivery_manifest.json'),'--project-root',str(ROOT)]
with (F/'packaging.stdout.bin').open('xb') as stdout,(F/'packaging.stderr.bin').open('xb') as stderr:
    start=time.monotonic();code=subprocess.run(command,cwd=ROOT,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW,timeout=20).returncode
save(F/'packaging.wait.json',dict(command=command,native_exit_code=code,direct_child_wait_returned=True,elapsed_seconds=time.monotonic()-start))
assert code==0,(F/'packaging.stderr.bin').read_bytes()
check('fixture_standard_evidence_packaging_real_wait0',lambda:None)
save(HERE/'regression_result.json',dict(status='PASS_G1_ONLY',methods=len(ROWS),cases=ROWS,actual_before='SOURCE_CONTENT_ONLY_CHILD0_WRAPPER2_UNKNOWN27',actual_after='NOT_AVAILABLE_NOT_EXECUTED',budget='BLOCKED_PRESERVED',fixture_package='NOT_ACTUAL_SOURCE_CLOSURE',tool_prepost_unchanged=True,originals=[capture_row,budget_row],limitations=['生产after尚不存在，真实完整封包必须等ROOT两阶段实际完成与新入口独审。','package positive仅机械fixture，真实before与全部固定依赖已只读核验。']))
print(json.dumps(dict(status='PASS_G1_ONLY',methods=len(ROWS),actual_after='NOT_AVAILABLE',budget='BLOCKED_PRESERVED'),ensure_ascii=False))
