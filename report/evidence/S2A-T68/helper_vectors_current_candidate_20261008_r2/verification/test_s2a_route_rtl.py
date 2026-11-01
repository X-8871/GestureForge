"""按 G0 冻结清单和共享随机流验证 route 单输出查询 RTL。"""

from __future__ import annotations

import hashlib
import json
import math
import struct
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


_MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
_XILINX_BIN = Path(r"D:\Xilinx\2026.1\Vivado\bin")
_RANDOM_SEED = 20260922
_EXPECTED_ROUTE_FINAL_STATE = 0x0BE74782
_MAX_SOURCE_CHANNELS = 256
_MAX_OUTPUT_CHANNELS = 512


class XorShift32:
    """维护 G0 定义的一条共享 xorshift32 状态流。"""

    def __init__(self, seed: int) -> None:
        self.state = seed & 0xFFFFFFFF

    def next_u32(self) -> int:
        value = self.state
        value ^= (value << 13) & 0xFFFFFFFF
        value &= 0xFFFFFFFF
        value ^= value >> 17
        value &= 0xFFFFFFFF
        value ^= (value << 5) & 0xFFFFFFFF
        self.state = value & 0xFFFFFFFF
        return self.state

    def selector(self, bound: int) -> int:
        if bound <= 0:
            raise ValueError("G0 随机选择器上界必须大于零")
        return self.next_u32() % bound

    def int8(self) -> int:
        return (self.next_u32() & 0xFF) % 255 - 127

    def int32(self) -> int:
        value = self.next_u32()
        return value if value < 0x80000000 else value - 0x100000000


def _sha256_bytes(data: bytes) -> str:
    """计算不可变字节的 SHA-256。"""
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    """计算文件原始字节的 SHA-256。"""
    return _sha256_bytes(path.read_bytes())


def _conv_reduction_lengths(manifest: dict) -> list[int]:
    """按 cfg layer_index 提取真实卷积点积长度。"""
    layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "convolutional"),
        key=lambda layer: layer["layer_index"],
    )
    lengths: list[int] = []
    for layer in layers:
        input_channels = layer["input_shape_nchw"][1]
        groups = layer["groups"]
        kernel_height, kernel_width = layer["kernel_hw"]
        if input_channels % groups:
            raise ValueError("G0 卷积输入通道不能被 groups 整除")
        lengths.append((input_channels // groups) * kernel_height * kernel_width)
    if len(lengths) != 21:
        raise ValueError("G0 tiny416 卷积层数量不再是 21")
    return lengths


def _advance_to_route_start(manifest: dict, rng: XorShift32) -> dict:
    """独立按 G0 ASCII operator 顺序推进卷积、MAC 与 maxpool。"""
    plan = manifest["operator_test_plan"]
    cases = plan["random_cases_per_model_layer"]
    if (cases != 1000 or plan["shared_primitive_random_cases"] != 1000 or
            "ASCII order" not in plan["case_order"] or
            "int8_mac" not in plan["case_order"]):
        raise ValueError("G0 算子随机顺序或样本数发生变化")

    conv_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "convolutional"),
        key=lambda layer: layer["layer_index"],
    )
    reduction_lengths = _conv_reduction_lengths(manifest)
    for layer, reduction_length in zip(conv_layers, reduction_lengths, strict=True):
        output_channels, output_height, output_width = layer["output_shape_nchw"][1:]
        for _ in range(cases):
            rng.selector(output_channels)
            rng.selector(output_height)
            rng.selector(output_width)
            for _ in range(reduction_length):
                rng.int8()
    state_after_convolution = rng.state

    for case_index in range(plan["shared_primitive_random_cases"]):
        reduction_length = reduction_lengths[case_index % len(reduction_lengths)]
        for _ in range(reduction_length):
            rng.int8()
        for _ in range(reduction_length):
            rng.int8()
        rng.int32()
    state_after_mac = rng.state

    pool_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "maxpool"),
        key=lambda layer: layer["layer_index"],
    )
    if [layer["layer_index"] for layer in pool_layers] != [9, 17, 25]:
        raise ValueError("G0 tiny416 maxpool 层顺序变化")
    for layer in pool_layers:
        channels, output_height, output_width = layer["output_shape_nchw"][1:]
        kernel_height, kernel_width = layer["kernel_hw"]
        for _ in range(cases):
            rng.selector(channels)
            rng.selector(output_height)
            rng.selector(output_width)
            for _ in range(kernel_height * kernel_width):
                rng.int8()
    state_after_maxpool = rng.state

    if (state_after_convolution != 0x2DC4F9F4 or
            state_after_mac != 0x3AFEA916 or
            state_after_maxpool != 0xA9D661B5):
        raise ValueError("G0 共享 PRNG 在 route 前的状态与冻结顺序不符")
    return {
        "state_after_convolution": f"0x{state_after_convolution:08X}",
        "state_after_int8_mac": f"0x{state_after_mac:08X}",
        "state_after_maxpool": f"0x{state_after_maxpool:08X}",
        "convolution_layers": len(conv_layers),
        "int8_mac_random_vectors": plan["shared_primitive_random_cases"],
        "maxpool_layers": len(pool_layers),
    }


