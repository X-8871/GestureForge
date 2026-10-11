"""纯模拟history双射与标签语义，不读取live记录或访问真实进程。"""
import copy,importlib.util,json,types
from pathlib import Path
WORK=Path(__file__).parent; ROOT=WORK.parents[3]
def load(name,file):
 spec=importlib.util.spec_from_file_location(name,WORK/file); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
new=load('new','collector.py'); old=load('old','collector_before_r03.py')
labels=['launch_invalid','launch','wait','open_run','reports','close']
commands=['launch_runs impl_1 -to_step invalid -jobs 1','launch_runs impl_1 -jobs 1','wait_on_run impl_1','open_run impl_1','report_timing_summary -file {MOCK.rpt}; report_route_status','close_project']
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
 return module.closed_gate(Path('gate'))
cases=[]
def run(name,mutate=None,accept=False,extra=False,override=None):
 gate,history=base()
 if extra:
  history.append(dict(id=7,command='puts MOCK_EXTRA',code=0)); gate['design_mcp_records'].append(dict(id=7,label='extra',**binding('call7')))
 if mutate: mutate(gate,history)
 try: evaluate(new,gate,history,override); outcome='ACCEPT'
 except ValueError as error: outcome='REJECT'; reason=str(error)
 assert (outcome=='ACCEPT')==accept,(name,outcome)
 cases.append(dict(name=name,outcome=outcome,reason=None if accept else reason,simulated_gate=gate,simulated_history=history))
gate,history=base(); gate['design_mcp_records'][3].update(id=3,path='fixture/call3')
evaluate(old,gate,history)
run('reviewer_duplicate_wait_id_omits_open',lambda g,h:g['design_mcp_records'][3].update(id=3,path='fixture/call3'))
run('valid_six',accept=True)
run('valid_reordered_declarations',lambda g,h:g['design_mcp_records'].reverse(),accept=True)
run('valid_extra_history',accept=True,extra=True)
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
result=dict(status='PASS_SIMULATED_HISTORY_CLOSURE',cases=cases,count=len(cases),old_review_bug_reproduced=True,new_bug_rejected=True,simulated_not_actual_pnr=True,actual_pnr_or_process_access=False)
with (WORK/'history_test_result_r03.json').open('x',encoding='utf-8',newline='\n') as f: json.dump(result,f,ensure_ascii=False,indent=2); f.write('\n')
print(json.dumps(dict(status=result['status'],count=len(cases),positive=sum(r['outcome']=='ACCEPT' for r in cases),negative=sum(r['outcome']=='REJECT' for r in cases)),ensure_ascii=False))
