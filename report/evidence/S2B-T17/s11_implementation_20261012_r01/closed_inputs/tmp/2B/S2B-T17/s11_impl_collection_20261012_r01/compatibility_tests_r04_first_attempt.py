"""轻量真实关闭输入只读与纯模拟反例；不执行整理或进程查询。"""
import copy,hashlib,importlib.util,json,types
from pathlib import Path
WORK=Path(__file__).parent; ROOT=WORK.parents[3]

def load(name,file):
 spec=importlib.util.spec_from_file_location(name,WORK/file); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

new=load('new_r04','collector.py'); old=load('old_r03','collector_before_r04.py'); common=new.c
labels=['launch_invalid','launch','wait','open_run','reports','close']
commands=['launch_runs impl_1 -to_step invalid -jobs 1',new.APPROVED_LAUNCH,'wait_on_run impl_1','open_run impl_1','report_timing_summary -file {MOCK.rpt}; report_route_status','close_project']

def binding(name): return dict(path='fixture/'+name,sha256='0'*64,bytes=1)

def base():
 history=[dict(id=i+1,command=cmd,code=1 if i==0 else 0) for i,cmd in enumerate(commands)]
 gate=dict(root_explicit_signal='CLOSED_PNR_INPUTS_READY',project_closed=True,owned_root_exited=True,source_commit=new.COMMIT,root_declared_implementation_execution_count=1,additional_closed_files=[],native_files=[])
 for key in ('source_before','source_after','source_before_native','source_after_native','mcp_history','immutable_session_log','guard_receipt','supervisor_receipt','owned_root_exit_proof','resource_admission'): gate[key]=binding(key)
 gate['design_mcp_records']=[dict(id=i+1,label=label,**binding('call'+str(i+1))) for i,label in enumerate(labels)]
 return gate,history

def evaluate(module,gate,history,call_override=None):
 calls={'call'+str(r['id']):dict(input=dict(command=r['command']),result=dict(exit_code=r['code'])) for r in history}
 if call_override: calls.update(call_override)
 def read(p):
  name=Path(p).name
  if name=='gate': return gate
  if name=='mcp_history': return dict(history=history)
  return calls[name]
 def require(condition,message):
  if not condition: raise ValueError(message)
 module.c=types.SimpleNamespace(read=read,binding=lambda p:binding(Path(p).name),require=require,mcp_json=lambda r:r.get('result',r))
 try: return module.closed_gate(Path('gate'))
 finally: module.c=common

cases=[]

def run(name,mutate=None,accept=False,extra=False,override=None):
 gate,history=base()
 if extra:
  history.append(dict(id=7,command='puts MOCK_EXTRA',code=0)); gate['design_mcp_records'].append(dict(id=7,label='extra',**binding('call7')))
 if mutate: mutate(gate,history)
 try: evaluate(new,gate,history,override); outcome='ACCEPT'; reason=None
 except ValueError as error: outcome='REJECT'; reason=str(error)
 assert (outcome=='ACCEPT')==accept,(name,outcome)
 cases.append(dict(name=name,outcome=outcome,reason=reason,simulated_gate=gate,simulated_history=history))

run('valid_exact_postroute',accept=True)
run('valid_reordered_declarations',lambda g,h:g['design_mcp_records'].reverse(),accept=True)
run('valid_extra_history',accept=True,extra=True)
run('reviewer_duplicate_wait_id_omits_open',lambda g,h:g['design_mcp_records'][3].update(id=3,path='fixture/call3'))
run('missing_declaration',lambda g,h:g['design_mcp_records'].pop())
run('unique_id_set_mismatch',lambda g,h:g['design_mcp_records'][3].update(id=42,path='fixture/call4'))
run('duplicate_native_history_id',lambda g,h:h[3].update(id=3))
run('missing_extra_declaration',lambda g,h:g['design_mcp_records'].pop(),extra=True)
run('extra_duplicate_id',lambda g,h:g['design_mcp_records'][-1].update(id=6,path='fixture/call6'),extra=True)

def swap(g,h): g['design_mcp_records'][3]['label'],g['design_mcp_records'][4]['label']=g['design_mcp_records'][4]['label'],g['design_mcp_records'][3]['label']

run('swapped_open_reports_labels',swap)
for i,cmd in enumerate(['wait_on_run impl_1 -to_step invalid','launch_runs impl_10 -jobs 1','open_run impl_1','wait_on_run impl_1','wait_on_run impl_1','puts {close_project}']):
 run('wrong_command_'+labels[i],lambda g,h,i=i,cmd=cmd:h[i].update(command=cmd))
