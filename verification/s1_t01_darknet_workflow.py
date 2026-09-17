#!/usr/bin/env python3
"""S1-T01 官方 Darknet 训练、恢复和逐验证图评估入口。"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import struct
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


EXPECTED_CLASSES = ["fist", "palm", "one", "two_up", "three"]
MIN_TRAIN_UPDATES = 10
MIN_RESUME_UPDATES = 1
MAX_SHORT_BATCHES = 100
FORMAL_TRAINING_MAX_BATCHES = 6000
FORMAL_TRAINING_STEPS = (4800, 5400)
MAX_DARKNET_PATH_BYTES = 256
REPORT_SCHEMA_VERSION = 1
D6_CAPTURE_THRESHOLD = 0.249999
D6_SCORE_THRESHOLD_RANGE = (0.25, 0.50)
DARKNET_SEED_ENV = "GESTUREFORGE_DARKNET_SEED"
MAX_DARKNET_SEED = 0xFFFFFFFF
REQUIRED_MANIFEST_FIELDS = {
    "image",
    "label",
    "split",
    "session_id",
    "person_id",
    "source",
    "license",
    "is_real",
}
REQUIRED_DATA_KEYS = {"train", "valid", "backup", "saveweights", "savelast"}
BAD_NUMERIC_RE = re.compile(r"(?i)(?<![a-z])(?:nan|inf(?:inity)?)(?![a-z])")
STOP_RE = re.compile(
    r"(?i)(?:out\s+of\s+memory|cuda[^\n]*alloc[^\n]*fail|cudnn_status_alloc_failed|"
    r"error\s+opening\s+(?:image|label)|cannot\s+open\s+(?:image|label)|"
    r"cannot\s+load\s+image|can['’]t\s+open\s+label(?:\s+file)?|"
    r"couldn['’]t\s+open\s+file|file\s+not\s+found|corrupt\s+(?:image|label))"
)
STEP_RE = re.compile(r"^\s*(\d+):\s+", re.MULTILINE)


def _now_iso() -> str:
    """返回东八区当前时间。"""

    return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec="seconds")


def _sha256(path: Path) -> str:
    """按字节计算文件 SHA-256。"""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_darknet_seed(value: str) -> int:
    """解析仅供 Darknet 子进程使用的非负 32 位十进制种子。"""

    if re.fullmatch(r"[0-9]+", value or "") is None:
        raise argparse.ArgumentTypeError("--darknet-seed 必须是非负 32 位十进制整数")
    parsed = int(value, 10)
    if parsed > MAX_DARKNET_SEED:
        raise argparse.ArgumentTypeError("--darknet-seed 超出非负 32 位整数范围")
    return parsed


def _seed_binding(seed: int | None) -> dict[str, Any]:
    """返回种子环境变量的可审计绑定，不修改当前 Python 进程环境。"""

    return {
        "environment_variable": DARKNET_SEED_ENV,
        "value": seed,
        "passed_to_child_process": seed is not None,
        "parent_process_unchanged": True,
    }


def _child_environment(seed: int | None) -> dict[str, str]:
    """复制父环境，并仅为有显式种子的子进程覆盖种子变量。"""

    environment = os.environ.copy()
    if seed is not None:
        environment[DARKNET_SEED_ENV] = str(seed)
    return environment


def _read_json(path: Path) -> dict[str, Any]:
    """读取 UTF-8 JSON 对象。"""

    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"JSON 顶层必须是对象: {path}")
    return value


def _is_windows_pe(path: Path) -> bool:
    """检查文件是否具有可执行的基本 Windows PE 结构。"""

    try:
        with path.open("rb") as stream:
            header = stream.read(64)
            if len(header) < 64 or header[:2] != b"MZ":
                return False
            pe_offset = struct.unpack_from("<I", header, 0x3C)[0]
            stream.seek(0, 2)
            file_size = stream.tell()
            if pe_offset < 64 or pe_offset + 4 + 20 > file_size:
                return False
            stream.seek(pe_offset)
            if stream.read(4) != b"PE\0\0":
                return False
            coff = stream.read(20)
            if len(coff) != 20:
                return False
            machine, sections, _, _, _, optional_size, characteristics = struct.unpack("<HHIIIHH", coff)
            if machine not in {0x014C, 0x8664, 0xAA64} or not 1 <= sections <= 96:
                return False
            if optional_size < 2 or optional_size > 4096:
                return False
            optional = stream.read(optional_size)
            if len(optional) != optional_size or struct.unpack_from("<H", optional, 0)[0] not in {0x010B, 0x020B}:
                return False
            if not characteristics & 0x0002:
                return False
            table_end = pe_offset + 4 + 20 + optional_size + sections * 40
            return table_end <= file_size
    except (OSError, struct.error):
        return False


def _same_path(left: Path, right: Path) -> bool:
    """比较两个路径的规范绝对路径。"""

    return os.path.normcase(str(left.resolve())) == os.path.normcase(str(right.resolve()))


def _canonical_path(path: Path) -> str:
    """返回路径的规范键，尽量在目标不存在时也保持稳定。"""

    try:
        return os.path.normcase(str(path.resolve()))
    except (OSError, RuntimeError):
        return os.path.normcase(str(path.absolute()))


def _safe_sha256(path: Path) -> str:
    """返回文件摘要；文件不可用时明确记录 unavailable。"""

    if not path.is_file():
        return "unavailable"
    try:
        return _sha256(path)
    except OSError:
        return "unavailable"


def _resolve_working_path(value: str, working_directory: Path) -> Path:
    """按 Darknet 工作目录解析 data 配置中的相对路径。"""

    path = Path(value)
    if not path.is_absolute():
        path = working_directory / path
    return path.resolve()


def _darknet_cli_path(path: Path) -> str:
    """将 Windows 路径转换为 Darknet JSON 可安全记录的命令参数。"""

    value = str(path)
    return value.replace("\\", "/") if os.name == "nt" else value


def _darknet_path_size(path: Path) -> int:
    """按 UTF-8 字节数计算 Darknet 路径及结尾空字符的长度。"""

    return len(str(path).encode("utf-8")) + 1


def _validate_darknet_path_lengths(
    args: argparse.Namespace,
    context: dict[str, Any],
    errors: list[str],
) -> None:
    """拒绝可能超过官方 256 字节路径缓冲区的路径，不截断任何输入。"""

    candidates: list[tuple[str, Path]] = []

    def add(label: str, value: Any) -> None:
        if isinstance(value, Path):
            candidates.append((label, value))
        elif isinstance(value, str) and value:
            candidates.append((label, Path(value)))

    add("Darknet 可执行文件", context.get("executable"))
    add("Darknet 工作目录", context.get("working_directory"))
    for command_index, command in enumerate(_commands_for_action(args, context), start=1):
        for argument_index, argument in enumerate(command):
            if argument_index in {0, 1, 2, 3, 4, 5, 6} or argument in {"-out"}:
                add(f"Darknet 命令 {command_index} 参数 {argument_index}", argument)
        for argument_index, argument in enumerate(command):
            if argument == "-out" and argument_index + 1 < len(command):
                add(f"Darknet 命令 {command_index} 输出路径", command[argument_index + 1])
    add("data 配置", args.data_config.resolve())
    add("model 配置", args.model_config.resolve())
    add("names 文件", args.names_file.resolve())
    if args.action == "train":
        add("初始权重", args.initial_weights.resolve())
    elif args.action == "resume":
        add("resume 输入检查点", args.checkpoint.resolve())
    else:
        add("评估 valid 清单", args.valid_list.resolve())
        add("zero-prediction-image", args.zero_prediction_image.resolve())
    if args.action in {"train", "resume"}:
        add("checkpoint-output", context.get("checkpoint_output"))
        checkpoint_plan = context.get("checkpoint_plan", {})
        for index, candidate in enumerate(checkpoint_plan.get("candidates", []), start=1):
            add(f"checkpoint 候选 {index}", candidate)
    for index, image in enumerate(context.get("valid_images", []), start=1):
        add(f"valid 图片 {index}", image)

    seen: set[tuple[str, str]] = set()
    for label, path in candidates:
        key = (label, _canonical_path(path))
        if key in seen:
            continue
        seen.add(key)
        size = _darknet_path_size(path)
        if size >= MAX_DARKNET_PATH_BYTES:
            errors.append(
                f"{label} UTF-8 路径含终止符长度 {size} >= {MAX_DARKNET_PATH_BYTES}，"
                "超过官方 Darknet 固定 256 字节缓冲区；不会截断路径"
            )


def _parse_key_values_text(text: str) -> dict[str, str]:
    """解析 Darknet data 配置文本中的键值。"""
    values: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip().casefold()] = value.strip()
    return values


def _parse_key_values(path: Path) -> dict[str, str]:
    """读取并解析 Darknet data 配置中的键值。"""

    return _parse_key_values_text(path.read_text(encoding="utf-8-sig"))


def _read_stable_bytes(path: Path) -> tuple[bytes, os.stat_result]:
    """读取文件并拒绝读取期间大小或文件版本发生变化的快照。"""

    before = path.stat()
    raw = path.read_bytes()
    after = path.stat()
    before_identity = (before.st_size, before.st_mtime_ns, before.st_dev, before.st_ino)
    after_identity = (after.st_size, after.st_mtime_ns, after.st_dev, after.st_ino)
    if before_identity != after_identity or len(raw) != after.st_size:
        raise OSError(f"读取期间文件发生变化: {path}")
    return raw, after


def _capture_training_list(
    path: Path,
    split: str,
    working_directory: Path,
    manifest_images: dict[str, dict[str, dict[str, Any]]],
) -> tuple[dict[str, Any], list[str]]:
    """对训练清单同一份字节计算哈希、行数并核对 manifest 划分。"""

    errors: list[str] = []
    canonical_path = _canonical_path(path)
    record: dict[str, Any] = {
        "path": canonical_path,
        "sha256": "unavailable",
        "size_bytes": None,
        "line_count": None,
        "sample_count": None,
        "capture_status": "FAILED",
    }
    try:
        raw, _ = _read_stable_bytes(path)
        text = raw.decode("utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"{split} 清单缺失、不可读或读取期间发生变化: {canonical_path}: {exc}")
        return record, errors

    lines = text.splitlines()
    record.update(
        {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "size_bytes": len(raw),
            "line_count": len(lines),
        }
    )
    expected = manifest_images.get(split, {})
    expected_keys = set(expected)
    observed_keys: set[str] = set()
    sample_count = 0
    for line_number, raw_line in enumerate(lines, start=1):
        value = raw_line.strip()
        if not value or value.startswith("#"):
            continue
        sample_count += 1
        image = Path(value)
        if not image.is_absolute():
            image = working_directory / image
        try:
            resolved = image.resolve()
        except (OSError, RuntimeError) as exc:
            errors.append(f"{split} 清单第 {line_number} 行路径无法规范化: {value}: {exc}")
            continue
        key = _canonical_path(resolved)
        if key in observed_keys:
            errors.append(f"{split} 清单存在重复图片: {value}")
        observed_keys.add(key)
        if key not in expected_keys:
            errors.append(f"{split} 清单图片不在 manifest {split} 集合: {value}")
        elif not resolved.is_file():
            errors.append(f"{split} 清单图片不存在: {resolved}")
    record["sample_count"] = sample_count
    if observed_keys != expected_keys:
        errors.append(
            f"{split} 清单与 manifest 集合不一致: list={len(observed_keys)}, manifest={len(expected_keys)}"
        )
    record["capture_status"] = "CAPTURED" if not errors else "FAILED"
    return record, errors


def _capture_training_input_snapshot(
    args: argparse.Namespace,
    working_directory: Path,
    capture_point: str,
) -> tuple[
    dict[str, Any],
    dict[str, dict[str, dict[str, Any]]],
    dict[str, str],
]:
    """记录 train/resume 的 .data、manifest 和两份实际清单输入快照。"""

    errors: list[str] = []
    data_path = args.data_config.resolve()
    manifest_path = args.manifest.resolve()
    manifest_images: dict[str, dict[str, dict[str, Any]]] = {}
    data_values: dict[str, str] = {}
    data_record: dict[str, Any] = {
        "path": _canonical_path(data_path),
        "sha256": "unavailable",
        "size_bytes": None,
        "train_list_path": "unavailable",
        "valid_list_path": "unavailable",
        "values": data_values,
        "capture_status": "FAILED",
    }
    try:
        data_bytes, _ = _read_stable_bytes(data_path)
        data_text = data_bytes.decode("utf-8-sig")
        data_values = _parse_key_values_text(data_text)
        data_record.update(
            {
                "sha256": hashlib.sha256(data_bytes).hexdigest(),
                "size_bytes": len(data_bytes),
                "values": data_values,
                "capture_status": "CAPTURED",
            }
        )
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"Darknet .data 缺失、不可读或读取期间发生变化: {data_path}: {exc}")

    list_paths: dict[str, Path | None] = {"train": None, "valid": None}
    for key in ("train", "valid"):
        configured = data_values.get(key)
        if not configured:
            errors.append(f"Darknet .data 未提供可解析的 {key} 清单路径")
            continue
        try:
            resolved = _resolve_working_path(configured, working_directory)
        except (OSError, RuntimeError) as exc:
            errors.append(f"Darknet .data 的 {key} 清单路径无法规范化: {configured}: {exc}")
            continue
        list_paths[key] = resolved
        data_record[f"{key}_list_path"] = _canonical_path(resolved)

    try:
        manifest_bytes, _ = _read_stable_bytes(manifest_path)
        manifest_parse_errors: list[str] = []
        manifest_images = _load_manifest_images_from_bytes(
            manifest_bytes,
            manifest_path,
            args.data_root.resolve(),
            manifest_parse_errors,
        )
        errors.extend(manifest_parse_errors)
        manifest_counts = {
            split: len(manifest_images.get(split, {})) for split in ("train", "val", "test")
        }
        manifest_record: dict[str, Any] = {
            "path": _canonical_path(manifest_path),
            "sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "size_bytes": len(manifest_bytes),
            "sample_counts": manifest_counts,
            "capture_status": "CAPTURED",
        }
        if manifest_parse_errors:
            manifest_record["capture_status"] = "FAILED"
    except OSError as exc:
        errors.append(f"manifest 缺失、不可读或读取期间发生变化: {manifest_path}: {exc}")
        manifest_record = {
            "path": _canonical_path(manifest_path),
            "sha256": "unavailable",
            "size_bytes": None,
            "sample_counts": {"train": 0, "val": 0, "test": 0},
            "capture_status": "FAILED",
        }
    except (UnicodeDecodeError, csv.Error) as exc:
        errors.append(f"manifest 字节无法解析: {manifest_path}: {exc}")
        manifest_record = {
            "path": _canonical_path(manifest_path),
            "sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "size_bytes": len(manifest_bytes),
            "sample_counts": {"train": 0, "val": 0, "test": 0},
            "capture_status": "FAILED",
        }

    lists: dict[str, dict[str, Any]] = {}
    for key, split in (("train", "train"), ("valid", "val")):
        path = list_paths[key]
        if path is None:
            lists[key] = {
                "path": "unavailable",
                "sha256": "unavailable",
                "size_bytes": None,
                "line_count": None,
                "sample_count": None,
                "capture_status": "FAILED",
            }
            continue
        lists[key], list_errors = _capture_training_list(path, split, working_directory, manifest_images)
        errors.extend(list_errors)

    if data_record["capture_status"] != "CAPTURED":
        errors.append("Darknet .data 快照未通过")
    if manifest_record["capture_status"] != "CAPTURED":
        errors.append("manifest 快照未通过")
    status = "CAPTURED" if not errors else "FAILED"
    snapshot = {
        "capture_point": capture_point,
        "captured_at_utc8": _now_iso(),
        "status": status,
        "data_config": data_record,
        "manifest": manifest_record,
        "lists": lists,
        "errors": errors,
    }
    return snapshot, manifest_images, data_values


def _training_snapshot_differences(before: dict[str, Any], current: dict[str, Any]) -> list[str]:
    """逐字段比较训练输入身份，忽略不同采集时点的时间戳。"""

    differences: list[str] = []
    if current.get("status") != "CAPTURED":
        differences.append(f"当前快照状态为 {current.get('status', 'unavailable')}")
        differences.extend(current.get("errors", []))
    for section, fields in (
        ("data_config", ("path", "sha256", "size_bytes", "values", "train_list_path", "valid_list_path")),
        ("manifest", ("path", "sha256", "size_bytes", "sample_counts")),
    ):
        expected = before.get(section, {})
        observed = current.get(section, {})
        for field in fields:
            if expected.get(field) != observed.get(field):
                differences.append(f"{section}.{field} 已变化")
    for key in ("train", "valid"):
        expected = before.get("lists", {}).get(key, {})
        observed = current.get("lists", {}).get(key, {})
        for field in ("path", "sha256", "size_bytes", "line_count", "sample_count", "capture_status"):
            if expected.get(field) != observed.get(field):
                differences.append(f"lists.{key}.{field} 已变化")
    return differences


def _parse_cfg_sections(path: Path) -> list[dict[str, str]]:
    """读取 Darknet cfg 的简单 section 键值。"""

    sections: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = {"__section__": line[1:-1].strip().casefold()}
            sections.append(current)
            continue
        if current is not None and "=" in line:
            key, value = line.split("=", 1)
            current[key.strip().casefold()] = value.strip()
    return sections


def _cfg_int(section: dict[str, str], key: str) -> int | None:
    """读取 section 中的整数值。"""

    try:
        return int(section[key])
    except (KeyError, TypeError, ValueError):
        return None


def _validate_model_config(
    path: Path,
    errors: list[str],
    require_short_batches: bool = True,
    formal_training: bool = False,
) -> dict[str, Any]:
    """校验五类模型，并对诊断短训或正式训练应用各自固定的 schedule。"""

    if not path.is_file():
        errors.append(f"模型 cfg 不存在: {path}")
        return {}
    try:
        sections = _parse_cfg_sections(path)
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"模型 cfg 不可读取: {exc}")
        return {}
    net = next((section for section in sections if section.get("__section__") == "net"), None)
    if net is None:
        errors.append("模型 cfg 缺少 [net] section")
        return {}
    max_batches = _cfg_int(net, "max_batches")
    width = _cfg_int(net, "width")
    height = _cfg_int(net, "height")
    if max_batches is None:
        errors.append("模型 cfg 的 [net] 缺少有效 max_batches")
    elif require_short_batches and formal_training and max_batches != FORMAL_TRAINING_MAX_BATCHES:
        errors.append(
            f"正式训练 cfg max_batches 必须恰好为 {FORMAL_TRAINING_MAX_BATCHES}，实际为 {max_batches}"
        )
    elif require_short_batches and not formal_training and not (
        MIN_TRAIN_UPDATES + MIN_RESUME_UPDATES <= max_batches <= MAX_SHORT_BATCHES
    ):
        errors.append(
            f"模型 cfg max_batches={max_batches} 不在短训安全范围 "
            f"[{MIN_TRAIN_UPDATES + MIN_RESUME_UPDATES}, {MAX_SHORT_BATCHES}]"
        )
    steps_value = net.get("steps")
    steps: tuple[int, ...] | None = None
    if steps_value is not None:
        try:
            steps = tuple(int(value.strip()) for value in steps_value.split(","))
        except ValueError:
            steps = None
    if require_short_batches and formal_training and steps != FORMAL_TRAINING_STEPS:
        errors.append(
            "正式训练 cfg steps 必须为 4800,5400，"
            f"实际为 {steps_value!r}"
        )
    if width is None or height is None or width <= 0 or height <= 0:
        errors.append("模型 cfg 的 width/height 必须为正整数")
    yolo_sections = [section for section in sections if section.get("__section__") == "yolo"]
    if not yolo_sections:
        errors.append("模型 cfg 缺少 [yolo] 检测头")
    class_values = [_cfg_int(section, "classes") for section in yolo_sections]
    if any(value != len(EXPECTED_CLASSES) for value in class_values):
        errors.append(f"每个 [yolo] 检测头必须 classes={len(EXPECTED_CLASSES)}")
    expected_filters = 3 * (len(EXPECTED_CLASSES) + 5)
    head_details: list[dict[str, Any]] = []
    for head_number, section in enumerate(yolo_sections, start=1):
        section_index = next(index for index, candidate in enumerate(sections) if candidate is section)
        previous = sections[section_index - 1] if section_index else None
        if previous is None or previous.get("__section__") != "convolutional":
            errors.append(f"第 {head_number} 个 [yolo] 缺少紧邻的前置 [convolutional] section")
            head_details.append({"head": head_number, "filters": None, "expected_filters": expected_filters})
            continue
        filters = _cfg_int(previous, "filters")
        if filters != expected_filters:
            errors.append(
                f"第 {head_number} 个 [yolo] 的前置卷积 filters={filters!r}，必须为 {expected_filters}"
            )
        head_details.append({"head": head_number, "filters": filters, "expected_filters": expected_filters})
    return {
        "max_batches": max_batches,
        "steps": list(steps) if steps is not None else None,
        "width": width,
        "height": height,
        "yolo_heads": len(yolo_sections),
        "yolo_head_details": head_details,
    }


def _validate_names_file(path: Path, errors: list[str]) -> None:
    """校验类别文件与项目固定顺序一致。"""

    if not path.is_file():
        errors.append(f"names 文件不存在: {path}")
        return
    try:
        names = [line.strip() for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"names 文件不可读取: {exc}")
        return
    if names != EXPECTED_CLASSES:
        errors.append(f"names 文件必须严格为 {EXPECTED_CLASSES}，实际为 {names}")


def _validate_data_config(
    path: Path,
    names_path: Path,
    errors: list[str],
    working_directory: Path | None = None,
) -> dict[str, str]:
    """校验 official Darknet data 配置和类别文件绑定。"""

    if not path.is_file():
        errors.append(f"data cfg 不存在: {path}")
        return {}
    try:
        values = _parse_key_values(path)
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"data cfg 不可读取: {exc}")
        return {}
    return _validate_data_config_values(values, path, names_path, errors, working_directory)


def _validate_data_config_values(
    values: dict[str, str],
    path: Path,
    names_path: Path,
    errors: list[str],
    working_directory: Path | None = None,
) -> dict[str, str]:
    """校验已绑定的 data 配置值，不重新读取配置路径。"""

    if values.get("classes") != str(len(EXPECTED_CLASSES)):
        errors.append(f"data cfg 必须 classes={len(EXPECTED_CLASSES)}")
    missing = sorted(key for key in REQUIRED_DATA_KEYS if not values.get(key))
    if missing:
        errors.append(f"data cfg 缺少必要键: {missing}；训练不得让 Darknet 静默采用默认值")
    configured_names = values.get("names")
    if not configured_names:
        errors.append("data cfg 缺少 names")
    else:
        configured_path = Path(configured_names)
        if not configured_path.is_absolute():
            configured_path = (working_directory or path.parent) / configured_path
        if not _same_path(configured_path, names_path):
            errors.append(f"data cfg names 未绑定到显式 names 文件: {configured_names}")
    base = working_directory or path.parent
    for key in ("train", "valid"):
        if values.get(key):
            configured_list = _resolve_working_path(values[key], base)
            if not configured_list.is_file():
                errors.append(f"data cfg {key} 清单不存在: {configured_list}")
    if values.get("backup"):
        backup = _resolve_working_path(values["backup"], base)
        if not backup.is_dir():
            errors.append(f"data cfg backup 目录不存在或不是目录: {backup}")
    for key in ("saveweights", "savelast"):
        if values.get(key):
            try:
                interval = int(values[key])
            except (TypeError, ValueError):
                interval = 0
            if interval <= 0:
                errors.append(f"data cfg {key} 必须是正整数: {values[key]!r}")
    if values.get("saveweights") and values.get("savelast"):
        try:
            if int(values["saveweights"]) <= int(values["savelast"]):
                errors.append("data cfg 必须满足 saveweights > savelast，才能产生可区分的 *_last.weights")
        except (TypeError, ValueError):
            pass
    return values


def _load_manifest_images_from_bytes(
    raw: bytes,
    manifest: Path,
    data_root: Path,
    errors: list[str],
) -> dict[str, dict[str, dict[str, Any]]]:
    """从指定 manifest 字节解析划分索引，供快照与 SHA/大小共用。"""

    try:
        text = raw.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text, newline=""))
        fieldnames = set(reader.fieldnames or [])
        if not fieldnames or not REQUIRED_MANIFEST_FIELDS.issubset(fieldnames):
            errors.append(f"manifest 缺少必要列: {sorted(REQUIRED_MANIFEST_FIELDS - fieldnames)}")
            return {}
        rows = list(reader)
    except (UnicodeDecodeError, csv.Error) as exc:
        errors.append(f"manifest 不可读取: {exc}")
        return {}
    result: dict[str, dict[str, dict[str, Any]]] = {"train": {}, "val": {}, "test": {}}
    all_images: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        split = (row.get("split") or "").strip()
        if split not in result:
            errors.append(f"manifest 第 {row_number} 行 split 非法: {split!r}")
            continue
        image_text = (row.get("image") or "").strip()
        if not image_text:
            errors.append(f"manifest 第 {row_number} 行缺少 image")
            continue
        label_text = (row.get("label") or "").strip()
        if not label_text:
            errors.append(f"manifest 第 {row_number} 行缺少 label")
            continue
        for field in sorted(REQUIRED_MANIFEST_FIELDS - {"image", "label", "split"}):
            if not (row.get(field) or "").strip():
                errors.append(f"manifest 第 {row_number} 行缺少 {field}")
        image = Path(image_text)
        if not image.is_absolute():
            image = data_root / image
        label = Path(label_text)
        if not label.is_absolute():
            label = data_root / label
        image_resolved = image.resolve()
        label_resolved = label.resolve()
        key = _canonical_path(image_resolved)
        if key in all_images:
            errors.append(f"manifest 图片跨 split 重复: {image_text}")
        all_images.add(key)
        if not image_resolved.is_file():
            errors.append(f"manifest 图片不存在: {image_resolved}")
        if not label_resolved.is_file():
            errors.append(f"manifest 标签不存在，拒绝交给 Darknet 静默跳过: {label_resolved}")
        if image_resolved.stem.casefold() != label_resolved.stem.casefold():
            errors.append(f"manifest image/label 基名不匹配: {image_text} -> {label_text}")
        result[split][key] = {
            "image": str(image_resolved),
            "label": str(label_resolved),
            "manifest_image": image_text,
            "manifest_label": label_text,
            "split": split,
            "manifest_row": row_number,
            "row": {key_name: value for key_name, value in row.items() if value is not None},
        }
    if not result["val"]:
        errors.append("manifest 没有 val 图片")
    return result


def _load_manifest_images(manifest: Path, data_root: Path, errors: list[str]) -> dict[str, dict[str, dict[str, Any]]]:
    """读取清单全部划分并建立 image、label 和审计字段绑定索引。"""

    try:
        raw = manifest.read_bytes()
    except OSError as exc:
        errors.append(f"manifest 不可读取: {exc}")
        return {}
    return _load_manifest_images_from_bytes(raw, manifest, data_root, errors)


def _load_valid_list(
    valid_list: Path,
    manifest_images: dict[str, dict[str, dict[str, Any]]],
    working_directory: Path,
    errors: list[str],
    split: str = "val",
) -> list[Path]:
    """读取 Darknet 清单并要求与 manifest 指定划分完全一致。"""

    if not valid_list.is_file():
        errors.append(f"valid 清单不存在: {valid_list}")
        return []
    entries: list[Path] = []
    seen: set[str] = set()
    try:
        lines = valid_list.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"valid 清单不可读取: {exc}")
        return []
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        image = Path(line)
        if not image.is_absolute():
            image = working_directory / image
        resolved = image.resolve()
        key = _canonical_path(resolved)
        if key in seen:
            errors.append(f"valid 清单存在重复图片: {line}")
        seen.add(key)
        expected_split = manifest_images.get(split, {}) if split in manifest_images else manifest_images
        if key not in expected_split:
            errors.append(f"{split} 清单图片不在 manifest 的 {split} 集合: {line}")
        elif not resolved.is_file():
            errors.append(f"valid 清单图片不存在: {resolved}")
        entries.append(resolved)
    manifest_keys = set(manifest_images.get(split, {}) if split in manifest_images else manifest_images)
    if seen != manifest_keys:
        errors.append(f"{split} 清单与 manifest {split} 集合不一致: list={len(seen)}, manifest={len(manifest_keys)}")
    return entries


def _validate_runtime_stdin_list(
    runtime_list: Path,
    expected_images: list[Path],
    errors: list[str],
) -> dict[str, Any]:
    """严格核对交给 Darknet stdin 的规范化清单与 source valid 顺序绑定。"""

    if not runtime_list.is_file():
        errors.append(f"runtime stdin 清单不存在: {runtime_list}")
        return {"path": str(runtime_list), "sha256": "unavailable", "line_count": 0}
    try:
        lines = runtime_list.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"runtime stdin 清单不可读取: {exc}")
        return {"path": str(runtime_list), "sha256": _safe_sha256(runtime_list), "line_count": 0}

    expected_keys = [_canonical_path(image) for image in expected_images]
    observed_keys: list[str] = []
    if len(lines) != len(expected_images):
        errors.append(
            f"runtime stdin 清单行数与 source valid.list 不一致: runtime={len(lines)}, expected={len(expected_images)}"
        )
    for index, line in enumerate(lines, start=1):
        if not line or line.strip() != line or line.startswith("#"):
            errors.append(f"runtime stdin 清单第 {index} 行格式非法，必须是单个规范化绝对路径: {line!r}")
            continue
        try:
            runtime_image = Path(line)
            resolved_key = _canonical_path(runtime_image)
        except (OSError, RuntimeError, ValueError) as exc:
            errors.append(f"runtime stdin 清单第 {index} 行路径非法: {exc}")
            continue
        if not runtime_image.is_absolute():
            errors.append(f"runtime stdin 清单第 {index} 行不是绝对路径: {line}")
        observed_keys.append(resolved_key)
        if resolved_key in observed_keys[:-1]:
            errors.append(f"runtime stdin 清单存在重复图片，第 {index} 行: {line}")
        if index > len(expected_images):
            continue
        expected_image = expected_images[index - 1]
        expected_key = expected_keys[index - 1]
        if resolved_key != expected_key:
            errors.append(
                f"runtime stdin 清单第 {index} 行未 canonical-resolve 到 source valid.list 对应图片: {line} -> {expected_image}"
            )
        expected_cli_path = _darknet_cli_path(expected_image)
        if line != expected_cli_path:
            errors.append(
                f"runtime stdin 清单第 {index} 行未保持 source valid.list 的规范化路径映射: {line!r} != {expected_cli_path!r}"
            )
    if observed_keys != expected_keys:
        errors.append(
            f"runtime stdin 清单顺序或集合不一致，拒绝只依靠 frame_id 继续: observed={len(observed_keys)}, expected={len(expected_keys)}"
        )
    return {
        "path": str(runtime_list),
        "sha256": _safe_sha256(runtime_list),
        "line_count": len(lines),
        "mapping": "runtime 每行使用 _darknet_cli_path(source valid.list 对应绝对路径)，并按 canonical-resolve 一一且有序绑定",
        "source_to_runtime_ordered_canonical": observed_keys == expected_keys,
    }


def _prepare_runtime_stdin_list(
    source_valid_list: Path,
    runtime_list: Path,
    expected_images: list[Path],
    errors: list[str],
) -> dict[str, Any]:
    """在隔离 run-dir 创建不可覆盖的 Darknet stdin runtime 清单并立即复核。"""

    source_info: dict[str, Any] = {
        "path": str(source_valid_list),
        "sha256": _safe_sha256(source_valid_list),
        "entry_count": len(expected_images),
    }
    try:
        source_lines = source_valid_list.read_text(encoding="utf-8-sig").splitlines()
        source_info["physical_line_count"] = len(source_lines)
        source_info["nonempty_entry_count"] = sum(
            1 for line in source_lines if line.strip() and not line.lstrip().startswith("#")
        )
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"source valid.list 不可读取，不能生成 runtime stdin 清单: {exc}")
        source_info["physical_line_count"] = 0
        source_info["nonempty_entry_count"] = 0
    try:
        runtime_list.parent.mkdir(parents=True, exist_ok=True)
        with runtime_list.open("x", encoding="utf-8", newline="\n") as stream:
            for image in expected_images:
                stream.write(_darknet_cli_path(image) + "\n")
    except (OSError, UnicodeError) as exc:
        errors.append(f"runtime stdin 清单创建失败，拒绝启动 Darknet: {exc}")
    runtime_info = _validate_runtime_stdin_list(runtime_list, expected_images, errors)
    runtime_info["source_valid_list"] = source_info
    return runtime_info


def _validate_environment_gate(report_path: Path, executable: Path, errors: list[str]) -> dict[str, Any]:
    """验证环境报告确实证明 official Darknet/CUDA 路线已就绪。"""

    if not report_path.is_file():
        errors.append(f"环境报告不存在: {report_path}")
        return {}
    try:
        report = _read_json(report_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"环境报告不可读取: {exc}")
        return {}
    if report.get("status") != "PASS" or report.get("framework") != "official-darknet-cuda":
        errors.append("环境报告不是 official-darknet-cuda PASS")
    checks = report.get("checks", {})
    if not isinstance(checks, dict):
        errors.append("环境报告 checks 必须是对象，不能是列表或标量")
        checks = {}
    for name in ("python", "numpy", "nvidia_smi", "nvcc", "darknet", "cuda_device_smoke"):
        value = checks.get(name)
        if not isinstance(value, str) or not value.startswith("通过"):
            errors.append(f"环境报告检查未通过: {name}")
    reported_executable = report.get("darknet_executable")
    if not isinstance(reported_executable, str) or not reported_executable.strip():
        errors.append("环境报告中的 Darknet 可执行文件必须是非空字符串")
    elif not _same_path(Path(reported_executable), executable):
        errors.append("环境报告中的 Darknet 可执行文件与本次参数不一致")
    if not _is_windows_pe(executable):
        errors.append("Darknet 可执行文件不是有效 Windows PE")
    expected_hash = report.get("darknet_sha256")
    if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash):
        errors.append("环境报告没有真实 Darknet SHA-256")
    elif executable.is_file() and _sha256(executable).casefold() != expected_hash.casefold():
        errors.append("Darknet 可执行文件 SHA-256 与环境报告不一致")
    return report


def _validate_dataset_gate(
    report_path: Path,
    approval_path: Path,
    manifest: Path,
    data_root: Path,
    errors: list[str],
    training_manifest_snapshot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """验证自动数据检查和 Wong 人工批准均绑定到同一清单。"""

    if not report_path.is_file():
        errors.append(f"数据检查报告不存在: {report_path}")
        return {}
    if not approval_path.is_file():
        errors.append(f"数据人工批准记录不存在: {approval_path}")
        return {}
    try:
        report = _read_json(report_path)
        approval = _read_json(approval_path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"数据报告或批准记录不可读取: {exc}")
        return {}
    if report.get("status") != "PASS_AUTOMATED_MANUAL_PENDING":
        errors.append("数据检查报告不是自动检查通过且待人工抽查状态")
    checks = report.get("checks", {})
    if not isinstance(checks, dict):
        errors.append("数据检查报告 checks 必须是对象，不能是列表或标量")
        checks = {}
    if not str(checks.get("AC02", "")).startswith("通过"):
        errors.append("数据报告 AC02 未通过")
    if not str(checks.get("AC03", "")).startswith("通过"):
        errors.append("数据报告 AC03 未通过")
    if not str(checks.get("AC04", "")).startswith("待人工抽查"):
        errors.append("数据报告 AC04 不是待人工抽查状态")
    reported_manifest = report.get("manifest")
    if not isinstance(reported_manifest, str) or not _same_path(Path(reported_manifest), manifest):
        errors.append("数据报告中的 manifest 与本次参数不一致")
    reported_root = report.get("data_root")
    if not isinstance(reported_root, str) or not reported_root.strip():
        errors.append("数据检查报告中的 data_root 必须是非空字符串")
    elif not _same_path(Path(reported_root), data_root):
        errors.append("数据报告中的 data_root 与本次参数不一致")
    if approval.get("status") != "APPROVED":
        errors.append("数据人工批准记录 status 必须严格为 APPROVED")
    if approval.get("reviewer") != "Wong":
        errors.append("数据人工批准记录 reviewer 必须严格为 Wong，禁止空值或其他身份")
    reported_approval_report = approval.get("dataset_report")
    if not isinstance(reported_approval_report, str) or not reported_approval_report.strip():
        errors.append("人工批准记录 dataset_report 必须是非空字符串")
    elif not _same_path(Path(reported_approval_report), report_path):
        errors.append("人工批准记录未绑定本次数据检查报告")
    reported_report_hash = approval.get("dataset_report_sha256")
    if (
        not isinstance(reported_report_hash, str)
        or not re.fullmatch(r"[0-9a-fA-F]{64}", reported_report_hash)
        or not report_path.is_file()
        or _sha256(report_path).casefold() != reported_report_hash.casefold()
    ):
        errors.append("人工批准记录中的数据报告 SHA-256 不一致")
    reported_manifest_hash = approval.get("manifest_sha256")
    reported_manifest_hash_valid = isinstance(reported_manifest_hash, str) and bool(
        re.fullmatch(r"[0-9a-fA-F]{64}", reported_manifest_hash)
    )
    manifest_snapshot_matches_approval: bool | None = None
    if training_manifest_snapshot is None:
        if (
            not reported_manifest_hash_valid
            or not manifest.is_file()
            or _sha256(manifest).casefold() != str(reported_manifest_hash).casefold()
        ):
            errors.append("人工批准记录中的 manifest SHA-256 不一致")
    else:
        snapshot_path = training_manifest_snapshot.get("path")
        snapshot_hash = training_manifest_snapshot.get("sha256")
        snapshot_hash_valid = isinstance(snapshot_hash, str) and bool(
            re.fullmatch(r"[0-9a-fA-F]{64}", snapshot_hash)
        )
        snapshot_valid = (
            training_manifest_snapshot.get("capture_status") == "CAPTURED"
            and isinstance(snapshot_path, str)
            and _same_path(Path(snapshot_path), manifest)
            and snapshot_hash_valid
        )
        manifest_snapshot_matches_approval = bool(
            snapshot_valid
            and reported_manifest_hash_valid
            and str(reported_manifest_hash).casefold() == str(snapshot_hash).casefold()
        )
        if not snapshot_valid:
            errors.append("训练输入中的 manifest 稳定快照无效，不能校验人工批准 SHA")
        elif not manifest_snapshot_matches_approval:
            errors.append("人工批准记录中的 manifest SHA-256 与训练输入稳定快照不一致")
    return {
        "report": report,
        "approval": approval,
        "manifest_snapshot_matches_approval": manifest_snapshot_matches_approval,
    }


def _validate_no_hand_approval(
    approval: dict[str, Any],
    manifest_images: dict[str, dict[str, dict[str, Any]]],
    data_root: Path,
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    """验证人工批准的 no_hand 图片确实绑定到 manifest val 行。"""

    raw_items = approval.get("no_hand_images")
    if not isinstance(raw_items, list) or not raw_items:
        errors.append("人工批准记录必须提供非空 no_hand_images 列表")
        return {}
    val_rows = manifest_images.get("val", {})
    approved: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(raw_items, start=1):
        if not isinstance(item, dict):
            errors.append(f"no_hand_images 第 {index} 项必须是对象")
            continue
        image_text = item.get("image")
        split = item.get("split")
        role = item.get("role")
        row_number = item.get("manifest_row")
        if not isinstance(image_text, str) or not image_text.strip():
            errors.append(f"no_hand_images 第 {index} 项 image 必须是非空字符串")
            continue
        if split != "val" or role != "no_hand":
            errors.append(f"no_hand_images 第 {index} 项必须 split=val 且 role=no_hand")
        if not isinstance(row_number, int) or isinstance(row_number, bool):
            errors.append(f"no_hand_images 第 {index} 项 manifest_row 必须是整数")
        image = Path(image_text)
        if not image.is_absolute():
            image = data_root / image
        key = _canonical_path(image)
        row = val_rows.get(key)
        if row is None:
            errors.append(f"zero/no_hand 图片未绑定 manifest val 行: {image_text}")
            continue
        if isinstance(row_number, int) and not isinstance(row_number, bool) and row.get("manifest_row") != row_number:
            errors.append(f"no_hand_images 第 {index} 项 manifest_row 与 manifest 不一致: {row_number}")
        if not _same_path(Path(str(row["image"])), image):
            errors.append(f"no_hand_images 第 {index} 项 image 与 manifest 行不一致: {image_text}")
        label_path = Path(str(row["label"]))
        try:
            label_bytes = label_path.read_bytes()
        except OSError as exc:
            errors.append(f"no_hand 图片标签不可读取: {label_path}: {exc}")
            continue
        if label_bytes.strip():
            errors.append(f"no_hand 图片标签必须为空，实际存在标注: {label_path}")
        approved[key] = row
    if not approved:
        errors.append("没有一条 no_hand 批准记录成功绑定 manifest val 行")
    return approved


def _checkpoint_name_kind(path: Path, cfg_stem: str) -> tuple[str, int | None] | None:
    """解析 official Darknet 按 cfg 基名生成的检查点名称。"""

    match = re.fullmatch(rf"{re.escape(cfg_stem)}_(\d+)\.weights", path.name, flags=re.IGNORECASE)
    if match:
        return ("numbered", int(match.group(1)))
    if path.name.casefold() == f"{cfg_stem}_last.weights".casefold():
        return ("last", None)
    if path.name.casefold() == f"{cfg_stem}_final.weights".casefold():
        return ("final", None)
    return None


def _checkpoint_plan(
    data_values: dict[str, str],
    model_config: Path,
    working_directory: Path,
    max_batches: int | None,
    start_iteration: int,
    errors: list[str],
) -> dict[str, Any]:
    """按 detector.c 的 backup、saveweights、savelast 规则建立输出候选。"""

    plan: dict[str, Any] = {"cfg_stem": model_config.stem, "candidates": []}
    backup_value = data_values.get("backup")
    if not backup_value:
        return plan
    backup = _resolve_working_path(backup_value, working_directory)
    plan["backup"] = str(backup)
    if not backup.is_dir():
        return plan
    try:
        saveweights = int(data_values.get("saveweights", "0"))
        savelast = int(data_values.get("savelast", "0"))
    except (TypeError, ValueError):
        return plan
    plan["saveweights"] = saveweights
    plan["savelast"] = savelast
    if max_batches is None or saveweights <= 0 or savelast <= 0:
        return plan
    base = model_config.stem
    candidates: list[Path] = []
    iter_save = start_iteration
    iter_save_last = start_iteration
    for iteration in range(max(1, start_iteration + 1), max_batches + 1):
        if iteration >= iter_save + saveweights or iteration % saveweights == 0:
            candidates.append(backup / f"{base}_{iteration}.weights")
            iter_save = iteration
        if saveweights > savelast and (
            iteration >= iter_save_last + savelast or (iteration % savelast == 0 and iteration > 1)
        ):
            candidates.append(backup / f"{base}_last.weights")
            iter_save_last = iteration
    candidates.append(backup / f"{base}_final.weights")
    unique: dict[str, Path] = {_canonical_path(path): path for path in candidates}
    plan["candidates"] = [str(path) for path in unique.values()]
    plan["candidate_names"] = [path.name for path in unique.values()]
    return plan


def _validate_checkpoint_io(
    action: str,
    checkpoint_input: Path | None,
    checkpoint_output: Path,
    checkpoint_plan: dict[str, Any],
    cfg_stem: str,
    resume_from_step: int | None,
    errors: list[str],
) -> None:
    """校验输入输出检查点的名称、目录、迭代绑定和不可覆盖条件。"""

    output_kind = _checkpoint_name_kind(checkpoint_output, cfg_stem)
    candidate_names = set(checkpoint_plan.get("candidate_names", []))
    if output_kind is None:
        errors.append(f"checkpoint-output 必须使用 cfg 基名的官方权重名: {cfg_stem}_<iteration>.weights/_last.weights/_final.weights")
    elif checkpoint_output.name not in candidate_names:
        errors.append(f"checkpoint-output 不是本次 {action} 按 saveweights/savelast 可能产生的输出: {checkpoint_output.name}")
    backup_text = checkpoint_plan.get("backup")
    backup_path = Path(backup_text) if isinstance(backup_text, str) and backup_text else None
    if backup_path is not None and not _same_path(checkpoint_output.parent, backup_path):
        errors.append(f"checkpoint-output 必须位于 .data backup 目录: {backup_path}")
    if checkpoint_output.exists():
        errors.append(f"checkpoint-output 已存在，为避免覆盖请指定新输出: {checkpoint_output}")
    for candidate_text in checkpoint_plan.get("candidates", []):
        candidate = Path(candidate_text)
        if candidate.is_file() and not (action == "resume" and checkpoint_input is not None and _same_path(candidate, checkpoint_input)):
            errors.append(f"本次 official Darknet 可能写入的检查点已存在，拒绝覆盖: {candidate}")
    if action != "resume" or checkpoint_input is None:
        return
    if resume_from_step is None:
        errors.append("resume-from-step 缺失")
    else:
        input_kind = _checkpoint_name_kind(checkpoint_input, cfg_stem)
        if input_kind is None or input_kind[0] != "numbered":
            errors.append("resume checkpoint 只允许同一 cfg 基名的 numbered 权重，禁止使用 *_last.weights 或 *_final.weights")
        elif input_kind[1] != resume_from_step:
            errors.append("resume-from-step 与输入 numbered checkpoint 的迭代号不一致")
    if _same_path(checkpoint_input, checkpoint_output):
        errors.append("resume 的 checkpoint 输入和 checkpoint-output 必须是两个不同路径")


def _validate_formal_update_range(
    action: str,
    observed_steps: list[int],
    resume_from_step: int | None,
    errors: list[str],
) -> None:
    """要求正式 train/resume 日志覆盖本次动作应执行的全部连续更新步。"""

    first_step = 1 if action == "train" else (resume_from_step or 0) + 1
    expected_steps = list(range(first_step, FORMAL_TRAINING_MAX_BATCHES + 1))
    if observed_steps != expected_steps:
        errors.append(
            "正式训练日志未证明本次动作完整连续更新至 6000："
            f"期望 {first_step}..{FORMAL_TRAINING_MAX_BATCHES} 共 {len(expected_steps)} 步，"
            f"实际 {len(observed_steps)} 步，首末步为 "
            f"{observed_steps[0] if observed_steps else '无'}/"
            f"{observed_steps[-1] if observed_steps else '无'}"
        )


def _check_no_existing_process(executable: Path) -> str | None:
    """拒绝在同一 Windows 主机已有同名 Darknet 进程时启动。"""

    if os.name != "nt":
        return None
    image_name = executable.name
    try:
        completed = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {image_name}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"无法确认同名进程状态: {exc}"
    if completed.returncode != 0:
        return f"tasklist 退出码 {completed.returncode}，无法确认同名进程状态"
    output = completed.stdout.strip()
    if output and "INFO: No tasks are running" not in output:
        return f"检测到已有同名 Darknet 进程: {image_name}"
    return None


def _make_lock(run_directory: Path) -> Path:
    """以独占方式创建运行锁，防止同一证据目录重复启动。"""

    run_directory.mkdir(parents=True, exist_ok=True)
    lock = run_directory / ".s1_t01_darknet.lock"
    with lock.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps({"pid": os.getpid(), "created_at_utc8": _now_iso()}, ensure_ascii=False) + "\n")
    return lock


def _read_log(path: Path) -> str:
    """读取运行日志并替换不可解码字节。"""

    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _stop_process(process: subprocess.Popen[bytes]) -> None:
    """尽量温和地终止超时或异常进程。"""

    try:
        process.terminate()
        process.wait(timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        try:
            process.kill()
            process.wait(timeout=10)
        except (OSError, subprocess.TimeoutExpired):
            pass


def _run_command(
    command: list[str],
    working_directory: Path,
    log_path: Path,
    timeout_seconds: float,
    no_progress_timeout_seconds: float,
    stdin_path: Path | None = None,
    darknet_seed: int | None = None,
) -> dict[str, Any]:
    """执行一个显式官方 Darknet 命令，禁止 shell 并监控停止条件。"""

    log_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    process: subprocess.Popen[bytes] | None = None
    stop_reason: str | None = None
    stdin_stream = None
    try:
        if stdin_path is not None:
            stdin_stream = stdin_path.open("rb")
        with log_path.open("wb") as log_stream:
            process = subprocess.Popen(
                command,
                cwd=working_directory,
                stdin=stdin_stream,
                stdout=log_stream,
                stderr=subprocess.STDOUT,
                shell=False,
                env=_child_environment(darknet_seed),
            )
            last_size = 0
            last_progress = time.monotonic()
            while process.poll() is None:
                time.sleep(0.25)
                try:
                    current_size = log_path.stat().st_size
                except OSError:
                    current_size = last_size
                now = time.monotonic()
                if current_size > last_size:
                    last_size = current_size
                    last_progress = now
                log_text = _read_log(log_path)
                if BAD_NUMERIC_RE.search(log_text):
                    stop_reason = "日志出现 NaN/Inf"
                elif STOP_RE.search(log_text):
                    stop_reason = "日志出现 OOM 或数据损坏停止标记"
                elif now - last_progress > no_progress_timeout_seconds:
                    stop_reason = f"日志超过 {no_progress_timeout_seconds} 秒无进度"
                elif now - started > timeout_seconds:
                    stop_reason = f"总运行时间超过 {timeout_seconds} 秒"
                if stop_reason:
                    _stop_process(process)
                    break
            exit_code = process.returncode
    except OSError as exc:
        return {
            "command": command,
            "cwd": str(working_directory),
            "log": str(log_path),
            "exit_code": None,
            "error": str(exc),
            "stop_reason": "启动失败",
            "seed_binding": _seed_binding(darknet_seed),
        }
    finally:
        if stdin_stream is not None:
            stdin_stream.close()
    text = _read_log(log_path)
    if stop_reason is None:
        if BAD_NUMERIC_RE.search(text):
            stop_reason = "日志出现 NaN/Inf"
        elif STOP_RE.search(text):
            stop_reason = "日志出现 OOM 或数据损坏停止标记"
    result = {
        "command": command,
        "cwd": str(working_directory),
        "log": str(log_path),
        "exit_code": exit_code,
        "stop_reason": stop_reason,
        "log_sha256": _sha256(log_path) if log_path.is_file() else None,
        "observed_update_steps": sorted(set(int(value) for value in STEP_RE.findall(text))),
        "loss_token_observed": bool(re.search(r"(?i)\bloss\b", text)),
        "non_finite_observed": bool(BAD_NUMERIC_RE.search(text)),
        "output": text,
        "seed_binding": _seed_binding(darknet_seed),
    }
    return result


def _git_identity() -> dict[str, Any]:
    """采集当前提交和工作树身份，不把工作树改动写入 Git。"""

    repository = Path(__file__).resolve().parent.parent
    identity: dict[str, Any] = {
        "repository": str(repository),
        "head": "unavailable",
        "worktree": "unavailable",
        "status_lines": [],
    }
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=10,
        )
        if head.returncode == 0 and re.fullmatch(r"[0-9a-fA-F]{40}", head.stdout.strip()):
            identity["head"] = head.stdout.strip()
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=repository,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=10,
        )
        if status.returncode == 0:
            identity["status_lines"] = status.stdout.splitlines()
            identity["worktree"] = "clean" if not identity["status_lines"] else "dirty"
    except (OSError, subprocess.TimeoutExpired):
        pass
    return identity


def _identity_artifacts(environment: dict[str, Any], executable: Path) -> dict[str, Any]:
    """记录环境探针、数据检查器、CUDA 冒烟和官方 Darknet 身份。"""

    verification_dir = Path(__file__).resolve().parent
    source_commit = environment.get("darknet_source_commit")
    if not isinstance(source_commit, str) or not source_commit.strip():
        source_commit = "unavailable"
    binary_hash = _safe_sha256(executable)
    smoke_value = environment.get("cuda_smoke_executable")
    smoke_hash = "unavailable"
    if isinstance(smoke_value, str) and smoke_value.strip():
        smoke_hash = _safe_sha256(Path(smoke_value))
    smoke_path = smoke_value if isinstance(smoke_value, str) and smoke_value.strip() else "unavailable"
    source_path = environment.get("darknet_source")
    if not isinstance(source_path, str) or not source_path.strip():
        source_path = "unavailable"
    return {
        "environment_probe_py": str(verification_dir / "s1_t01_environment_probe.py"),
        "dataset_check_py": str(verification_dir / "s1_t01_dataset_check.py"),
        "cuda_smoke_source": str(verification_dir / "s1_t01_cuda_smoke.cu"),
        "cuda_smoke_executable": smoke_path,
        "official_darknet_source": source_path,
        "official_darknet_source_reference": "https://raw.githubusercontent.com/AlexeyAB/darknet/master/src/detector.c",
        "environment_probe_py_sha256": _safe_sha256(verification_dir / "s1_t01_environment_probe.py"),
        "dataset_check_py_sha256": _safe_sha256(verification_dir / "s1_t01_dataset_check.py"),
        "cuda_smoke_source_sha256": _safe_sha256(verification_dir / "s1_t01_cuda_smoke.cu"),
        "cuda_smoke_executable_sha256": smoke_hash,
        "official_darknet_source_commit": source_commit,
        "official_darknet_binary_sha256": binary_hash,
    }


def _finite_number(value: Any) -> bool:
    """判断 JSON 数值为有限实数。"""

    try:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and value == value and abs(float(value)) != float("inf")
    except (TypeError, ValueError, OverflowError):
        return False


def _validate_detection_object(item: Any, record_index: int, object_index: int, errors: list[str]) -> None:
    """校验 Darknet JSON 中一个检测框的类别、分数和坐标。"""

    if not isinstance(item, dict):
        errors.append(f"检测 JSON 第 {record_index} 条的第 {object_index} 个框必须是对象")
        return
    has_class_id = "class_id" in item
    has_name = "name" in item
    class_id = item.get("class_id")
    name = item.get("name")
    if not has_class_id and not has_name:
        errors.append(f"检测 JSON 第 {record_index} 条的第 {object_index} 个框缺少 class_id/name")
    if has_class_id and (not isinstance(class_id, int) or isinstance(class_id, bool) or not 0 <= class_id < len(EXPECTED_CLASSES)):
        errors.append(f"检测 JSON 第 {record_index} 条的第 {object_index} 个框 class_id 越界或类型错误: {class_id!r}")
    if has_name and (not isinstance(name, str) or name not in EXPECTED_CLASSES):
        errors.append(f"检测 JSON 第 {record_index} 条的第 {object_index} 个框 name 未知或类型错误: {name!r}")
    if (
        has_class_id
        and has_name
        and isinstance(class_id, int)
        and not isinstance(class_id, bool)
        and 0 <= class_id < len(EXPECTED_CLASSES)
        and isinstance(name, str)
        and name in EXPECTED_CLASSES
        and EXPECTED_CLASSES[class_id] != name
    ):
        errors.append(f"检测 JSON 第 {record_index} 条的第 {object_index} 个框 class_id/name 不一致: {class_id!r}/{name!r}")
    score = item.get("confidence", item.get("score", item.get("probability")))
    if not _finite_number(score):
        errors.append(f"检测 JSON 第 {record_index} 条的第 {object_index} 个框分数不是有限数")
    bbox = item.get("relative_coordinates", item.get("bbox"))
    if isinstance(bbox, dict):
        coordinate_values = [bbox.get(key) for key in ("center_x", "center_y", "width", "height")]
        if any(value is None for value in coordinate_values):
            coordinate_values = [bbox.get(key) for key in ("x", "y", "w", "h")]
    elif isinstance(bbox, list):
        coordinate_values = bbox
    else:
        coordinate_values = []
    if len(coordinate_values) != 4 or any(not _finite_number(value) for value in coordinate_values):
        errors.append(f"检测 JSON 第 {record_index} 条的第 {object_index} 个框坐标无效")


def _parse_detection_output(
    output_path: Path,
    expected_images: list[Path],
    zero_image: Path,
    errors: list[str],
    working_directory: Path | None = None,
    require_zero: bool = True,
    allow_ordered_records: bool = False,
) -> dict[str, Any]:
    """解析官方 detector test -out JSON，并以 objects 数量证明零框。"""

    if not output_path.is_file():
        errors.append(f"Darknet 未生成评估 JSON: {output_path}")
        return {}
    try:
        value = json.loads(output_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"评估 JSON 不可读取或损坏: {exc}")
        return {}
    if not isinstance(value, list):
        errors.append("评估 JSON 顶层必须是 detector test 生成的数组")
        return {}
    expected_keys = [_canonical_path(image) for image in expected_images]
    expected_set = set(expected_keys)
    observed: dict[str, dict[str, Any]] = {}
    for record_index, record in enumerate(value, start=1):
        if not isinstance(record, dict):
            errors.append(f"检测 JSON 第 {record_index} 条必须是对象")
            continue
        filename = record.get("filename")
        if allow_ordered_records:
            frame_id = record.get("frame_id")
            if (
                not isinstance(frame_id, int)
                or isinstance(frame_id, bool)
                or frame_id != record_index
            ):
                errors.append(f"检测 JSON 第 {record_index} 条 frame_id 不匹配 valid 顺序: {frame_id!r}")
        objects = record.get("objects")
        if not isinstance(filename, str) or not filename.strip():
            errors.append(f"检测 JSON 第 {record_index} 条缺少 filename")
            continue
        if not isinstance(objects, list):
            errors.append(f"检测 JSON 第 {record_index} 条 objects 必须是数组")
            continue
        filename_path = Path(filename)
        if not filename_path.is_absolute() and working_directory is not None:
            filename_path = working_directory / filename_path
        key = _canonical_path(filename_path)
        if allow_ordered_records and record_index <= len(expected_keys) and key != expected_keys[record_index - 1]:
            errors.append(
                f"检测 JSON 第 {record_index} 条 filename 未与 valid.list 同序绑定: {filename}"
            )
        if key in observed:
            errors.append(f"检测 JSON 重复 filename: {filename}")
        if key not in expected_set:
            errors.append(f"检测 JSON filename 不在本次 valid 清单: {filename}")
        for object_index, item in enumerate(objects, start=1):
            _validate_detection_object(item, record_index, object_index, errors)
        observed[key] = {"filename": filename, "box_count": len(objects), "objects": objects}
    if set(observed) != expected_set:
        errors.append(f"检测 JSON 图片集合不完整: observed={len(observed)}, expected={len(expected_set)}")
    zero_key = _canonical_path(zero_image)
    zero_record = observed.get(zero_key)
    if require_zero:
        if zero_record is None:
            errors.append("zero-prediction-image 没有对应的结构化检测 JSON 记录")
        elif zero_record["box_count"] != 0:
            errors.append(f"zero-prediction-image 实际检测框数量为 {zero_record['box_count']}，不是零框")
    return {
        "record_count": len(value),
        "image_count": len(observed),
        "binding_mode": "filename_and_frame_id_ordered_valid_list" if allow_ordered_records else "filename",
        "raw_records": value,
        "records": observed,
        "zero_prediction": {
            "image": str(zero_image),
            "record_present": zero_record is not None,
            "box_count": zero_record["box_count"] if zero_record is not None else None,
            "actual_zero_boxes": bool(require_zero and zero_record is not None and zero_record["box_count"] == 0),
        },
    }


def _common_parser(parser: argparse.ArgumentParser) -> None:
    """添加所有动作共用的严格输入参数。"""

    parser.add_argument("--darknet-executable", type=Path, required=True, help="已构建且已在环境报告中绑定的 darknet.exe")
    parser.add_argument("--environment-report", type=Path, required=True, help="status=PASS 的 official-darknet-cuda 环境报告")
    parser.add_argument("--data-root", type=Path, required=True, help="外部数据根目录")
    parser.add_argument("--manifest", type=Path, required=True, help="与数据报告绑定的 UTF-8 manifest.csv")
    parser.add_argument("--dataset-report", type=Path, required=True, help="AC02/AC03 自动通过的数据检查报告")
    parser.add_argument("--dataset-approval", type=Path, required=True, help="Wong 人工抽查后的 APPROVED JSON")
    parser.add_argument("--data-config", type=Path, required=True, help="官方 Darknet .data 配置")
    parser.add_argument("--model-config", type=Path, required=True, help="官方 Darknet YOLO cfg")
    parser.add_argument("--names-file", type=Path, required=True, help="严格为五类固定顺序的 names 文件")
    parser.add_argument("--working-directory", type=Path, required=True, help="运行 Darknet 的工作目录")
    parser.add_argument("--run-dir", type=Path, required=True, help="本次运行日志和 JSONL 输出目录")
    parser.add_argument("--report", type=Path, required=True, help="本次运行 JSON 报告路径")
    parser.add_argument("--dry-run", action="store_true", help="只生成待执行命令，不启动 Darknet")
    parser.add_argument("--timeout-seconds", type=float, default=1800.0, help="单动作总超时，默认1800秒")
    parser.add_argument("--no-progress-timeout-seconds", type=float, default=300.0, help="日志无增长停止时间，默认300秒")


def _build_parser() -> argparse.ArgumentParser:
    """构建命令行解析器。"""

    parser = argparse.ArgumentParser(description="S1-T01 官方 Darknet 训练、恢复和逐验证图评估")
    subparsers = parser.add_subparsers(dest="action", required=True)
    train = subparsers.add_parser("train", help="运行诊断短训或固定 6000-step 正式训练")
    _common_parser(train)
    train.add_argument(
        "--formal-training",
        action="store_true",
        help="显式选择固定正式 schedule：max_batches=6000、steps=4800,5400；不代表精度或最终模型通过",
    )
    train.add_argument(
        "--darknet-seed",
        type=_parse_darknet_seed,
        default=None,
        help=f"仅传给 Darknet 子进程的非负 32 位十进制种子（环境变量 {DARKNET_SEED_ENV}）",
    )
    train.add_argument("--initial-weights", type=Path, required=True, help="显式提供的初始权重，不自动下载")
    train.add_argument("--checkpoint-output", type=Path, required=True, help="按 .data/cfg 规则由本次训练新生成的检查点路径")
    resume = subparsers.add_parser("resume", help="从既有检查点恢复诊断短训或正式训练")
    _common_parser(resume)
    resume.add_argument(
        "--formal-training",
        action="store_true",
        help="显式选择固定正式 schedule：max_batches=6000、steps=4800,5400；不代表精度或最终模型通过",
    )
    resume.add_argument(
        "--darknet-seed",
        type=_parse_darknet_seed,
        default=None,
        help=f"仅传给 Darknet 子进程的非负 32 位十进制种子（环境变量 {DARKNET_SEED_ENV}）",
    )
    resume.add_argument("--checkpoint", type=Path, required=True, help="既有检查点路径")
    resume.add_argument("--checkpoint-output", type=Path, required=True, help="恢复动作应新生成的检查点路径，不得与输入相同")
    resume.add_argument("--resume-from-step", type=int, required=True, help="检查点记录的恢复起始步数")
    evaluate = subparsers.add_parser(
        "evaluate",
        help="读取 valid 清单生成隔离 runtime stdin 清单，单进程执行官方 Darknet detector test -out JSON；-thresh 0.249999 仅用于捕获，并逐图解析",
    )
    _common_parser(evaluate)
    evaluate.add_argument("--weights", type=Path, required=True, help="显式提供的评估权重")
    evaluate.add_argument("--valid-list", type=Path, required=True, help="必须与 manifest val 集合完全一致的 valid 清单")
    evaluate.add_argument("--zero-prediction-image", type=Path, required=True, help="人工确认的无手图，必须包含在 valid 清单中")
    return parser


def _base_report(args: argparse.Namespace) -> dict[str, Any]:
    """建立不含运行结果的报告。"""

    action = getattr(args, "action", None)
    if action in {"train", "resume"}:
        training_profile = "formal_6000" if getattr(args, "formal_training", False) else "diagnostic_short"
    else:
        training_profile = "not_applicable"

    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "created_at_utc8": _now_iso(),
        "framework": "official-darknet-cuda",
        "action": args.action,
        "training_profile": training_profile,
        "training_profile_notice": (
            "profile 仅绑定训练 schedule；训练完成不代表精度、泛化、INT8、资源、最终模型选择或板上验收通过。"
        ),
        "seed_binding": _seed_binding(getattr(args, "darknet_seed", None)),
        "status": "BLOCKED_PREFLIGHT",
        "exit_code": 2,
        "commands": [],
        "errors": [],
        "notes": [
            "本入口不下载数据、不安装依赖、不切换 YOLO 框架。",
            "train/resume 默认仅允许 11..100 诊断短训；只有显式 --formal-training 才允许固定 max_batches=6000、steps=4800,5400。",
            "检查点输出严格绑定 .data backup、cfg 基名、saveweights、savelast，已有候选文件一律不覆盖。",
            "日志不能独立证明梯度有限或优化器状态恢复，相关 AC05 结论仍需审查证据。",
            "evaluate 必须由 detector test -out JSON 的 objects 数量证明零框，并拒绝 NaN/Inf/OOM/损坏。",
        ],
    }
    if action in {"train", "resume"}:
        report["training_input_binding"] = {
            "status": "NOT_CAPTURED",
            "preflight": None,
            "before_child": None,
            "after_child": None,
            "execution_status": "NOT_STARTED",
            "scope_notice": "仅比较 preflight、before_child、after_child 各采样点；不证明 child 运行期间未发生后又恢复的修改。",
        }
    if action == "evaluate":
        report["evaluation_threshold_policy"] = {
            "darknet_capture": {
                "cli_flag": "-thresh",
                "value": D6_CAPTURE_THRESHOLD,
                "comparison": "Darknet YOLO retains score > capture_threshold (strict)",
                "purpose": "pre-D6 candidate capture threshold only; not a final model/metric threshold",
            },
            "final_metric_score_threshold": {
                "allowed_range_inclusive": list(D6_SCORE_THRESHOLD_RANGE),
                "comparison": "D6 retains confidence >= selected score_threshold",
                "selected": None,
                "frozen": False,
            },
        }
    return report


def _preflight(args: argparse.Namespace, report: dict[str, Any]) -> dict[str, Any]:
    """执行所有动作共用的启动前检查。"""

    errors: list[str] = report["errors"]
    training_action = args.action in {"train", "resume"}
    executable = args.darknet_executable.resolve()
    working_directory = args.working_directory.resolve()
    data_root = args.data_root.resolve()
    manifest = args.manifest.resolve()
    if not executable.is_file():
        errors.append(f"Darknet 可执行文件不存在: {executable}")
    if not working_directory.is_dir():
        errors.append(f"Darknet 工作目录不存在: {working_directory}")
    if not data_root.is_dir():
        errors.append(f"数据根目录不存在: {data_root}")
    if not manifest.is_file():
        errors.append(f"manifest 不存在: {manifest}")
    if args.timeout_seconds <= 0 or args.no_progress_timeout_seconds <= 0:
        errors.append("超时参数必须为正数")
    environment = _validate_environment_gate(args.environment_report.resolve(), executable, errors)
    formal_training = bool(getattr(args, "formal_training", False))
    if formal_training and args.action not in {"train", "resume"}:
        errors.append("--formal-training 仅允许用于 train 或 resume")
    if formal_training and getattr(args, "darknet_seed", None) is None:
        errors.append("正式训练必须显式提供 --darknet-seed（uint32）")
    model = _validate_model_config(
        args.model_config.resolve(),
        errors,
        args.action in {"train", "resume"},
        formal_training=formal_training,
    )
    _validate_names_file(args.names_file.resolve(), errors)
    training_input_snapshot: dict[str, Any] | None = None
    manifest_approval_matches_snapshot = True
    if training_action:
        training_input_snapshot, manifest_images, data_config_values = _capture_training_input_snapshot(
            args,
            working_directory,
            "preflight",
        )
        errors.extend(training_input_snapshot["errors"])
        dataset = _validate_dataset_gate(
            args.dataset_report.resolve(),
            args.dataset_approval.resolve(),
            manifest,
            data_root,
            errors,
            training_manifest_snapshot=training_input_snapshot["manifest"],
        )
        approval = dataset.get("approval", {})
        approved_manifest_hash = approval.get("manifest_sha256") if isinstance(approval, dict) else None
        captured_manifest_hash = training_input_snapshot["manifest"].get("sha256")
        approved_hash_valid = isinstance(approved_manifest_hash, str) and re.fullmatch(
            r"[0-9a-fA-F]{64}", approved_manifest_hash
        )
        captured_hash_valid = isinstance(captured_manifest_hash, str) and re.fullmatch(
            r"[0-9a-fA-F]{64}", captured_manifest_hash
        )
        manifest_approval_matches_snapshot = bool(
            dataset.get("manifest_snapshot_matches_approval") is True
            and approved_hash_valid
            and captured_hash_valid
            and approved_manifest_hash.casefold() == captured_manifest_hash.casefold()
        )
        if not manifest_approval_matches_snapshot:
            expected_hash = approved_manifest_hash.casefold() if approved_hash_valid else "<invalid-or-unavailable>"
            actual_hash = captured_manifest_hash.casefold() if captured_hash_valid else "<invalid-or-unavailable>"
            errors.append(
                "获批 manifest SHA-256 与训练输入快照不一致，拒绝启动: "
                f"expected={expected_hash} actual={actual_hash}"
            )
        data_config = _validate_data_config_values(
            data_config_values,
            Path(training_input_snapshot["data_config"]["path"]),
            args.names_file.resolve(),
            errors,
            working_directory,
        )
    else:
        dataset = _validate_dataset_gate(
            args.dataset_report.resolve(),
            args.dataset_approval.resolve(),
            manifest,
            data_root,
            errors,
        )
        data_config = _validate_data_config(
            args.data_config.resolve(),
            args.names_file.resolve(),
            errors,
            working_directory,
        )
        manifest_images = _load_manifest_images(manifest, data_root, errors)
    train_images: list[Path] = []
    valid_images: list[Path] = []
    configured_train = None
    configured_valid = None
    if data_config.get("train"):
        configured_train = _resolve_working_path(data_config["train"], working_directory)
        train_images = _load_valid_list(configured_train, manifest_images, working_directory, errors, "train")
    if data_config.get("valid"):
        configured_valid = _resolve_working_path(data_config["valid"], working_directory)
        valid_images = _load_valid_list(configured_valid, manifest_images, working_directory, errors, "val")
    approved_no_hand = _validate_no_hand_approval(dataset.get("approval", {}), manifest_images, data_root, errors)
    if training_action:
        for key, configured in (("train", configured_train), ("valid", configured_valid)):
            expected_path = _canonical_path(configured) if configured is not None else "unavailable"
            observed_path = training_input_snapshot["data_config"].get(f"{key}_list_path")
            if observed_path != expected_path:
                errors.append(f".data 的 {key} 路径在校验与输入快照之间发生变化")
                training_input_snapshot["status"] = "FAILED"
        if training_input_snapshot["status"] != "CAPTURED" or not manifest_approval_matches_snapshot:
            report["training_input_binding"].update(
                {
                    "status": "BLOCKED",
                    "preflight": training_input_snapshot,
                    "execution_status": "BLOCKED_PREFLIGHT",
                }
            )
        else:
            report["training_input_binding"].update(
                {
                    "status": "PREFLIGHT_CAPTURED",
                    "preflight": training_input_snapshot,
                    "execution_status": "NOT_STARTED",
                }
            )
    if args.action == "evaluate":
        explicit_valid = args.valid_list.resolve()
        if configured_valid is None or not _same_path(configured_valid, explicit_valid):
            errors.append("data cfg valid 未绑定到显式 valid 清单")
        valid_images = _load_valid_list(explicit_valid, manifest_images, working_directory, errors, "val")
        zero_image = args.zero_prediction_image.resolve()
        zero_key = _canonical_path(zero_image)
        if zero_key not in approved_no_hand:
            errors.append("zero-prediction-image 未属于 Wong 批准的 no_hand manifest val 样本")
        if not any(_same_path(zero_image, image) for image in valid_images):
            errors.append("zero-prediction-image 不在完整 valid 清单中")
    for path in (args.data_config, args.model_config, args.names_file):
        if not path.resolve().is_file():
            errors.append(f"配置文件不存在: {path.resolve()}")
    checkpoint_plan: dict[str, Any] = {}
    if args.action == "train":
        initial_weights = args.initial_weights.resolve()
        if not initial_weights.is_file() or initial_weights.stat().st_size == 0:
            errors.append(f"初始权重不存在或为空: {initial_weights}")
        checkpoint_input = None
        checkpoint_output = args.checkpoint_output.resolve()
    elif args.action == "resume":
        checkpoint_input = args.checkpoint.resolve()
        checkpoint_output = args.checkpoint_output.resolve()
        if not checkpoint_input.is_file() or checkpoint_input.stat().st_size == 0:
            errors.append(f"恢复输入检查点不存在或为空: {checkpoint_input}")
        if args.resume_from_step < MIN_TRAIN_UPDATES:
            errors.append(f"resume-from-step 必须至少为 {MIN_TRAIN_UPDATES}")
    elif args.action == "evaluate":
        weights = args.weights.resolve()
        if not weights.is_file() or weights.stat().st_size == 0:
            errors.append(f"评估权重不存在或为空: {weights}")
        checkpoint_input = None
        checkpoint_output = None
    if args.action in {"train", "resume"}:
        checkpoint_plan = _checkpoint_plan(
            data_config,
            args.model_config.resolve(),
            working_directory,
            model.get("max_batches"),
            0 if args.action == "train" else args.resume_from_step,
            errors,
        )
        _validate_checkpoint_io(
            args.action,
            checkpoint_input,
            checkpoint_output,
            checkpoint_plan,
            args.model_config.resolve().stem,
            args.resume_from_step if args.action == "resume" else None,
            errors,
        )
        if args.action == "resume" and model.get("max_batches") is not None and args.resume_from_step >= model["max_batches"]:
            errors.append("resume-from-step 必须小于 cfg max_batches，才能继续至少一个更新步")
    process_error = _check_no_existing_process(executable)
    if process_error:
        errors.append(process_error)
    report["git"] = _git_identity()
    report["identity"] = _identity_artifacts(environment, executable)
    seed = getattr(args, "darknet_seed", None)
    report["seed_binding"] = _seed_binding(seed)
    report["inputs"] = {
        "darknet_executable": str(executable),
        "environment_report": str(args.environment_report.resolve()),
        "data_root": str(data_root),
        "manifest": str(manifest),
        "manifest_sha256": (
            training_input_snapshot["manifest"].get("sha256", "unavailable")
            if training_action and training_input_snapshot is not None
            else _safe_sha256(manifest)
        ),
        "dataset_report": str(args.dataset_report.resolve()),
        "dataset_approval": str(args.dataset_approval.resolve()),
        "data_config": (
            training_input_snapshot["data_config"]["path"]
            if training_action and training_input_snapshot is not None
            else str(args.data_config.resolve())
        ),
        "model_config": str(args.model_config.resolve()),
        "names_file": str(args.names_file.resolve()),
        "working_directory": str(working_directory),
        "darknet_executable_sha256": _safe_sha256(executable),
        "seed_binding": _seed_binding(seed),
        "model_config_values": model,
        "data_config_values": data_config,
        "resolved_data_paths": {
            "train": str(configured_train) if configured_train is not None else "unavailable",
            "valid": str(configured_valid) if configured_valid is not None else "unavailable",
            "backup": checkpoint_plan.get("backup", "unavailable"),
        },
        "train_manifest_count": len(manifest_images.get("train", {})),
        "validation_image_count": len(valid_images),
        "workflow_script_sha256": _safe_sha256(Path(__file__).resolve()),
    }
    if args.action in {"train", "resume"}:
        report["inputs"]["manifest_size_bytes"] = training_input_snapshot["manifest"].get("size_bytes")
        report["inputs"]["checkpoint_mapping"] = checkpoint_plan
        report["inputs"]["checkpoint_output"] = str(checkpoint_output)
    if args.action == "resume":
        report["inputs"]["resume_checkpoint"] = str(checkpoint_input)
        report["inputs"]["resume_checkpoint_sha256_before"] = _safe_sha256(checkpoint_input)
    if args.action == "evaluate":
        report["inputs"]["zero_prediction_image"] = str(args.zero_prediction_image.resolve())
        report["inputs"]["approved_no_hand_manifest_rows"] = sorted(
            int(row["manifest_row"]) for row in approved_no_hand.values() if isinstance(row.get("manifest_row"), int)
        )
    artifact_paths: dict[str, Path] = {
        "environment_report": args.environment_report.resolve(),
        "dataset_report": args.dataset_report.resolve(),
        "dataset_approval": args.dataset_approval.resolve(),
        "data_config": (
            Path(training_input_snapshot["data_config"]["path"])
            if training_action and training_input_snapshot is not None
            else args.data_config.resolve()
        ),
        "model_config": args.model_config.resolve(),
        "names_file": args.names_file.resolve(),
    }
    if args.action == "evaluate":
        artifact_paths["valid_list"] = args.valid_list.resolve()
    if args.action == "train":
        artifact_paths["initial_weights"] = args.initial_weights.resolve()
    elif args.action == "resume":
        artifact_paths["resume_checkpoint_before"] = args.checkpoint.resolve()
    else:
        artifact_paths["evaluation_weights"] = args.weights.resolve()
    report["inputs"]["artifact_sha256"] = {
        key: (
            training_input_snapshot["data_config"].get("sha256", "unavailable")
            if key == "data_config" and training_action and training_input_snapshot is not None
            else _safe_sha256(path)
        )
        for key, path in artifact_paths.items()
    }
    report["inputs"]["environment_report_sha256"] = _safe_sha256(args.environment_report.resolve())
    report["outputs"] = {
        "checkpoint_output": {
            "path": str(checkpoint_output) if checkpoint_output is not None else "unavailable",
            "sha256_before": "unavailable",
            "created_by_this_run": "not_executed",
        },
        "evaluation_json": {
            "path": str(args.run_dir.resolve() / "evaluation.json") if args.action == "evaluate" else "unavailable",
            "sha256": "unavailable",
        },
    }
    evaluation_output_paths: list[Path] = []
    if args.action == "evaluate":
        evaluation_directory = args.run_dir.resolve() / "detections"
        evaluation_output_paths = [
            evaluation_directory / f"eval_{index:06d}.json" for index in range(1, len(valid_images) + 1)
        ]
        existing_outputs = [path for path in evaluation_output_paths if path.exists()]
        if existing_outputs:
            errors.append(f"评估逐图 JSON 已存在，为避免覆盖请指定新的 run-dir；已有 {len(existing_outputs)} 个文件")
        if (args.run_dir.resolve() / "evaluation.json").exists() or (args.run_dir.resolve() / "evaluation.jsonl").exists():
            errors.append("评估汇总 JSON/JSONL 已存在，为避免覆盖请指定新的 run-dir")
        report["outputs"]["evaluation_per_image"] = {
            "directory": str(evaluation_directory),
            "count": len(evaluation_output_paths),
            "all_completed": "not_executed",
        }
    return {
        "executable": executable,
        "working_directory": working_directory,
        "valid_images": valid_images,
        "train_images": train_images,
        "model": model,
        "environment": environment,
        "dataset": dataset,
        "manifest_images": manifest_images,
        "data_config_values": data_config,
        "training_input_preflight": training_input_snapshot,
        "approved_no_hand": approved_no_hand,
        "checkpoint_plan": checkpoint_plan,
        "checkpoint_input": checkpoint_input,
        "checkpoint_output": checkpoint_output,
        "evaluation_json": args.run_dir.resolve() / "evaluation.json" if args.action == "evaluate" else None,
        "evaluation_output_paths": evaluation_output_paths,
    }


def _commands_for_action(args: argparse.Namespace, context: dict[str, Any]) -> list[list[str]]:
    """构造不经过 shell 的官方 Darknet 命令。"""

    executable = str(context["executable"])
    data_config = str(args.data_config.resolve())
    model_config = str(args.model_config.resolve())
    if args.action == "train":
        return [[executable, "detector", "train", data_config, model_config, str(args.initial_weights.resolve()), "-dont_show"]]
    if args.action == "resume":
        return [[executable, "detector", "train", data_config, model_config, str(args.checkpoint.resolve()), "-dont_show"]]
    output_json = context.get("evaluation_json") or context["working_directory"] / "evaluation.json"
    return [[
        executable,
        "detector",
        "test",
        data_config,
        model_config,
        str(args.weights.resolve()),
        "-dont_show",
        "-out",
        str(output_json),
        "-thresh",
        f"{D6_CAPTURE_THRESHOLD:.6f}",
    ]]


def _write_report(path: Path, report: dict[str, Any]) -> None:
    """以 UTF-8 写入 JSON 报告。"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _workflow_exit_code(report: dict[str, Any]) -> int:
    """根据最终状态计算 workflow 进程退出码。"""

    if report["status"] in {"PLANNED_NO_EXECUTION", "EXECUTED_REVIEW_REQUIRED"} and not report["errors"]:
        return 0
    return 2


