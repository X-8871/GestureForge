#!/usr/bin/env python3
"""为 S2A-T58 生成并核验 row22 的独立 CPU oracle 与准备证据。"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
BASE_HEAD = "7b8bad78a456310d2ca797a02e3a5a7f873f9c18"
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
T58_SOURCE_PATHS = (
    *RTL_PATHS,
    "sim/tb_s2a_conv_layer35_row22_all_channels.sv",
    "verification/test_s2a_conv_layer35_row22_all_channels_rtl.py",
)
T58_RUNNER_RELATIVE = "verification/test_s2a_conv_layer35_row22_all_channels_rtl.py"
XPR_PATH = ROOT / "vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr"
EVIDENCE_ROOT = ROOT / "report/evidence/S2A-T58"
ROOT_PROJECT_PREFLIGHT = EVIDENCE_ROOT / "project_preflight_binding.json"
RUN01_ROOT = EVIDENCE_ROOT / "run01"
RUN_ROOT = EVIDENCE_ROOT / "run02"
FIXTURE_ROOT = RUN_ROOT / "fixture"
PREPARE_REPORT = RUN_ROOT / "prepare_summary.json"
PROJECT_PREFLIGHT = RUN_ROOT / "project_preflight_binding.json"
POINTS = tuple((22, x) for x in range(26))
RAW_COUNT = 6_656
INT8_COUNT = 6_656
RAW_BYTES = RAW_COUNT * 4
INT8_BYTES = INT8_COUNT
GOLDEN_BYTES = RAW_BYTES + INT8_BYTES
FEATURE_BYTES = 259_584
WEIGHT_BYTES = 884_736
PROCESS_NAMES = (
    "vivado.exe", "vivado_lab.exe", "xsim.exe", "xsimk.exe",
    "xelab.exe", "xvlog.exe", "xvhdl.exe", "xsct.exe",
)
XPR_SHA256 = "9e637bb8a31c8c74cdb703d632282a020875f5623893665719c1bbb5035be1ec"
RUN01_ROOT_BINDING_SHA256 = "826b77342a20c9fa3ead66e9496f67b7f41c26c45b3744c7a1bb10438a38aa01"
RUN01_ROOT_BINDING_BYTES = 4_335
RUN01_SOURCE_HASHES = {
    "src/int8_conv_tap_geometry.sv": "109b58473fa2f5d6de5c362e0c780ae2e98bce260c1d92714fde58ae706e4bbc",
    "src/int8_conv_weight_address.sv": "0914df477c9e160d227c74f9eaf926e502069e563145e1e1f3e03673654d4592",
    "src/int8_mac_accumulator.sv": "b3f6a425e2db58b86c63524b9caf0019ddf7a103c5b66f8bfcc3cf86966d0a74",
    "src/s2a_conv_engine.sv": "8656f43f510a8f7c74aaee44f809da74adeb3b8c5fed32f8f009aabecb05c994",
    "src/s2a_conv_layer35_channel_probe.sv": "91f1e954c1a50a0047861b40df75d1f0523ae2307f03d0c7328abaf4d5469ef4",
    "sim/tb_s2a_conv_layer35_row22_all_channels.sv": "57fc1a6e1db1e4ae90661c007ebfa4e6f7a5cdbd8ac3fbc1d7bf8aebfb2cfdec",
    "verification/test_s2a_conv_layer35_row22_all_channels_rtl.py": "7a065d38f583c3af13cd15ae3286dd911fbb05fb55bdab7bf52dab75e51d4165",
}
RUN02_TB_IO_LITERALS = {
    "feature_input.bin": r"D:\\FPGA_Competition\\report\\evidence\\S2A-T58\\run02\\fixture\\feature_input.bin",
    "layer35_weights.bin": r"D:\\FPGA_Competition\\report\\evidence\\S2A-T58\\run02\\fixture\\layer35_weights.bin",
    "golden.bin": r"D:\\FPGA_Competition\\report\\evidence\\S2A-T58\\run02\\fixture\\golden.bin",
    "vectors.txt": r"D:\\FPGA_Competition\\report\\evidence\\S2A-T58\\run02\\fixture\\vectors.txt",
    "observed_raw.bin": r"D:\\FPGA_Competition\\report\\evidence\\S2A-T58\\run02\\observed_raw.bin",
    "observed_output.bin": r"D:\\FPGA_Competition\\report\\evidence\\S2A-T58\\run02\\observed_output.bin",
}
PREVIOUS_RUN01_SNAPSHOT = {
    "fixture/feature_input.bin": (259_584, "f7cbcdae9627c974b0210b3329be66a4264d96d0e2474d3c7f30a1b9c2f59ff1"),
    "fixture/fixture_manifest.json": (6_145, "895dd04ba9d50e22705849783842f921d319982ef9b7b00834af774bb2dc9b48"),
    "fixture/golden.bin": (33_280, "0892e785cfb724eb10c9fd39b5bdba2836fa4eb9c0374dd31e5fd2aa7ce50271"),
    "fixture/layer35_weights.bin": (884_736, "e7b7d6fd8511b918d0a3ee372ef9d35eb4f3a2827fac77e28cf4f9d775d85bc2"),
    "fixture/vectors.txt": (254_606, "ba7d9a9944fe0d1a2b62b7831fea6963a0e86945e68f0feaf4c73ce55fcaffed"),
    "prepare_summary.json": (13_196, "33c67467387ec6ecd2c6945fb34c0485b351ed7b60f449135158f33e19b9f341"),
}
POWERSHELL_PREFLIGHT = r"""
$ErrorActionPreference = 'Stop'
$expectRun02Absent = __EXPECT_RUN02_ABSENT__
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
if ($xprItem.PSIsContainer -or
    (($xprItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
    throw "目标 XPR 不是普通文件：$xpr"
}
$evidenceRoot = 'D:\FPGA_Competition\report\evidence\S2A-T58'
$run01Root = Join-Path $evidenceRoot 'run01'
$run02Root = Join-Path $evidenceRoot 'run02'
$rootExists = Test-Path -LiteralPath $evidenceRoot
$run01Exists = Test-Path -LiteralPath $run01Root
$run02Exists = Test-Path -LiteralPath $run02Root
$rootPreflightPath = Join-Path $evidenceRoot 'project_preflight_binding.json'
$run02PreflightPath = Join-Path $run02Root 'project_preflight_binding.json'
if (-not $rootExists -or -not $run01Exists -or
    -not (Test-Path -LiteralPath $rootPreflightPath -PathType Leaf)) {
    throw 'T58 run01/root binding 历史证据缺失'
}
if ($expectRun02Absent -and $run02Exists) {
    throw 'T58 run02 目标已存在，拒绝覆盖'
}
if (-not $expectRun02Absent -and -not $run02Exists) {
    throw 'T58 run02 准备目录缺失'
}
$rootPreflightItem = Get-Item -LiteralPath $rootPreflightPath -Force -ErrorAction Stop
if ($rootPreflightItem.PSIsContainer -or
    (($rootPreflightItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
    throw 'T58 历史工程预检绑定不是普通文件'
}
if ($run01Exists) {
    foreach ($path in @($evidenceRoot, $run01Root, (Join-Path $run01Root 'fixture'))) {
        $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if (-not $item.PSIsContainer -or
            (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "T58 run01 路径不是普通目录：$path"
        }
    }
}
if ($run02Exists) {
    foreach ($path in @($run02Root, (Join-Path $run02Root 'fixture'), $run02PreflightPath)) {
        $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
        $isDirectory = $path -ne $run02PreflightPath
        if (($item.PSIsContainer -ne $isDirectory) -or
            (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "T58 run02 路径类型或 reparse 状态错误：$path"
        }
    }
}
$expectedRootEntries = @('project_preflight_binding.json', 'run01')
if ($run02Exists) { $expectedRootEntries += 'run02' }
$expectedRootEntries = @($expectedRootEntries | Sort-Object)
$actualRootEntries = @(Get-ChildItem -LiteralPath $evidenceRoot -Force |
    ForEach-Object { $_.Name } | Sort-Object)
if (($actualRootEntries -join '|') -ne ($expectedRootEntries -join '|')) {
    throw 'T58 根目录含非预期节点'
}
foreach ($scanRoot in @($run01Root, $(if ($run02Exists) { $run02Root }))) {
    if (-not $scanRoot) { continue }
    $pending = [Collections.Generic.Stack[string]]::new()
    $pending.Push($scanRoot)
    while ($pending.Count -gt 0) {
        $directory = $pending.Pop()
        foreach ($entry in [IO.Directory]::EnumerateFileSystemEntries($directory)) {
            $attributes = [IO.File]::GetAttributes($entry)
            if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "T58 历史/新准备目录中发现 reparse point：$entry"
            }
            if (($attributes -band [IO.FileAttributes]::Directory) -ne 0) {
                $pending.Push($entry)
            }
        }
    }
}
$names = @('vivado.exe', 'vivado_lab.exe', 'xsim.exe', 'xsimk.exe',
           'xelab.exe', 'xvlog.exe', 'xvhdl.exe', 'xsct.exe')
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
    path_chain_valid = $true
    checked_directories = $requiredDirectories
    checked_xpr = $xpr
    target_absent = (-not $run02Exists)
    existing_run01 = $run01Exists
    existing_run02 = $run02Exists
    process_names = $names
    processes_before_prepare = $processes
}
[Console]::Out.Write((ConvertTo-Json -InputObject $result -Depth 5 -Compress))
"""


class T58Error(RuntimeError):
    """表示 S2A-T58 冻结输入或准备证据核验失败。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T58Error(message)


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
    temporary = path.with_name(path.name + ".t58.tmp")
    _require(not temporary.exists(), f"拒绝覆盖 T58 临时文件：{temporary}")
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with temporary.open("xb") as stream:
        stream.write(payload)
    temporary.replace(path)


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


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise T58Error(
        "Git merge-base ancestor 检查失败："
        f"{result.stderr.strip() or result.returncode}"
    )


def _verify_file_record(record: dict[str, Any], label: str) -> Path:
    path = Path(str(record.get("path", "")))
    if not path.is_absolute():
        path = ROOT / path
    _require(path.is_file(), f"{label} 工件不存在：{path}")
    if "bytes" in record:
        _require(path.stat().st_size == int(record["bytes"]),
                 f"{label} 字节数不符：{path}")
    if "sha256" in record:
        _require(_sha_file(path) == str(record["sha256"]).lower(),
                 f"{label} SHA-256 不符：{path}")
    return path


def _verify_parent() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    current_head = _current_head()
    _require(_is_ancestor(BASE_HEAD, current_head),
             f"当前 HEAD 不包含 T58 冻结基线祖先：{current_head}")
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
    _require(parent_sources.get(T56_RUNNER.relative_to(ROOT).as_posix()) ==
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
    summary, _ = _read_json(_verify_file_record(
        {"path": str(T56_SUMMARY), "sha256": T56_SUMMARY_SHA256},
        "T56 仿真摘要",
    ))
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


def _load_oracle_runner(runtime_head: str) -> tuple[Any, str]:
    _require(T54_RUNNER.is_file() and _sha_file(T54_RUNNER) == T54_RUNNER_SHA256,
             "T54 独立 oracle 源码缺失或 SHA-256 不匹配")
    spec = importlib.util.spec_from_file_location("s2a_t54_reviewed_oracle_for_t58",
                                                  T54_RUNNER)
    _require(spec is not None and spec.loader is not None,
             "无法载入 T54 独立 oracle")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    historical_head = str(module.BASE_HEAD)
    module.BASE_HEAD = runtime_head
    return module, historical_head


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative in T58_SOURCE_PATHS:
        path = ROOT / relative
        _require(path.is_file(), f"缺少 T58 源码：{relative}")
        hashes[relative] = _sha_file(path)
    return hashes


def _vectors_bytes(vectors: list[tuple[int, int, int, int, int, int, int, int]]) -> bytes:
    return ("".join(" ".join(str(value) for value in vector) + "\n"
                    for vector in vectors)).encode("ascii")


def _runtime_preflight(expect_run02_absent: bool) -> dict[str, Any]:
    executable = "powershell.exe"
    powershell_script = POWERSHELL_PREFLIGHT.replace(
        "__EXPECT_RUN02_ABSENT__",
        "$true" if expect_run02_absent else "$false",
    )
    _require("__EXPECT_RUN02_ABSENT__" not in powershell_script,
             "T58 PowerShell 预检阶段参数未替换")
    result = subprocess.run(
        [executable, "-NoProfile", "-NonInteractive", "-Command",
         powershell_script],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False, timeout=30,
    )
    _require(result.returncode == 0,
             f"PowerShell 路径/进程预检失败：{result.stderr.strip()}")
    try:
        snapshot = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise T58Error(f"PowerShell 预检输出不是 JSON：{error}") from error
    _require(isinstance(snapshot, dict) and
             snapshot.get("path_chain_valid") is True and
             snapshot.get("target_absent") is expect_run02_absent and
             snapshot.get("existing_run01") is True and
             snapshot.get("existing_run02") is (not expect_run02_absent) and
             tuple(snapshot.get("process_names", ())) == PROCESS_NAMES and
             snapshot.get("processes_before_prepare") == [],
             "T58 路径/reparse 或 8 类 Vivado/XSim 进程门禁不通过")
    snapshot["powershell_exit_code"] = result.returncode
    snapshot["mcp_status"] = "NOT_QUERIED"
    return snapshot


def _verify_previous_run01() -> dict[str, Any]:
    _require(EVIDENCE_ROOT.is_dir() and RUN01_ROOT.is_dir() and
             (RUN01_ROOT / "fixture").is_dir(),
             "既有 T58 run01 路径类型错误")
    _require(ROOT_PROJECT_PREFLIGHT.is_file() and
             ROOT_PROJECT_PREFLIGHT.stat().st_size == RUN01_ROOT_BINDING_BYTES and
             _sha_file(ROOT_PROJECT_PREFLIGHT) == RUN01_ROOT_BINDING_SHA256,
             "T58 历史 root binding 的字节数或 SHA-256 不匹配")
    actual_files = {
        path.relative_to(RUN01_ROOT).as_posix()
        for path in RUN01_ROOT.rglob("*") if path.is_file()
    }
    _require(actual_files == set(PREVIOUS_RUN01_SNAPSHOT),
             f"既有 T58 run01 文件集合不匹配：{sorted(actual_files)}")
    for relative, (expected_size, expected_sha256) in PREVIOUS_RUN01_SNAPSHOT.items():
        path = RUN01_ROOT / relative
        _require(path.is_file() and path.stat().st_size == expected_size and
                 _sha_file(path) == expected_sha256,
                 f"既有 T58 run01 不等于本任务先前准备快照：{relative}")
    root_binding, root_binding_sha = _read_json(ROOT_PROJECT_PREFLIGHT)
    _require(root_binding_sha == RUN01_ROOT_BINDING_SHA256 and
             root_binding.get("schema") ==
             "GestureForge-S2A-T58-project-preflight-v1" and
             root_binding.get("task_id") == "S2A-T58" and
             root_binding.get("run_id") == "run01" and
             root_binding.get("run_directory") == str(RUN01_ROOT.resolve()) and
             root_binding.get("project_xpr_path") == str(XPR_PATH.resolve()) and
             root_binding.get("target_xpr_sha256_before_prepare") == XPR_SHA256 and
             root_binding.get("target_xpr_sha256_after_prepare") == XPR_SHA256 and
             root_binding.get("target_xpr_unchanged") is True and
             root_binding.get("T58_source_hashes") == RUN01_SOURCE_HASHES,
             "T58 历史 root binding 结构或固定哈希不匹配")
    for relative, expected in RUN01_SOURCE_HASHES.items():
        if relative not in (T58_RUNNER_RELATIVE,
                            "sim/tb_s2a_conv_layer35_row22_all_channels.sv"):
            source = ROOT / relative
            _require(source.is_file() and _sha_file(source) == expected,
                     f"T58 run01 保留源码哈希不匹配：{relative}")

    summary_path = RUN01_ROOT / "prepare_summary.json"
    summary, summary_sha = _read_json(summary_path)
    manifest_path = RUN01_ROOT / "fixture/fixture_manifest.json"
    manifest, manifest_sha = _read_json(manifest_path)
    root_binding_record = _artifact(ROOT_PROJECT_PREFLIGHT)
    expected_old_files = {
        name.removeprefix("fixture/"): {
            "path": str((RUN01_ROOT / name).resolve()),
            "bytes": size,
            "sha256": sha,
        }
        for name, (size, sha) in PREVIOUS_RUN01_SNAPSHOT.items()
        if name.startswith("fixture/") and name != "fixture/fixture_manifest.json"
    }
    _require(summary.get("schema") ==
             "GestureForge-S2A-T58-preparation-summary-v2" and
             summary.get("task_id") == "S2A-T58" and
             summary.get("run_id") == "run01" and
             summary.get("status") == "PREPARED_NOT_SIMULATED" and
             summary.get("baseline_head") == BASE_HEAD and
             summary.get("bindings", {}).get("T58_source_hashes") ==
             RUN01_SOURCE_HASHES and
             summary.get("bindings", {}).get("project_preflight_binding") ==
             root_binding_record and
             summary.get("fixture", {}).get("manifest") == {
                 "path": str(manifest_path.resolve()),
                 "bytes": PREVIOUS_RUN01_SNAPSHOT[
                     "fixture/fixture_manifest.json"][0],
                 "sha256": PREVIOUS_RUN01_SNAPSHOT[
                     "fixture/fixture_manifest.json"][1],
             } and
             summary.get("fixture", {}).get("files") == expected_old_files,
             "T58 run01 prepare summary 历史绑定不匹配")
    _require(manifest.get("schema") ==
             "GestureForge-S2A-T58-fixture-manifest-v2" and
             manifest.get("task_id") == "S2A-T58" and
             manifest.get("run_id") == "run01" and
             manifest.get("status") == "PREPARED_NOT_SIMULATED" and
             manifest.get("baseline_head") == BASE_HEAD and
             manifest.get("T58_source_hashes") == RUN01_SOURCE_HASHES and
             manifest.get("project_preflight_binding") == root_binding_record and
             manifest.get("files") == expected_old_files,
             "T58 run01 fixture manifest 历史绑定不匹配")
    return {
        "run_id": "run01",
        "run_directory": str(RUN01_ROOT.resolve()),
        "prepare_summary": {
            "path": str(summary_path.resolve()),
            "bytes": PREVIOUS_RUN01_SNAPSHOT["prepare_summary.json"][0],
            "sha256": summary_sha,
        },
        "fixture_manifest": {
            "path": str(manifest_path.resolve()),
            "bytes": PREVIOUS_RUN01_SNAPSHOT[
                "fixture/fixture_manifest.json"][0],
            "sha256": manifest_sha,
        },
        "root_project_preflight_binding": root_binding_record,
        "fixture_files": expected_old_files,
    }


def _project_xpr_sha() -> str:
    _require(XPR_PATH.is_file(), f"目标 XPR 缺失：{XPR_PATH}")
    digest = _sha_file(XPR_PATH)
    _require(digest == XPR_SHA256,
             f"目标 XPR SHA-256 与 T58 冻结值不符：{digest}")
    return digest


def _verify_tb_run_paths() -> dict[str, Any]:
    tb_path = ROOT / "sim/tb_s2a_conv_layer35_row22_all_channels.sv"
    _require(tb_path.is_file(), f"T58 testbench 缺失：{tb_path}")
    try:
        content = tb_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise T58Error(f"T58 testbench 不是 UTF-8：{error}") from error
    fopen_paths = re.findall(r'\$fopen\("([^"]+)"\s*,', content)
    expected_paths = list(RUN02_TB_IO_LITERALS.values())
    _require(len(fopen_paths) == len(expected_paths) and
             sorted(fopen_paths) == sorted(expected_paths) and
             all("\\run01\\" not in path for path in fopen_paths),
             "T58 testbench 的六个 fopen 路径未全部绑定到 run02")
    return {
        "run_id": "run02",
        "fopen_count": len(fopen_paths),
        "paths": {
            name: str((RUN_ROOT / relative).resolve())
            for name, relative in (
                ("feature_input.bin", "fixture/feature_input.bin"),
                ("layer35_weights.bin", "fixture/layer35_weights.bin"),
                ("golden.bin", "fixture/golden.bin"),
                ("vectors.txt", "fixture/vectors.txt"),
                ("observed_raw.bin", "observed_raw.bin"),
                ("observed_output.bin", "observed_output.bin"),
            )
        },
    }


def _prepare() -> dict[str, Any]:
    parent, parent_bindings, parent_simulation = _verify_parent()
    preparation_head = _current_head()
    _require(_is_ancestor(BASE_HEAD, preparation_head),
             "T58 prepare HEAD 不包含冻结基线祖先")
    runtime = _runtime_preflight(expect_run02_absent=True)
    preserved_run01 = _verify_previous_run01()
    _require(not RUN_ROOT.exists(),
             f"T58 run02 目标已存在，拒绝覆盖：{RUN_ROOT}")
    tb_io_paths = _verify_tb_run_paths()
    xpr_sha_before = _project_xpr_sha()

    oracle_runner, historical_oracle_head = _load_oracle_runner(preparation_head)
    inputs = oracle_runner._load_frozen_inputs()
    input_bindings = inputs["bindings"]
    _require(input_bindings["T01_manifest"]["sha256"] == T01_SHA256 and
             input_bindings["T23_parameter_table"]["sha256"] == T23_SHA256 and
             input_bindings["GF8_package"]["sha256"] == GF8_SHA256,
             "独立 oracle 返回的模型/量化输入绑定不匹配")
    _require(inputs["weight_sha256"] ==
             parent_bindings["weight_layer35"]["sha256"] and
             len(inputs["weight_bytes"]) == WEIGHT_BYTES,
             "layer35 GF8 权重与 T56 继承权重不一致")
    oracle = oracle_runner._build_oracle(inputs, progress=True, points=POINTS)
    _require(len(oracle["feature"]) == FEATURE_BYTES and
             len(oracle["raw_values"]) == RAW_COUNT and
             len(oracle["quantized_values"]) == INT8_COUNT and
             len(oracle["combined_golden"]) == GOLDEN_BYTES,
             "T58 oracle 输出长度或比较数错误")
    _require(oracle["oracle"]["raw_int32_count"] == RAW_COUNT and
             oracle["oracle"]["quantized_int8_count"] == INT8_COUNT and
             oracle["oracle"]["d2_t23_match_count"] == INT8_COUNT and
             all(y == 22 for y, _ in POINTS) and
             tuple(x for _, x in POINTS) == tuple(range(26)),
             "T58 oracle 点集或 raw/INT8/D2 逐项计数错误")

    source_hashes = _source_hashes()
    blobs = {
        "feature_input.bin": oracle["feature"],
        "layer35_weights.bin": inputs["weight_bytes"],
        "golden.bin": oracle["combined_golden"],
        "vectors.txt": _vectors_bytes(oracle["vectors"]),
    }
    expected_sizes = {
        "feature_input.bin": FEATURE_BYTES,
        "layer35_weights.bin": WEIGHT_BYTES,
        "golden.bin": GOLDEN_BYTES,
    }
    for name, content in blobs.items():
        _require(name not in expected_sizes or
                 len(content) == expected_sizes[name],
                 f"T58 fixture 长度错误：{name}")

    RUN_ROOT.mkdir(parents=False, exist_ok=False)
    FIXTURE_ROOT.mkdir(parents=False, exist_ok=False)
    for name, content in blobs.items():
        with (FIXTURE_ROOT / name).open("xb") as stream:
            stream.write(content)

    fixture_files = {
        name: _artifact(FIXTURE_ROOT / name)
        for name in sorted(blobs)
    }
    preparation_inputs = {
        "T56_parent_report": {
            "path": str(T56_REPORT.resolve()),
            "sha256": T56_REPORT_SHA256,
        },
        "T56_summary": {
            "path": str(T56_SUMMARY.resolve()),
            "sha256": T56_SUMMARY_SHA256,
        },
        "G0_specification": {"path": str(G0_PATH.resolve()), "sha256": G0_SHA256},
        "T01_manifest": input_bindings["T01_manifest"],
        "T23_parameter_table": input_bindings["T23_parameter_table"],
        "GF8_package": input_bindings["GF8_package"],
        "weight_layer35": {
            "byte_offset": inputs["layer35_weight_offset"],
            "bytes": len(inputs["weight_bytes"]),
            "sha256": inputs["weight_sha256"],
        },
        "oracle_source": {
            "path": str(T54_RUNNER.resolve()),
            "sha256": T54_RUNNER_SHA256,
        },
    }
    xpr_sha_after = _project_xpr_sha()
    _require(xpr_sha_after == xpr_sha_before == XPR_SHA256,
             "T58 prepare 期间真实 XPR SHA-256 发生变化")
    _require(_current_head() == preparation_head and
             _is_ancestor(BASE_HEAD, preparation_head),
             "T58 prepare 期间 Git HEAD 发生变化或不再包含冻结基线")
    preflight = {
        "schema": "GestureForge-S2A-T58-project-preflight-v2",
        "status": "READ_ONLY_BOUND",
        "task_id": "S2A-T58",
        "run_id": "run02",
        "baseline_head": BASE_HEAD,
        "preparation_head": preparation_head,
        "run_directory": str(RUN_ROOT.resolve()),
        "project_name": "AX7Z020_Gesture",
        "project_xpr_path": str(XPR_PATH.resolve()),
        "target_xpr_sha256_before_prepare": xpr_sha_before,
        "target_xpr_sha256_after_prepare": xpr_sha_after,
        "target_xpr_unchanged": True,
        "T58_source_hashes": source_hashes,
        "preparation_inputs": preparation_inputs,
        "tb_io_paths": tb_io_paths,
        "preserved_run01": preserved_run01,
        "runtime_preflight": runtime,
        "mcp_status": "NOT_QUERIED",
        "vivado_opened": False,
        "vivado_cli_invoked": False,
    }
    _require(not PROJECT_PREFLIGHT.exists(),
             f"拒绝覆盖 T58 工程预检绑定：{PROJECT_PREFLIGHT}")
    _write_json_exclusive(PROJECT_PREFLIGHT, preflight)
    project_preflight_record = _artifact(PROJECT_PREFLIGHT)

    fixture_manifest_path = FIXTURE_ROOT / "fixture_manifest.json"
    fixture_manifest = {
        "schema": "GestureForge-S2A-T58-fixture-manifest-v3",
        "task_id": "S2A-T58",
        "run_id": "run02",
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "preparation_head": preparation_head,
        "preserved_run01": preserved_run01,
        "parent_report": preparation_inputs["T56_parent_report"],
        "generator_source": preparation_inputs["oracle_source"],
        "runner_source_sha256": source_hashes[T58_RUNNER_RELATIVE],
        "T58_source_hashes": source_hashes,
        "preparation_inputs": preparation_inputs,
        "project_preflight_binding": project_preflight_record,
        "tb_io_paths": tb_io_paths,
        "fixture_root": str(FIXTURE_ROOT.resolve()),
        "files": fixture_files,
        "oracle": oracle["oracle"],
        "fixed_points_yx": [list(point) for point in POINTS],
    }
    _write_json_exclusive(fixture_manifest_path, fixture_manifest)

    layer = inputs["layer35"]
    summary = {
        "schema": "GestureForge-S2A-T58-preparation-summary-v3",
        "task_id": "S2A-T58",
        "run_id": "run02",
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "preparation_head": preparation_head,
        "preserved_run01": preserved_run01,
        "tb_io_paths": tb_io_paths,
        "scope": "tiny416 cfg section36 layer35; all 256 output channels at y=22, x=0..25",
        "T56_parent_report": {
            "path": str(T56_REPORT.resolve()),
            "sha256": T56_REPORT_SHA256,
            "acceptance_status": parent["acceptance_status"],
            "fixed_points_yx": parent_bindings["fixed_points_yx"],
        },
        "T56_summary": {
            "path": str(T56_SUMMARY.resolve()),
            "sha256": T56_SUMMARY_SHA256,
        },
        "T56_simulation": {
            key: parent_simulation[key] for key in (
                "raw_int32_compares", "int8_compares",
                "progress_checkpoint_count",
                "raw_byte_identical_to_independent_golden",
                "int8_byte_identical_to_independent_golden",
            )
        },
        "oracle_source": {
            "path": str(T54_RUNNER.resolve()),
            "sha256": T54_RUNNER_SHA256,
            "methods": ["_load_frozen_inputs", "_build_oracle"],
            "historical_BASE_HEAD": historical_oracle_head,
            "runtime_BASE_HEAD": preparation_head,
            "reason": "T54 冻结 oracle 工作树基线不同；先核验 T56 父证据，再仅在内存中更新 HEAD 守卫。",
        },
        "bindings": {
            **preparation_inputs,
            "model": {
                "name": "tiny416",
                "cfg_section": layer["cfg_section"],
                "layer_index": layer["layer_index"],
                "input_shape_nchw": layer["input_shape_nchw"],
                "output_shape_nchw": layer["output_shape_nchw"],
                "kernel_hw": layer["kernel_hw"],
                "stride_hw": layer["stride_hw"],
                "padding_lrtb": layer["padding_lrtb"],
                "padding_value_int8": layer["padding_value_int8"],
                "layout": layer["layout"],
                "accumulator_bits": layer["accumulator_bits"],
            },
            "fixed_points_yx": [list(point) for point in POINTS],
            "T56_source_hashes": parent_bindings["T56_source_hashes"],
            "T58_source_hashes": source_hashes,
            "preparation_head": preparation_head,
            "preserved_run01": preserved_run01,
            "tb_io_paths": tb_io_paths,
            "project_preflight_binding": project_preflight_record,
        },
        "fixture": {
            "root": str(FIXTURE_ROOT.resolve()),
            "files": fixture_files,
            "manifest": _artifact(fixture_manifest_path),
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
        "runtime_preflight": runtime,
        "simulation": {
            "status": "NOT_RUN",
            "reason": "本任务只准备 CPU oracle 与 fixture，未创建 T58 launcher/Tcl，也未运行 Vivado/XSim。",
        },
        "review": {
            "G2": "NOT_REVIEWED",
            "G3": "NOT_CLAIMED",
            "G4": "NOT_CLAIMED",
            "G5": "NOT_CLAIMED",
        },
        "limitations": [
            "仅覆盖 y=22、x=0..25、256 个输出通道，不代表 layer35 全层或整网。",
            "本报告仅为 CPU oracle 与 fixture 准备结果，未运行 RTL 仿真。",
        ],
    }
    _write_json_exclusive(PREPARE_REPORT, summary)
    print(json.dumps({
        "result": summary["status"],
        "prepare_report": str(PREPARE_REPORT.resolve()),
        "project_preflight": str(PROJECT_PREFLIGHT.resolve()),
        "fixture_root": str(FIXTURE_ROOT.resolve()),
        "source_hashes": source_hashes,
        "counts": {
            "raw_int32": RAW_COUNT,
            "int8": INT8_COUNT,
            "progress_checkpoints_expected": 256,
        },
        "oracle": oracle["oracle"],
        "fixture_files": fixture_files,
        "project_preflight_binding": project_preflight_record,
    }, ensure_ascii=False, indent=2), flush=True)
    return summary


def _verify_prepared_fixture(preparation: dict[str, Any]) -> tuple[dict[str, Any], str, bytes]:
    fixture = preparation.get("fixture")
    _require(isinstance(fixture, dict), "T58 prepare_summary 缺少 fixture 对象")
    _require(Path(str(fixture.get("root", ""))).resolve() == FIXTURE_ROOT.resolve(),
             "T58 fixture 根目录与准备摘要绑定不一致")
    manifest_record = fixture.get("manifest")
    _require(isinstance(manifest_record, dict),
             "T58 prepare_summary 缺少 fixture manifest 绑定")
    manifest_path = _verify_file_record(manifest_record, "T58 fixture manifest")
    _require(manifest_path.resolve() == (FIXTURE_ROOT / "fixture_manifest.json").resolve(),
             "T58 fixture manifest 路径不匹配")
    manifest, manifest_sha256 = _read_json(manifest_path)
    _require(manifest_sha256 == str(manifest_record.get("sha256", "")).lower(),
             "T58 fixture manifest SHA-256 与 prepare_summary 不一致")
    _require(manifest.get("schema") == "GestureForge-S2A-T58-fixture-manifest-v3" and
             manifest.get("task_id") == "S2A-T58" and
             manifest.get("run_id") == "run02" and
             manifest.get("status") == "PREPARED_NOT_SIMULATED" and
             manifest.get("baseline_head") == BASE_HEAD and
             manifest.get("preparation_head") == preparation.get("preparation_head") and
             manifest.get("preserved_run01") == preparation.get("preserved_run01") and
             manifest.get("tb_io_paths") == preparation.get("tb_io_paths") and
             manifest.get("fixture_root") == str(FIXTURE_ROOT.resolve()) and
             manifest.get("fixed_points_yx") == [list(point) for point in POINTS],
             "T58 fixture manifest 的 schema、基线、根目录或坐标不匹配")
    _require(manifest.get("parent_report", {}).get("sha256") == T56_REPORT_SHA256,
             "T58 manifest 未绑定已审 T56 父报告")

    prepared_hashes = preparation.get("bindings", {}).get("T58_source_hashes")
    _require(isinstance(prepared_hashes, dict) and
             set(prepared_hashes) == set(T58_SOURCE_PATHS) and
             manifest.get("T58_source_hashes") == prepared_hashes,
             "T58 manifest 与 prepare_summary 源码绑定不一致")
    for relative, expected in prepared_hashes.items():
        source = ROOT / relative
        _require(source.is_file() and _sha_file(source) == str(expected).lower(),
                 f"T58 准备后源码哈希变化：{relative}")
    _require(manifest.get("runner_source_sha256") ==
             prepared_hashes.get(T58_RUNNER_RELATIVE),
             "T58 manifest 未绑定 runner SHA-256")
    preparation_inputs = {
        key: preparation.get("bindings", {}).get(key)
        for key in (
            "T56_parent_report", "T56_summary", "G0_specification",
            "T01_manifest", "T23_parameter_table", "GF8_package",
            "weight_layer35", "oracle_source",
        )
    }
    _require(all(isinstance(value, dict) for value in preparation_inputs.values()) and
             manifest.get("preparation_inputs") == preparation_inputs,
             "T58 manifest 与 prepare_summary 的冻结输入绑定不一致")
    project_preflight_record = preparation.get("bindings", {}).get(
        "project_preflight_binding")
    _require(isinstance(project_preflight_record, dict) and
             manifest.get("project_preflight_binding") == project_preflight_record,
             "T58 manifest 与 prepare_summary 的本地工程预检绑定不一致")
    tb_io_paths = _verify_tb_run_paths()
    _require(preparation.get("tb_io_paths") == tb_io_paths and
             manifest.get("tb_io_paths") == tb_io_paths,
             "T58 runner/TB run02 路径绑定不一致")

    expected_names = {
        "feature_input.bin", "layer35_weights.bin", "golden.bin", "vectors.txt",
    }
    prepared_files = fixture.get("files")
    manifest_files = manifest.get("files")
    _require(isinstance(prepared_files, dict) and set(prepared_files) == expected_names and
             isinstance(manifest_files, dict) and set(manifest_files) == expected_names,
             "T58 fixture 文件集合不匹配")
    for name in sorted(expected_names):
        prepared_record = prepared_files[name]
        manifest_file_record = manifest_files[name]
        _require(isinstance(prepared_record, dict) and
                 isinstance(manifest_file_record, dict),
                 f"T58 fixture 文件绑定格式错误：{name}")
        prepared_path = _verify_file_record(prepared_record, f"T58 prepare_summary {name}")
        manifest_file_path = _verify_file_record(manifest_file_record,
                                                 f"T58 manifest {name}")
        expected_path = FIXTURE_ROOT / name
        _require(prepared_path.resolve() == expected_path.resolve() and
                 manifest_file_path.resolve() == expected_path.resolve() and
                 prepared_record.get("bytes") == manifest_file_record.get("bytes") and
                 str(prepared_record.get("sha256", "")).lower() ==
                 str(manifest_file_record.get("sha256", "")).lower(),
                 f"T58 fixture 路径或摘要/manifest 绑定不一致：{name}")

    expected_sizes = {
        "feature_input.bin": FEATURE_BYTES,
        "layer35_weights.bin": WEIGHT_BYTES,
        "golden.bin": GOLDEN_BYTES,
    }
    for name, size in expected_sizes.items():
        _require(prepared_files[name].get("bytes") == size,
                 f"T58 fixture 字节数错误：{name}")

    prepared_oracle = preparation.get("oracle")
    _require(isinstance(prepared_oracle, dict) and
             manifest.get("oracle") == prepared_oracle and
             prepared_oracle.get("raw_int32_count") == RAW_COUNT and
             prepared_oracle.get("quantized_int8_count") == INT8_COUNT and
             prepared_oracle.get("d2_t23_match_count") == INT8_COUNT,
             "T58 oracle 字段或逐项计数不匹配")
    golden = (FIXTURE_ROOT / "golden.bin").read_bytes()
    raw_golden = golden[:RAW_BYTES]
    int8_golden = golden[RAW_BYTES:]
    combined_sha256 = _sha256(golden)
    raw_sha256 = _sha256(raw_golden)
    int8_sha256 = _sha256(int8_golden)
    _require(len(golden) == GOLDEN_BYTES and len(raw_golden) == RAW_BYTES and
             len(int8_golden) == INT8_BYTES and
             combined_sha256 == prepared_oracle.get("combined_golden_sha256") and
             raw_sha256 == prepared_oracle.get("raw_int32_le_sha256") and
             int8_sha256 == prepared_oracle.get("quantized_int8_sha256"),
             "T58 combined/raw/INT8 golden 字节摘要不匹配")
    vector_lines = (FIXTURE_ROOT / "vectors.txt").read_text(
        encoding="ascii").splitlines()
    _require(len(vector_lines) == RAW_COUNT,
             "T58 vectors.txt 行数不等于 6656")
    for index, line in enumerate(vector_lines):
        values = [int(value) for value in line.split()]
        _require(len(values) == 8 and values[0] == index // 26 and
                 values[1] == 22 and values[2] == index % 26,
                 f"T58 vectors.txt 坐标或字段错误：row={index}")
    return manifest, manifest_sha256, golden


def _verify_prepared() -> dict[str, Any]:
    parent, parent_bindings, _ = _verify_parent()
    current_head = _current_head()
    _require(_is_ancestor(BASE_HEAD, current_head),
             "verify-only 当前 HEAD 不包含 T58 冻结基线祖先")
    current_runtime = _runtime_preflight(expect_run02_absent=False)
    preserved_run01 = _verify_previous_run01()
    _require(PREPARE_REPORT.is_file(), "缺少 T58 prepare_summary.json")
    preparation, prepare_sha256 = _read_json(PREPARE_REPORT)
    preparation_head = str(preparation.get("preparation_head", ""))
    _require(preparation.get("schema") ==
             "GestureForge-S2A-T58-preparation-summary-v3" and
             preparation.get("task_id") == "S2A-T58" and
             preparation.get("run_id") == "run02" and
             preparation.get("status") == "PREPARED_NOT_SIMULATED" and
             preparation.get("baseline_head") == BASE_HEAD and
             len(preparation_head) == 40 and
             all(character in "0123456789abcdef" for character in preparation_head) and
             _is_ancestor(BASE_HEAD, preparation_head) and
             _is_ancestor(preparation_head, current_head) and
             preparation.get("preserved_run01") == preserved_run01 and
             preparation.get("tb_io_paths") == _verify_tb_run_paths() and
             preparation.get("scope") ==
             "tiny416 cfg section36 layer35; all 256 output channels at y=22, x=0..25" and
             preparation.get("bindings", {}).get("fixed_points_yx") ==
             [list(point) for point in POINTS],
             "T58 prepare_summary schema、状态、范围或基线不匹配")
    _verify_prepared_fixture(preparation)

    project_record = preparation.get("project_preflight", {})
    _require(project_record.get("path") == str(PROJECT_PREFLIGHT.resolve()) and
             PROJECT_PREFLIGHT.is_file(),
             "T58 prepare_summary 的只读工程预检路径不匹配")
    project_binding, project_sha256 = _read_json(PROJECT_PREFLIGHT)
    current_xpr_sha256 = _project_xpr_sha()
    binding_record = preparation.get("bindings", {}).get(
        "project_preflight_binding")
    _require(isinstance(binding_record, dict),
             "T58 prepare_summary 缺少自身工程预检摘要绑定")
    _require(project_sha256 == project_record.get("sha256") ==
             binding_record.get("sha256") and
             project_record.get("bytes") == binding_record.get("bytes") and
             project_record.get("path") == binding_record.get("path") ==
             str(PROJECT_PREFLIGHT.resolve()) and
             project_binding.get("schema") ==
             "GestureForge-S2A-T58-project-preflight-v2" and
             project_binding.get("task_id") == "S2A-T58" and
             project_binding.get("run_id") == "run02" and
             project_binding.get("baseline_head") == BASE_HEAD and
             project_binding.get("preparation_head") == preparation_head and
             project_binding.get("run_directory") == str(RUN_ROOT.resolve()) and
             project_binding.get("project_xpr_path") == str(XPR_PATH.resolve()) and
             project_binding.get("target_xpr_sha256_before_prepare") ==
             current_xpr_sha256 ==
             project_binding.get("target_xpr_sha256_after_prepare") and
             project_binding.get("target_xpr_unchanged") is True and
             project_record.get("target_xpr_sha256") == current_xpr_sha256 and
             project_record.get("target_xpr_unchanged") is True and
             project_binding.get("preserved_run01") == preserved_run01 and
             project_binding.get("tb_io_paths") == preparation.get("tb_io_paths"),
             "T58 prepare_summary、manifest、本地工程预检与真实 XPR SHA 不一致")
    expected_source_hashes = _source_hashes()
    _require(project_binding.get("T58_source_hashes") == expected_source_hashes ==
             preparation.get("bindings", {}).get("T58_source_hashes"),
             "T58 工程预检绑定的源码哈希与当前文件不一致")
    preparation_inputs = {
        key: preparation.get("bindings", {}).get(key)
        for key in (
            "T56_parent_report", "T56_summary", "G0_specification",
            "T01_manifest", "T23_parameter_table", "GF8_package",
            "weight_layer35", "oracle_source",
        )
    }
    _require(project_binding.get("preparation_inputs") == preparation_inputs,
             "T58 工程预检绑定与 prepare_summary 输入绑定不一致")
    _require(preparation_inputs["T56_parent_report"] == {
                 "path": str(T56_REPORT.resolve()),
                 "sha256": T56_REPORT_SHA256,
             } and
             preparation_inputs["T56_summary"] == {
                 "path": str(T56_SUMMARY.resolve()),
                 "sha256": T56_SUMMARY_SHA256,
             } and
             preparation_inputs["G0_specification"] == {
                 "path": str(G0_PATH.resolve()),
                 "sha256": G0_SHA256,
             } and
             preparation_inputs["T01_manifest"].get("path") ==
                 str(T01_PATH.resolve()) and
             preparation_inputs["T01_manifest"].get("sha256") == T01_SHA256 and
             preparation_inputs["T23_parameter_table"].get("path") ==
                 str(T23_PATH.resolve()) and
             preparation_inputs["T23_parameter_table"].get("sha256") == T23_SHA256 and
             preparation_inputs["GF8_package"].get("sha256") == GF8_SHA256 and
             preparation_inputs["weight_layer35"] ==
                 parent_bindings.get("weight_layer35") and
             preparation_inputs["oracle_source"] == {
                 "path": str(T54_RUNNER.resolve()),
                 "sha256": T54_RUNNER_SHA256,
             },
             "T58 工程预检绑定未指向冻结 G0/T01/T23/GF8/T56/oracle 输入")
    for name in (
        "T56_parent_report", "T56_summary", "G0_specification",
        "T01_manifest", "T23_parameter_table", "GF8_package", "oracle_source",
    ):
        record = preparation_inputs[name]
        _require(isinstance(record, dict), f"T58 输入绑定格式错误：{name}")
        source_path = _verify_file_record(record, f"T58 输入 {name}")
        _require(source_path.is_file(), f"T58 输入文件缺失：{name}")
    _require(project_binding.get("mcp_status") == "NOT_QUERIED" and
             project_binding.get("vivado_opened") is False and
             project_binding.get("vivado_cli_invoked") is False,
             "T58 工程预检不得声称查询 MCP 或打开/启动 Vivado")
    runtime = preparation.get("runtime_preflight", {})
    _require(runtime.get("path_chain_valid") is True and
             runtime.get("target_absent") is True and
             runtime.get("existing_run01") is True and
             runtime.get("existing_run02") is False and
             runtime.get("process_names") == list(PROCESS_NAMES) and
             runtime.get("processes_before_prepare") == [] and
             runtime.get("mcp_status") == "NOT_QUERIED" and
             project_binding.get("runtime_preflight") == runtime and
             current_runtime.get("existing_run02") is True and
             current_runtime.get("target_absent") is False and
             current_runtime.get("processes_before_prepare") == [],
             "T58 prepare_summary 路径/进程/MCP 状态不匹配")
    _require(preparation.get("simulation", {}).get("status") == "NOT_RUN",
             "T58 当前证据不应包含仿真状态")
    expected_files = {
        "prepare_summary.json",
        "project_preflight_binding.json",
        "fixture/feature_input.bin",
        "fixture/layer35_weights.bin",
        "fixture/golden.bin",
        "fixture/vectors.txt",
        "fixture/fixture_manifest.json",
    }
    actual_files = {
        path.relative_to(RUN_ROOT).as_posix()
        for path in RUN_ROOT.rglob("*") if path.is_file()
    }
    _require(actual_files == expected_files,
             f"T58 run02 文件集合不匹配：extra={sorted(actual_files - expected_files)} "
             f"missing={sorted(expected_files - actual_files)}")
    oracle_runner, historical_oracle_head = _load_oracle_runner(current_head)
    inputs = oracle_runner._load_frozen_inputs()
    recomputed = oracle_runner._build_oracle(inputs, progress=False, points=POINTS)
    _require(inputs["weight_sha256"] ==
             preparation_inputs["weight_layer35"]["sha256"] and
             inputs["weight_bytes"] ==
             (FIXTURE_ROOT / "layer35_weights.bin").read_bytes() and
             recomputed["feature"] ==
             (FIXTURE_ROOT / "feature_input.bin").read_bytes() and
             recomputed["combined_golden"] ==
             (FIXTURE_ROOT / "golden.bin").read_bytes() and
             _vectors_bytes(recomputed["vectors"]) ==
             (FIXTURE_ROOT / "vectors.txt").read_bytes() and
             recomputed["oracle"] == preparation.get("oracle") and
             recomputed["expected_counts"] == preparation.get("expected_counts") and
             historical_oracle_head ==
             preparation.get("oracle_source", {}).get("historical_BASE_HEAD") and
             preparation.get("oracle_source", {}).get("runtime_BASE_HEAD") ==
             preparation_head,
             "T58 verify-only 重新计算的独立 oracle 与 run02 fixture 不一致")
    print(json.dumps({
        "result": "PREPARED_NOT_SIMULATED",
        "preparation_head": preparation_head,
        "current_head_at_verify": current_head,
        "prepare_summary_sha256": prepare_sha256,
        "fixture_manifest_sha256": preparation["fixture"]["manifest"]["sha256"],
        "golden_sha256": preparation["oracle"]["combined_golden_sha256"],
        "output_counts": {
            "raw_int32": RAW_COUNT,
            "int8": INT8_COUNT,
            "d2_t23_matches": INT8_COUNT,
        },
        "tb_fopen_count": preparation["tb_io_paths"]["fopen_count"],
        "simulation": "NOT_RUN",
    }, ensure_ascii=False, indent=2))
    return preparation


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--prepare-only", action="store_true")
    mode.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.prepare_only:
            _prepare()
        else:
            _verify_prepared()
        return 0
    except Exception as error:
        print(f"FAIL T58 {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