run('reports_word_inside_puts',lambda g,h:h[4].update(command='puts {report_timing_summary}'))
run('open_wrong_run',lambda g,h:h[3].update(command='open_run impl_2'))
run('actual_call_command_diff',override={'call4':dict(input=dict(command='wait_on_run impl_1'),result=dict(exit_code=0))})
run('extra_actual_command_diff',extra=True,override={'call7':dict(input=dict(command='puts DIFFERENT'),result=dict(exit_code=0))})
for index,command in enumerate(['launch_runs impl_1 -to_step {phys_opt_design (PostRoute)} -jobs 1','launch_runs impl_1 -to_step {phys_opt_design (Post-Route)} -jobs 2','launch_runs impl_1 -to_step phys_opt_design -jobs 1','launch_runs impl_1 -jobs 1',new.APPROVED_LAUNCH+'; puts EXTRA']):
 run('unapproved_launch_'+str(index),lambda g,h,command=command:h[1].update(command=command))

def twice(g,h):
 h.append(dict(id=7,command=new.APPROVED_LAUNCH,code=0)); g['design_mcp_records'].append(dict(id=7,label='extra_launch',**binding('call7')))

run('two_successful_launches',twice)
gate_path=ROOT/'tmp/2B/S2B-T17/s11_impl_root_run_20261012_r01/closed_gate_actual_r01.json'
assert common.sha(gate_path)=='3ed4bb61a4157fb7295bee34dc95ddd72966855ec1b485f8ead180726b483368'
gate=common.read(gate_path); actual={}
try: old.closed_gate(gate_path)
except ValueError as error: actual['old_gate_rejection']=repr(error)
else: raise AssertionError('旧r03必须复现实际launch拒绝')
accepted,paired=new.closed_gate(gate_path)
actual['gate_binding']=common.binding(gate_path)
actual['history_binding']=gate['mcp_history']
actual['paired_calls']=[dict(label=r['label'],id=r['history']['id'],command=r['history']['command'],native_history_code=r['history']['code'],client_exit_code=r['client_exit_code'],client_error=r['client_timeout_or_error']) for r in paired]
assert len(paired)==13
assert next(r for r in paired if r['label']=='launch')['history']['id']==6
assert next(r for r in paired if r['label']=='launch_invalid')['history']['id']==4
report=ROOT/'tmp/2B/S2B-T17/s11_impl_root_run_20261012_r01/reports/timing_summary_postroute.rpt'
text=common.exact(report).read_text(encoding='utf-8')
actual['report_binding']=common.binding(report)
try: old.timing(text)
except ValueError as error: actual['old_timing_rejection']=repr(error)
else: raise AssertionError('旧r03必须复现postRoute状态拒绝')
result=new.timing(text)
assert result['status']=='FAIL_TIMING' and result['design_state']=='Physopt postRoute'
assert result['timing']['wns_ns']==-3.201 and result['timing']['tns_ns']==-2123.755
assert result['timing']['setup_failing_endpoints']==908 and result['timing']['setup_total_endpoints']==15082 and result['timing']['hold_failing_endpoints']==0
actual['timing']=result
timing_cases=[]
for state,accept in [('Physopt postRoute',True),('Routed',True),('Fully Routed',True),('Placed',False),('Unrouted',False),('Synthesized',False),('Physopt postroute',False),('Physopt postRoute UNKNOWN',False),('',False)]:
 mutated=text.replace('Physopt postRoute',state)
 try: parsed=new.timing(mutated); outcome='ACCEPT'; reason=None
 except ValueError as error: outcome='REJECT'; reason=str(error)
 assert (outcome=='ACCEPT')==accept,(state,outcome)
 if accept: assert parsed['status']=='FAIL_TIMING' and parsed['timing']==result['timing']
 timing_cases.append(dict(state=state,outcome=outcome,reason=reason,simulated_header_only=True))
output=dict(status='PASS_G1_EXACT_POSTROUTE_COMPATIBILITY',history_cases=cases,history_count=len(cases),timing_cases=timing_cases,actual_readonly=actual,actual_collect_executed=False,external_process_query=False)
with (WORK/'compatibility_result_r04.json').open('x',encoding='utf-8',newline='\n') as f: json.dump(output,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps(dict(status=output['status'],history_cases=len(cases),history_positive=sum(r['outcome']=='ACCEPT' for r in cases),history_negative=sum(r['outcome']=='REJECT' for r in cases),timing_cases=len(timing_cases),actual_history=13,actual_timing_status=result['status']),ensure_ascii=False))
