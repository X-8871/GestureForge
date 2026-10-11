#!/usr/bin/env python3
"""保留轻量补核的真实原生返回及日志。"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

work = Path(__file__).resolve().parent
root = work.parents[3]
command = [sys.executable, "-B", str(work / "supplement_review.py")]
log = work / "supplement_stdout.log"
receipt = work / "supplement_native.json"
assert not log.exists() and not receipt.exists()
begin = time.monotonic()
with log.open("wb") as stream:
    result = subprocess.run(command, cwd=root, stdout=stream, stderr=subprocess.STDOUT)
data = {"command": command, "cwd": str(root), "native_exit_code": result.returncode,
        "elapsed_seconds": round(time.monotonic() - begin, 3), "log": log.relative_to(root).as_posix(), "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()}
receipt.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps(data, ensure_ascii=False))
raise SystemExit(result.returncode)
