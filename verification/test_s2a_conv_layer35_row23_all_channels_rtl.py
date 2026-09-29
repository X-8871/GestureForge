#!/usr/bin/env python3
"""为 S2A-T59 生成并核验 row23 的独立 CPU oracle 与准备证据。"""

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
T58_PREPARE_REPORT = ROOT / "report/evidence/S2A-T58/run01/prepare_summary.json"
T58_PREPARE_SHA256 = "33c67467387ec6ecd2c6945fb34c0485b351ed7b60f449135158f33e19b9f341"
T58_MANIFEST = ROOT / "report/evidence/S2A-T58/run01/fixture/fixture_manifest.json"
T58_MANIFEST_SHA256 = "895dd04ba9d50e22705849783842f921d319982ef9b7b00834af774bb2dc9b48"
T58_GOLDEN_SHA256 = "0892e785cfb724eb10c9fd39b5bdba2836fa4eb9c0374dd31e5fd2aa7ce50271"
T54_RUNNER = ROOT / "verification/test_s2a_conv_layer35_row18_all_channels_rtl.py"
T54_RUNNER_SHA256 = "4ec6a743d6a80c380505be2a8601879c311a7f42e07323027098c07a8dadd4f3"
T16_PROOF_PATH = Path(r"D:\FPGA_Competition\report\evidence\S2A-T16\conv_requant_proof.json")
T16_PROOF_SHA256 = "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24"
T17_ENGINE_PATH = Path(r"D:\FPGA_Competition\report\evidence\S2A-T17\conv_engine_simulation.json")
T17_ENGINE_SHA256 = "4cd1d0f0e5edf7b34907179dea47a9a9c0994eb1d8bd89adfa341067cac17ab2"
T20_SCHEDULER_PATH = Path(r"D:\FPGA_Competition\report\evidence\S2A-T20\conv_layer_scheduler_simulation.json")
T20_SCHEDULER_SHA256 = "d6bc16966a2d3c7707d98aafa6b435ae158cd28faa53baa8f795e13e86a17887"
T16_PROOF_SOURCE_PATH = Path(r"D:\FPGA_Competition\verification\s2a_conv_requant_proof.py")
T16_PROOF_SOURCE_SHA256 = "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9"
D2_FORWARD_SOURCE_PATH = Path(r"D:\FPGA_Competition\verification\s1_t02_d2_int8_forward.py")
D2_FORWARD_SOURCE_SHA256 = "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393"
UPSTREAM_BINDINGS = {
    "T16_conv_requant_proof": (T16_PROOF_PATH, T16_PROOF_SHA256),
    "T17_conv_engine_evidence": (T17_ENGINE_PATH, T17_ENGINE_SHA256),
    "T20_layer_scheduler_evidence": (T20_SCHEDULER_PATH, T20_SCHEDULER_SHA256),
    "T16_requant_proof_source": (T16_PROOF_SOURCE_PATH, T16_PROOF_SOURCE_SHA256),
    "D2_forward_reference_source": (D2_FORWARD_SOURCE_PATH, D2_FORWARD_SOURCE_SHA256),
    "oracle_source": (T54_RUNNER, T54_RUNNER_SHA256),
}
PREPARATION_INPUT_KEYS = (
    "T56_parent_report", "T56_summary", "T58_parent_prepare_summary",
    "T58_parent_fixture_manifest", "T58_parent_golden", "G0_specification",
    "T01_manifest", "T23_parameter_table", "GF8_package",
    "weight_layer35", "oracle_source", "T16_conv_requant_proof",
    "T17_conv_engine_evidence", "T20_layer_scheduler_evidence",
    "T16_requant_proof_source", "D2_forward_reference_source",
)
G0_PATH = ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
G0_SHA256 = "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"
T01_PATH = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
T01_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
T23_PATH = ROOT / "report/evidence/S2A-T23/conv_requant_parameter_table.json"
T23_SHA256 = "396dc66aa3ccc41050cc8183bff16b86143a6f5553cf38fed16b0ba8b4eb4ae1"
GF8_SHA256 = "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39"
EXPECTED_PARAMETER_DIGEST_SHA256 = "93a49c25387a459cb2964d988ac6e803d8ba9c8a3fcab664b948efb6354e3f29"
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
T59_SOURCE_PATHS = (
    *RTL_PATHS,
    "sim/tb_s2a_conv_layer35_row23_all_channels.sv",
    "verification/test_s2a_conv_layer35_row23_all_channels_rtl.py",
    "verification/test_s2a_t59_upstream_fail_closed.py",
)
T59_RUNNER_RELATIVE = "verification/test_s2a_conv_layer35_row23_all_channels_rtl.py"
XPR_PATH = ROOT / "vivado/AX7Z020_Gesture/AX7Z020_Gesture.xpr"
EVIDENCE_ROOT = ROOT / "report/evidence/S2A-T59"
ROOT_PROJECT_PREFLIGHT = EVIDENCE_ROOT / "project_preflight_binding.json"
ROOT_PROJECT_PREFLIGHT_SHA256 = "79177d4f0591762d9cccce9700fc4104a6a7c7c4fe7cc89ae136928e1e06b5d1"
RUN05_PREPARE_REPORT = EVIDENCE_ROOT / "run05/prepare_summary.json"
RUN05_PREPARE_REPORT_SHA256 = "ed42285130ba07d82b6b64cf437c27b52ec12a610bc2d2a94554670367342929"
RUN05_FIXTURE_MANIFEST = EVIDENCE_ROOT / "run05/fixture/fixture_manifest.json"
RUN05_FIXTURE_MANIFEST_SHA256 = "52f008959ecef8c73969bec7f46ced7af8ebedd1b5b05d2976d0d55d1428908a"
RUN05_FAILED_AUDIT = EVIDENCE_ROOT / "run05/upstream_fail_closed_audit.json"
RUN05_FAILED_AUDIT_SHA256 = "b3734cd917e0a7248b702137a1fe72215f18b8b0d13169cad33c890eafcc21f2"
RUN06_PREPARE_REPORT = EVIDENCE_ROOT / "run06/prepare_summary.json"
RUN06_PREPARE_REPORT_SHA256 = "3666d5b419dacd608d3a6a2b22ea22dfabe0ae63ad80ef325ff3593c943eeeaf"
RUN06_FIXTURE_MANIFEST = EVIDENCE_ROOT / "run06/fixture/fixture_manifest.json"
RUN06_FIXTURE_MANIFEST_SHA256 = "9d59acf04fba74eea5a34cd5165b92803dd020204308c49580428686e4fa9a8b"
RUN06_PROJECT_PREFLIGHT = EVIDENCE_ROOT / "run06/project_preflight_binding.json"
RUN06_PROJECT_PREFLIGHT_SHA256 = "67e6dbfeedcb29d0325a4c15038513f1a0bc6523bf98d7638e5a89bcc3eb3afb"
RUN06_AUDIT = EVIDENCE_ROOT / "run06/upstream_fail_closed_audit.json"
RUN06_AUDIT_SHA256 = "60ff1be9a5b39e1cc1b3e7b8910bcaf774d4ffa735dad178270c968f52f74f04"
RUN_ROOT = EVIDENCE_ROOT / "run07"
PROJECT_PREFLIGHT = RUN_ROOT / "project_preflight_binding.json"
FIXTURE_ROOT = RUN_ROOT / "fixture"
PREPARE_REPORT = RUN_ROOT / "prepare_summary.json"
FAIL_CLOSED_AUDIT = RUN_ROOT / "upstream_fail_closed_audit.json"
PRIOR_ATTEMPT_ARTIFACTS = {
    "run05": {
        "prepare_summary": (RUN05_PREPARE_REPORT, RUN05_PREPARE_REPORT_SHA256),
        "fixture_manifest": (RUN05_FIXTURE_MANIFEST, RUN05_FIXTURE_MANIFEST_SHA256),
        "upstream_fail_closed_audit": (RUN05_FAILED_AUDIT, RUN05_FAILED_AUDIT_SHA256),
    },
    "run06": {
        "prepare_summary": (RUN06_PREPARE_REPORT, RUN06_PREPARE_REPORT_SHA256),
        "fixture_manifest": (RUN06_FIXTURE_MANIFEST, RUN06_FIXTURE_MANIFEST_SHA256),
        "project_preflight_binding": (RUN06_PROJECT_PREFLIGHT, RUN06_PROJECT_PREFLIGHT_SHA256),
        "upstream_fail_closed_audit": (RUN06_AUDIT, RUN06_AUDIT_SHA256),
    },
}
POINTS = tuple((23, x) for x in range(26))
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
POWERSHELL_PREFLIGHT = r"""
$ErrorActionPreference = 'Stop'
$requiredDirectories = @(
    'D:\',
    'D:\FPGA_Competition',
    'D:\FPGA_Competition\report',
    'D:\FPGA_Competition\report\evidence',
    'D:\FPGA_Competition\report\evidence\S2A-T59',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run01',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run01\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run02',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run02\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run03',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run03\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run04',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run04\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run05',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run05\fixture',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run06',
    'D:\FPGA_Competition\report\evidence\S2A-T59\run06\fixture',
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
$evidenceRoot = 'D:\FPGA_Competition\report\evidence\S2A-T59'
$run01 = Join-Path $evidenceRoot 'run01'
$run02 = Join-Path $evidenceRoot 'run02'
$run03 = Join-Path $evidenceRoot 'run03'
$run04 = Join-Path $evidenceRoot 'run04'
$run05 = Join-Path $evidenceRoot 'run05'
$run06 = Join-Path $evidenceRoot 'run06'
$run07 = Join-Path $evidenceRoot 'run07'
$run07Preflight = Join-Path $run07 'project_preflight_binding.json'
$oldRootBinding = Join-Path $evidenceRoot 'project_preflight_binding.json'
$oldBindingItem = Get-Item -LiteralPath $oldRootBinding -Force -ErrorAction Stop
if ($oldBindingItem.PSIsContainer -or
    (($oldBindingItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0)) {
    throw "既有 T59 根级绑定不是普通文件：$oldRootBinding"
}
if (Test-Path -LiteralPath $run07 -PathType Any) {
    throw "T59 run07 目标已存在，拒绝覆盖：$run07"
}
if (Test-Path -LiteralPath $run07Preflight -PathType Any) {
    throw "T59 run07 预检绑定目标已存在，拒绝覆盖：$run07Preflight"
}
$expectedRootEntries = @('project_preflight_binding.json', 'run01', 'run02', 'run03', 'run04', 'run05', 'run06')
$actualRootEntries = @(Get-ChildItem -LiteralPath $evidenceRoot -Force |
    ForEach-Object { $_.Name } | Sort-Object)
if (($actualRootEntries -join '|') -ne ($expectedRootEntries -join '|')) {
    throw 'T59 根目录与预期 run01-run06/根级旧绑定不一致；拒绝写入 run07'
}
$pendingRoots = @($run01, $run02, $run03, $run04, $run05, $run06)
foreach ($root in $pendingRoots) {
    $pending = [Collections.Generic.Stack[string]]::new()
    $pending.Push($root)
    while ($pending.Count -gt 0) {
        $directory = $pending.Pop()
        foreach ($entry in [IO.Directory]::EnumerateFileSystemEntries($directory)) {
            $attributes = [IO.File]::GetAttributes($entry)
            if (($attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "既有 T59 证据目录中发现 reparse point：$entry"
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
        [ordered]@{ name = $_.Name; process_id = [int]$_.ProcessId }
    })
$result = [ordered]@{
    path_chain_valid = $true
    checked_directories = $requiredDirectories
    checked_xpr = $xpr
    evidence_root = $evidenceRoot
    run07_path = $run07
    target_absent = $true
    existing_run01 = $true
    existing_run02 = $true
    existing_run03 = $true
    existing_run04 = $true
    existing_run05 = $true
    existing_run06 = $true
    existing_run07 = $false
    process_names = $names
    processes_before_prepare = $processes
}
[Console]::Out.Write((ConvertTo-Json -InputObject $result -Depth 5 -Compress))
"""

