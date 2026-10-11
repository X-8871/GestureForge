"""最终封存325份原件归档，动态最终核验日志仅写隔离tmp。"""
from collect_archive import *

def main():
    """只绑定已关闭日志，再重复核验所有副本及依赖。"""
    start=time.perf_counter();exact(ARCHIVE,"directory")
    prior=read(ARCHIVE/"delivery_manifest_r01.json")
    for row in prior["files"]:checked(ROOT/row["path"],row["sha256"])
    mapping=read(ARCHIVE/"raw_copy_mapping.json");require(mapping["count"]==325,"raw数量不同")
    for row in mapping["copies"]:
        source=checked(ROOT/row["source"],row["sha256"]);dest=checked(ROOT/row["copy"],row["sha256"])
        require(source.stat().st_size==dest.stat().st_size==row["bytes"],"raw长度不同")
    for name in ("seal_archive.py","run_collector.py","run_seal.py","collector.native.json","collector.stdout.log","collector.stderr.log","collector_inner_result.json"):
        copy(exact(TMP/name),ARCHIVE/name)
    native_record=read(ARCHIVE/"collector.native.json");require(native_record["native_exit_code"]==0,"Collector原生失败")
    external=[r for r in prior["files"] if not r["path"].startswith(rel(ARCHIVE)+"/")]
    closed=[{"path":rel(p),"sha256":sha(p),"bytes":p.stat().st_size} for p in sorted(ARCHIVE.rglob("*")) if p.is_file()]
    save(ARCHIVE/"closed_archive_inventory.json",{"files":closed,"count":len(closed),"scope":"当前已关闭归档原件；本记录与最终manifest由清单绑定，不自绑定动态stdout。"})
    prior["files"]=external+[binding(p,"source" if p.suffix==".py" else "log" if p.suffix==".log" else "result") for p in sorted(ARCHIVE.rglob("*")) if p.is_file()]
    prior["checks"].append({"name":"325份原字节归档Collector","status":"PASS","command":subprocess.list2cmdline(native_record["command"]),"exit_code":0,"reason":"复制前后源与副本SHA/length一致；原R01/R02状态不改，未重跑审查/综合。"})
    final=ARCHIVE/"delivery_manifest_r02.json";save(final,prior)
    stage=checked(ROOT/"report/evidence/S2B-T17/s3_platform_20261011_r01/s3_collection_stage_checker_snapshot.py",STAGE_SHA)
    codes={}
    for mode,expected in (("evidence",0),("inputs",2)):
        codes[mode]=native([sys.executable,"-B",str(stage),"--mode",mode,"--manifest",str(final),"--project-root",str(ROOT)],"final_"+mode,where=TMP)
        require(codes[mode]["native_exit_code"]==expected,"最终检查码不同")
        if mode=="evidence":
            parsed=read(TMP/"final_evidence.stdout.log");require(parsed["errors"]==parsed["warnings"]==[],"最终包装错误")
    for row in prior["files"]:checked(ROOT/row["path"],row["sha256"])
    for row in prior["interfaces"]:checked(ROOT/row["path"],row["sha256"])
    for row in mapping["copies"]:
        require(sha(ROOT/row["source"])==sha(ROOT/row["copy"])==row["sha256"] and (ROOT/row["source"]).stat().st_size==(ROOT/row["copy"]).stat().st_size==row["bytes"],"封存末字节不同")
    files=[p for p in ARCHIVE.rglob("*") if p.is_file()]
    result={"status":"STOP_PASS_ARCHIVE_RAW_INTEGRITY_ONLY","manifest":rel(final),"manifest_sha256":sha(final),"manifest_files":len(prior["files"]),"manifest_interfaces":len(prior["interfaces"]),"total_bindings":len(prior["files"])+len(prior["interfaces"]),"archive_files":len(files),"archive_bytes":sum(p.stat().st_size for p in files),"raw_copy_count":325,"raw_copy_bytes":mapping["bytes"],"raw_copy_mapping_sha256":sha(ARCHIVE/"raw_copy_mapping.json"),"all_raw_copies_equal":True,"all_final_bindings_verified":True,"root_files":sorted(p.name for p in ARCHIVE.iterdir()),"native_commands":codes,"seconds":time.perf_counter()-start,"peak_memory":"NOT_MEASURED","sta_status":"FAIL_TIMING","review_r01_status":"CHANGES_REQUIRED","review_r02_status":"PASS_EVIDENCE_INTEGRITY","hardware":"NOT_RUN","runtime_compatibility":"NOT_APPROVED"}
    save(TMP/"final_status.json",result);print(json.dumps({k:v for k,v in result.items() if k!="native_commands"},ensure_ascii=True))

if __name__=="__main__":
    try:main()
    except BaseException as error:
        p=TMP/"seal_failure.json"
        if not p.exists():save(p,{"status":"SEAL_FAILURE_PRESERVED","error":repr(error)})
        raise
