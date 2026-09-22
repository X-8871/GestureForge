"""S1-T02-D2 的 Darknet 浮点逐层输出绑定检查器。

本模块消费隔离 Darknet hook 导出的 float32 卷积层张量，并与独立
Python 浮点参考逐层比较。它不训练、不修改权重、不生成部署文件，
也不把浮点逐值核对误写成 INT8 精度或 FPGA 验收。
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np

try:
    from s1_t02_d2_int8_forward import (
        cfg_int,
        conv_float,
        convolution_parameters,
        load_image_chw,
        maxpool,
        maxpool_parameters,
        parse_cfg_sections,
        read_fused_float_layers,
        resolve_reference,
        route_float,
        sha256_file,
        upsample_stride,
    )
except ModuleNotFoundError:
    from verification.s1_t02_d2_int8_forward import (
        cfg_int,
        conv_float,
        convolution_parameters,
        load_image_chw,
        maxpool,
        maxpool_parameters,
        parse_cfg_sections,
        read_fused_float_layers,
        resolve_reference,
        route_float,
        sha256_file,
        upsample_stride,
    )


EXPECTED_SAMPLE_COUNT = 512
REQUIRED_COLUMNS = {"sample_index", "layer_index", "output_count", "file"}


class FloatBindingError(ValueError):
    """表示逐层浮点绑定输入或结果无效。"""


@dataclass(frozen=True)
class DumpRecord:
    """记录一个 Darknet dump 文件。"""

    sample_index: int
    layer_index: int
    output_count: int
    path: Path


def utc8_now() -> str:
    """返回东八区时间。"""

    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def require_file(path: Path, field: str) -> Path:
    """校验普通文件并返回绝对路径。"""

    resolved = path.resolve()
    if not resolved.is_file():
        raise FloatBindingError(f"{field} 不是普通文件: {resolved}")
    return resolved


def parse_dump_index(index_path: Path, dump_dir: Path, expected_layers: set[int], sample_count: int) -> dict[tuple[int, int], DumpRecord]:
    """严格读取 dump 索引并核对每个二进制文件长度。"""

    records: dict[tuple[int, int], DumpRecord] = {}
    try:
        handle = index_path.open("r", encoding="utf-8", newline="")
    except OSError as exc:
        raise FloatBindingError(f"dump 索引不可读取: {index_path}: {exc}") from exc
    with handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - columns)
        if missing:
            raise FloatBindingError(f"dump 索引缺少字段: {missing}")
        for row_number, row in enumerate(reader, 2):
            try:
                sample_index = int(row["sample_index"], 10)
                layer_index = int(row["layer_index"], 10)
                output_count = int(row["output_count"], 10)
            except (KeyError, TypeError, ValueError) as exc:
                raise FloatBindingError(f"dump 索引第 {row_number} 行整数无效") from exc
            if not 0 <= sample_index < sample_count:
                raise FloatBindingError(f"dump 索引第 {row_number} 行 sample_index 越界")
            if layer_index not in expected_layers or output_count <= 0:
                raise FloatBindingError(f"dump 索引第 {row_number} 行层号或元素数无效")
            path = Path(row["file"]).resolve()
            expected_name = dump_dir / f"sample_{sample_index:04d}_layer_{layer_index:02d}.bin"
            if path != expected_name.resolve():
                raise FloatBindingError(f"dump 索引第 {row_number} 行路径不符合固定命名: {path}")
            if not path.is_file() or path.stat().st_size != output_count * 4:
                raise FloatBindingError(f"dump 文件不存在或长度不符: {path}")
            key = (sample_index, layer_index)
            if key in records:
                raise FloatBindingError(f"dump 索引重复: sample={sample_index}, layer={layer_index}")
            records[key] = DumpRecord(sample_index, layer_index, output_count, path)
    expected = {(sample, layer) for sample in range(sample_count) for layer in expected_layers}
    if set(records) != expected:
        missing = sorted(expected - set(records))
        extra = sorted(set(records) - expected)
        raise FloatBindingError(f"dump 集合不完整: missing={missing[:5]}, extra={extra[:5]}")
    return records


def read_sample_paths(calibration_list: Path, sample_count: int) -> list[Path]:
    """读取并校验固定 train-only 清单的前 sample_count 项。"""

    try:
        lines = [line.strip() for line in calibration_list.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, UnicodeError) as exc:
        raise FloatBindingError(f"校准清单不可读取: {calibration_list}: {exc}") from exc
    if len(lines) != EXPECTED_SAMPLE_COUNT or len({line.casefold() for line in lines}) != len(lines):
        raise FloatBindingError("校准清单必须是 512 行且无重复")
    if not 0 < sample_count <= EXPECTED_SAMPLE_COUNT:
        raise FloatBindingError("sample_count 必须位于 1..512")
    paths = [Path(line).resolve() for line in lines[:sample_count]]
    if any(not path.is_file() for path in paths):
        raise FloatBindingError("校准清单包含不存在图像")
    return paths


def float_forward_outputs(image_chw: np.ndarray, sections: list[Any], layers: dict[int, Any]) -> dict[int, np.ndarray]:
    """按 cfg 执行独立 Python 浮点参考并返回每层输出。"""

    current = image_chw.astype(np.float64)
    outputs: list[np.ndarray] = []
    convolution_outputs: dict[int, np.ndarray] = {}
    for layer_index, section in enumerate(sections[1:]):
        kind = section.kind
        options = section.options
        if kind == "convolutional":
            stride, padding = convolution_parameters(options, cfg_int(options, "size"))
            current = conv_float(current, layers[layer_index], stride, padding)
            activation = options.get("activation", "linear").lower()
            if activation == "leaky":
                current = np.where(current >= 0.0, current, current * 0.1)
            elif activation != "linear":
                raise FloatBindingError(f"暂不支持浮点激活: {activation}")
            convolution_outputs[layer_index] = current
        elif kind == "route":
            raw_refs = [int(item.strip(), 10) for item in options.get("layers", "").split(",") if item.strip()]
            if not raw_refs:
                raise FloatBindingError(f"route {layer_index} 缺少 layers")
            current = route_float(
                outputs,
                raw_refs,
                layer_index,
                cfg_int(options, "groups", 1),
                cfg_int(options, "group_id", 0),
            )
        elif kind == "maxpool":
            size = cfg_int(options, "size")
            _, stride, padding = maxpool_parameters(options, size)
            current = maxpool(current, size, stride, padding)
        elif kind == "upsample":
            stride = upsample_stride(options)
            current = np.repeat(np.repeat(current, stride, axis=1), stride, axis=2)
        elif kind == "yolo":
            pass
        else:
            raise FloatBindingError(f"暂不支持 cfg section: [{kind}]")
        outputs.append(current)
    return convolution_outputs


def compare_dump(expected: np.ndarray, actual: np.ndarray) -> dict[str, Any]:
    """计算 Darknet float32 dump 与 Python 浮点参考的差异。"""

    if expected.size != actual.size:
        raise FloatBindingError(f"输出元素数量不一致: expected={expected.size}, actual={actual.size}")
    expected = expected.astype(np.float64)
    actual = actual.astype(np.float64)
    if not np.all(np.isfinite(expected)) or not np.all(np.isfinite(actual)):
        raise FloatBindingError("逐层输出含 NaN/Inf")
    difference = actual - expected
    squared = float(np.sum(expected * expected))
    return {
        "elements": int(expected.size),
        "max_absolute_error": float(np.max(np.abs(difference))),
        "mean_absolute_error": float(np.mean(np.abs(difference))),
        "rmse": float(math.sqrt(np.mean(difference * difference))),
        "relative_l2_error": float(math.sqrt(np.sum(difference * difference) / squared)) if squared else 0.0,
        "expected_min": float(np.min(expected)),
        "expected_max": float(np.max(expected)),
        "actual_min": float(np.min(actual)),
        "actual_max": float(np.max(actual)),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    """执行逐层绑定并生成报告。"""

    cfg = require_file(args.cfg, "cfg")
    weights = require_file(args.weights, "weights")
    calibration_list = require_file(args.calibration_list, "calibration_list")
    dump_dir = args.dump_dir.resolve()
    index_path = require_file(dump_dir / "index.csv", "dump_index")
    darknet_executable = require_file(args.darknet_executable, "darknet_executable")
    hook_source = require_file(args.hook_source, "hook_source")
    sections = parse_cfg_sections(cfg)
    float_layers = read_fused_float_layers(cfg, weights)
    expected_layers = set(float_layers)
    samples = read_sample_paths(calibration_list, args.sample_count)
    records = parse_dump_index(index_path, dump_dir, expected_layers, args.sample_count)
    per_layer: dict[int, list[dict[str, Any]]] = {layer: [] for layer in expected_layers}
    sample_records = []
    for sample_index, image_path in enumerate(samples):
        image = load_image_chw(image_path, 416, 416)
        expected_outputs = float_forward_outputs(image, sections, float_layers)
        sample_metrics = {}
        for layer_index in sorted(expected_layers):
            record = records[(sample_index, layer_index)]
            actual = np.fromfile(record.path, dtype="<f4")
            result = compare_dump(expected_outputs[layer_index].reshape(-1), actual)
            per_layer[layer_index].append(result)
            sample_metrics[str(layer_index)] = result
        sample_records.append({"sample_index": sample_index, "path": str(image_path), "sha256": sha256_file(image_path), "layers": sample_metrics})
    layer_metrics = {}
    for layer_index, values in sorted(per_layer.items()):
        elements = sum(item["elements"] for item in values)
        layer_metrics[str(layer_index)] = {
            "sample_count": len(values),
            "elements": elements,
            "max_absolute_error": max(item["max_absolute_error"] for item in values),
            "mean_absolute_error_mean_by_sample": float(np.mean([item["mean_absolute_error"] for item in values])),
            "rmse": float(math.sqrt(sum(item["rmse"] ** 2 * item["elements"] for item in values) / elements)),
            "relative_l2_error_mean_by_sample": float(np.mean([item["relative_l2_error"] for item in values])),
            "expected_min": min(item["expected_min"] for item in values),
            "expected_max": max(item["expected_max"] for item in values),
            "actual_min": min(item["actual_min"] for item in values),
            "actual_max": max(item["actual_max"] for item in values),
        }
    return {
        "schema_version": "s1_t02_d2_darknet_float_binding_v1",
        "status": "DARKNET_FLOAT_LAYER_BINDING_COMPLETE_INT8_REFERENCE_REVIEW_PENDING",
        "generated_at_utc8": utc8_now(),
        "tool": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__).resolve())},
        "scope": "隔离 Darknet GPU float32 卷积输出与独立 Python 浮点参考的逐层绑定；不含 INT8 精度或部署验收",
        "inputs": {
            "cfg": {"path": str(cfg), "sha256": sha256_file(cfg)},
            "weights": {"path": str(weights), "sha256": sha256_file(weights)},
            "calibration_list": {"path": str(calibration_list), "sha256": sha256_file(calibration_list), "total_samples": EXPECTED_SAMPLE_COUNT},
            "sample_count": args.sample_count,
            "dump_dir": str(dump_dir),
            "dump_index": {"path": str(index_path), "sha256": sha256_file(index_path)},
            "darknet_executable": {"path": str(darknet_executable), "sha256": sha256_file(darknet_executable)},
            "hook_source": {"path": str(hook_source), "sha256": sha256_file(hook_source)},
            "darknet_source_commit": args.darknet_source_commit,
        },
        "network": {"width": 416, "height": 416, "convolution_count": len(expected_layers), "sample_count": args.sample_count},
        "layer_metrics": layer_metrics,
        "samples": sample_records,
        "limitations": [
            "Python 与 Darknet 均为浮点参考，比较不构成 INT8 检测精度或 mAP 结论",
            "尚未冻结 route scale 重定标、检测头后处理或 FPGA 部署接口",
            "独立审查需确认公式修正、INT64 边界审计与 cfg 参数绑定后，才能作为 G2 候选证据",
        ],
    }


def write_summary(report: dict[str, Any], path: Path) -> None:
    """写出逐层绑定摘要。"""

    rows = [
        "# S1-T02-D2 tiny416 Darknet 浮点逐层绑定摘要",
        "",
        f"- status: `{report['status']}`",
        f"- sample count: `{report['inputs']['sample_count']}` / train-only calibration list 512",
        "",
        "| layer | samples | RMSE | relative L2 mean | max abs error |",
        "|---:|---:|---:|---:|---:|",
    ]
    for layer, item in report["layer_metrics"].items():
        rows.append(
            f"| {layer} | {item['sample_count']} | {item['rmse']:.8g} | "
            f"{item['relative_l2_error_mean_by_sample']:.8g} | {item['max_absolute_error']:.8g} |"
        )
    rows.extend(["", "该报告只核对 Darknet float32 输出与 Python 浮点参考，不代表 INT8 或 FPGA 通过。", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(rows), encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数。"""

    parser = argparse.ArgumentParser(description="核对 Darknet float32 逐层输出")
    parser.add_argument("--cfg", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--calibration-list", type=Path, required=True)
    parser.add_argument("--dump-dir", type=Path, required=True)
    parser.add_argument("--darknet-executable", type=Path, required=True)
    parser.add_argument("--hook-source", type=Path, required=True)
    parser.add_argument("--darknet-source-commit", required=True)
    parser.add_argument("--sample-count", type=int, default=8)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """执行逐层绑定。"""

    args = build_parser().parse_args(argv)
    try:
        report = build_report(args)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        write_summary(report, args.summary)
        print(json.dumps({"status": report["status"], "sample_count": report["inputs"]["sample_count"], "report": str(args.report)}, ensure_ascii=False, indent=2))
        return 0
    except (FloatBindingError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"D2_FLOAT_BINDING_ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
