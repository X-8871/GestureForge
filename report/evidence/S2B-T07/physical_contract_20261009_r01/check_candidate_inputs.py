import json
import os
import pathlib
import subprocess
import sys


# 只读核查候选清单，预期inputs被尚未冻结的物理接口和未执行验收阻断。
run = pathlib.Path(__file__).resolve().parent
root = run.parents[3]
relative = run.relative_to(root).as_posix()
cmd = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "inputs", "--manifest", f"{relative}/delivery_manifest.json"]
result = subprocess.run(cmd, cwd=root, capture_output=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
(run / "inputs_check_console.txt").write_bytes(result.stdout + result.stderr)
(run / "inputs_check_execution.json").write_text(json.dumps({
    "command": f"PYTHONIOENCODING=utf-8 python -B verification/check_stage_delivery.py --mode inputs --manifest {relative}/delivery_manifest.json",
    "argv": cmd, "exit_code": result.returncode,
    "scope": "原始checker退出2原样记录；候选未冻结及未执行验证阻断inputs，不影响文档候选可审查性",
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
subprocess.run([sys.executable, "-B", str(run / "layout_analysis.py"), "--mode", "manifest"], cwd=root, check=True)
print(json.dumps({"raw_checker_exit_code": result.returncode, "candidate_inputs_not_ready": result.returncode == 2}))
raise SystemExit(0 if result.returncode == 2 else 1)
