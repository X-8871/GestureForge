#!/usr/bin/env python3
"""生成阶段 2A 的模型层描述与固定输入清单。"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone, timedelta
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
from typing import Any

import cv2
import numpy as np
from PIL import Image

try:
    from .s1_t02_d2_int8_forward import (
        INT8_MAX,
        INT8_MIN,
        INPUT_SCALE,
        parse_package,
        parse_cfg_sections,
        round_away_array,
        saturate_array,
    )
    from .s1_t02_d2_numeric_reference import letterbox_geometry
except ImportError:
    from s1_t02_d2_int8_forward import (
        INT8_MAX,
        INT8_MIN,
        INPUT_SCALE,
        parse_package,
        parse_cfg_sections,
        round_away_array,
        saturate_array,
    )
    from s1_t02_d2_numeric_reference import letterbox_geometry


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "report" / "evidence" / "S1-T02"
EXPECTED_CLASSES = ("fist", "palm", "one", "two_up", "three")
EXPECTED_CFG_SHA256 = "5475dff0daa8ac791ffbfcd10a188aa63d146244e561d62867ac59d627725376"
EXPECTED_WEIGHTS_SHA256 = "3984affa0a7fdd83ff851646139ea4e734c3df93569bfbaab214774cd92f7d8a"
EXPECTED_PACKAGE_SHA256 = "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39"
EXPECTED_CALIBRATION_SHA256 = "d637a2feb671429741c8b6703caaa9cdf995abf49dfa4b72e41f62dfbea1a35c"
EXPECTED_MANIFEST_SHA256 = "fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74"
BASELINE_COMMIT = "0ce55634c4e07000b0f8c1640b3b6ba4ab072386"
BASELINE_D9_TEST_SHA256 = "7c5aebac28f316c16e4fbef80905c73b21036cfeab80115c926f143605277f5a"
INPUT_BASE = 0x00000000
WEIGHT_BASE = 0x00100000
FEATURE_BASE = 0x01000000
ALIGNMENT = 64


class DeliveryError(ValueError):
    """表示模型交付绑定、cfg 或样本清单错误。"""


def sha256_file(path: Path) -> str:
    """计算普通文件的 SHA-256。"""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    """计算内存数据的 SHA-256。"""

    return hashlib.sha256(value).hexdigest()


def decode_rgb(path: Path) -> np.ndarray:
    """按 D2 INT8 前向的 OpenCV 解码路径读取 RGB 8-bit 像素。"""

    encoded = np.fromfile(str(path), dtype=np.uint8)
    image_bgr = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image_bgr is None or image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
        raise DeliveryError(f"图片无法按三通道 RGB 输入解码: {path}")
    return image_bgr[:, :, ::-1].copy()


def preprocess_rgb_chw_int8(rgb: np.ndarray, dst_width: int = 416, dst_height: int = 416) -> np.ndarray:
    """向量化复现 D2 RGB letterbox、CHW/255 和对称 INT8 量化。"""

    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype != np.uint8:
        raise DeliveryError("预处理输入必须为 HWC RGB uint8")
    src_height, src_width = rgb.shape[:2]
    geometry = letterbox_geometry(src_width, src_height, dst_width, dst_height)
    new_width = int(geometry["new_width"])
    new_height = int(geometry["new_height"])
    offset_x = int(geometry["offset_x"])
    offset_y = int(geometry["offset_y"])
    source = rgb.astype(np.float64)
    if (src_width, src_height) == (new_width, new_height):
        resized = source
    else:
        x_scale = (src_width - 1) / (new_width - 1) if new_width != 1 else 0.0
        y_scale = (src_height - 1) / (new_height - 1) if new_height != 1 else 0.0
        x_positions = np.arange(new_width, dtype=np.float64) * x_scale
        y_positions = np.arange(new_height, dtype=np.float64) * y_scale
        x0 = np.floor(x_positions).astype(np.int64)
        y0 = np.floor(y_positions).astype(np.int64)
        x1 = np.minimum(x0 + 1, src_width - 1)
        y1 = np.minimum(y0 + 1, src_height - 1)
        if new_width == 1:
            x0[0] = x1[0] = src_width - 1
        else:
            x0[-1] = x1[-1] = src_width - 1
        if new_height == 1:
            y0[0] = y1[0] = src_height - 1
        else:
            y0[-1] = y1[-1] = src_height - 1
        dx = (x_positions - x0).reshape(1, new_width, 1)
        dy = (y_positions - y0).reshape(new_height, 1, 1)
        dx[:, -1, :] = 0.0
        dy[-1, :, :] = 0.0
        top = source[y0[:, None], x0[None, :], :] * (1.0 - dx) + source[y0[:, None], x1[None, :], :] * dx
        bottom = source[y1[:, None], x0[None, :], :] * (1.0 - dx) + source[y1[:, None], x1[None, :], :] * dx
        resized = top * (1.0 - dy) + bottom * dy
    boxed = np.full((dst_height, dst_width, 3), 0.5, dtype=np.float64)
    normalized = np.clip(resized / 255.0, 0.0, 1.0)
    boxed[offset_y : offset_y + new_height, offset_x : offset_x + new_width, :] = normalized
    chw = boxed.transpose(2, 0, 1)
    quantized = saturate_array(round_away_array(chw / INPUT_SCALE))
    if quantized.shape != (3, dst_height, dst_width):
        raise DeliveryError("D2 预处理输出形状错误")
    if quantized.size and (int(quantized.min()) < INT8_MIN or int(quantized.max()) > INT8_MAX):
        raise DeliveryError("D2 输入量化超出对称 INT8 范围")
    return np.ascontiguousarray(quantized)


def preprocess_file_sha256(path: Path) -> str:
    """计算逐字节 CHW INT8 输入张量哈希，不保留派生图像副本。"""

    return sha256_bytes(preprocess_rgb_chw_int8(decode_rgb(path)).tobytes(order="C"))


def image_metadata(path: Path) -> dict[str, Any]:
    """读取图片宽高和格式，不解码或修改图像文件。"""

    with Image.open(path) as image:
        width, height = image.size
        image_format = image.format
    if width <= 0 or height <= 0:
        raise DeliveryError(f"图片尺寸无效: {path}")
    return {"width": width, "height": height, "format": image_format}


def align_up(value: int, alignment: int) -> int:
    """按二的幂边界向上对齐地址。"""

    return (value + alignment - 1) & ~(alignment - 1)


def parse_package_offsets(path: Path) -> dict[int, dict[str, int]]:
    """解析 GFINT8W1 包并返回各层参数在包内的字节偏移。"""

    blob = path.read_bytes()
    if len(blob) < 28:
        raise DeliveryError("GFINT8W1 包头不完整")
    magic, version, layer_count, width, height = struct.unpack_from("<8sIIII", blob, 0)
    channels = struct.unpack_from("<I", blob, 24)[0]
    if (magic, version, width, height, channels) != (b"GFINT8W1", 1, 416, 416, 3):
        raise DeliveryError("GFINT8W1 magic/version/模型输入与 tiny416 不符")
    offset = 28
    result: dict[int, dict[str, int]] = {}
    for _ in range(layer_count):
        if offset + 32 > len(blob):
            raise DeliveryError("GFINT8W1 层记录提前结束")
        layer_index, filters, _inputs, _groups, _kernel, weight_count, _bn, scale_count = struct.unpack_from(
            "<8I", blob, offset
        )
        if layer_index in result or filters <= 0 or scale_count != filters:
            raise DeliveryError("GFINT8W1 层索引或 scale 数量无效")
        offset += 32
        scale_offset = offset
        bias_offset = scale_offset + filters * 4
        weight_offset = bias_offset + filters * 4
        end = weight_offset + weight_count
        if end > len(blob):
            raise DeliveryError("GFINT8W1 参数记录长度超出文件")
        result[layer_index] = {
            "record_offset": offset - 32,
            "weight_scale_offset": scale_offset,
            "fused_bias_offset": bias_offset,
            "quantized_weight_offset": weight_offset,
            "quantized_weight_bytes": weight_count,
        }
        offset = end
    if offset != len(blob) or len(result) != layer_count:
        raise DeliveryError("GFINT8W1 尾部长度或层数量不一致")
    return result


def resolve_ref(reference: int, layer_index: int) -> int:
    """解析 Darknet route 相对/绝对层号。"""

    return layer_index + reference if reference < 0 else reference


def read_network(path: Path, activation_report: dict[str, Any], package_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any], dict[int, Any]]:
    """按冻结 cfg、scale 报告和 GF8 参数构建完整层与地址清单。"""

    sections = parse_cfg_sections(path)
    net = sections[0].options
    width, height, channels = (int(net[key]) for key in ("width", "height", "channels"))
    if (width, height, channels) != (416, 416, 3):
        raise DeliveryError("cfg 输入不是 RGB 416×416")
    activation_scales = {
        int(key): float(value["activation_scale"])
        for key, value in activation_report["layers"].items()
    }
    package_header, package_layers = parse_package(package_path)
    package_offsets = parse_package_offsets(package_path)
    if (package_header["width"], package_header["height"], package_header["channels"]) != (416, 416, 3):
        raise DeliveryError("GF8 权重包头不是 tiny416")

    layers: list[dict[str, Any]] = []
    shapes: list[dict[str, Any]] = []
    scales: list[float] = []
    next_address = FEATURE_BASE
    conv_seen: set[int] = set()
    for layer_index, section in enumerate(sections[1:]):
        kind = section.kind
        options = section.options
        prev_shape = shapes[-1] if shapes else {"n": 1, "c": channels, "h": height, "w": width}
        prev_scale = scales[-1] if scales else 1.0 / 127.0
        refs = [layer_index - 1] if layer_index else ["network_input"]
        descriptor: dict[str, Any] = {
            "layer_index": layer_index,
            "cfg_section": layer_index + 1,
            "op": kind,
            "input_tensor_indices": refs,
            "input_shape_nchw": [prev_shape["n"], prev_shape["c"], prev_shape["h"], prev_shape["w"]],
            "input_scale": prev_scale,
            "layout": "NCHW",
            "element_type": "int8_twos_complement",
        }
        output_scale = prev_scale
        output = dict(prev_shape)

        if kind == "convolutional":
            filters, kernel = int(options["filters"]), int(options["size"])
            stride = int(options.get("stride", "1"))
            pad = int(options.get("pad", "0"))
            padding = kernel // 2 if pad else int(options.get("padding", "0"))
            groups = int(options.get("groups", "1"))
            out_h = (prev_shape["h"] + 2 * padding - kernel) // stride + 1
            out_w = (prev_shape["w"] + 2 * padding - kernel) // stride + 1
            if out_h <= 0 or out_w <= 0 or layer_index not in package_layers or layer_index not in activation_scales:
                raise DeliveryError(f"卷积层 {layer_index} 的尺寸或量化参数不完整")
            weights = package_layers[layer_index]
            if weights.filters != filters or weights.input_channels != prev_shape["c"]:
                raise DeliveryError(f"卷积层 {layer_index} cfg 与 GF8 权重维度不符")
            output_scale = activation_scales[layer_index]
            output = {"n": 1, "c": filters, "h": out_h, "w": out_w}
            descriptor.update({
                "kernel_hw": [kernel, kernel], "stride_hw": [stride, stride],
                "padding_lrtb": [padding, padding, padding, padding], "groups": groups,
                "padding_value_int8": 0,
                "activation": options.get("activation", "linear"),
                "accumulator_bits": 32, "output_scale": output_scale,
                "weight_layer_index": layer_index,
                "gf8_parameter_offsets": package_offsets[layer_index],
                "weight_scale_per_output_channel": [float(value) for value in weights.weight_scales],
                "fused_bias_float32_per_output_channel": [float(value) for value in weights.fused_biases],
                "bias_accumulator_int32_per_output_channel": [
                    int(math.floor(abs(float(bias)) / (prev_scale * float(weight_scale)) + 0.5))
                    * (1 if float(bias) >= 0.0 else -1)
                    for bias, weight_scale in zip(weights.fused_biases, weights.weight_scales)
                ],
            })
            conv_seen.add(layer_index)
        elif kind == "route":
            refs = [resolve_ref(int(part.strip()), layer_index) for part in options["layers"].split(",")]
            if not refs or any(index < 0 or index >= len(shapes) for index in refs):
                raise DeliveryError(f"route 层 {layer_index} 引用越界")
            source_shapes = [shapes[index] for index in refs]
            if any((item["h"], item["w"]) != (source_shapes[0]["h"], source_shapes[0]["w"]) for item in source_shapes):
                raise DeliveryError(f"route 层 {layer_index} 空间维不一致")
            groups = int(options.get("groups", "1"))
            group_id = int(options.get("group_id", "0"))
            if groups <= 0 or not 0 <= group_id < groups:
                raise DeliveryError(f"route 层 {layer_index} 分组参数非法")
            if groups == 1:
                channel_ranges = [[0, item["c"]] for item in source_shapes]
            else:
                if len(refs) != 1 or source_shapes[0]["c"] % groups:
                    raise DeliveryError(f"route 层 {layer_index} 分组参数非法")
                channels_per_group = source_shapes[0]["c"] // groups
                channel_start = group_id * channels_per_group
                channel_ranges = [[channel_start, channel_start + channels_per_group]]
            channels_total = sum(end - start for start, end in channel_ranges)
            output = {"n": 1, "c": channels_total, "h": source_shapes[0]["h"], "w": source_shapes[0]["w"]}
            output_scale = max(scales[index] for index in refs)
            descriptor.update({
                "input_tensor_indices": refs,
                "input_shape_nchw": [[1, item["c"], item["h"], item["w"]] for item in source_shapes],
                "input_scales": [scales[index] for index in refs],
                "route_groups": groups, "route_group_id": group_id,
                "route_source_channel_ranges": channel_ranges,
                "route_group_slice_order": "select [group_id*C/groups:(group_id+1)*C/groups] per referenced tensor before requantization and cfg-order concatenation; groups=1 selects [0:C]",
                "requantization": "以最大输入 scale 为目标；half_away_from_zero 后饱和 INT8",
                "output_scale": output_scale,
            })
        elif kind == "maxpool":
            kernel, stride = int(options["size"]), int(options["stride"])
            padding = int(options.get("padding", str(kernel - 1)))
            out_h = (prev_shape["h"] + padding - kernel) // stride + 1
            out_w = (prev_shape["w"] + padding - kernel) // stride + 1
            offset_y = -(padding // 2)
            offset_x = -(padding // 2)
            start_y = offset_y + max(0, -offset_y)
            start_x = offset_x + max(0, -offset_x)
            end_y = offset_y + (out_h - 1) * stride + kernel - 1
            end_x = offset_x + (out_w - 1) * stride + kernel - 1
            pad_top = max(0, -offset_y)
            pad_left = max(0, -offset_x)
            pad_bottom = max(0, end_y - (prev_shape["h"] - 1))
            pad_right = max(0, end_x - (prev_shape["w"] - 1))
            output = {"n": 1, "c": prev_shape["c"], "h": out_h, "w": out_w}
            descriptor.update({
                "kernel_hw": [kernel, kernel], "stride_hw": [stride, stride],
                "darknet_padding_parameter": padding,
                "output_hw_formula": "(input_hw + padding - kernel_hw) // stride_hw + 1",
                "window_origin_yx_at_output_0": [start_y - pad_top, start_x - pad_left],
                "padding_lrtb_actual": [pad_left, pad_right, pad_top, pad_bottom],
                "pad_value_int8": INT8_MIN,
                "output_scale": output_scale,
            })
        elif kind == "upsample":
            stride = int(options.get("stride", "2"))
            output = {"n": 1, "c": prev_shape["c"], "h": prev_shape["h"] * stride, "w": prev_shape["w"] * stride}
            descriptor.update({"scale": float(options.get("scale", "1")), "stride": stride, "method": "nearest_repeat", "output_scale": output_scale})
        elif kind == "yolo":
            mask = [int(part.strip()) for part in options["mask"].split(",")]
            anchors_raw = [int(part.strip()) for part in options["anchors"].split(",")]
            anchors = [[anchors_raw[index], anchors_raw[index + 1]] for index in range(0, len(anchors_raw), 2)]
            output = dict(prev_shape)
            descriptor.update({
                "output_tensor_index": layer_index - 1,
                "input_tensor_indices": [layer_index - 1],
                "anchors_wh": anchors, "mask": mask, "classes": int(options["classes"]),
                "scale_x_y": float(options.get("scale_x_y", "1")),
                "new_coords": int(options.get("new_coords", "0")),
                "head_logit_scale": prev_scale,
                "output_scale": output_scale,
            })
        else:
            raise DeliveryError(f"不支持 cfg section: [{kind}]")

        length = output["n"] * output["c"] * output["h"] * output["w"]
        if kind == "yolo":
            address = layers[-1]["tensor_address"]
            length = layers[-1]["tensor_length_bytes"]
        else:
            address = align_up(next_address, ALIGNMENT)
            next_address = address + length
        descriptor.update({
            "output_shape_nchw": [output["n"], output["c"], output["h"], output["w"]],
            "output_scale": output_scale,
            "tensor_address": address,
            "tensor_length_bytes": length,
            "tensor_address_space": "S2A logical simulation byte address; not Zynq DDR physical address",
        })
        layers.append(descriptor)
        shapes.append(output)
        scales.append(output_scale)

    if len(conv_seen) != 21 or set(package_layers) != conv_seen or set(activation_scales) != conv_seen:
        raise DeliveryError("cfg、GF8 权重层和激活 scale 层集合不完全一致")
    heads = []
    for name, yolo_index, stride in (("head13", 30, 32), ("head26", 37, 16)):
        layer = layers[yolo_index]
        shape = layer["output_shape_nchw"]
        heads.append({
            "name": name,
            "yolo_layer_index": yolo_index,
            "source_convolution_layer_index": yolo_index - 1,
            "stride": stride,
            "shape_nchw": shape,
            "layout_view": "[anchor=3, entry=10, row, col] over contiguous NCHW channels; channel=anchor*10+entry",
            "int8_scale": layer["head_logit_scale"],
            "address": layer["tensor_address"],
            "length_bytes": layer["tensor_length_bytes"],
        })
    return layers, {
        "input": {"address": INPUT_BASE, "length_bytes": 416 * 416 * 3, "shape_nchw": [1, 3, 416, 416], "scale": 1.0 / 127.0},
        "weight_package": {"address": WEIGHT_BASE, "length_bytes": package_path.stat().st_size, "format": "GFINT8W1", "sha256": sha256_file(package_path)},
        "feature_workspace": {"base_address": FEATURE_BASE, "end_address_exclusive": next_address, "alignment_bytes": ALIGNMENT, "strategy": "每层输出单独分配并保持到任务结束；仅 YOLO 视图与其卷积输出共享地址"},
        "heads": heads,
    }, package_layers


MAC_DIRECTED_RULES: list[dict[str, Any]] = [
    {"k": 4, "activation_pattern": [0], "weight_pattern": [0], "bias_int32": 0},
    {"k": 4, "activation_pattern": [127, 127, -127, -127], "weight_pattern": [127, -127, 127, -127], "bias_int32": 0},
    {"k": 8, "activation_pattern": [127], "weight_pattern": [127], "bias_int32": 0},
    {"k": 8, "activation_pattern": [-127], "weight_pattern": [127], "bias_int32": 0},
    {"k": 8, "activation_pattern": [127, 0, 0, 0, 0, 0, 0, 0], "weight_pattern": [127], "bias_int32": 0},
    {"k": 8, "activation_pattern": [0, 0, 0, 0, 0, 0, 0, 127], "weight_pattern": [127], "bias_int32": 0},
    {"k": 1, "activation_pattern": [0], "weight_pattern": [0], "bias_int32": (1 << 31) - 1},
    {"k": 1, "activation_pattern": [0], "weight_pattern": [0], "bias_int32": -(1 << 31)},
    {"k": 1, "activation_pattern": [127], "weight_pattern": [127], "bias_int32": (1 << 31) - 1 - 127 * 127},
    {"k": 1, "activation_pattern": [127], "weight_pattern": [127], "bias_int32": (1 << 31) - 127 * 127},
    {"k": 1, "activation_pattern": [-127], "weight_pattern": [127], "bias_int32": -(1 << 31) + 127 * 127},
    {"k": 1, "activation_pattern": [-127], "weight_pattern": [127], "bias_int32": -(1 << 31) + 127 * 127 - 1},
    {"k": 4, "activation_pattern": [127, -127], "weight_pattern": [127], "bias_int32": 0},
    {"k": 4, "activation_pattern": [-127, 127], "weight_pattern": [127], "bias_int32": 0},
    {"k": 1, "activation_pattern": [-127], "weight_pattern": [127], "bias_int32": 0},
    {"k": "maximum_model_reduction_length", "activation_pattern": [127, -127], "weight_pattern": [127], "bias_int32": 0},
]


CONV_DIRECTED_RULES: list[dict[str, Any]] = [
    {"target": ["first", "first", "first"], "input_pattern": "zero"},
    {"target": ["first", "first", "first"], "input_pattern": "positive_extreme"},
    {"target": ["first", "first", "first"], "input_pattern": "negative_extreme"},
    {"target": ["first", "first", "first"], "input_pattern": "alternating_extremes_start_negative"},
    {"target": ["middle", "middle", "middle"], "input_pattern": "first_reduction_tap_positive_extreme"},
    {"target": ["middle", "middle", "middle"], "input_pattern": "last_reduction_tap_positive_extreme"},
    {"target": ["first", "first", "first"], "input_pattern": "first_valid_input_channel_and_spatial_point_positive_extreme"},
    {"target": ["last", "last", "last"], "input_pattern": "last_valid_input_channel_and_spatial_point_positive_extreme"},
    {"target": ["first", "first", "first"], "input_pattern": "kernel_center_positive_extreme"},
    {"target": ["last", "last", "last"], "input_pattern": "kernel_center_positive_extreme"},
    {"target": ["first", "first", "first"], "input_pattern": "positive_unit"},
    {"target": ["last", "last", "last"], "input_pattern": "negative_unit"},
    {"target": ["last", "last", "last"], "input_pattern": "zero"},
    {"target": ["first", "first", "first"], "input_pattern": "alternating_unit_start_negative"},
    {"target": ["middle", "middle", "middle"], "input_pattern": "first_reduction_tap_positive_unit"},
    {"target": ["middle", "middle", "middle"], "input_pattern": "last_reduction_tap_negative_unit"},
]


ROUTE_DIRECTED_RULES: list[dict[str, Any]] = [
    {"spatial": "first", "profile": "zero"},
    {"spatial": "first", "profile": "positive_extreme"},
    {"spatial": "first", "profile": "negative_extreme"},
    {"spatial": "first", "profile": "alternating_extremes_start_negative"},
    {"spatial": "first", "profile": "first_source_positive_extreme"},
    {"spatial": "first", "profile": "last_source_positive_extreme"},
    {"spatial": "first", "profile": "first_output_channel_positive_extreme"},
    {"spatial": "first", "profile": "last_output_channel_positive_extreme"},
    {"spatial": "middle", "profile": "distinct_source_constants"},
    {"spatial": "middle", "profile": "scale_conversion_or_identity_fallback"},
    {"spatial": "first", "profile": "positive_unit"},
    {"spatial": "first", "profile": "negative_unit"},
    {"spatial": "first", "profile": "first_output_channel_positive_extreme"},
    {"spatial": "last", "profile": "last_output_channel_negative_extreme"},
    {"spatial": "middle", "profile": "first_output_channel_negative_extreme"},
    {"spatial": "last", "profile": "last_output_channel_positive_extreme"},
]


MAXPOOL_DIRECTED_RULES: list[dict[str, Any]] = [
    {"target": ["first", "first", "first"], "profile": "zero"},
    {"target": ["first", "first", "first"], "profile": "positive_extreme"},
    {"target": ["first", "first", "first"], "profile": "negative_extreme"},
    {"target": ["first", "first", "first"], "profile": "alternating_extremes_start_negative"},
    *[{"target": ["first", "first", "first"], "profile": f"positive_tap_{tap}"} for tap in range(4)],
    *[{"target": ["first", "first", "first"], "profile": f"negative_tap_{tap}"} for tap in range(4)],
    {"target": ["first", "first", "first"], "profile": "first_output_coordinate_marker"},
    {"target": ["first", "last", "last"], "profile": "last_output_coordinate_marker"},
    {"target": ["first", "first", "first"], "profile": "first_channel_small_increasing"},
    {"target": ["last", "last", "last"], "profile": "last_channel_small_decreasing"},
]


UPSAMPLE_DIRECTED_RULES: list[dict[str, Any]] = [
    {"output": ["first", "first", "first"], "profile": "first_source_marker", "value": 1},
    {"output": ["last", "last", "last"], "profile": "last_source_marker", "value": -1},
    {"output": ["first", "first", "first"], "profile": "top_left_marker", "value": 2},
    {"output": ["first", "first", "last"], "profile": "top_right_marker", "value": 3},
    {"output": ["first", "last", "first"], "profile": "bottom_left_marker", "value": 4},
    {"output": ["first", "last", "last"], "profile": "bottom_right_marker", "value": 5},
    {"output": ["first", "first", "first"], "profile": "horizontal_pair_marker", "value": 6, "pair": "horizontal"},
    {"output": ["first", "first", "first"], "profile": "vertical_pair_marker", "value": 7, "pair": "vertical"},
    {"output": ["first", "first", "first"], "profile": "zero_source", "value": 0},
    {"output": ["first", "first", "first"], "profile": "positive_extreme_source", "value": 127},
    {"output": ["first", "first", "first"], "profile": "negative_extreme_source", "value": -127},
    {"output": ["first", "first", "first"], "profile": "alternating_source_first_element", "value": -127},
    {"output": ["first", "first", "first"], "profile": "first_channel_marker", "value": 17},
    {"output": ["last", "first", "first"], "profile": "last_channel_marker", "value": -17},
    {"output": ["first", "first", "first"], "profile": "first_output_coordinate_marker", "value": 23},
    {"output": ["last", "last", "last"], "profile": "last_output_coordinate_marker", "value": -23},
]


YOLO_DIRECTED_RULES: list[dict[str, Any]] = [
    {"queries": [[0, 0, "first", "first"]]},
    {"queries": [[0, 9, "first", "first"]]},
    {"queries": [[1, 0, "first", "first"]]},
    {"queries": [[2, 9, "last", "last"]]},
    {"queries": [[0, 0, "first", "middle"]]},
    {"queries": [[0, 0, "last", "middle"]]},
    {"queries": [[0, 0, "middle", "first"]]},
    {"queries": [[0, 0, "middle", "last"]]},
    {"queries": [[0, 0, "first", "first"]]},
    {"queries": [[2, 9, "last", "last"]]},
    {"queries": [[0, 0, "first", "first"]]},
    {"queries": [[2, 9, "first", "first"]]},
    {"queries": [[0, 0, "first", "first"]]},
    {"queries": [[2, 9, "last", "last"]]},
    {"queries": [[0, 9, "last", "last"], [1, 0, "first", "first"]]},
    {"queries": [[2, 9, "last", "last"]]},
]


def _select_index(selector: str, dimension: int) -> int:
    """按明确的首/中/末规则选择一个维度索引。"""

    if dimension <= 0:
        raise DeliveryError("定向向量的维度必须为正")
    if selector == "first":
        return 0
    if selector == "last":
        return dimension - 1
    if selector == "middle":
        return dimension // 2
    raise DeliveryError(f"未知定向索引规则: {selector}")


def _repeat_pattern(pattern: list[int], count: int) -> list[int]:
    """从索引零开始循环指定整数模式，生成恰好 count 个值。"""

    if not pattern or count < 0:
        raise DeliveryError("定向数值模式为空或长度非法")
    return [pattern[index % len(pattern)] for index in range(count)]


def _checked_mac_vector(activations: list[int], weights: list[int], bias: int) -> dict[str, Any]:
    """按 bias 后逐项乘加顺序生成 MAC 的 INT64 审计与 INT32 结果。"""

    if len(activations) != len(weights):
        raise DeliveryError("MAC 定向向量两端 K 长度不一致")
    low, high = -(1 << 31), (1 << 31) - 1
    accumulator = bias
    exact = bias
    first_overflow: int | None = None
    if not low <= accumulator <= high:
        first_overflow = -1
    for index, (activation, weight) in enumerate(zip(activations, weights)):
        product = activation * weight
        exact += product
        if first_overflow is None:
            accumulator += product
            if not low <= accumulator <= high:
                first_overflow = index
    return {
        "bias_int32": bias,
        "exact_int64_sum": exact,
        "first_int32_overflow_product_index": first_overflow,
        "expected_int32_result": exact if first_overflow is None else None,
        "accumulation_order": "initialize accumulator with bias_int32, then add activation[i]*weight[i] for i=0..K-1; check signed INT32 after every addition",
    }


def build_directed_case_vectors(
    layers: list[dict[str, Any]],
    package_layers: dict[int, Any],
    case_names: dict[str, list[str]],
) -> dict[str, Any]:
    """展开 MAC、卷积和 route 定向目录，输出唯一的有序输入向量。"""

    if not all(len(rules) == 16 for rules in (MAC_DIRECTED_RULES, CONV_DIRECTED_RULES, ROUTE_DIRECTED_RULES, MAXPOOL_DIRECTED_RULES, UPSAMPLE_DIRECTED_RULES, YOLO_DIRECTED_RULES)):
        raise DeliveryError("支持算子的定向规则必须各有 16 项")
    vectors: dict[str, Any] = {"int8_mac": [], "convolutional": {}, "maxpool": {}, "route": {}, "upsample": {}, "yolo": {}}
    max_reduction = max(int(weights.quantized_weights[0].size) for weights in package_layers.values())
    mac_names = case_names["int8_mac"]
    for case_index, rule in enumerate(MAC_DIRECTED_RULES):
        k = max_reduction if rule["k"] == "maximum_model_reduction_length" else int(rule["k"])
        activations = _repeat_pattern(rule["activation_pattern"], k)
        weights = _repeat_pattern(rule["weight_pattern"], k)
        result = _checked_mac_vector(activations, weights, int(rule["bias_int32"]))
        vectors["int8_mac"].append({
            "case_index": case_index,
            "case_name": mac_names[case_index],
            "k": k,
            "activation_int8": activations,
            "weight_int8": weights,
            **result,
        })

    conv_names = case_names["convolutional"]
    for layer in layers:
        if layer["op"] != "convolutional":
            continue
        layer_index = int(layer["layer_index"])
        package_layer = package_layers[layer_index]
        input_shape = layer["input_shape_nchw"]
        _, input_channels, input_height, input_width = input_shape
        _, output_channels, output_height, output_width = layer["output_shape_nchw"]
        kernel_height, kernel_width = layer["kernel_hw"]
        stride_y, stride_x = layer["stride_hw"]
        pad_left, pad_right, pad_top, pad_bottom = layer["padding_lrtb"]
        local_input_channels = package_layer.quantized_weights.shape[1]
        reduction_length = local_input_channels * kernel_height * kernel_width
        output_per_group = output_channels // layer["groups"]
        layer_vectors = []
        for case_index, rule in enumerate(CONV_DIRECTED_RULES):
            channel = _select_index(rule["target"][0], output_channels)
            row = _select_index(rule["target"][1], output_height)
            col = _select_index(rule["target"][2], output_width)
            patch = [0] * reduction_length
            profile = rule["input_pattern"]
            if profile == "positive_extreme":
                patch = [127] * reduction_length
            elif profile == "negative_extreme":
                patch = [-127] * reduction_length
            elif profile == "positive_unit":
                patch = [1] * reduction_length
            elif profile == "negative_unit":
                patch = [-1] * reduction_length
            elif profile == "alternating_extremes_start_negative":
                patch = _repeat_pattern([-127, 127], reduction_length)
            elif profile == "alternating_unit_start_negative":
                patch = _repeat_pattern([-1, 1], reduction_length)
            elif profile == "first_reduction_tap_positive_extreme":
                patch[0] = 127
            elif profile == "last_reduction_tap_positive_extreme":
                patch[-1] = 127
            elif profile == "first_reduction_tap_positive_unit":
                patch[0] = 1
            elif profile == "last_reduction_tap_negative_unit":
                patch[-1] = -1
            elif profile in {
                "zero",
                "first_valid_input_channel_and_spatial_point_positive_extreme",
                "last_valid_input_channel_and_spatial_point_positive_extreme",
                "kernel_center_positive_extreme",
            }:
                if profile == "first_valid_input_channel_and_spatial_point_positive_extreme":
                    local_channel = 0
                    window_y = row * stride_y - pad_top
                    window_x = col * stride_x - pad_left
                    source_y, source_x = max(0, window_y), max(0, window_x)
                    tap_y = source_y - window_y
                    tap_x = source_x - window_x
                    value = 127
                elif profile == "last_valid_input_channel_and_spatial_point_positive_extreme":
                    local_channel = local_input_channels - 1
                    window_y = row * stride_y - pad_top
                    window_x = col * stride_x - pad_left
                    source_y = min(input_height - 1, window_y + kernel_height - 1)
                    source_x = min(input_width - 1, window_x + kernel_width - 1)
                    tap_y = source_y - window_y
                    tap_x = source_x - window_x
                    value = 127
                elif profile == "kernel_center_positive_extreme":
                    local_channel = 0
                    tap_y = kernel_height // 2 if kernel_height % 2 else 0
                    tap_x = kernel_width // 2 if kernel_width % 2 else 0
                    value = 127
                else:
                    local_channel, tap_y, tap_x, value = 0, 0, 0, 0
                if profile != "zero":
                    input_y = row * stride_y - pad_top + tap_y
                    input_x = col * stride_x - pad_left + tap_x
                    if not (0 <= local_channel < local_input_channels and 0 <= tap_y < kernel_height and 0 <= tap_x < kernel_width and 0 <= input_y < input_height and 0 <= input_x < input_width):
                        raise DeliveryError(f"卷积层 {layer_index} 定向源坐标不在有效 receptive field")
                    patch[(local_channel * kernel_height + tap_y) * kernel_width + tap_x] = value
            else:
                raise DeliveryError(f"未知卷积定向输入模式: {profile}")
            weights = package_layer.quantized_weights[channel].reshape(-1).astype(np.int16).tolist()
            bias = int(layer["bias_accumulator_int32_per_output_channel"][channel])
            input_patch_origin = [row * stride_y - pad_top, col * stride_x - pad_left]
            input_channel_base = (channel // output_per_group) * local_input_channels
            source_reduction_values: list[int | None] = []
            effective_reduction_values: list[int] = []
            for reduction_index, source_value in enumerate(patch):
                local_channel = reduction_index // (kernel_height * kernel_width)
                tap_y = (reduction_index // kernel_width) % kernel_height
                tap_x = reduction_index % kernel_width
                input_y, input_x = input_patch_origin[0] + tap_y, input_patch_origin[1] + tap_x
                in_bounds = 0 <= input_y < input_height and 0 <= input_x < input_width
                source_reduction_values.append(source_value if in_bounds else None)
                effective_reduction_values.append(source_value if in_bounds else int(layer["padding_value_int8"]))
            result = _checked_mac_vector(effective_reduction_values, weights, bias)
            layer_vectors.append({
                "case_index": case_index,
                "case_name": conv_names[case_index],
                "target_output_nchw": [0, channel, row, col],
                "input_pattern": profile,
                "input_patch_origin_yx": input_patch_origin,
                "input_channel_base": input_channel_base,
                "input_channel_count_per_group": local_input_channels,
                "reduction_order": "local_input_channel, kernel_y, kernel_x; flattened index=((channel*kernel_h)+kernel_y)*kernel_w+kernel_x",
                "source_tensor_default_int8": 0,
                "source_reduction_values_int8": source_reduction_values,
                "input_reduction_int8": effective_reduction_values,
                "weight_reduction_int8": weights,
                "bias_int32": bias,
                "input_scale": layer["input_scale"],
                "weight_scale": layer["weight_scale_per_output_channel"][channel],
                "output_scale": layer["output_scale"],
                "activation": layer["activation"],
                "padding_lrtb": [pad_left, pad_right, pad_top, pad_bottom],
                "padding_value_int8": layer["padding_value_int8"],
                **result,
            })
        vectors["convolutional"][str(layer_index)] = layer_vectors

    route_names = case_names["route"]
    for layer in layers:
        if layer["op"] != "route":
            continue
        layer_index = int(layer["layer_index"])
        source_shapes = layer["input_shape_nchw"]
        source_scales = layer["input_scales"]
        source_ranges = layer["route_source_channel_ranges"]
        output_shape = layer["output_shape_nchw"]
        target_scale = max(source_scales)
        output_channels = output_shape[1]
        layer_vectors = []
        for case_index, rule in enumerate(ROUTE_DIRECTED_RULES):
            row = _select_index(rule["spatial"], output_shape[2])
            col = _select_index(rule["spatial"], output_shape[3])
            source_values: list[list[int]] = []
            selected_channels: list[list[int]] = []
            for source_index, (shape, channel_range) in enumerate(zip(source_shapes, source_ranges)):
                start, end = channel_range
                channels = list(range(start, end))
                selected_channels.append(channels)
                source_values.append([0] * len(channels))
            profile = rule["profile"]
            if profile == "positive_extreme":
                source_values = [[127] * len(values) for values in source_values]
            elif profile == "negative_extreme":
                source_values = [[-127] * len(values) for values in source_values]
            elif profile == "alternating_extremes_start_negative":
                source_values = [_repeat_pattern([-127, 127], len(values)) for values in source_values]
            elif profile in {"first_source_positive_extreme", "last_source_positive_extreme"}:
                selected_source = 0 if profile.startswith("first") else len(source_values) - 1
                source_values[selected_source] = [127] * len(source_values[selected_source])
            elif profile in {
                "first_output_channel_positive_extreme",
                "last_output_channel_positive_extreme",
                "first_output_channel_negative_extreme",
                "last_output_channel_negative_extreme",
            }:
                is_first = profile.startswith("first")
                value = -127 if "negative" in profile else 127
                output_channel = 0 if is_first else output_channels - 1
                remaining = output_channel
                for source_index, values in enumerate(source_values):
                    if remaining < len(values):
                        values[remaining] = value
                        break
                    remaining -= len(values)
            elif profile == "distinct_source_constants":
                source_values = [[source_index + 1] * len(values) for source_index, values in enumerate(source_values)]
            elif profile == "scale_conversion_or_identity_fallback":
                conversion_source_index = next(
                    (index for index, scale in enumerate(source_scales) if scale != target_scale),
                    None,
                )
                if conversion_source_index is not None:
                    source_values = [[0] * len(values) for values in source_values]
                    source_values[conversion_source_index] = [-127] * len(source_values[conversion_source_index])
                else:
                    source_values = [_repeat_pattern([-1, 1], len(values)) for values in source_values]
            elif profile == "positive_unit":
                source_values = [[1] * len(values) for values in source_values]
            elif profile == "negative_unit":
                source_values = [[-1] * len(values) for values in source_values]
            elif profile == "last_output_channel_negative_extreme":
                source_values[-1][-1] = -127
            elif profile != "zero":
                raise DeliveryError(f"未知 route 定向输入模式: {profile}")

            requantized = [
                [_requantize_route_scalar(value, scale, target_scale) for value in values]
                for values, scale in zip(source_values, source_scales)
            ]
            concatenated = [value for values in requantized for value in values]
            if len(concatenated) != output_channels:
                raise DeliveryError(f"route 层 {layer_index} 定向向量输出通道数错误")
            layer_vectors.append({
                "case_index": case_index,
                "case_name": route_names[case_index],
                "profile": profile,
                "scale_rule_applied": "unlike_source_scales_requantize" if any(scale != source_scales[0] for scale in source_scales[1:]) else "equal_source_scales_identity",
                "scale_conversion_source_index": conversion_source_index if profile == "scale_conversion_or_identity_fallback" else None,
                "scale_conversion_input_value_int8": -127 if profile == "scale_conversion_or_identity_fallback" and conversion_source_index is not None else None,
                "target_spatial_yx": [row, col],
                "target_scale": target_scale,
                "source_tensors": [
                    {
                        "tensor_index": tensor_index,
                        "input_shape_nchw": shape,
                        "input_scale": scale,
                        "selected_source_channel_range": channel_range,
                        "selected_source_channels": channels,
                        "source_values_int8": values,
                        "requantized_values_int8": converted,
                    }
                    for tensor_index, shape, scale, channel_range, channels, values, converted in zip(
                        layer["input_tensor_indices"], source_shapes, source_scales, source_ranges,
                        selected_channels, source_values, requantized,
                    )
                ],
                "output_channel_values_int8": concatenated,
            })
        vectors["route"][str(layer_index)] = layer_vectors

    pool_names = case_names["maxpool"]
    for layer in layers:
        if layer["op"] != "maxpool":
            continue
        layer_index = int(layer["layer_index"])
        _, channels, input_height, input_width = layer["input_shape_nchw"]
        _, output_channels, output_height, output_width = layer["output_shape_nchw"]
        kernel_height, kernel_width = layer["kernel_hw"]
        stride_y, stride_x = layer["stride_hw"]
        if kernel_height * kernel_width != 4:
            raise DeliveryError(f"maxpool 层 {layer_index} 的定向 tap 目录要求四个窗口元素")
        origin_base_y, origin_base_x = layer["window_origin_yx_at_output_0"]
        layer_vectors = []
        for case_index, rule in enumerate(MAXPOOL_DIRECTED_RULES):
            channel = _select_index(rule["target"][0], output_channels)
            row = _select_index(rule["target"][1], output_height)
            col = _select_index(rule["target"][2], output_width)
            profile = rule["profile"]
            if profile == "zero":
                window_values = [0] * 4
            elif profile == "positive_extreme":
                window_values = [127] * 4
            elif profile == "negative_extreme":
                window_values = [-127] * 4
            elif profile == "alternating_extremes_start_negative":
                window_values = [-127, 127, -127, 127]
            elif profile.startswith("positive_tap_"):
                active_tap = int(profile.rsplit("_", 1)[1])
                window_values = [-127] * 4
                window_values[active_tap] = 127
            elif profile.startswith("negative_tap_"):
                active_tap = int(profile.rsplit("_", 1)[1])
                window_values = [127] * 4
                window_values[active_tap] = -127
            elif profile == "first_output_coordinate_marker":
                window_values = [1, 2, 3, 4]
            elif profile == "last_output_coordinate_marker":
                window_values = [-1, -2, -3, -4]
            elif profile == "first_channel_small_increasing":
                window_values = [11, 12, 13, 14]
            elif profile == "last_channel_small_decreasing":
                window_values = [-11, -12, -13, -14]
            else:
                raise DeliveryError(f"未知 maxpool 定向输入模式: {profile}")
            window_origin = [origin_base_y + row * stride_y, origin_base_x + col * stride_x]
            source_values: list[int | None] = []
            candidates: list[int] = []
            coordinates: list[list[int] | None] = []
            for tap_index, value in enumerate(window_values):
                tap_y, tap_x = divmod(tap_index, kernel_width)
                input_y, input_x = window_origin[0] + tap_y, window_origin[1] + tap_x
                in_bounds = 0 <= input_y < input_height and 0 <= input_x < input_width
                coordinates.append([channel, input_y, input_x] if in_bounds else None)
                source_values.append(value if in_bounds else None)
                candidates.append(value if in_bounds else int(layer["pad_value_int8"]))
            layer_vectors.append({
                "case_index": case_index,
                "case_name": pool_names[case_index],
                "target_output_nchw": [0, channel, row, col],
                "input_window_origin_yx": window_origin,
                "input_coordinates_cyx": coordinates,
                "source_window_values_int8": source_values,
                "candidate_values_int8": candidates,
                "pad_value_int8": layer["pad_value_int8"],
                "expected_output_int8": max(candidates),
                "window_order": "kernel_y then kernel_x; row-major tap index=kernel_y*kernel_width+kernel_x",
            })
        vectors["maxpool"][str(layer_index)] = layer_vectors

    upsample_names = case_names["upsample"]
    for layer in layers:
        if layer["op"] != "upsample":
            continue
        layer_index = int(layer["layer_index"])
        _, channels, input_height, input_width = layer["input_shape_nchw"]
        _, output_channels, output_height, output_width = layer["output_shape_nchw"]
        stride = int(layer["stride"])
        layer_vectors = []
        for case_index, rule in enumerate(UPSAMPLE_DIRECTED_RULES):
            profile = rule["profile"]
            channel = _select_index(rule["output"][0], output_channels)
            output_row = _select_index(rule["output"][1], output_height)
            output_col = _select_index(rule["output"][2], output_width)
            source_row, source_col = output_row // stride, output_col // stride
            value = int(rule["value"])
            source_rule = "single_marker_else_zero"
            target_outputs = [[0, channel, output_row, output_col]]
            if profile in {"zero_source", "positive_extreme_source", "negative_extreme_source", "alternating_source_first_element"}:
                source_rule = "flat_nchw_even=-127_odd=+127" if profile == "alternating_source_first_element" else profile
            if "pair" in rule:
                if rule["pair"] == "horizontal":
                    target_outputs = [[0, channel, output_row, output_col], [0, channel, output_row, output_col + 1]]
                else:
                    target_outputs = [[0, channel, output_row, output_col], [0, channel, output_row + 1, output_col]]
                source_rule = "single_marker_else_zero"
            queries = []
            for target in target_outputs:
                _, query_channel, query_y, query_x = target
                query_source_y, query_source_x = query_y // stride, query_x // stride
                queries.append({
                    "output_nchw": target,
                    "source_cyx": [query_channel, query_source_y, query_source_x],
                    "source_value_int8": value,
                    "expected_output_int8": value,
                })
            layer_vectors.append({
                "case_index": case_index,
                "case_name": upsample_names[case_index],
                "profile": profile,
                "source_tensor_rule": source_rule,
                "source_tensor_default_int8": 0,
                "stride": stride,
                "queries": queries,
                "all_queries_share_source_coordinate": len({tuple(item["source_cyx"]) for item in queries}) == 1,
            })
        vectors["upsample"][str(layer_index)] = layer_vectors

    yolo_names = case_names["yolo"]
    for layer in layers:
        if layer["op"] != "yolo":
            continue
        layer_index = int(layer["layer_index"])
        _, channels, height, width = layer["output_shape_nchw"]
        source_layer = layers[layer["output_tensor_index"]]
        layer_vectors = []
        for case_index, rule in enumerate(YOLO_DIRECTED_RULES):
            queries = []
            for anchor, entry, row_selector, col_selector in rule["queries"]:
                row = _select_index(row_selector, height)
                col = _select_index(col_selector, width)
                channel = anchor * 10 + entry
                if channel >= channels:
                    raise DeliveryError(f"YOLO 层 {layer_index} 定向查询通道越界")
                offset = (channel * height + row) * width + col
                queries.append({
                    "anchor_local": anchor,
                    "entry": entry,
                    "channel": channel,
                    "row": row,
                    "column": col,
                    "tensor_byte_offset": offset,
                    "tensor_byte_address": layer["tensor_address"] + offset,
                    "source_tensor_byte_address": source_layer["tensor_address"] + offset,
                })
            layer_vectors.append({
                "case_index": case_index,
                "case_name": yolo_names[case_index],
                "source_convolution_layer_index": source_layer["layer_index"],
                "tensor_shape_nchw": layer["output_shape_nchw"],
                "head_base_address": layer["tensor_address"],
                "source_convolution_base_address": source_layer["tensor_address"],
                "zero_copy_alias": layer["tensor_address"] == source_layer["tensor_address"],
                "queries": queries,
                "contiguous_channel_boundary": len(queries) == 2 and queries[1]["tensor_byte_address"] - queries[0]["tensor_byte_address"] == 1,
                "tail_byte_query": len(queries) == 1 and queries[0]["tensor_byte_offset"] == layer["tensor_length_bytes"] - 1,
            })
        vectors["yolo"][str(layer_index)] = layer_vectors
    return vectors


def _requantize_route_scalar(value: int, source_scale: float, target_scale: float) -> int:
    """按 half-away-from-zero 与对称 INT8 饱和重定标一个 route 值。"""

    scaled = value * source_scale / target_scale
    rounded = math.floor(abs(scaled) + 0.5) * (-1 if scaled < 0.0 else 1)
    return min(INT8_MAX, max(INT8_MIN, rounded))


def validate_address_map(layers: list[dict[str, Any]], address_map: dict[str, Any]) -> None:
    """验证固定逻辑地址空间不越界，且仅 YOLO 视图允许重叠。"""

    address_limit = 1 << 32
    input_buffer = address_map["input"]
    weight_buffer = address_map["weight_package"]
    workspace = address_map["feature_workspace"]
    ranges = [
        ("input", input_buffer["address"], input_buffer["length_bytes"]),
        ("weights", weight_buffer["address"], weight_buffer["length_bytes"]),
        ("features", workspace["base_address"], workspace["end_address_exclusive"] - workspace["base_address"]),
    ]
    for name, start, length in ranges:
        if start < 0 or length <= 0 or start + length > address_limit:
            raise DeliveryError(f"{name} 地址范围超出 32 位字节地址空间")
    ordered_ranges = sorted((start, start + length, name) for name, start, length in ranges)
    if any(left[1] > right[0] for left, right in zip(ordered_ranges, ordered_ranges[1:])):
        raise DeliveryError("输入、权重和特征地址范围发生重叠")

    feature_start = workspace["base_address"]
    feature_end = workspace["end_address_exclusive"]
    allocations: dict[tuple[int, int], int] = {}
    for layer in layers:
        address = layer["tensor_address"]
        length = layer["tensor_length_bytes"]
        end = address + length
        if address < feature_start or length <= 0 or end > feature_end:
            raise DeliveryError(f"第 {layer['layer_index']} 层张量越出特征地址范围")
        if layer["op"] == "yolo":
            source_index = layer["output_tensor_index"]
            source = layers[source_index]
            if (address, length) != (source["tensor_address"], source["tensor_length_bytes"]):
                raise DeliveryError(f"YOLO 第 {layer['layer_index']} 层没有与来源卷积共享地址")
        else:
            if address % workspace["alignment_bytes"]:
                raise DeliveryError(f"第 {layer['layer_index']} 层张量起始地址未对齐")
            key = (address, end)
            if key in allocations:
                raise DeliveryError("两个非视图特征张量意外共享地址")
            allocations[key] = layer["layer_index"]
    allocated = sorted((start, end, index) for (start, end), index in allocations.items())
    if any(left[1] > right[0] for left, right in zip(allocated, allocated[1:])):
        raise DeliveryError("不同特征张量地址区间发生重叠")


def xorshift32(seed: int, count: int) -> bytes:
    """按冻结的 xorshift32 规则生成确定性 RGB 样本字节。"""

    state = seed & 0xFFFFFFFF
    if state == 0:
        raise DeliveryError("xorshift32 不接受零种子")
    output = bytearray(count)
    for index in range(count):
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= state >> 17
        state ^= (state << 5) & 0xFFFFFFFF
        output[index] = state & 0xFF
    return bytes(output)


def synthetic_cases(seed: int) -> list[dict[str, Any]]:
    """列出全网输入强度边界和可重现的高变化样本。"""

    width = height = 416
    pixel_count = width * height
    black = bytes(pixel_count * 3)
    white = bytes([255]) * (pixel_count * 3)
    checker = bytearray(pixel_count * 3)
    for y in range(height):
        for x in range(width):
            value = 255 if (x + y) & 1 else 0
            offset = (y * width + x) * 3
            checker[offset:offset + 3] = bytes([value]) * 3
    random = xorshift32(seed, pixel_count * 3)
    samples = []
    for name, raw, tags in (
        ("synthetic_black", black, ["input_extreme_min"]),
        ("synthetic_white", white, ["input_extreme_max"]),
        ("synthetic_checkerboard", bytes(checker), ["input_extreme_transition"]),
        ("synthetic_xorshift32", random, ["input_seeded_random"]),
    ):
        rgb = np.frombuffer(raw, dtype=np.uint8).reshape(height, width, 3)
        input_tensor = preprocess_rgb_chw_int8(rgb)
        samples.append({
            "sample_id": name, "source": "synthetic_rgb416", "width": width, "height": height,
            "rgb_sha256": sha256_bytes(raw), "pl_input_sha256": sha256_bytes(input_tensor.tobytes(order="C")),
            "coverage_tags": tags,
        })
    return samples


def build_image_samples(manifest_path: Path, calibration_path: Path, data_root: Path) -> list[dict[str, Any]]:
    """从冻结 test manifest 和校准清单生成不含图像本体的固定输入 ID。"""

    if sha256_file(manifest_path) != EXPECTED_MANIFEST_SHA256:
        raise DeliveryError("官方 manifest SHA 与 D6 冻结值不符")
    if sha256_file(calibration_path) != EXPECTED_CALIBRATION_SHA256:
        raise DeliveryError("校准清单 SHA 与 D2 冻结值不符")
    selected: dict[str, list[dict[str, Any]]] = {name: [] for name in EXPECTED_CLASSES}
    all_test_rows: list[tuple[str, dict[str, Any]]] = []
    with manifest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"image", "label", "split"}
        if not required.issubset(reader.fieldnames or []):
            raise DeliveryError("官方 manifest 缺少 image/label/split 字段")
        for row in reader:
            if row["split"] != "test":
                continue
            parts = Path(row["image"]).parts
            class_name = parts[1] if len(parts) >= 3 and parts[0] == "dataset" else ""
            if class_name not in selected:
                continue
            all_test_rows.append((class_name, row))
            if len(selected[class_name]) < 20:
                selected[class_name].append(row)
    if any(len(rows) != 20 for rows in selected.values()):
        raise DeliveryError("官方 test manifest 无法为五类各选出 20 张")

    samples: list[dict[str, Any]] = []
    selected_images = {row["image"] for rows in selected.values() for row in rows}
    multi_ground_truth_rows: list[tuple[str, dict[str, Any]]] = []
    for class_id, class_name in enumerate(EXPECTED_CLASSES):
        for row in selected[class_name]:
            image_path = data_root / Path(row["image"])
            label_path = data_root / Path(row["label"])
            if not image_path.is_file() or not label_path.is_file():
                raise DeliveryError(f"固定样本图片或标签缺失: {row['image']}")
            image_info = image_metadata(image_path)
            labels = []
            for line in label_path.read_text(encoding="utf-8").splitlines():
                parts = line.split()
                if not parts:
                    continue
                if len(parts) != 5:
                    raise DeliveryError(f"YOLO 标签列数不是 5: {row['label']}")
                label = [int(parts[0]), *[float(value) for value in parts[1:]]]
                if label[0] != class_id or not all(math.isfinite(value) for value in label[1:]):
                    raise DeliveryError(f"固定 test 样本标签类别或坐标异常: {row['label']}")
                labels.append(label)
            tags = [f"class:{class_name}"]
            if len(labels) > 1:
                tags.append("multi_ground_truth_boxes")
            for _class, cx, cy, box_w, box_h in labels:
                if min(cx - box_w / 2, cy - box_h / 2, 1 - cx - box_w / 2, 1 - cy - box_h / 2) <= 0.02:
                    tags.append("boundary_ground_truth_box")
                if min(box_w, box_h) <= 0.1:
                    tags.append("small_ground_truth_box")
            samples.append({
                "sample_id": f"test_{class_name}_{len(samples):03d}",
                "source": "official_hagrid_test",
                "relative_image": row["image"],
                "relative_label": row["label"],
                **image_info,
                "image_sha256": sha256_file(image_path),
                "label_sha256": sha256_file(label_path),
                "pl_input_sha256": preprocess_file_sha256(image_path),
                "ground_truth_yolo": labels,
                "coverage_tags": sorted(set(tags)),
            })

    for class_name, row in all_test_rows:
        if row["image"] in selected_images:
            continue
        label_path = data_root / Path(row["label"])
        if not label_path.is_file():
            continue
        label_lines = [line for line in label_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(label_lines) > 1:
            multi_ground_truth_rows.append((class_name, row))
    if not multi_ground_truth_rows:
        raise DeliveryError("官方 test manifest 没有可绑定的多 GT 固定网络输入")
    for class_name, row in multi_ground_truth_rows:
        image_path = data_root / Path(row["image"])
        label_path = data_root / Path(row["label"])
        if not image_path.is_file() or not label_path.is_file():
            raise DeliveryError(f"多 GT 固定样本图片或标签缺失: {row['image']}")
        image_info = image_metadata(image_path)
        class_id = EXPECTED_CLASSES.index(class_name)
        labels = []
        for line in label_path.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if not parts:
                continue
            if len(parts) != 5:
                raise DeliveryError(f"YOLO 标签列数不是 5: {row['label']}")
            label = [int(parts[0]), *[float(value) for value in parts[1:]]]
            if label[0] != class_id or not all(math.isfinite(value) for value in label[1:]):
                raise DeliveryError(f"多 GT 固定 test 样本标签类别或坐标异常: {row['label']}")
            labels.append(label)
        if len(labels) < 2:
            raise DeliveryError(f"多 GT 固定样本标签少于两框: {row['label']}")
        tags = [f"class:{class_name}", "multi_ground_truth_boxes"]
        for _class, cx, cy, box_w, box_h in labels:
            if min(cx - box_w / 2, cy - box_h / 2, 1 - cx - box_w / 2, 1 - cy - box_h / 2) <= 0.02:
                tags.append("boundary_ground_truth_box")
            if min(box_w, box_h) <= 0.1:
                tags.append("small_ground_truth_box")
        samples.append({
            "sample_id": f"test_{class_name}_{len(samples):03d}",
            "source": "official_hagrid_test_multibox",
            "relative_image": row["image"],
            "relative_label": row["label"],
            **image_info,
            "image_sha256": sha256_file(image_path),
            "label_sha256": sha256_file(label_path),
            "pl_input_sha256": preprocess_file_sha256(image_path),
            "ground_truth_yolo": labels,
            "coverage_tags": sorted(set(tags)),
        })

    calibration_lines = calibration_path.read_text(encoding="utf-8").splitlines()
    negative_paths = [Path(line.replace("/", "\\")) for line in calibration_lines if "/user_no_hand/" in line.replace("\\", "/")]
    if len(negative_paths) != 3:
        raise DeliveryError("冻结校准清单中的 user_no_hand 数量不是 3")
    for index, listed_path in enumerate(negative_paths, start=1):
        image_path = Path(str(listed_path))
        label_path = data_root / "labels" / "user_no_hand" / f"20260915_friend_{index:03d}.txt"
        if not image_path.is_file() or not label_path.is_file() or label_path.read_text(encoding="utf-8").strip():
            raise DeliveryError("批准的 no_hand 图片/空标签绑定无效")
        samples.append({
            "sample_id": f"approved_no_hand_{index:03d}",
            "source": "approved_train_negative_from_calibration_list",
            "relative_image": image_path.relative_to(data_root).as_posix(),
            "relative_label": label_path.relative_to(data_root).as_posix(),
            **image_metadata(image_path),
            "image_sha256": sha256_file(image_path),
            "label_sha256": sha256_file(label_path),
            "pl_input_sha256": preprocess_file_sha256(image_path),
            "ground_truth_yolo": [],
            "coverage_tags": ["empty_ground_truth", "no_hand_negative"],
        })
    return samples


def write_new_json(path: Path, value: dict[str, Any]) -> None:
    """以 UTF-8 创建新 JSON；拒绝覆盖已存在文件。"""

    if path.exists():
        raise DeliveryError(f"输出已存在，为避免覆盖拒绝写入: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    """校验冻结模型绑定并生成阶段 2A 交付清单。"""

    parser = argparse.ArgumentParser(description="生成 tiny416 阶段 2A 模型交付与固定样本清单")
    parser.add_argument("--cfg", type=Path, default=Path(r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny416_formal_r2\configs\gesture_yolov4_tiny_416_d8_formal.cfg"))
    parser.add_argument("--weights", type=Path, default=Path(r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d8_tiny416_formal_r2\checkpoints\gesture_yolov4_tiny_416_d8_formal_6000.weights"))
    parser.add_argument("--package", type=Path, default=Path(r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_tiny416_int8_weight_r2\gesture_yolov4_tiny_416_int8_weights.gf8"))
    parser.add_argument("--manifest", type=Path, default=Path(r"D:\FPGA_Data\HaGRIDv2\manifest.csv"))
    parser.add_argument("--data-root", type=Path, default=Path(r"D:\FPGA_Data\HaGRIDv2"))
    parser.add_argument("--calibration-list", type=Path, default=Path(r"D:\FPGA_Data\HaGRIDv2\darknet_inputs\runs\s1_t02_d2_calibration_r2\calibration.list"))
    parser.add_argument("--output-dir", type=Path, default=ROOT / "report" / "evidence" / "S2A-T01")
    args = parser.parse_args(argv)

    cfg_hash, weights_hash, package_hash = (sha256_file(args.cfg), sha256_file(args.weights), sha256_file(args.package))
    if cfg_hash != EXPECTED_CFG_SHA256 or weights_hash != EXPECTED_WEIGHTS_SHA256 or package_hash != EXPECTED_PACKAGE_SHA256:
        raise DeliveryError("cfg、Darknet weights 或 GF8 package SHA 与阶段一冻结绑定不一致")
    weight_evidence_path = EVIDENCE / "20260922_s1_t02_d2_tiny416_int8_weight_r2.json"
    activation_path = EVIDENCE / "20260922_s1_t02_d2_tiny416_activation_calibration_r1.json"
    forward_path = EVIDENCE / "20260922_s1_t02_d2_tiny416_int8_forward_r2.json"
    metric_policy_path = EVIDENCE / "20260922_s1_t02_d6_metric_policy_r2.json"
    d2_reference_path = ROOT / "verification" / "s1_t02_d2_numeric_reference.py"
    d2_forward_path = ROOT / "verification" / "s1_t02_d2_int8_forward.py"
    d6_metrics_path = ROOT / "verification" / "s1_t02_d6_detection_metrics.py"
    d9_decoder_path = ROOT / "verification" / "s1_t02_d9_yolo_decode.py"
    activation_report = json.loads(activation_path.read_text(encoding="utf-8"))
    weight_report = json.loads(weight_evidence_path.read_text(encoding="utf-8"))
    forward_report = json.loads(forward_path.read_text(encoding="utf-8"))
    if forward_report["inputs"]["weight_report"]["sha256"] != sha256_file(weight_evidence_path):
        raise DeliveryError("INT8 forward 没有绑定当前 weight report")
    if forward_report["inputs"]["activation_report"]["sha256"] != sha256_file(activation_path):
        raise DeliveryError("INT8 forward 没有绑定当前 activation report")
    if weight_report["package"]["sha256"] != package_hash:
        raise DeliveryError("GF8 package 与权重量化报告绑定不一致")
    layers, address_map, package_layers = read_network(args.cfg, activation_report, args.package)
    validate_address_map(layers, address_map)
    sample_seed = 20260922
    dataset_samples = build_image_samples(args.manifest, args.calibration_list, args.data_root)
    samples = dataset_samples + synthetic_cases(sample_seed)
    directed_case_names = {
        "int8_mac": ["all-zero products and bias", "four sign combinations at magnitude 127", "alternating maximal positive products", "alternating maximal negative products", "only first product nonzero", "only last product nonzero", "bias INT32_MAX with zero products", "bias INT32_MIN with zero products", "exact INT32_MAX result", "INT32_MAX plus one overflow", "exact INT32_MIN result", "INT32_MIN minus one overflow", "positive cancellation order", "negative cancellation order", "K=1 signed product", "K=maximum model reduction length"],
        "convolutional": ["zero activations", "all +127 activations", "all -127 activations", "alternating activations", "first reduction tap only", "last reduction tap only", "input channel 0 at first valid point of first output receptive field", "last input channel at last valid point of final output receptive field", "kernel center tap at first output point when kernel is odd, otherwise first tap", "kernel center tap at last output point when kernel is odd, otherwise last tap", "output channel 0 at output coordinate 0,0", "last output channel at final output coordinate", "bias-only with zero activations", "alternating signs by reduction index", "first row-major output point", "last row-major output point"],
        "maxpool": ["all-zero candidate window", "all +127 candidate window", "all -127 candidate window", "alternating -127/+127 candidates", "+127 only at kernel tap 0", "+127 only at kernel tap 1", "+127 only at kernel tap 2", "+127 only at kernel tap 3", "-127 only at kernel tap 0", "-127 only at kernel tap 1", "-127 only at kernel tap 2", "-127 only at kernel tap 3", "first valid output coordinate", "last valid output coordinate", "channel 0 at first output coordinate", "last channel at last output coordinate"],
        "route": ["all-zero source values", "all +127 source values", "all -127 source values", "alternating source values", "source 0 nonzero and others zero", "last source nonzero and others zero", "first channel preserved", "last channel preserved", "cfg reference order preserved with distinct source constants", "actual unlike source scales or equal-scale identity fallback", "all source values +1", "all source values -1", "source 0 at first spatial coordinate", "last source at final spatial coordinate", "first output channel", "last output channel"],
        "upsample": ["first source element", "last source element", "top-left replication", "top-right replication", "bottom-left replication", "bottom-right replication", "horizontal repeated pair", "vertical repeated pair", "all-zero source", "all +127 source", "all -127 source", "alternating source values", "first channel", "last channel", "first output coordinate", "last output coordinate"],
        "yolo": ["anchor0 entry0 row0 col0", "anchor0 entry9 row0 col0", "anchor1 entry0 row0 col0", "anchor2 entry9 last row last col", "row0 col-mid", "last row col-mid", "row-mid col0", "row-mid last col", "first source byte", "last source byte", "channel0 row0 col0", "channel29 row0 col0", "head13 source alias", "head26 source alias", "channel29 to next anchor channel boundary", "tensor tail address"],
    }
    if any(len(names) != 16 for names in directed_case_names.values()):
        raise DeliveryError("每个算子的定向样例名必须恰好有 16 项")
    directed_case_vectors = build_directed_case_vectors(layers, package_layers, directed_case_names)
    layer_index = {
        "generator": {"path": str(Path(__file__).resolve().relative_to(ROOT)), "sha256": sha256_file(Path(__file__).resolve())},
        "cfg": {"path": str(args.cfg.resolve()), "sha256": cfg_hash, "bytes": args.cfg.stat().st_size},
        "darknet_weights": {"path": str(args.weights.resolve()), "sha256": weights_hash, "bytes": args.weights.stat().st_size},
        "gf8_package": {"path": str(args.package.resolve()), "sha256": package_hash, "bytes": args.package.stat().st_size, "format": "GFINT8W1 v1"},
        "activation_report": {"path": str(activation_path.relative_to(ROOT)), "sha256": sha256_file(activation_path)},
        "int8_forward_report": {"path": str(forward_path.relative_to(ROOT)), "sha256": sha256_file(forward_path), "existing_sample_count": forward_report["sample_count"], "status": forward_report["status"]},
        "d2_numeric_reference": {"path": str(d2_reference_path.relative_to(ROOT)), "sha256": sha256_file(d2_reference_path)},
        "d2_int8_forward_reference": {"path": str(d2_forward_path.relative_to(ROOT)), "sha256": sha256_file(d2_forward_path)},
        "input_preprocess_reference": {"path": str(d2_reference_path.relative_to(ROOT)), "callable": "preprocess_rgb_uint8_to_chw_int8", "sha256": sha256_file(d2_reference_path), "authority": "named as the preprocessing numerical reference by S1-T02-D2; D2 int8-forward float32 loader is bound as forward evidence but is not the PL input hash oracle"},
        "d6_metrics_reference": {"path": str(d6_metrics_path.relative_to(ROOT)), "sha256": sha256_file(d6_metrics_path)},
        "d6_metric_policy": {"path": str(metric_policy_path.relative_to(ROOT)), "sha256": sha256_file(metric_policy_path)},
        "d9_decoder_reference": {"path": str(d9_decoder_path.relative_to(ROOT)), "sha256": sha256_file(d9_decoder_path)},
        "d9_fixture_source": {"path": "verification/test_s1_t02_d9_yolo_decode.py", "source_commit": BASELINE_COMMIT, "sha256": BASELINE_D9_TEST_SHA256, "fixture_names": ["test_same_class_overlap_is_suppressed_but_other_class_is_kept", "test_output_limit_is_fifteen", "test_empty_and_below_threshold_inputs_return_no_predictions"]},
        "official_test_manifest": {"path": str(args.manifest.resolve()), "sha256": sha256_file(args.manifest)},
        "calibration_list": {"path": str(args.calibration_list.resolve()), "sha256": sha256_file(args.calibration_list), "sample_count": 512},
        "preprocess_runtime": {"python": sys.version.split()[0], "numpy": np.__version__, "opencv": cv2.__version__, "image_decoder": "cv2.imdecode(IMREAD_COLOR); BGR channels reversed to RGB", "tensor_digest": "SHA-256 over contiguous CHW signed INT8 two's-complement raw bytes"},
        "input_contract": {"owner": "PS/2A testbench prepares the input; PL receives a complete preprocessed INT8 tensor", "rgb": True, "image_decoder": "OpenCV imdecode(IMREAD_COLOR), BGR to RGB", "preprocess_oracle": "verification/s1_t02_d2_numeric_reference.py::preprocess_rgb_uint8_to_chw_int8", "letterbox": "D2 endpoint-aligned bilinear; integer-truncated dimensions; top-left floor pad", "layout": "contiguous CHW", "normalization": "pixel/255", "quantization": "round_half_away(normalized/(1/127)); saturate [-127,127]", "input_scale": INPUT_SCALE, "pad_value_rgb": 128, "tensor_bytes": 519168, "input_tensor_hash": "SHA-256 over raw contiguous two's-complement INT8 CHW bytes"},
        "quantization_contract": {"weight_quantization": "per_output_channel symmetric INT8", "activation_scale": "per cfg convolution output tensor from 512-image approved train calibration", "bias": "BN folded; round_half_away(fused_bias/(input_scale*weight_scale)) into INT32 accumulator", "accumulator": "INT32 result with independent exact INT64 audit; any signed INT32 accumulation overflow aborts with ACCUMULATOR_OVERFLOW and never wraps or saturates", "rounding": "half_away_from_zero", "activation_order": "linear/leaky(0.1) before output requantization", "saturation": [-127, 127], "route_scale": "all inputs requantized to largest source scale before channel concat"},
        "classes": [{"class_id": index, "name": name} for index, name in enumerate(EXPECTED_CLASSES)],
        "weight_report": {"path": str(weight_evidence_path.relative_to(ROOT)), "sha256": sha256_file(weight_evidence_path)},
    }
    manifest = {
        "schema_version": "gestureforge_s2a_model_manifest_v1",
        "created_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "status": "G0_FROZEN",
        "scope": "2A tiny416 PL simulation specification; no RTL result, full-network golden output, synthesis, or board claim",
        "model": {"model_id": "tiny416", "architecture": "YOLOv4-tiny", "input_wh": [416, 416], "classes": len(EXPECTED_CLASSES)},
        "bindings": layer_index,
        "address_map": address_map,
        "control_protocol": {
            "interface": "2A simulation CSR; not an AXI-Lite pin-level contract",
            "signals": ["csr_valid", "csr_ready", "csr_write", "csr_addr[7:0]", "csr_wdata[31:0]", "csr_rdata[31:0]"],
            "port_roles": {"ps_to_pl": ["csr_valid", "csr_write", "csr_addr", "csr_wdata"], "pl_to_ps": ["csr_ready", "csr_rdata"]},
            "handshake": "single outstanding transfer accepted on rising edge when csr_valid && csr_ready; csr_rdata is the read value on that same cycle",
            "ready": "csr_ready is high outside hard reset; software must change/deassert valid after each accepted transfer",
            "locked_write": "configuration writes are ignored unless PS owns buffers and busy/done/error are all clear",
            "start": "accepted only from idle after argument validation; busy=1 and PL buffer ownership begin on acceptance edge",
            "argument_errors": {"wrong_input_or_weight_address": "BAD_RANGE", "wrong_input_or_weight_length": "BAD_LENGTH", "zero_timeout": "BAD_ARGUMENT", "signed_int32_accumulator_overflow": "ACCUMULATOR_OVERFLOW"},
            "error_codes": {"0": "NONE", "1": "BAD_ARGUMENT", "2": "BAD_RANGE", "3": "BAD_LENGTH", "4": "UNSUPPORTED_OP", "5": "TIMEOUT", "6": "INTERNAL", "7": "ACCUMULATOR_OVERFLOW"},
            "status": "done and error are mutually exclusive sticky bits; each remains set until its ACK bit or reset",
            "register_alignment": "csr_addr must be 32-bit aligned; unaligned/reserved reads return zero and writes are ignored; writes to RO registers are ignored",
            "register_map": [
                {"offset": "0x00", "name": "CMD", "access": "W1P", "bits": {"0": "start", "1": "soft_reset"}, "reset": 0},
                {"offset": "0x04", "name": "STATUS", "access": "RO", "bits": {"0": "busy", "1": "done", "2": "error", "3": "pl_owns_buffers"}, "reset": 0},
                {"offset": "0x08", "name": "ERROR_CODE", "access": "RO", "reset": 0},
                {"offset": "0x0C", "name": "FRAME_ID", "access": "RW_IDLE", "reset": 0},
                {"offset": "0x10", "name": "INPUT_ADDR", "access": "RW_IDLE", "reset": INPUT_BASE},
                {"offset": "0x14", "name": "INPUT_BYTES", "access": "RW_IDLE", "reset": 519168},
                {"offset": "0x18", "name": "WEIGHT_ADDR", "access": "RW_IDLE", "reset": WEIGHT_BASE},
                {"offset": "0x1C", "name": "WEIGHT_BYTES", "access": "RW_IDLE", "reset": address_map["weight_package"]["length_bytes"]},
                {"offset": "0x20", "name": "FEATURE_BASE", "access": "RO", "reset": FEATURE_BASE},
                {"offset": "0x24", "name": "FEATURE_LIMIT", "access": "RO", "reset": address_map["feature_workspace"]["end_address_exclusive"]},
                {"offset": "0x28", "name": "TIMEOUT_CYCLES", "access": "RW_IDLE", "reset": 0},
                {"offset": "0x2C", "name": "HEAD13_ADDR", "access": "RO", "reset": address_map["heads"][0]["address"]},
                {"offset": "0x30", "name": "HEAD13_BYTES", "access": "RO", "reset": address_map["heads"][0]["length_bytes"]},
                {"offset": "0x34", "name": "HEAD26_ADDR", "access": "RO", "reset": address_map["heads"][1]["address"]},
                {"offset": "0x38", "name": "HEAD26_BYTES", "access": "RO", "reset": address_map["heads"][1]["length_bytes"]},
                {"offset": "0x3C", "name": "ACK", "access": "W1P", "bits": {"0": "clear_done", "1": "clear_error_and_error_code"}, "reset": 0},
            ],
            "soft_reset": "accepted CMD.soft_reset aborts current task and has priority over CMD.start in the same write",
            "timeout": "timeout_cycles must be nonzero; count rising edges after the accepted start edge; completion at the Nth edge wins over timeout, otherwise abort at that edge",
            "operator_completion_event": {
                "signals": ["operator_result_valid", "operator_error_code[2:0]"],
                "direction": "internal PL compute backend to PL CSR control FSM; not a PS-facing pin or CSR register",
                "handshake": "operator_result_valid is a one-cycle pulse sampled on a rising edge while busy; no backpressure; operator_error_code is stable on that edge",
                "success": "error_code=0 means all required feature/head writes completed and the result may be committed as done",
                "error": "known nonzero CSR error codes 1..7 are latched and abort the task; unknown nonzero values map to INTERNAL; error invalidates heads and returns buffer ownership to PS",
                "timeout_boundary": "a valid operator result on the Nth timeout edge wins over timeout; code 0 completes successfully and a nonzero code completes with error",
            },
            "priority": ["hard_reset", "soft_reset", "memory_or_argument_or_numeric_error", "completion", "timeout"],
            "ownership": "PL owns input/weight read and feature write access while busy; ownership returns to PS on done/error/reset",
        },
        "memory_protocol": {
            "signals": ["mem_valid", "mem_ready", "mem_write", "mem_addr[31:0]", "mem_wdata[31:0]", "mem_rstrb[3:0]", "mem_wstrb[3:0]", "mem_rdata[31:0]", "mem_error_code[2:0]"],
            "port_roles": {"pl_to_testbench_memory": ["mem_valid", "mem_write", "mem_addr", "mem_wdata", "mem_rstrb", "mem_wstrb"], "testbench_memory_to_pl": ["mem_ready", "mem_rdata", "mem_error_code"]},
            "handshake": "single outstanding word request; accepted when mem_valid && mem_ready; selected read lanes, mem_rdata and mem_error_code are valid on that same cycle",
            "alignment": "32-bit byte address; mem_addr[1:0] must be zero or the accepted request returns error code BAD_RANGE; little-endian byte lanes",
            "stability": "hold valid, address, direction, write data and both strobes stable until handshake or abort",
            "access": "while busy, PL may read input, weights and feature tensors; PL may write feature tensors; input and weights are read-only to PL",
            "idle_reset": "testbench memory model drives mem_ready low and mem_error_code=NONE while idle or reset; while PL is busy and owns buffers, it drives mem_ready according to the frozen stall schedule; a transfer requires mem_valid && mem_ready",
            "read_strobe": "read requires mem_rstrb != 0 and mem_wstrb == 0; selected lanes must each lie in one logical readable object; disabled lanes return zero",
            "write_strobe": "write requires mem_wstrb != 0 and mem_rstrb == 0; selected lanes must each lie in one logical feature tensor; disabled lanes have no side effect",
            "last_word": "partial read/write is required at an odd tensor tail; for a 5070-byte head the last aligned word uses lane mask 0011",
            "error_response_codes": {"0": "NONE; successful transfer", "1": "BAD_ARGUMENT; zero or conflicting strobes", "2": "BAD_RANGE; unaligned address, selected byte outside one allowed logical object/tensor, or write to input/weights", "6": "INTERNAL; memory-model storage failure"},
            "error_code_mapping": "memory model returns one 3-bit project error code with the handshake; PL copies codes 1, 2 or 6 to CSR ERROR_CODE and aborts; any other nonzero response is converted to INTERNAL; failed requests have no memory side effect",
            "range_error": "bad/zero/conflicting strobe returns BAD_ARGUMENT; selected bytes outside an allowed half-open logical object/tensor range or a write to input/weights returns BAD_RANGE; accepted errors abort",
            "reset_abort": "hard/soft reset or timeout cancels a pending request without a later memory side effect",
            "hardware_scope": "simulation-only logical memory contract; physical AXI, DMA and cache binding is deferred to approved 2B G0",
        },
        "layers": layers,
        "operators": sorted({layer["op"] for layer in layers}),
        "detection_postprocess": {"decoder_reference": "verification/s1_t02_d9_yolo_decode.py", "score_threshold": 0.25, "nms_iou": 0.45, "max_outputs": 15, "nms": "stable class-wise greedy; threshold then stable score sort then top 15 then NMS; suppress when same-class IoU >= 0.45", "coordinate_policy": "D2 integer-truncated resize and floor pad; clip finite positive raw xyxy to [0,1]; reject zero-area after clipping", "score": "sigmoid(objectness_logit)*sigmoid(class_logit)", "head_layout": "Darknet entry planes; [anchor,entry,row,col], entry=x,y,w,h,obj,class0..class4", "class_order": list(EXPECTED_CLASSES), "tie_order": "head order, row-major cell, anchor-local order, class_id; stable input order for equal scores", "comparison": {"head_bytes": "exact byte-for-byte INT8 equality", "frame_id_count_class_source_order": "exact equality", "score_absolute_tolerance": 1e-6, "coordinate_absolute_tolerance_normalized": 1e-6, "relative_tolerance": 0.0, "nms_decision_and_output_order": "exact equality", "frame_mismatch": "any count/order/class/source_order mismatch or any score/coordinate absolute error above tolerance"}},
        "operator_test_plan": {
            "scope": "each supported cfg operator layer plus the shared signed INT8 MAC primitive",
            "random_cases_per_model_layer": 1000,
            "directed_cases_per_model_layer": 16,
            "shared_primitive_random_cases": 1000,
            "shared_primitive_directed_cases": 16,
            "case_order": "operator name ASCII order including int8_mac; cfg layer_index ascending within each cfg operator, random case_index 0..999 then directed case_index 0..15; int8_mac is one shared instance; directed cases consume no PRNG state",
            "model_layer_geometry": "all per-layer vectors use the exact input/output shapes, kernel, stride, padding, activation, scales and channel counts in layers; no reduced geometry or synthetic parameter override is allowed",
            "prng": "one shared xorshift32 stream; state starts 20260922; per draw apply x=(x^(x<<13))&0xffffffff, x=x^(x>>17), x=(x^(x<<5))&0xffffffff; each selector uses next_u32 % bound; each INT8 operand uses (next_u32 & 255) % 255 - 127; signed INT32 bias is next_u32 interpreted two's complement",
            "tensor_order": "NCHW contiguous; convolution reduction and maxpool window order are input_channel then kernel_y then kernel_x; route inputs follow cfg reference order then channel; spatial coordinate is row-major",
            "int8_mac": "one shared dot-product primitive; 1000 cases total with K=conv_reduction_lengths[case_index % 21], where lengths are ordered by ascending cfg layer_index; consume K activation INT8 values, K weight INT8 values, then one signed INT32 bias; exact INT64 audit precedes checked signed INT32 accumulation",
            "convolutional": "1000 cases per cfg convolution layer; one output element per case; consume output_channel,row,col selectors then exactly K activation bytes in input_channel,kernel_y,kernel_x order, including taps later replaced by zero padding; use that layer's frozen GF8 weights, quantized bias and configured activation only; out-of-input taps contribute the layer padding value 0",
            "maxpool": "1000 cases per cfg maxpool layer; one output element per case; consume channel,row,col selectors then exactly kernel_h*kernel_w candidate values in kernel_y,kernel_x order; replace out-of-input candidates with -127; use the layer's frozen Darknet formula/origin and actual logical shape",
            "route": "1000 cases per cfg route layer; one spatial coordinate per case; consume y,x selectors, then source values in cfg reference order and channel order at that coordinate; requantize each source to max(input_scales) with half-away rounding and symmetric saturation before concatenation",
            "upsample": "1000 cases per cfg upsample layer; consume output_channel,y,x selectors and the one selected source INT8 value; expected coordinate is source[channel,floor(y/stride),floor(x/stride)]",
            "yolo": "1000 address-view queries per cfg YOLO layer; consume anchor_local,entry,row,col selectors in that order and verify byte address aliases source convolution NCHW offset",
            "selectors_and_values": "each bounded selector consumes one next_u32 and uses modulo bound; each random INT8 value consumes one next_u32 and maps (value&255)%255-127; one shared stream carries between cases and layers; no implicit reseed",
            "directed_vector_rules": {
                "count_semantics": "each case_index 0..15 is exactly one vector; directed_case_vectors is the normative materialized plan for every operator and shared int8_mac",
                "base_values": {"zero": 0, "positive_extreme": 127, "negative_extreme": -127, "alternating_extremes_start_negative": [-127, 127], "alternating_unit_start_negative": [-1, 1]},
                "selector_rules": {"first": 0, "last": "dimension-1", "middle": "dimension//2", "target_order": "NCHW [batch, channel, row, column]"},
                "convolution_materialization": "expanded vectors contain target_output_nchw, exact K activation bytes, the output channel's exact GFINT8W1 weight bytes in input_channel/kernel_y/kernel_x order, quantized INT32 bias, input/weight/output scales, activation and padding; source input outside this receptive field is zero; initialize accumulation from bias, add products in listed order and check signed INT32 after each addition",
                "int8_mac_materialization": "expanded vectors contain exact K, activation/weight arrays, bias, exact INT64 sum, first signed INT32 overflow product index and expected result; short patterns repeat from element zero to exactly K",
                "maxpool": "one kernel_h*kernel_w candidate window in kernel_y/kernel_x order; out-of-input candidates are -127; case-specific channel/row/column uses first=0,last=dimension-1,middle=floor(dimension/2)",
                "route_materialization": "expanded route vectors select source_channel_ranges before requantization; for groups>1 Darknet selects [group_id*C/groups:(group_id+1)*C/groups] from the single source tensor; source tensors remain in cfg reference order and selected channels remain ascending; each vector records selected indices, exact source bytes, per-source requantized bytes and concatenated output bytes",
                "route_scale_fallback": "case 9 selects the first cfg source whose scale differs from target=max(source_scales), fills only that source's selected channels with -127 and requires the requantized values to change; all other sources are zero; if all source scales equal target it uses the exact alternating [-1,1] identity-path vector and records equal_source_scales_identity",
                "upsample": "each query has exact target output and source coordinates, selected source INT8 value, expected output, pair queries, source-tensor fill rule and zero default; alternating source profile uses flat NCHW even index=-127, odd index=+127",
                "yolo": "one query is (anchor_local,entry,row,column); first=0,last=dimension-1,middle=floor(dimension/2); channel=anchor_local*10+entry and source address is base+(channel*height+row)*width+column",
            },
            "directed_cases_by_operator": directed_case_names,
            "directed_case_vectors": directed_case_vectors,
            "actual_cfg_edge_facts": {"maxpool_layers": {str(layer["layer_index"]): {"input_shape_nchw": layer["input_shape_nchw"], "kernel_hw": layer["kernel_hw"], "stride_hw": layer["stride_hw"], "darknet_padding_parameter": layer["darknet_padding_parameter"], "padding_lrtb_actual": layer["padding_lrtb_actual"], "window_origin_yx_at_output_0": layer["window_origin_yx_at_output_0"]} for layer in layers if layer["op"] == "maxpool"}, "conv_1x1_layers": [layer["layer_index"] for layer in layers if layer["op"] == "convolutional" and layer["kernel_hw"] == [1, 1]], "configured_activation_is_not_overridden": True},
            "separate_unit_fixtures": {
                "scope": "generic primitive checks only; not full cfg layers and not counted in per-model-layer random/directed totals",
                "conv_zero_padding_3x3": {"input_shape_nchw": [1, 1, 3, 3], "input_int8_nchw": [[[[1, 1, 1], [1, 1, 1], [1, 1, 1]]]], "weight_oihw": [[[[1, 1, 1], [1, 1, 1], [1, 1, 1]]]], "bias_int32": [0], "stride_hw": [1, 1], "padding_lrtb": [1, 1, 1, 1], "padding_value_int8": 0, "expected_accumulator_nchw": [[[[4, 6, 4], [6, 9, 6], [4, 6, 4]]]]},
                "maxpool_darknet_padding": {"input_shape_nchw": [1, 1, 4, 4], "input_int8_nchw": [[[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]]], "kernel_hw": [3, 3], "stride_hw": [1, 1], "darknet_padding_parameter": 2, "output_hw_formula": "(input_hw + padding - kernel_hw) // stride_hw + 1", "window_origin_yx_at_output_0": [-1, -1], "padding_lrtb_actual": [1, 1, 1, 1], "pad_value_int8": -127, "expected_output_nchw": [[[[6, 7, 8, 8], [10, 11, 12, 12], [14, 15, 16, 16], [14, 15, 16, 16]]]]},
                "requantize_half_away_and_saturate": {"scaled_values": [-128.5, -127.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 127.5, 128.5], "expected_int8": [-127, -127, -3, -2, -1, 1, 2, 3, 127, 127]},
                "leaky_relu_0_1": {"scaled_pre_activation": [-25.0, -15.0, -5.0, 0.0, 5.0, 15.0, 25.0], "expected_scaled_output": [-2.5, -1.5, -0.5, 0.0, 5.0, 15.0, 25.0], "expected_quantized_int8": [-3, -2, -1, 0, 5, 15, 25]},
                "route_half_away": {"source_scales": [0.25, 0.5], "target_scale": 0.5, "source0_values": [-5, -3, -1, 1, 3, 5], "source0_expected": [-3, -2, -1, 1, 2, 3], "source1_values": [1, 2, 3, 4, 5, 6], "source1_expected": [1, 2, 3, 4, 5, 6], "concat_order": "source0 then source1"},
                "upsample_nearest_repeat": {"input_shape_nchw": [1, 1, 2, 2], "input_int8_nchw": [[[[1, 2], [3, 4]]]], "stride": 2, "expected_output_nchw": [[[[1, 1, 2, 2], [1, 1, 2, 2], [3, 3, 4, 4], [3, 3, 4, 4]]]]}
            },
            "protocol_vectors": {
                "csr": {"ready_outside_hard_reset": 1, "stall_cycles": [], "transfer_rule": "CSR has no backpressure; PS presents valid for one accepted rising edge, then deasserts or changes the request before the next rising edge"},
                "memory_stall_cycles": [0, 1, 2, 7, 3],
                "memory_stall_repeat": "testbench memory model drives mem_ready low for exactly N cycles for each N in listed order on each memory request class; PL request fields stay stable, no transfer occurs during those cycles, acceptance occurs on the first following ready-high edge",
                "memory_error_recovery": {
                    "response_cases": [
                        {"mem_error_code": 6, "expected_csr_error_code": 6},
                        {"mem_error_code": 7, "expected_csr_error_code": 6},
                    ],
                    "trigger": "issue a legal feature-memory read and inject each listed nonzero mem_error_code on its handshake; codes 6 and 7 respectively cover INTERNAL and unknown-nonzero mapping",
                    "expected_status_bits": {"busy": 0, "done": 0, "error": 1, "pl_owns_buffers": 0},
                    "expected_buffer_owner": "PS",
                    "head_output_valid": False,
                    "failed_request_side_effect": "none",
                    "recovery": "write ACK bit1 to clear error, then a legal start is accepted",
                },
                "accumulator_overflow_recovery": {
                    "arithmetic_vector_case_index": 9,
                    "arithmetic_test_scope": "run the exact shared int8_mac directed vector independently at the MAC unit boundary; it is not a cfg/GF8 convolution vector and is not claimed as a full-network inference",
                    "expected_first_int32_overflow_product_index": 0,
                    "expected_csr_error_code": 7,
                    "controller_fault_injection": {"fixture": "controller unit test with a behavioral operator backend stub", "after_start": "wait until STATUS.busy=1, then pulse operator_result_valid for one rising edge with operator_error_code=7", "interface": "control_protocol.operator_completion_event"},
                    "expected_status_bits": {"busy": 0, "done": 0, "error": 1, "pl_owns_buffers": 0},
                    "expected_buffer_owner": "PS",
                    "head_output_valid": False,
                    "recovery": "the independent MAC test reports overflow for case 9; the controller stub separately injects operator error code 7 during an active task; write ACK bit1, then accept a legal start",
                },
                "completion_boundary": {"engine_done_edge_after_start": 5, "timeout_cycles_equal": 5, "expected": "completion wins, done=1,error=0"},
                "timeout_recovery": {"engine_done_edge_after_start": 5, "timeout_cycles": 4, "expected": "error=1,error_code=TIMEOUT,busy=0,ownership=PS; ACK then a legal start is accepted"},
                "cancel_pending_write": {"request": "feature write with mem_valid=1 while testbench holds mem_ready=0 for 7 cycles", "abort_actions": ["assert hard reset before ready rises", "separate run: trigger timeout before ready rises"], "expected": "request is canceled and the addressed bytes remain unchanged after ready later rises"},
                "required_cases": ["reset idle", "reset while busy", "CSR valid deassert/update after accepted edge", "soft reset while busy", "start while busy", "start before ACK", "wrong address", "wrong length", "zero timeout", "unaligned address", "zero or conflicting strobes", "partial final word", "read disabled lanes return zero", "write disabled lanes unchanged", "input/weight write rejected", "memory request held stable through stalls", "memory error code 6 and unknown nonzero map to INTERNAL; error ACK then legal recovery", "INT32 accumulator overflow maps to code 7, invalidates heads and recovers after ACK", "completion on timeout boundary wins", "reset/timeout cancels pending write", "error ACK then successful recovery", "timeout then successful recovery"]
            },
        },
        "fixed_test_samples_path": "report/evidence/S2A-T01/fixed_test_samples.json",
    }
    model_manifest_sha256 = sha256_bytes(
        (json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    )
    sample_manifest = {
        "schema_version": "gestureforge_s2a_fixed_test_samples_v1",
        "created_utc8": datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds"),
        "seed": sample_seed,
        "seeded_generator": "xorshift32; uint32 state, shifts 13/17/5, each sample byte=state&255",
        "model_manifest_binding": {"path": "report/evidence/S2A-T01/tiny416_model_manifest.json", "sha256": model_manifest_sha256},
        "pl_input_contract": {"source": "bindings.preprocess_runtime and bindings.input_contract in model_manifest_binding", "per_sample_hash": "pl_input_sha256", "tensor_shape_nchw": [1, 3, 416, 416], "tensor_dtype": "signed int8 two's complement", "byte_order": "contiguous channel-major then row-major then column-major", "includes_preprocessing": True},
        "official_test_selection": "first 20 rows per class plus every additional official test row with at least two GT boxes, each in approved manifest order",
        "official_test_manifest": {"path": str(args.manifest.resolve()), "sha256": sha256_file(args.manifest)},
        "calibration_list": {"path": str(args.calibration_list.resolve()), "sha256": sha256_file(args.calibration_list)},
        "sample_count": len(samples),
        "samples": [{"frame_id": index, **sample} for index, sample in enumerate(samples)],
        "coverage": {
            "five_classes": sorted({tag for item in samples for tag in item["coverage_tags"] if tag.startswith("class:")}),
            "empty_ground_truth": sum("empty_ground_truth" in item["coverage_tags"] for item in samples),
            "boundary_ground_truth": sum("boundary_ground_truth_box" in item["coverage_tags"] for item in samples),
            "full_network_inputs": {"count": len(samples), "official_first_twenty_per_class": 100, "official_additional_multi_ground_truth_samples": sum(item["source"] == "official_hagrid_test_multibox" for item in dataset_samples), "approved_empty_label_samples": 3, "synthetic_extreme_samples": 4, "official_multi_ground_truth_count": sum("multi_ground_truth_boxes" in item["coverage_tags"] for item in dataset_samples), "boundary_ground_truth_count": sum("boundary_ground_truth_box" in item["coverage_tags"] for item in dataset_samples), "multi_prediction_claim": "CPU golden and decoder output must still verify multi-candidate predictions; GT coverage is bound by the listed multi-box source images"},
            "postprocess_fixtures": {"source_path": "verification/test_s1_t02_d9_yolo_decode.py", "source_commit": BASELINE_COMMIT, "source_sha256": BASELINE_D9_TEST_SHA256, "multi_box": ["test_same_class_overlap_is_suppressed_but_other_class_is_kept", "test_output_limit_is_fifteen"], "empty": ["test_empty_and_below_threshold_inputs_return_no_predictions"], "boundary_and_tie": ["test_floor_padding_clips_boxes_and_drops_padding_only_boxes", "test_odd_padding_uses_d2_floor_not_darknet_half_pixel", "test_threshold_boundary_uses_d6_greater_or_equal_semantics"]},
            "operator_extremes": {"direct_int8_values": [-127, -1, 0, 1, 127], "mac_products": [[-127, -127], [-127, 127], [127, -127], [127, 127]]},
            "operator_random_suite": {"cases_per_model_layer": 1000, "directed_cases_per_model_layer": 16, "shared_primitive_random_cases": 1000, "shared_primitive_directed_cases": 16, "seed": sample_seed, "generator_binding": "tiny416_model_manifest.operator_test_plan", "signed_int8_mapping": "(next_u32 & 255) % 255 - 127"},
        },
    }
    output_dir = args.output_dir.resolve()
    manifest_path = output_dir / "tiny416_model_manifest.json"
    samples_path = output_dir / "fixed_test_samples.json"
    write_new_json(manifest_path, manifest)
    try:
        write_new_json(samples_path, sample_manifest)
    except Exception:
        manifest_path.unlink(missing_ok=True)
        raise
    print(f"MODEL_MANIFEST={manifest_path}")
    print(f"FIXED_SAMPLES={samples_path}")
    print(f"LAYER_COUNT={len(layers)} CONV_COUNT=21")
    print(f"FIXED_SAMPLE_COUNT={len(samples)} FEATURE_END=0x{address_map['feature_workspace']['end_address_exclusive']:08X}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (DeliveryError, OSError, KeyError, ValueError, TypeError, struct.error) as exc:
        print(f"S2A_MODEL_DELIVERY_ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
