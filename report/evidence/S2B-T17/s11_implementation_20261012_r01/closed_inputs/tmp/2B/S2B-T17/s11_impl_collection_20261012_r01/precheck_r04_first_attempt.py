"""捕获r04真实轻量原生结果与最小差异；不运行collect或实际source-after。"""
import ast,difflib,hashlib,json,os,subprocess,sys,time
from pathlib import Path
import psutil
WORK=Path(__file__).parent; ROOT=WORK.parents[3]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p,value):
 assert p.parent==WORK and not p.exists()
 with p.open('x',encoding='utf-8',newline='\n') as f: json.dump(value,f,ensure_ascii=False,indent=2); f.write('\n')

def capture(name,args):
 command=[sys.executable,'-X','utf8','-B',str(WORK/args[0]),*args[1:]]; start=time.monotonic(); peak=0
 with (WORK/(name+'.stdout.log')).open('xb') as out,(WORK/(name+'.stderr.log')).open('xb') as err:
  child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err,env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8'))
  while child.poll() is None:
   try: peak=max(peak,psutil.Process(child.pid).memory_info().rss)
   except psutil.Error: pass
   assert time.monotonic()-start<60 and peak<134217728; time.sleep(.02)
 record=dict(command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=child.returncode,elapsed_seconds=time.monotonic()-start,sampled_owned_child_rss_peak_bytes=peak,absolute_peak_bytes=None,stdout_sha256=sha(WORK/(name+'.stdout.log')),stderr_sha256=sha(WORK/(name+'.stderr.log')))
 save(WORK/(name+'.native.json'),record); return record

start=time.monotonic()
old_manifest=WORK/'raw_manifest_r03.jsonl'
assert sha(old_manifest)=='5bd67dd972646252da8a0207670f449c0a1a4aa25f024916a601f93b9da5ed95'
old_bindings=[json.loads(line) for line in old_manifest.read_text(encoding='utf-8').splitlines()]
for row in old_bindings:
 if row['path']!=(WORK/'collector.py').relative_to(ROOT).as_posix(): assert sha(ROOT/row['path'])==row['sha256'],row['path']
assert sha(WORK/'collector_before_r04.py')=='63def20a125a983a86a374bc7bc1eef8e375cb232a5222822c6f886f6a10cbe9'
fixed={'source_after_check.py':'15edba9468b8dd3c99dc55135913cbc98d2f625220d94a10f76b18601346b3a8','native_source_after.py':'8e9a12ce58f5ec045cd6c454d62936d918b6f6a47fa15d096243591855d57ddd'}
for name,digest in fixed.items(): assert sha(WORK/name)==digest
for name in ('collector.py','compatibility_tests_r04.py','source_after_check.py','native_source_after.py'): ast.parse((WORK/name).read_text(encoding='utf-8'))
old=(WORK/'collector_before_r04.py').read_text(encoding='utf-8').splitlines(keepends=True); new=(WORK/'collector.py').read_text(encoding='utf-8').splitlines(keepends=True)
with (WORK/'source_diff_r04.patch').open('x',encoding='utf-8',newline='\n') as f: f.writelines(difflib.unified_diff(old,new,fromfile='collector_before_r04.py',tofile='collector.py'))
tests={}
report=ROOT/'tmp/2B/S2B-T17/s11_impl_root_run_20261012_r01/reports/timing_summary_postroute.rpt'
plans=[('compatibility_r04',['compatibility_tests_r04.py'],0),('collector_help_r04',['collector.py','--help'],0),('collector_missing_gate_r04',['collector.py','collect'],1),('classify_actual_r04',['collector.py','classify','--report',str(report),'--result',str(WORK/'actual_sta_classification_r04.json')],2),('prepare_r04',['collector.py','prepare'],0),('prepare_overwrite_r04',['collector.py','prepare'],1)]
for name,args,expected in plans:
 tests[name]=capture(name,args)
 assert tests[name]['native_exit_code']==expected,(name,tests[name])
for row in old_bindings:
 if row['path']!=(WORK/'collector.py').relative_to(ROOT).as_posix(): assert sha(ROOT/row['path'])==row['sha256'],row['path']
