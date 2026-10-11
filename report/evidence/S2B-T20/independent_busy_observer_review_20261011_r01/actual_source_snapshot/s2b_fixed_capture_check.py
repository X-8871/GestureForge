#!/usr/bin/env python3
"""按冻结 tiny416 规则检查保存到 PC 的固定输入结果，不操作板卡。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    from . import s1_t02_d9_yolo_decode as d9
except ImportError:
    import s1_t02_d9_yolo_decode as d9


REPO_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = "report/evidence/S2A-T01/tiny416_model_manifest.json"
MODEL_SHA256 = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
SPEC_PATH = "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
SPEC_SHA256 = "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"
CPU_D9_RECORD_PATH = "report/evidence/S2A-T29/cpu_decode_nms_reference.json"
CPU_D9_RECORD_COMMIT = "671f9cf494b92ce182b3f1542fefd0cfd4b209f5"
CPU_D9_RECORD_LF_SHA256 = "24361a13e262d1774ae255195dac3b05df4c16b9c287ff06945f2d630d3a0231"
SOURCE_LF_HASHES = {
    "verification/s1_t02_d9_yolo_decode.py": "0be8e2dc0878116b5239a20a397f4f063de7b33c2ee38e1d0aadf1ced7d365c6",
    "verification/s1_t02_d6_detection_metrics.py": "5ff91ffbbaa82935811f2ddc335434a3c70afa58eaa980e353e64b057803bea2",
}
HEAD_LENGTHS = {"head13": 5070, "head26": 20280}
ABS_TOLERANCE = 1e-6
GOLDEN_RECORD_TOLERANCE = 1e-12
MAX_FRAMES = 4096
MAX_JSON_BYTES = 16 * 1024 * 1024
MAX_MODEL_BYTES = 32 * 1024 * 1024
MAX_SOURCE_ORDER = (13 * 13 + 26 * 26) * 3 * 5 - 1
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
FRAME_FIELDS = {"frame_id", "sample_id", "input", "head_tensors", "nms_output_box_count", "detections"}
DETECTION_FIELDS = {"class_id", "class_name", "score", "xyxy", "source_order"}
SCOPE = "仅检查本地离线文件；不代表物理通信、阶段2B G0/G3或1000次连续板上任务通过。"


class CaptureCheckError(ValueError):
    """输入格式、来源绑定或输出路径不符合离线检查约定。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CaptureCheckError(message)


def sha256_bytes(payload: bytes) -> str:
    """计算原始字节摘要，检测头不进行任何换行或 word 补齐。"""

    return hashlib.sha256(payload).hexdigest()


