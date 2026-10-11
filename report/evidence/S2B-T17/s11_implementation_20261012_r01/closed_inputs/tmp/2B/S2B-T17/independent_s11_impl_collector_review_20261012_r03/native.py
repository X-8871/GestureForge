import json
import subprocess
import sys
import time
from pathlib import Path

# 保存独立只读审查实际stdout、stderr和native，不执行实际collect。
out=Path(__file__).absolute().parent
argv=[sys.executable,'-B','-X','utf8',str(out/'review.py')]
start=time.monotonic()
with (out/'review.stdout.log').open('xb') as stdout,(out/'review.stderr.log').open('xb') as stderr:
    cp=subprocess.run(argv,stdout=stdout,stderr=stderr,check=False)
record={'command':argv,'native_exit_code':cp.returncode,'elapsed_seconds':time.monotonic()-start}
with (out/'review.native.json').open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2)
print(json.dumps(record,ensure_ascii=False))
raise SystemExit(cp.returncode)
