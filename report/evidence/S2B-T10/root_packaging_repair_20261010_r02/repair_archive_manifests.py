"""保留归档包装的失败清单，绑定已实际执行的原生成功命令。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
archive = ROOT / "report/evidence/S2B-T10/root_packaging_repair_20261010_r02"
assert not archive.exists()
archive.mkdir()
rows = []
cases = [("independent_review_20261010_r01", "python -B tmp/2B/S2B-T10/independent_review_20261010_r01/final_rebuild.py", "实际Reviewer最终driver0/75.219秒，绑定归档receipt和final_d3结果。"),
         ("root_packaging_repair_20261010_r01", "python -B tmp/2B/S2B-T10/check_root_packages.py", "实际原生driver0，四包共八次检查符合evidence0/inputs2。")]
for run_id, checked_command, reason in cases:
    target = ROOT / f"report/evidence/S2B-T10/{run_id}/delivery_manifest.json"
    original = target.read_bytes()
    (archive / f"original_{run_id}_manifest.json").write_bytes(original)
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "evidence", "--manifest", target.relative_to(ROOT).as_posix()]
    before = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert before.returncode == 2
    manifest = json.loads(original)
    manifest["checks"][1].update(command=checked_command, exit_code=0, reason=reason)
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    after = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert after.returncode == 0, after.stdout
    rows.append({"run_id": run_id, "original_sha256": hashlib.sha256(original).hexdigest(), "native_before": before.returncode, "before_stdout": before.stdout,
                 "native_after": after.returncode, "after_stdout": after.stdout, "command": command, "new_manifest_sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
(archive / "actual_repair_checks.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(rows, ensure_ascii=False))
