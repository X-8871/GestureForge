"""独立记录pin验证实际退出码、原始stdout/stderr及自身采样峰。"""
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

W = Path(__file__).resolve().parent
argv = [sys.executable, "-B", "-X", "utf8", str(W / "tests.py")]
began = time.monotonic()
peak = 0
limit = None
with (W / "stdout.log").open("xb") as so, (W / "stderr.log").open("xb") as se:
    child = subprocess.Popen(argv, cwd=W, stdout=so, stderr=se)
    owned = psutil.Process(child.pid)
    birth = owned.create_time()
    while child.poll() is None:
        try:
            peak = max(peak, sum(p.memory_info().rss for p in [owned]+owned.children(recursive=True)))
        except psutil.NoSuchProcess:
            pass
        if peak > 256*1024**2 or time.monotonic()-began > 180:
            limit = "OWNED_RESOURCE_BOUND"
            if owned.create_time() == birth:
                child.terminate()
            break
        time.sleep(.02)
    code = child.wait(timeout=3)
receipt = dict(command=argv, native_exit_code=code, elapsed_seconds=time.monotonic()-began,
               maximum_sampled_owned_tree_rss_bytes=peak, sampling_seconds=.02,
               continuous_absolute_peak_bytes=None, resource_limit_reason=limit, python=sys.version, psutil_version=psutil.__version__)
with (W / "native_receipt.json").open("x", encoding="utf-8", newline="\n") as f:
    json.dump(receipt,f,ensure_ascii=False,indent=2)
print(json.dumps(receipt,ensure_ascii=False))
raise SystemExit(code)
