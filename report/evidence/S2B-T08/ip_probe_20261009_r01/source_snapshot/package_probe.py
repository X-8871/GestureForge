"""打包当前隔离配置探针的原始证据及可核对清单。"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
RUN = Path(__file__).resolve().parent
DEST = ROOT / "report/evidence/S2B-T08/ip_probe_20261009_r01"


def digest(path):
    """计算原始字节的 SHA-256。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_once(source, dest):
    """只新增归档；已有目标必须逐字节一致。"""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if digest(source) != digest(dest):
            raise RuntimeError(f"拒绝覆盖不同证据：{dest}")
    else:
        shutil.copyfile(source, dest)


for folder in (RUN / "batch", RUN / ".vivado-ai"):
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix in (".tcl", ".log", ".jou"):
            copy_once(path, DEST / ("batch" if folder.name == "batch" else "mcp_native") / path.name)
for path in (RUN / "prepare_probe.tcl", RUN / "configure_ps.tcl", Path(__file__)):
    copy_once(path, DEST / "source_snapshot" / path.name)
for relative in ("vivado/s2b_ps_platform.tcl", "board/ps_platform_fields.json"):
    copy_once(ROOT / relative, DEST / "source_snapshot" / Path(relative).name)

helper = Path("C:/Users/22061/.codex/plugins/cache/amd-ross-agentic-ai-assistant/amd-ross-agentic-ai-assistant/2026.9.1/skills/vivado-ip-configurator/lib/ipcfg.tcl")
native_logs = list((DEST / "batch").glob("*.log"))
metrics = {}
for path in native_logs:
    data = path.read_text(encoding="utf-8", errors="replace")
    metrics[path.name] = {
        "memory_peak_mb_readbacks": re.findall(r"Memory \(MB\): peak = ([\d.]+)", data),
        "elapsed_seconds_readbacks": re.findall(r"elapsed = ([\d:]+)", data),
        "command_line": re.findall(r"# Command line +: (.*)", data),
    }
meta = {
    "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "timezone": "Asia/Shanghai",
    "archive_command_exit_code": 0,
    "reset_initial_host_exit_code": None,
    "reset_initial_status": "配置与验证通过；归档Tcl错误，宿主退出码未留存",
    "helper": {"path": str(helper), "sha256": digest(helper), "plugin_version": "2026.9.1"},
    "metrics": metrics,
    "batch_invocations": len(list((DEST / "batch").glob("*.jou"))),
    "full_tool_call_count": None,
    "whole_workflow_peak_memory_mb": None,
    "warnings": ["最终验证存在未打印 WARNING 增量，见 capture；无 ERROR/CRITICAL WARNING", "xlconstant 旧 VLNV 支持存在 INFO 提示，完整平台重新核对支持状态"],
}
(DEST / "run_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
budget = json.loads((ROOT / "report/evidence/S2B-T08/request_budget_20261009_r01/delivery_manifest.json").read_text(encoding="utf-8"))
manifest = {
    "schema_version": 1, "stage": "2B", "task_id": "S2B-T08", "run_id": DEST.name,
    "source_commit": meta["source_commit"], "evidence_dir": DEST.relative_to(ROOT).as_posix(),
    "interfaces": budget["interfaces"], "files": [],
    "checks": [
        {"name": "最终BD重新打开及完整路径归档（验证调用复用已验证状态）", "status": "PASS", "command": meta["metrics"]["archive_probe_vivado.log"]["command_line"][0], "exit_code": 0},
        {"name": "完整物理接口冻结", "status": "BLOCKED", "command": None, "exit_code": None, "reason": "adapter/控制前端/缓存可见性及deadline未实现验证，当前仅最小IPI探针"},
        {"name": "综合实现与实板传输", "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "本次范围为最小配置探针，未综合或操作实物"},
    ],
    "limitations": ["失败日志全部保留；早期脚本只归档最后版本，未完整恢复每次失败源码", "converter r2 capture的native路径错绑，依据完整r2日志及最终capture核查", "原MCP会话失效与执行工具不可用属于工具故障，batch是等价离线路径", "探针配置通过不等于RTL/时序/实物/G0/G4/G5通过；50MHz是元数据", "整个流程耗时、全部工具调用量及整体峰值未测；单批原生读回见元数据", "初次reset归档失败，宿主退出码未知；后续成功不覆盖其失败事实"],
    "tool_versions": {"Vivado": "2026.1 SW Build 6511674", "ROSS": "2026.9.1"},
}
for path in sorted(DEST.rglob("*")):
    if not path.is_file() or path.name == "delivery_manifest.json":
        continue
    role = "log" if path.suffix in (".log", ".jou") else "artifact"
    if path.suffix in (".tcl", ".py") or "source_snapshot" in path.parts:
        role = "source"
    if path.name.endswith("readback.tcldict") or path.name == "run_metadata.json":
        role = "result"
    manifest["files"].append({"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": role})
for relative, role in (("vivado/s2b_ps_platform.tcl", "source"), ("board/ps_platform_fields.json", "input")):
    manifest["files"].append({"path": relative, "sha256": digest(ROOT / relative), "role": role})
(DEST / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"PACKAGED:{len(manifest['files'])}")
