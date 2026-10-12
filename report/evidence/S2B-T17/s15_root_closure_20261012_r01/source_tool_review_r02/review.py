"""独立R2封包工具复审；真实SOURCE封包和严格schema反例仅写本审查目录。"""
import copy,hashlib,importlib.util,json,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).parent;ROOT=HERE.parents[3]
W=ROOT/'tmp/2B/S2B-T17/s15_source_closure_fallback_20261012_r02'
entry=W/'source_closure.py'
spec=importlib.util.spec_from_file_location('reviewed_source_closure',entry);c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as stream:json.dump(v,stream,ensure_ascii=False,indent=2,allow_nan=False);stream.write('\n')
checks=[]
def check(name,fun):
    try:value=fun();checks.append(dict(name=name,status='PASS',value=value))
    except Exception as error:checks.append(dict(name=name,status='FAIL',error=repr(error)))
def require(value):
    if not value:raise AssertionError('独立断言失败')
def reject(fun):
    try:fun()
    except (ValueError,KeyError,TypeError,AttributeError):return True
    raise AssertionError('负向记录未拒绝')
inventory=c.read(W/'frozen_inventory.json');g1=c.read(W/'g1_receipt.json')
check('572_frozen_hashes',lambda:[c.bound(row) for row in inventory['files']] and len(inventory['files']))
check('entry_frozen_7c7e_hash',lambda:require(c.binding(entry)==g1['implementation'] and c.binding(entry)['sha256']=='7c7e6bd1ea554efe070897d3d2d973a5f09ca1b84fab0c4337dfb86845120c5e'))
request=c.read(W/'actual_request_r01.json');cfg,freeze,tools,deps=c.baseline(request['config']);closed=c.verify(request)
check('actual_before_after_46_33_14_and_tool13_dependency',lambda:require(closed['source_count']==46 and closed['static_count']==33 and len(closed['frozen14'])==14 and len(tools)==13))
check('actual_UNKNOWN27_26_wrapper2_budgetBLOCKED_preserved',lambda:require([(r['original_wrapper_exit_code'],r['unknown_count']) for r in closed['captures']]==[(2,27),(2,26)] and closed['budget']['status']=='BLOCKED' and closed['budget']['continuous_budget_pass'] is False))
check('MCP9_STA_explicit_not_in_scope',lambda:require(closed['mcp9_sta_validation']=='NOT_IN_SCOPE' and closed['original_seal']=='NOT_CALLED_NOT_PASSED' and request['additional_evidence']==[]))
actual=c.read(c.bound(request['capture_after']))
variants=[
    ('missing_target',lambda r:r.pop('capture_target_kind')),
    ('missing_budget_stop',lambda r:r.pop('budget_stop')),
    ('missing_terminal',lambda r:r.pop('known_descendant_identity_terminal_observations')),
    ('missing_absent_summary',lambda r:r.pop('known_descendants_same_identity_absent_at_observation')),
    ('native_boolean',lambda r:r.update(native_exit_code=False)),
    ('wrapper_boolean',lambda r:r.update(wrapper_exit_code=True)),
    ('wrapper_float',lambda r:r.update(wrapper_exit_code=2.0)),
    ('unknown_count_boolean',lambda r:r.update(unknown_count=True)),
    ('unknown_exception_missing',lambda r:r['unknown_samples'][0].pop('exception')),
    ('unknown_phase_missing',lambda r:r['unknown_samples'][0].pop('phase')),
    ('unknown_birth_boolean',lambda r:r['unknown_samples'][0].update(create_time=True)),
    ('unknown_pid_boolean',lambda r:r['unknown_samples'][0].update(pid=True)),
    ('unknown_mismatch',lambda r:r.update(unknown_count=25)),
    ('terminal_sixfield_missing',lambda r:r['known_descendant_identity_terminal_observations'][0].pop('cwd')),
    ('terminal_state_unknown',lambda r:r['known_descendant_identity_terminal_observations'][0].update(observed_status='UNKNOWN')),
    ('terminal_status_missing',lambda r:r['known_descendant_identity_terminal_observations'][0].pop('observed_status')),
    ('terminal_exists_integer',lambda r:r['known_descendant_identity_terminal_observations'][0].update(same_identity_exists=0)),
    ('terminal_alive_contradiction',lambda r:r['known_descendant_identity_terminal_observations'][0].update(same_identity_exists=True)),
    ('terminal_empty',lambda r:r.update(known_descendant_identity_terminal_observations=[])),
    ('absence_summary_contradiction',lambda r:r.update(known_descendants_same_identity_absent_at_observation=False)),
    ('absence_summary_integer',lambda r:r.update(known_descendants_same_identity_absent_at_observation=1)),
    ('budget_string_empty',lambda r:r.update(budget_stop='')),
    ('budget_integer',lambda r:r.update(budget_stop=0)),
    ('generic_capture',lambda r:r.update(capture_target_kind='GENERIC_CANARY')),
    ('launcher_ppid_boolean',lambda r:r['launcher_identity'].update(ppid=False)),
    ('launcher_birth_boolean',lambda r:r['launcher_identity'].update(create_time=True)),
    ('terminal_child_unbound',lambda r:r['known_descendant_identity_terminal_observations'][0].update(pid=987654321)),
    ('collect_gate_in_SOURCE',lambda r:r.update(consumed_gate=request['config'])),
    ('absolute_peak_false',lambda r:r.update(absolute_tree_peak_bytes=1)),
    ('sample_peak_boolean',lambda r:r.update(sampled_owned_tree_peak_bytes=False)),
    ('tool_version_missing',lambda r:r.pop('psutil')),
    ('confirmed_exit_missing',lambda r:r.pop('confirmed_capture_exits')),
]
for name,change in variants:
    record=copy.deepcopy(actual);change(record)
    save(HERE/(name+'.json'),dict(fixture_test=True,record=record))
    check('reject_'+name,lambda record=record:reject(lambda:c.capture_schema(record)))
