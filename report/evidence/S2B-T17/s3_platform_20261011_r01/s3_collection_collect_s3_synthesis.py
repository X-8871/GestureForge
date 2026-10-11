"""归集 S3 实际综合失败证据；只消费冻结快照、已关闭工具历史及原生日志。"""
from collection_common import *
from datetime import datetime,timezone,timedelta
import re,zipfile,zlib

def git_blob(relative):
    """仅访问指定 Git 对象，不读取后续 S4 源文件。"""
    command=["git","show",BASELINE+":"+relative]
    proc=subprocess.run(command,cwd=ROOT,capture_output=True)
    require(proc.returncode==0,"冻结 Git 对象不可读："+relative)
    return proc.stdout,command,proc.returncode

def first(pattern,text):
    """原报告字段必须实际存在。"""
    values=re.findall(pattern,text,re.M);require(values,"报告字段缺失："+pattern);return values[0].strip()

started=time.monotonic()
try:
    originals=original_check()
    for source in sorted(CACHE.glob("*.py")):
        rawcopy(source,REPORT/("s3_collection_"+source.name))
    before=read(PRE/"source_before.json");after=read(PRE/"source_after.json")
    require(before["source_commit"]==after["source_commit"]==BASELINE and after["status"]=="PASS_SOURCE_BEFORE_AFTER","S3来源基线不同")
    rows=before["source_files"];later={r["path"]:r for r in after["source_files"]}
    require(len(rows)==len(later)==33 and len({r["path"] for r in rows})==33,"冻结33闭包不符")
    sources=[]
    for row in rows:
        old=exact(ROOT/row["snapshot"]);new=exact(ROOT/later[row["path"]]["snapshot"])
        require(binding(old)["sha256"]==binding(new)["sha256"]==row["sha256"]==later[row["path"]]["sha256"] and old.stat().st_size==new.stat().st_size==row["bytes"]==later[row["path"]]["bytes"],"前后冻结快照不同："+row["path"])
        blob,command,code=git_blob(row["path"]);raw=old.read_bytes();same=blob==raw
        eol=not same and b"\r\n" not in blob and blob.replace(b"\n",b"\r\n")==raw
        h=hashlib.sha256(blob).hexdigest()
        require(h==row["git_blob_sha256"] and (same or eol),"非精确Git RAW/EOL关系："+row["path"])
        require(row["git_relation"]==("RAW_IDENTICAL" if same else "GIT_LF_TO_RAW_CRLF"),"旧记录关系不同")
        sources.append({**row,"snapshot_after":rel(new),"git_native_command":command,"git_native_exit_code":code,"git_raw_same":same,"exact_git_lf_to_snapshot_crlf":eol})
    require(sum(s["git_raw_same"] for s in sources)==29 and sum(s["exact_git_lf_to_snapshot_crlf"] for s in sources)==4,"应为29 RAW/4 EOL")
    profile=read(PRE/"source_snapshot/board/s2b_inference_platform.json")
    require(profile["version"]=="s2b-inference-platform/0.1.3" and profile["visibility_default"]==0 and profile["clock_hz"]==50000000 and profile["vivado_part"]=="xc7z020clg400-2","S3固定profile不同")
    save(REPORT/"s3_collection_source_binding.json",{"status":"SOURCE33_BEFORE_AFTER_RAW_SAME_GIT_F3_BOUND","source_commit":BASELINE,"observed_after_head":after["observed_head"],"sources":sources,"raw_same_count":29,"exact_eol_count":4,"source_current_s4_consumed":False,"note":"4项仅Git LF精确转换到当时RAW CRLF验证通过，不声称RAW等于Git blob；after observed_head为当时其他提交事实，不替换构建基线。"})

    native_root=mkdir_new(REPORT/"native_jobs");run_root=exact(PROJECT/"s2b_inference_candidate.runs","directory")
    dirs=sorted(p for p in run_root.iterdir() if p.is_dir() and p.name!=".jobs")
    require(len(dirs)==5,"原生运行目录数不是5")
    mapping=[];jobs=[];dcps=[]
    for directory in dirs:
        exact(directory,"directory")
        target=mkdir_new(native_root/("wrapper_native_s3_r01" if directory.name=="synth_1" else directory.name))
        log=(directory/"runme.log").read_text(encoding="utf-8")
        require("synth_design completed successfully" in log and "0 Critical Warnings and 0 Errors encountered" in log,"原生综合未完成")
        require((directory/"__synthesis_is_complete__").is_file() and (directory/".vivado.end.rst").is_file() and not (directory/".vivado.error.rst").exists(),"原生结束marker错误")
        for p in sorted(directory.iterdir()):
            if not p.is_file():continue
            if p.suffix in (".tcl",".log",".jou",".xdc",".rpt") or p.name in (".vivado.begin.rst",".vivado.end.rst",".vivado.error.rst","__synthesis_is_complete__",".Vivado_Synthesis.queue.rst"):
                mapping.append(rawcopy(p,target/p.name))
            elif p.suffix==".dcp":
                dcps.append({"path":str(p),"sha256":sha(p),"bytes":p.stat().st_size,"permanent":False,"purpose":"仅ignored重建缓存引用，不复制，不作为长期恢复依赖"})
        m=re.search(r"synth_design:.*?elapsed = (\d+):(\d+):(\d+)",log);require(m,"原生耗时缺失")
        counts=re.findall(r"(\d+) Infos, (\d+) Warnings, (\d+) Critical Warnings and (\d+) Errors encountered",log);require(counts,"原生最终诊断数缺失")
        jobs.append({"run":directory.name,"saved_directory":rel(target),"status":"NATIVE_SYNTH_COMPLETED_LOG_AND_MARKERS","pid":int(first(r"Process ID\s*:\s*(\d+)",log)),"session_start":first(r"Start of session at:\s*([^\r\n]+)",log),"session_end":first(r"Exiting Vivado at ([^\r\n]+)",log),"synth_design_elapsed_seconds":int(m[1])*3600+int(m[2])*60+int(m[3]),"reported_single_process_peak_mb":max(map(float,re.findall(r"peak = ([0-9.]+)",log))),"final_diagnostics":dict(zip(("infos","warnings","critical_warnings","errors"),map(int,counts[-1]))),"raw_process_exit_code":None,"reason":"子进程OS退出码未直接观测；成功依据原生日志、结束markers及同次wait0。PS7有本次真实PID/log，不从查询Complete虚构另进程。"})
    infer=next(j for j in jobs if j["run"]=="s2b_inference_infer_0_synth_1")
    require(infer["synth_design_elapsed_seconds"]==180 and infer["reported_single_process_peak_mb"]==2265.180 and infer["final_diagnostics"]["warnings"]==118,"核心原生指标不符")
    tcl=(native_root/"s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl").read_text(encoding="utf-8")
    block=first(r"read_verilog -library xil_defaultlib -sv \{([^}]+)\}",tcl)
    compiled=[Path(line.strip()).relative_to(ROOT).as_posix() for line in block.splitlines() if line.strip()]
    require(len(compiled)==18 and set(compiled)==set(profile["rtl_sources"]) and set(compiled)<=set(later),"实际编译18源与固定profile不符")
    require("synth_design -top s2b_inference_infer_0 -part xc7z020clg400-2" in tcl,"核心part绑定不符")
    save(REPORT/"s3_collection_native_mapping.json",{"files":mapping,"jobs":jobs,"actual_compiled_rtl_sources":compiled,"actual_compiled_source_count":18,"source_snapshot_binding":rel(REPORT/"s3_collection_source_binding.json"),"dcp_references":dcps,"root_source_paths_moved":False,"wrapper_saved_directly_as":"wrapper_native_s3_r01","process_tree_peak_memory":"NOT_MEASURED","aggregate_wall_time":"NOT_MEASURED"})

    raw=read(PRE/"root_mcp_calls_closed.json")
    blocks=[json.loads(c["text"]) for c in raw["history"]["content"] if c["type"]=="text"]
    history=[h for b in blocks for h in b["history"]]
    selected=[h for h in history if 77<=h["id"]<=85]
    require([h["id"] for h in selected]==list(range(77,86)) and len(raw["calls"])==9,"本次历史范围不完整")
    paired=[]
    for call,h in zip(raw["calls"],selected):
        require(call["command"]==h["command"] or (h["id"]==77 and call["command"]=="source_utf8"),"调用与原生历史不符")
        paired.append({"client_command_label":call["command"],"native_history":h,"client_result":call["result"],"source_label_expanded_from_actual_history":h["id"]==77})
    by_id={h["id"]:h for h in selected}
    require(by_id[78]["code"]==1 and by_id[78]["elapsed"]==24.498 and by_id[81]["command"]=="wait_on_run synth_1" and by_id[81]["code"]==0 and by_id[81]["elapsed"]==351.6 and by_id[83]["code"]==0 and by_id[83]["elapsed"]==31.089,"原生关键码或耗时不符")
    require(raw["calls"][4]["result"].get("isError") is True and "after 300s" in raw["calls"][4]["result"]["content"][0]["text"],"客户端wait超时原件缺失")
    query_result=json.loads(raw["calls"][2]["result"]["content"][0]["text"])
    require("source_count 18 wrapper_count 1" in query_result["output"] and "part xc7z020clg400-2 visibility 0" in query_result["output"],"实际source/top/visibility查询不符")
    state_result=json.loads(raw["calls"][7]["result"]["content"][0]["text"])
    require("clock_period 20.000" in state_result["output"] and state_result["output"].count("status {synth_design Complete!} progress 100%") ==5 and state_result["output"].count("status {Not started} progress 0%") ==5,"闭合运行/实现状态不符")
    products=(REPORT/"products.tcldict").read_text(encoding="utf-8")
    require("status FAIL code 0 raw PRODUCTS:OK" in products and "WARNING emitted=-8 exported=2" in products and "native_counts_before {WARNING 9" in products and "native_counts_after {WARNING 1" in products,"products原失败capture不符")
    save(REPORT/"s3_collection_mcp_history_binding.json",{"status":"S3_NATIVE_HISTORY77_TO85_BOUND_CLIENT_FAILURE_PRESERVED","session_id":raw["session_id"],"paired_calls":paired,"excluded_prior_history_ids":[h["id"] for h in history if h["id"]<77],"mcp_calls":9,"wait_client_status":"TIMEOUT_ERROR_300_SECONDS","wait_client_exit_code":None,"wait_native_exit_code":0,"wait_native_elapsed_seconds":351.6,"whole_builder_native_exit_code":1,"products_native_exit_code":0,"products_capture_exit_code":1,"reason":"WARNING9→1导致emitted−8/exported2失败；不改为成功，不重复products。source_utf8标签由实际history77补全。"})

    classifier=run_closed([sys.executable,"-B",str(CACHE/"classify_s3_sta.py"),"--report",str(REPORT/"timing_summary_synth.rpt"),"--result",str(REPORT/"s3_collection_sta_result.json")],"s3_collection_sta")
    require(classifier["native_exit_code"]==2,"分类器必须实际返回2")
    sta=read(REPORT/"s3_collection_sta_result.json");timing=sta["timing"]
    require(timing["wns_ns"]==-18.745 and timing["tns_ns"]==-6349.595 and timing["setup_failing_endpoints"]==806 and timing["setup_total_endpoints"]==14653 and timing["whs_ns"]==0.037 and timing["ths_ns"]==0 and timing["wpws_ns"]==8.870 and timing["tpws_ns"]==0 and not any(sta["check_timing"].values()),"实际S3 STA数值不同")
    util=(REPORT/"utilization_flat_synth.rpt").read_text(encoding="utf-8")
    resources={k:int(first(r"^\|\s*"+re.escape(label)+r"\s*\|\s*(\d+)\s*\|",util)) for k,label in (("lut","Slice LUTs*"),("ff","Slice Registers"),("bram","Block RAM Tile"),("dsp","DSPs"))}
    require(resources=={"lut":32790,"ff":4017,"bram":32,"dsp":160},"实际资源不同")
    worst=(REPORT/"timing_worst_synth.rpt").read_text(encoding="utf-8")
    w={"source":first(r"^\s*Source:\s*(\S+)",worst),"destination":first(r"^\s*Destination:\s*(\S+)",worst),"logic_levels":int(first(r"^\s*Logic Levels:\s*(\d+)",worst)),"carry4":int(first(r"^\s*Logic Levels:.*?CARRY4=(\d+)",worst)),"data_path_delay_ns":float(first(r"^\s*Data Path Delay:\s*([\d.]+)ns",worst)),"logic_delay_ns":float(first(r"^\s*Data Path Delay:.*?logic ([\d.]+)ns",worst)),"route_delay_ns":float(first(r"^\s*Data Path Delay:.*?route ([\d.]+)ns",worst))}
    require(w["source"].endswith("u_conv_engine/input_batch_count_latched_reg[0]/C") and w["destination"].endswith("u_conv_engine/request_address_latched_reg[10]/CE") and (w["logic_levels"],w["carry4"],w["data_path_delay_ns"],w["logic_delay_ns"],w["route_delay_ns"])==(67,39,38.133,20.141,17.992),"最坏CONV路径不符")
    require("No valid timing exceptions found." in (REPORT/"exceptions_synth.rpt").read_text(encoding="utf-8"),"exceptions不同")

    old_xsa=exact(ROOT/"report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa");new_xsa=exact(REPORT/"s2b_inference_no_bit.xsa")
    members=[]
    with zipfile.ZipFile(old_xsa) as a,zipfile.ZipFile(new_xsa) as b:
        for name in ("ps7_init.c","ps7_init.h","ps7_init.html","ps7_init.tcl","ps7_init_gpl.c","ps7_init_gpl.h","s2b_inference.hwh"):
            x=a.read(name);y=b.read(name);require(zlib.crc32(x)==a.getinfo(name).CRC and zlib.crc32(y)==b.getinfo(name).CRC,"XSA成员CRC错误")
            members.append({"member":name,"old_sha256":hashlib.sha256(x).hexdigest(),"new_sha256":hashlib.sha256(y).hexdigest(),"old_bytes":len(x),"new_bytes":len(y),"raw_equal":x==y,"old_crc32":a.getinfo(name).CRC,"new_crc32":b.getinfo(name).CRC})
    require(all(r["raw_equal"] for r in members[:6]) and not members[6]["raw_equal"],"PSinit/HWH比较不符合实际")
    save(REPORT/"s3_collection_xsa_member_comparison.json",{"status":"SIX_PSINIT_BYTES_SAME_HWH_CHANGED","old_xsa":binding(old_xsa),"new_xsa":binding(new_xsa),"members":members,"elf_runtime_compatibility":"NOT_APPROVED","limitation":"旧六PSinit字节相同不批准旧BSP/ELF与新PL整体兼容，未下载。"})

    blob,checker_command,checker_code=git_blob("verification/check_stage_delivery.py")
    require(hashlib.sha256(blob).hexdigest()==CHECKER_SHA,"固定stage checker Git字节不同")
    checker=REPORT/"s3_collection_stage_checker_snapshot.py"
    require(not checker.exists(),"checker快照已有")
    with checker.open("xb") as out:out.write(blob)
    save(REPORT/"s3_collection_stage_checker_binding.json",{"source_commit":BASELINE,"original_path":"verification/check_stage_delivery.py","snapshot":binding(checker),"git_command":checker_command,"git_native_exit_code":checker_code,"current_s4_checker_consumed":False})
    interface_source=exact(ROOT/"report/evidence/S2B-T17/s2_platform_20261011_r01/collection_fix_delivery_manifest_r04.json")
    interfaces=read(interface_source)["interfaces"]
    for interface in interfaces:require(sha(ROOT/interface["path"])==interface["sha256"],"冻结接口文档不同")
    external=[old_xsa,exact(ROOT/"report/evidence/S2B-T15/full_build_20261011_r01/build_details.json"),interface_source]
    summary={"status":"COLLECTED_FAIL_TIMING_PENDING_EVIDENCE_REVIEW","source_commit":BASELINE,"source_count":33,"compiled_rtl_count":18,"profile_version":profile["version"],"visibility":0,"original_raw_file_count":len(originals),"original_raw_unchanged":True,"native_raw_copy_count":len(mapping),"native_job_count":len(jobs),"native_wait_exit_code":0,"native_wait_elapsed_seconds":351.6,"native_report_exit_code":0,"native_report_elapsed_seconds":31.089,"native_classifier_exit_code":2,"timing":timing,"check_timing":sta["check_timing"],"resources":resources,"worst_path":w,"no_valid_timing_exceptions":True,"prior_source_preflight_attempt":before["prior_attempt"],"external_inputs":[binding(p) for p in external],"collector_elapsed_seconds":time.monotonic()-started,"peak_memory_bytes":None,"time_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat()}
    limitations=["G1仅失败证据归集，独立完整性审查待执行；STA仍FAIL_TIMING，不等于G2时序通过或G3/G4/G5。","仅33 S3前后冻结快照及Gitf3来源；实际编译18，当前S4源/profile不消费；29RAWsame与4精确EOL分别声明。","MCP客户端300s timeout与同次nativewait0/351.6s分记，后者是wait耗时而非总wall。","whole builder1/24.498s；products native0但WARNING9→1 capture1/emitted−8/exported2原FAIL保留，未重跑products。","report命令0/31.089s与独立STA classifier真实2分别记录；原生综合成功不代表50MHz时序满足。","根会话累计peak2677.445MB含旧S1/S2/S3，infer单进程peak2265.180MB/180s/118warning分别记录，不是全tree峰；实际全tree峰/总墙钟及Collector峰未测。","五job按真实PID/log/结束marker核验，PS7不是依据查询Complete伪造的虚拟进程；各OS子进程退出码未直接观测为null。","DCP仅ignored原路径/SHA引用，不复制，不作为长期冻结恢复依赖；native源文件名不改，wrapper副本直接保存至wrapper_native_s3_r01，未迁移旧路径。","root完整native日志含旧非UTF8字节，副本原字节保存；活动源路径仅metadata，后续变化不影响副本绑定。","六PSinit成员相同而HWH变化，不批准旧BSP/ELF整体runtime兼容；物理接口候选0.1.1未冻结。","source_before.prior_attempt记录首次inlinePython SyntaxError原生1且整个未执行；原件不改，不视作RTL失败。","postroute/bit/cache/model/109/G3均NOT_RUN；不创建SDKsession、不硬件/ROSS/Vivado/重型/提交。"]
    summary["limitations"]=limitations;save(REPORT/"s3_collection_summary.json",summary)
    checks=[{"name":"S3冻结33来源Git字节核验","status":"PASS","command":" ".join(sources[0]["git_native_command"]),"exit_code":0,"reason":"显示第一条实际Git命令；其余32条真实command/exit0均另绑定，不消费S4。"},{"name":"本次原生综合完成","status":"PASS","command":by_id[81]["command"],"exit_code":0,"reason":"history81 wait351.6s，客户端timeout保持原错误。"},{"name":"STA报告生成","status":"PASS","command":by_id[83]["command"],"exit_code":0},{"name":"独立50MHz综合STA分类","status":"FAIL","command":" ".join(classifier["command"]),"exit_code":2,"reason":"WNS−18.745/TNS−6349.595，806/14653 setup失败。"},{"name":"完整builder/products capture原失败","status":"FAIL","command":by_id[78]["command"],"exit_code":1,"reason":"产品native0，capture1，whole1；旧FAIL不改。"},{"name":"首次source preflight inlinePython包装失败","status":"FAIL","command":"root原inlinePython命令：source_before.prior_attempt记录，原完整命令未捕获","exit_code":1,"reason":before["prior_attempt"]["reason"]}]
    for name in ("postroute实现","bitstream生成","板上缓存probe","板上模型推理","109样本回归","G3实物验收"):
        checks.append({"name":name,"status":"NOT_RUN","command":None,"exit_code":None,"reason":"本次只有完整综合；STA失败，未实施此项。"})
    files=manifest_files()+[{**binding(p),"role":"input"} for p in external]
    manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":REPORT.name,"source_commit":BASELINE,"evidence_dir":rel(REPORT),"interfaces":interfaces,"files":files,"checks":checks,"tool_versions":{"python":sys.version,"Vivado":"2026.1 Build6511674 原报告/日志","part":"xc7z020clg400-2","profile":"s2b-inference-platform/0.1.3"},"limitations":limitations}
    original_check();save(REPORT/"s3_collection_delivery_manifest_r01.json",manifest)
    codes={}
    for mode in ("evidence","inputs"):
        codes[mode]=run_closed([sys.executable,"-B",str(checker),"--mode",mode,"--manifest",str(REPORT/"s3_collection_delivery_manifest_r01.json"),"--project-root",str(ROOT)],"s3_collection_"+mode+"_r01")
    save(REPORT/"s3_collection_packaging_r01.json",{"checker":codes,"scope":"CHECKS_OK仅目录/hash包装，实际STA2保持失败，interfaces未冻结。"})
    require({k:v["native_exit_code"] for k,v in codes.items()}=={"evidence":0,"inputs":2},"包装检查退出码不同")
    original_check();print(json.dumps({"status":"COLLECTED_FAIL_TIMING","original_files":len(originals),"source_files":len(sources),"native_copies":len(mapping),"native_jobs":len(jobs),"classifier_native_exit_code":2,"packaging_codes":{k:v["native_exit_code"] for k,v in codes.items()},"elapsed_seconds":time.monotonic()-started},ensure_ascii=False))
except BaseException as error:
    failure=REPORT/"s3_collection_failure_r01.json"
    if not failure.exists():save(failure,{"status":"COLLECTOR_FAILURE_PRESERVED","error":repr(error),"design_failure":False,"elapsed_seconds":time.monotonic()-started})
    raise
