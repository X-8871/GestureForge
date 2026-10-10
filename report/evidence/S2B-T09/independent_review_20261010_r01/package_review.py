"""归档准入模块独立审查，显式排除可重建编译缓存。"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "tmp/2B/S2B-T09/review_request_guard_20261010_r01"
DEST = ROOT / "report/evidence/S2B-T09/independent_review_20261010_r01"
DEST.mkdir(exist_ok=False)
paths = [p for p in SOURCE.iterdir() if p.is_file()]
paths += [p for p in (SOURCE / "evidence").rglob("*") if p.is_file()]
paths += [p for p in (SOURCE / "work/source").rglob("*") if p.is_file()]
for path in paths:
    dest = DEST / path.relative_to(SOURCE)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, dest)
shutil.copyfile(__file__, DEST / "package_review.py")
summary = json.loads((DEST / "review_summary.json").read_text(encoding="utf-8"))
if summary["verdict"] != "PASS":
    raise RuntimeError("独立审查尚未通过")
upstream = ROOT / "report/evidence/S2B-T09/request_guard_20261010_r03/delivery_manifest.json"
checks = [
    {"name": "独立重建70736条RTL验证", "status": "PASS", "command": "见rebuild_result.json中逐项实际命令", "exit_code": 0},
    {"name": "独立二分区间参考214065条RTL验证", "status": "PASS", "command": "见independent_result.json的实际仿真命令", "exit_code": 0},
    {"name": "原审查driver错误预期inputs退出码", "status": "FAIL", "command": "python -B independent_verify.py", "exit_code": 1, "reason": "错误预期原生失败码1，实际2；原日志保留，checker_followup关闭审查脚本错误"},
    {"name": "补充检查器原生退出码核对", "status": "PASS", "command": "python -B checker_followup.py", "exit_code": 0},
    {"name": "完整物理部署接口冻结", "status": "BLOCKED", "command": None, "exit_code": None, "reason": "本审查仅候选组合模块，不批准AXI/所有权/DDR部署"},
]
manifest = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T09", "run_id": DEST.name,
            "source_commit": summary["source_commit"], "evidence_dir": DEST.relative_to(ROOT).as_posix(),
            "interfaces": json.loads(upstream.read_text(encoding="utf-8"))["interfaces"],
            "files": [], "checks": checks, "limitations": summary["limitations"],
            "tool_versions": {"python": sys.version.split()[0], "verilator": "5.050"}}
for path in sorted(DEST.rglob("*")):
    if not path.is_file():
        continue
    role = "source" if path.suffix in (".py", ".sv") else "log" if path.suffix == ".log" else "input" if path.suffix == ".txt" else "result"
    manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "role": role})
for item in summary["sources"]:
    path = ROOT / item["path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
        raise RuntimeError("被审源码在审查后改变")
    manifest["files"].append({**item, "role": "source"})
manifest["files"].append({"path": upstream.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(upstream.read_bytes()).hexdigest(), "role": "input"})
(DEST / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"PASS_REVIEW_ARCHIVE files={len(manifest['files'])}")
