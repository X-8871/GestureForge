#!/usr/bin/env python3
"""在隔离目录中运行S2C 32 lane候选OOC综合，并绑定证据与报告。"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ROOT = Path("D:/FPGA_Competition/w2c")
BASELINE_COMMIT = "8856a2cd35eda0269ad5cc0178955013902688f6"
RTL_COMMIT = "3dfac02277c13d68c1adcfc4ea057025179c62b2"
TCL_PATH = "vivado/s2c_lane32_ooc.tcl"
EXPECTED_TCL_SHA256 = "c783b82251fbe1a30795cc4086a244b30b15c8b0506f25d1d13cd30858660a71"
VIVADO = Path("D:/Xilinx/2026.1/Vivado/bin/vivado.bat")
MIN_FREE_BYTES = 6 * 1024**3
POLL_SECONDS = 30
COMPLETION_MARKER = "S2C_LANE32_OOC:COMPLETED_REPORTS_NOT_ACCEPTANCE"
REPORT_NAMES = (
    "utilization.rpt",
    "utilization_hierarchical.rpt",
    "timing_summary.rpt",
    "methodology.rpt",
    "clock_100mhz.xdc",
)
HEAVY_PROCESS_NAMES = {
    "vivado.exe", "vivado_lab.exe", "xsim.exe", "xsimk.exe", "xelab.exe",
    "xvlog.exe", "xvhdl.exe", "hw_server.exe", "xsdb.exe", "vitis.exe",
    "vitis_hls.exe",
}


def sha256(path: Path) -> str:
    """以流式方式计算文件的磁盘字节SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> str:
    """执行只读Git查询，失败时中止。"""
    done = subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True,
        check=False, text=True, encoding="utf-8", errors="replace", timeout=30,
    )
    if done.returncode != 0:
        raise RuntimeError(f"Git查询失败 exit={done.returncode}: {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout.strip()


def tracked_inputs() -> tuple[list[str], dict[str, Any]]:
    """从候选平台JSON读取21个RTL源，并核对Tcl实际读入顺序。"""
    profile_path = ROOT / "board/s2b_inference_platform.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    sources = profile.get("rtl_sources")
    if not isinstance(sources, list) or len(sources) != 21 or not all(isinstance(x, str) for x in sources):
        raise ValueError("board平台必须声明21个RTL源")
    if profile.get("vivado_part") != "xc7z020clg400-2" or profile.get("clock_hz") != 100000000:
        raise ValueError("平台器件或时钟与S2C OOC候选不符")
    if profile.get("candidate_generics") != {"CONV_OUTPUT_LANES": 32, "ENABLE_BULK": 1}:
        raise ValueError("平台候选generics与32 lane成段版本不符")

    platform_tcl_path = ROOT / "vivado/s2b_inference_platform.tcl"
    platform_tcl = platform_tcl_path.read_text(encoding="utf-8")
    match = re.search(r"variable rtl_sources \{(.*?)\n\s*\}", platform_tcl, re.S)
    if match is None or match.group(1).split() != sources:
        raise ValueError("board JSON与平台Tcl中的RTL源清单/顺序不一致")

    extra = [
        TCL_PATH,
        "vivado/s2b_inference_platform.tcl",
        "vivado/s2b_ps_platform.tcl",
        "board/s2b_inference_platform.json",
        "board/ps_platform_fields.json",
        "verification/check_s2c_inference_platform.py",
        "verification/check_s2b_inference_platform.py",
    ]
    physical_doc = profile.get("physical_interface_document")
    if not isinstance(physical_doc, str) or not physical_doc:
        raise ValueError("board JSON缺少物理接口文档路径")
    extra.append(physical_doc)
    all_paths = list(dict.fromkeys(sources + extra + ["verification/run_s2c_lane32_ooc.py"]))
    for relative in all_paths:
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            raise ValueError(f"输入路径必须是仓库内相对路径：{relative}")
        if not (ROOT / relative).is_file():
            raise FileNotFoundError(f"候选输入文件不存在：{relative}")
    if sha256(ROOT / TCL_PATH) != EXPECTED_TCL_SHA256:
        raise ValueError("OOC Tcl SHA与已审版本不一致")
    return all_paths, profile


def powershell_json(script: str, timeout: int = 30) -> dict[str, Any]:
    """运行只读PowerShell/CIM查询；查询失败时拒绝继续。"""
    command = (
        "$ErrorActionPreference='Stop'; "
        "[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false); " + script
    )
    done = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True, check=False, text=True, encoding="utf-8", errors="replace", timeout=timeout,
    )
    if done.returncode != 0:
        raise RuntimeError(f"PowerShell/CIM查询失败 exit={done.returncode}: {done.stderr.strip()}")
    parsed = json.loads(done.stdout)
    if not isinstance(parsed, dict):
        raise ValueError("PowerShell/CIM输出不是对象")
    return parsed


