from __future__ import annotations
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

root = Path(r"D:\codex-worktrees\w4")
tmp = root / "tmp" / "4" / "codex_review" / "s4_r1_20261023_r02"
manifest_path = root / "report" / "evidence" / "S4-CTRL" / "s4_g2_closure_20261023_r02" / "final_source_snapshot.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
checker_path = root / "scripts" / "stage4_s4ctrl" / "verify_shared_io_contract.py"
runbook_path = root / "docs" / "stage4" / "S4B_injection_path_runbook.md"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def head_matches(m, r):
    actual = subprocess.check_output(["git", "-C", str(r), "rev-parse", "HEAD"], text=True).strip()
    return actual == m["base_commit"], actual

spec = importlib.util.spec_from_file_location("s4_contract_checker_review", checker_path)
if spec is None or spec.loader is None:
    raise RuntimeError("无法载入只读检查函数")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
source = runbook_path.read_text(encoding="utf-8")
checks = []

def record(name: str, condition: bool, detail: str) -> None:
    checks.append({"name": name, "pass": bool(condition), "detail": detail})

baseline_errors = module.validate_runbook_cache_order(source)
record("actual_runbook_positive", not baseline_errors, f"errors={baseline_errors}")
mutations = [
    ("summary_input_invalidate_after_start", "输入帧在 `consumer_start` 前执行 invalidate + DSB", "输入帧在 `consumer_start` 后执行 invalidate + DSB"),
    ("summary_heads_read_before_invalidate", "PL done 后对输出 heads 先 invalidate + DSB 再读取", "PL done 后对输出 heads 先再读取后 invalidate + DSB"),
    ("detail_heads_read_before_invalidate", "PL done 后先 invalidate（64 B 外对齐）+ DSB，再读取 heads", "PL done 后先读取 heads，再 invalidate（64 B 外对齐）+ DSB"),
    ("template_heads_invalidate_before_done", "等 PL done → 输出 heads invalidate + DSB → 读 heads", "输出 heads invalidate + DSB → 等 PL done → 读 heads"),
]
for name, before, after in mutations:
    if source.count(before) != 1:
        record(name, False, f"expected exactly one source phrase, found={source.count(before)}")
        continue
    mutated = source.replace(before, after, 1)
    errors = module.validate_runbook_cache_order(mutated)
    record(name, bool(errors), f"errors={errors}")

manifest_rows = []
for row in manifest["files"]:
    p = root / Path(row["path"])
    actual = sha256(p) if p.is_file() else None
    byte_count = p.stat().st_size if p.is_file() else None
    manifest_rows.append({"path": row["path"], "expected_sha256": row["sha256"], "actual_sha256": actual, "expected_bytes": row["bytes"], "actual_bytes": byte_count, "match": actual == row["sha256"] and byte_count == row["bytes"]})
head_ok, head_actual = head_matches(manifest, root)
out = {
    "phase": sys.argv[1] if len(sys.argv) > 1 else "unspecified",
    "head_expected": manifest["base_commit"],
    "head_actual": head_actual,
    "head_match": head_ok,
    "snapshot_manifest_sha256": sha256(manifest_path),
    "source_files_listed": len(manifest_rows),
    "source_files_matched": sum(1 for x in manifest_rows if x["match"]),
    "source_hash_mismatches": [x for x in manifest_rows if not x["match"]],
    "runbook_sha256": sha256(runbook_path),
    "checker_sha256": sha256(checker_path),
    "cache_order_checks": checks,
    "status": "PASS" if head_ok and all(x["match"] for x in manifest_rows) and all(x["pass"] for x in checks) else "FAIL",
}
print(json.dumps(out, ensure_ascii=False, indent=2))
sys.exit(0 if out["status"] == "PASS" else 1)
