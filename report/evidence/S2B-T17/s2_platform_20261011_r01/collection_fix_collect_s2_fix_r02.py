"""S2已结束证据的轻量包装修复；不读取当前S3工程源，不运行Vivado。"""
from pathlib import Path
from datetime import datetime,timezone,timedelta
import hashlib
import json
import subprocess
import sys
import os
import re
import time

ROOT=Path(__file__).absolute().parents[4];CACHE=Path(__file__).absolute().parent
REPORT=ROOT/"report/evidence/S2B-T17/s2_platform_20261011_r01"
PREFLIGHT=ROOT/"report/evidence/S2B-T17/s2_source_preflight_20261011_r01"
BASELINE="5a676b700af4c27297977379417b1694dd64840e"
def require(condition,message):
    """冻结字节门禁，不用当前源码替代历史快照。"""
    if not condition:raise RuntimeError(message)
def sha(file):
    """流式hash，不复制DCP或大型模型。"""
    h=hashlib.sha256()
    with file.open("rb") as source:
        for block in iter(lambda:source.read(1048576),b""):h.update(block)
    return h.hexdigest()
def rel(file):return file.relative_to(ROOT).as_posix()
def read(file):return json.loads(file.read_text(encoding="utf-8"))
def save(file,value):
    """只创建新UTF8机器记录。"""
    require(file.parent.is_dir() and not file.exists(),"新输出名称已存在或父路径无效")
    with file.open("x",encoding="utf-8",newline="\n") as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write("\n")
def original_check():
    """仅核对本修复开始前146原件，不对历史活动日志强求旧emptySHA。"""
    items=read(REPORT/"collection_fix_original_inventory.json")["files"]
    for row in items:
        path=ROOT/row["path"]
        require(path.is_file() and path.stat().st_size==row["bytes"] and sha(path)==row["sha256"],"已结束原件漂移："+row["path"])
    return items
