"""仅包装本目录collector轻量命令，保存原生码、原字节日志和进程树峰。"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import psutil

import compat_pins
from collector import CACHE,ROOT,WORK,binding,exact,fresh,save,require

parser=argparse.ArgumentParser()
parser.add_argument("--prefix",required=True)
parser.add_argument("arguments",nargs=argparse.REMAINDER)
args=parser.parse_args()
compat_pins.require_ready()
require(re.fullmatch(r"s12_[A-Za-z0-9_-]+",args.prefix),"prefix必须是安全s12_名称")
arguments=args.arguments[1:] if args.arguments and args.arguments[0]=="--" else args.arguments
require(arguments and arguments[0] in ("prepare","source","collect","seal"),"只能包装本collector轻量模式")
mode=arguments[0]; directory=WORK if mode=="prepare" else exact(CACHE,"directory")
command=[sys.executable,"-X","utf8","-B",str(exact(WORK/"collector.py")),*arguments]
logs=[directory/(args.prefix+"."+suffix) for suffix in ("stdout.log","stderr.log")]
for path in logs: fresh(path)
record_path=directory/(args.prefix+".native.json"); fresh(record_path)
started=time.monotonic(); peak=0; failure=None
with logs[0].open("xb") as out,logs[1].open("xb") as err:
    process=subprocess.Popen(command,cwd=ROOT,stdout=out,stderr=err,env=dict(os.environ,PYTHONUTF8="1",PYTHONIOENCODING="utf-8"))
    while process.poll() is None:
        try:
            parent=psutil.Process(process.pid); members=[parent]+parent.children(recursive=True)
            peak=max(peak,sum(p.memory_info().rss for p in members if p.is_running()))
        except psutil.Error: pass
        if time.monotonic()-started>90 or peak>536870912:
            failure="TIMEOUT" if time.monotonic()-started>90 else "RSS_LIMIT"
            try:
                parent=psutil.Process(process.pid)
                for child in parent.children(recursive=True): child.terminate()
                parent.terminate()
            except psutil.Error: pass
            process.wait(timeout=20); break
        time.sleep(0.05)
record=dict(mode=mode,prefix=args.prefix,command=command,windows_command=subprocess.list2cmdline(command),native_exit_code=process.returncode,host_shell_exit_code=None,elapsed_seconds=time.monotonic()-started,peak_tree_rss_bytes=peak,failure=failure,closed_logs=[binding(p) for p in logs],heavy_ross_hardware_executed=False)
save(record_path,record)
print(json.dumps(record,ensure_ascii=False),flush=True)
raise SystemExit(process.returncode if failure is None else 3)

