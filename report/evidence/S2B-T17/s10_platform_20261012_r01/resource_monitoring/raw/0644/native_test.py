"""保留自测真实Popen返回码、命令、工具来源和原字节日志。"""
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil
from supervisor import sha

w=Path(__file__).resolve().parent
command=[sys.executable,"-X","utf8","-B",str(w/"selftest.py")]; start=time.monotonic(); peak=0
with (w/"selftest.stdout.log").open("xb") as out,(w/"selftest.stderr.log").open("xb") as err:
    p=subprocess.Popen(command,cwd=w,stdout=out,stderr=err)
    while p.poll() is None:
        try:root=psutil.Process(p.pid);peak=max(peak,sum(x.memory_info().rss for x in [root]+root.children(recursive=True) if x.is_running()))
        except psutil.Error:pass
        time.sleep(0.05)
    code=p.wait()
receipt=dict(command=subprocess.list2cmdline(command),argv=command,native_exit_code=code,elapsed_seconds=time.monotonic()-start,sampled_peak_tree_rss_bytes=peak,python=sys.version,psutil_version=psutil.__version__,source_hashes={n:sha(w/n) for n in ("supervisor.py","selftest.py","fake_guard.py","native_test.py")},logs={n:sha(w/n) for n in ("selftest.stdout.log","selftest.stderr.log")},real_guard_or_target_started=False,supervisor_source_lines=len((w/"supervisor.py").read_text(encoding="utf-8").splitlines()))
with (w/"native_receipt.json").open("x",encoding="utf-8") as f:json.dump(receipt,f,ensure_ascii=False,indent=2);f.write("\n")
print(json.dumps(receipt,ensure_ascii=False));raise SystemExit(code)
