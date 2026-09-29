#!/usr/bin/env python3
"""准备并核验 T57 row21 的 CPU oracle、Vivado 工程仿真和逐字节证据。"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PureWindowsPath
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE_HEAD = "8c47ecf8118960a94ce81ad54ea494b85b7e2daa"
T56_REPORT = ROOT / "report/evidence/S2A-T56/layer35_row20_all_channels.json"
T56_REPORT_SHA256 = "44a25b6b5af6f8868dd2cb9780c4834bdd87860ba43a71b0c696c0b67627da12"
T56_SUMMARY = ROOT / "report/evidence/S2A-T56/mcp_project_run01/simulation_summary.json"
T56_SUMMARY_SHA256 = "eceb674cdc63c25bcc990885e27a81690efbd1312a095a07fd1d8c3235ac9e0b"
T56_RUNNER = ROOT / "verification/test_s2a_conv_layer35_row20_all_channels_rtl.py"
T56_RUNNER_SHA256 = "74be10fa915cd9cdb38d4d0329f72c529322317cda758789098489bc1ad4fd58"
T54_RUNNER = ROOT / "verification/test_s2a_conv_layer35_row18_all_channels_rtl.py"
T54_RUNNER_SHA256 = "4ec6a743d6a80c380505be2a8601879c311a7f42e07323027098c07a8dadd4f3"
G0_PATH = ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
G0_SHA256 = "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"
T01_PATH = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
T01_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
T23_PATH = ROOT / "report/evidence/S2A-T23/conv_requant_parameter_table.json"
T23_SHA256 = "396dc66aa3ccc41050cc8183bff16b86143a6f5553cf38fed16b0ba8b4eb4ae1"
GF8_SHA256 = "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39"
EVIDENCE_ROOT = ROOT / "report/evidence/S2A-T57"
RUN_ROOT = EVIDENCE_ROOT / "run09" / "attempt09"
FIXTURE_ROOT = RUN_ROOT / "fixture"
FINAL_REPORT = RUN_ROOT / "layer35_row21_all_channels.json"
PREPARE_REPORT = RUN_ROOT / "prepare_summary.json"
RECOVERY_RECORD = RUN_ROOT / "attempt09_recovery.json"
VERIFY_ONLY_LOG = RUN_ROOT / "verify_only.log"
RUN_SUMMARY = RUN_ROOT / "run_summary.json"
STAGE_STATUS = RUN_ROOT / "stage_status.json"
PROCESS_STATUS = RUN_ROOT / "process_status.json"
T56_PARENT_SOURCES = (
    "src/int8_conv_tap_geometry.sv",
    "src/int8_conv_weight_address.sv",
    "src/int8_mac_accumulator.sv",
    "src/s2a_conv_engine.sv",
    "src/s2a_conv_layer35_channel_probe.sv",
    "sim/tb_s2a_conv_layer35_row20_all_channels.sv",
    "sim/s2a_t56_no_wave.tcl",
    "verification/test_s2a_conv_layer35_row20_all_channels_rtl.py",
)
RTL_PATHS = T56_PARENT_SOURCES[:5]
T57_SOURCE_PATHS = (
    *RTL_PATHS,
    "sim/tb_s2a_conv_layer35_row21_all_channels.sv",
    "sim/s2a_t57_no_wave.tcl",
    "verification/test_s2a_conv_layer35_row21_all_channels_rtl.py",
    "verification/test_s2a_t57_attempt09_transcript.py",
    "report/evidence/S2A-T57/run_project_sim.tcl",
    "verification/run_s2a_t57_project_sim.ps1",
)
SIMULATION_COMPILE_SOURCE_PATHS = (
    *RTL_PATHS,
    "sim/tb_s2a_conv_layer35_row21_all_channels.sv",
)
XPR_PATH = ROOT / "vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr"
XPR_PREFLIGHT = EVIDENCE_ROOT / "project_preflight_binding.json"
ENV_PREFLIGHT = EVIDENCE_ROOT / "environment_preflight.json"
SCRATCH_PROJECT_DIRECTORY = RUN_ROOT / "isolated_project"
SCRATCH_PROJECT_NAME = "s2a_t57_row21_isolated"
T57_RUNNER_RELATIVE = "verification/test_s2a_conv_layer35_row21_all_channels_rtl.py"
T57_TRANSCRIPT_TEST_RELATIVE = "verification/test_s2a_t57_attempt09_transcript.py"
T57_RECOVERY_CONTROLLER_RELATIVE = "verification/run_s2a_t57_project_sim.ps1"
T57_RECOVERY_DELTA_PATHS = (T57_RUNNER_RELATIVE, T57_TRANSCRIPT_TEST_RELATIVE)
T57_PREPARED_RUNNER_SHA256 = "85a903ab016b319d3431fae33d2b6285ae0b7eeec61b648dcfb723fcb8c3bdd8"
T57_PREPARED_TRANSCRIPT_TEST_SHA256 = "f889c496a3922a89fbdf2defdf35500e8e87f039974be0faca9400fbd146591e"
T57_PREPARED_WRAPPER_SHA256 = "ea4f50ba0557b04e8be42a8fcf90b26f1db15ec7bb53acd5e8114d5d01abbc5d"
T57_PARSER_FIX_RUNNER_SHA256 = "e47f5290c8562d88b22eea17ca521ddb1972d1b8ad70bb846a582ed898540358"
T57_PARSER_FIX_TEST_SHA256 = "2e0599940551ff71942956ee82629f1daf6ccc984cd84069a55f7f829164ca14"
T57_ATTEMPT09_CONSOLE_SHA256 = "421933be6d255abd5bf4189e2e6b71b4e7f036f1217f4e0689d1a03f2676e403"
T57_ATTEMPT09_PREPARE_SHA256 = "325dfeb5728777155bc224489a5115f3a31c746aad0ed8dc1af8eb0e2d8658a7"
T57_ATTEMPT09_FIXTURE_MANIFEST_SHA256 = "3ab48a2c786c64c0636199db9081c8ca6c4ce8f7c9a6e9994255ff17cf023b2f"
T57_ATTEMPT09_STAGE_FAIL_SHA256 = "2cf2ba3d014917f495077fd8ca4213a5ac3101fb113a7340773c8cf604ccb592"
T57_ATTEMPT09_PROCESS_FAIL_SHA256 = "f31a18797345d809543489103bffbbdc3ea29c65ad52199e32e419b5d93785f8"
T57_ATTEMPT09_RUN_FAIL_SHA256 = "0e6e297ef0eeb8e640308491bcffeb0c64cb93cefc702f49d9b5d70708174448"
POINTS = tuple((21, x) for x in range(26))
RAW_COUNT = 6_656
INT8_COUNT = 6_656
RAW_BYTES = RAW_COUNT * 4
INT8_BYTES = INT8_COUNT
GOLDEN_BYTES = RAW_BYTES + INT8_BYTES
FEATURE_BYTES = 259_584
WEIGHT_BYTES = 884_736
SIMSET = "sim_s2a_t57_row21"
TOP = "tb_s2a_conv_layer35_row21_all_channels"
PROJECT_SIM_TCL = EVIDENCE_ROOT / "run_project_sim.tcl"
PROJECT_SIM_WRAPPER = ROOT / "verification/run_s2a_t57_project_sim.ps1"
XSIM_CUSTOM_TCL = RUN_ROOT / "xsim_run.tcl"
XSIM_SIMULATE_TRANSCRIPT = RUN_ROOT / "xsim_simulate_transcript.log"
COMPILE_SOURCE_MANIFEST = RUN_ROOT / "compile_source_manifest.tsv"
XSIM_CUSTOM_TCL_TEXT = (
    'puts "T57_CUSTOM_TCL_SENTINEL=run09_attempt09"\n'
    "run all\n"
    "quit\n"
)


class T57Error(RuntimeError):
    """表示 T57 的冻结绑定、仿真或逐字节核验失败。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T57Error(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> tuple[dict[str, Any], str]:
    data = path.read_bytes()
    value = json.loads(data.decode("utf-8"))
    _require(isinstance(value, dict), f"JSON 根节点不是对象：{path}")
    return value, _sha256(data)


def _write_json_exclusive(path: Path, value: dict[str, Any]) -> None:
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(payload)


def _write_json_replace(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    _require(not temporary.exists() and not temporary.is_symlink(),
             f"拒绝覆盖临时报告：{temporary}")
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with temporary.open("xb") as stream:
        stream.write(payload)
    temporary.replace(path)


def _write_bytes_replace(path: Path, payload: bytes) -> None:
    temporary = path.with_name(path.name + ".recovery.tmp")
    _require(not temporary.exists() and not temporary.is_symlink(),
             f"拒绝覆盖临时证据：{temporary}")
    with temporary.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def _capture_json_snapshot(path: Path) -> dict[str, Any]:
    info = path.lstat()
    _require(path.is_file() and not path.is_symlink() and
             (getattr(info, "st_file_attributes", 0) & 0x400) == 0,
             f"恢复前 JSON 快照不是普通文件：{path}")
    data = path.read_bytes()
    value = json.loads(data.decode("utf-8"))
    _require(isinstance(value, dict), f"恢复前 JSON 不是对象：{path}")
    return {"path": str(path.resolve()), "bytes": len(data),
            "sha256": _sha256(data), "base64": base64.b64encode(data).decode("ascii")}


def _decode_json_snapshot(snapshot: dict[str, Any], expected_path: Path) -> tuple[bytes, dict[str, Any]]:
    _require(snapshot.get("path") == str(expected_path.resolve()),
             f"恢复快照路径不匹配：{expected_path}")
    try:
        data = base64.b64decode(str(snapshot.get("base64", "")), validate=True)
        value = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise T57Error(f"恢复快照编码或 JSON 无效：{expected_path}") from exc
    _require(len(data) == snapshot.get("bytes") and _sha256(data) == snapshot.get("sha256") and
             isinstance(value, dict) and
             ("parsed" not in snapshot or snapshot.get("parsed") == value),
             f"恢复快照字节、SHA 或解析值不一致：{expected_path}")
    return data, value


def _validate_recoverable_failure_shape(
        stage: dict[str, Any], process: dict[str, Any], run_summary: dict[str, Any]) -> None:
    """只接受 attempt09 已记录的单一 transcript PASS 解析器误报。"""
    stage_failure = str(stage.get("failure", ""))
    wrapper = stage.get("wrapper_finalization", {})
    extraction_failure = str(stage.get(
        "simulate_log_extraction_failure",
        wrapper.get("transcript_extraction_failure", "")))
    process_failure = str(process.get("failure", ""))
    _require(stage.get("status") == "SIMULATION_FLOW_FAIL" and
             stage.get("compile_exit_code") == 0 and
             stage.get("elaboration_exit_code") == 0 and
             stage.get("vivado_process_exit_code") == 0 and
             stage.get("simulate_step_tcl_code") is None and
             stage.get("xsim_exit_code") is None and
             stage.get("xsim_exit_code_captured") is False and
             stage.get("wdb_generated") is False,
             "attempt09 原 stage 状态不符合受限恢复前提")
    _require(stage_failure.startswith("XSim transcript 提取失败：Python transcript extractor 返回非零：1；") and
             stage_failure.count("T57Error: XSim transcript PASS") == 1 and
             stage_failure.count("缺少运行证据：xsim_simulate_transcript.log") == 1 and
             stage_failure.endswith("Vivado/XSim transcript 不完整：custom= pass= progress= finish= errors=") and
             extraction_failure.startswith("Python transcript extractor 返回非零：1；") and
             extraction_failure.count("T57Error: XSim transcript PASS") == 1 and
             "int8=" not in extraction_failure,
             "attempt09 failure 不是唯一的旧 PASS 缺少 int8 字段解析误报")
    _require(wrapper.get("original_status") == "SIMULATION_FLOW_RUNNING" and
             wrapper.get("terminal_status") == "SIMULATION_FLOW_FAIL" and
             wrapper.get("transcript_extraction_exit_code") == 1 and
             wrapper.get("transcript_extraction_failure") == extraction_failure and
             process_failure == stage_failure and process.get("cleanup_failure") is None,
             "attempt09 wrapper/process failure 不唯一或未绑定同一解析错误")
    _require(run_summary.get("overall_status") == "FAIL" and
             run_summary.get("simulation_flow_status") == "SIMULATION_FLOW_FAIL" and
             run_summary.get("data_verification_status") == "NOT_RUN" and
             run_summary.get("failure") == "Simulation-flow gate 未通过；未执行 data verify-only。" and
             run_summary.get("verify_only", {}).get("exit_code") is None and
             run_summary.get("verify_only", {}).get("report") is None and
             run_summary.get("verify_only", {}).get("log") is None,
             "attempt09 run_summary 含额外失败或 data verify-only 已运行")


def _validate_recovery_source_delta(
        prepared_hashes: dict[str, Any], current_hashes: dict[str, str]) -> dict[str, str]:
    """限定源快照差异只落在已授权的 runner、专项测试和恢复 wrapper。"""
    _require(set(prepared_hashes) == set(T57_SOURCE_PATHS) and
             set(current_hashes) == set(T57_SOURCE_PATHS),
             "T57 恢复源码绑定集合不完整")
    expected_prepared = {
        T57_RUNNER_RELATIVE: T57_PREPARED_RUNNER_SHA256,
        T57_TRANSCRIPT_TEST_RELATIVE: T57_PREPARED_TRANSCRIPT_TEST_SHA256,
        T57_RECOVERY_CONTROLLER_RELATIVE: T57_PREPARED_WRAPPER_SHA256,
    }
    for relative, expected in expected_prepared.items():
        record = prepared_hashes[relative]
        bound = record.get("sha256") if isinstance(record, dict) else record
        _require(str(bound).lower() == expected,
                 f"attempt09 prepare 源绑定未匹配冻结 SHA：{relative}")
    changed = {relative for relative in T57_SOURCE_PATHS
               if str((prepared_hashes[relative].get("sha256")
                       if isinstance(prepared_hashes[relative], dict)
                       else prepared_hashes[relative])).lower() !=
               str(current_hashes[relative]).lower()}
    _require(changed == set(T57_RECOVERY_DELTA_PATHS) |
             {T57_RECOVERY_CONTROLLER_RELATIVE},
             f"T57 当前源变化超出 parser/test/recovery wrapper：{sorted(changed)}")
    return {relative: str(current_hashes[relative]).lower()
            for relative in T57_SOURCE_PATHS}


def _assert_recovery_outputs_absent(paths: tuple[Path, ...]) -> None:
    collisions = [str(path) for path in paths if path.exists() or path.is_symlink()]
    _require(not collisions, f"受限恢复输出路径已存在，拒绝覆盖：{collisions}")


def _windows_vivado_process_snapshot() -> list[dict[str, Any]]:
    command = (
        "$names=@('vivado.exe','xsim.exe','xsimk.exe','xelab.exe','xvlog.exe',"
        "'vivado_lab.exe','xsct.exe','xvhdl.exe'); "
        "$items=@(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop | "
        "Where-Object { $names -contains $_.Name.ToLowerInvariant() } | "
        "Sort-Object ProcessId | ForEach-Object { [ordered]@{name=$_.Name;process_id=[int]$_.ProcessId} }); "
        "ConvertTo-Json -InputObject $items -Compress -Depth 4"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
        check=False,
    )
    _require(result.returncode == 0,
             f"读取 Vivado/XSim 实时进程快照失败：{result.stderr.strip()}")
    try:
        value = json.loads(result.stdout.strip() or "[]")
    except json.JSONDecodeError as exc:
        raise T57Error("Vivado/XSim 实时进程快照不是有效 JSON") from exc
    if isinstance(value, dict):
        value = [value]
    _require(isinstance(value, list), "Vivado/XSim 实时进程快照类型错误")
    return value


def _artifact(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "bytes": path.stat().st_size,
            "sha256": _sha_file(path)}


def _current_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
        text=True, encoding="utf-8", errors="replace", check=False,
    )
    _require(result.returncode == 0, f"读取 Git HEAD 失败：{result.stderr.strip()}")
    return result.stdout.strip()


def _head_is_ancestor(base_head: str, current_head: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", base_head, current_head],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise T57Error(f"git merge-base --is-ancestor 失败：{result.stderr.strip()}")


def _verify_file_record(record: dict[str, Any], label: str) -> Path:
    path = Path(str(record.get("path", "")))
    if not path.is_absolute():
        path = ROOT / path
    _require(path.is_file(), f"{label} 工件不存在：{path}")
    if "bytes" in record:
        _require(path.stat().st_size == int(record["bytes"]), f"{label} 字节数不符：{path}")
    if "sha256" in record:
        _require(_sha_file(path) == str(record["sha256"]).lower(), f"{label} SHA-256 不符：{path}")
    return path


def _verify_parent() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    current_head = _current_head()
    _require(_head_is_ancestor(BASE_HEAD, current_head),
             f"T57 冻结基线不是当前 HEAD 的祖先：baseline={BASE_HEAD} current={current_head}")
    _require(T56_REPORT.is_file() and _sha_file(T56_REPORT) == T56_REPORT_SHA256,
             "T56 canonical 报告缺失或 SHA-256 不匹配")
    parent, _ = _read_json(T56_REPORT)
    _require(parent.get("task_id") == "S2A-T56" and
             parent.get("status") == "PASS_SIMULATION_DATA_ONLY" and
             parent.get("acceptance_status") == "PASS_INDEPENDENT_REVIEW_DATA_ONLY",
             "T56 父报告状态或独立审查状态不匹配")
    _require(parent.get("scope") ==
             "tiny416 cfg section36 layer35; all 256 output channels at y=20, x=0..25; not full layer or network",
             "T56 父报告范围不匹配")
    bindings = parent.get("bindings", {})
    _require(bindings.get("fixed_points_yx") == [[20, x] for x in range(26)],
             "T56 父报告固定坐标不是 y=20、x=0..25")
    parent_sources = bindings.get("T56_source_hashes", {})
    _require(set(parent_sources) == set(T56_PARENT_SOURCES),
             "T56 父报告源码绑定集合不匹配")
    for relative, expected in parent_sources.items():
        source = ROOT / relative
        _require(source.is_file() and _sha_file(source) == str(expected).lower(),
                 f"T56 已审查源码绑定不匹配：{relative}")
    _require(parent_sources.get("verification/test_s2a_conv_layer35_row20_all_channels_rtl.py") ==
             T56_RUNNER_SHA256, "T56 runner SHA-256 与冻结值不符")

    simulation = parent.get("simulation", {})
    _require(simulation.get("status") == "PASS_SIMULATION_DATA_ONLY" and
             simulation.get("raw_int32_compares") == RAW_COUNT and
             simulation.get("int8_compares") == INT8_COUNT and
             simulation.get("progress_checkpoint_count") == 256 and
             simulation.get("raw_byte_identical_to_independent_golden") is True and
             simulation.get("int8_byte_identical_to_independent_golden") is True and
             simulation.get("raw_mismatch_bytes") == 0 and
             simulation.get("int8_mismatch_bytes") == 0 and
             simulation.get("wdb_generated") is False,
             "T56 仿真证据字段不匹配")
    t56_run = bindings.get("mcp_project_run01", {})
    _require(t56_run.get("summary_sha256") == T56_SUMMARY_SHA256,
             "T56 仿真摘要 SHA-256 与 canonical 绑定不匹配")
    summary_path = _verify_file_record({"path": str(T56_SUMMARY),
                                        "sha256": T56_SUMMARY_SHA256},
                                       "T56 仿真摘要")
    summary, _ = _read_json(summary_path)
    _require(summary.get("status") == "PASS_SIMULATION_DATA",
             "T56 仿真摘要不是 PASS_SIMULATION_DATA")
    _require(bindings.get("G0_specification", {}).get("sha256") == G0_SHA256 and
             bindings.get("T01_manifest", {}).get("sha256") == T01_SHA256 and
             bindings.get("T23_parameter_table", {}).get("sha256") == T23_SHA256 and
             bindings.get("GF8_package", {}).get("sha256") == GF8_SHA256,
             "T56 继承的 G0/T01/T23/GF8 SHA-256 与冻结值不匹配")

    artifacts = simulation.get("artifacts", {})
    for name in ("compile.log", "elaborate.log", "simulate.log",
                 "observed_raw.bin", "observed_output.bin"):
        _require(name in artifacts, f"T56 缺少仿真工件绑定：{name}")
        _verify_file_record(artifacts[name], f"T56 {name}")
    return parent, bindings, simulation


def _load_t54_oracle_runner(runtime_head: str) -> tuple[Any, str]:
    _require(T54_RUNNER.is_file() and _sha_file(T54_RUNNER) == T54_RUNNER_SHA256,
             "T54 独立 oracle 源码缺失或 SHA-256 不匹配")
    module_name = "s2a_t54_reviewed_oracle_for_t57"
    spec = importlib.util.spec_from_file_location(module_name, T54_RUNNER)
    _require(spec is not None and spec.loader is not None, "无法载入 T54 独立 oracle")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    historical_head = str(module.BASE_HEAD)
    module.BASE_HEAD = runtime_head
    return module, historical_head


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative in T57_SOURCE_PATHS:
        path = ROOT / relative
        _require(path.is_file(), f"缺少 T57 仿真源码：{relative}")
        hashes[relative] = _sha_file(path)
    return hashes


def _source_bindings(relative_paths: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    bindings: dict[str, dict[str, Any]] = {}
    for relative in relative_paths:
        path = ROOT / relative
        _require(path.is_file() and not path.is_symlink(),
                 f"源码不是普通文件：{relative}")
        info = path.stat()
        _require((getattr(info, "st_file_attributes", 0) & 0x400) == 0,
                 f"源码是 reparse point：{relative}")
        bindings[relative] = {
            "path": str(path.resolve()),
            "bytes": info.st_size,
            "sha256": _sha_file(path),
        }
    return bindings


def _compile_source_manifest_bytes(
        bindings: list[dict[str, Any]]) -> bytes:
    lines = ["GestureForge-S2A-T57-compile-source-manifest-v1"]
    for record in bindings:
        lines.append("\t".join((str(record["sha256"]), str(record["bytes"]),
                                str(record["path"]))))
    return ("\n".join(lines) + "\n").encode("utf-8")


def _vectors_bytes(vectors: list[tuple[int, int, int, int, int, int, int, int]]) -> bytes:
    return ("".join(" ".join(str(value) for value in vector) + "\n"
                    for vector in vectors)).encode("ascii")


def _prepare() -> dict[str, Any]:
    parent, parent_bindings, parent_simulation = _verify_parent()
    current_head = _current_head()
    _require(_head_is_ancestor(BASE_HEAD, current_head),
             f"T57 准备态 current_head 不在冻结基线之后：{current_head}")
    _require(EVIDENCE_ROOT.is_dir(), f"T57 evidence 根目录不是目录：{EVIDENCE_ROOT}")
    run_root_precreated = RUN_ROOT.exists() or RUN_ROOT.is_symlink()
    if run_root_precreated:
        run_root_info = RUN_ROOT.lstat()
        _require(RUN_ROOT.is_dir() and not RUN_ROOT.is_symlink() and
                 (getattr(run_root_info, "st_file_attributes", 0) & 0x400) == 0,
                 f"T57 run 根必须是普通目录：{RUN_ROOT}")
        _require(not any(RUN_ROOT.iterdir()),
                 f"拒绝复用非空 T57 run 目录：{RUN_ROOT}")
    _require(not PREPARE_REPORT.exists(), f"拒绝覆盖已有 T57 准备摘要：{PREPARE_REPORT}")
    _require(not FINAL_REPORT.exists(), f"拒绝覆盖已有 T57 最终报告：{FINAL_REPORT}")
    _require(not FIXTURE_ROOT.exists(), f"拒绝复用已有 T57 fixture 目录：{FIXTURE_ROOT}")
    _require(XPR_PATH.is_file(), f"目标 XPR 缺失：{XPR_PATH}")
    _require(XPR_PREFLIGHT.is_file(), f"缺少工程预检绑定：{XPR_PREFLIGHT}")
    _require(ENV_PREFLIGHT.is_file(), f"缺少环境预检绑定：{ENV_PREFLIGHT}")
    xpr_binding, _ = _read_json(XPR_PREFLIGHT)
    environment, _ = _read_json(ENV_PREFLIGHT)
    _require(xpr_binding.get("project_name") == "AX7Z020_Gesture" and
             xpr_binding.get("project_path") == str(XPR_PATH.resolve()),
             "工程预检不是目标 AX7Z020_Gesture XPR")
    xpr_sha = _sha_file(XPR_PATH)
    _require(xpr_sha == xpr_binding.get("xpr_sha256_before_run"),
             "XPR 当前 SHA-256 与工程预检快照不一致")
    _require(environment.get("vivado_mcp", {}).get("status") == "NOT_REACHABLE" and
             environment.get("vivado_processes_before_run") == [],
             "MCP 或 Vivado/XSim 进程预检状态与本轮记录不一致")

    oracle_runner, historical_oracle_head = _load_t54_oracle_runner(current_head)
    inputs = oracle_runner._load_frozen_inputs()
    input_bindings = inputs["bindings"]
    _require(input_bindings["T01_manifest"]["sha256"] == T01_SHA256 and
             input_bindings["T23_parameter_table"]["sha256"] == T23_SHA256 and
             input_bindings["GF8_package"]["sha256"] == GF8_SHA256,
             "T54 oracle 返回的模型/量化输入绑定不匹配")
    _require(inputs["weight_sha256"] == parent_bindings["weight_layer35"]["sha256"] and
             len(inputs["weight_bytes"]) == WEIGHT_BYTES,
             "layer35 GF8 权重与 T56 继承权重不一致")
    oracle = oracle_runner._build_oracle(inputs, progress=True, points=POINTS)
    _require(len(oracle["feature"]) == FEATURE_BYTES and
             len(oracle["raw_values"]) == RAW_COUNT and
             len(oracle["quantized_values"]) == INT8_COUNT and
             len(oracle["combined_golden"]) == GOLDEN_BYTES,
             "T57 oracle 输出长度或逐项比较数错误")
    _require(oracle["oracle"]["raw_int32_count"] == RAW_COUNT and
             oracle["oracle"]["quantized_int8_count"] == INT8_COUNT and
             oracle["oracle"]["d2_t23_match_count"] == INT8_COUNT,
             "T57 oracle 的 raw/INT8/MQ 逐项计数错误")
    _require(all(y == 21 for y, _ in POINTS) and
             tuple(x for _, x in POINTS) == tuple(range(26)),
             "T57 点集不是 y=21、x=0..25")
    _require(_current_head() == current_head,
             "T57 prepare-only 期间 Git HEAD 发生变化")

    if not run_root_precreated:
        RUN_ROOT.mkdir(parents=False, exist_ok=False)
    FIXTURE_ROOT.mkdir(parents=False, exist_ok=False)
    with XSIM_CUSTOM_TCL.open("xb") as stream:
        stream.write(XSIM_CUSTOM_TCL_TEXT.encode("utf-8"))
    source_hashes = _source_hashes()
    source_bindings = _source_bindings(T57_SOURCE_PATHS)
    _require(all(source_hashes[relative] == source_bindings[relative]["sha256"]
                 for relative in T57_SOURCE_PATHS),
             "T57 源码哈希与路径/大小绑定在准备时不一致")
    compile_source_bindings = [
        _source_bindings((relative,))[relative]
        for relative in SIMULATION_COMPILE_SOURCE_PATHS
    ]
    custom_tcl_record = _artifact(XSIM_CUSTOM_TCL)
    with COMPILE_SOURCE_MANIFEST.open("xb") as stream:
        stream.write(_compile_source_manifest_bytes(compile_source_bindings))
    compile_source_manifest_record = _artifact(COMPILE_SOURCE_MANIFEST)
    blobs = {
        "feature_input.bin": oracle["feature"],
        "layer35_weights.bin": inputs["weight_bytes"],
        "golden.bin": oracle["combined_golden"],
        "vectors.txt": _vectors_bytes(oracle["vectors"]),
    }
    expected_sizes = {"feature_input.bin": FEATURE_BYTES,
                      "layer35_weights.bin": WEIGHT_BYTES,
                      "golden.bin": GOLDEN_BYTES}
    for name, content in blobs.items():
        _require(name not in expected_sizes or len(content) == expected_sizes[name],
                 f"T57 fixture 长度错误：{name}")
        path = FIXTURE_ROOT / name
        with path.open("xb") as stream:
            stream.write(content)
    fixture_files = {name: _artifact(path) for name, path in
                     ((name, FIXTURE_ROOT / name) for name in blobs)}
    fixture_manifest_path = FIXTURE_ROOT / "fixture_manifest.json"
    fixture_manifest = {
        "schema": "GestureForge-S2A-T57-fixture-manifest-v3",
        "task_id": "S2A-T57",
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "current_head": current_head,
        "parent_report": {"path": str(T56_REPORT.resolve()),
                          "sha256": T56_REPORT_SHA256},
        "generator_source": {"path": str(T54_RUNNER.resolve()),
                             "sha256": T54_RUNNER_SHA256},
        "runner_source_sha256": _sha_file(Path(__file__).resolve()),
        "T57_source_hashes": source_hashes,
        "T57_source_bindings": source_bindings,
        "simulation_compile_sources": compile_source_bindings,
        "compile_source_manifest": compile_source_manifest_record,
        "xsim_custom_tcl": custom_tcl_record,
        "fixture_root": str(FIXTURE_ROOT.resolve()),
        "files": fixture_files,
        "oracle": oracle["oracle"],
        "fixed_points_yx": [list(point) for point in POINTS],
    }
    _write_json_exclusive(fixture_manifest_path, fixture_manifest)

    layer = inputs["layer35"]
    summary = {
        "schema": "GestureForge-S2A-T57-preparation-summary-v3",
        "task_id": "S2A-T57",
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "current_head": current_head,
        "scope": "tiny416 cfg section36 layer35; all 256 output channels at y=21, x=0..25",
        "T56_parent_report": {"path": str(T56_REPORT.resolve()),
                              "sha256": T56_REPORT_SHA256,
                              "acceptance_status": parent["acceptance_status"],
                              "fixed_points_yx": parent_bindings["fixed_points_yx"]},
        "T56_summary": {"path": str(T56_SUMMARY.resolve()),
                        "sha256": T56_SUMMARY_SHA256},
        "T56_simulation": {key: parent_simulation[key] for key in
                           ("raw_int32_compares", "int8_compares",
                            "progress_checkpoint_count", "raw_byte_identical_to_independent_golden",
                            "int8_byte_identical_to_independent_golden")},
        "oracle_source": {
            "path": str(T54_RUNNER.resolve()),
            "sha256": T54_RUNNER_SHA256,
            "methods": ["_load_frozen_inputs", "_build_oracle"],
            "historical_BASE_HEAD": historical_oracle_head,
            "T57_baseline_head": BASE_HEAD,
            "runtime_head_guard": current_head,
            "reason": "T54 冻结 oracle 的源码 SHA 与所有输入绑定保持固定；T57 将其仅用于当前 HEAD 相等性检查的模块内守卫设为准备时 current_head，并单独保留 T57 的祖先基线。",
        },
        "bindings": {
            "G0_specification": {"path": str(G0_PATH.resolve()), "sha256": G0_SHA256},
            "T01_manifest": input_bindings["T01_manifest"],
            "T23_parameter_table": input_bindings["T23_parameter_table"],
            "GF8_package": input_bindings["GF8_package"],
            "weight_layer35": {"byte_offset": inputs["layer35_weight_offset"],
                               "bytes": len(inputs["weight_bytes"]),
                               "sha256": inputs["weight_sha256"]},
            "model": {"name": "tiny416", "cfg_section": layer["cfg_section"],
                      "layer_index": layer["layer_index"],
                      "input_shape_nchw": layer["input_shape_nchw"],
                      "output_shape_nchw": layer["output_shape_nchw"],
                      "kernel_hw": layer["kernel_hw"], "stride_hw": layer["stride_hw"],
                      "padding_lrtb": layer["padding_lrtb"],
                      "padding_value_int8": layer["padding_value_int8"],
                      "layout": layer["layout"],
                      "accumulator_bits": layer["accumulator_bits"]},
            "fixed_points_yx": [list(point) for point in POINTS],
            "T56_source_hashes": parent_bindings["T56_source_hashes"],
            "T57_source_hashes": source_hashes,
            "T57_source_bindings": source_bindings,
            "simulation_compile_sources": compile_source_bindings,
            "compile_source_manifest": compile_source_manifest_record,
            "xsim_custom_tcl": custom_tcl_record,
            "oracle_source": {"path": str(T54_RUNNER.resolve()),
                              "sha256": T54_RUNNER_SHA256},
        },
        "fixture": {"root": str(FIXTURE_ROOT.resolve()),
                    "files": fixture_files,
                    "manifest": _artifact(fixture_manifest_path),
                    "golden_layout": {"raw_int32_le_bytes": RAW_BYTES,
                                      "int8_bytes": INT8_BYTES,
                                      "total_bytes": GOLDEN_BYTES,
                                      "order": "全部 raw INT32 little-endian，随后全部 INT8"}},
        "feature_fixture": oracle["fixture"],
        "oracle": oracle["oracle"],
        "expected_counts": oracle["expected_counts"],
        "project_preflight": {"path": str(XPR_PREFLIGHT.resolve()),
                              "sha256": _sha_file(XPR_PREFLIGHT),
                              "binding_file": _artifact(XPR_PREFLIGHT),
                              "target_xpr_sha256": xpr_sha,
                              "T57_source_hashes": source_hashes,
                              "T57_source_bindings": source_bindings,
                              "simulation_compile_sources": compile_source_bindings,
                              "compile_source_manifest": compile_source_manifest_record,
                              "compile_source_scope": "isolated T57 project compiles only simulation_compile_sources; source paths and hashes are explicitly bound above"},
        "environment_preflight": {"path": str(ENV_PREFLIGHT.resolve()),
                                  "sha256": _sha_file(ENV_PREFLIGHT),
                                  "vivado_mcp_status": environment["vivado_mcp"]["status"],
                                  "vivado_processes_before_run": environment["vivado_processes_before_run"]},
        "simulation": {"status": "NOT_RUN", "control": "CUSTOM_TCL_RUN_ALL",
                       "custom_tcl": custom_tcl_record,
                       "compile_exit_code": None,
                       "elaboration_exit_code": None, "xsim_exit_code": None,
                       "simset": SIMSET, "top": TOP},
        "review": {"G2": "NOT_REVIEWED", "G3": "NOT_CLAIMED",
                    "G4": "NOT_CLAIMED", "G5": "NOT_CLAIMED"},
        "limitations": ["仅验证 y=21、x=0..25、256 个输出通道，不代表 layer35 全层或整网。",
                        "本报告只记仿真数据；G2 须由独立 reviewer 审核，G3/G4/G5 未声明通过。"],
    }
    _write_json_exclusive(PREPARE_REPORT, summary)
    print(json.dumps({"result": summary["status"],
                      "prepare_report": str(PREPARE_REPORT.resolve()),
                      "fixture_root": str(FIXTURE_ROOT.resolve()),
                      "source_hashes": source_hashes,
                      "counts": {"raw_int32": RAW_COUNT, "int8": INT8_COUNT,
                                 "progress_checkpoints_expected": 256},
                      "oracle": oracle["oracle"],
                      "fixture_files": fixture_files}, ensure_ascii=False, indent=2),
          flush=True)
    return summary


def _parse_pass_line(sim_log: str) -> tuple[str, dict[str, int]]:
    lines = [line for line in sim_log.splitlines() if line.startswith("PASS T57 ")]
    _require(len(lines) == 1, f"PASS T57 行数不是 1：{len(lines)}")
    values = {key: int(value) for key, value in
              re.findall(r"(?:^|\s)([A-Za-z][A-Za-z0-9_]*)=(-?\d+)", lines[0])}
    return lines[0], values


def _verify_xsim_transcript_text(sim_log: str) -> tuple[str, dict[str, int], list[int], int]:
    """核验已经截取的 custom Tcl 到 XSim $finish 输出，兼容 CRLF。"""
    sentinel_count = len(re.findall(
        r"(?m)^T57_CUSTOM_TCL_SENTINEL=run09_attempt09[ \t]*\r?$", sim_log))
    _require(sentinel_count == 1, f"XSim transcript sentinel 行数不是 1：{sentinel_count}")
    _require(not re.search(r"(?im)^[ \t]*(?:ERROR|FATAL)(?:[ \t]|:)", sim_log),
             "XSim transcript 含 ERROR/FATAL")
    progress = [int(value) for value in re.findall(
        r"(?m)^PROGRESS T57 outputs=(\d+)/6656[ \t]*\r?$", sim_log)]
    _require(progress == list(range(26, 6657, 26)) and len(progress) == 256,
             "T57 transcript progress 必须从 26 到 6656、间隔 26 且恰好 256 个")
    pass_line, pass_values = _parse_pass_line(sim_log)
    _require(pass_values.get("outputs") == RAW_COUNT and
             pass_values.get("raw") == RAW_COUNT,
             "XSim transcript PASS outputs/raw 计数不匹配")
    finish_matches = list(re.finditer(
        r"\$finish called at time[ \t]*:[ \t]*(\d+)[ \t]+ns", sim_log))
    _require(len(finish_matches) == 1, f"XSim transcript $finish 行数不是 1：{len(finish_matches)}")
    finish_time_ns = int(finish_matches[0].group(1))
    _require(finish_time_ns > 1000, "XSim transcript 未证明运行超过默认 1000ns")
    return pass_line, pass_values, progress, finish_time_ns


def _extract_xsim_transcript(console_bytes: bytes) -> tuple[bytes, dict[str, int]]:
    """按实际 sentinel 与唯一 $finish 从 Vivado console 保留原始字节片段。"""
    lines = console_bytes.splitlines(keepends=True)
    sentinel_pattern = re.compile(rb"^T57_CUSTOM_TCL_SENTINEL=run09_attempt09[ \t]*$")
    line_bodies = [line.rstrip(b"\r\n") for line in lines]
    sentinel_indices = [index for index, line in enumerate(line_bodies)
                        if sentinel_pattern.fullmatch(line)]
    _require(len(sentinel_indices) == 1,
             f"Vivado console 中实际 sentinel 行数不是 1：{len(sentinel_indices)}")
    start_index = sentinel_indices[0]
    finish_pattern = re.compile(rb"\$finish called at time[ \t]*:[ \t]*(\d+)[ \t]+ns")
    finish_matches: list[tuple[int, re.Match[bytes]]] = []
    for index in range(start_index + 1, len(lines)):
        match = finish_pattern.search(line_bodies[index])
        if match is not None:
            finish_matches.append((index, match))
    _require(len(finish_matches) == 1,
             f"实际 sentinel 后的 $finish 行数不是 1：{len(finish_matches)}")
    end_index, finish_match = finish_matches[0]
    segment = b"".join(lines[start_index:end_index + 1])
    segment_text = segment.decode("utf-8", errors="replace")
    _, _, progress, finish_time_ns = _verify_xsim_transcript_text(segment_text)
    _require(finish_time_ns == int(finish_match.group(1)),
             "截取片段中的 $finish 与 console 边界不一致")
    return segment, {"start_line": start_index + 1,
                     "end_line": end_index + 1,
                     "progress_checkpoint_count": len(progress),
                     "finish_time_ns": finish_time_ns}


def _extract_xsim_transcript_file() -> dict[str, Any]:
    """将唯一 run09 console 的 XSim 执行片段独占写入 attempt 根目录。"""
    expected_root = ROOT / "report/evidence/S2A-T57/run09/attempt09"
    _require(RUN_ROOT.resolve() == expected_root.resolve(),
             "拒绝从非固定的 attempt09 根目录提取 XSim transcript")
    _require(RUN_ROOT.is_dir() and not RUN_ROOT.is_symlink(),
             "attempt09 根目录不是普通目录")
    for directory in (EVIDENCE_ROOT, RUN_ROOT.parent, RUN_ROOT):
        info = directory.lstat()
        _require(directory.is_dir() and not directory.is_symlink() and
                 (getattr(info, "st_file_attributes", 0) & 0x400) == 0,
                 f"attempt09 证据路径链包含 reparse point 或非目录：{directory}")
    console_path = RUN_ROOT / "vivado_batch_console.log"
    _require(console_path.is_file() and not console_path.is_symlink(),
             "缺少普通文件 vivado_batch_console.log")
    _require(not XSIM_SIMULATE_TRANSCRIPT.exists() and
             not XSIM_SIMULATE_TRANSCRIPT.is_symlink(),
             "拒绝覆盖已存在的 xsim_simulate_transcript.log")
    console_bytes = console_path.read_bytes()
    transcript_bytes, facts = _extract_xsim_transcript(console_bytes)
    with XSIM_SIMULATE_TRANSCRIPT.open("xb") as stream:
        stream.write(transcript_bytes)
    record = {
        "schema": "S2A-T57-xsim-transcript-extraction-v1",
        "status": "PASS",
        "algorithm": "byte_lines_unique_sentinel_through_unique_finish_v1",
        "source": {"path": str(console_path.resolve()),
                   "bytes": len(console_bytes), "sha256": _sha256(console_bytes)},
        "transcript": _artifact(XSIM_SIMULATE_TRANSCRIPT),
        "line_range_1based_inclusive": [facts["start_line"], facts["end_line"]],
        "progress_checkpoint_count": facts["progress_checkpoint_count"],
        "finish_time_ns": facts["finish_time_ns"],
    }
    print(json.dumps(record, ensure_ascii=False, separators=(",", ":")), flush=True)
    return record


def _require_artifact_record(record: dict[str, Any], label: str) -> None:
    _require({"path", "bytes", "sha256"}.issubset(record),
             f"{label} 缺少 path、bytes 或 SHA-256 字段")
    _require(isinstance(record.get("bytes"), int) and record["bytes"] >= 0,
             f"{label} 字节数字段格式错误")
    _require(re.fullmatch(r"[0-9a-fA-F]{64}", str(record.get("sha256", ""))) is not None,
             f"{label} SHA-256 字段格式错误")


def _verify_prepared_fixture(
        preparation: dict[str, Any], *, allow_recovery_source_delta: bool = False,
        recovery_record: dict[str, Any] | None = None) -> tuple[dict[str, Any], str, bytes]:
    fixture = preparation.get("fixture")
    _require(isinstance(fixture, dict), "T57 prepare_summary 缺少 fixture 对象")
    _require(Path(str(fixture.get("root", ""))).resolve() == FIXTURE_ROOT.resolve(),
             "T57 fixture 根目录与准备摘要绑定不一致")

    expected_manifest_path = FIXTURE_ROOT / "fixture_manifest.json"
    manifest_record = fixture.get("manifest")
    _require(isinstance(manifest_record, dict), "T57 prepare_summary 缺少 fixture manifest 绑定")
    _require_artifact_record(manifest_record, "T57 prepare_summary manifest")
    manifest_path = _verify_file_record(manifest_record, "T57 fixture manifest")
    _require(manifest_path.resolve() == expected_manifest_path.resolve(),
             "T57 fixture manifest 路径与固定 fixture 目录不一致")
    manifest, manifest_sha256 = _read_json(manifest_path)
    _require(manifest_sha256 == str(manifest_record.get("sha256", "")).lower(),
             "T57 fixture manifest SHA-256 与 prepare_summary 不一致")
    _require(manifest.get("schema") == "GestureForge-S2A-T57-fixture-manifest-v3" and
             manifest.get("task_id") == "S2A-T57" and
             manifest.get("status") == "PREPARED_NOT_SIMULATED" and
             manifest.get("baseline_head") == BASE_HEAD and
             manifest.get("current_head") == preparation.get("current_head") and
             _head_is_ancestor(BASE_HEAD, str(preparation.get("current_head", ""))) and
             manifest.get("fixture_root") == str(FIXTURE_ROOT.resolve()) and
             manifest.get("fixed_points_yx") == [list(point) for point in POINTS],
             "T57 fixture manifest schema、状态、基线/current_head、根目录或坐标不匹配")
    _require(manifest.get("parent_report", {}).get("sha256") == T56_REPORT_SHA256,
             "T57 fixture manifest 的 T56 父报告绑定不匹配")
    prepared_source_hashes = preparation.get("bindings", {}).get("T57_source_hashes")
    _require(isinstance(prepared_source_hashes, dict) and
             set(prepared_source_hashes) == set(T57_SOURCE_PATHS),
             "T57 prepare_summary 的源码绑定集合不匹配")
    _require(manifest.get("T57_source_hashes") == prepared_source_hashes,
             "T57 fixture manifest 与 prepare_summary 源码绑定不一致")
    prepared_bindings = preparation.get("bindings", {}).get("T57_source_bindings")
    _require(isinstance(prepared_bindings, dict) and
             set(prepared_bindings) == set(T57_SOURCE_PATHS) and
             manifest.get("T57_source_bindings") == prepared_bindings,
             "T57 源码路径/大小/SHA 绑定集合或 manifest 不匹配")
    current_source_hashes = _source_hashes()
    recovery_delta: set[str] = set()
    if recovery_record is not None:
        recovery_sources = recovery_record.get("source_bindings", {})
        _require(recovery_record.get("schema") == "GestureForge-S2A-T57-attempt09-recovery-v1" and
                 recovery_record.get("prepare_summary_sha256") == _sha_file(PREPARE_REPORT) and
                 recovery_sources.get("prepared_sha256") == prepared_source_hashes and
                 recovery_sources.get("current_sha256") == current_source_hashes,
                 "attempt09 recovery record 未绑定当前 prepare_summary 与源码 SHA")
        _validate_recovery_source_delta(prepared_source_hashes, current_source_hashes)
        recovery_delta = set(T57_RECOVERY_DELTA_PATHS) | {T57_RECOVERY_CONTROLLER_RELATIVE}
    elif allow_recovery_source_delta:
        _validate_recovery_source_delta(prepared_source_hashes, current_source_hashes)
        recovery_delta = set(T57_RECOVERY_DELTA_PATHS) | {T57_RECOVERY_CONTROLLER_RELATIVE}
    for relative, expected_sha256 in prepared_source_hashes.items():
        source_path = ROOT / relative
        record = prepared_bindings[relative]
        info = source_path.stat() if source_path.exists() else None
        _require(source_path.is_file() and not source_path.is_symlink() and info is not None and
                 (getattr(info, "st_file_attributes", 0) & 0x400) == 0 and
                 str(source_path.resolve()) == record.get("path") and
                 (relative in recovery_delta or info.st_size == record.get("bytes")) and
                 str(record.get("sha256", "")).lower() == str(expected_sha256).lower() and
                 _sha_file(source_path) == current_source_hashes.get(relative) and
                 (relative in recovery_delta or current_source_hashes.get(relative) ==
                  expected_sha256),
                 f"T57 准备后源码哈希变化：{relative}")

    compile_bindings = preparation.get("bindings", {}).get("simulation_compile_sources")
    expected_compile_bindings = [prepared_bindings[relative]
                                 for relative in SIMULATION_COMPILE_SOURCE_PATHS]
    _require(compile_bindings == expected_compile_bindings and
             manifest.get("simulation_compile_sources") == compile_bindings,
             "isolated project 实际编译源路径、顺序或绑定不匹配")
    for relative, record in zip(SIMULATION_COMPILE_SOURCE_PATHS, compile_bindings):
        _require(prepared_source_hashes[relative] == record.get("sha256"),
                 f"compile source SHA 未与 T57 source map 绑定：{relative}")

    manifest_record = preparation.get("bindings", {}).get("compile_source_manifest")
    _require(isinstance(manifest_record, dict) and
             manifest.get("compile_source_manifest") == manifest_record,
             "compile-source manifest 未在 summary 与 fixture manifest 间绑定")
    _require_artifact_record(manifest_record, "T57 compile-source manifest")
    source_manifest_path = _verify_file_record(manifest_record,
                                               "T57 compile-source manifest")
    _require(source_manifest_path.resolve() == COMPILE_SOURCE_MANIFEST.resolve() and
             source_manifest_path.read_bytes() ==
             _compile_source_manifest_bytes(compile_bindings),
             "compile-source manifest 路径或内容与隔离工程源列表不一致")

    custom_tcl_record = preparation.get("bindings", {}).get("xsim_custom_tcl")
    _require(isinstance(custom_tcl_record, dict),
             "T57 prepare_summary 缺少 run09/attempt09 XSim Tcl 绑定")
    _require_artifact_record(custom_tcl_record, "T57 run09/attempt09 XSim Tcl")
    custom_tcl_path = _verify_file_record(custom_tcl_record, "T57 run09/attempt09 XSim Tcl")
    _require(custom_tcl_path.resolve() == XSIM_CUSTOM_TCL.resolve() and
             custom_tcl_path.read_text(encoding="utf-8") == XSIM_CUSTOM_TCL_TEXT,
             "T57 run09/attempt09 custom Tcl 路径或 run-all 内容不匹配")
    _require(manifest.get("xsim_custom_tcl") == custom_tcl_record,
             "T57 manifest 与 prepare_summary custom Tcl 绑定不一致")

    expected_names = {
        "feature_input.bin", "layer35_weights.bin", "golden.bin", "vectors.txt",
    }
    prepared_files = fixture.get("files")
    manifest_files = manifest.get("files")
    _require(isinstance(prepared_files, dict) and set(prepared_files) == expected_names,
             "T57 prepare_summary fixture 文件集合不匹配")
    _require(isinstance(manifest_files, dict) and set(manifest_files) == expected_names,
             "T57 fixture manifest 文件集合不匹配")

    resolved_files: dict[str, Path] = {}
    for name in sorted(expected_names):
        prepared_record = prepared_files[name]
        manifest_file_record = manifest_files[name]
        _require(isinstance(prepared_record, dict) and isinstance(manifest_file_record, dict),
                 f"T57 fixture 文件绑定格式错误：{name}")
        _require_artifact_record(prepared_record, f"prepare_summary {name}")
        _require_artifact_record(manifest_file_record, f"fixture manifest {name}")
        prepared_path = _verify_file_record(prepared_record, f"prepare_summary {name}")
        manifest_file_path = _verify_file_record(manifest_file_record, f"fixture manifest {name}")
        expected_path = FIXTURE_ROOT / name
        _require(prepared_path.resolve() == expected_path.resolve() and
                 manifest_file_path.resolve() == expected_path.resolve(),
                 f"T57 fixture 文件路径绑定不匹配：{name}")
        _require(prepared_record.get("bytes") == manifest_file_record.get("bytes") and
                 str(prepared_record.get("sha256", "")).lower() ==
                 str(manifest_file_record.get("sha256", "")).lower(),
                 f"prepare_summary 与 fixture manifest 的文件绑定不一致：{name}")
        resolved_files[name] = expected_path

    expected_sizes = {
        "feature_input.bin": FEATURE_BYTES,
        "layer35_weights.bin": WEIGHT_BYTES,
        "golden.bin": GOLDEN_BYTES,
    }
    for name, expected_size in expected_sizes.items():
        _require(prepared_files[name].get("bytes") == expected_size,
                 f"T57 fixture 长度绑定不符：{name}")

    prepared_oracle = preparation.get("oracle")
    manifest_oracle = manifest.get("oracle")
    _require(isinstance(prepared_oracle, dict) and manifest_oracle == prepared_oracle,
             "T57 fixture manifest oracle 与 prepare_summary oracle 不一致")
    runner_sha_from_prepare = preparation.get("bindings", {}).get(
        "T57_source_hashes", {}).get(T57_RUNNER_RELATIVE)
    _require(runner_sha_from_prepare is not None and
             manifest.get("runner_source_sha256") == runner_sha_from_prepare,
             "T57 fixture manifest runner SHA 与 prepare_summary 源码绑定不一致")
    _require(prepared_oracle.get("raw_int32_count") == RAW_COUNT and
             prepared_oracle.get("quantized_int8_count") == INT8_COUNT,
             "T57 oracle 输出数量绑定不匹配")

    golden = resolved_files["golden.bin"].read_bytes()
    raw_golden = golden[:RAW_BYTES]
    int8_golden = golden[RAW_BYTES:]
    combined_sha256 = _sha256(golden)
    raw_sha256 = _sha256(raw_golden)
    int8_sha256 = _sha256(int8_golden)
    _require(len(golden) == GOLDEN_BYTES and len(raw_golden) == RAW_BYTES and
             len(int8_golden) == INT8_BYTES,
             "T57 golden.bin 分段长度不匹配")
    _require(combined_sha256 == prepared_oracle.get("combined_golden_sha256") and
             combined_sha256 == manifest_oracle.get("combined_golden_sha256"),
             "T57 combined golden SHA-256 与 oracle 绑定不匹配")
    _require(raw_sha256 == prepared_oracle.get("raw_int32_le_sha256") and
             raw_sha256 == manifest_oracle.get("raw_int32_le_sha256"),
             "T57 raw INT32 分段 SHA-256 与 oracle 绑定不匹配")
    _require(int8_sha256 == prepared_oracle.get("quantized_int8_sha256") and
             int8_sha256 == manifest_oracle.get("quantized_int8_sha256"),
             "T57 INT8 分段 SHA-256 与 oracle 绑定不匹配")
    return manifest, manifest_sha256, golden


def _normalized_path_key(path: str | Path) -> str:
    return str(Path(path).resolve()).replace("\\", "/").rstrip("/").casefold()


def _same_absolute_windows_path(actual: str | Path, expected: str | Path) -> bool:
    """允许 Tcl 的正斜杠写法，同时要求盘符和完整路径完全一致。"""
    actual_path = PureWindowsPath(str(actual))
    expected_path = PureWindowsPath(str(expected))
    if (not actual_path.is_absolute() or not actual_path.drive or
            not expected_path.is_absolute() or not expected_path.drive):
        return False
    return (actual_path.as_posix().rstrip("/").casefold() ==
            expected_path.as_posix().rstrip("/").casefold())


def _batch_command(batch_path: Path, executable: str) -> str:
    text = batch_path.read_text(encoding="utf-8", errors="replace")
    matches = re.findall(
        rf"(?im)^[ \t]*call[ \t]+{re.escape(executable)}(?:\.exe)?[ \t]+(.+?)[ \t]*$",
        text,
    )
    _require(len(matches) == 1,
             f"{batch_path.name} 必须保留唯一实际 {executable} 命令，实得 {len(matches)} 条")
    return re.sub(r"[ \t]+", " ", matches[0].strip())


def _option_values(command: str, option: str) -> list[str]:
    matches = re.findall(
        rf"(?i)(?:^|[ \t]){re.escape(option)}[ \t]+(?:\{{([^}}]*)\}}|\"([^\"]*)\"|([^ \t]+))",
        command,
    )
    return [next(value for value in match if value != "") for match in matches]


def _verify_batch_script_snapshots(stage: dict[str, Any]) -> dict[str, Path]:
    """核对 compile 与 elaboration 各阶段实际生成的命令行签名。"""
    snapshot_stages = ("before_compile", "after_compile", "after_elaborate")
    snapshots: dict[str, Path] = {}
    xelab_signatures: list[str] = []
    xsim_signatures: list[str] = []
    for snapshot_stage in snapshot_stages:
        for executable, field_prefix, signatures in (
            ("xelab", "elaborate", xelab_signatures),
            ("xsim", "simulate", xsim_signatures),
        ):
            filename = f"{field_prefix}.{snapshot_stage}.bat"
            path = RUN_ROOT / filename
            status_field = f"{field_prefix}_{snapshot_stage}_batch_path"
            _require(path.is_file(), f"缺少 {snapshot_stage} 阶段仿真脚本：{path}")
            recorded_path = str(stage.get(status_field, ""))
            _require(_normalized_path_key(recorded_path) == _normalized_path_key(path),
                     f"stage_status 未绑定 {snapshot_stage} 阶段脚本：{filename}")
            signature = _batch_command(path, executable)
            signatures.append(signature)
            snapshots[filename] = path

    _require(len(set(xelab_signatures)) == 1,
             "xelab 命令签名在 compile/elaboration 阶段间变化")
    _require(len(set(xsim_signatures)) == 1,
             "xsim 命令签名在 compile/elaboration 阶段间变化")
    xelab = xelab_signatures[-1]
    simulate = xsim_signatures[-1]
    debug_values = _option_values(xelab, "--debug")
    snapshot_values = _option_values(xelab, "--snapshot")
    top_token = f"xil_defaultlib.{TOP}"
    _require(debug_values == ["off"],
             "唯一 xelab 命令必须且只能使用 --debug off")
    _require(snapshot_values == [f"{TOP}_behav"],
             "唯一 xelab 命令的 snapshot 与 T57 top 不符")
    _require(xelab.split().count(top_token) == 1,
             "唯一 xelab 命令未且仅一次指向 T57 top")

    key_values = _option_values(simulate, "-key")
    tclbatch_values = _option_values(simulate, "-tclbatch")
    testplusarg_values = _option_values(simulate, "-testplusarg")
    expected_key = f"Behavioral:{SIMSET}:Functional:{TOP}"
    expected_testplusarg = f"T57_RUN_ROOT={RUN_ROOT.resolve().as_posix()}"
    _require(simulate.split()[0] == f"{TOP}_behav",
             "唯一 xsim 命令的 snapshot 与 T57 top 不符")
    _require(key_values == [expected_key],
             "唯一 xsim 命令的 Behavioral key 与 T57 simset/top 不符")
    expected_tclbatch = XSIM_CUSTOM_TCL.resolve().as_posix()
    _require(len(tclbatch_values) == 1 and
             "\\" not in tclbatch_values[0] and
             tclbatch_values[0].casefold() == expected_tclbatch.casefold(),
             "唯一 xsim 命令的 -tclbatch 必须是 run09/attempt09 自定义 Tcl 的正斜杠绝对路径")
    _require(testplusarg_values == [expected_testplusarg],
             "唯一 xsim 命令的 -testplusarg 必须精确绑定 attempt09 根目录")
    _require(re.search(r"(?i)(?:^|[ \t])-wdb(?:[ \t=]|$)", simulate) is None,
             "唯一 xsim 命令启用了 WDB")
    _require(stage.get("elaborate_command_signature") == xelab and
             stage.get("simulate_command_signature") == simulate,
             "stage_status 命令签名与保存的实际脚本不一致")

    for executable, final_field, filename in (
        ("xelab", "elaborate_batch_path", "elaborate.after_elaborate.bat"),
        ("xsim", "simulate_batch_path", "simulate.after_elaborate.bat"),
    ):
        _require(_normalized_path_key(str(stage.get(final_field, ""))) ==
                 _normalized_path_key(RUN_ROOT / filename),
                 f"stage_status 的最终 {executable} 脚本路径不匹配")
    return snapshots


def _recovery_report_details(record: dict[str, Any]) -> dict[str, Any]:
    snapshots = record.get("original_snapshots", {})
    source_bindings = record.get("source_bindings", {})
    return {
        "method": "RECOVER_FROM_SAVED_ATTEMPT09_CONSOLE_BYTE_SLICE",
        "recovery_record_path": str(RECOVERY_RECORD.resolve()),
        "attempt_root": str(RUN_ROOT.resolve()),
        "baseline_head": BASE_HEAD,
        "prepare_summary_sha256": record.get("prepare_summary_sha256"),
        "fixture_manifest_sha256": record.get("fixture_manifest_sha256"),
        "prepared_source_sha256": source_bindings.get("prepared_sha256"),
        "recovered_source_sha256": source_bindings.get("current_sha256"),
        "source_delta_paths": source_bindings.get("delta_paths"),
        "parser_fix_checkpoint": source_bindings.get("parser_fix_checkpoint"),
        "root_cause": record.get("root_cause"),
        "original_snapshot_sha256": {
            name: value.get("sha256") for name, value in snapshots.items()
        },
        "original_states": record.get("original_states"),
        "new_states": {"stage_status": "SIMULATION_FLOW_PASS",
                       "process_status": "RECOVERY_PASS",
                       "data_verification": "PASS"},
        "console": record.get("console"),
        "transcript": record.get("transcript"),
        "vivado_batch_exit_code": 0,
        "compile_exit_code": 0,
        "elaboration_exit_code": 0,
        "simulate_step_tcl_code": None,
        "xsim_exit_code": None,
        "xsim_exit_code_captured": False,
        "exit_code_limitation": "Tcl/XSim 单独退出码未捕获；保留原始 null 事实。",
        "process_snapshots": record.get("runtime_process_snapshots"),
        "golden_byte_comparison": "PASS_FROM_STANDARD_VERIFY_ONLY",
        "recovery_report_state_at_verify": record.get("status"),
    }


def _validate_recovery_record(
        record: dict[str, Any], preparation: dict[str, Any],
        stage: dict[str, Any], process: dict[str, Any]) -> dict[str, Any]:
    _require(record.get("schema") == "GestureForge-S2A-T57-attempt09-recovery-v1" and
             record.get("task_id") == "S2A-T57" and
             record.get("attempt_root") == str(RUN_ROOT.resolve()) and
             record.get("baseline_head") == BASE_HEAD and
             record.get("prepare_summary_sha256") == T57_ATTEMPT09_PREPARE_SHA256 and
             record.get("fixture_manifest_sha256") == T57_ATTEMPT09_FIXTURE_MANIFEST_SHA256 and
             record.get("console", {}).get("sha256") == T57_ATTEMPT09_CONSOLE_SHA256 and
             record.get("simulate_step_tcl_code") is None and
             record.get("xsim_exit_code") is None and
             record.get("xsim_exit_code_captured") is False,
             "attempt09 recovery record 的固定绑定或未捕获退出码事实不匹配")
    _require(record.get("status") in ("RECOVERY_IN_PROGRESS", "RECOVERY_PASS"),
             "attempt09 recovery record 状态不是恢复进行中或通过")
    _require(record.get("prepare_summary_sha256") == _sha_file(PREPARE_REPORT) and
             record.get("fixture_manifest_sha256") ==
             preparation.get("fixture", {}).get("manifest", {}).get("sha256"),
             "attempt09 recovery record 与实际 prepare/fixture manifest 不一致")
    source_bindings = record.get("source_bindings", {})
    current_sources = _source_hashes()
    _validate_recovery_source_delta(
        preparation.get("bindings", {}).get("T57_source_hashes", {}), current_sources)
    _require(source_bindings.get("current_sha256") == current_sources and
             source_bindings.get("current_snapshot") == _source_bindings(T57_SOURCE_PATHS) and
             source_bindings.get("delta_paths") == sorted(
                 (*T57_RECOVERY_DELTA_PATHS, T57_RECOVERY_CONTROLLER_RELATIVE)),
             "attempt09 recovery record 当前源码 SHA/字节或差异路径不匹配")
    _require(source_bindings.get("parser_fix_checkpoint") == {
                 "runner_sha256": T57_PARSER_FIX_RUNNER_SHA256,
                 "transcript_test_sha256": T57_PARSER_FIX_TEST_SHA256,
                 "contract": "PASS 行只要求 outputs/raw；INT8 由 observed 文件长度与 verify-only golden 比对证明。"} and
             record.get("root_cause", {}).get("kind") ==
             "OLD_PASS_PARSER_REQUIRED_UNEMITTED_INT8_FIELD" and
             record.get("root_cause", {}).get("prepared_runner_sha256") ==
             T57_PREPARED_RUNNER_SHA256 and
             record.get("root_cause", {}).get("actual_pass_line_has_int8_field") is False,
             "attempt09 recovery record 未绑定已审 parser 修复与实际根因")
    snapshots = record.get("original_snapshots", {})
    expected = {
        "stage_status.json": (STAGE_STATUS, T57_ATTEMPT09_STAGE_FAIL_SHA256),
        "process_status.json": (PROCESS_STATUS, T57_ATTEMPT09_PROCESS_FAIL_SHA256),
        "run_summary.json": (RUN_SUMMARY, T57_ATTEMPT09_RUN_FAIL_SHA256),
    }
    original_values: dict[str, dict[str, Any]] = {}
    for name, (path, expected_sha256) in expected.items():
        _require(name in snapshots, f"recovery record 缺少原始快照：{name}")
        _, original = _decode_json_snapshot(snapshots[name], path)
        _require(snapshots[name].get("sha256") == expected_sha256,
                 f"recovery record 原始快照 SHA 与 attempt09 失败原件不符：{name}")
        original_values[name] = original
    _validate_recoverable_failure_shape(
        original_values["stage_status.json"], original_values["process_status.json"],
        original_values["run_summary.json"])
    _require(record.get("original_states") == {
                 "stage_status": "SIMULATION_FLOW_FAIL",
                 "process_failure": original_values["process_status.json"].get("failure"),
                 "run_summary": "FAIL",
                 "data_verification": "NOT_RUN"} and
             stage.get("status") == "SIMULATION_FLOW_PASS" and
             process.get("mode") == "recover" and
             process.get("failure") is None and
             stage.get("recovery_previous_failure") ==
             original_values["stage_status.json"].get("failure") and
             process.get("recovery_previous_failure") ==
             original_values["process_status.json"].get("failure"),
             "恢复记录没有保留 FAIL 历史，或当前 stage/process 未绑定恢复状态")
    runtime = record.get("runtime_process_snapshots", {})
    _require(runtime.get("before") == [] and runtime.get("after") == [],
             "恢复期间保存的 Vivado/XSim 进程快照非空")
    transcript_record = record.get("transcript", {})
    _require(transcript_record.get("path") == str(XSIM_SIMULATE_TRANSCRIPT.resolve()) and
             transcript_record.get("bytes") == XSIM_SIMULATE_TRANSCRIPT.stat().st_size and
             transcript_record.get("sha256") == _sha_file(XSIM_SIMULATE_TRANSCRIPT),
             "恢复 transcript 文件未与恢复记录绑定")
    console_bytes = (RUN_ROOT / "vivado_batch_console.log").read_bytes()
    extracted_bytes, facts = _extract_xsim_transcript(console_bytes)
    actual_pass_line, actual_pass_values, _, _ = _verify_xsim_transcript_text(
        extracted_bytes.decode("utf-8", errors="replace"))
    _require(transcript_record.get("sha256") == _sha256(extracted_bytes) and
             record.get("transcript_line_range_1based_inclusive") ==
             [facts["start_line"], facts["end_line"]] and
             record.get("root_cause", {}).get("actual_emitted_pass_line") == actual_pass_line and
             actual_pass_values.get("outputs") == RAW_COUNT and
             actual_pass_values.get("raw") == RAW_COUNT and
             "int8" not in actual_pass_values and
             (RUN_ROOT / "vivado_batch_console.log").stat().st_size ==
             record.get("console", {}).get("bytes"),
             "恢复 transcript 不等于原 console 的 sentinel 至 finish 字节片段")
    _require(record.get("verify_only", {}).get("exit_code") in (None, 0),
             "恢复记录 verify-only 退出码异常")
    return record


def _verify_attempt09_recovery_preconditions() -> tuple[
        dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], bytes,
        bytes, dict[str, int], dict[str, str]]:
    expected_attempt_root = ROOT / "report/evidence/S2A-T57/run09/attempt09"
    _require(RUN_ROOT.resolve() == expected_attempt_root.resolve() and
             _current_head() == BASE_HEAD,
             "attempt09 恢复根目录或 Git HEAD 不等于冻结目标")
    _require(RUN_ROOT.is_dir() and not RUN_ROOT.is_symlink(),
             "attempt09 根目录不是普通目录")
    _assert_recovery_outputs_absent((RECOVERY_RECORD, RECOVERY_RECORD.with_name(
        RECOVERY_RECORD.name + ".tmp"), XSIM_SIMULATE_TRANSCRIPT,
        XSIM_SIMULATE_TRANSCRIPT.with_name(XSIM_SIMULATE_TRANSCRIPT.name + ".tmp"),
        XSIM_SIMULATE_TRANSCRIPT.with_name(XSIM_SIMULATE_TRANSCRIPT.name + ".recovery.tmp"),
        FINAL_REPORT, FINAL_REPORT.with_name(FINAL_REPORT.name + ".tmp"),
        VERIFY_ONLY_LOG, VERIFY_ONLY_LOG.with_name(VERIFY_ONLY_LOG.name + ".tmp"),
        RUN_SUMMARY.with_name(RUN_SUMMARY.name + ".tmp"),
        STAGE_STATUS.with_name(STAGE_STATUS.name + ".tmp"),
        PROCESS_STATUS.with_name(PROCESS_STATUS.name + ".tmp")))
    preparation, prepare_sha256 = _read_json(PREPARE_REPORT)
    _require(prepare_sha256 == T57_ATTEMPT09_PREPARE_SHA256 and
             preparation.get("baseline_head") == BASE_HEAD and
             preparation.get("current_head") == BASE_HEAD,
             "attempt09 prepare_summary SHA 或基线绑定不匹配")
    fixture_manifest, manifest_sha256, golden = _verify_prepared_fixture(
        preparation, allow_recovery_source_delta=True)
    _require(manifest_sha256 == T57_ATTEMPT09_FIXTURE_MANIFEST_SHA256,
             "attempt09 fixture manifest SHA 不匹配")

    snapshots = {
        "stage_status.json": _capture_json_snapshot(STAGE_STATUS),
        "process_status.json": _capture_json_snapshot(PROCESS_STATUS),
        "run_summary.json": _capture_json_snapshot(RUN_SUMMARY),
    }
    expected_snapshot_hashes = {
        "stage_status.json": T57_ATTEMPT09_STAGE_FAIL_SHA256,
        "process_status.json": T57_ATTEMPT09_PROCESS_FAIL_SHA256,
        "run_summary.json": T57_ATTEMPT09_RUN_FAIL_SHA256,
    }
    for name, expected_hash in expected_snapshot_hashes.items():
        _require(snapshots[name]["sha256"] == expected_hash,
                 f"attempt09 原始 FAIL 证据 SHA 不匹配：{name}")
    _, stage = _decode_json_snapshot(snapshots["stage_status.json"], STAGE_STATUS)
    _, process = _decode_json_snapshot(snapshots["process_status.json"], PROCESS_STATUS)
    _, run_summary = _decode_json_snapshot(snapshots["run_summary.json"], RUN_SUMMARY)
    _validate_recoverable_failure_shape(stage, process, run_summary)
    _require(process.get("startup_source_bindings", {}).get("prepare_summary_sha256") ==
             prepare_sha256 and
             process.get("startup_source_bindings", {}).get("fixture_manifest_sha256") ==
             manifest_sha256 and
             process.get("startup_source_bindings", {}).get("python_runner_sha256") ==
             T57_PREPARED_RUNNER_SHA256 and
             process.get("launcher_script_sha256") == T57_PREPARED_WRAPPER_SHA256 and
             process.get("simulation_tcl_sha256") == _sha_file(PROJECT_SIM_TCL) and
             process.get("xsim_tcl_sha256") == _sha_file(XSIM_CUSTOM_TCL) and
             process.get("compile_source_manifest_sha256") ==
             _sha_file(COMPILE_SOURCE_MANIFEST),
             "attempt09 process_status 未绑定原始 prepare/仿真脚本/源码清单 SHA")
    _require(stage.get("simulate_log_origin_sha256") == T57_ATTEMPT09_CONSOLE_SHA256 and
             stage.get("simulate_log_sha256") == T57_ATTEMPT09_CONSOLE_SHA256 and
             stage.get("simulate_log_origin_bytes") == 56_666 and
             stage.get("simulate_log_bytes") == 56_666,
             "attempt09 stage_status 未绑定指定原始 console")

    xpr_binding, xpr_binding_sha256 = _read_json(XPR_PREFLIGHT)
    current_xpr_sha256 = _sha_file(XPR_PATH)
    expected_xpr_sha256 = str(preparation.get("project_preflight", {}).get(
        "target_xpr_sha256", "")).lower()
    _require(xpr_binding.get("preflight_exit_code") == 0 and
             xpr_binding.get("xpr_sha256_before_run") == expected_xpr_sha256 and
             current_xpr_sha256 == expected_xpr_sha256 and
             process.get("xpr_sha256_before") == expected_xpr_sha256 and
             process.get("xpr_sha256_after") == expected_xpr_sha256 and
             process.get("xpr_unchanged") is True and
             stage.get("source_project_xpr_sha256") == expected_xpr_sha256,
             "attempt09 XPR 当前 SHA 与原始 prepare/process 绑定不一致")
    _require(process.get("vivado_process_exit_code") == 0 and
             process.get("compile_source_manifest_sha256") ==
             preparation["bindings"]["compile_source_manifest"]["sha256"] and
             process.get("scratch_project_removed") is True and
             process.get("owner_marker_removed") is True and
             process.get("cleanup_verified") is True and
             process.get("unrelated_processes_before") == [] and
             process.get("unrelated_processes_after") == [] and
             not SCRATCH_PROJECT_DIRECTORY.exists(),
             "attempt09 原始 batch 退出、scratch 清理或历史进程门禁不满足")
    _verify_batch_script_snapshots(stage)

    console_path = RUN_ROOT / "vivado_batch_console.log"
    _require(console_path.is_file() and not console_path.is_symlink() and
             _sha_file(console_path) == T57_ATTEMPT09_CONSOLE_SHA256 and
             console_path.stat().st_size == 56_666,
             "attempt09 原 console 路径、字节或 SHA 不匹配")
    console_bytes = console_path.read_bytes()
    transcript_bytes, transcript_facts = _extract_xsim_transcript(console_bytes)
    raw_golden = golden[:RAW_BYTES]
    int8_golden = golden[RAW_BYTES:]
    raw_path = RUN_ROOT / "observed_raw.bin"
    int8_path = RUN_ROOT / "observed_output.bin"
    _require(raw_path.is_file() and int8_path.is_file() and
             raw_path.stat().st_size == RAW_BYTES and int8_path.stat().st_size == INT8_BYTES and
             raw_path.read_bytes() == raw_golden and int8_path.read_bytes() == int8_golden,
             "attempt09 observed raw/INT8 文件长度或当前 oracle byte compare 不通过")
    _require(not list(RUN_ROOT.rglob("*.wdb")),
             "attempt09 根目录存在 WDB，拒绝恢复")
    for log_path in (RUN_ROOT / "compile.log", RUN_ROOT / "elaborate.log"):
        _require(log_path.is_file() and not log_path.is_symlink(),
                 f"attempt09 缺少普通阶段日志：{log_path.name}")
    compile_text = (RUN_ROOT / "compile.log").read_text(encoding="utf-8", errors="replace")
    elaborate_text = (RUN_ROOT / "elaborate.log").read_text(encoding="utf-8", errors="replace")
    for relative in (*RTL_PATHS, "sim/tb_s2a_conv_layer35_row21_all_channels.sv"):
        _require(Path(relative).name in compile_text,
                 f"attempt09 compile.log 未包含预期源码：{relative}")
    _require(f"Built simulation snapshot {TOP}_behav" in elaborate_text,
             "attempt09 elaborate.log 未绑定目标 snapshot")
    _verify_parent()
    _require(_windows_vivado_process_snapshot() == [],
             "当前存在 Vivado/XSim 进程，拒绝执行 attempt09 recover")

    xpr_details = {"path": str(XPR_PATH.resolve()), "sha256": current_xpr_sha256,
                   "preflight_sha256": xpr_binding_sha256}
    hashes = {"prepare_summary": prepare_sha256,
              "fixture_manifest": manifest_sha256,
              "source_xpr": current_xpr_sha256,
              "console": T57_ATTEMPT09_CONSOLE_SHA256,
              "compile_log": _sha_file(RUN_ROOT / "compile.log"),
              "elaborate_log": _sha_file(RUN_ROOT / "elaborate.log"),
              "raw_observed": _sha_file(raw_path),
              "int8_observed": _sha_file(int8_path)}
    return (preparation, stage, process, run_summary, transcript_bytes,
            golden, transcript_facts, {**hashes, "xpr_details": xpr_details,
                                       "original_snapshots": snapshots,
                                       "current_source_hashes": _source_hashes(),
                                       "current_source_snapshot": _source_bindings(T57_SOURCE_PATHS)})


def _recover_attempt09() -> dict[str, Any]:
    (preparation, original_stage, original_process, original_run_summary,
     transcript_bytes, golden, transcript_facts, preflight) = \
        _verify_attempt09_recovery_preconditions()
    process_before = _windows_vivado_process_snapshot()
    _require(process_before == [], "attempt09 recover 启动前进程快照非空")
    prepared_hashes = preparation["bindings"]["T57_source_hashes"]
    current_hashes = preflight["current_source_hashes"]
    source_delta_paths = sorted(
        (set(T57_RECOVERY_DELTA_PATHS) | {T57_RECOVERY_CONTROLLER_RELATIVE}))
    source_binding_record = {
        "prepared_sha256": prepared_hashes,
        "current_sha256": current_hashes,
        "current_snapshot": preflight["current_source_snapshot"],
        "parser_fix_checkpoint": {
            "runner_sha256": T57_PARSER_FIX_RUNNER_SHA256,
            "transcript_test_sha256": T57_PARSER_FIX_TEST_SHA256,
            "contract": "PASS 行只要求 outputs/raw；INT8 由 observed 文件长度与 verify-only golden 比对证明。",
        },
        "delta_paths": source_delta_paths,
        "delta_description": (
            "仅允许 parser/verifier、attempt09 专项测试和 -Mode recover 控制器变更；"
            "RTL、TB、oracle、fixture、XPR、仿真 Tcl 与 compile/elab wrapper 仍由 prepare SHA 固定绑定。"
        ),
    }
    original_snapshots = preflight["original_snapshots"]
    recovery_record: dict[str, Any] = {
        "schema": "GestureForge-S2A-T57-attempt09-recovery-v1",
        "task_id": "S2A-T57",
        "status": "RECOVERY_IN_PROGRESS",
        "attempt_root": str(RUN_ROOT.resolve()),
        "baseline_head": BASE_HEAD,
        "prepare_summary_sha256": T57_ATTEMPT09_PREPARE_SHA256,
        "fixture_manifest_sha256": T57_ATTEMPT09_FIXTURE_MANIFEST_SHA256,
        "source_bindings": source_binding_record,
        "original_snapshots": original_snapshots,
        "original_states": {
            "stage_status": "SIMULATION_FLOW_FAIL",
            "process_failure": original_process.get("failure"),
            "run_summary": "FAIL",
            "data_verification": "NOT_RUN",
        },
        "new_states": {
            "stage_status": "SIMULATION_FLOW_PASS",
            "process_status": "RECOVERY_PASS",
            "data_verification": "PASS_AFTER_VERIFY_ONLY",
        },
        "root_cause": {
            "kind": "OLD_PASS_PARSER_REQUIRED_UNEMITTED_INT8_FIELD",
            "prepared_runner_sha256": T57_PREPARED_RUNNER_SHA256,
            "actual_pass_line_has_int8_field": False,
            "approved_parser_fix_checkpoint": T57_PARSER_FIX_RUNNER_SHA256,
            "actual_emitted_pass_line": _verify_xsim_transcript_text(
                transcript_bytes.decode("utf-8", errors="replace"))[0],
        },
        "console": {"path": str((RUN_ROOT / "vivado_batch_console.log").resolve()),
                    "bytes": 56_666,
                    "sha256": T57_ATTEMPT09_CONSOLE_SHA256,
                    "transcript_algorithm":
                    "byte_lines_unique_sentinel_through_unique_finish_v1"},
        "transcript": {"path": str(XSIM_SIMULATE_TRANSCRIPT.resolve()),
                        "bytes": len(transcript_bytes),
                        "sha256": _sha256(transcript_bytes)},
        "transcript_line_range_1based_inclusive": [
            transcript_facts["start_line"], transcript_facts["end_line"]],
        "transcript_progress_checkpoint_count": transcript_facts[
            "progress_checkpoint_count"],
        "finish_time_ns": transcript_facts["finish_time_ns"],
        "exit_codes": {
            "vivado_batch": 0,
            "compile": 0,
            "elaboration": 0,
            "simulate_step_tcl": None,
            "xsim": None,
            "xsim_exit_code_captured": False,
            "reason": "保留 attempt09 已保存事实；未伪造 Tcl/XSim 独立退出码。",
        },
        "simulate_step_tcl_code": None,
        "xsim_exit_code": None,
        "xsim_exit_code_captured": False,
        "xpr": preflight["xpr_details"],
        "compile_log": _artifact(RUN_ROOT / "compile.log"),
        "elaborate_log": _artifact(RUN_ROOT / "elaborate.log"),
        "observed": {
            "observed_raw.bin": _artifact(RUN_ROOT / "observed_raw.bin"),
            "observed_output.bin": _artifact(RUN_ROOT / "observed_output.bin"),
            "raw_int32_golden_mismatch_bytes": 0,
            "int8_golden_mismatch_bytes": 0,
        },
        "scratch_cleanup_verified": True,
        "wdb_generated": False,
        "runtime_process_snapshots": {"before": process_before, "after": None},
        "verify_only": {"command": [sys.executable, "-X", "utf8", "-B",
                                     str((ROOT / T57_RUNNER_RELATIVE).resolve()),
                                     "--verify-only"],
                        "runner_sha256": current_hashes[T57_RUNNER_RELATIVE],
                        "exit_code": None, "log": None, "report": None},
    }
    _write_json_exclusive(RECOVERY_RECORD, recovery_record)
    try:
        with XSIM_SIMULATE_TRANSCRIPT.open("xb") as stream:
            stream.write(transcript_bytes)
            stream.flush()
            os.fsync(stream.fileno())
        recovery_record["transcript"] = _artifact(XSIM_SIMULATE_TRANSCRIPT)
        _write_json_replace(RECOVERY_RECORD, recovery_record)

        recovered_stage = json.loads(json.dumps(original_stage, ensure_ascii=False))
        previous_failure = recovered_stage.get("failure")
        recovered_stage.update({
            "status": "SIMULATION_FLOW_PASS",
            "data_verification_status": "DATA_VERIFICATION_PENDING",
            "data_verification_report": None,
            "custom_tcl_executed": True,
            "simulate_log_complete": True,
            "simulate_log_path": str(XSIM_SIMULATE_TRANSCRIPT.resolve()),
            "simulate_log_source": XSIM_SIMULATE_TRANSCRIPT.name,
            "simulate_log_sha256": _sha_file(XSIM_SIMULATE_TRANSCRIPT),
            "simulate_log_bytes": XSIM_SIMULATE_TRANSCRIPT.stat().st_size,
            "simulate_log_origin_path": str((RUN_ROOT / "vivado_batch_console.log").resolve()),
            "simulate_log_origin_sha256": T57_ATTEMPT09_CONSOLE_SHA256,
            "simulate_log_origin_bytes": 56_666,
            "simulate_log_extraction_algorithm":
                "byte_lines_unique_sentinel_through_unique_finish_v1",
            "simulate_log_extraction_status": "PASS",
            "simulate_log_extraction_exit_code": 0,
            "simulate_log_extraction_failure": None,
            "simulate_log_extraction_line_range": recovery_record[
                "transcript_line_range_1based_inclusive"],
            "finish_time_ns": transcript_facts["finish_time_ns"],
            "wdb_generated": False,
            "failure": None,
            "recovery_previous_failure": previous_failure,
            "recovery_provenance": {
                "record_path": str(RECOVERY_RECORD.resolve()),
                "original_status": "SIMULATION_FLOW_FAIL",
                "terminal_status": "SIMULATION_FLOW_PASS",
                "simulate_step_tcl_code": None,
                "xsim_exit_code": None,
                "xsim_exit_code_captured": False,
            },
        })
        recovered_stage["wrapper_finalization"] = {
            "source": "PowerShell wrapper",
            "original_status": "SIMULATION_FLOW_FAIL",
            "terminal_status": "SIMULATION_FLOW_PASS",
            "recovery_controller": "attempt09 recover mode",
            "transcript_source": XSIM_SIMULATE_TRANSCRIPT.name,
            "transcript_origin": "vivado_batch_console.log",
            "transcript_origin_sha256": T57_ATTEMPT09_CONSOLE_SHA256,
            "transcript_extraction_algorithm":
                "byte_lines_unique_sentinel_through_unique_finish_v1",
            "transcript_extraction_exit_code": 0,
            "transcript_extraction_failure": None,
            "transcript_extraction_line_range": recovery_record[
                "transcript_line_range_1based_inclusive"],
            "sentinel_count": 1,
            "pass_line_count": 1,
            "progress_checkpoint_count": 256,
            "finish_time_ns": transcript_facts["finish_time_ns"],
            "xsim_exit_code_captured": False,
        }
        _write_json_replace(STAGE_STATUS, recovered_stage)
        stage_sha256 = _sha_file(STAGE_STATUS)

        recovered_process = json.loads(json.dumps(original_process, ensure_ascii=False))
        previous_process_failure = recovered_process.get("failure")
        recovered_process.update({
            "mode": "recover",
            "failure": None,
            "data_verification_status": "DATA_VERIFICATION_PENDING",
            "stage_status_sha256": stage_sha256,
            "stage_status_terminal_status": "SIMULATION_FLOW_PASS",
            "stage_status_finalized": True,
            "recovery_previous_failure": previous_process_failure,
            "recovery_provenance": {
                "record_path": str(RECOVERY_RECORD.resolve()),
                "original_status": "SIMULATION_FLOW_FAIL",
                "terminal_status": "SIMULATION_FLOW_PASS",
                "vivado_batch_reused": True,
                "vivado_or_xsim_started_by_recovery": False,
            },
        })
        _write_json_replace(PROCESS_STATUS, recovered_process)
        recovery_record["runtime_process_snapshots"]["after"] = \
            _windows_vivado_process_snapshot()
        _require(recovery_record["runtime_process_snapshots"]["after"] == [],
                 "恢复写入后发现 Vivado/XSim 进程")
        recovery_record["process_status_after_stage_update"] = _artifact(PROCESS_STATUS)
        _write_json_replace(RECOVERY_RECORD, recovery_record)

        with VERIFY_ONLY_LOG.open("xb") as verify_stream:
            verify_result = subprocess.run(
                [sys.executable, "-X", "utf8", "-B", str(Path(__file__).resolve()),
                 "--verify-only"],
                cwd=ROOT, stdout=verify_stream, stderr=subprocess.STDOUT,
                check=False,
            )
            verify_stream.flush()
            os.fsync(verify_stream.fileno())
        recovery_record["verify_only"]["exit_code"] = int(verify_result.returncode)
        recovery_record["verify_only"]["log"] = _artifact(VERIFY_ONLY_LOG)
        _require(verify_result.returncode == 0,
                 f"标准 --verify-only 返回 {verify_result.returncode}；详见 verify_only.log")
        report, report_sha256 = _read_json(FINAL_REPORT)
        _require(report.get("status") == "PASS_SIMULATION_DATA_ONLY" and
                 report.get("acceptance_status") == "NOT_REVIEWED" and
                 report.get("simulation", {}).get("raw_int32_compares") == RAW_COUNT and
                 report.get("simulation", {}).get("int8_compares") == INT8_COUNT and
                 report.get("simulation", {}).get("raw_mismatch_bytes") == 0 and
                 report.get("simulation", {}).get("int8_mismatch_bytes") == 0 and
                 report.get("simulation", {}).get("raw_byte_identical_to_independent_golden") is True and
                 report.get("simulation", {}).get("int8_byte_identical_to_independent_golden") is True,
                 "标准 verify-only 报告未证明 raw/INT8 golden byte compare 全等")
        recovery_record["verify_only"]["report"] = {
            "path": str(FINAL_REPORT.resolve()),
            "bytes": FINAL_REPORT.stat().st_size,
            "sha256": report_sha256,
            "raw_int32_compares": RAW_COUNT,
            "int8_compares": INT8_COUNT,
            "raw_mismatch_bytes": 0,
            "int8_mismatch_bytes": 0,
        }

        run_summary = json.loads(json.dumps(original_run_summary, ensure_ascii=False))
        run_summary.update({
            "mode": "recover",
            "overall_status": "PASS",
            "simulation_flow_status": "SIMULATION_FLOW_PASS",
            "data_verification_status": "PASS",
            "verify_only": {
                "command": recovery_record["verify_only"]["command"],
                "runner_sha256": current_hashes[T57_RUNNER_RELATIVE],
                "exit_code": 0,
                "log": _artifact(VERIFY_ONLY_LOG),
                "report": recovery_record["verify_only"]["report"],
                "failure": None,
            },
            "stage_status": {
                "path": str(STAGE_STATUS.resolve()),
                "sha256": _sha_file(STAGE_STATUS),
                "terminal_status": "SIMULATION_FLOW_PASS",
            },
            "process_status": {
                "path": str(PROCESS_STATUS.resolve()),
                "sha256": _sha_file(PROCESS_STATUS),
            },
            "failure": None,
            "recovery_record": {
                "path": str(RECOVERY_RECORD.resolve()),
                "provenance": "RECOVERED_FROM_EXISTING_ATTEMPT09_CONSOLE",
            },
        })
        _write_json_replace(RUN_SUMMARY, run_summary)
        recovery_record["status"] = "RECOVERY_PASS"
        recovery_record["run_summary_after_recovery"] = _artifact(RUN_SUMMARY)
        recovery_record["finished_head"] = _current_head()
        _write_json_replace(RECOVERY_RECORD, recovery_record)
        print(json.dumps({"result": "RECOVERY_PASS",
                          "attempt_root": str(RUN_ROOT.resolve()),
                          "recovery_record": _artifact(RECOVERY_RECORD),
                          "final_report": _artifact(FINAL_REPORT),
                          "run_summary": _artifact(RUN_SUMMARY),
                          "raw_int32_compares": RAW_COUNT,
                          "int8_compares": INT8_COUNT,
                          "raw_mismatch_bytes": 0,
                          "int8_mismatch_bytes": 0,
                          "simulate_step_tcl_code": None,
                          "xsim_exit_code": None,
                          "xsim_exit_code_captured": False},
                         ensure_ascii=False, indent=2), flush=True)
        return recovery_record
    except Exception as exc:
        failure_text = f"{type(exc).__name__}: {exc}"
        if not FINAL_REPORT.exists():
            _write_bytes_replace(STAGE_STATUS,
                                 base64.b64decode(original_snapshots[
                                     "stage_status.json"]["base64"], validate=True))
            _write_bytes_replace(PROCESS_STATUS,
                                 base64.b64decode(original_snapshots[
                                     "process_status.json"]["base64"], validate=True))
        recovery_record["status"] = "RECOVERY_NON_ACCEPTANCE"
        recovery_record["failure"] = failure_text
        recovery_record["failed_head"] = _current_head()
        if VERIFY_ONLY_LOG.exists():
            recovery_record["verify_only"]["log"] = _artifact(VERIFY_ONLY_LOG)
        _write_json_replace(RECOVERY_RECORD, recovery_record)
        raise


def _verify_simulation() -> dict[str, Any]:
    _require(PREPARE_REPORT.is_file(), "缺少 T57 prepare_summary.json")
    preparation, prepare_summary_sha256 = _read_json(PREPARE_REPORT)
    recovery_record: dict[str, Any] | None = None
    if RECOVERY_RECORD.exists():
        _require(RECOVERY_RECORD.is_file() and not RECOVERY_RECORD.is_symlink(),
                 "attempt09 recovery record 不是普通文件")
        recovery_record, _ = _read_json(RECOVERY_RECORD)
    _require(preparation.get("schema") == "GestureForge-S2A-T57-preparation-summary-v3" and
             preparation.get("status") == "PREPARED_NOT_SIMULATED" and
             preparation.get("baseline_head") == BASE_HEAD and
             _head_is_ancestor(BASE_HEAD, str(preparation.get("current_head", ""))) and
             _head_is_ancestor(BASE_HEAD, _current_head()),
             "T57 preparation schema 或基线不匹配")
    fixture_manifest, fixture_manifest_sha256, golden = _verify_prepared_fixture(
        preparation, recovery_record=recovery_record)
    prepared_project = preparation.get("project_preflight", {})
    _require(prepared_project.get("path") == str(XPR_PREFLIGHT.resolve()) and
             XPR_PATH.is_file(),
             "T57 prepare_summary 的源工程预检路径不匹配")
    xpr_binding, xpr_binding_sha256 = _read_json(XPR_PREFLIGHT)
    expected_source_xpr_sha256 = str(prepared_project.get("target_xpr_sha256", "")).lower()
    current_source_xpr_sha256 = _sha_file(XPR_PATH)
    _require(xpr_binding.get("project_name") == "AX7Z020_Gesture" and
             xpr_binding.get("project_path") == str(XPR_PATH.resolve()) and
             xpr_binding.get("xpr_sha256_before_run") == expected_source_xpr_sha256 and
             current_source_xpr_sha256 == expected_source_xpr_sha256 and
             xpr_binding.get("preflight_exit_code") == 0,
             "只读源工程预检、prepare_summary 与当前 XPR 哈希绑定不一致")
    preflight_log_record = xpr_binding.get("preflight_log")
    _require(isinstance(preflight_log_record, dict),
             "当前工程预检绑定缺少日志记录")
    project_preflight_log_path = _verify_file_record(preflight_log_record,
                                                     "目标工程只读预检日志")
    stage_path = RUN_ROOT / "stage_status.json"
    process_path = RUN_ROOT / "process_status.json"
    stage, _ = _read_json(stage_path)
    process, _ = _read_json(process_path)
    if recovery_record is not None:
        recovery_record = _validate_recovery_record(
            recovery_record, preparation, stage, process)
    expected_scratch_xpr = SCRATCH_PROJECT_DIRECTORY / f"{SCRATCH_PROJECT_NAME}.xpr"
    _require(stage.get("schema") == "GestureForge-S2A-T57-isolated-simulation-status-v5" and
             stage.get("status") == "SIMULATION_FLOW_PASS" and
             stage.get("data_verification_status") == "DATA_VERIFICATION_PENDING" and
             stage.get("data_verification_report") is None and
             stage.get("simulation_context") == "ISOLATED_SCRATCH_PROJECT" and
             stage.get("project_name") == SCRATCH_PROJECT_NAME and
             stage.get("project_directory") == str(SCRATCH_PROJECT_DIRECTORY.resolve()) and
             _same_absolute_windows_path(stage.get("project_xpr_path", ""),
                                         expected_scratch_xpr.resolve()) and
             stage.get("source_project_name") == "AX7Z020_Gesture" and
             stage.get("source_project_xpr_path") == str(XPR_PATH.resolve()) and
             stage.get("source_project_xpr_sha256") == expected_source_xpr_sha256 and
             stage.get("source_project_modified") is False and
             stage.get("simset") == SIMSET and stage.get("top") == TOP and
             stage.get("runtime_property_empty") is True and
             stage.get("runtime_control") == "CUSTOM_TCL_RUN_ALL" and
             stage.get("effective_debug_level") == "off" and
             stage.get("custom_tcl_path") == str(XSIM_CUSTOM_TCL.resolve()) and
             stage.get("custom_tcl_executed") is True and
             stage.get("simulate_log_complete") is True and
             stage.get("simulate_log_source") == XSIM_SIMULATE_TRANSCRIPT.name and
             stage.get("simulate_log_extraction_status") == "PASS" and
             stage.get("simulate_log_extraction_exit_code") == 0 and
             stage.get("xsim_exit_code_captured") is False and
             stage.get("xsim_exit_code") is None and
             stage.get("xsim_exit_code_source") is None and
             stage.get("simulate_step_tcl_code") in (None, 0) and
             stage.get("vivado_process_exit_code") == 0 and
             stage.get("wrapper_finalization", {}).get("source") == "PowerShell wrapper" and
             stage.get("wrapper_finalization", {}).get("terminal_status") == "SIMULATION_FLOW_PASS" and
             stage.get("log_all_signals") == 0,
             "Vivado 隔离工程仿真状态或源工程绑定不匹配")
    _require(stage.get("compile_exit_code") == 0 and
             stage.get("elaboration_exit_code") == 0,
             "Vivado compile/elaboration 阶段未全部返回 0")
    _require(process.get("vivado_process_exit_code") == 0,
             "Vivado batch 主进程未返回 0")
    _require(process.get("schema") == "GestureForge-S2A-T57-isolated-process-status-v1",
             "T57 PowerShell process status schema 不匹配")
    _require(process.get("xpr_sha256_before") == process.get("xpr_sha256_after") and
             process.get("xpr_unchanged") is True and
             process.get("xpr_sha256_after") == expected_source_xpr_sha256 and
             current_source_xpr_sha256 == process.get("xpr_sha256_after"),
             "Vivado batch 运行期间源 XPR SHA-256 发生变化")
    _require(process.get("unrelated_processes_before") == [] and
             process.get("unrelated_processes_after") == [],
             "Vivado/XSim 进程快照中发现未绑定的进程")
    _require(process.get("failure") is None and
             process.get("cleanup_failure") is None and
             process.get("stage_status_finalized") is True and
             process.get("stage_status_terminal_status") == "SIMULATION_FLOW_PASS" and
             process.get("data_verification_status") == "DATA_VERIFICATION_PENDING" and
             process.get("stage_status_path") == str(stage_path.resolve()) and
             process.get("stage_status_sha256") == _sha_file(stage_path),
             "PowerShell wrapper 未绑定通过态 stage_status 或存在运行/清理失败")
    _require(process.get("source_project_name") == "AX7Z020_Gesture" and
             process.get("source_project_xpr_path") == str(XPR_PATH.resolve()) and
             process.get("scratch_project_name") == SCRATCH_PROJECT_NAME and
             process.get("scratch_project_path") == str(SCRATCH_PROJECT_DIRECTORY.resolve()) and
             process.get("scratch_project_xpr_path") == str(expected_scratch_xpr.resolve()) and
             process.get("scratch_project_created") is True and
             process.get("scratch_project_removed") is True and
             process.get("owner_marker_removed") is True and
             process.get("cleanup_verified") is True and
             not SCRATCH_PROJECT_DIRECTORY.exists(),
             "隔离工程路径、所有权清理或运行结束状态不匹配")
    expected_mode = "recover" if recovery_record is not None else "run"
    expected_launcher_sha = (T57_PREPARED_WRAPPER_SHA256
                            if recovery_record is not None else
                            _sha_file(PROJECT_SIM_WRAPPER))
    _require(process.get("mode") == expected_mode and
             process.get("simulation_tcl_sha256") == _sha_file(PROJECT_SIM_TCL) and
             process.get("launcher_script_sha256") == expected_launcher_sha and
             process.get("xsim_tcl_sha256") == _sha_file(XSIM_CUSTOM_TCL),
             "T57 隔离仿真脚本、PowerShell launcher 或 XSim Tcl SHA-256 不匹配")
    batch_script_snapshots = _verify_batch_script_snapshots(stage)
    elaborate_batch_path = RUN_ROOT / "elaborate.after_elaborate.bat"
    simulate_batch_path = RUN_ROOT / "simulate.after_elaborate.bat"

    compile_log_path = RUN_ROOT / "compile.log"
    elaborate_log_path = RUN_ROOT / "elaborate.log"
    console_log_path = RUN_ROOT / "vivado_batch_console.log"
    transcript_source = str(stage.get("simulate_log_source", ""))
    _require(transcript_source == XSIM_SIMULATE_TRANSCRIPT.name,
             "stage_status 必须绑定独立的 XSim simulate transcript")
    simulate_log_path = XSIM_SIMULATE_TRANSCRIPT
    recorded_transcript = Path(str(stage.get("simulate_log_path", ""))).resolve()
    _require(recorded_transcript == simulate_log_path.resolve() and
             stage.get("simulate_log_sha256") == _sha_file(simulate_log_path),
             "stage_status 的仿真 transcript 路径或 SHA-256 不匹配")
    _require(Path(str(stage.get("simulate_log_origin_path", ""))).resolve() ==
             console_log_path.resolve() and
             stage.get("simulate_log_origin_sha256") == _sha_file(console_log_path) and
             stage.get("simulate_log_origin_bytes") == console_log_path.stat().st_size and
             stage.get("simulate_log_bytes") == simulate_log_path.stat().st_size and
             stage.get("simulate_log_extraction_algorithm") ==
             "byte_lines_unique_sentinel_through_unique_finish_v1",
             "stage_status 未绑定原始 console 与 byte-slice 提取算法")
    console_bytes = console_log_path.read_bytes()
    expected_transcript_bytes, extraction_facts = _extract_xsim_transcript(console_bytes)
    transcript_bytes = simulate_log_path.read_bytes()
    _require(transcript_bytes == expected_transcript_bytes and
             stage.get("simulate_log_extraction_line_range") ==
             [extraction_facts["start_line"], extraction_facts["end_line"]],
             "持久化 transcript 不是 console 中 sentinel 至唯一 $finish 的原始字节片段")
    for path in (compile_log_path, elaborate_log_path, simulate_log_path):
        _require(path.is_file(), f"缺少 Vivado/XSim 阶段日志：{path}")
    compile_log = compile_log_path.read_text(encoding="utf-8", errors="replace")
    elaborate_log = elaborate_log_path.read_text(encoding="utf-8", errors="replace")
    with simulate_log_path.open("r", encoding="utf-8", errors="replace", newline="") as stream:
        simulate_log = stream.read()
    for relative in (*RTL_PATHS, "sim/tb_s2a_conv_layer35_row21_all_channels.sv"):
        _require(Path(relative).name in compile_log,
                 f"compile.log 未包含 T57 预期源码：{relative}")
    _require(f"Built simulation snapshot {TOP}_behav" in elaborate_log,
             "elaborate.log 未构建 T57 snapshot")
    pass_line, pass_values, progress, finish_time_ns = _verify_xsim_transcript_text(simulate_log)
    _require(stage.get("finish_time_ns") == finish_time_ns,
             "stage_status 的完成时间与完整 XSim transcript 不一致")

    fixture_manifest_path = FIXTURE_ROOT / "fixture_manifest.json"
    raw_golden = golden[:RAW_BYTES]
    int8_golden = golden[RAW_BYTES:]
    raw_observed_path = RUN_ROOT / "observed_raw.bin"
    int8_observed_path = RUN_ROOT / "observed_output.bin"
    raw_observed = raw_observed_path.read_bytes()
    int8_observed = int8_observed_path.read_bytes()
    _require(len(raw_observed) == RAW_BYTES and len(int8_observed) == INT8_BYTES,
             "observed 二进制长度不匹配")
    raw_mismatches = sum(a != b for a, b in zip(raw_observed, raw_golden))
    int8_mismatches = sum(a != b for a, b in zip(int8_observed, int8_golden))
    _require(raw_mismatches == 0 and int8_mismatches == 0,
             f"逐字节比较失败：raw={raw_mismatches} INT8={int8_mismatches}")
    wdb_paths = list(RUN_ROOT.rglob("*.wdb"))
    _require(not wdb_paths and stage.get("wdb_generated") is False,
             f"run09 no-wave 证据发现 WDB：{wdb_paths}")

    expected_counts = preparation["expected_counts"]
    expected_values = {
        "outputs": RAW_COUNT, "raw": RAW_COUNT,
        "feature_reads": expected_counts["feature_reads"],
        "weight_reads": expected_counts["weight_reads"],
        "output_writes": expected_counts["output_writes"],
        "padding": expected_counts["padding_taps"],
        "taps": expected_counts["all_kernel_taps"],
        "feature_lanes": 15, "weight_lanes": 15, "output_lanes": 15,
        "error_mask": 70, "fault_responses": 3, "abort_cancel": 2,
        "reset_cancel": 1, "recovery": 1,
        "request_stalls": expected_counts["total_request_stall_cycles"],
        "feature_transfers": expected_counts["feature_transfers"],
        "feature_stall_cycles": expected_counts["feature_stall_cycles"],
        "weight_transfers": expected_counts["weight_transfers"],
        "weight_stall_cycles": expected_counts["weight_stall_cycles"],
        "output_transfers": expected_counts["output_transfers"],
        "output_stall_cycles": expected_counts["output_stall_cycles"],
    }
    for key, expected in expected_values.items():
        _require(pass_values.get(key) == expected,
                 f"PASS T57 事务统计 {key}={pass_values.get(key)}，expected={expected}")
    for class_name in ("feature", "weight", "output"):
        expected_slots = expected_counts[f"{class_name}_slot_counts"]
        for index, expected in enumerate(expected_slots):
            key = f"{class_name}_slot{index}"
            _require(pass_values.get(key) == expected,
                     f"PASS T57 停顿槽统计 {key}={pass_values.get(key)}，expected={expected}")

    source_hashes = _source_hashes()
    prepared_source_hashes = preparation["bindings"]["T57_source_hashes"]
    for relative, expected in prepared_source_hashes.items():
        if recovery_record is not None and relative in (
                *T57_RECOVERY_DELTA_PATHS, T57_RECOVERY_CONTROLLER_RELATIVE):
            continue
        if relative == T57_RUNNER_RELATIVE:
            continue
        _require(source_hashes.get(relative) == expected,
                 f"T57 待审源码在仿真后发生变化：{relative}")
    current_runner_sha256 = source_hashes[T57_RUNNER_RELATIVE]
    prepared_runner_sha256 = prepared_source_hashes[T57_RUNNER_RELATIVE]
    if recovery_record is None:
        _require(current_runner_sha256 == prepared_runner_sha256,
                 "verify-only runner 与 prepare_summary 固定 runner 版本不一致")
    else:
        _require(current_runner_sha256 ==
                 recovery_record["source_bindings"]["current_sha256"][T57_RUNNER_RELATIVE],
                 "恢复期间 verify-only runner SHA 与 recovery record 不一致")
    _require(fixture_manifest.get("runner_source_sha256") == prepared_runner_sha256,
             "fixture manifest 未绑定 prepare_summary 中的 runner 版本")
    parent, parent_bindings, _ = _verify_parent()
    environment, _ = _read_json(ENV_PREFLIGHT)
    raw_record = _artifact(raw_observed_path)
    int8_record = _artifact(int8_observed_path)
    log_records = {name: _artifact(path) for name, path in
                   (("compile.log", compile_log_path),
                    ("elaborate.log", elaborate_log_path),
                    ("vivado_batch_console.log", console_log_path),
                    (transcript_source, simulate_log_path),
                    ("elaborate.after_elaborate.bat", elaborate_batch_path),
                    ("simulate.after_elaborate.bat", simulate_batch_path))}
    for snapshot_name, snapshot_path in batch_script_snapshots.items():
        log_records[snapshot_name] = _artifact(snapshot_path)
    log_records["xsim_run.tcl"] = _artifact(XSIM_CUSTOM_TCL)
    all_records = {name: _artifact(FIXTURE_ROOT / name)
                   for name in ("feature_input.bin", "layer35_weights.bin", "golden.bin", "vectors.txt")}
    run_files = {**all_records, "observed_raw.bin": raw_record,
                 "observed_output.bin": int8_record, **log_records,
                 "stage_status.json": _artifact(stage_path),
                 "process_status.json": _artifact(process_path)}
    report = {
        "schema": "GestureForge-S2A-T57-layer35-row21-simulation-data-v2",
        "task_id": "S2A-T57",
        "status": "PASS_SIMULATION_DATA_ONLY",
        "acceptance_status": "NOT_REVIEWED",
         "baseline_head": BASE_HEAD,
        "current_head_at_prepare": preparation["current_head"],
         "current_head_at_verify": _current_head(),
        "scope": "tiny416 cfg section36 layer35; all 256 output channels at y=21, x=0..25; not full layer or network",
        "recovery_provenance": _recovery_report_details(recovery_record)
        if recovery_record is not None else None,
        "bindings": {
            "T56_parent_report": {"path": str(T56_REPORT.resolve()),
                                  "sha256": T56_REPORT_SHA256,
                                  "acceptance_status": parent["acceptance_status"],
                                  "fixed_points_yx": parent_bindings["fixed_points_yx"]},
            "T56_summary": {"path": str(T56_SUMMARY.resolve()),
                            "sha256": T56_SUMMARY_SHA256},
            "T57_prepare_summary": {
                "path": str(PREPARE_REPORT.resolve()),
                "sha256": prepare_summary_sha256,
            },
            "T56_source_hashes": parent_bindings["T56_source_hashes"],
            "T57_source_hashes": source_hashes,
            "G0_specification": {"path": str(G0_PATH.resolve()), "sha256": G0_SHA256},
            "T01_manifest": preparation["bindings"]["T01_manifest"],
            "T23_parameter_table": preparation["bindings"]["T23_parameter_table"],
            "GF8_package": preparation["bindings"]["GF8_package"],
            "weight_layer35": preparation["bindings"]["weight_layer35"],
            "model": preparation["bindings"]["model"],
            "source_project_preflight": {
                "path": str(XPR_PREFLIGHT.resolve()),
                "sha256": xpr_binding_sha256,
                "log_path": str(project_preflight_log_path.resolve()),
                "log_sha256": preflight_log_record["sha256"],
                "target_xpr_path": str(XPR_PATH.resolve()),
                "target_xpr_sha256": expected_source_xpr_sha256,
            },
            "fixture_manifest": {
                "path": str((FIXTURE_ROOT / "fixture_manifest.json").resolve()),
                "sha256": fixture_manifest_sha256,
                "prepare_runner_sha256": prepared_runner_sha256,
            },
            "verification_runner": {
                "path": str((ROOT / T57_RUNNER_RELATIVE).resolve()),
                "prepare_runner_sha256": prepared_runner_sha256,
                "verify_runner_sha256": current_runner_sha256,
            },
            "project_simulation_scripts": {
                "tcl_sha256": process["simulation_tcl_sha256"],
                "launcher_sha256": process["launcher_script_sha256"],
                "xsim_custom_tcl_sha256": process["xsim_tcl_sha256"],
                "elaborate_command_signature": stage["elaborate_command_signature"],
                "simulate_command_signature": stage["simulate_command_signature"],
                "batch_script_snapshots": {name: _artifact(path)
                                            for name, path in batch_script_snapshots.items()},
            },
            "fixed_points_yx": [list(point) for point in POINTS],
            "oracle_source": preparation["oracle_source"],
        },
        "fixture": {"generator": preparation["feature_fixture"],
                    "root": str(FIXTURE_ROOT.resolve()),
                    "files": all_records,
                    "manifest": _artifact(fixture_manifest_path),
                    "golden_layout": {"raw_int32_le_bytes": RAW_BYTES,
                                      "int8_bytes": INT8_BYTES,
                                      "total_bytes": GOLDEN_BYTES,
                                      "order": "全部 raw INT32 little-endian，随后全部 INT8"}},
        "oracle": preparation["oracle"],
        "expected_counts": expected_counts,
        "simulation": {
            "status": "PASS_SIMULATION_DATA_ONLY",
            "evidence_role": "SIMULATION_DATA_ONLY",
            "source_project": {"name": stage["source_project_name"],
                               "xpr_path": stage["source_project_xpr_path"],
                               "xpr_sha256_before": process["xpr_sha256_before"],
                               "xpr_sha256_after": process["xpr_sha256_after"],
                               "unchanged": True,
                               "modified": False},
            "simulation_project": {
                "context": "ISOLATED_SCRATCH_PROJECT_CREATED_FROM_BOUND_SOURCE_FILES",
                "name": stage["project_name"],
                "directory": stage["project_directory"],
                "xpr_path": stage["project_xpr_path"],
                "created_by_t57": True,
                "removed_after_run": process["scratch_project_removed"],
            },
            "simset": SIMSET, "top": TOP,
            "runtime_control": "CUSTOM_TCL_RUN_ALL",
            "runtime_property_empty": True,
            "effective_debug_level": "off", "log_all_signals": 0,
            "custom_tcl_executed": True,
            "finish_time_ns": finish_time_ns,
            "compile_exit_code": stage["compile_exit_code"],
            "elaboration_exit_code": stage["elaboration_exit_code"],
            "xsim_exit_code": stage["xsim_exit_code"],
            "xsim_exit_code_captured": stage["xsim_exit_code_captured"],
            "xsim_completion_evidence_source": transcript_source,
            "xsim_completion_evidence_sha256": stage["simulate_log_sha256"],
            "xsim_completion_evidence_origin": {
                "path": stage["simulate_log_origin_path"],
                "sha256": stage["simulate_log_origin_sha256"],
                "line_range_1based_inclusive": stage.get("simulate_log_extraction_line_range"),
                "algorithm": stage["simulate_log_extraction_algorithm"],
            },
            "vivado_process_exit_code": process["vivado_process_exit_code"],
            "raw_int32_compares": RAW_COUNT, "int8_compares": INT8_COUNT,
            "raw_bytes": RAW_BYTES, "int8_bytes": INT8_BYTES,
            "progress_checkpoint_count": len(progress),
            "progress_first_output_count": progress[0],
            "progress_last_output_count": progress[-1],
            "progress_step": 26,
            "raw_int32_sha256": raw_record["sha256"],
            "int8_sha256": int8_record["sha256"],
            "golden_combined_sha256": preparation["oracle"]["combined_golden_sha256"],
            "raw_byte_identical_to_independent_golden": True,
            "int8_byte_identical_to_independent_golden": True,
            "raw_mismatch_bytes": raw_mismatches,
            "int8_mismatch_bytes": int8_mismatches,
            "pass_line": pass_line,
            "wdb_generated": stage.get("wdb_generated"),
            "finish_observed": True,
            "artifacts": run_files,
        },
        "operations": {
            "vivado_mcp": {"status": environment["vivado_mcp"]["status"],
                            "error": environment["vivado_mcp"].get("error"),
                            "check_connection_called": True},
            "vivado_cli": {"path": environment["vivado_cli"],
                           "mode": "batch",
                           "project_file": stage["project_xpr_path"],
                           "source_project_file": str(XPR_PATH.resolve()),
                           "source_project_sha256": expected_source_xpr_sha256,
                           "command": process["command"],
                           "project_preflight_log": str(project_preflight_log_path.resolve()),
                           "project_preflight_exit_code": 0},
            "vivado_xsim_processes_before": environment["vivado_processes_before_run"],
            "vivado_xsim_processes_after": process["unrelated_processes_after"],
        },
        "review": {"G2": "NOT_REVIEWED", "G3": "NOT_CLAIMED",
                    "G4": "NOT_CLAIMED", "G5": "NOT_CLAIMED"},
        "limitations": ["仅为 tiny416 cfg section36 layer35 的 y=21、x=0..25、256 通道数据。",
                        "不代表 layer35 全层、整网推理或阶段整体 G2/G3/G4/G5 通过。",
                        "需要独立 reviewer 审查本报告与 T57 绑定源码；未执行板上验证。"],
    }
    _require(report["simulation"]["wdb_generated"] is False,
             "T57 no-wave 仿真仍生成了 WDB")
    _write_json_exclusive(FINAL_REPORT, report)
    written, report_sha = _read_json(FINAL_REPORT)
    _require(written.get("schema") == report["schema"] and
             written.get("status") == "PASS_SIMULATION_DATA_ONLY" and
             written.get("acceptance_status") == "NOT_REVIEWED" and
             written["simulation"]["raw_mismatch_bytes"] == 0 and
             written["simulation"]["int8_mismatch_bytes"] == 0,
             "T57 最终证据 JSON schema 自检失败")
    print(json.dumps({"result": written["status"],
                      "acceptance_status": written["acceptance_status"],
                      "report": str(FINAL_REPORT.resolve()),
                      "report_sha256": report_sha,
                      "raw_int32_compares": RAW_COUNT,
                      "int8_compares": INT8_COUNT,
                      "raw_mismatch_bytes": raw_mismatches,
                      "int8_mismatch_bytes": int8_mismatches,
                      "progress_checkpoints": len(progress),
                      "xpr_unchanged": True,
                      "artifacts": run_files}, ensure_ascii=False, indent=2),
          flush=True)
    return report


def _main() -> int:
    parser = argparse.ArgumentParser(description="T57 layer35 row21 oracle and Vivado evidence verifier")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare-only", action="store_true", help="准备独立 Python oracle 与 XSim fixture")
    group.add_argument("--verify-only", action="store_true", help="比较 XSim 输出并生成最终证据 JSON")
    group.add_argument("--extract-console-transcript", action="store_true",
                       help="从本轮 Vivado console 中独占保存 custom Tcl 到 $finish 的字节片段")
    group.add_argument("--recover-attempt09", action="store_true",
                       help="仅从保存的 attempt09 console 与输出恢复验证证据，不启动 Vivado/XSim")
    args = parser.parse_args()
    try:
        if args.prepare_only:
            _prepare()
        elif args.verify_only:
            _verify_simulation()
        elif args.extract_console_transcript:
            _extract_xsim_transcript_file()
        else:
            _recover_attempt09()
        return 0
    except Exception as exc:
        print(f"FAIL T57 {type(exc).__name__}: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(_main())
