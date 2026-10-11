"""捕获仅自有模拟自测的真实子码和原字节，不枚举进程。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

w=Path(__file__).resolve().parent
argv=[sys.executable,"-B","-X","utf8",str(w/"selftest.py")]
start=time.monotonic()
with (w/"selftest.stdout.log").open("xb") as so,(w/"selftest.stderr.log").open("xb") as se:
    result=subprocess.run(argv,cwd=w,stdout=so,stderr=se,check=False,timeout=20)
row={"command":subprocess.list2cmdline(argv),"native_exit_code":result.returncode,"elapsed_seconds":time.monotonic()-start,
     "stdout_sha256":hashlib.sha256((w/"selftest.stdout.log").read_bytes()).hexdigest(),"stderr_sha256":hashlib.sha256((w/"selftest.stderr.log").read_bytes()).hexdigest()}
with (w/"selftest.native.json").open("x",encoding="utf-8") as stream:json.dump(row,stream,ensure_ascii=False,indent=2)
print(json.dumps(row,ensure_ascii=False))
raise SystemExit(result.returncode)
