"""验证 layer36 通道0完整26行 tile16 空间 MAC、重定标与外存协议。"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import platform
import re
import subprocess
import tempfile
import time
import unittest
import uuid
from pathlib import Path
from typing import Any


_ROOT = Path(__file__).resolve().parents[1]
_BASELINE_HEAD = "3b1172f23454e2ceda6d9e9e47847690e2872f3d"
_VIVADO_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_INPUT_BASE = 27966080
_INPUT_BYTES = 173056
_OUTPUT_BASE = 28139136
_OUTPUT_BYTES = 20280
_WEIGHT_PACKAGE_BASE = 0x00100000
_WEIGHT_OFFSET = 5895420
_CHANNEL0_WEIGHT_BYTES = 256
_BIAS = -40
_FEATURE_REQUESTS = 46592
_WEIGHT_REQUESTS = 13312
_OUTPUT_WRITES = 676
_STALL_SEED = 0x20260927
_T16_PROOF_SHA256 = "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24"
_T16_SCRIPT_SHA256 = "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9"
_T20_RUNNER_SHA256 = "9474108ee39ed1d89113241ebaef1ac177a0d0cca6878dbfc1415f25543117c2"
_T20_EVIDENCE_SHA256 = "d6bc16966a2d3c7707d98aafa6b435ae158cd28faa53baa8f795e13e86a17887"
_T20_INPUT_SHA256 = "3ab3cb8aba6e67fe3ffa6b9b071c706a905563b125d4f500b814fa9d0092572b"
_T20_GOLDEN_SHA256 = "80462a11ba6e9e0f3ba2bfbf5c25e6c6db24bf884dd93d0c00d79b348f5a6bda"
_T30_RTL_SHA256 = "42ad5217e7be65b8fa255a587bb27382b10da7b32ede2ce6f24b2e7787b97fdb"
_T30_RUNNER_SHA256 = "9b9345a9d8d36b2f7ac53fd8ce27a24da21675bd0f36c68300e0a5c55ced4f45"
_T30_EVIDENCE_SHA256 = "eba77ffd0a94524dfc3844207bbbe646b064066ba346ba4b344b3e3425c58443"
_T31_EVIDENCE_SHA256 = "4704981f3d6882ad1f81e0794aab9886a7da23d0e9ac7c5aa83aef95be3357c1"
_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_G0_SHA256 = "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"
_D2_SHA256 = "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393"
_CHANNEL0_WEIGHT_SHA256 = "62b6b53c4f05027806a42e441e6de0a5d123fed4ff4dd4aff3299748772228d9"


class T32Error(RuntimeError):
    """报告冻结输入、仿真或综合失败。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T32Error(message)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _git_output(arguments: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *arguments], cwd=cwd, capture_output=True,
        text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        raise T32Error(
            f"git {' '.join(arguments)} 失败，exit={result.returncode}："
            f"{result.stderr.strip()}"
        )
    return result.stdout.strip()


def _read_git_head(cwd: Path) -> str:
    return _git_output(["rev-parse", "HEAD"], cwd)


def _is_ancestor(ancestor: str, descendant: str, cwd: Path) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise T32Error(
        "git merge-base --is-ancestor 执行失败，"
        f"exit={result.returncode}：{result.stderr.strip()}"
    )


def _require_baseline_ancestor(baseline: str, runtime_head: str, cwd: Path) -> None:
    _require(
        _is_ancestor(baseline, runtime_head, cwd),
        f"运行 HEAD 不属于冻结基线的后代：baseline={baseline} runtime={runtime_head}",
    )


