"""修正初轮诊断的跨目录输入角色；保留首次包装失败记录并完成收尾。"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

out = Path(__file__).resolve().parent
root = out.parents[3]
manifest_path = out / "delivery_manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
for entry in manifest["files"]:
    if entry["path"].startswith("report/evidence/S6-E/s6e_gate_fix_20261024_r01/"):
        entry["role"] = "input"
        entry["keep_reason"] = "只读初轮诊断输入，用于比较修复过程；非最终源码验证"
manifest["files"].append({"path": Path(__file__).relative_to(root).as_posix(),
                          "sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                          "role": "source", "keep_reason": "本次包装字段修复与核验命令"})
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
results = []
for mode, filename in (("inputs", "inputs_manifest.json"), ("evidence", "delivery_manifest.json")):
    command = [sys.executable, "-B", str(root / "verification/check_stage_delivery.py"),
               "--mode", mode, "--manifest", str(out / filename), "--project-root", str(root)]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
    results.append({"command": subprocess.list2cmdline(command), "exit_code": result.returncode,
                    "output": result.stdout + result.stderr})
    print(mode, result.returncode, result.stdout)
target = out / "packaging_recheck.json"
target.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
manifest["files"].append({"path": target.relative_to(root).as_posix(),
                          "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                          "role": "result", "keep_reason": "字段修复后包装复核结果；首次失败保留在 packaging_checks.json"})
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if all(r["exit_code"] == 0 for r in results) else 1)
