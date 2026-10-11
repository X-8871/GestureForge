"""仅本隔离目录的AST/help/拒绝门禁与模拟报告解析，不执行实际收集。"""
import ast,hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
import psutil
WORK=Path(__file__).parent; ROOT=WORK.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):
 assert p.parent==WORK and not p.exists()
 with p.open('x',encoding='utf-8',newline='\n') as f: json.dump(obj,f,ensure_ascii=False,indent=2); f.write('\n')
def capture(name,args):
 command=[sys.executable,'-X','utf8','-B',str(WORK/'collector.py'),*args]; start=time.monotonic(); peak=0
 with (WORK/(name+'_r02.stdout.log')).open('xb') as out,(WORK/(name+'_r02.stderr.log')).open('xb') as err:
  p=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err,env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8'))
  while p.poll() is None:
   try: peak=max(peak,psutil.Process(p.pid).memory_info().rss)
   except psutil.Error: pass
   assert time.monotonic()-start<60 and peak<134217728
   time.sleep(.02)
 r=dict(command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=p.returncode,elapsed_seconds=time.monotonic()-start,sampled_owned_child_rss_peak_bytes=peak,stdout_sha256=sha(WORK/(name+'_r02.stdout.log')),stderr_sha256=sha(WORK/(name+'_r02.stderr.log')))
 save(WORK/(name+'_r02.native.json'),r); return r
ast.parse((WORK/'collector.py').read_text(encoding='utf-8'))
tests={}
tests['help']=capture('help',['--help']); assert tests['help']['native_exit_code']==0
tests['missing_gate']=capture('missing_gate',['collect']); assert tests['missing_gate']['native_exit_code']==1
save(WORK/'unclosed_gate_r02.json',{})
tests['unclosed_gate']=capture('unclosed_gate',['collect','--gate',str(WORK/'unclosed_gate_r02.json')]); assert tests['unclosed_gate']['native_exit_code']==1
tests['prepare']=capture('prepare',['prepare']); assert tests['prepare']['native_exit_code']==0
prepared_sha=sha(WORK/'prepared_receipt_r02.json')
tests['overwrite_rejected']=capture('overwrite_rejected',['prepare']); assert tests['overwrite_rejected']['native_exit_code']==1 and sha(WORK/'prepared_receipt_r02.json')==prepared_sha
spec=importlib.util.spec_from_file_location('candidate',WORK/'collector.py'); c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
text=(ROOT/'report/evidence/S2B-T17/s11_platform_20261012_r01/timing_summary_synth.rpt').read_text(encoding='utf-8')
mock=text.replace('Synthesized','Routed'); result=c.timing(mock); assert result['status']=='FAIL_TIMING' and result['timing']['wns_ns']==-4.404
rejected=[]
for name,sample in [('synth_state',text),('missing_check',mock.replace('checking no_clock','checking missing_clock')),('missing_clock',mock.replace('clk_fpga_0','unknown_clock'))]:
 try: c.timing(sample)
 except ValueError: rejected.append(name)
 else: raise AssertionError(name)
save(WORK/'precheck_result_r02.json',dict(status='PASS_PREPARATION_ONLY',developer_stop=True,actual_collect_executed=False,actual_pnr_terminal_consumed=False,real_target_process_or_hardware_access=False,AST=True,commands=tests,simulated_report_cases=4,simulated_not_actual_pnr=True,rejected=rejected,prepared_receipt_sha256=prepared_sha,collector_sha256=sha(WORK/'collector.py'),limitations=['只做冻结依赖/AST/help/门禁与模拟解析，未消费实际PNR、ROOT终态或新STA报告。','所有RSS仅自有轻量Python子进程采样，绝对峰未知；无真实guard/Vivado启动。','collected正式清单需ROOT关闭释放及独立Reviewer；准备0不代表真实预算或时序通过。']))
rows=[]
for p in sorted(WORK.iterdir()):
 if p.is_file() and p.name!='raw_manifest_r02.jsonl': rows.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),role='source' if p.suffix=='.py' else 'log' if p.suffix=='.log' else 'result'))
with (WORK/'raw_manifest_r02.jsonl').open('x',encoding='utf-8',newline='\n') as f:
 for r in rows: f.write(json.dumps(r,ensure_ascii=False)+'\n')
print(json.dumps(dict(status='PASS_PREPARATION_ONLY_STOP',collector_sha256=sha(WORK/'collector.py'),prepared_sha256=prepared_sha,receipt_sha256=sha(WORK/'precheck_result_r02.json'),raw_manifest_sha256=sha(WORK/'raw_manifest_r02.jsonl'),raw_rows=len(rows),commands=len(tests),max_sampled_owned_child_rss_bytes=max(r['sampled_owned_child_rss_peak_bytes'] for r in tests.values())),ensure_ascii=False))