def resource_snapshot() -> dict[str, Any]:
    """检查全机Vivado类进程并读取可用物理内存。"""
    names = ",".join(f"'{name}'" for name in sorted(HEAVY_PROCESS_NAMES))
    script = (
        f"$names=@({names}); "
        "$all=@(Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,WorkingSetSize,UserModeTime,KernelModeTime); "
        "$p=@($all | Where-Object { $names -contains $_.Name.ToLowerInvariant() }); "
        "$o=Get-CimInstance Win32_OperatingSystem; "
        "if($null -eq $o.FreePhysicalMemory -or $null -eq $o.TotalVisibleMemorySize){throw 'MEMORY_QUERY_MISSING'}; "
        "@{processes=$p;all_processes=$all;available_bytes=([long]$o.FreePhysicalMemory*1024);"
        "total_bytes=([long]$o.TotalVisibleMemorySize*1024)} | ConvertTo-Json -Depth 5 -Compress"
    )
    snapshot = powershell_json(script)
    if isinstance(snapshot.get("processes"), dict):
        snapshot["processes"] = [snapshot["processes"]]
    if isinstance(snapshot.get("all_processes"), dict):
        snapshot["all_processes"] = [snapshot["all_processes"]]
    if not isinstance(snapshot.get("processes"), list) or not isinstance(snapshot.get("all_processes"), list):
        raise ValueError("CIM进程清单缺失")
    if not isinstance(snapshot.get("available_bytes"), int) or not isinstance(snapshot.get("total_bytes"), int):
        raise ValueError("CIM内存字段缺失")
    return snapshot


def file_entry(relative: str, role: str) -> dict[str, str]:
    path = ROOT / relative
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path),
            "hash_basis": "worktree_disk", "role": role}


def snapshot_inputs(paths: list[str], evidence: Path) -> list[dict[str, str]]:
    """将Tcl、RTL、平台档案及检查器按仓库相对目录冻结到证据目录。"""
    snapshot_root = evidence / "source_snapshot"
    entries: list[dict[str, str]] = []
    for relative in paths:
        source = ROOT / relative
        target = snapshot_root / Path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        digest = sha256(target)
        if digest != sha256(source):
            raise RuntimeError(f"冻结源快照与源文件不一致：{relative}")
        entries.append({"path": target.relative_to(ROOT).as_posix(), "source_path": relative,
                        "sha256": digest, "hash_basis": "worktree_disk", "role": "source_snapshot"})
    return entries


def check_source_integrity(entries: list[dict[str, str]]) -> dict[str, Any]:
    """逐项核对活动工作树文件与持久快照，缺失或哈希漂移均失败。"""
    mismatches = []
    for entry in entries:
        live = ROOT / entry["source_path"]
        snapshot = ROOT / entry["path"]
        expected = entry["sha256"]
        for label, path in (("live", live), ("snapshot", snapshot)):
            try:
                actual = sha256(path)
            except OSError as exc:
                actual = None
                error = f"{type(exc).__name__}: {exc}"
            else:
                error = None
            if actual != expected:
                mismatches.append({"path": path.relative_to(ROOT).as_posix(),
                                   "kind": label, "expected_sha256": expected,
                                   "actual_sha256": actual, "error": error})
    return {"status": "MATCH" if not mismatches else "DRIFT",
            "checked_source_count": len(entries), "mismatches": mismatches}


def log_progress_signature(paths: list[Path]) -> tuple[tuple[str, int, int], ...]:
    """读取日志大小和修改时间，作为无进展监测的一部分。"""
    signature = []
    for path in paths:
        try:
            info = path.stat()
            signature.append((str(path), info.st_size, info.st_mtime_ns))
        except OSError:
            signature.append((str(path), -1, -1))
    return tuple(signature)


def numeric(token: str) -> tuple[str, float | None]:
    """解析有限数及Inf/NA；非有限值保留原文且不伪造成数值。"""
    raw = token.strip()
    if raw.upper() == "NA":
        return raw, None
    try:
        value = float(raw.replace(",", ""))
    except ValueError as exc:
        raise ValueError(f"报告数值无法解析：{raw}") from exc
    return raw, value if math.isfinite(value) else None


