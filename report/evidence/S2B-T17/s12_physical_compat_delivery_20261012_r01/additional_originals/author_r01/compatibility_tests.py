"""完整隔离草稿的真实哈希/schema/history模拟；所有文件与码均明确为合成夹具。"""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import types
import compat_pins as p

WORK=p.WORK; ROOT=p.ROOT; FIX=WORK/'fixtures'; FIX.mkdir()
results=[]

def save(path,value):
 """夹具仅在新的隔离目录创建，不覆盖原件。"""
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x',encoding='utf-8',newline='\n') as stream: json.dump(value,stream,ensure_ascii=False,indent=2); stream.write('\n')

def module(name,path):
 """导入完整待审草稿，不启动CLI运行。"""
 spec=importlib.util.spec_from_file_location(name,path); item=importlib.util.module_from_spec(spec); spec.loader.exec_module(item); return item

def case(name,action,expected=None):
 """明确记录合成接受或拒绝，不把夹具返回值当物理STA/预算结果。"""
 try:
  value=action()
  assert expected is None,'误接受：'+name
  results.append(dict(name=name,status='PASS_FIXTURE_ONLY',outcome='accepted_synthetic_or_read_only',detail=value))
 except (ValueError,AssertionError) as error:
  assert expected is not None and expected in str(error),name+':'+repr(error)
  results.append(dict(name=name,status='PASS_FIXTURE_ONLY',outcome='rejected',exception=repr(error)))

c=module('s12_compat_synth',WORK/'collector.py')
impl=module('s12_compat_impl',WORK/'impl_collector.py')
after=module('s12_compat_after',WORK/'source_after_check.py')
for name in ('collector.py','impl_collector.py','source_after_check.py','native_source_after.py','native.py','compat_pins.py'):
 case('完整AST '+name,lambda name=name: bool(ast.parse((WORK/name).read_text(encoding='utf-8')).body))
case('待最终冻结门禁直接阻断',p.require_ready,'BLOCKED_PENDING_S12_PINS')
case('固定guard永久对象',lambda: p.resolve_permanent(p.GUARD,p.GUARD_SHA))
case('固定supervisor永久对象',lambda: p.resolve_permanent(p.SUP,p.SUP_SHA))
case('RAW相同',lambda:after.compare_raw(b'abc\n',b'abc\n'))
case('精确LF到CRLF',lambda:after.compare_raw(b'a\nb\n',b'a\r\nb\r\n'))
case('内容变化拒绝',lambda:after.compare_raw(b'a\n',b'b\n'),'Git blob与RAW')
case('混合换行不规范化',lambda:after.compare_raw(b'a\r\nb\n',b'a\r\nb\r\n'),'Git blob与RAW')
case('增加末尾字节拒绝',lambda:after.compare_raw(b'a\n',b'a\n\n'),'Git blob与RAW')

