#!/usr/bin/env python3
"""隔离验证候选控制层，绑定真实公共runtime与adapter源码及全部失败证据。"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import textwrap

from s2b_process_supervisor import SUPERVISOR_VERSION, supervise_process

ROOT = Path(__file__).resolve().parents[1]
SPEC = "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md"
SPEC_SHA = "1486a7f69e7a2053acfcad05151a9c54cfffab776d4154141741236aa88c401b"
COMPILE_TIMEOUT_SECONDS = 600
SIMULATION_TIMEOUT_SECONDS = 60
CHECKPOINT_INTERVAL_SECONDS = 15
SOURCES = ("src/s2b_control_csr.sv", "src/s2b_hp0_word_adapter.sv", "src/s2b_request_guard.sv",
           "src/s2a_control_csr.sv", "src/s2a_memory_master.sv", "src/s2a_runtime_shell.sv",
           "sim/tb_s2b_control_csr.sv", "verification/test_s2b_control_csr_rtl.py",
           "verification/s2b_process_supervisor.py", "verification/s15_job_guard.py",
           "verification/test_s2b_process_supervisor.py")
REGRESSION_MODULES = (
    ("adapter", "verification/test_s2b_hp0_word_adapter_rtl.py", "s2b_t10"),
    ("guard", "verification/test_s2b_request_guard_rtl.py", "s2b_t09"),
)
REGRESSION_SUPERVISOR_TIMEOUT_SECONDS = 420
REGRESSION_CHILD_CODE = textwrap.dedent("""
    import importlib.util
    import json
    import sys
    from pathlib import Path

    module_path, work_path, evidence_path, toolchain_path, result_path, module_name = sys.argv[1:]
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = {"status": "FAIL", "runs": []}
    try:
        module.run(Path(work_path), Path(evidence_path), Path(toolchain_path), report)
        exit_code = 0 if report.get("status", "").startswith("PASS_") else 2
    except BaseException as error:
        report["status"] = "FAIL"
        report["error"] = f"{type(error).__name__}: {error}"
        exit_code = 2
    Path(result_path).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    sys.exit(exit_code)
