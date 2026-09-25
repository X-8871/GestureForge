"""为 S2A-T17 生成冻结卷积向量并验证单输出元素 RTL。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import time
import unittest

import numpy as np

try:
    from . import s2a_conv_requant_proof as requant_proof
except ImportError:
    import s2a_conv_requant_proof as requant_proof


_ROOT = Path(__file__).resolve().parents[1]
_MANIFEST = _ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
_T16_PROOF = _ROOT / "report/evidence/S2A-T16/conv_requant_proof.json"
_T16_SCRIPT = _ROOT / "verification/s2a_conv_requant_proof.py"
_WEIGHT_REPORT = _ROOT / "report/evidence/S1-T02/20260922_s1_t02_d2_tiny416_int8_weight_r2.json"
_EVIDENCE = _ROOT / "report/evidence/S2A-T17/conv_engine_simulation.json"
_BASELINE = "f0b7791d2db7b0a13126d3a0d3db586a01a294b1"
_MANIFEST_SHA = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_D2_SHA = "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393"
_T16_PROOF_SHA = "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24"
_T16_SCRIPT_SHA = "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_RANDOM_PER_LAYER = 1000
_DIRECTED_PER_LAYER = 16
_CASE_HEADER = struct.Struct("<11IB")
_CONFIG_FIELDS = (
    "layer_index", "weight_layer_index", "input_base", "input_length",
    "input_batch_count", "input_channels", "input_height", "input_width",
    "output_base", "output_length", "output_batch_count", "output_channels",
    "output_height", "output_width", "kernel_height", "kernel_width",
    "stride_y", "stride_x", "pad_left", "pad_right", "pad_top",
    "pad_bottom", "groups", "padding_value", "weight_base",
    "weight_package_length", "weight_offset", "weight_bytes", "case_count",
    "protocol_enable", "activation_mode",
)


class T17Error(RuntimeError):
    """报告冻结输入或仿真失败。"""


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _u32(value: int) -> int:
    return value & 0xFFFF_FFFF


def _signed_byte(value: int) -> int:
    value &= 0xFF
    return value if value < 128 else value - 256


class _XorShift32:
    """按 T01 规范维护单条共享随机数流。"""

    def __init__(self, state: int = 20260922) -> None:
        if not 0 < state <= 0xFFFF_FFFF:
            raise T17Error("xorshift32 状态必须为非零 uint32")
        self.state = state
        self.draws = 0

    def next_u32(self) -> int:
        value = self.state
        value = (value ^ ((value << 13) & 0xFFFF_FFFF)) & 0xFFFF_FFFF
        value ^= value >> 17
        value = (value ^ ((value << 5) & 0xFFFF_FFFF)) & 0xFFFF_FFFF
        self.state = value
        self.draws += 1
        return value

    def selector(self, bound: int) -> int:
        if bound <= 0:
            raise T17Error(f"非法随机 selector 上界：{bound}")
        return self.next_u32() % bound

    def int8(self) -> int:
        return (self.next_u32() & 255) % 255 - 127


def _load_bound_inputs() -> tuple[dict, dict, dict[int, bytes], Path]:
    if _sha(_MANIFEST) != _MANIFEST_SHA:
        raise T17Error("T01 manifest SHA-256 与冻结值不符")
    manifest = json.loads(_MANIFEST.read_text(encoding="utf-8"))
    d2_ref = _ROOT / "verification/s1_t02_d2_int8_forward.py"
    if _sha(d2_ref) != _D2_SHA:
        raise T17Error("D2 forward reference SHA-256 与冻结值不符")
    if _sha(_T16_PROOF) != _T16_PROOF_SHA or _sha(_T16_SCRIPT) != _T16_SCRIPT_SHA:
        raise T17Error("T16 证明文件或脚本 SHA-256 与冻结值不符")
    if _sha(_WEIGHT_REPORT) != manifest["bindings"]["weight_report"]["sha256"]:
        raise T17Error("T01 绑定的量化权重报告 SHA-256 不符")
    weight_report = json.loads(_WEIGHT_REPORT.read_text(encoding="utf-8"))
    package_binding = weight_report["package"]
    package_path = Path(package_binding["path"])
    if not package_path.is_file():
        raise T17Error(f"T01 绑定的 GFINT8W1 权重包不可读：{package_path}")
    package_bytes = package_path.read_bytes()
    package_sha = hashlib.sha256(package_bytes).hexdigest()
    if (len(package_bytes) != int(package_binding["bytes"]) or
            package_sha != package_binding["sha256"] or
            package_binding["sha256"] != manifest["address_map"]["weight_package"]["sha256"]):
        raise T17Error("GFINT8W1 包大小或 SHA-256 与 T01 绑定不符")
    if len(package_bytes) < 28:
        raise T17Error("GFINT8W1 包头截断")
    magic, version, layer_count, width, height = struct.unpack_from("<8sIIII", package_bytes, 0)
    channels = struct.unpack_from("<I", package_bytes, 24)[0]
    if (magic, version, width, height, channels) != (b"GFINT8W1", 1, 416, 416, 3):
        raise T17Error("GFINT8W1 包头不匹配 tiny416 冻结模型")

    layers = {int(layer["layer_index"]): layer for layer in manifest["layers"]}
    package_weights: dict[int, bytes] = {}
    offset = 28
    seen: set[int] = set()
    for _ in range(layer_count):
        if offset + 32 > len(package_bytes):
            raise T17Error("GFINT8W1 layer record 截断")
        record_offset = offset
        layer_id, filters, input_channels, groups, kernel, weight_count, _bn, scale_count = (
            struct.unpack_from("<8I", package_bytes, offset)
        )
        offset += 32
        scale_offset = offset
        bias_offset = scale_offset + filters * 4
        weight_offset = bias_offset + filters * 4
        end = weight_offset + weight_count
        if end > len(package_bytes) or layer_id in seen:
            raise T17Error(f"GFINT8W1 layer {layer_id} 区间越界或重复")
        seen.add(layer_id)
        if layer_id in layers and layers[layer_id]["op"] == "convolutional":
            layer = layers[layer_id]
            expected_offsets = layer["gf8_parameter_offsets"]
            actual_offsets = {
                "record_offset": record_offset,
                "weight_scale_offset": scale_offset,
                "fused_bias_offset": bias_offset,
                "quantized_weight_offset": weight_offset,
                "quantized_weight_bytes": weight_count,
            }
            if expected_offsets != actual_offsets:
                raise T17Error(f"layer {layer_id} GFINT8W1 偏移与 T01 manifest 不符")
            _, expected_channels, _, _ = layer["input_shape_nchw"]
            _, output_channels, _, _ = layer["output_shape_nchw"]
            kernel_h, kernel_w = layer["kernel_hw"]
            if (filters != output_channels or input_channels != expected_channels or groups != 1 or
                    kernel_h != kernel or kernel_w != kernel or
                    weight_count != output_channels * expected_channels * kernel_h * kernel_w or
                    scale_count != output_channels):
                raise T17Error(f"layer {layer_id} GFINT8W1 geometry与 T01 不符")
            package_weights[layer_id] = package_bytes[weight_offset:end]
        offset = end
    if offset != len(package_bytes) or len(package_weights) != 21:
        raise T17Error("GFINT8W1 包尾或 21 个卷积记录数量不匹配")
    t16 = json.loads(_T16_PROOF.read_text(encoding="utf-8"))
    if (t16["status"] != "EXACT_FIXED_POINT_FOUND" or
            t16["coverage"]["convolution_layers_audited"] != 21 or
            t16["coverage"]["output_channels_audited"] != 3164 or
            t16["coverage"]["output_channels_with_exact_candidate"] != 3164 or
            t16["coverage"]["failures"] != 0):
        raise T17Error("T16 不是完整 tiny416 卷积通道精确证明")
    return manifest, t16, package_weights, package_path


def _candidate_parameters(layer: dict, proof_summary: dict) -> list[dict[str, int]]:
    scales = np.asarray(layer["weight_scale_per_output_channel"], dtype=np.float64)
    real_scales = np.float64(float(layer["input_scale"])) * scales
    output_scale = float(layer["output_scale"])
    activation = str(layer["activation"])
    thresholds, _low, _high = requant_proof._d2_thresholds(
        real_scales, output_scale, activation
    )
    rows: list[dict[str, int]] = []
    digest = hashlib.sha256()
    for channel in range(len(real_scales)):
        positive_targets, negative_targets = requant_proof._branch_magnitude_thresholds(
            thresholds[channel]
        )
        ideal_positive = float(real_scales[channel]) / output_scale
        ideal_negative = ideal_positive if activation == "linear" else ideal_positive * 0.1
        if activation == "linear":
            positive, negative = requant_proof._find_linear_joint_candidate(
                positive_targets, negative_targets, ideal_positive
            )
        else:
            positive = requant_proof._find_candidate(
                positive_targets, requant_proof.INT32_MAX, ideal_positive
            )
            negative = requant_proof._find_candidate(
                negative_targets, 1 << 31, ideal_negative
            )
        if positive.get("status") != "exact" or negative.get("status") != "exact":
            raise T17Error(f"layer {layer['layer_index']} channel {channel} 缺少 T16 精确 M/Q")
        row = {
            "positive_multiplier": int(positive["multiplier"]),
            "positive_q_shift": int(positive["q_shift"]),
            "negative_multiplier": int(negative["multiplier"]),
            "negative_q_shift": int(negative["q_shift"]),
        }
        if (max(row["positive_multiplier"].bit_length(),
                row["negative_multiplier"].bit_length()) > 30 or
                max(row["positive_q_shift"], row["negative_q_shift"]) > 47):
            raise T17Error(f"layer {layer['layer_index']} channel {channel} M/Q 超过 T16 位宽")
        if activation == "linear" and (
                row["positive_multiplier"] != row["negative_multiplier"] or
                row["positive_q_shift"] != row["negative_q_shift"]):
            raise T17Error(f"layer {layer['layer_index']} channel {channel} linear M/Q 不共用")
        digest.update((f"{channel},{row['positive_q_shift']},{row['positive_multiplier']},"
                       f"{row['negative_q_shift']},{row['negative_multiplier']}\n").encode("ascii"))
        rows.append(row)
    if digest.hexdigest() != proof_summary["candidate_parameter_sha256"]:
        raise T17Error(f"layer {layer['layer_index']} T16 M/Q 参数 hash 不匹配")
    return rows


def _d2_quantize(accumulator: int, input_scale: float, weight_scale: float,
                 output_scale: float, activation: str) -> int:
    real_scale = float(np.float64(input_scale) * np.float64(weight_scale))
    scaled = float(accumulator) * real_scale
    scaled = scaled / float(output_scale)
    if activation == "leaky" and scaled < 0.0:
        scaled = scaled * 0.1
    rounded = math.floor(abs(scaled) + 0.5)
    if scaled < 0.0:
        rounded = -rounded
    return max(-127, min(127, rounded))


def _fixed_point_quantize(accumulator: int, parameters: dict[str, int]) -> int:
    negative = accumulator < 0
    magnitude = abs(accumulator)
    multiplier = parameters["negative_multiplier"] if negative else parameters["positive_multiplier"]
    q_shift = parameters["negative_q_shift"] if negative else parameters["positive_q_shift"]
    product = magnitude * multiplier
    rounded = (product + (1 << (q_shift - 1))) >> q_shift if q_shift else product
    return max(-127, min(127, -rounded if negative else rounded))


def _mask_padding_activations(layer: dict, row: int, col: int,
                              activations: list[int]) -> tuple[list[int], int]:
    """按 D2 NCHW 几何将边界 padding tap 替换为 INT8 零。"""
    _, input_channels, input_height, input_width = map(int, layer["input_shape_nchw"])
    kernel_height, kernel_width = map(int, layer["kernel_hw"])
    stride_y, stride_x = map(int, layer["stride_hw"])
    pad_left, _pad_right, pad_top, _pad_bottom = map(int, layer["padding_lrtb"])
    reduction_count = input_channels * kernel_height * kernel_width
    if len(activations) != reduction_count:
        raise T17Error("边界 golden 向量 K 长度不匹配")
    effective = list(activations)
    padding_taps = 0
    for index in range(reduction_count):
        kernel_y = (index % (kernel_height * kernel_width)) // kernel_width
        kernel_x = index % kernel_width
        input_y = row * stride_y + kernel_y - pad_top
        input_x = col * stride_x + kernel_x - pad_left
        if not (0 <= input_y < input_height and 0 <= input_x < input_width):
            effective[index] = 0
            padding_taps += 1
    return effective, padding_taps


def _expected_lane_masks(layer: dict, manifest: dict,
                         output_queries: list[dict[str, int]]) -> tuple[int, int, int]:
    """独立计算各后端字节地址的 lane 覆盖。"""
    _, input_channels, input_height, input_width = map(int, layer["input_shape_nchw"])
    _, output_channels, output_height, output_width = map(int, layer["output_shape_nchw"])
    kernel_height, kernel_width = map(int, layer["kernel_hw"])
    stride_y, stride_x = map(int, layer["stride_hw"])
    pad_left, _pad_right, pad_top, _pad_bottom = map(int, layer["padding_lrtb"])
    input_base, _input_length = _input_base(manifest, layer)
    weight_base = int(manifest["address_map"]["weight_package"]["address"])
    weight_offset = int(layer["gf8_parameter_offsets"]["quantized_weight_offset"])
    output_base = int(layer["tensor_address"])
    reduction_count = input_channels * kernel_height * kernel_width
    feature_mask = 0
    weight_mask = 0
    output_mask = 0
    for query in output_queries:
        channel = int(query["output_channel"])
        row = int(query["output_y"])
        col = int(query["output_x"])
        if not 0 <= channel < output_channels:
            raise T17Error("lane golden output channel 越界")
        output_address = output_base + ((channel * output_height + row) * output_width + col)
        output_mask |= 1 << (output_address & 3)
        for index in range(reduction_count):
            input_channel = index // (kernel_height * kernel_width)
            kernel_y = (index % (kernel_height * kernel_width)) // kernel_width
            kernel_x = index % kernel_width
            input_y = row * stride_y + kernel_y - pad_top
            input_x = col * stride_x + kernel_x - pad_left
            if 0 <= input_y < input_height and 0 <= input_x < input_width:
                feature_address = input_base + (
                    (input_channel * input_height + input_y) * input_width + input_x
                )
                weight_address = weight_base + weight_offset + channel * reduction_count + index
                feature_mask |= 1 << (feature_address & 3)
                weight_mask |= 1 << (weight_address & 3)
    return feature_mask, weight_mask, output_mask


def _checked_accumulator(activations: list[int], weights: list[int], bias: int) -> int:
    if len(activations) != len(weights):
        raise T17Error("向量 K 长度不匹配")
    accumulator = int(bias)
    for index, (activation, weight) in enumerate(zip(activations, weights)):
        accumulator += int(activation) * int(weight)
        if not -(1 << 31) <= accumulator <= (1 << 31) - 1:
            raise T17Error(f"卷积向量在 tap {index} 发生 INT32 overflow")
    return accumulator


def _input_base(manifest: dict, layer: dict) -> tuple[int, int]:
    source = layer["input_tensor_indices"][0]
    if source == "network_input":
        tensor = manifest["address_map"]["input"]
        return int(tensor["address"]), int(tensor["length_bytes"])
    producer = manifest["layers"][int(source)]
    return int(producer["tensor_address"]), int(producer["tensor_length_bytes"])


def _case_record(layer: dict, parameters: dict[str, int], weights_all: bytes,
                 case_ordinal: int, case_kind: int, channel: int, row: int,
                 col: int, bias: int, activations: list[int], expected_accumulator: int | None = None) -> tuple[bytes, dict[str, int]]:
    _, input_channels, _, _ = layer["input_shape_nchw"]
    output_channels = int(layer["output_shape_nchw"][1])
    kernel_h, kernel_w = map(int, layer["kernel_hw"])
    reduction_count = input_channels * kernel_h * kernel_w
    if len(activations) != reduction_count or not 0 <= channel < output_channels:
        raise T17Error(f"layer {layer['layer_index']} case {case_ordinal} K/channel mismatch")
    effective_activations, padding_taps = _mask_padding_activations(
        layer, row, col, activations
    )
    weight_begin = channel * reduction_count
    weights = [_signed_byte(value) for value in weights_all[weight_begin:weight_begin + reduction_count]]
    accumulator = _checked_accumulator(effective_activations, weights, bias)
    if expected_accumulator is not None and accumulator != int(expected_accumulator):
        raise T17Error(f"layer {layer['layer_index']} directed case {case_ordinal} INT32 golden mismatch")
    d2_output = _d2_quantize(
        accumulator, float(layer["input_scale"]),
        float(layer["weight_scale_per_output_channel"][channel]),
        float(layer["output_scale"]), str(layer["activation"]),
    )
    candidate_output = _fixed_point_quantize(accumulator, parameters)
    if candidate_output != d2_output:
        raise T17Error(
            f"layer {layer['layer_index']} case {case_ordinal} D2/T16 output mismatch "
            f"{d2_output} != {candidate_output}"
        )
    packed = _CASE_HEADER.pack(
        _u32(case_ordinal), _u32(case_kind), _u32(channel), _u32(row), _u32(col),
        _u32(bias), _u32(parameters["positive_multiplier"]),
        _u32(parameters["positive_q_shift"]), _u32(parameters["negative_multiplier"]),
        _u32(parameters["negative_q_shift"]), _u32(accumulator), d2_output & 255,
    )
    packed += bytes(_u32(value) & 255 for value in activations)
    packed += bytes(_u32(value) & 255 for value in weights)
    return packed, {
        "case_ordinal": case_ordinal, "case_kind": case_kind, "output_channel": channel,
        "output_y": row, "output_x": col, "accumulator_int32": accumulator,
        "output_int8": d2_output, "padding_taps": padding_taps,
    }


def _write_layer_vectors(path: Path, layer: dict, package_weights: bytes,
                         parameters: list[dict[str, int]], manifest: dict,
                         mode: str, random_stream: _XorShift32 | None = None) -> dict:
    plan = manifest["operator_test_plan"]
    layer_id = int(layer["layer_index"])
    layer_directed = plan["directed_case_vectors"]["convolutional"][str(layer_id)]
    if len(layer_directed) != _DIRECTED_PER_LAYER:
        raise T17Error(f"layer {layer_id} T01 directed 覆盖不是 16 项")
    output_channels, output_height, output_width = map(int, layer["output_shape_nchw"][1:])
    input_channels = int(layer["input_shape_nchw"][1])
    kernel_h, kernel_w = map(int, layer["kernel_hw"])
    reduction_count = input_channels * kernel_h * kernel_w
    tensor_weights = package_weights
    if len(tensor_weights) != output_channels * reduction_count:
        raise T17Error(f"layer {layer_id} GF8 权重张量长度不符")
    vectors_sha = hashlib.sha256()
    activations_sha = hashlib.sha256()
    used_weights_sha = hashlib.sha256()
    golden_sha = hashlib.sha256()
    golden_rows: list[dict[str, int]] = []
    padding_taps_expected = 0
    random_draw_start = random_stream.draws if random_stream else 0
    initial_state = random_stream.state if random_stream else None
    random_count = 0
    directed_count = 0
    with path.open("wb") as handle:
        if mode == "full":
            for case_index in range(_RANDOM_PER_LAYER):
                channel = random_stream.selector(output_channels)
                row = random_stream.selector(output_height)
                col = random_stream.selector(output_width)
                activations = [random_stream.int8() for _ in range(reduction_count)]
                bias = int(layer["bias_accumulator_int32_per_output_channel"][channel])
                record, golden = _case_record(
                    layer, parameters[channel], tensor_weights, case_index, 0,
                    channel, row, col, bias, activations,
                )
                handle.write(record)
                vectors_sha.update(record)
                activations_sha.update(bytes(_u32(value) & 255 for value in activations))
                begin = channel * reduction_count
                used_weights_sha.update(tensor_weights[begin:begin + reduction_count])
                golden_rows.append(golden)
                padding_taps_expected += golden["padding_taps"]
                random_count += 1

            directed_offset = _RANDOM_PER_LAYER
            for directed_index, vector in enumerate(layer_directed):
                batch, channel, row, col = map(int, vector["target_output_nchw"])
                if batch != 0:
                    raise T17Error(f"layer {layer_id} directed batch 非零")
                activations = [int(value) for value in vector["input_reduction_int8"]]
                vector_weights = [int(value) for value in vector["weight_reduction_int8"]]
                begin = channel * reduction_count
                package_row = [_signed_byte(value) for value in tensor_weights[begin:begin + reduction_count]]
                if vector_weights != package_row:
                    raise T17Error(f"layer {layer_id} directed {directed_index} 权重字节与 GF8 包不符")
                if int(vector["bias_int32"]) != int(layer["bias_accumulator_int32_per_output_channel"][channel]):
                    raise T17Error(f"layer {layer_id} directed {directed_index} bias 与 T01 不符")
                if (float(vector["weight_scale"]) != float(layer["weight_scale_per_output_channel"][channel]) or
                        float(vector["output_scale"]) != float(layer["output_scale"]) or
                        str(vector["activation"]) != str(layer["activation"]) or
                        vector["padding_value_int8"] != 0):
                    raise T17Error(f"layer {layer_id} directed {directed_index} scale/activation/padding 不符")
                record, golden = _case_record(
                    layer, parameters[channel], tensor_weights,
                    directed_offset + directed_index, 1, channel, row, col,
                    int(vector["bias_int32"]), activations,
                    int(vector["expected_int32_result"]),
                )
                handle.write(record)
                vectors_sha.update(record)
                activations_sha.update(bytes(_u32(value) & 255 for value in activations))
                used_weights_sha.update(tensor_weights[begin:begin + reduction_count])
                golden_rows.append(golden)
                padding_taps_expected += golden["padding_taps"]
                directed_count += 1
        else:
            vector = layer_directed[0]
            batch, channel, row, col = map(int, vector["target_output_nchw"])
            if batch != 0:
                raise T17Error(f"layer {layer_id} directed batch 非零")
            activations = [int(value) for value in vector["input_reduction_int8"]]
            vector_weights = [int(value) for value in vector["weight_reduction_int8"]]
            begin = channel * reduction_count
            package_row = [_signed_byte(value) for value in tensor_weights[begin:begin + reduction_count]]
            if vector_weights != package_row:
                raise T17Error(f"layer {layer_id} directed 0 权重字节与 GF8 包不符")
            if int(vector["bias_int32"]) != int(layer["bias_accumulator_int32_per_output_channel"][channel]):
                raise T17Error(f"layer {layer_id} directed 0 bias 与 T01 不符")
            record, golden = _case_record(
                layer, parameters[channel], tensor_weights, 0, 1, channel, row, col,
                int(vector["bias_int32"]), activations,
                int(vector["expected_int32_result"]),
            )
            handle.write(record)
            vectors_sha.update(record)
            activations_sha.update(bytes(_u32(value) & 255 for value in activations))
            used_weights_sha.update(tensor_weights[begin:begin + reduction_count])
            golden_rows.append(golden)
            padding_taps_expected += golden["padding_taps"]
            directed_count = 1
    for row in golden_rows:
        golden_sha.update(struct.pack(
            "<IIIIIiBI", row["case_ordinal"], row["case_kind"],
            row["output_channel"], row["output_y"], row["output_x"],
            row["accumulator_int32"], row["output_int8"] & 255,
            row["padding_taps"],
        ))
    feature_lane_mask, weight_lane_mask, output_lane_mask = _expected_lane_masks(
        layer, manifest, golden_rows
    )
    return {
        "layer_index": layer_id,
        "random_cases": random_count,
        "directed_cases": directed_count,
        "case_count": random_count + directed_count,
        "reduction_length": reduction_count,
        "vector_sha256": vectors_sha.hexdigest(),
        "activation_bytes_sha256": activations_sha.hexdigest(),
        "selected_gf8_weight_bytes_sha256": used_weights_sha.hexdigest(),
        "golden_output_sha256": golden_sha.hexdigest(),
        "random_stream_start_state": initial_state,
        "random_stream_end_state": random_stream.state if random_stream else None,
        "random_stream_u32_draws": (random_stream.draws - random_draw_start) if random_stream else 0,
        "output_queries": len(golden_rows),
        "expected_padding_taps": padding_taps_expected,
        "expected_valid_taps": len(golden_rows) * reduction_count - padding_taps_expected,
        "expected_feature_lane_mask": feature_lane_mask,
        "expected_weight_lane_mask": weight_lane_mask,
        "expected_output_lane_mask": output_lane_mask,
    }


def _layer_config(manifest: dict, layer: dict, case_count: int,
                  protocol_enable: bool) -> dict[str, int]:
    input_base, input_length = _input_base(manifest, layer)
    amap = manifest["address_map"]
    input_batch, input_channels, input_height, input_width = map(int, layer["input_shape_nchw"])
    output_batch, output_channels, output_height, output_width = map(int, layer["output_shape_nchw"])
    kernel_height, kernel_width = map(int, layer["kernel_hw"])
    stride_y, stride_x = map(int, layer["stride_hw"])
    pad_left, pad_right, pad_top, pad_bottom = map(int, layer["padding_lrtb"])
    weights = amap["weight_package"]
    offsets = layer["gf8_parameter_offsets"]
    return {
        "layer_index": int(layer["layer_index"]),
        "weight_layer_index": int(layer["weight_layer_index"]),
        "input_base": input_base,
        "input_length": input_length,
        "input_batch_count": input_batch,
        "input_channels": input_channels,
        "input_height": input_height,
        "input_width": input_width,
        "output_base": int(layer["tensor_address"]),
        "output_length": int(layer["tensor_length_bytes"]),
        "output_batch_count": output_batch,
        "output_channels": output_channels,
        "output_height": output_height,
        "output_width": output_width,
        "kernel_height": kernel_height,
        "kernel_width": kernel_width,
        "stride_y": stride_y,
        "stride_x": stride_x,
        "pad_left": pad_left,
        "pad_right": pad_right,
        "pad_top": pad_top,
        "pad_bottom": pad_bottom,
        "groups": int(layer["groups"]),
        "padding_value": int(layer["padding_value_int8"]),
        "weight_base": int(weights["address"]),
        "weight_package_length": int(weights["length_bytes"]),
        "weight_offset": int(offsets["quantized_weight_offset"]),
        "weight_bytes": int(offsets["quantized_weight_bytes"]),
        "case_count": case_count,
        "protocol_enable": int(protocol_enable),
        "activation_mode": 1 if layer["activation"] == "leaky" else 0,
    }


def _write_test_files(work: Path, config: dict[str, int]) -> None:
    values = [config[name] for name in _CONFIG_FIELDS]
    (work / "s2a_t17_config.txt").write_text(
        " ".join(str(value) for value in values) + "\n", encoding="ascii", newline="\n"
    )


def _run_phase(name: str, args: list[str], work: Path, timeout: float) -> dict:
    tool = _XILINX_BIN / f"{name}.bat"
    if not tool.is_file():
        raise T17Error(f"找不到 Vivado 工具：{tool}")
    command = " ".join(f'"{value}"' if (" " in value or "&" in value) else value
                       for value in [str(tool), *args])
    started = time.monotonic()
    result = subprocess.run(
        f'cmd.exe /d /s /c "{command}"', cwd=work, shell=False,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout, check=False,
    )
    output = result.stdout + "\n" + result.stderr
    (work / f"{name}.log").write_text(output, encoding="utf-8", newline="\n")
    if result.returncode != 0 or "ERROR:" in output or "FATAL:" in output or "FAIL" in output:
        raise T17Error(f"{name} exit={result.returncode}; log={work / (name + '.log')}; tail={output[-4000:]}")
    return {
        "phase": name,
        "command": [str(tool), *args],
        "exit_code": result.returncode,
        "seconds": round(time.monotonic() - started, 3),
        "log_path": str(work / f"{name}.log"),
    }


def _compile_simulator(work: Path) -> list[dict]:
    sources = [
        _ROOT / "src/int8_conv_tap_geometry.sv",
        _ROOT / "src/int8_conv_weight_address.sv",
        _ROOT / "src/int8_mac_accumulator.sv",
        _ROOT / "src/s2a_conv_engine.sv",
        _ROOT / "sim/tb_s2a_conv_engine.sv",
    ]
    phases = [
        _run_phase("xvlog", ["-sv", *map(str, sources)], work, timeout=600),
        _run_phase("xelab", ["-top", "tb_s2a_conv_engine", "-snapshot", "s2a_t17_snapshot"],
                   work, timeout=600),
    ]
    return phases


def _run_xsim(work: Path, timeout: float) -> tuple[dict, str]:
    started = time.monotonic()
    tool = _XILINX_BIN / "xsim.bat"
    if not tool.is_file():
        raise T17Error(f"找不到 Vivado 工具：{tool}")
    command = f'"{tool}" -R s2a_t17_snapshot'
    result = subprocess.run(
        f'cmd.exe /d /s /c "{command}"', cwd=work, shell=False,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=timeout, check=False,
    )
    output = result.stdout + "\n" + result.stderr
    (work / "xsim.log").write_text(output, encoding="utf-8", newline="\n")
    if result.returncode != 0 or "ERROR:" in output or "FATAL:" in output or "FAIL" in output:
        raise T17Error(f"xsim exit={result.returncode}; log={work / 'xsim.log'}; tail={output[-5000:]}")
    version_line = next((line.strip() for line in output.splitlines()
                         if "xsim v" in line.lower()), "unknown")
    return ({"phase": "xsim", "exit_code": result.returncode,
              "command": [str(tool), "-R", "s2a_t17_snapshot"],
              "tool_version": version_line,
              "seconds": round(time.monotonic() - started, 3),
             "log_path": str(work / "xsim.log")}, output)


def _verify_summary(output: str, layer_id: int, vector_meta: dict) -> dict[str, int]:
    import re

    match = re.search(
        r"PASS S2A-T17 layer=(\d+) vectors=(\d+) input_reads=(\d+) "
        r"weight_reads=(\d+) output_writes=(\d+) padding_taps=(\d+) "
        r"protocol_cases=(\d+) protocol_errors=(\d+) "
        r"feature_lane_mask=([0-9a-fA-F]+) weight_lane_mask=([0-9a-fA-F]+) "
        r"output_lane_mask=([0-9a-fA-F]+)", output,
    )
    if not match:
        raise T17Error(f"xsim 缺少唯一 PASS 汇总；末尾：{output[-2500:]}")
    names = ("layer_index", "vectors", "input_reads", "weight_reads", "output_writes",
             "padding_taps", "protocol_cases", "protocol_errors")
    summary = {name: int(value) for name, value in zip(names, match.groups()[:8])}
    summary.update({
        "feature_lane_mask": int(match.group(9), 16),
        "weight_lane_mask": int(match.group(10), 16),
        "output_lane_mask": int(match.group(11), 16),
    })
    expected_vectors = int(vector_meta["case_count"])
    if summary["layer_index"] != layer_id or summary["vectors"] != expected_vectors:
        raise T17Error(f"xsim 汇总覆盖不符：{summary}")
    if summary["output_writes"] != expected_vectors:
        raise T17Error(f"xsim 成功写回数量不符：{summary}")
    if (summary["input_reads"] != int(vector_meta["expected_valid_taps"]) or
            summary["weight_reads"] != int(vector_meta["expected_valid_taps"]) or
            summary["padding_taps"] != int(vector_meta["expected_padding_taps"])):
        raise T17Error(f"xsim 特征/权重/填充 tap 数量与 Python 几何 golden 不符：{summary}")
    expected_masks = {
        "feature_lane_mask": int(vector_meta["expected_feature_lane_mask"]),
        "weight_lane_mask": int(vector_meta["expected_weight_lane_mask"]),
        "output_lane_mask": int(vector_meta["expected_output_lane_mask"]),
    }
    if any(summary[name] != expected for name, expected in expected_masks.items()):
        raise T17Error(f"xsim byte-lane 覆盖与 Python 地址 golden 不符：{summary}")
    return summary


def _source_hashes() -> dict[str, str]:
    names = [
        "src/s2a_conv_engine.sv", "sim/tb_s2a_conv_engine.sv",
        "verification/test_s2a_conv_engine_rtl.py",
        "src/int8_conv_tap_geometry.sv", "src/int8_conv_weight_address.sv",
        "src/int8_mac_accumulator.sv",
    ]
    return {name: _sha(_ROOT / name) for name in names}


class TestS2AConvEngineSmoke(unittest.TestCase):
    """先用 T01 已物化的 layer0 第 0 个向量闭合仿真路径。"""

    def test_directed_memory_smoke(self) -> None:
        manifest, proof, package_weights, _package_path = _load_bound_inputs()
        proof_layers = {int(item["layer_index"]): item for item in proof["layers"]}
        layer = next(item for item in manifest["layers"]
                     if item["op"] == "convolutional" and item["layer_index"] == 0)
        parameters = _candidate_parameters(layer, proof_layers[0])
        work = Path(tempfile.mkdtemp(prefix="s2a_t17_conv_smoke_"))
        vector_meta = _write_layer_vectors(
            work / "s2a_t17_vectors.bin", layer, package_weights[0], parameters,
            manifest, "smoke",
        )
        _write_test_files(work, _layer_config(manifest, layer, 1, True))
        phases = _compile_simulator(work)
        phase, output = _run_xsim(work, timeout=600)
        summary = _verify_summary(output, 0, vector_meta)
        self.assertEqual(summary["input_reads"], summary["weight_reads"])
        self.assertEqual(summary["protocol_cases"], 1)
        self.assertGreaterEqual(summary["protocol_errors"], 4)
        print(json.dumps({"work_dir": str(work), "phases": [*phases, phase],
                          "vectors": vector_meta, "summary": summary}, ensure_ascii=False))


def _run_full() -> int:
    started = time.monotonic()
    manifest, proof, package_weights, package_path = _load_bound_inputs()
    conv_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "convolutional"),
        key=lambda layer: int(layer["layer_index"]),
    )
    proof_layers = {int(item["layer_index"]): item for item in proof["layers"]}
    random_stream = _XorShift32(20260922)
    work = Path(tempfile.mkdtemp(prefix="s2a_t17_conv_full_"))
    log_dir = work / "logs"
    log_dir.mkdir()
    all_parameters: dict[int, list[dict[str, int]]] = {}
    all_vector_meta: dict[int, dict] = {}
    for layer in conv_layers:
        layer_id = int(layer["layer_index"])
        all_parameters[layer_id] = _candidate_parameters(layer, proof_layers[layer_id])

    bindings = {
        "baseline_commit": _BASELINE,
        "t01_manifest_sha256": _sha(_MANIFEST),
        "d2_forward_sha256": _sha(_ROOT / "verification/s1_t02_d2_int8_forward.py"),
        "t16_proof_sha256": _sha(_T16_PROOF),
        "t16_script_sha256": _sha(_T16_SCRIPT),
        "weight_report_sha256": _sha(_WEIGHT_REPORT),
        "gfint8w1_package_sha256": _sha(package_path),
        "gfint8w1_package_bytes": package_path.stat().st_size,
        "source_sha256": _source_hashes(),
    }
    evidence = {
        "schema": "GestureForge-S2A-T17-conv-engine-simulation-v1",
        "task": "S2A-T17",
        "result": "IN_PROGRESS",
        "baseline_head": _BASELINE,
        "bindings": bindings,
        "random_policy": {
            "seed": 20260922,
            "generator": "xorshift32；每次 draw 执行 x=(x^(x<<13))&0xffffffff; x^=x>>17; x=(x^(x<<5))&0xffffffff",
            "suite_order": "仅 conv suite；按 cfg layer_index 升序，每层 random case 0..999 后接 directed case 0..15；conv 是 T01 operator ASCII 次序首项",
            "random_draw_order": "output_channel,row,col selector 后恰好 K 个 activation byte；每个 selector 用 next_u32 % bound；INT8=(next_u32&255)%255-127；GF8 weight 不耗随机数；padding activation 仍消耗后由 geometry 替换为零贡献；directed 不耗随机数",
            "total_random_cases_required": 21 * _RANDOM_PER_LAYER,
            "directed_cases_per_layer": _DIRECTED_PER_LAYER,
        },
        "t16_parameters": {
            "generation": "使用冻结 T16 proof helper 从 T01 binary64 scales 重建每通道 M/Q；每层 candidate_parameter_sha256 必须与 T16 JSON 一致",
            "channel_count": proof["coverage"]["output_channels_audited"],
            "all_parameters_verified": True,
        },
        "layers": [],
        "compile_phases": [],
        "vivado": {"bin": str(_XILINX_BIN), "logs_directory": str(log_dir)},
        "runner": {
            "command": [sys.executable, *sys.argv],
            "python_version": sys.version.split()[0],
        },
        "logs": "完整 stdout/stderr、命令耗时与向量文件留在系统 TEMP 日志目录；证据仅保存 SHA 与按层摘要。",
        "limitations": ["仅单卷积输出元素引擎，不代表完整卷积层调度或整网集成。",
                        "本任务未执行综合、资源/时序分析、板上验证或阶段 G5。"],
    }
    # 建立完整 M/Q hash 和 Vivado 快照后再逐层检查点运行。
    for layer in conv_layers:
        layer_id = int(layer["layer_index"])
        vector_path = work / f"layer_{layer_id}.bin"
        vector_meta = _write_layer_vectors(
            vector_path, layer, package_weights[layer_id], all_parameters[layer_id],
            manifest, "full", random_stream,
        )
        all_vector_meta[layer_id] = vector_meta
    expected_draws = sum(
        _RANDOM_PER_LAYER * (3 + int(layer["input_shape_nchw"][1]) *
                             int(layer["kernel_hw"][0]) * int(layer["kernel_hw"][1]))
        for layer in conv_layers
    )
    if random_stream.draws != expected_draws:
        raise T17Error(f"T01 PRNG draw count mismatch: {random_stream.draws} != {expected_draws}")
    evidence["random_policy"].update({
        "u32_draws_total": random_stream.draws,
        "expected_u32_draws_total": expected_draws,
        "final_state": random_stream.state,
    })
    base_layer = conv_layers[0]
    evidence["planned_layers"] = [all_vector_meta[int(layer["layer_index"])]
                                  for layer in conv_layers]
    _EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    _EVIDENCE.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8", newline="\n")
    _write_test_files(work, _layer_config(manifest, base_layer, 1016, True))
    evidence["compile_phases"] = _compile_simulator(work)
    evidence["layers"] = []
    for layer in conv_layers:
        layer_id = int(layer["layer_index"])
        vector_path = work / f"layer_{layer_id}.bin"
        vector_path.replace(work / "s2a_t17_vectors.bin")
        _write_test_files(work, _layer_config(manifest, layer, 1016, layer_id == 0))
        layer_start = time.monotonic()
        phase, output = _run_xsim(work, timeout=7200)
        summary = _verify_summary(output, layer_id, all_vector_meta[layer_id])
        evidence["tool_versions"] = {"vivado_simulator": phase["tool_version"]}
        (log_dir / f"layer_{layer_id}_xsim.log").write_text(output, encoding="utf-8", newline="\n")
        layer_entry = {
            **all_vector_meta[layer_id],
            "xsim": phase,
            "summary": summary,
            "elapsed_seconds": round(time.monotonic() - layer_start, 3),
            "protocol_suite": "executed once on layer 0" if layer_id == 0 else "covered by layer0",
        }
        evidence["layers"].append(layer_entry)
        evidence["result"] = "IN_PROGRESS"
        evidence["elapsed_seconds"] = round(time.monotonic() - started, 3)
        _EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
        _EVIDENCE.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8", newline="\n")
        print(json.dumps({"checkpoint_layer": layer_id,
                          "completed_layers": len(evidence["layers"]),
                          "elapsed_seconds": evidence["elapsed_seconds"],
                          "summary": summary}, ensure_ascii=False), flush=True)
    evidence["result"] = "PASS"
    evidence["elapsed_seconds"] = round(time.monotonic() - started, 3)
    evidence["acceptance"] = {
        "random_cases": 21 * _RANDOM_PER_LAYER,
        "directed_cases": 21 * _DIRECTED_PER_LAYER,
        "output_queries": 21 * (_RANDOM_PER_LAYER + _DIRECTED_PER_LAYER),
        "integer_mismatch_count": 0,
        "all_layer_xsim_exit_codes_zero": all(item["xsim"]["exit_code"] == 0 for item in evidence["layers"]),
        "all_layer_vectors": all(item["case_count"] == 1016 for item in evidence["layers"]),
    }
    _EVIDENCE.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8", newline="\n")
    print(f"PASS S2A-T17 full layers={len(conv_layers)} vectors=21336 "
          f"xorshift32_draws={random_stream.draws} evidence_sha256={_sha(_EVIDENCE)} "
          f"elapsed_seconds={evidence['elapsed_seconds']} log_dir={work}", flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="验证 S2A-T17 单卷积输出元素引擎")
    parser.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    args = parser.parse_args(argv)
    if args.mode == "full":
        return _run_full()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestS2AConvEngineSmoke)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