original_ready=p.require_ready
p.require_ready=lambda pnr=False:None
try:
 def schema_test(name,mutate=None,expected=None):
  """实际创建43源和快照哈希；静态检查器替身只提供显式33/原14契约。"""
  base=FIX/'schema'/name; base.mkdir(parents=True)
  profile=dict(version='s2b-inference-platform/0.1.12',rtl_sources=['src/FIXTURE_'+str(i)+'.sv' for i in range(18)],source_derivation=dict(derived_sources=['FIXTURE_D'+str(i) for i in range(8)]),clock_hz=50000000,visibility_default=0)
  names=['board/s2b_inference_platform.json']+profile['rtl_sources']+['fixture_source_'+str(i)+'.txt' for i in range(24)]
  files={name:(json.dumps(profile).encode('utf-8') if name.startswith('board/') else ('SYNTHETIC '+name+'\n').encode('utf-8')) for name in names}
  hashes={name:hashlib.sha256(raw).hexdigest() for name,raw in files.items()}
  frozen14={name:hashes[name] for name in names[1:15]}; static={name:hashes[name] for name in names[:33]}
  freeze=dict(profile='s2b-inference-platform/0.1.12',source_files=[dict(path=name,sha256=hashes[name]) for name in names],active_rtl_sources=profile['rtl_sources'][:],frozen14=frozen14.copy(),fixture_test=True)
  if mutate: mutate(freeze,profile,files,static)
  files['board/s2b_inference_platform.json']=json.dumps(profile).encode('utf-8')
  board_hash=hashlib.sha256(files['board/s2b_inference_platform.json']).hexdigest()
  for row in freeze['source_files']:
   if row['path']=='board/s2b_inference_platform.json': row['sha256']=board_hash
  if 'board/s2b_inference_platform.json' in static: static['board/s2b_inference_platform.json']=board_hash
  for path,raw in files.items():
   target=base/path; target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb') as stream: stream.write(raw)
  freeze_path=base/'freeze.json'; save(freeze_path,freeze)
  old_root,old_freeze,old_sha=c.ROOT,c.FREEZE,c.FREEZE_SHA
  old_spec=c.importlib.util.spec_from_file_location; old_mod=c.importlib.util.module_from_spec
  checker=types.SimpleNamespace(check_static=lambda root:static,FROZEN_CORE_SHA256=frozen14)
  class Loader:
   """只提供夹具静态检查器，无生产文件读取。"""
   def exec_module(self,item): item.check_static=checker.check_static; item.FROZEN_CORE_SHA256=checker.FROZEN_CORE_SHA256
  c.ROOT=base; c.FREEZE=freeze_path; c.FREEZE_SHA=hashlib.sha256(freeze_path.read_bytes()).hexdigest()
  c.importlib.util.spec_from_file_location=lambda *args:types.SimpleNamespace(loader=Loader())
  c.importlib.util.module_from_spec=lambda spec:types.SimpleNamespace()
  checker_path=base/'verification/check_s2b_inference_platform.py'; checker_path.parent.mkdir()
  with checker_path.open('x',encoding='utf-8') as stream:stream.write('"""合成静态契约替身，非生产检查器。"""\n')
  try:
   def action():
    f,h,s,profile_actual=c.load_freeze(); return dict(source_count=len(h),static_count=len(s),rtl_count=len(profile_actual['rtl_sources']),derived_count=len(profile_actual['source_derivation']['derived_sources']),frozen14_count=len(f['frozen14']),scope='SYNTHETIC_FIXTURE_ONLY')
   case('source schema '+name,action,expected)
  finally:
   c.ROOT,c.FREEZE,c.FREEZE_SHA=old_root,old_freeze,old_sha
   c.importlib.util.spec_from_file_location,c.importlib.util.module_from_spec=old_spec,old_mod
 schema_test('valid_43_33_18_8_14')
 schema_test('old_profile',lambda f,p,r,s:f.update(profile='s2b-inference-platform/0.1.11'),'freeze版本')
 schema_test('missing_source',lambda f,p,r,s:f['source_files'].pop(),'43源')
 schema_test('duplicate_source',lambda f,p,r,s:f['source_files'].__setitem__(-1,copy.deepcopy(f['source_files'][0])),'freeze版本或路径重复')
 schema_test('static32',lambda f,p,r,s:s.pop(next(reversed(s))),'static33')
 schema_test('frozen13',lambda f,p,r,s:f['frozen14'].pop(next(iter(f['frozen14']))),'原14声明')
 schema_test('frozen_sha_drift',lambda f,p,r,s:f['frozen14'].__setitem__(next(iter(f['frozen14'])),'0'*64),'原14固定SHA')
 schema_test('raw_source_drift',lambda f,p,r,s:r.__setitem__('src/FIXTURE_0.sv',b'CHANGED'),'已审源漂移')
 schema_test('rtl17',lambda f,p,r,s:p['rtl_sources'].pop(),'实际18RTL')
 schema_test('derived7',lambda f,p,r,s:p['source_derivation']['derived_sources'].pop(),'8派生')
 schema_test('clock_drift',lambda f,p,r,s:p.update(clock_hz=100000000),'8派生')
 schema_test('visibility1',lambda f,p,r,s:p.update(visibility_default=1),'8派生')

 def history_test(name,pnr=True,mutate=None,expected=None,invalid_code=None):
  """真实原字节绑定的合成history；从未执行其中Tcl命令。"""
  base=FIX/'history'/name; base.mkdir(parents=True)
  common=impl.c if pnr else c
  commit='0'*40
  labels=['launch','wait','open_run','reports','close'] if pnr else list(c.LABELS)
  commands=['launch_runs impl_1 -to_step {phys_opt_design (Post-Route)} -jobs 1','wait_on_run impl_1','open_run impl_1','report_timing_summary -file {SYNTHETIC.rpt}','close_project'] if pnr else ['source {SYNTHETIC.tcl}','SYNTHETIC_BUILDER','SYNTHETIC_SETUP','launch_runs synth_1 -jobs 1','wait_on_run synth_1','open_run synth_1','report_timing_summary -file {SYNTHETIC.rpt}','SYNTHETIC_QUERY','close_project']
  if invalid_code is not None:
   labels.insert(0,'launch_invalid'); commands.insert(0,'launch_runs impl_1 -to_step post_route_phys_opt_design -jobs 1')
  history=[dict(id=i,command=command,code=invalid_code if label=='launch_invalid' else 0,fixture_test=True) for i,(label,command) in enumerate(zip(labels,commands),1)]
  calls=[dict(input=dict(command=row['command']),result=dict(content=[dict(type='text',text=json.dumps(dict(exit_code=row['code'])))]),fixture_test=True) for row in history]
  gate=dict(root_explicit_signal='CLOSED_PNR_INPUTS_READY' if pnr else 'CLOSED_INPUTS_READY',project_closed=True,owned_root_exited=True,source_commit=commit,root_declared_implementation_execution_count=1,root_declared_products_execution_count=1,root_declared_synthesis_execution_count=1,design_mcp_records=[],additional_closed_files=[],native_files=[],approved_evidence=[],fixture_test=True)
  extra={}
  if mutate: mutate(gate,history,calls,labels,extra)
  for i,(label,call) in enumerate(zip(labels,calls),1):
   path=base/('call_'+str(i)+'.json'); save(path,call)
   row=common.binding(path); row.update(id=history[i-1]['id'],label=label); gate['design_mcp_records'].append(row)
  history_path=base/'history.json'; save(history_path,dict(content=[dict(type='text',text=json.dumps(dict(history=history)))]))
  log=base/'synthetic_log.json'; save(log,dict(fixture_test=True,not_real_result=True))
  keys=('source_before','source_after','source_before_native','source_after_native','mcp_history','immutable_session_log','guard_receipt','supervisor_receipt','owned_root_exit_proof','resource_admission') if pnr else ('preparation_receipt','source_before','source_after','static_source_closed','immutable_session_log','mcp_history')
  for key in keys: gate[key]=common.binding(history_path if key=='mcp_history' else log)
  if extra.get('hash_drift'): gate['design_mcp_records'][0]['sha256']='0'*64
  if extra.get('id_declared_drift'): gate['design_mcp_records'][0]['id']=999
  if extra.get('declared_duplicate_id'): gate['design_mcp_records'][1]['id']=gate['design_mcp_records'][0]['id']
  gate_path=base/'gate.json'; save(gate_path,gate)
  old_commit=impl.COMMIT; impl.COMMIT=commit
  try:
   def action():
    value=impl.closed_gate(gate_path) if pnr else c.closed_gate(gate_path,commit)
    return dict(scope='SYNTHETIC_HISTORY_ONLY',actual_hashes_checked=True,accepted=True,paired=len(value[1]) if pnr else None)
   case(('PNR ' if pnr else 'synth ')+name,action,expected)
  finally: impl.COMMIT=old_commit
 history_test('valid_no_invalid')
 history_test('actual_invalid_nonzero',invalid_code=1)
 history_test('actual_invalid_other_nonzero',invalid_code=2)
 history_test('invalid_zero',expected='可选历史invalid',invalid_code=0)
 history_test('invalid_unknown',expected='可选历史invalid',invalid_code='UNKNOWN')
 def wrong_token(g,h,c,l,e):
  h[0]['command']='launch_runs impl_1 -to_step post_route_phys_opt_design -jobs 1';c[0]['input']['command']=h[0]['command']
 history_test('wrong_success_token',mutate=wrong_token,expected='合法launch不是')
 history_test('input_history_drift',mutate=lambda g,h,c,l,e:c[0]['input'].update(command='launch_runs impl_1 -jobs 1'),expected='命令输入/history')
 history_test('client_native_drift',mutate=lambda g,h,c,l,e:c[0]['result'].update(content=[dict(type='text',text=json.dumps(dict(exit_code=2)))]),expected='客户端/原生返回码')
 history_test('actual_bound_hash_drift',mutate=lambda g,h,c,l,e:e.update(hash_drift=True),expected='输入漂移')
 history_test('declared_id_drift',mutate=lambda g,h,c,l,e:e.update(id_declared_drift=True),expected='声明history id')
 history_test('declared_id_duplicate',mutate=lambda g,h,c,l,e:e.update(declared_duplicate_id=True),expected='声明history id')
 history_test('history_id_duplicate',mutate=lambda g,h,c,l,e:h[1].update(id=h[0]['id']),expected='完整原生history闭包')
 history_test('missing_wait',mutate=lambda g,h,c,l,e:l.__setitem__(1,'extra_query'),expected='必需PNR标签')
 history_test('duplicate_launch_label',mutate=lambda g,h,c,l,e:l.__setitem__(1,'launch'),expected='必需PNR标签')
 history_test('root_not_closed',mutate=lambda g,h,c,l,e:g.update(owned_root_exited=False),expected='ROOT关闭门禁')
 history_test('project_not_closed',mutate=lambda g,h,c,l,e:g.update(project_closed=False),expected='ROOT关闭门禁')
 history_test('commit_drift',mutate=lambda g,h,c,l,e:g.update(source_commit='1'*40),expected='ROOT关闭门禁')
 def launch_twice(g,h,c,l,e):
  h.append(dict(id=99,command=h[0]['command'],code=0));c.append(copy.deepcopy(c[0]));l.append('extra_query')
 history_test('second_success_launch',mutate=launch_twice,expected='合法impl启动不是一次')
 def close_fail(g,h,c,l,e):
  h[-1]['code']=1;c[-1]['result']['content'][0]['text']=json.dumps(dict(exit_code=1))
 history_test('close_native_failure',mutate=close_fail,expected='工程关闭失败')
 history_test('actual_client_timeout_distinct',mutate=lambda g,h,c,l,e:c[0]['result'].update(isError=True),expected=None)
 history_test('nine_labels_real_hash_schema',pnr=False)
 history_test('source_hash_drift',pnr=False,mutate=lambda g,h,c,l,e:e.update(hash_drift=True),expected='声明原件漂移')
 history_test('source_missing_products',pnr=False,mutate=lambda g,h,c,l,e:g.update(root_declared_products_execution_count=0),expected='products/synth只执行一次')
 history_test('source_closed_false',pnr=False,mutate=lambda g,h,c,l,e:g.update(project_closed=False),expected='ROOT关闭门禁')
 history_test('source_wrong_nine_labels',pnr=False,mutate=lambda g,h,c,l,e:l.reverse(),expected='实际九design命令')
