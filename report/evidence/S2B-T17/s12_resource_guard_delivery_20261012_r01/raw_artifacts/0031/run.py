"""只测自有审查子树离散RSS并保存原生命令输出。"""
import json,subprocess,sys,time
from pathlib import Path
import psutil
W=Path(__file__).parent;cmd=[sys.executable,'-B','-X','utf8',str(W/'review.py')];t=time.monotonic();peak=0
with (W/'stdout.log').open('xb') as out,(W/'stderr.log').open('xb') as err:
    p=subprocess.Popen(cmd,cwd=W,stdout=out,stderr=err)
    while p.poll() is None:
        try:
            proc=psutil.Process(p.pid);rss=0
            for member in [proc]+proc.children(recursive=True):
                try:rss+=member.memory_info().rss
                except psutil.NoSuchProcess:pass
            peak=max(peak,rss)
        except psutil.NoSuchProcess:pass
        if peak>268435456 or time.monotonic()-t>180:raise RuntimeError('本审查自有任务超预算')
        time.sleep(.02)
native=dict(command=cmd,native_exit_code=p.wait(),elapsed_seconds=time.monotonic()-t,sampled_owned_tree_peak_bytes=peak,absolute_peak_bytes=None,sample_interval_seconds=.02)
with (W/'native_receipt.json').open('x',encoding='utf-8') as f:json.dump(native,f,ensure_ascii=False,indent=2)
print(json.dumps(native,ensure_ascii=False));print((W/'stdout.log').read_text(encoding='utf-8'));print((W/'stderr.log').read_text(encoding='utf-8'));raise SystemExit(native['native_exit_code'])
