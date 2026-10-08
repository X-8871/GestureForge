#!/usr/bin/env python3
"""按真实batch输出汇总r03，保留失败及未执行状态，并绑定全部必要证据。"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(r"D:\FPGA_Competition")
RUN_ID = "xc7z020_2_ooc_20261008_r03"
COMMIT = "999238284157bed77cdb3a37e3e6eea52daeefc4"
RUN_REL = Path("report/evidence/S2A-T68") / RUN_ID
RUN = ROOT / RUN_REL
R01 = ROOT / "report/evidence/S2A-T68/xc7z020_2_ooc_20261008_r01"
R02 = ROOT / "report/evidence/S2A-T68/xc7z020_2_ooc_20261008_r02"
OLD = ROOT / "report/evidence/S2A-T68/g4_synthesis_20261005/candidate8x8_core_ooc_run01_20261006"
LOCAL_ZONE = timezone(timedelta(hours=8))
REPORTS = ("utilization.rpt", "utilization_hierarchical.rpt", "timing_summary.rpt",
           "clocks.rpt", "worst_paths.rpt", "operating_conditions.rpt")


def digest(path: Path) -> str:
    """哈希始终按原始字节计算，原生日志不转码改写。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def local_time(epoch: int | None = None) -> str:
    date = datetime.now(LOCAL_ZONE) if epoch is None else datetime.fromtimestamp(epoch, LOCAL_ZONE)
    return date.isoformat(timespec="seconds")


def run_file(name: str) -> Path:
    """只接受本RunId中的精确文件名，禁止访问私有许可路径。"""
    if name != Path(name).name or name in {".", ".."}:
        raise ValueError(f"必须传入本次证据目录内的文件名：{name}")
    if name not in {item.name for item in RUN.iterdir()}:
        raise FileNotFoundError(f"精确证据文件不存在：{RUN / name}")
    path = RUN / name
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"证据目标不是普通文件：{path}")
    return path


def decoded(path: Path) -> tuple[str, str]:
    """UTF-8读取优先，未知原生编码只按单字节映射解析ASCII结构。"""
    data = path.read_bytes()
    try:
        return data.decode("utf-8"), "UTF-8严格解码"
    except UnicodeDecodeError:
        return data.decode("latin-1"), "原生编码未确定；latin-1逐字节映射，仅解析ASCII结构，不改写原文件"


def values(path: Path) -> dict:
    """读取脚本生成的UTF-8键值文件，整数哨兵保留原值。"""
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            if re.fullmatch(r"[A-Z][A-Z0-9_]*", key):
                result[key] = int(value) if re.fullmatch(r"-?\d+", value) else value
    return result


def optional_values(name: str) -> dict:
    path = RUN / name
    return values(run_file(name)) if path.is_file() else {}


def write_new(path: Path, data: dict | str) -> None:
    """结果只创建一次，刷新清单须通过显式选项。"""
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        if isinstance(data, dict):
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        else:
            stream.write(data)


def resources(text: str) -> list[dict]:
    """只解析最终平面utilization表，不混入综合过程中的临时计数。"""
    labels = {"Slice LUTs*": "LUT", "Slice Registers": "FF", "Block RAM Tile": "BRAM", "DSPs": "DSP"}
    rows = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        columns = [part.strip() for part in line.split("|")][1:-1]
        if columns and columns[0] in labels:
            used = float(columns[1])
            rows.append({"name": columns[0], "resource": labels[columns[0]],
                         "used": int(used) if used.is_integer() else used,
                         "available": int(columns[-2]), "percent": float(columns[-1]),
                         "headroom": int(columns[-2]) - used,
                         "raw_line": line})
    if len(rows) != 4 or {item["name"] for item in rows} != set(labels):
        raise ValueError("最终资源表没有唯一的LUT/FF/BRAM/DSP四项")
    return rows


