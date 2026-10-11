#!/usr/bin/env python3
"""保存真实子进程退出码与宿主返回的区别；不修改源码或旧证据。"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
EVIDENCE=ROOT/"report/evidence/S2B-T17/length_guard_20261011_r02"
label=sys.argv[1]
if not label.replace("_","").isalnum():raise ValueError("原生日志名称非法")
log=EVIDENCE/(label+".log")
receipt=EVIDENCE/(label+"_native.json")
if not EVIDENCE.is_dir() or log.exists() or receipt.exists():raise ValueError("父目录缺失或禁止覆盖")
command=sys.argv[2:]
env=os.environ.copy();env.update(PYTHONUTF8="1",PYTHONIOENCODING="utf-8")
started=time.monotonic();now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
with log.open("x",encoding="utf-8",newline="\n") as output:
    process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8",errors="strict")
    for line in process.stdout:
        output.write(line);output.flush();print(line,end="",flush=True)
    native=process.wait()
record={"command":command,"cwd":str(ROOT),"started_utc8":now,"native_exit_code":native,
    "elapsed_seconds":round(time.monotonic()-started,3),"stdout_log":log.relative_to(ROOT).as_posix(),
    "stdout_sha256":hashlib.sha256(log.read_bytes()).hexdigest(),"host_exit_code":"由外层exec返回另行记录，不用替代native退出码"}
receipt.write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
print(json.dumps({"native_exit_code":native,"receipt":str(receipt)},ensure_ascii=False),flush=True)
raise SystemExit(native)