POWERSHELL_PROCESS_SNAPSHOT = r"""
$ErrorActionPreference = 'Stop'
$names = @('vivado.exe', 'vivado_lab.exe', 'xsim.exe', 'xsimk.exe',
           'xelab.exe', 'xvlog.exe', 'xvhdl.exe', 'xsct.exe')
$processes = @(Get-CimInstance -ClassName Win32_Process -ErrorAction Stop |
    Where-Object { $names -contains $_.Name.ToLowerInvariant() } |
    Sort-Object ProcessId |
    ForEach-Object {
        [ordered]@{ name = $_.Name; process_id = [int]$_.ProcessId }
    })
$result = [ordered]@{ process_names = $names; processes = $processes }
[Console]::Out.Write((ConvertTo-Json -InputObject $result -Depth 4 -Compress))
"""


class T59Error(RuntimeError):
    """表示 S2A-T59 冻结输入或准备证据核验失败。"""


class T59UpstreamShaMismatch(T59Error):
    """表示某项冻结上游的 SHA-256 门禁拒绝了变更内容。"""

    def __init__(self, dependency_key: str, path: Path,
                 expected_sha256: str, actual_sha256: str) -> None:
        self.failure_record = {
            "code": "EXPECTED_UPSTREAM_SHA_MISMATCH",
            "dependency_key": dependency_key,
            "dependency_path": str(path.resolve()),
            "expected_sha256": expected_sha256,
            "actual_sha256": actual_sha256,
        }
        super().__init__(
            f"冻结上游 SHA-256 不匹配：{dependency_key}：{path} "
            f"expected={expected_sha256} actual={actual_sha256}"
        )


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T59Error(message)


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


def _is_git_ancestor(ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False,
    )
    return result.returncode == 0


def _require_head_descends_from(ancestor: str, descendant: str, label: str) -> None:
    _require(bool(ancestor) and bool(descendant) and
             _is_git_ancestor(ancestor, descendant),
             f"{label} 不是冻结基线的后代：baseline={ancestor} current={descendant}")


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