# 合法未知/复用终态保持三态语义；只测试schema，不操作真实PID。
terminal=copy.deepcopy(actual['known_descendant_identity_terminal_observations'][0])
alive=copy.deepcopy(terminal);alive.update(observed_status='ALIVE',same_identity_exists=True,actual={k:terminal[k] for k in c.IDENTITY})
check('valid_alive_terminal_schema',lambda:c.terminal_schema(alive))
changed=copy.deepcopy(alive);changed['actual']['ppid']+=1;changed.update(observed_status='IDENTITY_CHANGED',same_identity_exists=None)
check('valid_changed_terminal_schema',lambda:c.terminal_schema(changed))
reuse=copy.deepcopy(terminal);reuse.update(observed_status='PID_REUSED',same_identity_exists=False,new_object_untouched=True)
check('valid_reused_terminal_schema',lambda:c.terminal_schema(reuse))
unknown=copy.deepcopy(terminal);unknown.update(observed_status='UNKNOWN_ACCESS_DENIED',same_identity_exists=None,exception='独立逻辑权限未知')
check('valid_unknown_terminal_schema',lambda:c.terminal_schema(unknown))
reuse.pop('new_object_untouched')
check('reject_reused_without_untouched',lambda:reject(lambda:c.terminal_schema(reuse)))
check('reject_fake_budget_PASS',lambda:reject(lambda:c.budget(request['budget_records'],'PASS')))
check('reject_wrong_actual_after_hash',lambda:reject(lambda:c.verify(dict(request,source_after=dict(request['source_after'],sha256='0'*64)))))

# 原入口逐字节复制到相同层级新审查目录，真实CLI只改受授权的输出目录。
copy_entry=HERE/'source_closure.py';copy_entry.write_bytes(entry.read_bytes());require(c.binding(copy_entry)['sha256']==c.binding(entry)['sha256'])
out=HERE/'s15_source_closure_independent_r01'
command=[sys.executable,'-X','utf8','-B',str(copy_entry),'--request',str(W/'actual_request_r01.json'),'--output-dir',str(out)]
start=time.monotonic()
with (HERE/'actual.stdout.bin').open('xb') as so,(HERE/'actual.stderr.bin').open('xb') as se:
    child=subprocess.Popen(command,cwd=ROOT,stdout=so,stderr=se,creationflags=subprocess.DETACHED_PROCESS)
    code=child.wait(timeout=60)
