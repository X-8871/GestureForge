"""仅包装本任务生成、帮助、模拟测试与待冻结拒绝，保存真实原生结果。"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

WORK=Path(__file__).parent; ROOT=WORK.parents[3]
parser=argparse.ArgumentParser(); parser.add_argument('case',choices=('generate','refresh','validate','harness')); args=parser.parse_args()
commands=[('generate', 'generate_drafts.py', [],0)] if args.case=='generate' else [('refresh','refresh_drafts.py',[],0)] if args.case=='refresh' else [('harness','source_after_harness_tests.py',[],0)] if args.case=='harness' else [
 ('fixtures','compatibility_tests.py',[],0),
 ('synth_help','collector.py',['--help'],0),('pnr_help','impl_collector.py',['--help'],0),
 ('after_help','source_after_check.py',['--help'],0),('after_native_help','native_source_after.py',['--help'],0),
 ('synth_native_help','native.py',['--help'],0),
 ('synth_prepare_blocked','collector.py',['prepare'],1),
 ('synth_source_blocked','collector.py',['source','--commit','0'*40,'--phase','before'],1),
 ('synth_collect_blocked','collector.py',['collect','--commit','0'*40,'--gate','NONEXISTENT_NOT_READ'],1),
 ('synth_seal_blocked','collector.py',['seal','--commit','0'*40,'--gate','NONEXISTENT_NOT_READ'],1),
 ('pnr_prepare_blocked','impl_collector.py',['prepare'],1),
 ('pnr_collect_blocked','impl_collector.py',['collect','--gate','NONEXISTENT_NOT_READ'],1),
 ('after_blocked','source_after_check.py',['--expected-head','0'*40,'--output-dir',str(WORK/'NONEXISTENT_NOT_CREATED')],1),
 ('after_native_blocked','native_source_after.py',['--expected-head','0'*40,'--output-dir',str(WORK/'NONEXISTENT_NOT_CREATED')],1),
 ('synth_native_blocked','native.py',['--prefix','s12_pending','--','prepare'],1),
]
records=[]
for label,script,arguments,expected in commands:
 command=[sys.executable,'-X','utf8','-B',str(WORK/script),*arguments]; started=time.monotonic(); peak=None; failure=None
 with (WORK/(label+'.stdout.bin')).open('xb') as stdout,(WORK/(label+'.stderr.bin')).open('xb') as stderr:
  child=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr)
  proc=psutil.Process(child.pid); birth=proc.create_time()
  while child.poll() is None:
   try:
    if proc.create_time()==birth: peak=max(peak or 0,proc.memory_info().rss+psutil.Process().memory_info().rss)
   except psutil.NoSuchProcess: pass
   if (peak or 0)>128*1024**2 or time.monotonic()-started>180:
    failure='OWNED_NATIVE_BUDGET'
    if child.poll() is None and psutil.Process(child.pid).create_time()==birth: child.terminate()
    break
   time.sleep(.02)
  code=child.wait(timeout=10)
 stderr=(WORK/(label+'.stderr.bin')).read_bytes()
 passed=code==expected and failure is None and (not label.endswith('_blocked') or b'BLOCKED_PENDING_S12_PINS' in stderr)
 record=dict(label=label,command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=code,expected_native_code=expected,check_status='PASS' if passed else 'FAIL',elapsed_seconds=time.monotonic()-started,sampled_own_parent_plus_direct_child_peak_bytes=peak,absolute_peak_bytes=None,failure=failure,child_pid=child.pid,child_create_time=birth)
 with (WORK/(label+'.native.json')).open('x',encoding='utf-8',newline='\n') as stream: json.dump(record,stream,ensure_ascii=False,indent=2); stream.write('\n')
 records.append(record)
receipt=dict(status='PASS_CHEAP_ONLY' if all(row['check_status']=='PASS' for row in records) else 'FAIL_PRESERVED',actual_outer_command=sys.orig_argv,python=sys.version,psutil=psutil.__version__,records=records,physical_g0='BLOCKED_PENDING_REAL_PINS',physical_g2='NOT_RUN',sta='NOT_RUN',new_budget='NOT_RUN',old_s11_budget='BLOCKED',heavy_or_hardware=False)
with (WORK/(args.case+'.wrapper.json')).open('x',encoding='utf-8',newline='\n') as stream: json.dump(receipt,stream,ensure_ascii=False,indent=2); stream.write('\n')
print(json.dumps(dict(status=receipt['status'],native_codes=[row['native_exit_code'] for row in records]),ensure_ascii=False))
raise SystemExit(0 if receipt['status']=='PASS_CHEAP_ONLY' else 2)
