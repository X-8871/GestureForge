import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

# 保留第一次检查器参数错误的失败原件，在独立新输出中补全精确根目录。
root = Path.cwd().resolve()
out = Path(__file__).resolve().parent
e = root / "report/evidence/S2B-T17/s7_platform_20261011_r01"
checks = []
inputs = {}
commands = []

def raw(path, role="input"):
    path = Path(path)
    if not path.is_absolute():
        path = root / path
    assert path.is_file() and not path.is_symlink(), str(path)
    value = path.read_bytes()
    inputs[path.relative_to(root).as_posix()] = {"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(value).hexdigest(), "role": role}
    return value

def check(name, value, detail):
    checks.append({"name": name, "status": "PASS" if value else "FAIL", "detail": detail})

def obj(path):
    return json.loads(raw(path))

def native(label, argv):
    start = time.monotonic()
    cp = subprocess.run(argv, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    for suffix, value in (("stdout.log", cp.stdout), ("stderr.log", cp.stderr)):
        with (out / (label + "." + suffix)).open("xb") as stream:
            stream.write(value)
    record = {"command": argv, "native_exit_code": cp.returncode, "elapsed_seconds": time.monotonic() - start}
    with (out / (label + ".native.json")).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    commands.append(record)
    return cp

for mode, expected in (("evidence", 0), ("inputs", 2)):
    cp = native("checker_" + mode + "_corrected", [sys.executable, "-B", "-X", "utf8", str(e / "s7_collection_stage_checker_snapshot.py"), "--project-root", str(root), "--mode", mode, "--manifest", str(e / "s7_collection_delivery_manifest_r03.json")])
    value = json.loads(cp.stdout)
    check("精确根目录checker_" + mode, cp.returncode == expected and value["task_id"] == "S2B-T17" and value["run_id"] == "s7_platform_20261011_r01", {"expected": expected, "actual": cp.returncode, "status": value["status"], "errors": value["errors"]})

history = obj(out / "history_decoded.json")
records = history.get("history", history.get("commands", []))
if not records:
    records = next((v for v in history.values() if isinstance(v, list) and v and isinstance(v[0], dict) and "command" in v[0]), [])
compact_history = [{k: x.get(k) for k in ("id", "command", "code", "elapsed", "timestamp")} for x in records]
with (out / "history_compact.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(compact_history, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
check("history恰好单次synthesis及products", len([x for x in records if "launch_runs synth_1" in x["command"]]) == 1 and len([x for x in records if "::s2b_inference_platform::products" in x["command"]]) == 1, compact_history)
builder = obj(out / "mcp_builder_decoded.json")
products = raw(e / "products.tcldict", "diagnostic").decode("utf-8")
check("builder1/products0/capture1原FAIL", builder["exit_code"] == 1 and "status FAIL code 0 raw PRODUCTS:OK" in products and "capture_options {-code 1" in products and "WARNING emitted=-8 exported=2" in products and "native_counts_before {WARNING 9" in products and "native_counts_after {WARNING 1" in products, "真实native与capture区分；原捕获失败不归为STA失败")
query = obj(out / "mcp_query_xdc_decoded.json")
query_text = query.get("output", "")
check("run状态fivecomplete/impl未启", query.get("exit_code") == 0 and query_text.count("status {synth_design Complete!} progress 100%") == 5 and "impl_1 {status {Not started} progress 0%}" in query_text, query_text)
close = obj(out / "mcp_close_decoded.json")
check("project关闭", close.get("exit_code") == 0, close)
summary = obj(e / "s7_collection_summary_final_r03.json")
manifest = obj(e / "s7_collection_delivery_manifest_r03.json")
check("命令更正与history逐字符一致", next(x["command"] for x in records if x["id"] == 7) == next(x["command"] for x in manifest["checks"] if x["name"] == "非预期锁存器"), "原reports batch原生码0不改写")
reg = root / "tmp/2B/S2B-T17/s7p1/s2b_inference_candidate.srcs/sources_1/bd/s2b_inference/ip"
xci_files = sorted(reg.glob("*/*.xci"))
check("精确注册XCI六文件", len(xci_files) == 6, [p.relative_to(root).as_posix() for p in xci_files])
xci_summary = []
for path in xci_files:
    value = raw(path, "artifact").decode("utf-8")
    xci_summary.append({"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(value.encode("utf-8")).hexdigest(), "type": "json" if value.lstrip().startswith("{") else "xml"})
    with (out / (path.stem + ".xci.snapshot")).open("xb") as stream:
        stream.write(path.read_bytes())
with (out / "xci_summary.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(xci_summary, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
for name, suffix in (("s2b_inference_ps7_0", "ps7"), ("s2b_inference_infer_0", "infer")):
    value = json.loads(raw(reg / name / (name + ".xci")))
    with (out / (suffix + "_xci_decoded.json")).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
resources = obj(e / "s7_collection_resource_and_closure_metrics.json")
check("峰值未测与before原生码不伪填", resources["process_tree_peak_memory_bytes"] is None and resources["source_before_native_exit_code"] is None and resources["source_after_native_exit_code"] == 0, resources["source_before_native_reason"])
initial = obj(out / "audit_result.json")
check("初次唯一失败为Reviewer根目录参数", initial["failures"] == ["checker_evidence真实退出码"] and "project-root 必须精确指向 Git 仓库根目录" in raw(out / "checker_evidence.stdout.log").decode("utf-8"), "失败stdout/stderr/native保留；此项已用明确--project-root补核")
result = {"status": "SUPPLEMENT_PASS_PENDING_MANUAL_COMPLETION" if all(x["status"] == "PASS" for x in checks) else "CHANGES_REQUIRED", "checks": checks, "commands": commands}
with (out / "supplement_result.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(result, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
with (out / "supplement_inputs_raw_manifest.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
    for row in sorted(inputs.values(), key=lambda x: x["path"]):
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
print(json.dumps({"status": result["status"], "failures": [x for x in checks if x["status"] == "FAIL"]}, ensure_ascii=False))
raise SystemExit(0 if all(x["status"] == "PASS" for x in checks) else 2)
