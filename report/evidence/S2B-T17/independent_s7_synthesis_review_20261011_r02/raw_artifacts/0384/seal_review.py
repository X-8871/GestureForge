import hashlib
import json
from pathlib import Path

# 不回写任何已关闭输入；清单每行仅路径、SHA和既有六种role。
root = Path.cwd().resolve()
out = Path(__file__).resolve().parent

def write_new(name, value):
    with (out / name).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")

write_new("initial_python_launch_failure.tool.json", {"tool": "exec_command", "chunk_id": "e5a58b", "host_shell_exit_code": 1, "child_native_exit_code": None, "output": "Unable to create process using '\"C:\\Users\\22061\\AppData\\Local\\Programs\\Python\\Python312\\python.exe\" tmp/2B/S2B-T17/independent_s7_synthesis_review_20261011_r01/inspect_inputs.py report/evidence/S2B-T17/s7_platform_20261011_r01/s7_collection_delivery_manifest_r03.json report/evidence/S2B-T17/s7_platform_20261011_r01/s7_collection_closed_inventory_r03.json report/evidence/S2B-T17/s7_platform_20261011_r01/s7_collection_closed_input_mapping.json report/evidence/S2B-T17/s7_platform_20261011_r01/s7_collection_original_inventory.json report/evidence/S2B-T17/s7_platform_20261011_r01/s7_collection_constraints_binding.json report/evidence/S2B-T17/s7_platform_20261011_r01/s7_collection_xsa_member_comparison.json'\r\n", "reason": "PATH Espressif venv的底层Python launcher创建失败；未执行审查。使用已核验完整路径经明确范围自动审批成功恢复。"})
write_new("supplement_execution.tool.json", {"tool": "exec_command", "chunk_id": "a8de1e", "host_shell_exit_code": 1, "child_native_exit_code": None, "stdout_structured_result_path": "tmp/2B/S2B-T17/independent_s7_synthesis_review_20261011_r01/supplement_result.json", "stderr": "", "reason": "宿主工具退出码1，未另行捕获子进程native码；完整脚本结果已以UTF8结构化原件保留。products顶层history匹配失败由后续原Tcl内嵌调用核查关闭。"})
write_new("finalize_execution.tool.json", {"tool": "exec_command", "chunk_id": "c20dca", "host_shell_exit_code": 0, "child_native_exit_code": None, "output": "{\"status\": \"PASS\", \"checks\": 8, \"failures\": []}\r\n", "stderr": "", "reason": "实际exec工具结果，未将host码冒充独立捕获的child原生码。"})
review = json.loads((out / "review_result.json").read_text(encoding="utf-8"))
assert review["status"] == "PASS"
records = {}
for name in ("inputs_raw_manifest.jsonl", "supplement_inputs_raw_manifest.jsonl"):
    for line in (out / name).read_text(encoding="utf-8").splitlines():
        value = json.loads(line)
        records[value["path"]] = value
for path in sorted(out.iterdir()):
    if not path.is_file():
        continue
    key = path.relative_to(root).as_posix()
    role = "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "artifact" if path.name.endswith(".xci.snapshot") else "diagnostic" if "failure" in path.name or ".tool." in path.name else "result"
    records[key] = {"path": key, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": role}
assert all(set(x) == {"path", "sha256", "role"} and x["role"] in {"source", "input", "result", "log", "diagnostic", "artifact"} for x in records.values())
assert not any(x["path"].lower().endswith(".exe") for x in records.values())
for entry in records.values():
    p = root / entry["path"]
    assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == entry["sha256"], entry["path"]
with (out / "raw_manifest.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
    for entry in sorted(records.values(), key=lambda x: x["path"]):
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
manifest_path = out / "raw_manifest.jsonl"
manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
result_sha = hashlib.sha256((out / "review_result.json").read_bytes()).hexdigest()
receipt = {
    "status": "PASS",
    "scope": review["scope"],
    "source_commit": review["source_commit"],
    "review_result": {"path": (out / "review_result.json").relative_to(root).as_posix(), "sha256": result_sha},
    "raw_manifest": {"path": manifest_path.relative_to(root).as_posix(), "sha256": manifest_sha, "file_count": len(records)},
    "formal_inputs": [review["manifest"], review["collector_receipt"]],
    "native_verification_exit_codes": {"initial_audit": 2, "initial_evidence_wrong_root": 2, "initial_inputs_wrong_root": 2, "corrected_evidence": 0, "corrected_inputs": 2, "classifier": 2},
    "reviewer_execution_failures": "初次PATH launcher宿主1；审查checker未指定root和history嵌套计数两项原失败已保留并关闭。",
    "findings": [],
    "sta": "FAIL_TIMING",
    "implementation": "NOT_RUN",
    "postroute": "NOT_RUN",
    "bitstream": "NOT_RUN",
    "BOARD_G3_G4_G5": "NOT_RUN_OR_NOT_APPROVED",
    "no_shared_write_git_ross_hardware": True,
    "stop": "STOP_READONLY_REVIEW_FROZEN_ROOT_OWNS_NEXT_ACTION"
}
write_new("final_review_receipt.json", receipt)
print(json.dumps({"status": "PASS", "receipt_sha256": hashlib.sha256((out / "final_review_receipt.json").read_bytes()).hexdigest(), "raw_manifest_sha256": manifest_sha, "review_result_sha256": result_sha, "raw_file_count": len(records), "STOP": receipt["stop"]}, ensure_ascii=False))
