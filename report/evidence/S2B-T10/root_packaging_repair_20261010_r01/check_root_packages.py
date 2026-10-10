"""只读检查本轮声明的证据，保存真实原生退出码。"""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
run_ids = ["hp0_adapter_20261010_r09", "vivado_lint_20261010_r01", "vivado_lint_20261010_r02", "vivado_lint_20261010_r03"]
rows = []
for run_id in run_ids:
    for mode in ["evidence", "inputs"]:
        command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", mode,
                   "--manifest", f"report/evidence/S2B-T10/{run_id}/delivery_manifest.json"]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        rows.append({"run_id": run_id, "mode": mode, "command": command,
                     "native_exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        assert result.returncode == (0 if mode == "evidence" else 2), rows[-1]
target = ROOT / "tmp/2B/S2B-T10/root_package_checks.json"
assert not target.exists()
target.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps([{k: row[k] for k in ("run_id", "mode", "native_exit_code")} for row in rows], ensure_ascii=False))
