#!/usr/bin/env python3
"""S1-T02-D6 PC 检测结果离线评估器。

本模块只读取 manifest、YOLO 标签和带显式坐标格式的预测结果，执行固定
score threshold、类别内 NMS、IoU 一对一匹配、101 点 AP 以及辅助误检率统计。
它不启动 Darknet，不下载权重，也不实现训练、INT8 整网或检测头推理。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import subprocess
import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence


EXPECTED_CLASSES = ["fist", "palm", "one", "two_up", "three"]
G0_DECISION_DATE = "2026-09-18"
G0_POLICY_DOCUMENT_PATH = "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D6_检测评估口径与离线指标基础.md"
G0_POLICY_DOCUMENT_SHA256 = "1fdfdb74281ccd14271c79a9622ac14c743f489dce2a7e420f945b23b4bddaff"
COORDINATE_POLICY_DECISION_DATE = "2026-09-21"
COORDINATE_POLICY = "clip_finite_positive_xyxy_to_unit_range"
COORDINATE_POLICY_DIAGNOSTIC_PATH = "report/evidence/S1-T02/20260918_s1_t02_d6_tiny416_val_coordinate_clip_impact_r1.json"
COORDINATE_POLICY_DIAGNOSTIC_SHA256 = "88896cedea23f8cb50ea981c1a7072f1bae41871dbd425f575ec4f8ec423f569"
APPROVED_TEST_MANIFEST_SHA256 = "fd60e7a67161f242276a1b97b09ad07c0d7f41d30067266bb99620abe6d7ed74"
APPROVED_TEST_IMAGE_COUNT = 25484
APPROVED_SPLIT_IMAGE_COUNTS = {"train": 118001, "val": 15195, "test": 25484}
# 当前没有完整、获批且哈希绑定的 G0 指标策略快照。
APPROVED_G0_METRIC_POLICY_EVIDENCE: tuple[str, str] | None = None
ROBUSTNESS_MIN_IMAGES_PER_CLASS = 100
ROBUSTNESS_CONDITION_BUCKETS = {
    "no_hand": 100,
    "non-target": 100,
    "multi-hand": 100,
    "occlusion": 100,
    "small-target": 100,
}
IOU_THRESHOLDS = [round(0.50 + 0.05 * index, 2) for index in range(10)]
MAX_OUTPUTS = 15
FIXED_NMS_IOU = 0.45
DEFAULT_COORDINATE_FORMAT = "darknet_relative_coordinates"
SUPPORTED_COORDINATE_FORMATS = {DEFAULT_COORDINATE_FORMAT, "xyxy_normalized"}
AP_POINTS = 101
IOU_EPSILON = 1e-12
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


class EvaluationError(ValueError):
    """表示输入或固定评估口径不合法。"""


@dataclass(frozen=True)
class ImageEntry:
    """manifest 中一个评估图片及其标签绑定。"""

    index: int
    image_text: str
    image_path: Path
    label_text: str
    label_path: Path
    key: str


_EVALUATION_CONTEXT_SEAL = object()


@dataclass(frozen=True)
class EvaluationContext:
    """不可变的 manifest、split 与当前评估授权绑定。"""

    manifest_path: Path
    data_root: Path
    labels_root: Path
    split: str
    manifest_sha256: str
    manifest_bytes: bytes = field(repr=False)
    split_counts: tuple[tuple[str, int], ...]
    entries: tuple[ImageEntry, ...] = field(repr=False)
    authorization_state: str
    metric_policy_evidence: tuple[str, str] | None
    _integrity_sha256: str = field(default="", repr=False, compare=False)
    _seal: object = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class GroundTruth:
    """一个归一化 YOLO 标注框。"""

    class_id: int
    name: str
    box: tuple[float, float, float, float]


@dataclass(frozen=True)
class Prediction:
    """一个已解析、已归一化的预测框。"""

    image_key: str
    class_id: int
    name: str
    confidence: float
    box: tuple[float, float, float, float]
    source_order: int
    raw_box: tuple[float, float, float, float] | None = None
    coordinate_clipped: bool = False


def _now_iso() -> str:
    """返回东八区当前时间。"""

    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    """按字节计算文件 SHA-256。"""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _finite(value: Any, field: str) -> float:
    """解析有限浮点数，拒绝 NaN、Inf 和不可转换值。"""

    if isinstance(value, bool):
        raise EvaluationError(f"{field} 不能是 bool")
    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise EvaluationError(f"{field} 必须是数值") from exc
    if not math.isfinite(converted):
        raise EvaluationError(f"{field} 必须是有限数")
    return converted


def _canonical_path(path: Path) -> str:
    """生成大小写不敏感的规范绝对路径键。"""

    try:
        return os.path.normcase(str(path.resolve(strict=False)))
    except (OSError, RuntimeError) as exc:
        raise EvaluationError(f"路径无法规范化: {path}") from exc


def _resolve_input_path(value: str, root: Path) -> Path:
    """按绝对路径或指定根目录解析输入路径。"""

    candidate = Path(value)
    return candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()


def _resolve_label_path(value: str, labels_root: Path) -> Path:
    """解析 manifest 标签路径，避免 labels/ 前缀被重复拼接。"""

    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.resolve()
    parts = candidate.parts
    if parts and parts[0].casefold() == labels_root.name.casefold():
        return (labels_root.parent / candidate).resolve()
    return (labels_root / candidate).resolve()


def _validate_sha256(value: Any, field: str) -> str:
    """校验非空 64 位十六进制 SHA-256。"""

    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise EvaluationError(f"{field} 必须是 64 位十六进制 SHA-256")
    return value.lower()


def _read_class_names(path: Path) -> list[str]:
    """读取并校验固定五类 names 文件。"""

    if not path.is_file():
        raise EvaluationError(f"class names 文件不存在: {path}")
    try:
        names = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    except (OSError, UnicodeError) as exc:
        raise EvaluationError(f"class names 文件不可读取: {path}: {exc}") from exc
    if names != EXPECTED_CLASSES:
        raise EvaluationError(f"class names 必须严格为 {EXPECTED_CLASSES}，实际为 {names}")
    return names


def _entries_from_manifest_snapshot(
    manifest_path: Path,
    data_root: Path,
    labels_root: Path,
    split: str,
    manifest_bytes: bytes,
) -> tuple[ImageEntry, ...]:
    """从已校验的完整快照构造一个 split 的不可变条目序列。"""

    if not data_root.is_dir():
        raise EvaluationError(f"data-root 不存在: {data_root}")
    if not labels_root.is_dir():
        raise EvaluationError(f"labels-root 不存在: {labels_root}")
    entries: list[ImageEntry] = []
    seen: set[str] = set()
    try:
        if manifest_bytes is None:
            manifest_bytes = manifest_path.read_bytes()
        text = manifest_bytes.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text, newline=""))
        required = {"image", "label", "split"}
        fields = set(reader.fieldnames or [])
        missing = sorted(required - fields)
        if missing:
            raise EvaluationError(f"manifest 缺少字段: {missing}")
        for row_number, row in enumerate(reader, start=2):
            if row.get("split", "") != split:
                continue
            image_text = (row.get("image") or "").strip()
            label_text = (row.get("label") or "").strip()
            if not image_text or not label_text:
                raise EvaluationError(f"manifest 第 {row_number} 行 image/label 不能为空")
            image_path = _resolve_input_path(image_text, data_root)
            label_path = _resolve_label_path(label_text, labels_root)
            if image_path.stem != label_path.stem:
                raise EvaluationError(
                    f"manifest 第 {row_number} 行图片与标签 stem 不一致: {image_path.name} / {label_path.name}"
                )
            if not label_path.is_file():
                raise EvaluationError(f"标签文件不存在: {label_path}")
            key = _canonical_path(image_path)
            if key in seen:
                raise EvaluationError(f"manifest split={split} 图片重复: {image_text}")
            seen.add(key)
            entries.append(ImageEntry(len(entries) + 1, image_text, image_path, label_text, label_path, key))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise EvaluationError(f"manifest 不可读取: {manifest_path}: {exc}") from exc
    if not entries:
        raise EvaluationError(f"manifest 中没有 split={split} 图片")
    return tuple(entries)


def load_manifest(context: EvaluationContext | None = None) -> tuple[ImageEntry, ...]:
    """从已验证上下文取回条目；不接受裸路径或未绑定 split。"""

    validated = _require_valid_evaluation_context(context)
    return validated.entries


def _validate_approved_manifest_binding(manifest_bytes: bytes, manifest_sha256: str, split: str) -> int:
    """在读取标签、预测和计算指标前校验完整 manifest 快照及 split 计数。"""

    if manifest_sha256 != APPROVED_TEST_MANIFEST_SHA256:
        raise EvaluationError(
            f"split={split} manifest SHA-256 与 Wong 批准的完整 train/val/test manifest 不一致: "
            f"expected={APPROVED_TEST_MANIFEST_SHA256}, actual={manifest_sha256}"
        )
    try:
        text = manifest_bytes.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text, newline=""))
        required = {"image", "label", "split"}
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise EvaluationError(f"manifest 缺少字段: {missing}")
        counts = {name: 0 for name in APPROVED_SPLIT_IMAGE_COUNTS}
        for row_number, row in enumerate(reader, start=2):
            row_split = row.get("split", "")
            if row_split not in counts:
                raise EvaluationError(
                    f"manifest 第 {row_number} 行 split 非规范；只允许 {sorted(counts)}"
                )
            counts[row_split] += 1
    except (UnicodeError, csv.Error) as exc:
        raise EvaluationError(f"manifest 不可读取或 CSV 格式错误: {exc}") from exc
    for split_name, expected_count in APPROVED_SPLIT_IMAGE_COUNTS.items():
        actual_count = counts[split_name]
        if actual_count != expected_count:
            raise EvaluationError(
                f"manifest split={split_name} 图片数与 Wong 批准口径不一致: "
                f"expected={expected_count}, actual={actual_count}"
            )
    return counts[split]


def _require_complete_g0_metric_policy(split: str) -> None:
    """在读取 test/robustness 标签或预测前要求完整获批策略证据。"""

    if split not in {"test", "robustness"}:
        return
    if APPROVED_G0_METRIC_POLICY_EVIDENCE is None:
        raise EvaluationError(
            f"split={split} 已阻断：缺少完整、获批且哈希绑定的 D6 G0 指标策略证据；"
            "最终 score threshold 与 mAP/逐类 precision-recall 验收门槛仍未冻结"
        )
    raise EvaluationError(
        f"split={split} 已阻断：本版本尚无完整 G0 指标策略快照验证器，不能据此开放正式评估"
    )


def create_evaluation_context(
    manifest_path: Path,
    data_root: Path,
    labels_root: Path,
    split: str,
) -> EvaluationContext:
    """校验完整 manifest 快照并建立只供该 split 使用的授权上下文。"""

    allowed_splits = {*APPROVED_SPLIT_IMAGE_COUNTS, "robustness"}
    if not isinstance(split, str) or split not in allowed_splits:
        raise EvaluationError(f"split 非规范；只允许 {sorted(allowed_splits)}，不接受大小写/别名映射")
    if split == "robustness":
        _require_complete_g0_metric_policy(split)
    try:
        resolved_manifest = manifest_path.resolve()
        resolved_data_root = data_root.resolve()
        resolved_labels_root = labels_root.resolve()
        manifest_bytes = resolved_manifest.read_bytes()
    except (OSError, RuntimeError) as exc:
        raise EvaluationError(f"manifest 或输入根目录不可解析/不可读取: {exc}") from exc
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    if split in APPROVED_SPLIT_IMAGE_COUNTS:
        _validate_approved_manifest_binding(manifest_bytes, manifest_sha256, split)
    _require_complete_g0_metric_policy(split)
    entries = _entries_from_manifest_snapshot(
        resolved_manifest,
        resolved_data_root,
        resolved_labels_root,
        split,
        manifest_bytes,
    )
    context = EvaluationContext(
        manifest_path=resolved_manifest,
        data_root=resolved_data_root,
        labels_root=resolved_labels_root,
        split=split,
        manifest_sha256=manifest_sha256,
        manifest_bytes=manifest_bytes,
        split_counts=tuple(sorted(APPROVED_SPLIT_IMAGE_COUNTS.items())),
        entries=entries,
        authorization_state=("VAL_ONLY_G0_PENDING" if split == "val" else "TRAIN_DIAGNOSTIC_ONLY"),
        metric_policy_evidence=APPROVED_G0_METRIC_POLICY_EVIDENCE,
        _seal=_EVALUATION_CONTEXT_SEAL,
    )
    object.__setattr__(context, "_integrity_sha256", _evaluation_context_integrity(context))
    _require_valid_evaluation_context(context)
    return context


def _evaluation_context_integrity(context: EvaluationContext) -> str:
    """为冻结上下文的全部授权字段生成一致性摘要。"""

    payload = {
        "manifest_path": str(context.manifest_path),
        "data_root": str(context.data_root),
        "labels_root": str(context.labels_root),
        "split": context.split,
        "manifest_sha256": context.manifest_sha256,
        "manifest_bytes_sha256": hashlib.sha256(context.manifest_bytes).hexdigest(),
        "split_counts": list(context.split_counts),
        "entries": [
            [entry.index, entry.image_text, str(entry.image_path), entry.label_text, str(entry.label_path), entry.key]
            for entry in context.entries
        ],
        "authorization_state": context.authorization_state,
        "metric_policy_evidence": context.metric_policy_evidence,
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _require_valid_evaluation_context(
    context: EvaluationContext | None,
    expected_split: str | None = None,
) -> EvaluationContext:
    """拒绝裸路径、手造上下文、损坏快照及未授权 split。"""

    if type(context) is not EvaluationContext or context._seal is not _EVALUATION_CONTEXT_SEAL:
        raise EvaluationError("评估 API 必须使用 create_evaluation_context 返回的已验证上下文")
    allowed_splits = {*APPROVED_SPLIT_IMAGE_COUNTS, "robustness"}
    if not isinstance(context.split, str) or context.split not in allowed_splits:
        raise EvaluationError(f"上下文 split 非规范；只允许 {sorted(allowed_splits)}")
    if expected_split is not None and context.split != expected_split:
        raise EvaluationError(f"上下文 split={context.split} 与调用要求 split={expected_split} 不一致")
    if context.split in {"test", "robustness"}:
        _require_complete_g0_metric_policy(context.split)
    expected_authorization = "VAL_ONLY_G0_PENDING" if context.split == "val" else "TRAIN_DIAGNOSTIC_ONLY"
    if context.authorization_state != expected_authorization:
        raise EvaluationError("上下文 split 授权状态与当前 G0 策略不一致")
    if context.metric_policy_evidence != APPROVED_G0_METRIC_POLICY_EVIDENCE:
        raise EvaluationError("上下文 G0 策略证据已变化，必须重新验证 manifest")
    if (
        not isinstance(context.manifest_path, Path)
        or not isinstance(context.data_root, Path)
        or not isinstance(context.labels_root, Path)
        or type(context.entries) is not tuple
    ):
        raise EvaluationError("上下文路径或条目序列类型无效")
    if type(context.manifest_bytes) is not bytes:
        raise EvaluationError("上下文必须绑定不可变 manifest bytes")
    actual_sha256 = hashlib.sha256(context.manifest_bytes).hexdigest()
    if actual_sha256 != context.manifest_sha256 or actual_sha256 != APPROVED_TEST_MANIFEST_SHA256:
        raise EvaluationError("上下文 manifest SHA-256 与当前批准的完整快照不一致")
    if context.split_counts != tuple(sorted(APPROVED_SPLIT_IMAGE_COUNTS.items())):
        raise EvaluationError("上下文 train/val/test 计数政策与当前批准口径不一致")
    if context._integrity_sha256 != _evaluation_context_integrity(context):
        raise EvaluationError("上下文内容与工厂签发时的不可变快照不一致")
    if context.split not in APPROVED_SPLIT_IMAGE_COUNTS:
        raise EvaluationError(f"split={context.split} 缺少已批准的正式 manifest 绑定")
    if len(context.entries) != APPROVED_SPLIT_IMAGE_COUNTS[context.split]:
        raise EvaluationError(f"上下文条目数与批准 split={context.split} 计数不一致")
    if any(type(entry) is not ImageEntry for entry in context.entries):
        raise EvaluationError("上下文包含未验证 manifest 条目")
    if len({entry.key for entry in context.entries}) != len(context.entries):
        raise EvaluationError("上下文 manifest 条目包含重复图片")
    return context


def _require_context_entries(
    entries: Sequence[ImageEntry],
    context: EvaluationContext | None,
) -> EvaluationContext:
    """确认下游 API 使用上下文原样绑定的完整条目顺序。"""

    validated = _require_valid_evaluation_context(context)
    try:
        candidate_entries = tuple(entries)
    except TypeError as exc:
        raise EvaluationError("评估条目必须是上下文绑定的有序序列") from exc
    if candidate_entries != validated.entries:
        raise EvaluationError("评估条目与上下文绑定的完整 manifest split 不一致")
    return validated


def _checked_class_id(value: Any, field: str) -> int:
    """严格解析五类范围内的非 bool 整数类别编号。"""

    if type(value) is not int or not 0 <= value < len(EXPECTED_CLASSES):
        raise EvaluationError(f"{field} 必须是 0..{len(EXPECTED_CLASSES) - 1} 的整数")
    return value


def _checked_box(box: Sequence[Any], field: str) -> tuple[float, float, float, float]:
    """校验归一化 xyxy 框位于 [0,1] 且面积为正。"""

    if not isinstance(box, (list, tuple)) or len(box) != 4:
        raise EvaluationError(f"{field} 必须是四元素 xyxy 数组")
    values = tuple(_finite(value, f"{field}[{index}]") for index, value in enumerate(box))
    left, top, right, bottom = values
    if not all(0.0 <= value <= 1.0 for value in values):
        raise EvaluationError(f"{field} 必须是 [0,1] 内归一化坐标")
    if right <= left or bottom <= top:
        raise EvaluationError(f"{field} 必须满足 right>left 且 bottom>top")
    return values


def _clip_prediction_box(
    box: Sequence[Any], field: str
) -> tuple[tuple[float, float, float, float], tuple[float, float, float, float]]:
    """校验预测框并将有限正面积框裁剪到单位图像范围。"""

    if not isinstance(box, (list, tuple)) or len(box) != 4:
        raise EvaluationError(f"{field} 必须是四元素 xyxy 数组")
    raw_values = tuple(_finite(value, f"{field}[{index}]") for index, value in enumerate(box))
    raw_left, raw_top, raw_right, raw_bottom = raw_values
    if raw_right <= raw_left or raw_bottom <= raw_top:
        raise EvaluationError(f"{field} 原始框必须满足 right>left 且 bottom>top")
    clipped = tuple(min(max(value, 0.0), 1.0) for value in raw_values)
    left, top, right, bottom = clipped
    if right <= left or bottom <= top:
        raise EvaluationError(f"{field} 裁剪后必须满足 right>left 且 bottom>top")
    return raw_values, clipped


def _yolo_to_xyxy(
    values: Sequence[Any], field: str, allow_out_of_range: bool = False
) -> tuple[float, float, float, float]:
    """将归一化 YOLO 中心点格式转换为归一化 xyxy。"""

    if not isinstance(values, (list, tuple)) or len(values) != 4:
        raise EvaluationError(f"{field} 必须是四元素中心点坐标对象")
    center_x, center_y, width, height = (
        _finite(value, f"{field}.{name}") for value, name in zip(values, ("center_x", "center_y", "width", "height"))
    )
    if allow_out_of_range:
        if width <= 0.0 or height <= 0.0:
            raise EvaluationError(f"{field} 的 width 和 height 必须为正数")
    elif not (0.0 <= center_x <= 1.0 and 0.0 <= center_y <= 1.0 and 0.0 < width <= 1.0 and 0.0 < height <= 1.0):
        raise EvaluationError(f"{field} 必须是合法归一化 YOLO 坐标")
    box = (center_x - width / 2.0, center_y - height / 2.0, center_x + width / 2.0, center_y + height / 2.0)
    if allow_out_of_range:
        return box
    return _checked_box(box, field)


def parse_yolo_label(
    entry: ImageEntry,
    context: EvaluationContext | None = None,
) -> list[GroundTruth]:
    """按已验证上下文解析其中一个条目的 YOLO 标签。"""

    validated = _require_valid_evaluation_context(context)
    if type(entry) is not ImageEntry or entry not in validated.entries:
        raise EvaluationError("标签条目不属于已验证上下文")
    return _read_yolo_label_file(entry.label_path)


def _read_yolo_label_file(path: Path) -> list[GroundTruth]:
    """读取单个标签文件正文；调用方必须先验证所属上下文。"""

    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        raise EvaluationError(f"标签文件不可读取: {path}: {exc}") from exc
    result: list[GroundTruth] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) != 5:
            raise EvaluationError(f"标签 {path} 第 {line_number} 行必须有5列")
        class_id = _checked_class_id(int(fields[0]) if fields[0].lstrip("-").isdigit() else None, f"{path}:{line_number}:class_id")
        box = _yolo_to_xyxy(fields[1:], f"{path}:{line_number}:yolo")
        result.append(GroundTruth(class_id, EXPECTED_CLASSES[class_id], box))
    return result


def load_ground_truths(
    entries: Sequence[ImageEntry],
    context: EvaluationContext | None = None,
) -> dict[str, list[GroundTruth]]:
    """读取上下文完整 split 的标签。"""

    validated = _require_context_entries(entries, context)
    return {entry.key: _read_yolo_label_file(entry.label_path) for entry in validated.entries}


def _validated_coordinate_format(value: Any, field: str) -> str:
    """校验坐标格式枚举，不根据数值猜测格式。"""

    if not isinstance(value, str) or value not in SUPPORTED_COORDINATE_FORMATS:
        raise EvaluationError(
            f"{field} 必须是 {sorted(SUPPORTED_COORDINATE_FORMATS)} 之一"
        )
    return value


def _record_coordinate_format(
    record: dict[str, Any], root_format: str | None, record_index: int
) -> str:
    """确定单条记录格式，并拒绝记录内声明冲突。"""

    declared: list[tuple[str, str]] = []
    if root_format is not None:
        declared.append(("顶层 coordinate_format", _validated_coordinate_format(root_format, "顶层 coordinate_format")))
    if "coordinate_format" in record:
        declared.append(
            (
                f"预测记录 {record_index} coordinate_format",
                _validated_coordinate_format(record["coordinate_format"], f"预测记录 {record_index} coordinate_format"),
            )
        )
    objects = record.get("objects")
    if isinstance(objects, list):
        for object_index, object_value in enumerate(objects):
            if not isinstance(object_value, dict) or "coordinate_format" not in object_value:
                continue
            declared.append(
                (
                    f"预测记录 {record_index} object {object_index} coordinate_format",
                    _validated_coordinate_format(
                        object_value["coordinate_format"],
                        f"预测记录 {record_index} object {object_index} coordinate_format",
                    ),
                )
            )
    formats = {value for _, value in declared}
    if len(formats) > 1:
        details = ", ".join(f"{field}={value}" for field, value in declared)
        raise EvaluationError(f"预测记录 {record_index} coordinate_format 声明冲突: {details}")
    return next(iter(formats), DEFAULT_COORDINATE_FORMAT)


def _prediction_class(object_value: dict[str, Any]) -> tuple[int, str]:
    """校验预测 name/class_id 双重类别绑定。"""

    name_value = object_value.get("name")
    class_value = object_value.get("class_id")
    if name_value is None and class_value is None:
        raise EvaluationError("预测 object 必须包含 name 或 class_id")
    if name_value is not None and (not isinstance(name_value, str) or name_value not in EXPECTED_CLASSES):
        raise EvaluationError(f"预测 name 不属于五类: {name_value!r}")
    class_id = None if class_value is None else _checked_class_id(class_value, "预测 class_id")
    if class_id is None:
        class_id = EXPECTED_CLASSES.index(name_value)
    if name_value is not None and EXPECTED_CLASSES[class_id] != name_value:
        raise EvaluationError("预测 class_id 与 name 不一致")
    return class_id, EXPECTED_CLASSES[class_id]


def parse_prediction_record(
    record: Any,
    image_key: str,
    record_index: int,
    root_format: str | None,
    record_format: str | None = None,
) -> list[Prediction]:
    """解析一个预测记录中的 objects。"""

    if not isinstance(record, dict):
        raise EvaluationError(f"预测记录 {record_index} 必须是对象")
    objects = record.get("objects")
    if not isinstance(objects, list):
        raise EvaluationError(f"预测记录 {record_index} 的 objects 必须是数组")
    expected_format = record_format or _record_coordinate_format(record, root_format, record_index)
    result: list[Prediction] = []
    for object_index, object_value in enumerate(objects):
        if not isinstance(object_value, dict):
            raise EvaluationError(f"预测记录 {record_index} object {object_index} 必须是对象")
        confidence = _finite(object_value.get("confidence"), f"预测 {record_index}/{object_index}:confidence")
        if not 0.0 <= confidence <= 1.0:
            raise EvaluationError(f"预测 {record_index}/{object_index}:confidence 必须在 [0,1]")
        class_id, name = _prediction_class(object_value)
        object_format = expected_format
        if "coordinate_format" in object_value:
            object_format = _validated_coordinate_format(
                object_value["coordinate_format"],
                f"预测记录 {record_index} object {object_index} coordinate_format",
            )
            if object_format != expected_format:
                raise EvaluationError(
                    f"预测记录 {record_index} object {object_index} coordinate_format 与记录不一致"
                )
        has_relative = "relative_coordinates" in object_value
        has_xyxy = "xyxy" in object_value
        if has_relative == has_xyxy:
            raise EvaluationError("预测 object 必须且只能提供 relative_coordinates 或显式 xyxy")
        if object_format == DEFAULT_COORDINATE_FORMAT and not has_relative:
            raise EvaluationError(
                f"预测记录 {record_index} object {object_index} 声明为 {DEFAULT_COORDINATE_FORMAT}，但缺少 relative_coordinates"
            )
        if object_format == "xyxy_normalized" and not has_xyxy:
            raise EvaluationError(
                f"预测记录 {record_index} object {object_index} 声明为 xyxy_normalized，但缺少 xyxy"
            )
        if object_format == DEFAULT_COORDINATE_FORMAT:
            relative = object_value["relative_coordinates"]
            if not isinstance(relative, dict):
                raise EvaluationError(f"预测 {record_index}/{object_index}:relative_coordinates 必须是对象")
            values = [relative.get(key) for key in ("center_x", "center_y", "width", "height")]
            raw_box = _yolo_to_xyxy(values, f"预测 {record_index}/{object_index}:relative_coordinates", allow_out_of_range=True)
            raw_box, box = _clip_prediction_box(raw_box, f"预测 {record_index}/{object_index}:relative_coordinates")
        else:
            raw_box, box = _clip_prediction_box(object_value["xyxy"], f"预测 {record_index}/{object_index}:xyxy")
        result.append(
            Prediction(
                image_key,
                class_id,
                name,
                confidence,
                box,
                object_index,
                raw_box,
                raw_box != box,
            )
        )
    return result


def _load_prediction_records(
    path: Path,
    context: EvaluationContext | None = None,
) -> tuple[list[dict[str, Any]], str | None]:
    """仅在已验证上下文下读取 JSON、records JSON 或 JSONL。"""

    _require_valid_evaluation_context(context)
    if not path.is_file():
        raise EvaluationError(f"预测输入不存在: {path}")
    try:
        if path.suffix.casefold() == ".jsonl":
            records: list[dict[str, Any]] = []
            for line_number, raw_line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
                if not raw_line.strip():
                    continue
                value = json.loads(raw_line)
                if not isinstance(value, dict):
                    raise EvaluationError(f"JSONL 第 {line_number} 行必须是对象")
                records.append(value)
            return records, None
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"预测 JSON/JSONL 不可读取或解析: {path}: {exc}") from exc
    if isinstance(payload, list):
        return payload, None
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        root_format = payload.get("coordinate_format")
        return payload["records"], root_format
    raise EvaluationError("预测 JSON 顶层必须是记录数组，或包含 records 数组的自描述对象")


def bind_predictions(
    prediction_path: Path,
    entries: Sequence[ImageEntry],
    context: EvaluationContext | None = None,
) -> dict[str, list[Prediction]]:
    """按 manifest 原始顺序严格绑定预测 filename、frame_id 和对象。"""

    validated = _require_context_entries(entries, context)
    records, root_format = _load_prediction_records(prediction_path, validated)
    if len(records) != len(validated.entries):
        raise EvaluationError(f"预测记录数 {len(records)} 与 split 图片数 {len(validated.entries)} 不一致")
    bound: dict[str, list[Prediction]] = {}
    document_format: str | None = None
    for position, (record, entry) in enumerate(zip(records, validated.entries), start=1):
        if not isinstance(record, dict):
            raise EvaluationError(f"预测记录 {position} 必须是对象")
        filename = record.get("filename")
        if not isinstance(filename, str) or not filename.strip():
            raise EvaluationError(f"预测记录 {position} 缺少 filename")
        predicted_path = _resolve_input_path(filename, validated.data_root)
        predicted_key = _canonical_path(predicted_path)
        if predicted_key in bound:
            raise EvaluationError(f"预测 filename 重复: {filename}")
        if predicted_key != entry.key:
            raise EvaluationError(
                f"预测记录 {position} filename 错序或错 split；期望 {entry.image_text}，实际 {filename}"
            )
        if "frame_id" in record and (type(record["frame_id"]) is not int or record["frame_id"] != position):
            raise EvaluationError(f"预测记录 {position} frame_id 必须等于清单序号 {position}")
        record_format = _record_coordinate_format(record, root_format, position)
        if document_format is None:
            document_format = record_format
        elif record_format != document_format:
            raise EvaluationError(
                f"预测记录 {position} coordinate_format 与前序记录冲突: {record_format} != {document_format}"
            )
        bound[entry.key] = parse_prediction_record(
            record, entry.key, position, root_format, record_format
        )
    if set(bound) != {entry.key for entry in validated.entries}:
        raise EvaluationError("预测 filename 集合与 manifest split 不一致")
    return bound


def box_iou(left: Sequence[float], right: Sequence[float]) -> float:
    """计算两个 xyxy 框的 IoU。"""

    intersection_left = max(left[0], right[0])
    intersection_top = max(left[1], right[1])
    intersection_right = min(left[2], right[2])
    intersection_bottom = min(left[3], right[3])
    intersection = max(0.0, intersection_right - intersection_left) * max(0.0, intersection_bottom - intersection_top)
    area_left = max(0.0, left[2] - left[0]) * max(0.0, left[3] - left[1])
    area_right = max(0.0, right[2] - right[0]) * max(0.0, right[3] - right[1])
    union = area_left + area_right - intersection
    return intersection / union if union else 0.0


def stable_nms(predictions: Sequence[Prediction], score_threshold: float, nms_iou: float, max_outputs: int) -> list[Prediction]:
    """执行分数阈值、稳定排序、每图截断和类别内 greedy NMS。"""

    candidates = [prediction for prediction in predictions if prediction.confidence >= score_threshold]
    candidates = sorted(candidates, key=lambda item: -item.confidence)[:max_outputs]
    kept: list[Prediction] = []
    for candidate in candidates:
        if any(
            candidate.class_id == existing.class_id and box_iou(candidate.box, existing.box) >= nms_iou
            for existing in kept
        ):
            continue
        kept.append(candidate)
    return kept


def _match_predictions(
    entries: Sequence[ImageEntry],
    ground_truths: dict[str, list[GroundTruth]],
    predictions: dict[str, list[Prediction]],
    class_id: int,
    iou_threshold: float,
) -> tuple[list[bool], list[bool], int]:
    """收集一个类别的全局 TP/FP 标志，执行同图一对一匹配。"""

    selected: list[tuple[int, Prediction]] = []
    for entry in entries:
        selected.extend(
            (entry.index, prediction)
            for prediction in predictions[entry.key]
            if prediction.class_id == class_id
        )
    selected.sort(key=lambda item: (-item[1].confidence, item[0], item[1].source_order))
    matched: dict[str, set[int]] = {entry.key: set() for entry in entries}
    true_positive: list[bool] = []
    false_positive: list[bool] = []
    for _, prediction in selected:
        candidates = [
            (index, box_iou(prediction.box, truth.box))
            for index, truth in enumerate(ground_truths[prediction.image_key])
            if truth.class_id == class_id and index not in matched[prediction.image_key]
        ]
        eligible = [(index, overlap) for index, overlap in candidates if overlap + IOU_EPSILON >= iou_threshold]
        if eligible:
            best_index, _ = max(eligible, key=lambda item: item[1])
            matched[prediction.image_key].add(best_index)
            true_positive.append(True)
            false_positive.append(False)
        else:
            true_positive.append(False)
            false_positive.append(True)
    support = sum(1 for entry in entries for truth in ground_truths[entry.key] if truth.class_id == class_id)
    return true_positive, false_positive, support


def average_precision(true_positive: Sequence[bool], false_positive: Sequence[bool], support: int) -> float | None:
    """按 101 个 recall threshold 计算 all-point interpolation AP。"""

    if support == 0:
        return None
    cumulative_tp = 0
    cumulative_fp = 0
    precisions: list[float] = []
    recalls: list[float] = []
    for is_tp, is_fp in zip(true_positive, false_positive):
        cumulative_tp += int(is_tp)
        cumulative_fp += int(is_fp)
        precisions.append(cumulative_tp / (cumulative_tp + cumulative_fp))
        recalls.append(cumulative_tp / support)
    values = []
    for index in range(AP_POINTS):
        threshold = index / (AP_POINTS - 1)
        eligible = [precision for precision, recall in zip(precisions, recalls) if recall >= threshold]
        values.append(max(eligible, default=0.0))
    return sum(values) / AP_POINTS


def _precision_recall(tp: int, fp: int, fn: int, support: int) -> tuple[float | None, float | None]:
    """计算固定阈值下的 precision 和 recall，空 support 保留 null。"""

    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / support if support else None
    return precision, recall


def _validate_range(value: float, field: str, lower: float, upper: float) -> float:
    """校验有限闭区间参数。"""

    value = _finite(value, field)
    if not lower <= value <= upper:
        raise EvaluationError(f"{field} 必须位于 [{lower}, {upper}]")
    return value


def _subset_images(path: Path | None, entries: Sequence[ImageEntry], data_root: Path, ground_truths: dict[str, list[GroundTruth]], subset_name: str) -> dict[str, Any]:
    """读取可选负样本子集并计算按图误检率。"""

    if path is None:
        return {"status": "NOT_EXECUTED", "reason": f"未提供批准的 {subset_name} 图片集合", "count": None, "false_positive_image_count": None, "false_positive_rate": None}
    if not path.is_file():
        raise EvaluationError(f"{subset_name} subset 文件不存在: {path}")
    try:
        values = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    except (OSError, UnicodeError) as exc:
        raise EvaluationError(f"{subset_name} subset 不可读取: {path}: {exc}") from exc
    entry_map = {entry.key: entry for entry in entries}
    keys: list[str] = []
    for value in values:
        key = _canonical_path(_resolve_input_path(value, data_root))
        if key not in entry_map:
            raise EvaluationError(f"{subset_name} subset 图片不属于当前评估 split: {value}")
        if key in keys:
            raise EvaluationError(f"{subset_name} subset 图片重复: {value}")
        if ground_truths[key]:
            raise EvaluationError(f"{subset_name} subset 必须是空标签负样本: {value}")
        keys.append(key)
    return {"status": "BOUND", "path": str(path), "count": len(keys), "image_keys": keys}


def evaluate_metrics(
    entries: Sequence[ImageEntry],
    ground_truths: dict[str, list[GroundTruth]],
    bound_predictions: dict[str, list[Prediction]],
    score_threshold: float,
    nms_iou: float,
    max_outputs: int,
    context: EvaluationContext | None = None,
) -> dict[str, Any]:
    """执行完整离线指标计算并返回机器可读结果。"""

    validated = _require_context_entries(entries, context)
    expected_keys = {entry.key for entry in validated.entries}
    if set(ground_truths) != expected_keys:
        raise EvaluationError("ground_truths 图片集合与上下文绑定的 manifest split 不一致")
    if set(bound_predictions) != expected_keys:
        raise EvaluationError("predictions 图片集合与上下文绑定的 manifest split 不一致")
    if type(max_outputs) is not int or max_outputs != MAX_OUTPUTS:
        raise EvaluationError(f"max_outputs 必须是整数 {MAX_OUTPUTS}")
    if isinstance(score_threshold, bool) or type(score_threshold) not in (int, float):
        raise EvaluationError("score_threshold 必须是有限数值")
    score_threshold = _validate_range(score_threshold, "score_threshold", 0.25, 0.50)
    if nms_iou != FIXED_NMS_IOU:
        raise EvaluationError(f"nms_iou 必须固定为 {FIXED_NMS_IOU}")
    filtered = {
        key: stable_nms(value, score_threshold, nms_iou, max_outputs)
        for key, value in bound_predictions.items()
    }
    all_predictions = [prediction for values in bound_predictions.values() for prediction in values]
    clipped_predictions = [prediction for prediction in all_predictions if prediction.coordinate_clipped]
    per_class: dict[str, Any] = {}
    ap_by_threshold: dict[str, dict[str, float | None]] = {name: {} for name in EXPECTED_CLASSES}
    for class_id, name in enumerate(EXPECTED_CLASSES):
        support = sum(1 for values in ground_truths.values() for truth in values if truth.class_id == class_id)
        tp_flags, fp_flags, _ = _match_predictions(entries, ground_truths, filtered, class_id, 0.5)
        tp = sum(tp_flags)
        fp = sum(fp_flags)
        fn = support - tp
        precision, recall = _precision_recall(tp, fp, fn, support)
        for threshold in IOU_THRESHOLDS:
            tp_at, fp_at, support_at = _match_predictions(entries, ground_truths, filtered, class_id, threshold)
            ap_by_threshold[name][f"{threshold:.2f}"] = average_precision(tp_at, fp_at, support_at)
        available_values = [value for value in ap_by_threshold[name].values() if value is not None]
        per_class[name] = {
            "class_id": class_id,
            "support_gt": support,
            "prediction_count_after_nms": len([prediction for values in filtered.values() for prediction in values if prediction.class_id == class_id]),
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision_at_score_threshold_iou_0_50": precision,
            "recall_at_score_threshold_iou_0_50": recall,
            "ap_at_0_50": ap_by_threshold[name]["0.50"],
            "ap_by_iou": ap_by_threshold[name],
            "ap_0_50_to_0_95": sum(available_values) / len(available_values) if available_values else None,
            "ap_available": bool(available_values),
        }
    available_classes = [value for value in per_class.values() if value["ap_available"]]
    map_50 = sum(value["ap_at_0_50"] for value in available_classes) / len(available_classes) if available_classes else None
    map_50_95 = sum(value["ap_0_50_to_0_95"] for value in available_classes) / len(available_classes) if available_classes else None
    return {
        "image_count": len(entries),
        "ground_truth_box_count": sum(len(values) for values in ground_truths.values()),
        "prediction_box_count_raw": sum(len(values) for values in bound_predictions.values()),
        "prediction_box_count_after_score_nms": sum(len(values) for values in filtered.values()),
        "coordinate_policy": {
            "name": COORDINATE_POLICY,
            "decision_date": COORDINATE_POLICY_DECISION_DATE,
            "raw_box_must_be_finite": True,
            "raw_box_must_have_positive_area": True,
            "operation": "min(max(value, 0), 1) per xyxy coordinate",
            "clipped_box_must_have_positive_area": True,
            "raw_reject_diagnostic": {
                "path": COORDINATE_POLICY_DIAGNOSTIC_PATH,
                "sha256": COORDINATE_POLICY_DIAGNOSTIC_SHA256,
                "status": "REFERENCE_DIAGNOSTIC_ONLY",
            },
            "raw_out_of_range_box_count": sum(
                1 for prediction in all_predictions if prediction.raw_box is not None and prediction.raw_box != prediction.box
            ),
            "clipped_box_count": len(clipped_predictions),
            "clipped_box_count_after_score_nms": sum(
                1 for values in filtered.values() for prediction in values if prediction.coordinate_clipped
            ),
        },
        "metrics": {
            "mAP@0.5": map_50,
            "mAP@0.5:0.95": map_50_95,
            "iou_thresholds": IOU_THRESHOLDS,
            "ap_interpolation": "101-point all-point interpolation",
            "macro_classes_with_gt_only": len(available_classes),
            "per_class": per_class,
        },
        "predictions_after_nms": filtered,
    }


def _repo_identity() -> dict[str, Any]:
    """现场采集竞赛仓库 HEAD，不执行网络操作。"""

    repository = Path(__file__).resolve().parent.parent
    identity: dict[str, Any] = {"repository": str(repository), "head": "unavailable", "status": "unavailable", "network_access": False}
    try:
        head = subprocess.run(["git", "-C", str(repository), "rev-parse", "HEAD"], capture_output=True, text=True, encoding="utf-8", check=False, timeout=10)
        status = subprocess.run(["git", "-C", str(repository), "status", "--short"], capture_output=True, text=True, encoding="utf-8", check=False, timeout=10)
        if head.returncode == 0 and re.fullmatch(r"[0-9a-fA-F]{40}", head.stdout.strip()):
            identity["head"] = head.stdout.strip()
        if status.returncode == 0:
            identity["status"] = "clean" if not status.stdout.strip() else "dirty"
    except (OSError, subprocess.TimeoutExpired):
        pass
    return identity


def _output_paths_are_safe(predictions: Path, manifest: Path, class_names: Path, report: Path, summary: Path, subsets: Iterable[Path | None]) -> None:
    """拒绝输入输出同路径、报告摘要同路径及覆盖已有输出。"""

    if _canonical_path(report) == _canonical_path(summary):
        raise EvaluationError("--report 与 --summary 不能是同一路径")
    input_paths = [predictions, manifest, class_names, *[path for path in subsets if path is not None]]
    output_keys = {_canonical_path(report), _canonical_path(summary)}
    for input_path in input_paths:
        if _canonical_path(input_path) in output_keys:
            raise EvaluationError("--report/--summary 不能覆盖预测、manifest、names 或 subset 输入")
    for output_path in (report, summary):
        if output_path.exists():
            raise EvaluationError(f"输出文件已存在，为避免覆盖请指定新路径: {output_path}")


def _json_safe(value: Any) -> Any:
    """将内部 Prediction/Path 对象转换为可序列化摘要对象。"""

    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, Prediction):
        return {
            "class_id": value.class_id,
            "name": value.name,
            "confidence": value.confidence,
            "xyxy_normalized": list(value.box),
            "raw_xyxy_normalized": list(value.raw_box) if value.raw_box is not None else None,
            "coordinate_clipped": value.coordinate_clipped,
            "source_order": value.source_order,
        }
    if isinstance(value, Path):
        return str(value)
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    """以 UTF-8、禁止 NaN 的格式写出 JSON。"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_safe(value), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def _summary_text(report: dict[str, Any]) -> str:
    """生成简洁中文摘要，不把 G0 pending 改写为精度通过。"""

    validation = report["validation"]
    metrics = report.get("metrics", {})
    sample_policy = report["sample_policy"]
    official_test = sample_policy["official_test"]
    robustness = sample_policy["robustness"]
    lines = [
        "# S1-T02-D6 离线检测指标证据",
        "",
        f"状态：`{report['status']}`；schema_valid=`{validation['schema_valid']}`；errors={len(validation['errors'])}。",
        "本文件只验证离线评估口径和夹具/输入绑定，不代表正式训练、正式浮点/INT8 精度、G0/G4 或板上通过。",
        "",
        "## 固定评估配置",
        "",
        f"- split：`{report['evaluation']['split']}`；图片数：`{report['counts']['image_count']}`；GT 框数：`{report['counts']['ground_truth_box_count']}`。",
        f"- score threshold：`{report['evaluation']['score_threshold']}`；NMS：类别内 greedy IoU=`{report['evaluation']['nms_iou']}`；每图最大输出=`{report['evaluation']['max_outputs']}`。",
        "- AP：IoU 0.50:0.05:0.95、101-point all-point interpolation、五类宏平均；无 GT 类别保留 support 并不静默计入0。",
        f"- mAP@0.5：`{metrics.get('mAP@0.5')}`；mAP@0.5:0.95：`{metrics.get('mAP@0.5:0.95')}`（仅夹具/当前输入结果）。",
        f"- 坐标政策：`{report['evaluation']['coordinate_policy']['name']}`；有限正面积框逐坐标裁剪到 `[0,1]`，裁剪后零面积仍拒绝；本次 raw 越界框=`{report['coordinate_diagnostics']['raw_out_of_range_box_count']}`，实际裁剪=`{report['coordinate_diagnostics']['clipped_box_count']}`。",
        "",
        "## 绑定与限制",
        "",
        f"- manifest、预测、names 和代码 SHA 见机器报告：`{report['report_path']}`。",
        f"- 批准样本政策决策日期：`{sample_policy['decision_date']}`；正式口径文档 SHA-256：`{sample_policy['decision_document']['sha256']}`。",
        f"- 官方 test：批准 manifest SHA-256=`{official_test['approved_manifest_sha256']}`，完整图片数=`{official_test['required_image_count']}`；本次绑定状态=`{official_test['runtime_binding_status']}`。",
        f"- 独立 robustness：每个目标类别至少 `{robustness['minimum_unique_images_per_class']}` 张、每个条件 bucket 至少 `{min(robustness['condition_bucket_minimum_unique_images'].values())}` 张；实际数据绑定=`{robustness['dataset_binding_status']}`。",
        f"- 完整 G0 指标策略快照：`{sample_policy['metric_policy_evidence']['status']}`；test/robustness 在策略获批并哈希绑定前阻断。",
        f"- no_hand 误检率：`{report['subsets']['no_hand']['status']}`；non-target 误检率：`{report['subsets']['non_target']['status']}`。缺少批准 subset 时不生成0%。",
        "- 仍未决：最终 score threshold、mAP 与逐类 precision/recall 验收门槛，以及 robustness 数据集构建和人物/session 隔离审计。test/robustness 不得重新调参。",
        "- 本轮未启动 Darknet、训练、权重下载、INT8 整网或硬件测量。",
        "",
        "## 验证",
        "",
        "- 评估器使用显式 relative_coordinates 或 xyxy_normalized，严格拒绝缺失、重复、额外、错序 filename/frame_id、非法类别、非有限/非正面积坐标和输出覆盖；有限正面积的越界框按冻结政策裁剪。",
        "- 预测输出中的对象字段保留 class_id/name、confidence、裁剪后和 raw 归一化 xyxy；原始预测输入保持外部/夹具位置，不被报告覆盖。",
    ]
    return "\n".join(lines) + "\n"


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    """读取输入并构建完整离线评估报告。"""

    allowed_splits = {*APPROVED_SPLIT_IMAGE_COUNTS, "robustness"}
    if not isinstance(args.split, str) or args.split not in allowed_splits:
        raise EvaluationError(f"split 非规范；只允许 {sorted(allowed_splits)}，不接受大小写/别名映射")
    manifest = args.manifest.resolve()
    predictions = args.predictions.resolve()
    class_names_path = args.class_names.resolve()
    data_root = args.data_root.resolve()
    labels_root = args.labels_root.resolve()
    report_path = args.report.resolve()
    summary_path = args.summary.resolve()
    _output_paths_are_safe(predictions, manifest, class_names_path, report_path, summary_path, (args.no_hand_list, args.non_target_list))
    context = create_evaluation_context(manifest, data_root, labels_root, args.split)
    names = _read_class_names(class_names_path)
    score_threshold = _validate_range(args.score_threshold, "score-threshold", 0.25, 0.50)
    nms_iou = _finite(args.nms_iou, "nms-iou")
    if nms_iou != FIXED_NMS_IOU:
        raise EvaluationError(f"nms-iou 必须固定为 {FIXED_NMS_IOU}")
    if type(args.max_outputs) is not int or args.max_outputs != MAX_OUTPUTS:
        raise EvaluationError(f"max-outputs 必须固定为 {MAX_OUTPUTS}")
    entries = load_manifest(context)
    ground_truths = load_ground_truths(entries, context)
    bound_predictions = bind_predictions(predictions, entries, context)
    measured = evaluate_metrics(entries, ground_truths, bound_predictions, score_threshold, nms_iou, args.max_outputs, context)

    def subset_result(path: Path | None, name: str) -> dict[str, Any]:
        value = _subset_images(path, entries, data_root, ground_truths, name)
        if value["status"] == "BOUND":
            keys = value.pop("image_keys")
            false_positive_count = sum(1 for key in keys if measured["predictions_after_nms"][key])
            value.update({"false_positive_image_count": false_positive_count, "false_positive_rate": false_positive_count / len(keys) if keys else None})
        return value

    subset_values = {"no_hand": subset_result(args.no_hand_list, "no_hand"), "non_target": subset_result(args.non_target_list, "non_target")}
    sample_policy = {
        "decision_date": G0_DECISION_DATE,
        "decision_document": {
            "path": G0_POLICY_DOCUMENT_PATH,
            "sha256": G0_POLICY_DOCUMENT_SHA256,
        },
        "metric_policy_evidence": {
            "status": "MISSING" if APPROVED_G0_METRIC_POLICY_EVIDENCE is None else "UNSUPPORTED",
            "binding": APPROVED_G0_METRIC_POLICY_EVIDENCE,
            "required_for_splits": ["test", "robustness"],
        },
        "official_test": {
            "approved_manifest_sha256": APPROVED_TEST_MANIFEST_SHA256,
            "required_image_count": APPROVED_TEST_IMAGE_COUNT,
            "runtime_binding_status": "BOUND" if args.split == "test" else "NOT_EVALUATED",
            "runtime_manifest_sha256": context.manifest_sha256,
            "runtime_test_image_count": len(entries) if args.split == "test" else None,
        },
        "robustness": {
            "minimum_unique_images_per_class": ROBUSTNESS_MIN_IMAGES_PER_CLASS,
            "target_classes": list(EXPECTED_CLASSES),
            "condition_bucket_minimum_unique_images": dict(ROBUSTNESS_CONDITION_BUCKETS),
            "unique_count_basis": "image",
            "same_image_may_count_in_multiple_condition_buckets": True,
            "multiple_bucket_membership_requires_evidence": True,
            "no_hand_is_a_target_class": False,
            "person_and_session_must_be_disjoint_from": ["train", "val", "test"],
            "dataset_binding_status": "PENDING",
            "observed_counts": None,
            "person_session_isolation_audit_status": "PENDING",
        },
    }
    g0_open_items = [
        {"id": "complete_metric_policy_snapshot", "status": "OPEN", "requirement": "完整获批且哈希绑定的指标策略快照尚不存在；test/robustness 必须阻断。"},
        {"id": "final_score_threshold", "status": "OPEN", "requirement": "在 val 的 0.25..0.50 范围内选择并冻结；test/robustness 不调参。"},
        {"id": "map_acceptance_threshold", "status": "OPEN", "requirement": "正式 mAP 验收门槛尚未冻结。"},
        {"id": "per_class_precision_recall_thresholds", "status": "OPEN", "requirement": "每类 precision/recall 验收门槛尚未全部冻结。"},
        {"id": "robustness_dataset_and_isolation", "status": "OPEN", "requirement": "robustness 实际数据集、类别/条件计数及 person/session 隔离证据尚未绑定。"},
    ]
    report: dict[str, Any] = {
        "schema_version": "s1-t02-d6-detection-metrics-v1",
        "task": "S1-T02-D6",
        "generated_utc8": _now_iso(),
        "status": "G0_PENDING",
        "validation": {"schema_valid": True, "errors": [], "warnings": ["样本数量政策已批准；最终阈值、指标验收门槛和 robustness 数据集绑定仍未完成"], "status": "G0_PENDING"},
        "code": {"path": str(Path(__file__).resolve()), "sha256": sha256_file(Path(__file__).resolve()), "repository": _repo_identity()},
        "inputs": {
            "manifest": {"path": str(manifest), "sha256": context.manifest_sha256},
            "predictions": {"path": str(predictions), "sha256": sha256_file(predictions)},
            "class_names": {"path": str(class_names_path), "sha256": sha256_file(class_names_path), "values": names},
            "data_root": str(data_root),
            "labels_root": str(labels_root),
            "no_hand_list": {"path": str(args.no_hand_list.resolve()), "sha256": sha256_file(args.no_hand_list.resolve())} if args.no_hand_list else None,
            "non_target_list": {"path": str(args.non_target_list.resolve()), "sha256": sha256_file(args.non_target_list.resolve())} if args.non_target_list else None,
        },
        "evaluation": {
            "split": args.split,
            "score_threshold": score_threshold,
            "threshold_selection": "val 0.25-0.50 选择后固定；本轮只绑定 CLI 值，G0_PENDING",
            "nms": "class-wise greedy",
            "nms_iou": nms_iou,
            "max_outputs": args.max_outputs,
            "coordinate_formats": ["darknet_relative_coordinates", "xyxy_normalized"],
            "coordinate_policy": {
                "name": COORDINATE_POLICY,
                "decision_date": COORDINATE_POLICY_DECISION_DATE,
                "description": "有限且原始正面积的预测框逐坐标裁剪到[0,1]；裁剪后零面积或完全在图像外的框拒绝。",
                "raw_reject_diagnostic": {
                    "path": COORDINATE_POLICY_DIAGNOSTIC_PATH,
                    "sha256": COORDINATE_POLICY_DIAGNOSTIC_SHA256,
                    "status": "REFERENCE_DIAGNOSTIC_ONLY",
                },
            },
            "matching": "同图同类一对一，IoU>=阈值，score 降序稳定排序",
            "test_and_robustness_retuning": "forbidden",
        },
        "counts": {key: measured[key] for key in ("image_count", "ground_truth_box_count", "prediction_box_count_raw", "prediction_box_count_after_score_nms")},
        "coordinate_diagnostics": measured["coordinate_policy"],
        "sample_policy": sample_policy,
        "g0_open_items": g0_open_items,
        "metrics": measured["metrics"],
        "subsets": subset_values,
        "outputs": {"report": str(report_path), "summary": str(summary_path)},
        "limitations": [
            "本轮未启动 Darknet 或任何正式模型推理；输入可以是夹具或外部生成的 raw JSON，但 raw JSON 不等于 mAP。",
            "官方 test 样本口径已绑定，但 robustness 实际数据集尚未构建/绑定；最终 score threshold 和 mAP/逐类 precision-recall 验收门槛仍未冻结，因此状态保持 G0_PENDING。",
            "mAP 和辅助误检率不构成最终验收门槛通过；no_hand/non-target 未提供批准集合时为 NOT_EXECUTED。",
        ],
    }
    report["report_path"] = str(report_path)
    return report


