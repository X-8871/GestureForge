"""保存本次静态分析的真实源快照、版本与交付包装。"""

import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent


def digest(path):
    """计算当前原始文件字节哈希。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, data):
    """仅更新本次运行自己的包装文件，不修改源码或旧运行。"""
    (RUN / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


sources = ["src/" + name + ".sv" for name in [
    "s2a_stage2a_core_ooc", "s2a_runtime_shell", "s2a_control_csr", "s2a_memory_master",
    "s2a_network_backend", "s2a_network_descriptor_pkg", "s2a_conv_tile_engine",
    "s2a_route_engine", "s2a_maxpool_engine", "s2a_upsample_engine",
    "int8_maxpool_geometry", "int8_route_query", "int8_upsample_query",
]]
sources.append("verification/check_stage_delivery.py")
snapshot = RUN / "source_snapshot"
if not snapshot.exists():
    snapshot.mkdir()
    for relative in sources:
        source = ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copyfile(source, snapshot / source.name)
    save("source_binding.json", {
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "created_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        "bindings": [{"original_path": path, "sha256": digest(ROOT / path),
                      "snapshot_path": (snapshot / Path(path).name).relative_to(ROOT).as_posix(),
                      "snapshot_sha256": digest(snapshot / Path(path).name)} for path in sources],
        "tools": {"python": platform.python_version(),
                  "git": subprocess.check_output(["git", "--version"], text=True).strip(),
                  "git_bash": "GNU bash 5.3.15(2)-release (x86_64-pc-cygwin)",
                  "vivado": "NOT_RUN_STATIC_ANALYSIS"},
    })
for relative in sources:
    if digest(ROOT / relative) != digest(snapshot / Path(relative).name):
        raise ValueError(("源码在本次分析后发生变化", relative))
previous = json.loads((ROOT / "report/evidence/S2B-T07/physical_contract_20261009_r02/delivery_manifest.json").read_text(encoding="utf-8"))
result = json.loads((RUN / "request_budget_result.json").read_text(encoding="utf-8"))
checks = [
    {"name": "正常路径静态请求计算与消费元数据一致性", "status": "PASS",
     "command": "python -B report/evidence/S2B-T08/request_budget_20261009_r01/calculate_budget.py", "exit_code": 0},
    {"name": "物理部署deadline值", "status": "BLOCKED", "command": None, "exit_code": None,
     "reason": "物理候选未冻结、adapter未实现；HP服务及完整周期界未取得，静态必要条件不能证明部署期限"},
    {"name": "RTL仿真与综合及软件测试", "status": "NOT_APPLICABLE", "command": None, "exit_code": None,
     "reason": "本次仅授权读取RTL/模型元数据进行静态整数计算，没有实现变更或测试运行"},
    {"name": "实物推理100样本与1000任务", "status": "NOT_RUN", "command": None, "exit_code": None,
     "reason": "本次没有实物操作；静态数量不代表完整阶段2B验收"},
]
receipt = RUN / "packaging_check_receipt.json"
if receipt.is_file():
    actual = json.loads(receipt.read_text(encoding="utf-8"))
    checks.append({"name": "首次真实evidence包装检查", "status": "PASS",
                   "command": actual["evidence"]["command"], "exit_code": actual["evidence"]["exit_code"]})
    checks.append({"name": "首次真实inputs检查保留未冻结阻断", "status": "FAIL",
                   "command": actual["inputs"]["command"], "exit_code": actual["inputs"]["exit_code"],
                   "reason": "实际检查退出1：候选frozen=false及部署BLOCKED/实物NOT_RUN，不能消费为已冻结部署依赖；静态分析仍有效"})
files = [{"path": path, "sha256": digest(ROOT / path), "role": "source"} for path in sources]
for relative in ["report/evidence/S2A-T01/tiny416_model_manifest.json",
                 "report/evidence/S2B-T07/physical_contract_20261009_r02/layout_result.json"]:
    files.append({"path": relative, "sha256": digest(ROOT / relative), "role": "input"})
for path in sorted(RUN.rglob("*")):
    if path.is_file() and path.name != "delivery_manifest.json":
        role = "source" if path.parent == snapshot or path.suffix == ".py" else "artifact"
        if path.name == "request_budget_result.json":
            role = "result"
        elif path.suffix == ".log":
            role = "log"
        elif path.name == "consumed_input_projection.json":
            role = "input"
        files.append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": role})
save("delivery_manifest.json", {
    "schema_version": 1, "stage": "2B", "task_id": "S2B-T08", "run_id": RUN.name,
    "source_commit": result["source_commit"], "evidence_dir": RUN.relative_to(ROOT).as_posix(),
    "interfaces": previous["interfaces"], "files": files, "checks": checks,
    "limitations": result["limitations"],
    "tool_versions": {"python": platform.python_version(),
                      "git": subprocess.check_output(["git", "--version"], text=True).strip(),
                      "git_bash": "GNU bash 5.3.15(2)-release (x86_64-pc-cygwin)"},
})
print("SOURCE_SNAPSHOT_AND_MANIFEST_PACKAGED", len(files))
