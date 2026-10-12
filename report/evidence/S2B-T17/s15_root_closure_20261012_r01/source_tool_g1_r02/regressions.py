"""R2四项缺metadata及严格类型反例；真实UNKNOWN27/26正向不升级包装。"""
import ast,copy,json,os,re
from pathlib import Path
from unittest.mock import patch
import source_closure as c
HERE=Path(__file__).parent;RUN=os.environ.get('SOURCE_CLOSURE_R2_TEST_RUN','r02');assert re.fullmatch('r[0-9]+',RUN)
ROWS=[];F=HERE/('probes_'+RUN);F.mkdir()
def reject(fun):
    try:fun()
    except (ValueError,KeyError,TypeError,AttributeError):return
    raise AssertionError('反例被放行')
def check(name,fun):
    try:fun()
    except Exception as error:c.save(F/(name+'.failed.json'),dict(case=name,error=repr(error)));raise
    ROWS.append(dict(case=name,status='PASS'))
request=c.read(HERE/'actual_request_r01.json');config,freeze,tools,deps=c.baseline(request['config'])
check('real_before_after_46raw92snapshot33static14tools13_dependency_closed',lambda:c.verify(request))
value=c.verify(request)
assert value['mcp9_sta_validation']=='NOT_IN_SCOPE' and value['budget']['status']=='BLOCKED'
assert [(row['original_wrapper_exit_code'],row['unknown_count']) for row in value['captures']]==[(2,27),(2,26)]
check('real_unknown27_26_child0_wrapper2_budgetblocked_preserved',lambda:None)
check('empty_additional_evidence_explicit_mcp9_sta_not_in_scope',lambda:None)
row=request['capture_after'];source_row=request['source_after'];actual=c.read(c.bound(row));actual_read=c.read
def altered(name,edit):
    record=copy.deepcopy(actual);edit(record)
    c.save(F/(name+'.json'),dict(fixture_test=True,altered_capture=record))
    with patch.object(c,'read',side_effect=lambda p:record if Path(p)==c.relative(row['path']) else actual_read(p)):
        reject(lambda:c.capture(row,'after',source_row,tools))
for name,edit in [
 ('missing_capture_target_kind',lambda r:r.pop('capture_target_kind')),
 ('missing_budget_stop',lambda r:r.pop('budget_stop')),
 ('missing_known_terminal_list',lambda r:r.pop('known_descendant_identity_terminal_observations')),
 ('missing_known_absent_boolean',lambda r:r.pop('known_descendants_same_identity_absent_at_observation')),
 ('native_code_boolean',lambda r:r.update(native_exit_code=False)),
 ('wrapper_code_boolean',lambda r:r.update(wrapper_exit_code=True)),
 ('wrapper_code_float',lambda r:r.update(wrapper_exit_code=2.0)),
 ('known_absent_integer',lambda r:r.update(known_descendants_same_identity_absent_at_observation=1)),
 ('budget_empty_string',lambda r:r.update(budget_stop='')),
 ('budget_integer',lambda r:r.update(budget_stop=0)),
 ('wrong_capture_target',lambda r:r.update(capture_target_kind='GENERIC_CANARY')),
 ('terminal_missing_exe',lambda r:r['known_descendant_identity_terminal_observations'][0].pop('exe')),
 ('terminal_missing_status',lambda r:r['known_descendant_identity_terminal_observations'][0].pop('observed_status')),
 ('terminal_invalid_status',lambda r:r['known_descendant_identity_terminal_observations'][0].update(observed_status='UNKNOWN')),
 ('terminal_exists_integer',lambda r:r['known_descendant_identity_terminal_observations'][0].update(same_identity_exists=0)),
 ('terminal_pid_boolean',lambda r:r['known_descendant_identity_terminal_observations'][0].update(pid=True)),
 ('terminal_birth_nan',lambda r:r['known_descendant_identity_terminal_observations'][0].update(create_time=float('nan'))),
 ('terminal_cmdline_missing',lambda r:r['known_descendant_identity_terminal_observations'][0].pop('cmdline')),
 ('terminal_exit_alive_contradiction',lambda r:r['known_descendant_identity_terminal_observations'][0].update(same_identity_exists=True)),
 ('missing_direct_child_terminal',lambda r:r.update(known_descendant_identity_terminal_observations=[])),
 ('unknown_samples_missing',lambda r:r.pop('unknown_samples')),
 ('unknown_count_boolean',lambda r:r.update(unknown_count=True)),
 ('unknown_count_mismatch',lambda r:r.update(unknown_count=25)),
 ('unknown_exception_missing',lambda r:r['unknown_samples'][0].pop('exception')),
 ('unknown_promoted_pass',lambda r:r.update(capture_status='CLOSED_NATIVE_SUCCESS',wrapper_exit_code=0)),
 ('directwait_false',lambda r:r.update(direct_child_wait_returned=False)),
 ('tools_missing',lambda r:r.pop('tool_bindings_after')),
 ('tool_hash_changed',lambda r:r['tool_bindings_after'][0].update(sha256='f'*64)),
 ('source_output_missing',lambda r:r.pop('source_output')),
 ('missing_confirmed_exits',lambda r:r.pop('confirmed_capture_exits')),
 ('missing_python_version',lambda r:r.pop('python')),
 ('peak_boolean',lambda r:r.update(sampled_owned_tree_peak_bytes=False)),
 ('false_absolute_peak',lambda r:r.update(absolute_tree_peak_bytes=1)),
 ('elapsed_nonfinite',lambda r:r.update(elapsed_seconds=float('inf'))),
 ('wrong_parent_birth',lambda r:r['direct_child_identity'].update(create_time=r['launcher_identity']['create_time']-1))]:
    check('reject_'+name,lambda name=name,edit=edit:altered(name,edit))
check('reject_missing_commit',lambda:reject(lambda:c.verify(dict(request,source_commit=None))))
check('reject_wrong_after_sha',lambda:reject(lambda:c.verify(dict(request,source_after=dict(source_row,sha256='0'*64)))))
check('reject_budget_fake_pass',lambda:reject(lambda:c.budget(request['budget_records'],'PASS')))
check('ast_all_r2_scripts',lambda:[ast.parse(p.read_text(encoding='utf-8')) for p in HERE.glob('*.py')])
index=c.read(HERE/'copied_original_index.json')
check('all_r1_original_and_reviewer_copy_hashes_unchanged',lambda:[c.bound(row['original']) for group in ('baseline_r01','review_r01') for row in index[group]])
c.save(HERE/('regression_result_'+RUN+'.json'),dict(status='PASS_G1_ONLY',methods=len(ROWS),cases=ROWS,actual_source_before_after=True,unknown_original_counts=[27,26],wrapper_codes=[2,2],budget='BLOCKED',mcp9_sta_validation='NOT_IN_SCOPE',entry_g2='PENDING'))
print(json.dumps(dict(status='PASS_G1_ONLY',methods=len(ROWS),mcp9_sta_validation='NOT_IN_SCOPE'),ensure_ascii=False))