def parse_timing(path: Path) -> dict[str, Any]:
    """解析Vivado综合时序摘要的首个Design Timing Summary数据行。"""
    text = path.read_text(encoding="utf-8", errors="replace")
    start = text.find("Design Timing Summary")
    if start < 0:
        raise ValueError("timing_summary.rpt缺少Design Timing Summary")
    end = text.find("Clock Summary", start)
    if end < 0:
        end = len(text)
    section = text[start:end]
    header = re.search(r"WNS\(ns\).*?TNS\(ns\).*?WHS\(ns\).*?THS\(ns\)", section)
    if header is None:
        raise ValueError("timing_summary.rpt缺少WNS/TNS/WHS/THS栏")
    number_pattern = re.compile(r"(?<!\S)(?:[-+]?(?:\d+(?:\.\d*)?|\.\d+)|[-+]?(?:inf|nan)|NA)(?!\S)", re.I)
    row = None
    for line in section[header.end():].splitlines():
        tokens = number_pattern.findall(line)
        if len(tokens) >= 6:
            row = tokens
            break
    if row is None:
        raise ValueError("timing_summary.rpt没有可解析的时序指标行")
    return {
        "wns_ns": dict(zip(("raw", "value"), numeric(row[0]))),
        "tns_ns": dict(zip(("raw", "value"), numeric(row[1]))),
        "whs_ns": dict(zip(("raw", "value"), numeric(row[4]))),
        "ths_ns": dict(zip(("raw", "value"), numeric(row[5]))),
        "tns_failing_endpoints": int(row[2]),
        "tns_total_endpoints": int(row[3]),
        "ths_failing_endpoints": int(row[6]) if len(row) > 6 and row[6].isdigit() else None,
        "ths_total_endpoints": int(row[7]) if len(row) > 7 and row[7].isdigit() else None,
    }


def parse_utilization(path: Path) -> dict[str, Any]:
    """解析综合利用率报告中的LUT、寄存器、BRAM和DSP用量。"""
    found: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.lstrip().startswith("|"):
            continue
        columns = [value.strip() for value in line.strip().strip("|").split("|")]
        if len(columns) < 6:
            continue
        label = columns[0]
        key = None
        if label.startswith("Slice LUTs"):
            key = "slice_luts"
        elif label == "Slice Registers":
            key = "slice_registers"
        elif label == "Block RAM Tile":
            key = "block_ram_tiles"
        elif label == "DSPs":
            key = "dsps"
        if key is None:
            continue
        used_value = float(columns[1].replace(",", ""))
        available = int(columns[4].replace(",", ""))
        utilization = float(columns[5].replace("%", "").replace(",", ""))
        if not math.isfinite(used_value) or used_value < 0 or not math.isfinite(utilization):
            raise ValueError(f"利用率报告中存在非有限或负数值：{label}")
        if key != "block_ram_tiles" and not used_value.is_integer():
            raise ValueError(f"整数型资源报告出现小数：{label}={columns[1]}")
        used: int | float = int(used_value) if used_value.is_integer() else used_value
        found[key] = {
            "used": used,
            "available": available,
            "utilization_percent": utilization,
        }
    missing = {"slice_luts", "slice_registers", "block_ram_tiles", "dsps"} - found.keys()
    if missing:
        raise ValueError("utilization.rpt缺少资源行：" + ",".join(sorted(missing)))
    return found


def write_json(path: Path, value: dict[str, Any]) -> None:
    """以UTF-8、稳定格式写入机器可读记录。"""
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def build_manifest(evidence: Path, artifacts: list[dict[str, str]], limitations: list[str],
                   baseline_commit: str) -> Path:
    """生成仅含源码快照、报告和结果的小型清单；排除日志与DCP。"""
    for relative in REPORT_NAMES:
        report = evidence / "reports" / relative
        if report.is_file():
            artifacts.append({"path": report.relative_to(ROOT).as_posix(), "sha256": sha256(report),
                              "hash_basis": "worktree_disk", "role": "vivado_report"})
    result = evidence / "result.json"
    if result.is_file():
        artifacts.append({"path": result.relative_to(ROOT).as_posix(), "sha256": sha256(result),
                          "hash_basis": "worktree_disk", "role": "run_result"})
    manifest = {
        "schema_version": "s2c-lane32-ooc-evidence/1.0.0",
        "task_id": "S2C-SYN01",
        "run_id": evidence.name,
        "hash_basis": "worktree_disk",
        "baseline_commit": baseline_commit,
        "artifacts": artifacts,
        "excluded_artifacts": ["Vivado日志/journal/控制台日志和综合DCP保存在隔离tmp目录，不作为manifest清单项。"],
        "limitations": limitations,
    }
    path = evidence / "manifest.json"
    write_json(path, manifest)
    return path