def _round_away_from_zero(value: float) -> int:
    """使用 D2 CPU 参考的 half-away-from-zero 舍入。"""
    return math.floor(value + 0.5) if value >= 0.0 else -math.floor(-value + 0.5)


def _requantize_reference(value: int, source_scale: float,
                          target_scale: float) -> int:
    """重现 D2 route_int8 的 float64 缩放、舍入和对称饱和。"""
    scaled = float(value) * source_scale / target_scale
    rounded = _round_away_from_zero(scaled)
    return max(-127, min(127, rounded))


def _multiplier_q31(source_scale: float, target_scale: float) -> int:
    """从冻结 scale 推导无符号 Q31 比例乘数。"""
    ratio = source_scale / target_scale
    multiplier = math.floor(ratio * (1 << 31) + 0.5)
    if not (0 < multiplier <= (1 << 31)):
        raise ValueError("route 来源 scale 推导出的 Q31 乘数超出支持范围")
    return multiplier


def _apply_q31(value: int, multiplier: int) -> int:
    """实现 RTL 的绝对值乘法、Q31 half-away 舍入和对称饱和。"""
    magnitude = (abs(value) * multiplier + (1 << 30)) >> 31
    scaled = -magnitude if value < 0 else magnitude
    return max(-127, min(127, scaled))


def _nchw_offset(channel: int, height: int, width: int,
                 y: int, x: int) -> int:
    """按 G0 NCHW 连续 INT8 byte order 计算来源偏移。"""
    return (channel * height + y) * width + x


def _pack_signed_values(values: list[int], width_bytes: int) -> str:
    """将 INT8 字节低位优先打包成固定宽度十六进制。"""
    if len(values) > width_bytes:
        raise ValueError("route 向量长度超过单来源通道缓冲区")
    packed = 0
    for index, value in enumerate(values):
        if value < -127 or value > 127:
            raise ValueError("route 输入违反对称 INT8 范围 [-127,127]")
        packed |= (value & 0xFF) << (index * 8)
    return f"{packed:0{width_bytes * 2}x}"


def _pack_output_values(values: list[int]) -> str:
    """将输出通道值打包到最多 512 个低字节优先槽。"""
    if len(values) > _MAX_OUTPUT_CHANNELS:
        raise ValueError("route 输出通道超过测试缓冲区上限")
    return _pack_signed_values(values, _MAX_OUTPUT_CHANNELS)