""").strip()


def sha(path: Path) -> str:
    """哈希原始文件字节。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checkpoint(evidence: Path, record: dict, log: Path, started: float, message: str,
               details: dict | None = None) -> None:
    """追加运行检查点并同步到终端，便于长编译期间恢复观察。"""
    item = {"time": datetime.now().astimezone().isoformat(timespec="milliseconds"),
        "phase": record["name"], "message": message,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "process_id": record.get("process_id"), "exit_code": record.get("exit_code"),
        "log_bytes": log.stat().st_size if log.exists() else 0}
    if details:
        item["supervisor"] = details
    with (evidence / "runner_checkpoints.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(item, ensure_ascii=False) + "\n")
        stream.flush()
    print(json.dumps(item, ensure_ascii=False), flush=True)


def execute(name: str, command: list[str], work: Path, evidence: Path, env: dict,
            report: dict, timeout_seconds: int) -> dict:
    """用独立Job运行compile/simulation并在失败时记录完整状态。"""
    started = time.monotonic()
    log = evidence / (name + ".log")
    record = {"name": name, "command": command, "working_directory": str(work),
        "timeout_seconds": timeout_seconds, "exit_code": None, "timed_out": False,
        "status": "FAIL_LOG_OPEN", "log_path": log.relative_to(ROOT).as_posix(),
        "process_id": None, "started_at": datetime.now().astimezone().isoformat(timespec="milliseconds")}
    try:
        with log.open("x", encoding="utf-8") as stream:
            supervised = supervise_process(name=name, command=command, cwd=str(work),
                environment=env, output_stream=stream, timeout_seconds=timeout_seconds,
                checkpoint_callback=lambda details: checkpoint(
                    evidence, record, log, started, details.get("message", details.get("event", "运行中")), details))
            record.update(supervised)
            stream.flush()
    except Exception as exc:
        record["status"] = "FAIL_RUNNER_EXCEPTION"
        record["error"] = f"{type(exc).__name__}: {exc}"
    if log.exists():
        record["log_sha256"] = sha(log)
        record["log_bytes"] = log.stat().st_size
    record.setdefault("seconds", round(time.monotonic() - started, 3))
    record.setdefault("finished_at", datetime.now().astimezone().isoformat(timespec="milliseconds"))
    report["runs"].append(record)
    return record


def run_succeeded(record: dict) -> bool:
    """只有真实退出0且监督与Job清理均闭合才视为成功。"""
    return (record.get("status") == "PASS" and record.get("exit_code") == 0
        and record.get("timed_out") is False and record.get("cleanup_confirmed") is True)


def manifest_run_status(record: dict) -> str:
    """将监督器终态转换为不会掩盖超时或清理失败的清单状态。"""
    if run_succeeded(record):
        return "PASS"
    if str(record.get("status", "")).startswith("BLOCKED_"):
        return "BLOCKED"
    return "FAIL"


def load_module(module_path: str, module_name: str):
    """按仓库内精确路径加载既有回归入口。"""
    spec = importlib.util.spec_from_file_location(module_name, ROOT / module_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"回归模块不可加载：{module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def regression_source_closure() -> tuple[list[str], list[str]]:
    """收集T10、T09的实际RTL、runner和输入绑定。"""
    source_paths = []
    input_paths = []
    for _name, module_path, module_name in REGRESSION_MODULES:
        module = load_module(module_path, module_name)
        source_paths.extend((module_path, *module.SOURCES))
        input_paths.extend((module.MODEL, module.SPEC))
    return list(dict.fromkeys(source_paths)), list(dict.fromkeys(input_paths))


def run_supervised_regression(name: str, module_path: str, module_name: str,
                              work: Path, evidence: Path, toolchain: Path,
                              env: dict, report: dict) -> None:
    """在独立Job内运行既有module.run及其全部后代工具进程。"""
    sub_work, sub_evidence = work / name, evidence / name
    sub_work.mkdir(); sub_evidence.mkdir()
    child_result_path = sub_evidence / "supervised_child_result.json"
    command = [sys.executable, "-c", REGRESSION_CHILD_CODE,
        str(ROOT / module_path), str(sub_work), str(sub_evidence), str(toolchain),
        str(child_result_path), module_name]
    supervisor_run = execute(name + "_regression", command, work, evidence, env,
        report, REGRESSION_SUPERVISOR_TIMEOUT_SECONDS)
    child_result = None
    if child_result_path.is_file():
        try:
            child_result = json.loads(child_result_path.read_text(encoding="utf-8"))
        except Exception as error:
            child_result = {"status": "FAIL_CHILD_RESULT_INVALID",
                "error": f"{type(error).__name__}: {error}", "runs": []}
    if child_result is None:
        child_result = {"status": "FAIL_CHILD_RESULT_MISSING", "runs": []}
    inner_runs_ok = bool(child_result.get("runs")) and all(
        row.get("exit_code") == 0 and row.get("timed_out") is not True
        for row in child_result.get("runs", []))
    module_status = child_result.get("status")
    full_pass = (run_succeeded(supervisor_run)
        and isinstance(module_status, str) and module_status.startswith("PASS_") and inner_runs_ok)
    child_result["module_status"] = module_status
    child_result["supervisor_run_status"] = supervisor_run.get("status")
    child_result["supervisor_cleanup_confirmed"] = supervisor_run.get("cleanup_confirmed")
    child_result["status"] = "PASS_SUPERVISED_REGRESSION" if full_pass else "FAIL_SUPERVISED_REGRESSION"
    report[name + "_regression"] = child_result
    if not full_pass:
        raise RuntimeError(f"{name}回归的子模块、监督器或Job清理未通过")


def _tool_version(command: list[str], cwd: Path, env: dict) -> str:
    """读取工具首行版本；命令失败时不启动正式compile。"""
    completed = subprocess.run(command, cwd=cwd, env=env, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", timeout=30)
    if completed.returncode != 0 or not completed.stdout.strip():
        raise RuntimeError(f"工具版本查询失败：{command!r} exit={completed.returncode}")
    return completed.stdout.strip().splitlines()[0]


def run(work: Path, evidence: Path, toolchain: Path, report: dict,
        include_adapter_regression: bool = False) -> None:
    """冻结实际源码并严格Wall编译真实控制/内核CSR/内存master/adapter闭包。"""
    if sha(ROOT / SPEC) != SPEC_SHA:
        raise ValueError("候选契约SHA变化")
    source_paths = list(SOURCES)
    input_paths = [SPEC]
    if include_adapter_regression:
        extra_sources, extra_inputs = regression_source_closure()
        source_paths.extend(extra_sources)
        input_paths.extend(extra_inputs)
    source_paths = list(dict.fromkeys(source_paths))
    input_paths = list(dict.fromkeys(input_paths))
    report["sources"] = [{"path": p, "sha256": sha(ROOT / p)} for p in source_paths]
    report["inputs"] = [{"path": p, "sha256": sha(ROOT / p)} for p in input_paths]
    (work / "source").mkdir(); (evidence / "source_snapshot").mkdir()
    for p in source_paths:
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
    gxx, make = tools_dir / "g++.exe", make_dir / "make.exe"
    report["tool_versions"] = {
        "python": sys.version.split()[0],
        "windows": platform.platform(),
        "psutil": importlib.metadata.version("psutil"),
        "process_supervisor": SUPERVISOR_VERSION,
        "verilator": _tool_version([str(verilator), "--version"], work, env),
        "g++": _tool_version([str(gxx), "--version"], work, env),
        "make": _tool_version([str(make), "--version"], work, env),
    }
    report["tool_files"] = [{"path": str(p), "sha256": sha(p)}
        for p in (verilator, gxx, make)]
    compile_command = [str(verilator), "--binary", "--timing", "--timescale", "1ns/1ps", "-Wall", "--output-groups", "8",
        "-j", "1", "--threads", "1", "--top-module", "tb_s2b_control_csr", "--Mdir", "obj_dir",
        "-MAKEFLAGS", "PYTHON3='\"" + sys.executable + "\"'", "-CFLAGS", "-D_GLIBCXX_USE_CXX11_ABI=0 -O0",
        *["source/" + Path(p).name for p in SOURCES if p.endswith(".sv")]]
    compile_run = execute("compile", compile_command, work, evidence, env, report,
        COMPILE_TIMEOUT_SECONDS)
    if not run_succeeded(compile_run):
        report["simulation"] = {"status": "NOT_RUN", "started": False,
            "exit_code": None, "reason": f"编译监督未通过：{compile_run.get('status')}；禁止启动仿真。"}
        if str(compile_run.get("status", "")).startswith("BLOCKED_"):
            report["status"] = compile_run["status"]
        raise RuntimeError("编译或资源/Job监督未成功完成，禁止启动本Run仿真")
    simulation_run = execute("simulation", [str(work / "obj_dir/Vtb_s2b_control_csr.exe")], work,
        evidence, env, report, SIMULATION_TIMEOUT_SECONDS)
    report["simulation"] = {"status": "PASS" if run_succeeded(simulation_run) else simulation_run["status"],
        "started": True, "exit_code": simulation_run.get("exit_code"),
        "reason": None if run_succeeded(simulation_run) else "仿真退出、资源监视或Job清理未通过。"}
    if not run_succeeded(simulation_run):
        raise RuntimeError(f"仿真监督未通过：{simulation_run.get('status')}")
    report["rtl_functional_check"] = {"status": "RUNNING",
        "reason": "正在核验仿真PASS标记、固定样本数和四相位覆盖。"}
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
    report["rtl_functional_check"] = {"status": "PASS",
        "reason": "唯一PASS标记、固定128随机/25集成数、两组四相位覆盖均匹配。"}
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
        "simulation": SIMULATION_TIMEOUT_SECONDS, "checkpoint_interval": CHECKPOINT_INTERVAL_SECONDS,
        "adapter_regression_supervisor": REGRESSION_SUPERVISOR_TIMEOUT_SECONDS},
        "simulation": {"status": "NOT_RUN", "started": False, "exit_code": None,
            "reason": "尚未启动；主compile通过后才允许运行。"},
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
        run(work, evidence, args.toolchain.absolute(), report, args.adapter_regression)
        if args.adapter_regression:
            env = os.environ.copy()
            for name, module_path, module_name in REGRESSION_MODULES:
                run_supervised_regression(name, module_path, module_name, work, evidence,
                    args.toolchain.absolute(), env, report)
            report["status"] = "PASS_RTL_SIMULATION_AND_ADAPTER_REGRESSION"
    except Exception as exc:
        if not str(report.get("status", "")).startswith("BLOCKED_"):
            report["status"] = "FAIL"
        report["error"] = str(exc)
        if report.get("rtl_functional_check", {}).get("status") == "RUNNING":
            report["rtl_functional_check"] = {"status": "FAIL",
                "reason": f"仿真功能/覆盖核验失败：{type(exc).__name__}: {exc}"}
            report["simulation"]["status"] = "FAIL_FUNCTIONAL_RESULT"
            report["simulation"]["reason"] = report["rtl_functional_check"]["reason"]
    report["elapsed_seconds"] = round(time.monotonic() - started, 3)
    (evidence / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files = [{"path": row["path"], "sha256": row["sha256"], "role": "source"}
        for row in report.get("sources", [{"path": p, "sha256": sha(ROOT / p)} for p in SOURCES])]
    files += [{"path": row["path"], "sha256": row["sha256"], "role": "input"}
        for row in report.get("inputs", [{"path": SPEC, "sha256": sha(ROOT / SPEC)}])]
    files += [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p),
        "role": "source" if p.parent.name=="source_snapshot" else "log" if p.suffix==".log" else "result"}
        for p in sorted(evidence.rglob("*")) if p.is_file()]
    checks = [{"name": r["name"] + "_control", "status": manifest_run_status(r),
        "command": subprocess.list2cmdline(r["command"]), "exit_code": r.get("exit_code"),
        "reason": f"supervisor_status={r.get('status')}; timed_out={r.get('timed_out')}; cleanup_confirmed={r.get('cleanup_confirmed')}。"}
        for r in report.get("runs", [])]
    if not any(r["name"] == "compile" for r in report.get("runs", [])):
        checks.append({"name": "compile", "status": "BLOCKED", "command": None,
            "exit_code": None, "reason": report.get("error", "编译未启动。")})
    for name in ("adapter", "guard"):
        regression = report.get(name + "_regression")
        if regression is not None:
            wrapper = next(r for r in report["runs"] if r["name"] == name + "_regression")
            checks.append({"name": name + "_full_regression",
                "status": "PASS" if regression.get("status") == "PASS_SUPERVISED_REGRESSION" else "FAIL",
                "command": subprocess.list2cmdline(wrapper["command"]),
                "exit_code": wrapper.get("exit_code"),
                "reason": f"module_status={regression.get('module_status')}; supervisor_status={regression.get('supervisor_run_status')}。"})
    if report.get("simulation", {}).get("status") == "NOT_RUN":
        checks.append({"name": "simulation", "status": "BLOCKED", "command": None,
            "exit_code": None, "reason": report["simulation"].get("reason")})
    functional = report.get("rtl_functional_check")
    if functional is None:
        checks.append({"name": "RTL断言与覆盖", "status": "BLOCKED", "command": None,
            "exit_code": None, "reason": "仿真未到达功能标记及固定计数核验。"})
    else:
        sim_run = next((r for r in report.get("runs", []) if r["name"] == "simulation"), None)
        checks.append({"name": "RTL断言与覆盖", "status": functional["status"],
            "command": None if sim_run is None else subprocess.list2cmdline(sim_run["command"]),
            "exit_code": None if sim_run is None else sim_run.get("exit_code"),
            "reason": functional["reason"]})
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