def main() -> int:
    """检查源与资源，执行单Vivado线程Tcl并解析时序/资源报告。"""
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="唯一运行标识，仅字母、数字、下划线、连字符")
    parser.add_argument("--timeout-seconds", type=int, default=4 * 60 * 60,
                        help="综合总超时秒数，默认4小时")
    parser.add_argument("--no-progress-seconds", type=int, default=30 * 60,
                        help="日志与进程树CPU均无进展超时秒数；0禁用，默认30分钟")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", args.run_id):
        parser.error("run-id必须为1–64个安全ASCII字母/数字/下划线/连字符，首字符为字母或数字")
    if args.timeout_seconds <= 0 or args.no_progress_seconds < 0:
        parser.error("timeout-seconds须大于0，no-progress-seconds须大于或等于0")

    if os.path.normcase(str(ROOT)) != os.path.normcase(str(EXPECTED_ROOT)):
        parser.error(f"runner必须位于精确工作树{EXPECTED_ROOT}；当前为{ROOT}")
    evidence = ROOT / "report/evidence/S2C-SYN01" / args.run_id
    work = ROOT / "tmp/S2C/S2C-SYN01" / args.run_id
    if evidence.exists() or work.exists():
        parser.error("run-id证据或工作目录已存在，拒绝覆盖")
    if not VIVADO.is_file():
        parser.error(f"Vivado批处理入口不存在：{VIVADO}")

    artifacts: list[dict[str, str]] = []
    limitations = [
        "这是综合OOC报告；没有实现/布线结果，也不是板级验证。",
        "仅对clk施加100MHz约束，接口输入/输出延迟未约束；未约束路径限制须结合timing_summary及methodology报告解读。",
        "合成报告成功只表示报告可用；OOC timing指标单独记录，不能替代实现后时序收敛。",
    ]
    result: dict[str, Any] = {
        "schema_version": "s2c-lane32-ooc-run/1.0.0",
        "task_id": "S2C-SYN01",
        "run_id": args.run_id,
        "status": "NOT_STARTED",
        "hash_basis": "worktree_disk",
        "baseline_commit": None,
        "rtl_commit": RTL_COMMIT,
        "branch": None,
        "dirty_before_run": None,
        "sources": [],
        "commands": [],
        "reports": {},
        "timing_assessment": "NOT_ASSESSED",
        "resource_preflight": None,
        "peak_vivado_process_tree_working_set_bytes": None,
        "launcher_pid": None,
        "timeout_seconds": args.timeout_seconds,
        "no_progress_seconds": args.no_progress_seconds,
        "limitations": limitations,
    }

    try:
        all_inputs, profile = tracked_inputs()
        result["baseline_commit"] = git("rev-parse", "HEAD")
        result["branch"] = git("branch", "--show-current")
        result["dirty_before_run"] = git("status", "--porcelain")
        result["source_identity"] = {
            "configured_baseline_commit": BASELINE_COMMIT,
            "baseline_is_ancestor": subprocess.run(
                ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", BASELINE_COMMIT, "HEAD"],
                check=False, timeout=30,
            ).returncode == 0,
            "rtl_implementation_is_ancestor": subprocess.run(
                ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", RTL_COMMIT, "HEAD"],
                check=False, timeout=30,
            ).returncode == 0,
            "platform_version": profile.get("version"),
            "part": profile["vivado_part"],
            "clock_hz": profile["clock_hz"],
            "generics": profile["candidate_generics"],
        }
        if not result["source_identity"]["baseline_is_ancestor"]:
            raise ValueError(f"HEAD不在指定基线{BASELINE_COMMIT}之上")
        if not result["source_identity"]["rtl_implementation_is_ancestor"]:
            raise ValueError(f"HEAD不包含指定RTL实现提交{RTL_COMMIT}")

        evidence.mkdir(parents=True, exist_ok=False)
        work.mkdir(parents=True, exist_ok=False)
        reports_dir = evidence / "reports"
        # Tcl的new_directory要求reports目标当前不存在、父evidence目录已存在；由Tcl创建它。
        snapshot_entries = snapshot_inputs(all_inputs, evidence)
        artifacts.extend(snapshot_entries)
        result["sources"] = snapshot_entries

        checker = ROOT / "verification/check_s2c_inference_platform.py"
        checker_command = [sys.executable, "-B", str(checker), "--root", str(ROOT), "--json"]
        checker_run = subprocess.run(checker_command, cwd=ROOT, capture_output=True, check=False,
                                     text=True, encoding="utf-8", errors="replace", timeout=120)
        checker_log = work / "static_checker_console.log"
        checker_log.write_text(checker_run.stdout + checker_run.stderr, encoding="utf-8")
        result["static_checker"] = {
            "argv": checker_command, "exit_code": checker_run.returncode,
            "stdout": checker_run.stdout[-12000:], "stderr": checker_run.stderr[-4000:],
            "log_path": checker_log.relative_to(ROOT).as_posix(), "log_sha256": sha256(checker_log),
            "hash_basis": "worktree_disk",
        }
        if checker_run.returncode != 0:
            raise RuntimeError("S2C平台静态闭包检查失败，拒绝启动Vivado")

        # 检查器完成后再次核对活动文件与快照，避免后续Tcl读到混合版本。
        pre_run_integrity = check_source_integrity(snapshot_entries)
        result["pre_run_source_integrity"] = pre_run_integrity
        if pre_run_integrity["status"] != "MATCH":
            raise RuntimeError("运行前活动源码或持久快照哈希发生漂移")

        try:
            preflight = resource_snapshot()
        except Exception as exc:
            result["status"] = "RESOURCE_PREFLIGHT_ERROR_NOT_STARTED"
            result["resource_preflight_error"] = f"{type(exc).__name__}: {exc}"
            raise
        result["resource_preflight"] = {
            "processes": preflight["processes"],
            "available_bytes": preflight["available_bytes"],
            "total_bytes": preflight["total_bytes"],
        }
        if preflight["processes"]:
            result["status"] = "RESOURCE_BUSY_NOT_STARTED"
            result["resource_decision"] = "检测到本机Vivado/XSim/Vitis类重型进程"
            raise RuntimeError("重型资源忙，未启动本次Vivado")
        if preflight["available_bytes"] < MIN_FREE_BYTES:
            result["status"] = "RESOURCE_BUSY_NOT_STARTED"
            result["resource_decision"] = f"可用内存低于6GiB：{preflight['available_bytes']}字节"
            raise RuntimeError("可用物理内存不足6GiB，未启动本次Vivado")

        snapshot_root = evidence / "source_snapshot"
        snapshot_tcl = snapshot_root / TCL_PATH
        report_output = reports_dir.resolve()
        argv = [
            str(VIVADO), "-mode", "batch", "-log", str(work / "vivado.log"),
            "-journal", str(work / "vivado.jou"), "-source", str(snapshot_tcl),
            "-tclargs", str(snapshot_root), str(report_output),
        ]
        command = "call " + " ".join(subprocess.list2cmdline([value]) for value in argv)
        console = work / "vivado_console.log"
        result["commands"].append({"argv": argv, "shell_command": command,
                                   "cwd": str(work), "console_log": console.relative_to(ROOT).as_posix(),
                                   "hash_basis": "worktree_disk"})
        started = time.monotonic()
        last_progress_at = started
        progress_logs = [console, work / "vivado.log", work / "vivado.jou"]
        last_progress_signature: tuple[Any, ...] = (log_progress_signature(progress_logs), None)
        peak_tree = 0
        process_samples = [{"available_bytes": preflight["available_bytes"],
                            "processes": preflight["processes"]}]
        with console.open("wb") as output:
            process = subprocess.Popen(command, cwd=work, stdout=output, stderr=subprocess.STDOUT,
                                       shell=True, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            result["launcher_pid"] = process.pid
            result["launcher_parent_pid"] = os.getpid()
            print(f"Vivado OOC launcher pid={process.pid}; poll interval={POLL_SECONDS}s", flush=True)
            try:
                while True:
                    try:
                        return_code = process.wait(timeout=POLL_SECONDS)
                        break
                    except subprocess.TimeoutExpired:
                        now = time.monotonic()
                        elapsed = round(now - started, 1)
                        try:
                            sample = resource_snapshot()
                            process_samples.append({"available_bytes": sample["available_bytes"],
                                                    "processes": sample["processes"]})
                            descendants = process_tree_working_set(process.pid, sample["all_processes"])
                            if descendants is not None:
                                peak_tree = max(peak_tree, descendants)
                            cpu_ticks = process_tree_cpu_ticks(process.pid, sample["all_processes"])
                        except Exception as exc:
                            result.setdefault("monitor_errors", []).append(f"{type(exc).__name__}: {exc}")
                            cpu_ticks = None
                        progress_signature = (log_progress_signature(progress_logs), cpu_ticks)
                        if progress_signature != last_progress_signature:
                            last_progress_signature = progress_signature
                            last_progress_at = now
                        total_timeout = elapsed >= args.timeout_seconds
                        no_progress_timeout = (args.no_progress_seconds > 0 and
                                               now - last_progress_at >= args.no_progress_seconds)
                        if total_timeout or no_progress_timeout:
                            reason = "TOTAL_TIMEOUT" if total_timeout else "NO_PROGRESS_TIMEOUT"
                            result["timeout_event"] = {
                                "reason": reason,
                                "elapsed_seconds": elapsed,
                                "no_progress_seconds": round(now - last_progress_at, 1),
                                "stop_policy": "只对CIM核实为本runner直接创建的cmd.exe及其子进程树执行taskkill /T",
                            }
                            result["status"] = "TIMEOUT_STOPPING_OWN_TREE"
                            try:
                                termination = terminate_owned_process_tree(process.pid, os.getpid(), process)
                            except Exception as exc:
                                termination = {"success": False,
                                               "resource_held": True,
                                               "reason": f"{type(exc).__name__}: {exc}"}
                            result["timeout_event"]["termination"] = termination
                            if not termination["success"]:
                                result["status"] = "TIMEOUT_STOP_FAILED"
                                result["resource_state"] = "RESOURCE_HELD"
                                result["resource_held"] = True
                                result["failure"] = "超时后无法确认该runner进程树已结束；需总控按记录PID处理"
                                print(f"RUNNER_REQUIRES_CONTROLLER_ACTION launcher_pid={process.pid} "
                                      f"reason={termination.get('reason')}", flush=True)
                                raise RuntimeError(result["failure"])
                            return_code = process.returncode
                            result["status"] = "TIMED_OUT_OWN_TREE_TERMINATED"
                            break
                        print(f"Vivado OOC running launcher_pid={process.pid}; elapsed={elapsed}s; "
                              f"idle={now - last_progress_at:.0f}s", flush=True)
            except KeyboardInterrupt:
                result["interrupt_note"] = "收到中断，正在核实并结束本runner创建的进程树。"
                try:
                    termination = terminate_owned_process_tree(process.pid, os.getpid(), process)
                except Exception as exc:
                    termination = {"success": False,
                                   "resource_held": True,
                                   "reason": f"{type(exc).__name__}: {exc}"}
                result["interrupt_termination"] = termination
                if termination["success"]:
                    return_code = process.returncode
                    result["status"] = "INTERRUPTED_OWN_TREE_TERMINATED"
                else:
                    result["status"] = "INTERRUPTED_STOP_FAILED"
                    result["resource_state"] = "RESOURCE_HELD"
                    result["resource_held"] = True
                    result["failure"] = "中断后无法确认该runner进程树已结束；需总控按记录PID处理"
                    print(f"RUNNER_REQUIRES_CONTROLLER_ACTION launcher_pid={process.pid} "
                          f"reason={termination.get('reason')}", flush=True)
                    raise
        elapsed = round(time.monotonic() - started, 3)
        result["commands"][-1].update({"exit_code": return_code, "elapsed_seconds": elapsed})
        post_run_integrity = check_source_integrity(snapshot_entries)
        result["post_run_source_integrity"] = post_run_integrity
        result["resource_samples"] = [{"available_bytes": item["available_bytes"],
                                       "heavy_process_count": len(item["processes"])} for item in process_samples]
        if peak_tree:
            result["peak_vivado_process_tree_working_set_bytes"] = peak_tree

        console_text = console.read_text(encoding="utf-8", errors="replace")
        vivado_log = work / "vivado.log"
        log_text = vivado_log.read_text(encoding="utf-8", errors="replace") if vivado_log.is_file() else ""
        marker_locations = [name for name, content in (("vivado_console.log", console_text),
                                                       ("vivado.log", log_text))
                            if COMPLETION_MARKER in content]
        result["completion_marker"] = {"required": COMPLETION_MARKER,
                                       "found": bool(marker_locations), "locations": marker_locations}
        version_match = re.search(r"Vivado\s+v?\.?\s*([0-9]+(?:\.[0-9]+)+)", console_text + "\n" + log_text, re.I)
        result["vivado_version"] = version_match.group(1) if version_match else None

        report_digests: dict[str, Any] = {}
        for name in REPORT_NAMES:
            path = reports_dir / name
            report_digests[name] = ({"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path),
                                     "hash_basis": "worktree_disk", "size_bytes": path.stat().st_size}
                                    if path.is_file() else {"path": path.relative_to(ROOT).as_posix(),
                                                            "status": "MISSING"})
        result["reports"] = report_digests

        parse_errors = []
        if post_run_integrity["status"] != "MATCH":
            parse_errors.append("Vivado运行后活动源码与持久快照哈希不一致")
        missing_reports = [name for name, entry in report_digests.items() if entry.get("status") == "MISSING"]
        if missing_reports:
            parse_errors.append("综合输出报告缺失：" + ",".join(missing_reports))
        try:
            result["timing"] = parse_timing(reports_dir / "timing_summary.rpt")
            timing_values = [result["timing"][key]["value"]
                             for key in ("wns_ns", "tns_ns", "whs_ns", "ths_ns")]
            if any(value is None for value in timing_values):
                result["timing_assessment"] = "METRICS_PARSED_NONFINITE_OR_UNAVAILABLE"
            else:
                result["timing_assessment"] = (
                    "OOC_SYNTH_METRICS_NONNEGATIVE" if all(value >= 0 for value in timing_values)
                    else "OOC_SYNTH_METRICS_NEGATIVE_SLACK"
                )
        except Exception as exc:
            parse_errors.append(f"timing_summary.rpt: {type(exc).__name__}: {exc}")
        try:
            result["resources"] = parse_utilization(reports_dir / "utilization.rpt")
        except Exception as exc:
            parse_errors.append(f"utilization.rpt: {type(exc).__name__}: {exc}")

        dcp = reports_dir / "lane32_bulk_post_synth.dcp"
        if dcp.is_file():
            retained_dcp = work / dcp.name
            dcp.replace(retained_dcp)
            result["checkpoint"] = {"path": retained_dcp.relative_to(ROOT).as_posix(),
                                    "size_bytes": retained_dcp.stat().st_size,
                                    "sha256": None, "manifested": False}
        else:
            parse_errors.append("综合DCP缺失：lane32_bulk_post_synth.dcp")

        if parse_errors:
            result["report_parse_errors"] = parse_errors
        if result["status"] not in ("TIMED_OUT_OWN_TREE_TERMINATED", "INTERRUPTED_OWN_TREE_TERMINATED"):
            result["status"] = (
                "SYNTH_REPORTS_PARSED" if return_code == 0 and marker_locations and not parse_errors
                else "SYNTH_FAILED_OR_REPORTS_INCOMPLETE"
            )
        result["tool_success"] = (return_code == 0 and bool(marker_locations)
                                  and post_run_integrity["status"] == "MATCH")
        result["reports_parse_success"] = not parse_errors
        result["acceptance"] = "OOC综合与指标提取结果；是否时序合格须按独立门槛判断，不等于实现或板级通过。"
        result["execution_seconds"] = elapsed
        result["resource_preflight_threshold_bytes"] = MIN_FREE_BYTES
        # 构建完成后再取一次空闲内存；该值不等同于本进程树峰值。
        try:
            final_resources = resource_snapshot()
            result["final_available_memory_bytes"] = final_resources["available_bytes"]
        except Exception as exc:
            result["final_resource_query_error"] = f"{type(exc).__name__}: {exc}"

    except KeyboardInterrupt:
        if result["status"] == "NOT_STARTED":
            result["status"] = "INTERRUPTED"
    except Exception as exc:
        if not result.get("failure"):
            result["failure"] = f"{type(exc).__name__}: {exc}"
        if result["status"] in ("NOT_STARTED", "RESOURCE_PREFLIGHT_ERROR_NOT_STARTED"):
            if result["status"] == "NOT_STARTED":
                result["status"] = "RUNNER_FAILED_NOT_ACCEPTED"
    finally:
        # 即使门禁拒绝或脚本异常，也保留真实状态与源快照；日志/DCP不列入manifest。
        if evidence.is_dir():
            log_entries = {}
            if work.is_dir():
                for name in ("static_checker_console.log", "vivado_console.log", "vivado.log", "vivado.jou"):
                    path = work / name
                    if path.is_file():
                        log_entries[name] = {
                            "path": path.relative_to(ROOT).as_posix(),
                            "sha256": sha256(path),
                            "hash_basis": "worktree_disk",
                            "size_bytes": path.stat().st_size,
                            "digest_state": "PARTIAL_NONFINAL_RESOURCE_HELD" if result.get("resource_held") else "PROCESS_FINISHED_OR_NOT_STARTED",
                        }
            result["logs"] = log_entries
            result_path = evidence / "result.json"
            write_json(result_path, result)
            try:
                manifest_path = build_manifest(evidence, list(artifacts), limitations,
                                               result.get("baseline_commit") or git("rev-parse", "HEAD"))
                # 清单路径已由固定的S2C-SYN01/run-id目录推导；不回写result以免破坏其自身SHA。
                _ = manifest_path
            except Exception as exc:
                result["manifest_error"] = f"{type(exc).__name__}: {exc}"
                write_json(result_path, result)

    print(json.dumps({"status": result["status"], "run_id": args.run_id,
                      "launcher_pid": result.get("launcher_pid"),
                      "timing_assessment": result.get("timing_assessment"),
                      "failure": result.get("failure")}, ensure_ascii=False), flush=True)
    if result["status"] == "SYNTH_REPORTS_PARSED":
        return 0
    if result["status"] in ("RESOURCE_BUSY_NOT_STARTED", "RESOURCE_PREFLIGHT_ERROR_NOT_STARTED"):
        return 2
    return 1


def process_parent_map(processes: list[dict[str, Any]]) -> dict[int, int] | None:
    """严格读取CIM进程父子关系；任何缺失或重复PID都视为无法核实。"""
    pid_parent: dict[int, int] = {}
    for process in processes:
        if not isinstance(process, dict):
            return None
        try:
            pid = int(process["ProcessId"])
            parent_pid = int(process["ParentProcessId"])
        except (KeyError, TypeError, ValueError):
            return None
        if pid in pid_parent:
            return None
        pid_parent[pid] = parent_pid
    return pid_parent


def process_tree_pids(root_pid: int, processes: list[dict[str, Any]]) -> set[int] | None:
    """由指定启动器PID向下追踪当前进程树；根PID缺失或清单不完整时返回None。"""
    pid_parent = process_parent_map(processes)
    if pid_parent is None:
        return None
    if root_pid not in pid_parent:
        return None
    descendants = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, parent in pid_parent.items():
            if parent in descendants and pid not in descendants:
                descendants.add(pid)
                changed = True
    return descendants


def process_descendants_of_known_pids(seed_pids: set[int],
                                      processes: list[dict[str, Any]]) -> set[int] | None:
    """保留已退出父PID作为追溯种子，只返回当前仍存活的已知子孙。"""
    pid_parent = process_parent_map(processes)
    if pid_parent is None:
        return None
    descendants = set(seed_pids)
    changed = True
    while changed:
        changed = False
        for pid, parent in pid_parent.items():
            if parent in descendants and pid not in descendants:
                descendants.add(pid)
                changed = True
    return descendants.intersection(pid_parent)


def process_tree_working_set(root_pid: int, processes: list[dict[str, Any]]) -> int | None:
    """按已启动Vivado批处理PID的父子关系估算其当前工作集。"""
    pids = process_tree_pids(root_pid, processes)
    if pids is None:
        return None
    memory = {}
    for process in processes:
        try:
            memory[int(process["ProcessId"])] = int(process.get("WorkingSetSize") or 0)
        except (KeyError, TypeError, ValueError):
            continue
    return sum(memory.get(pid, 0) for pid in pids)


def process_tree_cpu_ticks(root_pid: int, processes: list[dict[str, Any]]) -> int | None:
    """按工作集监控同一进程树的累计内核/用户CPU时间。"""
    pids = process_tree_pids(root_pid, processes)
    if pids is None:
        return None
    total = 0
    for process in processes:
        try:
            if int(process["ProcessId"]) in pids:
                total += int(process.get("UserModeTime") or 0)
                total += int(process.get("KernelModeTime") or 0)
        except (KeyError, TypeError, ValueError):
            continue
    return total


def terminate_owned_process_tree(root_pid: int, owner_pid: int,
                                 process: subprocess.Popen[Any]) -> dict[str, Any]:
    """核实启动器由本Python直接创建后，仅结束并复核该启动器进程树。"""
    try:
        before = resource_snapshot()
    except Exception as exc:
        return {"success": False, "resource_held": True,
                "reason": f"无法读取进程树：{type(exc).__name__}: {exc}"}
    if process_parent_map(before["all_processes"]) is None:
        return {"success": False, "resource_held": True,
                "reason": "taskkill前CIM进程清单不完整，无法证明启动器归属或列全其子孙"}
    records = {int(item["ProcessId"]): item for item in before["all_processes"]}
    launcher = records.get(root_pid)
    if launcher is None:
        return {"success": False, "resource_held": True,
                "reason": "启动器PID不在CIM进程表，无法核实其子孙是否仍存活；保留资源占用状态"}
    try:
        launcher_parent_pid = int(launcher["ParentProcessId"])
    except (KeyError, TypeError, ValueError):
        return {"success": False, "resource_held": True,
                "reason": "无法核实启动器直接父PID，保留资源占用状态"}
    if str(launcher.get("Name", "")).lower() != "cmd.exe" or launcher_parent_pid != owner_pid:
        return {"success": False, "resource_held": True,
                "reason": "启动器名称或直接父PID与本runner不符，保留资源占用状态"}
    tree_pids = process_tree_pids(root_pid, before["all_processes"])
    if tree_pids is None:
        return {"success": False, "resource_held": True,
                "reason": "无法核实启动器的完整父子进程树，保留资源占用状态"}
    try:
        killed = subprocess.run(["taskkill.exe", "/PID", str(root_pid), "/T", "/F"],
                                capture_output=True, check=False, text=True, encoding="utf-8",
                                errors="replace", timeout=20)
    except Exception as exc:
        return {"success": False, "resource_held": True,
                "reason": f"无法确认taskkill完成：{type(exc).__name__}: {exc}",
                "tree_pids": sorted(tree_pids)}
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        return {"success": False, "resource_held": True, "reason": "taskkill后启动器仍未退出",
                "taskkill_exit_code": killed.returncode,
                "taskkill_stdout": killed.stdout[-2000:],
                "taskkill_stderr": killed.stderr[-2000:], "tree_pids": sorted(tree_pids)}
    except Exception as exc:
        return {"success": False, "resource_held": True,
                "reason": f"taskkill后无法确认启动器退出：{type(exc).__name__}: {exc}",
                "taskkill_exit_code": killed.returncode, "tree_pids": sorted(tree_pids)}
    try:
        after = resource_snapshot()
    except Exception as exc:
        return {"success": False, "resource_held": True,
                "reason": f"进程结束后无法核验：{type(exc).__name__}: {exc}",
                "taskkill_exit_code": killed.returncode, "tree_pids": sorted(tree_pids)}
    current_tree = process_descendants_of_known_pids(tree_pids, after["all_processes"])
    if current_tree is None:
        return {"success": False, "resource_held": True,
                "reason": "taskkill后CIM进程清单不完整，无法确认已知进程树及新子孙全部退出",
                "taskkill_exit_code": killed.returncode, "tree_pids": sorted(tree_pids)}
    remaining_pids = sorted(current_tree)
    ended_cleanly = process.poll() is not None and not remaining_pids
    success = not remaining_pids and (killed.returncode == 0 or ended_cleanly)
    return {"success": success, "resource_held": not success,
            "reason": None if success else "taskkill退出码非零且无法确认整个进程树已退出",
            "taskkill_exit_code": killed.returncode,
            "taskkill_stdout": killed.stdout[-2000:],
            "taskkill_stderr": killed.stderr[-2000:],
            "tree_pids": sorted(tree_pids), "remaining_pids": remaining_pids,
            "post_taskkill_tree_pids": sorted(current_tree)}


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[FAIL] {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
