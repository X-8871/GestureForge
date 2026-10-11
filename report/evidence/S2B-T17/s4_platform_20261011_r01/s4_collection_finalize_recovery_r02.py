"""绑定关闭的Collector与检查输出，再对最终清单只读核验。"""
from collection_common import *
from datetime import datetime,timezone,timedelta
started=time.monotonic()
try:
    original=original_check()
    prior=read(REPORT/"s4_collection_delivery_manifest_r01.json")
    for row in prior["files"]:require(sha(ROOT/row["path"])==row["sha256"],"r01绑定漂移")
    collector=read(REPORT/"s4_collection_recovery_r02.native.json");require(collector["native_exit_code"]==0,"Collector原生失败")
    pack=read(REPORT/"s4_collection_packaging_r01.json")
    require({k:v["native_exit_code"] for k,v in pack["checks"].items()}=={"evidence":0,"inputs":2},"包装实际码不同")
    summary=read(REPORT/"s4_collection_summary.json")
    summary.update(collector_native_exit_code=0,collector_command=collector["command"],collector_elapsed_seconds=collector["elapsed_seconds"],closed_packaging_codes={k:v["native_exit_code"] for k,v in pack["checks"].items()},final_timestamp_utc8=datetime.now(timezone(timedelta(hours=8))).isoformat(),final_validation_log_policy="最终核验输出仅写tmp；清单绑定此前已关闭的r01检查及Collector原件，避免自绑定活动stdout。")
    save(REPORT/"s4_collection_summary_final.json",summary)
    formal_rows=[binding(p) for p in sorted(REPORT.rglob("*")) if p.is_file()]
    save(REPORT/"s4_collection_closed_inventory.json",{"status":"CLOSED_FORMAL_FILES_BEFORE_FINAL_MANIFEST","file_count":len(formal_rows),"total_bytes":sum(r["bytes"] for r in formal_rows),"files":formal_rows,"note":"该索引自身及最终manifest由最终manifest绑定，不自绑定；original142另逐项核验。"})
    externals=[ROOT/r["path"] for r in summary["external_inputs"]]
    prior["files"]=manifest_files(externals)
    prior["checks"] += [{"name":"S4失败证据Collector执行","status":"PASS","command":" ".join(collector["command"]),"exit_code":0,"reason":"只核验及封装原件，STA2保留；真实Collector0且关闭输出已绑定。"},{"name":"已关闭的证据包装检查","status":"PASS","command":" ".join(pack["checks"]["evidence"]["command"]),"exit_code":0,"reason":"仅目录/hash包装通过，inputs实际2、STA实际2及BOARD未执行分别保留。"},{"name":"已关闭的阶段inputs检查","status":"FAIL","command":" ".join(pack["checks"]["inputs"]["command"]),"exit_code":2,"reason":"未冻结候选接口、实际FAIL和NOT_RUN阻断输入验收；没有把包装通过误记阶段通过。"}]
    final=REPORT/"s4_collection_delivery_manifest_r02.json";save(final,prior)
    checks={}
    for mode in ("evidence","inputs"):
        checks[mode]=run_closed([sys.executable,"-B",str(REPORT/"s4_collection_stage_checker_snapshot.py"),"--mode",mode,"--manifest",str(final),"--project-root",str(ROOT)],"s4_final_"+mode)
    require({k:v["native_exit_code"] for k,v in checks.items()}=={"evidence":0,"inputs":2},"最终核验原生码不同")
    result=read(CACHE/"s4_final_evidence.stdout.log");require(result["status"]=="CHECKS_OK" and not result["errors"] and not result["warnings"],"最终包装仍有错误或警告")
    for row in prior["files"]:require(sha(ROOT/row["path"])==row["sha256"],"最终索引漂移")
    for row in prior["interfaces"]:require(sha(ROOT/row["path"])==row["sha256"],"接口索引漂移")
    original_check()
    formal=[p for p in REPORT.rglob("*") if p.is_file()]
    record={"status":"STOP_S4_FAIL_TIMING_EVIDENCE_PENDING_INDEPENDENT_REVIEW","source_commit":BASELINE,"final_manifest":binding(final),"file_bindings":len(prior["files"]),"interface_bindings":len(prior["interfaces"]),"formal_report_files":len(formal),"formal_report_bytes":sum(p.stat().st_size for p in formal),"original_raw_files":len(original),"native_raw_copy_count":summary["native_raw_copy_count"],"source_count":37,"platform_static_source_count":31,"compiled_rtl_count":18,"git_raw_same_count":31,"exact_eol_count":6,"collector_native_exit_code":collector["native_exit_code"],"native_classifier_exit_code":2,"final_checks":checks,"finalize_elapsed_seconds":time.monotonic()-started,"collector_peak_memory_bytes":None,"process_tree_peak_memory_bytes":None,"git_or_state_modified":False,"hardware_or_ross_touched":False}
    save(CACHE/"final_status.json",record);print(json.dumps(record,ensure_ascii=False))
except BaseException as error:
    failure=CACHE/"finalization_recovery_failure.json"
    if not failure.exists():save(failure,{"status":"FINALIZATION_FAILURE_PRESERVED","error":repr(error)})
    raise