def _parser() -> argparse.ArgumentParser:
    """构建独立、无副作用的 CLI。"""

    parser = argparse.ArgumentParser(description="S1-T02-D6 PC 检测结果离线评估器")
    parser.add_argument("--manifest", type=Path, required=True, help="包含 image/label/split 的 manifest CSV")
    parser.add_argument("--data-root", type=Path, required=True, help="解析 manifest 和预测 filename 的数据根目录")
    parser.add_argument("--labels-root", type=Path, required=True, help="解析 manifest label 字段的根目录")
    parser.add_argument("--predictions", type=Path, required=True, help="Darknet 数组 JSON 或每行一个记录的 JSONL")
    parser.add_argument("--class-names", type=Path, required=True, help="五类 names 文件")
    parser.add_argument("--split", required=True, help="严格评估的 manifest split，例如 val 或 test")
    parser.add_argument("--score-threshold", type=float, required=True, help="固定 score threshold，必须在0.25..0.50")
    parser.add_argument("--nms-iou", type=float, default=0.45, help="类别内 greedy NMS IoU，默认0.45")
    parser.add_argument("--max-outputs", type=int, default=15, help="每图最大预测框数，默认15")
    parser.add_argument("--no-hand-list", type=Path, help="可选的批准 no_hand 图片清单")
    parser.add_argument("--non-target-list", type=Path, help="可选的批准 non-target 图片清单")
    parser.add_argument("--report", type=Path, required=True, help="独立 JSON 报告输出")
    parser.add_argument("--summary", type=Path, required=True, help="独立 Markdown 摘要输出")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """执行离线评估，输入非法时返回2且不覆盖输入。"""

    parser = _parser()
    try:
        args = parser.parse_args(argv)
        report = build_report(args)
        report_path = Path(report["outputs"]["report"])
        summary_path = Path(report["outputs"]["summary"])
        _write_json(report_path, report)
        summary_path.write_text(_summary_text(report), encoding="utf-8", newline="\n")
        print(json.dumps({"status": report["status"], "errors": report["validation"]["errors"], "report": str(report_path), "summary": str(summary_path)}, ensure_ascii=False, indent=2))
        return 0
    except EvaluationError as exc:
        print(f"D6_ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception:
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