def _expected_upstream_records() -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    for name, (path, expected_sha256) in UPSTREAM_BINDINGS.items():
        _require(path.is_file(), f"T54 冻结上游缺失：{path}")
        actual_sha256 = _sha_file(path)
        if actual_sha256 != expected_sha256:
            raise T59UpstreamShaMismatch(name, path, expected_sha256, actual_sha256)
        records[name] = {
            "path": str(path.resolve()),
            "sha256": expected_sha256,
        }
    return records


def _verify_upstream_records(preparation_inputs: dict[str, Any]) -> None:
    for name, (path, expected_sha256) in UPSTREAM_BINDINGS.items():
        expected = {
            "path": str(path.resolve()),
            "sha256": expected_sha256,
        }
        record = preparation_inputs.get(name)
        _require(record == expected,
                 f"T59 冻结上游路径/SHA-256 绑定不符：{name}")
        checked_path = _verify_file_record(
            {"path": str(record["path"])}, f"T59 冻结上游 {name}"
        )
        actual_sha256 = _sha_file(checked_path)
        if actual_sha256 != expected_sha256:
            raise T59UpstreamShaMismatch(
                name, checked_path, expected_sha256, actual_sha256
            )
        _require(checked_path.resolve() == path.resolve(),
                 f"T59 冻结上游文件复核失败：{name}")


def _verify_loader_upstream_records(input_bindings: dict[str, Any],
                                    expected: dict[str, dict[str, str]]) -> None:
    loader_to_t59 = {
        "T16_proof": "T16_conv_requant_proof",
        "T17_engine_evidence": "T17_conv_engine_evidence",
        "T20_scheduler_evidence": "T20_layer_scheduler_evidence",
        "T16_script": "T16_requant_proof_source",
        "D2_forward_reference": "D2_forward_reference_source",
    }
    for loader_key, t59_key in loader_to_t59.items():
        _require(input_bindings.get(loader_key) == expected.get(t59_key),
                 f"T54 loader 返回的上游绑定与 T59 冻结路径/SHA 不一致：{loader_key}")


def _quantization_parameter_coverage(inputs: dict[str, Any]) -> dict[str, Any]:
    channels = inputs.get("channels", [])
    mq_values = inputs.get("mq_values", ())
    _require(len(channels) == 256 and len(mq_values) == 256,
             "T23 layer35 M/Q 输入没有覆盖全部 256 个输出通道")
    digest = hashlib.sha256()
    fields = ("positive_Q", "positive_M", "negative_Q", "negative_M")
    for index, channel in enumerate(channels):
        _require(int(channel.get("channel", -1)) == index,
                 f"T23 layer35 通道索引不连续：index={index}")
        values = tuple(int(channel[field]) for field in
                       ("positive_M", "positive_Q", "negative_M", "negative_Q"))
        _require(values == tuple(mq_values[index]),
                 f"T54 loader M/Q 值与 T23 channel record 不一致：channel={index}")
        digest.update((f"{index},{int(channel['positive_Q'])},{int(channel['positive_M'])},"
                       f"{int(channel['negative_Q'])},{int(channel['negative_M'])}\n").encode("ascii"))
    t16, _ = _read_json(T16_PROOF_PATH)
    t23, _ = _read_json(T23_PATH)
    t16_layer = next((row for row in t16.get("layers", [])
                      if int(row.get("layer_index", -1)) == 35), None)
    t23_layer = next((row for row in t23.get("layers", [])
                      if int(row.get("layer_index", -1)) == 35), None)
    expected_digest = (t23_layer or {}).get("candidate_parameter_sha256")
    _require(t16_layer is not None and t23_layer is not None and
             digest.hexdigest() == expected_digest ==
             t16_layer.get("candidate_parameter_sha256") ==
             EXPECTED_PARAMETER_DIGEST_SHA256,
             "T23 layer35 Q+/M+/Q-/M- canonical digest 与冻结摘要或 T16 proof 不匹配")
    return {
        "source": str(T23_PATH.resolve()),
        "source_sha256": T23_SHA256,
        "channel_count": len(channels),
        "first_channel": int(channels[0]["channel"]),
        "last_channel": int(channels[-1]["channel"]),
        "fields_in_digest_order": list(fields),
        "canonical_parameter_digest_sha256": digest.hexdigest(),
    }


def _verify_parent() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    _require_head_descends_from(BASE_HEAD, _current_head(), "当前 HEAD")
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
    for relative in T59_SOURCE_PATHS:
        path = ROOT / relative
        _require(path.is_file(), f"缺少 T59 源码：{relative}")
        hashes[relative] = _sha_file(path)
    return hashes


def _vectors_bytes(vectors: list[tuple[int, int, int, int, int, int, int, int]]) -> bytes:
    return ("".join(" ".join(str(value) for value in vector) + "\n"
                    for vector in vectors)).encode("ascii")


def _verify_tb_run_paths() -> dict[str, list[str]]:
    tb_path = ROOT / "sim/tb_s2a_conv_layer35_row23_all_channels.sv"
    _require(tb_path.is_file(), f"T59 row23 testbench 缺失：{tb_path}")
    source = tb_path.read_text(encoding="utf-8")
    paths = re.findall(r'\$fopen\("([^"]+)"', source)
    expected_inputs = [
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run07\\fixture\\feature_input.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run07\\fixture\\layer35_weights.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run07\\fixture\\golden.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run07\\fixture\\vectors.txt",
    ]
    expected_outputs = [
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run07\\observed_raw.bin",
        r"D:\\FPGA_Competition\\report\\evidence\\S2A-T59\\run07\\observed_output.bin",
    ]
    _require(len(paths) == 6 and sorted(paths) == sorted(expected_inputs + expected_outputs),
             "T59 testbench 的六个 $fopen 路径未全部固定到 run07")
    _require(not any(re.search(r"\\run0[123]\\", path) for path in paths),
             "T59 testbench 仍引用旧 run01/run02/run03/run04/run05 路径")
    return {"fixture_inputs": expected_inputs, "observed_outputs": expected_outputs}



