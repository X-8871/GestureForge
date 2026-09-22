"""S1-T02-D2 的 Darknet 权重解析、BN 折叠和 INT8 权重量化参考。

本模块只生成可复核的权重级中间产物，不执行训练、激活校准、整网推理或检测
指标评估。激活 scale、累加器 bias 的最终部署域和整网误差仍需后续任务绑定。
"""

from __future__ import annotations

import argparse
from array import array
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import subprocess
import sys
from typing import Any


INT8_MIN = -127
INT8_MAX = 127
INPUT_SCALE = 1.0 / 127.0
BN_EPSILON = 1.0e-5
PACKAGE_MAGIC = b"GFINT8W1"
PACKAGE_VERSION = 1
SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")


class Int8WeightReferenceError(ValueError):
    """表示输入绑定或权重解析失败。"""


@dataclass(frozen=True)
class ConvolutionSpec:
    """记录 cfg 中一个卷积层的权重布局。"""

    layer_index: int
    filters: int
    input_channels: int
    groups: int
    size: int
    batch_normalize: bool
    activation: str
    weight_count: int

    @property
    def channels_per_group(self) -> int:
        """返回每个分组看到的输入通道数。"""

        return self.input_channels // self.groups


@dataclass(frozen=True)
class NetworkSpec:
    """记录模型输入和所有卷积层。"""

    width: int
    height: int
    channels: int
    layer_channels: tuple[int, ...]
    convolutions: tuple[ConvolutionSpec, ...]


@dataclass(frozen=True)
class QuantizedLayer:
    """记录一个卷积层的折叠参数、量化权重和误差统计。"""

    spec: ConvolutionSpec
    source_weight_offset: int
    scales: tuple[float, ...]
    fused_biases: tuple[float, ...]
    quantized_weights: bytes
    statistics: dict[str, Any]


def sha256_bytes(value: bytes) -> str:
    """计算字节串的 SHA-256。"""

    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    """以二进制方式计算文件 SHA-256。"""

    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise Int8WeightReferenceError(f"文件不可读取: {path}: {exc}") from exc
    return digest.hexdigest()


def _utc8_now() -> str:
    """返回东八区 ISO-8601 时间。"""

    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _read_utf8(path: Path) -> str:
    """读取 UTF-8 文本并统一转换为领域错误。"""

    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise Int8WeightReferenceError(f"UTF-8 文件不可读取: {path}: {exc}") from exc


