"""按冻结 tiny416 descriptor 逐层复算 S2B 单字节 HP0 请求量。"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_CEILING
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

try:
    from .test_s2a_conv_tile_cycle_budget import maxpool_read_bytes
except ImportError:
    from test_s2a_conv_tile_cycle_budget import maxpool_read_bytes


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_RELATIVE = "report/evidence/S2A-T01/tiny416_model_manifest.json"
MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
LEGACY_ESTIMATOR_RELATIVE = "verification/test_s2a_conv_tile_cycle_budget.py"
T66_ACCEPTANCE_RELATIVE = "report/evidence/S2A-T68/stage2a_g4_g5_acceptance_20261005.md"
T66_ACCEPTANCE_SHA256 = "7c6e8db6eabbeee56c9791398c0d40c56435654e158cc597119e6949b989eb9c"
T66_RECORD_RELATIVE = (
    "report/evidence/S2A-T66/candidate999_t66_postfix_retry_20261008/"
    "simulation/simulation_execution_record.json"
)
T66_RECORD_SHA256 = "1b7bb9efcf4dc1f5ef0e920a28e5549888005cc2986e42158fc4adfca8e848b3"
T66_LAYER0_REQUESTS = 2_551_955
T66_LAYER0_WRITES = 1_384_448
LANES = 8
TILE_EDGE = 8
TIMEOUT_MAX = (1 << 32) - 1
CLOCK_HZ = 50_000_000
EXPECTED_STALL_PATTERN = (0, 1, 2, 7, 3)
EXPECTED_OP_COUNTS = {
    "convolutional": 21,
    "route": 11,
    "maxpool": 3,
    "upsample": 1,
    "yolo": 2,
}

ROOT_FIELDS = {
    "schema_version",
    "created_utc8",
    "status",
    "scope",
    "model",
    "bindings",
    "address_map",
    "control_protocol",
    "memory_protocol",
    "layers",
    "operators",
    "detection_postprocess",
    "operator_test_plan",
    "fixed_test_samples_path",
}
COMMON_LAYER_FIELDS = {
    "layer_index",
    "cfg_section",
    "op",
    "input_tensor_indices",
    "input_shape_nchw",
    "input_scale",
    "layout",
    "element_type",
    "output_scale",
    "output_shape_nchw",
    "tensor_address",
    "tensor_length_bytes",
    "tensor_address_space",
}
LAYER_FIELDS = {
    "convolutional": COMMON_LAYER_FIELDS
    | {
        "kernel_hw",
        "stride_hw",
        "padding_lrtb",
        "groups",
        "padding_value_int8",
        "activation",
        "accumulator_bits",
        "weight_layer_index",
        "gf8_parameter_offsets",
        "weight_scale_per_output_channel",
        "fused_bias_float32_per_output_channel",
        "bias_accumulator_int32_per_output_channel",
    },
    "route": COMMON_LAYER_FIELDS
    | {
        "input_scales",
        "route_groups",
        "route_group_id",
        "route_source_channel_ranges",
        "route_group_slice_order",
        "requantization",
    },
    "maxpool": COMMON_LAYER_FIELDS
    | {
        "kernel_hw",
        "stride_hw",
        "darknet_padding_parameter",
        "output_hw_formula",
        "window_origin_yx_at_output_0",
        "padding_lrtb_actual",
        "pad_value_int8",
    },
    "upsample": COMMON_LAYER_FIELDS | {"scale", "stride", "method"},
    "yolo": COMMON_LAYER_FIELDS
    | {
        "output_tensor_index",
        "anchors_wh",
        "mask",
        "classes",
        "scale_x_y",
        "new_coords",
        "head_logit_scale",
    },
}

SOURCE_PATHS = (
    "src/s2a_conv_tile_engine.sv",
    "src/s2a_maxpool_engine.sv",
    "src/s2a_route_engine.sv",
    "src/s2a_upsample_engine.sv",
    "src/s2a_network_backend.sv",
    "src/s2a_network_descriptor_pkg.sv",
    "src/s2b_conv_tile_engine.sv",
    "src/s2b_maxpool_engine.sv",
    "src/s2b_maxpool_geometry.sv",
    "src/s2b_route_engine.sv",
    "src/s2b_route_query.sv",
    "src/s2b_upsample_engine.sv",
    "src/s2b_network_backend.sv",
    "src/s2b_hp0_word_adapter.sv",
    "src/s2b_request_guard.sv",
)


@dataclass(frozen=True)
class ConvTileMetrics:
    """保存卷积层按 8×8 输出 tile 扫描后的静态计数。"""

    tile_rows: int
    tile_columns: int
    spatial_tiles: int
    patch_scan_slots: int
    padding_scan_slots: int
    feature_read_requests: int
    weight_read_requests: int
    mac_group_taps: int


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _integer(value: Any, context: str, minimum: int = 0) -> int:
    _require(type(value) is int and value >= minimum, f"{context} must be an integer >= {minimum}")
    return value


def _positive_shape(shape: Any, context: str) -> tuple[int, ...]:
    _require(type(shape) is list and len(shape) == 4, f"{context} must be an NCHW list")
    values = tuple(_integer(value, context, 1) for value in shape)
    _require(values[0] == 1, f"{context} only supports batch size one")
    return values


def _elements(shape: tuple[int, ...]) -> int:
    result = 1
    for value in shape:
        result *= value
    return result


def _pair(value: Any, context: str) -> tuple[int, int]:
    _require(type(value) is list and len(value) == 2, f"{context} must contain two integers")
    return (_integer(value[0], context, 1), _integer(value[1], context, 1))


def conv_tile_metrics(
    input_shape: Any,
    output_shape: Any,
    kernel_hw: Any,
    stride_hw: Any,
    padding_lrtb: Any,
    groups: int = 1,
    lanes: int = LANES,
    tile_edge: int = TILE_EDGE,
) -> ConvTileMetrics:
    """逐 tile 计算有效 feature、重复权重、padding 扫描和 MAC-group taps。"""
    batch, input_channels, input_height, input_width = _positive_shape(input_shape, "conv input")
    output_batch, output_channels, output_height, output_width = _positive_shape(output_shape, "conv output")
    _require(batch == output_batch, "conv batch dimensions must match")
    kernel_height, kernel_width = _pair(kernel_hw, "conv kernel_hw")
    stride_y, stride_x = _pair(stride_hw, "conv stride_hw")
    _require(type(padding_lrtb) is list and len(padding_lrtb) == 4, "padding_lrtb must contain L,R,T,B")
    pad_left, pad_right, pad_top, pad_bottom = (
        _integer(value, "conv padding_lrtb") for value in padding_lrtb
    )
    _require(type(groups) is int and groups == 1, "当前 S2B 卷积只支持 groups=1")
    _integer(lanes, "lanes", 1)
    _integer(tile_edge, "tile_edge", 1)
    expected_height = (input_height + pad_top + pad_bottom - kernel_height) // stride_y + 1
    expected_width = (input_width + pad_left + pad_right - kernel_width) // stride_x + 1
    _require((output_height, output_width) == (expected_height, expected_width), "不支持的卷积输出几何")

    tile_rows = (output_height + tile_edge - 1) // tile_edge
    tile_columns = (output_width + tile_edge - 1) // tile_edge
    patch_scan_slots = 0
    feature_reads = 0
    for tile_y in range(0, output_height, tile_edge):
        current_height = min(tile_edge, output_height - tile_y)
        patch_height = (current_height - 1) * stride_y + kernel_height
        input_origin_y = tile_y * stride_y - pad_top
        valid_height = max(0, min(input_height, input_origin_y + patch_height) - max(0, input_origin_y))
        for tile_x in range(0, output_width, tile_edge):
            current_width = min(tile_edge, output_width - tile_x)
            patch_width = (current_width - 1) * stride_x + kernel_width
            input_origin_x = tile_x * stride_x - pad_left
            valid_width = max(0, min(input_width, input_origin_x + patch_width) - max(0, input_origin_x))
            patch_scan_slots += input_channels * patch_height * patch_width
            feature_reads += input_channels * valid_height * valid_width

    spatial_tiles = tile_rows * tile_columns
    weight_reads = spatial_tiles * output_channels * input_channels * kernel_height * kernel_width
    mac_group_taps = (
        ((output_channels + lanes - 1) // lanes)
        * output_height
        * output_width
        * input_channels
        * kernel_height
        * kernel_width
    )
    return ConvTileMetrics(
        tile_rows=tile_rows,
        tile_columns=tile_columns,
        spatial_tiles=spatial_tiles,
        patch_scan_slots=patch_scan_slots,
        padding_scan_slots=patch_scan_slots - feature_reads,
        feature_read_requests=feature_reads,
        weight_read_requests=weight_reads,
        mac_group_taps=mac_group_taps,
    )


def upsample_read_requests(input_shape: Any, output_shape: Any, stride: int, method: str, scale: float) -> int:
    """计算当前 nearest-repeat 引擎逐输出坐标发起的源读请求数。"""
    input_nchw = _positive_shape(input_shape, "upsample input")
    output_nchw = _positive_shape(output_shape, "upsample output")
    _require(type(stride) is int and stride == 2 and method == "nearest_repeat" and scale == 1.0,
             "只支持冻结的 2× nearest_repeat upsample")
    _require(output_nchw == (input_nchw[0], input_nchw[1], input_nchw[2] * 2, input_nchw[3] * 2),
             "upsample output shape is unsupported")
    return _elements(output_nchw)


def _expected_input_shape(layer: dict[str, Any], previous_shapes: dict[int, list[int]]) -> list[list[int]]:
    refs = layer["input_tensor_indices"]
    expected: list[list[int]] = []
    for ref in refs:
        if ref == "network_input":
            expected.append([1, 3, 416, 416])
        else:
            expected.append(previous_shapes[ref])
    return expected


def validate_manifest(manifest: Any) -> list[dict[str, Any]]:
    """校验冻结 descriptor 的完整字段、支持的几何和层间引用。"""
    _require(type(manifest) is dict and set(manifest) == ROOT_FIELDS, "manifest 含未知或缺失的根字段")
    _require(manifest["schema_version"] == "gestureforge_s2a_model_manifest_v1", "不支持的 manifest schema")
    model = manifest["model"]
    _require(type(model) is dict and set(model) == {"model_id", "architecture", "input_wh", "classes"},
             "不支持的 model 字段")
    _require(
        model == {"model_id": "tiny416", "architecture": "YOLOv4-tiny", "input_wh": [416, 416], "classes": 5},
        "只支持冻结 tiny416 模型",
    )
    layers = manifest["layers"]
    _require(type(layers) is list and len(layers) == 38, "只支持冻结的 38 层 descriptor")
    counts = {name: 0 for name in EXPECTED_OP_COUNTS}
    previous_shapes: dict[int, list[int]] = {}
    output_rows: list[dict[str, Any]] = []

    for expected_index, layer in enumerate(layers):
        _require(type(layer) is dict, f"layer {expected_index} must be an object")
        op = layer.get("op")
        _require(op in LAYER_FIELDS, f"layer {expected_index} has unsupported operation {op!r}")
        _require(set(layer) == LAYER_FIELDS[op], f"layer {expected_index} has unknown or missing fields")
        counts[op] += 1
        _require(layer["layer_index"] == expected_index, "layer indices must be contiguous and ordered")
        _require(layer["layout"] == "NCHW" and layer["element_type"] == "int8_twos_complement",
                 f"layer {expected_index} has unsupported tensor layout or element type")
        refs = layer["input_tensor_indices"]
        _require(type(refs) is list and bool(refs), f"layer {expected_index} needs input tensor references")
        for ref in refs:
            if ref == "network_input":
                _require(expected_index == 0 and len(refs) == 1, "network_input is supported only by layer 0")
            else:
                _require(type(ref) is int and 0 <= ref < expected_index, f"layer {expected_index} has unsupported input reference")
        expected_inputs = _expected_input_shape(layer, previous_shapes)
        if op == "route":
            _require(layer["input_shape_nchw"] == expected_inputs, f"route {expected_index} input shapes disagree with references")
            input_shapes = expected_inputs
        else:
            _require(len(expected_inputs) == 1 and layer["input_shape_nchw"] == expected_inputs[0],
                     f"layer {expected_index} input shape disagrees with its reference")
            input_shapes = [expected_inputs[0]]
        output_shape = _positive_shape(layer["output_shape_nchw"], f"layer {expected_index} output")
        _integer(layer["tensor_address"], f"layer {expected_index} tensor_address")
        output_length = _integer(layer["tensor_length_bytes"], f"layer {expected_index} tensor_length_bytes", 1)
        _require(output_length == _elements(output_shape), f"layer {expected_index} tensor length disagrees with shape")

        if op == "convolutional":
            metrics = conv_tile_metrics(
                input_shapes[0],
                list(output_shape),
                layer["kernel_hw"],
                layer["stride_hw"],
                layer["padding_lrtb"],
                groups=layer["groups"],
            )
            _require(type(layer["weight_layer_index"]) is int and layer["weight_layer_index"] >= 0,
                     f"conv {expected_index} has invalid weight layer index")
            reads = metrics.feature_read_requests + metrics.weight_read_requests
            read_breakdown = {
                "feature": metrics.feature_read_requests,
                "weight": metrics.weight_read_requests,
                "maxpool": 0,
                "route": 0,
                "upsample": 0,
            }
            detail = asdict(metrics)
            mac_taps = metrics.mac_group_taps
        elif op == "maxpool":
            input_shape = input_shapes[0]
            _pair(layer["kernel_hw"], "maxpool kernel_hw")
            stride_y, stride_x = _pair(layer["stride_hw"], "maxpool stride_hw")
            padding = layer["padding_lrtb_actual"]
            _require(type(padding) is list and len(padding) == 4 and all(type(x) is int and x == 0 for x in padding),
                     "当前统计只支持无实际 padding 的 maxpool")
            _require(layer["output_hw_formula"] == "(input_hw + padding - kernel_hw) // stride_hw + 1",
                     "不支持的 maxpool 输出公式")
            pool_padding = _integer(layer["darknet_padding_parameter"], "darknet_padding_parameter")
            expected_height = (input_shape[2] + pool_padding - layer["kernel_hw"][0]) // stride_y + 1
            expected_width = (input_shape[3] + pool_padding - layer["kernel_hw"][1]) // stride_x + 1
            _require(output_shape == (input_shape[0], input_shape[1], expected_height, expected_width),
                     f"maxpool {expected_index} output shape is unsupported")
            reads = maxpool_read_bytes(layer)
            read_breakdown = {"feature": 0, "weight": 0, "maxpool": reads, "route": 0, "upsample": 0}
            detail = {
                "valid_window_read_requests": reads,
                "padding_scan_slots": 0,
                "mac_group_taps": 0,
            }
            mac_taps = 0
        elif op == "route":
            ranges = layer["route_source_channel_ranges"]
            groups = _integer(layer["route_groups"], "route_groups", 1)
            group_id = _integer(layer["route_group_id"], "route_group_id")
            _require(group_id < groups and type(ranges) is list and len(ranges) == len(input_shapes),
                     f"route {expected_index} has unsupported source ranges")
            selected_channels = 0
            for source_shape, source_range in zip(input_shapes, ranges):
                _require(type(source_range) is list and len(source_range) == 2, "route range must be [start,stop]")
                start, stop = (_integer(value, "route channel range") for value in source_range)
                _require(source_shape[1] % groups == 0, "route groups must divide source channels")
                expected_start = group_id * (source_shape[1] // groups)
                expected_stop = expected_start + source_shape[1] // groups
                _require((start, stop) == (expected_start, expected_stop), "route range does not match group selection")
                _require(source_shape[0] == output_shape[0] and tuple(source_shape[2:]) == output_shape[2:],
                         f"route {expected_index} source {source_shape} disagrees with output {output_shape}")
                selected_channels += stop - start
            _require(output_shape[1] == selected_channels, f"route {expected_index} channel count disagrees with ranges")
            reads = output_length
            read_breakdown = {"feature": 0, "weight": 0, "maxpool": 0, "route": reads, "upsample": 0}
            detail = {"source_read_requests": reads, "padding_scan_slots": 0, "mac_group_taps": 0}
            mac_taps = 0
        elif op == "upsample":
            input_shape = input_shapes[0]
            reads = upsample_read_requests(
                input_shape, list(output_shape), layer["stride"], layer["method"], layer["scale"]
            )
            _require(reads == output_length, f"upsample {expected_index} must read once per output element")
            read_breakdown = {"feature": 0, "weight": 0, "maxpool": 0, "route": 0, "upsample": reads}
            detail = {
                "source_read_requests_per_output_element": 1,
                "source_read_requests": reads,
                "padding_scan_slots": 0,
                "mac_group_taps": 0,
            }
            mac_taps = 0
        else:
            _require(len(input_shapes) == 1 and list(output_shape) == input_shapes[0],
                     f"YOLO {expected_index} must be an exact tensor alias")
            _require(layer["output_tensor_index"] == refs[0], f"YOLO {expected_index} alias index disagrees with reference")
            reads = 0
            read_breakdown = {"feature": 0, "weight": 0, "maxpool": 0, "route": 0, "upsample": 0}
            detail = {"alias": True, "padding_scan_slots": 0, "mac_group_taps": 0}
            mac_taps = 0

        writes = 0 if op == "yolo" else output_length
        output_rows.append(
            {
                "layer_index": expected_index,
                "cfg_section": layer["cfg_section"],
                "op": op,
                "input_shape_nchw": layer["input_shape_nchw"],
                "output_shape_nchw": list(output_shape),
                "read_requests": read_breakdown,
                "read_request_total": reads,
                "write_requests": writes,
                "request_total": reads + writes,
                "mac_group_taps": mac_taps,
                "geometry": detail,
            }
        )
        previous_shapes[expected_index] = list(output_shape)

    _require(counts == EXPECTED_OP_COUNTS, f"unsupported tiny416 op counts: {counts}")
    return output_rows


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _bound_file(relative: str, expected_sha256: str | None = None) -> dict[str, str]:
    path = ROOT / relative
    _require(path.is_file(), f"required file is missing or not a regular file: {relative}")
    digest = _sha256(path)
    if expected_sha256 is not None:
        _require(digest == expected_sha256, f"SHA-256 mismatch for {relative}: {digest}")
    return {"path": relative, "sha256": digest}


def cycle_sensitivity(
    requests: int,
    mac_group_taps: int,
    output_bytes: int,
    layer_count: int,
    stall_pattern: tuple[int, ...],
) -> dict[str, Any]:
    """输出 32 位超时的条件性平均请求预算，不代表实测或部署结论。"""
    mac_cycles = mac_group_taps * 2
    control_cycles = output_bytes * 8 + layer_count * 8
    fixed_cycles = mac_cycles + control_cycles
    request_path_budget = TIMEOUT_MAX - fixed_cycles
    average_cost = Decimal(request_path_budget) / Decimal(requests)
    _require(stall_pattern == EXPECTED_STALL_PATTERN, "unexpected frozen testbench stall pattern")
    full_periods, remainder = divmod(requests, len(stall_pattern))
    periodic_stall_cycles = full_periods * sum(stall_pattern) + sum(stall_pattern[:remainder])
    periodic_pattern_cycles = fixed_cycles + requests * 3 + periodic_stall_cycles
    periodic_average_cost = Decimal(requests * 3 + periodic_stall_cycles) / Decimal(requests)
    scenarios = []
    for name, cost_text in (
        ("no_added_wait", "3"),
        ("continuous_average_at_frozen_tb_pattern_mean", "5.6"),
        ("old_max_stall_per_request", "10"),
        ("near_budget_under", "34.89"),
        ("near_budget_over", "34.9"),
        ("integer_cost_over", "35"),
    ):
        cost = Decimal(cost_text)
        cycles = int((Decimal(requests) * cost + Decimal(fixed_cycles)).to_integral_value(rounding=ROUND_CEILING))
        scenarios.append(
            {
                "name": name,
                "assumed_average_total_request_cycles": cost_text,
                "estimated_total_cycles": cycles,
                "estimated_seconds_at_50mhz": format(Decimal(cycles) / Decimal(CLOCK_HZ), ".9f"),
                "exceeds_uint32_timeout_max": cycles > TIMEOUT_MAX,
                "timeout_counter_overflow_count": max(0, cycles - TIMEOUT_MAX),
                "status": "ASSUMED_NOT_MEASURED",
            }
        )
    scenarios.append(
        {
            "name": "frozen_tb_pattern_periodic_sequence",
            "stall_pattern_cycles": list(stall_pattern),
            "assumed_average_total_request_cycles": format(periodic_average_cost, ".12f"),
            "estimated_total_cycles": periodic_pattern_cycles,
            "estimated_seconds_at_50mhz": format(Decimal(periodic_pattern_cycles) / Decimal(CLOCK_HZ), ".9f"),
            "exceeds_uint32_timeout_max": periodic_pattern_cycles > TIMEOUT_MAX,
            "timeout_counter_overflow_count": max(0, periodic_pattern_cycles - TIMEOUT_MAX),
            "status": "ASSUMED_NOT_MEASURED",
            "interpretation": "仅按冻结 TB 向量从请求 0 周期重复，不是板卡 HP latency 记录。",
        }
    )
    return {
        "status": "ASSUMED_NOT_MEASURED",
        "timeout_counter_max_cycles": TIMEOUT_MAX,
        "clock_hz": CLOCK_HZ,
        "timeout_max_seconds_at_50mhz": format(Decimal(TIMEOUT_MAX) / Decimal(CLOCK_HZ), ".9f"),
        "static_mac_assumption": {"formula": "MAC_group_taps * 2", "cycles": mac_cycles, "status": "ASSUMED_NOT_MEASURED"},
        "static_control_assumption": {
            "formula": "non_yolo_output_bytes * 8 + layer_count * 8",
            "cycles": control_cycles,
            "status": "ASSUMED_NOT_MEASURED",
        },
        "fixed_compute_control_cycles": fixed_cycles,
        "cycles_left_for_request_path": request_path_budget,
        "average_total_request_cycles_budget": {
            "exact_numerator": request_path_budget,
            "exact_denominator": requests,
            "decimal": format(average_cost, ".9f"),
            "includes_assumed_three_cycle_request_base": True,
            "average_added_wait_cycles_after_three_cycle_base": format(average_cost - Decimal(3), ".9f"),
            "status": "ASSUMED_NOT_MEASURED",
        },
        "core_timeout_deployment_value": {"value": None, "status": "NOT_MEASURED"},
        "drain_timeout_deployment_value": {"value": None, "status": "NOT_MEASURED"},
        "scenarios": scenarios,
        "interpretation": (
            "MAC×2 与 control×8 是历史静态预算假设，不是 RTL 全程周期上界；"
            "冻结 TB stall pattern 是测试向量，不是 HP 实际响应延迟。"
        ),
    }


def build_summary() -> dict[str, Any]:
    """读取冻结 manifest、当前源码和 T66 冻结引用并生成可复算摘要。"""
    manifest_binding = _bound_file(MANIFEST_RELATIVE, MANIFEST_SHA256)
    legacy_binding = _bound_file(LEGACY_ESTIMATOR_RELATIVE)
    acceptance_binding = _bound_file(T66_ACCEPTANCE_RELATIVE, T66_ACCEPTANCE_SHA256)
    budget_tool_binding = _bound_file("verification/s2b_memory_request_budget.py")
    budget_test_binding = _bound_file("verification/test_s2b_memory_request_budget.py")
    manifest_raw = (ROOT / MANIFEST_RELATIVE).read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    layers = validate_manifest(manifest)

    acceptance_text = (ROOT / T66_ACCEPTANCE_RELATIVE).read_text(encoding="utf-8")
    _require(T66_RECORD_RELATIVE in acceptance_text, "T68 acceptance record no longer names the exact T66 record")
    _require(T66_RECORD_SHA256 in acceptance_text, "T68 acceptance record no longer binds the T66 SHA")
    _require("2,551,955" in acceptance_text, "T68 acceptance record no longer reports the T66 request count")
    _require("1,384,448" in acceptance_text, "T68 acceptance record no longer reports the T66 output write count")
    t66_path = ROOT / T66_RECORD_RELATIVE
    t66_available = t66_path.is_file()
    if t66_available:
        _require(_sha256(t66_path) == T66_RECORD_SHA256, "available T66 record does not match its frozen SHA")

    totals = {"feature": 0, "weight": 0, "maxpool": 0, "route": 0, "upsample": 0, "write": 0, "mac_group_taps": 0}
    for layer in layers:
        for name, value in layer["read_requests"].items():
            totals[name] += value
        totals["write"] += layer["write_requests"]
        totals["mac_group_taps"] += layer["mac_group_taps"]
    read_total = sum(totals[name] for name in ("feature", "weight", "maxpool", "route", "upsample"))
    request_total = read_total + totals["write"]
    _require(request_total == 96_135_961, f"current static total changed: {request_total}")

    legacy_feature = 0
    legacy_weight = 0
    legacy_upsample_read = 0
    for layer in manifest["layers"]:
        if layer["op"] == "convolutional":
            input_shape = layer["input_shape_nchw"]
            output_shape = layer["output_shape_nchw"]
            kernel_height, kernel_width = layer["kernel_hw"]
            input_channels = input_shape[1]
            output_channels = output_shape[1]
            output_groups = (output_channels + LANES - 1) // LANES
            legacy_feature += _elements(tuple(input_shape)) * output_groups
            legacy_weight += output_channels * input_channels * kernel_height * kernel_width
        elif layer["op"] == "upsample":
            legacy_upsample_read += _elements(tuple(layer["input_shape_nchw"]))
    legacy_total = legacy_feature + legacy_weight + totals["maxpool"] + totals["route"] + legacy_upsample_read + totals["write"]
    _require(legacy_total == 100_044_902, f"historical estimator reproduction changed: {legacy_total}")

    source_bindings = [_bound_file(relative) for relative in SOURCE_PATHS]
    source_bindings.append(legacy_binding)
    layer0 = layers[0]
    _require(layer0["request_total"] == T66_LAYER0_REQUESTS, "layer0 request count does not reproduce the T66 frozen reference")
    _require(layer0["write_requests"] == T66_LAYER0_WRITES, "layer0 write count does not reproduce the T66 frozen reference")
    stall_pattern_raw = manifest["operator_test_plan"]["protocol_vectors"]["memory_stall_cycles"]
    _require(type(stall_pattern_raw) is list and all(type(value) is int and value >= 0 for value in stall_pattern_raw),
             "frozen memory stall vector is missing or unsupported")
    stall_pattern = tuple(stall_pattern_raw)
    cycle = cycle_sensitivity(request_total, totals["mac_group_taps"], totals["write"], len(layers), stall_pattern)

    return {
        "schema_version": 1,
        "status": "PASS_STATIC_REQUEST_BUDGET_FOR_FROZEN_INPUTS",
        "scope": "成功完成一帧、未发生异常中止时的静态逻辑 HP0 请求数量；不表示运行周期、部署超时或板上通过。",
        "source_commit": "5b4b140d9540759a6940b339e93278371c06987e",
        "model_manifest": manifest_binding,
        "budget_tool_source": budget_tool_binding,
        "budget_test_source": budget_test_binding,
        "current_logic_sources": source_bindings,
        "operation_counts": EXPECTED_OP_COUNTS,
        "request_accounting": {
            "lane_mode": "single_byte_lane",
            "logical_reads": read_total,
            "logical_writes": totals["write"],
            "logical_total": request_total,
            "physical_read_single_beat_transactions": read_total,
            "physical_write_single_beat_transactions": totals["write"],
            "physical_single_beat_transactions": request_total,
            "physical_mapping": (
                "当前引擎逐字节读取使用 one-hot rstrb，逐字节写入使用 one-hot wstrb；"
                "adapter ARLEN/AWLEN=0，byte read ARSIZE=0，每个单字节逻辑请求对应一个物理 single-beat。"
                "写 beat 的 AWSIZE 为 4-byte transfer size，但仅 one-hot WSTRB lane 生效。"
                "这不是一般 word/burst/coalescing 结论。"
            ),
            "includes": ["每个非 YOLO 层输出写", "每空间 tile 重复权重读", "每 tile 有效 feature patch 读", "upsample 每个输出元素一次源读"],
            "excludes": ["padding 坐标的 HP0 读（仅扫描并填零）", "YOLO alias 读写", "异常停止后的未完成后缀"],
        },
        "totals_by_category": totals,
        "old_100044902_reconciliation": {
            "old_total": legacy_total,
            "current_total": request_total,
            "old_minus_current": legacy_total - request_total,
            "components": {
                "feature": {"old": legacy_feature, "current": totals["feature"], "old_minus_current": legacy_feature - totals["feature"],
                            "reason": "旧估算把完整输入 tensor 按输出 lane group 重复计数；当前按 8×8 F patch 有效边界每 tile 只读一次。"},
                "weight": {"old": legacy_weight, "current": totals["weight"], "old_minus_current": legacy_weight - totals["weight"],
                           "reason": "旧估算每层只读一次权重；当前引擎每个空间 tile 重读对应输出通道权重。"},
                "maxpool": {"old": totals["maxpool"], "current": totals["maxpool"], "old_minus_current": 0,
                            "reason": "复用冻结 maxpool valid-window 统计 helper。"},
                "route": {"old": totals["route"], "current": totals["route"], "old_minus_current": 0,
                          "reason": "每个 route 输出元素对应一次源读。"},
                "upsample": {"old": legacy_upsample_read, "current": totals["upsample"], "old_minus_current": legacy_upsample_read - totals["upsample"],
                             "reason": "旧估算按输入大小读一次；当前引擎每个输出坐标发起一次源查询。"},
                "non_yolo_writes": {"old": totals["write"], "current": totals["write"], "old_minus_current": 0,
                                    "reason": "逐层输出 tensor 字节数；YOLO alias 不写。"},
            },
            "legacy_source": legacy_binding,
        },
        "padding_and_compute": {
            "patch_scan_slots_all_convolution_tiles": sum(layer["geometry"].get("patch_scan_slots", 0) for layer in layers),
            "padding_scan_slots_not_read": sum(layer["geometry"].get("padding_scan_slots", 0) for layer in layers),
            "mac_group_taps": totals["mac_group_taps"],
            "mac_group_taps_meaning": "ceil(Cout/8) × Hout × Wout × Cin × Kh × Kw；含 padding tap，按八 lane 输出组计。",
        },
        "t66_layer0_cross_check": {
            "computed_layer0_requests": layer0["request_total"],
            "computed_layer0_writes": layer0["write_requests"],
            "frozen_acceptance_report": acceptance_binding,
            "raw_execution_record_path": T66_RECORD_RELATIVE,
            "raw_execution_record_sha256_as_bound_by_acceptance_report": T66_RECORD_SHA256,
            "raw_execution_record_available_at_exact_path": t66_available,
            "direct_raw_record_verification": "PASS" if t66_available else "BLOCKED_MISSING_LOCAL_FILE",
            "cross_check": "与 T68 冻结验收记录报告的 T66 layer0 count 相符；原 T66 JSON 未在此工作树的精确路径下提供。",
            "manual_reproduction": {
                "tile_grid": "26×26=676",
                "valid_feature": "Cin×(16+25×17)^2=3×441^2=583443",
                "weight": "Cout×Cin×Kh×Kw×tiles=32×3×3×3×676=584064",
                "writes": 1384448,
                "sum": "583443+584064+1384448=2551955",
            },
        },
        "cycle_sensitivity": cycle,
        "cycle_source_classification": {
            "frozen_testbench_stall_vector": {
                "path": MANIFEST_RELATIVE,
                "field": "operator_test_plan.protocol_vectors.memory_stall_cycles",
                "values": list(stall_pattern),
                "status": "TB_VECTOR_NOT_HP_MEASUREMENT",
            },
            "mac_times_two_and_control_times_eight": "HISTORICAL_STATIC_ASSUMPTIONS_NOT_RTL_UPPER_BOUND",
            "hp_response_latency": "UNKNOWN_NOT_MEASURED",
            "core_timeout_and_drain_timeout": "NOT_MEASURED; NOT_WRITTEN_TO_RUNTIME_CONFIG",
        },
        "limitations": [
            "不执行 Vivado、硬件、整网仿真或旧 2A 的 109 样本回归。",
            "物理事务数基于当前单字节 lane 请求与 adapter 单拍定义；不适用于 word/burst 合并路径。",
            "T66 原始 execution_record.json 的精确文件路径在当前工作树不存在；只以 SHA 绑定的 T68 冻结验收记录作间接计数交叉核对。",
            "周期场景全部为 ASSUMED_NOT_MEASURED；没有实测 HP 响应延迟，不能据此宣称部署可行、超时已证明或风险已关闭。",
            "本交付不冻结 G0，不执行上板；后续 G0、限定探针准入与板上验收仍待总控决策/验证。",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="复算当前 tiny416 S2B 单字节请求数量")
    parser.add_argument("--output", help="可选 JSON 输出路径；目标必须尚不存在，- 表示 stdout")
    args = parser.parse_args(argv)
    summary = build_summary()
    payload = (json.dumps(summary, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    if args.output and args.output != "-":
        target = Path(args.output)
        if not target.is_absolute():
            target = ROOT / target
        with target.open("xb") as stream:
            stream.write(payload)
    else:
        sys.stdout.buffer.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
