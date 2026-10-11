"""仅归档两轮已停止 S3 完整性审查的绑定原件，不重跑审查或综合。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib,json,subprocess,sys,time,os

ROOT=Path(__file__).absolute().parents[4]
TMP=Path(__file__).absolute().parent
ARCHIVE=ROOT/"report/evidence/S2B-T17/independent_s3_synthesis_review_20261011_r01"
BASELINE="f3a0b0514c90983c41c8729b93f18d627bfc1bb5"
MAIN_SHA="86d9aff8dcda7161bc5027b5906824a59748e1439ed6e87e76637d086409bcd0"
STAGE_SHA="cf640f8202a673319d45a573584e854aefd71dd08226091b96fdbdfd76983dbf"
ROUNDS=[("r01","c6643e33a86d8b41a3f04d245f0452ec2307f94c540428a60da0375a5c57fe57","1d4ce154b8ac4ef5ca7a02fdc93a612f4569d18b9b26930af0ff9999a7cf112c",162,2277942,"CHANGES_REQUIRED",1),
        ("r02","c214f0b90a277db530ff918aa96942d7fda6af53e5bea498fddd558d80ad1834","0d534e6ab6a22bfac6f8a8b5183c9e2fe16ee871e6c5938f3583768d4cfe97b3",161,2279761,"PASS_EVIDENCE_INTEGRITY",0)]

def require(test,message):
    """来源绑定失败立即停止，原件与部分副本保留。"""
    if not test:raise RuntimeError(message)

def exact(path,kind="file"):
    """核验精确路径、类型、归属与链接。"""
    require((path.is_file() if kind=="file" else path.is_dir()) and not path.is_symlink(),str(path))
    require(path.resolve().is_relative_to(ROOT),"路径越界："+str(path));return path

def sha(path):
    """只读取原字节，内存按块有界。"""
    h=hashlib.sha256()
    with exact(path).open("rb") as f:
        for block in iter(lambda:f.read(1048576),b""):h.update(block)
    return h.hexdigest()

def rel(path):return path.relative_to(ROOT).as_posix()
def read(path):return json.loads(exact(path).read_text(encoding="utf-8"))
def checked(path,expected):require(sha(path)==expected,"SHA不同："+str(path));return path
def binding(path,role):return {"path":rel(path),"sha256":sha(path),"role":role}

def save(path,obj):
    """只创建新 UTF-8 记录，绝不覆盖旧输出。"""
    exact(path.parent,"directory");require(not path.exists(),"名称已存在："+str(path))
    with path.open("x",encoding="utf-8",newline="\n") as f:json.dump(obj,f,ensure_ascii=False,indent=2);f.write("\n")

def copy(source,target):
    """复制前后来源、目标 SHA 和长度必须完全相同。"""
    exact(source);exact(target.parent,"directory");require(not target.exists(),"副本已存在")
    before=(sha(source),source.stat().st_size)
    with source.open("rb") as src,target.open("xb") as out:
        for block in iter(lambda:src.read(1048576),b""):out.write(block)
    require(before==(sha(source),source.stat().st_size)==(sha(target),target.stat().st_size),"rawcopy漂移")
    return {"source":rel(source),"source_absolute_path":str(source),"copy":rel(target),"sha256":before[0],"bytes":before[1],"raw_bytes_equal":True}

def native(command,prefix,where=ARCHIVE):
    """仅运行轻量封包检查并记录真实子进程退出码。"""
    start=time.perf_counter();p=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=45,env=dict(os.environ,PYTHONIOENCODING="utf-8"))
    logs=[]
    for suffix,raw in (("stdout",p.stdout),("stderr",p.stderr)):
        path=where/(prefix+"."+suffix+".log");require(not path.exists(),"日志已有")
        with path.open("xb") as f:f.write(raw)
        logs.append({"path":rel(path),"sha256":sha(path),"bytes":path.stat().st_size})
    result={"command":command,"native_exit_code":p.returncode,"seconds":time.perf_counter()-start,"closed_logs":logs,"peak_memory":"NOT_MEASURED"}
    save(where/(prefix+".native.json"),result);return result

def main():
    """先验证实际 schema 和所有范围，再新建唯一归档目录。"""
    start=time.perf_counter();exact(TMP,"directory");exact(ARCHIVE.parent,"directory");require(not ARCHIVE.exists(),"归档目录必须不存在")
    main_path=checked(ROOT/"report/evidence/S2B-T17/s3_platform_20261011_r01/s3_collection_delivery_manifest_r03.json",MAIN_SHA)
    main_manifest=read(main_path);require(main_manifest["source_commit"]==BASELINE and len(main_manifest["files"])+len(main_manifest["interfaces"])==226,"主清单版本/数量不同")
    deps={rel(main_path):binding(main_path,"input")}
    for row in main_manifest["files"]:
        p=checked(ROOT/row["path"],row["sha256"]);deps[rel(p)]=binding(p,"input")
    for row in main_manifest["interfaces"]:checked(ROOT/row["path"],row["sha256"])
    stage=checked(ROOT/"report/evidence/S2B-T17/s3_platform_20261011_r01/s3_collection_stage_checker_snapshot.py",STAGE_SHA)
    require(rel(stage) in deps,"固定checker快照未列入主输入")
    prepared=[]
    for tag,manifest_sha,receipt_sha,count,total,status,code in ROUNDS:
        directory=exact(ROOT/("tmp/2B/S2B-T17/independent_s3_synthesis_review_20261011_"+tag),"directory")
        manifest_path=checked(directory/"raw_delivery_manifest.json",manifest_sha);manifest=read(manifest_path)
        receipt_path=checked(directory/"receipt.json",receipt_sha);receipt=read(receipt_path)
        require(manifest["schema_version"]==1 and manifest["source_commit"]==receipt["source_commit"]==BASELINE and manifest["reviewed_manifest"]==receipt["manifest"]=={"path":rel(main_path),"sha256":MAIN_SHA},"审查依赖版本不符")
        require(receipt["status"]==status and receipt["business_status"]==manifest["business_status"]=="FAIL_TIMING" and receipt["check_count"]==1714,"审查状态/范围不同")
        require(len(receipt["failed_checks"])==(1 if tag=="r01" else 0),"失败记录数量不同")
        rawrows=manifest["files"];require(len(rawrows)==count and sum(r["bytes"] for r in rawrows)==total,"raw范围数量/长度不同")
        require(len({r["path"] for r in rawrows})==count and any(r["path"]==rel(receipt_path) for r in rawrows),"raw重复或收据未绑定")
        for row in rawrows:
            source=checked(ROOT/row["path"],row["sha256"]);require(source.resolve().is_relative_to(directory) and source.stat().st_size==row["bytes"],"raw路径/大小不同")
        actual_native=read(directory/"review.native.json");require(actual_native["native_exit_code"]==code,"审查native码不同")
        prepared.append({"tag":tag,"directory":directory,"manifest_path":manifest_path,"manifest":manifest,"receipt":receipt,"native":actual_native})
    require(sum(len(r["manifest"]["files"])+1 for r in prepared)==325,"应该精确复制325原件")
    ARCHIVE.mkdir();mappings=[];rounds=[]
    for item in prepared:
        target=ARCHIVE/("reviewer_"+item["tag"]);require(not target.exists(),"子目录已存在");target.mkdir()
        records=item["manifest"]["files"]+[{"path":rel(item["manifest_path"]),"sha256":sha(item["manifest_path"]),"bytes":item["manifest_path"].stat().st_size}]
        for row in records:
            source=checked(ROOT/row["path"],row["sha256"]);suffix=source.relative_to(item["directory"]);dest=target/suffix
            require(dest.parent==target,"本轮actualbinding均应为原根文件；不扫描或复制未绑定缓存")
            mapping=copy(source,dest);mapping["review_round"]=item["tag"];mappings.append(mapping)
        rounds.append({"round":item["tag"],"receipt_status":item["receipt"]["status"],"business_status":"FAIL_TIMING","review_check_count":1714,"failed_checks":item["receipt"]["failed_checks"],"review_native":item["native"],"original_receipt_sha256":sha(item["directory"]/"receipt.json"),"original_raw_manifest_sha256":sha(item["manifest_path"]),"copied_file_count":len(records),"findings":item["receipt"]["findings"],"limitations":item["receipt"]["limitations"]})
    copy(Path(__file__),ARCHIVE/"collect_archive.py")
    save(ARCHIVE/"raw_copy_mapping.json",{"schema_version":1,"copies":mappings,"count":len(mappings),"bytes":sum(r["bytes"] for r in mappings),"originals_retained":True,"paths_and_raw_receipts_not_rewritten":True})
    save(ARCHIVE/"archive_result.json",{"status":"PASS_ARCHIVE_RAW_INTEGRITY_ONLY","source_commit":BASELINE,"rounds":rounds,"raw_copy_count":325,"approved_main_manifest":binding(main_path,"input"),"main_file_bindings":224,"main_interface_bindings":2,"elapsed_seconds_before_packaging":time.perf_counter()-start,"peak_memory":"NOT_MEASURED","hardware":"NOT_RUN","synthesis":"NOT_RUN","runtime_compatibility":"NOT_APPROVED","limitations":["R01为1713PASS/1FAIL的Reviewer超时文本误断言，原CHANGES_REQUIRED/native1保持；R02实际1714PASS/native0，范围仅完整性。","STA仍WNS−18.745/TNS−6349.595、806/14653 setup失败，不授予设计G2/部署/G3/G4/G5。","主证据/33前后快照只作精确input，不重复复制；当前S4工作树source未消费。","第一tmp名称检查遇到此前S3软件归档缓存同名，test原生1且未创建/修改；改用独占新名称，本事实不是业务失败。","不执行原审查/STA分类/综合/业务测试；只复制其已绑定raw日志与Git输出。"]})
    r1,r2=prepared;classifier=next(c for c in r2["receipt"]["commands"] if "--report" in c["command"])
    require(classifier["native_exit_code"]==2,"原独立classifier码不是2")
    checks=[{"name":"R01独立Reviewer原断言失败","status":"FAIL","command":subprocess.list2cmdline(r1["native"]["command"]),"exit_code":1,"reason":"原timeout文本误匹配，1713PASS/1FAIL保留，不改为PASS。"},{"name":"R02独立完整性审查原执行","status":"PASS","command":subprocess.list2cmdline(r2["native"]["command"]),"exit_code":0,"reason":"1714项PASS_EVIDENCE_INTEGRITY，原件复制，不重跑审查。"},{"name":"原独立50MHz STA分类","status":"FAIL","command":subprocess.list2cmdline(classifier["command"]),"exit_code":2,"reason":"原分类器2，业务FAIL_TIMING保持。"},{"name":"实物/实现/位流/运行兼容性","status":"NOT_RUN","command":None,"exit_code":None,"reason":"纯归档，不批准runtime兼容性或G3。"}]
    files=list(deps.values())+[binding(p,"source" if p.suffix==".py" else "log" if p.suffix==".log" else "result") for p in sorted(ARCHIVE.rglob("*")) if p.is_file()]
    manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":ARCHIVE.name,"source_commit":BASELINE,"evidence_dir":rel(ARCHIVE),"interfaces":main_manifest["interfaces"],"files":files,"checks":checks,"tool_versions":{"python":sys.version,"fixed_stage_checker_sha256":STAGE_SHA},"limitations":["归档原件完整性PASS不代表STA/设计G2/部署/G3/G5；物理候选未冻结，inputs2。","R01失败和R02完整性结果分别保留；所有raw receipt路径/语义不改。","最终动态stdout不自绑定；先前已关闭日志由封存清单绑定。"]}
    save(ARCHIVE/"delivery_manifest_r01.json",manifest)
    codes={}
    for mode,expected in (("evidence",0),("inputs",2)):
        require(sha(stage)==STAGE_SHA,"固定checker漂移")
        codes[mode]=native([sys.executable,"-B",str(stage),"--mode",mode,"--manifest",str(ARCHIVE/"delivery_manifest_r01.json"),"--project-root",str(ROOT)],"packaging_"+mode+"_r01")
        require(codes[mode]["native_exit_code"]==expected,"包装检查码不同")
        if mode=="evidence":
            parsed=read(ARCHIVE/"packaging_evidence_r01.stdout.log");require(parsed["errors"]==[] and parsed["warnings"]==[],"包装目录错误")
    save(ARCHIVE/"packaging_result_r01.json",{"commands":codes,"peak_memory":"NOT_MEASURED"})
    result={"status":"PASS_ARCHIVE_RAW_INTEGRITY_ONLY","raw_copies":325,"raw_bytes":sum(r["bytes"] for r in mappings),"seconds":time.perf_counter()-start}
    save(TMP/"collector_inner_result.json",result);print(json.dumps(result,ensure_ascii=True))

if __name__=="__main__":
    try:main()
    except BaseException as error:
        p=TMP/"collector_failure.json"
        if not p.exists():save(p,{"status":"COLLECTOR_FAILURE_PRESERVED","error":repr(error)})
        raise
