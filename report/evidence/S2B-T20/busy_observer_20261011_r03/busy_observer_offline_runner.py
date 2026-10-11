"""运行T20轻量回归并保存真实退出码、进程内存及源码字节，不访问硬件。"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil

root = Path(__file__).absolute().parents[3]
run = root / sys.argv[1]
if not run.parent.is_dir() or run.exists():
    raise RuntimeError("新的证据路径父目录缺失或RunId已存在")
run.mkdir()
fixtures = run / "fixtures"; fixtures.mkdir()
sources = {}
for relative in ("verification/s2b_csr_busy_observer.py", "verification/test_s2b_csr_busy_observer.py",
                 "verification/s2b_csr_board_acceptance.py", "verification/s2b_board_jtag.py",
                 "verification/s2b_board_transport.py", "verification/s2b_board_acceptance.py",
                 "verification/s2b_fixed_capture_check.py", "verification/test_s2b_csr_board_acceptance.py"):
    raw = (root / relative).read_bytes()
    sources[relative] = hashlib.sha256(raw).hexdigest()
env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "S2B_BUSY_FIXTURE_OUTPUT": str(fixtures)}
command = [sys.executable, "-B", "-m", "unittest", "verification.test_s2b_csr_busy_observer",
           "verification.test_s2b_csr_board_acceptance", "-v"]
started = time.monotonic()
peak = 0
budget_hit = False
with (run / "unittest.log").open("xb") as log:
    process = subprocess.Popen(command, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
    monitored = psutil.Process(process.pid)
    while process.poll() is None:
        try:
            rss = monitored.memory_info().rss
            for child in monitored.children(recursive=True):
                rss += child.memory_info().rss
            peak = max(peak, rss)
            if rss > 300 * 1024 * 1024 or time.monotonic() - started > 180:
                budget_hit = True
                process.terminate()
                break
        except psutil.NoSuchProcess:
            pass
        time.sleep(.05)
    code = process.wait(timeout=10)
record = {"hardware_execution": "NOT_RUN", "command": command, "cwd": str(root), "exit_code": code,
          "elapsed_seconds": time.monotonic() - started, "peak_rss_bytes": peak,
          "resource_budget_bytes": 300 * 1024 * 1024, "budget_exceeded": budget_hit,
          "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
          "source_sha256": sources, "python": sys.version, "psutil": psutil.__version__,
          "environment": {name: env[name] for name in ("PYTHONUTF8", "PYTHONIOENCODING", "S2B_BUSY_FIXTURE_OUTPUT")},
          "limitations": ["MOCK_ONLY；没有SDK/Serial硬件连接；峰值为50ms轮询，未测瞬时最大值。"]}
(run / "execution.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, ensure_ascii=False))
raise SystemExit(code if not budget_hit else 3)
