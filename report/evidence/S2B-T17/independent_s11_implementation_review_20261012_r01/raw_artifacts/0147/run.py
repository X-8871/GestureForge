"""封存本次轻量只读命令的原始输出和真实原生码。"""
import json, subprocess, sys, time
from pathlib import Path
w=Path(__file__).parent
command=[sys.executable,'-B','-X','utf8',str(w/'review.py')]
t=time.monotonic(); p=subprocess.run(command,capture_output=True)
for name,data in [('stdout.log',p.stdout),('stderr.log',p.stderr)]:
    with (w/('review_r03.'+name)).open('xb') as f:f.write(data)
native=dict(command=command,native_exit_code=p.returncode,elapsed_seconds=time.monotonic()-t)
with (w/'review_r03.native.json').open('x',encoding='utf-8') as f:json.dump(native,f,ensure_ascii=False,indent=2)
print(json.dumps(native,ensure_ascii=False)); print(p.stdout.decode('utf-8')); print(p.stderr.decode('utf-8'))
raise SystemExit(p.returncode)