wait=dict(command=command,native_exit_code=code,direct_child_wait_returned=True,elapsed_seconds=time.monotonic()-start,entry_original=c.binding(entry),entry_copy=c.binding(copy_entry),stdout=c.binding(HERE/'actual.stdout.bin'),stderr=c.binding(HERE/'actual.stderr.bin'),limits='仅轻量逐文件字节核封，无Git/重编译/ROSS/硬件')
save(HERE/'actual.wait.json',wait)
check('independent_real_before_after_package_native0',lambda:require(code==0))
pack=c.read(out/'source_closure_receipt.json');manifest=c.read(out/'delivery_manifest.json')
check('independent_manifest_every_hash',lambda:[c.bound(dict(path=r['path'],sha256=r['sha256'],bytes=(ROOT/r['path']).stat().st_size)) for r in manifest['files']] and len(manifest['files']))
check('independent_raw_mapping_complete_bytes',lambda:require(all(c.binding(c.relative(r['original']['path']))==r['original'] and c.binding(c.relative(r['saved']['path']))==r['saved'] and r['original']['sha256']==r['saved']['sha256'] for r in pack['raw_mapping'])))
check('independent_package_failure_originals_NOT_IN_SCOPE',lambda:require(pack['mcp9_sta_validation']=='NOT_IN_SCOPE' and pack['budget']['status']=='BLOCKED' and [(r['original_wrapper_exit_code'],r['unknown_count']) for r in pack['captures']]==[(2,27),(2,26)] and len([r for r in manifest['checks'] if r['status']=='FAIL' and r['exit_code']==2])==2))
repeat_start=time.monotonic()
with (HERE/'existing.stdout.bin').open('xb') as so,(HERE/'existing.stderr.bin').open('xb') as se:
    repeat=subprocess.Popen(command,cwd=ROOT,stdout=so,stderr=se,creationflags=subprocess.DETACHED_PROCESS);repeat_code=repeat.wait(timeout=60)
save(HERE/'existing.wait.json',dict(command=command,native_exit_code=repeat_code,direct_child_wait_returned=True,elapsed_seconds=time.monotonic()-repeat_start,stdout=c.binding(HERE/'existing.stdout.bin'),stderr=c.binding(HERE/'existing.stderr.bin')))
check('actual_existing_directory_CLI1_no_overwrite',lambda:require(repeat_code==1 and all(c.binding(c.relative(r['saved']['path']))==r['saved'] for r in pack['raw_mapping'])))
check('STOP_original_entry_config_tool_hashes',lambda:require(c.binding(entry)==g1['implementation'] and c.binding(c.CONFIG)==request['config'] and all(c.binding(c.relative(r['path']))==r for r in tools)))
result=dict(status='PASS_SOURCE_CLOSURE_TOOL_G2_ONLY' if all(r['status']=='PASS' for r in checks) else 'CHANGES_REQUIRED',checks=checks,entry=c.binding(entry),g1_receipt=c.binding(W/'g1_receipt.json'),frozen_inventory=c.binding(W/'frozen_inventory.json'),reviewed_572_originals=len(inventory['files']),actual_native=wait,existing_native_exit_code=repeat_code,package_receipt=c.binding(out/'source_closure_receipt.json'),package_manifest=c.binding(out/'delivery_manifest.json'),scope='SOURCE_ONLY',mcp9_sta_validation='NOT_IN_SCOPE',source_commit=c.SOURCE,tools_unchanged=tools,hardware_ross_vivado_git=False)
save(HERE/'review_result.json',result)
print(json.dumps(dict(status=result['status'],checks=len(checks),failures=[r for r in checks if r['status']=='FAIL'],native0_elapsed=wait['elapsed_seconds'],repeat_exit=repeat_code,files=len(manifest['files'])),ensure_ascii=False))
