"""补充原生检查器退出码，保留此前宿主 Shell 归一化结果。"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "report/evidence/S2B-T08/native_exit_clarification_20261010_r01"
DEST.mkdir(exist_ok=False)
checks = []
inputs = []
for task, run in (("S2B-T08", "request_budget_20261009_r01"),
                  ("S2B-T08", "ip_probe_20261009_r01"),
                  ("S2B-T09", "request_guard_20261010_r03")):
    relative = f"report/evidence/{task}/{run}/delivery_manifest.json"
    command = [sys.executable, "-B", "verification/check_stage_delivery.py", "--mode", "inputs", "--manifest", relative]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=30)
    (DEST / f"{run}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    parsed = json.loads(result.stdout)
    checks.append({"manifest": relative, "command": command, "python_process_exit_code": result.returncode,
                   "status": parsed["status"], "errors": parsed["errors"]})
    inputs.append(relative)
    if result.returncode != 2 or parsed["status"] != "CHECKS_FAILED":
        raise RuntimeError("实际退出码或部署阻断状态不符合检查器源定义")
receipt = {"status": "PASS_NATIVE_EXIT_CLARIFICATION", "checks": checks,
           "clarification": "此前工具exec_command的exit_code=1来自PowerShell宿主对Git Bash非零结果的归一化；check_stage_delivery.py实际Python失败码为2。旧T08文字中的退出1应解释为宿主退出码，不是Python退出码。旧日志/清单SHA及语义阻断保留，不覆盖历史。",
           "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()}
(DEST / "result.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
shutil.copyfile(__file__, DEST / "native_exit_clarification.py")
manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T08", "run_id": DEST.name,
            "source_commit": receipt["source_commit"], "evidence_dir": DEST.relative_to(ROOT).as_posix(),
            "interfaces": [], "interfaces_not_applicable_reason": "只澄清现有检查器的原生退出码，不定义或冻结任何模型/硬件接口。",
            "files": [], "checks": [{"name": "三个现有清单原生退出码及阻断结果一致", "status": "PASS", "command": "python -B tmp/2B/S2B-T08/native_exit_clarification.py", "exit_code": 0}],
            "limitations": ["退出码澄清不改变接口未冻结、部署BLOCKED及实物未验证事实。"],
            "tool_versions": {"python": sys.version.split()[0]}}
for path in sorted(DEST.iterdir()):
    role = "source" if path.suffix == ".py" else "log" if path.suffix == ".log" else "result"
    manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": role})
for relative in ["verification/check_stage_delivery.py", *inputs]:
    manifest["files"].append({"path": relative, "sha256": hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), "role": "source" if relative.endswith(".py") else "input"})
(DEST / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("PASS_NATIVE_EXIT_CLARIFICATION")
