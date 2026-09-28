#!/usr/bin/env python3
"""为 S2A-T60 准备并独立核验 layer35 y=24 行证据，不启动 Vivado 或 XSim。"""

from __future__ import annotations

import argparse
import ast
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE_HEAD = "7b8bad78a456310d2ca797a02e3a5a7f873f9c18"
TASK_ID = "S2A-T60"
ROW_Y = 24
OUTPUT_SIZE = 26
INPUT_CHANNELS = 384
OUTPUT_CHANNELS = 256
OUTPUT_PIXELS = OUTPUT_SIZE * OUTPUT_SIZE
KERNEL_AREA = 9
REDUCTION = INPUT_CHANNELS * KERNEL_AREA
INPUT_BYTES = INPUT_CHANNELS * OUTPUT_PIXELS
OUTPUT_BYTES = OUTPUT_CHANNELS * OUTPUT_PIXELS
RAW_COUNT = OUTPUT_CHANNELS * OUTPUT_SIZE
INT8_COUNT = RAW_COUNT
RAW_BYTES = RAW_COUNT * 4
INT8_BYTES = INT8_COUNT
GOLDEN_BYTES = RAW_BYTES + INT8_BYTES
WEIGHT_OFFSET = 5_010_412
WEIGHT_BYTES = OUTPUT_CHANNELS * REDUCTION
SEED = 20260922
STALL_SEQUENCE = (0, 1, 2, 7, 3)
POINTS = tuple((ROW_Y, x) for x in range(OUTPUT_SIZE))

T54_REPORT = ROOT / "report/evidence/S2A-T54/layer35_row18_all_channels.json"
T54_REPORT_SHA256 = "089c0aa4b0b163d49c38602e44c61c0e606b8efc7ecbc546c1cfc8385f327f7a"
T54_RUNNER = ROOT / "verification/test_s2a_conv_layer35_row18_all_channels_rtl.py"
T54_RUNNER_SHA256 = "4ec6a743d6a80c380505be2a8601879c311a7f42e07323027098c07a8dadd4f3"
T54_TESTBENCH = ROOT / "sim/tb_s2a_conv_layer35_row18_all_channels.sv"
T54_TESTBENCH_SHA256 = "e7e4490128dcde59071daefe81e6b0754b50b4e0dae3858fa3d4c428f71951e8"
G0_PATH = ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
T01_PATH = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
T16_PATH = ROOT / "report/evidence/S2A-T16/conv_requant_proof.json"
T17_PATH = ROOT / "report/evidence/S2A-T17/conv_engine_simulation.json"
T20_PATH = ROOT / "report/evidence/S2A-T20/conv_layer_scheduler_simulation.json"
T23_PATH = ROOT / "report/evidence/S2A-T23/conv_requant_parameter_table.json"
T16_SCRIPT = ROOT / "verification/s2a_conv_requant_proof.py"
D2_REFERENCE = ROOT / "verification/s1_t02_d2_int8_forward.py"
WEIGHT_REPORT = ROOT / "report/evidence/S1-T02/20260922_s1_t02_d2_tiny416_int8_weight_r2.json"
GF8_SHA256 = "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39"
GF8_BYTES = 5_903_100
G0_SHA256 = "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"
T01_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
T16_SHA256 = "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24"
T17_SHA256 = "4cd1d0f0e5edf7b34907179dea47a9a9c0994eb1d8bd89adfa341067cac17ab2"
T20_SHA256 = "d6bc16966a2d3c7707d98aafa6b435ae158cd28faa53baa8f795e13e86a17887"
T23_SHA256 = "396dc66aa3ccc41050cc8183bff16b86143a6f5553cf38fed16b0ba8b4eb4ae1"
T16_SCRIPT_SHA256 = "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9"
D2_REFERENCE_SHA256 = "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393"
WEIGHT_REPORT_SHA256 = "d867cd5dc7497f0de9db5c4e0643afd2e52d4c1e77632852487e8afceaa0dd80"

RTL_PATHS = (
    "src/int8_conv_tap_geometry.sv",
    "src/int8_conv_weight_address.sv",
    "src/int8_mac_accumulator.sv",
    "src/s2a_conv_engine.sv",
    "src/s2a_conv_layer35_channel_probe.sv",
)
T54_SOURCE_PATHS = (*RTL_PATHS, T54_TESTBENCH.relative_to(ROOT).as_posix(),
                    T54_RUNNER.relative_to(ROOT).as_posix())
T60_RUNNER_RELATIVE = Path(__file__).resolve().relative_to(ROOT).as_posix()
T60_TESTBENCH_RELATIVE = "sim/tb_s2a_conv_layer35_row24_all_channels.sv"
T60_SOURCE_PATHS = (*RTL_PATHS, T60_TESTBENCH_RELATIVE, T60_RUNNER_RELATIVE)

XPR_PATH = ROOT / "vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr"
EVIDENCE_ROOT = ROOT / "report/evidence/S2A-T60"
RUN_ROOT = EVIDENCE_ROOT / "run02"
FIXTURE_ROOT = RUN_ROOT / "fixture"
PROJECT_PREFLIGHT = RUN_ROOT / "project_preflight_binding.json"
PREPARE_REPORT = RUN_ROOT / "prepare_summary.json"
FIXTURE_MANIFEST = FIXTURE_ROOT / "fixture_manifest.json"
FIXTURE_NAMES = (
    "feature_input.bin",
    "layer35_weights.bin",
    "golden.bin",
    "vectors.txt",
    "fixture_manifest.json",
)
PROCESS_NAMES = (
    "vivado.exe",
    "vivado_lab.exe",
    "xsct.exe",
    "xsim.exe",
    "xsimk.exe",
    "xelab.exe",
    "xvlog.exe",
    "xvhdl.exe",
)