def _execute(args: argparse.Namespace, report: dict[str, Any], context: dict[str, Any]) -> None:
    """执行动作并填充可复核的运行结果。"""

    report["status"] = "EXECUTING"
    commands = _commands_for_action(args, context)
    seed = getattr(args, "darknet_seed", None)
    report["planned_commands"] = [
        {
            "command": command,
            "cwd": str(context["working_directory"]),
            "seed_binding": _seed_binding(seed),
            "training_profile": report.get("training_profile", "not_applicable"),
        }
        for command in commands
    ]
    if args.action in {"train", "resume"}:
        binding = report.get("training_input_binding")
        if (
            not isinstance(binding, dict)
            or binding.get("status") not in {"PREFLIGHT_CAPTURED", "PLANNED_NO_EXECUTION"}
            or not isinstance(binding.get("preflight"), dict)
            or binding["preflight"].get("status") != "CAPTURED"
        ):
            report["errors"].append("train/resume 缺少有效的 preflight 清单快照，拒绝将流程标为通过")
            report["status"] = "BLOCKED_PREFLIGHT"
            report["exit_code"] = 2
            if isinstance(binding, dict):
                binding["status"] = "BLOCKED"
                binding["execution_status"] = "BLOCKED_PREFLIGHT"
            return
    if args.dry_run:
        if args.action in {"train", "resume"}:
            binding = report.get("training_input_binding")
            if isinstance(binding, dict):
                binding["execution_status"] = "PLANNED_NO_EXECUTION"
                binding["status"] = "PLANNED_NO_EXECUTION"
                binding["before_child"] = None
                binding["after_child"] = None
        report["status"] = "PLANNED_NO_EXECUTION"
        report["acceptance"] = {"command_executed": False, "reason": "dry-run"}
        if args.action in {"train", "resume"}:
            report["acceptance"]["training_input_binding"] = "仅记录 preflight；before-child 与 after-child 未执行"
        return
    try:
        lock = _make_lock(args.run_dir.resolve())
    except FileExistsError:
        report["errors"].append(f"运行目录已被另一进程锁定: {args.run_dir.resolve()}")
        return
    try:
        if args.action in {"train", "resume"}:
            binding = report.get("training_input_binding")
            if (
                not isinstance(binding, dict)
                or binding.get("status") != "PREFLIGHT_CAPTURED"
                or not isinstance(binding.get("preflight"), dict)
                or binding["preflight"].get("status") != "CAPTURED"
            ):
                report["errors"].append("缺少通过预检的训练输入快照，拒绝启动 Darknet child")
                report["status"] = "EXECUTION_FAILED"
                if isinstance(binding, dict):
                    binding["status"] = "BLOCKED"
                    binding["execution_status"] = "PRELAUNCH_REJECTED"
                return
            log_path = args.run_dir.resolve() / f"{args.action}.log"
            started_ns = time.time_ns()
            before_child, _, _ = _capture_training_input_snapshot(
                args,
                context["working_directory"],
                "before_child",
            )
            preflight_differences = _training_snapshot_differences(binding["preflight"], before_child)
            before_child["comparison_to_preflight"] = {
                "matches": not preflight_differences,
                "differences": preflight_differences,
            }
            binding["before_child"] = before_child
            if preflight_differences:
                report["errors"].append(
                    "Darknet child 启动前训练输入与 preflight 不一致: " + "; ".join(preflight_differences)
                )
                binding["status"] = "PRELAUNCH_REJECTED"
                binding["execution_status"] = "PRELAUNCH_REJECTED"
                report["acceptance"] = {"command_executed": False, "reason": "training_input_changed_before_child"}
                report["status"] = "EXECUTION_FAILED"
                return
            result: dict[str, Any]
            try:
                result = _run_command(
                    commands[0],
                    context["working_directory"],
                    log_path,
                    args.timeout_seconds,
                    args.no_progress_timeout_seconds,
                    darknet_seed=seed,
                )
            finally:
                after_child, _, _ = _capture_training_input_snapshot(
                    args,
                    context["working_directory"],
                    "after_child",
                )
                postrun_differences = _training_snapshot_differences(binding["preflight"], after_child)
                after_child["comparison_to_preflight"] = {
                    "matches": not postrun_differences,
                    "differences": postrun_differences,
                }
                binding["after_child"] = after_child
                if postrun_differences:
                    binding["status"] = "POSTRUN_MISMATCH"
                    binding["execution_status"] = "POSTRUN_MISMATCH"
                    report["errors"].append(
                        "Darknet child 返回后训练输入与 preflight 不一致: " + "; ".join(postrun_differences)
                    )
                else:
                    binding["status"] = "AFTER_CHILD_MATCHED_PREFLIGHT"
                    binding["execution_status"] = "AFTER_CHILD_MATCHED_PREFLIGHT"
            result.setdefault("seed_binding", _seed_binding(seed))
            result["training_profile"] = report.get("training_profile", "not_applicable")
            report["commands"].append(result)
            if report["training_input_binding"].get("status") == "POSTRUN_MISMATCH":
                report["status"] = "EXECUTION_FAILED"
                return
            if result.get("exit_code") != 0 or result.get("stop_reason") or result.get("non_finite_observed"):
                report["errors"].append("Darknet 训练/恢复未以干净状态结束")
                return
            if not result.get("loss_token_observed"):
                report["errors"].append("Darknet 日志未观察到 loss，不能核对训练数值")
                return
            steps = result.get("observed_update_steps", [])
            log_text = result.get("output", "")
            checkpoint_output = context["checkpoint_output"]
            if not checkpoint_output.is_file() or checkpoint_output.stat().st_size == 0:
                report["errors"].append(f"本次运行未生成明确 checkpoint-output: {checkpoint_output}")
                return
            output_stat = checkpoint_output.stat()
            output_hash = _sha256(checkpoint_output)
            report["outputs"]["checkpoint_output"].update(
                {
                    "sha256_after": output_hash,
                    "size": output_stat.st_size,
                    "mtime_ns": output_stat.st_mtime_ns,
                    "created_by_this_run": output_stat.st_mtime_ns >= started_ns,
                }
            )
            if output_stat.st_mtime_ns < started_ns:
                report["errors"].append("checkpoint-output 修改时间早于本次 Darknet 启动，不能证明由本次运行生成")
                return
            if args.action == "train":
                report["checkpoint"] = {
                    "path": str(checkpoint_output),
                    "sha256": output_hash,
                    "size": output_stat.st_size,
                    "mapping": report["inputs"].get("checkpoint_mapping", {}),
                }
                if len(steps) < MIN_TRAIN_UPDATES:
                    report["errors"].append(f"日志只观察到 {len(steps)} 个更新步，少于 {MIN_TRAIN_UPDATES}")
                    return
                if report.get("training_profile") == "formal_6000":
                    _validate_formal_update_range(args.action, steps, None, report["errors"])
                    if report["errors"]:
                        return
                report["acceptance"] = {
                    "ac05_candidate": True,
                    "training_profile": report.get("training_profile", "diagnostic_short"),
                    "observed_update_steps": steps,
                    "loss_finite_in_log": not bool(BAD_NUMERIC_RE.search(log_text)),
                    "gradient_finite": "NOT_OBSERVABLE_FROM_OFFICIAL_DARKNET_LOG",
                    "checkpoint_saved": True,
                    "optimizer_state_restore": "待恢复动作和独立审查",
                }
            else:
                checkpoint = args.checkpoint.resolve()
                after_input_hash = _safe_sha256(checkpoint)
                before_hash = report.get("inputs", {}).get("resume_checkpoint_sha256_before")
                report["checkpoint"] = {
                    "input_path": str(checkpoint),
                    "input_sha256_before": before_hash,
                    "input_sha256_after": after_input_hash,
                    "input_unchanged": before_hash == after_input_hash,
                    "output_path": str(checkpoint_output),
                    "output_sha256": output_hash,
                    "output_size": output_stat.st_size,
                    "mapping": report["inputs"].get("checkpoint_mapping", {}),
                }
                if len(steps) < MIN_RESUME_UPDATES or max(steps, default=-1) < args.resume_from_step + MIN_RESUME_UPDATES:
                    report["errors"].append("恢复日志未证明至少继续一个更新步")
                    return
                if before_hash == "unavailable" or before_hash != after_input_hash:
                    report["errors"].append("恢复后输入 checkpoint SHA-256 发生变化或不可核对")
                    return
                if report.get("training_profile") == "formal_6000":
                    _validate_formal_update_range(args.action, steps, args.resume_from_step, report["errors"])
                    if report["errors"]:
                        return
                report["acceptance"] = {
                    "ac05_resume_candidate": True,
                    "training_profile": report.get("training_profile", "diagnostic_short"),
                    "resume_from_step": args.resume_from_step,
                    "observed_update_steps": steps,
                    "checkpoint_output_created": True,
                    "input_checkpoint_unchanged": True,
                    "model_and_optimizer_state_restore": "需核对 Darknet 日志和检查点内部状态",
                    "counter_continued": True,
                }
        else:
            output_json = context["evaluation_json"]
            output_jsonl = args.run_dir.resolve() / "evaluation.jsonl"
            if output_json.exists():
                report["errors"].append(f"评估 JSON 已存在，为避免覆盖请指定新的 run-dir: {output_json}")
                return
            output_directory = args.run_dir.resolve() / "detections"
            output_directory.mkdir(parents=True, exist_ok=True)
            evaluation_output_paths = context.get("evaluation_output_paths") or [
                output_directory / f"eval_{index:06d}.json"
                for index, _ in enumerate(context["valid_images"], start=1)
            ]
            records: list[dict[str, Any]] = []
            command_records: list[dict[str, Any]] = []
            zero_result: dict[str, Any] = {}
            parsed: dict[str, Any] = {}
            runtime_stdin_list = args.run_dir.resolve() / "runtime_valid.list"
            runtime_info = _prepare_runtime_stdin_list(
                args.valid_list.resolve(),
                runtime_stdin_list,
                context["valid_images"],
                report["errors"],
            )
            report.setdefault("inputs", {})
            report.setdefault("inputs", {})
            report["inputs"]["valid_list_source"] = runtime_info.get("source_valid_list", {})
            report["inputs"]["darknet_stdin_list"] = runtime_info
            report["outputs"]["runtime_stdin_list"] = runtime_info
            if report["errors"]:
                report["commands"] = command_records
                return
            command = commands[0]
            log_path = args.run_dir.resolve() / "evaluate.log"
            result = _run_command(
                command,
                context["working_directory"],
                log_path,
                args.timeout_seconds,
                args.no_progress_timeout_seconds,
                stdin_path=runtime_stdin_list,
            )
            command_record = {
                **result,
                "stdin_valid_list_source": str(args.valid_list.resolve()),
                "stdin_valid_list_runtime": str(runtime_stdin_list),
                "evaluation_json": str(output_json),
                "evaluation_json_sha256": _safe_sha256(output_json),
            }
            command_records.append(command_record)
            if result.get("non_finite_observed"):
                report["errors"].append("evaluate 单进程观察到 NaN/Inf 非有限值，失败即停")
            elif result.get("exit_code") != 0 or result.get("stop_reason"):
                report["errors"].append("evaluate 单进程未以干净状态结束，失败即停")
            else:
                error_count = len(report["errors"])
                parsed = _parse_detection_output(
                    output_json,
                    context["valid_images"],
                    args.zero_prediction_image.resolve(),
                    report["errors"],
                    context["working_directory"],
                    require_zero=True,
                    allow_ordered_records=True,
                )
                if len(report["errors"]) == error_count:
                    parsed_records = parsed.get("records", {})
                    raw_records = parsed.get("raw_records", [])
                    for index, (image, image_output, raw_record) in enumerate(
                        zip(context["valid_images"], evaluation_output_paths, raw_records), start=1
                    ):
                        if image_output.exists():
                            report["errors"].append(f"评估逐图 JSON 在写入前已出现，拒绝覆盖: {image_output}")
                            break
                        normalized_record = dict(raw_record)
                        normalized_record["filename"] = _darknet_cli_path(image)
                        with image_output.open("x", encoding="utf-8", newline="\n") as stream:
                            stream.write(json.dumps([normalized_record], ensure_ascii=False, indent=2) + "\n")
                        parsed_record = parsed_records.get(_canonical_path(image), {})
                        records.append(
                            {
                                "index": index,
                                "frame_id": raw_record.get("frame_id"),
                                "image": str(image),
                                "box_count": parsed_record.get("box_count"),
                                "objects": parsed_record.get("objects", []),
                                "output_json": str(image_output),
                                "output_json_sha256": _safe_sha256(image_output),
                                "log": str(log_path),
                                "log_sha256": result.get("log_sha256"),
                            }
                        )
                    zero_result = parsed.get("zero_prediction", {})
            report["commands"] = command_records
            with output_jsonl.open("x", encoding="utf-8", newline="\n") as stream:
                for record in records:
                    stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            report["evaluation_jsonl"] = {
                "path": str(output_jsonl),
                "sha256": _sha256(output_jsonl),
                "record_count": len(records),
            }
            report["outputs"]["evaluation_json"].update(
                {"sha256": _safe_sha256(output_json), "size": output_json.stat().st_size if output_json.is_file() else 0}
            )
            report["outputs"]["evaluation_per_image"] = {
                "directory": str(output_directory),
                "count": len(records),
                "planned_count": len(context["valid_images"]),
                "all_completed": len(records) == len(context["valid_images"]),
            }
            report["acceptance"] = {
                "ac06_candidate": not report["errors"] and len(records) == len(context["valid_images"]),
                "validation_manifest_count": len(context["valid_images"]),
                "completed_image_count": len(records),
                "all_validation_images_completed": len(records) == len(context["valid_images"]),
                "detector_test_command_count": len(command_records),
                "per_image_box_class_score_output": "evaluation.jsonl 和 detections/eval_*.json 由单进程 detector test -out JSON 按 runtime stdin 清单与 source valid.list 的同序 canonical 映射结构化绑定",
                "ordered_binding": parsed.get("binding_mode", "unavailable"),
                "zero_prediction_actual_zero_boxes": zero_result.get("actual_zero_boxes", False),
                "zero_prediction_box_count": zero_result.get("box_count"),
                "zero_prediction_semantics": "同时绑定 Wong 批准 no_hand manifest 行和 detector test JSON 的 objects=[]",
                "mAP_threshold": "未设置",
            }
    finally:
        try:
            lock.unlink()
        except OSError:
            pass
    if not report["errors"]:
        report["status"] = "EXECUTED_REVIEW_REQUIRED"


def main(argv: list[str] | None = None) -> int:
    """运行严格预检和显式官方 Darknet 动作。"""

    args = _build_parser().parse_args(argv)
    report = _base_report(args)
    try:
        context = _preflight(args, report)
        _validate_darknet_path_lengths(args, context, report["errors"])
        if report["errors"]:
            report["exit_code"] = 2
            _write_report(args.report, report)
            print(json.dumps({"status": report["status"], "errors": report["errors"]}, ensure_ascii=False, indent=2))
            return 2
        _execute(args, report, context)
    except Exception as exc:
        report["errors"].append(f"流程入口异常: {exc}")
        if report["status"] == "EXECUTING":
            report["status"] = "EXECUTION_FAILED"
        else:
            report["status"] = "BLOCKED_PREFLIGHT"
    if report["errors"] and report["status"] not in {"BLOCKED_PREFLIGHT", "PLANNED_NO_EXECUTION"}:
        report["status"] = "EXECUTION_FAILED"
    report["exit_code"] = _workflow_exit_code(report)
    _write_report(args.report, report)
    print(json.dumps({"status": report["status"], "errors": report["errors"], "report": str(args.report.resolve())}, ensure_ascii=False, indent=2))
    return report["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
