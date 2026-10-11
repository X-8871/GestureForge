#!/usr/bin/env python3
"""仅包装同目录轻量封包脚本，保存真实native结果于缓存；不增未绑定正式文件。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[3]


def main():
    """封包输出和原生码一次保存；检查器输出仍留隔离缓存。"""
    command=[sys.executable,"-X","utf8","-B",str(WORK/"finalize.py")]
    started=time.monotonic()
    with (WORK/"finalize_stdout.log").open("xb") as out,(WORK/"finalize_stderr.log").open("xb") as err:
        result=subprocess.run(command,cwd=ROOT,stdout=out,stderr=err,timeout=120)
    capture={"command":subprocess.list2cmdline(command),"argv":command,"native_exit_code":result.returncode,
             "seconds":round(time.monotonic()-started,3),"script_sha256":hashlib.sha256((WORK/"finalize.py").read_bytes()).hexdigest()}
    for name in ("finalize_stdout.log","finalize_stderr.log"):
        path=WORK/name;capture[name]={"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"bytes":path.stat().st_size}
    with (WORK/"finalize_native.json").open("x",encoding="utf-8",newline="\n") as f:
        json.dump(capture,f,ensure_ascii=False,indent=2);f.write("\n")
    print(json.dumps(capture,ensure_ascii=False))
    print((WORK/"finalize_stdout.log").read_text(encoding="utf-8"))
    return result.returncode


if __name__=="__main__":raise SystemExit(main())
