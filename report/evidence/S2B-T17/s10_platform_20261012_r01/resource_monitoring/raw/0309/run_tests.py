import json
import subprocess
import sys
import time
from pathlib import Path

# 每组自测独立保存真实原生码，失败不吞掉，不覆盖旧运行。
base = Path(__file__).absolute().parent
for label, script in [("final_base_selftest", "selftest.py"), ("final_supplement_selftest", "supplement_selftest.py"), ("final_target_selftest", "target_selftest.py")]:
    argv = [sys.executable, "-B", "-X", "utf8", str(base / script)]
    start = time.monotonic()
    cp = subprocess.run(argv, capture_output=True, check=False)
    for suffix, data in (("stdout.log", cp.stdout), ("stderr.log", cp.stderr)):
        with (base / (label + "." + suffix)).open("xb") as stream:
            stream.write(data)
    with (base / (label + ".native.json")).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"command": argv, "native_exit_code": cp.returncode, "elapsed_seconds": time.monotonic() - start}, ensure_ascii=False, indent=2) + "\n")
    sys.stdout.buffer.write(cp.stdout)
    sys.stderr.buffer.write(cp.stderr)
    if cp.returncode:
        raise SystemExit(cp.returncode)
