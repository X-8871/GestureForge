"""独立保存补充运行原生退出码及原字节，不覆盖首轮。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

W = Path(__file__).resolve().parent
cmd = [sys.executable, "-B", "-X", "utf8", str(W / "supplement.py")]
began = time.monotonic()
peak = 0
with (W / "supplement.stdout.log").open("xb") as so, (W / "supplement.stderr.log").open("xb") as se:
    p = subprocess.Popen(cmd, cwd=W, stdout=so, stderr=se)
    proc = psutil.Process(p.pid)
    while p.poll() is None:
        try:
            peak = max(peak, proc.memory_info().rss)
        except psutil.NoSuchProcess:
            pass
        if time.monotonic()-began > 30:
            p.terminate()
            break
        time.sleep(.02)
    code = p.wait(timeout=3)
receipt = dict(command=cmd, native_exit_code=code, elapsed_seconds=time.monotonic()-began,
               maximum_sampled_process_rss_bytes=peak, continuous_absolute_peak_bytes=None)
with (W / "supplement_native_receipt.json").open("x", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
print(json.dumps(receipt, ensure_ascii=False))
raise SystemExit(code)
