"""只读重新核验真实失败包装；保存原生退出码，不改变BLOCKED结论。"""
from pathlib import Path
import json
import os
import subprocess
import sys
root=Path(__file__).absolute().parents[4]
parent=root/"report/evidence/S2B-T19"
folder=parent/"cache_probe_packaging_20261013_r04"
folder.mkdir()
for name in ("cache_probe_20261013_r01","cache_probe_execution_20261013_r01"):
    path=parent/name/"delivery_manifest.json"
    (folder/(name+"_manifest_before.json")).write_bytes(path.read_bytes())
    manifest=json.loads(path.read_text(encoding="utf-8"))
    manifest["checks"][0].update(command="vitis.bat -s vitis/run_s2b_visibility_probe.py；入口结果见visibility_probe_result.json",
        exit_code=None)
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
results=[]
for name in ("cache_probe_20261013_r01","cache_probe_execution_20261013_r01"):
    for mode in ("inputs","evidence"):
        command=[sys.executable,"-X","utf8","-B","verification/check_stage_delivery.py","--mode",mode,"--manifest",str(parent/name/"delivery_manifest.json")]
        env=os.environ.copy();env["PYTHONIOENCODING"]="utf-8"
        actual=subprocess.run(command,cwd=root,env=env,capture_output=True)
        label=name+"_"+mode
        (folder/(label+"_stdout.log")).write_bytes(actual.stdout)
        (folder/(label+"_stderr.log")).write_bytes(actual.stderr)
        results.append({"command":command,"native_exit_code":actual.returncode,"expected_exit_code":2 if mode=="inputs" else 0})
(folder/"execution.json").write_text(json.dumps({"checks":results,"hardware_execution":"NOT_RUN"},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(results,ensure_ascii=False))
sys.exit(0 if all(x["native_exit_code"]==x["expected_exit_code"] for x in results) else 1)
