"""最终清单绑定已关闭的封存日志；最后只读核验输出留在隔离 tmp。"""
from collection_common import *
from datetime import datetime,timezone,timedelta
started=time.monotonic()
try:
    original=original_check()
    prior=REPORT/"s3_collection_delivery_manifest_r02.json";obj=read(prior)
    for row in obj["files"]:require(sha(ROOT/row["path"])==row["sha256"],"r02冻结文件漂移")
    seal=read(REPORT/"s3_collection_seal.native.json");require(seal["native_exit_code"]==0,"封存恢复实际失败")
    pack=read(REPORT/"s3_collection_packaging_r02.json")
    require({k:v["native_exit_code"] for k,v in pack["checks"].items()}=={"evidence":0,"inputs":2},"已结束包装结果不同")
    for source in (Path(__file__),CACHE/"run_seal.py"):
        rawcopy(source,REPORT/("s3_collection_"+source.name))
    summary=read(REPORT/"s3_collection_summary_r02.json")
    summary["recovery_collector_native_exit_code"]=seal["native_exit_code"]
    summary["recovery_collector_command"]=seal["command"]
    summary["recovery_collector_elapsed_seconds"]=seal["elapsed_seconds"]
    summary["closed_packaging_codes"]={k:v["native_exit_code"] for k,v in pack["checks"].items()}
    summary["final_timestamp_utc8"]=datetime.now(timezone(timedelta(hours=8))).isoformat()
    summary["final_validation_log_policy"]="最后只读核验日志写tmp并返回原生码；不自绑定仍在执行的stdout，清单绑定之前已关闭的r02检查原件。"
    save(REPORT/"s3_collection_summary_final.json",summary)
    closed_rows=[binding(ROOT/r["path"]) for r in manifest_files() if r["path"].startswith(rel(REPORT)+"/")]
    save(REPORT/"s3_collection_closed_inventory.json",{"status":"CLOSED_REPORT_FILES_BOUND_BEFORE_FINAL_MANIFEST","files":closed_rows,"note":"本记录和最终manifest由最终清单绑定；原126项及44rawcopy已另核验，不自绑定本文件。"})
    files=manifest_files()+[{**binding(ROOT/r["path"]),"role":"input"} for r in summary["external_inputs"]]
    obj["files"]=[{k:r[k] for k in ("path","sha256","role")} for r in files]
    obj["checks"] += [{"name":"S3失败证据封存恢复","status":"PASS","command":" ".join(seal["command"]),"exit_code":0,"reason":"真实封存native0；原126项/44副本字节核验，首schema失败保留。"},{"name":"已关闭r02包装检查","status":"PASS","command":" ".join(pack["checks"]["evidence"]["command"]),"exit_code":0,"reason":"目录与hash包装通过，STA2/候选inputs2/G3未执行分别保留。"}]
    final=REPORT/"s3_collection_delivery_manifest_r03.json";save(final,obj)
    codes={}
    for mode in ("evidence","inputs"):
        codes[mode]=run_closed([sys.executable,"-B",str(REPORT/"s3_collection_stage_checker_snapshot.py"),"--mode",mode,"--manifest",str(final),"--project-root",str(ROOT)],"s3_final_"+mode,where=CACHE)
    require({k:v["native_exit_code"] for k,v in codes.items()}=={"evidence":0,"inputs":2},"最终核验退出码不符")
    evidence=read(CACHE/"s3_final_evidence.stdout.log")
    require(evidence["status"]=="CHECKS_OK" and not evidence["errors"] and not evidence["warnings"],"最终目录/hash还有错误")
    for row in obj["files"]:require(sha(ROOT/row["path"])==row["sha256"],"最终清单文件漂移")
    original_check()
    found=[p for p in REPORT.rglob("*") if p.is_file()]
    record={"status":"STOP_G1_FAIL_TIMING_EVIDENCE_PENDING_INDEPENDENT_REVIEW","manifest":binding(final),"bound_files":len(obj["files"]),"interface_count":len(obj["interfaces"]),"total_bindings":len(obj["files"])+len(obj["interfaces"]),"report_file_count":len(found),"report_total_bytes":sum(p.stat().st_size for p in found),"original_raw_file_count":len(original),"native_raw_copy_count":44,"source_count":33,"actual_compiled_rtl_count":18,"source_raw_same_git":29,"source_exact_eol":4,"source_commit":BASELINE,"stage_checker_sha256":sha(REPORT/"s3_collection_stage_checker_snapshot.py"),"native_wait_exit_code":0,"native_wait_elapsed_seconds":351.6,"native_report_exit_code":0,"native_report_elapsed_seconds":31.089,"native_classifier_exit_code":2,"first_collector_exit_code":1,"recovery_collector_exit_code":0,"checker":codes,"finalize_elapsed_seconds":time.monotonic()-started,"peak_memory_bytes":None,"whole_collection_wall_seconds":None,"scope":"只有G1包装，STA真实失败；未postroute/bit/cache/model/109/G3；不提交，不读取S4源。"}
    save(CACHE/"final_status.json",record);print(json.dumps(record,ensure_ascii=False))
except BaseException as error:
    failure=CACHE/"finalize_failure.json"
    if not failure.exists():save(failure,{"status":"FINALIZE_FAILURE_PRESERVED","error":repr(error)})
    raise
