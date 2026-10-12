"""S1-T02-D2 的 tiny416 INT8 整数前向参考实现。

本模块读取已冻结的 Darknet cfg、浮点权重、GFINT8W1 权重包和激活
scale 校准报告，在 CPU 上执行可审计的卷积整数累加、BN 折叠 bias
累加器映射、激活重定标及 INT8 饱和。该路径不训练、不修改模型，也
不执行检测头解码或 NMS。
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
from typing import Any

import numpy as np

try:
    from s1_t02_d2_int8_weight_reference import BN_EPSILON, parse_cfg
except ModuleNotFoundError:
    from verification.s1_t02_d2_int8_weight_reference import BN_EPSILON, parse_cfg


INT8_MIN = -127
INT8_MAX = 127
INT32_MIN = -(1 << 31)
INT32_MAX = (1 << 31) - 1
INT64_MIN = -(1 << 63)
INT64_MAX = (1 << 63) - 1
INPUT_SCALE = 1.0 / 127.0
PACKAGE_MAGIC = b"GFINT8W1"
PACKAGE_VERSION = 1
EXPECTED_CALIBRATION_SAMPLES = 512


class Int8ForwardError(ValueError):
    """表示整数前向输入绑定、形状或数值检查失败。"""


@dataclass(frozen=True)
class Section:
    """记录一个 cfg section。"""

    kind: str
    options: dict[str, str]


@dataclass(frozen=True)
class PackageLayer:
    """记录 GFINT8W1 中一个卷积层的量化参数。"""

    layer_index: int
    filters: int
    input_channels: int
    groups: int
    size: int
    weight_count: int
    weight_scales: np.ndarray
    fused_biases: np.ndarray
    quantized_weights: np.ndarray


@dataclass(frozen=True)
class FloatLayer:
    """记录一个卷积层的 BN 折叠浮点参数。"""

    layer_index: int
    filters: int
    input_channels: int
    groups: int
    size: int
    weights: np.ndarray
    fused_biases: np.ndarray


@dataclass(frozen=True)
class Tensor:
    """记录 CHW 张量及其统一量化 scale。"""

    values: np.ndarray
    scale: float


def sha256_file(path: Path) -> str:
    """计算文件 SHA-256。"""

    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise Int8ForwardError(f"文件不可读取: {path}: {exc}") from exc
    return digest.hexdigest()


def utc8_now() -> str:
    """返回东八区时间。"""

    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def require_file(path: Path, field: str) -> Path:
    """校验路径为普通文件并返回绝对路径。"""

    resolved = path.resolve()
    if not resolved.is_file():
        raise Int8ForwardError(f"{field} 不是普通文件: {resolved}")
    return resolved


def finite_positive(value: Any, field: str) -> float:
    """解析有限正浮点数。"""

    try:
        converted = float(value)
    except (TypeError, ValueError) as exc:
        raise Int8ForwardError(f"{field} 不是浮点数: {value!r}") from exc
    if not math.isfinite(converted) or converted <= 0.0:
        raise Int8ForwardError(f"{field} 必须为有限正数: {value!r}")
    return converted


def round_away_array(values: np.ndarray) -> np.ndarray:
    """对数组执行正负对称、半数远离零点的舍入。"""

    values = np.asarray(values, dtype=np.float64)
    magnitudes = np.floor(np.abs(values) + 0.5)
    return np.where(values >= 0.0, magnitudes, -magnitudes).astype(np.int64)


def saturate_array(values: np.ndarray) -> np.ndarray:
    """把数组饱和到项目规定的 [-127,127]。"""

    return np.clip(values, INT8_MIN, INT8_MAX).astype(np.int8)


def parse_cfg_sections(path: Path) -> list[Section]:
    """读取 cfg section，保持文件层号和 route 语义。"""

    sections: list[Section] = []
    current_kind: str | None = None
    current: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise Int8ForwardError(f"cfg UTF-8 读取失败: {path}: {exc}") from exc
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            if current_kind is not None:
                sections.append(Section(current_kind, current))
            current_kind = line[1:-1].strip().lower()
            current = {}
            continue
        if current_kind is None or "=" not in line:
            raise Int8ForwardError(f"cfg 第 {line_number} 行格式无效")
        key, value = line.split("=", 1)
        key = key.strip().lower()
        value = value.strip()
        if not key or not value or key in current:
            raise Int8ForwardError(f"cfg 第 {line_number} 行键值无效或重复")
        current[key] = value
    if current_kind is not None:
        sections.append(Section(current_kind, current))
    if not sections or sections[0].kind != "net":
        raise Int8ForwardError("cfg 第一段必须是 [net]")
    return sections


def cfg_int(options: dict[str, str], key: str, default: int | None = None) -> int:
    """读取 cfg 十进制整数。"""

    value = options.get(key)
    if value is None:
        if default is None:
            raise Int8ForwardError(f"cfg 缺少字段: {key}")
        return default
    try:
        return int(value, 10)
    except ValueError as exc:
        raise Int8ForwardError(f"cfg 字段不是整数: {key}={value}") from exc


def _optional_cfg_int(options: dict[str, str], key: str, default: int) -> int:
    """读取可选 cfg 整数，并把非法值转换为统一错误。"""

    return cfg_int(options, key, default)


def convolution_parameters(options: dict[str, str], size: int) -> tuple[int, int]:
    """绑定 Darknet 卷积的 stride、pad/padding 语义。"""

    if size <= 0:
        raise Int8ForwardError(f"卷积 size 无效: {size}")
    stride = cfg_int(options, "stride", 1)
    stride_x = _optional_cfg_int(options, "stride_x", stride)
    stride_y = _optional_cfg_int(options, "stride_y", stride)
    if stride <= 0 or stride_x != stride or stride_y != stride:
        raise Int8ForwardError(
            f"暂不支持非方形卷积 stride: stride={stride}, stride_x={stride_x}, stride_y={stride_y}"
        )
    dilation = _optional_cfg_int(options, "dilation", 1)
    if dilation != 1:
        raise Int8ForwardError(f"暂不支持卷积 dilation={dilation}")
    if _optional_cfg_int(options, "antialiasing", 0) != 0:
        raise Int8ForwardError("暂不支持卷积 antialiasing")
    pad_flag = _optional_cfg_int(options, "pad", 0)
    if pad_flag not in (0, 1):
        raise Int8ForwardError(f"卷积 pad 必须为 0 或 1: {pad_flag}")
    padding = _optional_cfg_int(options, "padding", 0)
    if pad_flag:
        padding = size // 2
    if padding < 0:
        raise Int8ForwardError(f"卷积 padding 不能为负数: {padding}")
    return stride, padding


def maxpool_parameters(options: dict[str, str], size: int) -> tuple[int, int, int]:
    """绑定 Darknet 最大池化的 stride、padding 和受支持选项。"""

    if size <= 0:
        raise Int8ForwardError(f"最大池化 size 无效: {size}")
    stride = cfg_int(options, "stride", 1)
    stride_x = _optional_cfg_int(options, "stride_x", stride)
    stride_y = _optional_cfg_int(options, "stride_y", stride)
    if stride <= 0 or stride_x != stride or stride_y != stride:
        raise Int8ForwardError(
            f"暂不支持非方形最大池化 stride: stride={stride}, stride_x={stride_x}, stride_y={stride_y}"
        )
    padding = _optional_cfg_int(options, "padding", size - 1)
    if padding < 0:
        raise Int8ForwardError(f"最大池化 padding 不能为负数: {padding}")
    for key, default in (("maxpool_depth", 0), ("out_channels", 1), ("antialiasing", 0), ("maxpool_zero_nonmax", 0)):
        value = _optional_cfg_int(options, key, default)
        if value != default:
            raise Int8ForwardError(f"暂不支持最大池化 {key}={value}")
    return size, stride, padding


def upsample_stride(options: dict[str, str]) -> int:
    """绑定 Darknet upsample 的 stride/scale 语义。"""

    stride = cfg_int(options, "stride", 2)
    stride_x = _optional_cfg_int(options, "stride_x", stride)
    stride_y = _optional_cfg_int(options, "stride_y", stride)
    if stride <= 0 or stride_x != stride or stride_y != stride:
        raise Int8ForwardError(
            f"暂不支持非方形 upsample stride: stride={stride}, stride_x={stride_x}, stride_y={stride_y}"
        )
    try:
        scale = float(options.get("scale", "1"))
    except ValueError as exc:
        raise Int8ForwardError(f"upsample scale 不是浮点数: {options.get('scale')}") from exc
    if not math.isfinite(scale) or not math.isclose(scale, 1.0, rel_tol=0.0, abs_tol=0.0):
        raise Int8ForwardError(f"暂不支持 upsample scale={scale}")
    reverse = _optional_cfg_int(options, "reverse", 0)
    if reverse != 0:
        raise Int8ForwardError(f"暂不支持 upsample reverse={reverse}")
    return stride


def resolve_reference(reference: int, layer_index: int) -> int:
    """解析 Darknet route 的相对或绝对层号。"""

    return layer_index + reference if reference < 0 else reference


def parse_package(path: Path) -> tuple[dict[str, int], dict[int, PackageLayer]]:
    """严格读取 GFINT8W1 权重包。"""

    try:
        blob = path.read_bytes()
    except OSError as exc:
        raise Int8ForwardError(f"INT8 权重包不可读取: {path}: {exc}") from exc
    offset = 0

    def read_struct(format_string: str, field: str) -> tuple[Any, ...]:
        nonlocal offset
        size = struct.calcsize(format_string)
        if offset + size > len(blob):
            raise Int8ForwardError(f"权重包读取 {field} 时提前结束")
        values = struct.unpack_from(format_string, blob, offset)
        offset += size
        return values

    magic, version, layer_count, width, height = read_struct("<8sIIII", "header")
    channels = read_struct("<I", "channels")[0]
    if magic != PACKAGE_MAGIC or version != PACKAGE_VERSION:
        raise Int8ForwardError(f"权重包 magic/version 无效: {magic!r}/{version}")
    if min(layer_count, width, height, channels) <= 0:
        raise Int8ForwardError("权重包网络尺寸或层数无效")
    layers: dict[int, PackageLayer] = {}
    for _ in range(layer_count):
        (
            layer_index,
            filters,
            input_channels,
            groups,
            size,
            weight_count,
            _batch_normalize,
            scale_count,
        ) = read_struct("<8I", f"layer {_}")
        if layer_index in layers or scale_count != filters:
            raise Int8ForwardError(f"权重包层索引或 scale 数量无效: {layer_index}")
        scale_bytes = filters * 4
        if offset + scale_bytes > len(blob):
            raise Int8ForwardError(f"权重包 layer {layer_index} scale 提前结束")
        scales = np.frombuffer(blob, dtype="<f4", count=filters, offset=offset).astype(np.float64)
        offset += scale_bytes
        if offset + scale_bytes > len(blob):
            raise Int8ForwardError(f"权重包 layer {layer_index} bias 提前结束")
        biases = np.frombuffer(blob, dtype="<f4", count=filters, offset=offset).astype(np.float64)
        offset += scale_bytes
        if offset + weight_count > len(blob):
            raise Int8ForwardError(f"权重包 layer {layer_index} weight 提前结束")
        weights = np.frombuffer(blob, dtype=np.int8, count=weight_count, offset=offset).copy()
        offset += weight_count
        if not np.all(np.isfinite(scales)) or not np.all(scales > 0.0) or not np.all(np.isfinite(biases)):
            raise Int8ForwardError(f"权重包 layer {layer_index} 含无效 scale/bias")
        if np.any(weights < INT8_MIN) or np.any(weights > INT8_MAX):
            raise Int8ForwardError(f"权重包 layer {layer_index} 含不符合规范的 INT8 值")
        expected_count = filters * (input_channels // groups) * size * size
        if groups <= 0 or input_channels % groups != 0 or expected_count != weight_count:
            raise Int8ForwardError(f"权重包 layer {layer_index} 布局无效")
        layers[layer_index] = PackageLayer(
            layer_index,
            filters,
            input_channels,
            groups,
            size,
            weight_count,
            scales,
            biases,
            weights.reshape(filters, input_channels // groups, size, size),
        )
    if offset != len(blob):
        raise Int8ForwardError(f"权重包存在未绑定尾部字节: {len(blob) - offset}")
    return {"version": version, "layer_count": layer_count, "width": width, "height": height, "channels": channels}, layers


def read_fused_float_layers(cfg: Path, weights: Path) -> dict[int, FloatLayer]:
    """读取 Darknet 权重并复现推理态 BN 折叠。"""

    network = parse_cfg(cfg)
    try:
        blob = weights.read_bytes()
    except OSError as exc:
        raise Int8ForwardError(f"浮点权重不可读取: {weights}: {exc}") from exc
    if len(blob) < 16:
        raise Int8ForwardError("浮点权重头不完整")
    major, minor, _revision = struct.unpack_from("<3i", blob, 0)
    offset = 20 if major * 10 + minor >= 2 else 16
    result: dict[int, FloatLayer] = {}
    for conv in network.convolutions:
        def read_floats(count: int, field: str) -> np.ndarray:
            nonlocal offset
            size = count * 4
            if offset + size > len(blob):
                raise Int8ForwardError(f"权重读取 {field} 时提前结束")
            values = np.frombuffer(blob, dtype="<f4", count=count, offset=offset).astype(np.float32).copy()
            offset += size
            if not np.all(np.isfinite(values)):
                raise Int8ForwardError(f"权重 {field} 含 NaN/Inf")
            return values

        raw_biases = read_floats(conv.filters, f"layer{conv.layer_index}.biases").astype(np.float64)
        if conv.batch_normalize:
            bn_scales = read_floats(conv.filters, f"layer{conv.layer_index}.scales").astype(np.float64)
            rolling_mean = read_floats(conv.filters, f"layer{conv.layer_index}.rolling_mean").astype(np.float64)
            rolling_variance = read_floats(conv.filters, f"layer{conv.layer_index}.rolling_variance").astype(np.float64)
            if np.any(rolling_variance + BN_EPSILON <= 0.0):
                raise Int8ForwardError(f"layer {conv.layer_index} BN variance 无效")
            factors = bn_scales / np.sqrt(rolling_variance + BN_EPSILON)
            # Darknet 的卷积 bias 是 BN 的 beta；推理折叠为 beta - mean * factor。
            biases = raw_biases - rolling_mean * factors
        else:
            factors = np.ones(conv.filters, dtype=np.float64)
            biases = raw_biases
        raw_weights = read_floats(conv.weight_count, f"layer{conv.layer_index}.weights").astype(np.float64)
        per_filter = conv.weight_count // conv.filters
        fused = (raw_weights.reshape(conv.filters, per_filter) * factors[:, None]).reshape(
            conv.filters, conv.input_channels // conv.groups, conv.size, conv.size
        )
        result[conv.layer_index] = FloatLayer(
            conv.layer_index,
            conv.filters,
            conv.input_channels,
            conv.groups,
            conv.size,
            fused,
            biases,
        )
    if offset != len(blob):
        raise Int8ForwardError(f"浮点权重存在未绑定尾部字节: {len(blob) - offset}")
    return result


def load_activation_scales(path: Path, cfg: Path, weights: Path, calibration_list: Path) -> dict[int, float]:
    """读取并校验真实激活校准报告。"""

    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise Int8ForwardError(f"激活校准报告不可读取: {path}: {exc}") from exc
    if report.get("status") != "ACTIVATION_SCALE_CALIBRATION_COMPLETE_INTEGER_FORWARD_PENDING":
        raise Int8ForwardError(f"激活校准报告状态不允许继续: {report.get('status')!r}")
    inputs = report.get("inputs", {})
    expected = {
        "cfg_sha256": sha256_file(cfg),
        "weights_sha256": sha256_file(weights),
        "calibration_list_sha256": sha256_file(calibration_list),
    }
    for key, actual in expected.items():
        if inputs.get(key, "").lower() != actual:
            raise Int8ForwardError(f"激活报告 {key} 与当前输入不一致")
    if inputs.get("calibration_sample_count") != EXPECTED_CALIBRATION_SAMPLES:
        raise Int8ForwardError("激活报告不是固定 512 张 train-only 校准")
    layers = report.get("layers")
    if not isinstance(layers, dict) or not layers:
        raise Int8ForwardError("激活报告缺少 layers")
    result: dict[int, float] = {}
    for key, item in layers.items():
        try:
            layer_index = int(key, 10)
        except (TypeError, ValueError) as exc:
            raise Int8ForwardError(f"激活报告层号无效: {key!r}") from exc
        result[layer_index] = finite_positive(item.get("activation_scale"), f"layer {layer_index} activation_scale")
    return result


def read_calibration_list(path: Path, count: int) -> list[Path]:
    """读取 train-only 清单的前 count 项并验证路径。"""

    try:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, UnicodeError) as exc:
        raise Int8ForwardError(f"校准清单读取失败: {path}: {exc}") from exc
    if len(lines) != EXPECTED_CALIBRATION_SAMPLES or len({line.casefold() for line in lines}) != len(lines):
        raise Int8ForwardError("校准清单必须是 512 行且无重复")
    if count <= 0 or count > EXPECTED_CALIBRATION_SAMPLES:
        raise Int8ForwardError(f"sample_count 必须位于 1..{EXPECTED_CALIBRATION_SAMPLES}")
    result = []
    for index, raw in enumerate(lines[:count]):
        path_value = Path(raw)
        if not path_value.is_file():
            raise Int8ForwardError(f"校准图像不存在，第 {index} 行: {path_value}")
        result.append(path_value.resolve())
    return result


def load_image_chw(path: Path, width: int, height: int) -> np.ndarray:
    """按固定 letterbox、RGB/255、CHW 读取图像。"""

    try:
        import cv2
    except ImportError as exc:
        raise Int8ForwardError("真实图像前向需要 cv2") from exc
    encoded = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
    if image is None or image.ndim != 3 or image.shape[2] != 3:
        raise Int8ForwardError(f"图像不可解码为三通道: {path}")
    rgb = image[:, :, ::-1].astype(np.float64)
    src_height, src_width = rgb.shape[:2]
    if (float(width) / src_width) < (float(height) / src_height):
        new_width = width
        new_height = (src_height * width) // src_width
    else:
        new_height = height
        new_width = (src_width * height) // src_height
    if new_width <= 0 or new_height <= 0:
        raise Int8ForwardError(f"图像缩放尺寸无效: {path}")
    if new_width == src_width and new_height == src_height:
        resized = rgb
    else:
        x_positions = np.zeros(new_width, dtype=np.float64) if new_width == 1 else np.arange(new_width) * (src_width - 1) / (new_width - 1)
        y_positions = np.zeros(new_height, dtype=np.float64) if new_height == 1 else np.arange(new_height) * (src_height - 1) / (new_height - 1)
        x0 = np.floor(x_positions).astype(np.int64)
        y0 = np.floor(y_positions).astype(np.int64)
        x1 = np.minimum(x0 + 1, src_width - 1)
        y1 = np.minimum(y0 + 1, src_height - 1)
        xd = (x_positions - x0).reshape(1, new_width, 1)
        yd = (y_positions - y0).reshape(new_height, 1, 1)
        top = rgb[y0[:, None], x0[None, :], :] * (1.0 - xd) + rgb[y0[:, None], x1[None, :], :] * xd
        bottom = rgb[y1[:, None], x0[None, :], :] * (1.0 - xd) + rgb[y1[:, None], x1[None, :], :] * xd
        resized = top * (1.0 - yd) + bottom * yd
    boxed = np.full((height, width, 3), 0.5, dtype=np.float64)
    offset_x = (width - new_width) // 2
    offset_y = (height - new_height) // 2
    boxed[offset_y : offset_y + new_height, offset_x : offset_x + new_width, :] = resized / 255.0
    return boxed.transpose(2, 0, 1).astype(np.float32)


def make_patches(values: np.ndarray, size: int, stride: int, padding: int | None = None) -> tuple[np.ndarray, int, int]:
    """把 CHW 张量转换为卷积 im2col 视图。"""

    channels, height, width = values.shape
    if padding is None:
        padding = size // 2
    if size <= 0 or stride <= 0 or padding < 0:
        raise Int8ForwardError(f"卷积参数无效: size={size}, stride={stride}, padding={padding}")
    padded = np.pad(values, ((0, 0), (padding, padding), (padding, padding)), mode="constant")
    out_height = (height + 2 * padding - size) // stride + 1
    out_width = (width + 2 * padding - size) // stride + 1
    if out_height <= 0 or out_width <= 0:
        raise Int8ForwardError("卷积输出尺寸无效")
    view = np.lib.stride_tricks.sliding_window_view(padded, (size, size), axis=(1, 2))
    view = view[:, ::stride, ::stride, :, :]
    view = view[:, :out_height, :out_width, :, :]
    return view.transpose(0, 3, 4, 1, 2).reshape(channels * size * size, out_height * out_width), out_height, out_width


def conv_float(values: np.ndarray, layer: FloatLayer, stride: int, padding: int | None = None) -> np.ndarray:
    """执行浮点参考卷积和激活。"""

    if layer.groups != 1:
        raise Int8ForwardError("当前参考器只支持 groups=1 卷积")
    patches, out_height, out_width = make_patches(values, layer.size, stride, padding)
    output = np.matmul(layer.weights.reshape(layer.filters, -1).astype(np.float64), patches.astype(np.float64))
    output += layer.fused_biases[:, None]
    output = output.reshape(layer.filters, out_height, out_width)
    return output


def conv_int8(
    values: Tensor,
    layer: PackageLayer,
    activation_scale: float,
    activation: str,
    stride: int,
    padding: int | None = None,
) -> tuple[Tensor, dict[str, Any]]:
    """执行 INT8 卷积、严格 INT64 边界证明、INT32 审计和重定标。"""

    if layer.groups != 1:
        raise Int8ForwardError("当前参考器只支持 groups=1 卷积")
    if np.any(values.values < INT8_MIN) or np.any(values.values > INT8_MAX):
        raise Int8ForwardError("输入 INT8 张量超出项目规定的 [-127,127]")
    patches, out_height, out_width = make_patches(values.values, layer.size, stride, padding)
    qweights = layer.quantized_weights.reshape(layer.filters, -1).astype(np.int64)
    qpatches = patches.astype(np.int64)
    if np.any(qweights < INT8_MIN) or np.any(qweights > INT8_MAX):
        raise Int8ForwardError(f"layer {layer.layer_index} 权重超出项目规定的 [-127,127]")
    reduction_length = qweights.shape[1]
    product_abs_bound = INT8_MAX * INT8_MAX
    raw_abs_bound = product_abs_bound * reduction_length
    if raw_abs_bound > INT64_MAX:
        raise Int8ForwardError(
            f"layer {layer.layer_index} 原始累加器理论边界超出 INT64: {raw_abs_bound}"
        )
    # 已先验证输入/权重范围，并以 K*127*127 证明每个点积不会溢出，
    # 因而 NumPy 的 INT64 矩阵乘法在这里是精确整数路径，而非溢出后再检测。
    raw_acc = np.matmul(qweights, qpatches)
    input_scale = values.scale
    bias_values = layer.fused_biases / (input_scale * layer.weight_scales)
    if not np.all(np.isfinite(bias_values)) or np.any(np.abs(bias_values) > float(INT64_MAX)):
        raise Int8ForwardError(f"layer {layer.layer_index} bias 累加器无法安全映射到 INT64")
    bias_acc = round_away_array(bias_values)
    bias_abs_bound = int(np.max(np.abs(bias_acc))) if bias_acc.size else 0
    with_bias_abs_bound = raw_abs_bound + bias_abs_bound
    if with_bias_abs_bound > INT64_MAX:
        raise Int8ForwardError(
            f"layer {layer.layer_index} 含 bias 累加器理论边界超出 INT64: {with_bias_abs_bound}"
        )
    with_bias = raw_acc + bias_acc[:, None]
    raw_int32_overflow_count = int(np.count_nonzero((raw_acc < INT32_MIN) | (raw_acc > INT32_MAX)))
    bias_int32_overflow_count = int(np.count_nonzero((bias_acc < INT32_MIN) | (bias_acc > INT32_MAX)))
    with_bias_int32_overflow_count = int(np.count_nonzero((with_bias < INT32_MIN) | (with_bias > INT32_MAX)))
    real_scale = input_scale * layer.weight_scales[:, None]
    scaled = with_bias.astype(np.float64) * real_scale / activation_scale
    if activation == "leaky":
        scaled = np.where(scaled >= 0.0, scaled, scaled * 0.1)
    elif activation != "linear":
        raise Int8ForwardError(f"暂不支持的卷积激活: {activation}")
    quantized = saturate_array(round_away_array(scaled)).reshape(layer.filters, out_height, out_width)
    stats = {
        "input_scale": input_scale,
        "output_scale": activation_scale,
        "bias_accumulator_min": int(np.min(bias_acc)),
        "bias_accumulator_max": int(np.max(bias_acc)),
        "raw_accumulator_min": int(np.min(raw_acc)),
        "raw_accumulator_max": int(np.max(raw_acc)),
        "accumulator_with_bias_min": int(np.min(with_bias)),
        "accumulator_with_bias_max": int(np.max(with_bias)),
        "product_abs_bound": product_abs_bound,
        "product_int64_overflow_count": 0,
        "raw_accumulator_abs_bound": raw_abs_bound,
        "raw_accumulator_int64_overflow_count": 0,
        "raw_accumulator_int32_overflow_count": raw_int32_overflow_count,
        "bias_accumulator_abs_bound": bias_abs_bound,
        "bias_accumulator_int64_overflow_count": 0,
        "bias_accumulator_int32_overflow_count": bias_int32_overflow_count,
        "accumulator_with_bias_abs_bound": with_bias_abs_bound,
        "accumulator_with_bias_int64_overflow_count": 0,
        "accumulator_with_bias_int32_overflow_count": with_bias_int32_overflow_count,
        "int32_overflow_count": with_bias_int32_overflow_count,
        "saturated_count": int(np.count_nonzero((quantized == INT8_MIN) | (quantized == INT8_MAX))),
        "quantized_min": int(np.min(quantized)),
        "quantized_max": int(np.max(quantized)),
    }
    return Tensor(quantized, activation_scale), stats


def maxpool(values: np.ndarray, size: int, stride: int, padding: int | None = None) -> np.ndarray:
    """执行 Darknet 最大池化，按其单侧 padding 和负半 padding 偏移语义。"""

    channels, height, width = values.shape
    if padding is None:
        padding = 0
    if size <= 0 or stride <= 0 or padding < 0:
        raise Int8ForwardError(f"最大池化参数无效: size={size}, stride={stride}, padding={padding}")
    out_height = (height + padding - size) // stride + 1
    out_width = (width + padding - size) // stride + 1
    if out_height <= 0 or out_width <= 0:
        raise Int8ForwardError("最大池化输出尺寸无效")
    offset = -(padding // 2)
    start_height = offset + max(0, -offset)
    start_width = offset + max(0, -offset)
    end_height = offset + (out_height - 1) * stride + size - 1
    end_width = offset + (out_width - 1) * stride + size - 1
    pad_top = max(0, -offset)
    pad_left = max(0, -offset)
    pad_bottom = max(0, end_height - (height - 1))
    pad_right = max(0, end_width - (width - 1))
    if np.issubdtype(values.dtype, np.floating):
        constant = -np.inf
    else:
        constant = INT8_MIN
    padded = np.pad(
        values,
        ((0, 0), (pad_top, pad_bottom), (pad_left, pad_right)),
        mode="constant",
        constant_values=constant,
    )
    view = np.lib.stride_tricks.sliding_window_view(padded, (size, size), axis=(1, 2))
    return view[:, start_height::stride, start_width::stride, :size, :size][:, :out_height, :out_width].max(axis=(-1, -2))


def route_float(tensors: list[np.ndarray], references: list[int], layer_index: int, groups: int, group_id: int) -> np.ndarray:
    """执行浮点 route 拼接和分组选择。"""

    selected = [tensors[resolve_reference(reference, layer_index)] for reference in references]
    if any(item.shape[1:] != selected[0].shape[1:] for item in selected):
        raise Int8ForwardError(f"route {layer_index} 空间尺寸不一致")
    merged = selected[0] if len(selected) == 1 else np.concatenate(selected, axis=0)
    if groups == 1:
        return merged
    if len(selected) != 1 or merged.shape[0] % groups != 0 or not 0 <= group_id < groups:
        raise Int8ForwardError(f"route {layer_index} 分组参数无效")
    channels_per_group = merged.shape[0] // groups
    return merged[group_id * channels_per_group : (group_id + 1) * channels_per_group]


def rescale_tensor(tensor: Tensor, target_scale: float) -> Tensor:
    """把 INT8 张量重定标到 route 统一 scale。"""

    if math.isclose(tensor.scale, target_scale, rel_tol=0.0, abs_tol=0.0):
        return tensor
    values = round_away_array(tensor.values.astype(np.float64) * tensor.scale / target_scale)
    return Tensor(saturate_array(values), target_scale)


def route_int8(tensors: list[Tensor], references: list[int], layer_index: int, groups: int, group_id: int) -> Tensor:
    """执行 INT8 route，并以最大输入 scale 统一拼接张量。"""

    selected = [tensors[resolve_reference(reference, layer_index)] for reference in references]
    if any(item.values.shape[1:] != selected[0].values.shape[1:] for item in selected):
        raise Int8ForwardError(f"route {layer_index} 空间尺寸不一致")
    target_scale = max(item.scale for item in selected)
    merged = selected[0] if len(selected) == 1 else Tensor(
        np.concatenate([rescale_tensor(item, target_scale).values for item in selected], axis=0), target_scale
    )
    if groups == 1:
        return merged
    if len(selected) != 1 or merged.values.shape[0] % groups != 0 or not 0 <= group_id < groups:
        raise Int8ForwardError(f"route {layer_index} 分组参数无效")
    channels_per_group = merged.values.shape[0] // groups
    start = group_id * channels_per_group
    return Tensor(merged.values[start : start + channels_per_group], merged.scale)


def metric(float_values: np.ndarray, integer_values: Tensor) -> dict[str, Any]:
    """计算整数张量反量化相对浮点参考的误差。"""

    dequantized = integer_values.values.astype(np.float64) * integer_values.scale
    reference = float_values.astype(np.float64)
    if not np.all(np.isfinite(reference)) or not np.all(np.isfinite(dequantized)):
        raise Int8ForwardError("浮点或反量化张量含 NaN/Inf")
    difference = dequantized - reference
    squared_reference = float(np.sum(reference * reference))
    return {
        "elements": int(reference.size),
        "float_min": float(np.min(reference)),
        "float_max": float(np.max(reference)),
        "dequant_min": float(np.min(dequantized)),
        "dequant_max": float(np.max(dequantized)),
        "max_absolute_error": float(np.max(np.abs(difference))),
        "mae": float(np.mean(np.abs(difference))),
        "rmse": float(math.sqrt(np.mean(difference * difference))),
        "relative_l2_error": float(math.sqrt(np.sum(difference * difference) / squared_reference)) if squared_reference else 0.0,
        "saturated_count": int(np.count_nonzero((integer_values.values == INT8_MIN) | (integer_values.values == INT8_MAX))),
    }


def forward_one(
    image_chw: np.ndarray,
    sections: list[Section],
    float_layers: dict[int, FloatLayer],
    package_layers: dict[int, PackageLayer],
    activation_scales: dict[int, float],
) -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
    """执行单张图的浮点和 INT8 双路径前向。"""

    metrics: dict[int, dict[str, Any]] = {}
    integer_stats: dict[int, dict[str, Any]] = {}
    float_tensors: list[np.ndarray] = []
    int_tensors: list[Tensor] = []
    float_current = image_chw.astype(np.float64)
    int_current = Tensor(saturate_array(round_away_array(float_current / INPUT_SCALE)), INPUT_SCALE)
    for layer_index, section in enumerate(sections[1:]):
        kind = section.kind
        options = section.options
        if kind == "convolutional":
            size = cfg_int(options, "size")
            stride, padding = convolution_parameters(options, size)
            float_layer = float_layers.get(layer_index)
            package_layer = package_layers.get(layer_index)
            if float_layer is None or package_layer is None:
                raise Int8ForwardError(f"卷积层 {layer_index} 缺少权重参数")
            float_current = conv_float(float_current, float_layer, stride, padding)
            activation = options.get("activation", "linear").lower()
            if activation == "leaky":
                float_current = np.where(float_current >= 0.0, float_current, float_current * 0.1)
            elif activation != "linear":
                raise Int8ForwardError(f"暂不支持浮点激活: {activation}")
            if layer_index not in activation_scales:
                raise Int8ForwardError(f"卷积层 {layer_index} 缺少激活 scale")
            int_current, int_stat = conv_int8(
                int_current,
                package_layer,
                activation_scales[layer_index],
                activation,
                stride,
                padding,
            )
            integer_stats[layer_index] = int_stat
            metrics[layer_index] = metric(float_current, int_current)
        elif kind == "route":
            raw_refs = [int(item.strip(), 10) for item in options.get("layers", "").split(",") if item.strip()]
            if not raw_refs:
                raise Int8ForwardError(f"route {layer_index} 缺少 layers")
            groups = cfg_int(options, "groups", 1)
            group_id = cfg_int(options, "group_id", 0)
            float_current = route_float(float_tensors, raw_refs, layer_index, groups, group_id)
            int_current = route_int8(int_tensors, raw_refs, layer_index, groups, group_id)
        elif kind == "maxpool":
            size = cfg_int(options, "size")
            _, stride, padding = maxpool_parameters(options, size)
            float_current = maxpool(float_current, size, stride, padding)
            int_current = Tensor(maxpool(int_current.values, size, stride, padding), int_current.scale)
        elif kind == "upsample":
            stride = upsample_stride(options)
            float_current = np.repeat(np.repeat(float_current, stride, axis=1), stride, axis=2)
            int_current = Tensor(np.repeat(np.repeat(int_current.values, stride, axis=1), stride, axis=2), int_current.scale)
        elif kind == "yolo":
            metrics[layer_index] = metric(float_current, int_current)
        else:
            raise Int8ForwardError(f"前向暂不支持 cfg section: [{kind}]")
        float_tensors.append(float_current)
        int_tensors.append(int_current)
    if not metrics:
        raise Int8ForwardError("前向没有产生可比较输出")
    return metrics, {"integer_stats": integer_stats, "final_float_shape": list(float_current.shape), "final_int_shape": list(int_current.values.shape)}


def aggregate_metrics(per_sample: list[dict[int, dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    """按层聚合多张图的误差指标。"""

    result: dict[str, dict[str, Any]] = {}
    for layer_index in sorted({index for item in per_sample for index in item}):
        items = [item[layer_index] for item in per_sample]
        total_elements = sum(item["elements"] for item in items)
        total_squared = sum((item["rmse"] ** 2) * item["elements"] for item in items)
        result[str(layer_index)] = {
            "sample_count": len(items),
            "elements": total_elements,
            "float_min": min(item["float_min"] for item in items),
            "float_max": max(item["float_max"] for item in items),
            "dequant_min": min(item["dequant_min"] for item in items),
            "dequant_max": max(item["dequant_max"] for item in items),
            "max_absolute_error": max(item["max_absolute_error"] for item in items),
            "mae_mean_by_sample": float(np.mean([item["mae"] for item in items])),
            "rmse": float(math.sqrt(total_squared / total_elements)),
            "relative_l2_error_mean_by_sample": float(np.mean([item["relative_l2_error"] for item in items])),
            "saturated_count": sum(item["saturated_count"] for item in items),
        }
    return result


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    """执行绑定、前向和报告生成。"""

    cfg = require_file(args.cfg, "cfg")
    weights = require_file(args.weights, "weights")
    package = require_file(args.weight_package, "weight_package")
    weight_report_path = require_file(args.weight_report, "weight_report")
    activation_report_path = require_file(args.activation_report, "activation_report")
    calibration_list = require_file(args.calibration_list, "calibration_list")
    sections = parse_cfg_sections(cfg)
    weight_report = json.loads(weight_report_path.read_text(encoding="utf-8"))
    package_binding = weight_report.get("package", {})
    if package_binding.get("sha256", "").lower() != sha256_file(package):
        raise Int8ForwardError("权重量化报告与实际 GFINT8W1 包 SHA 不一致")
    if weight_report.get("inputs", {}).get("weights", {}).get("sha256", "").lower() != sha256_file(weights):
        raise Int8ForwardError("权重量化报告与实际浮点权重 SHA 不一致")
    activation_scales = load_activation_scales(activation_report_path, cfg, weights, calibration_list)
    samples = read_calibration_list(calibration_list, args.sample_count)
    package_header, package_layers = parse_package(package)
    float_layers = read_fused_float_layers(cfg, weights)
    conv_indices = {index for index, section in enumerate(sections[1:]) if section.kind == "convolutional"}
    if set(package_layers) != conv_indices or set(float_layers) != conv_indices or set(activation_scales) != conv_indices:
        raise Int8ForwardError("cfg、权重包、浮点权重和激活 scale 的卷积层集合不一致")
    if package_header["width"] != 416 or package_header["height"] != 416 or package_header["channels"] != 3:
        raise Int8ForwardError("当前证据只接受 tiny416 的 GFINT8W1 包")
    per_sample_metrics: list[dict[int, dict[str, Any]]] = []
    per_sample_integer_stats: list[dict[int, dict[str, Any]]] = []
    sample_records = []
    for index, image_path in enumerate(samples):
        image_chw = load_image_chw(image_path, package_header["width"], package_header["height"])
        metrics, details = forward_one(image_chw, sections, float_layers, package_layers, activation_scales)
        per_sample_metrics.append(metrics)
        per_sample_integer_stats.append(details["integer_stats"])
        sample_records.append(
            {
                "sample_index": index,
                "path": str(image_path),
                "sha256": sha256_file(image_path),
                "metrics": {str(layer): value for layer, value in sorted(metrics.items())},
                "integer_stats": {str(layer): value for layer, value in sorted(details["integer_stats"].items())},
            }
        )
    layer_metrics = aggregate_metrics(per_sample_metrics)
    conv_stats = [stat for item in per_sample_integer_stats for stat in item.values()]
    report = {
        "schema_version": "s1_t02_d2_int8_forward_v1",
        "status": "INT8_INTEGER_FORWARD_COMPLETE_FLOAT_REFERENCE_COMPARISON_PENDING_REVIEW",
        "generated_at_utc8": utc8_now(),
        "tool": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__).resolve())},
        "scope": "tiny416 训练完成权重的 CPU INT8 整网参考前向；不含训练、检测头解码、NMS、mAP 或 FPGA 部署",
        "inputs": {
            "cfg": {"path": str(cfg), "sha256": sha256_file(cfg)},
            "weights": {"path": str(weights), "sha256": sha256_file(weights)},
            "weight_package": {"path": str(package), "sha256": sha256_file(package)},
            "weight_report": {"path": str(weight_report_path), "sha256": sha256_file(weight_report_path)},
            "activation_report": {"path": str(activation_report_path), "sha256": sha256_file(activation_report_path)},
            "calibration_list": {"path": str(calibration_list), "sha256": sha256_file(calibration_list), "total_samples": EXPECTED_CALIBRATION_SAMPLES},
        },
        "network": {"width": package_header["width"], "height": package_header["height"], "channels": package_header["channels"], "convolution_count": len(conv_indices)},
        "numeric_policy": {
            "input_scale": INPUT_SCALE,
            "int8_range": [INT8_MIN, INT8_MAX],
            "zero_point": 0,
            "weight_scale": "GFINT8W1 per-output-channel symmetric",
            "bias_domain": "round(fused_bias / (input_scale * weight_scale)) into accumulator",
            "accumulator": "INT64 exact reference with separate raw/bias/with-bias INT32 range audit",
            "int64_boundary_proof": "输入与权重先验证在 [-127,127]；逐乘积界为 127*127，原始累加器界为 K*127*127，并在 INT64 矩阵乘法、bias 映射和加 bias 前分别证明边界",
            "rounding": "half_away_from_zero",
            "activation": "leaky slope 0.1 before output requantization",
            "route_rescale": "all route inputs rescaled to the maximum input tensor scale",
            "saturation": "[-127,127]",
        },
        "sample_count": len(samples),
        "samples": sample_records,
        "layer_metrics": layer_metrics,
        "integer_accumulator_summary": {
            "int32_overflow_count": sum(item["int32_overflow_count"] for item in conv_stats),
            "int64_overflow_counts": {
                "product": sum(item["product_int64_overflow_count"] for item in conv_stats),
                "raw_accumulator": sum(item["raw_accumulator_int64_overflow_count"] for item in conv_stats),
                "bias_accumulator": sum(item["bias_accumulator_int64_overflow_count"] for item in conv_stats),
                "with_bias": sum(item["accumulator_with_bias_int64_overflow_count"] for item in conv_stats),
            },
            "int32_overflow_counts": {
                "raw_accumulator": sum(item["raw_accumulator_int32_overflow_count"] for item in conv_stats),
                "bias_accumulator": sum(item["bias_accumulator_int32_overflow_count"] for item in conv_stats),
                "with_bias": sum(item["accumulator_with_bias_int32_overflow_count"] for item in conv_stats),
            },
            "raw_accumulator_min": min(item["raw_accumulator_min"] for item in conv_stats),
            "raw_accumulator_max": max(item["raw_accumulator_max"] for item in conv_stats),
            "accumulator_with_bias_min": min(item["accumulator_with_bias_min"] for item in conv_stats),
            "accumulator_with_bias_max": max(item["accumulator_with_bias_max"] for item in conv_stats),
            "saturated_output_count": sum(item["saturated_count"] for item in conv_stats),
        },
        "limitations": [
            "浮点参考与 INT8 参考共享本工具的固定输入预处理，尚未用 Darknet 二进制逐层导出做逐值绑定",
            "route 使用最大输入 scale 统一重定标；这是本轮明确的参考语义，不等同于已冻结 FPGA 接口",
            "未执行 YOLO 解码、sigmoid/exp、NMS、mAP、鲁棒性、Vivado 综合、时序、资源或上板测试",
            "本报告需独立 Reviewer 复核后才能作为 G2 候选证据，不构成 G4/G5 或阶段1通过",
        ],
    }
    return report


def write_summary(report: dict[str, Any], path: Path) -> None:
    """写出可读的整数前向摘要。"""

    aggregate = report["integer_accumulator_summary"]
    lines = [
        "# S1-T02-D2 tiny416 INT8 整数前向摘要",
        "",
        f"- status: `{report['status']}`",
        f"- sample count: `{report['sample_count']}` / train-only calibration list 512",
        f"- INT32 overflow count: `{aggregate['int32_overflow_count']}`",
        f"- INT64 overflow counts (product/raw/bias/with-bias): `{aggregate['int64_overflow_counts']['product']}` / `{aggregate['int64_overflow_counts']['raw_accumulator']}` / `{aggregate['int64_overflow_counts']['bias_accumulator']}` / `{aggregate['int64_overflow_counts']['with_bias']}`",
        f"- INT32 overflow counts (raw/bias/with-bias): `{aggregate['int32_overflow_counts']['raw_accumulator']}` / `{aggregate['int32_overflow_counts']['bias_accumulator']}` / `{aggregate['int32_overflow_counts']['with_bias']}`",
        f"- accumulator range with bias: `{aggregate['accumulator_with_bias_min']}` .. `{aggregate['accumulator_with_bias_max']}`",
        f"- saturated INT8 output count: `{aggregate['saturated_output_count']}`",
        "",
        "| layer | samples | RMSE | relative L2 mean | max abs error | saturation |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for layer, item in report["layer_metrics"].items():
        lines.append(
            f"| {layer} | {item['sample_count']} | {item['rmse']:.8g} | "
            f"{item['relative_l2_error_mean_by_sample']:.8g} | {item['max_absolute_error']:.8g} | {item['saturated_count']} |"
        )
    lines.extend(["", "该结果是 CPU INT8 参考前向和共享预处理下的浮点对照，不含检测精度或 FPGA 部署结论。", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数。"""

    parser = argparse.ArgumentParser(description="生成 tiny416 INT8 整数前向参考报告")
    parser.add_argument("--cfg", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--weight-package", type=Path, required=True)
    parser.add_argument("--weight-report", type=Path, required=True)
    parser.add_argument("--activation-report", type=Path, required=True)
    parser.add_argument("--calibration-list", type=Path, required=True)
    parser.add_argument("--sample-count", type=int, default=4)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """执行整数前向并在失败时不写入伪通过报告。"""

    args = build_parser().parse_args(argv)
    try:
        report = build_report(args)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        write_summary(report, args.summary)
        print(json.dumps({"status": report["status"], "sample_count": report["sample_count"], "report": str(args.report)}, ensure_ascii=False, indent=2))
        return 0
    except (Int8ForwardError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"D2_INT8_FORWARD_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