def _verify_t58_parent() -> dict[str, Any]:
    _require(T58_PREPARE_REPORT.is_file() and _sha_file(T58_PREPARE_REPORT) == T58_PREPARE_SHA256,
             "T58 row22 summary SHA 不匹配")
    _require(T58_MANIFEST.is_file() and _sha_file(T58_MANIFEST) == T58_MANIFEST_SHA256,
             "T58 row22 manifest SHA 不匹配")
    summary, summary_sha = _read_json(T58_PREPARE_REPORT)
    manifest, manifest_sha = _read_json(T58_MANIFEST)
    points = [[22, x] for x in range(26)]
    _require(summary.get("task_id") == "S2A-T58" and summary.get("run_id") == "run01" and
             summary.get("status") == "PREPARED_NOT_SIMULATED" and
             summary.get("baseline_head") == BASE_HEAD and
             summary.get("scope") == "tiny416 cfg section36 layer35; all 256 output channels at y=22, x=0..25" and
             summary.get("bindings", {}).get("fixed_points_yx") == points,
             "T58 row22 prepare 身份/范围不匹配")
    oracle = summary.get("oracle", {})
    _require(manifest.get("task_id") == "S2A-T58" and manifest.get("run_id") == "run01" and
             manifest.get("status") == "PREPARED_NOT_SIMULATED" and
             manifest.get("fixed_points_yx") == points and manifest.get("oracle") == oracle and
             oracle.get("raw_int32_count") == RAW_COUNT and
             oracle.get("quantized_int8_count") == INT8_COUNT and
             oracle.get("d2_t23_match_count") == INT8_COUNT and
             oracle.get("combined_golden_sha256") == T58_GOLDEN_SHA256 and
             summary.get("simulation", {}).get("status") == "NOT_RUN",
             "T58 row22 oracle/manifest 状态不匹配")
    sources = summary.get("bindings", {}).get("T58_source_hashes", {})
    _require(set(sources) == set((*RTL_PATHS,
             "sim/tb_s2a_conv_layer35_row22_all_channels.sv",
             "verification/test_s2a_conv_layer35_row22_all_channels_rtl.py")) and
             manifest.get("T58_source_hashes") == sources,
             "T58 row22 源码绑定集合不匹配")
    for rel, digest in sources.items():
        _require(_sha_file(ROOT / rel) == str(digest).lower(), f"T58 源码 SHA 不匹配：{rel}")
    fixture = summary.get("fixture", {})
    mrec = fixture.get("manifest", {})
    _require(mrec.get("path") == str(T58_MANIFEST.resolve()) and
             mrec.get("sha256") == manifest_sha == T58_MANIFEST_SHA256,
             "T58 summary/manifest SHA 绑定不匹配")
    files, manifest_files = fixture.get("files", {}), manifest.get("files", {})
    names = {"feature_input.bin", "layer35_weights.bin", "golden.bin", "vectors.txt"}
    _require(set(files) == names and set(manifest_files) == names, "T58 fixture 集合不匹配")
    for name in names:
        _require(files[name] == manifest_files[name], f"T58 fixture 双向绑定不匹配：{name}")
        _verify_file_record(files[name], f"T58 parent {name}")
    golden = dict(files["golden.bin"])
    _require(golden.get("sha256") == T58_GOLDEN_SHA256 and golden.get("bytes") == GOLDEN_BYTES,
             "T58 parent golden 摘要不匹配")
    return {"prepare_summary": {"path": str(T58_PREPARE_REPORT.resolve()), "sha256": summary_sha},
            "fixture_manifest": {"path": str(T58_MANIFEST.resolve()), "sha256": manifest_sha},
            "golden": golden, "status": "PREPARED_NOT_SIMULATED"}

def _runtime_preflight() -> dict[str, Any]:
    executable = "powershell.exe"
    result = subprocess.run(
        [executable, "-NoProfile", "-NonInteractive", "-Command",
         POWERSHELL_PREFLIGHT],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False, timeout=30,
    )
    _require(result.returncode == 0,
             f"PowerShell 路径/进程预检失败：{result.stderr.strip()}")
    try:
        snapshot = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise T59Error(f"PowerShell 预检输出不是 JSON：{error}") from error
    _require(ROOT_PROJECT_PREFLIGHT.is_file() and
             not ROOT_PROJECT_PREFLIGHT.is_symlink(),
             f"T59 根级旧绑定缺失或路径类型错误：{ROOT_PROJECT_PREFLIGHT}")
    snapshot["root_binding_sha256"] = _sha_file(ROOT_PROJECT_PREFLIGHT)
    _require(isinstance(snapshot, dict) and
             snapshot.get("path_chain_valid") is True and
             snapshot.get("target_absent") is True and
             snapshot.get("existing_run01") is True and
             snapshot.get("existing_run02") is True and
             snapshot.get("existing_run03") is True and
             snapshot.get("existing_run04") is True and
             snapshot.get("existing_run05") is True and
             snapshot.get("existing_run06") is True and
             snapshot.get("existing_run07") is False and
             snapshot.get("root_binding_sha256") == ROOT_PROJECT_PREFLIGHT_SHA256 and
             tuple(snapshot.get("process_names", ())) == PROCESS_NAMES and
             snapshot.get("processes_before_prepare") == [],
             "T59 路径/reparse 或 8 类 Vivado/XSim 进程门禁不通过")
    snapshot["powershell_exit_code"] = result.returncode
    snapshot["mcp_status"] = "NOT_QUERIED"
    return snapshot


def _runtime_process_snapshot() -> dict[str, Any]:
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
         POWERSHELL_PROCESS_SNAPSHOT],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False, timeout=30,
    )
    _require(result.returncode == 0,
             f"PowerShell Vivado/XSim 进程快照失败：{result.stderr.strip()}")
    try:
        snapshot = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise T59Error(f"PowerShell 进程快照不是 JSON：{error}") from error
    _require(isinstance(snapshot, dict) and
             tuple(snapshot.get("process_names", ())) == PROCESS_NAMES and
             snapshot.get("processes") == [],
             "T59 当前存在 Vivado/XSim 相关进程，拒绝继续")
    return {
        "process_names": list(PROCESS_NAMES),
        "processes": snapshot["processes"],
        "powershell_exit_code": result.returncode,
    }