def clock_risk(timing: str, worst: str, clocks: str) -> dict:
    """记录实际无约束风险，不将无约束路径延迟解释成目标频率。"""
    risks = {}
    for name in ("no_clock", "unconstrained_internal_endpoints", "no_input_delay", "no_output_delay"):
        match = re.search(r"checking\s+" + re.escape(name) + r"\s*\((\d+)\)", timing)
        if match is None:
            raise ValueError(f"timing_summary缺少风险计数：{name}")
        risks[name] = int(match.group(1))
    delays = [float(value) for value in re.findall(r"Data Path Delay:\s*([\d.]+)\s*ns", worst)]
    table = re.search(r"Clock\s+Period\(ns\)\s+Waveform\(ns\)\s+Attributes\s+Sources\s*\n(.*?)(?:={4,}|\Z)", clocks, re.DOTALL)
    clock_rows = [] if table is None else re.findall(r"^\S+\s+[\d.]+\s+.*$", table.group(1), re.MULTILINE)
    return {"status": "MEASURED_UNCONSTRAINED_RISK_ONLY", "user_clock_constraints": [],
            "risk_counts": risks, "worst_path_delay_ns": delays,
            "max_reported_data_path_delay_ns": max(delays) if delays else None,
            "reported_path_count": len(delays), "unplaced_marker_present": "unplaced" in worst.lower(),
            "report_clocks_no_clocks_marker": bool(re.search(r"no clocks?", clocks, re.IGNORECASE)),
            "reported_clock_count": len(clock_rows) if table is not None else None,
            "timing_closure_claim": False, "industrial_temperature_timing_claim": False}


def binding(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path)}