started=time.monotonic();require(REPORT.is_dir() and PREFLIGHT.is_dir() and CACHE.is_dir(),"授权目录无效")
original=original_check()
try:
    for source in (Path(__file__),CACHE/"classify_s2_sta.py",CACHE/"classify_s2_sta_r02.py"):
        target=REPORT/("collection_fix_"+source.name)
        if target.exists():require(sha(target)==sha(source),"已有脚本副本不同，不能覆盖")
        else:
            with target.open("xb") as out:out.write(source.read_bytes())
        require(sha(target)==sha(source),"Collector脚本rawcopy失败")
    history_root=read(REPORT/"root_mcp_calls_final.json")
    blocks=[json.loads(x["text"]) for x in history_root["history_after_reports"]["content"] if x["type"]=="text"]
    histories=[x for block in blocks for x in block.get("history",[])]
    s2=[x for x in histories if x["id"]>=67];waits=[x for x in s2 if x["command"].startswith("wait_on_run synth_1")]
    require(len(waits)==1 and waits[0]["id"]==72 and waits[0]["code"]==0 and waits[0]["elapsed"]==381.939,"本次S2 wait原生记录不符")
    old_waits=[x for x in histories if x["id"]<67 and x["command"].startswith("wait_on_run synth_1")]
    report_entries=[x for x in s2 if "report_timing_summary" in x["command"]]
    require(len(report_entries)==1 and report_entries[0]["code"]==0,"报告生成命令真实返回不是0")
    save(REPORT/"collection_fix_history_selection_r02.json",{"scope":"原history包含旧S1与本次S2，只选id>=67；未改变MCP客户端timeout","s2_wait":waits,"prior_wait_excluded":old_waits,"s2_report_entry":report_entries,"history_ids_original":[x["id"] for x in histories],"history_ids_s2":[x["id"] for x in s2]})
    before=read(PREFLIGHT/"source_before.json");after=read(REPORT/"source_after.json")
    require(before["source_commit"]==after["source_commit_at_build_start"]==after["source_commit_at_check"]==BASELINE and before["platform_version"]==after["platform_version"]=="0.1.2" and before["visibility"]==after["visibility"]==0 and before["sources"]==after["sources"] and len(before["sources"])==28,"S2源码28 before/after不符")
    root_binding=read(REPORT/"collector_source_binding.json");by_path={x["path"]:x for x in root_binding["sources"]};sources=[]
    for row in before["sources"]:
        snapshot=PREFLIGHT/"source_snapshot"/row["path"]
        require(snapshot.is_file() and sha(snapshot)==row["sha256"] and snapshot.stat().st_size==row["bytes"],"冻结S2快照损坏")
        command=["git","show",BASELINE+":"+row["path"]];proc=subprocess.run(command,cwd=ROOT,capture_output=True)
        require(proc.returncode==0,"Git5a blob不可读")
        blob=proc.stdout;raw=snapshot.read_bytes();same=blob==raw;crlf=not same and b"\r\n" not in blob and blob.replace(b"\n",b"\r\n")==raw
        require(same or crlf,"冻结S2 RAW与Git5a不符，非纯CRLF")
        git_sha=hashlib.sha256(blob).hexdigest();require(git_sha==by_path[row["path"]]["git_blob_sha256"],"既有Git绑定不符")
        sources.append({**row,"snapshot_path":rel(snapshot),"git_blob_sha256":git_sha,"git_native_exit_code":proc.returncode,"git_raw_same":same,"exact_git_lf_to_snapshot_crlf":crlf})
    save(REPORT/"collection_fix_source_recheck.json",{"source_commit":BASELINE,"status":"SOURCE28_SNAPSHOT_BEFORE_AFTER_GIT5A_RECHECKED","sources":sources,"current_s3_source_consumed":False,"crlf_note":"true只证明Git LF精确转换到当时compiled RAW，不声称RAW字节等于Gitblob。"})
    sta=read(REPORT/"collection_fix_sta_result_r02.json");sta_native=read(REPORT/"collection_fix_sta_native_r02.json");upstream_sta=read(REPORT/"collector_sta_classification.json")
    require(sta["status"]=="FAIL_TIMING" and sta["native_exit_code"]==sta_native["native_exit_code"]==2 and sta["timing"]==upstream_sta["timing"] and sta["check_timing"]==upstream_sta["check_timing"],"独立STA分类与原报告解析不符")
    utilization=(REPORT/"utilization_flat_synth.rpt").read_text(encoding="utf-8")
    resources={}
    for key,label in (("lut","Slice LUTs*"),("ff","Slice Registers"),("bram","Block RAM Tile"),("dsp","DSPs")):
        values=re.findall(r"^\|\s*"+re.escape(label)+r"\s*\|\s*(\d+)\s*\|",utilization,re.M);require(len(values)==1,"资源字段歧义")
        resources[key]=int(values[0])
    require(resources==upstream_sta["resources"],"资源原报告与root解析不符")
    worst=(REPORT/"timing_worst_synth.rpt").read_text(encoding="utf-8")
    def first(pattern):
        values=re.findall(pattern,worst,re.M);require(bool(values),"最坏路径字段缺失");return values[0].strip()
    worst_fields={"source":first(r"^\s*Source:\s*(\S+)"),"destination":first(r"^\s*Destination:\s*(\S+)"),"logic_levels":int(first(r"^\s*Logic Levels:\s*(\d+)")),"carry4":int(first(r"^\s*Logic Levels:.*?CARRY4=(\d+)")),"data_path_delay_ns":float(first(r"^\s*Data Path Delay:\s*([\d.]+)ns"))}
    require(worst_fields=={"source":upstream_sta["worst_source"],"destination":upstream_sta["worst_destination"],"logic_levels":upstream_sta["logic_levels"],"carry4":upstream_sta["carry4"],"data_path_delay_ns":upstream_sta["data_path_delay_ns"]},"最坏ROUTE路径原报告不符")
    exceptions=(REPORT/"exceptions_synth.rpt").read_text(encoding="utf-8");require("No valid timing exceptions found." in exceptions,"有效exceptions与原描述不同")
    inventories=[]
    for name in ("collector_original_inventory.json","collector_original_inventory_r02.json"):
        inventory=read(REPORT/name);differences=[]
        for path,record in inventory.items():
            actual=ROOT/path;current={"sha256":sha(actual),"bytes":actual.stat().st_size}
            if current!=record:differences.append({"path":path,"historical_binding":record,"current_closed_file_binding":current})
        if name=="collector_original_inventory.json":require(all(x["path"]==rel(REPORT/"collector_attempt_01.log") for x in differences),"首历史inventory有非活动stdout漂移")
        else:require(not differences,"r02已关闭原件绑定漂移")
        inventories.append({"path":rel(REPORT/name),"differences":differences})
    xsa=read(REPORT/"collector_xsa_member_comparison.json")
    require(len([x for x in xsa["members"] if x["raw_equal"]])==6,"六PSinit相同依据不符")
    external=[ROOT/xsa["old_xsa_path"],ROOT/"report/evidence/S2B-T15/full_build_20261011_r01/build_details.json"]
    require(sha(external[0])==xsa["old_xsa_sha256"],"external旧XSA漂移")
    limitations=["完整native综合wait0/381.939s与MCP300s客户端timeout分记；products生成native0但capture1/wholeplatform入口1保留，不把工具故障误判成RTL综合失败。","STA FAIL_TIMING由实际classifier原生2给出；原report命令实际0保持单独，不改为2。","首root Collector统计混入旧S1 wait导致native1，r02按id>=67恢复native0；原source/logs保留。","首本轮分类器CRLF表头解析失败native3为Collector输入解析缺陷；原source/result/stdout/stderr保留，r02实际分类原生2。","first_inventory里attempt01 emptySHA属当时活动stdout历史；最终已关闭字节单独绑定，不重写旧inventory。","S2快照+Git5a恢复来源；当前S3工程正在变更，本Collector不消费当前RTL/profile。","六PSinit字节相同但HWH变化，不批准旧ELF或runtime平台兼容；postroute/bit/G3均NOT_RUN。","DCP只引用既有ignored路径/SHA及用途，不复制、不作为长期冻结恢复依赖；五native_job原日志保持raw不转码。","综合全进程树峰值与精确总排队wall未知；只沿用各单进程原报告值，不能混加或声称同一测量。","轻量Collector峰值内存未测；未执行Vivado/ROSS/hardware/业务测试/提交。"]
    save(REPORT/"collection_fix_summary.json",{"status":"COLLECTED_FAIL_TIMING","source_commit":BASELINE,"original_raw_file_count":len(original),"original_raw_unchanged":True,"native_synthesis_wait":waits[0],"report_generation_native_exit_code":report_entries[0]["code"],"sta_classifier_native_exit_code":sta_native["native_exit_code"],"timing":sta["timing"],"check_timing":sta["check_timing"],"resources":resources,"worst_path":worst_fields,"no_valid_timing_exceptions":True,"historical_inventory_differences":inventories,"six_ps_init_same":"不等于ELF兼容批准","external_inputs":[{"path":rel(x),"sha256":sha(x)} for x in external],"old_root_manifest_checker":"NOT_RUN_旧清单FAIL字段使用report0不符合检查schema，保留原件不虚构checker失败码","collector_elapsed_seconds":time.monotonic()-started,"peak_memory_bytes":None,"timestamp_utc8":datetime.now(timezone(timedelta(hours=8))).isoformat(),"limitations":limitations})
    old_manifest=read(REPORT/"collector_delivery_manifest.json")
    checks=[{"name":"原件与S2冻结快照采集核验","status":"PASS","command":"python -B "+rel(Path(__file__).absolute()),"exit_code":0},
            {"name":"本次native综合完成","status":"PASS","command":waits[0]["command"],"exit_code":waits[0]["code"],"reason":"实际history72耗时381.939；旧S1wait62排除，MCPtimeout另存。"},
            {"name":"STA报告生成","status":"PASS","command":report_entries[0]["command"],"exit_code":report_entries[0]["code"]},
            {"name":"50MHz综合STA独立分类","status":"FAIL","command":" ".join(sta_native["command"]),"exit_code":sta_native["native_exit_code"],"reason":"WNS−62.174/TNS−12041.195，811setup端点失败；时序FAIL不等于report命令失败。"},
            {"name":"products入口capture原失败","status":"FAIL","command":"::s2b_inference_platform::run","exit_code":1,"reason":"原products native0/capture1、wholeplatform入口1；原记录保留。"},
            {"name":"首本轮分类器输入解析失败原件","status":"FAIL","command":" ".join(read(REPORT/"collection_fix_sta_native.json")["command"]),"exit_code":3,"reason":"CRLF表头解析；旧结果不重写，r02真实分类2。"},
            {"name":"实现/位流/实板","status":"NOT_RUN","command":None,"exit_code":None,"reason":"综合时序未满足，未实现/下载/实板。"}]
    def make_manifest():
        """绑定两个已结束Run所有原件，使用快照而非变化中的工程源。"""
        files=[]
        for directory in (REPORT,PREFLIGHT):
            for path in sorted(directory.rglob("*")):
                if not path.is_file():continue
                role="source" if path.suffix in (".py",".sv",".v",".tcl",".xdc") else "log" if path.suffix in (".log",".rpt") else "artifact" if path.suffix in (".xsa",".bd",".rst","") else "result"
                if path==PREFLIGHT/"source_before.json":role="input"
                files.append({"path":rel(path),"sha256":sha(path),"role":role})
        for path in external:files.append({"path":rel(path),"sha256":sha(path),"role":"input"})
        path=ROOT/"verification/check_stage_delivery.py";files.append({"path":rel(path),"sha256":sha(path),"role":"source"})
        return {"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":REPORT.name,"source_commit":BASELINE,"evidence_dir":rel(REPORT),"interfaces":old_manifest["interfaces"],"files":files,"checks":checks,"tool_versions":{"python":sys.version,"vivado":"2026.1 Build6511674 原综合report，只读解析，无新调用"},"limitations":limitations}
    original_check();save(REPORT/"collection_fix_delivery_manifest_r02.json",make_manifest());codes={}
    for mode in ("evidence","inputs"):
        command=[sys.executable,"-B",str(ROOT/"verification/check_stage_delivery.py"),"--mode",mode,"--manifest",str(REPORT/"collection_fix_delivery_manifest_r02.json")]
        proc=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=30,env=dict(os.environ,PYTHONIOENCODING="utf-8"));path=REPORT/("collection_fix_"+mode+"_probe.log");require(not path.exists(),"新checker日志已存在")
        with path.open("xb") as out:out.write(proc.stdout);out.write(proc.stderr)
        codes[mode]={"command":command,"native_exit_code":proc.returncode}
    save(REPORT/"collection_fix_packaging_probe.json",{"checks":codes,"scope":"包装检查不能代表STA/G2/G3；classifier实际2保留。"})
    original_check();print(json.dumps({"status":"COLLECTED_FAIL_TIMING","source_count":len(sources),"source_raw_same_git":sum(x["git_raw_same"] for x in sources),"source_crlf_only":sum(x["exact_git_lf_to_snapshot_crlf"] for x in sources),"native_sta":2,"probe_checker":codes,"original_raw_unchanged":True},ensure_ascii=False))
    require({k:v["native_exit_code"] for k,v in codes.items()}=={"evidence":0,"inputs":2},"包装probe退出码不符")
except BaseException as error:
    file=REPORT/"collection_fix_collector_failure_r02.json"
    if not file.exists():save(file,{"status":"FAIL_COLLECTOR_PRESERVED","error":repr(error),"business_failure":False})
    raise
