"""独立保存r02轻量native原字节、实际退出码、耗时及128MiB自身树采样。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

WORK=Path(__file__).parent;ROOT=WORK.parents[3]
commands=[('derive_verify','derive_verify.py',[]),('legacy57','native_checks.py',['validate']),('legacy9','native_checks.py',['harness']),('r02_regressions','r02_regression_tests.py',[])]
records=[]
for label,name,arguments in commands:
 command=[sys.executable,'-X','utf8','-B',str(WORK/name),*arguments]
 script_sha=hashlib.sha256((WORK/name).read_bytes()).hexdigest();started=time.monotonic();peak=None;failure=None
 with (WORK/(label+'.stdout.raw')).open('xb') as stdout,(WORK/(label+'.stderr.raw')).open('xb') as stderr:
  child=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr);process=psutil.Process(child.pid);birth=process.create_time()
  while child.poll() is None:
   try:
    if process.create_time()==birth:
     members=[psutil.Process()]+[process]+process.children(recursive=True)
     peak=max(peak or 0,sum(member.memory_info().rss for member in members if member.is_running()))
   except psutil.NoSuchProcess:pass
   if (peak or 0)>128*1024**2 or time.monotonic()-started>180:
    failure='OWNED_NATIVE_LIMIT'
    if child.poll() is None and psutil.Process(child.pid).create_time()==birth:child.terminate()
    break
   time.sleep(.03)
  code=child.wait(timeout=10)
 record=dict(label=label,command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=code,script_sha_before=script_sha,script_sha_after=hashlib.sha256((WORK/name).read_bytes()).hexdigest(),elapsed_seconds=time.monotonic()-started,sampled_owned_tree_peak_bytes=peak,absolute_peak_bytes=None,child_pid=child.pid,child_create_time=birth,failure=failure)
 with (WORK/(label+'.native.json')).open('x',encoding='utf-8',newline='\n') as stream:json.dump(record,stream,ensure_ascii=False,indent=2);stream.write('\n')
 records.append(record)
 if code or failure:break
receipt=dict(status='PASS_NATIVE_LIGHTWEIGHT_ONLY' if len(records)==len(commands) and all(row['native_exit_code']==0 and row['failure'] is None and row['script_sha_before']==row['script_sha_after'] for row in records) else 'FAIL_PRESERVED',actual_outer_command=sys.orig_argv,python=sys.version,psutil=psutil.__version__,records=records,physical_g0='BLOCKED_PENDING_REAL_PINS',actual_sta='NOT_RUN',actual_new_budget='NOT_RUN',old_s11_budget='BLOCKED')
with (WORK/'native_r02_receipt.json').open('x',encoding='utf-8',newline='\n') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(dict(status=receipt['status'],native_codes=[row['native_exit_code'] for row in records]),ensure_ascii=False))
raise SystemExit(0 if receipt['status']=='PASS_NATIVE_LIGHTWEIGHT_ONLY' else 2)
