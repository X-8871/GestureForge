"""保存本次轻量数学审查原始日志与真实返回码。"""
import json,subprocess,sys,time
from pathlib import Path
W=Path(__file__).parent;command=[sys.executable,'-B','-X','utf8',str(W/'review.py')];t=time.monotonic();p=subprocess.run(command,capture_output=True,cwd=W)
for name,data in [('stdout.log',p.stdout),('stderr.log',p.stderr)]:
    with (W/name).open('xb') as f:f.write(data)
n=dict(command=command,native_exit_code=p.returncode,elapsed_seconds=time.monotonic()-t,absolute_peak_memory_bytes=None)
with (W/'native_receipt.json').open('x',encoding='utf-8') as f:json.dump(n,f,ensure_ascii=False,indent=2)
print(json.dumps(n,ensure_ascii=False));print(p.stdout.decode('utf-8'));print(p.stderr.decode('utf-8'));raise SystemExit(p.returncode)
