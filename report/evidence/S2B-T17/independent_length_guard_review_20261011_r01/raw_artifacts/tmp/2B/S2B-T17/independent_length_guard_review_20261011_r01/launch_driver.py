#!/usr/bin/env python3
"""保存本独立审查driver真实原生退出，避免宿主归一化混用。"""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

work = Path(__file__).resolve().parent
root = work.parents[3]
command = [sys.executable, "-B", str(work / "review_driver.py")]
log = work / "attempt02_driver_stdout.log"
receipt = work / "attempt02_driver_native.json"
if log.exists() or receipt.exists():
    raise ValueError("不覆盖既有调用原件")
started = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
begin = time.monotonic()
with log.open("wb") as stream:
    result = subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT)
data = {"command": command, "cwd": str(root), "started_utc8": started, "native_exit_code": result.returncode,
        "elapsed_seconds": round(time.monotonic() - begin, 3), "log": log.relative_to(root).as_posix(),
        "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()}
receipt.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps(data, ensure_ascii=False))
raise SystemExit(result.returncode)
