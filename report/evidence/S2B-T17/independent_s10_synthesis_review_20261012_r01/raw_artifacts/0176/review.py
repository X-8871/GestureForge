import hashlib
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

# 仅核验当前S10失败证据；真实命令只读Git与轻量包装检查，输出仅新审查目录。
ROOT = Path.cwd().resolve()
OUT = Path(__file__).absolute().parent
E = ROOT / "report/evidence/S2B-T17/s10_platform_20261012_r01"
COMMIT = "1eed350c43aae4cdee1f8179a93ce87d75d9f2a8"
MANIFEST_SHA = "85f10b671fb6a43fb69cb4a947f2fd2abea5fd00707281d4cc2d1ed7cbaf5abf"
checks, seen, commands, encoding_notes = [], {}, [], []
started = time.monotonic()


def raw(path, role="input", record=True):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    assert path.is_file() and not path.is_symlink(), str(path)
    value = path.read_bytes()
    if record:
        key = path.relative_to(ROOT).as_posix()
        seen[key] = {"path": key, "sha256": hashlib.sha256(value).hexdigest(), "role": role}
    return value


def text(path, role="log"):
    value = raw(path, role)
    try:
        return value.decode("utf-8", "strict")
    except UnicodeDecodeError:
        encoding_notes.append({"path": str(path), "original_bytes_preserved": True, "inspection": "LATIN1_ASCII_BYTE_PRESERVING_ONLY"})
        return value.decode("latin1")


def obj(path):
    return json.loads(raw(path).decode("utf-8", "strict"))


def check(name, condition, evidence):
    checks.append({"name": name, "status": "PASS" if condition else "FAIL", "evidence": evidence})


