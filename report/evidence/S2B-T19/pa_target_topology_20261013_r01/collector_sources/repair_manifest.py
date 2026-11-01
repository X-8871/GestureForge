"""保留首版不兼容清单和原生失败，按既有schema重建包装清单，不修改源码或回归结果。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

root=Path(__file__).resolve().parents[4]
folder=root/"report/evidence/S2B-T19/pa_target_topology_20261013_r01"
command=[sys.executable,"-X","utf8","-B","verification/check_stage_delivery.py","--mode","evidence","--manifest",str(folder/"delivery_manifest.json")]
result=subprocess.run(command,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
for label,raw in (("stdout",result.stdout),("stderr",result.stderr)):
    (folder/("packing_failure_r01."+label+".log")).write_bytes(raw)
(folder/"packing_failure_r01.json").write_text(json.dumps({"command":command,"exit_code":result.returncode,
    "reason":"首版checks含schema不支持的elapsed_seconds；耗时留run_result原件，r02只移除不支持字段。","run_count":2},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
shutil.copyfile(__file__,folder/"collector_sources/repair_manifest.py")
manifest=json.loads((folder/"delivery_manifest.json").read_text(encoding="utf-8"))
for row in manifest["checks"]:row.pop("elapsed_seconds",None)
manifest["checks"].append({"name":"首版包装清单schema检查","status":"FAIL","command":subprocess.list2cmdline(command),"exit_code":result.returncode,
                           "reason":"不支持elapsed_seconds字段；真实失败原件保留，r02更正包装字段。"})
files=[]
for file in sorted(folder.rglob("*")):
    if file.is_file():
        files.append({"path":file.relative_to(root).as_posix(),"sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
                      "role":"source" if file.suffix==".py" else "input" if file.name in ("actual_r04_topology.json","sdk_basis.json") else "result",
                      "keep_reason":"本轮实际输入、固定源码快照、原生回归/包装失败与更正证据。"})
manifest["files"]=files
with (folder/"delivery_manifest_r02.json").open("x",encoding="utf-8",newline="\n") as out:
    json.dump(manifest,out,ensure_ascii=False,indent=2);out.write("\n")
print(json.dumps({"preserved_failure_exit_code":result.returncode,"files":len(files),
                  "manifest_sha256":hashlib.sha256((folder/"delivery_manifest_r02.json").read_bytes()).hexdigest()},ensure_ascii=False))
