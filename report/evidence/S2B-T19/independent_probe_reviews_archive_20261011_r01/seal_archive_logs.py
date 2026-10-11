"""将已完成Collector真实日志归档，新增清单不覆盖首清单。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import os
ROOT=Path(__file__).absolute().parents[4];CACHE=Path(__file__).absolute().parent
REPORT=ROOT/"report/evidence/S2B-T19/independent_probe_reviews_archive_20261011_r01"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,value):
    """独占UTF8创建。"""
    assert p.parent.is_dir() and not p.exists()
    with p.open("x",encoding="utf-8",newline="\n") as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write("\n")
def rel(p):return p.relative_to(ROOT).as_posix()
old=REPORT/"delivery_manifest.json";obj=json.loads(old.read_text(encoding="utf-8"));before={x["path"]:x["sha256"] for x in obj["files"]}
assert all(sha(ROOT/name)==value for name,value in before.items())
native=json.loads((CACHE/"collector_native.json").read_text(encoding="utf-8"));assert native["native_exit_code"]==0
names=("collector_stdout.log","collector_stderr.log","collector_native.json","evidence.log","inputs.log","collection_status.json")
copies=[]
for name in names:
    source=CACHE/name;target=REPORT/name;assert source.is_file() and not target.exists()
    with target.open("xb") as out:out.write(source.read_bytes())
    assert sha(source)==sha(target);copies.append({"source":str(source),"archive_path":rel(target),"sha256":sha(target),"bytes":target.stat().st_size})
script=REPORT/Path(__file__).name;assert not script.exists()
with script.open("xb") as out:out.write(Path(__file__).read_bytes())
assert sha(script)==sha(Path(__file__))
save(REPORT/"collector_log_mapping.json",{"files":copies,"prior_manifest_sha256":sha(old),"scope":"真实Collector/包装码归档，未重跑SDK或业务测试。"})
project=[row for row in obj["files"] if not row["path"].startswith(rel(REPORT)+"/")];obj["files"]=[]
for p in sorted(REPORT.rglob("*")):
    if not p.is_file():continue
    role="source" if p.suffix==".py" else "log" if p.suffix in (".log",".jsonl") else "artifact" if p.suffix in (".bin",".raw","") else "result"
    if p.name=="review_receipt.json":role="input"
    obj["files"].append({"path":rel(p),"sha256":sha(p),"role":role})
obj["files"].extend(project);final=REPORT/"delivery_manifest_r02.json";save(final,obj);codes={}
for mode in ("evidence","inputs"):
    cmd=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(final)]
    proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=30,env=dict(os.environ,PYTHONIOENCODING="utf-8"));p=CACHE/(mode+"_r02.log");assert not p.exists()
    with p.open("xb") as out:out.write(proc.stdout);out.write(proc.stderr)
    codes[mode]={"native_exit_code":proc.returncode,"command":cmd}
assert all(sha(ROOT/name)==value for name,value in before.items())
result={"manifest_sha256":sha(final),"manifest_path":rel(final),"checker":codes,"all_prior_raw_bindings_unchanged":True,"bound_file_count":len(obj["files"])}
save(CACHE/"final_status.json",result);print(json.dumps(result,ensure_ascii=False))
raise SystemExit(0 if {k:v["native_exit_code"] for k,v in codes.items()}=={"evidence":0,"inputs":2} else 2)
