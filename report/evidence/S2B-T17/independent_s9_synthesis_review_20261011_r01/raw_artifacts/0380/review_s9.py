import hashlib
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from pathlib import Path

# 核验冻结S9失败证据；仅执行明确Git只读对象和轻量包装/分类器。
ROOT = Path.cwd().resolve()
OUT = Path(__file__).resolve().parent
E = ROOT / "report/evidence/S2B-T17/s9_platform_20261011_r01"
COMMIT = "38c5bc02f42920d4203aa6752530d09c80fc4c57"
checks = []
seen = {}
commands = []
encoding_notes = []
started = time.monotonic()

def raw(path, role="input"):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    assert path.is_file() and not path.is_symlink(), str(path)
    value = path.read_bytes()
    key = path.relative_to(ROOT).as_posix()
    seen[key] = {"path": key, "sha256": hashlib.sha256(value).hexdigest(), "role": role}
    return value

def text(path, role="log"):
    value = raw(path, role)
    try:
        return value.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        # 厂商原日志可能混合编码，只用Latin1保留逐字节ASCII定位，绝不重写原日志。
        encoding_notes.append({"path": str(path), "utf8_strict": "FAILED", "ascii_inspection": "LATIN1_BYTE_PRESERVING", "original_bytes_preserved": True})
        return value.decode("latin1")

def obj(name):
    return json.loads(raw(E / name).decode("utf-8", errors="strict"))

def check(name, condition, evidence):
    checks.append({"name": name, "status": "PASS" if condition else "FAIL", "evidence": evidence})

def run(label, argv):
    start = time.monotonic()
    cp = subprocess.run(argv, cwd=ROOT, capture_output=True, check=False)
    for suffix, value in (("stdout.log", cp.stdout), ("stderr.log", cp.stderr)):
        with (OUT / (label + "." + suffix)).open("xb") as stream:
            stream.write(value)
    record = {"command": argv, "native_exit_code": cp.returncode, "elapsed_seconds": time.monotonic() - start}
    with (OUT / (label + ".native.json")).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    commands.append(record)
    return cp

def verify(entry, path_key="path"):
    value = raw(entry[path_key])
    return hashlib.sha256(value).hexdigest() == entry["sha256"] and ("bytes" not in entry or len(value) == entry["bytes"])

def mcp(name):
    value = obj("mcp_closed/" + name + ".json")
    result = value.get("result", value)
    if "content" in result:
        try:
            return json.loads(next(x["text"] for x in result["content"] if x.get("type") == "text"))
        except (ValueError, StopIteration):
            return result
    return result

manifest = obj("s9_delivery_manifest_r02.json")
summary = obj("s9_collection_summary.json")
source = obj("s9_source_binding.json")
check("固定manifestSHA/353绑定", hashlib.sha256(raw(E / "s9_delivery_manifest_r02.json")).hexdigest() == "8c66275d2452ac3f538be019e3f77470264fe18fd9d21ffa7fa47f5f0c39d5ea" and manifest["source_commit"] == COMMIT and len(manifest["files"]) == 353, COMMIT)
check("所有353绑定SHA/role", all(verify(x) and set(x) == {"path", "sha256", "role"} and x["role"] in {"source", "input", "result", "log", "diagnostic", "artifact"} for x in manifest["files"]), 353)
before = json.loads(raw(source["before"]["path"]))
after = json.loads(raw(source["after"]["path"]))
check("before/after冻结JSON绑定", verify(source["before"]) and verify(source["after"]) and before["source_commit"] == after["source_commit"] == COMMIT, [source["before"]["sha256"], source["after"]["sha256"]])
bm = {x["path"]: x for x in before["source_files"]}
am = {x["path"]: x for x in after["source_files"]}
static = obj("mcp_closed/static_actual_closed.json")
check("42=32static+10extra同前后SHA", len(bm) == len(am) == 42 and set(bm) == set(am) and all(bm[k]["sha256"] == am[k]["sha256"] for k in bm) and len(static["source_sha256"]) == 32 and set(bm) - set(static["source_sha256"]) == set(source["extra_paths"]), {"sources": 42, "static": 32, "extra": 10})
counts = {"RAW_IDENTICAL": 0, "GIT_LF_TO_RAW_CRLF": 0}
git_results = []
for key in bm:
    value = raw(bm[key]["snapshot"], "source")
    second = raw(am[key]["snapshot"], "source")
    argv = ["git", "show", COMMIT + ":" + key]
    cp = subprocess.run(argv, cwd=ROOT, capture_output=True, check=False)
    relation = "RAW_IDENTICAL" if cp.stdout == value else "GIT_LF_TO_RAW_CRLF"
    git_results.append({"command": argv, "native_exit_code": cp.returncode, "stdout_sha256": hashlib.sha256(cp.stdout).hexdigest(), "stderr": cp.stderr.decode("utf-8", errors="replace")})
    check("实际Git源：" + key, cp.returncode == 0 and value == second and hashlib.sha256(value).hexdigest() == bm[key]["sha256"] and hashlib.sha256(cp.stdout).hexdigest() == bm[key]["git_blob_sha256"] and (cp.stdout == value or (b"\r\n" not in cp.stdout and cp.stdout.replace(b"\n", b"\r\n") == value)) and relation == bm[key]["git_relation"], relation)
    counts[relation] += 1