def _resolve_sources(manifest: dict, layer: dict) -> tuple[list[dict], dict]:
    """绑定 route 来源 producer、通道切片、地址、scale 与 Q31 参数。"""
    layer_by_index = {item["layer_index"]: item for item in manifest["layers"]}
    tensor_indices = layer["input_tensor_indices"]
    ranges = layer["route_source_channel_ranges"]
    scales = layer["input_scales"]
    input_shapes = layer["input_shape_nchw"]
    if not (1 <= len(tensor_indices) <= 2 and
            len(tensor_indices) == len(ranges) == len(scales) == len(input_shapes)):
        raise ValueError(f"route layer {layer['layer_index']} 来源描述数量不一致")
    groups = layer["route_groups"]
    group_id = layer["route_group_id"]
    if groups <= 0 or group_id < 0 or group_id >= groups:
        raise ValueError("G0 route groups/group_id 非法")
    if groups > 1 and len(tensor_indices) != 1:
        raise ValueError("G0 groups>1 route 必须只有一个来源")

    target_scale = layer["output_scale"]
    if target_scale != max(scales):
        raise ValueError("G0 route 输出 scale 不是来源最大 scale")
    output_shape = layer["output_shape_nchw"]
    if output_shape[0] != 1:
        raise ValueError("G0 route batch 必须为 1")
    height, width = output_shape[2:]
    output_channels = output_shape[1]
    descriptors: list[dict] = []
    for source_index, (tensor_index, value_range, source_scale, source_shape) in enumerate(
            zip(tensor_indices, ranges, scales, input_shapes, strict=True)):
        producer = layer_by_index[tensor_index]
        start, end = value_range
        if (producer["output_shape_nchw"] != source_shape or
                producer["output_scale"] != source_scale or
                source_shape[0] != 1 or source_shape[2:] != [height, width]):
            raise ValueError("G0 route 来源 shape/scale 未绑定到 producer")
        channels = source_shape[1]
        if groups == 1:
            expected_range = [0, channels]
        else:
            if channels % groups:
                raise ValueError("G0 route 来源通道不能整除 groups")
            group_width = channels // groups
            expected_range = [group_id * group_width, (group_id + 1) * group_width]
        if value_range != expected_range or not (0 <= start < end <= channels):
            raise ValueError("G0 route 来源通道范围与 group 切片规则不一致")
        if end - start > _MAX_SOURCE_CHANNELS:
            raise ValueError("G0 route 来源切片超过实际测试缓冲区支持范围")
        base = producer["tensor_address"]
        length = producer["tensor_length_bytes"]
        if (length != channels * height * width or base + length > 0x1_0000_0000):
            raise ValueError("G0 route producer 字节长度或 uint32 对象边界非法")
        multiplier = _multiplier_q31(source_scale, target_scale)
        mismatches: list[dict] = []
        for value in range(-127, 128):
            reference = _requantize_reference(value, source_scale, target_scale)
            hardware_integer = _apply_q31(value, multiplier)
            if hardware_integer != reference:
                mismatches.append({
                    "input_value": value,
                    "d2_reference": reference,
                    "q31_integer": hardware_integer,
                })
        if mismatches:
            raise ValueError(
                f"route layer {layer['layer_index']} source {source_index} "
                f"Q31 穷举不匹配：{mismatches[:3]}"
            )
        descriptors.append({
            "tensor_index": tensor_index,
            "base_address": base,
            "length_bytes": length,
            "channels": channels,
            "height": height,
            "width": width,
            "channel_start": start,
            "channel_end": end,
            "input_scale": source_scale,
            "multiplier_q31": multiplier,
            "multiplier_hex": f"0x{multiplier:08X}",
            "exhaustive_values": 255,
            "mismatch_count": 0,
        })
    if sum(item["channel_end"] - item["channel_start"] for item in descriptors) != output_channels:
        raise ValueError("G0 route 输出通道数与来源切片拼接长度不符")
    return descriptors, {
        "layer_index": layer["layer_index"],
        "groups": groups,
        "group_id": group_id,
        "output_channels": output_channels,
        "height": height,
        "width": width,
        "target_scale": target_scale,
    }


