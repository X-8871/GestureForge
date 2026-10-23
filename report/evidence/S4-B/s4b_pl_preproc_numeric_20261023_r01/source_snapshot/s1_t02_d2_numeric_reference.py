"""S1-T02-D2 的独立预处理与 INT8 数值参考。

本模块只覆盖输入预处理、量化、累加和重定标，不实现训练、检测头解码或 NMS。
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable, Sequence


INT8_MIN = -127
INT8_MAX = 127
INT32_MIN = -(1 << 31)
INT32_MAX = (1 << 31) - 1
INT64_MIN = -(1 << 63)
INT64_MAX = (1 << 63) - 1
INPUT_SCALE = 1.0 / 127.0


def _finite(value: float, name: str = "value") -> float:
    """拒绝 NaN/Inf，返回可参与计算的浮点数。"""
    converted = float(value)
    if not math.isfinite(converted):
        raise ValueError(f"{name} 必须是有限数")
    return converted


def round_away_from_zero(value: float) -> int:
    """执行正负对称、半数远离零的舍入。"""
    value = _finite(value)
    magnitude = math.floor(abs(value) + 0.5)
    return int(magnitude if value >= 0 else -magnitude)


def saturate_int8(value: int) -> int:
    """将整数饱和到本项目规定的有符号 [-127, 127]。"""
    if type(value) is not int:
        raise TypeError("INT8 饱和输入必须是整数")
    return max(INT8_MIN, min(INT8_MAX, value))


def quantize_symmetric(value: float, scale: float) -> int:
    """按零点为零的对称规则量化一个浮点值。"""
    scale = _finite(scale, "scale")
    if scale <= 0:
        raise ValueError("scale 必须为正数")
    return saturate_int8(round_away_from_zero(_finite(value) / scale))


def symmetric_scale(max_abs: float) -> float:
    """由最大绝对值生成 INT8 对称 scale，零层回退到 1/127。"""
    max_abs = _finite(max_abs, "max_abs")
    if max_abs < 0:
        raise ValueError("max_abs 不能为负数")
    return max_abs / INT8_MAX if max_abs else INPUT_SCALE


def activation_scale(values: Iterable[float]) -> float:
    """计算逐层逐张量激活 scale。"""
    finite_values = [_finite(value) for value in values]
    return symmetric_scale(max((abs(value) for value in finite_values), default=0.0))


def quantize_activation(values: Sequence[float]) -> tuple[list[int], float]:
    """按单个激活张量的最大绝对值量化。"""
    scale = activation_scale(values)
    return [quantize_symmetric(value, scale) for value in values], scale


def weight_scales_per_output_channel(weights: Sequence[Sequence[float]]) -> list[float]:
    """计算每个输出通道的权重对称 scale。"""
    scales = []
    for channel, values in enumerate(weights):
        finite_values = [_finite(value, f"weights[{channel}]") for value in values]
        scales.append(symmetric_scale(max((abs(value) for value in finite_values), default=0.0)))
    return scales


def quantize_weights_per_output_channel(
    weights: Sequence[Sequence[float]],
) -> tuple[list[list[int]], list[float]]:
    """按输出通道逐行执行对称 INT8 权重量化。"""
    scales = weight_scales_per_output_channel(weights)
    quantized = [
        [quantize_symmetric(value, scales[channel]) for value in row]
        for channel, row in enumerate(weights)
    ]
    return quantized, scales


def rgb_to_chw_255(rgb: Sequence[Sequence[Sequence[float]]]) -> list[list[list[float]]]:
    """将 HWC RGB 像素转为 Darknet 风格 CHW，并除以 255。"""
    height = len(rgb)
    width = len(rgb[0]) if height else 0
    if height == 0 or width == 0:
        raise ValueError("RGB 图像不能为空")
    if any(len(row) != width for row in rgb):
        raise ValueError("RGB 图像行宽不一致")
    output = [[[0.0 for _ in range(width)] for _ in range(height)] for _ in range(3)]
    for y, row in enumerate(rgb):
        for x, pixel in enumerate(row):
            if len(pixel) != 3:
                raise ValueError("RGB 图像必须有三个通道")
            for channel, value in enumerate(pixel):
                value = _finite(value, f"rgb[{y}][{x}][{channel}]")
                if not 0.0 <= value <= 255.0:
                    raise ValueError("像素必须位于 [0, 255]")
                output[channel][y][x] = value / 255.0
    return output


def letterbox_geometry(src_width: int, src_height: int, dst_width: int, dst_height: int) -> dict[str, int | float]:
    """复现 Darknet letterbox_image 的整数尺寸和左上 floor 偏移。"""
    if min(src_width, src_height, dst_width, dst_height) <= 0:
        raise ValueError("图像尺寸必须为正整数")
    if (float(dst_width) / src_width) < (float(dst_height) / src_height):
        new_width = dst_width
        new_height = (src_height * dst_width) // src_width
    else:
        new_height = dst_height
        new_width = (src_width * dst_height) // src_height
    return {
        "src_width": src_width,
        "src_height": src_height,
        "dst_width": dst_width,
        "dst_height": dst_height,
        "new_width": new_width,
        "new_height": new_height,
        "offset_x": (dst_width - new_width) // 2,
        "offset_y": (dst_height - new_height) // 2,
        "padding_normalized": 0.5,
        "padding_uint8": 128,
    }


def _resize_bilinear_rgb_values(
    rgb: Sequence[Sequence[Sequence[float]]], new_width: int, new_height: int
) -> list[list[list[float]]]:
    """复现 Darknet resize_image 的端点对齐双线性插值。"""
    src_height = len(rgb)
    src_width = len(rgb[0]) if src_height else 0
    if src_width <= 0 or src_height <= 0 or new_width <= 0 or new_height <= 0:
        raise ValueError("resize 尺寸必须为正数")
    if src_width == new_width and src_height == new_height:
        return [[list(pixel) for pixel in row] for row in rgb]
    result = [[[0.0 for _ in range(3)] for _ in range(new_width)] for _ in range(new_height)]
    w_scale = (src_width - 1) / (new_width - 1) if new_width != 1 else 0.0
    h_scale = (src_height - 1) / (new_height - 1) if new_height != 1 else 0.0
    for y in range(new_height):
        # Darknet 在目标最后一行或目标高度为 1 时直接取源图最后一行。
        if new_height == 1 or y == new_height - 1:
            iy = src_height - 1
            iy1 = iy
            dy = 0.0
        else:
            sy = y * h_scale
            iy = int(sy)
            dy = sy - iy
            iy1 = min(iy + 1, src_height - 1)
        for x in range(new_width):
            # Darknet 在目标最后一列或目标宽度为 1 时直接取源图最后一列。
            if new_width == 1 or x == new_width - 1:
                ix = src_width - 1
                ix1 = ix
                dx = 0.0
            else:
                sx = x * w_scale
                ix = int(sx)
                dx = sx - ix
                ix1 = min(ix + 1, src_width - 1)
            for channel in range(3):
                top = (1.0 - dx) * rgb[iy][ix][channel] + dx * rgb[iy][ix1][channel]
                bottom = (1.0 - dx) * rgb[iy1][ix][channel] + dx * rgb[iy1][ix1][channel]
                result[y][x][channel] = (1.0 - dy) * top + dy * bottom
    return result


def letterbox_rgb_uint8(rgb: Sequence[Sequence[Sequence[int]]], dst_width: int, dst_height: int) -> list[list[list[float]]]:
    """将原始 8-bit RGB 变换为仍使用 0..255 单位的 letterbox 像素值。"""
    src_height = len(rgb)
    src_width = len(rgb[0]) if src_height else 0
    geometry = letterbox_geometry(src_width, src_height, dst_width, dst_height)
    for row in rgb:
        for pixel in row:
            if len(pixel) != 3 or any(type(value) is not int or not 0 <= value <= 255 for value in pixel):
                raise ValueError("原始 RGB 输入必须是三个 8-bit 整数通道")
    resized = _resize_bilinear_rgb_values(rgb, int(geometry["new_width"]), int(geometry["new_height"]))
    boxed = [
        [[128.0, 128.0, 128.0] for _ in range(dst_width)] for _ in range(dst_height)
    ]
    for y, row in enumerate(resized):
        for x, pixel in enumerate(row):
            boxed[y + int(geometry["offset_y"])][x + int(geometry["offset_x"])] = list(pixel)
    return boxed


def letterbox_rgb_normalized(rgb: Sequence[Sequence[Sequence[int]]], dst_width: int, dst_height: int) -> list[list[list[float]]]:
    """将原始 8-bit RGB letterbox 后转换为 0..1 单位，补边为 0.5。"""
    src_height = len(rgb)
    src_width = len(rgb[0]) if src_height else 0
    geometry = letterbox_geometry(src_width, src_height, dst_width, dst_height)
    for row in rgb:
        for pixel in row:
            if len(pixel) != 3 or any(type(value) is not int or not 0 <= value <= 255 for value in pixel):
                raise ValueError("原始 RGB 输入必须是三个 8-bit 整数通道")
    resized = _resize_bilinear_rgb_values(rgb, int(geometry["new_width"]), int(geometry["new_height"]))
    boxed = [[[0.5, 0.5, 0.5] for _ in range(dst_width)] for _ in range(dst_height)]
    for y, row in enumerate(resized):
        for x, pixel in enumerate(row):
            boxed[y + int(geometry["offset_y"])][x + int(geometry["offset_x"])] = [
                max(0.0, min(1.0, _finite(value, "resized_rgb") / 255.0)) for value in pixel
            ]
    return boxed


def rgb_to_hwc_normalized(rgb: Sequence[Sequence[Sequence[float]]]) -> list[list[list[float]]]:
    """将仍以 0..255 表示的 HWC RGB 像素转换为 0..1，保持 HWC。"""
    return [
        [[_finite(value, "rgb") / 255.0 for value in pixel] for pixel in row]
        for row in rgb
    ]


def normalized_hwc_to_chw(normalized_hwc: Sequence[Sequence[Sequence[float]]]) -> list[list[list[float]]]:
    """将已经处于 0..1 单位的 HWC RGB 转为 CHW，不再次除以 255。"""
    height = len(normalized_hwc)
    width = len(normalized_hwc[0]) if height else 0
    if height == 0 or width == 0:
        raise ValueError("归一化 RGB 图像不能为空")
    output = [[[0.0 for _ in range(width)] for _ in range(height)] for _ in range(3)]
    for y, row in enumerate(normalized_hwc):
        if len(row) != width:
            raise ValueError("归一化 RGB 图像行宽不一致")
        for x, pixel in enumerate(row):
            if len(pixel) != 3:
                raise ValueError("归一化 RGB 图像必须有三个通道")
            for channel, value in enumerate(pixel):
                value = _finite(value, "normalized_rgb")
                if not 0.0 <= value <= 1.0:
                    raise ValueError("归一化 RGB 像素必须位于 [0, 1]")
                output[channel][y][x] = value
    return output


def quantize_input_chw(normalized_chw: Sequence[Sequence[Sequence[float]]]) -> list[list[list[int]]]:
    """对已经归一化为 0..1 的 CHW 输入执行固定 scale=1/127 量化。"""
    return [
        [[quantize_symmetric(value, INPUT_SCALE) for value in row] for row in channel]
        for channel in normalized_chw
    ]


def preprocess_rgb_uint8_to_chw_int8(
    rgb: Sequence[Sequence[Sequence[int]]], dst_width: int, dst_height: int
) -> list[list[list[int]]]:
    """执行原始 8-bit RGB -> letterbox -> CHW/255 -> 固定输入 INT8 的完整路径。"""
    normalized_hwc = letterbox_rgb_normalized(rgb, dst_width, dst_height)
    return quantize_input_chw(normalized_hwc_to_chw(normalized_hwc))


def checked_int32(value: int, name: str = "value") -> int:
    """检查整数是否能表示为 INT32。"""
    if type(value) is not int or not INT32_MIN <= value <= INT32_MAX:
        raise OverflowError(f"{name} 超出 INT32 范围")
    return value


def checked_int64(value: int, name: str = "value") -> int:
    """检查整数是否能表示为 INT64。"""
    if type(value) is not int or not INT64_MIN <= value <= INT64_MAX:
        raise OverflowError(f"{name} 超出 INT64 范围")
    return value


def checked_quantized_int8(value: int, name: str = "value") -> int:
    """严格检查量化输入为非 bool 的有符号 [-127,127] 整数。"""
    if type(value) is not int or not INT8_MIN <= value <= INT8_MAX:
        raise ValueError(f"{name} 必须是 [-127,127] 内的整数")
    return value


def int32_accumulate(values: Iterable[int], bias: int = 0) -> int:
    """逐项在 INT32 域累加，并对每一步检查 INT64 乘法语义的输入范围。"""
    accumulator = checked_int32(bias, "bias")
    for index, value in enumerate(values):
        checked_quantized_int8(value, f"values[{index}]")
        accumulator = checked_int32(accumulator + value, f"accumulator[{index}]")
    return accumulator


def int64_dot(a: Sequence[int], b: Sequence[int], bias: int = 0) -> int:
    """以 Python 精确整数计算并逐项检查 INT64 乘积和累加边界。"""
    if len(a) != len(b):
        raise ValueError("点积两侧长度必须一致")
    accumulator = checked_int64(bias, "bias")
    for index, (left, right) in enumerate(zip(a, b)):
        checked_quantized_int8(left, f"a[{index}]")
        checked_quantized_int8(right, f"b[{index}]")
        product = checked_int64(left * right, f"product[{index}]")
        accumulator = checked_int64(accumulator + product, f"int64_accumulator[{index}]")
    return accumulator


def bias_to_accumulator(bias: Sequence[float], input_scale: float, weight_scales: Sequence[float]) -> list[int]:
    """把 BN 折叠后的浮点 bias 映射到每个输出通道的累加器域。"""
    input_scale = _finite(input_scale, "input_scale")
    if input_scale <= 0 or len(bias) != len(weight_scales):
        raise ValueError("bias 与 weight scale 长度或 input scale 无效")
    result = []
    for index, (value, weight_scale) in enumerate(zip(bias, weight_scales)):
        weight_scale = _finite(weight_scale, f"weight_scales[{index}]")
        if weight_scale <= 0:
            raise ValueError("weight scale 必须为正数")
        accumulator_bias = round_away_from_zero(_finite(value, f"bias[{index}]") / (input_scale * weight_scale))
        result.append(checked_int32(accumulator_bias, f"bias_accumulator[{index}]") )
    return result


def requantize_accumulator(accumulator: int, input_scale: float, weight_scale: float, activation_scale_value: float) -> int:
    """将累加器域结果重定标至激活 INT8 域并饱和。"""
    checked_int32(accumulator, "accumulator")
    input_scale = _finite(input_scale, "input_scale")
    weight_scale = _finite(weight_scale, "weight_scale")
    activation_scale_value = _finite(activation_scale_value, "activation_scale")
    if min(input_scale, weight_scale, activation_scale_value) <= 0:
        raise ValueError("所有重定标 scale 必须为正数")
    real_value = accumulator * input_scale * weight_scale
    return saturate_int8(round_away_from_zero(real_value / activation_scale_value))


def golden_vectors() -> dict[str, object]:
    """生成可审查的固定向量及期望值。"""
    rgb = [[[255.0, 0.0, 128.0]]]
    endpoint_rgb = [
        [[5, 10, 15], [25, 30, 35]],
        [[45, 50, 55], [115, 120, 125]],
    ]
    odd_geometry = letterbox_geometry(4, 3, 7, 7)
    letterboxed = letterbox_rgb_normalized([[[255, 0, 0]] * 4 for _ in range(3)], 7, 7)
    return {
        "round_away_from_zero": {
            "inputs": [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5],
            "outputs": [round_away_from_zero(value) for value in [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5]],
        },
        "saturation": {"inputs": [-1000, -127, 0, 127, 1000], "outputs": [saturate_int8(value) for value in [-1000, -127, 0, 127, 1000]]},
        "rgb_chw_255": {"input": rgb, "output": rgb_to_chw_255(rgb)},
        "input_pad": {"normalized": 0.5, "scale": INPUT_SCALE, "int8": quantize_symmetric(0.5, INPUT_SCALE)},
        "letterbox_odd_geometry": odd_geometry,
        "letterbox_pad_corner": {"pixel": letterboxed[0][0], "expected_normalized": [0.5, 0.5, 0.5]},
        "resize_endpoint_1x1": {
            "input_rgb_uint8": endpoint_rgb,
            "resized_rgb": _resize_bilinear_rgb_values(endpoint_rgb, 1, 1),
            "preprocess_chw_int8": preprocess_rgb_uint8_to_chw_int8(endpoint_rgb, 1, 1),
            "darknet_boundary_rule": "目标宽或高为1，以及目标最后列/行，取源最后列/行",
        },
        "weights_per_output_channel": {
            "weights": [[-2.0, 0.0, 2.0], [-0.5, 0.25, 0.5]],
            "quantized_and_scales": [list(item) for item in zip(*quantize_weights_per_output_channel([[-2.0, 0.0, 2.0], [-0.5, 0.25, 0.5]]))],
        },
        "bias_requant": {
            "bias_accumulator": bias_to_accumulator([0.5], INPUT_SCALE, [2.0 / 127.0]),
            "requantized": requantize_accumulator(64, INPUT_SCALE, 2.0 / 127.0, 1.0 / 127.0),
        },
        "int64_boundary": {
            "max_value": INT64_MAX,
            "max_sum": int64_dot([0], [0], bias=INT64_MAX),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 S1-T02-D2 固定数值 golden JSON")
    parser.add_argument("--output", type=Path, required=True, help="golden JSON 输出路径")
    args = parser.parse_args()
    payload = {
        "schema_version": "s1_t02_d2_numeric_golden_v1",
        "scope": "预处理与 INT8 数值参考，不含训练、解码和 NMS",
        "spec": {
            "input": "RGB -> CHW -> /255",
            "letterbox": "Darknet 整数尺寸、左上 floor 偏移、双线性、归一化 pad=0.5",
            "int8_range": [INT8_MIN, INT8_MAX],
            "zero_point": 0,
            "input_scale": INPUT_SCALE,
            "weight_quantization": "per-output-channel symmetric",
            "activation_quantization": "per-layer per-tensor symmetric",
            "accumulator": "INT32 with independent INT64 overflow checks",
            "rounding": "symmetric half-away-from-zero",
        },
        "vectors": golden_vectors(),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
