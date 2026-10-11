"""原生封包调用捕获；只写新缓存日志，不把宿主返回码替代原生码。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[3]
argv=[sys.executable,"-X","utf8","-B",str(WORK/"finalize.py")]
started=time.monotonic()
with (WORK/"finalize_stdout.log").open("xb") as out,(WORK/"finalize_stderr.log").open("xb") as err:
    child=subprocess.Popen(argv,cwd=ROOT,stdout=out,stderr=err)
    code=child.wait(timeout=120)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt={"command":subprocess.list2cmdline(argv),"argv":argv,"cwd":str(ROOT),"native_exit_code":code,"host_shell_exit_code":None,"elapsed_seconds":time.monotonic()-started,"source_sha256":sha(WORK/"finalize.py"),"stdout_sha256":sha(WORK/"finalize_stdout.log"),"stderr_sha256":sha(WORK/"finalize_stderr.log")}
with (WORK/"finalize_native.json").open("x",encoding="utf-8") as f:json.dump(receipt,f,ensure_ascii=False,indent=2)
print(json.dumps(receipt));raise SystemExit(code)