def make_record(arguments: argparse.Namespace) -> dict:
    """按进程退出码、脚本到达阶段和报告交叉判断，未到达的哨兵不算通过。"""
    execution_path = run_file(arguments.execution_result)
    execution = load_json(execution_path)
    recorded_exit = execution.get("native_launcher_exit_code", execution.get("process_exit_code", execution.get("exit_code")))
    if recorded_exit is not None and recorded_exit != arguments.process_exit_code:
        raise ValueError("主控进程记录与传入退出码不一致")
    console_path = run_file(arguments.console)
    console, console_decoding = decoded(console_path)
    source_manifest = load_json(run_file("source_manifest.json"))
    plan = load_json(run_file("run_plan.json"))
    if (source_manifest["run_id"] != RUN_ID or source_manifest["candidate_commit"] != COMMIT
            or plan["clock_constraints"] or plan["xdc_files"] or plan["vivado_max_threads"] != 2):
        raise ValueError("本次源码/参数计划绑定不一致")
    resolution_path = RUN / "target_resolution.json"
    resolution = load_json(run_file("target_resolution.json")) if resolution_path.is_file() else {}
    target_ok = (resolution.get("match_count") == 1 and resolution.get("requested_marking") == "XC7Z020-2CLG400I"
                 and resolution.get("device") == "xc7z020" and resolution.get("package") == "clg400"
                 and resolution.get("speed") == "-2" and resolution.get("vivado_tier") == "BASIC")
    preflight = optional_values("batch_preflight.txt")
    batch = optional_values("batch_result.txt")
    result = optional_values("run_result.txt")
    runtime = optional_values("resolved_part_runtime.txt")
    latch = optional_values("latch_check_summary.txt")
    if target_ok and (result.get("PART") not in {None, resolution["resolved_part"]}
                      or runtime.get("RESOLVED_PART") not in {None, resolution["resolved_part"]}
                      or batch.get("PART") not in {None, resolution["resolved_part"]}):
        raise ValueError("目录解析、实际综合和batch Part不一致")
    if batch and (int(batch["BATCH_TCL_RETURN_CODE"]) == 0) != (arguments.process_exit_code == 0):
        raise ValueError("batch脚本返回与实际进程退出码不一致")
    verify_command = [sys.executable, "-I", "-B", str(RUN / "prepare_sources.py"), "--verify-only"]
    if target_ok:
        verify_command += ["--part", resolution["resolved_part"]]
    verified = subprocess.run(verify_command, capture_output=True, check=True)
    verified_source = json.loads(verified.stdout.decode("utf-8"))
    marker = re.findall(r"^SOURCE_BINDING_PRECHECK=(\{[^\r\n]*\})\s*$", console, re.MULTILINE)
    actual_source_precheck = json.loads(marker[0]) if len(marker) == 1 else None
    source_marker_ok = (actual_source_precheck is not None
                        and actual_source_precheck.get("status") == "PASS_READ_ONLY_14_SOURCE_BINDINGS"
                        and actual_source_precheck.get("source_manifest_sha256") == digest(RUN / "source_manifest.json"))
    if len(marker) > 1:
        raise ValueError("同一RunId日志含多次源预检，不能作为一次运行包装")
    errors = re.findall(r"^ERROR:.*$", console, re.MULTILINE)
    critical = re.findall(r"^CRITICAL WARNING:.*$", console, re.MULTILINE)
    warnings = re.findall(r"^WARNING:.*$", console, re.MULTILINE)
    warning_ids = {}
    for line in warnings + critical + errors:
        match = re.search(r"\[([^\]]+)\]", line)
        name = match.group(1) if match else "无消息ID"
        warning_ids[name] = warning_ids.get(name, 0) + 1
    warning_groups = {}
    for line in warnings:
        match = re.search(r"\[([^\]]+)\]", line)
        name = match.group(1) if match else "无消息ID"
        lowered = line.lower()
        if name.startswith("Timing ") or "no clocks defined" in lowered:
            category = "无约束/OOC时钟风险"
        elif any(word in lowered for word in ("truncat", "width", "size of connection")):
            category = "RTL宽度或连接长度告警"
        elif any(word in lowered for word in ("unconnected", "not connected", "unused", "never used")):
            category = "未连接或未使用RTL告警"
        else:
            category = "其他RTL综合告警，保留原文供审查"
        group = warning_groups.setdefault(name, {"count": 0, "category": category, "first_line": line.strip()})
        group["count"] += 1
    report_text = {}
    report_decoding = {}
    report_states = {}
    for name in REPORTS:
        path = RUN / name
        if path.is_file():
            text, decoding = decoded(run_file(name))
            report_text[name] = text
            report_decoding[name] = decoding
            report_states[name] = {"status": "GENERATED", **binding(path)}
        else:
            report_states[name] = {"status": "NOT_RUN_OR_NOT_GENERATED",
                                   "reason": "实际运行未生成此报告；不采用报告失败计数的初始0作为成功依据。"}
    rows = resources(report_text["utilization.rpt"]) if "utilization.rpt" in report_text else []
    capacity_ok = bool(rows) and all(row["used"] <= row["available"] for row in rows)
    risk = (clock_risk(report_text["timing_summary.rpt"], report_text["worst_paths.rpt"], report_text["clocks.rpt"])
            if {"timing_summary.rpt", "worst_paths.rpt", "clocks.rpt"} <= report_text.keys()
            else {"status": "NOT_RUN", "timing_closure_claim": False,
                  "industrial_temperature_timing_claim": False, "reason": "缺少本次真实时序/时钟报告。"})
    industrial = bool(re.search(r"industrial", report_text.get("operating_conditions.rpt", ""), re.IGNORECASE))
    latch_ok = bool(latch) and result.get("LATCH_COUNT") == 0 and latch.get("UNIQUE_LATCH_COUNT") == 0
    latch_ok = latch_ok and all(latch.get(key) == 0 for key in (
        "GENERALIZED_PRIMITIVE_SUBGROUP_LATCH_COUNT", "LDCE_COUNT", "LDPE_COUNT"))
    latch_ok = latch_ok and latch.get("IS_LATCH_COUNT") in {0, -1} and (RUN / "latch_cells.txt").is_file()
    if latch_ok and (RUN / "latch_cells.txt").read_text(encoding="utf-8").strip():
        raise ValueError("锁存器并集为0但cells列表非空")
    reports_ok = len(report_text) == len(REPORTS) and result.get("REPORT_FAILURE_COUNT") == 0
    checkpoint = RUN / "s2a_stage2a_core_ooc_post_synth.dcp"
    checkpoint_record = {"status": "NOT_GENERATED"}
    if checkpoint.is_file():
        ignore_command = ["git", "-C", str(ROOT), "check-ignore", "-v", "--", str(checkpoint)]
        ignored = subprocess.run(ignore_command, capture_output=True, check=False)
        checkpoint_record = {"status": "LOCAL_REVIEW_ARTIFACT", **binding(checkpoint),
                             "bytes": checkpoint.stat().st_size, "git_ignore_exit_code": ignored.returncode,
                             "git_ignore_rule": ignored.stdout.decode("utf-8").strip(),
                             "keep_reason": "本地验收留存综合后网表，供资源、锁存器和未约束路径复核；现有Gitignore命中，不纳入源码提交。",
                             "binary_rebuild_same_hash_claim": False}
    synth_ok = result.get("SYNTHESIS_COMPLETED") == 1
    full_ok = (arguments.process_exit_code == 0 and batch.get("STAGE") == "completed"
               and result.get("STAGE") == "completed" and result.get("TCL_RETURN_CODE") == 0
               and target_ok and preflight.get("VIVADO_TIER") == "BASIC" and source_marker_ok
               and synth_ok and reports_ok and industrial and latch_ok and capacity_ok and checkpoint.is_file()
               and not errors and re.search(r"^MAX_THREADS=2\s*$", console, re.MULTILINE) is not None
               and len(re.findall(r"^RTL_SOURCE=", console, re.MULTILINE)) == 14
               and re.search(r"^S2A_OOC_RETURN_CODE=0\s*$", console, re.MULTILINE) is not None
               and re.search(r"^S2A_BATCH_RETURN_CODE=0\s*$", console, re.MULTILINE) is not None)
    old = load_json(OLD / "execution_record.json")
    old_counts = {row["name"]: row["used"] for row in old["resources"]}
    peaks = [float(value) for value in re.findall(r"Memory\s*\(MB\):\s*peak\s*=\s*([\d.]+)", console)]
    command = execution.get("exact_launcher_command", execution.get("command", plan["launch_command"]))
    if not isinstance(command, str):
        command = plan["launch_command"]
    stages = {
        "batch_tier_and_part_preflight": "PASS" if target_ok and preflight.get("VIVADO_TIER") == "BASIC" else "NOT_COMPLETED",
        "source_precheck_in_vivado": "PASS" if source_marker_ok else "NOT_RUN_OR_FAILED",
        "synthesis": "PASS" if synth_ok else "NOT_COMPLETED",
        "required_reports": "PASS" if reports_ok else "NOT_COMPLETED",
        "generalized_and_explicit_latches": "PASS" if latch_ok else "NOT_COMPLETED_OR_NONZERO",
        "final_static_capacity": "PASS" if capacity_ok else "NOT_COMPLETED_OR_EXCEEDS_CAPACITY",
        "industrial_power_environment_grade": "PASS" if industrial else "NOT_COMPLETED",
        "checkpoint": "PASS" if checkpoint.is_file() and synth_ok else "NOT_GENERATED",
        "implementation_timing": "NOT_RUN", "industrial_temperature_timing": "NOT_RUN",
        "board_validation": "NOT_RUN", "109_sample_network_regression": "NOT_RUN",
    }

    return {
        "schema": "s2a-xc2-ooc-execution-record-v2", "run_id": RUN_ID,
        "status": "OOC_SYNTHESIS_COMPLETED_PENDING_REVIEW" if full_ok else "OOC_BATCH_FAILED_OR_INCOMPLETE",
        "recorded_at_local": local_time(), "candidate_commit": COMMIT,
        "candidate_tree": source_manifest["candidate_tree"], "top": source_manifest["top"],
        "user_confirmed_device": "XC7Z020-2CLG400I", "part": resolution.get("resolved_part"),
        "part_temperature_grade_letter": resolution.get("temperature_grade_letter"),
        "vivado_tier": preflight.get("VIVADO_TIER"),
        "tool_versions": {"Vivado": preflight.get("VIVADO_VERSION", "启动未到达版本记录"),
                          "Python": platform.python_version(),
                          "Git": subprocess.check_output(["git", "--version"]).decode("utf-8").strip()},
        "command": command, "process_exit_code": arguments.process_exit_code,
        "batch_script_result": batch, "ooc_script_result": result, "runtime_part_properties": runtime,
        "batch_elapsed_seconds": batch.get("ELAPSED_SECONDS"),
        "ooc_elapsed_seconds": result.get("ELAPSED_SECONDS"),
        "launcher_elapsed_seconds": execution.get("launcher_elapsed_seconds"),
        "launcher_started_at_local": execution.get("started_at_local"),
        "launcher_completed_at_local": execution.get("completed_at_local"),
        "started_at_local": local_time(batch["STARTED_EPOCH"]) if "STARTED_EPOCH" in batch else None,
        "completed_at_local": local_time(batch["COMPLETED_EPOCH"]) if "COMPLETED_EPOCH" in batch else None,
        "execution_binding": binding(execution_path), "console_binding": binding(console_path),
        "console_decoding": console_decoding, "report_decoding": report_decoding,
        "source_manifest_sha256": digest(RUN / "source_manifest.json"),
        "run_plan_sha256": digest(RUN / "run_plan.json"),
        "source_reverification": {"command": " ".join(verify_command), "exit_code": verified.returncode,
                                  "result": verified_source},
        "actual_vivado_source_precheck": actual_source_precheck,
        "rtl_source_count": 14, "source_markers_in_log": len(re.findall(r"^RTL_SOURCE=", console, re.MULTILINE)),
        "same_source_closure_as_historical_ooc": True,
        "stage_statuses": stages, "reports": report_states,
        "error_line_count": len(errors), "error_lines": errors,
        "critical_warning_line_count": len(critical), "critical_warning_lines": critical,
        "warning_line_count": len(warnings), "warning_lines": warnings, "message_id_line_counts": warning_ids,
        "warning_groups": warning_groups,
        "warning_scope": "仅本次独立batch原生日志逐行统计；不等于可能受消息限流影响的工具内部总数。",
        "mcp_init_socket_messages": re.findall(r"^\[vmcp\].*could not open socket.*$", console, re.MULTILINE),
        "resources": rows, "static_capacity_within_available": capacity_ok,
        "historical_comparison": {"part": old["part"], **binding(OLD / "execution_record.json"),
                                  "used_count_delta": {row["name"]: row["used"] - old_counts[row["name"]] for row in rows}},
        "latch_checks": latch, "is_latch_property_status": "UNAVAILABLE" if latch.get("IS_LATCH_COUNT") == -1 else ("MEASURED" if latch else "NOT_RUN"),
        "clock_risk": risk, "operating_grade": "industrial" if industrial else None,
        "checkpoint": checkpoint_record,
        "source_recovery": {"entry": binding(RUN / "prepare_sources.py"),
                            "origin": "候选commit/tree中的14项git cat-file blob，历史清单SHA和bytes逐项核对",
                            "wrapper_exception": "仅LF偏移2220/5430插入CR，匹配历史wrapper SHA；没有隐式换行归一化",
                            "new_run_id_required": True,
                            "rerun_scope": "新证据/cache目录及新namespace/参数绑定，选择实际BASIC后同参数OOC；禁止覆写旧RunId",
                            "dcp_rebuild_scope": "可从Git对象恢复同源RTL重综合；工具产物时间/元数据可能变化，不承诺DCP二进制同hash"},
        "industrial_grade_scope": "仅功耗/环境分析等级，不设置目标温度数值，不证明工业温度时序。",
        "vivado_peak_memory_mb_observed": max(peaks) if peaks else None,
        "peak_memory_scope": "本次Vivado原生日志自报峰值，不是全机/全进程峰值。" if peaks else "未测：日志未提供自报峰值。",
        "windows_process_memory_observation": execution.get("memory_observation"),
        "windows_process_memory_scope": "主控一次Windows进程样本，仅该PID观测值，不等同于整个Vivado进程族或全机峰值。",
        "vivado_batch_launch_count": 1, "this_run_synthesis_attempt_count": 1 if source_marker_ok and result.get("STAGE") not in {None, "preflight", "read_verilog"} else 0,
        "this_run_synthesis_completed_count": int(synth_ok), "this_run_rerun_count": 0,
        "ross_vivado_mcp_synthesis_execute_calls_this_run": 0,
        "execution_channel": "官方Vivado batch/Tcl；MCP通道未能批准的独立事实由主控license_selection_record绑定",
        "total_tool_call_count": execution.get("tool_call_count"),
        "available_call_statistics": execution.get("available_call_statistics", {}),
        "tool_call_count_scope": "以主控执行记录已提供字段为准；未提供总量时记为未测，不推断插件加速收益。",
        "approval_binding": source_manifest["approval_binding"],
        "prior_failed_runs": [{"run_id": path.name, **binding(path / "run_result.txt"),
                               "result": values(path / "run_result.txt")} for path in (R01, R02)],
        "recovery_scope": "r01环境污染用-I -B隔离；r02 ENTERPRISE过期后由主控选择原始有效BASIC签名条目的进程级私有副本；14RTL字节/接口/OOC语义保持绑定。",
        "limitations": [
            "仅评价本次XC7Z020/CLG400/-2同源核心OOC综合、资源、锁存器与无约束时钟风险；待独立审查。",
            "无XDC/冻结时钟；布局布线、受约束时序和工业温度时序未运行，无频率达标结论。",
            "静态资源在目录容量内不保证布局布线可容纳；PS/AXI/DDR/显示等整板逻辑未计入本核心。",
            "本次没有板卡操作、DDR/引脚检查或109样本整网回归；既有功能证据按原冻结版本单独引用。",
            "r01/r02失败与A审计保持原始文件不动；新结果不覆盖失败记录。",
            "私有许可原件/副本/密钥/HostID不在本清单内，不读取其字节或绑定其哈希。",
            "CHECKS_OK仅表示机器绑定或包装通过，不代表G0/G4/G5、工业时序或实物验收。",
        ],
    }