def _parse_cfg_sections(path: Path) -> list[tuple[str, dict[str, str]]]:
    """解析 Darknet cfg 的 section 和键值。"""

    sections: list[tuple[str, dict[str, str]]] = []
    current_name: str | None = None
    current: dict[str, str] = {}
    for line_number, raw_line in enumerate(_read_utf8(path).splitlines(), 1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            if current_name is not None:
                sections.append((current_name, current))
            current_name = line[1:-1].strip().lower()
            if not current_name:
                raise Int8WeightReferenceError(f"cfg 第 {line_number} 行 section 名为空")
            current = {}
            continue
        if current_name is None or "=" not in line:
            raise Int8WeightReferenceError(f"cfg 第 {line_number} 行不是合法键值")
        key, value = line.split("=", 1)
        key = key.strip().lower()
        value = value.strip()
        if not key or not value:
            raise Int8WeightReferenceError(f"cfg 第 {line_number} 行键值为空")
        if key in current:
            raise Int8WeightReferenceError(f"cfg 第 {line_number} 行重复字段: {key}")
        current[key] = value
    if current_name is not None:
        sections.append((current_name, current))
    if not sections or sections[0][0] != "net":
        raise Int8WeightReferenceError("cfg 第一段必须是 [net]")
    return sections


def _cfg_int(options: dict[str, str], key: str, default: int | None = None) -> int:
    """读取严格十进制 cfg 整数。"""

    value = options.get(key)
    if value is None:
        if default is None:
            raise Int8WeightReferenceError(f"cfg 缺少字段: {key}")
        return default
    try:
        parsed = int(value, 10)
    except ValueError as exc:
        raise Int8WeightReferenceError(f"cfg 字段不是整数: {key}={value}") from exc
    return parsed


def _resolve_route_layer(reference: int, layer_index: int) -> int:
    """把 route 的相对或绝对层号解析为零基索引。"""

    return layer_index + reference if reference < 0 else reference


def parse_cfg(path: Path) -> NetworkSpec:
    """解析 tiny cfg 的通道流并提取卷积权重布局。"""

    sections = _parse_cfg_sections(path)
    net = sections[0][1]
    width = _cfg_int(net, "width")
    height = _cfg_int(net, "height")
    channels = _cfg_int(net, "channels")
    if min(width, height, channels) <= 0:
        raise Int8WeightReferenceError("cfg net 的 width/height/channels 必须为正数")

    current_channels = channels
    layer_channels: list[int] = []
    convolutions: list[ConvolutionSpec] = []
    for layer_index, (kind, options) in enumerate(sections[1:]):
        if kind == "convolutional":
            filters = _cfg_int(options, "filters")
            groups = _cfg_int(options, "groups", 1)
            size = _cfg_int(options, "size")
            if filters <= 0 or groups <= 0 or size <= 0:
                raise Int8WeightReferenceError(f"卷积层 {layer_index} 的 filters/groups/size 无效")
            if current_channels % groups != 0:
                raise Int8WeightReferenceError(f"卷积层 {layer_index} 输入通道不能被 groups 整除")
            batch_normalize = _cfg_int(options, "batch_normalize", 0) == 1
            activation = options.get("activation", "linear")
            weight_count = filters * (current_channels // groups) * size * size
            convolutions.append(
                ConvolutionSpec(
                    layer_index=layer_index,
                    filters=filters,
                    input_channels=current_channels,
                    groups=groups,
                    size=size,
                    batch_normalize=batch_normalize,
                    activation=activation,
                    weight_count=weight_count,
                )
            )
            current_channels = filters
        elif kind == "route":
            raw_layers = options.get("layers")
            if raw_layers is None:
                raise Int8WeightReferenceError(f"route 层 {layer_index} 缺少 layers")
            try:
                references = [int(item.strip(), 10) for item in raw_layers.split(",") if item.strip()]
            except ValueError as exc:
                raise Int8WeightReferenceError(f"route 层 {layer_index} 的 layers 无效") from exc
            if not references:
                raise Int8WeightReferenceError(f"route 层 {layer_index} 没有引用层")
            resolved = [_resolve_route_layer(item, layer_index) for item in references]
            if any(item < 0 or item >= len(layer_channels) for item in resolved):
                raise Int8WeightReferenceError(f"route 层 {layer_index} 引用了不存在的层")
            current_channels = sum(layer_channels[item] for item in resolved)
            groups = _cfg_int(options, "groups", 1)
            group_id = _cfg_int(options, "group_id", 0)
            if groups <= 0 or group_id < 0 or group_id >= groups:
                raise Int8WeightReferenceError(f"route 层 {layer_index} 的 groups/group_id 无效")
            if groups != 1:
                if len(resolved) != 1 or current_channels % groups != 0:
                    raise Int8WeightReferenceError(f"route 层 {layer_index} 的分组布局无效")
                current_channels //= groups
        elif kind in {"maxpool", "upsample", "yolo", "shortcut", "dropout", "softmax"}:
            pass
        else:
            raise Int8WeightReferenceError(f"暂不支持的 cfg section: [{kind}]")
        if current_channels <= 0:
            raise Int8WeightReferenceError(f"cfg 层 {layer_index} 产生了非正通道数")
        layer_channels.append(current_channels)

    return NetworkSpec(width, height, channels, tuple(layer_channels), tuple(convolutions))


def _read_float_array(blob: bytes, offset: int, count: int, field: str) -> tuple[array, int]:
    """从 Darknet 权重字节流读取 little-endian float32 数组。"""

    if count < 0:
        raise Int8WeightReferenceError(f"读取 {field} 时 count 为负数")
    end = offset + count * 4
    if offset < 0 or end > len(blob):
        raise Int8WeightReferenceError(f"权重文件在读取 {field} 时提前结束")
    values = array("f")
    values.frombytes(blob[offset:end])
    if sys.byteorder != "little":
        values.byteswap()
    if len(values) != count:
        raise Int8WeightReferenceError(f"权重文件 {field} 数量不一致")
    if any(not math.isfinite(value) for value in values):
        raise Int8WeightReferenceError(f"权重文件 {field} 含 NaN/Inf")
    return values, end


def _round_away_from_zero(value: float) -> int:
    """执行正负对称、半数远离零的舍入。"""

    magnitude = math.floor(abs(value) + 0.5)
    return magnitude if value >= 0.0 else -magnitude


def _quantize_layer(
    spec: ConvolutionSpec,
    source_weight_offset: int,
    raw_biases: array,
    raw_weights: array,
    bn_scales: array | None,
    rolling_mean: array | None,
    rolling_variance: array | None,
) -> QuantizedLayer:
    """折叠 BN 并按输出通道量化一层卷积权重。"""

    per_filter = spec.weight_count // spec.filters
    scales: list[float] = []
    fused_biases: list[float] = []
    quantized = bytearray(spec.weight_count)
    absolute_error_max = 0.0
    squared_error = 0.0
    squared_source = 0.0
    saturated = 0
    nonzero = 0
    for filter_index in range(spec.filters):
        if spec.batch_normalize:
            if bn_scales is None or rolling_mean is None or rolling_variance is None:
                raise Int8WeightReferenceError(f"卷积层 {spec.layer_index} 缺少 BN 参数")
            variance = float(rolling_variance[filter_index])
            if variance + BN_EPSILON <= 0.0:
                raise Int8WeightReferenceError(f"卷积层 {spec.layer_index} BN variance 无效")
            bn_factor = float(bn_scales[filter_index]) / math.sqrt(variance + BN_EPSILON)
            fused_bias = (float(raw_biases[filter_index]) - float(rolling_mean[filter_index])) * bn_factor
        else:
            bn_factor = 1.0
            fused_bias = float(raw_biases[filter_index])
        fused_biases.append(fused_bias)

        start = filter_index * per_filter
        fused_values = [float(raw_weights[start + offset]) * bn_factor for offset in range(per_filter)]
        max_abs = max((abs(value) for value in fused_values), default=0.0)
        scale = max_abs / INT8_MAX if max_abs else INPUT_SCALE
        scales.append(scale)
        for offset, value in enumerate(fused_values):
            quantized_value = _round_away_from_zero(value / scale)
            quantized_value = max(INT8_MIN, min(INT8_MAX, quantized_value))
            if abs(quantized_value) == INT8_MAX:
                saturated += 1
            if quantized_value != 0:
                nonzero += 1
            quantized[start + offset] = quantized_value & 0xFF
            reconstructed = quantized_value * scale
            error = reconstructed - value
            absolute_error_max = max(absolute_error_max, abs(error))
            squared_error += error * error
            squared_source += value * value

    value_count = spec.weight_count
    return QuantizedLayer(
        spec=spec,
        source_weight_offset=source_weight_offset,
        scales=tuple(scales),
        fused_biases=tuple(fused_biases),
        quantized_weights=bytes(quantized),
        statistics={
            "weight_count": value_count,
            "nonzero_quantized_values": nonzero,
            "saturated_values": saturated,
            "max_absolute_error": absolute_error_max,
            "rmse": math.sqrt(squared_error / value_count) if value_count else 0.0,
            "relative_l2_error": math.sqrt(squared_error / squared_source) if squared_source else 0.0,
            "squared_error": squared_error,
            "squared_source": squared_source,
            "scale_min": min(scales),
            "scale_max": max(scales),
            "fused_bias_min": min(fused_biases),
            "fused_bias_max": max(fused_biases),
        },
    )


def parse_and_quantize(cfg_path: Path, weights_path: Path) -> tuple[NetworkSpec, tuple[int, int, int, int], tuple[QuantizedLayer, ...]]:
    """读取 cfg/weights 并生成所有卷积层的量化结果。"""

    spec = parse_cfg(cfg_path)
    try:
        blob = weights_path.read_bytes()
    except OSError as exc:
        raise Int8WeightReferenceError(f"权重文件不可读取: {weights_path}: {exc}") from exc
    if len(blob) < 16:
        raise Int8WeightReferenceError("Darknet 权重文件头不完整")
    major, minor, revision = struct.unpack_from("<3i", blob, 0)
    if major * 10 + minor >= 2:
        if len(blob) < 20:
            raise Int8WeightReferenceError("Darknet 权重文件缺少 64 位 seen")
        seen = struct.unpack_from("<q", blob, 12)[0]
        offset = 20
    else:
        seen = struct.unpack_from("<i", blob, 12)[0]
        offset = 16
    quantized_layers: list[QuantizedLayer] = []
    for conv in spec.convolutions:
        raw_biases, offset = _read_float_array(blob, offset, conv.filters, f"layer{conv.layer_index}.biases")
        bn_scales = rolling_mean = rolling_variance = None
        if conv.batch_normalize:
            bn_scales, offset = _read_float_array(blob, offset, conv.filters, f"layer{conv.layer_index}.scales")
            rolling_mean, offset = _read_float_array(blob, offset, conv.filters, f"layer{conv.layer_index}.rolling_mean")
            rolling_variance, offset = _read_float_array(blob, offset, conv.filters, f"layer{conv.layer_index}.rolling_variance")
        source_weight_offset = offset
        raw_weights, offset = _read_float_array(blob, offset, conv.weight_count, f"layer{conv.layer_index}.weights")
        quantized_layers.append(
            _quantize_layer(
                conv,
                source_weight_offset,
                raw_biases,
                raw_weights,
                bn_scales,
                rolling_mean,
                rolling_variance,
            )
        )
    if offset != len(blob):
        raise Int8WeightReferenceError(f"权重文件末尾存在未绑定字节: offset={offset}, size={len(blob)}")
    return spec, (major, minor, revision, seen), tuple(quantized_layers)


def write_package(path: Path, spec: NetworkSpec, layers: tuple[QuantizedLayer, ...]) -> None:
    """写出确定性 GFINT8W1 权重量化中间包。"""

    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("wb") as handle:
            handle.write(struct.pack("<8sIIII", PACKAGE_MAGIC, PACKAGE_VERSION, len(layers), spec.width, spec.height))
            handle.write(struct.pack("<I", spec.channels))
            for layer in layers:
                conv = layer.spec
                handle.write(
                    struct.pack(
                        "<8I",
                        conv.layer_index,
                        conv.filters,
                        conv.input_channels,
                        conv.groups,
                        conv.size,
                        conv.weight_count,
                        int(conv.batch_normalize),
                        len(layer.scales),
                    )
                )
                handle.write(struct.pack(f"<{len(layer.scales)}f", *layer.scales))
                handle.write(struct.pack(f"<{len(layer.fused_biases)}f", *layer.fused_biases))
                handle.write(layer.quantized_weights)
    except OSError as exc:
        raise Int8WeightReferenceError(f"量化包不可写入: {path}: {exc}") from exc


def _git_provenance(repository: Path) -> dict[str, Any]:
    """读取当前仓库 HEAD 和工作区状态，不把失败伪装成干净。"""

    result: dict[str, Any] = {"repository": str(repository), "head": None, "status": "unavailable"}
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repository, capture_output=True, text=True, check=False
        )
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repository, capture_output=True, text=True, check=False
        )
    except OSError:
        return result
    if head.returncode == 0:
        result["head"] = head.stdout.strip()
    if status.returncode == 0:
        result["status"] = "clean" if not status.stdout else "dirty"
    return result