with (OUT / "git_objects.native.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(git_results, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
check("36RAW+6精确EOL和原14", counts == {"RAW_IDENTICAL": 36, "GIT_LF_TO_RAW_CRLF": 6} and len(source["frozen14"]) == 14 and all(bm[k]["sha256"] == v for k, v in source["frozen14"].items()), counts)
diff = run("production_unchanged", ["git", "diff", "--name-only", "c3a53da3", COMMIT, "--", "src", "verification", "board", "vivado"])
check("已审c3a生产测试源未新增变更", diff.returncode == 0 and diff.stdout == b"", "不重做seed/math或RTL仿真")
check("55初始原件和51闭合副本", len(summary["original_raw_inventory"]) == 55 and all(verify(x) for x in summary["original_raw_inventory"]) and len(summary["closed_input_mapping"]) == 51 and all(verify(x, "original_path") and verify(x, "saved_path") for x in summary["closed_input_mapping"]), "原失败及原生输出不覆盖")
mapping = obj("s9_native_mapping.json")
check("100原生job文件同原件SHA", len(mapping["files"]) == 100 and all(verify(x, "original_path") and verify(x, "saved_path") for x in mapping["files"]), "只读核验日志/脚本/marker，不归档EXE/cache/DCP")
periods = []
for job in mapping["jobs"]:
    directory_name = job["run"]
    # 顶层与IP实际目录从文件映射取回，不按视觉拼接候选名。
    vds_entries = [x for x in mapping["files"] if x["saved_path"].endswith(".vds") and ("/" + directory_name + "/" in x["original_path"])]
    assert len(vds_entries) == 1, directory_name
    vds_text = text(vds_entries[0]["saved_path"])
    directory = (ROOT / vds_entries[0]["saved_path"]).parent
    markers = (directory / "__synthesis_is_complete__").is_file() and (directory / ".vivado.end.rst").is_file()
    check("五任务原生完成：" + directory_name, markers and "Synthesis finished with 0 errors" in vds_text and "synth_design completed successfully" in vds_text and not re.search(r"^ERROR:", vds_text, re.M) and job["raw_os_process_exit_code"] is None, {"os_code": None, "elapsed": job["synth_elapsed_seconds"], "single_process_peak_mb": job["reported_single_process_peak_mb"]})
    clock_start = re.search(r"# Start of session at:\s*(.+)", vds_text)
    clock_end = re.search(r"Exiting Vivado at (.+?)\.\.\.", vds_text)
    assert clock_start and clock_end
    periods.append((datetime.strptime(clock_start[1].strip(), "%a %b %d %H:%M:%S %Y"), datetime.strptime(clock_end[1].strip(), "%a %b %d %H:%M:%S %Y"), directory_name))
    peak = max(map(float, re.findall(r"Memory \(MB\): peak = ([\d.]+)", vds_text)))
    elapsed = re.findall(r"synth_design: Time \(s\): cpu = [\d:]+ ; elapsed = ([\d:]+)", vds_text)[-1]
    seconds = sum(int(v) * 60 ** i for i, v in enumerate(reversed(elapsed.split(":"))))
    check("job峰值与耗时口径：" + directory_name, peak == job["reported_single_process_peak_mb"] and seconds == job["synth_elapsed_seconds"], {"seconds": seconds, "peak_mb": peak, "tree_peak": None})
periods.sort()
check("五official job串行", len(periods) == 5 and all(periods[i][1] <= periods[i+1][0] for i in range(4)), [[str(a), str(b), name] for a, b, name in periods])
xpr_path = ROOT / "tmp/2B/S2B-T17/s9p1/s2b_inference_candidate.xpr"
xpr = ET.fromstring(raw(xpr_path, "artifact"))
paths = [x.attrib["Path"] for x in xpr.findall(".//FileSets/FileSet[@Name='sources_1']/File")]
rtl = ["src/" + x.split("src/", 1)[1] for x in paths if "src/" in x and x.endswith(".sv")]
check("XPR18RTL唯一wrapper/-2", len(rtl) == 18 and set(rtl) == set(source["compiled_rtl"]) and len([x for x in paths if x.endswith("/s2b_inference_wrapper.v")]) == 1 and all(x.attrib["Val"] == "xc7z020clg400-2" for x in xpr.findall(".//Option[@Name='Part']")), rtl)
reg = xpr_path.parent / "s2b_inference_candidate.srcs/sources_1/bd/s2b_inference/ip"
infer_path = reg / "s2b_inference_infer_0/s2b_inference_infer_0.xci"
infer_text = text(infer_path, "artifact")
check("XCI visibility0", re.search(r'"PROFILE_VISIBILITY_PROVEN"\s*:\s*\[\s*\{\s*"value"\s*:\s*"0"', infer_text) is not None, "实际注册XCI，非计划字段")
history_obj = mcp("mcp_history")
history = next(v for v in history_obj.values() if isinstance(v, list) and v and isinstance(v[0], dict) and "command" in v[0])
with (OUT / "history_compact.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump([{k: x.get(k) for k in ("id", "command", "code", "elapsed", "timestamp")} for x in history], stream, ensure_ascii=False, indent=2)
    stream.write("\n")
check("真实九history与单次launch/run", len(history) == 9 and sum(x["command"] == "launch_runs synth_1 -jobs 1" for x in history) == 1 and sum(x["command"].startswith("::s2b_inference_platform::run ") for x in history) == 1, "products为run内嵌调用一次")
builder = mcp("mcp_builder")
products = text(E / "products.tcldict", "diagnostic")
platform_tcl = text(before["source_files"][[x["path"] for x in before["source_files"]].index("vivado/s2b_inference_platform.tcl")]["snapshot"], "source")
check("单次products native0/capture1不重跑", builder.get("exit_code") == 1 and "status FAIL code 0" in products and "raw PRODUCTS:OK" in products and "WARNING emitted=-8 exported=2" in products and "native_counts_before {WARNING 9" in products and "native_counts_after {WARNING 1" in products and platform_tcl.split("proc ::s2b_inference_platform::run", 1)[1].count("capture $evidence_dir products") == 1, "capture错误与native产品生成分列")
wait_rows = [x for x in history if x["command"] == "wait_on_run synth_1"]
client_wait = obj("mcp_closed/mcp_wait.json")
client_text = next(x["text"] for x in client_wait["result"]["content"] if x["type"] == "text")
check("服务器nativewait0/336.601s与client300s错误", len(wait_rows) == 1 and wait_rows[0]["code"] == 0 and wait_rows[0]["elapsed"] == 336.601 and client_wait["result"]["isError"] is True and "timed out awaiting tools/call after 300s" in client_text, "客户端故障不改写成0；未重跑wait/综合")
query = mcp("mcp_query_xdc")
check("查询五complete与impl未启动", query.get("exit_code") == 0 and query.get("output", "").count("status {synth_design Complete!} progress 100%") == 5 and "impl_1 {status {Not started} progress 0%}" in query.get("output", ""), "原生状态非实物验收")
timing = text(E / "timing_summary_synth.rpt")
section = timing.split("| Design Timing Summary", 1)[1].split("| Clock Summary", 1)[0]
rows = [line.split() for line in section.splitlines() if re.fullmatch(r"\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*", line)]
check("实际50MHzSTA失败数值", len(rows) == 1 and list(map(float, rows[0])) == [-4.527, -1840.705, 757, 14925, 0.037, 0, 0, 14925, 8.870, 0, 0, 4156] and "Timing constraints are not met." in timing and summary["timing"]["status"] == "FAIL_TIMING", "综合态-2，不外推postroute")
check("check_timing十二项零/50MHz20ns", all(set(re.findall("checking " + k + r" \((\d+)\)", timing)) == {"0"} for k in summary["timing"]["check_timing"]) and re.search(r"^clk_fpga_0\s+20\.000\s+\{0\.000 10\.000\}", text(E / "clocks_synth.rpt"), re.M) is not None, "无内部漏约束报告")
worst = text(E / "timing_worst_synth.rpt").split("Slack (VIOLATED)", 2)[1]
check("实际CONV feature最差路径", summary["worst_path"]["source"] in worst and summary["worst_path"]["destination"] in worst and "24.123ns  (logic 17.312ns" in worst and "route 6.811ns" in worst and "28  (CARRY4=11 DSP48E1=4" in worst, summary["worst_path"])
util = text(E / "utilization_flat_synth.rpt")
for label, expected in (("Slice LUTs*", 17840), ("Slice Registers", 3992), ("Block RAM Tile", 32), ("DSPs", 143), ("Register as Latch", 0)):
    match = re.search(r"\|\s*" + re.escape(label) + r"\s*\|\s*(\d+)\s*\|", util)
    check("资源原报告：" + label, bool(match) and int(match[1]) == expected, expected)
xdc = text(E / "constraints_synth.xdc", "source")
old_xdc = text(ROOT / "report/evidence/S2B-T17/s7_platform_20261011_r01/constraints_synth.xdc", "source")
def xdc_commands(value):
    return [x.strip() for x in value.splitlines() if x.strip() and not x.lstrip().startswith("#")]
check("两原resetCDC与exceptions原文不抹除", xdc_commands(xdc) == xdc_commands(old_xdc) and xdc.count("set_false_path") == 2 and "No valid timing exceptions found." in text(E / "exceptions_synth.rpt"), "write_xdc两例外与report_exceptions文字分别保留")
check("方法学DRC原告警未关闭", "| TIMING-16 | Warning  | Large setup violation | 687" in text(E / "methodology_synth.rpt") and "Warning" in text(E / "drc_synth.rpt"), "687 TIMING-16仍在；无实现或功能批准")
xsa = obj("s9_xsa_comparison.json")
check("新旧XSA字节SHA", verify(xsa["old_xsa"]) and verify(xsa["new_xsa"]), "pre_synth/no-bit")
with zipfile.ZipFile(ROOT / xsa["old_xsa"]["path"]) as old, zipfile.ZipFile(ROOT / xsa["new_xsa"]["path"]) as new:
    init = [x["member"] for x in xsa["members"] if x["member"].startswith("ps7_init")]
    check("六PSinit同T13而HWH不同", len(init) == 6 and all(old.read(k) == new.read(k) == raw(E / "generated_inputs" / k) for k in init) and old.read("s2b_inference.hwh") != new.read("s2b_inference.hwh") and not any(k.endswith(".bit") for k in new.namelist()), "runtime ELF/BSP兼容NOT_APPROVED")
resource = obj("mcp_closed/s9_resource_binding.json")
samples = [json.loads(line) for line in text(E / "mcp_closed/s9_resource_r01__samples.jsonl").splitlines()]
sample = samples[0]
recovery = obj("mcp_closed/s9_resource_r02__snapshot.json")
sampler = obj("mcp_closed/s9_resource_r01__sampler_receipt.json")
check("真实离散树RSS4900474880超4GiB", len(samples) == 1 and sample["owned_tree_rss_bytes"] == resource["actual_sampled_tree_rss_bytes"] == sampler["sampled_peak_tree_rss_bytes"] == 4900474880 and resource["planned_tree_rss_limit_bytes"] == 4294967296 and 4900474880 > 4294967296 and "OWNED_TREE_RSS_GT_4GiB" in sample["alerts"], "单次采样不等于连续绝对峰")
check("恢复仅父RSS1.13GB/free3.98GB", len(recovery["tree"]) == 1 and recovery["owned_tree_rss_bytes"] == recovery["owned"]["rss_bytes"] == 1130930176 and recovery["available_ram_bytes"] == 3983429632 and all(x["status"] == "NoSuchProcess" for x in recovery["r01_children"]), "警报后核验时已完成；回落不改变失败/预算BLOCKED")
check("不提高预算不补造任务终止/child归属", resource["actual_tasks_stopped"] is False and resource["limit_raised"] is False and resource["official_run_jobs"] == 1 and resource["official_run_time_overlap"] is False and any("6940历史直接父PID/命令未捕获" in x for x in resource["limitations"]), resource["limitations"])
budget_check = next(x for x in manifest["checks"] if x["name"] == "本轮进程树RSS预算未满足")
check("最终resource BLOCKED/null而非伪造非零码", budget_check["status"] == "BLOCKED" and budget_check["command"] is None and budget_check["exit_code"] is None, budget_check)
first = obj("root_closed_r02/closure_r01_evidence.native.json")
first_output = obj("root_closed_r02/closure_r01_evidence.stdout.log")
check("首轮closure schema真实2保留", first["native_exit_code"] == 2 and any("真实非零整数退出码" in x for x in first_output["errors"]), "schema错误非设计/资源采样退出码，原件保持")
closed_pid = obj("root_closed_r02/owned_process_closed.json")
closed_state = json.loads(closed_pid["result"]["output"])
stop = obj("root_closed_r02/mcp_stop.json")
stop_payload = json.loads(stop["result"]["content"][0]["text"])
check("STOP与PID33940缺失实证", closed_pid["result"]["exit_code"] == 0 and closed_state["owned_pid"] == 33940 and closed_state["present"] is False and closed_state["processes"] == [] and stop_payload["status"] == "success", "停止工具成功与PID读回，不等于设计通过")
checker_blob = run("checker_git", ["git", "show", COMMIT + ":verification/check_stage_delivery.py"])
assert checker_blob.returncode == 0
checker = OUT / "check_stage_delivery_snapshot.py"
with checker.open("xb") as stream:
    stream.write(checker_blob.stdout)
for mode, expected in (("evidence", 0), ("inputs", 2)):
    cp = run(mode, [sys.executable, "-B", "-X", "utf8", str(checker), "--mode", mode, "--manifest", str(E / "s9_delivery_manifest_r02.json"), "--project-root", str(ROOT)])
    check("独立轻量" + mode + "真实码", cp.returncode == expected and json.loads(cp.stdout)["task_id"] == "S2B-T17", {"expected": expected, "actual": cp.returncode, "scope": "仅包装"})
cp = run("classifier", [sys.executable, "-B", "-X", "utf8", str(E / "collector_code/classify_s7_sta.py"), "--report", str(E / "timing_summary_synth.rpt"), "--result", str(OUT / "classifier_result.json")])
check("独立classifier真实2/FAIL_TIMING", cp.returncode == 2 and json.loads((OUT / "classifier_result.json").read_text(encoding="utf-8"))["status"] == "FAIL_TIMING", "不运行RTL/综合")
check("未冻结候选/NOT_RUN限制保留", manifest["interfaces"][1]["frozen"] is False and all(x["status"] == "NOT_RUN" for x in manifest["checks"] if x["name"] in {"实现及postroute", "G3板上cache/模型/109/1000任务"}), "STA仍FAIL；G3-G5/cache/109/1000未运行或未批准")
result = {"status": "PASS" if all(x["status"] == "PASS" for x in checks) else "CHANGES_REQUIRED", "scope": "S9实际失败证据准确性与可恢复性独立审查，不批准STA收敛或部署/G3-G5", "source_commit": COMMIT, "reviewed_manifest_hash": "8c66275d2452ac3f538be019e3f77470264fe18fd9d21ffa7fa47f5f0c39d5ea", "checks": checks, "commands": commands, "encoding_notes": encoding_notes, "reviewer_stop": "STOP_READONLY_S9_REVIEW_FROZEN", "review_elapsed_seconds": time.monotonic() - started, "reviewer_peak_memory_bytes": None, "limitations": ["50MHz综合STA仍FAIL_TIMING，WNS-4.527/TNS-1840.705/757端点；不批准部署", "资源单次样本4900474880B超过原4GiB；后续回落不取消BLOCKED，不提高预算", "两个child历史归属有限，五officialjob串行不能推出进程树内从无重叠", "nativewait0/336.601s与client300s错误分列；OS子任务退出码未捕获null", "六PSinit同T13而HWH不同，不继承ELF/BSP兼容或PSinit/模型实物批准", "厂商非UTF8原日志逐字节保存，只作ASCII定位，不猜测完整编码或覆盖字节", "未执行RTL/综合/实现/ROSS/硬件；未改共享Git/STATE/生产源或被审证据"], "findings": [x for x in checks if x["status"] == "FAIL"]}
with (OUT / "review_result.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
with (OUT / "inputs_raw_manifest.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
    for x in sorted(seen.values(), key=lambda x: x["path"]):
        stream.write(json.dumps(x, ensure_ascii=False) + "\n")
print(json.dumps({"status": result["status"], "checks": len(checks), "failed_checks": result["findings"], "elapsed_seconds": result["review_elapsed_seconds"]}, ensure_ascii=False))
raise SystemExit(0 if result["status"] == "PASS" else 2)
