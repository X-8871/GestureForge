#!/usr/bin/env python3
"""将 HaGRIDv2 目标类别标注转换为 S1-T01 的 YOLO 清单。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator


CLASS_NAMES = ("fist", "palm", "one", "two_up", "three")
CLASS_TO_ID = {name: index for index, name in enumerate(CLASS_NAMES)}
VALID_SPLITS = ("train", "val", "test")
IGNORED_LABELS = {"no_gesture"}
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
SOURCE = "HaGRIDv2 official dataset; https://github.com/hukenovs/hagrid"
LICENSE = (
    "Public license with attribution and conditions reserved; "
    "see license/en_us.pdf"
)
SOURCE_URLS = {
    "fist": (
        "https://rndml-team-cv.obs.ru-moscow-1.hc.sbercloud.ru/datasets/"
        "hagrid/hagrid_dataset_new_554800/hagrid_dataset/fist.zip"
    ),
    "palm": (
        "https://rndml-team-cv.obs.ru-moscow-1.hc.sbercloud.ru/datasets/"
        "hagrid/hagrid_dataset_new_554800/hagrid_dataset/palm.zip"
    ),
    "one": (
        "https://rndml-team-cv.obs.ru-moscow-1.hc.sbercloud.ru/datasets/"
        "hagrid_v2/hagrid_v2_zip/one.zip"
    ),
    "two_up": (
        "https://rndml-team-cv.obs.ru-moscow-1.hc.sbercloud.ru/datasets/"
        "hagrid/hagrid_dataset_new_554800/hagrid_dataset/two_up.zip"
    ),
    "three": (
        "https://rndml-team-cv.obs.ru-moscow-1.hc.sbercloud.ru/datasets/"
        "hagrid/hagrid_dataset_new_554800/hagrid_dataset/three.zip"
    ),
    "no_gesture": (
        "https://rndml-team-cv.obs.ru-moscow-1.hc.sbercloud.ru/datasets/"
        "hagrid_v2/hagrid_v2_zip/no_gesture.zip"
    ),
}


def _now_iso() -> str:
    """返回东八区带偏移量的当前时间。"""

    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _relative(path: Path, root: Path) -> str:
    """生成适合清单跨平台消费的正斜杠相对路径。"""

    return path.relative_to(root).as_posix()


def _find_annotation_root(data_root: Path) -> Path:
    """定位官方 annotations.zip 解压后的标注根目录。"""

    candidates = (data_root / "dataset" / "annotations" / "annotations", data_root / "dataset" / "annotations")
    for candidate in candidates:
        if all((candidate / split).is_dir() for split in VALID_SPLITS):
            return candidate
    raise FileNotFoundError("未找到包含 train/val/test 的 annotations 根目录")


def _build_image_index(data_root: Path, class_name: str) -> dict[str, Path]:
    """为一个类别建立 UUID 到图片路径的索引。"""

    class_root = data_root / "dataset" / class_name
    if not class_root.is_dir():
        raise FileNotFoundError(f"图片目录不存在：{class_root}")
    index: dict[str, Path] = {}
    duplicates: list[str] = []
    for path in sorted(class_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        stem = path.stem
        if stem in index:
            duplicates.append(stem)
        else:
            index[stem] = path
    if duplicates:
        raise ValueError(f"类别 {class_name} 存在重复图片 stem：{duplicates[:3]}")
    return index


def _iter_annotation_records(path: Path) -> Iterator[tuple[str, dict[str, Any]]]:
    """逐个返回一个官方 JSON 文件中的记录。"""

    with path.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise ValueError(f"标注文件顶层不是对象：{path}")
    for image_id, record in payload.items():
        if not isinstance(image_id, str) or not isinstance(record, dict):
            raise ValueError(f"标注记录格式异常：{path} / {image_id!r}")
        yield image_id, record


def _format_bbox(bbox: Any) -> str:
    """把归一化 COCO 左上角框转换为归一化 YOLO 中心框。"""

    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        raise ValueError(f"bbox 不是四元数组：{bbox!r}")
    left, top, box_width, box_height = (float(value) for value in bbox)
    if any(value < 0.0 or value > 1.0 for value in (left, top, box_width, box_height)):
        raise ValueError(f"bbox 超出 [0,1]：{bbox!r}")
    if box_width <= 0.0 or box_height <= 0.0:
        raise ValueError(f"bbox 宽高必须为正：{bbox!r}")
    if left + box_width > 1.0 or top + box_height > 1.0:
        raise ValueError(f"COCO bbox 右下角超出 [0,1]：{bbox!r}")
    center_x = left + box_width / 2.0
    center_y = top + box_height / 2.0
    return " ".join(f"{value:.8f}" for value in (center_x, center_y, box_width, box_height))


def prepare_dataset(data_root: Path, manifest_path: Path, labels_root: Path) -> dict[str, Any]:
    """按类别/划分转换标注，成功后原子发布清单。"""

    data_root = data_root.resolve()
    manifest_path = manifest_path.resolve()
    labels_root = labels_root.resolve()
    annotation_root = _find_annotation_root(data_root)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    labels_root.mkdir(parents=True, exist_ok=True)

    started_at = _now_iso()
    image_indexes = {
        class_name: _build_image_index(data_root, class_name)
        for class_name in (*CLASS_NAMES, "no_gesture")
    }
    partial_manifest = manifest_path.with_name(manifest_path.name + ".partial")
    counts: Counter[str] = Counter()
    split_counts: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    split_class_counts: Counter[str] = Counter()
    json_files: list[str] = []
    missing_images: list[str] = []
    unexpected_labels: list[str] = []
    malformed_records: list[str] = []
    ignored_label_counts: Counter[str] = Counter()
    referenced_ids: dict[str, set[str]] = defaultdict(set)
    rows_written = 0

    try:
        with partial_manifest.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=MANIFEST_COLUMNS)
            writer.writeheader()
            for split in VALID_SPLITS:
                for class_name in (*CLASS_NAMES, "no_gesture"):
                    annotation_path = annotation_root / split / f"{class_name}.json"
                    if not annotation_path.is_file():
                        raise FileNotFoundError(f"缺少目标标注文件：{annotation_path}")
                    json_files.append(_relative(annotation_path, data_root))
                    for image_id, record in _iter_annotation_records(annotation_path):
                        image_path = image_indexes[class_name].get(image_id)
                        if image_path is None:
                            missing_images.append(f"{split}/{class_name}/{image_id}")
                            continue
                        referenced_ids[class_name].add(image_id)

                        label_lines: list[str] = []
                        if class_name != "no_gesture":
                            bboxes = record.get("bboxes")
                            labels = record.get("labels")
                            if not isinstance(bboxes, list) or not isinstance(labels, list):
                                malformed_records.append(f"{annotation_path}:{image_id}:缺少 bboxes/labels")
                                continue
                            if len(bboxes) != len(labels):
                                malformed_records.append(f"{annotation_path}:{image_id}:框与标签数量不一致")
                                continue
                            for bbox, label in zip(bboxes, labels):
                                if label in IGNORED_LABELS:
                                    ignored_label_counts[str(label)] += 1
                                    continue
                                if label not in CLASS_TO_ID:
                                    unexpected_labels.append(f"{annotation_path}:{image_id}:{label!r}")
                                    continue
                                label_lines.append(f"{CLASS_TO_ID[label]} {_format_bbox(bbox)}")

                        label_path = labels_root / split / class_name / f"{image_id}.txt"
                        label_path.parent.mkdir(parents=True, exist_ok=True)
                        label_path.write_text(
                            ("\n".join(label_lines) + "\n") if label_lines else "",
                            encoding="utf-8",
                        )
                        row = {
                            "image": _relative(image_path, data_root),
                            "label": _relative(label_path, data_root),
                            "split": split,
                            # HaGRIDv2 按 user_id 划分；此字段是分区键，不代表物理采集会话。
                            "session_id": f"hagridv2_official_split_{split}",
                            "person_id": str(record.get("user_id", "")),
                            "source": SOURCE,
                            "license": LICENSE,
                            "is_real": "true",
                        }
                        if not row["person_id"]:
                            malformed_records.append(f"{annotation_path}:{image_id}:缺少 user_id")
                            continue
                        writer.writerow(row)
                        rows_written += 1
                        counts["images"] += 1
                        counts["boxes"] += len(label_lines)
                        split_counts[split] += 1
                        class_counts[class_name] += 1
                        split_class_counts[f"{split}/{class_name}"] += 1
        if missing_images or unexpected_labels or malformed_records:
            details = {
                "missing_images": f"{len(missing_images)}; first={missing_images[:3]}",
                "unexpected_labels": f"{len(unexpected_labels)}; first={unexpected_labels[:3]}",
                "malformed_records": f"{len(malformed_records)}; first={malformed_records[:3]}",
            }
            raise ValueError(f"数据转换发现异常，未发布最终清单：{details}")
        os.replace(partial_manifest, manifest_path)
    except Exception:
        if partial_manifest.exists():
            # 失败产物只用于诊断，允许覆盖上一次同名的失败临时文件。
            os.replace(partial_manifest, partial_manifest.with_suffix(partial_manifest.suffix + ".failed"))
        raise

    digest = hashlib.sha256()
    with manifest_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    report = {
        "status": "PASS",
        "started_at": started_at,
        "finished_at": _now_iso(),
        "data_root": str(data_root),
        "annotation_root": str(annotation_root),
        "manifest": str(manifest_path),
        "labels_root": str(labels_root),
        "manifest_sha256": digest.hexdigest(),
        "manifest_columns": list(MANIFEST_COLUMNS),
        "classes": {str(index): name for name, index in CLASS_TO_ID.items()},
        "source_urls": SOURCE_URLS,
        "bbox_conversion": {
            "source": "HaGRIDv2 normalized COCO [left, top, width, height]",
            "output": "normalized YOLO [center_x, center_y, width, height]",
        },
        "license_pdf": {
            "path": str(data_root / "license" / "en_us.pdf"),
            "sha256": "14f4845e9c8d3de875cbac4139491da368ab1040a7f565e02894477279134d22",
            "title": LICENSE.split(";", 1)[0],
        },
        "session_policy": (
            "HaGRIDv2 官方划分依据 user_id；manifest.session_id 使用官方 split 分区键，"
            "不宣称物理采集 session。AC03 的物理会话语义需审查确认。"
        ),
        "is_real_policy": "HaGRIDv2 原始照片记为 true；未使用合成图片。",
        "metrics": {
            "rows": rows_written,
            "images": counts["images"],
            "boxes": counts["boxes"],
            "image_files_indexed": {name: len(index) for name, index in image_indexes.items()},
            "unreferenced_image_counts": {
                name: len(set(index) - referenced_ids[name]) for name, index in image_indexes.items()
            },
            "unreferenced_image_examples": {
                name: sorted(set(index) - referenced_ids[name])[:20]
                for name, index in image_indexes.items()
                if set(index) - referenced_ids[name]
            },
            "by_split": dict(split_counts),
            "by_class": dict(class_counts),
            "by_split_class": dict(split_class_counts),
            "json_files": len(json_files),
            "ignored_label_counts": dict(ignored_label_counts),
        },
        "errors": {
            "missing_images": missing_images,
            "unexpected_labels": unexpected_labels,
            "malformed_records": malformed_records,
        },
        "source_archive_sha256": "未在删除压缩包前采集；仅保留 ZIP CRC、条目数与解压后尺寸证据。",
    }
    return report


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True, help="HaGRIDv2 外部数据根目录")
    parser.add_argument("--manifest", type=Path, required=True, help="输出 UTF-8 CSV 清单")
    parser.add_argument("--labels-root", type=Path, default=None, help="输出 YOLO 标签根目录")
    parser.add_argument("--report", type=Path, required=True, help="输出 JSON 证据报告")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """执行转换并返回进程退出码。"""

    args = _parse_args(argv)
    labels_root = args.labels_root or args.data_root / "labels"
    try:
        report = prepare_dataset(args.data_root, args.manifest, labels_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "metrics": report["metrics"], "manifest_sha256": report["manifest_sha256"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
