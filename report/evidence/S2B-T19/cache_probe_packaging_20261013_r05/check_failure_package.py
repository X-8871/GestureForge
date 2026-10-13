"""只读检查失败证据与依赖阻断，区分包装通过和功能失败。"""
from pathlib import Path
import json
import os
import subprocess
import sys
root=Path(__file__).absolute().parents[4]
parent=root/"report/evidence/S2B-T19"
folder=parent/"cache_probe_packaging_20261013_r05";folder.mkdir()
rows=[]
for name in ("cache_probe_20261013_r02","cache_probe_execution_20261013_r02"):
    for mode in ("inputs","evidence"):
        command=[sys.executable,"-X","utf8","-B","verification/check_stage_delivery.py","--mode",mode,"--manifest",str(parent/name/"delivery_manifest.json")]
        env=os.environ.copy();env["PYTHONIOENCODING"]="utf-8"
        actual=subprocess.run(command,cwd=root,capture_output=True,env=env)
        label=name+"_"+mode
        (folder/(label+"_stdout.log")).write_bytes(actual.stdout);(folder/(label+"_stderr.log")).write_bytes(actual.stderr)
        rows.append({"command":command,"native_exit_code":actual.returncode,"expected_exit_code":0 if mode=="evidence" else 2})
(folder/"execution.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(rows,ensure_ascii=False))
sys.exit(0 if all(x["native_exit_code"]==x["expected_exit_code"] for x in rows) else 1)