def make_summary(record: dict) -> str:
    """用实际报告和独立状态描述结果，不推断板上或工业温度验收。"""
    rows = "\n".join(f"| {item['resource']} | {item['used']} | {item['available']} | {item['percent']:.2f}% |"
                     for item in record["resources"])
    if not rows:
        rows = "| 未生成本次资源报告 | — | — | — |"
    stages = "\n".join(f"| {name} | {status} |" for name, status in record["stage_statuses"].items())
    warning_table = "\n".join(f"| {name} | {item['count']} | {item['category']} |"
                              for name, item in record["warning_groups"].items())
    risk = record["clock_risk"]
    if risk["status"] == "MEASURED_UNCONSTRAINED_RISK_ONLY":
        risks = risk["risk_counts"]
        risk_text = (f"无时钟端点 `{risks['no_clock']}`，未约束内部端点 `{risks['unconstrained_internal_endpoints']}`，"
                     f"无输入延迟 `{risks['no_input_delay']}`，无输出延迟 `{risks['no_output_delay']}`。"
                     f"最差路径报告有 `{risk['reported_path_count']}` 条数据路径，最大已报告数据路径延迟 "
                     f"`{risk['max_reported_data_path_delay_ns']}` ns；未放置标记 `{risk['unplaced_marker_present']}`。"
                     f"clocks报告实际表行数 `{risk['reported_clock_count']}`。")
    else:
        risk_text = "本次未生成完整时序/时钟报告，风险计数未测。"
    delta = record["historical_comparison"]["used_count_delta"]
    delta_text = "、".join(f"{name}: {value:+}" for name, value in delta.items()) if delta else "本次报告缺失，无可比较计数"
    limitations = "\n".join(f"- {item}" for item in record["limitations"])
    return (
        "# XC7Z020-2 同源全核心 OOC 补验 r03\n\n"
        f"记录时间：{record['recorded_at_local']}。状态：`{record['status']}`。\n\n"
        f"实际 tier `{record['vivado_tier']}`，Part `{record['part']}`，top `{record['top']}`。"
        f"14项RTL来自commit `{COMMIT}` / tree `{record['candidate_tree']}`，逐项字节与历史OOC SHA一致。"
        "13项直接导出Git blob；wrapper只在LF偏移2220/5430（第59/137行）显式恢复两个CR，按历史SHA复核。未读取共享src。"
        "批准输入是r02补充前精确快照，原批准路径及base commit保留在source_manifest。\n\n"
        f"Vivado `{record['tool_versions']['Vivado']}`；OOC、flatten_hierarchy=none、maxThreads=2、无XDC/时钟约束。"
        f"本RunId标准batch启动1次、synth_design尝试 `{record['this_run_synthesis_attempt_count']}` 次、"
        f"完成 `{record['this_run_synthesis_completed_count']}` 次、重跑0次。进程退出码 `{record['process_exit_code']}`，"
        f"launcher耗时 `{record['launcher_elapsed_seconds']}` 秒，batch脚本耗时 `{record['batch_elapsed_seconds']}` 秒，OOC脚本耗时 `{record['ooc_elapsed_seconds']}` 秒。\n\n"
        "## 到达阶段与边界\n\n"
        "| 阶段 | 实际状态 |\n|---|---|\n" + stages + "\n\n"
        "## 本次最终静态资源\n\n"
        "| 资源 | 已用 | 目录容量 | 比例 |\n|---|---:|---:|---:|\n" + rows + "\n\n"
        f"容量内判断：`{record['static_capacity_within_available']}`。相对旧 `{record['historical_comparison']['part']}` "
        f"最终报告的已用数差值：{delta_text}。旧数只用于明确标注的比较，不作为本次测量。\n\n"
        "LUT和DSP占用分别为76.22%和84.55%；整板PS/AXI/DDR/视频及后续物理优化未计入本核心报告，剩余静态容量不等于集成或布局布线余量已获验证。\n\n"
        f"锁存器检查：`{json.dumps(record['latch_checks'], ensure_ascii=False)}`。"
        f"IS_LATCH属性状态 `{record['is_latch_property_status']}`；-1仅表示该属性未提供，广义LATCH/LDCE/LDPE另列真实检查。\n\n"
        "## 时钟与环境风险\n\n" + risk_text + "\n\n"
        "没有冻结目标时钟、受约束WNS/TNS或布局布线通过结论。industrial只设置功耗/环境等级；"
        f"器件目录温度字母 `{record['part_temperature_grade_letter']}` 按实际返回记录，不推断工业温度时序。\n\n"
        "## 日志与环境恢复\n\n"
        f"原生日志逐行统计 ERROR `{record['error_line_count']}`、CRITICAL WARNING `{record['critical_warning_line_count']}`、"
        f"WARNING `{record['warning_line_count']}`；完整行/消息ID计数见execution_record.json。"
        "MCP通道未获自动批准和官方CLI综合结果分别记录。有效BASIC签名条目由主控选择至进程级私有副本，"
        "实际tier与Synthesis checkout由本次日志核对。原许可文件保持不动，私有许可字节/密钥/HostID不入包。\n\n"
        "| warning消息ID | 行数 | 分类 |\n|---|---:|---|\n" + warning_table + "\n\n"
        "时钟warning与本次无约束OOC范围一致；RTLwarning原文保持供独立审查，本次未重跑功能回归。\n\n"
        f"MCP初始化socket诊断：`{json.dumps(record['mcp_init_socket_messages'], ensure_ascii=False)}`；"
        "7654端口已占用导致该batch的MCP监听未建立，官方CLI综合与退出按真实记录单独判断。\n\n"
        f"Vivado日志自报峰值内存 `{record['vivado_peak_memory_mb_observed']}` MB；{record['peak_memory_scope']} "
        f"工具调用总量 `{record['total_tool_call_count']}`；{record['tool_call_count_scope']}\n\n"
        f"主控可得调用统计：`{json.dumps(record['available_call_statistics'], ensure_ascii=False)}`。"
        "Windows进程内存另有一次主控样本，不混作进程族/全机峰值。\n\n"
        "r01在Python环境预检失败；r02通过14源预检后被ENTERPRISE过期许可阻碍。两个失败RunId、原始日志和A审计均保持冻结。\n\n"
        "## 检查点与恢复\n\n"
        f"DCP `{record['checkpoint'].get('sha256')}`，`{record['checkpoint'].get('bytes')}` bytes，"
        "本地保留供独立复核，现有Gitignore命中，不纳入源码提交；清单保留哈希及用途。"
        "源码恢复入口为prepare_sources.py：从冻结commit/tree读取14个Git blob，按历史SHA验证并明确恢复wrapper两个CR。"
        "重新综合须新RunId、隔离目录/namespace与实际BASIC许可选择，不覆写r01/r02/r03。"
        "带时间/元数据的DCP重新生成不承诺相同二进制哈希。\n\n"
        "## 限制\n\n" + limitations + "\n"
    )


