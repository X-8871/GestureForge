import hashlib
import json
from pathlib import Path

root = Path(r"D:\codex-worktrees\w4")
snapshot_path = root / "report/evidence/S4-CTRL/s4_g2_closure_20261023_r01/final_source_snapshot.json"
snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
rows = []
for item in snapshot["files"]:
    path = root / item["path"]
    if not path.is_file():
        rows.append({"path": item["path"], "status": "MISSING"})
        continue
    data = path.read_bytes()
    actual_sha = hashlib.sha256(data).hexdigest()
    actual_bytes = len(data)
    rows.append({
        "path": item["path"],
        "expected_sha256": item["sha256"],
        "actual_sha256": actual_sha,
        "expected_bytes": item["bytes"],
        "actual_bytes": actual_bytes,
        "status": "MATCH" if actual_sha == item["sha256"] and actual_bytes == item["bytes"] else "MISMATCH",
    })
result = {
    "snapshot_sha256": hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),
    "base_commit": snapshot["base_commit"],
    "listed": len(snapshot["files"]),
    "match": sum(row["status"] == "MATCH" for row in rows),
    "issues": [row for row in rows if row["status"] != "MATCH"],
    "rows": rows,
}
out = Path(__file__).with_name("snapshot_hash_verification.json")
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: result[key] for key in ("snapshot_sha256", "base_commit", "listed", "match", "issues")}, ensure_ascii=False, indent=2))