def _prior_attempts_record() -> list[dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for run_id, artifact_pins in PRIOR_ATTEMPT_ARTIFACTS.items():
        artifacts: dict[str, dict[str, Any]] = {}
        for name, (path, expected_sha256) in artifact_pins.items():
            _require(path.is_file() and not path.is_symlink(),
                     f"T59 {run_id} 历史工件缺失或路径类型错误：{path}")
            _require(_sha_file(path) == expected_sha256,
                     f"T59 {run_id} 历史工件 SHA-256 已变化：{path}")
            artifacts[name] = _artifact(path)
        records[run_id] = {
            "task_id": "S2A-T59",
            "run_id": run_id,
            "artifacts": artifacts,
        }
    run05_audit, _ = _read_json(RUN05_FAILED_AUDIT)
    run05_cases = run05_audit.get("cases", [])
    _require(run05_audit.get("status") == "FAIL" and
             run05_audit.get("run_id") == "run05" and
             len(run05_cases) == len(UPSTREAM_BINDINGS) and
             all(case.get("result") == "FAIL" and
                 case.get("actual_exit_code") == 1 and
                 case.get("failure_record") is None
                 for case in run05_cases),
             "T59 run05 保留的 FAIL 审计内容不匹配")
    run06_audit, _ = _read_json(RUN06_AUDIT)
    run06_cases = run06_audit.get("cases", [])
    _require(run06_audit.get("status") == "PASS" and
             run06_audit.get("run_id") == "run06" and
             len(run06_cases) == len(UPSTREAM_BINDINGS) and
             {case.get("dependency_key") for case in run06_cases} ==
             set(UPSTREAM_BINDINGS) and
             all(case.get("result") == "PASS" and
                 case.get("actual_exit_code") == 1 and
                 case.get("failure_record", {}).get("code") ==
                 "EXPECTED_UPSTREAM_SHA_MISMATCH" and
                 case.get("failure_record", {}).get("dependency_key") ==
                 case.get("dependency_key") and
                 case.get("failure_record", {}).get("dependency_path") ==
                 case.get("temp_dependency_path") and
                 case.get("failure_record", {}).get("expected_sha256") ==
                 case.get("expected_sha256") and
                 case.get("failure_record", {}).get("actual_sha256") ==
                 case.get("mutated_sha256")
                 for case in run06_cases),
             "T59 run06 保留的 6/6 PASS 结构化审计内容不匹配")
    records["run05"].update({
        "status": "FAIL",
        "prepare_status": "PREPARED_NOT_SIMULATED",
        "audit_status": "FAIL",
        "audit_case_count": len(run05_cases),
        "audit_actual_exit_codes": [case["actual_exit_code"] for case in run05_cases],
        "failure_reason": "旧审计未取得结构化错误记录，六项均保留为 FAIL",
    })
    records["run06"].update({
        "status": "FAIL",
        "prepare_status": "PREPARED_NOT_SIMULATED",
        "audit_status": "PASS",
        "audit_case_count": len(run06_cases),
        "audit_actual_exit_codes": [case["actual_exit_code"] for case in run06_cases],
        "verify_only": {
            "status": "FAIL",
            "actual_exit_code": 1,
            "expected_exit_code": 2,
            "reason_code": "STALE_AUDIT_EXIT_CODE_EXPECTATION",
        },
    })
    return [records["run05"], records["run06"]]

def _ensure_run07_absent() -> None:
    _require(EVIDENCE_ROOT.is_dir() and not EVIDENCE_ROOT.is_symlink(),
             f"T59 evidence 根目录缺失或不是普通目录：{EVIDENCE_ROOT}")
    _require(not RUN_ROOT.exists() and not RUN_ROOT.is_symlink(),
             f"拒绝覆盖既有 T59 run07：{RUN_ROOT}")
    _require(not PROJECT_PREFLIGHT.exists() and not PROJECT_PREFLIGHT.is_symlink(),
             f"拒绝覆盖既有 T59 run07 工程预检绑定：{PROJECT_PREFLIGHT}")
    _require(ROOT_PROJECT_PREFLIGHT.is_file() and not ROOT_PROJECT_PREFLIGHT.is_symlink() and
             _sha_file(ROOT_PROJECT_PREFLIGHT) == ROOT_PROJECT_PREFLIGHT_SHA256,
             f"T59 根级旧绑定缺失、路径类型错误或 SHA-256 已变化：{ROOT_PROJECT_PREFLIGHT}")
    _prior_attempts_record()
    expected_root_entries = {
        "project_preflight_binding.json", "run01", "run02", "run03", "run04", "run05", "run06",
    }
    actual_root_entries = {entry.name for entry in EVIDENCE_ROOT.iterdir()}
    _require(actual_root_entries == expected_root_entries,
             "T59 根目录内容与 run01-run06/根级旧绑定不一致，拒绝创建 run07")

def _project_xpr_sha() -> str:
    _require(XPR_PATH.is_file(), f"目标 XPR 缺失：{XPR_PATH}")
    return _sha_file(XPR_PATH)


def _prepare() -> dict[str, Any]:
    parent, parent_bindings, parent_simulation = _verify_parent()
    t58_parent = _verify_t58_parent()
    tb_io_paths = _verify_tb_run_paths()
    runtime = _runtime_preflight()
    _ensure_run07_absent()
    prior_attempts = _prior_attempts_record()
    current_head = _current_head()
    _require_head_descends_from(BASE_HEAD, current_head, "T59 运行 HEAD")
    xpr_sha_before = _project_xpr_sha()

    oracle_runner, historical_oracle_head = _load_oracle_runner(current_head)
    inputs = oracle_runner._load_frozen_inputs()
    input_bindings = inputs["bindings"]
    upstream_records = _expected_upstream_records()
    _verify_loader_upstream_records(input_bindings, upstream_records)
    parameter_coverage = _quantization_parameter_coverage(inputs)
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
             "T59 oracle 输出长度或比较数错误")
    _require(oracle["oracle"]["raw_int32_count"] == RAW_COUNT and
             oracle["oracle"]["quantized_int8_count"] == INT8_COUNT and
             oracle["oracle"]["d2_t23_match_count"] == INT8_COUNT and
             all(y == 23 for y, _ in POINTS) and
             tuple(x for _, x in POINTS) == tuple(range(26)),
             "T59 oracle 点集或 raw/INT8/D2 逐项计数错误")

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
                 f"T59 fixture 长度错误：{name}")

    _ensure_run07_absent()
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
        "T58_parent_prepare_summary": t58_parent["prepare_summary"],
        "T58_parent_fixture_manifest": t58_parent["fixture_manifest"],
        "T58_parent_golden": t58_parent["golden"],
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
        **upstream_records,
    }
    _verify_upstream_records(preparation_inputs)
    runtime["processes_after_prepare"] = _runtime_process_snapshot()
    xpr_sha_after = _project_xpr_sha()
    _require(xpr_sha_after == xpr_sha_before,
             "T59 prepare 期间真实 XPR SHA-256 发生变化")
    _require(_current_head() == current_head,
             "T59 prepare 期间 Git HEAD 发生变化")
    preflight = {
        "schema": "GestureForge-S2A-T59-project-preflight-v5",
        "status": "READ_ONLY_BOUND",
        "task_id": "S2A-T59",
        "run_id": "run07",
        "baseline_head": BASE_HEAD,
        "current_head": current_head,
        "run_directory": str(RUN_ROOT.resolve()),
        "prior_attempts": prior_attempts,
        "project_name": "AX7Z020_Gesture",
        "project_xpr_path": str(XPR_PATH.resolve()),
        "target_xpr_sha256_before_prepare": xpr_sha_before,
        "target_xpr_sha256_after_prepare": xpr_sha_after,
        "target_xpr_unchanged": True,
        "T59_source_hashes": source_hashes,
        "preparation_inputs": preparation_inputs,
        "runtime_preflight": runtime,
        "mcp_status": "NOT_QUERIED",
        "vivado_opened": False,
        "vivado_cli_invoked": False,
    }
    _require(not PROJECT_PREFLIGHT.exists(),
             f"拒绝覆盖 T59 工程预检绑定：{PROJECT_PREFLIGHT}")
    _write_json_exclusive(PROJECT_PREFLIGHT, preflight)
    project_preflight_record = _artifact(PROJECT_PREFLIGHT)

    fixture_manifest_path = FIXTURE_ROOT / "fixture_manifest.json"
    fixture_manifest = {
        "schema": "GestureForge-S2A-T59-fixture-manifest-v6",
        "task_id": "S2A-T59",
        "run_id": "run07",
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "current_head": current_head,
        "prior_attempts": prior_attempts,
        "parent_report": preparation_inputs["T56_parent_report"],
        "T58_parent": t58_parent,
        "generator_source": preparation_inputs["oracle_source"],
        "runner_source_sha256": source_hashes[T59_RUNNER_RELATIVE],
        "T59_source_hashes": source_hashes,
        "preparation_inputs": preparation_inputs,
        "project_preflight_binding": project_preflight_record,
        "fixture_root": str(FIXTURE_ROOT.resolve()),
        "files": fixture_files,
        "oracle": oracle["oracle"],
        "quantization_parameter_coverage": parameter_coverage,
        "fixed_points_yx": [list(point) for point in POINTS],
        "tb_io_paths": tb_io_paths,
    }
    _write_json_exclusive(fixture_manifest_path, fixture_manifest)

    layer = inputs["layer35"]
    summary = {
        "schema": "GestureForge-S2A-T59-preparation-summary-v6",
        "task_id": "S2A-T59",
        "run_id": "run07",
        "status": "PREPARED_NOT_SIMULATED",
        "baseline_head": BASE_HEAD,
        "current_head": current_head,
        "prior_attempts": prior_attempts,
        "scope": "tiny416 cfg section36 layer35; all 256 output channels at y=23, x=0..25",
        "tb_io_paths": tb_io_paths,
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
        "T58_parent": t58_parent,
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
            "runtime_BASE_HEAD": current_head,
            "reason": "T54 loader 的历史精确 HEAD 守卫在内存中绑定到本次 current_head；独立验证冻结 BASE_HEAD 为当前及本次 HEAD 的祖先，并保持 T54 上游文件哈希校验。",
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
        "tb_io_paths": tb_io_paths,
            "T56_source_hashes": parent_bindings["T56_source_hashes"],
            "T59_source_hashes": source_hashes,
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
        "quantization_parameter_coverage": parameter_coverage,
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
            "reason": "本任务只准备 CPU oracle 与 fixture，未创建 T59 launcher/Tcl，也未运行 Vivado/XSim。",
        },
        "review": {
            "G2": "NOT_REVIEWED",
            "G3": "NOT_CLAIMED",
            "G4": "NOT_CLAIMED",
            "G5": "NOT_CLAIMED",
        },
        "limitations": [
            "仅覆盖 y=23、x=0..25、256 个输出通道，不代表 layer35 全层或整网。",
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


def _verify_fail_closed_audit(preparation: dict[str, Any],
                              manifest: dict[str, Any],
                              prepared_hashes: dict[str, Any]) -> None:
    record = preparation.get("fail_closed_audit")
    _require(isinstance(record, dict) and
             preparation.get("bindings", {}).get("fail_closed_audit") == record and
             manifest.get("fail_closed_audit") == record,
             "T59 六项 fail-closed 审计未由 summary/manifest 双向绑定")
    audit_path = _verify_file_record(record, "T59 fail-closed 审计 JSON")
    _require(audit_path.resolve() == FAIL_CLOSED_AUDIT.resolve(),
             "T59 fail-closed 审计路径不属于 run07")
    audit, _ = _read_json(audit_path)
    expected_keys = set(UPSTREAM_BINDINGS)
    cases = audit.get("cases", [])
    _require(audit.get("schema") == "GestureForge-S2A-T59-upstream-fail-closed-v2" and
             audit.get("task_id") == "S2A-T59" and
             audit.get("run_id") == "run07" and
             audit.get("status") == "PASS" and
             audit.get("verify_mode") == "--verify-only" and
             audit.get("audit_script_sha256") ==
             prepared_hashes.get("verification/test_s2a_t59_upstream_fail_closed.py") and
             len(cases) == len(expected_keys) and
             {case.get("dependency_key") for case in cases} == expected_keys,
             "T59 fail-closed 审计身份、源码绑定或六项覆盖数不匹配")
    for case in cases:
        dependency_key = case["dependency_key"]
        path, expected_sha256 = UPSTREAM_BINDINGS[dependency_key]
        failure = case.get("failure_record")
        temp_dependency_path = str(case.get("temp_dependency_path", ""))
        _require(case.get("dependency_path") == str(path.resolve()) and
                 case.get("expected_sha256") == expected_sha256 and
                 case.get("expected_rejection") ==
                 "exit_code=1 and structured EXPECTED_UPSTREAM_SHA_MISMATCH matches dependency key/path/SHA" and
                 case.get("actual_exit_code") == 1 and
                 isinstance(failure, dict) and
                 failure.get("code") == "EXPECTED_UPSTREAM_SHA_MISMATCH" and
                 failure.get("dependency_key") == dependency_key and
                 failure.get("dependency_path") == temp_dependency_path and
                 failure.get("expected_sha256") == expected_sha256 and
                 failure.get("actual_sha256") == case.get("mutated_sha256") and
                 failure.get("actual_sha256") != expected_sha256 and
                 case.get("temp_cleanup_policy") ==
                 "TemporaryDirectory 在 verify-only 子进程结束后清理" and
                 case.get("temp_path_cleaned") is True and
                 not Path(str(case.get("temp_root_path", ""))).exists() and
                 case.get("result") == "PASS",
                 f"T59 fail-closed 审计案例未命中预期 SHA 门禁：{dependency_key}")


def _verify_prepared_fixture(preparation: dict[str, Any]) -> tuple[dict[str, Any], str, bytes]:
    fixture = preparation.get("fixture")
    _require(isinstance(fixture, dict), "T59 prepare_summary 缺少 fixture 对象")
    _require(Path(str(fixture.get("root", ""))).resolve() == FIXTURE_ROOT.resolve(),
             "T59 fixture 根目录与准备摘要绑定不一致")
    manifest_record = fixture.get("manifest")
    _require(isinstance(manifest_record, dict),
             "T59 prepare_summary 缺少 fixture manifest 绑定")
    manifest_path = _verify_file_record(manifest_record, "T59 fixture manifest")
    _require(manifest_path.resolve() == (FIXTURE_ROOT / "fixture_manifest.json").resolve(),
             "T59 fixture manifest 路径不匹配")
    manifest, manifest_sha256 = _read_json(manifest_path)
    _require(manifest_sha256 == str(manifest_record.get("sha256", "")).lower(),
             "T59 fixture manifest SHA-256 与 prepare_summary 不一致")
    _require(manifest.get("schema") == "GestureForge-S2A-T59-fixture-manifest-v6" and
             manifest.get("task_id") == "S2A-T59" and
             manifest.get("run_id") == "run07" and
             manifest.get("status") == "PREPARED_NOT_SIMULATED" and
             manifest.get("baseline_head") == BASE_HEAD and
             manifest.get("current_head") == preparation.get("current_head") and
             manifest.get("fixture_root") == str(FIXTURE_ROOT.resolve()) and
             manifest.get("fixed_points_yx") == [list(point) for point in POINTS] and
             preparation.get("tb_io_paths") == manifest.get("tb_io_paths") ==
             _verify_tb_run_paths(),
             "T59 fixture manifest 的 schema、基线、根目录或坐标不匹配")
    _require(manifest.get("parent_report", {}).get("sha256") == T56_REPORT_SHA256 and
             manifest.get("T58_parent") == preparation.get("T58_parent") == _verify_t58_parent(),
             "T59 manifest 未绑定已审 T56/T58 父证据")
    _require(preparation.get("tb_io_paths") == _verify_tb_run_paths(),
             "T59 prepare_summary 的 testbench 输入/输出路径不属于 run07")

    prepared_hashes = preparation.get("bindings", {}).get("T59_source_hashes")
    _require(isinstance(prepared_hashes, dict) and
             set(prepared_hashes) == set(T59_SOURCE_PATHS) and
             manifest.get("T59_source_hashes") == prepared_hashes,
             "T59 manifest 与 prepare_summary 源码绑定不一致")
    for relative, expected in prepared_hashes.items():
        source = ROOT / relative
        _require(source.is_file() and _sha_file(source) == str(expected).lower(),
                 f"T59 准备后源码哈希变化：{relative}")
    _require(manifest.get("runner_source_sha256") ==
             prepared_hashes.get(T59_RUNNER_RELATIVE),
             "T59 manifest 未绑定 runner SHA-256")
    preparation_inputs = {
        key: preparation.get("bindings", {}).get(key)
        for key in PREPARATION_INPUT_KEYS
    }
    _require(all(isinstance(value, dict) for value in preparation_inputs.values()) and
             manifest.get("preparation_inputs") == preparation_inputs,
             "T59 manifest 与 prepare_summary 的冻结输入绑定不一致")
    _verify_upstream_records(preparation_inputs)
    _verify_fail_closed_audit(preparation, manifest, prepared_hashes)
    project_preflight_record = preparation.get("bindings", {}).get(
        "project_preflight_binding")
    _require(isinstance(project_preflight_record, dict) and
             manifest.get("project_preflight_binding") == project_preflight_record,
             "T59 manifest 与 prepare_summary 的本地工程预检绑定不一致")

    expected_names = {
        "feature_input.bin", "layer35_weights.bin", "golden.bin", "vectors.txt",
    }
    prepared_files = fixture.get("files")
    manifest_files = manifest.get("files")
    _require(isinstance(prepared_files, dict) and set(prepared_files) == expected_names and
             isinstance(manifest_files, dict) and set(manifest_files) == expected_names,
             "T59 fixture 文件集合不匹配")
    for name in sorted(expected_names):
        prepared_record = prepared_files[name]
        manifest_file_record = manifest_files[name]
        _require(isinstance(prepared_record, dict) and
                 isinstance(manifest_file_record, dict),
                 f"T59 fixture 文件绑定格式错误：{name}")
        prepared_path = _verify_file_record(prepared_record, f"T59 prepare_summary {name}")
        manifest_file_path = _verify_file_record(manifest_file_record,
                                                 f"T59 manifest {name}")
        expected_path = FIXTURE_ROOT / name
        _require(prepared_path.resolve() == expected_path.resolve() and
                 manifest_file_path.resolve() == expected_path.resolve() and
                 prepared_record.get("bytes") == manifest_file_record.get("bytes") and
                 str(prepared_record.get("sha256", "")).lower() ==
                 str(manifest_file_record.get("sha256", "")).lower(),
                 f"T59 fixture 路径或摘要/manifest 绑定不一致：{name}")

    expected_sizes = {
        "feature_input.bin": FEATURE_BYTES,
        "layer35_weights.bin": WEIGHT_BYTES,
        "golden.bin": GOLDEN_BYTES,
    }
    for name, size in expected_sizes.items():
        _require(prepared_files[name].get("bytes") == size,
                 f"T59 fixture 字节数错误：{name}")

    prepared_oracle = preparation.get("oracle")
    _require(isinstance(prepared_oracle, dict) and
             manifest.get("oracle") == prepared_oracle and
             prepared_oracle.get("raw_int32_count") == RAW_COUNT and
             prepared_oracle.get("quantized_int8_count") == INT8_COUNT and
             prepared_oracle.get("d2_t23_match_count") == INT8_COUNT,
             "T59 oracle 字段或逐项计数不匹配")
    _require(manifest.get("quantization_parameter_coverage") ==
             preparation.get("quantization_parameter_coverage"),
             "T59 manifest 与 prepare_summary 的 T23 通道参数覆盖绑定不一致")
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
             "T59 combined/raw/INT8 golden 字节摘要不匹配")
    vector_lines = (FIXTURE_ROOT / "vectors.txt").read_text(
        encoding="ascii").splitlines()
    _require(len(vector_lines) == RAW_COUNT,
             "T59 vectors.txt 行数不等于 6656")
    for index, line in enumerate(vector_lines):
        values = [int(value) for value in line.split()]
        _require(len(values) == 8 and values[0] == index // 26 and
                 values[1] == 23 and values[2] == index % 26,
                 f"T59 vectors.txt 坐标或字段错误：row={index}")
    return manifest, manifest_sha256, golden


