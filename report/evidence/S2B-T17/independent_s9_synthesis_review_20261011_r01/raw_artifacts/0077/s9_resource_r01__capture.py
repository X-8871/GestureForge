#!/usr/bin/env python3
"""保存资源采样工具的真实命令、原生码、日志和脚本SHA。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

work=Path(__file__).resolve().parent
target=work/"sampler.py"
argv=[sys.executable,"-X","utf8","-B",str(target)]
started=time.monotonic()
with (work/"native.log").open("x",encoding="utf-8",newline="\n") as log:
    process=subprocess.Popen(argv,cwd=work.parents[3],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8")
    for line in process.stdout:log.write(line);log.flush();print(line,end="",flush=True)
    code=process.wait()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={"command":subprocess.list2cmdline(argv),"argv":argv,"native_exit_code":code,"elapsed_seconds":time.monotonic()-started,"sampler_sha256":sha(target),"capture_sha256":sha(Path(__file__)),"log_sha256":sha(work/"native.log"),"sampler_receipt_sha256":sha(work/"sampler_receipt.json") if (work/"sampler_receipt.json").exists() else None}
with (work/"native_capture.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write("\n")
print(json.dumps(record,ensure_ascii=False),flush=True)
raise SystemExit(code)
