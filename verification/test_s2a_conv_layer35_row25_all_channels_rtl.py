#!/usr/bin/env python3
"""为 S2A-T61 准备并独立核验 layer35 y=25 行证据，不启动 Vivado 或 XSim。"""

from __future__ import annotations

import argparse
import ast
import copy
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
BASE_HEAD = "decaef9ceb97befab2ff6d6ba5a72fc822905f58"
TASK_ID = "S2A-T61"
RUN_ID = "run03"
ROW_Y = 25
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
T55_REPORT = ROOT / "report/evidence/S2A-T55/layer35_row19_all_channels.json"
T55_REPORT_SHA256 = "73000657e78b9477d7391391d84d336212a7c42ffe829e5fb2cf760190e97e0f"
T56_REPORT = ROOT / "report/evidence/S2A-T56/layer35_row20_all_channels.json"
T56_REPORT_SHA256 = "44a25b6b5af6f8868dd2cb9780c4834bdd87860ba43a71b0c696c0b67627da12"
T56_RUN_ROOT = ROOT / "report/evidence/S2A-T56/mcp_project_run01"
PUBLIC_INPUT_PATHS = {
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
NEGATIVE_DEPENDENCY_KEYS = (
    "G0_specification", "T01_manifest", "T16_proof",
    "T17_engine_evidence", "T20_scheduler_evidence",
    "T23_parameter_table",
)
NEGATIVE_ERROR_CODE = "PUBLIC_INPUT_SHA256_MISMATCH"

RTL_PATHS = (
    "src/int8_conv_tap_geometry.sv",
    "src/int8_conv_weight_address.sv",
    "src/int8_mac_accumulator.sv",
    "src/s2a_conv_engine.sv",
    "src/s2a_conv_layer35_channel_probe.sv",
)
T54_SOURCE_PATHS = (*RTL_PATHS, T54_TESTBENCH.relative_to(ROOT).as_posix(),
                    T54_RUNNER.relative_to(ROOT).as_posix())
T61_RUNNER_RELATIVE = Path(__file__).resolve().relative_to(ROOT).as_posix()
T61_TESTBENCH_RELATIVE = "sim/tb_s2a_conv_layer35_row25_all_channels.sv"
T61_SOURCE_PATHS = (*RTL_PATHS, T61_TESTBENCH_RELATIVE, T61_RUNNER_RELATIVE)

XPR_PATH = ROOT / "vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr"
EVIDENCE_ROOT = ROOT / "report/evidence/S2A-T61"
RUN01_ROOT = EVIDENCE_ROOT / "run01"
RUN01_PREPARE_REPORT = RUN01_ROOT / "prepare_summary.json"
RUN01_PROJECT_PREFLIGHT = RUN01_ROOT / "project_preflight_binding.json"
RUN01_FIXTURE_ROOT = RUN01_ROOT / "fixture"
RUN01_MAIN_REPORT = EVIDENCE_ROOT / "layer35_row25_all_channels.json"
RUN01_FAILURE_SIDECAR = EVIDENCE_ROOT / "NON_ACCEPTANCE_run01_verify_only.json"
RUN_ROOT = EVIDENCE_ROOT / RUN_ID
FIXTURE_ROOT = RUN_ROOT / "fixture"
NEGATIVE_ROOT = RUN_ROOT / "negative_dependency_tests"
MAIN_REPORT = EVIDENCE_ROOT / "layer35_row25_all_channels_run03.json"
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
$mode = $env:S2A_T61_PREFLIGHT_MODE
if (@('prepare', 'verify') -notcontains $mode) {
    throw 'T61 PowerShell 预检模式无效'
}
$requiredDirectories = @(
    'D:\',
    'D:\FPGA_Competition',
    'D:\FPGA_Competition\report',
    'D:\FPGA_Competition\report\evidence',
    'D:\FPGA_Competition\report\evidence\S2A-T61',
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
$evidenceRoot = 'D:\FPGA_Competition\report\evidence\S2A-T61'
$run01Root = Join-Path $evidenceRoot 'run01'
$run02Root = Join-Path $evidenceRoot 'run02'
$runRoot = Join-Path $evidenceRoot 'run03'
$run02FixtureRoot = Join-Path $run02Root 'fixture'
$run02NegativeRoot = Join-Path $run02Root 'negative_dependency_tests'
$fixtureRoot = Join-Path $runRoot 'fixture'
$negativeRoot = Join-Path $runRoot 'negative_dependency_tests'
$run01MainReport = Join-Path $evidenceRoot 'layer35_row25_all_channels.json'
$run02MainReport = Join-Path $evidenceRoot 'layer35_row25_all_channels_run02.json'
$failureSidecar = Join-Path $evidenceRoot 'NON_ACCEPTANCE_run01_verify_only.json'
$mainReport = Join-Path $evidenceRoot 'layer35_row25_all_channels_run03.json'
$existingEvidence = Get-Item -LiteralPath $evidenceRoot -Force -ErrorAction SilentlyContinue
$rootExists = $null -ne $existingEvidence
$run01Exists = Test-Path -LiteralPath $run01Root
$run02Exists = Test-Path -LiteralPath $run02Root
$run03Exists = Test-Path -LiteralPath $runRoot
if (-not $rootExists -or -not $run01Exists -or -not $run02Exists -or
    -not (Test-Path -LiteralPath $run01MainReport) -or
    -not (Test-Path -LiteralPath $run02MainReport) -or
    -not (Test-Path -LiteralPath $failureSidecar)) {
    throw 'T61 run03 前置 run01/run02 证据缺失或根目录状态错误'
}
foreach ($path in @($run01Root, $run02Root)) {
    $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
    if (-not $item.PSIsContainer -or
        (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "T61 前置证据目录不是普通目录：$path"
    }
}
$expectedRootEntriesBeforeRun03 = @(
    'layer35_row25_all_channels.json',
    'layer35_row25_all_channels_run02.json',
    'NON_ACCEPTANCE_run01_verify_only.json',
    'run01', 'run02'
)
$expectedRootEntriesAfterRun03 = @(
    'layer35_row25_all_channels.json',
    'layer35_row25_all_channels_run02.json',
    'layer35_row25_all_channels_run03.json',
    'NON_ACCEPTANCE_run01_verify_only.json',
    'run01', 'run02', 'run03'
)
$expectedPreviousRunEntries = @(
    'fixture', 'negative_dependency_tests', 'prepare_summary.json',
    'project_preflight_binding.json'
)
$expectedFixtureEntries = @(
    'feature_input.bin', 'fixture_manifest.json', 'golden.bin',
    'layer35_weights.bin', 'vectors.txt'
)
$expectedNegativeEntries = @(
    'case_01.json', 'case_02.json', 'case_03.json',
    'case_04.json', 'case_05.json', 'case_06.json', 'results.json'
)
$actualRootEntries = @(Get-ChildItem -LiteralPath $evidenceRoot -Force |
    ForEach-Object { $_.Name } | Sort-Object)
if ($mode -eq 'prepare') {
    if ($run03Exists -or
        (($actualRootEntries -join '|') -ne
         ($expectedRootEntriesBeforeRun03 -join '|'))) {
        throw 'T61 run03 prepare 目标已存在或前置证据根目录含非预期节点'
    }
}
else {
    if (-not $run03Exists -or
        -not (Test-Path -LiteralPath $fixtureRoot) -or
        -not (Test-Path -LiteralPath $negativeRoot) -or
        -not (Test-Path -LiteralPath $mainReport) -or
        (($actualRootEntries -join '|') -ne
         ($expectedRootEntriesAfterRun03 -join '|'))) {
        throw 'T61 run03 verify-only 所需证据节点或根目录清单错误'
    }
    foreach ($path in @(
        $evidenceRoot, $run01Root, $run02Root, $runRoot,
        $run02FixtureRoot, $run02NegativeRoot, $fixtureRoot, $negativeRoot
    )) {
        $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if (-not $item.PSIsContainer -or
            (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
            throw "T61 证据目录不是普通目录：$path"
        }
    }
    $expectedRunEntries = @(
        'fixture', 'negative_dependency_tests', 'prepare_summary.json',
        'project_preflight_binding.json'
    )
    $actualRunEntries = @(Get-ChildItem -LiteralPath $runRoot -Force |
        ForEach-Object { $_.Name } | Sort-Object)
    if (($actualRunEntries -join '|') -ne ($expectedRunEntries -join '|')) {
        throw 'T61 run03 根目录含非预期节点'
    }
    $actualFixtureEntries = @(Get-ChildItem -LiteralPath $fixtureRoot -Force |
        ForEach-Object { $_.Name } | Sort-Object)
    if (($actualFixtureEntries -join '|') -ne ($expectedFixtureEntries -join '|')) {
        throw 'T61 run03 fixture 含非预期节点'
    }
    $actualNegativeEntries = @(Get-ChildItem -LiteralPath $negativeRoot -Force |
        ForEach-Object { $_.Name } | Sort-Object)
    if (($actualNegativeEntries -join '|') -ne ($expectedNegativeEntries -join '|')) {
        throw 'T61 run03 依赖负向测试目录含非预期节点'
    }
    $mainItem = Get-Item -LiteralPath $mainReport -Force -ErrorAction Stop
    if ($mainItem.PSIsContainer -or $mainItem.Length -le 0 -or
        (($mainItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "T61 run03 主报告不是普通非空文件：$mainReport"
    }
}
$actualPreviousRunEntries = @(Get-ChildItem -LiteralPath $run02Root -Force |
    ForEach-Object { $_.Name } | Sort-Object)
if (($actualPreviousRunEntries -join '|') -ne
    ($expectedPreviousRunEntries -join '|')) {
    throw 'T61 run02 前置证据目录含非预期节点'
}
$actualPreviousFixtureEntries = @(Get-ChildItem -LiteralPath $run02FixtureRoot -Force |
    ForEach-Object { $_.Name } | Sort-Object)
if (($actualPreviousFixtureEntries -join '|') -ne
    ($expectedFixtureEntries -join '|')) {
    throw 'T61 run02 fixture 含非预期节点'
}
$actualPreviousNegativeEntries = @(Get-ChildItem -LiteralPath $run02NegativeRoot -Force |
    ForEach-Object { $_.Name } | Sort-Object)
if (($actualPreviousNegativeEntries -join '|') -ne
    ($expectedNegativeEntries -join '|')) {
    throw 'T61 run02 依赖负向测试目录含非预期节点'
}
foreach ($item in @(Get-ChildItem -LiteralPath $run02Root -Force -Recurse)) {
    if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "T61 run02 子节点不能是 reparse point：$($item.FullName)"
    }
}
foreach ($path in @($run01MainReport, $run02MainReport, $failureSidecar)) {
    $item = Get-Item -LiteralPath $path -Force -ErrorAction Stop
    if ($item.PSIsContainer -or $item.Length -le 0 -or
        (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
        throw "T61 前置报告或 sidecar 不是普通非空文件：$path"
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
    xpr_bytes = [long]$xprItem.Length
    xpr_sha256 = ([System.BitConverter]::ToString(
        [System.Security.Cryptography.SHA256]::Create().ComputeHash(
            [IO.File]::ReadAllBytes($xpr))).Replace('-', '').ToLowerInvariant())
    target_absent = (-not $run03Exists)
    existing_run03 = $run03Exists
    process_names = $names
    processes = $processes
}
[Console]::Out.Write((ConvertTo-Json -InputObject $result -Depth 5 -Compress))
"""


class T61Error(RuntimeError):
    """表示 S2A-T61 冻结输入、工程绑定或准备证据核验失败。"""

    def __init__(self, message: str, *, error_code: str = "T61_VALIDATION_ERROR",
                 dependency_key: str | None = None,
                 dependency_path: str | None = None) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.dependency_key = dependency_key
        self.dependency_path = dependency_path


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T61Error(message)


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


def _verify_baseline(recorded_current_head: str | None = None) -> str:
    """要求任务基线及可选生成基线均为当前 HEAD 祖先。"""
    current = _current_head()
    ancestors = [BASE_HEAD]
    if recorded_current_head is not None:
        _require(re.fullmatch(r"[0-9a-f]{40}", recorded_current_head) is not None,
                 "摘要中的生成 HEAD 不是完整提交 SHA")
        ancestors.append(recorded_current_head.lower())
    for ancestor in ancestors:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "merge-base", "--is-ancestor",
             ancestor, current],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            errors="replace", check=False, timeout=15,
        )
        _require(result.returncode == 0,
                 f"冻结提交不是当前 HEAD 祖先：{ancestor}; {result.stderr.strip()}")
    return current


def _load_prior_run01_failure() -> dict[str, Any]:
    """验证并绑定未修改的 run01 失败记录，供 run03 追溯。"""
    sidecar, sidecar_sha = _read_json(RUN01_FAILURE_SIDECAR)
    _require(sidecar.get("schema") ==
             "GestureForge-S2A-T61-non-acceptance-v1" and
             sidecar.get("task_id") == TASK_ID and
             sidecar.get("attempt_id") == "T61-run01-verify-only" and
             sidecar.get("status") == "NON_ACCEPTANCE" and
             sidecar.get("command") ==
             "python verification/test_s2a_conv_layer35_row25_all_channels_rtl.py --verify-only" and
             sidecar.get("exit_code") == 1 and
             sidecar.get("failure", {}).get("location") ==
             "_verify_negative_dependency_tests" and
             sidecar.get("failure", {}).get("expression") ==
             "results.get('cases') == expected_result_cases" and
             sidecar.get("failure", {}).get("classification") ==
             "checker_type_mismatch" and
             sidecar.get("failure", {}).get("evidence_data_defect") is False and
             sidecar.get("cpu_oracle_checkpoints") ==
             [832, 1664, 2496, 3328, 4160, 4992, 5824, 6656],
             "T61 run01 失败侧件身份、失败分类或 CPU 检查点不正确")
    expected_relative_paths = {
        "run01/project_preflight_binding.json",
        "run01/prepare_summary.json",
        "run01/fixture/feature_input.bin",
        "run01/fixture/layer35_weights.bin",
        "run01/fixture/golden.bin",
        "run01/fixture/vectors.txt",
        "run01/fixture/fixture_manifest.json",
        *(f"run01/negative_dependency_tests/case_{index:02d}.json"
          for index in range(1, 7)),
        "run01/negative_dependency_tests/results.json",
    }
    records = sidecar.get("preserved_run01_artifacts", [])
    _require(isinstance(records, list) and
             {record.get("relative_path") for record in records
              if isinstance(record, dict)} == expected_relative_paths and
             len(records) == len(expected_relative_paths),
             "T61 run01 失败前证据清单不完整或重复")
    record_by_relative: dict[str, dict[str, Any]] = {}
    for record in records:
        relative = record["relative_path"]
        expected_path = EVIDENCE_ROOT / Path(relative)
        _verify_file_record(record, expected_path, f"T61 run01 preserved {relative}")
        record_by_relative[relative] = record
    main_record = sidecar.get("preserved_run01_main_report", {})
    _verify_file_record(main_record, RUN01_MAIN_REPORT,
                        "T61 run01 preserved main report")
    _require(
             sidecar.get("run01_prepare_summary") ==
             record_by_relative["run01/prepare_summary.json"] and
             sidecar.get("run01_project_preflight") ==
             record_by_relative["run01/project_preflight_binding.json"] and
             sidecar.get("run01_fixture_manifest") ==
             record_by_relative["run01/fixture/fixture_manifest.json"],
             "T61 run01 失败侧件与原始摘要交叉引用不匹配")
    summary, summary_sha = _read_json(RUN01_PREPARE_REPORT)
    binding, binding_sha = _read_json(RUN01_PROJECT_PREFLIGHT)
    manifest, manifest_sha = _read_json(RUN01_FIXTURE_ROOT / "fixture_manifest.json")
    runner_relative = "verification/test_s2a_conv_layer35_row25_all_channels_rtl.py"
    testbench_relative = "sim/tb_s2a_conv_layer35_row25_all_channels.sv"
    source_hashes = summary.get("bindings", {}).get("T61_source_hashes", {})
    _require(summary_sha == record_by_relative["run01/prepare_summary.json"]["sha256"] and
             binding_sha == record_by_relative["run01/project_preflight_binding.json"]["sha256"] and
             manifest_sha == record_by_relative["run01/fixture/fixture_manifest.json"]["sha256"] and
             summary.get("task_id") == TASK_ID and
             summary.get("run_id") == "run01" and
             summary.get("status") == "PREPARED_NOT_SIMULATED" and
             summary.get("simulation", {}).get("status") == "NOT_RUN" and
             sidecar.get("runner_sha256_at_attempt") == source_hashes.get(runner_relative) and
             sidecar.get("testbench_sha256_at_attempt") == source_hashes.get(testbench_relative) and
             binding.get("T61_source_hashes") == source_hashes and
             manifest.get("T61_source_hashes") == source_hashes,
             "T61 run01 原始 prepare、工程绑定、fixture manifest 或源码 SHA 不匹配")
    main_report, main_report_sha = _read_json(RUN01_MAIN_REPORT)
    prepare_record = record_by_relative["run01/prepare_summary.json"]
    prepare_artifact = {key: prepare_record[key]
                        for key in ("path", "bytes", "sha256")}
    _require(main_report_sha == main_record.get("sha256") and
             main_report.get("task_id") == TASK_ID and
             main_report.get("status") == "PREPARED_NOT_SIMULATED" and
             main_report.get("baseline_head") == summary.get("baseline_head") and
             main_report.get("prepare_summary") == prepare_artifact and
             main_report.get("source_hashes") == source_hashes,
             "T61 run01 原始主报告与 prepare summary 不一致")
    return {
        "attempt_id": sidecar["attempt_id"],
        "status": sidecar["status"],
        "exit_code": sidecar["exit_code"],
        "failure_sidecar": {
            "path": str(RUN01_FAILURE_SIDECAR.resolve()),
            "bytes": RUN01_FAILURE_SIDECAR.stat().st_size,
            "sha256": sidecar_sha,
        },
        "runner_sha256_at_attempt": sidecar["runner_sha256_at_attempt"],
        "testbench_sha256_at_attempt": sidecar["testbench_sha256_at_attempt"],
        "run01_artifacts": records,
    }


def _source_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for relative in T61_SOURCE_PATHS:
        path = ROOT / relative
        _require(path.is_file(), f"T61 源码缺失：{relative}")
        hashes[relative] = _sha_file(path)
    return hashes


def _source_configuration_check() -> dict[str, Any]:
    """以 Python AST 和文本规则确认本 runner 仅支持准备/核验。"""
    runner_path = Path(__file__).resolve()
    runner_bytes = runner_path.read_bytes()
    _require(not runner_bytes.startswith(b"\xef\xbb\xbf") and
             b"\r" not in runner_bytes and runner_bytes.endswith(b"\n"),
             "T61 runner 必须是 UTF-8 无 BOM、LF 且以换行结尾")
    runner_text = runner_bytes.decode("utf-8")
    tree = ast.parse(runner_text, filename=str(runner_path))
    tb_path = ROOT / T61_TESTBENCH_RELATIVE
    tb_bytes = tb_path.read_bytes()
    _require(not tb_bytes.startswith(b"\xef\xbb\xbf") and
             b"\r" not in tb_bytes and tb_bytes.endswith(b"\n"),
             "T61 testbench 必须是 UTF-8 无 BOM、LF 且以换行结尾")
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
             f"T61 CLI 选项超出准备态范围：{mode_options}")
    subprocess_commands = []
    forbidden_process_apis = {
        "Popen", "call", "check_call", "check_output", "system", "startfile",
    }
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Attribute) and function.attr in forbidden_process_apis:
            raise T61Error(f"T61 runner 含未经批准的进程启动 API：{function.attr}")
        if (isinstance(function, ast.Attribute) and
                isinstance(function.value, ast.Name) and
                function.value.id == "subprocess"):
            _require(function.attr == "run" and node.args and
                     isinstance(node.args[0], ast.List) and
                     node.args[0].elts and
                     isinstance(node.args[0].elts[0], ast.Constant),
                     "T61 runner subprocess 命令必须是静态字面量")
            subprocess_commands.append(node.args[0].elts[0].value)
    _require(sorted(subprocess_commands) ==
             ["git", "git", "powershell.exe", "powershell.exe"],
             f"T61 runner 外部命令超出 git/只读 PowerShell：{subprocess_commands}")
    forbidden_powershell = (
        "start-process", "invoke-expression", "start-job", "remove-item",
        "set-content", "new-item", "move-item", "stop-process",
    )
    powershell_lower = POWERSHELL_PREFLIGHT.lower()
    _require(not any(token in powershell_lower for token in forbidden_powershell) and
             ".tcl" not in powershell_lower,
             "T61 内嵌 PowerShell 存在进程启动、文件写入或 Tcl 操作")
    _require("subprocess.run(" in runner_text and
             "powershell.exe" in runner_text and
             "Get-CimInstance -ClassName Win32_Process" in POWERSHELL_PREFLIGHT and
             "Get-Item -LiteralPath" in POWERSHELL_PREFLIGHT and
             "Get-ChildItem -LiteralPath" in POWERSHELL_PREFLIGHT,
             "T61 内嵌 PowerShell 只读路径/进程检查不完整")
    for name in PROCESS_NAMES:
        _require(f"'{name}'" in POWERSHELL_PREFLIGHT,
                 f"T61 PowerShell 进程名单缺失：{name}")
    powershell_ast = _powershell_ast_check()
    _require("values[1]},{values[0]},{values[3]},{values[2]" in runner_text,
             "T61 参数摘要顺序不是 Q+,M+,Q-,M-")
    _require("module tb_s2a_conv_layer35_row25_all_channels;" in tb_text and
             "vector_y[initial_index] != 25" in tb_text and
             tb_text.count("output_y == 25") == 2 and
             "PASS T61 outputs=%0d raw=%0d" in tb_text and
             "PROGRESS T61 outputs=%0d/%0d" in tb_text and
             "S2A-T58" not in tb_text and "row24" not in tb_text and
             "y=24" not in tb_text and ".tcl" not in tb_text.lower(),
             "T61 testbench 模块名、坐标、摘要或范围静态检查不匹配")
    for path_string in (
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T61\\run03\\fixture\\feature_input.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T61\\run03\\fixture\\layer35_weights.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T61\\run03\\fixture\\golden.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T61\\run03\\fixture\\vectors.txt",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T61\\run03\\observed_raw.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T61\\run03\\observed_output.bin",
    ):
        _require(path_string in tb_text, f"T61 testbench fixture 路径缺失：{path_string}")
    return {
        "python_ast": "PASS",
        "cli_modes": mode_options,
        "runner_no_xilinx_launch_or_tcl": True,
        "powershell_read_only_path_and_process_scan": "PASS",
        "powershell_ast": powershell_ast,
        "parameter_digest_order": "Q+,M+,Q-,M-",
        "testbench_top_row_and_fixture_paths": "PASS",
        "runner_sha256": _sha256(runner_bytes),
        "testbench_sha256": _sha256(tb_bytes),
        "powershell_source_sha256": _sha256(POWERSHELL_PREFLIGHT.encode("utf-8")),
    }


def _powershell_ast_check() -> str:
    """使用 PowerShell 解析器仅解析内嵌脚本文本，不执行该脚本。"""
    env = os.environ.copy()
    env["S2A_T61_PS_SOURCE"] = POWERSHELL_PREFLIGHT
    command = (
        "$tokens=$null;$errors=$null;"
        "[System.Management.Automation.Language.Parser]::ParseInput("
        "$env:S2A_T61_PS_SOURCE,[ref]$tokens,[ref]$errors)|Out-Null;"
        "if($errors.Count -gt 0){$errors|ForEach-Object{"
        "[Console]::Error.WriteLine($_.Message)};exit 1};"
        "[Console]::Out.Write('PASS')"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
        cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False, timeout=30,
    )
    _require(result.returncode == 0 and result.stdout.strip() == "PASS",
             f"T61 PowerShell AST 解析失败(exit={result.returncode})："
             f"{result.stderr.strip()}")
    return "PASS"


def _runtime_preflight(mode: str) -> dict[str, Any]:
    _require(mode in ("prepare", "verify"), f"T61 PowerShell 模式无效：{mode}")
    env = os.environ.copy()
    env["S2A_T61_PREFLIGHT_MODE"] = mode
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
        raise T61Error(f"PowerShell 预检输出不是 JSON：{error}") from error
    _require(isinstance(snapshot, dict) and
             snapshot.get("mode") == mode and
             snapshot.get("path_chain_valid") is True and
             snapshot.get("checked_xpr") == str(XPR_PATH.resolve()) and
             tuple(snapshot.get("process_names", ())) == PROCESS_NAMES and
             snapshot.get("processes") == [] and
             snapshot.get("xpr_bytes") == XPR_PATH.stat().st_size and
             snapshot.get("xpr_sha256") == _sha_file(XPR_PATH),
             "T61 路径、XPR 或 8 类 Vivado/XSim 进程检查失败")
    if mode == "prepare":
        _require(snapshot.get("target_absent") is True and
             snapshot.get("existing_run03") is False,
                 "T61 run03 prepare 目标已存在，拒绝覆盖")
    else:
        _require(snapshot.get("target_absent") is False and
             snapshot.get("existing_run03") is True,
                 "T61 verify-only 证据路径绑定不匹配")
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
    if _sha256(data) != record["sha256"].lower():
        raise T61Error(
            f"T54 公开输入 SHA-256 不符：{key}",
            error_code=NEGATIVE_ERROR_CODE,
            dependency_key=key,
            dependency_path=str(path.resolve()),
        )
    if "bytes" in record:
        _require(len(data) == record["bytes"],
                 f"T54 公开输入字节数不符：{key}")
    return record, data


def _load_frozen_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """只从公开 G0/T01/T23/GF8 输入构造 oracle，不访问其他任务 TEMP。"""
    _verify_baseline()
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

    expected_inputs = PUBLIC_INPUT_PATHS
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




def _load_t56_parent(expected_t54: dict[str, Any]) -> dict[str, Any]:
    """核验 T56 row20 父证据、T55/T54 祖先、源码和实际仿真工件。"""
    report, report_sha = _read_json(T56_REPORT)
    _require(report_sha == T56_REPORT_SHA256 and
             report.get("schema") ==
             "GestureForge-S2A-T56-layer35-row20-simulation-data-v1" and
             report.get("task_id") == "S2A-T56" and
             report.get("status") == "PASS_SIMULATION_DATA_ONLY" and
             report.get("acceptance_status") ==
             "PASS_INDEPENDENT_REVIEW_DATA_ONLY" and
             report.get("scope") ==
             "tiny416 cfg section36 layer35; all 256 output channels at y=20, x=0..25; not full layer or network",
             "T56 row20 父报告状态、范围或 SHA-256 不符")
    bindings = report.get("bindings", {})
    fixed_points = [[20, x] for x in range(OUTPUT_SIZE)]
    _require(bindings.get("fixed_points_yx") == fixed_points,
             "T56 固定行坐标不是 y=20")
    t54_record = bindings.get("T54_parent_report", {})
    _require(t54_record.get("path") == str(T54_REPORT.resolve()) and
             t54_record.get("sha256") == expected_t54["sha256"] and
             t54_record.get("acceptance_status") ==
             "PASS_INDEPENDENT_REVIEW_DATA_ONLY",
             "T56 到 T54 的父链绑定不匹配")

    t55, t55_sha = _read_json(T55_REPORT)
    t55_record = bindings.get("T55_parent_report", {})
    _require(t55_sha == T55_REPORT_SHA256 and
             t55_record.get("path") == str(T55_REPORT.resolve()) and
             t55_record.get("sha256") == t55_sha and
             t55_record.get("acceptance_status") ==
             "PASS_INDEPENDENT_REVIEW_DATA_ONLY" and
             t55.get("status") == "PASS_SIMULATION_DATA_ONLY" and
             t55.get("acceptance_status") ==
             "PASS_INDEPENDENT_REVIEW_DATA_ONLY" and
             t55.get("scope") ==
             "tiny416 cfg section36 layer35; all 256 output channels at y=19, x=0..25; not full layer or network" and
             t55.get("bindings", {}).get("fixed_points_yx") ==
             [[19, x] for x in range(OUTPUT_SIZE)],
             "T56 到 T55 的父链或 row19 证据不匹配")
    t55_t54 = t55.get("bindings", {}).get("T54_parent_report", {})
    _require(t55_t54.get("path") == str(T54_REPORT.resolve()) and
             t55_t54.get("sha256") == expected_t54["sha256"],
             "T55 到 T54 的递归父链不匹配")

    expected_t56_sources = {
        *RTL_PATHS,
        "sim/tb_s2a_conv_layer35_row20_all_channels.sv",
        "sim/s2a_t56_no_wave.tcl",
        "verification/test_s2a_conv_layer35_row20_all_channels_rtl.py",
    }
    source_hashes = bindings.get("T56_source_hashes", {})
    _require(set(source_hashes) == expected_t56_sources,
             "T56 源码绑定集合不匹配")
    for relative, expected in source_hashes.items():
        source = ROOT / relative
        _require(source.is_file() and _sha_file(source) == str(expected).lower(),
                 f"T56 源码 SHA-256 不匹配：{relative}")

    oracle = report.get("oracle", {})
    simulation = report.get("simulation", {})
    _require(oracle.get("raw_int32_count") == RAW_COUNT and
             oracle.get("quantized_int8_count") == INT8_COUNT and
             oracle.get("d2_t23_match_count") == INT8_COUNT and
             simulation.get("status") == "PASS_SIMULATION_DATA_ONLY" and
             simulation.get("raw_int32_compares") == RAW_COUNT and
             simulation.get("int8_compares") == INT8_COUNT and
             simulation.get("raw_mismatch_bytes") == 0 and
             simulation.get("int8_mismatch_bytes") == 0 and
             simulation.get("raw_byte_identical_to_independent_golden") is True and
             simulation.get("int8_byte_identical_to_independent_golden") is True and
             simulation.get("progress_checkpoint_count") == OUTPUT_CHANNELS and
             simulation.get("progress_first_output_count") == OUTPUT_SIZE and
             simulation.get("progress_last_output_count") == RAW_COUNT and
             simulation.get("finish_observed") is True,
             "T56 oracle 或实际运行逐值证据不完整")
    artifacts = simulation.get("artifacts", {})
    required_artifacts = {
        "compile.log", "elaborate.log", "simulate.log", "observed_raw.bin",
        "observed_output.bin", "elaborate.bat", "simulate.bat",
        "tb_s2a_conv_layer35_row20_all_channels.tcl",
    }
    _require(set(artifacts) == required_artifacts,
             "T56 运行工件集合不匹配")
    artifact_records: dict[str, dict[str, Any]] = {}
    for name, record in artifacts.items():
        expected_path = T56_RUN_ROOT / name
        _verify_file_record(record, expected_path, f"T56 工件 {name}")
        artifact_records[name] = _artifact(expected_path)
    _require(artifacts["observed_raw.bin"]["bytes"] == RAW_BYTES and
             artifacts["observed_raw.bin"]["sha256"] ==
             oracle.get("raw_int32_le_sha256") and
             artifacts["observed_output.bin"]["bytes"] == INT8_BYTES and
             artifacts["observed_output.bin"]["sha256"] ==
             oracle.get("quantized_int8_sha256"),
             "T56 实际 raw/INT8 工件大小或摘要与独立 oracle 不匹配")
    mcp_run = bindings.get("mcp_project_run01", {})
    _require(mcp_run.get("artifact_directory") == str(T56_RUN_ROOT.resolve()) and
             mcp_run.get("artifact_files") == artifacts,
             "T56 运行目录绑定与仿真工件表不匹配")
    process_path = Path(mcp_run.get("process_check_path", ""))
    _require(process_path == ROOT / "report/evidence/S2A-T56/process_check_before_xsim.json" and
             process_path.is_file() and
             _sha_file(process_path) == mcp_run.get("process_check_sha256"),
             "T56 启动前进程快照路径或 SHA-256 不匹配")
    process_snapshot, _ = _read_json(process_path)
    historical_processes = process_snapshot.get("processes", [])
    _require(process_snapshot.get("status") == "PASS_NO_XSIM" and
             process_snapshot.get("query_success") is True and
             process_snapshot.get("invocation", {}).get("exit_code") == 0 and
             process_snapshot.get("xsim_process_count") == 0 and
             process_snapshot.get("process_names") == [
                 "vivado", "vivado_lab", "xsct", "xsim",
                 "xsimk", "xelab", "xvlog", "xvhdl",
             ] and isinstance(historical_processes, list) and
             all(isinstance(process, dict) for process in historical_processes) and
             not any(str(process.get("Name", "")).lower() in
                     {"xsim.exe", "xsimk.exe"} for process in historical_processes),
             "T56 历史启动前快照不完整或记有 XSim 进程")
    simulation_summary_path = Path(mcp_run.get("summary_path", ""))
    _require(simulation_summary_path == T56_RUN_ROOT / "simulation_summary.json" and
             simulation_summary_path.is_file() and
             _sha_file(simulation_summary_path) == mcp_run.get("summary_sha256"),
             "T56 仿真摘要实际文件路径或 SHA-256 不匹配")
    simulation_summary, _ = _read_json(simulation_summary_path)
    simulation_result = simulation_summary.get("simulation_result", {})
    _require(simulation_result.get("status") == "PASS" and
             simulation_result.get("raw_int32_compares") == RAW_COUNT and
             simulation_result.get("int8_compares") == INT8_COUNT and
             simulation_result.get("byte_difference_count_raw") == 0 and
             simulation_result.get("byte_difference_count_int8") == 0,
             "T56 仿真摘要与父报告不一致")

    return {
        "path": str(T56_REPORT.resolve()),
        "bytes": T56_REPORT.stat().st_size,
        "sha256": report_sha,
        "status": report["status"],
        "acceptance_status": report["acceptance_status"],
        "scope": report["scope"],
        "fixed_points_yx": fixed_points,
        "T55_parent_report": {
            "path": str(T55_REPORT.resolve()),
            "bytes": T55_REPORT.stat().st_size,
            "sha256": t55_sha,
            "acceptance_status": t55["acceptance_status"],
        },
        "T54_parent_report": expected_t54,
        "T56_source_hashes": source_hashes,
        "raw_int32_le_sha256": oracle["raw_int32_le_sha256"],
        "quantized_int8_sha256": oracle["quantized_int8_sha256"],
        "simulation_artifacts": artifact_records,
        "simulation_summary": _artifact(simulation_summary_path),
        "process_check": _artifact(process_path),
        "rpc_status": simulation.get("rpc_status"),
        "rpc_timeout_seconds": simulation.get("rpc_timeout_seconds"),
    }


def _load_all_frozen_inputs() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """合并冻结 T54 oracle 与 T56 父行证据。"""
    parent, inputs, preparation_inputs = _load_frozen_inputs()
    t56 = _load_t56_parent(preparation_inputs["T54_parent_report"])
    preparation_inputs["T56_parent_report"] = t56
    preparation_inputs["T56_source_hashes"] = t56["T56_source_hashes"]
    preparation_inputs["requant_parameter_order"] = "Q+,M+,Q-,M-"
    return parent, inputs, preparation_inputs


def _tampered_sha256(value: str) -> str:
    _require(re.fullmatch(r"[0-9a-f]{64}", value) is not None,
             "负向测试输入不是 SHA-256")
    return ("0" if value[0] != "0" else "1") + value[1:]


def _write_negative_dependency_tests(preparation_inputs: dict[str, Any]) -> dict[str, Any]:
    """在独立 JSON 副本中篡改六项依赖摘要，并核对被拒绝的真实源路径。"""
    NEGATIVE_ROOT.mkdir(parents=False, exist_ok=False)
    source_records = {
        key: copy.deepcopy(preparation_inputs[key])
        for key in NEGATIVE_DEPENDENCY_KEYS
    }
    cases: list[dict[str, Any]] = []
    result_cases: list[dict[str, Any]] = []
    for index, key in enumerate(NEGATIVE_DEPENDENCY_KEYS, start=1):
        records = copy.deepcopy(source_records)
        expected_sha = records[key]["sha256"]
        expected_dependency_path = str(PUBLIC_INPUT_PATHS[key].resolve())
        isolated_dependency_path = records[key].get("path")
        _require(isolated_dependency_path == expected_dependency_path,
                 f"负向副本目标 dependency_path 与冻结路径不符：{key}")
        tampered_sha = _tampered_sha256(expected_sha)
        records[key]["sha256"] = tampered_sha
        error = None
        error_code = None
        rejected_dependency_key = None
        rejected_dependency_path = None
        try:
            _load_binding_record({"bindings": records}, key, PUBLIC_INPUT_PATHS[key])
        except T61Error as failure:
            error = f"{type(failure).__name__}: {failure}"
            error_code = failure.error_code
            rejected_dependency_key = failure.dependency_key
            rejected_dependency_path = failure.dependency_path
        _require(error is not None and
                 error_code == NEGATIVE_ERROR_CODE and
                 rejected_dependency_key == key and
                 rejected_dependency_path == expected_dependency_path,
                 f"依赖篡改未在预期路径以正确错误码和依赖键拒绝：{key}")
        isolated_copy = {
            "dependency_key": key,
            "dependency_path": isolated_dependency_path,
            "bindings": records,
        }
        case = {
            "schema": "GestureForge-S2A-T61-dependency-tamper-case-v1",
            "case_id": index,
            "dependency_key": key,
            "expected_dependency_path": expected_dependency_path,
            "observed_dependency_path": rejected_dependency_path,
            "isolated_dependency_path": isolated_dependency_path,
            "expected_sha256": expected_sha,
            "tampered_sha256": tampered_sha,
            "expected_error_code": NEGATIVE_ERROR_CODE,
            "observed_error_code": error_code,
            "observed_dependency_key": rejected_dependency_key,
            "isolated_binding_copy": isolated_copy,
            "rejection_observed": True,
            "rejection": error,
        }
        case_path = NEGATIVE_ROOT / f"case_{index:02d}.json"
        _write_json_exclusive(case_path, case)
        record = _artifact(case_path)
        cases.append(record)
        result_cases.append({
            "case_id": index,
            "dependency_key": key,
            "expected_dependency_path": expected_dependency_path,
            "observed_dependency_path": rejected_dependency_path,
            "isolated_dependency_path": isolated_dependency_path,
            "expected_error_code": NEGATIVE_ERROR_CODE,
            "observed_error_code": error_code,
            "observed_dependency_key": rejected_dependency_key,
            "rejection_observed": True,
            "case_file": record,
        })
    result_value = {
        "schema": "GestureForge-S2A-T61-dependency-tamper-results-v1",
        "status": "PASS_SIX_EXPECTED_REJECTIONS",
        "case_count": len(cases),
        "rejected_count": len(result_cases),
        "cases": result_cases,
    }
    result_path = NEGATIVE_ROOT / "results.json"
    _write_json_exclusive(result_path, result_value)
    return {
        "status": result_value["status"],
        "case_count": len(cases),
        "rejected_count": len(result_cases),
        "cases": cases,
        "results": _artifact(result_path),
    }


def _verify_negative_dependency_tests(summary: dict[str, Any]) -> int:
    """重读并重放六个隔离副本，核验错误码、依赖键和绝对源路径。"""
    metadata = summary.get("negative_dependency_tests", {})
    cases = metadata.get("cases", [])
    _require(metadata.get("status") == "PASS_SIX_EXPECTED_REJECTIONS" and
             metadata.get("case_count") == 6 and
             metadata.get("rejected_count") == 6 and len(cases) == 6,
             "T61 六项依赖篡改测试的报告计数错误")
    canonical_records = {
        key: summary.get("bindings", {}).get(key)
        for key in NEGATIVE_DEPENDENCY_KEYS
    }
    expected_result_cases = []
    for index, key in enumerate(NEGATIVE_DEPENDENCY_KEYS, start=1):
        case_path = NEGATIVE_ROOT / f"case_{index:02d}.json"
        case_record = _verify_file_record(
            cases[index - 1], case_path, f"T61 依赖篡改副本 {index}")
        case, _ = _read_json(case_record)
        expected_sha = canonical_records[key].get("sha256")
        expected_dependency_path = str(PUBLIC_INPUT_PATHS[key].resolve())
        tampered_sha = _tampered_sha256(expected_sha)
        isolated = copy.deepcopy(canonical_records)
        isolated[key]["sha256"] = tampered_sha
        isolated_dependency_path = isolated[key].get("path")
        isolated_copy = case.get("isolated_binding_copy", {})
        _require(isolated_dependency_path == expected_dependency_path and
                 canonical_records[key].get("path") == expected_dependency_path and
                 case.get("schema") ==
                 "GestureForge-S2A-T61-dependency-tamper-case-v1" and
                 case.get("case_id") == index and
                 case.get("dependency_key") == key and
                 case.get("expected_dependency_path") == expected_dependency_path and
                 case.get("observed_dependency_path") == expected_dependency_path and
                 case.get("isolated_dependency_path") == expected_dependency_path and
                 case.get("expected_sha256") == expected_sha and
                 case.get("tampered_sha256") == tampered_sha and
                 case.get("expected_error_code") == NEGATIVE_ERROR_CODE and
                 case.get("observed_error_code") == NEGATIVE_ERROR_CODE and
                 case.get("observed_dependency_key") == key and
                 isinstance(isolated_copy, dict) and
                 isolated_copy.get("dependency_key") == key and
                 isolated_copy.get("dependency_path") == expected_dependency_path and
                 isolated_copy.get("bindings") == isolated and
                 case.get("rejection_observed") is True and
                 isinstance(case.get("rejection"), str) and case["rejection"],
                 f"T61 依赖篡改副本路径、字段或变更范围错误：{key}")
        try:
            _load_binding_record({"bindings": isolated}, key, PUBLIC_INPUT_PATHS[key])
        except T61Error as failure:
            _require(failure.error_code == NEGATIVE_ERROR_CODE and
                     failure.dependency_key == key and
                     failure.dependency_path == expected_dependency_path,
                     f"T61 依赖篡改错误码、依赖键或路径不匹配：{key}")
        else:
            raise T61Error(f"依赖篡改副本未被拒绝：{key}")
        expected_result_cases.append(
            (index, key, expected_dependency_path, case_record))
    results_record = _verify_file_record(
        metadata.get("results", {}), NEGATIVE_ROOT / "results.json",
        "T61 依赖篡改汇总")
    results, _ = _read_json(results_record)
    _require(results.get("schema") ==
             "GestureForge-S2A-T61-dependency-tamper-results-v1" and
             results.get("status") == "PASS_SIX_EXPECTED_REJECTIONS" and
             results.get("case_count") == 6 and
             results.get("rejected_count") == 6 and
             isinstance(results.get("cases"), list) and
             len(results["cases"]) == len(expected_result_cases),
             "T61 六项依赖篡改汇总不匹配")
    for (index, key, expected_path, case_path), actual_case in zip(
            expected_result_cases, results["cases"]):
        expected_file = _artifact(case_path)
        actual_file = actual_case.get("case_file", {}) if isinstance(
            actual_case, dict) else {}
        _require(isinstance(actual_case, dict) and
                 actual_case.get("case_id") == index and
                 actual_case.get("dependency_key") == key and
                 actual_case.get("expected_dependency_path") == expected_path and
                 actual_case.get("observed_dependency_path") == expected_path and
                 actual_case.get("isolated_dependency_path") == expected_path and
                 actual_case.get("expected_error_code") == NEGATIVE_ERROR_CODE and
                 actual_case.get("observed_error_code") == NEGATIVE_ERROR_CODE and
                 actual_case.get("observed_dependency_key") == key and
                 actual_case.get("rejection_observed") is True and
                 isinstance(actual_file, dict) and
                 actual_file.get("path") == expected_file["path"] and
                 actual_file.get("bytes") == expected_file["bytes"] and
                 actual_file.get("sha256") == expected_file["sha256"],
                 f"T61 负向汇总字段、路径或 case artifact 不匹配：{key}")
    return 6


def _build_main_report(summary: dict[str, Any]) -> dict[str, Any]:
    """构造仅记录 CPU 准备状态的 T61 证据索引。"""
    return {
        "schema": "GestureForge-S2A-T61-row25-prepare-only-v1",
        "task_id": TASK_ID,
        "run_id": summary["run_id"],
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": summary["baseline_head"],
        "current_head": summary["current_head"],
        "current_head_after_prepare": summary["current_head_after_prepare"],
        "scope": summary["scope"],
        "parameter_digest_order": summary["parameter_digest_order"],
        "prepare_summary": _artifact(PREPARE_REPORT),
        "project_preflight_binding": _artifact(PROJECT_PREFLIGHT),
        "fixture_manifest": _artifact(FIXTURE_MANIFEST),
        "source_hashes": summary["bindings"]["T61_source_hashes"],
        "bindings": summary["bindings"],
        "previous_attempt": summary["previous_attempt"],
        "fixture": summary["fixture"],
        "oracle": summary["oracle"],
        "expected_counts": summary["expected_counts"],
        "negative_dependency_tests": summary["negative_dependency_tests"],
        "runtime_preflight": summary["runtime_preflight"],
        "static_checks": summary["static_checks"],
        "simulation": summary["simulation"],
        "review": summary["review"],
        "limitations": summary["limitations"],
        "completed_utc8": summary["completed_utc8"],
    }


def _load_t54_oracle_module() -> Any:
    """加载并绑定 T54 冻结 oracle 的纯计算函数，不执行其任务 runner。"""
    _require(T54_RUNNER.is_file() and _sha_file(T54_RUNNER) == T54_RUNNER_SHA256,
             "T54 oracle 源码缺失或 SHA-256 不匹配")
    spec = importlib.util.spec_from_file_location("s2a_t54_frozen_oracle_for_t61",
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
             "T61 T54 oracle 输出长度或比较计数不正确")
    _require(result["oracle"]["raw_int32_count"] == RAW_COUNT and
             result["oracle"]["quantized_int8_count"] == INT8_COUNT and
             result["oracle"]["d2_t23_match_count"] == INT8_COUNT and
             result["expected_counts"]["output_cases"] == RAW_COUNT and
             result["expected_counts"]["raw_int32_compares"] == RAW_COUNT and
             result["expected_counts"]["quantized_int8_compares"] == INT8_COUNT and
             tuple(POINTS) == tuple((ROW_Y, x) for x in range(OUTPUT_SIZE)) and
             result["oracle"]["padding_taps"] ==
             OUTPUT_CHANNELS * INPUT_CHANNELS * 82 and
             result["oracle"]["valid_taps"] ==
             OUTPUT_CHANNELS * INPUT_CHANNELS * 26 * 9 -
             OUTPUT_CHANNELS * INPUT_CHANNELS * 82,
             "T61 y=25 点集、底边 padding 或 raw/INT8/D2 逐值计数错误")
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
    current_head = _verify_baseline()
    static_checks = _source_configuration_check()
    previous_attempt = _load_prior_run01_failure()
    runtime_before = _runtime_preflight("prepare")
    xpr_sha_before = _sha_file(XPR_PATH)
    parent, inputs, preparation_inputs = _load_all_frozen_inputs()
    oracle = _build_oracle(inputs, progress=True)
    source_hashes = _source_hashes()
    _require(static_checks["runner_sha256"] ==
             source_hashes[T61_RUNNER_RELATIVE] and
             static_checks["testbench_sha256"] ==
             source_hashes[T61_TESTBENCH_RELATIVE],
             "T61 源文件在静态检查后发生变化")
    runtime_final = _runtime_preflight("prepare")
    current_head_after_prepare = _verify_baseline(current_head)
    _require(_sha_file(XPR_PATH) == xpr_sha_before and
             _source_hashes() == source_hashes,
             "T61 准备期间 XPR 或绑定源码发生变化")

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
             "T61 fixture 字节数或向量行数不正确")
    RUN_ROOT.mkdir(parents=False, exist_ok=False)
    FIXTURE_ROOT.mkdir(parents=False, exist_ok=False)
    for name, content in blobs.items():
        _write_bytes_exclusive(FIXTURE_ROOT / name, content)
    xpr_sha_after = _sha_file(XPR_PATH)
    _require(xpr_sha_after == xpr_sha_before,
             "T61 prepare 期间目标 XPR SHA-256 发生变化")
    fixture_files = {name: _artifact(FIXTURE_ROOT / name)
                     for name in sorted(blobs)}
    preparation_inputs["T61_source_hashes"] = source_hashes
    preparation_inputs["T54_parent_report"]["path"] = str(T54_REPORT.resolve())
    project_binding = {
        "schema": "GestureForge-S2A-T61-project-preflight-v1",
        "status": "READ_ONLY_BOUND",
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "run_directory": str(RUN_ROOT.resolve()),
        "project_name": "AX7Z020_Gesture",
        "project_xpr_path": str(XPR_PATH.resolve()),
        "baseline_head": BASE_HEAD,
        "current_head": current_head,
        "current_head_after_prepare": current_head_after_prepare,
        "previous_attempt": previous_attempt,
        "target_xpr_sha256_before_prepare": xpr_sha_before,
        "target_xpr_sha256_after_prepare": xpr_sha_after,
        "target_xpr_unchanged": True,
        "T61_source_hashes": source_hashes,
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
        "schema": "GestureForge-S2A-T61-fixture-manifest-v1",
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "current_head": current_head,
        "current_head_after_prepare": current_head_after_prepare,
        "previous_attempt": previous_attempt,
        "parameter_digest_order": "Q+,M+,Q-,M-",
        "scope": "tiny416 cfg section36 layer35; all 256 output channels at y=25, x=0..25",
        "parent_report": preparation_inputs["T54_parent_report"],
        "generator_source": preparation_inputs["T54_oracle_source"],
        "T61_source_hashes": source_hashes,
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
    negative_dependency_tests = _write_negative_dependency_tests(preparation_inputs)
    summary = {
        "schema": "GestureForge-S2A-T61-preparation-summary-v1",
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "current_head": current_head,
        "current_head_after_prepare": current_head_after_prepare,
        "previous_attempt": previous_attempt,
        "parameter_digest_order": "Q+,M+,Q-,M-",
        "scope": "tiny416 cfg section36 layer35; all 256 output channels at y=25, x=0..25",
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
        "negative_dependency_tests": negative_dependency_tests,
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
            "仅覆盖 y=25、x=0..25、256 个输出通道，不代表 layer35 全层或整网。",
            "本证据仅表示 CPU oracle 与 fixture 已准备，未运行 RTL 仿真。",
            "T54 仅作为冻结 oracle/协议来源；未读取其私有 TEMP 运行文件。",
        ],
        "completed_utc8": datetime.now(
            timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
    }
    _write_json_exclusive(PREPARE_REPORT, summary)
    main_report = _build_main_report(summary)
    _write_json_exclusive(MAIN_REPORT, main_report)
    print(json.dumps({
        "result": summary["status"],
        "prepare_report": str(PREPARE_REPORT.resolve()),
        "main_report": str(MAIN_REPORT.resolve()),
        "main_report_sha256": _sha_file(MAIN_REPORT),
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
    current_head_at_verify = _verify_baseline()
    static_checks = _source_configuration_check()
    previous_attempt = _load_prior_run01_failure()
    runtime = _runtime_preflight("verify")
    parent, inputs, preparation_inputs = _load_all_frozen_inputs()
    oracle = _build_oracle(inputs, progress=True)
    _require(PREPARE_REPORT.is_file() and PROJECT_PREFLIGHT.is_file() and
             FIXTURE_MANIFEST.is_file(),
             "T61 prepare_summary、工程预检绑定或 fixture manifest 缺失")
    summary, summary_sha = _read_json(PREPARE_REPORT)
    current_head_at_verify = _verify_baseline(
        summary.get("current_head") if isinstance(summary.get("current_head"), str) else None)
    _verify_baseline(
        summary.get("current_head_after_prepare")
        if isinstance(summary.get("current_head_after_prepare"), str) else None)
    _require(re.fullmatch(r"[0-9a-f]{40}", str(summary.get("current_head"))) is not None and
             re.fullmatch(r"[0-9a-f]{40}",
                          str(summary.get("current_head_after_prepare"))) is not None,
             "T61 prepare summary 未记录完整生成 HEAD SHA")
    binding, binding_sha = _read_json(PROJECT_PREFLIGHT)
    manifest, manifest_sha = _read_json(FIXTURE_MANIFEST)
    source_hashes = _source_hashes()
    preparation_inputs["T61_source_hashes"] = source_hashes
    _require(summary.get("schema") ==
             "GestureForge-S2A-T61-preparation-summary-v1" and
             summary.get("task_id") == TASK_ID and summary.get("run_id") == RUN_ID and
             summary.get("status") == "PREPARED_NOT_SIMULATED" and
             summary.get("baseline_head") == BASE_HEAD and
             summary.get("parameter_digest_order") == "Q+,M+,Q-,M-" and
             summary.get("scope") ==
             "tiny416 cfg section36 layer35; all 256 output channels at y=25, x=0..25" and
             binding.get("schema") ==
             "GestureForge-S2A-T61-project-preflight-v1" and
             binding.get("status") == "READ_ONLY_BOUND" and
             binding.get("task_id") == TASK_ID and binding.get("run_id") == RUN_ID and
             binding.get("baseline_head") == BASE_HEAD and
             binding.get("current_head") == summary.get("current_head") and
             binding.get("current_head_after_prepare") ==
             summary.get("current_head_after_prepare") and
             manifest.get("schema") ==
             "GestureForge-S2A-T61-fixture-manifest-v1" and
             manifest.get("task_id") == TASK_ID and manifest.get("run_id") == RUN_ID and
             manifest.get("status") == "PREPARED_NOT_SIMULATED" and
             manifest.get("baseline_head") == BASE_HEAD and
             manifest.get("current_head") == summary.get("current_head") and
             manifest.get("current_head_after_prepare") ==
             summary.get("current_head_after_prepare") and
             summary.get("previous_attempt") == previous_attempt and
             binding.get("previous_attempt") == previous_attempt and
             manifest.get("previous_attempt") == previous_attempt and
             manifest.get("parameter_digest_order") == "Q+,M+,Q-,M-" and
             manifest.get("fixed_points_yx") == [list(point) for point in POINTS],
             "T61 prepare evidence schema、状态、基线或范围不匹配")
    _require(summary.get("bindings", {}).get("T61_source_hashes") == source_hashes and
             binding.get("T61_source_hashes") == source_hashes and
             manifest.get("T61_source_hashes") == source_hashes and
             static_checks["runner_sha256"] == source_hashes[T61_RUNNER_RELATIVE] and
             static_checks["testbench_sha256"] == source_hashes[T61_TESTBENCH_RELATIVE],
             "T61 prepare 后源码哈希绑定发生变化")
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
             "T61 工程 XPR/只读状态绑定不匹配")
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
             "T61 自包含输入绑定或工程预检交叉引用不匹配")
    _require(binding.get("runtime_preflight", {}).get("processes") == [] and
             binding.get("runtime_preflight", {}).get("powershell_exit_code") == 0 and
             runtime.get("processes") == [] and
             binding.get("static_checks", {}).get("python_ast") == "PASS" and
             binding.get("static_checks", {}).get("powershell_ast") == "PASS" and
             binding.get("static_checks", {}).get("parameter_digest_order") ==
             "Q+,M+,Q-,M-" and
             binding.get("static_checks", {}).get(
                 "powershell_read_only_path_and_process_scan") == "PASS" and
             summary.get("runtime_preflight") == binding.get("runtime_preflight") and
             summary.get("static_checks") == binding.get("static_checks"),
             "T61 PowerShell 进程/路径或 Python 静态检查记录不匹配")
    _require(summary.get("oracle") == oracle["oracle"] and
             manifest.get("oracle") == oracle["oracle"] and
             summary.get("expected_counts") == oracle["expected_counts"] and
             manifest.get("expected_counts") == oracle["expected_counts"] and
             summary.get("feature_fixture") == oracle["fixture"] and
             manifest.get("fixture") == oracle["fixture"] and
             summary.get("bindings", {}).get("fixed_points_yx") ==
             [list(point) for point in POINTS],
             "T61 oracle、fixture 或 expected counts 重算不匹配")
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
             "T61 prepare_summary 与工程预检/manifest 摘要不一致")
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
             "T61 fixture 文件集或目录绑定不匹配")
    expected_blobs = {
        "feature_input.bin": oracle["feature"],
        "layer35_weights.bin": inputs["weight_bytes"],
        "golden.bin": oracle["combined_golden"],
        "vectors.txt": _vectors_bytes(oracle["vectors"]),
    }
    for name, data in expected_blobs.items():
        record = fixture_files[name]
        path = _verify_file_record(record, FIXTURE_ROOT / name,
                                   f"T61 fixture {name}")
        _require(path.read_bytes() == data,
                 f"T61 fixture 内容与重新计算的 oracle 不逐字节相同：{name}")
    golden = (FIXTURE_ROOT / "golden.bin").read_bytes()
    raw_golden, int8_golden = golden[:RAW_BYTES], golden[RAW_BYTES:]
    _require(len(raw_golden) == RAW_BYTES and len(int8_golden) == INT8_BYTES and
             _sha256(raw_golden) == oracle["oracle"]["raw_int32_le_sha256"] and
             _sha256(int8_golden) == oracle["oracle"]["quantized_int8_sha256"] and
             len(oracle["raw_values"]) == RAW_COUNT and
             len(oracle["quantized_values"]) == INT8_COUNT and
             oracle["oracle"]["d2_t23_match_count"] == INT8_COUNT,
             "T61 raw INT32/INT8/D2-T23 逐项验证计数或摘要错误")
    vector_lines = (FIXTURE_ROOT / "vectors.txt").read_text(
        encoding="ascii").splitlines()
    _require(len(vector_lines) == RAW_COUNT,
             "T61 vectors.txt 行数不等于6656")
    for index, line in enumerate(vector_lines):
        values = [int(value) for value in line.split()]
        _require(len(values) == 8 and values[0] == index // OUTPUT_SIZE and
                 values[1] == ROW_Y and values[2] == index % OUTPUT_SIZE and
                 tuple(values) == oracle["vectors"][index],
                 f"T61 vectors 坐标/字段错误：index={index}")
    expected_files = {
        "project_preflight_binding.json",
        "prepare_summary.json",
        "fixture/feature_input.bin",
        "fixture/layer35_weights.bin",
        "fixture/golden.bin",
        "fixture/vectors.txt",
        "fixture/fixture_manifest.json",
        *(f"negative_dependency_tests/case_{index:02d}.json"
          for index in range(1, 7)),
        "negative_dependency_tests/results.json",
    }
    _require(_file_set(RUN_ROOT) == expected_files,
             f"T61 run03 文件集合错误：actual={sorted(_file_set(RUN_ROOT))}")
    _require(summary.get("simulation", {}).get("status") == "NOT_RUN" and
             summary.get("review") == {
                 "G2": "NOT_REVIEWED", "G3": "NOT_CLAIMED",
                 "G4": "NOT_CLAIMED", "G5": "NOT_CLAIMED",
             },
             "T61 准备报告错误声明仿真或验收状态")
    _verify_negative_dependency_tests(summary)
    main_report, main_report_sha = _read_json(MAIN_REPORT)
    _require(main_report == _build_main_report(summary),
             "T61 主报告与独立 prepare summary 重建不一致")
    print(json.dumps({
        "result": "PREPARED_NOT_SIMULATED",
        "current_head_at_verify": current_head_at_verify,
        "prepare_summary_sha256": summary_sha,
        "main_report_sha256": main_report_sha,
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
        print(f"FAIL T61 {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
