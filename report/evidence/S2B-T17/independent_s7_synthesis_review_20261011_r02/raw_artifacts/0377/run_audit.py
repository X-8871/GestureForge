import json
import subprocess
import sys
import time
from pathlib import Path

# 宿主执行只记录真实子进程返回码，标准输出和错误使用原始字节保存。
directory = Path(__file__).resolve().parent
command = [sys.executable, "-B", "-X", "utf8", str(directory / "audit_s7.py")]
started = time.monotonic()
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
for suffix, raw in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
    with (directory / ("audit." + suffix)).open("xb") as stream:
        stream.write(raw)
receipt = {"command": command, "native_exit_code": result.returncode, "elapsed_seconds": time.monotonic() - started}
with (directory / "audit.native.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps(receipt, ensure_ascii=False))
print(result.stdout.decode("utf-8", errors="replace"))
print(result.stderr.decode("utf-8", errors="replace"))
raise SystemExit(result.returncode)
