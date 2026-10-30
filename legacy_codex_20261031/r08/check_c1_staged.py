"""只读验证既有C1暂存包与先前独立审查内容一致。"""

import hashlib
import json
import subprocess
from pathlib import Path


root = Path(__file__).resolve().parents[2]
run = root / "report/evidence/S6-E/s6e_xsdb_offline_entry_20261030_r01"
manifest = json.loads((run / "delivery_manifest.json").read_text(encoding="utf-8"))
problems = []
for entry in manifest["files"]:
    path = entry["path"]
    disk = (root / path).read_bytes()
    result = subprocess.run(["git", "-C", str(root), "show", ":" + path], capture_output=True)
    if hashlib.sha256(disk).hexdigest() != entry["sha256"] or result.returncode or result.stdout != disk:
        problems.append({"path": path, "staged": result.returncode == 0, "same": result.stdout == disk})
review = json.loads((run / "review_receipt.json").read_text(encoding="utf-8"))
for name, digest in review["files"].items():
    if hashlib.sha256((run / name).read_bytes()).hexdigest() != digest:
        problems.append({"review_mismatch": name})
print(json.dumps({"manifest_files": len(manifest["files"]), "review_files": len(review["files"]), "problems": problems}, ensure_ascii=False))
raise SystemExit(bool(problems))
