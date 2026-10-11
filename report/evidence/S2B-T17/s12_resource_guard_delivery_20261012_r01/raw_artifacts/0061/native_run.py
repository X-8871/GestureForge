"""保存真实命令、退出码、原始日志、自有采样峰及哈希清单；失败不覆盖。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import psutil

W = Path(__file__).resolve().parent
cmd = [sys.executable, "-B", "-X", "utf8", str(W / "selftest.py")]
began = time.monotonic()
peak = 0
timeout_reason = None
with (W / "selftest.stdout.log").open("xb") as so, (W / "selftest.stderr.log").open("xb") as se:
    p = subprocess.Popen(cmd, cwd=W, stdout=so, stderr=se)
    identity = psutil.Process(p.pid)
    birth = identity.create_time()
    while p.poll() is None:
        try:
            peak = max(peak, sum(x.memory_info().rss for x in [identity] + identity.children(recursive=True)))
        except psutil.NoSuchProcess:
            pass
        if time.monotonic() - began > 180 or peak > 256 * 1024**2:
            timeout_reason = "OWNED_TEST_RESOURCE_BOUND"
            if identity.create_time() == birth:
                p.terminate()
            break
        time.sleep(.02)
    code = p.wait(timeout=5)
receipt = dict(command=cmd, native_exit_code=code, elapsed_seconds=time.monotonic()-began,
               maximum_sampled_owned_tree_rss_bytes=peak, sample_interval_seconds=.02,
               continuous_absolute_peak_bytes=None, resource_limit_reason=timeout_reason,
               python=sys.version, psutil_version=psutil.__version__)
with (W / "native_receipt.json").open("x", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
files = sorted(x for x in W.rglob("*") if x.is_file())
assert sum(x.stat().st_size for x in files) <= 64 * 1024**2
with (W / "raw_manifest.jsonl").open("x", encoding="utf-8", newline="\n") as f:
    for x in files:
        f.write(json.dumps(dict(path=x.relative_to(W).as_posix(), bytes=x.stat().st_size, sha256=hashlib.sha256(x.read_bytes()).hexdigest()),ensure_ascii=False)+"\n")
print(json.dumps(receipt, ensure_ascii=False))
raise SystemExit(code)
