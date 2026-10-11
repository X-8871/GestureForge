import hashlib
import json
import sys
from pathlib import Path

# 只冻结本次失败证据审查；增加原14旧基线和真实旧schema失败码的只读复核。
base = Path(__file__).absolute().parent
root = Path.cwd().resolve()
result = json.loads((base / "review_result.json").read_text(encoding="utf-8"))
assert result["status"] == "PASS"
entries = {x["path"]: x for x in json.loads((base / "review_inputs.json").read_text(encoding="utf-8"))}
source_path = root / "report/evidence/S2B-T17/s10_platform_20261012_r01/s10_source_binding.json"
old_path = root / "report/evidence/S2B-T17/s7_platform_20261011_r01/s7_collection_source_binding.json"
source = json.loads(source_path.read_text(encoding="utf-8"))
old = json.loads(old_path.read_text(encoding="utf-8"))
assert source["frozen14"] == old["frozen14_sha256"]
failure_path = root / "report/evidence/S2B-T17/s10_platform_20261012_r01/root_native_closed/evidence_failed_r02.tool.json"
failure = json.loads(failure_path.read_text(encoding="utf-8"))["value"]["result"]
assert failure["exit_code"] == 2 and "checks[7] 为 BLOCKED 时 exit_code 必须为 null" in json.loads(failure["output"])["errors"]
for path in [old_path, failure_path]:
    relative = path.relative_to(root).as_posix()
    entries[relative] = {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": "input"}
for path in base.rglob("*"):
    if path.is_file():
        assert path.suffix.lower() not in {".exe", ".obj", ".dcp", ".bit", ".pyc"}
        relative = path.relative_to(root).as_posix()
        entries[relative] = {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "result"}
manifest = base / "raw_manifest.jsonl"
with manifest.open("x", encoding="utf-8", newline="\n") as stream:
    for entry in sorted(entries.values(), key=lambda x: x["path"]):
        assert set(entry) == {"path", "sha256", "role"}
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
native = json.loads((base / "review.native.json").read_text(encoding="utf-8"))
receipt = {k: result[k] for k in ("status", "scope", "source_commit", "reviewed_manifest_hash", "findings", "reviewer_stop", "elapsed_seconds", "peak_memory_bytes", "limitations", "encoding_notes")}
receipt.update({"checks": len(result["checks"]) + 2, "supplemental_checks": ["原14与S7实际冻结SHA逐字一致", "旧r02schema失败原生2和BLOCKED退出码应null错误正文一致，原件保留"], "review_native": native, "commands": result["commands"], "actual_sta_status": "FAIL_TIMING", "resource_full_coverage_status": "BLOCKED", "raw_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(), "raw_manifest_lines": len(entries)})
receipt["reviewer_seal_initial_failure"] = {"native_exit_code": 1, "evidence": "seal_initial_failure.json", "scope": "审查辅助脚本路径引用错误，原始综合证据不受影响"}
path = base / "final_review_receipt.json"
with path.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": receipt["status"], "receipt_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "raw_manifest_sha256": receipt["raw_manifest_sha256"], "raw_manifest_lines": len(entries), "STOP": True}, ensure_ascii=False))
