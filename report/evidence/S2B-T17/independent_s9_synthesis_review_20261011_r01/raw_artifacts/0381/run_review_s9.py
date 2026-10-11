import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

# 关闭审查原始输出与真实原生码，仅在核查完成后冻结回执。
root = Path.cwd().resolve()
out = Path(__file__).resolve().parent
start = time.monotonic()
argv = [sys.executable, "-B", "-X", "utf8", str(out / "review_s9.py")]
cp = subprocess.run(argv, cwd=root, capture_output=True, check=False)
for suffix, data in (("stdout.log", cp.stdout), ("stderr.log", cp.stderr)):
    (out / ("review." + suffix)).write_bytes(data)
record = {"command": argv, "native_exit_code": cp.returncode, "elapsed_seconds": time.monotonic() - start}
(out / "review.native.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
if not (out / "review_result.json").is_file():
    print(json.dumps(record, ensure_ascii=False))
    sys.stdout.buffer.write(cp.stdout)
    sys.stderr.buffer.write(cp.stderr)
    raise SystemExit(cp.returncode)
result = json.loads((out / "review_result.json").read_text(encoding="utf-8"))
entries = {x["path"]: x for x in map(json.loads, (out / "inputs_raw_manifest.jsonl").read_text(encoding="utf-8").splitlines())}
for path in out.iterdir():
    if path.is_file():
        role = "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "result"
        relative = path.relative_to(root).as_posix()
        entries[relative] = {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": role}
for entry in entries.values():
    assert set(entry) == {"path", "sha256", "role"}
    assert entry["role"] in {"source", "input", "result", "log", "diagnostic", "artifact"}
    assert Path(entry["path"]).suffix.lower() not in {".exe", ".obj", ".dcp", ".bit"}
raw = out / "raw_manifest.jsonl"
raw.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in sorted(entries.values(), key=lambda x: x["path"])), encoding="utf-8")
receipt = {k: result[k] for k in ("status", "scope", "source_commit", "reviewed_manifest_hash", "reviewer_stop", "limitations", "findings", "review_elapsed_seconds", "reviewer_peak_memory_bytes")}
receipt.update({"review_native": record, "commands": result["commands"], "checks": len(result["checks"]), "raw_manifest_path": raw.relative_to(root).as_posix(), "raw_manifest_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(), "raw_manifest_lines": len(entries), "actual_sta_status": "FAIL_TIMING", "resource_budget_status": "BLOCKED", "git_commit": "NOT_RUN_REVIEWER_NO_SOURCE_CHANGES"})
path = out / "final_review_receipt.json"
path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": receipt["status"], "receipt_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "raw_manifest_sha256": receipt["raw_manifest_sha256"], "raw_manifest_lines": len(entries), "reviewer_stop": receipt["reviewer_stop"], "findings": result["findings"]}, ensure_ascii=False))
raise SystemExit(cp.returncode)
