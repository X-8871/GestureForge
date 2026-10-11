import json
import subprocess
import sys
import time
from pathlib import Path

# 补充自测同样单独保留真实输出和原生码。
out = Path(__file__).absolute().parent
argv = [sys.executable, "-B", "-X", "utf8", str(out / "supplement_selftest.py")]
start = time.monotonic()
cp = subprocess.run(argv, capture_output=True, check=False)
for suffix, data in (("stdout.log", cp.stdout), ("stderr.log", cp.stderr)):
    with (out / ("supplement." + suffix)).open("xb") as stream:
        stream.write(data)
with (out / "supplement.native.json").open("x", encoding="utf-8", newline="\n") as stream:
    stream.write(json.dumps({"command": argv, "native_exit_code": cp.returncode, "elapsed_seconds": time.monotonic() - start}, ensure_ascii=False, indent=2) + "\n")
sys.stdout.buffer.write(cp.stdout)
sys.stderr.buffer.write(cp.stderr)
raise SystemExit(cp.returncode)
