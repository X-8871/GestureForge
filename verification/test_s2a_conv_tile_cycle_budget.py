"""根据冻结 tiny416 清单复算 8-lane 卷积后端的单帧周期估算。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json"
MANIFEST_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
STALL_SOURCE = "operator_test_plan.protocol_vectors.memory_stall_cycles"
EXPECTED_STALL_PATTERN = (0, 1, 2, 7, 3)
LANES = 8
TIMEOUT_MAX = (1 << 32) - 1


@dataclass(frozen=True)
class ConvMetrics:
    """保存单个卷积层的静态字节数和分组 MAC 计数。"""

    mac_group_taps: int
    feature_bytes: int
    weight_bytes: int
    line_buffer_bytes: int
    lane_weight_bytes: int


@dataclass(frozen=True)
class Estimate:
    """保存整帧估算结果；此结构不表示 RTL 仿真或周期证明。"""

    layers: int
    convolutional_layers: int
    yolo_alias_layers: int
    mac_group_taps: int
    feature_bytes: int
    weight_bytes: int
    maxpool_read_bytes: int
    route_read_bytes: int
    upsample_source_read_bytes: int
    nonconv_read_bytes: int
    owned_write_bytes: int
    request_count: int
    memory_request_cycles: int
    mac_cycles: int
    control_cycles: int
    cycles: int
    timeout_max: int
    headroom_cycles: int
    max_line_buffer_bytes: int
    max_lane_weight_bytes: int


def _positive_shape(shape: Any, context: str) -> tuple[int, ...]:
    if not isinstance(shape, (list, tuple)) or not shape:
        raise ValueError(f"{context}: NCHW shape must be a non-empty list")
    if any(type(value) is not int or value <= 0 for value in shape):
        raise ValueError(f"{context}: shape dimensions must be positive integers")
    return tuple(shape)


def _elements(shape: Any, context: str) -> int:
    count = 1
    for dimension in _positive_shape(shape, context):
        count *= dimension
    return count


def ceil_div(numerator: int, denominator: int) -> int:
    if type(numerator) is not int or numerator < 0:
        raise ValueError("numerator must be a non-negative integer")
    if type(denominator) is not int or denominator <= 0:
        raise ValueError("denominator must be a positive integer")
    return (numerator + denominator - 1) // denominator


def conv_metrics(layer: dict[str, Any], lanes: int = LANES) -> ConvMetrics:
    if layer.get("op") != "convolutional":
        raise ValueError("conv_metrics requires a convolutional descriptor")
    if type(lanes) is not int or lanes <= 0:
        raise ValueError("lanes must be a positive integer")

    input_shape = _positive_shape(layer.get("input_shape_nchw"), "conv input")
    output_shape = _positive_shape(layer.get("output_shape_nchw"), "conv output")
    if len(input_shape) != 4 or len(output_shape) != 4:
        raise ValueError("convolution descriptors must use NCHW shapes")
    batch, input_channels, input_height, input_width = input_shape
    output_batch, output_channels, output_height, output_width = output_shape
    if batch != 1 or output_batch != batch:
        raise ValueError("single-frame estimate requires batch size one")

    groups = layer.get("groups")
    kernel = layer.get("kernel_hw")
    if type(groups) is not int or groups <= 0 or input_channels % groups:
        raise ValueError("convolution groups must divide the input channels")
    if not isinstance(kernel, list) or len(kernel) != 2:
        raise ValueError("convolution kernel_hw must contain two dimensions")
    kernel_height, kernel_width = kernel
    if any(type(value) is not int or value <= 0 for value in kernel):
        raise ValueError("convolution kernel dimensions must be positive integers")

    reduction = (input_channels // groups) * kernel_height * kernel_width
    output_groups = ceil_div(output_channels, lanes)
    return ConvMetrics(
        mac_group_taps=output_groups * output_height * output_width * reduction,
        feature_bytes=_elements(input_shape, "conv input") * output_groups,
        weight_bytes=output_channels * reduction,
        line_buffer_bytes=input_channels * input_width * kernel_height,
        lane_weight_bytes=lanes * reduction,
    )


def maxpool_read_bytes(layer: dict[str, Any]) -> int:
    if layer.get("op") != "maxpool":
        raise ValueError("maxpool_read_bytes requires a maxpool descriptor")
    input_shape = _positive_shape(layer.get("input_shape_nchw"), "maxpool input")
    output_shape = _positive_shape(layer.get("output_shape_nchw"), "maxpool output")
    if len(input_shape) != 4 or len(output_shape) != 4:
        raise ValueError("maxpool descriptors must use NCHW shapes")
    batch, channels, input_height, input_width = input_shape
    output_batch, output_channels, output_height, output_width = output_shape
    if batch != output_batch or channels != output_channels:
        raise ValueError("maxpool must preserve batch and channels")

    kernel = layer.get("kernel_hw")
    stride = layer.get("stride_hw")
    origin = layer.get("window_origin_yx_at_output_0")
    if not isinstance(kernel, list) or len(kernel) != 2:
        raise ValueError("maxpool kernel_hw must contain two dimensions")
    if not isinstance(stride, list) or len(stride) != 2:
        raise ValueError("maxpool stride_hw must contain two dimensions")
    if not isinstance(origin, list) or len(origin) != 2:
        raise ValueError("maxpool origin must contain two coordinates")
    if any(type(value) is not int or value <= 0 for value in kernel + stride):
        raise ValueError("maxpool kernel and stride dimensions must be positive")
    if any(type(value) is not int for value in origin):
        raise ValueError("maxpool origin coordinates must be integers")

    total = 0
    for output_y in range(output_height):
        start_y = origin[0] + output_y * stride[0]
        valid_height = max(0, min(start_y + kernel[0], input_height) - max(start_y, 0))
        for output_x in range(output_width):
            start_x = origin[1] + output_x * stride[1]
            valid_width = max(0, min(start_x + kernel[1], input_width) - max(start_x, 0))
            total += batch * channels * valid_height * valid_width
    return total


def owned_write_bytes(layers: list[dict[str, Any]]) -> int:
    return sum(
        layer["tensor_length_bytes"]
        for layer in layers
        if layer.get("op") != "yolo"
    )


def cycle_components(
    request_count: int,
    mac_group_taps: int,
    owned_output_bytes: int,
    layer_count: int,
    request_cycles: int,
) -> tuple[int, int, int, int]:
    values = (request_count, mac_group_taps, owned_output_bytes, layer_count, request_cycles)
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("cycle-count inputs must be non-negative integers")
    memory_cycles = request_count * request_cycles
    mac_cycles = mac_group_taps * 2
    control_cycles = owned_output_bytes * 8 + layer_count * 8
    return memory_cycles, mac_cycles, control_cycles, memory_cycles + mac_cycles + control_cycles


def estimate_manifest(manifest: dict[str, Any], stall_pattern: tuple[int, ...]) -> Estimate:
    layers = manifest.get("layers")
    if not isinstance(layers, list) or not layers:
        raise ValueError("manifest layers must be a non-empty list")
    if not stall_pattern or any(type(value) is not int or value < 0 for value in stall_pattern):
        raise ValueError("memory stall pattern must contain non-negative integer cycles")

    conv_layers = [layer for layer in layers if layer.get("op") == "convolutional"]
    yolo_layers = [layer for layer in layers if layer.get("op") == "yolo"]
    maxpool_layers = [layer for layer in layers if layer.get("op") == "maxpool"]
    route_layers = [layer for layer in layers if layer.get("op") == "route"]
    upsample_layers = [layer for layer in layers if layer.get("op") == "upsample"]

    for layer in layers:
        output_bytes = layer.get("tensor_length_bytes")
        if type(output_bytes) is not int or output_bytes <= 0:
            raise ValueError(f"layer {layer.get('layer_index')} has invalid tensor_length_bytes")
        if output_bytes != _elements(layer.get("output_shape_nchw"), "layer output"):
            raise ValueError(f"layer {layer.get('layer_index')} tensor length disagrees with output shape")

    conv_totals = [conv_metrics(layer) for layer in conv_layers]
    mac_group_taps = sum(item.mac_group_taps for item in conv_totals)
    feature_bytes = sum(item.feature_bytes for item in conv_totals)
    weight_bytes = sum(item.weight_bytes for item in conv_totals)
    maxpool_reads = sum(maxpool_read_bytes(layer) for layer in maxpool_layers)
    route_reads = sum(layer["tensor_length_bytes"] for layer in route_layers)
    upsample_source_reads = sum(
        _elements(layer.get("input_shape_nchw"), "upsample input")
        for layer in upsample_layers
    )
    write_bytes = owned_write_bytes(layers)
    nonconv_reads = maxpool_reads + route_reads + upsample_source_reads
    requests = feature_bytes + weight_bytes + nonconv_reads + write_bytes
    request_cycles = max(stall_pattern) + 3
    memory_cycles, mac_cycles, control_cycles, cycles = cycle_components(
        requests, mac_group_taps, write_bytes, len(layers), request_cycles
    )

    return Estimate(
        layers=len(layers),
        convolutional_layers=len(conv_layers),
        yolo_alias_layers=len(yolo_layers),
        mac_group_taps=mac_group_taps,
        feature_bytes=feature_bytes,
        weight_bytes=weight_bytes,
        maxpool_read_bytes=maxpool_reads,
        route_read_bytes=route_reads,
        upsample_source_read_bytes=upsample_source_reads,
        nonconv_read_bytes=nonconv_reads,
        owned_write_bytes=write_bytes,
        request_count=requests,
        memory_request_cycles=memory_cycles,
        mac_cycles=mac_cycles,
        control_cycles=control_cycles,
        cycles=cycles,
        timeout_max=TIMEOUT_MAX,
        headroom_cycles=TIMEOUT_MAX - cycles,
        max_line_buffer_bytes=max(item.line_buffer_bytes for item in conv_totals),
        max_lane_weight_bytes=max(item.lane_weight_bytes for item in conv_totals),
    )


class BudgetArithmeticTests(unittest.TestCase):
    """覆盖别名排除、尾组分组和超时算术。"""

    def test_yolo_alias_does_not_add_owned_write(self) -> None:
        layers = [
            {"op": "convolutional", "tensor_length_bytes": 9},
            {"op": "yolo", "tensor_length_bytes": 9},
        ]
        self.assertEqual(owned_write_bytes(layers), 9)

    def test_tail_output_channels_use_ceiling_lane_group(self) -> None:
        layer = {
            "op": "convolutional",
            "input_shape_nchw": [1, 1, 1, 1],
            "output_shape_nchw": [1, 9, 1, 1],
            "groups": 1,
            "kernel_hw": [1, 1],
        }
        metrics = conv_metrics(layer, lanes=8)
        self.assertEqual(metrics.mac_group_taps, 2)
        self.assertEqual(metrics.feature_bytes, 2)
        self.assertEqual(metrics.weight_bytes, 9)

    def test_control_and_timeout_arithmetic(self) -> None:
        memory, mac, control, total = cycle_components(7, 3, 2, 4, 10)
        self.assertEqual((memory, mac, control, total), (70, 6, 48, 124))
        self.assertEqual(TIMEOUT_MAX, 4_294_967_295)
        self.assertEqual(TIMEOUT_MAX - total, 4_294_967_171)

    def test_maxpool_counts_only_valid_window_cells(self) -> None:
        layer = {
            "op": "maxpool",
            "input_shape_nchw": [1, 1, 2, 2],
            "output_shape_nchw": [1, 1, 3, 3],
            "kernel_hw": [2, 2],
            "stride_hw": [1, 1],
            "window_origin_yx_at_output_0": [-1, -1],
        }
        self.assertEqual(maxpool_read_bytes(layer), 16)


def _load_bound_manifest() -> tuple[dict[str, Any], str, tuple[int, ...]]:
    raw = MANIFEST_PATH.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != MANIFEST_SHA256:
        raise ValueError(f"T01 manifest SHA256 mismatch: got {digest}")
    manifest = json.loads(raw.decode("utf-8"))
    vectors = manifest.get("operator_test_plan", {}).get("protocol_vectors", {})
    stall_pattern_raw = vectors.get("memory_stall_cycles")
    if not isinstance(stall_pattern_raw, list):
        raise ValueError(f"missing manifest field: {STALL_SOURCE}")
    stall_pattern = tuple(stall_pattern_raw)
    if stall_pattern != EXPECTED_STALL_PATTERN:
        raise ValueError(f"unexpected frozen memory stall pattern: {stall_pattern}")
    return manifest, digest, stall_pattern


def _run_unit_tests() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BudgetArithmeticTests)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise AssertionError(stream.getvalue().strip())
    return result.testsRun


def _validate_frozen_metrics(estimate: Estimate) -> None:
    expected = {
        "layers": 38,
        "convolutional_layers": 21,
        "yolo_alias_layers": 2,
        "mac_group_taps": 424_506_368,
        "feature_bytes": 75_798_528,
        "weight_bytes": 5_877_088,
        "maxpool_read_bytes": 2_422_784,
        "route_read_bytes": 4_542_720,
        "upsample_source_read_bytes": 21_632,
        "nonconv_read_bytes": 6_987_136,
        "owned_write_bytes": 11_382_150,
        "request_count": 100_044_902,
        "memory_request_cycles": 1_000_449_020,
        "mac_cycles": 849_012_736,
        "control_cycles": 91_057_504,
        "cycles": 1_940_519_260,
        "timeout_max": 4_294_967_295,
        "headroom_cycles": 2_354_448_035,
        "max_line_buffer_bytes": 29_952,
        "max_lane_weight_bytes": 36_864,
    }
    actual = asdict(estimate)
    for name, value in expected.items():
        if actual[name] != value:
            raise AssertionError(f"{name}: expected {value}, computed {actual[name]}")


def main() -> int:
    manifest, digest, stall_pattern = _load_bound_manifest()
    estimate = estimate_manifest(manifest, stall_pattern)
    _validate_frozen_metrics(estimate)
    test_count = _run_unit_tests()
    summary = {
        "status": "ESTIMATE_ONLY_NOT_RTL_PROOF",
        "manifest_sha256": digest,
        "stall_source": STALL_SOURCE,
        "stall_pattern_cycles": list(stall_pattern),
        "lanes": LANES,
        "estimate": asdict(estimate),
        "model": "request=max_stall+3; MAC=2/group-tap; control=8/output-byte+8/layer; linebuf=Cin*Win*Kh",
        "unit_tests": test_count,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"verification failed: {error}", file=sys.stderr)
        raise SystemExit(1)