def _verify_runtime_oracle(preparation: dict[str, Any]) -> str:
    runtime_head = _current_head()
    _require_head_descends_from(BASE_HEAD, runtime_head,
                                "T59 verify-only 当前 HEAD")
    oracle_runner, historical_head = _load_oracle_runner(runtime_head)
    inputs = oracle_runner._load_frozen_inputs()
    expected_upstream = _expected_upstream_records()
    _verify_loader_upstream_records(inputs["bindings"], expected_upstream)
    coverage = _quantization_parameter_coverage(inputs)
    _require(coverage == preparation.get("quantization_parameter_coverage"),
             "verify-only 重载的 T23 Q+/M+/Q-/M- 覆盖摘要不匹配")
    oracle = oracle_runner._build_oracle(inputs, progress=False, points=POINTS)
    _require(oracle["oracle"] == preparation.get("oracle") and
             oracle["fixture"] == preparation.get("feature_fixture") and
             oracle["expected_counts"] == preparation.get("expected_counts"),
             "verify-only 重算的 T54 oracle/feature fixture/传输计数不匹配")
    _require(oracle["combined_golden"] == (FIXTURE_ROOT / "golden.bin").read_bytes() and
             oracle["feature"] == (FIXTURE_ROOT / "feature_input.bin").read_bytes() and
             inputs["weight_bytes"] ==
             (FIXTURE_ROOT / "layer35_weights.bin").read_bytes() and
             _vectors_bytes(oracle["vectors"]) ==
             (FIXTURE_ROOT / "vectors.txt").read_bytes(),
             "verify-only 重算的 feature/weight/golden/vectors 与 run07 字节不一致")
    _require(len(oracle["raw_values"]) == RAW_COUNT and
             len(oracle["quantized_values"]) == INT8_COUNT and
             oracle["oracle"].get("d2_t23_match_count") == INT8_COUNT and
             all(point[0] == 23 for point in POINTS) and
             tuple(point[1] for point in POINTS) == tuple(range(26)),
             "verify-only T59 y=23 / raw / INT8 / D2-T23 覆盖数错误")
    source = preparation.get("oracle_source", {})
    _require(source.get("historical_BASE_HEAD") == historical_head and
             source.get("runtime_BASE_HEAD") == preparation.get("current_head") and
             source.get("path") == str(T54_RUNNER.resolve()) and
             source.get("sha256") == T54_RUNNER_SHA256,
             "T59 summary 的 T54 runtime/current_head 来源记录不匹配")
    return runtime_head


