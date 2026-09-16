"""生成 S1-T02-D2 固定的 512 张训练校准集清单和机器报告。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


UTC8 = timezone(timedelta(hours=8))
CLASS_IDS = tuple(range(5))
CLASS_NAMES = ("fist", "palm", "one", "two_up", "three")
REQUIRED_COLUMNS = {"image", "label", "split", "session_id", "person_id"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def now_utc8() -> str:
    return datetime.now(UTC8).isoformat(timespec="seconds")


def canonical_path(data_root: Path, value: str) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = data_root / candidate
    return candidate.resolve(strict=True)


def parse_label(path: Path) -> list[int]:
    classes = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fields = line.split()
        if len(fields) != 5:
            raise ValueError(f"标签格式错误: {path}:{line_number}")
        class_id = int(fields[0])
        if class_id not in CLASS_IDS:
            raise ValueError(f"标签类别越界: {path}:{line_number}")
        for value in fields[1:]:
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"标签坐标不在 [0,1]: {path}:{line_number}")
        classes.append(class_id)
    return classes


def read_semantic(path: Path, data_root: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result = {}
    for row in rows:
        if not row.get("image"):
            raise ValueError("语义表存在空 image")
        key = os.path.normcase(str(canonical_path(data_root, row["image"])))
        result[key] = row
    return result


def validate_semantic_negative_counts(no_hand_keys: list[str], non_target_keys: list[str]) -> None:
    """强制校准集使用 3 张 train no_hand 和 5 张 train non-target。"""
    if len(no_hand_keys) != 3:
        raise ValueError(f"批准 train no_hand 数量不是 3: {len(no_hand_keys)}")
    if len(non_target_keys) != 5:
        raise ValueError(f"批准 train non_target_gesture 数量不是 5: {len(non_target_keys)}")


def select_calibration(
    data_root: Path, manifest_path: Path, train_list_path: Path, semantic_path: Path
) -> dict[str, object]:
    """按 train.list 顺序固定五类各 100 张和 12 张训练负样本。"""
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not REQUIRED_COLUMNS.issubset(reader.fieldnames or set()):
            raise ValueError("manifest 缺少校准选择所需列")
        manifest = {}
        for row in reader:
            image = Path(row["image"])
            if not image.is_absolute():
                image = data_root / image
            key = os.path.normcase(str(image.absolute()))
            if key in manifest:
                raise ValueError(f"manifest image 重复: {image}")
            manifest[key] = {**row}

    semantic = read_semantic(semantic_path, data_root)
    train_paths = []
    seen = set()
    train_lines = train_list_path.read_text(encoding="utf-8").splitlines()
    for line_number, line in enumerate(train_lines, 1):
        value = line.strip()
        if not value:
            raise ValueError(f"train.list 第 {line_number} 行为空")
        image = Path(value)
        if not image.is_absolute():
            image = data_root / image
        key = os.path.normcase(str(image.absolute()))
        if key in seen:
            raise ValueError(f"train.list 存在重复路径: {image}")
        seen.add(key)
        if key not in manifest:
            raise ValueError(f"train.list 路径不在 manifest: {image}")
        if manifest[key]["split"] != "train":
            raise ValueError(f"train.list 包含非 train 行: {image}")
        train_paths.append(key)

    def make_record(key: str, classes: list[int] | None = None) -> dict[str, object]:
        row = manifest[key]
        image_path = canonical_path(data_root, row["image"])
        label_path = canonical_path(data_root, row["label"])
        classes = parse_label(label_path) if classes is None else classes
        record = {
            "image": str(image_path),
            "manifest_image": row["image"],
            "label": str(label_path),
            "manifest_label": row["label"],
            "split": row["split"],
            "session_id": row["session_id"],
            "person_id": row["person_id"],
            "label_classes": classes,
        }
        semantic_row = semantic.get(key)
        if semantic_row:
            record["semantic_role"] = semantic_row.get("sample_role", "")
        return record

    # 只解析到配额已满；清单和 manifest 仍完整读取并独立哈希。
    class_counts = {class_id: 0 for class_id in CLASS_IDS}
    positive_keys = set()
    positive_records: list[dict[str, object]] = []
    empty_candidates: list[dict[str, object]] = []
    for key in train_paths:
        if all(count == 100 for count in class_counts.values()) and len(empty_candidates) >= 4:
            break
        row = manifest[key]
        image_parts = Path(row["image"]).parts
        candidate_class = next((class_id for class_id, name in enumerate(CLASS_NAMES) if name in image_parts), None)
        label_candidate = Path(row["label"])
        if not label_candidate.is_absolute():
            label_candidate = data_root / label_candidate
        if label_candidate.stat().st_size == 0:
            if key not in semantic and len(empty_candidates) < 4:
                empty_candidates.append(make_record(key, []))
            continue
        if key in positive_keys:
            continue
        if candidate_class is None or class_counts[candidate_class] >= 100:
            continue
        class_id = candidate_class
        record = make_record(key, [class_id])
        positive_keys.add(key)
        class_counts[class_id] += 1
        positive_records.append({**record, "selection_role": f"class_{class_id}"})

    if any(count != 100 for count in class_counts.values()):
        raise ValueError(f"训练正样本配额不足: {class_counts}")
    if len(positive_records) != 500:
        raise ValueError(f"五类校准图片不是 500 张: {len(positive_records)}")

    order = {key: index for index, key in enumerate(train_paths)}
    no_hand_keys = [key for key in train_paths if semantic.get(key, {}).get("sample_role") == "no_hand"]
    non_target_keys = [key for key in train_paths if semantic.get(key, {}).get("sample_role") == "non_target_gesture"]
    validate_semantic_negative_counts(no_hand_keys, non_target_keys)
    no_hand_rows = [make_record(key, []) for key in no_hand_keys]
    non_target_rows = [make_record(key, []) for key in non_target_keys]
    chosen_negative = [
        {**record, "selection_role": "approved_no_hand"} for record in no_hand_rows
    ] + [
        {**record, "selection_role": "approved_non_target"} for record in non_target_rows
    ]
    selected_keys = positive_keys | {os.path.normcase(item["image"]) for item in chosen_negative}
    for record in empty_candidates:
        key = os.path.normcase(record["image"])
        if len(chosen_negative) >= 12:
            break
        if key not in selected_keys:
            chosen_negative.append({**record, "selection_role": "unreviewed_empty_label_train"})
            selected_keys.add(key)
    chosen = positive_records + chosen_negative
    if len(chosen_negative) != 12:
        raise ValueError(f"训练负样本无法固定为 12: {len(chosen_negative)}")

    # 最终选择的每张图仍独立解析标签，防止目录候选或语义表替代真实标签。
    for record in chosen:
        actual_classes = parse_label(Path(record["label"]))
        if record["selection_role"].startswith("class_"):
            expected_class = int(record["selection_role"].split("_")[-1])
            if expected_class not in actual_classes:
                raise ValueError(f"选定图片标签与类别目录不一致: {record['image']}")
        elif actual_classes:
            raise ValueError(f"负样本标签非空: {record['image']}")
        record["label_classes"] = actual_classes

    chosen_keys = [os.path.normcase(item["image"]) for item in chosen]
    if len(chosen_keys) != len(set(chosen_keys)):
        raise ValueError("校准集存在重复图片")
    for record in chosen:
        record["image_sha256"] = sha256_file(Path(record["image"]))
    return {
        "records": chosen,
        "counts": {"total": len(chosen), "per_class": {str(k): 100 for k in CLASS_IDS}, "negative": 12, "train_no_hand": 3},
        "selection_rule": {
            "ordering": "按原始 train.list 首次出现顺序",
            "positive": "每个五类各选前 100 张包含该 class 的 train 图片；同图多类只计入一次最终图片",
            "negative": "3 张批准 train no_hand + 5 张批准 train non_target_gesture + 4 张其余 train 空标签",
            "no_hand_semantics": "只接受语义表 sample_role=no_hand，不把 no_gesture 或其他空标签改写为 no_hand",
        },
        "source": {
            "data_root": str(data_root),
            "manifest": str(manifest_path),
            "manifest_sha256": sha256_file(manifest_path),
            "train_list": str(train_list_path),
            "train_list_sha256": sha256_file(train_list_path),
            "train_list_count": len(train_paths),
            "semantic_review": str(semantic_path),
            "semantic_review_sha256": sha256_file(semantic_path),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 S1-T02-D2 固定训练校准集")
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--train-list", type=Path, required=True)
    parser.add_argument("--semantic-review", type=Path, required=True)
    parser.add_argument("--output-list", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    started = now_utc8()
    try:
        selection = select_calibration(args.data_root.resolve(), args.manifest.resolve(), args.train_list.resolve(), args.semantic_review.resolve())
        lines = [str(item["image"]).replace("\\", "/") for item in selection["records"]]
        args.output_list.parent.mkdir(parents=True, exist_ok=True)
        args.output_list.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        report = {
            "schema_version": "s1_t02_d2_calibration_v1",
            "status": "BOUND_TRAIN_ONLY",
            "started_utc8": started,
            "finished_utc8": now_utc8(),
            "argv": [str(value) for value in sys.argv],
            "cwd": str(Path.cwd()),
            "network_access": False,
            "training": False,
            "formal_evaluation": False,
            "output_list": str(args.output_list.resolve()),
            "output_list_sha256": sha256_file(args.output_list),
            "output_list_count": len(lines),
            **selection,
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({"count": len(lines), "list": str(args.output_list), "report": str(args.report)}, ensure_ascii=False))
        return 0
    except Exception as error:
        print(f"校准集生成失败: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
