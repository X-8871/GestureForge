import json
import subprocess
import sys
import time
from pathlib import Path

# 保留自测stdout/stderr及实际退出码，不归一化失败码。
out = Path(__file__).absolute().parent
argv = [sys.executable, "-B", "-X", "utf8", str(out / "selftest.py")]
start = time.monotonic()
cp = subprocess.run(argv, capture_output=True, check=False)
for suffix, data in (("stdout.log", cp.stdout), ("stderr.log", cp.stderr)):
    with (out / ("selftest." + suffix)).open("xb") as stream:
        stream.write(data)
with (out / "selftest.native.json").open("x", encoding="utf-8", newline="\n") as stream:
    stream.write(json.dumps({"command": argv, "native_exit_code": cp.returncode, "elapsed_seconds": time.monotonic() - start}, ensure_ascii=False, indent=2) + "\n")
sys.stdout.buffer.write(cp.stdout)
sys.stderr.buffer.write(cp.stderr)
raise SystemExit(cp.returncode)
