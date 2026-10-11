"""追加最终r04清单，绑定已结束r03包装及Collector日志，不覆盖历史。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import os
ROOT=Path(__file__).absolute().parents[4];CACHE=Path(__file__).absolute().parent
REPORT=ROOT/"report/evidence/S2B-T17/s2_platform_20261011_r01"
PREFLIGHT=ROOT/"report/evidence/S2B-T17/s2_source_preflight_20261011_r01"
def sha(p):
    """流式原字节hash。"""
    h=hashlib.sha256()
    with p.open("rb") as source:
        for block in iter(lambda:source.read(1048576),b""):h.update(block)
    return h.hexdigest()
def save(p,v):
    """仅创建新输出。"""
    assert p.parent.is_dir() and not p.exists()
    with p.open("x",encoding="utf-8",newline="\n") as out:json.dump(v,out,ensure_ascii=False,indent=2);out.write("\n")
def rel(p):return p.relative_to(ROOT).as_posix()
prior=REPORT/"collection_fix_delivery_manifest_r03.json";obj=json.loads(prior.read_text(encoding="utf-8"))
assert all(sha(ROOT/x["path"])==x["sha256"] for x in obj["files"])
native=json.loads((REPORT/"collection_fix_seal_native.json").read_text(encoding="utf-8"));assert native["native_exit_code"]==0
source=Path(__file__);target=REPORT/("collection_fix_"+source.name);assert not target.exists()
with target.open("xb") as out:out.write(source.read_bytes())
assert sha(source)==sha(target)
external=[x for x in obj["files"] if not x["path"].startswith(rel(REPORT)+"/") and not x["path"].startswith(rel(PREFLIGHT)+"/")]
obj["files"]=[]
for directory in (REPORT,PREFLIGHT):
    for p in sorted(directory.rglob("*")):
        if not p.is_file():continue
        role="source" if p.suffix in (".py",".sv",".v",".tcl",".xdc") else "log" if p.suffix in (".rpt",".log") else "artifact" if p.suffix in (".xsa",".bd",".rst","") else "result"
        if directory==PREFLIGHT:role="input"
        obj["files"].append({"path":rel(p),"sha256":sha(p),"role":role})
obj["files"].extend(external);final=REPORT/"collection_fix_delivery_manifest_r04.json";save(final,obj);codes={}
for mode in ("evidence","inputs"):
    cmd=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(final)]
    proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=30,env=dict(os.environ,PYTHONIOENCODING="utf-8"));path=CACHE/(mode+"_final_r04.log");assert not path.exists()
    with path.open("xb") as out:out.write(proc.stdout);out.write(proc.stderr)
    codes[mode]={"command":cmd,"native_exit_code":proc.returncode}
assert all(sha(ROOT/x["path"])==x["sha256"] for x in obj["files"])
result={"final_manifest":{"path":rel(final),"sha256":sha(final)},"bound_files":len(obj["files"]),"checker":codes,"original_file_raw_count":146,"moved_original_paths":9,"sta_native_exit_code":2,"scope":"G1包装候审，STA真实失败，未实现/位流/实板"}
save(CACHE/"final_status.json",result);print(json.dumps(result,ensure_ascii=False))
raise SystemExit(0 if {k:v["native_exit_code"] for k,v in codes.items()}=={"evidence":0,"inputs":2} else 2)
