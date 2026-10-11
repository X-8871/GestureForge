"""只捕获已关闭PNR的一次轻量整理及包装检查，不运行Vivado或外部进程。"""
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
import psutil
WORK=Path(__file__).parent; ROOT=WORK.parents[3]
REPORT=ROOT/'report/evidence/S2B-T17/s11_implementation_20261012_r01'
AUTHOR=ROOT/'tmp/2B/S2B-T17/s11_impl_collection_20261012_r01'
GATE=ROOT/'tmp/2B/S2B-T17/s11_impl_root_run_20261012_r01/closed_gate_actual_r04.json'
REVIEW=ROOT/'tmp/2B/S2B-T17/independent_s11_impl_collector_review_20261012_r03/final_review_receipt.json'
FIXED={AUTHOR/'collector.py':'ee0e697b59d7a9b9b6de22bd44fc93c7fbedade1e1710dd7dfb909e1654a8d35',AUTHOR/'prepared_receipt_r04.json':'3288fd2d1b07d565fd3fdeb1fda779d99e0ad9607158d7652fe9223f6174d6cc',GATE:'fb5f21e364e853b3f6afd22c25b3496c69637808fcefffedf89f9c7c2d7c628e',REVIEW:'76cfd62d545274113d0e5fe862b83737c94f603cd199da9f87fff1f933cd3aa7',REVIEW.with_name('raw_manifest.jsonl'):'6bdd4e36843aa7a2db8aff373489b07bfb71e06becf42e0b1aafab897c0e44ae'}

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def binding(path,role=None):
 row=dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path))
 if role: row['role']=role
 return row

def save(path,value):
 assert path.is_relative_to(WORK) or path.is_relative_to(REPORT)
 assert path.parent.is_dir() and not path.exists(),str(path)
 with path.open('x',encoding='utf-8',newline='\n') as f: json.dump(value,f,ensure_ascii=False,indent=2); f.write('\n')

def capture(name,args):
 """只采样由本次Popen创建的子树，原生码和包装码分别记录。"""
 command=[sys.executable,'-X','utf8','-B',*map(str,args)]; start=time.monotonic(); peak=0; own_peak=0; samples=0; breach=None
 with (WORK/(name+'.stdout.log')).open('xb') as out,(WORK/(name+'.stderr.log')).open('xb') as err:
  child=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err,env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8'))
  while child.poll() is None:
   own=psutil.Process(os.getpid()); own_peak=max(own_peak,own.memory_info().rss)
   try:
    root_child=psutil.Process(child.pid); members=[root_child,*root_child.children(recursive=True)]; rss=0
    for member in members:
     try: rss+=member.memory_info().rss
     except psutil.NoSuchProcess: pass
    peak=max(peak,rss+own.memory_info().rss); samples+=1
   except psutil.NoSuchProcess: pass
   size=sum(p.stat().st_size for directory in (WORK,REPORT) for p in directory.rglob('*') if p.is_file())
   if time.monotonic()-start>120 or peak>134217728 or size>209715200:
    breach=dict(elapsed_seconds=time.monotonic()-start,sampled_owned_tree_rss_bytes=peak,total_scope_bytes=size)
    child.terminate(); child.wait(timeout=5); break
   time.sleep(.05)
 record=dict(command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=child.returncode,elapsed_seconds=time.monotonic()-start,sampled_owned_tree_rss_peak_bytes=peak,sampled_wrapper_rss_peak_bytes=own_peak,samples=samples,absolute_tree_peak_bytes=None,scope='仅本次包装器及其Popen子树；不查询实际Vivado/guard/PID',limits=dict(tree_bytes=134217728,scope_disk_bytes=209715200,seconds=120),budget_breach=breach,stdout=binding(WORK/(name+'.stdout.log')),stderr=binding(WORK/(name+'.stderr.log')))
 save(WORK/(name+'.native.json'),record); return record

def fixed():
 for path,digest in FIXED.items(): assert path.is_file() and sha(path)==digest,str(path)

