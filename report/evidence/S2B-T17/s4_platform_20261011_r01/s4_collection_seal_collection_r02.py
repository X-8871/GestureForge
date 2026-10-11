"""封装 S4 实际综合失败原件；只消费快照、Git f96 和关闭历史。"""
from collection_common import *
from datetime import datetime,timezone,timedelta
import re,xml.etree.ElementTree as ET,zipfile,zlib

def first(pattern,text):
    """必须从实际文本中读到字段。"""
    values=re.findall(pattern,text,re.M);require(values,"字段缺失："+pattern);return values[0].strip()

def copy_closed_record(prefix):
    """把轻量检查的已关闭记录封存到正式证据目录。"""
    return [rawcopy(CACHE/(prefix+"."+s),REPORT/(prefix+"."+s)) for s in ("stdout.log","stderr.log","native.json")]


# 已有副本只读核验，不覆盖首轮任何原件。
rawcopy_new=rawcopy
mkdir_new_first=mkdir_new
save_new=save
def rawcopy(source,target):
    """首轮已经复制的文件只核验原字节。"""
    if not target.exists():return rawcopy_new(source,target)
    exact(source);exact(target)
    a=binding(source);b=binding(target)
    require(a["sha256"]==b["sha256"] and a["bytes"]==b["bytes"],"已有副本漂移："+str(target))
    return {"original_path":str(source),"saved_path":rel(target),"sha256":b["sha256"],"bytes":b["bytes"]}
def mkdir_new(path):
    """首轮新建目录仅验证并复用。"""
    return exact(path,"directory") if path.exists() else mkdir_new_first(path)
def save(path,value):
    """相同的首轮JSON仅验证，不重写。"""
    if path.exists():require(read(path)==value,"首轮JSON内容不同："+str(path))
    else:save_new(path,value)

