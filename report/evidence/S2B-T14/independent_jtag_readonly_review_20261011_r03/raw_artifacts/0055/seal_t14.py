import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

# 封存最后的独立核查真实退出码和新结果，保留原审查器假阳性失败原件。
root = Path.cwd().resolve()
out = Path(__file__).resolve().parent
command = [sys.executable, "-B", "-X", "utf8", str(out / "close_review_t14.py")]
started = time.monotonic()
closed = subprocess.run(command, cwd=root, capture_output=True, check=False)
for suffix, value in (("stdout.log", closed.stdout), ("stderr.log", closed.stderr)):
    with (out / ("closure." + suffix)).open("xb") as stream:
        stream.write(value)
native = {"command": command, "native_exit_code": closed.returncode, "elapsed_seconds": time.monotonic() - started}
with (out / "closure.native.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(native, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(closed.stdout.decode("utf-8", errors="replace"))
print(closed.stderr.decode("utf-8", errors="replace"))
if closed.returncode != 0:
    raise SystemExit(closed.returncode)
review = json.loads((out / "final_review_result.json").read_text(encoding="utf-8"))
records = {}
for line in (out / "inputs_raw_manifest.jsonl").read_text(encoding="utf-8").splitlines():
    row = json.loads(line)
    records[row["path"]] = row
for path in sorted(out.iterdir()):
    assert path.is_file() and not path.is_symlink()
    key = path.relative_to(root).as_posix()
    role = "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "diagnostic" if path.name == "package_encoding_diff.txt" else "result"
    records[key] = {"path": key, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": role}
for row in records.values():
    assert set(row) == {"path", "sha256", "role"} and row["role"] in {"source", "input", "result", "log", "diagnostic", "artifact"}
    assert not row["path"].lower().endswith((".exe", ".dcp", ".bit"))
    assert hashlib.sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"]
with (out / "raw_manifest.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
    for row in sorted(records.values(), key=lambda x: x["path"]):
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
raw_hash = hashlib.sha256((out / "raw_manifest.jsonl").read_bytes()).hexdigest()
receipt = {"status": "PASS", "reviewer_stop": "STOP_READONLY_REVIEW_FROZEN", "scope": review["scope"], "source_commit": review["source_commit"], "reviewed_manifest_hash": review["reviewed_manifest_hash"], "commands": review["commands"], "closure_native": native, "reviewed_hardware_native_codes": {"vitis_probe": 0, "start_host": 0, "close_host": 0, "closed_service_native": -1, "packaging_initial_host": 1, "packaging_r02_host": 0, "original_evidence_checker": 0}, "raw_manifest": {"path": (out / "raw_manifest.jsonl").relative_to(root).as_posix(), "sha256": raw_hash, "rows": len(records)}, "result": {"path": (out / "final_review_result.json").relative_to(root).as_posix(), "sha256": hashlib.sha256((out / "final_review_result.json").read_bytes()).hexdigest()}, "limits": review["limits"], "review_elapsed_seconds": json.loads((out / "review.native.json").read_text(encoding="utf-8"))["elapsed_seconds"] + native["elapsed_seconds"], "vitis_probe_elapsed_seconds": 6.6595342, "peak_memory_bytes": None, "reviewer_initial_false_positive_native_exit_code": 2, "reviewer_false_positive_resolution": "包装限制文字Stop-Process被字符串检查误命中；AST与实际subprocess调用独立关闭，原始失败stdout/stderr/native完整保留。", "findings": []}
with (out / "final_review_receipt.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": "PASS", "receipt_sha256": hashlib.sha256((out / "final_review_receipt.json").read_bytes()).hexdigest(), "raw_manifest_sha256": raw_hash, "rows": len(records), "review_elapsed_seconds": receipt["review_elapsed_seconds"], "peak_memory_bytes": None, "STOP": receipt["reviewer_stop"]}, ensure_ascii=False))