def _verify_prepared() -> dict[str, Any]:
    parent, parent_bindings, _ = _verify_parent()
    t58_parent = _verify_t58_parent()
    _require(PREPARE_REPORT.is_file(), "缺少 T59 prepare_summary.json")
    preparation, prepare_sha256 = _read_json(PREPARE_REPORT)
    _require(preparation.get("schema") ==
             "GestureForge-S2A-T59-preparation-summary-v6" and
             preparation.get("task_id") == "S2A-T59" and
             preparation.get("run_id") == "run07" and
             preparation.get("status") == "PREPARED_NOT_SIMULATED" and
             preparation.get("baseline_head") == BASE_HEAD and
             preparation.get("scope") ==
             "tiny416 cfg section36 layer35; all 256 output channels at y=23, x=0..25" and
             preparation.get("tb_io_paths") == _verify_tb_run_paths() and
             preparation.get("bindings", {}).get("fixed_points_yx") ==
             [list(point) for point in POINTS] and
             preparation.get("T58_parent") == t58_parent,
             "T59 prepare_summary schema、状态、范围或基线不匹配")
    recorded_head = str(preparation.get("current_head", ""))
    current_head = _current_head()
    _require_head_descends_from(BASE_HEAD, recorded_head, "T59 记录的 current_head")
    _require_head_descends_from(recorded_head, current_head,
                                "当前 HEAD 相对 T59 记录的 current_head")
    manifest, _, _ = _verify_prepared_fixture(preparation)
    revalidated_head = _verify_runtime_oracle(preparation)
    _require(revalidated_head == current_head,
             "T59 verify-only 期间 Git HEAD 发生变化")

    project_record = preparation.get("project_preflight", {})
    _require(project_record.get("path") == str(PROJECT_PREFLIGHT.resolve()) and
             PROJECT_PREFLIGHT.is_file(),
             "T59 prepare_summary 的只读工程预检路径不匹配")
    project_binding, project_sha256 = _read_json(PROJECT_PREFLIGHT)
    prior_attempts = _prior_attempts_record()
    _require(preparation.get("prior_attempts") == prior_attempts and
             manifest.get("prior_attempts") == prior_attempts and
             project_binding.get("prior_attempts") == prior_attempts,
             "T59 run07 未双向绑定保留的 run05/run06 历史尝试")
    current_xpr_sha256 = _sha_file(XPR_PATH)
    binding_record = preparation.get("bindings", {}).get(
        "project_preflight_binding")
    _require(isinstance(binding_record, dict),
             "T59 prepare_summary 缺少自身工程预检摘要绑定")
    _require(project_sha256 == project_record.get("sha256") ==
             binding_record.get("sha256") and
             project_record.get("bytes") == binding_record.get("bytes") and
             project_record.get("path") == binding_record.get("path") ==
             str(PROJECT_PREFLIGHT.resolve()) and
              project_binding.get("schema") ==
              "GestureForge-S2A-T59-project-preflight-v5" and
             project_binding.get("task_id") == "S2A-T59" and
              project_binding.get("run_id") == "run07" and
             project_binding.get("baseline_head") == BASE_HEAD and
             project_binding.get("current_head") == recorded_head and
             project_binding.get("run_directory") == str(RUN_ROOT.resolve()) and
             project_binding.get("project_xpr_path") == str(XPR_PATH.resolve()) and
             project_binding.get("target_xpr_sha256_before_prepare") ==
             current_xpr_sha256 ==
             project_binding.get("target_xpr_sha256_after_prepare") and
             project_binding.get("target_xpr_unchanged") is True and
             project_record.get("target_xpr_sha256") == current_xpr_sha256 and
             project_record.get("target_xpr_unchanged") is True,
             "T59 prepare_summary、manifest、本地工程预检与真实 XPR SHA 不一致")
    expected_source_hashes = _source_hashes()
    _require(project_binding.get("T59_source_hashes") == expected_source_hashes ==
             preparation.get("bindings", {}).get("T59_source_hashes"),
             "T59 工程预检绑定的源码哈希与当前文件不一致")
    preparation_inputs = {
        key: preparation.get("bindings", {}).get(key)
        for key in PREPARATION_INPUT_KEYS
    }
    _require(project_binding.get("preparation_inputs") == preparation_inputs,
             "T59 工程预检绑定与 prepare_summary 输入绑定不一致")
    _verify_upstream_records(preparation_inputs)
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
             "T59 工程预检绑定未指向冻结 G0/T01/T23/GF8/T56/oracle 输入")
    for name in (
        "T56_parent_report", "T56_summary", "T58_parent_prepare_summary",
        "T58_parent_fixture_manifest", "T58_parent_golden", "G0_specification",
        "T01_manifest", "T23_parameter_table", "GF8_package", "oracle_source",
        "T16_conv_requant_proof", "T17_conv_engine_evidence",
        "T20_layer_scheduler_evidence", "T16_requant_proof_source",
        "D2_forward_reference_source",
    ):
        record = preparation_inputs[name]
        _require(isinstance(record, dict), f"T59 输入绑定格式错误：{name}")
        source_path = _verify_file_record(record, f"T59 输入 {name}")
        _require(source_path.is_file(), f"T59 输入文件缺失：{name}")
    _require(project_binding.get("mcp_status") == "NOT_QUERIED" and
             project_binding.get("vivado_opened") is False and
             project_binding.get("vivado_cli_invoked") is False,
             "T59 工程预检不得声称查询 MCP 或打开/启动 Vivado")
    runtime = preparation.get("runtime_preflight", {})
    _require(runtime.get("path_chain_valid") is True and
             runtime.get("target_absent") is True and
             runtime.get("existing_run01") is True and
             runtime.get("existing_run02") is True and
             runtime.get("existing_run03") is True and
             runtime.get("existing_run04") is True and
             runtime.get("existing_run05") is True and
             runtime.get("existing_run06") is True and
             runtime.get("existing_run07") is False and
             runtime.get("root_binding_sha256") == ROOT_PROJECT_PREFLIGHT_SHA256 and
             runtime.get("process_names") == list(PROCESS_NAMES) and
             runtime.get("processes_before_prepare") == [] and
             runtime.get("processes_after_prepare") == {
                 "process_names": list(PROCESS_NAMES),
                 "processes": [],
                 "powershell_exit_code": 0,
             } and
             runtime.get("mcp_status") == "NOT_QUERIED" and
             project_binding.get("runtime_preflight") == runtime,
             "T59 prepare_summary 路径/进程/MCP 状态不匹配")
    postflight_now = _runtime_process_snapshot()
    _require(postflight_now["processes"] == [] and
             _project_xpr_sha() == current_xpr_sha256,
             "T59 verify-only 当前进程门禁或真实 XPR SHA 不匹配")
    _require(preparation.get("simulation", {}).get("status") == "NOT_RUN",
             "T59 当前证据不应包含仿真状态")
    expected_files = {
        "prepare_summary.json",
        "project_preflight_binding.json",
        "upstream_fail_closed_audit.json",
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
             f"T59 run07 文件集合不匹配：extra={sorted(actual_files - expected_files)} "
             f"missing={sorted(expected_files - actual_files)}")
    print(json.dumps({
        "result": "PREPARED_NOT_SIMULATED",
        "prepare_summary_sha256": prepare_sha256,
        "fixture_manifest_sha256": preparation["fixture"]["manifest"]["sha256"],
        "golden_sha256": preparation["oracle"]["combined_golden_sha256"],
        "baseline_head": BASE_HEAD,
        "prepared_current_head": recorded_head,
        "revalidated_current_head": current_head,
        "output_counts": {
            "raw_int32": RAW_COUNT,
            "int8": INT8_COUNT,
            "d2_t23_matches": INT8_COUNT,
        },
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
    except T59UpstreamShaMismatch as error:
        print("T59_FAILURE_JSON=" + json.dumps(
            error.failure_record, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"),
        ), file=sys.stderr, flush=True)
        print(f"FAIL T59 {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"FAIL T59 {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
