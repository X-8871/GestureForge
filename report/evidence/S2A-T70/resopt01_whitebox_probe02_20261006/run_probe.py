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
def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
if log_path.exists(): raise SystemExit("refuse overwrite")
record={"status":"RUNNING","command":[str(binary)],"binary_sha256":sha(binary),"compile_record":"compile_record.json","timeout_seconds":30,"started_utc":datetime.now(timezone.utc).isoformat()}
(work/"simulation_execution_record.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
started=time.monotonic()
try:
    with log_path.open("xb") as f:
        result=subprocess.run([str(binary)],cwd=work,stdout=f,stderr=subprocess.STDOUT,timeout=30,check=False)
    record["exit_code"]=result.returncode
    record["status"]="PASS_FIRST_QUERY" if result.returncode==0 else "FAILED_FIRST_QUERY"
except subprocess.TimeoutExpired:
    record["exit_code"]=None
    record["status"]="TIMEOUT_NO_PROGRESS"
record["duration_seconds"]=round(time.monotonic()-started,3)
record["log_sha256"]=sha(log_path)
record["log_bytes"]=log_path.stat().st_size
record["log_tail"]=log_path.read_text(encoding="utf-8",errors="replace").splitlines()[-30:]
record["pass_marker_count"]=sum(1 for line in record["log_tail"] if line.startswith("PASS TILE_FIRST_QUERY"))
record["finished_utc"]=datetime.now(timezone.utc).isoformat()
(work/"simulation_execution_record.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:record[k] for k in ("status","exit_code","duration_seconds","log_bytes","pass_marker_count","log_tail")},indent=2))
raise SystemExit(0 if record["status"]=="PASS_FIRST_QUERY" else 1)