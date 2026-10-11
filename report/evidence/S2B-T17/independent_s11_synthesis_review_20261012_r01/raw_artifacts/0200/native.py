import json
import subprocess
import sys
import time
from pathlib import Path

# 独立审查自身原生日志与真实退出码，不查询任务进程。
out=Path(__file__).absolute().parent
attempt=sys.argv[1]
command=[sys.executable,'-B','-X','utf8',str(out/'review.py')]+([attempt] if attempt!='attempt1' else [])
start=time.monotonic()
with (out/(attempt+'.stdout.log')).open('xb') as stdout,(out/(attempt+'.stderr.log')).open('xb') as stderr:
    cp=subprocess.run(command,stdout=stdout,stderr=stderr,check=False)
record={'command':command,'native_exit_code':cp.returncode,'elapsed_seconds':time.monotonic()-start}
with (out/(attempt+'.native.json')).open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps(record,ensure_ascii=False))
raise SystemExit(cp.returncode)
