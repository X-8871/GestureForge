#!/usr/bin/env python3
"""真实封存只读日志分析工具的命令、退出码与输出。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

work=Path(__file__).resolve().parent
argv=[sys.executable,"-X","utf8","-B",str(work/"log_analysis.py")]
started=time.monotonic()
done=subprocess.run(argv,cwd=work.parents[3],capture_output=True)
for name,data in (("analysis_stdout.log",done.stdout),("analysis_stderr.log",done.stderr)):
    with (work/name).open("xb") as f:f.write(data)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={"command":subprocess.list2cmdline(argv),"argv":argv,"native_exit_code":done.returncode,"elapsed_seconds":time.monotonic()-started,"script_sha256":sha(work/"log_analysis.py"),"stdout_sha256":sha(work/"analysis_stdout.log"),"stderr_sha256":sha(work/"analysis_stderr.log")}
with (work/"analysis_native_capture.json").open("x",encoding="utf-8",newline="\n") as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write("\n")
print(done.stdout.decode("utf-8"),end="");print(done.stderr.decode("utf-8"),file=sys.stderr,end="");print(json.dumps(report,ensure_ascii=False))
raise SystemExit(done.returncode)