finally:
 p.require_ready=original_ready

def recovery_negative(name,mutate,expected):
 """复制最小映射/入口和两个工具对象用于负向核查，不执行恢复。"""
 base=FIX/'recovery'/name;base.mkdir(parents=True)
 mapping=json.loads((p.ARCHIVE/'archive_mapping.json').read_text(encoding='utf-8'))
 recovery=json.loads((p.ARCHIVE/'recovery_entry.json').read_text(encoding='utf-8'))
 mapping['binding_rows']=[row for row in mapping['binding_rows'] if row['original_absolute_path'] in (str(p.GUARD),str(p.SUP))]
 for original in (p.GUARD,p.SUP):
  target=base/original.name
  with target.open('xb') as stream:stream.write(original.read_bytes())
  for row in mapping['binding_rows']:
   if row['original_absolute_path']==str(original):row['archived_repo_path']=target.relative_to(ROOT).as_posix()
  for row in recovery['tool_files']:
   if row['destination_absolute_path']==str(original):row['artifact_repo_path']=target.relative_to(ROOT).as_posix()
 mutate(mapping,recovery,base)
 save(base/'archive_mapping.json',mapping);save(base/'recovery_entry.json',recovery)
 previous=p.ARCHIVE,p.MAPPING_SHA,p.RECOVERY_SHA
 p.ARCHIVE=base;p.MAPPING_SHA=hashlib.sha256((base/'archive_mapping.json').read_bytes()).hexdigest();p.RECOVERY_SHA=hashlib.sha256((base/'recovery_entry.json').read_bytes()).hexdigest()
 try:case('永久恢复 '+name,lambda:p.resolve_permanent(p.GUARD,p.GUARD_SHA),expected)
 finally:p.ARCHIVE,p.MAPPING_SHA,p.RECOVERY_SHA=previous
