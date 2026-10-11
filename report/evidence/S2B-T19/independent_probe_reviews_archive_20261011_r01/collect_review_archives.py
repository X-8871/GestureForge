"""只归档已停止的三轮独立审查原字节；无SDK、硬件或业务测试。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib
import json
import sys
import subprocess
import os
import time

ROOT=Path(__file__).absolute().parents[4];CACHE=Path(__file__).absolute().parent
REPORT=ROOT/"report/evidence/S2B-T19/independent_probe_reviews_archive_20261011_r01"
RECEIPTS=[("r01","independent_review_20261011_r01","637d985d16d32ceac32c997e6f7d6f8c3cd31ddddceb3d236a41aa9bfe5b4bb9","independent_artifacts"),
          ("r02","independent_probe_review_20261011_r02","b012a80117dce51ae9d33c751a3ea34acce993a223de4a6ea67d46a03b498a03","artifact_files"),
          ("r03","independent_probe_review_20261011_r03","78a094a0e4ac3894554941f96eea9a8bb887d6c88d0054506197f9232378ed47","artifacts")]
SNAPSHOTS=["report/evidence/S2B-T19/offline_probe_entry_20261011_r01/source_snapshot_r03",
           "report/evidence/S2B-T19/offline_probe_fix_20261011_r01/source_snapshot",
           "report/evidence/S2B-T19/offline_probe_native_fix_20261011_r01/source_snapshot"]
def require(condition,message):
    """不会随-O消失的归档门禁。"""
    if not condition:raise RuntimeError(message)
def sha(path):
    """流式读取原件，不复制大产物。"""
    h=hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda:source.read(1048576),b""):h.update(block)
    return h.hexdigest()
def exact_file(path):
    """核验完整精确文件名及类型。"""
    require(path.is_file() and not path.is_symlink(),"源不是普通文件："+str(path))
    require(any(p.name==path.name for p in path.parent.iterdir()),"文件名大小写或字符漂移："+str(path))
    return path.absolute()
def rel(path):return path.relative_to(ROOT).as_posix()
def save(path,value):
    """只创建新UTF8中文机器记录。"""
    require(path.parent.is_dir() and not path.exists(),"记录目标已存在或父目录错误")
    with path.open("x",encoding="utf-8",newline="\n") as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write("\n")
def strict(raw):
    """收据只读严格JSON解析，不改其原路径或含义。"""
    def pairs(items):
        result={}
        for key,value in items:
            require(key not in result,"收据重复JSON键")
            result[key]=value
        return result
    def bad(value):raise RuntimeError("收据非标准常量："+value)
    return json.loads(raw.decode("utf-8-sig"),object_pairs_hook=pairs,parse_constant=bad)

require(REPORT.is_dir() and CACHE.is_dir(),"已授权新Run目录缺失")
started=time.monotonic();mapping=[];rounds=[];source_proofs=[];largest=0
try:
    # 三轮不同schema按实际键取原件，禁止扫描未绑定临时产物。
    plans=[]
    for index,(round_name,directory,digest,key) in enumerate(RECEIPTS):
        receipt=exact_file(ROOT/"tmp/2B/S2B-T19"/directory/"review_receipt.json")
        require(sha(receipt)==digest,"收据SHA漂移")
        value=strict(receipt.read_bytes());require(type(value["schema_version"]) is int and value["schema_version"]==1,"收据版本无效")
        items=value[key]
        if round_name=="r01":require(type(items) is dict,"R1原件schema错误");items=list(items.values())
        else:require(type(items) is list,"R2/R3原件schema错误")
        bound=[{"path":str(receipt),"sha256":digest,"bytes":receipt.stat().st_size,"kind":"receipt"}]
        for row in items:
            require(type(row) is dict and {"path","sha256"}<=set(row),"审查原件绑定错误")
            path=Path(row["path"]);path=path if path.is_absolute() else ROOT/path
            path=exact_file(path);path.relative_to(receipt.parent)
            require(path.stat().st_size<=2*1024*1024,"单原件超出归档预算")
            require(sha(path)==row["sha256"],"审查原件SHA漂移："+str(path))
            if "bytes" in row:require(type(row["bytes"]) is int and row["bytes"]==path.stat().st_size,"审查原件长度漂移")
            bound.append({"path":str(path),"declared_path":row["path"],"sha256":row["sha256"],"bytes":path.stat().st_size,"declared_bytes":row.get("bytes"),"kind":"artifact"})
        require(len({row["path"] for row in bound})==len(bound),"收据原件路径重复")
        source_bindings=value["source_bindings"] if round_name=="r01" else value["source_and_evidence_sha256"]
        for source in ("vitis/run_s2b_visibility_probe.py","verification/test_s2b_visibility_probe.py"):
            snapshot=exact_file(ROOT/SNAPSHOTS[index]/Path(source).name)
            require(sha(snapshot)==source_bindings[source],"历史源码精确快照与收据不符")
            source_proofs.append({"round":round_name,"reviewed_source_path":source,"reviewed_source_sha256":source_bindings[source],"snapshot_path":rel(snapshot),"snapshot_sha256":sha(snapshot),"current_source_equality_required":False})
        plans.append((round_name,receipt.parent,bound))
        rounds.append({"round":round_name,"receipt_original":str(receipt),"receipt_sha256":digest,"receipt_schema_field":key,"original_status":value["status"],"original_scope":value.get("scope"),"artifact_count":len(items),"raw_total_bytes":sum(row["bytes"] for row in bound)})
    require(sum(row["raw_total_bytes"] for row in rounds)<=32*1024*1024,"归档总量超过轻量预算")
    for round_name,parent,bound in plans:
        targetdir=REPORT/round_name;require(not targetdir.exists(),"归档轮次目标已存在");targetdir.mkdir()
        for row in bound:
            source=Path(row["path"]);target=targetdir/source.relative_to(parent)
            if not target.parent.exists():target.parent.mkdir(parents=True)
            require(target.parent.is_dir() and not target.exists(),"副本目标已存在或父类型错误")
            require(sha(source)==row["sha256"],"复制前原件漂移")
            with source.open("rb") as src,target.open("xb") as out:
                while block:=src.read(1048576):out.write(block)
            require(target.is_file() and target.stat().st_size==row["bytes"] and sha(target)==row["sha256"],"复制后原字节校验失败")
            mapping.append({**row,"round":round_name,"archive_path":rel(target),"archive_sha256":sha(target),"archive_bytes":target.stat().st_size})
            largest=max(largest,row["bytes"])
    script=REPORT/Path(__file__).name;require(not script.exists(),"Collector副本已存在")
    with script.open("xb") as out:out.write(Path(__file__).read_bytes())
    require(sha(script)==sha(Path(__file__)),"Collector原字节不符")
    save(REPORT/"source_snapshot_proofs.json",{"proofs":source_proofs,"reason":"旧审查源码按当时已冻结快照绑定，不要求当前R3源等于旧R1/R2源。"})
    save(REPORT/"archive_mapping.json",{"schema_version":1,"scope":"RAW_BYTES_ARCHIVE_ONLY","rounds":rounds,"files":mapping,"receipt_original_paths_unchanged":True})
    require(all(sha(Path(row["path"]))==row["sha256"] and sha(ROOT/row["archive_path"])==row["sha256"] for row in mapping),"归档结束原件或副本漂移")
    baseline=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT).decode("ascii").strip()
    limits=["只证明绑定原件复制完整；R1/R2状态CHANGES_REQUIRED及launcher0/inner1原件照存，不改为通过。","R3原件PASS范围仅软件G2，不批准runtimecompat/cold/cache/硬件或G3/G4/G5。","只复制收据绑定原件及收据本身，未绑定临时构建文件不扫描/不归档，tmp原件未删未改。","不执行SDK、串口、ROSS、业务测试或提交；峰值内存未测，最大原件和总字节如实记录。"]
    save(REPORT/"archive_result.json",{"status":"PASS_ARCHIVE_RAW_BYTES_ONLY","source_commit":baseline,"rounds":rounds,"raw_copy_count":len(mapping),"raw_copy_bytes":sum(row["bytes"] for row in mapping),"largest_raw_file_bytes":largest,"elapsed_seconds":time.monotonic()-started,"peak_memory_bytes":None,"collector_exit_code":0,"hardware_execution":"NOT_RUN","sdk_execution":"NOT_RUN","business_tests":"NOT_RUN","timestamp_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),"limitations":limits})
    formal=exact_file(ROOT/"report/evidence/S2B-T19/offline_probe_native_fix_20261011_r01/delivery_manifest_r03.json")
    require(sha(formal)=="bf7bae1ed9827159ed70f5115d43734959ac6b293e415180d6005ca85263d153","R3交付清单漂移")
    upstream=strict(formal.read_bytes())
    files=[]
    for p in sorted(REPORT.rglob("*")):
        if not p.is_file():continue
        role="source" if p.suffix==".py" else "log" if p.suffix in (".log",".jsonl") else "artifact" if p.suffix in (".bin",".raw","") else "result"
        if p.name=="review_receipt.json":role="input"
        files.append({"path":rel(p),"sha256":sha(p),"role":role})
    files.append({"path":rel(formal),"sha256":sha(formal),"role":"input"})
    for row in source_proofs:files.append({"path":row["snapshot_path"],"sha256":row["snapshot_sha256"],"role":"input"})
    manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T19","run_id":REPORT.name,"source_commit":baseline,"evidence_dir":rel(REPORT),"interfaces":upstream["interfaces"],"files":files,"checks":[{"name":"bound_review_raw_archive","status":"PASS","command":"python -B "+rel(Path(__file__).absolute()),"exit_code":0},{"name":"hardware_runtime_compatibility_cold_cache","status":"NOT_RUN","command":None,"exit_code":None,"reason":"归档原件任务不提供实物验证或正式兼容性批准。"}],"tool_versions":{"python":sys.version},"limitations":limits}
    save(REPORT/"delivery_manifest.json",manifest)
    codes={}
    for mode in ("evidence","inputs"):
        command=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(REPORT/"delivery_manifest.json")]
        proc=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=30,env=dict(os.environ,PYTHONIOENCODING="utf-8"))
        log=CACHE/(mode+".log");require(not log.exists(),"checker输出已存在")
        with log.open("xb") as out:out.write(proc.stdout);out.write(proc.stderr)
        codes[mode]={"command":command,"native_exit_code":proc.returncode}
    result={"manifest_sha256":sha(REPORT/"delivery_manifest.json"),"raw_copy_count":len(mapping),"raw_copy_bytes":sum(row["bytes"] for row in mapping),"rounds":rounds,"checker":codes}
    save(CACHE/"collection_status.json",result);print(json.dumps(result,ensure_ascii=False))
    require({k:v["native_exit_code"] for k,v in codes.items()}=={"evidence":0,"inputs":2},"归档机器包装退出与要求不同")
except BaseException as error:
    target=CACHE/"collector_failure.json"
    if not target.exists():save(target,{"status":"FAIL_ARCHIVE_COLLECTION_PRESERVED","error":repr(error),"copied_before_failure":len(mapping),"elapsed_seconds":time.monotonic()-started,"business_failure":False})
    raise
