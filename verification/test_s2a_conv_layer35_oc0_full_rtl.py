"""S2A-T34：绑定冻结证据并验证 tiny416 layer35 输出通道 0 全栅格 RTL。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import re
import struct
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASK_BASE = "83c603b327ac0d18959f49a38633521963aa3fbd"
T17_BASE = "f0b7791d2db7b0a13126d3a0d3db586a01a294b1"
MANIFEST_PATH = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
T16_PATH = ROOT / "report/evidence/S2A-T16/conv_requant_proof.json"
T17_PATH = ROOT / "report/evidence/S2A-T17/conv_engine_simulation.json"
T20_PATH = ROOT / "report/evidence/S2A-T20/conv_layer_scheduler_simulation.json"
T23_PATH = ROOT / "report/evidence/S2A-T23/conv_requant_parameter_table.json"
T01_SHA = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
T16_SHA = "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24"
T17_SHA = "4cd1d0f0e5edf7b34907179dea47a9a9c0994eb1d8bd89adfa341067cac17ab2"
T20_SHA = "d6bc16966a2d3c7707d98aafa6b435ae158cd28faa53baa8f795e13e86a17887"
T23_SHA = "396dc66aa3ccc41050cc8183bff16b86143a6f5553cf38fed16b0ba8b4eb4ae1"
T16_SCRIPT_SHA = "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9"
D2_FORWARD_SHA = "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393"
WEIGHT_REPORT_SHA = "d867cd5dc7497f0de9db5c4e0643afd2e52d4c1e77632852487e8afceaa0dd80"
GF8_SHA = "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39"
GF8_BYTES = 5903100
INPUT_BASE = 27706496
INPUT_BYTES = 259584
OUTPUT_BASE = 27966080
OUTPUT_BYTES = 173056
OUTPUT_WIDTH = 26
OUTPUT_PIXELS = OUTPUT_WIDTH * OUTPUT_WIDTH
INPUT_CHANNELS = 384
KERNEL_AREA = 9
REDUCTION = INPUT_CHANNELS * KERNEL_AREA
WEIGHT_BASE = 0x00100000
WEIGHT_OFFSET = 5010412
WEIGHT_LAYER_BYTES = 884736
SEED = 20260922
STALL_SEQUENCE = (0, 1, 2, 7, 3)
MAX_INT32 = (1 << 31) - 1
MIN_INT32 = -(1 << 31)
XILINX_BIN_DEFAULT = Path(r"D:\Xilinx\2026.1\Vivado\bin")

T17_SOURCE_HASHES = {
    "src/s2a_conv_engine.sv": "8656f43f510a8f7c74aaee44f809da74adeb3b8c5fed32f8f009aabecb05c994",
    "sim/tb_s2a_conv_engine.sv": "2b642eb47cded4644e4e9ba3a1e3fa60d484cf795ec6e51dd8d4cfcc97d2f001",
    "verification/test_s2a_conv_engine_rtl.py": "adbb7e2574c50fd8e702e386a0898d27a0e4a16aebfc782436e386d56c768357",
    "src/int8_conv_tap_geometry.sv": "109b58473fa2f5d6de5c362e0c780ae2e98bce260c1d92714fde58ae706e4bbc",
    "src/int8_conv_weight_address.sv": "0914df477c9e160d227c74f9eaf926e502069e563145e1e1f3e03673654d4592",
    "src/int8_mac_accumulator.sv": "b3f6a425e2db58b86c63524b9caf0019ddf7a103c5b66f8bfcc3cf86966d0a74",
}
T34_SOURCES = (
    "src/int8_conv_tap_geometry.sv",
    "src/int8_conv_weight_address.sv",
    "src/int8_mac_accumulator.sv",
    "src/s2a_conv_engine.sv",
    "src/s2a_conv_layer35_oc0_full.sv",
    "sim/tb_s2a_conv_layer35_oc0_full.sv",
)


class T34Error(RuntimeError):
    """报告冻结绑定、预检或工具运行失败。"""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> tuple[dict[str, Any], str]:
    data = path.read_bytes()
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise T34Error(f"JSON 无法按 UTF-8 解析：{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise T34Error(f"JSON 根节点不是对象：{path}")
    return value, _sha256_bytes(data)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise T34Error(message)


def _signed_byte(value: int) -> int:
    return value if value < 128 else value - 256


def _round_half_away(value: float) -> int:
    rounded = math.floor(abs(value) + 0.5)
    return -rounded if value < 0.0 else rounded


class _XorShift32:
    """按 T17 的固定 xorshift32 byte draw 生成输入 fixture。"""

    def __init__(self, seed: int) -> None:
        _require(0 < seed <= 0xFFFF_FFFF, "fixture seed 不在非零 uint32 范围")
        self.state = seed
        self.draw_count = 0

    def next_u32(self) -> int:
        value = self.state
        value = (value ^ ((value << 13) & 0xFFFF_FFFF)) & 0xFFFF_FFFF
        value ^= value >> 17
        value = (value ^ ((value << 5) & 0xFFFF_FFFF)) & 0xFFFF_FFFF
        self.state = value
        self.draw_count += 1
        return value

    def int8_byte(self) -> int:
        return (((self.next_u32() & 255) % 255) - 127) & 255


def _git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode != 0:
        raise T34Error(f"git {' '.join(args)} 失败：{result.stderr.strip()}")
    return result.stdout.strip()


def _verify_git_ancestry() -> dict[str, Any]:
    head = _git_output("rev-parse", "HEAD")
    _require(_git_output("merge-base", "--is-ancestor", TASK_BASE, head) == "",
             f"当前 HEAD 不是 T34 基线的后代：{head}")
    _require(_git_output("merge-base", "--is-ancestor", T17_BASE, head) == "",
             f"当前 HEAD 不是 T17 冻结基线的后代：{head}")
    return {"task_base": TASK_BASE, "t17_base": T17_BASE, "current_head": head,
            "task_base_is_ancestor": True, "t17_base_is_ancestor": True}


def _load_and_verify_inputs() -> dict[str, Any]:
    ancestry = _verify_git_ancestry()
    manifest, manifest_sha = _read_json(MANIFEST_PATH)
    t16, t16_sha = _read_json(T16_PATH)
    t17, t17_sha = _read_json(T17_PATH)
    t20, t20_sha = _read_json(T20_PATH)
    t23, t23_sha = _read_json(T23_PATH)

    _require(manifest_sha == T01_SHA, "T01 manifest SHA-256 与冻结值不符")
    _require(t16_sha == T16_SHA, "T16 proof SHA-256 与 T17 冻结绑定不符")
    _require(t17_sha == T17_SHA, "T17 仿真证据 SHA-256 与冻结值不符")
    _require(t20_sha == T20_SHA, "T20 调度仿真证据 SHA-256 与冻结值不符")
    _require(t23_sha == T23_SHA, "T23 M/Q 表 SHA-256 与冻结值不符")
    _require(t17.get("result") == "PASS", "T17 证据未通过")
    _require(t17.get("baseline_head") == T17_BASE, "T17 baseline head 不符")
    _require(t17["bindings"].get("t01_manifest_sha256") == T01_SHA,
             "T17 内部 T01 manifest 绑定不符")
    _require(t17["bindings"].get("t16_proof_sha256") == T16_SHA,
             "T17 内部 T16 proof 绑定不符")
    _require(t17["bindings"].get("gfint8w1_package_sha256") == GF8_SHA and
             t17["bindings"].get("gfint8w1_package_bytes") == GF8_BYTES,
             "T17 内部 GF8 权重包绑定不符")
    _require(t16.get("status") == "EXACT_FIXED_POINT_FOUND" and
             t16["coverage"].get("convolution_layers_audited") == 21 and
             t16["coverage"].get("output_channels_audited") == 3164 and
             t16["coverage"].get("failures") == 0,
             "T16 完整模型精确 M/Q 证明状态或覆盖数不符")
    _require(t23.get("status") == "ALL_CHANNELS_EXACT_AND_T16_DIGEST_MATCH",
             "T23 M/Q 表状态不符")
    _require(t20.get("result") == "PASS", "T20 调度仿真证据未通过")

    source_hashes: dict[str, str] = {}
    for relative, expected in T17_SOURCE_HASHES.items():
        path = ROOT / relative
        actual = _sha256_file(path)
        _require(actual == expected, f"T17 冻结源 SHA-256 不符：{relative}")
        source_hashes[relative] = actual

    t16_script = ROOT / "verification/s2a_conv_requant_proof.py"
    d2_forward = ROOT / "verification/s1_t02_d2_int8_forward.py"
    weight_report_path = ROOT / "report/evidence/S1-T02/20260922_s1_t02_d2_tiny416_int8_weight_r2.json"
    _require(_sha256_file(t16_script) == T16_SCRIPT_SHA, "T16 proof 脚本 SHA-256 不符")
    _require(_sha256_file(d2_forward) == D2_FORWARD_SHA, "D2 forward reference SHA-256 不符")
    weight_report, weight_report_sha = _read_json(weight_report_path)
    _require(weight_report_sha == WEIGHT_REPORT_SHA, "T01 绑定的权重报告 SHA-256 不符")
    _require(weight_report["package"].get("sha256") == GF8_SHA and
             weight_report["package"].get("bytes") == GF8_BYTES,
             "权重报告中的 GF8 包绑定不符")

    for binding in t23.get("source_bindings", []):
        relative = str(binding["path"])
        path = Path(relative)
        if not path.is_absolute():
            path = ROOT / path
        _require(_sha256_file(path) == str(binding["sha256"]).lower(),
                 f"T23 源绑定 SHA-256 不符：{relative}")
        source_hashes[relative] = str(binding["sha256"]).lower()
    for binding in t23.get("tooling_bindings", []):
        relative = str(binding["path"])
        path = ROOT / Path(relative)
        _require(_sha256_file(path) == str(binding["sha256"]).lower(),
                 f"T23 工具绑定 SHA-256 不符：{relative}")
        source_hashes[relative] = str(binding["sha256"]).lower()

    layers = {int(layer["layer_index"]): layer for layer in manifest.get("layers", [])}
    _require(34 in layers and 35 in layers, "T01 manifest 缺少 layer34/35")
    layer34 = layers[34]
    layer35 = layers[35]
    _require(layer34.get("op") == "route" and
             layer34.get("output_shape_nchw") == [1, 384, 26, 26] and
             layer34.get("tensor_address") == INPUT_BASE and
             layer34.get("tensor_length_bytes") == INPUT_BYTES,
             "T01 layer34 输入 tensor 地址/shape/长度不符")
    _require(layer35.get("cfg_section") == 36 and
             layer35.get("op") == "convolutional" and
             layer35.get("input_tensor_indices") == [34] and
             layer35.get("input_shape_nchw") == [1, 384, 26, 26] and
             layer35.get("output_shape_nchw") == [1, 256, 26, 26] and
             layer35.get("tensor_address") == OUTPUT_BASE and
             layer35.get("tensor_length_bytes") == OUTPUT_BYTES and
             layer35.get("kernel_hw") == [3, 3] and
             layer35.get("stride_hw") == [1, 1] and
             layer35.get("padding_lrtb") == [1, 1, 1, 1] and
             layer35.get("padding_value_int8") == 0 and
             layer35.get("activation") == "leaky" and
             layer35.get("layout") == "NCHW" and
             layer35.get("accumulator_bits") == 32 and
             layer35.get("weight_layer_index") == 35,
             "T01 layer35 固定卷积规格不符")
    offsets = layer35.get("gf8_parameter_offsets", {})
    _require(offsets.get("quantized_weight_offset") == WEIGHT_OFFSET and
             offsets.get("quantized_weight_bytes") == WEIGHT_LAYER_BYTES,
             "T01 layer35 GF8 权重区间不符")
    _require(layer35.get("bias_accumulator_int32_per_output_channel", [None])[0] == -896,
             "T01 layer35 oc0 INT32 bias 不符")
    _require(len(layer35.get("fused_bias_float32_per_output_channel", [])) == 256,
             "T01 layer35 融合 float32 bias 通道数不符")

    t16_layer = next((row for row in t16.get("layers", [])
                      if int(row.get("layer_index", -1)) == 35), None)
    t23_layer = next((row for row in t23.get("layers", [])
                      if int(row.get("layer_index", -1)) == 35), None)
    _require(t16_layer is not None and t23_layer is not None,
             "T16/T23 缺少 layer35 M/Q 摘要")
    _require(t16_layer.get("candidate_parameter_sha256") ==
             t23_layer.get("candidate_parameter_sha256"),
             "T16 与 T23 layer35 全通道 M/Q 摘要不一致")
    channels = t23_layer.get("channels", [])
    _require(len(channels) == 256, "T23 layer35 不是 256 个输出通道")
    digest = hashlib.sha256()
    for index, channel in enumerate(channels):
        _require(int(channel.get("channel", -1)) == index,
                 "T23 layer35 通道序号不连续")
        digest.update((f"{index},{int(channel['positive_Q'])},{int(channel['positive_M'])},"
                       f"{int(channel['negative_Q'])},{int(channel['negative_M'])}\n").encode("ascii"))
    _require(digest.hexdigest() == t16_layer.get("candidate_parameter_sha256"),
             "T23 全通道 M/Q 重算摘要与 T16 proof 不符")
    channel0 = channels[0]
    mq = {
        "positive_M": int(channel0["positive_M"]),
        "positive_Q": int(channel0["positive_Q"]),
        "negative_M": int(channel0["negative_M"]),
        "negative_Q": int(channel0["negative_Q"]),
    }
    _require(mq == {"positive_M": 94787, "positive_Q": 27,
                    "negative_M": 19412319, "negative_Q": 38},
             "T23 layer35/ch0 M/Q 与任务冻结值不符")

    package_path = Path(manifest["bindings"]["gf8_package"]["path"])
    _require(package_path.is_absolute() and package_path.is_file(),
             f"T01 GF8 包的精确路径不可读：{package_path}")
    package = package_path.read_bytes()
    _require(len(package) == GF8_BYTES and _sha256_bytes(package) == GF8_SHA,
             "GF8 包长度或 SHA-256 与 T01/T17 冻结绑定不符")
    old_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        if str(ROOT / "verification") not in sys.path:
            sys.path.insert(0, str(ROOT / "verification"))
        import test_s2a_conv_engine_rtl as t17_loader
    finally:
        sys.dont_write_bytecode = old_dont_write_bytecode
    t17_manifest, _t17_t16, t17_package_weights, t17_package_path = (
        t17_loader._load_bound_inputs()
    )
    _require(t17_manifest == manifest and t17_package_path == package_path,
             "T17 冻结加载路径返回的 T01 manifest/GF8 路径与 T34 绑定不符")
    _require(35 in t17_package_weights and
             len(t17_package_weights[35]) == WEIGHT_LAYER_BYTES,
             "T17 冻结加载路径未返回完整 layer35 权重")
    layer35_weight_offset = int(offsets["quantized_weight_offset"])
    layer35_bias_offset = int(offsets["fused_bias_offset"])
    _require(package[layer35_weight_offset:layer35_weight_offset + WEIGHT_LAYER_BYTES] ==
             t17_package_weights[35],
             "T17 返回的 layer35 权重与冻结 GF8 原始区间不一致")
    fused_bias_bytes = package[layer35_bias_offset:layer35_bias_offset + 4]
    _require(len(fused_bias_bytes) == 4, "GF8 layer35 oc0 fused bias 字段截断")
    package_fused_bias = struct.unpack("<f", fused_bias_bytes)[0]
    manifest_fused_bias = float(layer35["fused_bias_float32_per_output_channel"][0])
    _require(fused_bias_bytes == struct.pack("<f", manifest_fused_bias),
             "GF8 layer35 oc0 float32 fused bias 与 T01 不符")
    weight_oc0 = t17_package_weights[35][:REDUCTION]
    _require(len(weight_oc0) == REDUCTION, "GF8 oc0 slice 长度不符")

    evidence_bindings = {
        "T01_manifest": {"path": str(MANIFEST_PATH), "sha256": manifest_sha},
        "T16_proof": {"path": str(T16_PATH), "sha256": t16_sha},
        "T17_engine_evidence": {"path": str(T17_PATH), "sha256": t17_sha},
        "T20_scheduler_evidence": {"path": str(T20_PATH), "sha256": t20_sha},
        "T23_parameter_table": {"path": str(T23_PATH), "sha256": t23_sha},
        "T16_script": {"path": str(t16_script), "sha256": T16_SCRIPT_SHA},
        "D2_forward_reference": {"path": str(d2_forward), "sha256": D2_FORWARD_SHA},
        "weight_report": {"path": str(weight_report_path), "sha256": weight_report_sha},
        "GF8_package": {"path": str(package_path), "bytes": len(package),
                        "sha256": _sha256_bytes(package)},
    }
    evidence_bindings["T17_source_hashes"] = source_hashes
    return {
        "ancestry": ancestry,
        "manifest": manifest,
        "layers": layers,
        "layer35": layer35,
        "t16_layer35": t16_layer,
        "t23_layer35": t23_layer,
        "channel0_mq": mq,
        "evidence_bindings": evidence_bindings,
        "package": package,
        "package_path": package_path,
        "weight_oc0": weight_oc0,
        "weight_oc0_sha256": _sha256_bytes(weight_oc0),
        "layer35_weight_offset": layer35_weight_offset,
        "layer35_bias_offset": layer35_bias_offset,
        "package_fused_bias_float32": package_fused_bias,
        "manifest_fused_bias_float32": manifest_fused_bias,
    }


def _build_fixture_and_oracle(inputs: dict[str, Any], report_progress: bool = False) -> dict[str, Any]:
    rng = _XorShift32(SEED)
    input_fixture = bytes(rng.int8_byte() for _ in range(INPUT_BYTES))
    _require(len(input_fixture) == INPUT_BYTES and 128 not in input_fixture,
             "fixture 长度错误或包含非法 -128")

    layer = inputs["layer35"]
    input_scale = float(layer["input_scale"])
    output_scale = float(layer["output_scale"])
    weight_scale = float(layer["weight_scale_per_output_channel"][0])
    real_scale = input_scale * weight_scale
    bias = int(layer["bias_accumulator_int32_per_output_channel"][0])
    mq = inputs["channel0_mq"]
    raw_values: list[int] = []
    quantized_values: list[int] = []
    padding_taps = 0
    valid_taps = 0
    for y in range(OUTPUT_WIDTH):
        for x in range(OUTPUT_WIDTH):
            accumulator = bias
            for channel in range(INPUT_CHANNELS):
                input_channel_base = channel * OUTPUT_PIXELS
                weight_channel_base = channel * KERNEL_AREA
                for kernel_y in range(3):
                    input_y = y + kernel_y - 1
                    for kernel_x in range(3):
                        input_x = x + kernel_x - 1
                        if not (0 <= input_y < OUTPUT_WIDTH and 0 <= input_x < OUTPUT_WIDTH):
                            padding_taps += 1
                            continue
                        feature_byte = input_fixture[
                            input_channel_base + input_y * OUTPUT_WIDTH + input_x
                        ]
                        weight_byte = inputs["weight_oc0"][
                            weight_channel_base + kernel_y * 3 + kernel_x
                        ]
                        accumulator += _signed_byte(feature_byte) * _signed_byte(weight_byte)
                        valid_taps += 1
            _require(MIN_INT32 <= accumulator <= MAX_INT32,
                     f"Python oracle INT32 overflow at y={y} x={x}: {accumulator}")
            raw_values.append(accumulator)
            scaled = float(accumulator) * real_scale
            scaled = scaled / output_scale
            if scaled < 0.0:
                scaled = scaled * 0.1
            d2_value = max(-127, min(127, _round_half_away(scaled)))
            negative = accumulator < 0
            multiplier = mq["negative_M"] if negative else mq["positive_M"]
            q_shift = mq["negative_Q"] if negative else mq["positive_Q"]
            magnitude = abs(accumulator)
            product = magnitude * multiplier
            rounded = ((product + (1 << (q_shift - 1))) >> q_shift) if q_shift else product
            fixed_value = max(-127, min(127, -rounded if negative else rounded))
            _require(d2_value == fixed_value,
                     f"D2 与 T23 fixed-point 输出不同 y={y} x={x}: {d2_value} != {fixed_value}")
            quantized_values.append(d2_value)
        if report_progress:
            print(f"CPU_ORACLE row={y}/25 pixels={(y + 1) * OUTPUT_WIDTH}/676", flush=True)

    expected_valid = INPUT_CHANNELS * 76 * 76
    expected_padding = OUTPUT_PIXELS * REDUCTION - expected_valid
    _require(valid_taps == expected_valid and padding_taps == expected_padding,
             "独立 oracle 几何 tap 计数不符")
    raw_bytes = b"".join(struct.pack("<i", value) for value in raw_values)
    quantized_bytes = bytes(value & 255 for value in quantized_values)
    golden = raw_bytes + quantized_bytes
    fixture = {
        "generator": "T17 xorshift32; INT8=((next_u32&255)%255)-127",
        "seed": SEED,
        "draw_count": rng.draw_count,
        "final_state": rng.state,
        "bytes": len(input_fixture),
        "minimum_int8": min(_signed_byte(value) for value in input_fixture),
        "maximum_int8": max(_signed_byte(value) for value in input_fixture),
        "minus_128_count": 0,
        "sha256": _sha256_bytes(input_fixture),
    }
    oracle = {
        "reduction_order": "k=ic*9+ky*3+kx; input NCHW byte=base+ic*676+iy*26+ix",
        "bias_int32": bias,
        "raw_accumulator_count": len(raw_values),
        "raw_accumulator_min": min(raw_values),
        "raw_accumulator_max": max(raw_values),
        "valid_tap_count": valid_taps,
        "padding_tap_count": padding_taps,
        "d2_and_fixed_point_match_count": len(quantized_values),
        "raw_int32_le_sha256": _sha256_bytes(raw_bytes),
        "quantized_int8_sha256": _sha256_bytes(quantized_bytes),
        "combined_golden_sha256": _sha256_bytes(golden),
    }
    return {
        "input_fixture": input_fixture,
        "raw_values": raw_values,
        "quantized_values": quantized_values,
        "raw_bytes": raw_bytes,
        "quantized_bytes": quantized_bytes,
        "golden_bytes": golden,
        "fixture_summary": fixture,
        "oracle_summary": oracle,
        "valid_taps": valid_taps,
        "padding_taps": padding_taps,
    }


def _preflight(report_progress: bool = False) -> tuple[dict[str, Any], dict[str, Any]]:
    inputs = _load_and_verify_inputs()
    oracle = _build_fixture_and_oracle(inputs, report_progress=report_progress)
    summary = {
        "result": "PASS",
        "current_head": inputs["ancestry"]["current_head"],
        "T01_sha256": inputs["evidence_bindings"]["T01_manifest"]["sha256"],
        "T16_sha256": inputs["evidence_bindings"]["T16_proof"]["sha256"],
        "T17_sha256": inputs["evidence_bindings"]["T17_engine_evidence"]["sha256"],
        "T20_sha256": inputs["evidence_bindings"]["T20_scheduler_evidence"]["sha256"],
        "T23_sha256": inputs["evidence_bindings"]["T23_parameter_table"]["sha256"],
        "GF8_sha256": inputs["evidence_bindings"]["GF8_package"]["sha256"],
        "weight_oc0_sha256": inputs["weight_oc0_sha256"],
        "fixture": oracle["fixture_summary"],
        "oracle": oracle["oracle_summary"],
        "expected_counts": _expected_counts(inputs),
    }
    return inputs, {"summary": summary, "oracle": oracle}


def _expected_counts(inputs: dict[str, Any]) -> dict[str, Any]:
    total = OUTPUT_PIXELS * REDUCTION
    valid = INPUT_CHANNELS * 76 * 76
    expected: dict[str, Any] = {
        "output_pixels": OUTPUT_PIXELS,
        "raw_int32_compares": OUTPUT_PIXELS,
        "quantized_int8_compares": OUTPUT_PIXELS,
        "feature_reads": valid,
        "weight_reads": valid,
        "output_writes": OUTPUT_PIXELS,
        "all_kernel_taps": total,
        "padding_taps": total - valid,
        "corner_padding_taps_each": INPUT_CHANNELS * 5,
        "feature_lane_mask": 15,
        "weight_lane_mask": 15,
        "output_lane_mask": 15,
        "request_stall_sequence": list(STALL_SEQUENCE),
    }
    class_transfer_counts = {
        "feature": valid,
        "weight": valid,
        "output": OUTPUT_PIXELS,
    }
    for class_name, transfer_count in class_transfer_counts.items():
        slot_counts = [transfer_count // len(STALL_SEQUENCE) +
                       int(slot < transfer_count % len(STALL_SEQUENCE))
                       for slot in range(len(STALL_SEQUENCE))]
        stall_cycles = sum(count * STALL_SEQUENCE[slot]
                           for slot, count in enumerate(slot_counts))
        expected[f"{class_name}_transfers"] = transfer_count
        expected[f"{class_name}_stall_cycles"] = stall_cycles
        expected[f"{class_name}_slot_counts"] = slot_counts
        expected[f"{class_name}_slot0"] = slot_counts[0]
        expected[f"{class_name}_slot1"] = slot_counts[1]
        expected[f"{class_name}_slot2"] = slot_counts[2]
        expected[f"{class_name}_slot3"] = slot_counts[3]
        expected[f"{class_name}_slot4"] = slot_counts[4]
    expected["request_stall_cycles"] = sum(
        expected[f"{class_name}_stall_cycles"]
        for class_name in class_transfer_counts
    )
    return expected


def _geometry_record(inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_base_address": INPUT_BASE,
        "input_length_bytes": INPUT_BYTES,
        "input_shape_nchw": [1, INPUT_CHANNELS, OUTPUT_WIDTH, OUTPUT_WIDTH],
        "feature_byte_address": "base+ic*676+iy*26+ix",
        "output_base_address": OUTPUT_BASE,
        "output_length_bytes": OUTPUT_BYTES,
        "output_shape_nchw": [1, 256, OUTPUT_WIDTH, OUTPUT_WIDTH],
        "output_byte_address": "base+y*26+x for oc0",
        "weight_package_base": WEIGHT_BASE,
        "weight_package_bytes": GF8_BYTES,
        "layer35_weight_offset": WEIGHT_OFFSET,
        "layer35_weight_bytes": WEIGHT_LAYER_BYTES,
        "layer35_fused_bias_offset": inputs["layer35_bias_offset"],
        "fused_bias_storage": "little-endian IEEE-754 float32",
        "fused_bias_float32_oc0": inputs["package_fused_bias_float32"],
        "oc0_reduction_length": REDUCTION,
        "oc0_weight_slice_sha256": inputs["weight_oc0_sha256"],
        "bias_int32": int(inputs["layer35"]["bias_accumulator_int32_per_output_channel"][0]),
        "channel0_mq": inputs["channel0_mq"],
    }


def _require_new_absolute_directory(path: Path, label: str, beneath_temp: bool) -> None:
    _require(path.is_absolute(), f"{label} 必须是绝对路径")
    _require(not path.exists(), f"{label} 已存在，拒绝覆盖：{path}")
    _require(path.parent.is_dir(), f"{label} 的精确父目录不存在：{path.parent}")
    if beneath_temp:
        temp_root = Path(tempfile.gettempdir()).resolve()
        target = path.resolve()
        try:
            common = Path(os.path.commonpath((str(temp_root), str(target))))
        except ValueError as exc:
            raise T34Error(f"{label} 不在系统 TEMP 下：{path}") from exc
        _require(common == temp_root, f"{label} 必须位于系统 TEMP 下：{path}")


def _prepare_evidence_target(path: Path) -> None:
    _require(path.is_absolute(), "证据 JSON 路径必须是绝对路径")
    _require(path.suffix.lower() == ".json", "证据输出路径必须以 .json 结尾")
    _require(not path.exists(), f"证据 JSON 已存在，拒绝覆盖：{path}")
    if not path.parent.exists():
        _require(path.parent.parent.is_dir(),
                 f"证据 JSON 的精确上级目录不存在：{path.parent.parent}")
        path.parent.mkdir()
    _require(path.parent.is_dir(), f"证据 JSON 父路径不是目录：{path.parent}")


def _write_bytes_new(path: Path, data: bytes) -> None:
    with path.open("xb") as destination:
        destination.write(data)


def _quote_cmd(value: str) -> str:
    _require("\n" not in value and "\r" not in value, "命令参数包含换行")
    if any(character in value for character in " &()^"):  # Windows cmd 参数按单项加引号。
        return '"' + value.replace('"', '\\"') + '"'
    return value


def _run_tool(name: str, args: list[str], work: Path, tool_bin: Path,
              timeout_seconds: float, no_progress_seconds: float,
              progress_pattern: re.Pattern[str] | None = None) -> dict[str, Any]:
    tool = tool_bin / f"{name}.bat"
    _require(tool.is_file(), f"找不到 Vivado 工具：{tool}")
    command = " ".join(_quote_cmd(value) for value in [str(tool), *args])
    full_command = f'cmd.exe /d /s /c "{command}"'
    log_path = work / f"{name}.stdout.log"
    started = time.monotonic()
    _log(f"START {name} cwd={work} command={command}")
    process = subprocess.Popen(
        full_command, cwd=work, shell=False, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
        bufsize=1,
    )
    lines: queue.Queue[str | None] = queue.Queue()

    def _reader() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            lines.put(line)
        lines.put(None)

    thread = threading.Thread(target=_reader, daemon=True)
    thread.start()
    last_progress = time.monotonic()
    output_lines: list[str] = []
    sentinel_seen = False
    with log_path.open("x", encoding="utf-8", newline="\n") as logfile:
        while not sentinel_seen or process.poll() is None:
            if time.monotonic() - started > timeout_seconds:
                process.kill()
                raise T34Error(f"{name} 超时；日志：{log_path}")
            try:
                line = lines.get(timeout=1.0)
            except queue.Empty:
                if name == "xsim" and time.monotonic() - last_progress > no_progress_seconds:
                    process.kill()
                    raise T34Error(f"xsim 连续 {no_progress_seconds:.0f}s 无栅格进度；日志：{log_path}")
                continue
            if line is None:
                sentinel_seen = True
                continue
            logfile.write(line)
            logfile.flush()
            output_lines.append(line)
            if progress_pattern is not None and progress_pattern.search(line):
                last_progress = time.monotonic()
                print(line.rstrip(), flush=True)
    thread.join(timeout=5)
    output = "".join(output_lines)
    exit_code = process.wait()
    elapsed = round(time.monotonic() - started, 3)
    _log(f"END {name} exit={exit_code} seconds={elapsed} log={log_path}")
    if exit_code != 0 or "ERROR:" in output or "FATAL:" in output:
        raise T34Error(f"{name} exit={exit_code}；日志：{log_path}；末尾：{output[-3000:]}")
    version_line = next((line.strip() for line in output.splitlines()
                         if any(token in line.lower() for token in
                                ("xvlog v", "xelab v", "xsim v", "vivado v"))), "unknown")
    return {
        "phase": name,
        "command": [str(tool), *args],
        "exit_code": exit_code,
        "tool_version": version_line,
        "seconds": elapsed,
        "log_path": str(log_path),
    }


def _log(message: str) -> None:
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    line = f"{timestamp} {message}"
    print(line, flush=True)
    if getattr(_log, "path", None) is not None:
        with _log.path.open("a", encoding="utf-8", newline="\n") as output:
            output.write(line + "\n")


def _render_synth_tcl(run_dir: Path, sources: list[Path]) -> str:
    def _braced(path: Path) -> str:
        value = str(path)
        _require("{" not in value and "}" not in value and "\n" not in value,
                 "Vivado Tcl 路径含不能安全引用的字符")
        return "{" + value + "}"

    source_lines = "\n".join(f"read_verilog -sv {_braced(path)}" for path in sources[:5])
    report_path = run_dir / "utilization.rpt"
    tcl = "\n".join((
        source_lines,
        "synth_design -top s2a_conv_layer35_oc0_full -part xc7z020clg400-1 -flatten_hierarchy none",
        f"report_utilization -file {_braced(report_path)}",
        "exit",
        "",
    ))
    return tcl


def _generate_synth_tcl(run_dir: Path, sources: list[Path]) -> Path:
    tcl = _render_synth_tcl(run_dir, sources)
    path = run_dir / "synth.tcl"
    with path.open("x", encoding="utf-8", newline="\n") as output:
        output.write(tcl)
    return path


def _parse_utilization(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    patterns = {
        "lut": r"^\|\s*Slice LUTs\*?\s*\|\s*([\d,]+)",
        "ff": r"^\|\s*Slice Registers\s*\|\s*([\d,]+)",
        "bram_tile": r"^\|\s*Block RAM Tile\s*\|\s*([\d,]+)",
        "dsp": r"^\|\s*DSPs\s*\|\s*([\d,]+)",
    }
    resources: dict[str, int] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        _require(match is not None, f"综合 utilization.rpt 缺少资源项：{key}")
        resources[key] = int(match.group(1).replace(",", ""))
    return resources


def _parse_xsim_summary(output: str) -> dict[str, Any]:
    matches = re.findall(r"^PASS T34 (.+)$", output, re.MULTILINE)
    _require(len(matches) == 1, f"xsim 缺少唯一 PASS T34 汇总，匹配数={len(matches)}")
    values: dict[str, Any] = {}
    for key, value in re.findall(r"([a-z0-9_]+)=([0-9a-fA-F,]+)", matches[0]):
        if key == "corners":
            values[key] = [int(part) for part in value.split(",")]
        elif key.endswith("lanes") or key in ("error_mask",):
            values[key] = int(value, 16)
        else:
            values[key] = int(value)
    return values


def _validate_xsim_summary(summary: dict[str, Any], expected: dict[str, int]) -> None:
    expected_fields = {
        "pixels": expected["output_pixels"],
        "raw": expected["raw_int32_compares"],
        "feature_reads": expected["feature_reads"],
        "weight_reads": expected["weight_reads"],
        "output_writes": expected["output_writes"],
        "padding": expected["padding_taps"],
        "taps": expected["all_kernel_taps"],
        "feature_lanes": 15,
        "weight_lanes": 15,
        "output_lanes": 15,
        "corners": [expected["corner_padding_taps_each"]] * 4,
        "error_mask": (1 << 1) | (1 << 2) | (1 << 6),
        "fault_responses": 3,
        "abort_cancels": 2,
        "reset_cancels": 1,
        "request_stalls": expected["request_stall_cycles"],
        "feature_transfers": expected["feature_transfers"],
        "feature_stall_cycles": expected["feature_stall_cycles"],
        "weight_transfers": expected["weight_transfers"],
        "weight_stall_cycles": expected["weight_stall_cycles"],
        "output_transfers": expected["output_transfers"],
        "output_stall_cycles": expected["output_stall_cycles"],
    }
    for class_name in ("feature", "weight", "output"):
        for slot in range(len(STALL_SEQUENCE)):
            expected_fields[f"{class_name}_slot{slot}"] = expected[f"{class_name}_slot{slot}"]
    for key, value in expected_fields.items():
        _require(summary.get(key) == value,
                 f"xsim 计数不符 {key}: {summary.get(key)} != {value}")
    _require(int(summary.get("result_stalls", 0)) > 0, "xsim 未覆盖 result backpressure")


def _write_evidence(path: Path, evidence: dict[str, Any]) -> None:
    payload = (json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    with path.open("xb") as output:
        output.write(payload)


def _require_temp_run_directory(path: Path) -> None:
    _require(path.is_absolute() and path.is_dir(), "恢复运行目录必须是存在的绝对目录")
    temp_root = Path(tempfile.gettempdir()).resolve()
    target = path.resolve()
    try:
        common = Path(os.path.commonpath((str(temp_root), str(target))))
    except ValueError as exc:
        raise T34Error(f"恢复运行目录不在系统 TEMP 下：{path}") from exc
    _require(common == temp_root, f"恢复运行目录必须位于系统 TEMP 下：{path}")
    _require(re.fullmatch(r"s2a_t34_layer35_(?:full|frozen_stalls)_[A-Za-z0-9_-]+",
                          path.name) is not None,
             "恢复目录名不符合 T34 全跑目录格式")


def _verify_logged_phase(orchestration: str, name: str, run_dir: Path,
                         command: list[str]) -> dict[str, Any]:
    command_text = " ".join(_quote_cmd(value) for value in command)
    expected_start = f"START {name} cwd={run_dir} command={command_text}"
    rows = []
    for index, line in enumerate(orchestration.splitlines()):
        if " " in line:
            timestamp, payload = line.split(" ", 1)
            rows.append((index, timestamp, payload))
    starts = [(index, timestamp) for index, timestamp, payload in rows
              if payload == expected_start]
    ends = [(index, timestamp, payload) for index, timestamp, payload in rows
            if payload.startswith(f"END {name} ")]
    _require(len(starts) == 1 and len(ends) == 1,
             f"orchestration.log 的 {name} START/END 记录不唯一")
    start_index, _start_time = starts[0]
    end_index, end_time, end_payload = ends[0]
    _require(start_index < end_index, f"orchestration.log 的 {name} START/END 顺序错误")
    match = re.fullmatch(rf"END {re.escape(name)} exit=(\d+) seconds=([0-9.]+) log=(.+)",
                         end_payload)
    _require(match is not None, f"orchestration.log 的 {name} END 格式错误")
    exit_code = int(match.group(1))
    seconds = float(match.group(2))
    log_path = run_dir / f"{name}.stdout.log"
    _require(exit_code == 0 and seconds > 0 and match.group(3) == str(log_path),
             f"orchestration.log 的 {name} exit/path/duration 不通过")
    return {
        "phase": name,
        "command": command,
        "exit_code": exit_code,
        "seconds": seconds,
        "log_path": str(log_path),
        "start_index": start_index,
        "end_index": end_index,
        "end_timestamp": end_time,
    }


def _check_no_active_run_tool(run_dir: Path) -> str:
    script = (
        "$needle = '" + run_dir.name + "'; "
        "$p = Get-CimInstance Win32_Process | Where-Object { "
        "$_.Name -match '^(xvlog|xelab|xsim|vivado)\\.exe$' -and "
        "$_.CommandLine -and $_.CommandLine.Contains($needle) }; "
        "if ($p) { $p | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Compress; exit 3 }; "
        "Write-Output 'NO_ACTIVE_T34_TOOL_PROCESS'"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30, check=False,
    )
    _require(result.returncode == 0 and result.stdout.strip() == "NO_ACTIVE_T34_TOOL_PROCESS",
             f"无法确认 T34 工具进程已退出：{result.stdout.strip()} {result.stderr.strip()}")
    return result.stdout.strip()


def _finalize_existing_run(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    evidence_path = Path(args.evidence_path)
    _require_temp_run_directory(run_dir)
    _require(evidence_path.is_absolute(), "恢复证据 JSON 路径必须是绝对路径")
    _require(evidence_path.suffix.lower() == ".json", "恢复证据路径必须以 .json 结尾")
    _require(not evidence_path.exists(), f"恢复证据已存在，拒绝覆盖：{evidence_path}")
    _require(evidence_path.parent.is_dir(), f"恢复证据父目录不存在：{evidence_path.parent}")

    inputs, prepared = _preflight(report_progress=False)
    summary = prepared["summary"]
    oracle = prepared["oracle"]
    orchestration_path = run_dir / "orchestration.log"
    _require(orchestration_path.is_file(), "完成的 T34 orchestration.log 不存在")
    orchestration = orchestration_path.read_text(encoding="utf-8", errors="strict")
    evidence_paths = re.findall(r"^\S+ evidence_path=(.+)$", orchestration, re.MULTILINE)
    _require(len(evidence_paths) == 1, "orchestration.log 未唯一绑定原 FAIL evidence")
    failed_evidence_path = Path(evidence_paths[0])
    _require(failed_evidence_path.is_absolute() and failed_evidence_path.is_file(),
             "原 FAIL evidence 路径缺失或不是绝对路径")
    _require(failed_evidence_path.resolve() != evidence_path.resolve(),
             "恢复证据不能覆盖原 FAIL evidence")
    failed_evidence, failed_evidence_sha = _read_json(failed_evidence_path)
    _require(failed_evidence.get("schema") == "GestureForge-S2A-T34-layer35-oc0-full-v1" and
             failed_evidence.get("task_id") == "S2A-T34" and
             failed_evidence.get("status") == "FAIL" and
             failed_evidence.get("paths", {}).get("run_dir") == str(run_dir) and
             failed_evidence.get("paths", {}).get("evidence_path") == str(failed_evidence_path),
             "原 FAIL evidence 的任务、状态或运行路径不匹配")
    failure = failed_evidence.get("failure", {})
    failure_message = str(failure.get("message", ""))
    _require(failure.get("type") == "T34Error" and
             "utilization.rpt" in failure_message and failure_message.lower().endswith("lut"),
             "原 FAIL evidence 不是已知的 utilization LUT 标签解析失败")
    _require("FAIL T34Error:" in orchestration and
             f"failure_evidence={failed_evidence_path}" in orchestration,
             "orchestration.log 未记录原 utilization parser 失败")

    for key, expected in inputs["evidence_bindings"].items():
        _require(failed_evidence.get("bindings", {}).get(key) == expected,
                 f"原 FAIL evidence 冻结绑定已变化：{key}")
    original_t34_sources = failed_evidence.get("bindings", {}).get("T34_source_hashes", {})
    runner_relative = "verification/test_s2a_conv_layer35_oc0_full_rtl.py"
    expected_t34_keys = set((*T34_SOURCES[4:], runner_relative))
    _require(set(original_t34_sources) == expected_t34_keys,
             "原 FAIL evidence 的 T34 源 hash 键集合不符")
    current_source_hashes = {relative: _sha256_file(ROOT / relative) for relative in T34_SOURCES}
    for relative in T34_SOURCES:
        if relative in T17_SOURCE_HASHES:
            expected_hash = T17_SOURCE_HASHES[relative]
        else:
            expected_hash = original_t34_sources.get(relative)
        _require(current_source_hashes[relative] == expected_hash,
                 f"编译/综合 RTL 源 hash 与冻结运行绑定不符：{relative}")
    current_runner_hash = _sha256_file(ROOT / runner_relative)
    original_runner_hash = original_t34_sources[runner_relative]
    _require(re.fullmatch(r"[0-9a-f]{64}", original_runner_hash) is not None,
             "原运行 runner 源 hash 格式不符")

    expected_fixture = dict(summary["fixture"])
    expected_fixture["file_path"] = str(run_dir / "feature_input.bin")
    expected_fixture["weight_oc0_file_path"] = str(run_dir / "weight_oc0.bin")
    expected_oracle = dict(summary["oracle"])
    expected_oracle["golden_file_path"] = str(run_dir / "golden.bin")
    _require(failed_evidence.get("baseline") == inputs["ancestry"] and
             failed_evidence.get("fixture") == expected_fixture and
             failed_evidence.get("oracle") == expected_oracle and
             failed_evidence.get("expected_counts") == summary["expected_counts"] and
             failed_evidence.get("geometry") == _geometry_record(inputs),
             "原 FAIL evidence 的冻结基线、fixture、oracle、计数或几何与重算结果不符")

    expected_files = {
        "feature_input.bin": oracle["input_fixture"],
        "weight_oc0.bin": inputs["weight_oc0"],
        "golden.bin": oracle["golden_bytes"],
        "observed_raw.bin": oracle["raw_bytes"],
        "observed_output.bin": oracle["quantized_bytes"],
    }
    artifact_hashes: dict[str, dict[str, Any]] = {}
    for filename, expected_bytes in expected_files.items():
        path = run_dir / filename
        _require(path.is_file(), f"恢复 run 缺少 fixture/trace：{filename}")
        actual_bytes = path.read_bytes()
        _require(actual_bytes == expected_bytes, f"恢复 run 文件与重算 oracle 不逐字节相符：{filename}")
        artifact_hashes[filename] = {
            "bytes": len(actual_bytes), "sha256": _sha256_bytes(actual_bytes),
        }

    simulation = failed_evidence.get("simulation", {})
    _require(simulation.get("status") == "FAIL" and
             simulation.get("raw_int32_compares") == OUTPUT_PIXELS and
             simulation.get("quantized_int8_compares") == OUTPUT_PIXELS and
             simulation.get("grid_rows") == OUTPUT_WIDTH and
             simulation.get("grid_columns") == OUTPUT_WIDTH,
             "原 FAIL evidence 未记录完整的 26x26 逐值仿真")
    _require(simulation.get("observed_raw_int32_le_sha256") ==
             _sha256_bytes(oracle["raw_bytes"]) and
             simulation.get("observed_output_int8_sha256") ==
             _sha256_bytes(oracle["quantized_bytes"]),
             "原 FAIL evidence trace SHA-256 与重算 raw/output 不符")
    xsim_path = run_dir / "xsim.stdout.log"
    _require(xsim_path.is_file(), "xsim stdout 日志不存在")
    xsim_text = xsim_path.read_text(encoding="utf-8", errors="replace")
    xsim_summary = _parse_xsim_summary(xsim_text)
    _validate_xsim_summary(xsim_summary, summary["expected_counts"])
    _require(simulation.get("xsim_summary") == xsim_summary,
             "原 FAIL evidence xsim summary 与 xsim stdout 不一致")
    progress_rows = [(int(row), int(outputs)) for row, outputs in re.findall(
        r"^PROGRESS T34 row=(\d+)/25 outputs=(\d+)/676$", xsim_text, re.MULTILINE
    )]
    _require(progress_rows == [(row, (row + 1) * OUTPUT_WIDTH)
                               for row in range(OUTPUT_WIDTH)],
             "xsim stdout 未按序记录全部 26 行栅格进度")
    _require(simulation.get("memory_error_codes") == {
                 "1": "PASS feature read", "2": "PASS weight read", "6": "PASS output write"
             } and simulation.get("pending_cancellation") == {
                 "read_abort": "PASS", "read_hard_reset": "PASS",
                 "output_write_abort": "PASS; zero accepted write side effect"
             }, "原 FAIL evidence 的错误传播/取消恢复断言不完整")

    tool_bin = Path(args.xilinx_bin)
    _require(tool_bin.is_absolute() and tool_bin.is_dir(), "Vivado bin 绝对路径不可用")
    sources = [ROOT / relative for relative in T34_SOURCES]
    synth_tcl_path = run_dir / "synth.tcl"
    _require(synth_tcl_path.is_file() and
             synth_tcl_path.read_bytes() == _render_synth_tcl(run_dir, sources).encode("utf-8"),
             "恢复 run 的 synth.tcl 内容与当前固定综合命令不一致")
    expected_commands = {
        "xvlog": [str(tool_bin / "xvlog.bat"), "-sv", *map(str, sources)],
        "xelab": [str(tool_bin / "xelab.bat"), "-top", "tb_s2a_conv_layer35_oc0_full",
                  "-snapshot", "s2a_t34_snapshot"],
        "xsim": [str(tool_bin / "xsim.bat"), "-R", "s2a_t34_snapshot"],
        "vivado": [str(tool_bin / "vivado.bat"), "-mode", "batch", "-notrace",
                   "-source", str(synth_tcl_path), "-log", "vivado_synth.log",
                   "-journal", "vivado_synth.jou"],
    }
    old_phases = simulation.get("phases", [])
    _require(len(old_phases) == 3 and
             [phase.get("phase") for phase in old_phases] == ["xvlog", "xelab", "xsim"],
             "原 FAIL evidence 的仿真 phase 清单不完整")
    phase_records = []
    phase_order = []
    for name, phase in zip(("xvlog", "xelab", "xsim"), old_phases):
        _require(phase.get("command") == expected_commands[name] and
                 phase.get("exit_code") == 0 and
                 phase.get("log_path") == str(run_dir / f"{name}.stdout.log"),
                 f"原 evidence 的 {name} command/exit/log path 不符")
        record = _verify_logged_phase(orchestration, name, run_dir, expected_commands[name])
        _require(float(phase.get("seconds", -1)) == record["seconds"],
                 f"原 evidence 的 {name} elapsed 与 orchestration 不符")
        phase_records.append(record)
        phase_order.extend((record["start_index"], record["end_index"]))
    synth_record = _verify_logged_phase(
        orchestration, "vivado", run_dir, expected_commands["vivado"]
    )
    phase_order.extend((synth_record["start_index"], synth_record["end_index"]))
    _require(phase_order == sorted(phase_order), "四个工具阶段的 orchestration 顺序错误")

    log_files = (
        "orchestration.log", "xvlog.stdout.log", "xvlog.log",
        "xelab.stdout.log", "xelab.log", "xsim.stdout.log", "xsim.log", "xsim.jou",
        "vivado.stdout.log", "vivado_synth.log", "vivado_synth.jou",
    )
    for filename in log_files:
        path = run_dir / filename
        _require(path.is_file() and path.stat().st_size > 0, f"恢复 run 日志缺失/为空：{filename}")
        content = path.read_bytes()
        artifact_hashes[filename] = {"bytes": len(content), "sha256": _sha256_bytes(content)}
        decoded = content.decode("utf-8", errors="replace").upper()
        _require(re.search(r"(?m)^\s*(?:ERROR:|FATAL:)", decoded) is None,
                 f"恢复 run 日志含工具错误标记：{filename}")

    synth_stdout = (run_dir / "vivado.stdout.log").read_text(encoding="utf-8", errors="replace")
    synth_log = (run_dir / "vivado_synth.log").read_text(encoding="utf-8", errors="replace")
    _require("synth_design completed successfully" in synth_stdout and
             "synth_design completed successfully" in synth_log,
             "Vivado stdout/native log 未确认 synth_design 成功")
    synth_version = next((line.strip() for line in synth_stdout.splitlines()
                          if "vivado v" in line.lower()), "unknown")
    synth_record["tool_version"] = synth_version
    resources = _parse_utilization(run_dir / "utilization.rpt")
    for filename in ("synth.tcl", "utilization.rpt"):
        path = run_dir / filename
        _require(path.is_file() and path.stat().st_size > 0, f"综合产物缺失/为空：{filename}")
        content = path.read_bytes()
        artifact_hashes[filename] = {"bytes": len(content), "sha256": _sha256_bytes(content)}

    active_process_check = _check_no_active_run_tool(run_dir)
    failed_evidence_record = {
        "path": str(failed_evidence_path),
        "bytes": failed_evidence_path.stat().st_size,
        "sha256": failed_evidence_sha,
        "failure": failure,
    }
    _prepare_evidence_target(evidence_path)
    finalized = dict(failed_evidence)
    finalized.pop("failure", None)
    finalized["recovered_from_failure"] = failed_evidence_record
    finalized["status"] = "PASS"
    finalized["paths"] = dict(finalized["paths"])
    finalized["paths"]["evidence_path"] = str(evidence_path)
    finalized["simulation"] = dict(simulation)
    finalized["simulation"]["status"] = "PASS"
    finalized["simulation"]["summary"] = xsim_summary
    finalized["synthesis"] = {
        "status": "PASS",
        "part": "xc7z020clg400-1",
        "top": "s2a_conv_layer35_oc0_full",
        "xdc": "NOT_PROVIDED",
        "timing_conclusion": "N/A; standalone synthesis has no XDC",
        "resources": resources,
        "phase": {key: value for key, value in synth_record.items()
                  if key not in ("start_index", "end_index", "end_timestamp")},
        "report_path": str(run_dir / "utilization.rpt"),
    }
    finalized["recovery"] = {
        "method": "read-only finalize of completed run; no tools relaunched",
        "status": "PASS",
        "active_run_process_check": active_process_check,
        "xsim_progress_rows_verified": len(progress_rows),
        "raw_int32_elements_verified": OUTPUT_PIXELS,
        "quantized_int8_elements_verified": OUTPUT_PIXELS,
        "tool_exit_codes": {"xvlog": 0, "xelab": 0, "xsim": 0, "vivado": 0},
        "tool_phase_order": ["xvlog", "xelab", "xsim", "vivado"],
        "artifacts": artifact_hashes,
        "compiled_source_sha256": current_source_hashes,
        "runner_source_sha256_at_failed_run": original_runner_hash,
        "runner_source_sha256_at_finalization": current_runner_hash,
        "notes": "compiled RTL/TB sources, frozen bindings, existing fixtures/traces, tool logs, TCL and utilization report were rechecked before final evidence creation",
    }
    finalized["completed_utc8"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    _write_evidence(evidence_path, finalized)
    print(json.dumps({
        "result": "PASS",
        "evidence_path": str(evidence_path),
        "reused_run_dir": str(run_dir),
        "tool_exit_codes": finalized["recovery"]["tool_exit_codes"],
        "xsim_pixels": xsim_summary["pixels"],
        "resources": resources,
    }, ensure_ascii=False, indent=2), flush=True)
    return 0


def _attest_existing_pass(args: argparse.Namespace) -> int:
    """只读复核已通过的 T34 run，并为新路径生成含工件哈希的证据。"""
    run_dir = Path(args.run_dir)
    source_evidence_path = Path(args.source_evidence_path)
    evidence_path = Path(args.evidence_path)
    _require_temp_run_directory(run_dir)
    _require(source_evidence_path.is_absolute() and source_evidence_path.is_file(),
             "attestation 输入 evidence 必须是存在的绝对文件")
    _prepare_evidence_target(evidence_path)
    source_evidence_hash = _sha256_file(source_evidence_path)
    source_evidence = json.loads(source_evidence_path.read_text(encoding="utf-8"))
    _require(source_evidence.get("status") == "PASS" and
             source_evidence.get("paths", {}).get("run_dir") == str(run_dir),
             "输入 evidence 不是该 TEMP 目录的 PASS run")

    inputs, prepared = _preflight(report_progress=True)
    summary = prepared["summary"]
    oracle = prepared["oracle"]
    _require(source_evidence.get("baseline") == inputs["ancestry"] and
             source_evidence.get("geometry") == _geometry_record(inputs) and
             source_evidence.get("expected_counts") == summary["expected_counts"],
             "PASS evidence 的基线、几何或独立计数与当前冻结输入不符")
    _require(source_evidence.get("fixture", {}).get("seed") == SEED and
             source_evidence.get("fixture", {}).get("sha256") ==
             oracle["fixture_summary"]["sha256"] and
             source_evidence.get("oracle", {}).get("raw_int32_le_sha256") ==
             oracle["oracle_summary"]["raw_int32_le_sha256"] and
             source_evidence.get("oracle", {}).get("quantized_int8_sha256") ==
             oracle["oracle_summary"]["quantized_int8_sha256"],
             "PASS evidence fixture seed 或 golden SHA 与重算 oracle 不符")

    runner_relative = "verification/test_s2a_conv_layer35_oc0_full_rtl.py"
    recorded_sources = source_evidence.get("bindings", {}).get("T34_source_hashes", {})
    source_hashes_at_attestation = {
        relative: _sha256_file(ROOT / relative)
        for relative in (*T34_SOURCES[4:], runner_relative)
    }
    for relative in T34_SOURCES[4:]:
        _require(recorded_sources.get(relative) == source_hashes_at_attestation[relative],
                 f"RTL/TB 源码与通过 run 绑定不一致：{relative}")
    recorded_runner_hash = recorded_sources.get(runner_relative)
    _require(isinstance(recorded_runner_hash, str) and
             re.fullmatch(r"[0-9a-f]{64}", recorded_runner_hash) is not None,
             "PASS evidence runner 源 hash 格式错误")

    expected_fixture = dict(oracle["fixture_summary"])
    expected_fixture["file_path"] = str(run_dir / "feature_input.bin")
    expected_fixture["weight_oc0_file_path"] = str(run_dir / "weight_oc0.bin")
    expected_oracle = dict(oracle["oracle_summary"])
    expected_oracle["golden_file_path"] = str(run_dir / "golden.bin")
    _require(source_evidence.get("fixture") == expected_fixture and
             source_evidence.get("oracle") == expected_oracle,
             "PASS evidence fixture/oracle 描述与当前重算结果不符")

    expected_files = {
        "feature_input.bin": oracle["input_fixture"],
        "weight_oc0.bin": inputs["weight_oc0"],
        "golden.bin": oracle["golden_bytes"],
        "observed_raw.bin": oracle["raw_bytes"],
        "observed_output.bin": oracle["quantized_bytes"],
    }
    artifact_hashes: dict[str, dict[str, Any]] = {}
    for filename, expected_bytes in expected_files.items():
        path = run_dir / filename
        _require(path.is_file(), f"TEMP run 缺少输入/trace 工件：{filename}")
        actual_bytes = path.read_bytes()
        _require(actual_bytes == expected_bytes,
                 f"TEMP 工件未与独立 oracle 逐字节相符：{filename}")
        artifact_hashes[filename] = {
            "bytes": len(actual_bytes), "sha256": _sha256_bytes(actual_bytes),
        }

    simulation = source_evidence.get("simulation", {})
    _require(simulation.get("raw_int32_compares") == OUTPUT_PIXELS and
             simulation.get("quantized_int8_compares") == OUTPUT_PIXELS and
             simulation.get("observed_raw_int32_le_sha256") ==
             _sha256_bytes(oracle["raw_bytes"]) and
             simulation.get("observed_output_int8_sha256") ==
             _sha256_bytes(oracle["quantized_bytes"]),
             "PASS evidence 缺少 676/676 逐值比较或 observed trace SHA 不符")
    xsim_path = run_dir / "xsim.stdout.log"
    _require(xsim_path.is_file(), "xsim stdout 日志不存在")
    xsim_text = xsim_path.read_text(encoding="utf-8", errors="replace")
    xsim_summary = _parse_xsim_summary(xsim_text)
    _validate_xsim_summary(xsim_summary, summary["expected_counts"])
    _require(simulation.get("xsim_summary") == xsim_summary,
             "PASS evidence summary 与 xsim stdout 不一致")
    progress_rows = [(int(row), int(outputs)) for row, outputs in re.findall(
        r"^PROGRESS T34 row=(\d+)/25 outputs=(\d+)/676$", xsim_text, re.MULTILINE
    )]
    _require(progress_rows == [(row, (row + 1) * OUTPUT_WIDTH)
                               for row in range(OUTPUT_WIDTH)],
             "xsim stdout 未按序记录全部 26 行进度")

    tool_bin = Path(args.xilinx_bin)
    _require(tool_bin.is_absolute() and tool_bin.is_dir(), "Vivado bin 绝对路径不可用")
    sources = [ROOT / relative for relative in T34_SOURCES]
    synth_tcl_path = run_dir / "synth.tcl"
    _require(synth_tcl_path.is_file() and
             synth_tcl_path.read_bytes() == _render_synth_tcl(run_dir, sources).encode("utf-8"),
             "synth.tcl 与固定 standalone synthesis 命令不符")
    expected_commands = {
        "xvlog": [str(tool_bin / "xvlog.bat"), "-sv", *map(str, sources)],
        "xelab": [str(tool_bin / "xelab.bat"), "-top", "tb_s2a_conv_layer35_oc0_full",
                  "-snapshot", "s2a_t34_snapshot"],
        "xsim": [str(tool_bin / "xsim.bat"), "-R", "s2a_t34_snapshot"],
        "vivado": [str(tool_bin / "vivado.bat"), "-mode", "batch", "-notrace",
                   "-source", str(synth_tcl_path), "-log", "vivado_synth.log",
                   "-journal", "vivado_synth.jou"],
    }
    phases = simulation.get("phases", [])
    _require(len(phases) == 3 and
             [phase.get("phase") for phase in phases] == ["xvlog", "xelab", "xsim"],
             "PASS evidence 工具 phase 清单不完整")
    phase_records = []
    phase_order = []
    for name, phase in zip(("xvlog", "xelab", "xsim"), phases):
        _require(phase.get("command") == expected_commands[name] and
                 phase.get("exit_code") == 0 and
                 phase.get("log_path") == str(run_dir / f"{name}.stdout.log"),
                 f"PASS evidence 的 {name} command/exit/log path 不符")
        record = _verify_logged_phase(
            (run_dir / "orchestration.log").read_text(encoding="utf-8", errors="replace"),
            name, run_dir, expected_commands[name],
        )
        _require(float(phase.get("seconds", -1)) == record["seconds"],
                 f"PASS evidence 的 {name} duration 与 orchestration 不符")
        phase_records.append(record)
        phase_order.extend((record["start_index"], record["end_index"]))
    synth_phase = source_evidence.get("synthesis", {}).get("phase", {})
    _require(synth_phase.get("command") == expected_commands["vivado"] and
             synth_phase.get("phase") == "vivado" and
             synth_phase.get("exit_code") == 0 and
             synth_phase.get("log_path") == str(run_dir / "vivado.stdout.log"),
             "PASS evidence 的 Vivado command/exit/log path 不符")
    orchestration_text = (run_dir / "orchestration.log").read_text(encoding="utf-8", errors="replace")
    synth_record = _verify_logged_phase(
        orchestration_text, "vivado", run_dir, expected_commands["vivado"]
    )
    _require(float(synth_phase.get("seconds", -1)) == synth_record["seconds"],
             "PASS evidence 的 Vivado duration 與 orchestration 不符")
    phase_order.extend((synth_record["start_index"], synth_record["end_index"]))
    _require(phase_order == sorted(phase_order), "四个工具阶段的 orchestration 顺序错误")

    log_files = (
        "orchestration.log", "xvlog.stdout.log", "xvlog.log",
        "xelab.stdout.log", "xelab.log", "xsim.stdout.log", "xsim.log", "xsim.jou",
        "vivado.stdout.log", "vivado_synth.log", "vivado_synth.jou",
    )
    for filename in log_files:
        path = run_dir / filename
        _require(path.is_file() and path.stat().st_size > 0,
                 f"TEMP run 日志缺失/为空：{filename}")
        content = path.read_bytes()
        artifact_hashes[filename] = {"bytes": len(content), "sha256": _sha256_bytes(content)}
        decoded = content.decode("utf-8", errors="replace").upper()
        _require(re.search(r"(?m)^\s*(?:ERROR:|FATAL:)", decoded) is None,
                 f"TEMP run 日志包含 ERROR/FATAL：{filename}")

    synth_stdout = (run_dir / "vivado.stdout.log").read_text(encoding="utf-8", errors="replace")
    synth_log = (run_dir / "vivado_synth.log").read_text(encoding="utf-8", errors="replace")
    _require("synth_design completed successfully" in synth_stdout and
             "synth_design completed successfully" in synth_log,
             "Vivado stdout/native log 未确认 synth_design 成功")
    resources = _parse_utilization(run_dir / "utilization.rpt")
    _require(source_evidence.get("synthesis", {}).get("resources") == resources,
             "PASS evidence synthesis resources 与 utilization.rpt 不一致")
    for filename in ("synth.tcl", "utilization.rpt"):
        path = run_dir / filename
        _require(path.is_file() and path.stat().st_size > 0,
                 f"TEMP run 综合工件缺失/为空：{filename}")
        content = path.read_bytes()
        artifact_hashes[filename] = {"bytes": len(content), "sha256": _sha256_bytes(content)}

    active_process_check = _check_no_active_run_tool(run_dir)
    attested = dict(source_evidence)
    attested["paths"] = dict(source_evidence["paths"])
    attested["paths"]["evidence_path"] = str(evidence_path)
    attested["attestation"] = {
        "method": "read-only verification of the existing PASS run; no simulator or synthesis relaunch",
        "status": "PASS",
        "source_evidence": {
            "path": str(source_evidence_path),
            "bytes": source_evidence_path.stat().st_size,
            "sha256": source_evidence_hash,
        },
        "active_run_process_check": active_process_check,
        "xsim_progress_rows_verified": len(progress_rows),
        "raw_int32_elements_verified": OUTPUT_PIXELS,
        "quantized_int8_elements_verified": OUTPUT_PIXELS,
        "tool_exit_codes": {record["phase"]: record["exit_code"] for record in phase_records}
                            | {"vivado": synth_record["exit_code"]},
        "tool_phase_order": ["xvlog", "xelab", "xsim", "vivado"],
        "artifacts": artifact_hashes,
        "compiled_rtl_tb_sha256_verified": {
            relative: source_hashes_at_attestation[relative]
            for relative in T34_SOURCES[4:]
        },
        "runner_sha256_at_simulation": recorded_runner_hash,
        "runner_sha256_at_attestation": source_hashes_at_attestation[runner_relative],
        "notes": "fixtures/traces were compared byte-for-byte with a recomputed oracle; tool logs, synth TCL and utilization report were hashed",
    }
    attested["completed_utc8"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    _write_evidence(evidence_path, attested)
    print(json.dumps({
        "result": "PASS",
        "evidence_path": str(evidence_path),
        "source_evidence_sha256": source_evidence_hash,
        "run_dir": str(run_dir),
        "tool_exit_codes": attested["attestation"]["tool_exit_codes"],
        "xsim_pixels": xsim_summary["pixels"],
        "artifact_hash_count": len(artifact_hashes),
        "resources": resources,
    }, ensure_ascii=False, indent=2), flush=True)
    return 0


def _run_full(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    evidence_path = Path(args.evidence_path)
    _require_new_absolute_directory(run_dir, "运行目录", beneath_temp=True)
    _prepare_evidence_target(evidence_path)
    run_dir.mkdir()
    _log.path = run_dir / "orchestration.log"
    _log("S2A-T34 full run begins")
    _log(f"run_dir={run_dir}")
    _log(f"evidence_path={evidence_path}")

    evidence: dict[str, Any] = {
        "schema": "GestureForge-S2A-T34-layer35-oc0-full-v1",
        "task_id": "S2A-T34",
        "status": "RUNNING",
        "scope": "tiny416 cfg layer35 oc0; full 26x26 NCHW output grid",
        "bindings": {},
        "fixture": {},
        "oracle": {},
        "expected_counts": {},
        "simulation": {"phases": [], "summary": None},
        "synthesis": {"status": "NOT_RUN", "part": "xc7z020clg400-1",
                       "xdc": "NOT_PROVIDED", "timing_conclusion": "N/A"},
        "paths": {"run_dir": str(run_dir), "evidence_path": str(evidence_path)},
    }
    phases: list[dict[str, Any]] = evidence["simulation"]["phases"]
    try:
        inputs, prepared = _preflight(report_progress=True)
        oracle = prepared["oracle"]
        summary = prepared["summary"]
        evidence["baseline"] = inputs["ancestry"]
        evidence["bindings"] = inputs["evidence_bindings"]
        evidence["bindings"]["T34_source_hashes"] = {
            relative: _sha256_file(ROOT / relative)
            for relative in (*T34_SOURCES[4:], "verification/test_s2a_conv_layer35_oc0_full_rtl.py")
        }
        evidence["fixture"] = summary["fixture"]
        evidence["oracle"] = summary["oracle"]
        evidence["expected_counts"] = summary["expected_counts"]
        evidence["geometry"] = _geometry_record(inputs)
        _write_bytes_new(run_dir / "feature_input.bin", oracle["input_fixture"])
        _write_bytes_new(run_dir / "weight_oc0.bin", inputs["weight_oc0"])
        _write_bytes_new(run_dir / "golden.bin", oracle["golden_bytes"])
        evidence["fixture"]["file_path"] = str(run_dir / "feature_input.bin")
        evidence["fixture"]["weight_oc0_file_path"] = str(run_dir / "weight_oc0.bin")
        evidence["oracle"]["golden_file_path"] = str(run_dir / "golden.bin")

        tool_bin = Path(args.xilinx_bin)
        _require(tool_bin.is_absolute() and tool_bin.is_dir(),
                 f"Vivado bin 目录不可用：{tool_bin}")
        sources = [ROOT / relative for relative in T34_SOURCES]
        phases.append(_run_tool("xvlog", ["-sv", *map(str, sources)], run_dir,
                                tool_bin, 600, args.no_progress_seconds))
        phases.append(_run_tool("xelab", ["-top", "tb_s2a_conv_layer35_oc0_full",
                                           "-snapshot", "s2a_t34_snapshot"], run_dir,
                                tool_bin, 600, args.no_progress_seconds))
        xsim_phase = _run_tool("xsim", ["-R", "s2a_t34_snapshot"], run_dir,
                               tool_bin, args.overall_timeout, args.no_progress_seconds,
                               progress_pattern=re.compile(r"PROGRESS T34 row="))
        phases.append(xsim_phase)
        xsim_text = (run_dir / "xsim.stdout.log").read_text(encoding="utf-8", errors="replace")
        xsim_summary = _parse_xsim_summary(xsim_text)
        _validate_xsim_summary(xsim_summary, summary["expected_counts"])
        raw_observed = (run_dir / "observed_raw.bin").read_bytes()
        output_observed = (run_dir / "observed_output.bin").read_bytes()
        _require(raw_observed == oracle["raw_bytes"], "xsim 观察到的 raw INT32 trace 与 oracle 不同")
        _require(output_observed == oracle["quantized_bytes"],
                 "xsim 观察到的输出 INT8 trace 与 oracle 不同")
        evidence["simulation"].update({
            "status": "PASS",
            "xsim_summary": xsim_summary,
            "raw_int32_compares": OUTPUT_PIXELS,
            "quantized_int8_compares": OUTPUT_PIXELS,
            "observed_raw_int32_le_sha256": _sha256_bytes(raw_observed),
            "observed_output_int8_sha256": _sha256_bytes(output_observed),
            "address_lane_order": "PASS; per-request feature/weight/output byte address, word alignment, single-byte strobe, lane, and NCHW order checked",
            "single_outstanding_stability": "PASS; valid/address/write/data/strobes held to acceptance",
            "memory_error_codes": {"1": "PASS feature read", "2": "PASS weight read", "6": "PASS output write"},
            "pending_cancellation": {"read_abort": "PASS", "read_hard_reset": "PASS",
                                     "output_write_abort": "PASS; zero accepted write side effect"},
            "backpressure": {
                "request_policy": "per transfer class repeat exactly [0,1,2,7,3] low-ready cycles",
                "request_stall_sequence": list(STALL_SEQUENCE),
                "request_stall_prng_seed": None,
                "fixture_seed": SEED,
                "total_request_stall_cycles": xsim_summary["request_stalls"],
                "classes": {
                    class_name: {
                        "transfers": xsim_summary[f"{class_name}_transfers"],
                        "slot_counts": [xsim_summary[f"{class_name}_slot{slot}"]
                                        for slot in range(len(STALL_SEQUENCE))],
                        "stall_cycles": xsim_summary[f"{class_name}_stall_cycles"],
                    }
                    for class_name in ("feature", "weight", "output")
                },
                "held_result_cycles": xsim_summary["result_stalls"],
            },
            "grid_rows": 26,
            "grid_columns": 26,
        })

        synth_tcl = _generate_synth_tcl(run_dir, sources)
        synth_args = ["-mode", "batch", "-notrace", "-source", str(synth_tcl),
                      "-log", "vivado_synth.log", "-journal", "vivado_synth.jou"]
        synth = _run_tool("vivado", synth_args, run_dir, tool_bin, 3600,
                          args.no_progress_seconds)
        utilization_path = run_dir / "utilization.rpt"
        resources = _parse_utilization(utilization_path)
        evidence["synthesis"] = {
            "status": "PASS",
            "part": "xc7z020clg400-1",
            "top": "s2a_conv_layer35_oc0_full",
            "xdc": "NOT_PROVIDED",
            "timing_conclusion": "N/A; standalone synthesis has no XDC",
            "resources": resources,
            "phase": synth,
            "report_path": str(utilization_path),
        }
        evidence["simulation"]["elapsed_seconds"] = round(
            sum(float(phase["seconds"]) for phase in phases), 3
        )
        evidence["status"] = "PASS"
        evidence["completed_utc8"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    except Exception as exc:
        evidence["status"] = "FAIL"
        evidence["failure"] = {"type": type(exc).__name__, "message": str(exc)}
        evidence["simulation"]["status"] = "FAIL"
        evidence["simulation"]["phases"] = phases
        evidence["completed_utc8"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        _write_evidence(evidence_path, evidence)
        _log(f"FAIL {type(exc).__name__}: {exc}")
        _log(f"failure_evidence={evidence_path}")
        return 1
    _write_evidence(evidence_path, evidence)
    _log(f"PASS evidence={evidence_path}")
    _log(f"resources={evidence['synthesis']['resources']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="验证 tiny416 layer35/oc0 全 26x26 栅格")
    parser.add_argument("--preflight-only", action="store_true",
                        help="只核冻结绑定并计算独立 CPU oracle，不创建文件")
    parser.add_argument("--finalize-existing-run", action="store_true",
                        help="只读校验已完成的 TEMP run 并写新 evidence，不重跑工具")
    parser.add_argument("--attest-existing-pass", action="store_true",
                        help="只读复核现存 PASS run 并写入含工件 SHA-256 的新 evidence")
    parser.add_argument("--run-dir", help="全跑时的新 TEMP 目录，或 finalize 时的现存 TEMP 目录")
    parser.add_argument("--evidence-path", help="新建证据 JSON 的绝对路径，已存在时拒绝覆盖")
    parser.add_argument("--source-evidence-path", help="attest 时待复核的现存 PASS evidence 绝对路径")
    parser.add_argument("--xilinx-bin", default=str(XILINX_BIN_DEFAULT),
                        help="Vivado bin 绝对路径")
    parser.add_argument("--overall-timeout", type=float, default=7200.0)
    parser.add_argument("--no-progress-seconds", type=float, default=300.0)
    args = parser.parse_args(argv)
    try:
        if args.preflight_only:
            _require(not args.finalize_existing_run and not args.attest_existing_pass,
                     "--preflight-only 不能与 finalize/attest 同时使用")
            _inputs, result = _preflight(report_progress=True)
            print(json.dumps(result["summary"], ensure_ascii=False, indent=2), flush=True)
            return 0
        if args.finalize_existing_run:
            _require(not args.attest_existing_pass,
                     "--finalize-existing-run 与 --attest-existing-pass 不能同时使用")
            _require(args.run_dir is not None and args.evidence_path is not None,
                     "finalize 必须提供 --run-dir 与 --evidence-path")
            return _finalize_existing_run(args)
        if args.attest_existing_pass:
            _require(args.run_dir is not None and args.evidence_path is not None and
                     args.source_evidence_path is not None,
                     "attest 必须提供 --run-dir、--source-evidence-path 与 --evidence-path")
            return _attest_existing_pass(args)
        _require(args.run_dir is not None and args.evidence_path is not None,
                 "完整运行必须提供 --run-dir 与 --evidence-path")
        _require(args.overall_timeout > 0 and args.no_progress_seconds > 0,
                 "timeout 与 no-progress 时间必须为正数")
        return _run_full(args)
    except Exception as exc:
        print(f"FAIL {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
