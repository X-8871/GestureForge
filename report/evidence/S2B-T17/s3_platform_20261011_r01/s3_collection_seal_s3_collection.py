"""封存 S3 失败 STA；保留首清单 schema 失败，仅新增正确格式清单。"""
from collection_common import *
started=time.monotonic()
try:
    original=original_check()
    first=read(REPORT/"s3_collection_delivery_manifest_r01.json")
    collector=read(REPORT/"s3_collection_collector.native.json")
    require(collector["native_exit_code"]==1,"首Collector失败码不符")
    probe=read(REPORT/"s3_collection_packaging_r01.json")
    require(probe["checker"]["evidence"]["native_exit_code"]==2,"首checker失败碼不符")
    oldcheck=read(REPORT/"s3_collection_evidence_r01.stdout.log")
    require(oldcheck["errors"] and all("含未知字段：bytes" in s for s in oldcheck["errors"]),"首失败不只是声明schema问题")
    for row in first["files"]:require(sha(ROOT/row["path"])==row["sha256"],"首已有冻结内容漂移")
    mappings=read(REPORT/"s3_collection_native_mapping.json")["files"]
    for row in mappings:
        original_path=exact(Path(row["original_path"]));saved=exact(ROOT/row["saved_path"])
        require(sha(original_path)==sha(saved)==row["sha256"] and original_path.stat().st_size==saved.stat().st_size==row["bytes"],"原生raw副本不符")
    require(len(mappings)==44,"本次raw应为44项")
    rawcopy(Path(__file__),REPORT/"s3_collection_seal_s3_collection.py")
    save(REPORT/"s3_collection_raw_recheck.json",{"status":"ORIGINAL126_AND_NATIVE44_RAW_BYTES_MATCH","original_count":len(original),"original_files":original,"native_raw_copy_count":len(mappings),"native_raw_copies":mappings,"original_paths_moved":False,"root_session_source_not_future_dependency":True})
    summary=read(REPORT/"s3_collection_summary.json")
    summary["limitations"].append("首Collector原生1、evidence2仅为清单files附未知bytes字段；r01/source/stdout/stderr/native/失败JSON均保存。r02按既有schema只用path/sha256/role，长度仍在原inventory和mapping核验，不重跑综合/业务。")
    summary["collector_prior_attempts"]=[{"command":collector["command"],"native_exit_code":1,"checker_evidence_exit_code":2,"reason":"manifest.files含不支持的bytes字段，数据与STA解析本身通过"}]
    summary["collector_recovery_elapsed_seconds"]=time.monotonic()-started
    summary["script_restore_mapping"]=[{"original_temporary_basename":p.name,"permanent_raw_copy":rel(REPORT/("s3_collection_"+p.name)),"sha256":sha(REPORT/("s3_collection_"+p.name))} for p in sorted(CACHE.glob("*.py")) if (REPORT/("s3_collection_"+p.name)).is_file()]
    save(REPORT/"s3_collection_summary_r02.json",summary)
    checks=first["checks"]+[{"name":"首Collector清单schema失败原件","status":"FAIL","command":" ".join(collector["command"]),"exit_code":1,"reason":"原evidence2仅files未知bytes字段；旧输出不改。"},{"name":"首包装检查失败原件","status":"FAIL","command":" ".join(probe["checker"]["evidence"]["command"]),"exit_code":2,"reason":"实际checker2，原日志保留；长度仍单独校验。"}]
    external=[ROOT/r["path"] for r in summary["external_inputs"]]
    files=manifest_files()+[{**binding(p),"role":"input"} for p in external]
    obj={**{k:v for k,v in first.items() if k not in ("files","checks","limitations")},"files":[{k:r[k] for k in ("path","sha256","role")} for r in files],"checks":checks,"limitations":summary["limitations"]}
    current=REPORT/"s3_collection_delivery_manifest_r02.json";save(current,obj)
    codes={}
    for mode in ("evidence","inputs"):
        codes[mode]=run_closed([sys.executable,"-B",str(REPORT/"s3_collection_stage_checker_snapshot.py"),"--mode",mode,"--manifest",str(current),"--project-root",str(ROOT)],"s3_collection_"+mode+"_r02")
    save(REPORT/"s3_collection_packaging_r02.json",{"checks":codes,"sta_classifier_exit_code":2,"scope":"包装CHECKS_OK不证明STA/G2/G3；原失败完整保留。"})
    require({k:v["native_exit_code"] for k,v in codes.items()}=={"evidence":0,"inputs":2},"r02包装退出码不符")
    original_check()
    print(json.dumps({"status":"SEALED_FAIL_TIMING_PENDING_REVIEW","manifest_sha256":sha(current),"original_count":len(original),"native_raw_copy_count":len(mappings),"elapsed_seconds":time.monotonic()-started,"packaging_codes":{k:v["native_exit_code"] for k,v in codes.items()},"classifier_native_exit_code":2},ensure_ascii=False))
except BaseException as error:
    failure=REPORT/"s3_collection_seal_failure_r02.json"
    if not failure.exists():save(failure,{"status":"SEAL_FAILURE_PRESERVED","error":repr(error),"design_failure":False})
    raise
