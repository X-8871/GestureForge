"""S1-T02-D2 的真实网络激活范围与 INT8 scale 校准报告器。

本模块只消费隔离 Darknet 前向 hook 生成的逐层统计 CSV，不执行训练或修改
原始权重。缺少样本、层、重复记录、NaN/Inf 或输入绑定时统一 fail-closed。
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

try:
    from s1_t02_d2_int8_weight_reference import parse_cfg, sha256_file
except ModuleNotFoundError:
    from verification.s1_t02_d2_int8_weight_reference import parse_cfg, sha256_file


INT8_MAX = 127
INPUT_SCALE = 1.0 / 127.0
EXPECTED_SAMPLE_COUNT = 512
SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")
REQUIRED_COLUMNS = {
    "sample_index",
    "layer_index",
    "layer_type",
    "output_count",
    "minimum",
    "maximum",
    "sum",
    "sumsq",
    "nonfinite",
}


class ActivationCalibrationError(ValueError):
    """表示激活校准输入或统计记录无效。"""


def _utc8_now() -> str:
    """返回东八区 ISO-8601 时间。"""

    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _finite(value: str, field: str) -> float:
    """解析有限浮点字段。"""

    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ActivationCalibrationError(f"字段 {field} 不是浮点数: {value!r}") from exc
    if not math.isfinite(parsed):
        raise ActivationCalibrationError(f"字段 {field} 不是有限值: {value!r}")
    return parsed


def _positive_int(value: str, field: str) -> int:
    """解析正整数。"""

    try:
        parsed = int(value, 10)
    except (TypeError, ValueError) as exc:
        raise ActivationCalibrationError(f"字段 {field} 不是整数: {value!r}") from exc
    if parsed <= 0:
        raise ActivationCalibrationError(f"字段 {field} 必须为正数: {parsed}")
    return parsed


def _nonnegative_int(value: str, field: str) -> int:
    """解析非负整数。"""

    try:
        parsed = int(value, 10)
    except (TypeError, ValueError) as exc:
        raise ActivationCalibrationError(f"字段 {field} 不是整数: {value!r}") from exc
    if parsed < 0:
        raise ActivationCalibrationError(f"字段 {field} 不能为负数: {parsed}")
    return parsed


def _sha256_text_lines(path: Path) -> tuple[str, int, list[str]]:
    """读取 UTF-8 清单并返回字节摘要、非空行数和原始非空行。"""

    try:
        blob = path.read_bytes()
        text = blob.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise ActivationCalibrationError(f"校准清单不可读取或不是 UTF-8: {path}: {exc}") from exc
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return hashlib.sha256(blob).hexdigest(), len(lines), lines


def _require_file(path: Path, field: str) -> Path:
    """校验输入文件为普通文件并返回绝对路径。"""

    resolved = path.resolve()
    if not resolved.is_file():
        raise ActivationCalibrationError(f"{field} 不是可读普通文件: {resolved}")
    return resolved


def _parse_stats(path: Path, expected_layers: set[int], expected_samples: int) -> dict[int, dict[int, dict[str, Any]]]:
    """读取逐样本逐卷积层激活统计并拒绝不完整输入。"""

    rows_by_layer: dict[int, dict[int, dict[str, Any]]] = {layer: {} for layer in expected_layers}
    try:
        handle = path.open("r", encoding="utf-8", newline="")
    except OSError as exc:
        raise ActivationCalibrationError(f"激活统计不可读取: {path}: {exc}") from exc
    with handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = sorted(REQUIRED_COLUMNS - columns)
        if missing:
            raise ActivationCalibrationError(f"激活统计缺少字段: {missing}")
        for row_number, row in enumerate(reader, 2):
            try:
                sample_index = _nonnegative_int(row["sample_index"], f"第{row_number}行 sample_index")
                layer_index = _nonnegative_int(row["layer_index"], f"第{row_number}行 layer_index")
                layer_type = row["layer_type"].strip().upper()
                output_count = _positive_int(row["output_count"], f"第{row_number}行 output_count")
                minimum = _finite(row["minimum"], f"第{row_number}行 minimum")
                maximum = _finite(row["maximum"], f"第{row_number}行 maximum")
                total = _finite(row["sum"], f"第{row_number}行 sum")
                sumsq = _finite(row["sumsq"], f"第{row_number}行 sumsq")
                nonfinite = _nonnegative_int(row["nonfinite"], f"第{row_number}行 nonfinite")
            except KeyError as exc:
                raise ActivationCalibrationError(f"第{row_number}行缺少字段: {exc.args[0]}") from exc
            if layer_type != "CONVOLUTIONAL":
                raise ActivationCalibrationError(f"第{row_number}行不是卷积层统计: {layer_type!r}")
            if layer_index not in expected_layers:
                raise ActivationCalibrationError(f"统计包含 cfg 不存在的卷积层: {layer_index}")
            if sample_index >= expected_samples:
                raise ActivationCalibrationError(
                    f"第{row_number}行 sample_index 超出校准范围: {sample_index} >= {expected_samples}"
                )
            if minimum > maximum or sumsq < 0 or nonfinite != 0:
                raise ActivationCalibrationError(f"第{row_number}行激活统计无效: {row}")
            if sample_index in rows_by_layer[layer_index]:
                raise ActivationCalibrationError(f"卷积层 {layer_index} 重复 sample_index: {sample_index}")
            rows_by_layer[layer_index][sample_index] = {
                "output_count": output_count,
                "minimum": minimum,
                "maximum": maximum,
                "sum": total,
                "sumsq": sumsq,
                "nonfinite": nonfinite,
            }
    expected_indices = set(range(expected_samples))
    for layer_index, rows in rows_by_layer.items():
        actual_indices = set(rows)
        if actual_indices != expected_indices:
            missing = sorted(expected_indices - actual_indices)
            extra = sorted(actual_indices - expected_indices)
            raise ActivationCalibrationError(
                f"卷积层 {layer_index} 样本集合不完整: actual={len(actual_indices)}, "
                f"missing_head={missing[:5]}, extra={extra[:5]}"
            )
    return rows_by_layer


def _layer_calibration(rows: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """汇总一个卷积层的范围并生成对称激活 scale。"""

    output_counts = {item["output_count"] for item in rows.values()}
    if len(output_counts) != 1:
        raise ActivationCalibrationError(f"同一卷积层 output_count 不一致: {sorted(output_counts)}")
    minimum = min(item["minimum"] for item in rows.values())
    maximum = max(item["maximum"] for item in rows.values())
    max_abs = max(abs(minimum), abs(maximum))
    scale = max_abs / INT8_MAX if max_abs else INPUT_SCALE
    return {
        "sample_count": len(rows),
        "output_count": next(iter(output_counts)),
        "observed_minimum": minimum,
        "observed_maximum": maximum,
        "max_abs": max_abs,
        "activation_scale": scale,
        "zero_point": 0,
        "int8_range": [-127, 127],
        "nonfinite_count": sum(item["nonfinite"] for item in rows.values()),
    }


def calibrate(
    *,
    cfg: Path,
    weights: Path,
    calibration_list: Path,
    stats_csv: Path,
    darknet_executable: Path,
    activation_hook_source: Path | None,
    darknet_source_commit: str,
    expected_samples: int = EXPECTED_SAMPLE_COUNT,
) -> dict[str, Any]:
    """绑定输入并生成逐卷积层激活 scale 校准报告。"""

    if not COMMIT_PATTERN.fullmatch(darknet_source_commit):
        raise ActivationCalibrationError("Darknet source commit 必须为40位十六进制 SHA-1")
    if expected_samples != EXPECTED_SAMPLE_COUNT:
        raise ActivationCalibrationError(f"本任务固定要求 {EXPECTED_SAMPLE_COUNT} 张校准图")
    cfg = _require_file(cfg, "cfg")
    weights = _require_file(weights, "weights")
    calibration_list = _require_file(calibration_list, "calibration_list")
    stats_csv = _require_file(stats_csv, "stats_csv")
    darknet_executable = _require_file(darknet_executable, "darknet_executable")
    if activation_hook_source is not None:
        activation_hook_source = _require_file(activation_hook_source, "activation_hook_source")
    list_sha256, list_count, list_lines = _sha256_text_lines(calibration_list)
    if list_count != expected_samples:
        raise ActivationCalibrationError(f"校准清单非 {expected_samples} 行: {list_count}")
    if len({line.casefold() for line in list_lines}) != list_count:
        raise ActivationCalibrationError("校准清单包含重复路径")
    network = parse_cfg(cfg)
    expected_layers = {item.layer_index for item in network.convolutions}
    rows_by_layer = _parse_stats(stats_csv, expected_layers, expected_samples)
    layers = {str(layer_index): _layer_calibration(rows) for layer_index, rows in sorted(rows_by_layer.items())}
    max_abs = max(item["max_abs"] for item in layers.values())
    return {
        "schema_version": "s1_t02_d2_activation_calibration_v1",
        "status": "ACTIVATION_SCALE_CALIBRATION_COMPLETE_INTEGER_FORWARD_PENDING",
        "generated_at_utc8": _utc8_now(),
        "tool": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256_file(Path(__file__).resolve()),
        },
        "scope": "tiny416 formal 6000 的真实 Darknet GPU 浮点前向激活范围；不含整数前向、检测头和 mAP",
        "inputs": {
            "cfg": str(cfg),
            "cfg_sha256": sha256_file(cfg),
            "weights": str(weights),
            "weights_sha256": sha256_file(weights),
            "calibration_list": str(calibration_list),
            "calibration_list_sha256": list_sha256,
            "calibration_sample_count": list_count,
            "stats_csv": str(stats_csv),
            "stats_csv_sha256": sha256_file(stats_csv),
            "darknet_executable": str(darknet_executable),
            "darknet_executable_sha256": sha256_file(darknet_executable),
            "activation_hook_source": str(activation_hook_source) if activation_hook_source else None,
            "activation_hook_source_sha256": sha256_file(activation_hook_source) if activation_hook_source else None,
            "darknet_source_commit": darknet_source_commit.lower(),
        },
        "network": {
            "width": network.width,
            "height": network.height,
            "channels": network.channels,
            "convolution_count": len(network.convolutions),
            "expected_sample_count": expected_samples,
        },
        "activation_quantization": {
            "scheme": "per-layer per-tensor symmetric",
            "zero_point": 0,
            "int8_range": [-127, 127],
            "scale_formula": "max(abs(observed_minimum), abs(observed_maximum)) / 127; zero layer falls back to 1/127",
            "global_max_abs": max_abs,
        },
        "layers": layers,
        "limitations": [
            "仅校准浮点 Darknet 前向输出，未执行 INT8 整数卷积或逐层误差传播",
            "未验证累加器 bias 的实际整数输入域、重定标、检测头解码、NMS 或 mAP",
            "不构成 D3 Vivado 资源/时序、G4、G5 或阶段1通过",
        ],
    }


def write_summary(report: dict[str, Any], path: Path) -> None:
    """以稳定 Markdown 输出校准摘要。"""

    lines = [
        "# S1-T02-D2 tiny416 激活 scale 校准摘要",
        "",
        f"- status: `{report['status']}`",
        f"- calibration samples: `{report['inputs']['calibration_sample_count']}`",
        f"- convolution layers: `{report['network']['convolution_count']}`",
        f"- global max abs: `{report['activation_quantization']['global_max_abs']:.17g}`",
        "",
        "| layer | samples | output_count | min | max | scale |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for layer_index, item in report["layers"].items():
        lines.append(
            f"| {layer_index} | {item['sample_count']} | {item['output_count']} | "
            f"{item['observed_minimum']:.17g} | {item['observed_maximum']:.17g} | "
            f"{item['activation_scale']:.17g} |"
        )
    lines.extend(["", "激活 scale 仅绑定真实浮点前向统计；整数前向和检测精度仍待后续任务。", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _build_parser() -> argparse.ArgumentParser:
    """构建严格 CLI。"""

    parser = argparse.ArgumentParser(description="生成 S1-T02-D2 tiny416 激活 scale 校准报告")
    parser.add_argument("--cfg", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--calibration-list", type=Path, required=True)
    parser.add_argument("--stats-csv", type=Path, required=True)
    parser.add_argument("--darknet-executable", type=Path, required=True)
    parser.add_argument("--activation-hook-source", type=Path)
    parser.add_argument("--darknet-source-commit", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """执行 CLI 并在失败时不生成伪通过报告。"""

    args = _build_parser().parse_args(argv)
    try:
        report = calibrate(
            cfg=args.cfg,
            weights=args.weights,
            calibration_list=args.calibration_list,
            stats_csv=args.stats_csv,
            darknet_executable=args.darknet_executable,
            activation_hook_source=args.activation_hook_source,
            darknet_source_commit=args.darknet_source_commit,
        )
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        write_summary(report, args.summary)
        print(json.dumps({"status": report["status"], "report": str(args.report), "summary": str(args.summary)}, ensure_ascii=False, indent=2))
        return 0
    except (ActivationCalibrationError, OSError, ValueError) as error:
        print(f"激活校准失败: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
