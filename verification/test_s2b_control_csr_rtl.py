#!/usr/bin/env python3
"""隔离验证候选控制层，绑定真实公共runtime与adapter源码及全部失败证据。"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SPEC = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
SPEC_SHA = "1486a7f69e7a2053acfcad05151a9c54cfffab776d4154141741236aa88c401b"
COMPILE_TIMEOUT_SECONDS = 600
SIMULATION_TIMEOUT_SECONDS = 60
CHECKPOINT_INTERVAL_SECONDS = 15
SOURCES = ("src/s2b_control_csr.sv", "src/s2b_hp0_word_adapter.sv", "src/s2b_request_guard.sv",
           "src/s2a_control_csr.sv", "src/s2a_memory_master.sv", "src/s2a_runtime_shell.sv",
           "sim/tb_s2b_control_csr.sv", "verification/test_s2b_control_csr_rtl.py")


def sha(path: Path) -> str:
    """哈希原始文件字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checkpoint(evidence: Path, record: dict, log: Path, started: float, message: str) -> None:
    """追加运行检查点并同步到终端，便于长编译期间恢复观察。"""
    item = {"time": datetime.now().astimezone().isoformat(timespec="milliseconds"),
        "phase": record["name"], "message": message,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "process_id": record.get("process_id"), "exit_code": record.get("exit_code"),
        "log_bytes": log.stat().st_size if log.exists() else 0}
    with (evidence / "runner_checkpoints.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(item, ensure_ascii=False) + "\n")
        stream.flush()
    print(json.dumps(item, ensure_ascii=False), flush=True)


def stop_process_tree(process: subprocess.Popen, stream, record: dict) -> None:
    """超时后尝试结束整棵子进程树；收尾不确定时记录并失败关闭。"""
    cleanup = {"attempted": True, "tree_command": None, "tree_exit_code": None,
        "tree_output": "", "parent_exit_code": None, "parent_terminated": False}
    if os.name == "nt":
        cleanup["tree_command"] = ["taskkill", "/PID", str(process.pid), "/T", "/F"]
        try:
            result = subprocess.run(cleanup["tree_command"], stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", timeout=30)
            cleanup["tree_exit_code"] = result.returncode
            cleanup["tree_output"] = result.stdout or ""
        except Exception as exc:
            cleanup["tree_output"] = f"taskkill异常：{type(exc).__name__}: {exc}"
        if cleanup["tree_output"]:
            stream.write("\n[进程树收尾原始输出]\n" + cleanup["tree_output"] + "\n")
            stream.flush()
    else:
        try:
            process.kill()
            cleanup["tree_exit_code"] = 0
            cleanup["tree_output"] = "已向本进程发送kill；未枚举子进程。"
        except Exception as exc:
            cleanup["tree_output"] = f"kill异常：{type(exc).__name__}: {exc}"
    try:
        process.wait(timeout=30)
    except subprocess.TimeoutExpired:
        try:
            process.kill()
            process.wait(timeout=10)
        except Exception as exc:
            cleanup["tree_output"] += f"\n父进程强制结束异常：{type(exc).__name__}: {exc}"
    except Exception as exc:
        cleanup["tree_output"] += f"\n等待父进程异常：{type(exc).__name__}: {exc}"
    cleanup["parent_exit_code"] = process.poll()
    cleanup["parent_terminated"] = cleanup["parent_exit_code"] is not None
    cleanup["tree_termination_confirmed"] = (os.name != "nt" or cleanup["tree_exit_code"] == 0) and cleanup["parent_terminated"]
    record["cleanup"] = cleanup


def execute(name: str, command: list[str], work: Path, evidence: Path, env: dict,
            report: dict, timeout_seconds: int) -> dict:
    """单job运行，定期保存检查点，并在超时或异常时保留日志与进程状态。"""
    started = time.monotonic()
    log = evidence / (name + ".log")
    record = {"name": name, "command": command, "working_directory": str(work),
        "timeout_seconds": timeout_seconds, "exit_code": None, "timed_out": False,
        "status": "RUNNING", "log_path": log.relative_to(ROOT).as_posix(),
        "process_id": None, "started_at": datetime.now().astimezone().isoformat(timespec="milliseconds")}
    report["runs"].append(record)
    with log.open("x", encoding="utf-8") as stream:
        process = None
        try:
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
            process = subprocess.Popen(command, cwd=work, env=env, stdout=stream,
                stderr=subprocess.STDOUT, creationflags=creationflags)
            record["process_id"] = process.pid
            checkpoint(evidence, record, log, started, "进程已启动")
            deadline = started + timeout_seconds
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    record["timed_out"] = True
                    record["status"] = "FAIL_TIMEOUT"
                    checkpoint(evidence, record, log, started, "达到wall超时，开始进程树收尾")
                    stop_process_tree(process, stream, record)
                    break
                try:
                    process.wait(timeout=min(CHECKPOINT_INTERVAL_SECONDS, remaining))
                    record["exit_code"] = process.returncode
                    record["status"] = "PASS" if process.returncode == 0 else "FAIL_EXIT"
                    break
                except subprocess.TimeoutExpired:
                    stream.flush()
                    checkpoint(evidence, record, log, started, "运行中")
            if record["timed_out"]:
                record["exit_code"] = process.poll()
                if not record.get("cleanup", {}).get("tree_termination_confirmed", False):
                    record["status"] = "FAIL_TIMEOUT_CLEANUP_UNCONFIRMED"
        except Exception as exc:
            record["status"] = "FAIL_LAUNCH_OR_RUNNER_EXCEPTION"
            record["error"] = f"{type(exc).__name__}: {exc}"
            if process is not None and process.poll() is None:
                stop_process_tree(process, stream, record)
            record["exit_code"] = process.poll() if process is not None else None
        finally:
            record["seconds"] = round(time.monotonic() - started, 3)
            record["finished_at"] = datetime.now().astimezone().isoformat(timespec="milliseconds")
            record["log_sha256"] = sha(log)
            record["log_bytes"] = log.stat().st_size
    if record["status"] != "PASS":
        raise RuntimeError(f"{name}失败：status={record['status']} exit_code={record['exit_code']}")
    return record


def run(work: Path, evidence: Path, toolchain: Path, report: dict) -> None:
    """冻结实际源码并严格Wall编译真实控制/内核CSR/内存master/adapter闭包。"""
    if sha(ROOT / SPEC) != SPEC_SHA:
        raise ValueError("候选契约SHA变化")
    report["sources"] = [{"path": p, "sha256": sha(ROOT / p)} for p in SOURCES]
    report["inputs"] = [{"path": SPEC, "sha256": SPEC_SHA}]
    (work / "source").mkdir(); (evidence / "source_snapshot").mkdir()
    for p in SOURCES:
        shutil.copyfile(ROOT / p, evidence / "source_snapshot" / Path(p).name)
        if p.endswith(".sv"):
            shutil.copyfile(ROOT / p, work / "source" / Path(p).name)
    tools_dir, make_dir = toolchain / "mingw64/bin", toolchain / "usr/bin"
    verilator = tools_dir / "verilator_bin.exe"
    env = os.environ.copy()
    env["PATH"] = str(make_dir) + os.pathsep + str(tools_dir) + os.pathsep + env.get("PATH", "")
    env["VERILATOR_ROOT"] = str(tools_dir.parent / "share/verilator")
    report["runner_environment"] = {"inheritance": "Python os.environ.copy()",
        "path_entries": env["PATH"].split(os.pathsep), "verilator_root": env["VERILATOR_ROOT"],
        "python_executable": sys.executable, "cwd": str(work)}
    for path in (verilator, tools_dir / "g++.exe", make_dir / "make.exe", Path(env["VERILATOR_ROOT"])):
        if not path.exists():
            raise ValueError(f"工具精确路径不存在：{path}")
    report["tool_versions"] = {"python": sys.version.split()[0], "verilator": subprocess.check_output(
        [str(verilator), "--version"], cwd=work, env=env, text=True, timeout=30).strip()}
    report["tool_files"] = [{"path": str(p), "sha256": sha(p)}
        for p in (verilator, tools_dir / "g++.exe", make_dir / "make.exe")]
    compile_command = [str(verilator), "--binary", "--timing", "--timescale", "1ns/1ps", "-Wall",
        "-j", "1", "--threads", "1", "--top-module", "tb_s2b_control_csr", "--Mdir", "obj_dir",
        "-MAKEFLAGS", "PYTHON3='\"" + sys.executable + "\"'", "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0 -O0",
        *["source/" + Path(p).name for p in SOURCES if p.endswith(".sv")]]
    compile_run = execute("compile", compile_command, work, evidence, env, report,
        COMPILE_TIMEOUT_SECONDS)
    if compile_run["timed_out"] or compile_run["exit_code"] != 0:
        raise RuntimeError("编译未成功完成，禁止启动本Run产生的仿真二进制")
    execute("simulation", [str(work / "obj_dir/Vtb_s2b_control_csr.exe")], work,
        evidence, env, report, SIMULATION_TIMEOUT_SECONDS)
    matches = re.findall(r"PASS CONTROL_CSR directed=(\d+) random=(\d+) integration=(\d+) cycles=(\d+) status=(\d+) error=(\d+) debug=(\d+) starts=(\d+) resets=(\d+) acks=(\d+)",
        (evidence / "simulation.log").read_text(encoding="utf-8"))
    if len(matches) != 1:
        raise ValueError("缺少唯一计数PASS标记")
    report["simulation_counts"] = dict(zip(("directed", "random", "integration", "cycles", "status", "error", "debug", "starts", "resets", "acks"), map(int, matches[0])))
    if report["simulation_counts"]["random"] != 128 or report["simulation_counts"]["integration"] != 25:
        raise ValueError("固定验证数量不一致")
    phase_matches = re.findall(r"COVERAGE phases=(\d+),(\d+),(\d+),(\d+) logical_responses=(\d+) seed=0x2b111010",
        (evidence / "simulation.log").read_text(encoding="utf-8"))
    if len(phase_matches) != 1 or list(map(int, phase_matches[0][:4])) != [1, 1, 1, 1]:
        raise ValueError("四相位独立错误观察覆盖不完整")
    report["phase_coverage"] = list(map(int, phase_matches[0][:4]))
    report["logical_responses"] = int(phase_matches[0][4])
    runtime_phases = re.findall(r"RUNTIME_PHASES phases=(\d+),(\d+),(\d+),(\d+)",
        (evidence / "simulation.log").read_text(encoding="utf-8"))
    if len(runtime_phases) != 1 or list(map(int, runtime_phases[0])) != [1, 1, 1, 1]:
        raise ValueError("真实runtime四相位错误观察覆盖不完整")
    report["runtime_phase_coverage"] = list(map(int, runtime_phases[0]))
    for source in report["sources"]:
        if sha(ROOT / source["path"]) != source["sha256"]:
            raise ValueError("运行期间源码变化")
    report["status"] = "PASS_RTL_SIMULATION_ONLY"


def main() -> int:
    """每次独立RunId，按真实退出码记录FAIL/PASS，不把候选写成冻结。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--toolchain", type=Path, default=Path(r"D:\FPGA_S2A_MSYS2_20261001\env"))
    parser.add_argument("--adapter-regression", action="store_true")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.run_id):
        parser.error("RunId只允许英文、数字、下划线、连字符")
    parents = [ROOT / "report/evidence/S2B-T11", ROOT / "tmp/2B/S2B-T11"]
    for parent in parents:
        if not parent.parent.is_dir() or parent.is_symlink():
            parser.error(f"父目录未核验：{parent}")
        parent.mkdir(exist_ok=True)
    evidence, work = (parent / args.run_id for parent in parents)
    if evidence.exists() or work.exists():
        parser.error("RunId不可覆盖")
    evidence.mkdir(); work.mkdir()
    started = time.monotonic()
    report = {"status": "FAIL", "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "run_id": args.run_id, "runner_command": [sys.executable, *sys.argv],
        "timeouts_seconds": {"compile": COMPILE_TIMEOUT_SECONDS,
        "simulation": SIMULATION_TIMEOUT_SECONDS, "checkpoint_interval": CHECKPOINT_INTERVAL_SECONDS},
        "runs": [], "coverage": {"random_seed": "0x2b111010", "random_transactions": 128,
        "reference_basis": "候选契约0.1.2常量及独立公开CSR模型；25组真实runtime_shell/word_adapter集成，mock及真实runtime分别覆盖四种sticky产生相位，不窥busy/owner/backend_abort。",
        "bindings": ["零W1P不改变LAST_REJECT；非法编码BAD_ENCODING。",
        "START安全终态NEED_ACK、FAULT NOT_SAFE、运行BUSY；ABORT idle NOT_SAFE、安全终态NEED_ACK、恢复BUSY、FAULT NOT_SAFE；ACK非安全NOT_SAFE。",
        "epoch耗尽仅TB白盒force corner；正常cold硬件epoch为零。",
        "DRAIN_TIMEOUT观察完整恢复条件；真实S+2在恢复第4沿满足安全，deadline1/3保留bit3，deadline4同沿安全优先且不新增bit3。",
        "实际空账本下分别延迟可见性、公共CSR STOP和CORE首错ERROR取码，超限保持ownerPL/safe0，晚合法安全归还保留首错与bit3。"]},
        "limitations": ["候选物理接口未冻结；不构成完整2B G0/G4/G5与实板验收。",
        "visibility_confirmed低时真实任务禁止归还；实际HP/DDR属性、缓存路径与实物验证未执行。",
        "峰值内存未测；单job/单线程；各次RunId保留重跑次数；未采集波形。"]}
    try:
        run(work, evidence, args.toolchain.absolute(), report)
        if args.adapter_regression:
            module_spec = importlib.util.spec_from_file_location("s2b_t10", ROOT / "verification/test_s2b_hp0_word_adapter_rtl.py")
            if module_spec is None or module_spec.loader is None:
                raise ValueError("T10模块不可加载")
            module = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(module)
            for name, path in (("adapter", "verification/test_s2b_hp0_word_adapter_rtl.py"), ("guard", "verification/test_s2b_request_guard_rtl.py")):
                sub_work, sub_evidence = work / name, evidence / name
                sub_work.mkdir(); sub_evidence.mkdir()
                sub_report = {"status": "FAIL", "runs": []}
                report[name + "_regression"] = sub_report
                if name == "adapter":
                    module.run(sub_work, sub_evidence, args.toolchain.absolute(), sub_report)
                else:
                    guard_spec = importlib.util.spec_from_file_location("s2b_t09", ROOT / path)
                    if guard_spec is None or guard_spec.loader is None:
                        raise ValueError("guard模块不可加载")
                    guard = importlib.util.module_from_spec(guard_spec); guard_spec.loader.exec_module(guard)
                    guard.run(sub_work, sub_evidence, args.toolchain.absolute(), sub_report)
    except Exception as exc:
        report["status"] = "FAIL"; report["error"] = str(exc)
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    (evidence / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files = [{"path": p, "sha256": sha(ROOT / p), "role": "source"} for p in SOURCES]
    files += [{"path": SPEC, "sha256": sha(ROOT / SPEC), "role": "input"}]
    files += [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p),
        "role": "source" if p.parent.name=="source_snapshot" else "log" if p.suffix==".log" else "result"}
        for p in sorted(evidence.rglob("*")) if p.is_file()]
    checks = []
    for group in (report, report.get("adapter_regression", {}), report.get("guard_regression", {})):
        checks += [{"name": r["name"] + ("_control" if group is report else "_regression"),
            "status": "PASS" if r["exit_code"]==0 else "FAIL", "command": subprocess.list2cmdline(r["command"]),
            "exit_code": r["exit_code"], "reason": "严格Wall、隔离单job真实RTL与独立参考。"} for r in group.get("runs", [])]
    checks += [{"name": "实物与完整2B冻结", "status": "BLOCKED", "command": None, "exit_code": None,
        "reason": "本Run仅执行候选实现；上游物理契约未冻结、实物与可见性未验证。"}]
    delivery = {"schema_version": 1, "stage": "2B", "task_id": "S2B-T11", "run_id": args.run_id,
        "source_commit": report["source_commit"], "evidence_dir": evidence.relative_to(ROOT).as_posix(),
        "interfaces": [{"name": "阶段2B物理接口候选", "version": "s2b-physical-candidate/0.1.2",
        "frozen": False, "path": SPEC, "sha256": SPEC_SHA}], "files": files, "checks": checks,
        "limitations": report["limitations"], "tool_versions": report.get("tool_versions", {"python": sys.version.split()[0]})}
    (evidence / "delivery_manifest.json").write_text(json.dumps(delivery, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "error": report.get("error"), "counts": report.get("simulation_counts"),
        "seconds": report["elapsed_seconds"]}, ensure_ascii=False))
    return 0 if report["status"].startswith("PASS_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
