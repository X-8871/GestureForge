"""串行捕获本次自有测试的真实Popen返回码与原字节。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

work = Path(__file__).resolve().parent
name = sys.argv[1]
argv = [sys.executable, "-B", "-X", "utf8"] + sys.argv[2:]
start = time.monotonic()
peak = 0
with (work / (name + ".stdout.log")).open("xb") as so, (work / (name + ".stderr.log")).open("xb") as se:
    child = subprocess.Popen(argv, cwd=work, stdout=so, stderr=se)
    while child.poll() is None:
        try:
            objects = [psutil.Process(child.pid)] + psutil.Process(child.pid).children(recursive=True)
            peak = max(peak, sum(p.memory_info().rss for p in objects))
        except psutil.Error:
            pass
        time.sleep(0.02)
row = {"command": subprocess.list2cmdline(argv), "native_exit_code": child.returncode,
       "elapsed_seconds": time.monotonic()-start, "sampled_owned_test_tree_rss_peak_bytes": peak,
       "stdout_sha256": hashlib.sha256((work/(name+".stdout.log")).read_bytes()).hexdigest(),
       "stderr_sha256": hashlib.sha256((work/(name+".stderr.log")).read_bytes()).hexdigest()}
with (work/(name+".native.json")).open("x", encoding="utf-8") as stream:
    json.dump(row, stream, ensure_ascii=False, indent=2)
print(json.dumps(row, ensure_ascii=False))
raise SystemExit(child.returncode)