POWERSHELL_PREFLIGHT = r"""
$ErrorActionPreference = 'Stop'
$mode = $env:S2A_T60_PREFLIGHT_MODE
if (@('prepare', 'verify') -notcontains $mode) {
    throw 'T60 PowerShell 预检模式无效'
}
$requiredDirectories = @(
    'D:\',
    'D:\FPGA_Competition',
    'D:\FPGA_Competition\report',
    'D:\FPGA_Competition\report\evidence',
    'D:\FPGA_Competition\vivado',
    'D:\FPGA_Competition\vivado\AX7Z020_Gesture'
)
foreach ($path in $requiredDirectories) {
    $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
    if (-not $item.PSIsContainer -or
        (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "路径链不是普通目录：$path"
    }
}
$xpr = 'D:\FPGA_Competition\vivado\AX7Z020_Gesture\AX7Z020_Gesture.xpr'
$xprItem = Get-Item -LiteralPath $xpr -Force -ErrorAction Stop
if ($xprItem.PSIsContainer -or $xprItem.Length -le 0 -or
    (($xprItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
    throw "目标 XPR 不是普通非空文件：$xpr"
}
$evidenceRoot = 'D:\FPGA_Competition\report\evidence\S2A-T60'
$legacyRunRoot = Join-Path $evidenceRoot 'run01'
$legacyFixtureRoot = Join-Path $legacyRunRoot 'fixture'
$legacyPreflight = Join-Path $evidenceRoot 'project_preflight_binding.json'
$runRoot = Join-Path $evidenceRoot 'run02'
$fixtureRoot = Join-Path $runRoot 'fixture'
$rootExists = Test-Path -LiteralPath $evidenceRoot
$legacyRunExists = Test-Path -LiteralPath $legacyRunRoot
$legacyFixtureExists = Test-Path -LiteralPath $legacyFixtureRoot
$legacyPreflightExists = Test-Path -LiteralPath $legacyPreflight
$runExists = Test-Path -LiteralPath $runRoot
if ($mode -eq 'prepare') {
    if (-not $rootExists -or -not $legacyRunExists -or
        -not $legacyFixtureExists -or -not $legacyPreflightExists -or $runExists) {
        throw 'T60 run02 prepare 目标/保留快照不满足隔离条件'
    }
    foreach ($path in @($evidenceRoot, $legacyRunRoot, $legacyFixtureRoot)) {
        $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if (-not $item.PSIsContainer -or
            (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "T60 保留快照目录不是普通目录：$path"
        }
    }
    $legacyItem = Get-Item -LiteralPath $legacyPreflight -Force -ErrorAction Stop
    if ($legacyItem.PSIsContainer -or $legacyItem.Length -le 0 -or
        (($legacyItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "T60 保留 project_preflight_binding 不是普通非空文件：$legacyPreflight"
    }
    $expectedRootEntries = @('project_preflight_binding.json', 'run01')
    $actualRootEntries = @(Get-ChildItem -LiteralPath $evidenceRoot -Force |
        ForEach-Object { $_.Name } | Sort-Object)
    if (($actualRootEntries -join '|') -ne ($expectedRootEntries -join '|')) {
        throw 'T60 证据根目录不是预期的 run01 保留快照'
    }
    $expectedLegacyRunEntries = @('fixture', 'prepare_summary.json')
    $actualLegacyRunEntries = @(Get-ChildItem -LiteralPath $legacyRunRoot -Force |
        ForEach-Object { $_.Name } | Sort-Object)
    if (($actualLegacyRunEntries -join '|') -ne ($expectedLegacyRunEntries -join '|')) {
        throw 'T60 run01 保留快照含非预期节点'
    }
    $expectedLegacyFixtureEntries = @(
        'feature_input.bin', 'fixture_manifest.json', 'golden.bin',
        'layer35_weights.bin', 'vectors.txt'
    )
    $actualLegacyFixtureEntries = @(Get-ChildItem -LiteralPath $legacyFixtureRoot -Force |
        ForEach-Object { $_.Name } | Sort-Object)
    if (($actualLegacyFixtureEntries -join '|') -ne ($expectedLegacyFixtureEntries -join '|')) {
        throw 'T60 run01 fixture 保留快照含非预期节点'
    }
}
else {
    if (-not $rootExists -or -not $legacyRunExists -or
        -not $legacyFixtureExists -or -not $legacyPreflightExists -or -not $runExists) {
        throw 'T60 verify-only 所需证据目录缺失'
    }
    foreach ($path in @($evidenceRoot, $legacyRunRoot, $legacyFixtureRoot,
                        $runRoot, $fixtureRoot)) {
        $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if (-not $item.PSIsContainer -or
            (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "T60 既有证据目录不是普通目录：$path"
        }
    }
    $legacyItem = Get-Item -LiteralPath $legacyPreflight -Force -ErrorAction Stop
    if ($legacyItem.PSIsContainer -or $legacyItem.Length -le 0 -or
        (($legacyItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "T60 run01 保留 binding 不是普通非空文件：$legacyPreflight"
    }
    $expectedRootEntries = @('project_preflight_binding.json', 'run01', 'run02')
    $actualRootEntries = @(Get-ChildItem -LiteralPath $evidenceRoot -Force |
        ForEach-Object { $_.Name } | Sort-Object)
    if (($actualRootEntries -join '|') -ne ($expectedRootEntries -join '|')) {
        throw 'T60 evidence 根目录含非预期节点'
    }
    $expectedRunEntries = @('fixture', 'prepare_summary.json', 'project_preflight_binding.json')
    $actualRunEntries = @(Get-ChildItem -LiteralPath $runRoot -Force |
        ForEach-Object { $_.Name } | Sort-Object)
    if (($actualRunEntries -join '|') -ne ($expectedRunEntries -join '|')) {
        throw 'T60 run02 目录含非预期节点'
    }
    $expectedFixtureEntries = @(
        'feature_input.bin', 'fixture_manifest.json', 'golden.bin',
        'layer35_weights.bin', 'vectors.txt'
    )
    $actualFixtureEntries = @(Get-ChildItem -LiteralPath $fixtureRoot -Force |
        ForEach-Object { $_.Name } | Sort-Object)
    if (($actualFixtureEntries -join '|') -ne ($expectedFixtureEntries -join '|')) {
        throw 'T60 fixture 目录含非预期节点'
    }
}
$names = @(
    'vivado.exe', 'vivado_lab.exe', 'xsct.exe', 'xsim.exe',
    'xsimk.exe', 'xelab.exe', 'xvlog.exe', 'xvhdl.exe'
)
$processes = @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop |
    Where-Object { $names -contains $_.Name.ToLowerInvariant() } |
    Sort-Object ProcessId |
    ForEach-Object {
        [ordered]@{
            name = $_.Name
            process_id = [int]$_.ProcessId
        }
    })
$result = [ordered]@{
    mode = $mode
    path_chain_valid = $true
    checked_directories = $requiredDirectories
    checked_xpr = $xpr
    target_absent = (-not $runExists)
    existing_run02 = $runExists
    process_names = $names
    processes = $processes
}
[Console]::Out.Write((ConvertTo-Json -InputObject $result -Depth 5 -Compress))
"""


