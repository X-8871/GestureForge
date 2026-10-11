"""依次执行r04轻量验证，保存每条实际命令/退出码/原字节和采样峰。"""
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

W = Path(__file__).resolve().parent
started = time.monotonic()
rows = []
for label, script in [("guard_regression", W / "selftest.py"), ("guard_supplement", W / "supplement.py"),
                      ("birth_gate", W / "birth_tests.py"), ("supervisor_pin", W / "supervisor_pin/tests.py")]:
    argv = [sys.executable, "-B", "-X", "utf8", str(script)]
    began = time.monotonic()
    peak = 0
    bound = None
    with (W / (label+".stdout.log")).open("xb") as so, (W / (label+".stderr.log")).open("xb") as se:
        child = subprocess.Popen(argv, cwd=script.parent, stdout=so, stderr=se)
        own = psutil.Process(child.pid)
        birth = own.create_time()
        while child.poll() is None:
            try:
                peak = max(peak, sum(p.memory_info().rss for p in [own]+own.children(recursive=True)))
            except psutil.NoSuchProcess:
                pass
            if peak > 256*1024**2 or time.monotonic()-started > 180:
                bound = "OWNED_RESOURCE_BOUND"
                if own.create_time() == birth:
                    child.terminate()
                break
            time.sleep(.02)
        code = child.wait(timeout=3)
    row = dict(case=label, command=argv, native_exit_code=code, elapsed_seconds=time.monotonic()-began,
               maximum_sampled_owned_tree_rss_bytes=peak, sampling_seconds=.02,
               continuous_absolute_peak_bytes=None, resource_limit_reason=bound)
    with (W / (label+".native.json")).open("x", encoding="utf-8") as f:
        json.dump(row,f,ensure_ascii=False,indent=2)
    rows.append(row)
    print(json.dumps(row,ensure_ascii=False), flush=True)
    if code != 0:
        break
receipt = dict(command=[sys.executable]+sys.argv, executions=rows,
               native_exit_code=rows[-1]["native_exit_code"], elapsed_seconds=time.monotonic()-started,
               python=sys.version, psutil_version=psutil.__version__, output_limit_bytes=32*1024**2)
assert sum(p.stat().st_size for p in W.rglob("*") if p.is_file()) <= 32*1024**2
with (W / "r04_native_receipt.json").open("x", encoding="utf-8") as f:
    json.dump(receipt,f,ensure_ascii=False,indent=2)
raise SystemExit(receipt["native_exit_code"])