def _fields(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    _require(type(value) is dict, f"{label} 必须是对象")
    _require(set(value) == expected, f"{label} 字段错误：missing={sorted(expected - set(value))} extra={sorted(set(value) - expected)}")
    return value


def _integer(value: Any, low: int, high: int, label: str) -> int:
    _require(type(value) is int and low <= value <= high, f"{label} 必须是 [{low},{high}] 的整数，不能是布尔值")
    return value


def _text(value: Any, label: str) -> str:
    _require(type(value) is str and bool(value) and "\0" not in value, f"{label} 必须是无 NUL 的非空字符串")
    return value


def _hash(value: Any, label: str) -> str:
    _require(type(value) is str and SHA256_RE.fullmatch(value) is not None, f"{label} 必须是小写 SHA-256")
    return value


def _number(value: Any, low: float, high: float, label: str) -> float:
    _require(type(value) in (int, float), f"{label} 必须是数值，不能是布尔值")
    try:
        number = float(value)
    except (OverflowError, ValueError) as exc:
        raise CaptureCheckError(f"{label} 数值溢出") from exc
    _require(math.isfinite(number) and low <= number <= high, f"{label} 必须有限且在 [{low},{high}] 内")
    return number


def _literal_path(value: Any, root: Path, label: str) -> Path:
    """保留给定路径字符；相对路径以明确的仓库根为基准，不展开变量。"""

    path = Path(_text(value, label))
    return path if path.is_absolute() else root / path


def _same_file(left: Path, right: Path) -> bool:
    try:
        return left.samefile(right)
    except OSError as exc:
        raise CaptureCheckError(f"无法核对文件身份：{left} / {right}") from exc


@dataclass
class ReadFile:
    """保存本次实际读取的字节与路径，以便绑定结果和检查并发变化。"""

    path: Path
    label: str
    payload: bytes
    identity: tuple[int, int]

    @property
    def sha256(self) -> str:
        return sha256_bytes(self.payload)

    def binding(self) -> dict[str, Any]:
        return {"role": self.label, "path": str(self.path), "sha256": self.sha256, "bytes": len(self.payload)}


def _read_file(path: Path, label: str, limit: int, files: list[ReadFile]) -> ReadFile:
    try:
        _require(stat.S_ISREG(path.stat().st_mode), f"{label} 缺失或不是普通文件：{path}")
        with path.open("rb") as stream:
            opened = os.fstat(stream.fileno())
            _require(stat.S_ISREG(opened.st_mode), f"{label} 打开的目标不是普通文件：{path}")
            payload = stream.read(limit + 1)
    except OSError as exc:
        raise CaptureCheckError(f"{label} 无法读取精确路径：{path}") from exc
    _require(len(payload) <= limit, f"{label} 文件超过大小上限 {limit}：{path}")
    result = ReadFile(path, label, payload, (opened.st_dev, opened.st_ino))
    files.append(result)
    return result


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _require(key not in result, f"JSON 含重复键：{key}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> Any:
    raise CaptureCheckError(f"JSON 不允许非有限常量：{value}")


def _json(file: ReadFile) -> dict[str, Any]:
    try:
        value = json.loads(file.payload.decode("utf-8"), object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError, ValueError) as exc:
        if isinstance(exc, CaptureCheckError):
            raise
        raise CaptureCheckError(f"{file.label} 不是有效 UTF-8 JSON：{file.path}") from exc
    _require(type(value) is dict, f"{file.label} JSON 顶层必须是对象")
    return value


def _lf_digest(file: ReadFile) -> str:
    """仅对已冻结的 Git 文本计算 CRLF 转 LF 摘要，同时保留实际字节摘要。"""

    return sha256_bytes(file.payload.replace(b"\r\n", b"\n"))


@lru_cache(maxsize=1)
def _manifest_heads(payload: bytes) -> dict[str, dict[str, Any]]:
    """完整摘要通过后缓存固定清单解析，避免逐帧重复解析向量库。"""

    config = json.loads(payload.decode("utf-8"))
    _require(config["status"] == "G0_FROZEN", "模型清单未冻结")
    return {head["name"]: head for head in config["address_map"]["heads"]}


def _frozen_config(root: Path, files: list[ReadFile]) -> dict[str, dict[str, Any]]:
    spec = _read_file(root / SPEC_PATH, "frozen_spec", MAX_JSON_BYTES, files)
    model = _read_file(root / MODEL_PATH, "frozen_model_manifest", MAX_MODEL_BYTES, files)
    _require(spec.sha256 == SPEC_SHA256, "G0 规格原始字节 SHA-256 变化")
    _require(model.sha256 == MODEL_SHA256, "模型清单原始字节 SHA-256 变化")
    for relative, expected in SOURCE_LF_HASHES.items():
        source = _read_file(root / relative, "frozen_decoder_source", MAX_JSON_BYTES, files)
        _require(_lf_digest(source) == expected, f"冻结 D9/D6 源码变化：{relative}")
    _require(_same_file(Path(d9.__file__), root / "verification/s1_t02_d9_yolo_decode.py"), "实际导入的 D9 不是所绑定的仓库文件")
    return _manifest_heads(model.payload)


def _detections(value: Any, count: Any, label: str) -> list[dict[str, Any]]:
    _integer(count, 0, d9.MAX_OUTPUTS, f"{label}.nms_output_box_count")
    _require(type(value) is list and len(value) == count, f"{label}.detections 与框数量不符")
    seen_orders: set[int] = set()
    for index, item in enumerate(value):
        current = f"{label}.detections[{index}]"
        row = _fields(item, DETECTION_FIELDS, current)
        class_id = _integer(row["class_id"], 0, 4, f"{current}.class_id")
        _require(row["class_name"] == d9.CLASS_NAMES[class_id], f"{current}.class_name 与 class_id 不一致")
        order = _integer(row["source_order"], 0, MAX_SOURCE_ORDER, f"{current}.source_order")
        _require(order not in seen_orders, f"{current} source_order 重复")
        _require(order % 5 == class_id, f"{current} source_order 与 class_id 不一致")
        seen_orders.add(order)
        _number(row["score"], 0.25, 1.0, f"{current}.score")
        xyxy = row["xyxy"]
        _require(type(xyxy) is list and len(xyxy) == 4, f"{current}.xyxy 必须恰为四个分量")
        coords = [_number(number, 0.0, 1.0, f"{current}.xyxy[{axis}]") for axis, number in enumerate(xyxy)]
        _require(coords[2] > coords[0] and coords[3] > coords[1], f"{current}.xyxy 面积必须为正")
    return value


def _frame(row: Any, label: str, *, source_record: bool = False) -> dict[str, Any]:
    if source_record:
        _require(type(row) is dict and FRAME_FIELDS <= set(row), f"{label} 缺少 T29 样本字段")
        row = {key: row[key] for key in FRAME_FIELDS}
    else:
        _fields(row, FRAME_FIELDS, label)
    _integer(row["frame_id"], 0, 0xFFFFFFFF, f"{label}.frame_id")
    _text(row["sample_id"], f"{label}.sample_id")
    identity = _fields(row["input"], {"pl_input_sha256", "geometry_wh"}, f"{label}.input")
    _hash(identity["pl_input_sha256"], f"{label}.input.pl_input_sha256")
    geometry = identity["geometry_wh"]
    _require(type(geometry) is list and len(geometry) == 2, f"{label}.input.geometry_wh 必须恰为宽高")
    for index, number in enumerate(geometry):
        _integer(number, 1, 0xFFFFFFFF, f"{label}.input.geometry_wh[{index}]")
    heads = _fields(row["head_tensors"], set(HEAD_LENGTHS), f"{label}.head_tensors")
    for name, expected_length in HEAD_LENGTHS.items():
        if source_record:
            _require(type(heads[name]) is dict, f"{label}.{name} 必须是对象")
            _hash(heads[name].get("tensor_sha256"), f"{label}.{name}.tensor_sha256")
            _integer(heads[name].get("byte_length"), expected_length, expected_length, f"{label}.{name}.byte_length")
        else:
            head = _fields(heads[name], {"path", "tensor_sha256", "byte_length"}, f"{label}.{name}")
            _text(head["path"], f"{label}.{name}.path")
            _hash(head["tensor_sha256"], f"{label}.{name}.tensor_sha256")
            _integer(head["byte_length"], expected_length, expected_length, f"{label}.{name}.byte_length")
    _detections(row["detections"], row["nms_output_box_count"], label)
    return row


def _frames(value: Any, label: str, *, source_record: bool = False) -> list[dict[str, Any]]:
    _require(type(value) is list and 1 <= len(value) <= MAX_FRAMES, f"{label} 必须显式列出 1..{MAX_FRAMES} 帧")
    rows = [_frame(row, f"{label}[{index}]", source_record=source_record) for index, row in enumerate(value)]
    _require(len({row["sample_id"] for row in rows}) == len(rows), f"{label} sample_id 重复，身份歧义")
    _require(len({row["frame_id"] for row in rows}) == len(rows), f"{label} frame_id 重复，身份歧义")
    return rows


def _document(value: dict[str, Any], kind: str) -> list[dict[str, Any]]:
    keys = {"schema_version", "kind", "model_manifest_sha256", "samples"}
    if kind == "s2b_fixed_reference":
        keys.add("golden_source")
    _fields(value, keys, kind)
    _integer(value["schema_version"], 1, 1, f"{kind}.schema_version")
    _require(value["kind"] == kind, f"JSON kind 必须是 {kind}")
    _require(value["model_manifest_sha256"] == MODEL_SHA256, f"{kind} 模型哈希不等于冻结 tiny416 清单")
    return _frames(value["samples"], f"{kind}.samples")


def _golden_source(descriptor: Any, root: Path, files: list[ReadFile]) -> tuple[ReadFile, list[dict[str, Any]], dict[str, Any]]:
    source = _fields(descriptor, {"kind", "path", "sha256"}, "golden_source")
    _require(source["kind"] in ("frozen_cpu_d9", "synthetic_hand_computed"), "golden_source.kind 未知")
    expected = _hash(source["sha256"], "golden_source.sha256")
    file = _read_file(_literal_path(source["path"], root, "golden_source.path"), "independent_golden_source", MAX_JSON_BYTES, files)
    _require(file.sha256 == expected, "黄金来源记录原始字节 SHA-256 不匹配")
    record = _json(file)
    metadata = dict(source)
    if source["kind"] == "frozen_cpu_d9":
        _require(_lf_digest(file) == CPU_D9_RECORD_LF_SHA256, "CPU D9 黄金记录不等于已冻结 2A Git blob")
        _require(record.get("status") == "CPU_REFERENCE_GENERATED" and record.get("task_id") == "S2A-T29", "冻结 CPU D9 记录状态或任务不符")
        metadata.update({"source_commit": CPU_D9_RECORD_COMMIT, "repository_path": CPU_D9_RECORD_PATH, "git_lf_sha256": CPU_D9_RECORD_LF_SHA256})
    else:
        _fields(record, {"schema_version", "kind", "model_manifest_sha256", "basis", "samples"}, "synthetic golden record")
        _integer(record["schema_version"], 1, 1, "synthetic golden record.schema_version")
        _require(record["kind"] == "s2b_synthetic_hand_computed" and record["model_manifest_sha256"] == MODEL_SHA256, "合成手算来源 schema/kind/model 不符")
        basis = _fields(record["basis"], {"path", "sha256", "description"}, "synthetic golden record.basis")
        _text(basis["description"], "synthetic golden record.basis.description")
        basis_file = _read_file(_literal_path(basis["path"], root, "basis.path"), "independent_fixture_basis", MAX_JSON_BYTES, files)
        _require(basis_file.sha256 == _hash(basis["sha256"], "basis.sha256"), "手算 fixture 依据文件 SHA-256 不匹配")
        metadata["basis"] = basis
    rows = _frames(record.get("samples"), "golden_source.samples", source_record=True)
    if source["kind"] == "synthetic_hand_computed":
        _require(all(row["sample_id"].startswith("synthetic_") for row in rows), "手算来源仅允许显式 synthetic_ 样本，不冒充冻结真实样本")
    return file, rows, metadata


def _identity(row: dict[str, Any]) -> dict[str, Any]:
    return {key: row[key] for key in ("frame_id", "sample_id", "input")}


def _read_heads(row: dict[str, Any], root: Path, label: str, files: list[ReadFile]) -> dict[str, ReadFile]:
    heads: dict[str, ReadFile] = {}
    for name, length in HEAD_LENGTHS.items():
        binding = row["head_tensors"][name]
        file = _read_file(_literal_path(binding["path"], root, f"{label}.{name}.path"), f"{label}.{name}", length, files)
        _require(len(file.payload) == length, f"{label}.{name} 长度不等于 {length}，不得截断或补齐尾 word")
        _require(file.sha256 == binding["tensor_sha256"], f"{label}.{name} 原始字节 SHA-256 不匹配")
        _require(0x80 not in file.payload, f"{label}.{name} 含冻结对称 INT8 范围之外的 -128")
        heads[name] = file
    return heads


def _decode(heads: dict[str, ReadFile], row: dict[str, Any], config: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    logits = {
        name.removeprefix("head") + "x" + name.removeprefix("head"): [(value if value < 128 else value - 256) * config[name]["int8_scale"] for value in file.payload]
        for name, file in heads.items()
    }
    width, height = row["input"]["geometry_wh"]
    try:
        predictions = d9.decode_yolov4_tiny416(logits, row["sample_id"], width, height, score_threshold=0.25)
    except (ValueError, OverflowError) as exc:
        raise CaptureCheckError(f"独立黄金头 D9 解码失败：{row['sample_id']}") from exc
    return [{"class_id": item.class_id, "class_name": item.name, "score": item.confidence, "xyxy": list(item.box), "source_order": item.source_order} for item in predictions]


def compare_detections(expected: list[dict[str, Any]], actual: list[dict[str, Any]], tolerance: float = ABS_TOLERANCE) -> dict[str, Any]:
    """逐索引比较 D9 输出，离散字段和顺序不使用数值容差。"""

    errors: list[str] = []
    max_score = max_xyxy = 0.0
    if len(expected) != len(actual):
        errors.append(f"框数量不同：expected={len(expected)} actual={len(actual)}")
    for index, (golden, capture) in enumerate(zip(expected, actual)):
        for field in ("class_id", "class_name", "source_order"):
            if golden[field] != capture[field]:
                errors.append(f"detections[{index}].{field} 不同（含输出顺序）")
        score_error = abs(float(golden["score"]) - float(capture["score"]))
        max_score = max(max_score, score_error)
        if score_error > tolerance:
            errors.append(f"detections[{index}].score 绝对误差 {score_error!r} 超过 {tolerance!r}")
        for axis, (left, right) in enumerate(zip(golden["xyxy"], capture["xyxy"])):
            coordinate_error = abs(float(left) - float(right))
            max_xyxy = max(max_xyxy, coordinate_error)
            if coordinate_error > tolerance:
                errors.append(f"detections[{index}].xyxy[{axis}] 绝对误差 {coordinate_error!r} 超过 {tolerance!r}")
    return {"match": not errors, "errors": errors, "max_score_absolute_error": max_score, "max_coordinate_absolute_error": max_xyxy}


def check_capture(reference_path: Path, capture_path: Path, *, repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """读取黄金来源、两组完整检测头和捕获框，返回仅本次离线比对结果。"""

    files: list[ReadFile] = []
    config = _frozen_config(repo_root, files)
    reference_file = _read_file(reference_path, "reference_json", MAX_JSON_BYTES, files)
    capture_file = _read_file(capture_path, "capture_json", MAX_JSON_BYTES, files)
    _require(not _same_file(reference_path, capture_path), "reference 与 capture 不能是同一文件或硬链接")
    reference_document = _json(reference_file)
    reference = _document(reference_document, "s2b_fixed_reference")
    capture = _document(_json(capture_file), "s2b_fixed_capture")
    source_file, source_rows, source_metadata = _golden_source(reference_document["golden_source"], repo_root, files)
    _require(not _same_file(source_file.path, capture_path) and not _same_file(source_file.path, reference_path), "黄金来源不能使用捕获或 reference 文件自身")
    source_by_id = {row["sample_id"]: row for row in source_rows}
    golden_heads: list[dict[str, ReadFile]] = []
    capture_heads: list[dict[str, ReadFile]] = []
    decoded: list[list[dict[str, Any]]] = []
    for index, row in enumerate(reference):
        source = source_by_id.get(row["sample_id"])
        _require(source is not None, f"reference[{index}] 样本不在绑定的独立黄金记录中")
        _require(_identity(row) == _identity(source), f"reference[{index}] frame/sample/input/几何与黄金来源不同")
        for name in HEAD_LENGTHS:
            for field in ("tensor_sha256", "byte_length"):
                _require(row["head_tensors"][name][field] == source["head_tensors"][name][field], f"reference[{index}].{name}.{field} 未绑定到独立黄金记录")
        _require(row["detections"] == source["detections"] and row["nms_output_box_count"] == source["nms_output_box_count"], f"reference[{index}] 框记录与独立黄金来源不同")
        heads = _read_heads(row, repo_root, f"golden[{index}]", files)
        golden_heads.append(heads)
        expected = _decode(heads, row, config)
        consistency = compare_detections(expected, source["detections"], GOLDEN_RECORD_TOLERANCE)
        _require(consistency["match"], f"独立黄金记录与其完整 raw 头的 D9 结果不符：{row['sample_id']} {consistency['errors']}")
        decoded.append(expected)
    for index, row in enumerate(capture):
        capture_heads.append(_read_heads(row, repo_root, f"capture[{index}]", files))
    source_inputs = [reference_file, source_file] + [file for heads in golden_heads for file in heads.values()]
    source_inputs += [file for file in files if file.label == "independent_fixture_basis"]
    source_identities = {file.identity for file in source_inputs}
    captured_inputs = [capture_file] + [file for heads in capture_heads for file in heads.values()]
    for captured in captured_inputs:
        _require(captured.identity not in source_identities, f"捕获文件与黄金来源使用相同文件或硬链接：{captured.path}")
    frame_reports: list[dict[str, Any]] = []
    errors: list[str] = []
    if len(reference) != len(capture):
        errors.append(f"帧数量不同：expected={len(reference)} actual={len(capture)}")
    for index, (expected_row, actual_row) in enumerate(zip(reference, capture)):
        row_errors: list[str] = []
        if _identity(expected_row) != _identity(actual_row):
            row_errors.append("frame_id/sample_id/输入tensor哈希/图像几何不同（含帧顺序）")
        head_reports: dict[str, Any] = {}
        for name in HEAD_LENGTHS:
            golden = golden_heads[index][name].payload
            captured = capture_heads[index][name].payload
            offsets = [offset for offset, (left, right) in enumerate(zip(golden, captured)) if left != right]
            head_reports[name] = {"match": not offsets, "checked_bytes": len(golden), "mismatch_byte_count": len(offsets), "first_mismatch_offset": offsets[0] if offsets else None}
            if offsets:
                row_errors.append(f"{name} 全字节比对失败：{len(offsets)} 个字节，首个 offset={offsets[0]}")
        # 两头不一致时，不对捕获框做成功判定；保留整数阶段的明确失败。
        detection_report = compare_detections(decoded[index], actual_row["detections"]) if all(item["match"] for item in head_reports.values()) else {"match": False, "status": "NOT_RUN_HEAD_MISMATCH"}
        row_errors.extend(detection_report.get("errors", []))
        frame_reports.append({"reference_identity": _identity(expected_row), "capture_identity": _identity(actual_row), "match": not row_errors, "head_tensors": head_reports, "detections": detection_report, "errors": row_errors})
        errors.extend(f"frame[{index}]: {error}" for error in row_errors)
    # 报告只绑定刚刚使用的稳定快照；并发改写文件必须使本次检查失败。
    for file in files:
        try:
            with file.path.open("rb") as stream:
                opened = os.fstat(stream.fileno())
                _require((opened.st_dev, opened.st_ino) == file.identity, f"本次检查期间输入文件身份发生变化：{file.path}")
                current = stream.read(len(file.payload) + 1)
            _require(sha256_bytes(current) == file.sha256, f"本次检查期间输入发生变化：{file.path}")
        except OSError as exc:
            raise CaptureCheckError(f"检查后无法复核输入：{file.path}") from exc
    return {
        "schema_version": 1,
        "status": "PASS_OFFLINE_CAPTURE_CHECK" if not errors else "FAIL_OFFLINE_CAPTURE_CHECK",
        "scope": SCOPE,
        "model_manifest_sha256": MODEL_SHA256,
        "absolute_tolerance": ABS_TOLERANCE,
        "relative_tolerance": 0.0,
        "reference_frame_count": len(reference),
        "capture_frame_count": len(capture),
        "golden_source": source_metadata,
        "input_bindings": [file.binding() for file in files],
        "frames": frame_reports,
        "errors": errors,
        "limitations": ["输入tensor摘要是来源记录与捕获声明的身份绑定，本工具未读取实际输入tensor或证明传输。", "synthetic_hand_computed 的来源描述需要独立审查；本工具验证文件哈希和手算记录与D9的一致性，不能认证作者身份。", "冻结D9/D6及T29 Git文本仅在冻结摘要核对时将CRLF转LF，报告另绑定实际原始字节；所有raw头保持逐字节。"],
    }


def _new_output(path: Path) -> None:
    _require(path.name not in ("", ".", ".."), "report 名称无效")
    _require(path.parent.is_dir(), f"report 精确父目录不存在或不是目录：{path.parent}")
    _require(not os.path.lexists(path), f"report 已存在，本次未写入；该旧文件不是本次结果：{path}")


def _write_report(path: Path, report: dict[str, Any]) -> None:
    """独占创建结果；写入失败时只移除本次创建且身份未变的残缺文件。"""

    payload = (json.dumps(report, ensure_ascii=False, allow_nan=False, indent=2) + "\n").encode("utf-8")
    created_identity: tuple[int, int] | None = None
    try:
        with path.open("xb") as stream:
            identity = os.fstat(stream.fileno())
            created_identity = (identity.st_dev, identity.st_ino)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as exc:
        if created_identity is not None:
            try:
                current = path.stat()
                if stat.S_ISREG(current.st_mode) and (current.st_dev, current.st_ino) == created_identity:
                    path.unlink()
            except OSError:
                pass
        raise CaptureCheckError(f"report 独占创建或完整写入失败，本次没有有效报告：{path}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path, help="含独立黄金来源绑定的 reference JSON")
    parser.add_argument("--capture", required=True, type=Path, help="本地捕获 JSON；不连接串口或板卡")
    parser.add_argument("--report", required=True, type=Path, help="精确父目录已存在且尚未存在的新报告路径")
    args = parser.parse_args(argv)
    try:
        _new_output(args.report)
        report = check_capture(args.reference, args.capture)
        _write_report(args.report, report)
    except (ValueError, OSError, RecursionError) as exc:
        print(f"ERROR_OFFLINE_CAPTURE_CHECK: {exc}; 本次未生成可用报告。", file=sys.stderr)
        return 2
    print(f"{report['status']}: frames={report['reference_frame_count']} report={args.report}")
    return 0 if report["status"] == "PASS_OFFLINE_CAPTURE_CHECK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
