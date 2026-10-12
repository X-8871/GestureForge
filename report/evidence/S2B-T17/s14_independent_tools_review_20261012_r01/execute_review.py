"""独立审查原生命令捕获，保留真实返回码和离散树RSS观测。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

W=Path(__file__).resolve().parent
ROOT=W.parents[3]
label=sys.argv[1] if len(sys.argv)>1 else 'review'
command=[sys.executable,'-X','utf8','-B',str(W/'review_driver.py')]
began=time.monotonic(); peak=0; unknown=[]
with (W/(label+'.stdout.bin')).open('xb') as stdout,(W/(label+'.stderr.bin')).open('xb') as stderr:
    child=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr)
    while child.poll() is None:
        try:
            proc=psutil.Process(child.pid)
            processes=[proc]+proc.children(recursive=True)
            rss=0
            for process in processes:
                try: rss+=process.memory_info().rss
                except psutil.Error as error: unknown.append(repr(error))
            peak=max(peak,rss)
        except psutil.Error as error: unknown.append(repr(error))
        time.sleep(.05)
    code=child.wait()
record=dict(command=command,cwd=str(ROOT),native_exit_code=code,elapsed_seconds=time.monotonic()-began,
            sampled_owned_tree_peak_bytes=peak,continuous_peak_bytes=None,sample_interval_seconds=.05,unknown_samples=unknown,
            log_bindings=[dict(path=str(W/name),sha256=hashlib.sha256((W/name).read_bytes()).hexdigest(),bytes=(W/name).stat().st_size) for name in [label+'.stdout.bin',label+'.stderr.bin']],
            driver_sha256=hashlib.sha256((W/'review_driver.py').read_bytes()).hexdigest(),whole_os_tree_terminal='NOT_PROVEN',heavy_or_hardware_started=False)
with (W/(label+'.native.json')).open('x',encoding='utf-8',newline='\n') as stream:
    json.dump(record,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps(record,ensure_ascii=False));raise SystemExit(code)