def _write_record(vector_stream, expected_stream, vector_digest,
                  golden_digest, vector_class: int, layer_index: int,
                  case_index: int, y: int, x: int, route: dict,
                  sources: list[dict], source_values: list[list[int]],
                  expected_values: list[int]) -> None:
    """写一组共享空间点的来源通道刺激和所有输出通道黄金。"""
    output_channels = route["output_channels"]
    if len(expected_values) != output_channels:
        raise ValueError("route 期望输出通道数量不匹配")
    if len(source_values) != len(sources):
        raise ValueError("route 输入值来源数量不匹配")
    fields = [
        vector_class, layer_index, case_index, y, x, len(sources),
        route["groups"], route["group_id"], output_channels,
        route["height"], route["width"],
    ]
    for source_index in range(2):
        if source_index < len(sources):
            source = sources[source_index]
            fields.extend([
                source["base_address"], source["length_bytes"], source["channels"],
                source["channel_start"], source["channel_end"],
                f"{source['multiplier_q31']:08x}",
            ])
        else:
            fields.extend([0, 0, 0, 0, 0, "00000000"])
    input_hexes = [
        _pack_signed_values(values, _MAX_SOURCE_CHANNELS)
        for values in source_values
    ]
    while len(input_hexes) < 2:
        input_hexes.append("0" * (_MAX_SOURCE_CHANNELS * 2))
    vector_line = " ".join(str(value) for value in fields + input_hexes) + "\n"
    vector_bytes = vector_line.encode("ascii")
    vector_stream.write(vector_line)
    vector_digest.update(vector_bytes)
    expected_line = _pack_output_values(expected_values) + "\n"
    expected_stream.write(expected_line)

    golden_digest.update(struct.pack("<BiiII", vector_class, layer_index, case_index, y, x))
    source0_count = sources[0]["channel_end"] - sources[0]["channel_start"]
    for output_channel, expected_value in enumerate(expected_values):
        source_index = 0 if len(sources) == 1 or output_channel < source0_count else 1
        source = sources[source_index]
        local_channel = output_channel if source_index == 0 else output_channel - source0_count
        source_channel = source["channel_start"] + local_channel
        offset = _nchw_offset(source_channel, route["height"], route["width"], y, x)
        address = source["base_address"] + offset
        if offset >= source["length_bytes"] or address > 0xFFFFFFFF:
            raise ValueError("黄金 route 地址超出 producer 对象范围")
        golden_digest.update(struct.pack(
            "<BIIIIb", source_index, source_channel, offset, address,
            output_channel, expected_value,
        ))


