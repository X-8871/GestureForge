#!/usr/bin/env python3
"""保存独立脚本真实原生退出码和完整stdout/stderr，再冻结精确原件列表。"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
root=Path(r"C:\Users\22061\.codex\worktrees\96a3\FPGA_Competition")
work=Path(__file__).resolve().parent
env=os.environ.copy();env.update(PYTHONUTF8="1",PYTHONIOENCODING="utf-8")
started=time.monotonic()
command=[sys.executable,"-B",str(work/"review.py")]
result=subprocess.run(command,cwd=root,env=env,capture_output=True)
for name,value in (("host.stdout.log",result.stdout),("host.stderr.log",result.stderr)):
    with (work/name).open("xb") as f:f.write(value)
native={"command":command,"native_exit_code":result.returncode,"seconds":round(time.monotonic()-started,3),"stdout_bytes":len(result.stdout),"stderr_bytes":len(result.stderr),"r01_failure":"前次审查脚本把geometry/route/backend的simulation_counts误读为actual_coverage，未启动任何RTL；原宿主tool报告1，未观测该次Python原生退出，不补造。"}
(work/"host.native.json").write_text(json.dumps(native,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
raw=[p for p in work.iterdir() if p.is_file()]
raw+=list((work/"source").iterdir()) if (work/"source").is_dir() else []
prior=work.parent/"independent_patch_guard_review_20261011_r01"
raw+=list(prior.iterdir())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
manifest={"schema_version":1,"task_id":"S2B-T17-S5","files":[{"path":p.relative_to(root).as_posix(),"sha256":sha(p),"role":"independent_review_raw"} for p in raw],"bytes_by_path":{p.relative_to(root).as_posix():p.stat().st_size for p in raw},"status":json.loads((work/"review_receipt.json").read_text(encoding="utf-8"))["status"],"manifest_self":"raw_delivery_manifest_r02.json自身另报SHA与bytes；清单包含前版清单和r01失败，不扫描obj_dir缓存。"}
target=work/"raw_delivery_manifest_r02.json"
target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(result.stdout.decode("utf-8",errors="replace"))
print(result.stderr.decode("utf-8",errors="replace"))
print(json.dumps({"native_exit_code":result.returncode,"raw_manifest_sha256":sha(target),"raw_manifest_bytes":target.stat().st_size,"files":len(raw),"seconds":native["seconds"]}))