recovery_negative('fixed_destination_changed',lambda m,r,b:r['tool_files'][0].update(destination_absolute_path=str(p.GUARD)+'_WRONG'),'原绝对恢复目标')
recovery_negative('fixed_guard_sha_changed',lambda m,r,b:r.update(fixed_guard_sha256='0'*64),'恢复固定工具SHA')
recovery_negative('mapping_original_changed',lambda m,r,b:[row.update(original_absolute_path=row['original_absolute_path']+'_WRONG') for row in m['binding_rows'] if row['original_absolute_path']==str(p.GUARD)],'正式映射缺少')
def changed_artifact(m,r,b):
 with (b/'guard.py').open('ab') as stream:stream.write(b'\n')
recovery_negative('artifact_raw_drift',changed_artifact,'冻结输入漂移')
def ambiguous(m,r,b):
 row=copy.deepcopy(next(row for row in m['binding_rows'] if row['original_absolute_path']==str(p.GUARD)));row['archived_repo_path']=p.GUARD.relative_to(ROOT).as_posix();m['binding_rows'].append(row)
recovery_negative('ambiguous_mapping',ambiguous,'归档映射对象不唯一')

case('测试结束真实pins仍缺失并阻断',p.require_ready,'BLOCKED_PENDING_S12_PINS')
save(WORK/'fixture_results.json',dict(status='PASS_ISOLATED_COMPAT_LOGIC_ONLY',count=len(results),cases=results,
 fixture_codes_are_synthetic=True,fixture_paths_are_isolated=True,static_checker_replaced_only_in_fixture=True,
 gate_freeze_readiness_replaced_only_in_fixture=True,actual_hash_binding_and_exact_paths_not_mocked=True,
 source_commit=None,functional_g2='NOT_PINNED',physical_g0='BLOCKED',actual_sta='NOT_RUN',actual_new_budget='NOT_RUN',old_s11_budget='BLOCKED',production_modified=False))
print(json.dumps(dict(status='PASS_ISOLATED_COMPAT_LOGIC_ONLY',cases=len(results)),ensure_ascii=False))
