"""记录授权隔离命令的真实直接等待结果；不启动硬件或推断连续资源预算。"""
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
assert ROOT.name == "FPGA_Competition"
request_path = Path(sys.argv[1]).resolve(strict=True)
assert request_path.parent == HERE and request_path.is_file()
request = json.loads(request_path.read_text(encoding="utf-8"))
name = request["name"]
assert name and all(c.isalnum() or c == "_" for c in name)
targets = {key: HERE / (name + suffix) for key, suffix in (
    ("stdout", ".stdout.log"), ("stderr", ".stderr.log"), ("native", ".native.json"))}
assert all(not target.exists() for target in targets.values()), "不覆盖已有运行原件"
command = request["command"]
assert type(command) is list and command and all(type(x) is str for x in command)
assert Path(command[0]).resolve(strict=True) == Path(sys.executable).resolve(strict=True)
cwd = Path(request["cwd"]).resolve(strict=True)
assert cwd.is_dir() and cwd.is_relative_to(ROOT)
environment = dict(os.environ)
environment.update(request.get("environment", {}))
started = datetime.now(timezone(timedelta(hours=8))).isoformat()
start = time.monotonic()
with targets["stdout"].open("xb") as out, targets["stderr"].open("xb") as err:
    process = subprocess.Popen(command, cwd=cwd, env=environment, stdout=out, stderr=err)
    native_code = process.wait(timeout=request["timeout_seconds"])
receipt = dict(command=command, cwd=str(cwd), pid=process.pid, direct_wait=True,
    native_exit_code=native_code, started_at_utc8=started,
    ended_at_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),
    elapsed_seconds=time.monotonic() - start, peak_memory_bytes=None,
    limitation="真实直接等待返回码；未测量完整进程树峰值，未证明连续监护覆盖。",
    request_sha256=hashlib.sha256(request_path.read_bytes()).hexdigest(),
    logs=[dict(path=str(targets[key]), bytes=targets[key].stat().st_size,
               sha256=hashlib.sha256(targets[key].read_bytes()).hexdigest())
          for key in ("stdout", "stderr")])
with targets["native"].open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps(receipt, ensure_ascii=False))
raise SystemExit(native_code)
