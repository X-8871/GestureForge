"""采集 S1 已结束综合的只读原件，只新增本轮 collector 文件及清单。"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import time
import zipfile
import zlib
from datetime import datetime, timezone, timedelta

ROOT = Path.cwd().resolve()
RUN = ROOT / "report/evidence/S2B-T17/s1_platform_20261011_r01"
TMP = Path(__file__).resolve().parent
PROJECT = ROOT / "tmp/2B/S2B-T17/s1p1"
BASELINE = "6d00ff2d05e92fa6cff05243fb620f8a0232b9f1"
started = time.monotonic()
new_files = []
commands = []

def sha(path):
    """流式记录原始字节哈希。"""
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()

def read(path):
    """以 UTF-8 读取机器记录。"""
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(name, value):
    """只创建精确新文件，拒绝覆盖所有已有原件。"""
    path = RUN / name
    assert path.parent.is_dir(), str(path)
    if path.exists():
        assert path.is_file() and read(path) == value, str(path)
        return path
    with path.open("x", encoding="utf-8", newline="\n") as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write("\n")
    new_files.append(path)
    return path

def copy_once(source, target):
    """原始字节副本保存，不改写来源。"""
    assert source.is_file() and target.parent.is_dir()
    if target.exists():
        assert target.is_file() and sha(source) == sha(target)
        return
    with source.open("rb") as incoming, target.open("xb") as outgoing:
        for block in iter(lambda: incoming.read(1048576), b""):
            outgoing.write(block)
    assert sha(source) == sha(target)
    new_files.append(target)

assert RUN.is_dir() and PROJECT.is_dir() and TMP.is_dir()
original = read(RUN / "collector_original_inventory.json")["root_files_before_collection"] if (RUN / "collector_original_inventory.json").is_file() else {str(p.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha(p), "bytes": p.stat().st_size} for p in RUN.rglob("*") if p.is_file() and p.name != "collector_classify_sta.py"}
assert all(not Path(p).name.startswith("collector_") and Path(p).name != "delivery_manifest.json" for p in original)
old_inventory_path = ROOT / "report/evidence/S2B-T17/full_synthesis_20261011_r01/original_inventory.json"
old_inventory = read(old_inventory_path)
assert len(old_inventory) == 34
assert all((ROOT / p).is_file() and sha(ROOT / p) == digest for p, digest in old_inventory.items())
write_json("collector_original_inventory.json", {"root_files_before_collection": original, "previous_run_original_34_inventory_path": str(old_inventory_path), "previous_run_original_34_inventory_sha256": sha(old_inventory_path), "previous_run_original_34_checked": True, "previous_run_original_34": old_inventory})
before = read(RUN / "source_before.json")
after = read(RUN / "source_after.json")
assert before["source_commit"] == BASELINE and before["sources"] == after["sources"] and len(before["sources"]) == 28
source_rows = []
for row in before["sources"]:
    snapshot = RUN / "source_snapshot" / row["path"]
    assert snapshot.is_file() and sha(snapshot) == row["sha256"] and snapshot.stat().st_size == row["bytes"]
    blob = subprocess.run(["git", "show", BASELINE + ":" + row["path"]], cwd=ROOT, capture_output=True)
    assert blob.returncode == 0
    data = snapshot.read_bytes()
    raw_same = data == blob.stdout
    eol_only = b"\r\n" not in blob.stdout and blob.stdout.replace(b"\n", b"\r\n") == data
    assert raw_same or eol_only, row["path"]
    source_rows.append({**row, "snapshot_path": str(snapshot.relative_to(ROOT)).replace("\\", "/"), "git_blob_sha256": hashlib.sha256(blob.stdout).hexdigest(), "git_native_exit_code": blob.returncode, "git_raw_same": raw_same, "exact_git_lf_to_snapshot_crlf": eol_only})
write_json("collector_source_binding.json", {"source_commit": BASELINE, "status": "RAW_SNAPSHOTS_BEFORE_AFTER_IDENTICAL_AND_GIT_ORIGIN_BOUND", "source_count":28, "current_workspace_source_consumed": False, "current_source_may_be_S2": True, "files":source_rows, "git_raw_same_count":sum(r["git_raw_same"] for r in source_rows), "eol_only_paths":[r["path"] for r in source_rows if not r["git_raw_same"]]})

native_dir = RUN / "native_jobs"
assert not native_dir.exists() or native_dir.is_dir()
native_dir.mkdir(exist_ok=True)
native_map = []
jobs = []
dcp_refs = []
run_root = PROJECT / "s2b_inference_candidate.runs"
for directory in sorted(p for p in run_root.iterdir() if p.is_dir() and p.name != ".jobs"):
    name = "wrapper_native_r01" if directory.name == "synth_1" else directory.name
    destination = native_dir / name
    assert not destination.exists() or destination.is_dir()
    destination.mkdir(exist_ok=True)
    saved = []
    for source in sorted(directory.iterdir()):
        if not source.is_file():
            continue
        if source.suffix in {".tcl", ".log", ".jou", ".xdc", ".rpt"} or source.name in {".vivado.begin.rst", ".vivado.end.rst", ".vivado.error.rst", "__synthesis_is_complete__", ".Vivado_Synthesis.queue.rst"}:
            target = destination / source.name
            copy_once(source, target)
            native_map.append({"original_path": str(source), "saved_path": str(target.relative_to(ROOT)).replace("\\", "/"), "sha256":sha(target), "bytes":target.stat().st_size})
            saved.append(target.name)
        elif source.suffix == ".dcp":
            dcp_refs.append({"path":str(source), "sha256":sha(source), "bytes":source.stat().st_size, "permanent_artifact":False, "scope":"可重建 ignored 缓存引用，未复制；不作为长期独立恢复承诺"})
    log = (directory / "runme.log").read_text(encoding="utf-8")
    assert "synth_design completed successfully" in log and "0 Critical Warnings and 0 Errors encountered" in log
    assert "__synthesis_is_complete__" in saved and ".vivado.end.rst" in saved and ".vivado.error.rst" not in saved
    timing = re.search(r"synth_design:.*?elapsed = (\d+):(\d+):(\d+).*?peak = ([0-9.]+)",log)
    seconds = sum(int(timing[i]) * scale for i, scale in [(1,3600),(2,60),(3,1)])
    jobs.append({"run":directory.name, "saved_directory":name, "status":"NATIVE_SYNTH_COMPLETED_LOG_AND_MARKERS", "raw_process_exit_code":None, "raw_process_exit_reason":"未观察子进程OS退出码，仅记录真实日志、markers及wait原生code0。", "pid":int(re.search(r"Process ID\s*:\s*(\d+)",log)[1]), "synth_design_elapsed_seconds":seconds, "single_process_reported_peak_mb":max(map(float,re.findall(r"peak = ([0-9.]+)",log))), "native_exit_line":log.splitlines()[-1], "native_command_line":next(line for line in log.splitlines() if "Command line" in line), "saved_file_names":saved})
assert len(jobs) == 5
profile = read(RUN / "source_snapshot/board/s2b_inference_platform.json")
infer_tcl = (native_dir / "s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl").read_text(encoding="utf-8")
block = re.search(r"read_verilog -library xil_defaultlib -sv \{([^}]+)\}",infer_tcl)[1]
rtl_inputs = [Path(line.strip()).relative_to(ROOT).as_posix() for line in block.splitlines() if line.strip()]
assert set(rtl_inputs) == set(profile["rtl_sources"]) and len(rtl_inputs) == 18
write_json("collector_native_archive_mapping.json", {"files":native_map, "jobs":jobs, "native_rtl_inputs":rtl_inputs, "dcp_references":dcp_refs, "process_tree_peak_memory":"NOT_MEASURED", "aggregate_wall_time":"NOT_MEASURED", "resource_policy":"各job耗时及单进程峰值分别保留，不混加；wait时长为调用自身观测。"})

raw_path = RUN / "root_mcp_calls.json"
assert sha(raw_path) == "ef4b446ad61340859d9253b78da475bededa63ad9c69d2bb5e45a0db327953e1"
raw = read(raw_path)
history = json.loads(raw["history"]["content"][0]["text"])["history"]
assert [r["id"] for r in history] == list(range(55,65))
wait = next(r for r in history if r["command"] == "wait_on_run synth_1")
assert wait["code"] == 0 and wait["elapsed"] == 0.046
additional_path = RUN / "root_additional_reports_call.json"
assert sha(additional_path) == "c8fdcd7680e7ff4762b4d48f073aaa767aa6dc7bd8ba509d09391424b059b736"
additional = json.loads(read(additional_path)["content"][0]["text"])
assert additional["exit_code"] == 0 and additional["elapsed_seconds"] == 5.033
products = (RUN / "products.tcldict").read_text(encoding="utf-8")
assert "status FAIL code 0" in products and "native_counts_before {WARNING 9" in products and "native_counts_after {WARNING 1" in products
root_log = ROOT / "tmp/2B/S2B-T14/jtag_readonly_20261011_r01/.vivado-ai/vivado_94331856_49ab2ff7.log"
assert root_log.is_file()
log_snapshot = RUN / "collector_root_session_log_snapshot.log"
snapshot_time = datetime.fromtimestamp(log_snapshot.stat().st_mtime,timezone(timedelta(hours=8))).isoformat() if log_snapshot.exists() else datetime.now(timezone(timedelta(hours=8))).isoformat()
if log_snapshot.exists():
    assert log_snapshot.is_file() and root_log.read_bytes()[:log_snapshot.stat().st_size] == log_snapshot.read_bytes()
else:
    copy_once(root_log, log_snapshot)
write_json("collector_mcp_classification.json", {"raw_path":str(raw_path.relative_to(ROOT)).replace("\\", "/"), "raw_sha256":sha(raw_path), "raw_history_ids":[r["id"] for r in history], "old_raw_array_unchanged":True, "calls":len(raw["calls"]), "history":[{k:r[k] for k in ["id","command","code","elapsed","timestamp"]} for r in history], "additional_report_capture":{"path":str(additional_path.relative_to(ROOT)).replace("\\", "/"), "sha256":sha(additional_path), "native_exit_code":additional["exit_code"], "elapsed_seconds":additional["elapsed_seconds"], "history_id":None, "history_id_reason":"独立capture不携带id，root声明对应65；旧history实际止于64，不捏造补写。"}, "products_native_exit_code":0, "products_capture_exit_code":1, "products_capture_status":"FAIL_PRESERVED", "warning_counter_before":9, "warning_counter_after":1, "wait_native_exit_code":wait["code"], "wait_native_elapsed_seconds":wait["elapsed"], "wait_timestamp":wait["timestamp"], "wait_is_not_synthesis_wall_runtime":True, "root_session_log":{"original_path":str(root_log), "snapshot_path":str(log_snapshot.relative_to(ROOT)).replace("\\", "/"), "snapshot_sha256":sha(log_snapshot), "snapshot_bytes":log_snapshot.stat().st_size, "snapshot_time_utc8":snapshot_time, "byte_window":[0,log_snapshot.stat().st_size], "s1_history_time_window":[history[0]["timestamp"],history[-1]["timestamp"]], "scope":"追加日志在采集时保存全部前缀；含本会话此前记录，S1归属依据55至64history和独立additional capture。后续追加不改变此快照。"}, "root_session_reported_cumulative_peak_mb":max(map(float,re.findall(rb"peak = ([0-9.]+)",log_snapshot.read_bytes()))), "process_tree_peak_memory":"NOT_MEASURED", "limitations":["此前UTF8重载/globalUTF8与unique imported wrapper以实际原history绑定，不重跑products。", "root追加日志含非UTF8旧字节，原RAW不改写；仅以ASCII字节正则提取数值。", "root累计峰值不是此次全进程树峰值，未测总墙钟时间。"]})
write_json("collector_failure_r01.json", {"status":"FAIL_COLLECTION_UTF8_LOG_PARSE", "native_exit_code":1, "failure_log_path":"report/evidence/S2B-T17/s1_platform_20261011_r01/collector_failure_r01.log", "failure_log_sha256":sha(RUN / "collector_failure_r01.log"), "first_attempt_script_sha256":sha(RUN / "collector_attempt_r01.py"), "error":"UnicodeDecodeError: 0xc3 at offset33266 in raw root session log", "recovery":"保留旧原件和首轮采集新增文件；恢复时先核对既有文件字节，原追加日志仅以ASCII字节正则提取数值，不转码原件。"})

timing_path = RUN / "timing_summary_synth.rpt"
util_path = RUN / "utilization_flat_synth.rpt"
timing = timing_path.read_text(encoding="utf-8")
util = util_path.read_text(encoding="utf-8")
line = re.search(r"^\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(\d+)\s+(\d+)\s*$",timing,re.M)
keys = ["wns_ns","tns_ns","setup_failing_endpoints","setup_total_endpoints","whs_ns","ths_ns","hold_failing_endpoints","hold_total_endpoints","wpws_ns","tpws_ns","pulse_failing_endpoints","pulse_total_endpoints"]
timing_values = {k:int(line[i+1]) if "endpoints" in k else float(line[i+1]) for i,k in enumerate(keys)}
assert timing_values["wns_ns"] == -75.099 and timing_values["tns_ns"] == -117550.977 and timing_values["setup_failing_endpoints"] == 2636 and timing_values["setup_total_endpoints"] == 14635
clock = re.search(r"^clk_fpga_0\s+\{[^}]+\}\s+(\d+\.\d+)\s+(\d+\.\d+)\s*$",timing,re.M)
assert clock and float(clock[1]) == 20 and float(clock[2]) == 50 and "Design State : Synthesized" in timing
check_timing = {k:int(v) for k,v in re.findall(r"checking ([a-z_]+) \((\d+)\)",timing)}
assert len(check_timing) == 12 and check_timing["unconstrained_internal_endpoints"] == 0
levels = re.search(r"Logic Levels:\s+(\d+)\s+\(CARRY4=(\d+)",timing)
worst = {"logic_levels":int(levels[1]), "carry4":int(levels[2]), "source":re.search(r"Source:\s+([^\r\n]+)",timing)[1].strip(), "destination":re.search(r"Destination:\s+([^\r\n]+)",timing)[1].strip(), "data_path_delay_ns":float(re.search(r"Data Path Delay:\s+(\d+\.\d+)ns",timing)[1])}
assert worst["logic_levels"] == 237 and worst["carry4"] == 206 and worst["data_path_delay_ns"] == 94.695
resources = {}
for label,name in [("Slice LUTs*","lut"),("Slice Registers","ff"),("Block RAM Tile","bram_tiles"),("DSPs","dsp")]:
    resources[name] = int(re.search(r"\|\s*"+re.escape(label)+r"\s*\|\s*(\d+)\s*\|",util)[1])
write_json("collector_sta_classification.json", {"status":"FAIL_TIMING", "design_state":"Synthesized", "report_command_native_exit_code":0, "collector_parse_native_exit_code":0, "timing":timing_values, "clock":{"name":"clk_fpga_0","period_ns":20,"frequency_mhz":50}, "worst_setup_path":worst, "check_timing":check_timing, "resources":resources, "inputs":[{"path":str(p.relative_to(ROOT)).replace("\\", "/"),"sha256":sha(p)} for p in [timing_path,util_path]], "post_route":"NOT_RUN", "bitstream":"NOT_RUN", "hardware_execution":"NOT_RUN", "reason":"报告命令成功生成失败STA，命令原生0不等于STA通过；未降低时钟或忽略约束。"})
classifier_args = [sys.executable,"-B",str(RUN / "collector_classify_sta.py")]
classifier = subprocess.run(classifier_args,cwd=ROOT,capture_output=True)
assert classifier.returncode == 2
classifier_log = RUN / "collector_sta_exit.log"
with classifier_log.open("xb") as out:
    out.write(classifier.stdout + b"\nSTDERR\n" + classifier.stderr)
new_files.append(classifier_log)
write_json("collector_sta_command_result.json", {"command":classifier_args,"native_exit_code":classifier.returncode,"log_path":str(classifier_log.relative_to(ROOT)).replace("\\", "/"),"log_sha256":sha(classifier_log),"reason":"独立分类命令真实native2表示STA失败；原报告生成命令native0保持不变。"})

old_details_path = ROOT / "report/evidence/S2B-T15/full_build_20261011_r01/build_details.json"
old_details = read(old_details_path)
old_xsa = ROOT / "report/evidence/S2B-T13/artifact_recheck_20261011_r01/s2b_inference_no_bit.xsa"
new_xsa = RUN / "s2b_inference_no_bit.xsa"
assert old_xsa.is_file() and new_xsa.is_file() and sha(old_xsa) == old_details["xsa_sha256"]
members = ["ps7_init.c","ps7_init.h","ps7_init.html","ps7_init.tcl","ps7_init_gpl.c","ps7_init_gpl.h"]
comparisons = []
with zipfile.ZipFile(old_xsa) as old_zip, zipfile.ZipFile(new_xsa) as new_zip:
    for name in members + ["s2b_inference.hwh"]:
        a = old_zip.read(name)
        b = new_zip.read(name)
        assert zlib.crc32(a) == old_zip.getinfo(name).CRC and zlib.crc32(b) == new_zip.getinfo(name).CRC
        comparisons.append({"member":name, "old_sha256":hashlib.sha256(a).hexdigest(), "new_sha256":hashlib.sha256(b).hexdigest(), "old_crc32":old_zip.getinfo(name).CRC, "new_crc32":new_zip.getinfo(name).CRC, "old_bytes":len(a), "new_bytes":len(b), "raw_byte_identical":a == b})
assert all(r["raw_byte_identical"] for r in comparisons[:6]) and not comparisons[6]["raw_byte_identical"]
write_json("collector_xsa_member_comparison.json", {"status":"SIX_PS_INIT_MEMBERS_RAW_IDENTICAL_HWH_CHANGED", "new_xsa_path":str(new_xsa.relative_to(ROOT)).replace("\\", "/"), "new_xsa_sha256":sha(new_xsa), "compiled_old_xsa_path":str(old_xsa.relative_to(ROOT)).replace("\\", "/"), "compiled_old_xsa_sha256":sha(old_xsa), "old_actual_build_details_path":str(old_details_path.relative_to(ROOT)).replace("\\", "/"), "old_actual_build_details_sha256":sha(old_details_path), "members":comparisons, "same_whole_xsa":False, "limitation":"仅证明六个PS初始化成员相同；HWH已变化，不能把旧BSP/ELF构建记录冒称新XSA编译。"})

assert all((ROOT / p).is_file() and sha(ROOT / p) == r["sha256"] for p,r in original.items())
assert all(sha(ROOT / p) == digest for p,digest in old_inventory.items())
write_json("collector_result.json", {"status":"COLLECTED_FAIL_TIMING", "role":"DEVELOPER_COLLECTOR_NOT_INDEPENDENT_REVIEWER", "source_commit":BASELINE, "source_snapshots":28, "native_jobs":5, "original_root_file_count":len(original), "original_root_files_unchanged":True, "previous_run_original34_unchanged":True, "native_exit_code":0, "command":[sys.executable,"-B",str(Path(__file__).resolve())], "elapsed_seconds":time.monotonic()-started, "tool_versions":{"Vivado":"2026.1","Python":sys.version.split()[0],"part":"xc7z020clg400-2"}, "process_tree_peak_memory":"NOT_MEASURED", "post_route":"NOT_RUN", "bitstream":"NOT_RUN", "hardware_execution":"NOT_RUN", "limitations":["已存28份S1快照为唯一源码消费，不要求当前S2工作源码回到S1。", "collector成功仅为采集完成；待独立审查，不声明PASS_G2/G3/G4/G5。", "产品入口capture1/native0旧ROSS计数问题保留，report命令native0产生FAIL_TIMING原报告。", "各job峰值和root累计峰值分开，完整进程树峰值及严格总墙钟时间未测。"]})

upstream = read(ROOT / "report/evidence/S2B-T17/full_synthesis_20261011_r01/delivery_manifest.json")["interfaces"]
def manifest(path):
    """包装真实原件及新增采集文件，不读取变化中的业务源码。"""
    rows = []
    for p in sorted(RUN.rglob("*")):
        if not p.is_file() or p.name == "delivery_manifest.json":
            continue
        role = "source" if "source_snapshot" in p.parts or p.suffix == ".py" else "log" if p.suffix in {".log",".jou"} else "result"
        if p.name in {"source_before.json","source_after.json","s2b_inference_no_bit.xsa"}:
            role = "input"
        rows.append({"path":str(p.relative_to(ROOT)).replace("\\", "/"),"sha256":sha(p),"role":role})
    rows += [{"path":str(p.relative_to(ROOT)).replace("\\", "/"),"sha256":sha(p),"role":"input"} for p in [old_xsa,old_details_path]]
    value = {"schema_version":1,"stage":"2B","task_id":"S2B-T17","run_id":"s1_platform_20261011_r01","source_commit":BASELINE,"evidence_dir":str(RUN.relative_to(ROOT)).replace("\\", "/"),"interfaces":upstream,"tool_versions":{"Vivado":"2026.1","Python":sys.version.split()[0],"part":"xc7z020clg400-2"},"files":rows,"checks":[
        {"name":"28份S1原快照来源绑定","status":"PASS","command":'"'+sys.executable+'" -B "'+str(Path(__file__).resolve())+'"',"exit_code":0,"reason":"source_before/source_after/快照RAW一致；与6d00ff2GitRAW或精确LF到CRLF关系绑定，不消费当前S2源码。"},
        {"name":"products入口capture","status":"FAIL","command":"::s2b_inference_platform::run","exit_code":1,"reason":"原products.tcldict为FAIL/native0，WARNING累计9到1触发旧ROSS capture失败，原件未改写。"},
        {"name":"native综合完成","status":"PASS","command":"wait_on_run synth_1","exit_code":0,"reason":"真实wait历史code0/0.046秒为即时等待；5job完成日志和marker已保存，非完整综合墙钟时长。"},
        {"name":"50MHz综合STA","status":"FAIL","command":'"'+sys.executable+'" -B "'+str(RUN / "collector_classify_sta.py")+'"',"exit_code":2,"reason":"分类命令真实native2；报告生成原生0保持；WNS-75.099/TNS-117550.977，2636setup失败端点。"},
        {"name":"PSinit六成员精确比较","status":"PASS","command":'"'+sys.executable+'" -B "'+str(Path(__file__).resolve())+'"',"exit_code":0,"reason":"PSinit六成员ZIP CRC及SHA与旧实际编译XSA逐字节一致；HWH不同，不继承旧编译通过。"},
        {"name":"实现位流及实板验收","status":"NOT_RUN","command":None,"exit_code":None,"reason":"本候选综合STA失败，未执行impl/postroute/bit/download/模型实板验收。"}],"limitations":["证据包装通过不等于STA或2B G0/G2/G3/G4/G5通过，接口0.1.1仍候选未冻结。", "28份快照及Git来源为6d00ff2，不使用当前S2未完成版本。", "全进程树峰值和严格综合总墙钟时间NOT_MEASURED；native子进程OS退出码未观察。", "DCP仅缓存引用，未作为permanent artifact复制或独立长期恢复承诺。", "Root旧MCP数组止于64不改写；额外报告原capture分文件保存，不捏造旧historyid。", "本轮Developer采集，尚待独立审查；所有已有root原件和旧run原34文件SHA未变。"]}
    with path.open("x",encoding="utf-8",newline="\n") as out:
        json.dump(value,out,ensure_ascii=False,indent=2)
        out.write("\n")
    return value

for mode in ["evidence","inputs"]:
    probe_path = RUN / ("collector_manifest_probe_" + mode + ".json")
    manifest(probe_path)
    args = [sys.executable,"-B","verification/check_stage_delivery.py","--mode",mode,"--manifest",str(probe_path)]
    result = subprocess.run(args,cwd=ROOT,capture_output=True)
    log_path = RUN / ("collector_packaging_" + mode + ".log")
    with log_path.open("xb") as out:
        out.write(result.stdout + b"\nSTDERR\n" + result.stderr)
    new_files.append(log_path)
    commands.append({"mode":mode,"command":args,"native_exit_code":result.returncode,"log_path":str(log_path.relative_to(ROOT)).replace("\\", "/"),"log_sha256":sha(log_path),"probe_manifest_path":str(probe_path),"probe_manifest_sha256":sha(probe_path)})
    assert result.returncode == (0 if mode == "evidence" else 2), result.stdout.decode("utf-8",errors="replace")
write_json("collector_packaging_result.json", {"role":"DEVELOPER_COLLECTOR", "status":"PACKAGING_COMPLETE_WITH_DEPENDENCIES_BLOCKED", "commands":commands, "meaning":"evidence0仅包装；inputs2因接口候选未冻结、capture失败、STA失败和实板NOT_RUN而阻断。"})
manifest(RUN / "delivery_manifest.json")
assert all(sha(ROOT / p) == r["sha256"] for p,r in original.items())
assert all(sha(ROOT / p) == digest for p,digest in old_inventory.items())
print(json.dumps({"status":"STOP_COLLECTED_FAIL_TIMING", "manifest_sha256":sha(RUN/"delivery_manifest.json"), "root_original_files_unchanged":len(original), "previous_run_original34_unchanged":True,"native_files":len(native_map),"resources":resources,"peak_process_tree_memory":"NOT_MEASURED"},ensure_ascii=False))
