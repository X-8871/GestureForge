#!/usr/bin/env python3
"""封装真实许可受阻证据；不生成、继承或伪造未运行的综合结果。"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


ROOT = Path(r"D:\FPGA_Competition")
RUN_ID = "xc7z020_2_ooc_20261008_r02"
RUN_REL = Path("report/evidence/S2A-T68") / RUN_ID
RUN = ROOT / RUN_REL
PRIOR_REL = Path("report/evidence/S2A-T68/xc7z020_2_ooc_20261008_r01")
UTC8 = timezone(timedelta(hours=8))
REQUIRED_ABSENT = (
    "utilization.rpt", "utilization_hierarchical.rpt", "timing_summary.rpt",
    "clocks.rpt", "worst_paths.rpt", "operating_conditions.rpt",
    "latch_cells.txt", "latch_check_summary.txt", "synthesis_summary.txt",
    "s2a_stage2a_core_ooc_post_synth.dcp",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def tool_payload(path: Path) -> dict:
    """解析已保存工具原文的结构化返回，不改写原始文件。"""
    outer = load(path)
    blocks = [item["text"] for item in outer["content"] if item["type"] == "text"]
    if len(blocks) != 1:
        raise ValueError(f"工具结构化原文必须唯一：{path}")
    return json.loads(blocks[0])


def values(path: Path) -> dict:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = int(value) if re.fullmatch(r"-?\d+", value) else value
    return result


def write_new(name: str, content: dict | str) -> None:
    with (RUN / name).open("x", encoding="utf-8", newline="\n") as stream:
        if isinstance(content, dict):
            json.dump(content, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        else:
            stream.write(content)


def make_record() -> dict:
    """在失败码、完整源码预检与未生成报告之间交叉核对。"""
    source = load(RUN / "source_manifest.json")
    resolution = load(RUN / "target_resolution.json")
    result = values(RUN / "run_result.txt")
    payload = tool_payload(RUN / "synthesis_failed_tool_result.json")
    output = payload["output"].replace("\\r\\n", "\n")
    if result["TCL_RETURN_CODE"] != 1 or payload["exit_code"] != 1:
        raise ValueError("许可受阻封装要求真实 Tcl 与 MCP 返回码均为1")
    if result["STAGE"] != "synthesis" or result["SYNTHESIS_COMPLETED"] != 0:
        raise ValueError("失败位置不在实际 synth_design 许可关口")
    if result["PART"] != resolution["resolved_part"] or resolution["match_count"] != 1:
        raise ValueError("真实 Part 与实际目录解析不一致")
    if "[Common 17-348]" not in output or "expired" not in output or "[Common 17-345]" not in output:
        raise ValueError("缺少真实许可过期与有效许可未找到错误")
    sources_read = re.findall(r"^RTL_SOURCE=([^\r\n]+)$", output.replace("\r\n", "\n"), re.MULTILINE)
    if len(sources_read) != 14 or len(set(sources_read)) != 14:
        raise ValueError("不能证明14项隔离 RTL 均已进入读取顺序")
    if "PASS_READ_ONLY_14_SOURCE_BINDINGS" not in output:
        raise ValueError("实际 Vivado 输出缺少源码绑定通过标记")
    if any((RUN / name).exists() for name in REQUIRED_ABSENT):
        raise ValueError("受阻包出现未预期综合结果，必须先人工核查其来源")
    command = [sys.executable, "-I", "-B", str(RUN / "prepare_sources.py"),
               "--verify-only", "--part", resolution["resolved_part"]]
    checked = subprocess.run(command, check=True, capture_output=True)
    source_check = json.loads(checked.stdout.decode("utf-8"))
    warning_lines = re.findall(r"^WARNING:.*$", output, re.MULTILINE)
    error_lines = re.findall(r"^ERROR:.*$", output, re.MULTILINE)
    command_text = load(RUN / "preflight_resource_check.json")["command"]
    diagnosis_path = RUN / "license_diagnosis.json"
    diagnosis = load(diagnosis_path)
    tier_payload = json.loads(diagnosis["actual_tier_tool_result"]["content"][0]["text"])
    tier_output = tier_payload["output"].replace("\\r\\n", "\n")
    actual_tier = next(line.split("=", 1)[1] for line in tier_output.splitlines() if line.startswith("ACTUAL_LICENSE_TIER="))
    capture_path = RUN / "log_capture_record.json"
    capture = load(capture_path)
    snapshot_bindings = []
    for key, expected_sha in (
        ("retained_log", "c1eeda743aa02c28353913cd42c0df9107d9e5478d26a9304c070acee14d59bb"),
        ("retained_journal", "0605ca164064b8be7ae37a009b1d780f0d9da0b8cf5dac380e21707742e08421"),
    ):
        path = RUN / capture[key]
        if sha(path) != expected_sha:
            raise ValueError(f"主控固定的原始字节快照哈希不匹配：{path}")
        snapshot_bindings.append({"path": path.relative_to(ROOT).as_posix(), "sha256": expected_sha})
    return {
        "schema": "s2a-xc2-ooc-blocked-execution-record-v1", "run_id": RUN_ID,
        "status": "BLOCKED_LICENSE", "recorded_at_local": datetime.now(UTC8).isoformat(timespec="seconds"),
        "candidate_commit": source["candidate_commit"], "candidate_tree": source["candidate_tree"],
        "top": source["top"], "part": result["PART"],
        "user_confirmed_device": resolution["requested_marking"],
        "source_manifest_sha256": sha(RUN / "source_manifest.json"),
        "run_synthesis_tcl_sha256": sha(RUN / "run_synthesis.tcl"),
        "started_at_local": datetime.fromtimestamp(result["STARTED_EPOCH"], UTC8).isoformat(),
        "completed_at_local": datetime.fromtimestamp(result["COMPLETED_EPOCH"], UTC8).isoformat(),
        "tcl_elapsed_seconds": result["ELAPSED_SECONDS"], "mcp_elapsed_seconds": payload["elapsed_seconds"],
        "command": command_text, "command_exit_code": payload["exit_code"], "tcl_return_code": result["TCL_RETURN_CODE"],
        "session_id": payload["session_id"], "vivado_version": "2026.1 Build 6511674",
        "python_version": platform.python_version(),
        "git_version": subprocess.check_output(["git", "--version"]).decode("utf-8").strip(),
        "source_precheck": {"status": "PASS", "command": " ".join(command), "exit_code": checked.returncode, "result": source_check},
        "rtl_read_status": "PASS", "rtl_read_completed_count": len(sources_read), "rtl_read_paths_as_emitted": sources_read,
        "synth_design_invocations_this_run": 1, "synthesis_compute_completed": False,
        "synthesis_compute_completion_count_this_run": 0, "same_run_id_synthesis_reruns": 0,
        "error_line_count": len(error_lines), "error_lines": error_lines,
        "warning_line_count": len(warning_lines), "warning_lines": warning_lines,
        "critical_warning_line_count": len(re.findall(r"^CRITICAL WARNING:.*$", output, re.MULTILINE)),
        "reported_tool_counts_line": next((line for line in output.splitlines() if "Errors encountered." in line), None),
        "license_diagnosis": {"status": "BLOCKED", "code": "Common 17-345", "expired_license_warning": "Common 17-348",
                              "meaning": "工具发现 Synthesis 许可但已过期，实际目标 xc7z020 的综合许可检查失败。"},
        "license_diagnosis_binding": {"path": diagnosis_path.relative_to(ROOT).as_posix(), "sha256": sha(diagnosis_path)},
        "actual_license_tier": actual_tier,
        "license_tier_query_exit_code": tier_payload["exit_code"],
        "next_required_input": diagnosis["next_required_input"],
        "official_license_references": diagnosis["official_sources"],
        "raw_execution_window_snapshot": {
            "capture_record_path": capture_path.relative_to(ROOT).as_posix(), "capture_record_sha256": sha(capture_path),
            "capture_type": capture["capture_type"], "session_closed_at_capture": capture["session_closed_at_capture"],
            "not_entire_session_lifecycle_log": capture["not_entire_session_lifecycle_log"],
            "covers": capture["covers"], "files": snapshot_bindings,
            "encoding_policy": "原生日志 unknown-8bit，按原始字节保留和哈希；本汇总只解析UTF-8 MCP返回JSON，不重写原生日志。",
        },
        "resource_status": "NOT_RUN", "resources": None, "latch_status": "NOT_RUN", "latch_count": None,
        "timing_report_status": "NOT_RUN", "timing_closure_claim": False,
        "operating_grade_setting_status": "NOT_RUN", "industrial_temperature_timing_claim": False,
        "checkpoint_status": "NOT_RUN", "required_outputs_absent": list(REQUIRED_ABSENT),
        "report_loop_reached": False,
        "report_failure_count_sentinel": result["REPORT_FAILURE_COUNT"],
        "latch_count_sentinel": result["LATCH_COUNT"],
        "sentinel_interpretation": "报告循环未到达：0不是报告通过数；latch=-1表示未测，不是零锁存器。",
        "peak_memory_mb": None, "peak_memory_measurement": "未测：许可关口失败，工具原返回没有本次峰值内存。",
        "ross_total_tool_call_count": None, "ross_tool_call_measurement": "完整调用量未测；本次source调用1次，原始工具结果保留。",
        "approval_binding": source["approval_binding"],
        "prior_failed_run": {"run_id": "xc7z020_2_ooc_20261008_r01", "result": values(ROOT / PRIOR_REL / "run_result.txt"),
                             "reason": "Vivado继承的Python环境使Python3.12加载Vivado3.13库，SRE module mismatch；未读取RTL/启动综合。"},
        "limitations": ["新XC器件OOC尚未完成；不能以旧XA综合资源计数代替本次结果。",
                        "资源、锁存器、时钟风险、工业等级设置和DCP均未运行或未生成，不能称PASS。",
                        "无XDC/冻结时钟；即使后续许可恢复并综合成功，也不能仅据OOC宣称时序或工业温度达标。",
                        "未修改许可文件或绕过许可；恢复执行须由主控先核对现有合法许可/工具等级，并使用新RunId。",
                        "本次没有实物操作、109样本整网重跑或修改原候选RTL。",
                        "CHECKS_OK仅表示失败包绑定/包装完整，不代表业务PASS或G0/G4/G5/实物验收。"],
    }


def make_summary(record: dict) -> str:
    return (
        "# XC7Z020-2 同源 OOC 许可受阻记录\n\n"
        f"状态：`BLOCKED_LICENSE`。实际 Part `{record['part']}`，top `{record['top']}`。\n\n"
        f"14项隔离RTL源绑定与读取完成；源码从 commit `{record['candidate_commit']}` / tree `{record['candidate_tree']}` 恢复，与旧OOC字节逐项一致。"
        "顶层wrapper只有第59/137行显式恢复CRLF，历史SHA唯一匹配。共享src未被读取或改动。\n\n"
        f"实际 `synth_design` 在许可检查失败：Common 17-348报告Synthesis许可已过期，Common 17-345报告目标xc7z020的有效许可未找到；MCP/Tcl返回1。"
        f"Tcl耗时 {record['tcl_elapsed_seconds']} 秒，MCP自报 {record['mcp_elapsed_seconds']} 秒；此次source调用1次，同RunId重跑0次。完整原文见 synthesis_failed_tool_result.json。\n\n"
        "| 项目 | 本次真实状态 |\n|---|---|\n"
        "| 14项历史字节和隔离Python预检 | PASS |\n"
        "| 实际目标器件唯一解析、14项RTL读取 | PASS |\n"
        "| 全核心OOC综合 | FAILED，业务受许可阻碍 |\n"
        "| LUT/FF/BRAM/DSP资源结果 | NOT_RUN |\n"
        "| 广义/LDCE/LDPE锁存器检查 | NOT_RUN，latch=-1是未测哨兵 |\n"
        "| 时钟风险/最差路径、环境等级、DCP | NOT_RUN |\n\n"
        "r01失败原记录保留：独立Python被Vivado的PYTHONHOME/PYTHONPATH污染，出现SRE module mismatch，尚未读取RTL或综合。"
        "r02仅改用Python -I -B、source显式UTF-8和独立namespace，修复环境后如实暴露许可阻碍。\n\n"
        "本次峰值内存和完整ROSS工具调用量未测；旧XA报告的资源或峰值内存没有当作新XC实测数据。历史批准文本以本目录精确快照和Git基线绑定，A板卡文档审计留在r01。\n\n"
        f"实际工具等级查询为 `{record['actual_license_tier']}`（返回0），它不能代替真实Synthesis许可checkout。用户尚未取得有效BASIC许可；下一步输入是有效Vivado 2026.1 BASIC许可的精确路径或许可状态。"
        "[AMD许可FAQ](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/licensing-faq.html)、[许可等级支持范围](https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vivado/vivado-licensing-options.html)；官方说明与实际诊断绑定于 license_diagnosis.json。\n\n"
        "原始执行窗口快照：vivado_session_execution_snapshot.log（SHA c1eeda743aa02c28353913cd42c0df9107d9e5478d26a9304c070acee14d59bb）与对应.jou（SHA 0605ca164064b8be7ae37a009b1d780f0d9da0b8cf5dac380e21707742e08421）。"
        "两者按unknown-8bit原字节保留；覆盖r01环境失败、r02许可失败与ENTERPRISE查询，捕获时会话未关闭，不能称全生命周期日志。捕获范围见 log_capture_record.json；UTF-8 MCP结果另存。\n\n"
        + "\n".join(f"- {item}" for item in record["limitations"]) + "\n"
    )


def entry(path: Path, role: str) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path), "role": role}


def make_manifest(record: dict) -> dict:
    source = load(RUN / "source_manifest.json")
    files = []
    for path in sorted(RUN.rglob("*")):
        if not path.is_file() or path.name == "delivery_manifest.json":
            continue
        if path.suffix in {".py", ".tcl"}:
            role = "source"
        elif path.name.endswith("tool_result.json") or path.suffix in {".log", ".jou"}:
            role = "log"
        elif path.name in {"historical_stage2a_approval_snapshot.txt", "target_resolution.json", "preflight_resource_check.json", "run_plan.json", "source_manifest.json"}:
            role = "input"
        else:
            role = "result"
        files.append(entry(path, role))
    for path in sorted((ROOT / PRIOR_REL).rglob("*")):
        if path.is_file():
            files.append(entry(path, "input"))
    for item in source["rtl_sources"]:
        path = ROOT / item["exported_repo_relative_path"]
        if sha(path) != item["exported_sha256"]:
            raise ValueError(f"受阻后源码哈希变化：{path}")
        files.append(entry(path, "source"))
    old = ROOT / source["historical_source_manifest"]["path"]
    files.append(entry(old, "input"))
    checks = [
        {"name": "14项隔离源与冻结历史OOC字节一致", "status": "PASS", "command": record["source_precheck"]["command"], "exit_code": 0},
        {"name": "实际器件解析唯一", "status": "PASS", "command": load(RUN / "target_resolution.json")["catalog_query"], "exit_code": 0},
        {"name": "实际全核心OOC综合", "status": "FAIL", "command": record["command"], "exit_code": 1, "reason": "Common 17-348/17-345：Synthesis许可已过期，目标xc7z020的有效许可未找到。"},
    ]
    for name in ("最终资源报告", "广义与LDCE/LDPE锁存器检查", "时钟风险与最差路径报告", "industrial环境设置和报告", "综合后DCP"):
        checks.append({"name": name, "status": "NOT_RUN", "command": None, "exit_code": None, "reason": "前置synth_design在许可关口返回1，本步骤尚未运行。"})
    checks.append({"name": "本次实物验证", "status": "NOT_APPLICABLE", "command": None, "exit_code": None, "reason": "本任务只含器件资料与同源OOC补验，没有硬件操作范围。"})
    return {"schema_version": 1, "stage": "2A", "task_id": "S2A-T68", "run_id": RUN_ID,
            "source_commit": source["candidate_commit"], "evidence_dir": RUN_REL.as_posix(),
            "interfaces": [source["interface_binding"]], "files": files, "checks": checks,
            "tool_versions": {"Vivado": record["vivado_version"], "Python": record["python_version"], "Git": record["git_version"]},
            "limitations": record["limitations"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-manifest", action="store_true")
    parser.add_argument("--finalize-bindings", action="store_true")
    arguments = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        if not sys.flags.isolated or Path(__file__).parent != RUN:
            raise ValueError("必须在本次精确证据目录用python -I -B运行")
        if arguments.finalize_bindings:
            prior_record = load(RUN / "execution_record.json")
            if prior_record["run_id"] != RUN_ID or prior_record["status"] != "BLOCKED_LICENSE":
                raise ValueError("只能为本次许可受阻记录补齐最终原日志绑定")
            record = make_record()
            record["recorded_at_local"] = prior_record["recorded_at_local"]
            record["finalized_at_local"] = datetime.now(UTC8).isoformat(timespec="seconds")
            (RUN / "execution_record.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            (RUN / "summary.md").write_text(make_summary(record), encoding="utf-8", newline="\n")
        elif arguments.refresh_manifest:
            record = load(RUN / "execution_record.json")
        else:
            if any((RUN / name).exists() for name in ("execution_record.json", "summary.md", "delivery_manifest.json")):
                raise FileExistsError("拒绝覆盖运行结果；新增原日志落盘后仅用--refresh-manifest更新绑定")
            record = make_record()
            write_new("execution_record.json", record)
            write_new("summary.md", make_summary(record))
        manifest = make_manifest(record)
        if arguments.refresh_manifest or arguments.finalize_bindings:
            prior = load(RUN / "delivery_manifest.json")
            if prior["run_id"] != RUN_ID or prior["source_commit"] != record["candidate_commit"]:
                raise ValueError("不能更新不同运行的清单")
            (RUN / "delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            write_new("delivery_manifest.json", manifest)
        print(json.dumps({"packaging_status": "CREATED_BLOCKED_LICENSE_EVIDENCE", "business_status": record["status"], "file_count": len(manifest["files"]), "delivery_manifest_sha256": sha(RUN / "delivery_manifest.json")}, ensure_ascii=False))
        return 0
    except Exception as error:
        print(json.dumps({"packaging_status": "FAIL_BLOCKED_EVIDENCE_BINDING", "error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
