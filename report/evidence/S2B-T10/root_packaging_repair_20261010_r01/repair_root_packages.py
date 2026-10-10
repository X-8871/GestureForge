"""保留包装失败原件，再以实际零诊断检查绑定清单退出码。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
archive = ROOT / "report/evidence/S2B-T10/root_packaging_repair_20261010_r01"
assert not archive.exists()
archive.mkdir()
rows = []
for suffix in ("r01", "r02", "r03"):
    directory = ROOT / f"report/evidence/S2B-T10/vivado_lint_20261010_{suffix}"
    target = directory / "delivery_manifest.json"
    assert target.is_file()
    original = target.read_bytes()
    (archive / f"original_{suffix}_manifest.json").write_bytes(original)
    manifest = json.loads(original)
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "evidence", "--manifest", target.relative_to(ROOT).as_posix()]
    before = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    criterion = [r"C:\Program Files\Git\bin\bash.exe", "-lc", "test ! -s " + (directory / "linter.csv").relative_to(ROOT).as_posix()]
    actual = subprocess.run(criterion, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert actual.returncode == (0 if suffix == "r03" else 1)
    item = {"command": criterion, "cwd": str(ROOT), "native_exit_code": actual.returncode, "stdout": actual.stdout, "stderr": actual.stderr,
            "meaning": "只检查CSV是否为空，不解析或分组CSV；具体诊断数量由总控核对原文。"}
    criterion_file = directory / "zero_message_check.json"
    assert not criterion_file.exists()
    criterion_file.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest["files"].append({"path": criterion_file.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(criterion_file.read_bytes()).hexdigest(), "role": "result"})
    manifest["checks"][1].update(name="零诊断标准", status="PASS" if actual.returncode == 0 else "FAIL", command=subprocess.list2cmdline(criterion), exit_code=actual.returncode,
                                reason="实际原生退出码绑定：零诊断CSV应为空；FAIL保留历史实际诊断，工具lint本身仍为0。")
    target.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    after = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    rows.append({"run_id": manifest["run_id"], "original_manifest_sha256": hashlib.sha256(original).hexdigest(), "before": {"command": command, "native_exit_code": before.returncode, "stdout": before.stdout, "stderr": before.stderr},
                 "criterion": item, "after": {"command": command, "native_exit_code": after.returncode, "stdout": after.stdout, "stderr": after.stderr}, "new_manifest_sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    assert before.returncode == 2
    assert after.returncode == 0, rows[-1]
(archive / "actual_repair_checks.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps([{k: row[k] for k in ("run_id", "original_manifest_sha256", "new_manifest_sha256")} for row in rows]))
