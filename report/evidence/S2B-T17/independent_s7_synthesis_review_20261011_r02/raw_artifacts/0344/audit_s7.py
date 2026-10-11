import hashlib
import json
import re
import subprocess
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# 独立核验只读冻结输入，仅在本次精确隔离目录生成审查证据。
ROOT = Path.cwd().resolve()
OUT = ROOT / "tmp/2B/S2B-T17/independent_s7_synthesis_review_20261011_r01"
E = ROOT / "report/evidence/S2B-T17/s7_platform_20261011_r01"
C = "a5caefba952a08f365d57193696b08c0e1aff2a5"
seen = {}
checks = []
failures = []
native = []
started = time.monotonic()

def read(path, role="input"):
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    assert p.is_file() and not p.is_symlink(), str(p)
    raw = p.read_bytes()
    seen[p.relative_to(ROOT).as_posix()] = {"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(), "role": role}
    return raw

def data(name):
    return json.loads(read(E / name).decode("utf-8"))

def check(name, condition, detail):
    checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})
    if not condition:
        failures.append(name)

def verify(entry, path_key="path"):
    raw = read(entry[path_key])
    return hashlib.sha256(raw).hexdigest() == entry["sha256"] and ("bytes" not in entry or len(raw) == entry["bytes"])

def execute(label, argv):
    t = time.monotonic()
    result = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    for suffix, content in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
        with (OUT / f"{label}.{suffix}").open("xb") as stream:
            stream.write(content)
    entry = {"command": argv, "native_exit_code": result.returncode, "elapsed_seconds": time.monotonic() - t}
    with (OUT / f"{label}.native.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(entry, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    native.append(entry)
    return result

def decode_mcp(name):
    obj = data("mcp_closed/" + name + ".json")
    if "result" in obj:
        obj = obj["result"]
    if "content" in obj:
        values = [x["text"] for x in obj["content"] if x.get("type") == "text"]
        try:
            return json.loads(values[0])
        except (ValueError, IndexError):
            return obj
    return obj

manifest = data("s7_collection_delivery_manifest_r03.json")
check("正式清单冻结SHA", seen[(E / "s7_collection_delivery_manifest_r03.json").relative_to(ROOT).as_posix()]["sha256"] == "63582f7312bb1cb4ac3141ca826cf00e8ef621fac43abc994c82c66e7c1fb296", C)
receipt = data("s7_collection_execution_receipt_r03.json")
check("正式receipt冻结SHA", seen[(E / "s7_collection_execution_receipt_r03.json").relative_to(ROOT).as_posix()]["sha256"] == "6e742a785929159493c11f707eab6a1e3ce3d035651508fd49fcdb77b4b72977", receipt["status"])
check("336清单文件逐一SHA及role", all(verify(x) and set(x) == {"path", "sha256", "role"} and x["role"] in {"source", "input", "result", "log", "diagnostic", "artifact"} for x in manifest["files"]), len(manifest["files"]))
check("接口明确未冻结", manifest["interfaces"][1]["frozen"] is False and manifest["interfaces"][1]["version"] == "s2b-physical-candidate/0.1.1", manifest["interfaces"][1])
for interface in manifest["interfaces"]:
    check("接口文档SHA：" + interface["version"], verify(interface), interface["path"])
before_path = "report/evidence/S2B-T17/s7_source_preflight_20261011_r01/source_before.json"
after_path = "report/evidence/S2B-T17/s7_source_preflight_20261011_r01/source_after.json"
before = json.loads(read(before_path))
after = json.loads(read(after_path))
check("before/after JSON冻结SHA", seen[before_path]["sha256"] == "63ed047d38f4bb624c2661c6df5b8c0857973b87245a6daff864b44702d27af4" and seen[after_path]["sha256"] == "4b190e95c16ec6b0d150774cec1fe7a833e5db1b37416279933d82efb724bfd9", [before["source_commit"], after["source_commit"]])
bm = {x["path"]: x for x in before["source_files"]}
am = {x["path"]: x for x in after["source_files"]}
binding = data("s7_collection_source_binding.json")
static = data("mcp_closed/static_actual_closed.json")
freeze = json.loads(read("report/evidence/S2B-T17/route_address_guard_20261011_r04/source_freeze.json"))
check("39=31static+8extra且前后同SHA", len(bm) == len(am) == 39 and set(bm) == set(am) == set(freeze["source_sha256"]) and len(static["source_sha256"]) == 31 and set(bm) - set(static["source_sha256"]) == set(binding["extra_bindings"]) and all(bm[k]["sha256"] == am[k]["sha256"] == freeze["source_sha256"][k] for k in bm), {"source": len(bm), "static": len(static["source_sha256"]), "extra": len(binding["extra_bindings"])})
relations = {"RAW_IDENTICAL": 0, "GIT_LF_TO_RAW_CRLF": 0}
git_commands = []
for k in bm:
    raw = read(bm[k]["snapshot"], "source")
    after_raw = read(am[k]["snapshot"], "source")
    cp = subprocess.run(["git", "show", C + ":" + k], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT, check=False)
    git_commands.append({"command": ["git", "show", C + ":" + k], "native_exit_code": cp.returncode, "stdout_sha256": hashlib.sha256(cp.stdout).hexdigest(), "stderr": cp.stderr.decode("utf-8", errors="replace")})
    relation = "RAW_IDENTICAL" if cp.stdout == raw else "GIT_LF_TO_RAW_CRLF"
    valid = cp.returncode == 0 and raw == after_raw and hashlib.sha256(raw).hexdigest() == bm[k]["sha256"] and hashlib.sha256(cp.stdout).hexdigest() == bm[k]["git_blob_sha256"] and (cp.stdout == raw or (b"\r\n" not in cp.stdout and cp.stdout.replace(b"\n", b"\r\n") == raw))
    check("实际Git源码：" + k, valid and relation == bm[k]["git_relation"], relation)
    relations[relation] += 1
with (OUT / "git_objects.native.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(git_commands, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
check("33RAW+6精确EOL", relations == {"RAW_IDENTICAL": 33, "GIT_LF_TO_RAW_CRLF": 6}, relations)
check("原14冻结内容未变", len(freeze["frozen14_sha256"]) == 14 and freeze["frozen14_sha256"] == binding["frozen14_sha256"] and all(bm[k]["sha256"] == v for k, v in freeze["frozen14_sha256"].items()), "实际Git对象、before/after快照及原冻结表共同核对")
original = data("s7_collection_original_inventory.json")
check("55原件未改写", len(original["files"]) == 55 and sum(len(read(x["path"])) for x in original["files"]) == original["total_bytes"] and all(verify(x) for x in original["files"]), original["total_bytes"])
mapping = data("s7_collection_native_mapping.json")
check("94native原件同SHA", len(mapping["files"]) == 94 and sum(x["bytes"] for x in mapping["files"]) == 1184705 and all(verify(x, "original_path") and verify(x, "saved_path") for x in mapping["files"]), 1184705)
check("20关闭原件同SHA", all(verify(x, "original_path") and verify(x, "saved_path") for x in data("s7_collection_closed_input_mapping.json")["files"]), 20)
vds = []
for job in mapping["jobs"]:
    directory = ROOT / job["saved_directory"]
    files = list(directory.glob("*.vds"))
    check("综合job完成：" + job["run"], len(files) == 1 and (directory / "__synthesis_is_complete__").is_file() and (directory / ".vivado.end.rst").is_file(), job["status"])
    if len(files) == 1:
        text = read(files[0], "log").decode("utf-8")
        vds.append(files[0])
        check("原生VDS成功及无error：" + job["run"], "synth_design completed successfully" in text and "Synthesis finished with 0 errors" in text and not re.search(r"^ERROR:", text, re.M), job["reported_single_process_peak_mb"])
        peak = max(float(v) for v in re.findall(r"Memory \(MB\): peak = ([\d.]+)", text))
        elapsed = re.findall(r"synth_design: Time \(s\): cpu = [\d:]+ ; elapsed = ([\d:]+)", text)
        seconds = sum(int(v) * (60 ** i) for i, v in enumerate(reversed(elapsed[-1].split(":"))))
        check("VDS耗时及单进程峰：" + job["run"], peak == job["reported_single_process_peak_mb"] and seconds == job["synth_design_elapsed_seconds"], {"seconds": seconds, "peak_mb": peak})
check("5VDS及峰值口径", len(vds) == 5 and max(x["reported_single_process_peak_mb"] for x in mapping["jobs"]) == 2208.859 and mapping["process_tree_peak_memory_bytes"] is None, "进程树峰值未测；core161s/2160.531MB")
xpr_path = "tmp/2B/S2B-T17/s7p1/s2b_inference_candidate.xpr"
xpr = ET.fromstring(read(xpr_path))
compiled = [x.attrib["Path"].split("src/", 1)[1] for x in xpr.findall(".//FileSets/FileSet[@Name='sources_1']/File") if "src/" in x.attrib["Path"] and x.attrib["Path"].endswith(".sv")]
compiled = ["src/" + k for k in compiled]
check("XPR实际18RTL", len(compiled) == 18 and set(compiled) == set(mapping["actual_compiled_rtl_sources"]) and set(compiled) <= set(bm), compiled)
check("XPR Part一致", all(x.attrib["Val"] == "xc7z020clg400-2" for x in xpr.findall(".//Option[@Name='Part']")) and all(x.attrib["Part"] == "xc7z020clg400-2" for x in xpr.findall(".//Run")), "-2候选，未替代实物身份与PCB核查")
history = decode_mcp("mcp_history")
with (OUT / "history_decoded.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(history, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
wait = decode_mcp("mcp_wait")
check("原生wait0/241.088s", wait.get("exit_code") == 0 and wait.get("elapsed_seconds") == 241.088 and not wait.get("timeout", False) and "timeout" not in wait.get("error", "").lower(), {"exit_code": wait.get("exit_code"), "elapsed_seconds": wait.get("elapsed_seconds")})
reports = decode_mcp("mcp_reports")
check("原生reports0", reports.get("exit_code") == 0, reports.get("elapsed_seconds"))
for name in ("mcp_builder", "mcp_launch", "mcp_setup", "mcp_query_xdc", "mcp_close"):
    decoded = decode_mcp(name)
    with (OUT / (name + "_decoded.json")).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(decoded, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
rootlog = "tmp/2B/S2B-T17/s7_root_run_20261011_r01/root_session_snapshot.log"
check("ROOT原日志快照SHA", len(read(rootlog, "log")) == 65132 and seen[rootlog]["sha256"] == "da8b702cf5eaa08da7fa58b4cfe7364b3b9bed6b86765c3856c51a2740b2d1c9", 65132)
summary = data("s7_collection_summary_final_r03.json")
timing = read(E / "timing_summary_synth.rpt", "log").decode("utf-8")
block = timing.split("| Design Timing Summary", 1)[1].split("| Clock Summary", 1)[0]
rows = [line.split() for line in block.splitlines() if re.fullmatch(r"\s*-?\d+\.\d+(?:\s+-?\d+(?:\.\d+)?){11}\s*", line)]
expected = [-7.986, -2818.766, 784, 14784, 0.037, 0, 0, 14784, 8.870, 0, 0, 4134]
check("实际时序失败数值", len(rows) == 1 and list(map(float, rows[0])) == expected and "Timing constraints are not met." in timing and summary["sta_status"] == "FAIL_TIMING", expected)
check("check_timing全部零", all(re.findall("checking " + key + r" \((\d+)\)", timing) and set(re.findall("checking " + key + r" \((\d+)\)", timing)) == {"0"} for key in summary["check_timing"]), summary["check_timing"])
clock = read(E / "clocks_synth.rpt", "log").decode("utf-8")
check("实际50MHz20ns时钟", re.search(r"^clk_fpga_0\s+20\.000\s+\{0\.000 10\.000\}", clock, re.M) is not None, summary["clock"])
xdc = read(E / "constraints_synth.xdc", "source").decode("utf-8")
s6xdc = read("report/evidence/S2B-T17/s6_platform_20261011_r01/constraints_synth.xdc", "source").decode("utf-8")
def cmds(text):
    return [line.strip() for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
check("未扩大两原resetCDC例外", cmds(xdc) == cmds(s6xdc) and xdc.count("set_false_path") == 2 and "set_multicycle_path" not in xdc and "set_clock_groups" not in xdc, cmds(xdc))
worst = read(E / "timing_worst_synth.rpt", "log").decode("utf-8").split("Slack (VIOLATED)")[1]
wp = summary["worst_path"]
check("实际最差path及logic/route", wp["source"] in worst and wp["destination"] in worst and "27.582ns  (logic 18.686ns" in worst and "route 8.896ns" in worst and "39  (CARRY4=21 DSP48E1=5" in worst, wp)
util = read(E / "utilization_flat_synth.rpt", "log").decode("utf-8")
for label, value in (("Slice LUTs*", 18840), ("Slice Registers", 3969), ("Block RAM Tile", 32), ("DSPs", 145), ("Register as Latch", 0)):
    match = re.search(r"\|\s*" + re.escape(label) + r"\s*\|\s*(\d+)\s*\|", util)
    check("实际资源：" + label, bool(match) and int(match[1]) == value, value)
xsa_compare = data("s7_collection_xsa_member_comparison.json")
with zipfile.ZipFile(ROOT / xsa_compare["old_xsa"]["path"]) as old, zipfile.ZipFile(ROOT / xsa_compare["new_xsa"]["path"]) as new:
    init_members = [x for x in xsa_compare["members"] if x["member"].startswith("ps7_init")]
    check("六PSinit原字节与T13相同", len(init_members) == 6 and all(old.read(x["member"]) == new.read(x["member"]) == read(E / "generated_inputs" / x["member"]) for x in init_members), [x["member"] for x in init_members])
    check("HWH不同且无bit", old.read("s2b_inference.hwh") != new.read("s2b_inference.hwh") and not any(x.endswith(".bit") for x in new.namelist()), "PSinit相同不等于runtime兼容，XSA为pre_synth")
check("NOT_RUN与失败保留", all(x["status"] == "NOT_RUN" for x in manifest["checks"] if x["name"] in {"实现及postroute", "bitstream生成", "BOARD及G3验收", "板上模型及109样本", "1000次板上任务"}) and any(x["status"] == "FAIL" for x in manifest["checks"]), "impl/postroute/bit/BOARD/G3-G5均未执行或未批准")
for label, mode, expected_code in (("checker_evidence", "evidence", 0), ("checker_inputs", "inputs", 2)):
    result = execute(label, [sys.executable, "-B", "-X", "utf8", str(E / "s7_collection_stage_checker_snapshot.py"), "--mode", mode, "--manifest", str(E / "s7_collection_delivery_manifest_r03.json")])
    check(label + "真实退出码", result.returncode == expected_code, {"expected": expected_code, "actual": result.returncode, "scope": "仅目录/hash包装；不代替G0/G4/G5或实物"})
result = execute("classifier", [sys.executable, "-B", "-X", "utf8", str(E / "collector_code/classify_s7_sta.py"), "--report", str(E / "timing_summary_synth.rpt"), "--result", str(OUT / "classifier_result.json")])
check("classifier真实FAIL_TIMING码2", result.returncode == 2, result.returncode)
result_obj = {"status": "CHANGES_REQUIRED" if failures else "AUTOMATED_READONLY_CHECKS_PASS_PENDING_MANUAL_COMPLETION", "source_commit": C, "checks": checks, "failures": failures, "elapsed_seconds": time.monotonic() - started, "native_commands": native, "restrictions": "未运行RTL/综合/实现/ROSS/设备；未修改共享Git、生产代码或原证据"}
with (OUT / "audit_result.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(result_obj, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
with (OUT / "inputs_raw_manifest.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
    for value in sorted(seen.values(), key=lambda x: x["path"]):
        stream.write(json.dumps(value, ensure_ascii=False) + "\n")
print(json.dumps({"status": result_obj["status"], "checks": len(checks), "failures": failures, "input_files": len(seen), "elapsed_seconds": result_obj["elapsed_seconds"]}, ensure_ascii=False))
raise SystemExit(2 if failures else 0)
