#!/usr/bin/env python3
"""从本次真实 OOC 报告构建有限范围总结和统一交付清单。"""

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
COMMIT = "999238284157bed77cdb3a37e3e6eea52daeefc4"
RUN_REL = Path("report/evidence/S2A-T68") / RUN_ID
RUN = ROOT / RUN_REL
PRIOR_REL = Path("report/evidence/S2A-T68/xc7z020_2_ooc_20261008_r01")
OLD_REL = Path("report/evidence/S2A-T68/g4_synthesis_20261005/candidate8x8_core_ooc_run01_20261006")


def digest(path: Path) -> str:
    """按实际原始字节绑定文件。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def now_local() -> str:
    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def text_file(name: str) -> str:
    path = RUN / name
    if not path.is_file():
        raise FileNotFoundError(f"本次必要报告不存在：{path}")
    return path.read_text(encoding="utf-8")


def load_json_or_key_values(path: Path) -> dict:
    """保留先前失败 RunId 的真实返回信息，不以成功记录覆盖。"""
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = int(value) if re.fullmatch(r"-?\d+", value) else value
    return result


def integer_fields(name: str) -> dict:
    """解析 Tcl 生成的键值文件，保留正文消息。"""
    result = {}
    for line in text_file(name).splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            result[key] = int(value) if re.fullmatch(r"-?\d+", value) else value
    return result


def write_new(path: Path, data: dict | str) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        if isinstance(data, dict):
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        else:
            stream.write(data)


def resource_rows() -> list[dict]:
    """只消费最终平面资源报告，不混用中间综合计数。"""
    names = {"Slice LUTs*", "Slice Registers", "Block RAM Tile", "DSPs"}
    rows = []
    for line in text_file("utilization.rpt").splitlines():
        if not line.startswith("|"):
            continue
        columns = [part.strip() for part in line.split("|")][1:-1]
        if columns and columns[0] in names:
            rows.append({"name": columns[0], "used": int(columns[1]),
                         "available": int(columns[-2]), "percent": float(columns[-1]),
                         "raw_line": line})
    if len(rows) != 4 or {row["name"] for row in rows} != names:
        raise ValueError("不能唯一解析最终 LUT/FF/BRAM/DSP 四项资源")
    return rows


def count_risk(text: str, name: str) -> int:
    match = re.search(r"checking\s+" + re.escape(name) + r"\s*\((\d+)\)", text)
    if not match:
        raise ValueError(f"时钟风险字段未找到：{name}")
    return int(match.group(1))


def make_record(arguments: argparse.Namespace) -> dict:
    """同时校验独立原始报告、运行码和实际源哈希。"""
    source_manifest = load_json(RUN / "source_manifest.json")
    resolution = load_json(RUN / "target_resolution.json")
    if resolution["match_count"] != 1 or resolution["requested_marking"] != "XC7Z020-2CLG400I":
        raise ValueError("主控实际 Part 解析不满足本次目标")
    verify_command = [sys.executable, "-I", "-B", str(RUN / "prepare_sources.py"),
                      "--verify-only", "--part", resolution["resolved_part"]]
    verified = subprocess.run(verify_command, capture_output=True, check=True)
    source_result = json.loads(verified.stdout.decode("utf-8"))
    result = integer_fields("run_result.txt")
    latch = integer_fields("latch_check_summary.txt")
    runtime = integer_fields("resolved_part_runtime.txt")
    console_path = RUN / arguments.console
    console = text_file(arguments.console)
    start_marker = console.find("SOURCE_BINDING_PRECHECK=")
    end_marker = console.rfind("S2A_OOC_RETURN_CODE=" + str(result["TCL_RETURN_CODE"]))
    if start_marker < 0 or end_marker < start_marker:
        raise ValueError("原始控制台缺少本次成功预检与返回标记，不能证明完整运行范围")
    command_console = console[start_marker:end_marker + len("S2A_OOC_RETURN_CODE=") + 1]
    if result["PART"] != resolution["resolved_part"] or runtime["RESOLVED_PART"] != result["PART"]:
        raise ValueError("实际综合 Part 与目录解析不一致")
    if result["TCL_RETURN_CODE"] != arguments.tool_exit_code:
        raise ValueError("实际 Tcl 返回码与主控工具返回码不一致")
    if not re.search(r"S2A_OOC_RETURN_CODE=" + str(result["TCL_RETURN_CODE"]) + r"\b", console):
        raise ValueError("原始综合控制台缺少完整返回标记")
    errors = re.findall(r"^ERROR:.*$", command_console, re.MULTILINE)
    critical = re.findall(r"^CRITICAL WARNING:.*$", command_console, re.MULTILINE)
    warnings = re.findall(r"^WARNING:.*$", command_console, re.MULTILINE)
    resources = resource_rows()
    old = load_json(ROOT / OLD_REL / "execution_record.json")
    old_counts = {row["name"]: row["used"] for row in old["resources"]}
    timing = text_file("timing_summary.rpt")
    worst = text_file("worst_paths.rpt")
    delays = [float(value) for value in re.findall(r"Data Path Delay:\s*([\d.]+)\s*ns", worst)]
    if not delays:
        raise ValueError("最差路径报告没有数据路径延迟")
    operating = text_file("operating_conditions.rpt")
    if not re.search(r"industrial", operating, re.IGNORECASE):
        raise ValueError("实际环境报告没有确认 industrial 等级")
    peak = [float(value) for value in re.findall(r"Memory\s*\(MB\):\s*peak\s*=\s*([\d.]+)", command_console)]
    capacity_ok = all(row["used"] <= row["available"] for row in resources)
    nominal_success = (arguments.tool_exit_code == 0 and result["SYNTHESIS_COMPLETED"] == 1
                       and result["REPORT_FAILURE_COUNT"] == 0 and latch["UNIQUE_LATCH_COUNT"] == 0
                       and result["LATCH_COUNT"] == 0 and not errors and capacity_ok)
    version_match = re.search(r"^VIVADO_VERSION=(.*)$", text_file("target_resolution.txt"), re.MULTILINE)
    if not version_match:
        raise ValueError("实际目录查询日志缺少 Vivado 版本")
    command = f"set ::s2a_target_part {{{resolution['resolved_part']}}}; source -encoding utf-8 {{{RUN / 'run_synthesis.tcl'}}}"
    return {
        "schema": "s2a-xc2-ooc-execution-record-v1", "run_id": RUN_ID,
        "status": "OOC_SYNTHESIS_COMPLETED_PENDING_REVIEW" if nominal_success else "OOC_SYNTHESIS_FAILED",
        "recorded_at_local": now_local(),
        "candidate_commit": COMMIT, "candidate_tree": source_manifest["candidate_tree"],
        "top": source_manifest["top"], "part": result["PART"],
        "user_confirmed_device": resolution["requested_marking"],
        "part_temperature_grade_letter": resolution["temperature_grade_letter"],
        "operating_grade": "industrial", "industrial_temperature_timing_claim": False,
        "started_at_local": datetime.fromtimestamp(result["STARTED_EPOCH"], timezone(timedelta(hours=8))).isoformat(),
        "completed_at_local": datetime.fromtimestamp(result["COMPLETED_EPOCH"], timezone(timedelta(hours=8))).isoformat(),
        "tcl_elapsed_seconds": result["ELAPSED_SECONDS"],
        "mcp_command_exit_code": arguments.tool_exit_code,
        "tcl_return_code": result["TCL_RETURN_CODE"], "command": command,
        "synthesis_run_count": 1, "synthesis_reruns": 0,
        "synthesis_execute_tool_calls": 1, "ross_total_tool_call_count": None,
        "ross_total_tool_call_count_measurement": "本汇总未测；主控会话原始执行记录另行保留。",
        "vivado_version": version_match.group(1).strip(),
        "python_version": platform.python_version(),
        "git_version": subprocess.check_output(["git", "--version"]).decode("utf-8").strip(),
        "source_manifest_sha256": digest(RUN / "source_manifest.json"),
        "run_synthesis_tcl_sha256": digest(RUN / "run_synthesis.tcl"),
        "console_binding": {"path": (RUN_REL / arguments.console).as_posix(), "sha256": digest(console_path)},
        "source_precheck": {"command": " ".join(verify_command), "exit_code": verified.returncode,
                            "result": source_result},
        "rtl_source_count": source_manifest["rtl_source_count"],
        "same_source_closure_as_historical_ooc": True,
        "error_line_count": len(errors), "error_lines": errors,
        "critical_warning_line_count": len(critical), "critical_warning_lines": critical,
        "warning_line_count": len(warnings), "warning_lines": warnings,
        "warning_count_scope": "仅逐行统计绑定原日志中本次SOURCE_BINDING_PRECHECK至其返回标记；原日志可能保留r01与会话初始化输出，不混计；不等同于可能经限流的工具内部总数。",
        "latch_checks": latch, "report_generation_failures": result["REPORT_FAILURE_COUNT"],
        "resources": resources, "nominal_resource_counts_within_available": capacity_ok,
        "historical_comparison": {"part": old["part"], "execution_record_sha256": digest(ROOT / OLD_REL / "execution_record.json"),
                                  "used_count_delta": {row["name"]: row["used"] - old_counts[row["name"]] for row in resources}},
        "clock_risk": {"user_constraints_present": False,
                       "no_clock_register_pins": count_risk(timing, "no_clock"),
                       "unconstrained_internal_endpoints": count_risk(timing, "unconstrained_internal_endpoints"),
                       "input_ports_without_delay": count_risk(timing, "no_input_delay"),
                       "output_ports_without_delay": count_risk(timing, "no_output_delay"),
                       "max_reported_unconstrained_data_path_delay_ns": max(delays),
                       "reported_worst_path_count": len(delays), "unplaced_paths": "unplaced" in worst,
                       "timing_closure_claim": False},
        "vivado_peak_memory_mb_observed": max(peak) if peak else None,
        "peak_memory_scope": "原始控制台中 Vivado 自报峰值；不是本机全进程或系统峰值。" if peak else "未测：原始控制台没有 Vivado 峰值字段。",
        "initial_preparation_diagnosis": load_json(RUN / "source_binding_result.json")["top_wrapper_mixed_crlf_diagnosis"],
        "approval_binding": source_manifest["approval_binding"],
        "prior_failed_run_id": "xc7z020_2_ooc_20261008_r01",
        "prior_failed_run_result": load_json_or_key_values(ROOT / PRIOR_REL / "run_result.txt"),
        "recovery_scope": "r01因Vivado继承的PYTHONHOME/PYTHONPATH使独立Python3.12加载错误re模块，源读取/综合尚未开始；r02仅隔离Python环境和显式UTF-8加载，14RTL字节与综合语义不变。",
        "isolated_python": bool(sys.flags.isolated),
        "limitations": ["本次只补验新选择器件的同源全核心 OOC 综合；待独立审查。",
                        "无 XDC/冻结时钟，未运行布局布线，不证明 timing closure、频率或工业温度时序。",
                        "最终静态资源计数在器件容量内不保证布局布线可容纳；PS/AXI/DDR与显示等整板逻辑未计入本核心。",
                        "本次没有板卡操作、DDR/引脚检查或109样本整网重跑；既有功能证据须按原冻结版本单独引用。",
                        "CHECKS_OK 只表示绑定和证据包装通过，不代表 G0/G4/G5 或实物验收。"],
    }


def make_summary(record: dict) -> str:
    """报告计数和风险，不外推阶段或实物通过。"""
    rows = "\n".join(f"| {item['name']} | {item['used']} | {item['available']} | {item['percent']:.2f}% |" for item in record["resources"])
    risk = record["clock_risk"]
    return (
        "# XC7Z020-2 同源全核心 OOC 补验\n\n"
        f"记录时间：{record['recorded_at_local']}。状态：`{record['status']}`。\n\n"
        f"实际 Part 为 `{record['part']}`，top 为 `{record['top']}`；14 项 RTL 从 commit `{COMMIT}` / tree `{record['candidate_tree']}` 导出，与历史 OOC 源字节逐项一致。"
        "13 项直接复制 Git 字节；顶层 wrapper 仅在 Git LF 偏移 2220/5430（第59/137行）显式恢复 CR，9316 种两处组合只有这一项匹配旧 SHA。未读取共享 src。\n\n"
        f"Vivado `{record['vivado_version']}`，maxThreads=2，OOC、flatten_hierarchy=none；综合运行1次、重跑0次，Tcl耗时 {record['tcl_elapsed_seconds']} 秒，返回码 {record['tcl_return_code']}。"
        f"原始控制台观察到 {record['error_line_count']} 条 ERROR、{record['critical_warning_line_count']} 条 CRITICAL WARNING、{record['warning_line_count']} 条 WARNING；完整行保存在 execution_record.json。广义分组/可用IS_LATCH/LDCE/LDPE并集锁存器数 {record['latch_checks']['UNIQUE_LATCH_COUNT']}，报告失败数 {record['report_generation_failures']}。\n\n"
        "| 最终资源 | 已用 | 目录容量 | 比例 |\n|---|---:|---:|---:|\n" + rows + "\n\n"
        f"无时钟寄存器/锁存器端 {risk['no_clock_register_pins']}，未约束内部端点 {risk['unconstrained_internal_endpoints']}，无输入延迟端口 {risk['input_ports_without_delay']}，无输出延迟端口 {risk['output_ports_without_delay']}。"
        f"未约束最差报告路径数据延迟最大 {risk['max_reported_unconstrained_data_path_delay_ns']:.3f} ns，路径未放置；没有受约束 WNS/TNS 的达标结论。\n\n"
        "`set_operating_conditions -grade industrial` 与实际 operating_conditions.rpt 仅记录功耗/环境等级。器件目录的温度等级字母为空，不能作为工业温度时序证明。"
        "[AMD UG835](https://docs.amd.com/r/en-US/ug835-vivado-tcl-commands/set_operating_conditions)。\n\n"
        f"Vivado 自报峰值内存 MB：`{record['vivado_peak_memory_mb_observed']}`；{record['peak_memory_scope']} 总 ROSS 工具调用次数本汇总未测，主控原始记录另存。\n\n"
        + "\n".join(f"- {item}" for item in record["limitations"]) + "\n"
    )


def file_entry(path: Path, role: str, keep_reason: str | None = None) -> dict:
    item = {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path), "role": role}
    if keep_reason:
        item["keep_reason"] = keep_reason
    return item


def make_manifest(record: dict) -> dict:
    """枚举本 RunId 完整证据；可重建缓存仅以实际源码文件绑定。"""
    source_manifest = load_json(RUN / "source_manifest.json")
    files = []
    for path in sorted(RUN.rglob("*")):
        if not path.is_file() or path.name == "delivery_manifest.json":
            continue
        if path.suffix == ".dcp":
            files.append(file_entry(path, "artifact", "保留本次目标器件综合后网表，供资源、锁存器和未约束路径独立复核。"))
            continue
        if path.suffix in {".py", ".tcl"}:
            role = "source"
        elif path.name.endswith("tool_result.json") or path.suffix in {".log", ".jou"}:
            role = "log"
        elif path.suffix in {".png", ".jpg"} or path.name in {"device_audit.md", "target_resolution.json", "target_resolution.txt", "run_plan.json", "source_manifest.json", "preflight_resource_check.json"}:
            role = "input"
        else:
            role = "result"
        files.append(file_entry(path, role))
    for item in source_manifest["rtl_sources"]:
        path = ROOT / item["exported_repo_relative_path"]
        if digest(path) != item["exported_sha256"]:
            raise ValueError(f"实际综合源码在运行后变化：{path}")
        files.append(file_entry(path, "source"))
    for name in ("source_manifest.json", "execution_record.json", "run_synthesis.tcl"):
        files.append(file_entry(ROOT / OLD_REL / name, "input"))
    # 既有 A 审计、页图、器件解析与失败运行原始材料作为输入依赖，保持 r01 不动。
    for path in sorted((ROOT / PRIOR_REL).rglob("*")):
        if path.is_file():
            files.append(file_entry(path, "input"))
    command = record["command"]
    success = record["status"] == "OOC_SYNTHESIS_COMPLETED_PENDING_REVIEW"
    return {
        "schema_version": 1, "stage": "2A", "task_id": "S2A-T68", "run_id": RUN_ID,
        "source_commit": COMMIT, "evidence_dir": RUN_REL.as_posix(),
        "interfaces": [source_manifest["interface_binding"]], "files": files,
        "checks": [
            {"name": "14项候选Git源闭包与历史OOC字节一致", "status": "PASS",
             "command": record["source_precheck"]["command"], "exit_code": record["source_precheck"]["exit_code"]},
            {"name": "实际get_parts解析唯一器件", "status": "PASS",
             "command": load_json(RUN / "target_resolution.json")["catalog_query"], "exit_code": 0},
            {"name": "同源OOC综合、报告、锁存器和最终静态容量",
             "status": "PASS" if success else ("FAIL" if record["tcl_return_code"] else "BLOCKED"),
             "command": command if success or record["tcl_return_code"] else None,
             "exit_code": record["tcl_return_code"] if success or record["tcl_return_code"] else None,
             **({} if success else {"reason": "真实报告或运行码未满足同源OOC限定验收；详见execution_record。"})},
            {"name": "本次实物验证", "status": "NOT_APPLICABLE", "command": None, "exit_code": None,
             "reason": "本任务仅是器件目录和OOC补验，没有上板或硬件操作范围。"},
        ],
        "tool_versions": {"Vivado": record["vivado_version"], "Python": record["python_version"], "Git": record["git_version"]},
        "limitations": record["limitations"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--console", default="synthesis_console.log")
    parser.add_argument("--tool-exit-code", type=int, required=True)
    parser.add_argument("--refresh-manifest", action="store_true")
    arguments = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        if not sys.flags.isolated:
            raise ValueError("汇总助手必须以 python -I -B 启动")
        if not RUN.is_dir() or Path(__file__).parent != RUN:
            raise ValueError("结果解析脚本不在已确认的本次证据目录")
        if arguments.refresh_manifest:
            record = load_json(RUN / "execution_record.json")
        else:
            record = make_record(arguments)
            if any((RUN / name).exists() for name in ("execution_record.json", "summary.md", "delivery_manifest.json")):
                raise FileExistsError("拒绝覆盖本次运行结果；新增文件绑定仅用--refresh-manifest")
            write_new(RUN / "execution_record.json", record)
            write_new(RUN / "summary.md", make_summary(record))
        manifest = make_manifest(record)
        path = RUN / "delivery_manifest.json"
        if arguments.refresh_manifest:
            prior = load_json(path)
            if prior["run_id"] != RUN_ID or prior["source_commit"] != COMMIT:
                raise ValueError("拒绝改写不同运行或候选的清单")
            path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            write_new(path, manifest)
        print(json.dumps({"status": record["status"], "delivery_manifest_sha256": digest(path),
                          "file_count": len(manifest["files"])}, ensure_ascii=False))
        return 0
    except Exception as error:
        print(json.dumps({"status": "FAIL_RESULT_PARSING_OR_BINDING", "error": str(error)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