def _materialize_vectors(manifest: dict, vectors_path: Path,
                         expected_path: Path) -> dict:
    """生成 11 个 route 层的共享 PRNG 随机、冻结 directed 和 fixture 用例。"""
    plan = manifest["operator_test_plan"]
    rng = XorShift32(_RANDOM_SEED)
    prng_before_route = _advance_to_route_start(manifest, rng)
    route_layers = sorted(
        (layer for layer in manifest["layers"] if layer["op"] == "route"),
        key=lambda layer: layer["layer_index"],
    )
    if [item["layer_index"] for item in route_layers] != [3, 6, 8, 11, 14, 16, 19, 22, 24, 31, 34]:
        raise ValueError("G0 tiny416 route 层序变化")
    random_cases = plan["random_cases_per_model_layer"]
    directed_cases_per_layer = plan["directed_cases_per_model_layer"]
    if random_cases != 1000 or directed_cases_per_layer != 16:
        raise ValueError("G0 route 随机或定向样本数变化")
    directed_plan = plan["directed_case_vectors"]["route"]

    vector_digest = hashlib.sha256()
    golden_digest = hashlib.sha256()
    counts = {
        "model_random_spatial_cases": 0,
        "model_random_output_queries": 0,
        "model_directed_cases": 0,
        "model_directed_output_queries": 0,
        "route_half_away_fixture_values": 0,
    }
    per_layer: list[dict] = []
    source_manifest: list[dict] = []
    route_prng_states: list[dict] = []
    with vectors_path.open("w", encoding="ascii", newline="\n") as vector_stream, \
            expected_path.open("w", encoding="ascii", newline="\n") as expected_stream:
        for layer in route_layers:
            sources, route = _resolve_sources(manifest, layer)
            layer_index = layer["layer_index"]
            if str(layer_index) not in directed_plan or len(directed_plan[str(layer_index)]) != 16:
                raise ValueError(f"G0 route {layer_index} directed case 数量变化")
            state_before = rng.state
            random_query_count = 0
            for case_index in range(random_cases):
                y = rng.selector(route["height"])
                x = rng.selector(route["width"])
                source_values = [
                    [rng.int8() for _ in range(source["channel_end"] - source["channel_start"])]
                    for source in sources
                ]
                expected_values: list[int] = []
                for source, values in zip(sources, source_values, strict=True):
                    expected_values.extend(
                        _requantize_reference(value, source["input_scale"], route["target_scale"])
                        for value in values
                    )
                _write_record(
                    vector_stream, expected_stream, vector_digest, golden_digest,
                    0, layer_index, case_index, y, x, route, sources,
                    source_values, expected_values,
                )
                counts["model_random_spatial_cases"] += 1
                random_query_count += route["output_channels"]
                counts["model_random_output_queries"] += route["output_channels"]
            state_after = rng.state
            route_prng_states.append({
                "layer_index": layer_index,
                "state_before_random": f"0x{state_before:08X}",
                "state_after_random": f"0x{state_after:08X}",
                "selected_source_channels_per_case": [
                    source["channel_end"] - source["channel_start"] for source in sources
                ],
            })

            directed_vectors = directed_plan[str(layer_index)]
            directed_query_count = 0
            for expected_case_index, directed in enumerate(directed_vectors):
                if directed["case_index"] != expected_case_index:
                    raise ValueError("G0 route directed case_index 必须为 0..15")
                y, x = directed["target_spatial_yx"]
                if not (0 <= y < route["height"] and 0 <= x < route["width"]):
                    raise ValueError("G0 directed route 坐标超出冻结输出 shape")
                raw_values: list[list[int]] = []
                source_expected: list[list[int]] = []
                frozen_sources = directed["source_tensors"]
                if len(frozen_sources) != len(sources):
                    raise ValueError("G0 directed source tensor 数量变化")
                for source, frozen in zip(sources, frozen_sources, strict=True):
                    selected_channels = list(range(source["channel_start"], source["channel_end"]))
                    if (frozen["tensor_index"] != source["tensor_index"] or
                            frozen["input_shape_nchw"] != [
                                1, source["channels"], route["height"], route["width"]
                            ] or frozen["input_scale"] != source["input_scale"] or
                            frozen["selected_source_channel_range"] != [
                                source["channel_start"], source["channel_end"]
                            ] or frozen["selected_source_channels"] != selected_channels):
                        raise ValueError("G0 directed route 来源与冻结 manifest 不一致")
                    values = frozen["source_values_int8"]
                    requantized = frozen["requantized_values_int8"]
                    if len(values) != len(selected_channels) or len(requantized) != len(values):
                        raise ValueError("G0 directed route 来源值长度错误")
                    reference_values = [
                        _requantize_reference(value, source["input_scale"], route["target_scale"])
                        for value in values
                    ]
                    if reference_values != requantized:
                        raise ValueError("G0 directed route requantized_values 与 D2 参考不符")
                    raw_values.append(values)
                    source_expected.append(requantized)
                frozen_output = directed["output_channel_values_int8"]
                if frozen_output != [value for source_values_i in source_expected for value in source_values_i]:
                    raise ValueError("G0 directed route 输出通道值与来源顺序/期望不符")
                _write_record(
                    vector_stream, expected_stream, vector_digest, golden_digest,
                    1, layer_index, expected_case_index, y, x, route, sources,
                    raw_values, frozen_output,
                )
                counts["model_directed_cases"] += 1
                directed_query_count += route["output_channels"]
                counts["model_directed_output_queries"] += route["output_channels"]
            per_layer.append({
                "layer_index": layer_index,
                "source_tensor_indices": [source["tensor_index"] for source in sources],
                "source_base_addresses": [source["base_address"] for source in sources],
                "source_length_bytes": [source["length_bytes"] for source in sources],
                "source_channel_ranges": [
                    [source["channel_start"], source["channel_end"]] for source in sources
                ],
                "source_scales": [source["input_scale"] for source in sources],
                "target_scale": route["target_scale"],
                "groups": route["groups"],
                "group_id": route["group_id"],
                "output_shape_nchw": [1, route["output_channels"], route["height"], route["width"]],
                "random_spatial_cases": random_cases,
                "random_output_queries": random_query_count,
                "directed_cases": directed_cases_per_layer,
                "directed_output_queries": directed_query_count,
            })
            source_manifest.append({
                "layer_index": layer_index,
                "sources": [
                    {key: source[key] for key in (
                        "tensor_index", "base_address", "length_bytes", "channels",
                        "channel_start", "channel_end", "input_scale", "multiplier_hex",
                        "exhaustive_values", "mismatch_count",
                    )}
                    for source in sources
                ],
            })

        fixture = plan["separate_unit_fixtures"]["route_half_away"]
        if (fixture["concat_order"] != "source0 then source1" or
                fixture["source_scales"] != [0.25, 0.5] or fixture["target_scale"] != 0.5):
            raise ValueError("G0 route half-away fixture 规格变化")
        fixture_values = [fixture["source0_values"], fixture["source1_values"]]
        fixture_expected = [fixture["source0_expected"], fixture["source1_expected"]]
        if any(len(values) != 6 for values in fixture_values + fixture_expected):
            raise ValueError("G0 route half-away fixture 必须为两来源各 6 值")
        fixture_sources = [
            {
                "tensor_index": -1,
                "base_address": 0,
                "length_bytes": 6,
                "channels": 6,
                "height": 1,
                "width": 1,
                "channel_start": 0,
                "channel_end": 6,
                "input_scale": fixture["source_scales"][index],
                "multiplier_q31": _multiplier_q31(
                    fixture["source_scales"][index], fixture["target_scale"]
                ),
            }
            for index in range(2)
        ]
        for source, values, expected in zip(
                fixture_sources, fixture_values, fixture_expected, strict=True):
            actual = [
                _requantize_reference(value, source["input_scale"], fixture["target_scale"])
                for value in values
            ]
            q31 = [_apply_q31(value, source["multiplier_q31"]) for value in values]
            if actual != expected or q31 != expected:
                raise ValueError("G0 route half-away fixture 浮点/Q31 结果不匹配")
        fixture_route = {
            "groups": 1,
            "group_id": 0,
            "output_channels": 12,
            "height": 1,
            "width": 1,
            "target_scale": fixture["target_scale"],
        }
        fixture_outputs = fixture_expected[0] + fixture_expected[1]
        _write_record(
            vector_stream, expected_stream, vector_digest, golden_digest,
            2, -1, 0, 0, 0, fixture_route, fixture_sources,
            fixture_values, fixture_outputs,
        )
        counts["route_half_away_fixture_values"] = len(fixture_outputs)

    if rng.state != _EXPECTED_ROUTE_FINAL_STATE:
        raise ValueError(
            f"G0 route PRNG 终态错误：0x{rng.state:08X} != "
            f"0x{_EXPECTED_ROUTE_FINAL_STATE:08X}"
        )
    if not route_prng_states:
        raise ValueError("G0 route PRNG 层状态为空")
    state_before_route = route_prng_states[0]["state_before_random"]
    if (state_before_route != prng_before_route["state_after_maxpool"] or
            state_before_route != "0xA9D661B5"):
        raise ValueError("route 起始 PRNG 状态必须等于 maxpool 终态 0xA9D661B5")
    if counts["model_random_spatial_cases"] != 11000 or counts["model_directed_cases"] != 176:
        raise ValueError(f"G0 route 样本数量变化：{counts}")
    expected_query_total = sum(item["output_channels"] for item in [
        _resolve_sources(manifest, layer)[1] for layer in route_layers
    ])
    if counts["model_random_output_queries"] != expected_query_total * 1000:
        raise ValueError("G0 route 随机逐输出通道查询数不匹配")
    if counts["model_directed_output_queries"] != expected_query_total * 16:
        raise ValueError("G0 route directed 逐输出通道查询数不匹配")
    return {
        "vector_sha256": _sha256_file(vectors_path),
        "expected_stream_sha256": _sha256_file(expected_path),
        "golden_output_sha256": golden_digest.hexdigest(),
        "vector_file_bytes": vectors_path.stat().st_size,
        "expected_file_bytes": expected_path.stat().st_size,
        "record_count": counts["model_random_spatial_cases"] + counts["model_directed_cases"] + 1,
        "counts": counts,
        "per_layer": per_layer,
        "route_source_parameters_and_exhaustive_q31": source_manifest,
        "randomness": {
            "seed": _RANDOM_SEED,
            "state_after_convolution": prng_before_route["state_after_convolution"],
            "state_after_int8_mac": prng_before_route["state_after_int8_mac"],
            "state_after_maxpool": prng_before_route["state_after_maxpool"],
            "state_before_route": state_before_route,
            "state_after_route": f"0x{rng.state:08X}",
            "stage_counts": {
                "convolution_layers": prng_before_route["convolution_layers"],
                "int8_mac_random_vectors": prng_before_route["int8_mac_random_vectors"],
                "maxpool_layers": prng_before_route["maxpool_layers"],
                "route_layers": len(route_layers),
                "route_random_spatial_cases_per_layer": random_cases,
            },
            "route_layer_states": route_prng_states,
            "draw_order": "卷积层按 layer_index：channel/y/x selector 后 K 个 INT8；共享 MAC：按卷积 K 循环，K 个 activation、K 个 weight、一个 INT32 bias；maxpool 层按 layer_index：channel/y/x selector 后 kernel_y/kernel_x 候选；route 层按 layer_index：y/x selector 后，cfg 来源顺序、所选通道顺序各一个 INT8；directed 不消耗 PRNG。",
        },
        "fixture_address_semantics": "route_half_away 使用 source0/source1 base address=0 的独立局部夹具，不表示模型或硬件映射地址。",
    }


