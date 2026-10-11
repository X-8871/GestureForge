#!/usr/bin/env python3
"""真实保存封包工具命令/原生码/日志，不将包装成功当功能或独审。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

work=Path(__file__).resolve().parent
argv=[sys.executable,"-X","utf8","-B",str(work/"finalize.py")]
started=time.monotonic();done=subprocess.run(argv,cwd=work.parents[3],capture_output=True)
for name,data in (("finalize_stdout.log",done.stdout),("finalize_stderr.log",done.stderr)):
    with (work/name).open("xb") as f:f.write(data)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={"command":subprocess.list2cmdline(argv),"argv":argv,"native_exit_code":done.returncode,"elapsed_seconds":time.monotonic()-started,"script_sha256":sha(work/"finalize.py"),"stdout_sha256":sha(work/"finalize_stdout.log"),"stderr_sha256":sha(work/"finalize_stderr.log")}
with (work/"finalize_native.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write("\n")
print(done.stdout.decode("utf-8"),end="");print(done.stderr.decode("utf-8"),file=sys.stderr,end="");print(json.dumps(record,ensure_ascii=False));raise SystemExit(done.returncode)