def save(name, value):
    with (OUT / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def run(label, argv):
    start = time.monotonic()
    cp = subprocess.run(argv, cwd=ROOT, capture_output=True, check=False)
    for suffix, value in (("stdout.log", cp.stdout), ("stderr.log", cp.stderr)):
        with (OUT / (label + "." + suffix)).open("xb") as stream:
            stream.write(value)
    record = {"command": argv, "native_exit_code": cp.returncode, "elapsed_seconds": time.monotonic() - start}
    save(label + ".native.json", record)
    commands.append(record)
    return cp


def verify(row, key="path", record=False):
    data = raw(row[key], record=record)
    return hashlib.sha256(data).hexdigest() == row["sha256"] and ("bytes" not in row or len(data) == row["bytes"])


def unwrap(value):
    if value.get("status") == "fulfilled":
        value = value["value"]
    return value.get("result", value)


def mcp(value):
    value = unwrap(value)
    return json.loads(next(x["text"] for x in value["content"] if x["type"] == "text"))


manifest = obj(E / "s10_delivery_manifest_r03.json")
check("主manifest固定SHA/1000", hashlib.sha256(raw(E / "s10_delivery_manifest_r03.json")).hexdigest() == MANIFEST_SHA and manifest["source_commit"] == COMMIT and len(manifest["files"]) == 1000, MANIFEST_SHA)
check("1000绑定逐字节SHA与三字段", all(set(x) == {"path", "sha256", "role"} and verify(x) for x in manifest["files"]), "只记录主入口和关键读取原件，不复制1000副本")
head = run("head", ["git", "rev-parse", "HEAD"])
check("固定HEAD", head.returncode == 0 and head.stdout.decode("ascii").strip() == COMMIT, COMMIT)
source = obj(E / "s10_source_binding.json")
before, after = obj(ROOT / source["before"]["path"]), obj(ROOT / source["after"]["path"])
check("source_before/after入口SHA/43/33", verify(source["before"], record=True) and verify(source["after"], record=True) and before["source_commit"] == after["source_commit"] == COMMIT and before["source_count"] == after["source_count"] == 43 and before["platform_static_source_count"] == after["platform_static_source_count"] == 33 and before["source_sha256"] == after["source_sha256"], "43=33+10，profile0.1.10")
bm = {x["path"]: x for x in before["source_files"]}
am = {x["path"]: x for x in after["source_files"]}
git_records = []
counts = {"RAW_IDENTICAL": 0, "GIT_LF_TO_RAW_CRLF": 0}
for path, entry in bm.items():
    snap = raw(entry["snapshot"], "source")
    current = raw(path, "source")
    later = raw(am[path]["snapshot"], "source")
    argv = ["git", "show", COMMIT + ":" + path]
    cp = subprocess.run(argv, cwd=ROOT, capture_output=True, check=False)
    relation = "RAW_IDENTICAL" if cp.stdout == snap else "GIT_LF_TO_RAW_CRLF"
    good = cp.returncode == 0 and snap == current == later and hashlib.sha256(snap).hexdigest() == entry["sha256"] == am[path]["sha256"] and hashlib.sha256(cp.stdout).hexdigest() == entry["git_blob_sha256"] and (cp.stdout == snap or (b"\r\n" not in cp.stdout and cp.stdout.replace(b"\n", b"\r\n") == snap)) and relation == entry["git_relation"]
    check("真实Git/当前/前后源：" + path, good, relation)
    counts[relation] += 1
    git_records.append({"command": argv, "native_exit_code": cp.returncode, "stdout_sha256": hashlib.sha256(cp.stdout).hexdigest(), "stderr": cp.stderr.decode("utf-8", "replace")})
save("source_git.native.json", git_records)
check("37RAW/6精确EOL/原14", counts == {"RAW_IDENTICAL": 37, "GIT_LF_TO_RAW_CRLF": 6} and len(source["frozen14"]) == 14 and all(bm[k]["sha256"] == v for k, v in source["frozen14"].items()), counts)
summary = obj(E / "s10_collection_summary.json")
mapping = obj(E / "s10_native_mapping.json")
check("闭合原件及100原生job副本SHA", all(verify(x) for x in summary["original_raw_inventory"]) and all(verify(x, "original_path") and verify(x, "saved_path") for x in summary["closed_input_mapping"]) and len(mapping["files"]) == 100 and all(verify(x, "original_path") and verify(x, "saved_path") for x in mapping["files"]), "原失败、stdout/stderr/native完整，不重跑")
for job in mapping["jobs"]:
    entries = [x for x in mapping["files"] if x["saved_path"].endswith(".vds") and "/" + job["run"] + "/" in x["original_path"]]
    assert len(entries) == 1
    log = text(entries[0]["saved_path"])
    directory = (ROOT / entries[0]["saved_path"]).parent
    elapsed = re.findall(r"synth_design:.*?elapsed = (\d+:\d+:\d+)", log)[-1]
    seconds = sum(int(v) * m for v, m in zip(elapsed.split(":"), (3600, 60, 1)))
    peak = max(map(float, re.findall(r"peak = ([0-9.]+)", log)))
    check("五真实完成/峰值口径：" + job["run"], "synth_design completed successfully" in log and "0 Critical Warnings and 0 Errors encountered" in log and "maximum of 1 processes" in log and (directory / "__synthesis_is_complete__").is_file() and (directory / ".vivado.end.rst").is_file() and job["raw_os_process_exit_code"] is None and seconds == job["synth_elapsed_seconds"] and peak == job["reported_single_process_peak_mb"], {"seconds": seconds, "single_process_peak_mb": peak, "raw_os_code": None})
infer = text(E / "native_jobs/s2b_inference_infer_0_synth_1/s2b_inference_infer_0.tcl", "source")
block = re.search(r"read_verilog -library xil_defaultlib -sv \{([^}]+)\}", infer)[1]
rtl = [Path(x.strip()).relative_to(ROOT).as_posix() for x in block.splitlines() if x.strip()]
check("实际compiled18/profile/threads1", len(set(rtl)) == 18 and set(rtl) == set(source["compiled_rtl"]) and "profile 0.1.10 visibility 0 clock_hz 50000000" in text(E / "setup_synthesis.tcldict", "diagnostic") and "threads 1 jobs 1" in text(E / "setup_synthesis.tcldict"), rtl)
xpr = ET.fromstring(raw(ROOT / "tmp/2B/S2B-T17/s10p1/s2b_inference_candidate.xpr", "artifact"))
paths = [x.attrib["Path"] for x in xpr.findall(".//FileSets/FileSet[@Name='sources_1']/File")]
check("实际XPR唯一wrapper/-2", len([p for p in paths if p.endswith("/s2b_inference_wrapper.v")]) == 1 and all(x.attrib["Val"] == "xc7z020clg400-2" for x in xpr.findall(".//Option[@Name='Part']")), "非-1/非postroute")
binding = obj(E / "s10_mcp_binding.json")
gate = obj(ROOT / summary["root_gate"]["path"])
history = mcp(obj(ROOT / gate["mcp_history"]["path"]))["history"]
expected_labels = ["source", "builder", "setup_failed", "setup", "launch", "wait", "open_run", "reports", "query_xdc", "close"]
check("真实十history/单次launch和builder", len(history) == 10 and [x["label"] for x in binding["paired_calls"]] == expected_labels and all(x == pair["native_history"] for x, pair in zip(history, binding["paired_calls"])) and sum(x["command"] == "launch_runs synth_1 -jobs 1" for x in history) == 1 and binding["products_repeated"] is False, "setup失败原行不覆盖")
for row in binding["paired_calls"]:
    actual = obj(ROOT / row["client_record"]["path"])
    result = mcp(actual)
    check("真实client/native：" + row["label"], result["exit_code"] == row["client_exit_code"] == row["native_history"]["code"] and row["client_timeout"] is False, row["client_exit_code"])
labels = {x["label"]: x for x in binding["paired_calls"]}
check("setup失败1/wait0且无timeout296.366秒", labels["setup_failed"]["client_exit_code"] == 1 and "s10_platform_20261011_r01/setup_synthesis.tcldict" in labels["setup_failed"]["native_history"]["output"] and labels["setup"]["client_exit_code"] == 0 and labels["wait"]["native_history"]["elapsed"] == 296.366 and labels["wait"]["client_exit_code"] == 0, "MCP客户端/native/capture分列")
products = text(E / "products.tcldict", "diagnostic")
check("products native0/capture1/code1不重跑", "status FAIL code 0 raw PRODUCTS:OK" in products and "native_counts_before {WARNING 9" in products and "native_counts_after {WARNING 1" in products and labels["builder"]["client_exit_code"] == 1 and binding["products_native_exit_code"] == 0 and binding["products_capture_exit_code"] == 1, "warning emitted负值原样保留")
timing = text(E / "timing_summary_synth.rpt")
section = timing.split("| Design Timing Summary", 1)[1].split("| Clock Summary", 1)[0]
rows = [line.split() for line in section.splitlines() if re.fullmatch(r"\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*", line)]
check("真实50MHz STA FAIL数值", len(rows) == 1 and list(map(float, rows[0])) == [-4.405, -1759.757, 758, 14872, .037, 0, 0, 14872, 8.870, 0, 0, 4151] and "Timing constraints are not met." in timing and summary["timing"]["status"] == "FAIL_TIMING", "WNS−4.405/TNS−1759.757/758of14872")
check("内部漏约束12项0/50MHz20ns", all(set(re.findall("checking " + k + r" \((\d+)\)", timing)) == {"0"} for k in summary["timing"]["check_timing"]) and "20.000" in text(E / "clocks_synth.rpt"), "check_timing不代替STA通过")
worst = text(E / "timing_worst_synth.rpt").split("Slack (VIOLATED)", 2)[1]
check("layer_cursor→MaxPool result_error24.001ns/21levels", summary["worst_path"]["source"] in worst and summary["worst_path"]["destination"] in worst and "24.001ns" in worst and "21  (CARRY4=11 DSP48E1=3" in worst and summary["worst_path"]["speed_file"].startswith("-2"), summary["worst_path"])
util = text(E / "utilization_flat_synth.rpt")
for label, value in [("Slice LUTs*", 18471), ("Slice Registers", 3987), ("Block RAM Tile", 32), ("DSPs", 144), ("Register as Latch", 0)]:
    match = re.search(r"\|\s*" + re.escape(label) + r"\s*\|\s*(\d+)\s*\|", util)
    check("真实资源：" + label, bool(match) and int(match[1]) == value, value)
xdc = text(E / "constraints_synth.xdc", "source")
old_xdc = text(ROOT / "report/evidence/S2B-T17/s7_platform_20261011_r01/constraints_synth.xdc", "source")
def actual_xdc(value):
    return [x.strip() for x in value.splitlines() if x.strip() and not x.lstrip().startswith("#")]
check("50MHz两原resetCDC例外未扩张", actual_xdc(xdc) == actual_xdc(old_xdc) and xdc.count("set_false_path") == 2 and "No valid timing exceptions found." in text(E / "exceptions_synth.rpt"), "原report_exceptions文字保持")
check("方法学告警未关闭", "Large setup violation" in text(E / "methodology_synth.rpt") and "Warning" in text(E / "drc_synth.rpt"), "不将包装/综合成功解释为方法学通过")
xsa = obj(E / "s10_xsa_comparison.json")
check("XSA新旧SHA绑定", verify(xsa["old_xsa"], record=True) and verify(xsa["new_xsa"], record=True), "无bit XSA")
with zipfile.ZipFile(ROOT / xsa["old_xsa"]["path"]) as old, zipfile.ZipFile(ROOT / xsa["new_xsa"]["path"]) as new:
    init = [x["member"] for x in xsa["members"] if x["member"].startswith("ps7_init")]
    check("六PSinit相同/HWH不同/不批准runtime", len(init) == 6 and all(old.read(k) == new.read(k) == raw(E / "generated_inputs" / k) for k in init) and old.read("s2b_inference.hwh") != new.read("s2b_inference.hwh") and not any(x.endswith(".bit") for x in new.namelist()) and xsa["runtime_elf_bsp_compatibility"] == "NOT_APPROVED", "不继承ELF/BSP/模型批准")
index = obj(E / "resource_monitoring/resource_index.json")
check("资源index固定SHA/674副本", hashlib.sha256(raw(E / "resource_monitoring/resource_index.json")).hexdigest() == "50bdb4ed9543017bd2fd8225a452d2b344bc0cc0616b178897e252102e7f79eb" and len(index["files"]) == 674 and all(verify(x) and verify(x, "saved_path") for x in index["files"]), "仅入口和关键实际窗口绑定到本次审查raw")
def resource(suffix):
    rows = [x for x in index["files"] if x["path"].endswith(suffix)]
    assert len(rows) == 1, suffix
    return ROOT / rows[0]["saved_path"]
g1 = obj(resource("s10_guard_actual_20261012_r01/guard/guard_receipt.json"))
s1 = obj(resource("s10_guard_actual_20261012_r01/supervisor_receipt.json"))
check("r01未READY/0样本路径前缀拒绝", g1["status"] == "BLOCKED" and g1["samples"] == 0 and "进度日志不在本轮允许目录" in g1["reason"] and s1["ready"] is False and s1["child_native_exit_code"] == 3, "失败原件保留")
g2 = obj(resource("s10_guard_actual_20261012_r02/guard/guard_receipt.json"))
s2 = obj(resource("s10_guard_actual_20261012_r02/supervisor_receipt.json"))
samples2 = [json.loads(x) for x in text(resource("s10_guard_actual_20261012_r02/guard/samples.jsonl")).splitlines()]
check("r02 182样本BLOCKED/guard3", len(samples2) == g2["samples"] == 182 and g2["status"] == "BLOCKED" and g2["reason"] == "INCOMPLETE_TREE_IDENTITY" and s2["ready"] is True and s2["child_native_exit_code"] == 3 and any(x["pid"] == 8524 and x["readback"]["status"] == "ALIVE" and "20400" in x["readback"]["original_error"] for x in g2["retained"]), "短命parent消失不假报候选已退出；保留未知对象")
valid_rss = [x["tree_rss_bytes"] for x in samples2 if x["tree_rss_bytes"] is not None]
check("r02真实窗口峰5298892800/minRAM834310144", max(valid_rss) == g2["sampled_peak_tree_rss_bytes"] == 5298892800 and min(x["available_ram_bytes"] for x in samples2) == g2["minimum_sampled_available_ram_bytes"] == 834310144 and all(x["limits"] == {"tree_rss_bytes": 6442450944, "available_ram_bytes": 536870912, "c_disk_free_bytes": 8589934592} for x in samples2), "仅采样窗口，缺测未填补，全程覆盖BLOCKED")
g3 = obj(resource("s10_guard_actual_20261012_r03/guard/guard_receipt.json"))
s3 = obj(resource("s10_guard_actual_20261012_r03/supervisor_receipt.json"))
events3 = [json.loads(x) for x in text(resource("s10_guard_actual_20261012_r03/guard/events.jsonl")).splitlines()]
check("r03 guard0仅known缺失不追填", g3["status"] == "ROOT_EXITED" and s3["child_native_exit_code"] == 0 and g3["retained"] == [] and any(x["kind"] == "KNOWN_MEMBERS_READBACK" for x in events3) and "BLOCKED" in index["status"] and all(s["supervisor_exit_code"] == 2 for s in [s1, s2, s3]), "supervisor2/host1与guard3/0分列")
start_admission = json.loads(unwrap(obj(resource("s10_root_run_20261012_r01/dispatch_resource_before.tool.json")))["output"])
launch_resource = json.loads(unwrap(obj(E / "mcp_closed/s10_launchResource_actual.tool.json"))["output"])
check("整批5.015GB与综合前3.680GB分列", start_admission["free_ram_bytes"] == 5015552000 and start_admission["heavy"] == [] and 5015552000 > 4831838208 and launch_resource["available_ram_bytes"] == 3680423936 < 4831838208 and any("3.680GB" in x for x in manifest["limitations"]), "不声称综合派发达到4.5GiB")
closed = unwrap(obj(E / "mcp_closed/owned_process_closed_r01.tool.json"))
closed_data = json.loads(closed["output"])
check("真实关闭全heavy空/七PID缺失", closed["exit_code"] == 0 and len(closed_data["pids"]) == 7 and not any(x["exists"] for x in closed_data["pids"]) and closed_data["heavy"] == [], "只读原件瞬时快照，不重新探测设备")
blocked = next(x for x in manifest["checks"] if x["name"] == "全运行资源身份覆盖")
failedguard = next(x for x in manifest["checks"] if x["name"] == "实际r02资源守卫执行")
check("资源BLOCKED/null与guardFAIL3分列", blocked["status"] == "BLOCKED" and blocked["exit_code"] is None and blocked["command"] is None and failedguard["status"] == "FAIL" and failedguard["exit_code"] == 3, "scope不是资源验收PASS")
old_failure = obj(E / "root_native_closed/evidence_failed_r02.tool.json")
check("旧r02包装schema失败保留", "BLOCKED" in json.dumps(old_failure) or "退出码" in json.dumps(old_failure, ensure_ascii=False), "不吞旧失败")
for mode, expected in [("evidence", 0), ("inputs", 2)]:
    cp = run(mode, [sys.executable, "-B", "-X", "utf8", str(ROOT / "verification/check_stage_delivery.py"), "--mode", mode, "--manifest", str(E / "s10_delivery_manifest_r03.json"), "--project-root", str(ROOT)])
    check("独立轻量" + mode + "真实码", cp.returncode == expected, {"actual": cp.returncode, "expected": expected, "scope": "仅包装"})
check("impl/postroute/硬件NOT_RUN", summary["implementation"] == summary["postroute"] == summary["hardware"] == "NOT_RUN" and all(x["status"] == "NOT_RUN" for x in manifest["checks"] if x["name"] in {"实现及postroute", "G3板上cache/模型/109/1000任务"}), "STA仍FAIL/资源覆盖BLOCKED；不批准G3-G5/bit/部署")
result = {"status": "PASS" if all(x["status"] == "PASS" for x in checks) else "CHANGES_REQUIRED", "scope": "S10实际失败证据准确性与可恢复性；不批准STA/资源全覆盖/部署", "source_commit": COMMIT, "reviewed_manifest_hash": MANIFEST_SHA, "checks": checks, "findings": [x for x in checks if x["status"] == "FAIL"], "commands": commands, "encoding_notes": encoding_notes, "reviewer_stop": "STOP_READONLY_S10_REVIEW_FROZEN", "elapsed_seconds": time.monotonic() - started, "peak_memory_bytes": None, "limitations": ["50MHz/-2综合STA FAIL，WNS−4.405/TNS−1759.757/758端点；实现/postroute/bit/硬件/G3-G5未批准", "r02资源182样本仅窗口；全覆盖BLOCKED，r03重新监测不追填缺测", "启动整批5.015GB与综合前3.680GB分别保存；后者未达到4.5GiB", "r03根缺失只覆盖已知成员，关闭七PID/heavy快照不代表未采对象历史全覆盖", "native/client/capture/OS分列；五job日志成功不补造OS返回0", "六PSinit同T13而HWH不同，不继承runtime/BSP兼容", "未执行仿真/综合/ROSS/Vivado/硬件/进程操作；未修改源/正式原件/Git/STATE", "1000/674绑定读取核SHA，本次raw仅绑定主入口、关键原件与轻量命令，不复制历史包"]}
save("review_result.json", result)
save("review_inputs.json", list(seen.values()))
print(json.dumps({"status": result["status"], "checks": len(checks), "findings": result["findings"], "elapsed_seconds": result["elapsed_seconds"]}, ensure_ascii=False))
raise SystemExit(0 if result["status"] == "PASS" else 2)
