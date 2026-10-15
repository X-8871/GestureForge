"""在受控Job内运行已导出的同范围XSim矩阵，保存每阶段原生退出码。"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
WORK = ROOT / "tmp/2B/S2B-T11" / EVIDENCE.name
PREFLIGHT = ROOT / "report/evidence/S2B-T11/control_r18_xsim_preflight_20261016_r01"
sys.path.insert(0, str(ROOT))
from verification.s2b_process_supervisor import supervise_process, GIB


def sha(path):
    """按字节绑定实际运行输入。"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save():
    """每个检查点写入结果，保留终止前最后状态。"""
    (EVIDENCE / "result.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def checkpoint(payload):
    """保留监督器启动与运行检查点。"""
    with (EVIDENCE / "checkpoints.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
    print(json.dumps(payload, ensure_ascii=False), flush=True)


def package():
    """失败和成功均绑定本Run全部原件，不把包装通过当作功能通过。"""
    paths = sorted(path for path in EVIDENCE.rglob("*") if path.is_file()
                   and path.name != "delivery_manifest.json")
    paths.append(EVIDENCE / "result.json")
    paths += [ROOT / entry["path"] for entry in report["sources"]]
    paths.append(PREFLIGHT / "delivery_manifest.json")
    paths.append(PREFLIGHT / "native_tool_versions.txt")
    unique_paths = {path.relative_to(ROOT).as_posix(): path for path in paths}
    final_result = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    manifest = {
        "schema_version": 1, "stage": "2B", "task_id": "S2B-T11",
        "run_id": EVIDENCE.name, "source_commit": report["source_commit"],
        "evidence_dir": EVIDENCE.relative_to(ROOT).as_posix(),
        "interfaces": [{"name": "阶段2B物理接口候选", "version": "s2b-physical-candidate/0.1.2",
                        "frozen": False, "path": "docs/obsidian-project/02-方案设计/s2b_physical_interface_candidate.md",
                        "sha256": "1486a7f69e7a2053acfcad05151a9c54cfffab776d4154141741236aa88c401b"}],
        "files": [{"path": name, "sha256": hashlib.sha256(final_result).hexdigest() if path == EVIDENCE / "result.json" else sha(path),
                   "role": "source" if path.suffix in (".py", ".cmd", ".sv", ".prj", ".tcl", ".ini") else "input" if EVIDENCE not in path.parents else "log" if path.suffix == ".log" else "result",
                   "keep_reason": "保留本次实际输入、执行脚本、工具记录或原始结果以供复核。"}
                  for name, path in sorted(unique_paths.items())],
        "checks": [{"name": "xsim_complete_csr_matrix", "status": "PASS" if report["status"] == "PASS_RTL_SIMULATION_ONLY" else "BLOCKED" if report["status"] == "BLOCKED" else "FAIL",
                    "command": f"{sys.executable} -B {Path(__file__).resolve()}",
                    "exit_code": 0 if report["status"] == "PASS_RTL_SIMULATION_ONLY" else 1,
                    "reason": report.get("error", "全部阶段、原生退出、Job清理与完整矩阵判据均满足。")},
                   {"name": "hardware_validation", "status": "NOT_APPLICABLE", "command": None, "exit_code": None,
                    "reason": "本Run仅离线RTL矩阵，不访问板卡。"}],
        "limitations": report["limitations"],
        "tool_versions": {"Python": sys.version, "XSim": "2026.1；原生版本查询原件绑定预检包"},
    }
    (EVIDENCE / "delivery_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


report = {
    "source_commit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "status": "NOT_RUN", "stages": [], "sources": [],
    "stage_disposition": {name: {"status": "NOT_RUN", "reason": "尚未通过前置条件或尚未进入该阶段。"}
                          for name in ("compile", "elaborate", "simulation")},
    "resource_policy": {"start_floor_bytes": int(4.5 * GIB),
                        "stop_floor_bytes": 2 * GIB,
                        "reason": "XSim首次受控试验，独立工具预算；Verilator默认10GiB不变。"},
    "limitations": ["本次只做RTL矩阵仿真，不是板上验证。", "不更改断言、样本数、覆盖、RTL和testbench。"],
    "tool_identities": [],
}

if (EVIDENCE / "result.json").exists():
    raise RuntimeError("本Run已存在结果，禁止重跑覆盖")

try:
    snapshots = EVIDENCE / "source_snapshot"
    snapshots.mkdir()
    preflight_manifest_path = PREFLIGHT / "delivery_manifest.json"
    expected_manifest_sha = "32ce831d41bb91e753c84b1944547086ec6ed6805de4db72c3a16f39b2f916bc"
    if sha(preflight_manifest_path) != expected_manifest_sha:
        raise RuntimeError("已提交预检清单哈希发生变化")
    report["preflight_manifest"] = {"path": preflight_manifest_path.relative_to(ROOT).as_posix(),
                                    "sha256": expected_manifest_sha}
    preflight_manifest = json.loads(preflight_manifest_path.read_text(encoding="utf-8"))
    bindings = {entry["path"]: entry["sha256"] for entry in preflight_manifest["files"]}
    for entry in preflight_manifest["files"]:
        path = ROOT / entry["path"]
        if not path.is_file() or sha(path) != entry["sha256"]:
            raise RuntimeError(f"预检清单绑定发生变化：{path}")
        if entry["path"].startswith(("src/", "sim/")):
            report["sources"].append(entry)
    if len(report["sources"]) != 7:
        raise RuntimeError("预检SV闭包不是7份")
    actual_prj = (WORK / "tb_s2b_control_csr_vlog.prj").read_text(encoding="utf-8")
    actual_sv = re.findall(r'"([^"\r\n]+\.sv)"', actual_prj)
    expected_sv = {str(PREFLIGHT / "source_snapshot" / Path(entry["path"]).name).replace("\\", "/"):
                   entry["sha256"] for entry in report["sources"]}
    if len(actual_sv) != 7 or set(actual_sv) != set(expected_sv):
        raise RuntimeError("prj实际编译文件不等于冻结的7份SV快照")
    for name in actual_sv:
        if sha(Path(name)) != expected_sv[name]:
            raise RuntimeError(f"实际编译SV快照已变化：{name}")
        report["sources"].append({"path": Path(name).relative_to(ROOT).as_posix(),
                                  "sha256": expected_sv[name]})
    for name in ("s2b_process_supervisor.py", "s15_job_guard.py"):
        source = ROOT / "verification" / name
        shutil.copy2(source, snapshots / name)
        report["sources"].append({"path": source.relative_to(ROOT).as_posix(), "sha256": sha(source)})
    for name in ("tb_s2b_control_csr_vlog.prj", "tb_s2b_control_csr.tcl", "xsim.ini"):
        reference = PREFLIGHT / "exported_scripts" / name
        if sha(WORK / name) != bindings[reference.relative_to(ROOT).as_posix()]:
            raise RuntimeError(f"导出脚本已变化：{name}")
        shutil.copy2(WORK / name, EVIDENCE / name)
    old_log = WORK / "simulate.log"
    retained_old_log = WORK / "simulate.preflight_only.log"
    if old_log.is_file():
        if sha(old_log) != bindings[(PREFLIGHT / "exported_scripts/simulate.log").relative_to(ROOT).as_posix()]:
            raise RuntimeError("工作目录含来源不明的既有simulate.log")
        if retained_old_log.exists():
            raise RuntimeError("预检旧日志的保留目标已存在")
        shutil.copy2(old_log, EVIDENCE / "preflight_simulate.log")
        old_log.rename(retained_old_log)
    commands = [
        ("compile", "xvlog", "--incr -L uvm -prj tb_s2b_control_csr_vlog.prj -log xvlog.log", "xvlog.log", 600),
        ("elaborate", "xelab", "--incr --debug typical --mt off -L xil_defaultlib -L uvm -L unisims_ver -L unimacro_ver -L secureip --snapshot tb_s2b_control_csr_behav xil_defaultlib.tb_s2b_control_csr -log elaborate.log", "elaborate.log", 600),
        ("simulation", "xsim", "tb_s2b_control_csr_behav -key {Behavioral:sim_1:Functional:tb_s2b_control_csr} -tclbatch tb_s2b_control_csr.tcl -log simulate.log", "simulate.log", 60),
    ]
    report["status"] = "RUNNING"
    save()
    for name, tool, arguments, native_log, timeout in commands:
        native_exit = WORK / f"native_exit_{name}.txt"
        if native_exit.exists() or (WORK / native_log).exists():
            raise RuntimeError(f"阶段输出已存在，禁止覆盖或消费旧输出：{name}")
        wrapper = EVIDENCE / f"{name}.cmd"
        executable = Path(f"D:/Xilinx/2026.1/Vivado/bin/{tool}.bat")
        if not executable.is_file():
            raise RuntimeError(f"精确工具路径不存在：{executable}")
        report["tool_identities"].append({"path": str(executable), "sha256": sha(executable)})
        wrapper.write_text(
            '@echo off\n'
            + f'call "{executable}" {arguments}\n'
            + 'set "NATIVE_RC=%errorlevel%"\n'
            + f'> "{native_exit}" echo %NATIVE_RC%\n'
            + 'exit /b %NATIVE_RC%\n', encoding="utf-8", newline="\r\n")
        report["stage_disposition"][name] = {"status": "RUNNING"}
        save()
        with (EVIDENCE / f"{name}.stdout.log").open("wb") as stream:
            record = supervise_process(
                name=name, command=[str(Path(os.environ["SystemRoot"]) / "System32/cmd.exe"), "/d", "/c", str(wrapper)],
                cwd=str(WORK), environment=dict(os.environ), output_stream=stream,
                timeout_seconds=timeout, start_floor_bytes=int(4.5 * GIB),
                stop_floor_bytes=2 * GIB, checkpoint_callback=checkpoint)
        report["stages"].append(record)
        for source, destination in ((WORK / native_log, EVIDENCE / f"{name}.native.log"),
                                    (native_exit, EVIDENCE / native_exit.name)):
            if source.is_file():
                shutil.copy2(source, destination)
        native_rc = int(native_exit.read_text(encoding="utf-8").strip()) if native_exit.is_file() else None
        record["native_exit_code"] = native_rc
        report["stage_disposition"][name] = {"status": record["status"], "native_exit_code": native_rc}
        save()
        if not (record["status"] == "PASS" and record["exit_code"] == 0
                and record["timed_out"] is False and record["cleanup_confirmed"] is True
                and native_rc == 0):
            if record["status"].startswith("BLOCKED_"):
                report["status"] = "BLOCKED"
            raise RuntimeError(f"阶段未通过：{name} {record['status']} native={native_rc}")
        transcript = (EVIDENCE / f"{name}.stdout.log").read_text(encoding="utf-8", errors="replace")
        transcript += "\n" + (EVIDENCE / f"{name}.native.log").read_text(encoding="utf-8", errors="replace")
        if re.search(r"(?im)^\s*(?:ERROR:|FATAL(?:_ERROR)?:|Fatal:)|\$fatal", transcript):
            raise RuntimeError(f"阶段原始日志含错误：{name}")
    text = (EVIDENCE / "simulation.native.log").read_text(encoding="utf-8", errors="replace")
    matches = re.findall(r"PASS CONTROL_CSR directed=(\d+) random=(\d+) integration=(\d+) cycles=(\d+) status=(\d+) error=(\d+) debug=(\d+) starts=(\d+) resets=(\d+) acks=(\d+)", text)
    if len(matches) != 1:
        raise RuntimeError("缺少唯一完整PASS计数标记")
    report["simulation_counts"] = dict(zip(
        ("directed", "random", "integration", "cycles", "status", "error", "debug", "starts", "resets", "acks"), map(int, matches[0])))
    if report["simulation_counts"]["random"] != 128 or report["simulation_counts"]["integration"] != 25:
        raise RuntimeError("固定样本数不一致")
    phase = re.findall(r"COVERAGE phases=(\d+),(\d+),(\d+),(\d+) logical_responses=(\d+) seed=0x2b111010", text)
    runtime = re.findall(r"RUNTIME_PHASES phases=(\d+),(\d+),(\d+),(\d+)", text)
    if len(phase) != 1 or list(map(int, phase[0][:4])) != [1] * 4:
        raise RuntimeError("四相位独立错误覆盖缺失")
    if len(runtime) != 1 or list(map(int, runtime[0])) != [1] * 4:
        raise RuntimeError("runtime四相位覆盖缺失")
    report["phase_coverage"] = list(map(int, phase[0][:4]))
    report["logical_responses"] = int(phase[0][4])
    report["runtime_phase_coverage"] = list(map(int, runtime[0]))
    for entry in report["sources"]:
        if sha(ROOT / entry["path"]) != entry["sha256"]:
            raise RuntimeError(f"运行期间源码变化：{entry['path']}")
    report["status"] = "PASS_RTL_SIMULATION_ONLY"
except Exception as error:
    if report["status"] != "BLOCKED":
        report["status"] = "FAIL"
    report["error"] = f"{type(error).__name__}: {error}"
finally:
    try:
        # 清单先绑定拟写的最终结果；只有清单写入成功后才发布最终PASS结果。
        package()
        save()
    except Exception as error:
        report["status"] = "FAIL_EVIDENCE_PACKAGING"
        report["evidence_error"] = f"{type(error).__name__}: {error}"
        try:
            save()
        except Exception as save_error:
            print(f"无法保存失败结果：{save_error!r}", file=sys.stderr, flush=True)
        print(f"证据封包失败：{error!r}", file=sys.stderr, flush=True)
print(report["status"], flush=True)
sys.exit(0 if report["status"] == "PASS_RTL_SIMULATION_ONLY" else 1)