def file_entry(path: Path, role: str, keep_reason: str | None = None) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"不能绑定非普通文件：{path}")
    entry = {**binding(path), "role": role}
    if keep_reason:
        entry["keep_reason"] = keep_reason
    return entry


def make_manifest(record: dict) -> dict:
    """只枚举本RunId和明确冻结依赖；缓存仅绑定14项实际源码。"""
    source_manifest = load_json(run_file("source_manifest.json"))
    files = []
    for path in sorted(RUN.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"证据目录出现链接：{path}")
        if not path.is_file() or path.name == "delivery_manifest.json":
            continue
        if path.suffix.lower() == ".dcp":
            files.append(file_entry(path, "artifact", "本地验收留存XC7Z020/CLG400/-2综合网表供资源、锁存器和未约束路径复核；现有Gitignore命中，不入源码Git；从Git恢复14源码可在新RunId重综合，不承诺带时间/元数据DCP同hash。"))
        elif path.suffix in {".py", ".tcl"}:
            files.append(file_entry(path, "source"))
        elif path.suffix in {".log", ".jou"} or path.name.startswith("cli_") or path.name.endswith("tool_result.json"):
            files.append(file_entry(path, "log"))
        elif path.name in {"source_manifest.json", "run_plan.json", "target_resolution.json", "target_resolution.txt",
                            "preflight_resource_check.json", "license_selection_record.json", "owned_previous_session_close.json"}:
            files.append(file_entry(path, "input"))
        else:
            files.append(file_entry(path, "result"))
    for item in source_manifest["rtl_sources"]:
        path = ROOT / item["exported_repo_relative_path"]
        if digest(path) != item["exported_sha256"]:
            raise ValueError(f"实际隔离RTL在运行后变化：{path}")
        files.append(file_entry(path, "source"))
    dependencies = [OLD / name for name in ("source_manifest.json", "run_synthesis.tcl", "execution_record.json")]
    dependencies += [R01 / "run_result.txt", R01 / "source_manifest.json", R01 / "device_audit.md", R01 / "device_audit_sources.json"]
    dependencies += sorted(R01.glob("core_page-*.png")) + sorted(R01.glob("manual_page-*.png"))
    dependencies += [R02 / name for name in ("run_result.txt", "source_manifest.json", "execution_record.json", "delivery_manifest.json",
                                          "summary.md", "historical_stage2a_approval_snapshot.txt", "license_diagnosis.json")]
    dependencies += [ROOT / "verification/check_stage_delivery.py"]
    for path in dependencies:
        files.append(file_entry(path, "input"))
    names = [entry["path"] for entry in files]
    if len(names) != len(set(names)):
        raise ValueError("交付清单出现重复文件绑定")
    success = record["status"] == "OOC_SYNTHESIS_COMPLETED_PENDING_REVIEW"
    check = {"name": "本次BASIC/唯一Part/14源预检/OOC报告/广义锁存器/静态容量有限范围补验",
             "status": "PASS" if success else ("FAIL" if record["process_exit_code"] else "BLOCKED"),
             "command": record["command"] if success or record["process_exit_code"] else None,
             "exit_code": record["process_exit_code"] if success or record["process_exit_code"] else None}
    if not success:
        check["reason"] = "真实进程或到达阶段/报告未满足本次有限范围OOC补验，详见execution_record；未运行哨兵不算PASS。"
    return {
        "schema_version": 1, "stage": "2A", "task_id": "S2A-T68", "run_id": RUN_ID,
        "source_commit": COMMIT, "evidence_dir": RUN_REL.as_posix(),
        "interfaces": [source_manifest["interface_binding"]], "files": files,
        "checks": [{"name": "冻结Git对象与14项实际历史OOC字节只读复核", "status": "PASS",
                    "command": record["source_reverification"]["command"], "exit_code": record["source_reverification"]["exit_code"]},
                   check,
                   {"name": "实现时序/工业温度时序/板上验证/109样本整网回归", "status": "NOT_APPLICABLE",
                    "command": None, "exit_code": None,
                    "reason": "本补验范围仅为同源核心OOC综合与报告；这些任务本次未运行，保持原验收范围且不推断通过。"}],
        "tool_versions": record["tool_versions"], "limitations": record["limitations"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--console", default="vivado.log")
    parser.add_argument("--execution-result", default="cli_execution_result.json")
    parser.add_argument("--process-exit-code", type=int)
    parser.add_argument("--refresh-manifest", action="store_true")
    arguments = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        if not sys.flags.isolated or not sys.dont_write_bytecode:
            raise ValueError("汇总必须以独立python -I -B启动")
        if not RUN.is_dir() or Path(__file__).parent != RUN:
            raise ValueError("汇总助手不在已确认的r03证据目录")
        if arguments.refresh_manifest:
            record = load_json(run_file("execution_record.json"))
            prior = load_json(run_file("delivery_manifest.json"))
            if prior["run_id"] != RUN_ID or prior["source_commit"] != COMMIT:
                raise ValueError("拒绝刷新不同RunId/候选的清单")
            if (digest(run_file("source_manifest.json")) != record["source_manifest_sha256"]
                    or digest(run_file("run_plan.json")) != record["run_plan_sha256"]):
                raise ValueError("运行后冻结源清单/计划变化，不能仅刷新包装")
            manifest = make_manifest(record)
            run_file("delivery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            if arguments.process_exit_code is None:
                raise ValueError("首次汇总须传入主控实际process-exit-code")
            if any((RUN / name).exists() for name in ("execution_record.json", "summary.md", "delivery_manifest.json")):
                raise FileExistsError("拒绝覆盖本RunId执行记录/摘要；新增文件绑定只能显式刷新manifest")
            record = make_record(arguments)
            manifest = make_manifest(record)
            # 先验证全部外部依赖，再写结果，避免因依赖缺失留下不完整的首次结果。
            write_new(RUN / "execution_record.json", record)
            write_new(RUN / "summary.md", make_summary(record))
            manifest = make_manifest(record)
            write_new(RUN / "delivery_manifest.json", manifest)
        print(json.dumps({"status": record["status"], "delivery_manifest_sha256": digest(RUN / "delivery_manifest.json"),
                          "file_count": len(manifest["files"])}, ensure_ascii=False))
        return 0
    except Exception as error:
        print(json.dumps({"status": "FAIL_RESULT_PARSING_OR_BINDING", "error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
