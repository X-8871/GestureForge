import json
import subprocess
import sys
import time
from pathlib import Path

# 保存真实审查stdout/stderr/native，不归一化失败。
out = Path(__file__).absolute().parent
argv = [sys.executable, "-B", "-X", "utf8", str(out / "review.py")]
started = time.monotonic()
cp = subprocess.run(argv, capture_output=True, check=False)
for suffix, data in [("stdout.log", cp.stdout), ("stderr.log", cp.stderr)]:
    with (out / ("review." + suffix)).open("xb") as stream:
        stream.write(data)
with (out / "review.native.json").open("x", encoding="utf-8", newline="\n") as stream:
    stream.write(json.dumps({"command": argv, "native_exit_code": cp.returncode, "elapsed_seconds": time.monotonic() - started}, ensure_ascii=False, indent=2) + "\n")
sys.stdout.buffer.write(cp.stdout)
sys.stderr.buffer.write(cp.stderr)
raise SystemExit(cp.returncode)
