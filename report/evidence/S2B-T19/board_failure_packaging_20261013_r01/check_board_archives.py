"""逐包核验真实失败运行的原件与索引，不把包装成功当作功能成功。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

root = Path.cwd()
out = root / "report/evidence/S2B-T19/board_failure_packaging_20261013_r01"
assert out.parent.is_dir() and not out.exists()
out.mkdir()
rows = []
for run_id in ("cache_probe_20261013_r03", "cache_probe_execution_20261013_r03",
               "cache_probe_20261013_r04", "cache_probe_execution_20261013_r04"):
    manifest = root / "report/evidence/S2B-T19" / run_id / "delivery_manifest.json"
    assert manifest.is_file()
    for mode in ("evidence", "inputs"):
        command = [sys.executable, "-X", "utf8", "-B", "verification/check_stage_delivery.py",
                   "--mode", mode, "--manifest", str(manifest)]
        result = subprocess.run(command, cwd=root, capture_output=True)
        stem = run_id + "_" + mode
        (out / (stem + ".stdout.log")).write_bytes(result.stdout)
        (out / (stem + ".stderr.log")).write_bytes(result.stderr)
        rows.append({"run_id": run_id, "mode": mode, "command": command,
                     "manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                     "native_exit_code": result.returncode,
                     "expected_exit_code": 0 if mode == "evidence" else 2})
(out / "execution.json").write_text(json.dumps({"checks": rows,
    "meaning": "包装应0；真实运行失败和未执行依赖导致inputs为2，不能代表G3。"},
    ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(out / "check_board_archives.py").write_bytes(Path(__file__).read_bytes())
print(json.dumps(rows, ensure_ascii=False))
assert all(row["native_exit_code"] == row["expected_exit_code"] for row in rows)