def _run_tool(tool: Path, arguments: list[str], cwd: Path,
              log_path: Path, deadline: float) -> tuple[int, str]:
    """在共享 600 秒截止时间内运行一个 Vivado 批处理阶段。"""
    if not tool.is_file():
        raise FileNotFoundError(f"未找到 Vivado 工具：{tool}")
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise TimeoutError("Vivado 仿真总耗时达到 600 秒停止条件")
    command = " ".join(
        f'"{argument}"' if " " in argument else argument
        for argument in [str(tool), *arguments]
    )
    process = subprocess.run(
        f'cmd.exe /d /s /c "{command}"',
        cwd=cwd,
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=remaining,
    )
    output = process.stdout + process.stderr
    log_path.write_text(output, encoding="utf-8", newline="\n")
    return process.returncode, output


class TestS2ARouteQueryRtl(unittest.TestCase):
    """验证 tiny416 route 单输出来源映射、地址和重定标。"""

    def test_vivado_route_queries_against_g0_manifest(self) -> None:
        repository = Path(__file__).resolve().parents[1]
        manifest_path = repository / "report/evidence/S2A-T01/tiny416_model_manifest.json"
        manifest_bytes = manifest_path.read_bytes()
        manifest_sha = _sha256_bytes(manifest_bytes)
        self.assertEqual(
            manifest_sha, _MANIFEST_SHA256,
            "G0 manifest 原始字节 SHA 变化，按停止条件中止",
        )
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        evidence_path = repository / "report/evidence/S2A-T06/route_query_simulation.json"
        rtl_path = repository / "src/int8_route_query.sv"
        bench_path = repository / "sim/tb_s2a_route_query.sv"
        script_path = Path(__file__).resolve()
        for source in (rtl_path, bench_path, script_path):
            self.assertTrue(source.is_file(), f"缺少验证源文件：{source}")
        tools = {name: _XILINX_BIN / f"{name}.bat" for name in ("xvlog", "xelab", "xsim")}
        for tool in tools.values():
            self.assertTrue(tool.is_file(), f"未找到 Vivado 工具：{tool}")

        source_hashes_before = {
            "rtl_sha256": _sha256_file(rtl_path),
            "testbench_sha256": _sha256_file(bench_path),
            "runner_sha256": _sha256_file(script_path),
        }
        with tempfile.TemporaryDirectory(prefix="s2a_t06_route_query_") as temporary:
            work = Path(temporary)
            vectors_path = work / "vectors.dat"
            expected_path = work / "expected.dat"
            vector_result = _materialize_vectors(manifest, vectors_path, expected_path)
            self.assertGreater(vector_result["vector_file_bytes"], 0)
            self.assertGreater(vector_result["expected_file_bytes"], 0)

            phases = [
                ("xvlog", ["-sv", str(rtl_path), str(bench_path)]),
                ("xelab", ["-top", "tb_s2a_route_query",
                           "-snapshot", "s2a_route_query_snapshot"]),
                ("xsim", ["-R", "s2a_route_query_snapshot"]),
            ]
            phase_codes: list[dict] = []
            deadline = time.monotonic() + 600.0
            for name, arguments in phases:
                code, output = _run_tool(
                    tools[name], arguments, work, work / f"{name}.log", deadline
                )
                phase_codes.append({"phase": name, "exit_code": code})
                self.assertEqual(
                    code, 0,
                    f"{name} 退出码 {code}；临时日志尾部：\n{output[-5000:]}",
                )
                if name == "xsim":
                    expected_pass = (
                        "PASS: route_queries="
                        f"{vector_result['counts']['model_random_output_queries'] + vector_result['counts']['model_directed_output_queries'] + vector_result['counts']['route_half_away_fixture_values']} "
                        "random_cases=11000 directed_cases=176 fixture_values=12 "
                        "bad_argument=23 bad_range=4 boundary=1"
                    )
                    self.assertIn(expected_pass, output)

        self.assertEqual([item["exit_code"] for item in phase_codes], [0, 0, 0])
        source_hashes_after = {
            "rtl_sha256": _sha256_file(rtl_path),
            "testbench_sha256": _sha256_file(bench_path),
            "runner_sha256": _sha256_file(script_path),
        }
        self.assertEqual(source_hashes_before, source_hashes_after,
                         "仿真过程中源文件发生变化")
        self.assertEqual(_sha256_file(manifest_path), _MANIFEST_SHA256,
                         "仿真过程中 G0 manifest 原始字节发生变化")

        evidence = {
            "schema_version": "gestureforge_s2a_t06_route_query_simulation_v1",
            "result": "PASS",
            "scope": "tiny416 route 单输出元素的 cfg 来源映射、groups 切片、NCHW INT8 byte address 与 Q31/half-away 重标定",
            "bindings": {
                "manifest_path": "report/evidence/S2A-T01/tiny416_model_manifest.json",
                "manifest_sha256": manifest_sha,
                **source_hashes_after,
                "vector_sha256": vector_result["vector_sha256"],
                "expected_stream_sha256": vector_result["expected_stream_sha256"],
                "golden_output_sha256": vector_result["golden_output_sha256"],
            },
            "randomness": vector_result["randomness"],
            "counts": vector_result["counts"],
            "record_count": vector_result["record_count"],
            "vector_file_bytes": vector_result["vector_file_bytes"],
            "expected_file_bytes": vector_result["expected_file_bytes"],
            "route_layers": vector_result["per_layer"],
            "route_source_parameters_and_exhaustive_q31": vector_result[
                "route_source_parameters_and_exhaustive_q31"
            ],
            "invalid_assertions": {
                "BAD_ARGUMENT_code_1": 23,
                "BAD_RANGE_code_2": 4,
                "maximum_uint32_address_success": 1,
            },
            "vivado": {
                "tool_directory": str(_XILINX_BIN),
                "phase_exit_codes": phase_codes,
                "test_command": "python -B -m unittest verification.test_s2a_route_rtl -v",
            },
            "limitations": [
                "仅实现单输出元素组合查询，不发起访存事务，不是完整 route layer engine。",
                "未验证 tiny416 完整网络、PS/D9 联调、整网逐层黄金、综合资源或时序。",
                "route_half_away 的 base address=0 是独立局部夹具，不表示模型或硬件映射。",
            ],
        }
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_bytes = (json.dumps(evidence, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        evidence_path.write_bytes(evidence_bytes)
        self.assertEqual(evidence_path.read_bytes(), evidence_bytes,
                         "仿真证据必须按 UTF-8/LF 原始字节写入")
        self.assertFalse(evidence_bytes.startswith(b"\xef\xbb\xbf"),
                         "仿真证据不得包含 UTF-8 BOM")


if __name__ == "__main__":
    unittest.main()
