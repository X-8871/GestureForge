"""按获批的唯一目录迁移封存S2；旧失败、inventory和manifest不改。"""
from pathlib import Path
import json
import hashlib
import subprocess
import sys
import os
import time

ROOT=Path(__file__).absolute().parents[4];CACHE=Path(__file__).absolute().parent
REPORT=ROOT/"report/evidence/S2B-T17/s2_platform_20261011_r01"
PREFLIGHT=ROOT/"report/evidence/S2B-T17/s2_source_preflight_20261011_r01"
def require(condition,message):
    """严格原字节门禁。"""
    if not condition:raise RuntimeError(message)
def sha(p):
    """流式hash，任何原文件不转码。"""
    h=hashlib.sha256()
    with p.open("rb") as source:
        for block in iter(lambda:source.read(1048576),b""):h.update(block)
    return h.hexdigest()
def read(p):return json.loads(p.read_text(encoding="utf-8"))
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,value):
    """新UTF8输出，不覆盖旧记录。"""
    require(p.parent.is_dir() and not p.exists(),"输出名称已存在或父路径错误")
    with p.open("x",encoding="utf-8",newline="\n") as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write("\n")
started=time.monotonic()
relocation=read(REPORT/"collection_fix_native_relocation.json")
relocated={rel(Path(x["old_path"])):rel(Path(x["new_path"])) for x in relocation["files"]}
original=read(REPORT/"collection_fix_original_inventory.json")["files"]
checked=[]
for x in original:
    path=ROOT/relocated.get(x["path"],x["path"])
    require(path.is_file() and path.stat().st_size==x["bytes"] and sha(path)==x["sha256"],"原146项在迁移映射后字节不符")
    checked.append({"original_path":x["path"],"current_path":rel(path),"sha256":sha(path),"bytes":path.stat().st_size,"path_moved":x["path"] in relocated})
require(sum(x["path_moved"] for x in checked)==9,"只允许迁移9项")
summary=read(REPORT/"collection_fix_summary.json")
summary.update(original_file_raw_count=len(checked),original_raw_bytes_unchanged=True,original_paths_all_unchanged=False,
               moved_file_count=9,unchanged_path_file_count=137,relocation_mapping=rel(REPORT/"collection_fix_native_relocation.json"),
               collector_prior_attempts=[{"result":rel(REPORT/"collection_fix_collector_native.json"),"native_exit_code":1,"reason":"source_after采用source_commit_at_build_start/source_commit_at_check，首假定统一键错误；原件保留。"},
                                         {"result":rel(REPORT/"collection_fix_collector_native_r02.json"),"native_exit_code":1,"reason":"独立报告/Git28核验正确，包装缓存目录及external role拒绝，原checker2保留。"}])
summary["limitations"].append("获root批准，仅native_jobs/synth_1改目录名wrapper_native_s2_r01；9文件原字节/内部布局一致，旧inventory/native_mapping/失败清单里的原路径不改，以新增映射恢复。")
summary["limitations"].append("旧collector_delivery_manifest从未运行checker，不能声称它已有native失败码；真正本轮r02 checker2日志保留，r03只修目录和preflight input角色。")
save(REPORT/"collection_fix_original_recheck.json",{"status":"ORIGINAL146_RAW_BYTES_RECHECKED_WITH_APPROVED9_PATH_RELOCATION","files":checked,"raw_bytes_all_unchanged":True,"path_unchanged_count":137,"path_moved_count":9})
save(REPORT/"collection_fix_summary_r02.json",summary)
copy=REPORT/("collection_fix_"+Path(__file__).name);require(not copy.exists(),"新Collector副本已存在")
with copy.open("xb") as out:out.write(Path(__file__).read_bytes())
require(sha(copy)==sha(Path(__file__)),"Collector副本SHA不符")
old=read(REPORT/"collection_fix_delivery_manifest_r02.json")
sta_native=read(REPORT/"collection_fix_sta_native_r02.json")
checks=old["checks"]
checks[0]={"name":"S2原件146及唯一9目录迁移字节核验","status":"PASS","command":"python -B "+rel(Path(__file__).absolute()),"exit_code":0,"reason":"冻结Git5a/S2快照，当前S3工程源未读取。"}
checks.append({"name":"首本轮Collector schema错误原件","status":"FAIL","command":" ".join(read(REPORT/"collection_fix_collector_native.json")["command"]),"exit_code":1,"reason":"source_after真实schema不同，原件保留；后续按start/check字段验证。"})
checks.append({"name":"本轮r02目录/角色包装失败原件","status":"FAIL","command":" ".join(read(REPORT/"collection_fix_collector_native_r02.json")["command"]),"exit_code":1,"reason":"真实checker2：synth_1缓存目录、external preflight不能为result；本r03保存获批迁移与input角色。"})
external=[ROOT/x["path"] for x in summary["external_inputs"]]
utility=ROOT/"verification/check_stage_delivery.py"
def manifest():
    """按实际新路径绑定全Run，只用被冻结的S2源快照。"""
    files=[]
    for directory in (REPORT,PREFLIGHT):
        for path in sorted(directory.rglob("*")):
            if not path.is_file():continue
            role="source" if path.suffix in (".py",".sv",".v",".tcl",".xdc") else "log" if path.suffix in (".log",".rpt") else "artifact" if path.suffix in (".xsa",".bd",".rst","") else "result"
            if directory==PREFLIGHT:role="input"
            files.append({"path":rel(path),"sha256":sha(path),"role":role})
    for p in external:files.append({"path":rel(p),"sha256":sha(p),"role":"input"})
    files.append({"path":rel(utility),"sha256":sha(utility),"role":"source"})
    return {**{k:v for k,v in old.items() if k not in ("files","checks","limitations")},"files":files,"checks":checks,"limitations":summary["limitations"]}
probe=REPORT/"collection_fix_delivery_manifest_r03.json";save(probe,manifest());codes={}
for mode in ("evidence","inputs"):
    cmd=[sys.executable,"-B",str(utility),"--mode",mode,"--manifest",str(probe)]
    proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=30,env=dict(os.environ,PYTHONIOENCODING="utf-8"));path=REPORT/("collection_fix_"+mode+"_r03.log");require(not path.exists(),"包装日志名称已有")
    with path.open("xb") as out:out.write(proc.stdout);out.write(proc.stderr)
    codes[mode]={"command":cmd,"native_exit_code":proc.returncode}
save(REPORT/"collection_fix_packaging_r03.json",{"checker":codes,"semantic_sta_native_exit_code":sta_native["native_exit_code"],"scope":"目录/hash封装，不等于STA/G2/G3"})
require({k:v["native_exit_code"] for k,v in codes.items()}=={"evidence":0,"inputs":2},"r03包装退出码不符")
for row in checked:require(sha(ROOT/row["current_path"])==row["sha256"],"封存时原件变动")
save(CACHE/"seal_status.json",{"status":"SEALED_FAIL_TIMING_PENDING_REVIEW","r03_manifest_sha256":sha(probe),"original_raw_recheck_count":len(checked),"moved_path_count":9,"elapsed_seconds":time.monotonic()-started,"checker":codes})
print(json.dumps(read(CACHE/"seal_status.json"),ensure_ascii=False))
