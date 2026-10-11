import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

# 审查过程原始stdout/stderr及真实原生码单独保存，结束后封存清单。
root = Path.cwd().resolve()
out = Path(__file__).resolve().parent
argv = [sys.executable, "-B", "-X", "utf8", str(out / "review_t14.py")]
started = time.monotonic()
result = subprocess.run(argv, cwd=root, capture_output=True, check=False)
for suffix, data in (("stdout.log", result.stdout), ("stderr.log", result.stderr)):
    with (out / ("review." + suffix)).open("xb") as stream:
        stream.write(data)
native = {"command": argv, "native_exit_code": result.returncode, "elapsed_seconds": time.monotonic() - started}
with (out / "review.native.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(native, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(result.stdout.decode("utf-8", errors="replace"))
print(result.stderr.decode("utf-8", errors="replace"))
if result.returncode != 0:
    print(json.dumps(native, ensure_ascii=False))
    raise SystemExit(result.returncode)
review = json.loads((out / "review_result.json").read_text(encoding="utf-8"))
records = {}
for line in (out / "inputs_raw_manifest.jsonl").read_text(encoding="utf-8").splitlines():
    row = json.loads(line)
    records[row["path"]] = row
for path in sorted(out.iterdir()):
    assert path.is_file() and not path.is_symlink()
    key = path.relative_to(root).as_posix()
    role = "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "result"
    records[key] = {"path": key, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": role}
assert not any(row["path"].lower().endswith((".exe", ".dcp", ".bit")) for row in records.values())
for row in records.values():
    assert hashlib.sha256((root / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"]
with (out / "raw_manifest.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
    for row in sorted(records.values(), key=lambda x: x["path"]):
        assert set(row) == {"path", "sha256", "role"}
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
raw_sha = hashlib.sha256((out / "raw_manifest.jsonl").read_bytes()).hexdigest()
receipt = {"status": review["status"], "reviewer_stop": review["reviewer_stop"], "scope": review["scope"], "source_commit": review["source_commit"], "reviewed_manifest_hash": review["reviewed_manifest_hash"], "raw_manifest": {"path": (out / "raw_manifest.jsonl").relative_to(root).as_posix(), "sha256": raw_sha, "rows": len(records)}, "review_result_sha256": hashlib.sha256((out / "review_result.json").read_bytes()).hexdigest(), "commands": review["commands"], "review_process": native, "reviewed_hardware_native_codes": {"vitis_probe": 0, "start_host": 0, "close_host": 0, "closed_service_native": -1, "packaging_initial_host": 1, "packaging_r02_host": 0, "original_evidence_checker": 0}, "limits": review["limits"], "review_elapsed_seconds": native["elapsed_seconds"], "peak_memory_bytes": None, "findings": []}
with (out / "final_review_receipt.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": receipt["status"], "receipt_sha256": hashlib.sha256((out / "final_review_receipt.json").read_bytes()).hexdigest(), "raw_manifest_sha256": raw_sha, "rows": len(records), "elapsed_seconds": native["elapsed_seconds"], "STOP": receipt["reviewer_stop"]}, ensure_ascii=False))
