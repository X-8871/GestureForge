"""归档独立预算及 IPI 复核原件并绑定被审清单。"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[3]
DEST = ROOT / "report/evidence/S2B-T08/independent_review_20261010_r01"


def digest(path):
    """按原始字节校验被审版本和证据。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


DEST.mkdir(parents=True, exist_ok=True)
for source_name, target_name in (("review_budget_20261010_r01", "budget"), ("review_ip_20261010_r01", "ip")):
    source = ROOT / "tmp/2B/S2B-T08" / source_name
    if not source.is_dir():
        raise RuntimeError(f"缺失独立审查目录：{source}")
    for path in sorted(source.iterdir()):
        if not path.is_file() or path.suffix not in (".py", ".tcl", ".log", ".json", ".jou", ".txt"):
            continue
        dest = DEST / target_name / path.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and digest(path) != digest(dest):
            raise RuntimeError(f"拒绝覆盖独立证据：{dest}")
        if not dest.exists():
            shutil.copyfile(path, dest)
shutil.copyfile(__file__, DEST / "package_review.py")
budget = ROOT / "report/evidence/S2B-T08/request_budget_20261009_r01/delivery_manifest.json"
ip = ROOT / "report/evidence/S2B-T08/ip_probe_20261009_r01/delivery_manifest.json"
manifest = {
    "schema_version": 1, "stage": "2B", "task_id": "S2B-T08", "run_id": DEST.name,
    "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "evidence_dir": DEST.relative_to(ROOT).as_posix(),
    "interfaces": json.loads(budget.read_text(encoding="utf-8"))["interfaces"],
    "files": [],
    "checks": [
        {"name": "独立预算逐层坐标枚举及源码绑定", "status": "PASS", "command": "python -B tmp/2B/S2B-T08/review_budget_20261010_r01/independent_check.py", "exit_code": 0},
        {"name": "独立IPI重建后审查脚本字面量断言失败", "status": "FAIL", "command": "Vivado -mode batch -source tmp/2B/S2B-T08/review_ip_20261010_r01/rebuild_validate.tcl", "exit_code": 1, "reason": "真实validate已执行；RANGE同值不同字符串导致后续断言失败，补充核查关闭该审查脚本问题"},
        {"name": "补充独立IPI地址/reset只读断言", "status": "PASS", "command": "Vivado -mode batch -source tmp/2B/S2B-T08/review_ip_20261010_r01/readback_remainder.tcl", "exit_code": 0},
        {"name": "部署依赖未冻结", "status": "BLOCKED", "command": None, "exit_code": None, "reason": "本次审查仅预算及IPI最小连接；完整物理接口未冻结"},
    ],
    "limitations": ["审查PASS只适用于报告的被审内容；无时序/实现/实物/完整阶段验收", "候选接口frozen=false，inputs不可消费为冻结部署依赖"],
    "tool_versions": {"python": "3.12.10", "Vivado": "2026.1"},
}
for path in sorted(DEST.rglob("*")):
    if not path.is_file() or path.name == "delivery_manifest.json":
        continue
    role = "source" if path.suffix in (".py", ".tcl") else "log" if path.suffix in (".log", ".jou") else "result"
    manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": role})
for path in (budget, ip):
    manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": "input"})
(DEST / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"REVIEW_PACKAGED:{len(manifest['files'])}")