for name,digest in fixed.items(): assert sha(WORK/name)==digest
compatibility=json.loads((WORK/'compatibility_result_r04.json').read_text(encoding='utf-8'))
prepared=json.loads((WORK/'prepared_receipt_r04.json').read_text(encoding='utf-8'))
receipt=dict(status='PASS_G1_POSTROUTE_COMPATIBILITY_ONLY',developer_stop=True,source_commit='a710ec431474841a81912a6055f861e811a151e3',evidence_head_at_preparation='932051cdacdf02f729d6a7554b07118d05e96aa4',git_query_executed=False,commands=tests,elapsed_seconds=time.monotonic()-start,sampled_owned_child_rss_peak_bytes=max(r['sampled_owned_child_rss_peak_bytes'] for r in tests.values()),absolute_peak_bytes=None,source_before_sha256=sha(WORK/'collector_before_r04.py'),source_after_sha256=sha(WORK/'collector.py'),unchanged_adapters=fixed,old_r03_inputs_unchanged_except_authorized_collector=True,old_r03_manifest_sha256=sha(old_manifest),prepared_receipt_sha256=sha(WORK/'prepared_receipt_r04.json'),source_diff_sha256=sha(WORK/'source_diff_r04.patch'),actual_closed_gate=compatibility['actual_readonly']['gate_binding'],actual_readonly=compatibility['actual_readonly'],mock_history_count=compatibility['history_count'],mock_timing_count=len(compatibility['timing_cases']),dependency_bindings=prepared['dependencies'],actual_collect_executed=False,actual_source_after_executed=False,real_external_process_query=False,limitations=['真实已关闭gate仅验证原字节绑定与13history双射；不执行collect或操作实际PID。','模拟错误命令/多次启动/未知状态反例不是新的Vivado运行。','真实报告原生分类2仍FAIL_TIMING：WNS -3.201/TNS -2123.755/908of15082/hold0；r04兼容修复不改变时序结论。','工具G1不能代替独立G2、实际预算/PNR时序关闭、bit/runtime/硬件或G3批准。','本轮未查询Git；源码基线与证据HEAD沿冻结输入分别记录。'])
save(WORK/'tool_receipt_r04.json',receipt)
owned_names={'collector.py','collector_before_r04.py','compatibility_tests_r04.py','precheck_r04.py','source_after_check.py','native_source_after.py','compatibility_result_r04.json','actual_sta_classification_r04.json','source_diff_r04.patch','tool_receipt_r04.json','prepared_receipt_r04.json'}
owned_names.update(name+suffix for name,_,_ in plans for suffix in ('.native.json','.stdout.log','.stderr.log'))
inputs=[old_manifest,WORK/'tool_receipt_r03.json',WORK/'prepared_receipt_r03.json',ROOT/compatibility['actual_readonly']['gate_binding']['path'],ROOT/compatibility['actual_readonly']['history_binding']['path'],report]
gate=json.loads(inputs[3].read_text(encoding='utf-8')); inputs.extend(ROOT/r['path'] for r in gate['design_mcp_records'])
rows=[]
for name in sorted(owned_names):
 p=WORK/name; rows.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),role='source' if p.suffix=='.py' else 'log' if p.suffix=='.log' else 'result'))
for p in inputs: rows.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),role='input'))
with (WORK/'raw_manifest_r04.jsonl').open('x',encoding='utf-8',newline='\n') as f:
 for row in rows: f.write(json.dumps(row,ensure_ascii=False)+'\n')
print(json.dumps(dict(STOP=True,collector_sha256=sha(WORK/'collector.py'),prepared_sha256=sha(WORK/'prepared_receipt_r04.json'),receipt_sha256=sha(WORK/'tool_receipt_r04.json'),raw_manifest_sha256=sha(WORK/'raw_manifest_r04.jsonl'),diff_sha256=sha(WORK/'source_diff_r04.patch'),raw_rows=len(rows),commands=len(tests),mock_history=compatibility['history_count'],mock_timing=len(compatibility['timing_cases']),elapsed_seconds=receipt['elapsed_seconds'],sampled_child_peak_bytes=receipt['sampled_owned_child_rss_peak_bytes']),ensure_ascii=False))