started=time.monotonic()
try:
    for d in (REPORT,*PRES,CACHE,PROJECT):exact(d,"directory")
    inventories=original_check()
    counts=read(REPORT/"s4_collection_original_inventory.json")["directories"]
    require(len(inventories)==142,"原件冻结数量不同")
    for name in ("prepare_recovery_r02.py","seal_collection_r02.py","run_recovery_r02.py","finalize_recovery_r02.py","run_final_recovery_r02.py"):
        rawcopy(CACHE/name,REPORT/("s4_collection_"+name))
    for name in ("collection_common.py","classify_s4_sta.py","collect_s4_synthesis.py","run_collection.py","finalize_s4_manifest.py","run_finalization.py"):
        rawcopy(CACHE/name,REPORT/("s4_collection_"+name))
    root_log=REPORT/"s4_collection_root_session_snapshot.log"
    require(sha(root_log)=="5d604023f62bf8d1474ac63f49bbf759ab81eb1fc09da6ba262e2b285b9c1863" and root_log.stat().st_size==457507,"根会话immutable副本不同")
    save(REPORT/"s4_collection_root_session_snapshot.json",{"snapshot":binding(root_log),"scope":"原样累计副本包含旧运行，S4只按封闭history86–94及本次cache五run定位；不读取其活动源日志。","active_source_read":False,"s4_single_run_peak_from_root_log":False})

    before=read(PRE/"source_before.json");after=read(PRE/"source_after.json")
    require(before["source_commit"]==after["source_commit"]==BASELINE,"基线不是f96")
    require(before["status"]=="PASS_SOURCE_BEFORE_ONLY" and after["status"]=="PASS_SOURCE_AFTER_ONLY","原source状态不同")
    require(before["platform_static_source_count"]==after["platform_static_source_count"]==31,"static不是31")
    rows=before["source_files"];later={r["path"]:r for r in after["source_files"]}
    require(len(rows)==len(later)==37 and len({r["path"] for r in rows})==37,"37闭包不符")
    sources=[]
    for row in rows:
        old=exact(ROOT/row["snapshot"]);new=exact(ROOT/later[row["path"]]["snapshot"])
        require(sha(old)==sha(new)==row["sha256"]==later[row["path"]]["sha256"] and old.stat().st_size==new.stat().st_size==row["bytes"]==later[row["path"]]["bytes"],"前后快照漂移："+row["path"])
        blob,command,code=git_blob(row["path"]);raw=old.read_bytes();same=blob==raw
        eol=not same and b"\r\n" not in blob and blob.replace(b"\n",b"\r\n")==raw
        require(hashlib.sha256(blob).hexdigest()==row["git_blob_sha256"] and (same or eol),"非RAW/精确EOL关系："+row["path"])
        require(row["git_relation"]==("RAW_IDENTICAL" if same else "GIT_LF_TO_RAW_CRLF"),"关系标签不同")
        sources.append({**row,"snapshot_after":rel(new),"git_native_command":command,"git_native_exit_code":code,"git_raw_same":same,"exact_git_lf_to_snapshot_crlf":eol,"live_source_consumed":False})
    require(sum(s["git_raw_same"] for s in sources)==31 and sum(s["exact_git_lf_to_snapshot_crlf"] for s in sources)==6,"Git31RAW/6EOL计数不同")
    freeze=exact(ROOT/before["source_freeze"]);require(sha(freeze)==before["source_freeze_sha256"]==after["source_freeze_sha256"],"源冻结record漂移")
    frozen=read(freeze);require(frozen["source_sha256"]=={r["path"]:r["sha256"] for r in rows},"r15冻结37不同")
    originals14=before["frozen14_sha256"]
    require(originals14==after["frozen14_sha256"]==frozen["frozen14_sha256"] and len(originals14)==14,"原14绑定不同")
    for name,expected in originals14.items():require(sha(ROOT/later[name]["snapshot"])==expected,"原14快照漂移")
    profile=read(ROOT/next(r["snapshot"] for r in rows if r["path"]=="board/s2b_inference_platform.json"))
    require(profile["version"]=="s2b-inference-platform/0.1.4" and profile["visibility_default"]==0 and profile["clock_hz"]==50000000 and profile["vivado_part"]=="xc7z020clg400-2","profile不同")
    extra=read(PRES[1]/"failed_root_preflight_and_correction.json")["extra_frozen_sources"]
    require(len(extra)==6 and set(extra)<=set(later) and len(set(later)-set(extra))==31,"static31+extra6关系不同")
    save(REPORT/"s4_collection_source_binding.json",{"status":"S4_SOURCE37_BEFORE_AFTER_IDENTICAL_GIT_F96_BOUND","source_commit":BASELINE,"source_before":binding(PRE/"source_before.json"),"source_after":binding(PRE/"source_after.json"),"source_count":37,"platform_static_source_count":31,"extra_test_oracle_sources":extra,"sources":sources,"git_raw_same_count":31,"exact_eol_count":6,"frozen14_unchanged":True,"frozen14_sha256":originals14,"source_freeze":binding(freeze),"observed_head_before":before["actual_head_at_check"],"observed_head_after":after["actual_head_at_check"],"live_source_consumed":False,"note":"source.path是历史标识符，哈希绑定snapshot/snapshot_after及Gitf96，不把旧SHA绑定到可变live路径。"})

    native_root=mkdir_new(REPORT/"native_jobs");run_root=exact(PROJECT/"s2b_inference_candidate.runs","directory")
    dirs=sorted(p for p in run_root.iterdir() if p.is_dir() and p.name!=".jobs")
    require(len(dirs)==5,"原生run不是5")
    mapping=[];jobs=[]
    for directory in dirs:
        exact(directory,"directory");target=mkdir_new(native_root/("wrapper_native_s4_r01" if directory.name=="synth_1" else directory.name))
        log=exact(directory/"runme.log").read_text(encoding="utf-8")
        require("synth_design completed successfully" in log and "0 Critical Warnings and 0 Errors encountered" in log,"综合未成功结束")
        require((directory/"__synthesis_is_complete__").is_file() and (directory/".vivado.end.rst").is_file() and not (directory/".vivado.error.rst").exists(),"结束marker错误")
        for p in sorted(directory.iterdir()):
            if p.is_file() and (p.suffix in (".tcl",".log",".jou",".xdc",".rpt",".rst",".js",".sh",".bat",".xml") or p.name in ("htr.txt","__synthesis_is_complete__")):
                mapping.append(rawcopy(p,target/p.name))
        begin=ET.fromstring(exact(directory/".vivado.begin.rst").read_bytes()).find("Process");require(begin is not None,"launcher记录缺失")
        elapsed=re.search(r"synth_design:.*?elapsed = (\d+):(\d+):(\d+)",log);require(elapsed,"耗时缺失")
        diag=re.findall(r"(\d+) Infos, (\d+) Warnings, (\d+) Critical Warnings and (\d+) Errors encountered",log);require(diag,"诊断数缺失")
        start=first(r"Start of session at:\s*([^\r\n]+)",log);end=first(r"Exiting Vivado at ([^\r\n]+)",log).removesuffix("...")
        session_seconds=(datetime.strptime(end,"%a %b %d %H:%M:%S %Y")-datetime.strptime(start,"%a %b %d %H:%M:%S %Y")).total_seconds()
        jobs.append({"run":directory.name,"saved_directory":rel(target),"status":"NATIVE_SYNTH_COMPLETED_LOG_AND_MARKERS","actual_vivado_job_pid":int(first(r"Process ID\s*:\s*(\d+)",log)),"launcher_pid_from_begin_rst":int(begin.attrib["Pid"]),"launcher_command":begin.attrib["Command"],"session_start_local":start,"session_end_local":end,"timezone_context":"UTC+8","session_wall_seconds_from_native_timestamps":session_seconds,"synth_design_elapsed_seconds":int(elapsed[1])*3600+int(elapsed[2])*60+int(elapsed[3]),"reported_single_process_peak_mb":max(map(float,re.findall(r"peak = ([0-9.]+)",log))),"peak_unit":"Vivado原日志MB口径，未换算为GiB或全进程树峰","final_diagnostics":dict(zip(("infos","warnings","critical_warnings","errors"),map(int,diag[-1]))),"raw_os_process_exit_code":None,"os_exit_code_reason":"OS子进程退出码未单独采集；完成依据native日志、marker及同次wait0，不伪填子进程0。"})
    infer=next(j for j in jobs if j["run"]=="s2b_inference_infer_0_synth_1")
    require(infer["synth_design_elapsed_seconds"]==183 and infer["reported_single_process_peak_mb"]==2240.094 and infer["final_diagnostics"]["warnings"]==118,"核心指标不同")
    tcl=(native_root/"s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl").read_text(encoding="utf-8")
    block=first(r"read_verilog -library xil_defaultlib -sv \{([^}]+)\}",tcl)
    compiled=[Path(line.strip()).relative_to(ROOT).as_posix() for line in block.splitlines() if line.strip()]
    require(len(compiled)==len(set(compiled))==18 and set(compiled)==set(profile["rtl_sources"]) and set(compiled)<=set(later),"实际18源不同")
    require("synth_design -top s2b_inference_infer_0 -part xc7z020clg400-2" in tcl,"top/part不同")
    generated=mkdir_new(REPORT/"generated_inputs")
    generated_root=exact(PROJECT/"s2b_inference_candidate.gen/sources_1/bd/s2b_inference","directory")
    constraints=sorted(generated_root.rglob("*.xdc"))
    require(len(constraints)==5,"实际生成XDC数不同")
    constraints+=sorted(run_root.rglob("*_propImpl.xdc"))
    require(len(constraints)==7,"实际传播XDC数不同")
    for p in constraints:mapping.append(rawcopy(p,generated/p.name))
    imported=exact(PROJECT/"s2b_inference_candidate.srcs/sources_1/imports/hdl/s2b_inference_wrapper.v")
    generated_wrapper=exact(generated_root/"hdl/s2b_inference_wrapper.v")
    require(sha(imported)==sha(generated_wrapper),"最终import/generated wrapper不同")
    wrapper_map=rawcopy(imported,generated/imported.name);mapping.append(wrapper_map)
    for p in (exact(generated_root/"synth/s2b_inference.v"),exact(generated_root/"ip/s2b_inference_infer_0/synth/s2b_inference_infer_0.sv")):
        mapping.append(rawcopy(p,generated/p.name))
    wrapper_tcl=(native_root/"wrapper_native_s4_r01/s2b_inference_wrapper.tcl").read_text(encoding="utf-8")
    require(imported.as_posix() in wrapper_tcl,"wrapper实际编译路径缺失")
    save(REPORT/"s4_collection_native_mapping.json",{"files":mapping,"jobs":jobs,"native_job_count":5,"native_raw_copy_count":len(mapping),"actual_compiled_rtl_sources":compiled,"actual_compiled_source_count":18,"actual_compiled_source_snapshots":[{"source_identifier":name,"source_snapshot":later[name]["snapshot"],"sha256":later[name]["sha256"]} for name in compiled],"source_binding":rel(REPORT/"s4_collection_source_binding.json"),"wrapper_import":wrapper_map,"wrapper_generated_original":binding(generated_wrapper),"generated_wrapper_raw_equals_imported":True,"process_tree_peak_memory_bytes":None,"dcp_cache_copied":False,"root_project_or_sources_moved":False,"excluded_cache_policy":"DCP/VDS/PB/WDF及整个临时工程不复制；保留可重建的BD、Tcl、原生脚本、日志、生成约束和wrapper。"})

    raw=read(PRE/"root_mcp_calls_with_history.json")
    history=[h for c in raw["history"]["content"] if c["type"]=="text" for h in json.loads(c["text"]).get("history",[])]
    selected=[h for h in history if 86<=h["id"]<=94]
    require([h["id"] for h in selected]==list(range(86,95)) and len(raw["calls"])==9,"history86–94缺失")
    paired=[]
    for call,h in zip(raw["calls"],selected):
        require(call["command"]==h["command"],"MCP/native command不同")
        result=json.loads(call["result"]["content"][0]["text"])
        require(not call["result"].get("isError",False) and result["exit_code"]==h["code"],"MCP/native code不同")
        paired.append({"label":call["label"],"native_history":h,"client_result":call["result"]})
    by_id={h["id"]:h for h in selected}
    require((by_id[87]["code"],by_id[87]["elapsed"],by_id[90]["code"],by_id[90]["elapsed"],by_id[91]["elapsed"],by_id[92]["elapsed"],by_id[93]["elapsed"],by_id[94]["code"])==(1,24.06,0,271.383,18.529,29.896,1.108,0),"关键native码/耗时不同")
    require("source_count 18 wrapper_count 1" in by_id[88]["output"] and "part xc7z020clg400-2 visibility 0" in by_id[88]["output"],"源查询不同")
    states=by_id[93]["output"]
    require("clock_period 20.000" in states and states.count("status {synth_design Complete!} progress 100%")==5 and states.count("status {Not started} progress 0%")==5,"五synth/五impl状态不同")
    require("[Sun Oct 11 17:22:06 2026] Launched synth_1" in by_id[89]["output"] and "[Sun Oct 11 17:28:21 2026] synth_1 finished" in by_id[90]["output"],"整次launch/end不同")
    products=(REPORT/"products.tcldict").read_text(encoding="utf-8")
    require("status FAIL code 0 raw PRODUCTS:OK" in products and "WARNING emitted=-8 exported=2" in products and "native_counts_before {WARNING 9" in products and "native_counts_after {WARNING 1" in products,"products原失败不同")
    save(REPORT/"s4_collection_mcp_history_binding.json",{"status":"S4_CLOSED_HISTORY86_TO94_BOUND_CLIENT_NATIVE_RESULTS","source_record":binding(PRE/"root_mcp_calls_with_history.json"),"session_id":raw["session_id"],"paired_calls":paired,"mcp_execute_calls_in_s4_segment":9,"excluded_prior_history_ids":[h["id"] for h in history if h["id"]<86],"wait_client_status":"RETURNED_NATIVE_EXIT0","mcp_wait_timeout":False,"wait_native_exit_code":0,"wait_native_elapsed_seconds":271.383,"launch_timestamp_local":"2026-10-11T17:22:06+08:00","finished_timestamp_local":"2026-10-11T17:28:21+08:00","launch_to_finished_wall_seconds":375,"wall_resolution_seconds":1,"whole_builder_native_exit_code":1,"whole_builder_native_elapsed_seconds":24.06,"products_native_exit_code":0,"products_capture_exit_code":1,"products_warning_counter_before":9,"products_warning_counter_after":1,"products_warning_emitted_delta":-8,"products_warning_exported_count":2,"products_repeated":False,"implementation_strategy_list_only":states.split(" impl_strategies ",1)[1],"implementation_started":False,"root_session_cumulative_peak_mb":2691.660,"root_session_peak_is_s4_run_peak":False,"process_tree_peak_memory_bytes":None,"all_host_or_tool_call_count":None,"all_host_or_tool_call_count_reason":"只知封闭S4段9次MCP执行，未测全host/工具调用总数。"})

    classifier=run_closed([sys.executable,"-B",str(CACHE/"classify_s4_sta.py"),"--report",str(REPORT/"timing_summary_synth.rpt"),"--result",str(REPORT/"s4_collection_sta_result.json")],"s4_collection_sta")
    require(classifier["native_exit_code"]==2,"STA分类真实应为2");copy_closed_record("s4_collection_sta")
    sta=read(REPORT/"s4_collection_sta_result.json");timing=sta["timing"]
    require(timing["wns_ns"]==-21.981 and timing["tns_ns"]==-5506.339 and timing["setup_failing_endpoints"]==759 and timing["setup_total_endpoints"]==14655 and timing["whs_ns"]==0.037 and timing["ths_ns"]==0 and timing["wpws_ns"]==8.870 and timing["tpws_ns"]==0 and not any(sta["check_timing"].values()),"STA原数值不同")
    util=(REPORT/"utilization_flat_synth.rpt").read_text(encoding="utf-8")
    resources={k:int(first(r"^\|\s*"+re.escape(label)+r"\s*\|\s*(\d+)\s*\|",util)) for k,label in (("lut","Slice LUTs*"),("ff","Slice Registers"),("bram","Block RAM Tile"),("dsp","DSPs"),("latch","Register as Latch"))}
    require(resources=={"lut":29904,"ff":4006,"bram":32,"dsp":166,"latch":0},"资源原数值不同")
    worst=(REPORT/"timing_worst_synth.rpt").read_text(encoding="utf-8")
    w={"source":first(r"^\s*Source:\s*(\S+)",worst),"destination":first(r"^\s*Destination:\s*(\S+)",worst),"logic_levels":int(first(r"^\s*Logic Levels:\s*(\d+)",worst)),"carry4":int(first(r"^\s*Logic Levels:.*?CARRY4=(\d+)",worst)),"dsp48e1":int(first(r"^\s*Logic Levels:.*?DSP48E1=(\d+)",worst)),"data_path_delay_ns":float(first(r"^\s*Data Path Delay:\s*([\d.]+)ns",worst)),"logic_delay_ns":float(first(r"^\s*Data Path Delay:.*?logic ([\d.]+)ns",worst)),"route_delay_ns":float(first(r"^\s*Data Path Delay:.*?route ([\d.]+)ns",worst)),"reported_logic_resource":"full_tile_patch_bytes_wide3"}
    require(w["source"].endswith("u_conv_engine/output_width_latched_reg[7]/C") and w["destination"].endswith("u_conv_engine/result_error_latched_reg[0]/D") and (w["logic_levels"],w["carry4"],w["dsp48e1"],w["data_path_delay_ns"],w["logic_delay_ns"],w["route_delay_ns"])==(74,43,2,41.577,24.053,17.524) and "full_tile_patch_bytes_wide3" in worst,"最坏路径不同")
    xdc=(REPORT/"constraints_synth.xdc").read_text(encoding="utf-8")
    exceptions=re.findall(r"current_instance ([^\r\n]+)\r?\n(set_false_path[^\r\n]+)",xdc)
    require(len(exceptions)==2 and all("rst_fclk0/U0/EXT_LPF/" in scope and "syncstages_ff_reg[0]" in command for scope,command in exceptions),"resetCDC两例外不同")
    require("No valid timing exceptions found." in (REPORT/"exceptions_synth.rpt").read_text(encoding="utf-8"),"原exceptions文字不同")
    save(REPORT/"s4_collection_constraints_binding.json",{"clock":{"name":"clk_fpga_0","period_ns":20.0,"frequency_mhz":50,"input_jitter_ns":0.6},"check_timing":sta["check_timing"],"exported_reset_cdc_false_paths":[{"scope":scope,"command":command} for scope,command in exceptions],"exported_false_path_count":2,"report_exceptions_raw_statement":"No valid timing exceptions found.","interpretation":"report_exceptions本次文字与write_xdc两个scoped reset同步器false_path分别保留；不能据报告文字宣称零例外。无内部漏约束仅指本次check_timing计数为0。","constraint_artifact":binding(REPORT/"constraints_synth.xdc")})

    old_xsa=exact(ROOT/"report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa");new_xsa=exact(REPORT/"s2b_inference_no_bit.xsa")
    members=[]
    with zipfile.ZipFile(old_xsa) as a,zipfile.ZipFile(new_xsa) as b:
        require(not any(n.endswith(".bit") for n in b.namelist()),"XSA意外包含bit")
        for name in ("ps7_init.c","ps7_init.h","ps7_init.html","ps7_init.tcl","ps7_init_gpl.c","ps7_init_gpl.h","s2b_inference.hwh"):
            x=a.read(name);y=b.read(name);require(zlib.crc32(x)==a.getinfo(name).CRC and zlib.crc32(y)==b.getinfo(name).CRC,"XSA成员CRC错误")
            members.append({"member":name,"old_sha256":hashlib.sha256(x).hexdigest(),"new_sha256":hashlib.sha256(y).hexdigest(),"old_bytes":len(x),"new_bytes":len(y),"raw_equal":x==y,"old_crc32":a.getinfo(name).CRC,"new_crc32":b.getinfo(name).CRC})
    require(all(r["raw_equal"] for r in members[:6]) and not members[6]["raw_equal"],"实际PSinit/HWH关系不同")
    save(REPORT/"s4_collection_xsa_member_comparison.json",{"status":"SIX_PSINIT_BYTES_SAME_HWH_CHANGED_NO_BIT","old_xsa":binding(old_xsa),"new_xsa":binding(new_xsa),"members":members,"elf_runtime_compatibility":"NOT_APPROVED","note":"字节比对只说明这些成员，不能批准旧BSP/ELF与S4整个平台兼容，未下载。"})
    blob,checker_command,checker_code=git_blob("verification/check_stage_delivery.py")
    checker=REPORT/"s4_collection_stage_checker_snapshot.py"
    require(not checker.exists(),"checker快照已有")
    with checker.open("xb") as out:out.write(blob)
    save(REPORT/"s4_collection_stage_checker_binding.json",{"source_commit":BASELINE,"original_identifier":"verification/check_stage_delivery.py","snapshot":binding(checker),"git_native_command":checker_command,"git_native_exit_code":checker_code,"live_checker_consumed":False})

    interface_source=exact(ROOT/"report/evidence/S2B-T17/s3_platform_20261011_r01/s3_collection_delivery_manifest_r03.json")
    interfaces=read(interface_source)["interfaces"]
    for interface in interfaces:require(sha(ROOT/interface["path"])==interface["sha256"],"正式接口文档漂移")
    externals=[freeze,old_xsa,interface_source]
    limitations=["本项仅封装S4实际综合失败证据；STA真实FAIL_TIMING，独立准确性审查由总控另行执行，G3/G4/G5未通过。","f96源码37项before/after快照相同，static31+6测试/oracle；31Git RAW相同、6精确LF→CRLF关系，实际编译18且原14冻结源不变。live S5源码不消费。","整builder原生1/24.06秒，products原生0但WARNING9→1/capture1；原FAIL保留且不重跑products。","同次wait原生0/271.383秒，MCP本次没有timeout；launch17:22:06到finished17:28:21约375秒，与wait耗时分别记录。","五job实际Vivado PID与begin.rst launcher PID分开，子进程OS退出码未直接测量；infer183秒/单进程峰2240.094MB/118warning，root累计2691.660MB不当本run峰，全tree峰未测。","50MHz综合态WNS−21.981/TNS−5506.339，759/14655setup失败；74逻辑层/43CARRY4/2DSP路径位于CONV full_tile_patch_bytes宽校验。","无内部漏约束仅指check_timing计数；保留两个scoped resetCDC false_path与report_exceptions本次No valid文字，不声明零例外。","前置r01期望33/r02期望34失败原件保留；r01元数据误报actual34由r02明确纠正actual31，37冻结闭包不能混写static计数。两次记录1且inner码未单独测量，r03真正前后快照及哈希保留。","未复制DCP/VDS/PB/WDF、未搬全工程；source路径仅历史标识，快照和Git对象构成来源绑定。","六PSinit成员相同而HWH变化不批准旧BSP/ELF整体兼容；无bit的XSA不等于部署包；物理接口候选0.1.1未冻结。","实现策略只有实际查询列表，五impl均Not started；impl/postroute/bit/cache/model/109/1000次/BOARD均NOT_RUN。","只知封闭段9次MCP执行，全部host/tool调用数、Collector峰及全进程树峰未测；包装CHECKS_OK不表示时序或阶段通过。"]
    summary={"status":"COLLECTED_S4_FAIL_TIMING_PENDING_INDEPENDENT_EVIDENCE_REVIEW","source_commit":BASELINE,"source_count":37,"platform_static_source_count":31,"extra_test_oracle_count":6,"compiled_rtl_count":18,"profile_version":profile["version"],"visibility":0,"original_raw_file_count":len(inventories),"original_directory_counts":counts,"original_raw_unchanged":True,"native_raw_copy_count":len(mapping),"native_job_count":5,"native_wait_exit_code":0,"native_wait_elapsed_seconds":271.383,"mcp_wait_timeout":False,"launch_to_finished_wall_seconds":375,"native_report_exit_code":0,"native_report_elapsed_seconds":29.896,"native_classifier_exit_code":2,"timing":timing,"check_timing":sta["check_timing"],"resources":resources,"worst_path":w,"exported_reset_cdc_false_path_count":2,"external_inputs":[binding(p) for p in externals],"preflight_r01_reported_exit":1,"preflight_r02_reported_exit":1,"preflight_inner_exit_separately_measured":False,"preflight_r01_actual34_metadata_superseded_by_r02_actual31":True,"preflight_before_after_script_reported_exit_code":0,"preflight_r03_exit_note":"前后实际0为总控传回执行事实；原r03未独立保存native进程receipt，快照JSON及原driver仍保留，未在Collector重跑。","mcp_calls_in_closed_s4_segment":9,"process_tree_peak_memory_bytes":None,"collector_peak_memory_bytes":None,"limitations":limitations,"created_at_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),"collector_elapsed_so_far_seconds":time.monotonic()-started}
    save(REPORT/"s4_collection_summary.json",summary)
    checks=[{"name":"S4冻结37快照及Gitf96核验","status":"PASS","command":" ".join(sources[0]["git_native_command"]),"exit_code":0,"reason":"第一条真实Git命令；其余36条命令/退出码及快照字节在source_binding，原14同SHA。"},{"name":"五个原生综合完成","status":"PASS","command":by_id[90]["command"],"exit_code":0,"reason":"history90 wait271.383秒，本次MCP无timeout；native日志及结束marker逐项绑定。"},{"name":"实际STA报告生成","status":"PASS","command":by_id[92]["command"],"exit_code":0},{"name":"50MHz综合态STA分类","status":"FAIL","command":" ".join(classifier["command"]),"exit_code":2,"reason":"WNS−21.981/TNS−5506.339，759/14655 setup失败，综合态非postroute。"},{"name":"builder和products capture原失败","status":"FAIL","command":by_id[87]["command"],"exit_code":1,"reason":"builder1，products native0/capture1，WARNING9→1；失败原件未覆盖。"}]
    first_collector=read(REPORT/"s4_collection_collector.native.json")
    require(first_collector["native_exit_code"]==1,"首轮失败码不同")
    checks.append({"name":"首Collector生成文件扩展名门禁失败","status":"FAIL","command":" ".join(first_collector["command"]),"exit_code":1,"reason":"首轮预设infer生成文件.v不存在，路径门禁原生1；真实只读枚举为.sv，新脚本封装对应原件，不覆盖首轮脚本/日志/失败JSON，不重跑综合。"})
    for number in (1,2):
        record=read(PRES[number-1]/("failed_root_preflight.json" if number==1 else "failed_root_preflight_and_correction.json"))
        checks.append({"name":f"前置r0{number}计数断言原失败","status":"FAIL","command":record["command"],"exit_code":record["exec_command_exit_code"],"reason":"原exec_command记录1，inner码未单独测量；期望计数错误，r02纠正static实际31，原34错误record保留。"})
    for name in ("独立证据准确性审查","实现及postroute","bitstream生成","板上cache probe","板上模型及109样本","1000次板上任务","BOARD及G3验收"):
        checks.append({"name":name,"status":"NOT_RUN","command":None,"exit_code":None,"reason":"本Collector仅封装关闭的失败综合原件，未执行该项；不得继承为通过。"})
    manifest={"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":"s4_platform_20261011_r01","source_commit":BASELINE,"evidence_dir":rel(REPORT),"interfaces":interfaces,"tool_versions":{"python":sys.version,"Vivado":"2026.1 Build6511674 原报告/日志","part":profile["vivado_part"],"profile":profile["version"]},"files":manifest_files(externals),"checks":checks,"limitations":limitations}
    manifest_path=REPORT/"s4_collection_delivery_manifest_r01.json";save(manifest_path,manifest)
    results={}
    for mode in ("evidence","inputs"):
        results[mode]=run_closed([sys.executable,"-B",str(checker),"--mode",mode,"--manifest",str(manifest_path),"--project-root",str(ROOT)],"s4_collection_"+mode+"_r01")
    require({k:v["native_exit_code"] for k,v in results.items()}=={"evidence":0,"inputs":2},"r01检查原生码不同")
    for mode in results:copy_closed_record("s4_collection_"+mode+"_r01")
    save(REPORT/"s4_collection_packaging_r01.json",{"status":"EVIDENCE_PACKAGING_OK_INPUTS_ACTUAL_FAIL","checks":results,"policy":"evidence0只验证目录/hash包装；inputs2包含未冻结接口、实际FAIL和NOT_RUN，不改变阶段门禁。"})
    original_check()
    print(json.dumps({"status":summary["status"],"original_files":len(inventories),"native_copies":len(mapping),"source_count":37,"compiled_rtl_count":18,"codes":{"sta":2,"evidence":0,"inputs":2},"collector_elapsed_seconds":time.monotonic()-started},ensure_ascii=False))
except BaseException as error:
    failure=REPORT/"s4_collection_failure_r02.json"
    if not failure.exists():save(failure,{"status":"COLLECTOR_FAILURE_PRESERVED","error":repr(error),"elapsed_seconds":time.monotonic()-started})
    raise