def _validate_commit(value: str) -> str:
    """校验 Darknet 源 commit 的固定哈希格式。"""

    if not COMMIT_PATTERN.fullmatch(value):
        raise Int8WeightReferenceError("Darknet source commit 必须是 40 位十六进制 SHA-1")
    return value.lower()


def _calibration_binding(path: Path | None) -> dict[str, Any]:
    """绑定可选的 train-only 校准清单，但明确不读取图像。"""

    if path is None:
        return {"status": "NOT_BOUND", "path": None, "sha256": None, "nonempty_line_count": None}
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise Int8WeightReferenceError(f"校准清单不可按 UTF-8 读取: {path}: {exc}") from exc
    count = sum(1 for line in text.splitlines() if line.strip())
    return {
        "status": "BOUND_NOT_CONSUMED_BY_WEIGHT_ONLY_TOOL",
        "path": str(path),
        "sha256": sha256_bytes(raw),
        "nonempty_line_count": count,
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    """生成实际权重量化报告并写出中间包。"""

    cfg_path = args.cfg.resolve()
    weights_path = args.weights.resolve()
    output_path = args.output.resolve()
    report_path = args.report.resolve()
    summary_path = args.summary.resolve()
    calibration_path = args.calibration_list.resolve() if args.calibration_list else None
    repository = Path(__file__).resolve().parent.parent
    input_paths = [cfg_path, weights_path]
    if calibration_path is not None:
        input_paths.append(calibration_path)
    output_paths = [output_path, report_path, summary_path]
    if len({str(path) for path in input_paths + output_paths}) != len(input_paths) + len(output_paths):
        raise Int8WeightReferenceError("输入与输出路径不能相同")
    if not cfg_path.is_file() or not weights_path.is_file():
        raise Int8WeightReferenceError("cfg 或 weights 不存在")
    if calibration_path is not None and not calibration_path.is_file():
        raise Int8WeightReferenceError("校准清单不存在")
    source_commit = _validate_commit(args.darknet_source_commit)
    spec, header, layers = parse_and_quantize(cfg_path, weights_path)
    write_package(output_path, spec, layers)
    layer_reports = []
    for layer in layers:
        conv = layer.spec
        layer_reports.append(
            {
                "layer_index": conv.layer_index,
                "filters": conv.filters,
                "input_channels": conv.input_channels,
                "groups": conv.groups,
                "size": conv.size,
                "batch_normalize": conv.batch_normalize,
                "activation": conv.activation,
                "weight_count": conv.weight_count,
                "source_weight_offset": layer.source_weight_offset,
                "statistics": layer.statistics,
            }
        )
    total_weights = sum(item.spec.weight_count for item in layers)
    total_rmse_energy = sum(item.statistics["rmse"] ** 2 * item.spec.weight_count for item in layers)
    total_error_energy = sum(item.statistics["squared_error"] for item in layers)
    total_source_energy = sum(item.statistics["squared_source"] for item in layers)
    report = {
        "schema_version": "s1-t02-d2-int8-weight-reference-v1",
        "task": "S1-T02-D2",
        "status": "INT8_WEIGHT_REFERENCE_GENERATED_ACTIVATION_SCALE_PENDING",
        "generated_utc8": _utc8_now(),
        "code": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256_file(Path(__file__).resolve()),
            "repository": _git_provenance(repository),
        },
        "inputs": {
            "cfg": {"path": str(cfg_path), "sha256": sha256_file(cfg_path)},
            "weights": {"path": str(weights_path), "sha256": sha256_file(weights_path), "bytes": weights_path.stat().st_size},
            "darknet_source_commit": source_commit,
            "calibration": _calibration_binding(calibration_path),
        },
        "darknet_header": {"major": header[0], "minor": header[1], "revision": header[2], "seen": header[3]},
        "model": {
            "width": spec.width,
            "height": spec.height,
            "channels": spec.channels,
            "convolution_count": len(layers),
            "weight_count": total_weights,
        },
        "numeric_policy": {
            "int8_range": [INT8_MIN, INT8_MAX],
            "zero_point": 0,
            "input_scale": INPUT_SCALE,
            "weight_quantization": "per-output-channel symmetric",
            "bn_fold": "inference_fused_before_weight_quantization",
            "bn_epsilon": BN_EPSILON,
            "rounding": "half_away_from_zero",
            "saturation": [INT8_MIN, INT8_MAX],
            "bias_domain": "folded_float_before_activation_requantization",
        },
        "activation_calibration": {
            "status": "NOT_EXECUTED",
            "reason": "本工具只生成权重量化中间包，不执行图像前向或逐层激活统计",
        },
        "package": {
            "path": str(output_path),
            "sha256": sha256_file(output_path),
            "bytes": output_path.stat().st_size,
            "format": "GFINT8W1",
            "version": PACKAGE_VERSION,
        },
        "layers": layer_reports,
        "aggregate_error": {
            "rmse": math.sqrt(total_rmse_energy / total_weights) if total_weights else 0.0,
            "relative_l2_error": math.sqrt(total_error_energy / total_source_energy) if total_source_energy else 0.0,
            "max_absolute_error": max(item.statistics["max_absolute_error"] for item in layers),
            "saturated_values": sum(item.statistics["saturated_values"] for item in layers),
        },
        "limitations": [
            "本报告只证明 Darknet 权重头、cfg 卷积布局、BN 折叠和权重量化可复现。",
            "没有计算逐层激活 scale、累加器 bias 的实际输入域、整数前向、检测头输出或 mAP。",
            "量化包不是可直接烧录的 FPGA 部署封装，不关闭 D3、D6 G0、G4/G5 或阶段1。",
        ],
    }
    return report


