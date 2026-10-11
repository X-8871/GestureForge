"""独立审查执行器，保留真实退出码并限制轻量检查资源。"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import psutil

run = Path(__file__).resolve().parent
root = run.parents[3]
label, command = sys.argv[1], sys.argv[2:]
env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"}
started, peak, stopped = time.monotonic(), 0, None
with (run / (label + "_stdout.log")).open("xb") as out, (run / (label + "_stderr.log")).open("xb") as err:
    process = subprocess.Popen(command, cwd=root, env=env, stdout=out, stderr=err)
    monitored = psutil.Process(process.pid)
    while process.poll() is None:
        try:
            rss = monitored.memory_info().rss + sum(child.memory_info().rss for child in monitored.children(recursive=True))
            peak = max(peak, rss)
            if rss >= 300 * 1024 * 1024 or time.monotonic() - started > 180:
                stopped = "RSS_OR_TIME_LIMIT"
                process.terminate()
                break
        except psutil.NoSuchProcess:
            pass
        time.sleep(.025)
    code = process.wait(timeout=10)
record = {"command": command, "cwd": str(root), "exit_code": code, "elapsed_seconds": time.monotonic() - started,
          "sampled_peak_rss_bytes": peak, "rss_limit_bytes": 300 * 1024 * 1024, "stopped": stopped,
          "poll_seconds": .025, "hardware_execution": "NOT_RUN", "python": sys.version,
          "psutil": psutil.__version__, "limitations": ["25ms采样并非瞬时精确峰值；不含监督器自身。"]}
(run / (label + "_native.json")).write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(record, ensure_ascii=False))
raise SystemExit(code if stopped is None else 3)