class T60Error(RuntimeError):
    """表示 S2A-T60 冻结输入、工程绑定或准备证据核验失败。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T60Error(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _artifact(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "bytes": path.stat().st_size,
            "sha256": _sha_file(path)}


def _read_json(path: Path) -> tuple[dict[str, Any], str]:
    data = path.read_bytes()
    _require(not data.startswith(b"\xef\xbb\xbf"),
             f"JSON 不得带 UTF-8 BOM：{path}")
    value = json.loads(data.decode("utf-8"))
    _require(isinstance(value, dict), f"JSON 根节点不是对象：{path}")
    return value, _sha256(data)


def _write_bytes_exclusive(path: Path, data: bytes) -> None:
    with path.open("xb") as stream:
        stream.write(data)


def _write_json_exclusive(path: Path, value: dict[str, Any]) -> None:
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write_bytes_exclusive(path, payload)


def _current_head() -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False, timeout=15,
    )
    _require(result.returncode == 0, f"git rev-parse 失败：{result.stderr.strip()}")
    return result.stdout.strip().lower()


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative in T60_SOURCE_PATHS:
        path = ROOT / relative
        _require(path.is_file(), f"T60 源码缺失：{relative}")
        hashes[relative] = _sha_file(path)
    return hashes


def _source_configuration_check() -> dict[str, Any]:
    """以 Python AST 和文本规则确认本 runner 仅支持准备/核验。"""
    runner_path = Path(__file__).resolve()
    runner_bytes = runner_path.read_bytes()
    _require(not runner_bytes.startswith(b"\xef\xbb\xbf") and
             b"\r" not in runner_bytes and runner_bytes.endswith(b"\n"),
             "T60 runner 必须是 UTF-8 无 BOM、LF 且以换行结尾")
    runner_text = runner_bytes.decode("utf-8")
    tree = ast.parse(runner_text, filename=str(runner_path))
    tb_path = ROOT / T60_TESTBENCH_RELATIVE
    tb_bytes = tb_path.read_bytes()
    _require(not tb_bytes.startswith(b"\xef\xbb\xbf") and
             b"\r" not in tb_bytes and tb_bytes.endswith(b"\n"),
             "T60 testbench 必须是 UTF-8 无 BOM、LF 且以换行结尾")
    tb_text = tb_bytes.decode("utf-8")
    mode_options = sorted(
        node.args[0].value
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and
        isinstance(node.func, ast.Attribute) and
        node.func.attr == "add_argument" and node.args and
        isinstance(node.args[0], ast.Constant) and
        isinstance(node.args[0].value, str) and
        node.args[0].value.startswith("--")
    )
    _require(mode_options == ["--prepare-only", "--verify-only"],
             f"T60 CLI 选项超出准备态范围：{mode_options}")
    subprocess_commands = []
    forbidden_process_apis = {
        "Popen", "call", "check_call", "check_output", "system", "startfile",
    }
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Attribute) and function.attr in forbidden_process_apis:
            raise T60Error(f"T60 runner 含未经批准的进程启动 API：{function.attr}")
        if (isinstance(function, ast.Attribute) and
                isinstance(function.value, ast.Name) and
                function.value.id == "subprocess"):
            _require(function.attr == "run" and node.args and
                     isinstance(node.args[0], ast.List) and
                     node.args[0].elts and
                     isinstance(node.args[0].elts[0], ast.Constant),
                     "T60 runner subprocess 命令必须是静态字面量")
            subprocess_commands.append(node.args[0].elts[0].value)
    _require(sorted(subprocess_commands) == ["git", "powershell.exe"],
             f"T60 runner 外部命令超出 git/只读 PowerShell：{subprocess_commands}")
    forbidden_powershell = (
        "start-process", "invoke-expression", "start-job", "remove-item",
        "set-content", "new-item", "move-item", "stop-process",
    )
    powershell_lower = POWERSHELL_PREFLIGHT.lower()
    _require(not any(token in powershell_lower for token in forbidden_powershell) and
             ".tcl" not in powershell_lower,
             "T60 内嵌 PowerShell 存在进程启动、文件写入或 Tcl 操作")
    _require("subprocess.run(" in runner_text and
             "powershell.exe" in runner_text and
             "Get-CimInstance -ClassName Win32_Process" in POWERSHELL_PREFLIGHT and
             "Get-Item -LiteralPath" in POWERSHELL_PREFLIGHT and
             "Get-ChildItem -LiteralPath" in POWERSHELL_PREFLIGHT,
             "T60 内嵌 PowerShell 只读路径/进程检查不完整")
    for name in PROCESS_NAMES:
        _require(f"'{name}'" in POWERSHELL_PREFLIGHT,
                 f"T60 PowerShell 进程名单缺失：{name}")
    _require("module tb_s2a_conv_layer35_row24_all_channels;" in tb_text and
             "vector_y[initial_index] != 24" in tb_text and
             tb_text.count("output_y == 24") == 2 and
             "PASS T60 outputs=%0d raw=%0d" in tb_text and
             "PROGRESS T60 outputs=%0d/%0d" in tb_text and
             "S2A-T58" not in tb_text and "row22" not in tb_text and
             "y=22" not in tb_text and ".tcl" not in tb_text.lower(),
             "T60 testbench 模块名、坐标、摘要或范围静态检查不匹配")
    for path_string in (
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T60\\run02\\fixture\\feature_input.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T60\\run02\\fixture\\layer35_weights.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T60\\run02\\fixture\\golden.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T60\\run02\\fixture\\vectors.txt",
    ):
        _require(path_string in tb_text, f"T60 testbench fixture 路径缺失：{path_string}")
    return {
        "python_ast": "PASS",
        "cli_modes": mode_options,
        "runner_no_xilinx_launch_or_tcl": True,
        "powershell_read_only_path_and_process_scan": "PASS",
        "testbench_top_row_and_fixture_paths": "PASS",
        "runner_sha256": _sha256(runner_bytes),
        "testbench_sha256": _sha256(tb_bytes),
        "powershell_source_sha256": _sha256(POWERSHELL_PREFLIGHT.encode("utf-8")),
    }


def _runtime_preflight(mode: str) -> dict[str, Any]:
    _require(mode in ("prepare", "verify"), f"T60 PowerShell 模式无效：{mode}")
    env = os.environ.copy()
    env["S2A_T60_PREFLIGHT_MODE"] = mode
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
         POWERSHELL_PREFLIGHT],
        cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False, timeout=30,
    )
    _require(result.returncode == 0,
             f"PowerShell 路径/进程预检失败(exit={result.returncode})："
             f"{result.stderr.strip()}")
    try:
        snapshot = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise T60Error(f"PowerShell 预检输出不是 JSON：{error}") from error
    _require(isinstance(snapshot, dict) and
             snapshot.get("mode") == mode and
             snapshot.get("path_chain_valid") is True and
             snapshot.get("checked_xpr") == str(XPR_PATH.resolve()) and
             tuple(snapshot.get("process_names", ())) == PROCESS_NAMES and
             snapshot.get("processes") == [],
             "T60 路径、XPR 或 8 类 Vivado/XSim 进程检查失败")
    if mode == "prepare":
        _require(snapshot.get("target_absent") is True and
             snapshot.get("existing_run02") is False,
                 "T60 prepare 目标已存在，拒绝覆盖")
    else:
        _require(snapshot.get("target_absent") is False and
             snapshot.get("existing_run02") is True,
                 "T60 verify-only 证据路径绑定不匹配")
    snapshot["powershell_exit_code"] = result.returncode
    snapshot["mcp_status"] = "NOT_QUERIED"
    return snapshot


def _load_binding_record(parent: dict[str, Any], key: str,
                         expected_path: Path | None = None) -> tuple[dict[str, Any], bytes]:
    record = parent.get("bindings", {}).get(key)
    _require(isinstance(record, dict) and isinstance(record.get("path"), str) and
             isinstance(record.get("sha256"), str),
             f"T54 父绑定缺少公开输入：{key}")
    path = Path(record["path"])
    _require(path.is_absolute(), f"T54 输入路径不是绝对路径：{key}")
    if expected_path is not None:
        _require(path.resolve() == expected_path.resolve(),
                 f"T54 输入路径与冻结项目路径不符：{key}")
    _require(path.is_file(), f"T54 公开输入文件缺失：{key} {path}")
    data = path.read_bytes()
    _require(_sha256(data) == record["sha256"].lower(),
             f"T54 公开输入 SHA-256 不符：{key}")
    if "bytes" in record:
        _require(len(data) == record["bytes"],
                 f"T54 公开输入字节数不符：{key}")
    return record, data


def _load_frozen_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """只从公开 G0/T01/T23/GF8 输入构造 oracle，不访问其他任务 TEMP。"""
    _require(_current_head() == BASE_HEAD,
             f"当前 HEAD 与 T60 冻结基线不符：{_current_head()}")
    parent, parent_sha = _read_json(T54_REPORT)
    _require(parent_sha == T54_REPORT_SHA256 and
             parent.get("schema") == "GestureForge-S2A-T54-layer35-row18-all-channels-v1" and
             parent.get("task_id") == "S2A-T54" and
             parent.get("status") == "PASS_SIMULATION_DATA_ONLY" and
             parent.get("acceptance_status") == "PASS_INDEPENDENT_REVIEW_DATA_ONLY" and
             parent.get("scope") ==
             "tiny416 cfg section36 layer35; all 256 output channels at y=18, x=0..25; not full layer or network",
             "T54 冻结行证据状态、范围或 SHA-256 不符")
    parent_bindings = parent.get("bindings", {})
    parent_sources = parent_bindings.get("T54_source_hashes", {})
    _require(set(parent_sources) == set(T54_SOURCE_PATHS),
             "T54 源码绑定集合不匹配")
    for relative, expected in parent_sources.items():
        source = ROOT / relative
        _require(source.is_file() and _sha_file(source) == str(expected).lower(),
                 f"T54 冻结源码 SHA-256 不符：{relative}")
    _require(parent_sources.get(T54_RUNNER.relative_to(ROOT).as_posix()) ==
             T54_RUNNER_SHA256 and
             parent_sources.get(T54_TESTBENCH.relative_to(ROOT).as_posix()) ==
             T54_TESTBENCH_SHA256,
             "T54 oracle/testbench 源码 SHA-256 与冻结值不符")
    _require(parent_bindings.get("fixed_points_yx") ==
             [[18, x] for x in range(OUTPUT_SIZE)] and
             parent_bindings.get("weight_layer35", {}).get("byte_offset") ==
             WEIGHT_OFFSET and
             parent_bindings.get("weight_layer35", {}).get("bytes") == WEIGHT_BYTES,
             "T54 y18 坐标或冻结 layer35 权重区间不匹配")
    parent_oracle = parent.get("oracle", {})
    parent_simulation = parent.get("simulation", {})
    _require(parent_oracle.get("raw_int32_count") == RAW_COUNT and
             parent_oracle.get("quantized_int8_count") == INT8_COUNT and
             parent_oracle.get("d2_t23_match_count") == INT8_COUNT and
             parent_simulation.get("status") == "PASS" and
             parent_simulation.get("raw_int32_compares") == RAW_COUNT and
             parent_simulation.get("quantized_int8_compares") == INT8_COUNT and
             parent_simulation.get("progress_checkpoint_count") == OUTPUT_CHANNELS and
             parent_simulation.get("observed_raw_int32_le_sha256") ==
             parent_oracle.get("raw_int32_le_sha256") and
             parent_simulation.get("observed_quantized_int8_sha256") ==
             parent_oracle.get("quantized_int8_sha256"),
             "T54 冻结 oracle 或行仿真逐值计数不匹配")

    expected_inputs = {
        "G0_specification": G0_PATH,
        "T01_manifest": T01_PATH,
        "T16_proof": T16_PATH,
        "T17_engine_evidence": T17_PATH,
        "T20_scheduler_evidence": T20_PATH,
        "T23_parameter_table": T23_PATH,
        "T16_script": T16_SCRIPT,
        "D2_forward_reference": D2_REFERENCE,
        "weight_report": WEIGHT_REPORT,
    }
    public_records: dict[str, dict[str, Any]] = {}
    public_data: dict[str, bytes] = {}
    for key, expected_path in expected_inputs.items():
        record, data = _load_binding_record(parent, key, expected_path)
        public_records[key] = record
        public_data[key] = data
    _require(public_records["G0_specification"]["sha256"] == G0_SHA256 and
             public_records["T01_manifest"]["sha256"] == T01_SHA256 and
             public_records["T16_proof"]["sha256"] == T16_SHA256 and
             public_records["T17_engine_evidence"]["sha256"] == T17_SHA256 and
             public_records["T20_scheduler_evidence"]["sha256"] == T20_SHA256 and
             public_records["T23_parameter_table"]["sha256"] == T23_SHA256 and
             public_records["T16_script"]["sha256"] == T16_SCRIPT_SHA256 and
             public_records["D2_forward_reference"]["sha256"] == D2_REFERENCE_SHA256 and
             public_records["weight_report"]["sha256"] == WEIGHT_REPORT_SHA256,
             "T54 继承的 G0/T01/T16/T17/T20/T23/D2/weight SHA 与固定输入不符")
    manifest = json.loads(public_data["T01_manifest"].decode("utf-8"))
    t16 = json.loads(public_data["T16_proof"].decode("utf-8"))
    t23 = json.loads(public_data["T23_parameter_table"].decode("utf-8"))
    weight_report = json.loads(public_data["weight_report"].decode("utf-8"))
    layers = {int(row["layer_index"]): row for row in manifest.get("layers", [])}
    _require(35 in layers, "T01 manifest 缺少 layer35")
    layer35 = layers[35]
    _require(layer35.get("cfg_section") == 36 and
             layer35.get("op") == "convolutional" and
             layer35.get("input_tensor_indices") == [34] and
             layer35.get("input_shape_nchw") == [1, INPUT_CHANNELS, OUTPUT_SIZE, OUTPUT_SIZE] and
             layer35.get("output_shape_nchw") == [1, OUTPUT_CHANNELS, OUTPUT_SIZE, OUTPUT_SIZE] and
             layer35.get("kernel_hw") == [3, 3] and
             layer35.get("stride_hw") == [1, 1] and
             layer35.get("padding_lrtb") == [1, 1, 1, 1] and
             layer35.get("padding_value_int8") == 0 and
             layer35.get("activation") == "leaky" and
             layer35.get("layout") == "NCHW" and
             layer35.get("accumulator_bits") == 32,
             "T01 layer35 几何、量化或累加规格不符")
    _require(len(layer35.get("bias_accumulator_int32_per_output_channel", [])) ==
             OUTPUT_CHANNELS and
             len(layer35.get("fused_bias_float32_per_output_channel", [])) ==
             OUTPUT_CHANNELS and
             len(layer35.get("weight_scale_per_output_channel", [])) ==
             OUTPUT_CHANNELS and
             layer35.get("input_scale", 0) > 0 and
             layer35.get("output_scale", 0) > 0,
             "T01 layer35 逐通道 bias/scale/参数长度错误")
    offsets = layer35.get("gf8_parameter_offsets", {})
    _require(offsets.get("quantized_weight_offset") == WEIGHT_OFFSET and
             offsets.get("quantized_weight_bytes") == WEIGHT_BYTES and
             offsets.get("fused_bias_offset") is not None,
             "T01 layer35 GF8 权重或 fused bias 区间不符")
    t23_layer = next((row for row in t23.get("layers", [])
                      if int(row.get("layer_index", -1)) == 35), None)
    t16_layer = next((row for row in t16.get("layers", [])
                      if int(row.get("layer_index", -1)) == 35), None)
    _require(t23_layer is not None and t16_layer is not None and
             t23_layer.get("candidate_parameter_sha256") ==
             t16_layer.get("candidate_parameter_sha256"),
             "T16/T23 layer35 参数摘要不一致")
    channels = t23_layer.get("channels", [])
    _require(len(channels) == OUTPUT_CHANNELS,
             "T23 layer35 输出通道数不为256")
    parameter_digest = hashlib.sha256()
    mq_values: list[tuple[int, int, int, int]] = []
    for channel_index, channel in enumerate(channels):
        _require(int(channel.get("channel", -1)) == channel_index,
                 "T23 layer35 通道编号不连续")
        values = (int(channel["positive_M"]), int(channel["positive_Q"]),
                  int(channel["negative_M"]), int(channel["negative_Q"]))
        _require(0 < values[0] <= 0x3FFF_FFFF and 0 <= values[1] <= 47 and
                 0 < values[2] <= 0x3FFF_FFFF and 0 <= values[3] <= 47,
                 f"T23 M/Q 参数超范围：oc={channel_index}")
        mq_values.append(values)
        parameter_digest.update(
            (f"{channel_index},{values[1]},{values[0]},{values[3]},{values[2]}\n")
            .encode("ascii")
        )
    _require(parameter_digest.hexdigest() ==
             t16_layer.get("candidate_parameter_sha256"),
             "T23 M/Q 参数摘要与 T16 proof 不一致")

    package_record = parent_bindings.get("GF8_package")
    manifest_package = manifest.get("bindings", {}).get("gf8_package")
    _require(isinstance(package_record, dict) and
             package_record.get("path") == manifest_package.get("path") and
             package_record.get("bytes") == GF8_BYTES and
             package_record.get("sha256") == GF8_SHA256,
             "T54/T01 GF8 package 路径、字节或 SHA-256 不一致")
    package_path = Path(package_record["path"])
    _require(package_path.is_absolute() and package_path.is_file(),
             f"GF8 package 精确路径不可读：{package_path}")
    package_bytes = package_path.read_bytes()
    _require(len(package_bytes) == GF8_BYTES and
             _sha256(package_bytes) == GF8_SHA256 and
             weight_report.get("package", {}).get("bytes") == GF8_BYTES and
             weight_report.get("package", {}).get("sha256") == GF8_SHA256,
             "GF8 package 与权重报告的长度或 SHA-256 不一致")
    weight_bytes = package_bytes[WEIGHT_OFFSET:WEIGHT_OFFSET + WEIGHT_BYTES]
    _require(len(weight_bytes) == WEIGHT_BYTES and
             _sha256(weight_bytes) ==
             parent_bindings["weight_layer35"]["sha256"],
             "GF8 layer35 weight slice 长度或摘要不匹配")
    fused_offset = int(offsets["fused_bias_offset"])
    fused_bytes = package_bytes[fused_offset:fused_offset + 4 * OUTPUT_CHANNELS]
    _require(len(fused_bytes) == 4 * OUTPUT_CHANNELS and
             struct.unpack("<256f", fused_bytes) ==
             tuple(float(value) for value in
                   layer35["fused_bias_float32_per_output_channel"]),
             "GF8/T01 layer35 fused bias 逐通道不一致")
    biases = tuple(int(value) for value in
                   layer35["bias_accumulator_int32_per_output_channel"])
    _require(all(-(1 << 31) <= value < (1 << 31) for value in biases),
             "T01 layer35 INT32 bias 超出有符号范围")

    preparation_inputs: dict[str, Any] = {
        "T54_parent_report": {
            "path": str(T54_REPORT.resolve()),
            "bytes": T54_REPORT.stat().st_size,
            "sha256": T54_REPORT_SHA256,
            "status": parent["status"],
            "acceptance_status": parent["acceptance_status"],
            "scope": parent["scope"],
            "fixed_points_yx": parent_bindings["fixed_points_yx"],
            "raw_int32_le_sha256": parent_oracle["raw_int32_le_sha256"],
            "quantized_int8_sha256": parent_oracle["quantized_int8_sha256"],
        },
        "T54_oracle_source": {
            "path": str(T54_RUNNER.resolve()),
            "sha256": T54_RUNNER_SHA256,
            "method": "_build_oracle",
        },
        **public_records,
        "GF8_package": {
            "path": str(package_path.resolve()),
            "bytes": len(package_bytes),
            "sha256": _sha256(package_bytes),
        },
        "weight_layer35": {
            "byte_offset": WEIGHT_OFFSET,
            "bytes": len(weight_bytes),
            "sha256": _sha256(weight_bytes),
        },
        "T54_source_hashes": parent_sources,
    }
    inputs = {
        "manifest": manifest,
        "layer35": layer35,
        "channels": channels,
        "biases": biases,
        "mq_values": tuple(mq_values),
        "weight_bytes": weight_bytes,
        "weight_sha256": _sha256(weight_bytes),
        "bindings": preparation_inputs,
        "package_path": package_path,
        "layer35_weight_offset": WEIGHT_OFFSET,
    }
    return parent, inputs, preparation_inputs


def _load_t54_oracle_module() -> Any:
    """加载并绑定 T54 冻结 oracle 的纯计算函数，不执行其任务 runner。"""
    _require(T54_RUNNER.is_file() and _sha_file(T54_RUNNER) == T54_RUNNER_SHA256,
             "T54 oracle 源码缺失或 SHA-256 不匹配")
    spec = importlib.util.spec_from_file_location("s2a_t54_frozen_oracle_for_t60",
                                                  T54_RUNNER)
    _require(spec is not None and spec.loader is not None,
             "无法载入 T54 冻结 oracle 源码")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _require(callable(getattr(module, "_build_oracle", None)),
             "T54 冻结源码缺少 _build_oracle")
    return module


def _build_oracle(inputs: dict[str, Any], progress: bool) -> dict[str, Any]:
    module = _load_t54_oracle_module()
    oracle_inputs = {
        "layer35": inputs["layer35"],
        "biases": inputs["biases"],
        "mq_values": inputs["mq_values"],
        "weight_bytes": inputs["weight_bytes"],
    }
    result = module._build_oracle(oracle_inputs, progress=progress, points=POINTS)
    _require(len(result["feature"]) == INPUT_BYTES and
             len(result["raw_values"]) == RAW_COUNT and
             len(result["quantized_values"]) == INT8_COUNT and
             len(result["combined_golden"]) == GOLDEN_BYTES,
             "T60 T54 oracle 输出长度或比较计数不正确")
    _require(result["oracle"]["raw_int32_count"] == RAW_COUNT and
             result["oracle"]["quantized_int8_count"] == INT8_COUNT and
             result["oracle"]["d2_t23_match_count"] == INT8_COUNT and
             result["expected_counts"]["output_cases"] == RAW_COUNT and
             result["expected_counts"]["raw_int32_compares"] == RAW_COUNT and
             result["expected_counts"]["quantized_int8_compares"] == INT8_COUNT and
             tuple(POINTS) == tuple((ROW_Y, x) for x in range(OUTPUT_SIZE)),
             "T60 y=24 點集或 raw/INT8/D2 逐值計數錯誤")
    return result


def _vectors_bytes(vectors: list[tuple[int, int, int, int, int, int, int, int]]) -> bytes:
    return ("".join(" ".join(str(value) for value in row) + "\n"
                    for row in vectors)).encode("ascii")


def _verify_file_record(record: dict[str, Any], expected_path: Path,
                        label: str) -> Path:
    _require(isinstance(record, dict) and
             record.get("path") == str(expected_path.resolve()) and
             isinstance(record.get("bytes"), int) and
             isinstance(record.get("sha256"), str),
             f"{label} 路径/摘要字段错误")
    path = expected_path.resolve()
    _require(path.is_file() and path.stat().st_size == record["bytes"] and
             _sha_file(path) == record["sha256"].lower(),
             f"{label} 文件缺失或字节/SHA-256 不匹配：{path}")
    return path


def _source_records() -> dict[str, dict[str, str]]:
    records = {}
    for relative, digest in _source_hashes().items():
        records[relative] = {"path": str((ROOT / relative).resolve()),
                             "sha256": digest}
    return records


def _file_set(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix()
            for path in root.rglob("*") if path.is_file()}


def _prepare() -> dict[str, Any]:
    _require(_current_head() == BASE_HEAD,
             f"当前 HEAD 与 T60 冻结基线不符：{_current_head()}")
    static_checks = _source_configuration_check()
    runtime_before = _runtime_preflight("prepare")
    xpr_sha_before = _sha_file(XPR_PATH)
    parent, inputs, preparation_inputs = _load_frozen_inputs()
    oracle = _build_oracle(inputs, progress=True)
    source_hashes = _source_hashes()
    _require(static_checks["runner_sha256"] ==
             source_hashes[T60_RUNNER_RELATIVE] and
             static_checks["testbench_sha256"] ==
             source_hashes[T60_TESTBENCH_RELATIVE],
             "T60 源文件在静态检查后发生变化")
    runtime_final = _runtime_preflight("prepare")
    _require(_current_head() == BASE_HEAD and
             _sha_file(XPR_PATH) == xpr_sha_before and
             _source_hashes() == source_hashes,
             "T60 准备期间 HEAD、XPR 或绑定源码发生变化")

    blobs = {
        "feature_input.bin": oracle["feature"],
        "layer35_weights.bin": inputs["weight_bytes"],
        "golden.bin": oracle["combined_golden"],
        "vectors.txt": _vectors_bytes(oracle["vectors"]),
    }
    _require(len(blobs["feature_input.bin"]) == INPUT_BYTES and
             len(blobs["layer35_weights.bin"]) == WEIGHT_BYTES and
             len(blobs["golden.bin"]) == GOLDEN_BYTES and
             len(blobs["vectors.txt"].splitlines()) == RAW_COUNT,
             "T60 fixture 字节数或向量行数不正确")
    RUN_ROOT.mkdir(parents=False, exist_ok=False)
    FIXTURE_ROOT.mkdir(parents=False, exist_ok=False)
    for name, content in blobs.items():
        _write_bytes_exclusive(FIXTURE_ROOT / name, content)
    xpr_sha_after = _sha_file(XPR_PATH)
    _require(xpr_sha_after == xpr_sha_before,
             "T60 prepare 期间目标 XPR SHA-256 发生变化")
    fixture_files = {name: _artifact(FIXTURE_ROOT / name)
                     for name in sorted(blobs)}
    preparation_inputs["T60_source_hashes"] = source_hashes
    preparation_inputs["T54_parent_report"]["path"] = str(T54_REPORT.resolve())
    project_binding = {
        "schema": "GestureForge-S2A-T60-project-preflight-v1",
        "status": "READ_ONLY_BOUND",
        "task_id": TASK_ID,
        "run_id": "run02",
        "run_directory": str(RUN_ROOT.resolve()),
        "project_name": "AX7Z020_Gesture",
        "project_xpr_path": str(XPR_PATH.resolve()),
        "baseline_head": BASE_HEAD,
        "target_xpr_sha256_before_prepare": xpr_sha_before,
        "target_xpr_sha256_after_prepare": xpr_sha_after,
        "target_xpr_unchanged": True,
        "T60_source_hashes": source_hashes,
        "preparation_inputs": preparation_inputs,
        "fixed_points_yx": [list(point) for point in POINTS],
        "expected_counts": {
            "raw_int32_compares": RAW_COUNT,
            "quantized_int8_compares": INT8_COUNT,
            "d2_t23_match_count": INT8_COUNT,
        },
        "runtime_preflight": runtime_final,
        "static_checks": static_checks,
        "mcp_status": "NOT_QUERIED",
        "vivado_opened": False,
        "vivado_cli_invoked": False,
        "launcher_created": False,
        "tcl_created": False,
    }
    _write_json_exclusive(PROJECT_PREFLIGHT, project_binding)
    project_preflight_record = _artifact(PROJECT_PREFLIGHT)
    manifest = {
        "schema": "GestureForge-S2A-T60-fixture-manifest-v1",
        "task_id": TASK_ID,
        "run_id": "run02",
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "scope": "tiny416 cfg section36 layer35; all 256 output channels at y=24, x=0..25",
        "parent_report": preparation_inputs["T54_parent_report"],
        "generator_source": preparation_inputs["T54_oracle_source"],
        "T60_source_hashes": source_hashes,
        "preparation_inputs": preparation_inputs,
        "project_preflight_binding": project_preflight_record,
        "fixture_root": str(FIXTURE_ROOT.resolve()),
        "files": fixture_files,
        "fixture": oracle["fixture"],
        "oracle": oracle["oracle"],
        "expected_counts": oracle["expected_counts"],
        "fixed_points_yx": [list(point) for point in POINTS],
    }
    _write_json_exclusive(FIXTURE_MANIFEST, manifest)
    summary = {
        "schema": "GestureForge-S2A-T60-preparation-summary-v1",
        "task_id": TASK_ID,
        "run_id": "run02",
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "scope": "tiny416 cfg section36 layer35; all 256 output channels at y=24, x=0..25",
        "T54_parent_report": preparation_inputs["T54_parent_report"],
        "oracle_source": {
            **preparation_inputs["T54_oracle_source"],
            "method": "_build_oracle",
            "points": [list(point) for point in POINTS],
            "private_task_temp_used": False,
        },
        "bindings": {
            **preparation_inputs,
            "fixed_points_yx": [list(point) for point in POINTS],
            "model": {
                "name": inputs["manifest"].get("model", {}).get("name", "tiny416"),
                "cfg_section": inputs["layer35"]["cfg_section"],
                "layer_index": inputs["layer35"]["layer_index"],
                "input_shape_nchw": inputs["layer35"]["input_shape_nchw"],
                "output_shape_nchw": inputs["layer35"]["output_shape_nchw"],
                "kernel_hw": inputs["layer35"]["kernel_hw"],
                "stride_hw": inputs["layer35"]["stride_hw"],
                "padding_lrtb": inputs["layer35"]["padding_lrtb"],
                "padding_value_int8": inputs["layer35"]["padding_value_int8"],
                "layout": inputs["layer35"]["layout"],
                "accumulator_bits": inputs["layer35"]["accumulator_bits"],
                "activation": inputs["layer35"]["activation"],
                "input_scale": inputs["layer35"]["input_scale"],
                "output_scale": inputs["layer35"]["output_scale"],
            },
        },
        "fixture": {
            "root": str(FIXTURE_ROOT.resolve()),
            "files": fixture_files,
            "manifest": _artifact(FIXTURE_MANIFEST),
            "golden_layout": {
                "raw_int32_le_bytes": RAW_BYTES,
                "int8_bytes": INT8_BYTES,
                "total_bytes": GOLDEN_BYTES,
                "order": "全部 raw INT32 little-endian，随后全部 INT8",
            },
        },
        "feature_fixture": oracle["fixture"],
        "oracle": oracle["oracle"],
        "expected_counts": oracle["expected_counts"],
        "project_preflight": {
            **project_preflight_record,
            "project_name": "AX7Z020_Gesture",
            "target_xpr_sha256": xpr_sha_after,
            "target_xpr_unchanged": True,
        },
        "runtime_preflight": runtime_final,
        "static_checks": static_checks,
        "simulation": {
            "status": "NOT_RUN",
            "reason": "本任务只准备 CPU oracle 与 fixture，未生成 launcher/Tcl，也未运行 Vivado/XSim。",
        },
        "review": {
            "G2": "NOT_REVIEWED",
            "G3": "NOT_CLAIMED",
            "G4": "NOT_CLAIMED",
            "G5": "NOT_CLAIMED",
        },
        "limitations": [
            "仅覆盖 y=24、x=0..25、256 个输出通道，不代表 layer35 全层或整网。",
            "本证据仅表示 CPU oracle 与 fixture 已准备，未运行 RTL 仿真。",
            "T54 仅作为冻结 oracle/协议来源；未读取其私有 TEMP 运行文件。",
        ],
        "completed_utc8": datetime.now(
            timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
    }
    _write_json_exclusive(PREPARE_REPORT, summary)
    print(json.dumps({
        "result": summary["status"],
        "prepare_report": str(PREPARE_REPORT.resolve()),
        "project_preflight": str(PROJECT_PREFLIGHT.resolve()),
        "fixture_root": str(FIXTURE_ROOT.resolve()),
        "source_hashes": source_hashes,
        "counts": {
            "raw_int32_compares": RAW_COUNT,
            "quantized_int8_compares": INT8_COUNT,
            "d2_t23_match_count": INT8_COUNT,
        },
        "oracle": oracle["oracle"],
        "fixture_files": fixture_files,
        "project_preflight_binding": project_preflight_record,
        "simulation": "NOT_RUN",
    }, ensure_ascii=False, indent=2), flush=True)
    return summary


def _verify_prepared() -> dict[str, Any]:
    _require(_current_head() == BASE_HEAD,
             f"当前 HEAD 与 T60 冻结基线不符：{_current_head()}")
    static_checks = _source_configuration_check()
    runtime = _runtime_preflight("verify")
    parent, inputs, preparation_inputs = _load_frozen_inputs()
    oracle = _build_oracle(inputs, progress=True)
    _require(PREPARE_REPORT.is_file() and PROJECT_PREFLIGHT.is_file() and
             FIXTURE_MANIFEST.is_file(),
             "T60 prepare_summary、工程预检绑定或 fixture manifest 缺失")
    summary, summary_sha = _read_json(PREPARE_REPORT)
    binding, binding_sha = _read_json(PROJECT_PREFLIGHT)
    manifest, manifest_sha = _read_json(FIXTURE_MANIFEST)
    source_hashes = _source_hashes()
    preparation_inputs["T60_source_hashes"] = source_hashes
    _require(summary.get("schema") ==
             "GestureForge-S2A-T60-preparation-summary-v1" and
             summary.get("task_id") == TASK_ID and summary.get("run_id") == "run02" and
             summary.get("status") == "PREPARED_NOT_SIMULATED" and
             summary.get("baseline_head") == BASE_HEAD and
             summary.get("scope") ==
             "tiny416 cfg section36 layer35; all 256 output channels at y=24, x=0..25" and
             binding.get("schema") ==
             "GestureForge-S2A-T60-project-preflight-v1" and
             binding.get("status") == "READ_ONLY_BOUND" and
             binding.get("task_id") == TASK_ID and binding.get("run_id") == "run02" and
             binding.get("baseline_head") == BASE_HEAD and
             manifest.get("schema") ==
             "GestureForge-S2A-T60-fixture-manifest-v1" and
             manifest.get("task_id") == TASK_ID and manifest.get("run_id") == "run02" and
             manifest.get("status") == "PREPARED_NOT_SIMULATED" and
             manifest.get("baseline_head") == BASE_HEAD and
             manifest.get("fixed_points_yx") == [list(point) for point in POINTS],
             "T60 prepare evidence schema、状态、基线或范围不匹配")
    _require(summary.get("bindings", {}).get("T60_source_hashes") == source_hashes and
             binding.get("T60_source_hashes") == source_hashes and
             manifest.get("T60_source_hashes") == source_hashes and
             static_checks["runner_sha256"] == source_hashes[T60_RUNNER_RELATIVE] and
             static_checks["testbench_sha256"] == source_hashes[T60_TESTBENCH_RELATIVE],
             "T60 prepare 后源码哈希绑定发生变化")
    _require(binding.get("project_xpr_path") == str(XPR_PATH.resolve()) and
             binding.get("run_directory") == str(RUN_ROOT.resolve()) and
             binding.get("target_xpr_unchanged") is True and
             binding.get("target_xpr_sha256_before_prepare") ==
             binding.get("target_xpr_sha256_after_prepare") ==
             _sha_file(XPR_PATH) and
             binding.get("mcp_status") == "NOT_QUERIED" and
             binding.get("vivado_opened") is False and
             binding.get("vivado_cli_invoked") is False and
             binding.get("launcher_created") is False and
             binding.get("tcl_created") is False,
             "T60 工程 XPR/只读状态绑定不匹配")
    _require(binding.get("preparation_inputs") == preparation_inputs and
             summary.get("bindings", {}).get("T54_parent_report") ==
             preparation_inputs["T54_parent_report"] and
             manifest.get("parent_report") ==
             preparation_inputs["T54_parent_report"] and
             summary.get("project_preflight", {}).get("path") ==
             str(PROJECT_PREFLIGHT.resolve()) and
             summary.get("project_preflight", {}).get("bytes") ==
             PROJECT_PREFLIGHT.stat().st_size and
             summary.get("project_preflight", {}).get("sha256") == binding_sha and
             manifest.get("project_preflight_binding") ==
             _artifact(PROJECT_PREFLIGHT),
             "T60 自包含输入绑定或工程预检交叉引用不匹配")
    _require(binding.get("runtime_preflight", {}).get("processes") == [] and
             binding.get("runtime_preflight", {}).get("powershell_exit_code") == 0 and
             runtime.get("processes") == [] and
             binding.get("static_checks", {}).get("python_ast") == "PASS" and
             binding.get("static_checks", {}).get(
                 "powershell_read_only_path_and_process_scan") == "PASS" and
             summary.get("runtime_preflight") == binding.get("runtime_preflight") and
             summary.get("static_checks") == binding.get("static_checks"),
             "T60 PowerShell 进程/路径或 Python 静态检查记录不匹配")
    _require(summary.get("oracle") == oracle["oracle"] and
             manifest.get("oracle") == oracle["oracle"] and
             summary.get("expected_counts") == oracle["expected_counts"] and
             manifest.get("expected_counts") == oracle["expected_counts"] and
             summary.get("feature_fixture") == oracle["fixture"] and
             manifest.get("fixture") == oracle["fixture"] and
             summary.get("bindings", {}).get("fixed_points_yx") ==
             [list(point) for point in POINTS],
             "T60 oracle、fixture 或 expected counts 重算不匹配")
    project_record = {
        "path": str(PROJECT_PREFLIGHT.resolve()),
        "bytes": PROJECT_PREFLIGHT.stat().st_size,
        "sha256": binding_sha,
    }
    _require(summary.get("project_preflight", {}).get("path") ==
             str(PROJECT_PREFLIGHT.resolve()) and
             summary.get("project_preflight", {}).get("sha256") == binding_sha and
             manifest_sha == summary.get("fixture", {}).get("manifest", {}).get("sha256") and
             manifest_sha == _sha_file(FIXTURE_MANIFEST),
             "T60 prepare_summary 与工程预检/manifest 摘要不一致")
    fixture_files = summary.get("fixture", {}).get("files", {})
    expected_blob_names = {
        "feature_input.bin", "layer35_weights.bin", "golden.bin", "vectors.txt",
    }
    _require(set(fixture_files) == expected_blob_names and
             manifest.get("files") == fixture_files and
             Path(summary.get("fixture", {}).get("root", "")).resolve() ==
             FIXTURE_ROOT.resolve() and
             Path(manifest.get("fixture_root", "")).resolve() ==
             FIXTURE_ROOT.resolve(),
             "T60 fixture 文件集或目录绑定不匹配")
    expected_blobs = {
        "feature_input.bin": oracle["feature"],
        "layer35_weights.bin": inputs["weight_bytes"],
        "golden.bin": oracle["combined_golden"],
        "vectors.txt": _vectors_bytes(oracle["vectors"]),
    }
    for name, data in expected_blobs.items():
        record = fixture_files[name]
        path = _verify_file_record(record, FIXTURE_ROOT / name,
                                   f"T60 fixture {name}")
        _require(path.read_bytes() == data,
                 f"T60 fixture 内容与重新计算的 oracle 不逐字节相同：{name}")
    golden = (FIXTURE_ROOT / "golden.bin").read_bytes()
    raw_golden, int8_golden = golden[:RAW_BYTES], golden[RAW_BYTES:]
    _require(len(raw_golden) == RAW_BYTES and len(int8_golden) == INT8_BYTES and
             _sha256(raw_golden) == oracle["oracle"]["raw_int32_le_sha256"] and
             _sha256(int8_golden) == oracle["oracle"]["quantized_int8_sha256"] and
             len(oracle["raw_values"]) == RAW_COUNT and
             len(oracle["quantized_values"]) == INT8_COUNT and
             oracle["oracle"]["d2_t23_match_count"] == INT8_COUNT,
             "T60 raw INT32/INT8/D2-T23 逐项验证计数或摘要错误")
    vector_lines = (FIXTURE_ROOT / "vectors.txt").read_text(
        encoding="ascii").splitlines()
    _require(len(vector_lines) == RAW_COUNT,
             "T60 vectors.txt 行数不等于6656")
    for index, line in enumerate(vector_lines):
        values = [int(value) for value in line.split()]
        _require(len(values) == 8 and values[0] == index // OUTPUT_SIZE and
                 values[1] == ROW_Y and values[2] == index % OUTPUT_SIZE and
                 tuple(values) == oracle["vectors"][index],
                 f"T60 vectors 坐标/字段错误：index={index}")
    expected_files = {
        "project_preflight_binding.json",
        "prepare_summary.json",
        "fixture/feature_input.bin",
        "fixture/layer35_weights.bin",
        "fixture/golden.bin",
        "fixture/vectors.txt",
        "fixture/fixture_manifest.json",
    }
    _require(_file_set(RUN_ROOT) == expected_files,
             f"T60 run02 文件集合错误：actual={sorted(_file_set(RUN_ROOT))}")
    _require(summary.get("simulation", {}).get("status") == "NOT_RUN" and
             summary.get("review") == {
                 "G2": "NOT_REVIEWED", "G3": "NOT_CLAIMED",
                 "G4": "NOT_CLAIMED", "G5": "NOT_CLAIMED",
             },
             "T60 准备报告错误声明仿真或验收状态")
    print(json.dumps({
        "result": "PREPARED_NOT_SIMULATED",
        "prepare_summary_sha256": summary_sha,
        "project_preflight_sha256": binding_sha,
        "fixture_manifest_sha256": manifest_sha,
        "output_counts": {
            "raw_int32_compares": RAW_COUNT,
            "quantized_int8_compares": INT8_COUNT,
            "d2_t23_match_count": INT8_COUNT,
        },
        "oracle": oracle["oracle"],
        "simulation": "NOT_RUN",
    }, ensure_ascii=False, indent=2), flush=True)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--prepare-only", action="store_true")
    modes.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.prepare_only:
            _prepare()
        else:
            _verify_prepared()
        return 0
    except Exception as error:
        print(f"FAIL T60 {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
