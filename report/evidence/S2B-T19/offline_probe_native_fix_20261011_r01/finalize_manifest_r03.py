"""新清单将纯导入配置标为真实输入；旧清单保持原字节。"""
from pathlib import Path
import hashlib
import json
import subprocess
import os
import sys
ROOT=Path(__file__).absolute().parents[4];CACHE=Path(__file__).absolute().parent
REPORT=ROOT/"report/evidence/S2B-T19/offline_probe_native_fix_20261011_r01"
def sha(p):
    """原字节哈希。"""
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):
    """独占UTF8创建。"""
    assert p.parent.is_dir() and not p.exists()
    with p.open("x",encoding="utf-8",newline="\n") as out:json.dump(obj,out,ensure_ascii=False,indent=2);out.write("\n")
def rel(p):return p.relative_to(ROOT).as_posix()
old=REPORT/"delivery_manifest_r02.json";obj=json.loads(old.read_text(encoding="utf-8"))
assert all(sha(ROOT/x["path"])==x["sha256"] for x in obj["files"])
save(REPORT/"input_role_correction.json",{"reason":"r02把全部JSON默认result，漏标实际读取sdk_gate_only_config为input；补角色不改变输入文件或测试结果。","previous_manifest":{"path":rel(old),"sha256":sha(old)},"previous_inputs_native_exit_code":2,"old_files_unchanged":True})
copy=REPORT/Path(__file__).name;assert not copy.exists()
with copy.open("xb") as out:out.write(Path(__file__).read_bytes())
project=[x for x in obj["files"] if not x["path"].startswith(rel(REPORT)+"/")];obj["files"]=[]
for p in sorted(REPORT.rglob("*")):
    if not p.is_file():continue
    role="source" if p.suffix==".py" else "log" if p.suffix in (".log",".jsonl") else "artifact" if p.suffix in (".bin",".raw") else "result"
    if p.name in ("sdk_gate_only_config.json","upstream_r02_review_receipt.json","upstream_r02_native_origins.json"):role="input"
    obj["files"].append({"path":rel(p),"sha256":sha(p),"role":role})
obj["files"].extend(project);final=REPORT/"delivery_manifest_r03.json";save(final,obj);codes={}
for mode in ("evidence","inputs"):
    cmd=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(final)]
    proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=30,env=dict(os.environ,PYTHONIOENCODING="utf-8"));out=CACHE/(mode+"_r03.log");assert not out.exists()
    with out.open("xb") as file:file.write(proc.stdout);file.write(proc.stderr)
    codes[mode]=proc.returncode
assert all(sha(ROOT/x["path"])==x["sha256"] for x in obj["files"])
result={"manifest":{"path":rel(final),"sha256":sha(final)},"packaging":codes,"bound_files":len(obj["files"]),"sources":{x["path"]:x["sha256"] for x in project if x["path"] in ("vitis/run_s2b_visibility_probe.py","verification/test_s2b_visibility_probe.py")}}
save(CACHE/"final_status_r03.json",result);print(json.dumps(result,ensure_ascii=False))
raise SystemExit(0 if codes=={"evidence":0,"inputs":2} else 2)
