#!/usr/bin/env python3
"""S1-T01 数据清单、YOLO 标签、分组隔离和重复内容检查器。"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import html
import json
import math
import struct
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable


CLASS_NAMES = ("fist", "palm", "one", "two_up", "three")
CLASS_TO_ID = {name: index for index, name in enumerate(CLASS_NAMES)}
VALID_SPLITS = ("train", "val", "test")
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".ppm", ".pgm"}
MANIFEST_COLUMNS = (
    "image",
    "label",
    "split",
    "session_id",
    "person_id",
    "source",
    "license",
    "is_real",
)


@dataclass(frozen=True)
class Thresholds:
    """S1-T01 小样本流程门槛；不代表正式模型精度门槛。"""

    min_images: int = 30
    min_boxes_per_class: int = 5
    min_no_hand_images: int = 5


@dataclass
class RowResult:
    """清单行经过路径和标签检查后的内部结果。"""

    row_number: int
    values: dict[str, str]
    image_path: Path | None = None
    label_path: Path | None = None
    image_info: dict[str, int | str] | None = None
    image_sha256: str | None = None
    labels: list[tuple[int, float, float, float, float]] | None = None


def _now_iso() -> str:
    """返回东八区带偏移量的当前时间。"""

    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).isoformat(timespec="seconds")


def _error(report: dict, message: str) -> None:
    """向报告追加错误，保持错误顺序稳定。"""

    report["errors"].append(message)


def _warning(report: dict, message: str) -> None:
    """向报告追加非阻断提醒。"""

    report["warnings"].append(message)


def _parse_bool(value: str) -> bool:
    """解析清单中的布尔值。"""

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise ValueError(f"无法解析布尔值: {value!r}")


def _safe_path(root: Path, relative: str) -> Path:
    """解析相对路径并拒绝越出数据根目录。"""

    root_resolved = root.resolve()
    candidate = (root / relative).resolve()
    if candidate != root_resolved and root_resolved not in candidate.parents:
        raise ValueError(f"路径越出数据根目录: {relative}")
    return candidate


def _sha256(path: Path) -> str:
    """计算文件 SHA-256。"""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_png_info(path: Path) -> dict[str, int | str]:
    """读取 PNG 基本尺寸。"""

    with path.open("rb") as stream:
        header = stream.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise ValueError("PNG 文件头无效")
    width, height = struct.unpack(">II", header[16:24])
    if width <= 0 or height <= 0:
        raise ValueError("PNG 尺寸无效")
    return {"format": "png", "width": width, "height": height}


def _read_bmp_info(path: Path) -> dict[str, int | str]:
    """读取 BMP 基本尺寸。"""

    with path.open("rb") as stream:
        header = stream.read(26)
    if len(header) < 26 or header[:2] != b"BM":
        raise ValueError("BMP 文件头无效")
    width, signed_height = struct.unpack_from("<ii", header, 18)
    height = abs(signed_height)
    if width <= 0 or height <= 0:
        raise ValueError("BMP 尺寸无效")
    return {"format": "bmp", "width": width, "height": height}


def _read_jpeg_info(path: Path) -> dict[str, int | str]:
    """扫描 JPEG 标记并读取首个有效帧尺寸。"""

    sof_markers = set(range(0xC0, 0xC4)) | set(range(0xC5, 0xC8)) | set(range(0xC9, 0xCC)) | set(range(0xCD, 0xD0))
    with path.open("rb") as stream:
        if stream.read(2) != b"\xff\xd8":
            raise ValueError("JPEG 文件头无效")
        while True:
            byte = stream.read(1)
            if not byte:
                break
            if byte != b"\xff":
                continue
            marker_byte = stream.read(1)
            while marker_byte == b"\xff":
                marker_byte = stream.read(1)
            if not marker_byte:
                break
            marker = marker_byte[0]
            if marker == 0xD9:
                break
            if marker == 0xDA:
                break
            if marker == 0x01 or 0xD0 <= marker <= 0xD8:
                continue
            length_bytes = stream.read(2)
            if len(length_bytes) != 2:
                break
            length = struct.unpack(">H", length_bytes)[0]
            if length < 2:
                raise ValueError("JPEG 段长度无效")
            segment = stream.read(length - 2)
            if len(segment) != length - 2:
                raise ValueError("JPEG 段被截断")
            if marker in sof_markers and len(segment) >= 5:
                height, width = struct.unpack(">HH", segment[1:5])
                if width > 0 and height > 0:
                    return {"format": "jpeg", "width": width, "height": height}
    raise ValueError("JPEG 未找到有效帧尺寸")


def _read_pnm_info(path: Path) -> dict[str, int | str]:
    """读取 PPM/PGM 文本头部尺寸。"""

    tokens: list[bytes] = []
    current = bytearray()
    with path.open("rb") as stream:
        while len(tokens) < 4:
            byte = stream.read(1)
            if not byte:
                break
            if byte == b"#":
                stream.readline()
                continue
            if byte.isspace():
                if current:
                    tokens.append(bytes(current))
                    current.clear()
                continue
            current.extend(byte)
        if current and len(tokens) < 4:
            tokens.append(bytes(current))
    if len(tokens) < 4 or tokens[0] not in {b"P5", b"P6"}:
        raise ValueError("PNM 文件头无效")
    try:
        width, height, maximum = int(tokens[1]), int(tokens[2]), int(tokens[3])
    except ValueError as exc:
        raise ValueError("PNM 尺寸或最大值不是整数") from exc
    if width <= 0 or height <= 0 or maximum <= 0:
        raise ValueError("PNM 尺寸或最大值无效")
    return {"format": tokens[0].decode("ascii").lower(), "width": width, "height": height}


def read_image_info(path: Path) -> dict[str, int | str]:
    """用标准库读取支持格式的图片头部，确认文件可被基本解析。"""

    suffix = path.suffix.lower()
    if suffix not in IMAGE_SUFFIXES:
        raise ValueError(f"不支持的图片后缀: {suffix or '<无后缀>'}")
    if suffix == ".png":
        return _read_png_info(path)
    if suffix == ".bmp":
        return _read_bmp_info(path)
    if suffix in {".jpg", ".jpeg"}:
        return _read_jpeg_info(path)
    return _read_pnm_info(path)


def parse_yolo_label(path: Path) -> list[tuple[int, float, float, float, float]]:
    """解析并校验归一化 YOLO 标签。"""

    text = path.read_text(encoding="utf-8-sig")
    labels: list[tuple[int, float, float, float, float]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) != 5:
            raise ValueError(f"第 {line_number} 行应有 5 列，实际为 {len(fields)} 列")
        try:
            class_id = int(fields[0])
            values = tuple(float(value) for value in fields[1:])
        except ValueError as exc:
            raise ValueError(f"第 {line_number} 行存在非数字字段") from exc
        if class_id < 0 or class_id >= len(CLASS_NAMES):
            raise ValueError(f"第 {line_number} 行 class_id 越界: {class_id}")
        if not all(math.isfinite(value) for value in values):
            raise ValueError(f"第 {line_number} 行存在 NaN 或 Inf")
        center_x, center_y, width, height = values
        if not all(0.0 <= value <= 1.0 for value in values):
            raise ValueError(f"第 {line_number} 行坐标不在 [0, 1] 内")
        if width <= 0.0 or height <= 0.0:
            raise ValueError(f"第 {line_number} 行框宽高必须为正")
        labels.append((class_id, center_x, center_y, width, height))
    return labels


def _new_report(root: Path, manifest: Path, thresholds: Thresholds) -> dict:
    """创建稳定结构的 JSON 报告。"""

    return {
        "schema_version": 1,
        "created_at_utc8": _now_iso(),
        "data_root": str(root),
        "manifest": str(manifest),
        "class_mapping": {str(index): name for index, name in enumerate(CLASS_NAMES)},
        "thresholds": {
            "min_images": thresholds.min_images,
            "min_boxes_per_class": thresholds.min_boxes_per_class,
            "min_no_hand_images": thresholds.min_no_hand_images,
        },
        "status": "FAIL",
        "errors": [],
        "warnings": [],
        "metrics": {},
        "checks": {},
        "preview_candidates": [],
        "preview_files": [],
    }


def _load_manifest(path: Path, report: dict) -> list[RowResult]:
    """读取 CSV 清单并检查字段完整性。"""

    if not path.is_file():
        _error(report, f"清单不存在: {path}")
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fieldnames = tuple(reader.fieldnames or ())
            missing = [column for column in MANIFEST_COLUMNS if column not in fieldnames]
            if missing:
                _error(report, f"清单缺少必需列: {', '.join(missing)}")
                return []
            rows: list[RowResult] = []
            for row_number, raw in enumerate(reader, start=2):
                values = {key: (raw.get(key) or "").strip() for key in MANIFEST_COLUMNS}
                if not any(values.values()):
                    _warning(report, f"清单第 {row_number} 行为空，已跳过")
                    continue
                rows.append(RowResult(row_number=row_number, values=values))
            return rows
    except UnicodeDecodeError as exc:
        _error(report, f"清单不是 UTF-8 编码: {path} ({exc})")
    except OSError as exc:
        _error(report, f"读取清单失败: {path} ({exc})")
    return []


def _check_row(row: RowResult, root: Path, report: dict) -> None:
    """检查单条清单记录的字段、图片和标签。"""

    values = row.values
    required_text = ("image", "label", "split", "session_id", "person_id", "source", "license")
    for field in required_text:
        if not values[field]:
            _error(report, f"清单第 {row.row_number} 行缺少 {field}")
    if values["split"] not in VALID_SPLITS:
        _error(report, f"清单第 {row.row_number} 行 split 无效: {values['split']!r}")
    try:
        values["is_real"] = "true" if _parse_bool(values["is_real"]) else "false"
    except ValueError as exc:
        _error(report, f"清单第 {row.row_number} 行 is_real 无效: {exc}")
        return
    try:
        row.image_path = _safe_path(root, values["image"])
        row.label_path = _safe_path(root, values["label"])
    except ValueError as exc:
        _error(report, f"清单第 {row.row_number} 行路径无效: {exc}")
        return
    if row.image_path is None or not row.image_path.is_file():
        _error(report, f"清单第 {row.row_number} 行图片不存在: {values['image']}")
    else:
        try:
            row.image_info = read_image_info(row.image_path)
            row.image_sha256 = _sha256(row.image_path)
        except (OSError, ValueError, UnicodeError) as exc:
            _error(report, f"清单第 {row.row_number} 行图片不可解析: {values['image']} ({exc})")
    if row.label_path is None or not row.label_path.is_file():
        _error(report, f"清单第 {row.row_number} 行标签不存在: {values['label']}")
    else:
        try:
            row.labels = parse_yolo_label(row.label_path)
        except (OSError, ValueError, UnicodeError) as exc:
            _error(report, f"清单第 {row.row_number} 行标签无效: {values['label']} ({exc})")


def _group_overlaps(rows: Iterable[RowResult]) -> dict[str, list[str]]:
    """返回 train/val/test 之间重复的人员或会话。"""

    overlaps: dict[str, list[str]] = {}
    for field in ("session_id", "person_id"):
        by_split: dict[str, set[str]] = defaultdict(set)
        for row in rows:
            split = row.values["split"]
            value = row.values[field]
            if split in VALID_SPLITS and value:
                by_split[split].add(value)
        for left_index, left in enumerate(VALID_SPLITS):
            for right in VALID_SPLITS[left_index + 1 :]:
                common = sorted(by_split[left] & by_split[right])
                if common:
                    overlaps[f"{field}:{left}/{right}"] = common
    return overlaps


def _choose_preview_candidates(rows: list[RowResult]) -> list[RowResult]:
    """确定每类两个框和五个无手样本的抽查候选。"""

    no_hand = [row for row in rows if row.labels == []]
    result: list[RowResult] = []
    for class_id in range(len(CLASS_NAMES)):
        class_rows = [row for row in rows if row.labels and any(label[0] == class_id for label in row.labels)]
        result.extend(class_rows[:2])
    result.extend(no_hand[:5])
    unique: list[RowResult] = []
    seen: set[int] = set()
    for row in result:
        if row.row_number not in seen:
            unique.append(row)
            seen.add(row.row_number)
    return unique


def _write_svg_preview(row: RowResult, preview_dir: Path, index: int) -> Path | None:
    """生成自包含 SVG 叠框抽查图。"""

    if row.image_path is None or row.image_info is None or row.labels is None:
        return None
    width = int(row.image_info["width"])
    height = int(row.image_info["height"])
    mime = {"png": "image/png", "jpeg": "image/jpeg", "bmp": "image/bmp", "p5": "image/x-portable-graymap", "p6": "image/x-portable-pixmap"}.get(str(row.image_info["format"]))
    if mime is None:
        return None
    encoded = base64.b64encode(row.image_path.read_bytes()).decode("ascii")
    shapes: list[str] = []
    for class_id, center_x, center_y, box_width, box_height in row.labels:
        x = (center_x - box_width / 2.0) * width
        y = (center_y - box_height / 2.0) * height
        w = box_width * width
        h = box_height * height
        label = html.escape(f"{CLASS_NAMES[class_id]} ({class_id})")
        shapes.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="none" stroke="#ff3030" stroke-width="3"/><text x="{max(0.0, x):.2f}" y="{max(16.0, y + 16.0):.2f}" fill="#ff3030" font-size="16" stroke="#ffffff" stroke-width="3" paint-order="stroke">{label}</text>'
        )
    file_name = f"preview_{index:02d}_row{row.row_number}.svg"
    preview_dir.mkdir(parents=True, exist_ok=True)
    output = preview_dir / file_name
    source = html.escape(str(row.values["image"]))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<title>{source}</title><image href="data:{mime};base64,{encoded}" width="{width}" height="{height}"/>'
        + "".join(shapes)
        + "</svg>\n"
    )
    output.write_text(svg, encoding="utf-8", newline="\n")
    return output


def validate_dataset(root: Path, manifest: Path, thresholds: Thresholds, preview_dir: Path | None = None) -> dict:
    """执行 S1-T01 数据集自动检查并返回 JSON 兼容报告。"""

    report = _new_report(root, manifest, thresholds)
    if not root.is_dir():
        _error(report, f"数据根目录不存在: {root}")
        report["checks"] = {"AC02": "未执行", "AC03": "未执行", "AC04": "未执行"}
        return report
    rows = _load_manifest(manifest, report)
    for row in rows:
        _check_row(row, root, report)

    valid_rows = [row for row in rows if row.image_info is not None and row.labels is not None]
    image_paths = Counter(row.values["image"] for row in rows)
    for image, count in image_paths.items():
        if count > 1:
            _error(report, f"图片在清单中重复出现 {count} 次: {image}")

    split_rows: dict[str, list[RowResult]] = {split: [] for split in VALID_SPLITS}
    class_counts = Counter()
    split_class_counts: dict[str, Counter] = {split: Counter() for split in VALID_SPLITS}
    split_no_hand = Counter()
    image_hash_splits: dict[str, set[str]] = defaultdict(set)
    real_images = 0
    total_boxes = 0
    non_real_images = 0
    for row in valid_rows:
        split = row.values["split"]
        if split not in VALID_SPLITS:
            continue
        split_rows[split].append(row)
        if row.values["is_real"] == "true":
            real_images += 1
        else:
            non_real_images += 1
        if row.image_sha256:
            image_hash_splits[row.image_sha256].add(split)
        if row.labels == []:
            split_no_hand[split] += 1
        for class_id, *_ in row.labels:
            class_counts[class_id] += 1
            split_class_counts[split][class_id] += 1
            total_boxes += 1
    for image_hash, splits in sorted(image_hash_splits.items()):
        if len(splits) > 1:
            _error(report, f"相同图片内容跨集合重复: {image_hash[:16]} ({', '.join(sorted(splits))})")
    overlaps = _group_overlaps(rows)
    for key, values in overlaps.items():
        _error(report, f"人员/会话跨集合交叉 {key}: {', '.join(values)}")

    report["metrics"] = {
        "manifest_rows": len(rows),
        "valid_rows": len(valid_rows),
        "real_images": real_images,
        "non_real_images": non_real_images,
        "total_boxes": total_boxes,
        "boxes_per_class": {CLASS_NAMES[class_id]: class_counts[class_id] for class_id in range(len(CLASS_NAMES))},
        "images_per_split": {split: len(split_rows[split]) for split in VALID_SPLITS},
        "boxes_per_split": {split: {CLASS_NAMES[class_id]: split_class_counts[split][class_id] for class_id in range(len(CLASS_NAMES))} for split in VALID_SPLITS},
        "no_hand_images_per_split": {split: split_no_hand[split] for split in VALID_SPLITS},
        "session_person_overlap": overlaps,
    }

    ac02_ok = bool(rows) and all(row.values["source"] and row.values["license"] for row in rows)
    report["checks"]["AC02"] = "通过自动检查" if ac02_ok else "未通过"

    ac03_reasons: list[str] = []
    if real_images < thresholds.min_images:
        ac03_reasons.append(f"真实图片 {real_images} < {thresholds.min_images}")
    for class_id, class_name in enumerate(CLASS_NAMES):
        if class_counts[class_id] < thresholds.min_boxes_per_class:
            ac03_reasons.append(f"{class_name} 框数 {class_counts[class_id]} < {thresholds.min_boxes_per_class}")
    if sum(split_no_hand.values()) < thresholds.min_no_hand_images:
        ac03_reasons.append(f"无手图片 {sum(split_no_hand.values())} < {thresholds.min_no_hand_images}")
    for split in ("train", "val"):
        if not split_rows[split]:
            ac03_reasons.append(f"缺少 {split} 集")
        if any(split_class_counts[split][class_id] == 0 for class_id in range(len(CLASS_NAMES))):
            ac03_reasons.append(f"{split} 集未覆盖全部五类")
        if split_no_hand[split] == 0:
            ac03_reasons.append(f"{split} 集缺少无手图片")
    if overlaps:
        ac03_reasons.append("人员或会话跨集合交叉")
    report["checks"]["AC03"] = "通过自动检查" if not ac03_reasons else "未通过: " + "；".join(ac03_reasons)

    ac04_reasons: list[str] = []
    if len(valid_rows) != len(rows):
        ac04_reasons.append("存在图片或标签自动检查失败")
    if any(len(splits) > 1 for splits in image_hash_splits.values()):
        ac04_reasons.append("存在跨集合重复图片内容")
    if ac04_reasons:
        report["checks"]["AC04"] = "未通过: " + "；".join(ac04_reasons)
    elif not rows:
        report["checks"]["AC04"] = "未执行"
    else:
        report["checks"]["AC04"] = "待人工抽查：每类2框及5张无手图"

    candidates = _choose_preview_candidates(valid_rows)
    report["preview_candidates"] = [
        {
            "row_number": row.row_number,
            "image": row.values["image"],
            "split": row.values["split"],
            "session_id": row.values["session_id"],
            "person_id": row.values["person_id"],
            "classes": sorted({CLASS_NAMES[label[0]] for label in row.labels or []}),
        }
        for row in candidates
    ]
    if preview_dir is not None:
        for index, row in enumerate(candidates, start=1):
            preview = _write_svg_preview(row, preview_dir, index)
            if preview is not None:
                report["preview_files"].append(str(preview))

    if not report["errors"] and report["checks"].get("AC03") == "通过自动检查":
        report["status"] = "PASS_AUTOMATED_MANUAL_PENDING"
        _warning(report, "AC04 的人工可视化抽查仍需由 Wong 观察并回传结果")
    return report


def _build_parser() -> argparse.ArgumentParser:
    """构建命令行解析器。"""

    parser = argparse.ArgumentParser(description="检查 S1-T01 五类带框数据清单、标签和分组隔离")
    parser.add_argument("--data-root", type=Path, required=True, help="数据根目录，清单中的路径相对该目录")
    parser.add_argument("--manifest", type=Path, required=True, help="UTF-8 CSV 清单路径")
    parser.add_argument("--report", type=Path, help="输出 JSON 报告路径")
    parser.add_argument("--preview-dir", type=Path, help="输出自包含 SVG 抽查图目录")
    parser.add_argument("--min-images", type=int, default=30, help="真实图片最低数量，默认30")
    parser.add_argument("--min-boxes-per-class", type=int, default=5, help="每类最低框数，默认5")
    parser.add_argument("--min-no-hand-images", type=int, default=5, help="无手图片最低数量，默认5")
    return parser


def main(argv: list[str] | None = None) -> int:
    """执行检查、打印摘要并按检查结果返回退出码。"""

    parser = _build_parser()
    args = parser.parse_args(argv)
    thresholds = Thresholds(
        min_images=args.min_images,
        min_boxes_per_class=args.min_boxes_per_class,
        min_no_hand_images=args.min_no_hand_images,
    )
    report = validate_dataset(args.data_root, args.manifest, thresholds, args.preview_dir)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": report["status"], "checks": report["checks"], "metrics": report["metrics"], "errors": report["errors"], "warnings": report["warnings"]}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS_AUTOMATED_MANUAL_PENDING" else 2


if __name__ == "__main__":
    sys.exit(main())
