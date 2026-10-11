import hashlib
import json
import sys
from pathlib import Path

# 只冻结本次轻量审查产物，不执行被审collector真实收集。
base = Path(__file__).absolute().parent
root = Path.cwd().resolve()
result = json.loads((base / "review_result.json").read_text(encoding="utf-8"))
assert result["status"] == "PASS"
entries = {x["path"]: x for x in json.loads((base / "review_inputs.json").read_text(encoding="utf-8"))}
for path in base.rglob("*"):
    if path.is_file():
        role = "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "result"
        relative = path.relative_to(root).as_posix()
        entries[relative] = {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": role}
manifest = base / "raw_manifest.jsonl"
with manifest.open("x", encoding="utf-8", newline="\n") as stream:
    for entry in sorted(entries.values(), key=lambda x: x["path"]):
        assert set(entry) == {"path", "sha256", "role"}
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
receipt = {k: result[k] for k in ("status", "scope", "source_commit", "findings", "reviewer_stop", "elapsed_seconds", "peak_memory_bytes", "limitations")}
receipt.update({"reviewed_collector_sha256": "212c435081d15347d0353351f9bd893e85869173e8c5ce338ab8492ed1ce4e32", "reviewed_native_sha256": "ca5f2b0a2b670d0ac73068480d8f7dd1f50921172ceaa44f3773dad627b1c2fd", "reviewed_prepared_receipt_sha256": "7449541264cc74262a471c13b35f63af8dd5dbc42d74120960586c4508483a0a", "checks": result["checks"], "commands": [{"command": [sys.executable, "-B", "-X", "utf8", str(base / "review.py")], "native_exit_code": 0, "host_exec_exit_code": 0, "capture_note": "审查入口实际exec返回0；缺gate子命令原生码由subprocess单独捕获并绑定日志。"}] + result["commands"], "raw_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(), "raw_manifest_lines": len(entries)})
path = base / "final_review_receipt.json"
with path.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": receipt["status"], "receipt_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "raw_manifest_sha256": receipt["raw_manifest_sha256"], "raw_manifest_lines": len(entries), "STOP": True}, ensure_ascii=False))
