"""只修新Run清单遗漏，失败原件不覆盖，工程源码不写入。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import os

ROOT=Path(__file__).absolute().parents[4];CACHE=Path(__file__).absolute().parent
REPORT=ROOT/"report/evidence/S2B-T19/offline_probe_native_fix_20261011_r01"
def sha(p):
    """流式原字节校验。"""
    h=hashlib.sha256()
    with p.open("rb") as src:
        for block in iter(lambda:src.read(1048576),b""):h.update(block)
    return h.hexdigest()
def save(p,obj):
    """只创建新文件。"""
    assert p.parent.is_dir() and not p.exists()
    with p.open("x",encoding="utf-8",newline="\n") as out:json.dump(obj,out,ensure_ascii=False,indent=2);out.write("\n")
def rel(p):return p.relative_to(ROOT).as_posix()
old=REPORT/"delivery_manifest.json";obj=json.loads(old.read_text(encoding="utf-8"))
before={row["path"]:row["sha256"] for row in obj["files"]}
assert all(sha(ROOT/name)==expected for name,expected in before.items())
failure={"status":"FAIL_PACKAGING_SCHEMA_PRESERVED","evidence_native_exit_code":2,"inputs_native_exit_code":2,"reason":"checks中两个NOT_RUN记录遗漏必须的command/exit_code；修订只补null字段，不改变任何测试状态或旧文件。","old_manifest":{"path":rel(old),"sha256":sha(old)},"old_final_status":{"path":str(CACHE/"final_status.json"),"sha256":sha(CACHE/"final_status.json")},"not_design_or_runtime_failure":True}
save(REPORT/"packaging_schema_failure.json",failure)
target=REPORT/Path(__file__).name;assert not target.exists()
with target.open("xb") as out:out.write(Path(__file__).read_bytes())
assert sha(target)==sha(Path(__file__))
for row in obj["checks"]:
    if row["status"]=="NOT_RUN":row["command"]=None;row["exit_code"]=None
obj["checks"].append({"name":"initial_packaging_schema_failure_preserved","status":"FAIL","command":"python -B collect_native_fix.py","exit_code":2,"reason":"首清单缺NOT_RUN必填字段，旧清单/日志保留；r02新清单修复包装格式。"})
project=[row for row in obj["files"] if not row["path"].startswith(rel(REPORT)+"/")]
obj["files"]=[]
for file in sorted(REPORT.rglob("*")):
    if not file.is_file():continue
    role="source" if file.suffix==".py" else "log" if file.suffix in (".log",".jsonl") else "artifact" if file.suffix in (".bin",".raw") else "result"
    obj["files"].append({"path":rel(file),"sha256":sha(file),"role":role})
obj["files"].extend(project)
final=REPORT/"delivery_manifest_r02.json";save(final,obj);codes={}
for mode in ("evidence","inputs"):
    command=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(final)]
    proc=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=30,env=dict(os.environ,PYTHONIOENCODING="utf-8"))
    path=CACHE/(mode+"_r02.log");assert not path.exists()
    with path.open("xb") as out:out.write(proc.stdout);out.write(proc.stderr)
    codes[mode]=proc.returncode
assert all(sha(ROOT/name)==expected for name,expected in before.items())
status={"manifest":{"path":rel(final),"sha256":sha(final)},"packaging":codes,"prior_all_bound_bytes_unchanged":True,"sources":{row["path"]:row["sha256"] for row in project if row["path"] in ("vitis/run_s2b_visibility_probe.py","verification/test_s2b_visibility_probe.py")}}
save(CACHE/"final_status_r02.json",status);print(json.dumps(status,ensure_ascii=False))
raise SystemExit(0 if codes=={"evidence":0,"inputs":2} else 2)
