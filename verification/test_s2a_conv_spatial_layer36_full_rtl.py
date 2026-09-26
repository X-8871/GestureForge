"""验证 tiny416 layer36 的30通道空间卷积 RTL pilot。"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
import queue
import re
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True

_ROOT = Path(__file__).resolve().parents[1]
_BASELINE_HEAD = "b936273269de96e088a8790e5375006c9e7afd6b"
_VIVADO_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_INPUT_BASE = 27966080
_INPUT_BYTES = 173056
_K = 256
_HEIGHT = 26
_WIDTH = 26
_PIXELS = _HEIGHT * _WIDTH
_OUTPUT_BASE = 28139136
_OUTPUT_CHANNELS = 30
_OUTPUT_BYTES = _OUTPUT_CHANNELS * _PIXELS
_WEIGHT_PACKAGE_BASE = 0x00100000
_WEIGHT_OFFSET = 5895420
_WEIGHT_PACKAGE_BYTES = 5903100
_WEIGHT_BYTES = _OUTPUT_CHANNELS * _K
_STALL_SEED = 0x20260927
_T32_EVIDENCE_SHA256 = "ce8d7b2221804a016e36bb91412485b9cf43cef0f51c8eea5e780687156d4a06"
_PINNED_SHA256 = {
    "g0_spec": "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    "t01_manifest": "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    "d2_int8_forward": "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393",
    "t16_proof": "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24",
    "t16_proof_script": "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9",
    "t17_runner": "adbb7e2574c50fd8e702e386a0898d27a0e4a16aebfc782436e386d56c768357",
    "t17_engine": "8656f43f510a8f7c74aaee44f809da74adeb3b8c5fed32f8f009aabecb05c994",
    "t17_geometry": "109b58473fa2f5d6de5c362e0c780ae2e98bce260c1d92714fde58ae706e4bbc",
    "t17_weight_address": "0914df477c9e160d227c74f9eaf926e502069e563145e1e1f3e03673654d4592",
    "t17_mac": "b3f6a425e2db58b86c63524b9caf0019ddf7a103c5b66f8bfcc3cf86966d0a74",
    "t17_testbench": "2b642eb47cded4644e4e9ba3a1e3fa60d484cf795ec6e51dd8d4cfcc97d2f001",
    "t17_evidence": "4cd1d0f0e5edf7b34907179dea47a9a9c0994eb1d8bd89adfa341067cac17ab2",
    "t20_runner": "9474108ee39ed1d89113241ebaef1ac177a0d0cca6878dbfc1415f25543117c2",
    "t20_evidence": "d6bc16966a2d3c7707d98aafa6b435ae158cd28faa53baa8f795e13e86a17887",
    "t30_tile16_rtl": "42ad5217e7be65b8fa255a587bb27382b10da7b32ede2ce6f24b2e7787b97fdb",
    "t30_testbench": "8f2ef37d655557fe5d76a1afbb2ed47f1481cbf907ff2c3764c7a397e9f19483",
    "t30_runner": "9b9345a9d8d36b2f7ac53fd8ce27a24da21675bd0f36c68300e0a5c55ced4f45",
    "t30_evidence": "eba77ffd0a94524dfc3844207bbbe646b064066ba346ba4b344b3e3425c58443",
    "t31_feeder_rtl": "1be8b52858b562ceb24ba186eddd7485f0b43d1cebd4ae490b063e35d359bfdc",
    "t31_testbench": "a6184ab82eeb401f7601bbbc41c616982e4092b271525597cd20d47f9f4ff79b",
    "t31_runner": "dda5f4e2552f46ec7da4602d6af6bfdf0616a6d7a5b41b8b256497af44baf6b6",
    "t31_evidence": "4704981f3d6882ad1f81e0794aab9886a7da23d0e9ac7c5aa83aef95be3357c1",
    "t32_fullheight_rtl": "3ada6f32de9b96fe1b16a8cb2caed8bafd5445f0348fafab446352516088be4d",
    "t32_testbench": "e5a63a27846faba0d503ff1a58ae7a4ed599d7e4e2aaeb0174004f69a30d286f",
    "t32_runner": "6cebdbda87a85a2da1dd319cf1763305ef4b0b3a9e6304797a5db9c740c3b613",
}
_DEFAULT_EVIDENCE = _ROOT / "report/evidence/S2A-T33/layer36_spatial_full.json"
_RTL_PATH = _ROOT / "src/s2a_conv_spatial_layer36_full.sv"
_TILE_RTL_PATH = _ROOT / "src/s2a_conv_spatial_tile16.sv"
_TB_PATH = _ROOT / "sim/tb_s2a_conv_spatial_layer36_full.sv"
_RUNNER_PATH = Path(__file__).resolve()
_T32_EVIDENCE_PATH = _ROOT / "report/evidence/S2A-T32/channel0_fullheight_pilot.json"


class T33Error(RuntimeError):
    """报告 T33 冻结依赖、黄金数据、仿真或综合失败。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T33Error(message)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _git(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *arguments], cwd=_ROOT, capture_output=True,
        text=True, encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise T33Error(
            f"git {' '.join(arguments)} 失败，exit={result.returncode}："
            f"{result.stderr.strip()}"
        )
    return result


def _head() -> str:
    return _git(["rev-parse", "HEAD"]).stdout.strip()


