import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

# 捕获只读增量核查原生码与关闭输出，然后冻结最终receipt。
root = Path.cwd().resolve()
out = Path(__file__).resolve().parent
argv = [sys.executable, "-B", "-X", "utf8", str(out / "review_increment.py")]
started = time.monotonic()
cp = subprocess.run(argv, cwd=root, capture_output=True, check=False)
for suffix, content in (("stdout.log", cp.stdout), ("stderr.log", cp.stderr)):
    with (out / ("review." + suffix)).open("xb") as stream:
        stream.write(content)
native = {"command": argv, "native_exit_code": cp.returncode, "elapsed_seconds": time.monotonic() - started}
with (out / "review.native.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(native, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(cp.stdout.decode("utf-8", errors="replace"))
print(cp.stderr.decode("utf-8", errors="replace"))
if cp.returncode != 0:
    raise SystemExit(cp.returncode)
review = json.loads((out / "review_result.json").read_text(encoding="utf-8"))
entries = {}
for line in (out / "inputs_raw_manifest.jsonl").read_text(encoding="utf-8").splitlines():
    entry = json.loads(line)
    entries[entry["path"]] = entry
for path in sorted(out.iterdir()):
    assert path.is_file() and not path.is_symlink()
    key = path.relative_to(root).as_posix()
    role = "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "result"
    entries[key] = {"path": key, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": role}
for entry in entries.values():
    assert set(entry) == {"path", "sha256", "role"} and entry["role"] in {"source", "input", "result", "log", "diagnostic", "artifact"}
    assert not entry["path"].lower().endswith((".exe", ".dcp", ".bit"))
    assert hashlib.sha256((root / entry["path"]).read_bytes()).hexdigest() == entry["sha256"]
with (out / "raw_manifest.jsonl").open("x", encoding="utf-8", newline="\n") as stream:
    for entry in sorted(entries.values(), key=lambda x: x["path"]):
        stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
raw_hash = hashlib.sha256((out / "raw_manifest.jsonl").read_bytes()).hexdigest()
receipt = {"status": "PASS", "reviewer_stop": review["reviewer_stop"], "scope": review["scope"], "source_commit": review["source_commit"], "reviewed_manifest_hash": review["reviewed_manifest_hash"], "raw_manifest": {"path": (out / "raw_manifest.jsonl").relative_to(root).as_posix(), "sha256": raw_hash, "rows": len(entries)}, "review_result_sha256": hashlib.sha256((out / "review_result.json").read_bytes()).hexdigest(), "commands": review["commands"], "review_native": native, "inherited_review_receipt_sha256": "74918612225fa9105e16a5a7ac5d4c691a27ff9e8568fa3c811d3e1a74e7a974", "inherited_raw_manifest_sha256": "94db5024be7cd835f985ff07652e779a0137c01a0109a0f6361eb77663a7beb6", "reviewed_service_host_codes": {"start": 0, "close": 0, "service_native_exit": -1}, "limits": review["limits"], "review_elapsed_seconds": native["elapsed_seconds"], "peak_memory_bytes": None, "findings": []}
with (out / "final_review_receipt.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write("\n")
print(json.dumps({"status": "PASS", "receipt_sha256": hashlib.sha256((out / "final_review_receipt.json").read_bytes()).hexdigest(), "raw_manifest_sha256": raw_hash, "rows": len(entries), "elapsed_seconds": native["elapsed_seconds"], "STOP": receipt["reviewer_stop"]}, ensure_ascii=False))
