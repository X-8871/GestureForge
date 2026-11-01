import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

work = Path(__file__).resolve().parent
binary = work / "obj_dir" / "Vtb_s2a_conv_tile_unit.exe"
log_path = work / "simulation.log"
compile_record_path = work / "compile_record.json"

def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

if not compile_record_path.is_file():
    raise SystemExit("compile_record.json 不存在")
compile_record = json.loads(compile_record_path.read_text(encoding="utf-8"))
if compile_record.get("status") != "PASS_COMPILE" or compile_record.get("exit_code") != 0:
    raise SystemExit("编译记录不是 PASS")
if log_path.exists():
    raise SystemExit("simulation.log 已存在，拒绝覆盖")
command = [str(binary)]
record = {"status": "RUNNING", "python": sys.executable, "command": command,
          "binary_sha256": sha(binary), "compile_record": str(compile_record_path),
          "compile_log_sha256": compile_record["compile_log_sha256"],
          "source_sha256": compile_record["source_sha256_after"], "timeout_seconds": 1200,
          "started_utc": datetime.now(timezone.utc).isoformat()}
(work / "simulation_execution_record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
started = time.monotonic()
with log_path.open("xb") as log:
    result = subprocess.run(command, cwd=work, stdout=log, stderr=subprocess.STDOUT, timeout=1200, check=False)
record["exit_code"] = result.returncode
record["duration_seconds"] = round(time.monotonic() - started, 3)
record["log_sha256"] = sha(log_path)
text = log_path.read_text(encoding="utf-8", errors="replace")
marker = "PASS TILE_WHITEBOX queries=21336 lane_checks=169790"
record["pass_marker_count"] = text.count(marker)
record["query_checkpoints"] = sum(1 for line in text.splitlines() if line.startswith("CHECKPOINT TILE_WHITEBOX "))
record["status"] = "PASS_WHITEBOX_ARITHMETIC_ONLY" if result.returncode == 0 and record["pass_marker_count"] == 1 else "FAILED_SIMULATION"
record["finished_utc"] = datetime.now(timezone.utc).isoformat()
(work / "simulation_execution_record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: record[key] for key in ("status", "exit_code", "duration_seconds", "pass_marker_count", "query_checkpoints", "log_sha256")}, indent=2))
raise SystemExit(result.returncode if record["status"].startswith("PASS") else (result.returncode or 1))