def _is_ancestor(ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=_ROOT, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise T33Error(
        "git merge-base --is-ancestor 执行失败，"
        f"exit={result.returncode}：{result.stderr.strip()}"
    )


def _require_head_ancestor(head: str) -> None:
    _require(
        _is_ancestor(_BASELINE_HEAD, head),
        f"运行 HEAD 不属于 T32 基线后代：baseline={_BASELINE_HEAD} runtime={head}",
    )


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise T33Error(f"不能加载冻结 helper：{path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _verify_rtl_parameter_tables(reference_layer: dict[str, Any],
                                parameters: list[dict[str, int]]) -> None:
    """逐项核对 RTL 中的常量 ROM 与 T01/T16 通道表。"""
    source = _RTL_PATH.read_text(encoding="utf-8")

    def table_values(name: str, pattern: str) -> list[int]:
        match = re.search(
            rf"localparam logic \[\d+:0\] {name} = \{{(.*?)\}};",
            source, re.DOTALL,
        )
        _require(match is not None, f"RTL 缺少 {name}")
        return [int(value, 16 if "'h" in token.lower() else 10)
                for token, value in re.findall(pattern, match.group(1))]

    raw_biases = table_values("BIAS_TABLE", r"(32'h([0-9a-fA-F]{8}))")
    rtl_biases = []
    for value in reversed(raw_biases):
        rtl_biases.append(value - (1 << 32) if value & (1 << 31) else value)
    expected_biases = list(map(int, reference_layer[
        "bias_accumulator_int32_per_output_channel"]))
    _require(rtl_biases == expected_biases, "RTL bias ROM 与 T01 per-channel bias 不一致")

    raw_multipliers = table_values("MULTIPLIER_TABLE", r"(32'd(\d+))")
    rtl_multipliers = list(reversed(raw_multipliers))
    expected_multipliers = [int(row["positive_multiplier"]) for row in parameters]
    _require(rtl_multipliers == expected_multipliers,
             "RTL multiplier ROM 与 T16 per-channel table 不一致")

    raw_shifts = table_values("Q_SHIFT_TABLE", r"(6'd(\d+))")
    rtl_shifts = list(reversed(raw_shifts))
    expected_shifts = [int(row["positive_q_shift"]) for row in parameters]
    _require(rtl_shifts == expected_shifts,
             "RTL Q-shift ROM 与 T16 per-channel table 不一致")
    _require(re.search(r"localparam logic \[59:0\] ACTIVATION_TABLE = 60'd0;", source)
             is not None and reference_layer.get("activation") == "linear",
             "RTL activation ROM 与 T01 linear activation 不一致")


def _source_paths() -> dict[str, Path]:
    return {
        "g0_spec": _ROOT / "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md",
        "t01_manifest": _ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json",
        "d2_int8_forward": _ROOT / "verification/s1_t02_d2_int8_forward.py",
        "t16_proof": _ROOT / "report/evidence/S2A-T16/conv_requant_proof.json",
        "t16_proof_script": _ROOT / "verification/s2a_conv_requant_proof.py",
        "t17_runner": _ROOT / "verification/test_s2a_conv_engine_rtl.py",
        "t17_engine": _ROOT / "src/s2a_conv_engine.sv",
        "t17_geometry": _ROOT / "src/int8_conv_tap_geometry.sv",
        "t17_weight_address": _ROOT / "src/int8_conv_weight_address.sv",
        "t17_mac": _ROOT / "src/int8_mac_accumulator.sv",
        "t17_testbench": _ROOT / "sim/tb_s2a_conv_engine.sv",
        "t17_evidence": _ROOT / "report/evidence/S2A-T17/conv_engine_simulation.json",
        "t20_runner": _ROOT / "verification/test_s2a_conv_layer_scheduler_rtl.py",
        "t20_scheduler": _ROOT / "src/s2a_conv_layer_scheduler.sv",
        "t20_testbench": _ROOT / "sim/tb_s2a_conv_layer_scheduler.sv",
        "t20_evidence": _ROOT / "report/evidence/S2A-T20/conv_layer_scheduler_simulation.json",
        "t30_tile16_rtl": _TILE_RTL_PATH,
        "t30_testbench": _ROOT / "sim/tb_s2a_conv_spatial_tile16.sv",
        "t30_runner": _ROOT / "verification/test_s2a_conv_spatial_tile16_rtl.py",
        "t30_evidence": _ROOT / "report/evidence/S2A-T30/spatial_tile16_pilot.json",
        "t31_feeder_rtl": _ROOT / "src/s2a_conv_spatial_row0_pilot.sv",
        "t31_testbench": _ROOT / "sim/tb_s2a_conv_spatial_row0_pilot.sv",
        "t31_runner": _ROOT / "verification/test_s2a_conv_spatial_row0_pilot_rtl.py",
        "t31_evidence": _ROOT / "report/evidence/S2A-T31/spatial_row0_pilot.json",
        "t32_fullheight_rtl": _ROOT / "src/s2a_conv_spatial_channel0_fullheight.sv",
        "t32_testbench": _ROOT / "sim/tb_s2a_conv_spatial_channel0_fullheight.sv",
        "t32_runner": _ROOT / "verification/test_s2a_conv_spatial_channel0_fullheight_rtl.py",
        "t32_evidence": _T32_EVIDENCE_PATH,
        "t33_full_layer_rtl": _RTL_PATH,
        "t33_testbench": _TB_PATH,
        "t33_runner": _RUNNER_PATH,
    }


def _validate_t32_before_json(paths: dict[str, Path]) -> tuple[bytes, dict[str, str]]:
    """先核对冻结 T32 evidence 字节哈希，再允许解析其 JSON。"""
    path = paths["t32_evidence"]
    _require(path.is_file(), f"T32 evidence 缺失：{path}")
    raw = path.read_bytes()
    actual = _sha256_bytes(raw)
    _require(actual == _T32_EVIDENCE_SHA256,
             f"T32 evidence baseline SHA-256 不符：{actual}")
    hashes = {}
    for name, source in paths.items():
        _require(source.is_file(), f"冻结依赖缺失：{name} {source}")
        payload = source.read_bytes()
        if name.startswith("t33_"):
            _require(not payload.startswith(b"\xef\xbb\xbf") and b"\r\n" not in payload,
                     f"T33 文本必须为 UTF-8/LF：{source}")
            payload.decode("utf-8")
        hashes[name] = _sha256_bytes(payload)
    return raw, hashes


def _load_frozen_references() -> dict[str, Any]:
    """核验 T01/T16/T17/T20/T30/T31/T32 绑定并重建固定 CPU 参考。"""
    head = _head()
    _require_head_ancestor(head)
    paths = _source_paths()
    t32_raw, source_hashes = _validate_t32_before_json(paths)

    for name, expected in _PINNED_SHA256.items():
        _require(source_hashes.get(name) == expected,
                 f"冻结依赖 {name} SHA-256 不符：{source_hashes.get(name)}")
    _require(source_hashes["t32_fullheight_rtl"] == _PINNED_SHA256["t32_fullheight_rtl"],
             "T32 RTL source hash mismatch")
    _require(source_hashes["t32_testbench"] == _PINNED_SHA256["t32_testbench"],
             "T32 testbench source hash mismatch")
    _require(source_hashes["t32_runner"] == _PINNED_SHA256["t32_runner"],
             "T32 runner source hash mismatch")

    t32_evidence = json.loads(t32_raw.decode("utf-8"))
    t32_sources = t32_evidence.get("source_bindings_sha256", {})
    for name in (
        "g0_spec", "t01_manifest", "d2_int8_forward", "t16_proof",
        "t16_proof_script", "t17_runner", "t17_engine", "t17_geometry",
        "t17_weight_address", "t17_mac", "t17_testbench", "t17_evidence",
        "t20_runner", "t20_scheduler", "t20_testbench", "t20_evidence",
        "t30_tile16_rtl", "t30_testbench", "t30_runner", "t30_evidence",
        "t31_feeder_rtl", "t31_testbench", "t31_runner", "t31_evidence",
        "t32_fullheight_rtl", "t32_testbench", "t32_runner",
    ):
        _require(t32_sources.get(name) == source_hashes[name],
                 f"T32 evidence source hash 不匹配：{name}")
    _require(t32_evidence.get("task") == "S2A-T32" and
             t32_evidence.get("result") == "PASS",
             "冻结 T32 evidence 不是 PASS")

    t20_raw = paths["t20_evidence"].read_bytes()
    _require(_sha256_bytes(t20_raw) == _PINNED_SHA256["t20_evidence"],
             "T20 evidence SHA-256 不符")
    t20_evidence = json.loads(t20_raw.decode("utf-8"))
    t16_raw = paths["t16_proof"].read_bytes()
    _require(_sha256_bytes(t16_raw) == _PINNED_SHA256["t16_proof"],
             "T16 proof SHA-256 不符")
    t16_proof = json.loads(t16_raw.decode("utf-8"))
    t30_raw = paths["t30_evidence"].read_bytes()
    _require(_sha256_bytes(t30_raw) == _PINNED_SHA256["t30_evidence"],
             "T30 evidence SHA-256 不符")
    t30_evidence = json.loads(t30_raw.decode("utf-8"))
    t31_raw = paths["t31_evidence"].read_bytes()
    _require(_sha256_bytes(t31_raw) == _PINNED_SHA256["t31_evidence"],
             "T31 evidence SHA-256 不符")
    t31_evidence = json.loads(t31_raw.decode("utf-8"))
    t01_raw = paths["t01_manifest"].read_bytes()
    _require(_sha256_bytes(t01_raw) == _PINNED_SHA256["t01_manifest"],
             "T01 manifest SHA-256 不符")
    t01_manifest = json.loads(t01_raw.decode("utf-8"))

    _require(t20_evidence.get("task") == "S2A-T20" and
             t20_evidence.get("result") == "PASS" and
             t20_evidence.get("mode") == "FULL",
             "T20 layer36 CPU golden evidence 不是 FULL/PASS")
    _require(t30_evidence.get("task") == "S2A-T30" and
             t30_evidence.get("result") == "PASS" and
             t31_evidence.get("task") == "S2A-T31" and
             t31_evidence.get("result") == "PASS",
             "T30/T31 冻结 evidence 不是 PASS")
    _require(t32_evidence.get("frozen_layer36", {}).get("input_base_address") == _INPUT_BASE and
             t32_evidence.get("frozen_layer36", {}).get("output_base_address") == _OUTPUT_BASE and
             t32_evidence.get("frozen_layer36", {}).get("channel0_weight_bytes") == _K,
             "T32 evidence 固定 layer36 地址或几何不符")

    t20 = _load_module("s2a_t33_t20_helpers", paths["t20_runner"])
    t17 = t20._load_t17_runner()
    manifest, loaded_t16, weights_by_layer, package_path = t17._load_bound_inputs()
    package_sha256 = _sha256_file(package_path)
    _require(package_sha256 == t32_sources.get("gfint8w1_package") and
             package_sha256 == manifest["address_map"]["weight_package"]["sha256"],
             "T01 GFINT8W1 package SHA-256 与冻结 evidence 不一致")
    layers = {int(row["layer_index"]): row for row in manifest["layers"]}
    layer = layers[36]
    source_layer = layers[35]
    proof_layers = {int(row["layer_index"]): row for row in loaded_t16["layers"]}
    parameters = t17._candidate_parameters(layer, proof_layers[36])
    weights = weights_by_layer[36]

    _require(layer.get("cfg_section") == 37 and
             layer.get("input_shape_nchw") == [1, 256, 26, 26] and
             layer.get("output_shape_nchw") == [1, 30, 26, 26] and
             layer.get("kernel_hw") == [1, 1] and layer.get("layout") == "NCHW" and
             layer.get("activation") == "linear" and
             layer.get("tensor_address") == _OUTPUT_BASE and
             layer.get("tensor_length_bytes") == _OUTPUT_BYTES,
             "T01 layer36 固定尺寸、布局、地址或激活不符")
    _require(source_layer.get("tensor_address") == _INPUT_BASE and
             source_layer.get("tensor_length_bytes") == _INPUT_BYTES and
             source_layer.get("output_shape_nchw") == [1, 256, 26, 26],
             "T01 layer35 输入 tensor 绑定不符")
    weight_map = manifest["address_map"]["weight_package"]
    offsets = layer["gf8_parameter_offsets"]
    _require(int(weight_map["address"]) == _WEIGHT_PACKAGE_BASE and
             int(weight_map["length_bytes"]) == _WEIGHT_PACKAGE_BYTES and
             int(offsets["quantized_weight_offset"]) == _WEIGHT_OFFSET and
             int(offsets["quantized_weight_bytes"]) == _WEIGHT_BYTES and
             len(weights) == _WEIGHT_BYTES and len(parameters) == _OUTPUT_CHANNELS,
             "T01 layer36 GFINT8W1 slice 或 T16 channel 数量不符")
    _require(all(row["positive_multiplier"] == row["negative_multiplier"] and
                 row["positive_q_shift"] == row["negative_q_shift"]
                 for row in parameters),
             "linear activation 的 T16 正负 M/Q 必须一致")
    _verify_rtl_parameter_tables(layer, parameters)

    input_bytes, sentinel_offsets = t20._input_fixture()
    golden_input, golden, golden_stats = t20._input_and_golden(
        layer, weights, parameters, t17,
    )
    t20_input_sha = t20_evidence.get("fixture", {}).get("input_sha256_after_patch")
    t20_golden_sha = t20_evidence.get("golden", {}).get("expected_output_sha256")
    _require(input_bytes == golden_input and len(input_bytes) == _INPUT_BYTES and
             len(sentinel_offsets) == 675 and
             _sha256_bytes(input_bytes) == t20_input_sha,
             "T20/T10 固定输入 fixture 长度、sentinel 或 SHA-256 不符")
    _require(len(golden) == _OUTPUT_BYTES and _sha256_bytes(golden) == t20_golden_sha and
             golden_stats["d2_float_cross_checks"] == _OUTPUT_BYTES,
             "T20 full CPU golden 长度、SHA 或 D2 cross-check 数量不符")

    signed_input = [t17._signed_byte(value) for value in input_bytes]
    raw_values: list[int] = []
    for channel in range(_OUTPUT_CHANNELS):
        channel_weights = [
            t17._signed_byte(value)
            for value in weights[channel * _K:(channel + 1) * _K]
        ]
        bias = int(layer["bias_accumulator_int32_per_output_channel"][channel])
        for pixel in range(_PIXELS):
            accumulator = bias
            for reduction_index, weight in enumerate(channel_weights):
                accumulator += signed_input[reduction_index * _PIXELS + pixel] * weight
                _require(-(1 << 31) <= accumulator <= (1 << 31) - 1,
                         f"独立 raw oracle 检出 INT32 溢出：oc={channel} pixel={pixel} k={reduction_index}")
            raw_values.append(accumulator)
    _require(len(raw_values) == _OUTPUT_BYTES, "独立 raw oracle 输出长度不符")
    quantized = bytes(
        int(t17._fixed_point_quantize(value, parameters[index // _PIXELS])) & 0xFF
        for index, value in enumerate(raw_values)
    )
    _require(quantized == golden,
             "T16 CPU requant raw oracle 与 T20 full golden 不一致")

    t30_reference = t30_evidence.get("t20_cpu_reference", {})
    _require(raw_values[:16] == list(map(int, t30_reference.get(
        "tile_raw_accumulators_int32", []))) and
        list(map(t17._signed_byte, golden[:16])) == list(map(int, t30_reference.get(
            "tile_quantized_bytes_signed", []))),
        "T30 frozen tile16 channel0 参考与 T33 CPU oracle 不一致")
    t31_reference = t31_evidence.get("cpu_reference", {})
    _require(raw_values[:26] == list(map(int, t31_reference.get(
        "channel0_raw_int32_by_x", []))) and
        list(map(t17._signed_byte, golden[:26])) == list(map(int, t31_reference.get(
            "channel0_cpu_quantized_reference_by_x", []))),
        "T31 frozen row0 channel0 参考与 T33 CPU oracle 不一致")

    paths["gfint8w1_package"] = package_path
    source_hashes["gfint8w1_package"] = package_sha256
    return {
        "head": head,
        "paths": paths,
        "source_hashes": source_hashes,
        "manifest": manifest,
        "layer": layer,
        "t16_proof": loaded_t16,
        "parameters": parameters,
        "weights": weights,
        "package_path": package_path,
        "input_bytes": input_bytes,
        "sentinel_offsets": sentinel_offsets,
        "raw_values": raw_values,
        "raw_le_i32": b"".join((value & 0xFFFF_FFFF).to_bytes(4, "little")
                                 for value in raw_values),
        "golden": golden,
        "quantized": quantized,
        "golden_stats": golden_stats,
        "t20_evidence": t20_evidence,
        "t30_evidence": t30_evidence,
        "t31_evidence": t31_evidence,
        "t32_evidence": t32_evidence,
        "t17": t17,
    }


def _write_hex_bytes(path: Path, payload: bytes) -> None:
    path.write_text("".join(f"{value:02x}\n" for value in payload),
                    encoding="ascii", newline="\n")


def _write_hex_words(path: Path, values: list[int]) -> None:
    path.write_text("".join(f"{value & 0xFFFF_FFFF:08x}\n" for value in values),
                    encoding="ascii", newline="\n")


def _write_parameter_fixtures(work: Path, reference: dict[str, Any]) -> dict[str, Path]:
    layer = reference["layer"]
    parameters = reference["parameters"]
    biases = list(map(int, layer["bias_accumulator_int32_per_output_channel"]))
    _require(len(biases) == _OUTPUT_CHANNELS, "T01 bias table channel count 不符")
    paths = {
        "input": work / "input_fixture.hex",
        "weights": work / "layer36_weights.hex",
        "expected_raw": work / "expected_raw.hex",
        "expected_golden": work / "expected_golden.hex",
        "expected_bias": work / "expected_bias.hex",
        "expected_mq": work / "expected_mq.hex",
        "expected_activation": work / "expected_activation.hex",
    }
    _write_hex_bytes(paths["input"], reference["input_bytes"])
    _write_hex_bytes(paths["weights"], reference["weights"])
    _write_hex_words(paths["expected_raw"], reference["raw_values"])
    _write_hex_bytes(paths["expected_golden"], reference["golden"])
    _write_hex_words(paths["expected_bias"], biases)
    paths["expected_mq"].write_text(
        "".join(f"{(int(row['positive_multiplier']) << 6) | int(row['positive_q_shift']):010x}\n"
                for row in parameters), encoding="ascii", newline="\n",
    )
    paths["expected_activation"].write_text(
        "".join("00\n" for _ in range(_OUTPUT_CHANNELS)),
        encoding="ascii", newline="\n",
    )
    return paths


def _resource_value(report: str, labels: tuple[str, ...]) -> int:
    for label in labels:
        match = re.search(
            rf"^\s*(?:\|\s*)?{re.escape(label)}\s*\|\s*([0-9,]+)\s*\|",
            report, re.MULTILINE | re.IGNORECASE,
        )
        if match:
            return int(match.group(1).replace(",", ""))
    raise T33Error(f"Vivado utilization report 缺少资源字段：{labels}")


def _command_text(tool: Path, arguments: list[str]) -> str:
    parts = [str(tool), *arguments]
    return " ".join(f'"{part}"' if (" " in part or "&" in part) else part
                    for part in parts)


def _terminate_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is None:
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       capture_output=True, text=True, check=False)
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _run_logged(tool: Path, arguments: list[str], work: Path, log_path: Path,
                deadline: float, progress_timeout: int | None,
                progress: Any) -> dict[str, Any]:
    _require(tool.is_file(), f"未找到 Vivado 工具：{tool}")
    command = _command_text(tool, arguments)
    started = time.monotonic()
    process = subprocess.Popen(
        f'cmd.exe /d /s /c "{command}"', shell=False, cwd=work,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        encoding="utf-8", errors="replace", bufsize=1,
    )
    messages: queue.Queue[str | None] = queue.Queue()

    def read_output() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            messages.put(line)
        messages.put(None)

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    last_progress = started
    checkpoints: list[str] = []
    eof = False
    try:
        with log_path.open("x", encoding="utf-8", newline="\n") as log_file:
            while not eof or process.poll() is None:
                now = time.monotonic()
                if now > deadline:
                    _terminate_process_tree(process)
                    raise TimeoutError(f"T33 总时限到期；日志：{log_path}")
                if progress_timeout is not None and now - last_progress > progress_timeout:
                    _terminate_process_tree(process)
                    raise TimeoutError(
                        f"{tool.name} 超过 {progress_timeout}s 无进度；日志：{log_path}"
                    )
                try:
                    line = messages.get(timeout=1)
                except queue.Empty:
                    continue
                if line is None:
                    eof = True
                    continue
                log_file.write(line)
                log_file.flush()
                if line.startswith("PROGRESS "):
                    checkpoints.append(line.strip())
                    last_progress = time.monotonic()
                    print(line.rstrip(), flush=True)
    except BaseException:
        _terminate_process_tree(process)
        raise
    reader.join(timeout=5)
    exit_code = int(process.wait())
    elapsed = time.monotonic() - started
    return {
        "phase": tool.stem,
        "command": [str(tool), *arguments],
        "command_text": command,
        "exit_code": exit_code,
        "elapsed_seconds": round(elapsed, 3),
        "log_path": str(log_path),
        "log_sha256": _sha256_file(log_path),
        "progress_checkpoints": checkpoints,
    }


def _make_work_dir() -> Path:
    override = os.environ.get("S2A_T33_WORK_DIR")
    if override is None:
        parent = Path(tempfile.gettempdir()).resolve(strict=True)
        work = parent / f"s2a_t33_layer36_{uuid.uuid4().hex}"
    else:
        work = Path(override)
    _require(work.is_absolute(), "S2A_T33_WORK_DIR 必须是绝对路径")
    _require(not os.path.lexists(str(work)), f"TEMP 工作目录已存在，拒绝复用：{work}")
    _require(work.parent.is_dir(), f"TEMP 父目录不存在：{work.parent}")
    resolved_work = work.resolve(strict=False)
    try:
        _require(os.path.commonpath((str(resolved_work), str(_ROOT.resolve()))) !=
                 str(_ROOT.resolve()), f"Vivado 工作目录不能位于仓库内：{work}")
    except ValueError:
        pass
    work.mkdir()
    return work


def _select_evidence_path() -> tuple[Path, bool]:
    override = os.environ.get("S2A_T33_EVIDENCE_PATH")
    if override is None:
        path = _DEFAULT_EVIDENCE
        is_default = True
    else:
        path = Path(override)
        is_default = False
    _require(path.is_absolute(), "S2A_T33_EVIDENCE_PATH 必须是绝对路径")
    _require(not os.path.lexists(str(path)), f"T33 evidence 已存在，拒绝覆盖：{path}")
    return path, is_default


def _validate_summary(log_path: Path) -> dict[str, int]:
    output = log_path.read_text(encoding="utf-8", errors="replace")
    _require("S2A_T33_SIM_PASS" in output and
             output.count("S2A_T33_SIM_PASS") == 1,
             "xsim 必须恰有一个 S2A_T33_SIM_PASS marker")
    _require(not re.search(r"(?im)^\s*FAIL\b", output),
             "xsim 输出含 FAIL 标记")
    rows = re.findall(r"^PASS: requests=.*$", output, re.MULTILINE)
    _require(len(rows) == 1, "xsim 必须恰有一条完整计数 PASS summary")
    summary = {key: int(value) for key, value in re.findall(r"([a-z0-9_]+)=([0-9]+)", rows[0])}
    feature_reads = _OUTPUT_CHANNELS * _HEIGHT * _K * 7
    feature_bytes = _OUTPUT_CHANNELS * _HEIGHT * _K * _WIDTH
    weight_reads = _OUTPUT_CHANNELS * _HEIGHT * 2 * _K
    output_writes = _OUTPUT_BYTES
    expected = {
        "requests": feature_reads + weight_reads + output_writes,
        "feature_reads": feature_reads,
        "feature_bytes": feature_bytes,
        "weight_reads": weight_reads,
        "weight_bytes": weight_reads,
        "output_writes": output_writes,
        "raw_compares": output_writes,
        "parameter_checks": _OUTPUT_CHANNELS * _HEIGHT * 2,
        "error_codes": 3,
        "channel_boundary_error": 1,
        "abort_cancel": 1,
        "reset_cancel": 1,
        "output_abort_cancel": 1,
        "output_reset_cancel": 1,
        "output_cancel_handshakes": 0,
        "recovery": 1,
        "seed": _STALL_SEED,
    }
    _require(summary.get("stalls", 0) > 0, "memory/stream stall 没有覆盖")
    for name, value in expected.items():
        _require(summary.get(name) == value,
                 f"xsim summary {name}={summary.get(name)!r}，期望 {value}")
    return summary


def _preflight_syntax(work: Path, deadline: float) -> dict[str, Any]:
    progress_path = work / "progress.log"

    def progress(message: str) -> None:
        with progress_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(message + "\n")
        print(message, flush=True)

    tool = _VIVADO_BIN / "xvlog.bat"
    arguments = ["-sv", str(_TILE_RTL_PATH), str(_RTL_PATH), str(_TB_PATH)]
    phase = _run_logged(tool, arguments, work, work / "xvlog_preflight.log",
                        deadline, 1800, progress)
    _require(phase["exit_code"] == 0,
             f"xvlog preflight exit={phase['exit_code']}，日志：{phase['log_path']}")
    return phase


def _preflight_only() -> int:
    evidence_path, _is_default = _select_evidence_path()
    head_before = _head()
    _require_head_ancestor(head_before)
    reference = _load_frozen_references()
    work = Path(tempfile.gettempdir()).resolve(strict=True) / f"s2a_t33_preflight_{uuid.uuid4().hex}"
    _require(not os.path.lexists(str(work)), f"预检 TEMP 工作目录已存在：{work}")
    work.mkdir()
    phase = _preflight_syntax(work, time.monotonic() + 3600)
    head_after = _head()
    _require(head_before == head_after, "CPU/syntax preflight 期间 HEAD 发生变化")
    current_hashes = {name: _sha256_file(path) for name, path in reference["paths"].items()}
    _require(current_hashes == reference["source_hashes"],
             "CPU/syntax preflight 期间绑定源文件发生变化")
    _require(not os.path.lexists(str(evidence_path)),
             f"preflight 不得生成 evidence：{evidence_path}")
    print(json.dumps({
        "result": "PREFLIGHT_PASS",
        "head": head_before,
        "input_sha256": _sha256_bytes(reference["input_bytes"]),
        "weight_sha256": _sha256_bytes(reference["weights"]),
        "raw_accumulators": len(reference["raw_values"]),
        "raw_le_i32_sha256": _sha256_bytes(reference["raw_le_i32"]),
        "quantized_bytes": len(reference["quantized"]),
        "golden_sha256": _sha256_bytes(reference["golden"]),
        "parameter_channels": len(reference["parameters"]),
        "xvlog_exit_code": phase["exit_code"],
        "xvlog_log": phase["log_path"],
        "work_directory": str(work),
        "evidence_target": str(evidence_path),
    }, ensure_ascii=False), flush=True)
    return 0


def _run_full() -> int:
    started = time.monotonic()
    deadline = started + 4 * 60 * 60
    evidence_path, is_default_evidence = _select_evidence_path()
    head_start = _head()
    _require_head_ancestor(head_start)
    reference = _load_frozen_references()
    work = _make_work_dir()
    if not is_default_evidence:
        _require(evidence_path.parent.is_dir() or
                 os.path.commonpath((str(evidence_path.resolve(strict=False)), str(work.resolve()))) ==
                 str(work.resolve()),
                 f"自定义 evidence 父目录必须存在或位于新 TEMP 工作目录内：{evidence_path.parent}")

    progress_path = work / "progress.log"

    def progress(message: str) -> None:
        with progress_path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(message + "\n")
        print(message, flush=True)

    source_hashes_before = {
        name: _sha256_file(path) for name, path in reference["paths"].items()
    }
    _require(source_hashes_before == reference["source_hashes"],
             "冻结依赖在 CPU preflight 后发生变化")
    fixture_paths = _write_parameter_fixtures(work, reference)
    fixture_records = {
        name: {"path": str(path), "bytes": path.stat().st_size,
               "sha256": _sha256_file(path)}
        for name, path in fixture_paths.items()
    }
    progress(
        "PREFLIGHT_PASS work={} evidence={} head={} input_sha256={} raw={} golden_sha256={}".format(
            work, evidence_path, head_start,
            _sha256_bytes(reference["input_bytes"]), len(reference["raw_values"]),
            _sha256_bytes(reference["golden"]),
        )
    )
    _require(not os.path.lexists(str(evidence_path)),
             f"T33 evidence 目标在运行前出现，拒绝覆盖：{evidence_path}")

    tool_names = ("xvlog", "xelab", "xsim", "vivado")
    tools = {name: _VIVADO_BIN / f"{name}.bat" for name in tool_names}
    for tool in tools.values():
        _require(tool.is_file(), f"未找到 Vivado v2026.1 工具：{tool}")
    tool_versions = {}
    phases: list[dict[str, Any]] = []
    for name, tool in tools.items():
        if name == "vivado":
            version_script = work / "vivado_version.tcl"
            version_script.write_text(
                'puts "T33_VIVADO_VERSION=[version -short]"\nexit 0\n',
                encoding="utf-8", newline="\n",
            )
            version_arguments = [
                "-mode", "batch", "-nolog", "-nojournal",
                "-source", str(version_script),
            ]
        else:
            version_arguments = ["-version"]
        version = _run_logged(tool, version_arguments, work,
                              work / f"{name}_version.log", deadline, 1800, progress)
        _require(version["exit_code"] == 0,
                 f"{name} 版本查询 exit={version['exit_code']}")
        version_text = Path(version["log_path"]).read_text(
            encoding="utf-8", errors="replace",
        )
        if name == "vivado":
            version_match = re.search(
                r"(?m)^T33_VIVADO_VERSION=([^\r\n]+)$", version_text,
            )
            _require(version_match is not None and version_match.group(1) == "2026.1",
                     f"Vivado Tcl 版本查询结果不是 2026.1：{name}")
            version_line = f"Vivado v{version_match.group(1)}"
        else:
            _require(re.search(r"(?i)Vivado.*v2026\.1", version_text) is not None,
                     f"Vivado 工具版本不是 v2026.1：{name}")
            version_line = next((line.strip() for line in version_text.splitlines()
                                 if "Vivado" in line or "vivado" in line), "")
        tool_versions[name] = {
            "command": version["command_text"],
            "exit_code": version["exit_code"],
            "version_line": version_line,
            "log_path": version["log_path"],
            "log_sha256": version["log_sha256"],
            "query_script_sha256": (_sha256_file(version_script)
                                     if name == "vivado" else None),
        }

    phases_spec = [
        ("xvlog", tools["xvlog"], ["-sv", str(_TILE_RTL_PATH), str(_RTL_PATH), str(_TB_PATH)]),
        ("xelab", tools["xelab"], ["-top", "tb_s2a_conv_spatial_layer36_full",
                                     "-snapshot", "s2a_t33_layer36_full_snapshot"]),
        ("xsim", tools["xsim"], ["-R", "s2a_t33_layer36_full_snapshot"]),
    ]
    for name, tool, arguments in phases_spec:
        progress(f"PHASE_START {name} command={_command_text(tool, arguments)}")
        phase = _run_logged(tool, arguments, work, work / f"{name}_command.log",
                            deadline, 900 if name == "xsim" else 1800, progress)
        phases.append(phase)
        _require(phase["exit_code"] == 0,
                 f"{name} exit={phase['exit_code']}；日志：{phase['log_path']}")
        progress(f"PHASE_PASS {name} exit={phase['exit_code']} seconds={phase['elapsed_seconds']}")
    summary = _validate_summary(work / "xsim_command.log")

    tcl_path = work / "synth_layer36_full.tcl"
    utilization_path = work / "utilization.rpt"
    tcl_text = (
        f"read_verilog -sv {{{_TILE_RTL_PATH.as_posix()}}}\n"
        f"read_verilog -sv {{{_RTL_PATH.as_posix()}}}\n"
        "synth_design -top s2a_conv_spatial_layer36_full -part xc7z020clg400-1\n"
        f"report_utilization -file {{{utilization_path.as_posix()}}}\n"
        "puts \"S2A_T33_SYNTH_PASS\"\n"
        "exit\n"
    )
    tcl_path.write_text(tcl_text, encoding="utf-8", newline="\n")
    synth_arguments = ["-mode", "batch", "-source", str(tcl_path),
                       "-log", str(work / "vivado_native.log"),
                       "-journal", str(work / "vivado_native.jou")]
    progress(f"PHASE_START standalone_synthesis command={_command_text(tools['vivado'], synth_arguments)}")
    synthesis = _run_logged(tools["vivado"], synth_arguments, work,
                            work / "standalone_synthesis.stdout.log",
                            deadline, 1800, progress)
    phases.append(synthesis)
    _require(synthesis["exit_code"] == 0,
             f"standalone synthesis exit={synthesis['exit_code']}；日志：{synthesis['log_path']}")
    synthesis_output = Path(synthesis["log_path"]).read_text(encoding="utf-8", errors="replace")
    synthesis_markers = re.findall(r"(?m)^\s*S2A_T33_SYNTH_PASS\s*$", synthesis_output)
    _require(len(synthesis_markers) == 1 and
             not re.search(r"(?im)^\s*FAIL\b", synthesis_output),
             "standalone synthesis 必须恰有一个 PASS marker")
    _require(utilization_path.is_file(), "Vivado utilization report 缺失")
    utilization_text = utilization_path.read_text(encoding="utf-8", errors="replace")
    resources = {
        "lut": _resource_value(utilization_text, ("Slice LUTs*", "Slice LUTs", "CLB LUTs")),
        "ff": _resource_value(utilization_text, ("Slice Registers", "CLB Registers")),
        "bram_tile": _resource_value(utilization_text, ("Block RAM Tile",)),
        "dsp": _resource_value(utilization_text, ("DSPs",)),
    }
    progress(f"PHASE_PASS standalone_synthesis exit=0 resources={resources}")

    head_end = _head()
    _require_head_ancestor(head_end)
    _require(head_start == head_end, f"验证期间 HEAD 发生变化：{head_start} -> {head_end}")
    source_hashes_after = {
        name: _sha256_file(path) for name, path in reference["paths"].items()
    }
    _require(source_hashes_after == source_hashes_before,
             "验证期间冻结依赖/T33 源文件发生变化")
    _require(not os.path.lexists(str(evidence_path)),
             f"T33 evidence 目标在运行期间出现，拒绝覆盖：{evidence_path}")

    parameters = reference["parameters"]
    layer = reference["layer"]
    biases = list(map(int, layer["bias_accumulator_int32_per_output_channel"]))
    t16_layer = next(row for row in reference["t16_proof"]["layers"]
                     if int(row["layer_index"]) == 36)
    evidence = {
        "schema_version": 1,
        "task": "S2A-T33",
        "result": "PASS",
        "scope": "tiny416 fixed layer36 30-output-channel spatial full-layer RTL pilot",
        "baseline_git_head": _BASELINE_HEAD,
        "runtime_git_head_start": head_start,
        "runtime_git_head_end": head_end,
        "source_bindings_sha256": source_hashes_after,
        "frozen_layer36": {
            "model": "tiny416",
            "layer_index": 36,
            "cfg_section": 37,
            "input_shape_nchw": [1, 256, 26, 26],
            "input_base_address": _INPUT_BASE,
            "input_length_bytes": _INPUT_BYTES,
            "input_address": "base+k*676+y*26+x",
            "output_shape_nchw": [1, 30, 26, 26],
            "output_base_address": _OUTPUT_BASE,
            "output_length_bytes": _OUTPUT_BYTES,
            "output_address": "base+oc*676+y*26+x",
            "weight_package_base": _WEIGHT_PACKAGE_BASE,
            "weight_package_bytes": _WEIGHT_PACKAGE_BYTES,
            "layer36_weight_offset": _WEIGHT_OFFSET,
            "layer36_weight_bytes": _WEIGHT_BYTES,
            "weight_address": "package_base+layer36_offset+oc*256+k",
            "activation": "linear",
            "layout": "NCHW",
            "kernel_hw": [1, 1],
            "per_channel_bias_int32": biases,
            "t16_candidate_parameter_sha256": t16_layer["candidate_parameter_sha256"],
            "t16_mq_per_channel": parameters,
            "activation_per_channel": ["linear"] * _OUTPUT_CHANNELS,
            "requant_output_range": [-127, 127],
        },
        "reference": {
            "fixture_source": "T20 layer36 helper reproducing T10 address XOR byte pattern and 675 raw-0x80 patches",
            "input_seed": None,
            "input_bytes": len(reference["input_bytes"]),
            "input_sha256": _sha256_bytes(reference["input_bytes"]),
            "input_patched_minus128_count": len(reference["sentinel_offsets"]),
            "weight_package_path": str(reference["package_path"]),
            "weight_package_sha256": source_hashes_after["gfint8w1_package"],
            "layer36_weight_slice_sha256": _sha256_bytes(reference["weights"]),
            "layer36_weight_slice_bytes": len(reference["weights"]),
            "raw_oracle": "独立按oc/y/x/k顺序执行signed INT8乘加；每次累加检查signed INT32边界",
            "raw_accumulator_count": len(reference["raw_values"]),
            "raw_accumulator_le_i32_sha256": _sha256_bytes(reference["raw_le_i32"]),
            "t16_fixed_point_quantized_sha256": _sha256_bytes(reference["quantized"]),
            "t20_full_golden_sha256": _sha256_bytes(reference["golden"]),
            "t20_golden_bytes": len(reference["golden"]),
            "t20_d2_float_cross_checks": reference["golden_stats"]["d2_float_cross_checks"],
            "int32_accumulator_min": reference["golden_stats"]["int32_accumulator_min"],
            "int32_accumulator_max": reference["golden_stats"]["int32_accumulator_max"],
            "python_version": platform.python_version(),
            "numpy_version": reference["t17"].np.__version__,
        },
        "memory_protocol": {
            "aligned_word_bytes": 4,
            "byte_order": "little-endian; byte lane n maps to mem_addr+n",
            "single_outstanding": True,
            "request_fields_stable_until_handshake": True,
            "response_on_request_handshake": True,
            "feature_reads_expected": summary["feature_reads"],
            "selected_feature_bytes_expected": summary["feature_bytes"],
            "weight_reads_expected": summary["weight_reads"],
            "selected_weight_bytes_expected": summary["weight_bytes"],
            "output_writes_expected": summary["output_writes"],
            "feature_bytes_selected_once_per_channel": True,
            "weight_byte_use_count_per_oc_k": 52,
            "output_addresses_strobes_and_order_checked": True,
            "odd_row_overlap_cache_x16_x17_checked": True,
            "final_tile_lane_mask": "0x03ff",
            "feature_x26_or_later_selected": False,
            "memory_errors_propagated": [1, 2, 6],
            "error_2_injected_at_channel_boundary": "oc=1, row=0, tile=0, k=0 first weight read",
            "pending_abort_read_cancel": summary["abort_cancel"],
            "pending_reset_read_cancel": summary["reset_cancel"],
            "pending_abort_output_write_cancel": summary["output_abort_cancel"],
            "pending_reset_output_write_cancel": summary["output_reset_cancel"],
            "canceled_output_write_handshakes": summary["output_cancel_handshakes"],
            "recovery_runs": summary["recovery"],
            "added_local_timeout_counter": False,
            "stall_seed": _STALL_SEED,
            "observed_stall_cycles": summary["stalls"],
        },
        "verification": {
            "independently_computed_expected_counts": {
                "feature_reads": _OUTPUT_CHANNELS * _HEIGHT * _K * 7,
                "selected_feature_bytes": _OUTPUT_CHANNELS * _HEIGHT * _K * _WIDTH,
                "weight_reads_and_bytes": _OUTPUT_CHANNELS * _HEIGHT * 2 * _K,
                "output_writes": _OUTPUT_CHANNELS * _PIXELS,
                "raw_compares": _OUTPUT_CHANNELS * _PIXELS,
            },
            "testbench_summary": summary,
            "raw_values_compared_exactly": summary["raw_compares"],
            "requantized_output_bytes_compared_exactly": summary["output_writes"],
            "per_channel_parameter_switch_checks": summary["parameter_checks"],
            "unique_simulation_pass_marker": "S2A_T33_SIM_PASS",
            "simulator": "Vivado xvlog/xelab/xsim v2026.1",
            "tool_versions": tool_versions,
            "phases": phases[:3],
            "work_directory": str(work),
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "logs_and_fixture_hashes": fixture_records,
        },
        "standalone_synthesis": {
            "tool": "Vivado v2026.1",
            "top": "s2a_conv_spatial_layer36_full",
            "rtl_inputs": [str(_TILE_RTL_PATH), str(_RTL_PATH)],
            "part": "xc7z020clg400-1",
            "opened_project_xpr": False,
            "utilization": resources,
            "phase": {key: value for key, value in synthesis.items()},
            "tcl_path": str(tcl_path),
            "tcl_sha256": _sha256_file(tcl_path),
            "utilization_report_path": str(utilization_path),
            "utilization_report_sha256": _sha256_file(utilization_path),
            "timing_constraints_applied": False,
            "timing_conclusion": "未提供 XDC/时钟约束；不作时序结论。",
        },
        "limits": [
            "只验证 tiny416 layer36 的30个输出通道；不代表其它层、整网、G4或G5通过。",
            "32-bit aligned single-outstanding接口是仿真抽象，不代表物理AXI/DMA集成。",
            "综合仅为本模块与T30 tile16的资源估算；未加载XPR/XDC，不作时序结论。",
            "未操作板卡、未烧录、未使用Vitis，未进入阶段2B或阶段3。",
        ],
    }
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    with evidence_path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    evidence_sha = _sha256_file(evidence_path)
    progress(f"EVIDENCE_WRITTEN path={evidence_path} sha256={evidence_sha}")
    print(json.dumps({
        "result": "PASS",
        "head": head_end,
        "evidence_path": str(evidence_path),
        "evidence_sha256": evidence_sha,
        "work_directory": str(work),
        "resources": resources,
        "summary": summary,
    }, ensure_ascii=False), flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight-only", action="store_true",
                        help="只运行冻结引用、CPU oracle 和 xvlog 语法预检")
    arguments = parser.parse_args(argv)
    try:
        return _preflight_only() if arguments.preflight_only else _run_full()
    except Exception as error:
        print(f"FAIL S2A-T33: {type(error).__name__}: {error}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