def _require_stable_head(head_before: str, head_after: str) -> None:
    _require(
        head_before == head_after,
        f"验证期间 HEAD 发生变化：before={head_before} after={head_after}",
    )


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise T32Error(f"不能加载冻结 helper：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _signed_byte(value: int) -> int:
    value &= 0xFF
    return value if value < 128 else value - 256


def _raw_fullheight_oracle(input_bytes: bytes, channel0_weights: bytes) -> list[int]:
    """按 y、x、k 独立执行有序整数乘加，并逐步检查 signed INT32。"""
    _require(len(input_bytes) == _INPUT_BYTES, "layer36 输入张量字节数不符")
    _require(len(channel0_weights) == _CHANNEL0_WEIGHT_BYTES,
             "通道0权重字节数不符")
    outputs: list[int] = []
    for y in range(26):
        for x in range(26):
            accumulator = _BIAS
            for k in range(256):
                activation = _signed_byte(input_bytes[k * 676 + y * 26 + x])
                weight = _signed_byte(channel0_weights[k])
                _require(-127 <= activation <= 127 and -127 <= weight <= 127,
                         f"发现非法 INT8 -128：y={y} x={x} k={k}")
                accumulator += activation * weight
                _require(-(1 << 31) <= accumulator <= (1 << 31) - 1,
                         f"Python oracle 检出 INT32 溢出：y={y} x={x} k={k}")
            outputs.append(accumulator)
    return outputs


def _write_hex_bytes(path: Path, payload: bytes) -> None:
    path.write_text(
        "".join(f"{value:02x}\n" for value in payload),
        encoding="ascii", newline="\n",
    )


def _write_hex_words(path: Path, values: list[int]) -> None:
    path.write_text(
        "".join(f"{value & 0xFFFF_FFFF:08x}\n" for value in values),
        encoding="ascii", newline="\n",
    )


def _resource_value(report: str, labels: tuple[str, ...]) -> int:
    for label in labels:
        match = re.search(
            rf"^\s*(?:\|\s*)?{re.escape(label)}\s*\|\s*([0-9,]+)\s*\|",
            report, re.MULTILINE | re.IGNORECASE,
        )
        if match:
            return int(match.group(1).replace(",", ""))
    raise T32Error(f"Vivado utilization report 缺少资源字段：{labels}")


def _run_tool(
    name: str,
    tool: Path,
    arguments: list[str],
    work: Path,
    timeout_seconds: float = 600.0,
) -> dict[str, Any]:
    _require(tool.is_file(), f"未找到 Vivado 工具：{tool}")
    command = " ".join(
        f'"{argument}"' if " " in argument else argument
        for argument in [str(tool), *arguments]
    )
    started = time.monotonic()
    try:
        process = subprocess.run(
            f'cmd.exe /d /s /c "{command}"',
            cwd=work, shell=False, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        log_path = work / f"{name}.stdout.log"
        log_path.write_text(output, encoding="utf-8", newline="\n")
        raise T32Error(
            f"{name} 超过 {timeout_seconds:.0f}s；日志：{log_path}"
        ) from exc
    elapsed = time.monotonic() - started
    output = process.stdout + process.stderr
    log_path = work / f"{name}.stdout.log"
    log_path.write_text(output, encoding="utf-8", newline="\n")
    return {
        "name": name,
        "command": [str(tool), *arguments],
        "exit_code": process.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "stdout_log_path": str(log_path),
        "stdout_log_sha256": _sha256_file(log_path),
        "output": output,
    }


class S2ASpatialChannel0FullheightTests(unittest.TestCase):
    """绑定 T01/T16/T20/T30/T31 冻结数据并验证 full-height pilot。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = _ROOT
        cls.head_start = _read_git_head(cls.root)
        _require_baseline_ancestor(_BASELINE_HEAD, cls.head_start, cls.root)
        cls.rtl_path = cls.root / "src/s2a_conv_spatial_channel0_fullheight.sv"
        cls.tile_rtl_path = cls.root / "src/s2a_conv_spatial_tile16.sv"
        cls.tb_path = cls.root / "sim/tb_s2a_conv_spatial_channel0_fullheight.sv"
        cls.runner_path = Path(__file__).resolve()
        evidence_override = os.environ.get("S2A_T32_EVIDENCE_PATH")
        if evidence_override is None:
            cls.evidence_path = cls.root / (
                "report/evidence/S2A-T32/channel0_fullheight_pilot.json"
            )
        else:
            cls.evidence_path = Path(evidence_override)
            _require(cls.evidence_path.is_absolute(),
                     "S2A_T32_EVIDENCE_PATH 必须是绝对路径")
        _require(not os.path.lexists(str(cls.evidence_path)),
                 f"T32 evidence 已存在，拒绝覆盖：{cls.evidence_path}")
        for path in (cls.rtl_path, cls.tile_rtl_path, cls.tb_path):
            _require(path.is_file(), f"RTL/testbench 文件缺失：{path}")

        cls.g0_path = cls.root / (
            "docs/obsidian-project/04-提交材料/阶段验收/"
            "S2A-T01_模型交付规格与G0接口冻结.md"
        )
        cls.manifest_path = cls.root / "report/evidence/S2A-T01/tiny416_model_manifest.json"
        cls.d2_path = cls.root / "verification/s1_t02_d2_int8_forward.py"
        cls.t16_proof_path = cls.root / "report/evidence/S2A-T16/conv_requant_proof.json"
        cls.t16_script_path = cls.root / "verification/s2a_conv_requant_proof.py"
        cls.t20_path = cls.root / "verification/test_s2a_conv_layer_scheduler_rtl.py"
        cls.t20_evidence_path = cls.root / (
            "report/evidence/S2A-T20/conv_layer_scheduler_simulation.json"
        )
        cls.t30_evidence_path = cls.root / "report/evidence/S2A-T30/spatial_tile16_pilot.json"
        cls.t30_runner_path = cls.root / "verification/test_s2a_conv_spatial_tile16_rtl.py"
        cls.t31_path = cls.root / "src/s2a_conv_spatial_row0_pilot.sv"
        cls.t31_tb_path = cls.root / "sim/tb_s2a_conv_spatial_row0_pilot.sv"
        cls.t31_runner_path = cls.root / "verification/test_s2a_conv_spatial_row0_pilot_rtl.py"
        cls.t31_evidence_path = cls.root / "report/evidence/S2A-T31/spatial_row0_pilot.json"

        _require(_sha256_file(cls.g0_path) == _G0_SHA256,
                 "G0 冻结规格 SHA-256 不符")
        _require(_sha256_file(cls.manifest_path) == _MANIFEST_SHA256,
                 "T01 manifest SHA-256 不符")
        _require(_sha256_file(cls.d2_path) == _D2_SHA256,
                 "阶段一 D2 INT8 reference SHA-256 不符")
        _require(_sha256_file(cls.t16_proof_path) == _T16_PROOF_SHA256 and
                 _sha256_file(cls.t16_script_path) == _T16_SCRIPT_SHA256,
                 "T16 proof 或 proof script SHA-256 不符")
        _require(_sha256_file(cls.t20_path) == _T20_RUNNER_SHA256 and
                 _sha256_file(cls.t20_evidence_path) == _T20_EVIDENCE_SHA256,
                 "T20 runner/evidence SHA-256 不符")
        _require(_sha256_file(cls.tile_rtl_path) == _T30_RTL_SHA256 and
                 _sha256_file(cls.t30_runner_path) == _T30_RUNNER_SHA256 and
                 _sha256_file(cls.t30_evidence_path) == _T30_EVIDENCE_SHA256,
                 "T30 RTL/runner/evidence SHA-256 不符")
        _require(cls.t31_path.is_file() and cls.t31_tb_path.is_file() and
                 cls.t31_runner_path.is_file() and cls.t31_evidence_path.is_file(),
                 "T31 feeder 源码或 evidence 缺失")

        cls.t20 = _load_module("s2a_t32_t20_helpers", cls.t20_path)
        cls.t17 = cls.t20._load_t17_runner()
        cls.manifest, cls.t16_proof, cls.weights_by_layer, cls.package_path = (
            cls.t17._load_bound_inputs()
        )
        cls.layers = {int(row["layer_index"]): row for row in cls.manifest["layers"]}
        cls.layer = cls.layers[36]
        cls.source_layer = cls.layers[35]
        proof_layers = {
            int(row["layer_index"]): row for row in cls.t16_proof["layers"]
        }
        cls.parameters = cls.t17._candidate_parameters(cls.layer, proof_layers[36])
        cls.parameter0 = cls.parameters[0]
        _require(
            cls.layer.get("cfg_section") == 37 and
            cls.layer.get("input_shape_nchw") == [1, 256, 26, 26] and
            cls.layer.get("output_shape_nchw") == [1, 30, 26, 26] and
            cls.layer.get("kernel_hw") == [1, 1] and
            cls.layer.get("layout") == "NCHW" and
            cls.layer.get("activation") == "linear" and
            cls.layer.get("input_scale") == 0.12693486251230315 and
            cls.layer.get("output_scale") == 0.30223452951025775,
            "T01 layer36 shape/layout/activation/scales 不符",
        )
        _require(
            cls.layer.get("bias_accumulator_int32_per_output_channel", [None])[0] == _BIAS and
            cls.source_layer.get("tensor_address") == _INPUT_BASE and
            cls.source_layer.get("tensor_length_bytes") == _INPUT_BYTES and
            cls.source_layer.get("output_shape_nchw") == [1, 256, 26, 26] and
            cls.source_layer.get("output_scale") == cls.layer["input_scale"],
            "T01 输入边界或 channel0 INT32 bias 不符",
        )
        weight_map = cls.manifest["address_map"]["weight_package"]
        weight_offsets = cls.layer["gf8_parameter_offsets"]
        _require(
            int(weight_map["address"]) == _WEIGHT_PACKAGE_BASE and
            int(weight_offsets["quantized_weight_offset"]) == _WEIGHT_OFFSET and
            int(weight_offsets["quantized_weight_bytes"]) == 7680 and
            int(cls.manifest["address_map"]["head26"]["address"]
                if "head26" in cls.manifest["address_map"] else
                next(h["address"] for h in cls.manifest["address_map"]["heads"]
                     if h["name"] == "head26")) == _OUTPUT_BASE,
            "T01 GFINT8W1 或输出 slice 地址映射不符",
        )
        _require(
            cls.parameter0.get("positive_multiplier") == 4521539 and
            cls.parameter0.get("negative_multiplier") == 4521539 and
            cls.parameter0.get("positive_q_shift") == 33 and
            cls.parameter0.get("negative_q_shift") == 33,
            "T16 channel0 requant 参数不是共同 M/Q=4521539/33",
        )

        cls.layer_weights = cls.weights_by_layer[36]
        _require(len(cls.layer_weights) == 7680, "T01 layer36 权重长度不符")
        cls.channel0_weights = cls.layer_weights[:_CHANNEL0_WEIGHT_BYTES]
        _require(_sha256_bytes(cls.channel0_weights) == _CHANNEL0_WEIGHT_SHA256,
                 "T01/T17 channel0 权重 SHA-256 不符")
        cls.input_bytes, cls.sentinel_offsets = cls.t20._input_fixture()
        cls.golden_input, cls.full_golden, cls.golden_summary = cls.t20._input_and_golden(
            cls.layer, cls.layer_weights, cls.parameters, cls.t17,
        )
        _require(cls.input_bytes == cls.golden_input,
                 "T20 input fixture helper 重建结果不一致")
        _require(len(cls.input_bytes) == _INPUT_BYTES and
                 _sha256_bytes(cls.input_bytes) == _T20_INPUT_SHA256 and
                 len(cls.sentinel_offsets) == 675,
                 "T20 input fixture 长度/hash/sentinel 数量不符")
        _require(len(cls.full_golden) == _OUTPUT_BYTES and
                 _sha256_bytes(cls.full_golden) == _T20_GOLDEN_SHA256,
                 "T20 full golden 长度或 SHA-256 不符")
        cls.channel0_golden = bytes(cls.full_golden[:_OUTPUT_WRITES])
        cls.raw_values = _raw_fullheight_oracle(cls.input_bytes, cls.channel0_weights)
        _require(len(cls.raw_values) == _OUTPUT_WRITES,
                 "独立 raw oracle 未生成676个值")
        cls.quantized_cpu = bytes(
            int(cls.t17._fixed_point_quantize(value, cls.parameter0)) & 0xFF
            for value in cls.raw_values
        )
        _require(cls.quantized_cpu == cls.channel0_golden,
                 "T16 fixed-point CPU quantization 与 T20 full golden[0:676] 不符")

        cls.t20_evidence = json.loads(cls.t20_evidence_path.read_text(encoding="utf-8"))
        cls.t30_evidence = json.loads(cls.t30_evidence_path.read_text(encoding="utf-8"))
        cls.t31_evidence_bytes = cls.t31_evidence_path.read_bytes()
        cls.t31_evidence_sha256 = _sha256_bytes(cls.t31_evidence_bytes)
        _require(cls.t31_evidence_sha256 == _T31_EVIDENCE_SHA256,
                 "T31 frozen evidence SHA-256 不符")
        cls.t31_evidence = json.loads(cls.t31_evidence_bytes.decode("utf-8"))
        _require(cls.t20_evidence.get("task") == "S2A-T20" and
                 cls.t20_evidence.get("result") == "PASS" and
                 cls.t20_evidence.get("mode") == "FULL",
                 "T20 layer36 CPU golden evidence 不是 FULL/PASS")
        _require(cls.t30_evidence.get("task") == "S2A-T30" and
                 cls.t30_evidence.get("result") == "PASS",
                 "T30 tile16 evidence 不是 PASS")
        _require(cls.t31_evidence.get("task") == "S2A-T31" and
                 cls.t31_evidence.get("result") == "PASS",
                 "T31 row0 evidence 不是 PASS")
        _require(
            cls.t20_evidence.get("layer36", {}).get("input_base_address") == _INPUT_BASE and
            cls.t20_evidence.get("layer36", {}).get("input_length_bytes") == _INPUT_BYTES and
            cls.t20_evidence.get("layer36", {}).get("output_base_address") == _OUTPUT_BASE and
            cls.t20_evidence.get("layer36", {}).get("activation") == "linear" and
            cls.t20_evidence.get("fixture", {}).get("input_sha256_after_patch") ==
            _T20_INPUT_SHA256 and
            cls.t20_evidence.get("golden", {}).get("sha256") in (None, _T20_GOLDEN_SHA256),
            "T20 evidence layer/address/input fixture 与固定规格不符",
        )
        row0_raw = cls.raw_values[:26]
        row0_quant = [_signed_byte(value) for value in cls.channel0_golden[:26]]
        _require(cls.t31_evidence.get("cpu_reference", {}).get(
                     "channel0_raw_int32_by_x") == row0_raw and
                 cls.t31_evidence.get("cpu_reference", {}).get(
                     "channel0_cpu_quantized_reference_by_x") == row0_quant,
                 "T31 row0 raw/quantized 参考与 T32 重建不符")
        _require(
            cls.raw_values[:16] == list(map(int, cls.t30_evidence[
                "t20_cpu_reference"]["tile_raw_accumulators_int32"])) and
            [_signed_byte(value) for value in cls.channel0_golden[:16]] == list(map(
                int, cls.t30_evidence["t20_cpu_reference"]["tile_quantized_bytes_signed"])),
            "T30 tile16 前16个 CPU 参考与 T32 oracle 不符",
        )
        _require(
            cls.t31_evidence.get("frozen_layer36", {}).get(
                "channel0_requant_parameters_from_t16", {}).get("positive_multiplier") == 4521539 and
            cls.t31_evidence.get("frozen_layer36", {}).get(
                "channel0_requant_parameters_from_t16", {}).get("positive_q_shift") == 33 and
            cls.t31_evidence.get("cpu_reference", {}).get(
                "T20_full_layer_golden_sha256") == _T20_GOLDEN_SHA256,
            "T31 evidence 未绑定相同 T16/T20 参数与 golden",
        )

        cls.source_paths = {
            "g0_spec": cls.g0_path,
            "t01_manifest": cls.manifest_path,
            "d2_int8_forward": cls.d2_path,
            "t16_proof": cls.t16_proof_path,
            "t16_proof_script": cls.t16_script_path,
            "t17_runner": cls.root / "verification/test_s2a_conv_engine_rtl.py",
            "t17_engine": cls.root / "src/s2a_conv_engine.sv",
            "t17_geometry": cls.root / "src/int8_conv_tap_geometry.sv",
            "t17_weight_address": cls.root / "src/int8_conv_weight_address.sv",
            "t17_mac": cls.root / "src/int8_mac_accumulator.sv",
            "t17_testbench": cls.root / "sim/tb_s2a_conv_engine.sv",
            "t17_evidence": cls.root / "report/evidence/S2A-T17/conv_engine_simulation.json",
            "t20_runner": cls.t20_path,
            "t20_scheduler": cls.root / "src/s2a_conv_layer_scheduler.sv",
            "t20_testbench": cls.root / "sim/tb_s2a_conv_layer_scheduler.sv",
            "t20_evidence": cls.t20_evidence_path,
            "t30_tile16_rtl": cls.tile_rtl_path,
            "t30_testbench": cls.root / "sim/tb_s2a_conv_spatial_tile16.sv",
            "t30_runner": cls.t30_runner_path,
            "t30_evidence": cls.t30_evidence_path,
            "t31_feeder_rtl": cls.t31_path,
            "t31_testbench": cls.t31_tb_path,
            "t31_runner": cls.t31_runner_path,
            "t31_evidence": cls.t31_evidence_path,
            "t32_fullheight_rtl": cls.rtl_path,
            "t32_testbench": cls.tb_path,
            "t32_runner": cls.runner_path,
            "gfint8w1_package": cls.package_path,
        }
        for name, path in cls.source_paths.items():
            _require(path.is_file(), f"证据绑定源文件缺失：{name} {path}")
        cls.source_hashes = {
            name: _sha256_file(path) for name, path in cls.source_paths.items()
        }
        t20_hashes = cls.t20_evidence.get("bindings", {}).get("t20_sha256", {})
        _require(
            t20_hashes.get("t20_runner") == cls.source_hashes["t20_runner"] and
            t20_hashes.get("t20_scheduler") == cls.source_hashes["t20_scheduler"] and
            t20_hashes.get("t20_testbench") == cls.source_hashes["t20_testbench"],
            "T20 evidence 中 frozen runner/scheduler/testbench SHA 不符",
        )
        dependency_hashes = cls.t20_evidence.get("bindings", {}).get(
            "dependency_sha256", {}
        )
        for evidence_key, source_key in (
            ("t17_engine", "t17_engine"),
            ("t17_geometry", "t17_geometry"),
            ("t17_weight_address", "t17_weight_address"),
            ("t17_mac", "t17_mac"),
            ("t17_testbench", "t17_testbench"),
            ("t17_runner", "t17_runner"),
            ("t17_evidence", "t17_evidence"),
        ):
            _require(dependency_hashes.get(evidence_key) == cls.source_hashes[source_key],
                     f"T20 evidence 中 {evidence_key} dependency hash 不符")
        t31_bindings = cls.t31_evidence.get("source_bindings_sha256", {})
        _require(
            t31_bindings.get("t30_tile16_rtl") == cls.source_hashes["t30_tile16_rtl"] and
            t31_bindings.get("t20_runner") == cls.source_hashes["t20_runner"] and
            t31_bindings.get("t20_evidence") == cls.source_hashes["t20_evidence"],
            "T31 evidence 中 T30/T20 依赖 hash 不符",
        )
        cls.raw_reference_bytes = b"".join(
            (value & 0xFFFF_FFFF).to_bytes(4, "little") for value in cls.raw_values
        )
        print(
            "T32_PREFLIGHT_PASS head={} input_sha256={} golden_sha256={} "
            "weight_sha256={} raw_values=676".format(
                cls.head_start, _sha256_bytes(cls.input_bytes),
                _sha256_bytes(cls.full_golden), _sha256_bytes(cls.channel0_weights),
            ),
            flush=True,
        )

    def test_frozen_reference_and_parameters(self) -> None:
        self.assertEqual(len(self.raw_values), _OUTPUT_WRITES)
        self.assertEqual(len(self.channel0_golden), _OUTPUT_WRITES)
        self.assertEqual(self.parameter0.get("positive_multiplier"), 4521539)
        self.assertEqual(self.parameter0.get("negative_multiplier"), 4521539)
        self.assertEqual(self.parameter0.get("positive_q_shift"), 33)
        self.assertEqual(self.parameter0.get("negative_q_shift"), 33)
        self.assertEqual(self.layer.get("activation"), "linear")
        self.assertEqual(self.quantized_cpu, self.channel0_golden)

    def test_git_ancestry_policy(self) -> None:
        self.assertTrue(_is_ancestor(_BASELINE_HEAD, self.head_start, self.root))
        with self.assertRaises(T32Error):
            _require_baseline_ancestor("0" * 40, self.head_start, self.root)

    def test_vivado_simulation_and_standalone_synthesis(self) -> None:
        work_override = os.environ.get("S2A_T32_WORK_DIR")
        if work_override is None:
            temp_root = Path(os.environ.get("TEMP", tempfile.gettempdir()))
            work = temp_root / f"s2a_t32_channel0_fullheight_{uuid.uuid4().hex}"
        else:
            work = Path(work_override)
        _require(work.is_absolute(), "S2A_T32_WORK_DIR 必须是绝对路径")
        _require(not os.path.lexists(str(work)), f"TEMP 工作目录已存在，拒绝复用：{work}")
        _require(work.parent.is_dir(), f"TEMP 父目录不存在：{work.parent}")
        work.mkdir()
        progress_path = work / "progress.log"
        phases: list[dict[str, Any]] = []

        def progress(message: str) -> None:
            with progress_path.open("a", encoding="utf-8", newline="\n") as stream:
                stream.write(message + "\n")
            print(message, flush=True)

        head_before = _read_git_head(self.root)
        _require_baseline_ancestor(_BASELINE_HEAD, head_before, self.root)
        _require_stable_head(self.head_start, head_before)
        source_hashes_before = {
            name: _sha256_file(path) for name, path in self.source_paths.items()
        }
        self.assertEqual(source_hashes_before, self.source_hashes,
                         "冻结源在 preflight 后发生变化")
        progress(f"PREFLIGHT_PASS work={work} evidence={self.evidence_path} head={head_before}")

        fixture_paths = {
            "input": work / "input_fixture.hex",
            "weights": work / "channel0_weights.hex",
            "expected_raw": work / "expected_raw.hex",
            "expected_golden": work / "expected_golden.hex",
        }
        _write_hex_bytes(fixture_paths["input"], self.input_bytes)
        _write_hex_bytes(fixture_paths["weights"], self.channel0_weights)
        _write_hex_words(fixture_paths["expected_raw"], self.raw_values)
        _write_hex_bytes(fixture_paths["expected_golden"], self.channel0_golden)
        fixture_evidence = {
            name: {
                "path": str(path),
                "bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
            for name, path in fixture_paths.items()
        }
        progress("FIXTURE_READY input_bytes={} raw_values={} golden_bytes={} input_sha256={}".format(
            len(self.input_bytes), len(self.raw_values), len(self.channel0_golden),
            _sha256_bytes(self.input_bytes),
        ))

        xvlog = _VIVADO_BIN / "xvlog.bat"
        xelab = _VIVADO_BIN / "xelab.bat"
        xsim = _VIVADO_BIN / "xsim.bat"
        phases_spec = [
            ("xvlog", xvlog, ["-sv", str(self.tile_rtl_path),
                                str(self.rtl_path), str(self.tb_path)]),
            ("xelab", xelab, ["-top", "tb_s2a_conv_spatial_channel0_fullheight",
                               "-snapshot", "s2a_t32_fullheight_snapshot"]),
            ("xsim", xsim, ["-R", "s2a_t32_fullheight_snapshot"]),
        ]
        sim_output = ""
        for name, tool, arguments in phases_spec:
            progress(f"PHASE_START {name} command={[str(tool), *arguments]}")
            phase = _run_tool(name, tool, arguments, work)
            phases.append(phase)
            self.assertEqual(
                phase["exit_code"], 0,
                f"{name} exit={phase['exit_code']}；日志尾部：\n{phase['output'][-6000:]}",
            )
            if name == "xsim":
                sim_output = phase["output"]
                self.assertNotIn("FAIL:", sim_output,
                                 "xsim 输出包含 FAIL 标记")
            progress("PHASE_PASS {} exit_code={} elapsed_seconds={}".format(
                name, phase["exit_code"], phase["elapsed_seconds"],
            ))

        summary_match = re.search(r"^PASS: requests=.*$", sim_output, re.MULTILINE)
        self.assertIsNotNone(summary_match, "xsim 缺少唯一 PASS protocol summary")
        self.assertEqual(sim_output.count("S2A_T32_SIM_PASS"), 1,
                         "xsim PASS marker 必须恰好出现一次")
        summary = {
            key: int(value)
            for key, value in re.findall(
                r"([a-z0-9_]+)=([0-9]+)", summary_match.group(0),
            )
        }
        expected_summary = {
            "requests": 60580,
            "feature_reads": _FEATURE_REQUESTS,
            "feature_bytes": _INPUT_BYTES,
            "weight_reads": _WEIGHT_REQUESTS,
            "weight_bytes": _WEIGHT_REQUESTS,
            "output_writes": _OUTPUT_WRITES,
            "raw_compares": _OUTPUT_WRITES,
            "error_codes": 3,
            "abort_cancel": 1,
            "reset_cancel": 1,
            "output_abort_cancel": 1,
            "output_reset_cancel": 1,
            "output_cancel_handshakes": 0,
            "recovery": 1,
            "seed": _STALL_SEED,
        }
        self.assertGreater(summary.get("stalls", 0), 0,
                           "仿真未覆盖 stalled memory request")
        for key, value in expected_summary.items():
            self.assertEqual(summary.get(key), value, f"xsim summary {key} 不符")

        tcl_path = work / "synth_channel0_fullheight.tcl"
        utilization_path = work / "utilization.rpt"
        tcl_text = (
            f"read_verilog -sv {{{self.tile_rtl_path.as_posix()}}}\n"
            f"read_verilog -sv {{{self.rtl_path.as_posix()}}}\n"
            "synth_design -top s2a_conv_spatial_channel0_fullheight -part xc7z020clg400-1\n"
            f"report_utilization -file {{{utilization_path.as_posix()}}}\n"
            "puts \"S2A_T32_SYNTH_PASS\"\n"
            "exit\n"
        )
        tcl_path.write_text(tcl_text, encoding="utf-8", newline="\n")
        vivado = _VIVADO_BIN / "vivado.bat"
        synth_arguments = [
            "-mode", "batch", "-source", str(tcl_path),
            "-log", str(work / "vivado_native.log"),
            "-journal", str(work / "vivado_native.jou"),
        ]
        progress(f"PHASE_START standalone_synthesis command={[str(vivado), *synth_arguments]}")
        synthesis = _run_tool("standalone_synthesis", vivado, synth_arguments, work)
        phases.append(synthesis)
        self.assertEqual(
            synthesis["exit_code"], 0,
            f"standalone synth exit={synthesis['exit_code']}；"
            f"日志尾部：\n{synthesis['output'][-6000:]}",
        )
        self.assertIn("S2A_T32_SYNTH_PASS", synthesis["output"])
        self.assertTrue(utilization_path.is_file(), "Vivado utilization report 缺失")
        utilization_text = utilization_path.read_text(encoding="utf-8", errors="replace")
        resources = {
            "lut": _resource_value(utilization_text,
                                   ("Slice LUTs*", "Slice LUTs", "CLB LUTs")),
            "ff": _resource_value(utilization_text,
                                  ("Slice Registers", "CLB Registers")),
            "bram_tile": _resource_value(utilization_text, ("Block RAM Tile",)),
            "dsp": _resource_value(utilization_text, ("DSPs",)),
        }
        progress(f"PHASE_PASS standalone_synthesis exit_code=0 resources={resources}")

        head_after = _read_git_head(self.root)
        _require_baseline_ancestor(_BASELINE_HEAD, head_after, self.root)
        _require_stable_head(head_before, head_after)
        source_hashes_after = {
            name: _sha256_file(path) for name, path in self.source_paths.items()
        }
        self.assertEqual(source_hashes_after, source_hashes_before,
                         "验证期间冻结源发生变化")
        _require(not os.path.lexists(str(self.evidence_path)),
                 f"T32 evidence 目标在验证期间出现，拒绝覆盖：{self.evidence_path}")

        evidence = {
            "schema_version": 1,
            "task": "S2A-T32",
            "result": "PASS",
            "scope": "tiny416 layer36 channel0 26x26 full-height spatial MAC/requant/output pilot",
            "baseline_git_head": _BASELINE_HEAD,
            "runtime_git_head_start": head_before,
            "runtime_git_head_end": head_after,
            "source_bindings_sha256": source_hashes_after,
            "frozen_layer36": {
                "model": "tiny416",
                "layer_index": 36,
                "cfg_section": 37,
                "input_shape_nchw": [1, 256, 26, 26],
                "output_shape_nchw": [1, 30, 26, 26],
                "kernel_hw": [1, 1],
                "layout": "NCHW",
                "activation": "linear",
                "input_base_address": _INPUT_BASE,
                "input_length_bytes": _INPUT_BYTES,
                "input_address": "base+k*676+y*26+x",
                "output_base_address": _OUTPUT_BASE,
                "output_slice_bytes": _OUTPUT_WRITES,
                "output_address": "base+y*26+x",
                "channel0_weight_byte_base": _WEIGHT_PACKAGE_BASE + _WEIGHT_OFFSET,
                "channel0_weight_bytes": _CHANNEL0_WEIGHT_BYTES,
                "channel0_weight_sha256": _sha256_bytes(self.channel0_weights),
                "channel0_bias_int32": _BIAS,
                "channel0_requant_parameters": {
                    key: int(value) for key, value in self.parameter0.items()
                    if key in ("positive_multiplier", "positive_q_shift",
                               "negative_multiplier", "negative_q_shift")
                },
            },
            "reference": {
                "input_fixture_helper": "verification/test_s2a_conv_layer_scheduler_rtl.py::_input_fixture",
                "golden_helper": "verification/test_s2a_conv_layer_scheduler_rtl.py::_input_and_golden",
                "input_generator": "T20 T10 address XOR byte pattern; raw 0x80 sentinel patched to zero",
                "input_random_seed": None,
                "input_bytes": len(self.input_bytes),
                "input_sha256": _sha256_bytes(self.input_bytes),
                "patched_minus128_sentinel_count": len(self.sentinel_offsets),
                "channel0_weights_sha256": _sha256_bytes(self.channel0_weights),
                "raw_oracle": "Python y/x/k ordered signed INT8 multiply-accumulate with per-step signed INT32 bounds",
                "raw_accumulator_count": len(self.raw_values),
                "raw_accumulator_le_i32_sha256": _sha256_bytes(self.raw_reference_bytes),
                "raw_accumulators_compared_in_testbench": summary["raw_compares"],
                "t16_quantized_channel0_bytes": _OUTPUT_WRITES,
                "cpu_quantized_matches_full_golden_channel0": self.quantized_cpu ==
                self.channel0_golden,
                "full_golden_bytes": len(self.full_golden),
                "full_golden_sha256": _sha256_bytes(self.full_golden),
                "channel0_golden_bytes": len(self.channel0_golden),
                "channel0_golden_sha256": _sha256_bytes(self.channel0_golden),
                "python_version": platform.python_version(),
                "numpy_version": self.t17.np.__version__,
                "oracle_bias_int32": _BIAS,
            },
            "memory_protocol": {
                "aligned_word_bytes": 4,
                "byte_order": "little-endian; byte lane n maps to mem_addr+n",
                "single_outstanding": True,
                "request_fields_stable_until_handshake": True,
                "read_strobe_nonzero": True,
                "output_write_strobe_onehot": True,
                "normal_feature_requests": summary["feature_reads"],
                "normal_selected_feature_bytes": summary["feature_bytes"],
                "normal_weight_requests": summary["weight_reads"],
                "normal_selected_weight_bytes": summary["weight_bytes"],
                "normal_output_writes": summary["output_writes"],
                "selected_feature_byte_coverage_exact_once": True,
                "selected_weight_byte_uses_per_address": 52,
                "output_addresses_and_strobes_exact": True,
                "little_endian_read_data_checked": True,
                "memory_errors_propagated": [1, 2, 6],
                "fault_phases": {
                    "error_1": "first weight request",
                    "error_2": "directed mid-run read after 30000 accepted requests",
                    "error_6": "final output byte write",
                },
                "pending_abort_cancellations": summary["abort_cancel"],
                "pending_reset_cancellations": summary["reset_cancel"],
                "pending_output_write_abort_cancellations": summary[
                    "output_abort_cancel"
                ],
                "pending_output_write_reset_cancellations": summary[
                    "output_reset_cancel"
                ],
                "pending_output_write_handshakes_while_stalled": summary[
                    "output_cancel_handshakes"
                ],
                "successful_recovery_runs": summary["recovery"],
                "no_timeout_counter_added": True,
                "stall_seed": _STALL_SEED,
                "observed_stall_cycles": summary["stalls"],
            },
            "stimulus": {
                "fixtures": fixture_evidence,
                "work_directory": str(work),
                "work_directory_absolute": True,
                "evidence_written_after_all_phases_passed": True,
            },
            "simulation": {
                "simulator": "Vivado xvlog/xelab/xsim v2026.1",
                "commands": [phase["command"] for phase in phases[:3]],
                "phases": [
                    {key: value for key, value in phase.items() if key != "output"}
                    for phase in phases[:3]
                ],
                "testbench_summary": summary,
                "unique_pass_marker": "S2A_T32_SIM_PASS",
                "raw_values_compared": _OUTPUT_WRITES,
                "requantized_output_bytes_compared": _OUTPUT_WRITES,
                "tool_version_lines": {
                    phase["name"]: next((line.strip() for line in phase["output"].splitlines()
                                         if "Vivado" in line or "vivado" in line), "")
                    for phase in phases[:3]
                },
            },
            "standalone_synthesis": {
                "tool": "Vivado v2026.1",
                "top": "s2a_conv_spatial_channel0_fullheight",
                "rtl_inputs": [str(self.tile_rtl_path), str(self.rtl_path)],
                "part": "xc7z020clg400-1",
                "opened_project_xpr": False,
                "utilization": resources,
                "phase_exit_code": synthesis["exit_code"],
                "phase_elapsed_seconds": synthesis["elapsed_seconds"],
                "tcl_path": str(tcl_path),
                "stdout_log_path": synthesis["stdout_log_path"],
                "stdout_log_sha256": synthesis["stdout_log_sha256"],
                "utilization_report_path": str(utilization_path),
                "utilization_report_sha256": _sha256_file(utilization_path),
                "timing_constraints_applied": False,
                "timing_conclusion": "未提供 XDC/时钟约束；不作时序结论。",
            },
            "limits": [
                "这是 tiny416 layer36 通道0 26x26 的 full-height pilot，不代表 layer36 全输出通道、完整卷积层或整网通过。",
                "仅使用 T20 确定性输入 helper、T01/T16 参数和 T20 CPU full golden；未读取 T24/T25 tensor shards 或图像。",
                "memory interface 为仿真的 aligned 32-bit single-outstanding 抽象，不代表物理 AXI/DMA 集成。",
                "综合只覆盖本 pilot 与 T30 tile16 RTL，不加载 XPR/XDC；不作时序结论，也不代表全系统资源。",
                "未操作板卡、未使用 Vitis、未进入阶段2B/3，不能据此宣称 G4/G5。",
            ],
        }
        self.evidence_path.parent.mkdir(parents=True, exist_ok=True)
        with self.evidence_path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
        evidence_sha = _sha256_file(self.evidence_path)
        progress(f"EVIDENCE_WRITTEN path={self.evidence_path} sha256={evidence_sha}")
        print(
            "S2A_T32_PASS evidence={} evidence_sha256={} work={} resources={}".format(
                self.evidence_path, evidence_sha, work, resources,
            ),
            flush=True,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
