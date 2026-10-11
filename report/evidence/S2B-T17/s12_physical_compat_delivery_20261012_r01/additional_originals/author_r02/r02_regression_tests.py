"""复现r01两个P2并核r02关闭；使用真实隔离文件绑定，Tcl/Git全部为显式模拟。"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import types
import compat_pins as p

WORK=p.WORK; ROOT=p.ROOT; OLD=ROOT/'tmp/2B/S2B-T17/s12_physical_compat_prepare_20261012_r01'
FIX=WORK/'r02_regression_fixtures';FIX.mkdir()
def module(name,path):
 """只导入源码，不执行任何CLI或设备动作。"""
 spec=importlib.util.spec_from_file_location(name,path);item=importlib.util.module_from_spec(spec);spec.loader.exec_module(item);return item
old_impl=module('p2_old_impl',OLD/'impl_collector.py');new_impl=module('p2_new_impl',WORK/'impl_collector.py')
old_synth=module('p2_old_synth',OLD/'collector.py');new_synth=module('p2_new_synth',WORK/'collector.py')
results=[];counter=0
original_dump=json.dump
def save(path,value):
 """只在本任务新夹具目录创建真实文件及字节哈希。"""
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x',encoding='utf-8',newline='\n') as stream:original_dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n')
def expected(name,action,message=None):
 """模拟接受或拒绝与实际物理审批分列。"""
 try:
  detail=action();assert message is None,'误接受：'+name
  results.append(dict(name=name,status='PASS_FIXTURE_ONLY',outcome='accepted_synthetic',detail=detail))
 except ValueError as error:
  assert message is not None and message in str(error),name+':'+repr(error)
  results.append(dict(name=name,status='PASS_FIXTURE_ONLY',outcome='rejected',actual_exception=repr(error)))

previous_ready,previous_pin=p.require_ready,p.SOURCE_COMMIT
p.require_ready=lambda pnr=False:None;p.SOURCE_COMMIT='0'*40
try:
 def pnr_gate(tool,name,bad_label=None,bad_code=0,timeout=False,client_code_override='SAME',invalid_code='ABSENT',invalid_wrong=False,invalid_duplicate=False):
  """每次形成真实JSON/hash闭包，history码与命令始终标fixture_test。"""
  global counter
  counter+=1;base=FIX/'pnr'/str(counter);base.mkdir(parents=True)
  labels=['launch','wait','open_run','reports','close'];commands=[tool.APPROVED_LAUNCH,'wait_on_run impl_1','open_run impl_1','report_timing_summary -file {SYNTHETIC.rpt}','close_project']
  if invalid_code!='ABSENT':
   labels.insert(0,'launch_invalid');commands.insert(0,'launch_runs impl_1 -to_step post_route_phys_opt_design -jobs 1' if not invalid_wrong else 'launch_runs impl_1 -to_step WRONG -jobs 1')
   if invalid_duplicate:labels.insert(0,'launch_invalid');commands.insert(0,commands[0])
  history=[];declared=[]
  for number,(label,command) in enumerate(zip(labels,commands),1):
   code=invalid_code if label=='launch_invalid' else bad_code if label==bad_label else 0
   client=code if client_code_override=='SAME' or label!=bad_label else client_code_override
   row=dict(id=number,command=command,code=code,fixture_test=True);history.append(row)
   result=dict(content=[dict(type='text',text=json.dumps(dict(exit_code=client)))])
   if timeout and label==bad_label:result['isError']=True
   path=base/('call_'+str(number)+'.json');save(path,dict(input=dict(command=command),result=result,fixture_test=True))
   bound=tool.c.binding(path);bound.update(id=number,label=label);declared.append(bound)
  history_path=base/'history.json';save(history_path,dict(content=[dict(type='text',text=json.dumps(dict(history=history)))]))
  generic=base/'SYNTHETIC_INPUT.json';save(generic,dict(fixture_test=True,actual_vivado_executed=False))
  gate=dict(root_explicit_signal='CLOSED_PNR_INPUTS_READY',project_closed=True,owned_root_exited=True,source_commit='0'*40,root_declared_implementation_execution_count=1,design_mcp_records=declared,additional_closed_files=[],native_files=[],fixture_test=True)
  for key in ('source_before','source_after','source_before_native','source_after_native','mcp_history','immutable_session_log','guard_receipt','supervisor_receipt','owned_root_exit_proof','resource_admission'):gate[key]=tool.c.binding(history_path if key=='mcp_history' else generic)
  gate_path=base/'gate.json';save(gate_path,gate)
  old_commit=tool.COMMIT;tool.COMMIT='0'*40
  try:
   _,paired=tool.closed_gate(gate_path)
   return dict(name=name,synthetic_history=True,actual_hashes_verified=True,paired=len(paired),client_timeout_items=[dict(label=row['label'],native_code=row['history']['code'],client_code=row['client_exit_code']) for row in paired if row['client_timeout_or_error']])
  finally:tool.COMMIT=old_commit
 matrix=[]
 for label in ('launch','wait','open_run','reports','close'):
  for value in (1,None,False,0.0,'0'):
   name=label+':'+repr(value);old_accepted=False
   try:pnr_gate(old_impl,'r01_'+name,bad_label=label,bad_code=value);old_accepted=True
   except ValueError:pass
   expected('r02严格25矩阵 '+name,lambda label=label,value=value:pnr_gate(new_impl,name,bad_label=label,bad_code=value),'五必需PNR命令原生码必须严格int0')
   matrix.append(dict(label=label,value=value,type=type(value).__name__,old_accepted=old_accepted,new_rejected=True))
 assert len(matrix)==25 and sum(row['old_accepted'] for row in matrix)==19
 for label in ('launch','wait','open_run','reports','close'):
  expected('timeout+native int0 '+label,lambda label=label:pnr_gate(new_impl,label,bad_label=label,timeout=True))
  for value in (1,None,False,0.0,'0'):
   expected('timeout不掩盖native坏码 '+label+':'+repr(value),lambda label=label,value=value:pnr_gate(new_impl,label,bad_label=label,bad_code=value,timeout=True),'五必需PNR命令原生码必须严格int0')
  for client in (False,0.0,'0',None):
   expected('客户端类型漂移 '+label+':'+repr(client),lambda label=label,client=client:pnr_gate(new_impl,label,bad_label=label,client_code_override=client),'客户端/原生返回码类型或值不同')
 for value in (1,-1,2):expected('optional invalid严格int非0 '+repr(value),lambda value=value:pnr_gate(new_impl,'invalid',invalid_code=value))
 for value in (False,True,None,0.0,1.0,'1','0',0):expected('optional invalid坏类型/0 '+repr(value),lambda value=value:pnr_gate(new_impl,'invalid',invalid_code=value),'可选历史invalid必须')
 expected('optional invalid精确token',lambda:pnr_gate(new_impl,'invalid',invalid_code=1,invalid_wrong=True),'可选历史invalid必须')
 expected('optional invalid唯一性',lambda:pnr_gate(new_impl,'invalid',invalid_code=1,invalid_duplicate=True),'实际invalid失败记录重复')

 def synthetic_dump(obj,stream,*args,**kwargs):
  """将原source成功标记显式改名，不能形成冒充真实Git/source的证据。"""
  if isinstance(obj,dict):
   obj=dict(obj,fixture_test=True,actual_git_calls=0)
   if 'status' in obj:obj['synthetic_expected_status']=obj.pop('status');obj['status']='SYNTHETIC_TEST_ONLY'
  original_dump(obj,stream,*args,**kwargs)
 def complete_source(tool,name,cli_commit='0'*40,head='0'*40,freeze_commit='0'*40,expect_reject=None):
  """完整43 RAW/Git相同的反例；只替换Git及静态checker，真实哈希/快照写入逻辑保留。"""
  base=FIX/'source'/name;base.mkdir(parents=True)
  cache=base/'cache';cache.mkdir();evidence=base/'evidence';evidence.mkdir()
  profile=dict(version='s2b-inference-platform/0.1.12',rtl_sources=['src/FIXTURE_'+str(i)+'.sv' for i in range(18)],source_derivation=dict(derived_sources=['FIXTURE_D'+str(i) for i in range(8)]),clock_hz=50000000,visibility_default=0)
  names=['board/s2b_inference_platform.json']+profile['rtl_sources']+['fixture_extra_'+str(i)+'.txt' for i in range(24)]
  raw={name:(json.dumps(profile).encode() if name.startswith('board/') else ('SYNTHETIC '+name+'\n').encode()) for name in names}
  for path,data in raw.items():
   target=base/path;target.parent.mkdir(parents=True,exist_ok=True)
   with target.open('xb') as stream:stream.write(data)
  hashes={path:hashlib.sha256(data).hexdigest() for path,data in raw.items()};static={path:hashes[path] for path in names[:33]};frozen14={path:hashes[path] for path in names[1:15]}
  freeze=dict(source_commit=freeze_commit,profile=profile['version'],source_files=[dict(path=path,sha256=digest) for path,digest in hashes.items()],frozen14=frozen14,active_rtl_sources=profile['rtl_sources'],fixture_test=True)
  freeze_path=base/'freeze.json';save(freeze_path,freeze)
  checker_path=base/'verification/check_s2b_inference_platform.py';checker_path.parent.mkdir()
  with checker_path.open('x',encoding='utf-8') as stream:stream.write('"""合成静态契约替身。"""\n')
  keys=('ROOT','WORK','CACHE','PROJECT','REPORT','PRE','FREEZE','FREEZE_SHA','git');old_globals={key:getattr(tool,key) for key in keys}
  tool.ROOT=base;tool.WORK=base;tool.CACHE=cache;tool.PROJECT=base/'project_NOT_CREATED';tool.REPORT=evidence/'report_NOT_CREATED';tool.PRE=evidence/'pre_NOT_CREATED';tool.FREEZE=freeze_path;tool.FREEZE_SHA=hashlib.sha256(freeze_path.read_bytes()).hexdigest()
  calls=[]
  def git_fixture(*args):
   calls.append(args)
   if args==('rev-parse','HEAD'):return (head+'\n').encode(),['SYNTHETIC_GIT',*args]
   if args==('diff','--cached','--name-only'):return b'',['SYNTHETIC_GIT',*args]
   assert args[0]=='show';return raw[args[1].split(':',1)[1]],['SYNTHETIC_GIT',*args]
  tool.git=git_fixture
  old_spec,old_mod=tool.importlib.util.spec_from_file_location,tool.importlib.util.module_from_spec
  tool.importlib.util.spec_from_file_location=lambda *args:types.SimpleNamespace(loader=types.SimpleNamespace(exec_module=lambda value:None))
  tool.importlib.util.module_from_spec=lambda spec:types.SimpleNamespace(check_static=lambda root:static,FROZEN_CORE_SHA256=frozen14)
  json.dump=synthetic_dump;captured=io.StringIO()
  try:
   try:
    with contextlib.redirect_stdout(captured):tool.source(cli_commit,'before')
    assert expect_reject is None,'误接受：'+name
    record=json.loads((tool.PRE/'source_before.json').read_text(encoding='utf-8'))
    assert record['status']=='SYNTHETIC_TEST_ONLY' and len(record['source_files'])==43
    return dict(accepted=True,source_commit=record['source_commit'],pin=p.SOURCE_COMMIT,synthetic_git_calls=len(calls),real_git_calls=0,raw_files=43)
   except ValueError as error:
    assert expect_reject is not None and expect_reject in str(error),name+':'+repr(error)
    assert not tool.PRE.exists() and not tool.REPORT.exists() and not tool.PROJECT.exists(),'拒绝前写入了运行落点'
    return dict(rejected=True,error=repr(error),new_run_directories_absent=True,synthetic_git_calls=len(calls),real_git_calls=0)
  finally:
   json.dump=original_dump
   for key,value in old_globals.items():setattr(tool,key,value)
   tool.importlib.util.spec_from_file_location,tool.importlib.util.module_from_spec=old_spec,old_mod
 expected('r01完整source复现pinA/CLI_HEAD_freezeB仍接受',lambda:complete_source(old_synth,'old_B_accepted',cli_commit='1'*40,head='1'*40,freeze_commit='1'*40))
 expected('r02完整source pinA/CLI_HEAD_freezeB先拒绝不建目录',lambda:complete_source(new_synth,'new_B_blocked',cli_commit='1'*40,head='1'*40,freeze_commit='1'*40,expect_reject='SOURCE_COMMIT不同'))
 expected('r02完整source稳定同commit真43RAW接受',lambda:complete_source(new_synth,'new_A_accepted'))
 expected('r02实际HEAD不同先拒绝不建目录',lambda:complete_source(new_synth,'new_HEAD_B',head='1'*40,expect_reject='HEAD与实际提交不同'))
 expected('r02实际freeze.source_commit不同不建目录',lambda:complete_source(new_synth,'new_freeze_B',freeze_commit='1'*40,expect_reject='SOURCE_COMMIT不同'))

 for function in ('source','closed_gate','collect','seal'):
  base=FIX/'entry'/function;base.mkdir(parents=True);report=base/'REPORT_NOT_CREATED';pre=base/'PRE_NOT_CREATED'
  previous=new_synth.REPORT,new_synth.PRE;new_synth.REPORT=report;new_synth.PRE=pre
  try:
   def action(function=function):
    if function=='source':new_synth.source('1'*40,'before')
    elif function=='closed_gate':new_synth.closed_gate(base/'NONEXISTENT_NOT_READ','1'*40)
    else:getattr(new_synth,function)('1'*40,base/'NONEXISTENT_NOT_READ')
   expected('入口不能绕过SOURCE pin '+function,action,'SOURCE_COMMIT不同')
   assert not report.exists() and not pre.exists()
  finally:new_synth.REPORT,new_synth.PRE=previous

 def closed_source(name,freeze_commit='0'*40,before_commit='0'*40,after_commit='0'*40,entry='closed_gate'):
  """同CLI/pinA时检查freeze/before/after原字节字段，collect/seal不能绕过。"""
  base=FIX/'closed_source'/name;base.mkdir(parents=True)
  rows={}
  for key,commit in [('preparation_receipt','0'*40),('source_before',before_commit),('source_after',after_commit),('static_source_closed','0'*40),('immutable_session_log','0'*40),('mcp_history','0'*40)]:
   path=base/(key+'.json');save(path,dict(source_commit=commit,fixture_test=True));rows[key]=new_synth.binding(path)
  declared=[]
  for index,label in enumerate(new_synth.LABELS):
   path=base/('call_'+str(index)+'.json');save(path,dict(fixture_test=True));row=new_synth.binding(path);row.update(label=label);declared.append(row)
  gate=dict(rows,root_explicit_signal='CLOSED_INPUTS_READY',project_closed=True,source_commit='0'*40,root_declared_products_execution_count=1,root_declared_synthesis_execution_count=1,design_mcp_records=declared,additional_closed_files=[],approved_evidence=[],fixture_test=True)
  path=base/'gate.json';save(path,gate);freeze=base/'freeze.json';save(freeze,dict(source_commit=freeze_commit,fixture_test=True))
  previous=new_synth.FREEZE,new_synth.FREEZE_SHA,new_synth.REPORT,new_synth.PRE
  new_synth.FREEZE=freeze;new_synth.FREEZE_SHA=hashlib.sha256(freeze.read_bytes()).hexdigest();new_synth.REPORT=base/'REPORT_NOT_CREATED';new_synth.PRE=base/'PRE_NOT_CREATED'
  try:
   try:
    if entry=='closed_gate':new_synth.closed_gate(path,'0'*40)
    else:getattr(new_synth,entry)('0'*40,path)
    assert freeze_commit==before_commit==after_commit=='0'*40 and entry=='closed_gate','不该接受'
    return dict(accepted=True,fixture_only=True)
   except ValueError as error:
    assert 'SOURCE_COMMIT不同' in str(error) and not new_synth.REPORT.exists() and not new_synth.PRE.exists()
    return dict(rejected=True,error=repr(error),new_directories_absent=True)
  finally:new_synth.FREEZE,new_synth.FREEZE_SHA,new_synth.REPORT,new_synth.PRE=previous
 expected('闭合稳定pinA接受',lambda:closed_source('valid'))
 for entry in ('closed_gate','collect','seal'):
  for field in ('freeze','before','after'):
   args={field+'_commit':'1'*40}
   expected('闭合/'+entry+'/'+field+'提交漂移拒绝',lambda entry=entry,field=field,args=args:closed_source(entry+'_'+field,entry=entry,**args))
finally:
 p.require_ready,p.SOURCE_COMMIT=previous_ready,previous_pin
expected('结束真实最终pins仍None并阻断',p.require_ready,'BLOCKED_PENDING_S12_PINS')
save(WORK/'r02_regression_results.json',dict(status='PASS_COMPAT_LOGIC_FIXTURES_ONLY',count=len(results),cases=results,independent_bad_matrix=matrix,old_matrix_accepted=sum(row['old_accepted'] for row in matrix),new_matrix_rejected=25,actual_Tcl_calls=0,actual_Git_calls=0,physical_g0='BLOCKED',source_commit=None,actual_sta='NOT_RUN',actual_new_budget='NOT_RUN',old_s11_budget='BLOCKED'))
print(json.dumps(dict(status='PASS_COMPAT_LOGIC_FIXTURES_ONLY',cases=len(results),old_matrix_accepted=19,new_matrix_rejected=25),ensure_ascii=False))
