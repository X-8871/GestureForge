"""保存本次离线映射回归的真实命令、退出码、原始输出和源码快照。"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

root=Path(__file__).absolute().parents[4]
parent=root/"report/evidence/S2B-T19/debug_csr_memmap_20261013_r01"
parent.mkdir(exist_ok=True)
label=sys.argv[1]
if label not in ("targeted_r02","entry_r01","entry_r02","entry_r03","entry_r04","entry_r05","entry_r06"):
    raise RuntimeError("未知验证选择")
folder=parent/label
folder.mkdir()
files=["vitis/run_s2b_visibility_probe.py","verification/test_s2b_visibility_probe.py"]
before={}
for name in files:
    raw=(root/name).read_bytes()
    before[name]=hashlib.sha256(raw).hexdigest()
    target=folder/"source_snapshot"/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(raw)
module="verification.test_s2b_visibility_probe"+(".CsrDebugMapTests" if label.startswith("targeted") else "")
command=[sys.executable,"-X","utf8","-B","-m","unittest",module,"-v"]
env=os.environ.copy();env["PYTHONIOENCODING"]="utf-8"
started=time.monotonic()
result=subprocess.run(command,cwd=root,capture_output=True,env=env)
elapsed=time.monotonic()-started
(folder/"stdout.log").write_bytes(result.stdout)
(folder/"stderr.log").write_bytes(result.stderr)
after={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in files}
record={"command":command,"cwd":str(root),"native_exit_code":result.returncode,"elapsed_seconds":elapsed,
        "python_version":sys.version,"source_sha256_before":before,"source_sha256_after":after,
        "source_unchanged":before==after,"hardware_execution":"NOT_RUN","peak_memory":"未测",
        "stdout_sha256":hashlib.sha256(result.stdout).hexdigest(),"stderr_sha256":hashlib.sha256(result.stderr).hexdigest()}
with (folder/"execution.json").open("x",encoding="utf-8",newline="\n") as output:
    json.dump(record,output,ensure_ascii=False,indent=2);output.write("\n")
print(json.dumps(record,ensure_ascii=False))
print(result.stderr.decode("utf-8",errors="backslashreplace")[-2500:])
sys.exit(result.returncode if before==after else 3)