def _summary_text(report: dict[str, Any]) -> str:
    """生成简短中文摘要。"""

    model = report["model"]
    package = report["package"]
    aggregate = report["aggregate_error"]
    return "\n".join(
        [
            "# S1-T02-D2 tiny416 INT8 权重量化参考",
            "",
            f"状态：`{report['status']}`。",
            f"模型：{model['width']}×{model['height']}，卷积层 {model['convolution_count']} 个，权重值 {model['weight_count']} 个。",
            f"权重包：`{package['path']}`，{package['bytes']} bytes，SHA-256=`{package['sha256']}`。",
            f"聚合权重量化 RMSE=`{aggregate['rmse']}`，最大绝对误差=`{aggregate['max_absolute_error']}`，饱和值数量=`{aggregate['saturated_values']}`。",
            "BN 已按 Darknet 推理 epsilon=1e-5 折叠；权重按输出通道对称量化到 [-127,127]。",
            "激活校准、整数前向、检测头和 mAP 未执行；该证据不代表 INT8 整网或阶段1通过。",
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    """执行命令行入口。"""

    parser = argparse.ArgumentParser(description="生成 Darknet BN 折叠和 INT8 权重量化参考包")
    parser.add_argument("--cfg", type=Path, required=True, help="Darknet cfg 路径")
    parser.add_argument("--weights", type=Path, required=True, help="Darknet weights 路径")
    parser.add_argument("--output", type=Path, required=True, help="GFINT8W1 权重包输出路径")
    parser.add_argument("--report", type=Path, required=True, help="JSON 报告输出路径")
    parser.add_argument("--summary", type=Path, required=True, help="Markdown 摘要输出路径")
    parser.add_argument("--darknet-source-commit", required=True, help="Darknet 源 commit SHA-1")
    parser.add_argument("--calibration-list", type=Path, help="可选的 train-only 校准清单，仅绑定不读取图像")
    args = parser.parse_args(argv)
    try:
        report = build_report(args)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        args.summary.write_text(_summary_text(report), encoding="utf-8")
    except (Int8WeightReferenceError, OSError, ValueError) as exc:
        print(f"D2_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"status": report["status"], "report": str(args.report), "package": report["package"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