def collect():
 fixed(); assert REPORT.is_dir() and not list(REPORT.iterdir())
 gate=json.loads(GATE.read_text(encoding='utf-8')); assert gate['root_explicit_signal']=='CLOSED_PNR_INPUTS_READY'
 record=capture('collect_r01',[AUTHOR/'collector.py','collect','--gate',GATE])
 print(json.dumps(record,ensure_ascii=False))
 return record['native_exit_code'] or (3 if record['budget_breach'] else 0)

def role(path): return 'source' if path.suffix in ('.py','.sv','.v','.tcl','.xdc') else 'log' if path.suffix in ('.log','.rpt','.vds','.jou') else 'result'

def finalize():
 fixed(); collect_native=json.loads((WORK/'collect_r01.native.json').read_text(encoding='utf-8'))
 assert collect_native['native_exit_code']==0 and collect_native['budget_breach'] is None
 base_path=REPORT/'delivery_manifest.json'; base=json.loads(base_path.read_text(encoding='utf-8'))
 classifier=json.loads((REPORT/'pnr_classifier.native.json').read_text(encoding='utf-8')); sta=json.loads((REPORT/'pnr_sta_result.json').read_text(encoding='utf-8'))
 assert classifier['native_exit_code']==2 and sta['status']=='FAIL_TIMING' and sta['native_exit_code']==2
 closed=json.loads((REPORT/'pnr_closed_binding.json').read_text(encoding='utf-8'))
 assert closed['timing']['status']=='FAIL_TIMING' and closed['budget_status']=='BLOCKED_PENDING_INDEPENDENT_ACTUAL_COVERAGE_REVIEW'
 gate=json.loads(GATE.read_text(encoding='utf-8')); before=json.loads((ROOT/gate['source_before']['path']).read_text(encoding='utf-8')); after=json.loads((ROOT/gate['source_after']['path']).read_text(encoding='utf-8'))
 frozen=json.loads((ROOT/'report/evidence/S2B-T17/maxpool_geometry_factor_20261012_r02/source_freeze.json').read_text(encoding='utf-8'))
 expected={r['path']:r['sha256'] for r in frozen['source_files']}
 assert len(expected)==43 and {r['path']:r['sha256'] for r in before['source_files']}=={r['path']:r['sha256'] for r in after['source_files']}==expected
 checks={}
 for mode,expected_code in (('evidence',0),('inputs',2)):
  record=capture('initial_'+mode+'_r01',[ROOT/'verification/check_stage_delivery.py','--mode',mode,'--manifest',base_path,'--project-root',ROOT])
  checks[mode]=record
  assert record['native_exit_code']==expected_code and record['budget_breach'] is None,(mode,record)
 target=REPORT/'collection_native'; assert not target.exists(); target.mkdir()
 for source in (WORK/'run.py',WORK/'collect_r01.native.json',WORK/'collect_r01.stdout.log',WORK/'collect_r01.stderr.log'):
  shutil.copyfile(source,target/source.name); assert sha(source)==sha(target/source.name)
 assert len(after['static_source_sha256'])==33
 save(REPORT/'s11_implementation_source_binding.json',dict(source_commit=base['source_commit'],source_count=43,static_count=33,active_rtl_count=18,derived_rtl_count=8,frozen14_count=14,profile='s2b-inference-platform/0.1.11',clock_hz=50000000,visibility=0,source_files=frozen['source_files'],static_source_sha256=after['static_source_sha256'],active_rtl_sources=frozen['active_rtl_sources'],frozen14=frozen['frozen14'],before_original=gate['source_before'],after_original=gate['source_after'],before_scope='继承原S11 before与实际launch前43RAW核查；运行中source_during不冒充before/after',after_actual_record=after,restoration_mapping='pnr_closed_binding.json mapping',source_after_executed_by='ROOT；本包装器不执行source-after或Git查询'))
 for mode in ('evidence','inputs'):
  for suffix in ('.native.json','.stdout.log','.stderr.log'):
   source=WORK/('initial_'+mode+'_r01'+suffix); shutil.copyfile(source,target/source.name); assert sha(source)==sha(target/source.name)
 final=dict(base); final['checks']=list(base['checks'])
 final['checks'].append(dict(name='真实关闭后轻量收集',status='PASS',command=collect_native['windows_command'],exit_code=0,reason='只代表收集完成，STA仍FAIL且实际预算BLOCKED。'))
 for mode in ('evidence','inputs'):
  record=checks[mode]; final['checks'].append(dict(name='本轮原清单'+mode+'包装核验',status='PASS' if record['native_exit_code']==0 else 'FAIL',command=record['windows_command'],exit_code=record['native_exit_code'],reason='只读包装原生结果，不替代PNR时序、接口冻结或独立实际证据审查。'))
 for name in ('本次PNR XSA导出','本次bit/runtime/G3/109/1000'):
  final['checks'].append(dict(name=name,status='NOT_RUN',command=None,exit_code=None,reason='本次只采集已有PNR；未生成位流、导出XSA或操作硬件。'))
 final['files']=[binding(p,role(p)) for p in sorted(REPORT.rglob('*')) if p.is_file()]
 for row in base['files']:
  if not (ROOT/row['path']).is_relative_to(REPORT): final['files'].append(row)
 final['limitations']=list(base['limitations'])+['源after由ROOT实际执行；本轮包装器仅校验已关闭原件。','原清单evidence/inputs结果永久保存；最终清单的再核验在隔离运行目录保留，不为绑定它自身制造循环。']
 final_path=REPORT/'delivery_manifest_r02.json'; save(final_path,final)
 finals={}
 for mode,expected_code in (('evidence',0),('inputs',2)):
  record=capture('final_'+mode+'_r01',[ROOT/'verification/check_stage_delivery.py','--mode',mode,'--manifest',final_path,'--project-root',ROOT]); finals[mode]=record
  assert record['native_exit_code']==expected_code and record['budget_breach'] is None,(mode,record)
 receipt=dict(status='COLLECTED_ACTUAL_PNR_FAIL_PENDING_INDEPENDENT_REVIEW',developer_stop=True,source_commit=base['source_commit'],actual_evidence_head_recorded_by_root='932051cdacdf02f729d6a7554b07118d05e96aa4',manifest=binding(final_path),collect=collect_native,classifier=classifier,initial_checks=checks,final_checks=finals,source_binding=binding(REPORT/'s11_implementation_source_binding.json'),timing=sta,resource=dict(guard_status=closed['guard_status'],guard_native_exit_code=closed['guard_native_exit_code'],supervisor_native_exit_code=closed['supervisor_native_exit_code'],sampled_tree_peak_bytes=closed['sampled_tree_peak_bytes'],absolute_tree_peak_bytes=None,budget_status=closed['budget_status']),scope_bytes=sum(p.stat().st_size for directory in (WORK,REPORT) for p in directory.rglob('*') if p.is_file()),heavy_runs_started_by_author=0,collect_execution_count=1,source_after_or_git_or_external_process_query=False,independent_actual_review='NOT_RUN',sta_close='FAIL',bit_xsa_runtime_hardware_g3='NOT_RUN')
 save(WORK/'final_collection_receipt.json',receipt)
 rows=[binding(p,role(p)) for p in sorted(WORK.rglob('*')) if p.is_file()]
 rows.extend(binding(p,'input') for p in FIXED)
 rows.extend(binding(p,'input') for p in (final_path,REPORT/'pnr_closed_binding.json',REPORT/'s11_implementation_source_binding.json',REPORT/'pnr_sta_result.json',REPORT/'pnr_classifier.native.json'))
 with (WORK/'raw_manifest.jsonl').open('x',encoding='utf-8',newline='\n') as f:
  for row in rows: f.write(json.dumps(row,ensure_ascii=False)+'\n')
 print(json.dumps(dict(STOP=True,manifest=binding(final_path),manifest_files=len(final['files']),receipt=binding(WORK/'final_collection_receipt.json'),raw_manifest=binding(WORK/'raw_manifest.jsonl'),scope_bytes=receipt['scope_bytes'],codes=dict(collect=0,classifier=2,evidence=0,inputs=2)),ensure_ascii=False)); return 0

parser=argparse.ArgumentParser(); parser.add_argument('mode',choices=('collect','finalize'))
args=parser.parse_args(); raise SystemExit(collect() if args.mode=='collect' else finalize())
