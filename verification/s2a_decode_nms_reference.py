#!/usr/bin/env python3
"""根据冻结 T25 检测头张量生成阶段 2A 的 CPU 解码/NMS 参考。"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import zlib
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import cv2
import numpy as np

try:
    from . import s1_t02_d9_yolo_decode as d9
except ImportError:
    import s1_t02_d9_yolo_decode as d9


BASELINE_HEAD = "c9b35a44d3d62c6a30ad84f78670755f37c70398"
G0_SPEC_PATH = "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
MODEL_MANIFEST_PATH = "report/evidence/S2A-T01/tiny416_model_manifest.json"
SAMPLE_CATALOG_PATH = "report/evidence/S2A-T01/fixed_test_samples.json"
T25_INDEX_PATH = "report/evidence/S2A-T25/cpu_layer_golden_index.json"
T25_EXPORTER_PATH = "verification/s2a_cpu_layer_goldens.py"
T25_TEST_PATH = "verification/test_s2a_cpu_layer_goldens.py"
OUTPUT_RELATIVE_PATH = "report/evidence/S2A-T29/cpu_decode_nms_reference.json"
EXPECTED_SAMPLE_COUNT = 109
EXPECTED_CLASSES = ("fist", "palm", "one", "two_up", "three")
EMPTY_LABEL_SAMPLE_IDS = (
    "approved_no_hand_001",
    "approved_no_hand_002",
    "approved_no_hand_003",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


class ReferenceError(ValueError):
    """表示冻结输入、哈希或解码结果不符合阶段 2A 契约。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReferenceError(message)


def sha256_bytes(payload: bytes) -> str:
    """计算字节串的 SHA-256。"""

    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    """分块计算文件 SHA-256，不复制大型文件。"""

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReferenceError(f"{label} 无法按 UTF-8 JSON 读取：{path}") from exc
    _require(isinstance(value, dict), f"{label} 顶层必须是 JSON 对象")
    return value


def _repo_path(root: Path, relative_path: str) -> Path:
    """解析仓库内相对路径并拒绝越界或符号链接逃逸。"""

    rel = Path(relative_path)
    _require(not rel.is_absolute() and ".." not in rel.parts, f"仓库路径非法：{relative_path}")
    path = root / rel
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    _require(resolved_path.is_relative_to(resolved_root), f"仓库路径越界：{relative_path}")
    return path


def _repo_binding(root: Path, role: str, relative_path: str, expected_sha256: str | None = None) -> dict[str, str]:
    path = _repo_path(root, relative_path)
    _require(path.is_file(), f"绑定文件缺失或不是文件：{relative_path}")
    digest = sha256_file(path)
    if expected_sha256 is not None:
        _require(digest == expected_sha256, f"{role} SHA-256 与冻结值不符：{relative_path}")
    return {"role": role, "path": relative_path, "sha256": digest}


def current_git_head(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReferenceError("无法读取当前 Git HEAD") from exc
    return result.stdout.strip().lower()


def classify_runtime_head(
    baseline_head: str,
    runtime_head: str,
    is_ancestor: Callable[[str, str], bool],
) -> str:
    """允许冻结基线本身或其后代提交作为运行 HEAD。"""

    _require(GIT_COMMIT_RE.fullmatch(baseline_head) is not None, "冻结基线提交哈希格式错误")
    _require(GIT_COMMIT_RE.fullmatch(runtime_head) is not None, "运行时 HEAD 哈希格式错误")
    if runtime_head == baseline_head:
        return "baseline"
    _require(is_ancestor(baseline_head, runtime_head), f"运行时 HEAD 不是冻结基线后代：{runtime_head}")
    return "descendant"


def _git_is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, descendant],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        raise ReferenceError("无法验证运行 HEAD 与冻结基线的祖先关系") from exc
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise ReferenceError("git merge-base 无法完成运行 HEAD 祖先关系检查")


def validate_exact_shard_names(expected_names: set[str], found_names: set[str]) -> None:
    """要求 T25 shard 目录只含完整索引声明的文件集合。"""

    missing = sorted(expected_names - found_names)
    extra = sorted(found_names - expected_names)
    _require(not missing and not extra, f"T25 shard 集合不匹配：missing={missing[:3]} extra={extra[:3]}")


def _sample_ground_truth(sample: dict[str, Any]) -> list[list[Any]]:
    """读取冻结样本 GT；规则合成输入按 catalog 约定缺省为空列表。"""

    value = sample.get("ground_truth_yolo", [])
    _require(isinstance(value, list), f"样本 {sample.get('sample_id')} GT 必须是列表")
    return value


def verify_zlib_shard(
    compressed: bytes,
    shard_record: dict[str, Any],
    raw_record: dict[str, Any],
) -> bytes:
    """先校验压缩字节，再限长解压并验证完整原始流摘要。"""

    _require(shard_record.get("codec") == "zlib", "T25 shard codec 不是 zlib")
    packed_size = shard_record.get("compressed_bytes")
    packed_hash = shard_record.get("sha256")
    _require(type(packed_size) is int and packed_size >= 0, "T25 压缩长度类型非法")
    _require(isinstance(packed_hash, str) and SHA256_RE.fullmatch(packed_hash) is not None, "T25 压缩 SHA 格式非法")
    _require(len(compressed) == packed_size, "T25 shard 压缩长度不匹配")
    _require(sha256_bytes(compressed) == packed_hash, "T25 shard 压缩 SHA-256 不匹配")

    raw_size = shard_record.get("decompressed_bytes")
    raw_hash = shard_record.get("decompressed_sha256")
    _require(type(raw_size) is int and raw_size > 0, "T25 shard 原始长度类型非法")
    _require(isinstance(raw_hash, str) and SHA256_RE.fullmatch(raw_hash) is not None, "T25 原始 SHA 格式非法")
    _require(raw_record.get("unique_output_raw_bytes") == raw_size, "T25 shard 与 raw stream 长度声明不同")
    _require(raw_record.get("raw_stream_sha256") == raw_hash, "T25 shard 与 raw stream 摘要声明不同")

    decoder = zlib.decompressobj()
    try:
        raw = decoder.decompress(compressed, raw_size + 1)
        _require(len(raw) == raw_size, "T25 shard 解压长度不匹配或超过冻结上限")
        _require(not decoder.unconsumed_tail, "T25 shard 解压仍有未消费数据")
        _require(decoder.eof, "T25 shard zlib 流未完整结束")
        _require(not decoder.unused_data, "T25 shard 含未绑定尾部数据")
    except zlib.error as exc:
        raise ReferenceError("T25 shard zlib 解压失败") from exc
    _require(sha256_bytes(raw) == raw_hash, "T25 shard 解压后 SHA-256 不匹配")
    return raw


def _validate_catalog(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    samples = catalog.get("samples")
    _require(catalog.get("sample_count") == EXPECTED_SAMPLE_COUNT, "固定样本 catalog 计数不是 109")
    _require(isinstance(samples, list) and len(samples) == EXPECTED_SAMPLE_COUNT, "固定样本 catalog 列表不完整")
    _require(catalog.get("pl_input_contract", {}).get("tensor_shape_nchw") == [1, 3, 416, 416], "固定输入 shape 不匹配")
    _require(catalog.get("pl_input_contract", {}).get("tensor_dtype") == "signed int8 two's complement", "固定输入类型不匹配")

    expected_sources = {
        "official_hagrid_test": 100,
        "official_hagrid_test_multibox": 2,
        "approved_train_negative_from_calibration_list": 3,
        "synthetic_rgb416": 4,
    }
    source_counts: Counter[str] = Counter()
    coverage_counts: Counter[str] = Counter()
    observed_empty_ids: list[str] = []
    observed_class_ids: set[int] = set()
    observed_ids: set[str] = set()

    for expected_index, sample in enumerate(samples):
        _require(isinstance(sample, dict), f"固定样本 {expected_index} 不是对象")
        _require(sample.get("frame_id") == expected_index, f"固定样本 frame_id 顺序在 {expected_index} 处变化")
        sample_id = sample.get("sample_id")
        _require(isinstance(sample_id, str) and sample_id and sample_id not in observed_ids, f"固定样本 ID 非法或重复：{sample_id}")
        observed_ids.add(sample_id)
        source = sample.get("source")
        _require(source in expected_sources, f"固定样本来源未知：{source}")
        source_counts[source] += 1
        tags = sample.get("coverage_tags")
        _require(isinstance(tags, list) and all(isinstance(tag, str) for tag in tags), f"样本 {sample_id} coverage 标签非法")
        coverage_counts.update(tags)
        width = sample.get("width")
        height = sample.get("height")
        _require(type(width) is int and width > 0 and type(height) is int and height > 0, f"样本 {sample_id} 图像几何非法")
        input_sha = sample.get("pl_input_sha256")
        _require(isinstance(input_sha, str) and SHA256_RE.fullmatch(input_sha) is not None, f"样本 {sample_id} 输入 SHA 非法")

        ground_truth = _sample_ground_truth(sample)
        if source == "approved_train_negative_from_calibration_list":
            _require(not ground_truth and "empty_ground_truth" in tags and "no_hand_negative" in tags, f"获批 no_hand 样本 {sample_id} 标签或 coverage 异常")
            observed_empty_ids.append(sample_id)
        else:
            _require("empty_ground_truth" not in tags, f"非获批空标签样本 {sample_id} 错误带有 empty_ground_truth 标签")
        for box_index, row in enumerate(ground_truth):
            _require(isinstance(row, list) and len(row) == 5, f"样本 {sample_id} GT {box_index} 格式错误")
            class_id = row[0]
            _require(type(class_id) is int and 0 <= class_id < len(EXPECTED_CLASSES), f"样本 {sample_id} 含未知类别：{class_id}")
            observed_class_ids.add(class_id)
            _require(all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)) for value in row[1:]), f"样本 {sample_id} GT 数值非法")
            class_tag = f"class:{EXPECTED_CLASSES[class_id]}"
            _require(class_tag in tags, f"样本 {sample_id} GT class tag 与 class_id 不一致")

    _require(dict(source_counts) == expected_sources, f"固定样本来源计数变化：{dict(source_counts)}")
    _require(set(observed_empty_ids) == set(EMPTY_LABEL_SAMPLE_IDS), "三张获批空标签样本缺失、多出或次序数据异常")
    _require(coverage_counts["empty_ground_truth"] == 3, "固定 catalog 空 GT coverage 数不是 3")
    _require(coverage_counts["boundary_ground_truth_box"] == 1, "固定 catalog 边界框 coverage 数不是 1")
    _require(observed_class_ids == set(range(5)), "固定 catalog 未覆盖五类或含未知类")
    declared_five = set(catalog.get("coverage", {}).get("five_classes", []))
    expected_five = {f"class:{name}" for name in EXPECTED_CLASSES}
    _require(declared_five == expected_five, "固定 catalog 五类 coverage 声明与实际标签不一致")
    declared_full = catalog.get("coverage", {}).get("full_network_inputs", {})
    _require(declared_full.get("count") == EXPECTED_SAMPLE_COUNT, "固定 catalog full network 样本声明不为 109")
    _require(declared_full.get("approved_empty_label_samples") == 3, "固定 catalog 获批空标签声明不是 3")
    _require(declared_full.get("official_first_twenty_per_class") == 100, "固定 catalog 官方基础样本声明异常")
    _require(declared_full.get("official_additional_multi_ground_truth_samples") == 2, "固定 catalog 多 GT 样本声明异常")
    _require(declared_full.get("synthetic_extreme_samples") == 4, "固定 catalog 合成极值样本声明异常")
    return samples


def _validate_manifest(manifest: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    _require(manifest.get("status") == "G0_FROZEN", "tiny416 manifest 未处于 G0_FROZEN")
    _require(manifest.get("model", {}).get("model_id") == "tiny416", "模型不是 tiny416")
    _require(manifest.get("model", {}).get("input_wh") == [416, 416], "模型输入尺寸不是 416x416")
    _require(manifest.get("model", {}).get("classes") == 5, "模型类别数不是 5")
    layers = manifest.get("layers")
    _require(isinstance(layers, list) and len(layers) == 38, "manifest 层数不是 38")
    decoder = manifest.get("detection_postprocess", {})
    _require(decoder.get("decoder_reference") == "verification/s1_t02_d9_yolo_decode.py", "D9 reference 路径不符")
    _require(decoder.get("score_threshold") == 0.25, "冻结检测阈值不是 0.25")
    _require(decoder.get("nms_iou") == 0.45 and decoder.get("max_outputs") == 15, "冻结 NMS 参数不符")
    _require(decoder.get("class_order") == list(EXPECTED_CLASSES), "冻结类别顺序不符")
    _require(decoder.get("head_layout") == "Darknet entry planes; [anchor,entry,row,col], entry=x,y,w,h,obj,class0..class4", "冻结 head layout 不符")
    _require(decoder.get("score") == "sigmoid(objectness_logit)*sigmoid(class_logit)", "冻结 score 公式不符")
    _require(decoder.get("coordinate_policy") == "D2 integer-truncated resize and floor pad; clip finite positive raw xyxy to [0,1]; reject zero-area after clipping", "冻结坐标策略不符")
    _require(decoder.get("tie_order") == "head order, row-major cell, anchor-local order, class_id; stable input order for equal scores", "冻结同分顺序不符")
    heads = manifest.get("address_map", {}).get("heads")
    _require(isinstance(heads, list) and len(heads) == 2, "manifest head 列表不恰为两项")
    heads_by_name = {row.get("name"): row for row in heads if isinstance(row, dict)}
    _require(set(heads_by_name) == {"head13", "head26"}, "manifest head 名称集合不匹配")
    expected = {
        "head13": {"source_convolution_layer_index": 29, "yolo_layer_index": 30, "shape_nchw": [1, 30, 13, 13], "int8_scale": 0.24267549589862975, "length_bytes": 5070, "stride": 32},
        "head26": {"source_convolution_layer_index": 36, "yolo_layer_index": 37, "shape_nchw": [1, 30, 26, 26], "int8_scale": 0.30223452951025775, "length_bytes": 20280, "stride": 16},
    }
    for name, expected_fields in expected.items():
        head = heads_by_name[name]
        for key, expected_value in expected_fields.items():
            _require(head.get(key) == expected_value, f"{name} {key} 与 G0 冻结值不符")
        source_index = expected_fields["source_convolution_layer_index"]
        alias_index = expected_fields["yolo_layer_index"]
        source = layers[source_index]
        alias = layers[alias_index]
        _require(source.get("layer_index") == source_index and source.get("op") == "convolutional", f"{name} 来源不是冻结卷积层")
        _require(source.get("output_shape_nchw") == expected_fields["shape_nchw"], f"{name} 来源 shape 不匹配")
        _require(source.get("output_scale") == expected_fields["int8_scale"], f"{name} 来源 scale 不匹配")
        _require(source.get("tensor_length_bytes") == expected_fields["length_bytes"], f"{name} 来源长度不匹配")
        _require(source.get("tensor_address") == head.get("address"), f"{name} 来源地址与 manifest head 不匹配")
        _require(alias.get("layer_index") == alias_index and alias.get("op") == "yolo", f"{name} alias layer 不匹配")
        _require(alias.get("output_tensor_index") == source_index, f"{name} alias 未映射回来源卷积")
        _require(alias.get("output_shape_nchw") == expected_fields["shape_nchw"], f"{name} alias shape 不匹配")
        _require(alias.get("output_scale") == expected_fields["int8_scale"], f"{name} alias scale 不匹配")
    _require(d9.CLASS_NAMES == EXPECTED_CLASSES, "运行时 D9 类别名顺序与 G0 不符")
    _require(d9.NETWORK_WIDTH == 416 and d9.NETWORK_HEIGHT == 416, "运行时 D9 网络尺寸与 G0 不符")
    _require(d9.CLASS_COUNT == 5 and d9.SCALE_X_Y == 1.05, "运行时 D9 类别数或 scale_x_y 与 G0 不符")
    _require(d9.ANCHORS == ((10, 14), (23, 27), (37, 58), (81, 82), (135, 169), (344, 319)), "运行时 D9 anchors 与 G0 不符")
    _require([(spec.name, spec.grid_width, spec.grid_height, spec.anchor_mask) for spec in d9.HEAD_SPECS] == [("13x13", 13, 13, (3, 4, 5)), ("26x26", 26, 26, (1, 2, 3))], "运行时 D9 头尺寸或 anchor mask 与 G0 不符")
    return heads_by_name, decoder


def _validate_t25_source_bindings(root: Path, index: dict[str, Any]) -> None:
    for row in index.get("source_bindings", []):
        if not isinstance(row, dict) or not str(row.get("role", "")).startswith("repo:"):
            continue
        path_text = row.get("path")
        digest = row.get("sha256")
        _require(isinstance(path_text, str) and isinstance(digest, str), "T25 repo source binding 字段非法")
        actual = sha256_file(_repo_path(root, path_text))
        _require(actual == digest, f"T25 索引来源绑定与工作区文件不同：{path_text}")
    tooling = {row.get("role"): row for row in index.get("tooling_bindings", []) if isinstance(row, dict)}
    for role, path_text in (("t25_exporter", T25_EXPORTER_PATH), ("t25_test", T25_TEST_PATH)):
        row = tooling.get(role)
        _require(isinstance(row, dict) and row.get("path") == path_text, f"T25 {role} 路径缺失或改变")
        _require(sha256_file(_repo_path(root, path_text)) == row.get("sha256"), f"T25 {role} 哈希不匹配")


def _validate_t25_index(root: Path, index: dict[str, Any], catalog_samples: list[dict[str, Any]], manifest: dict[str, Any]) -> list[dict[str, Any]]:
    _require(index.get("schema_version") == "gestureforge_s2a_cpu_layer_golden_index_v2", "T25 索引 schema 不匹配")
    _require(index.get("task_id") == "S2A-T25" and index.get("status") == "COMPLETE", "T25 索引未完整完成")
    _require(index.get("model_id") == "tiny416", "T25 索引模型不是 tiny416")
    _require(index.get("fixed_sample_catalog", {}).get("total_samples") == EXPECTED_SAMPLE_COUNT, "T25 索引 total samples 不为 109")
    _require(index.get("fixed_sample_catalog", {}).get("completed_samples") == EXPECTED_SAMPLE_COUNT, "T25 索引未完成全部样本")
    _require(index.get("fixed_sample_catalog", {}).get("remaining_samples") == 0, "T25 索引仍有待处理样本")
    _require(index.get("fixed_sample_catalog", {}).get("path") == SAMPLE_CATALOG_PATH, "T25 sample catalog 路径不符")
    _require(index.get("fixed_sample_catalog", {}).get("sha256") == sha256_file(_repo_path(root, SAMPLE_CATALOG_PATH)), "T25 catalog hash 与当前 catalog 不符")
    _require(index.get("network", {}).get("layer_count") == 38, "T25 网络层数不是 38")
    _require(index.get("limitations", {}).get("cpu_per_layer_goldens") == "COMPLETE", "T25 未标记 CPU 逐层黄金完整")
    rows = index.get("samples")
    _require(isinstance(rows, list) and len(rows) == EXPECTED_SAMPLE_COUNT, "T25 sample 记录不为 109 项")
    expected_names = {f"sample_{i:03d}.zlib" for i in range(EXPECTED_SAMPLE_COUNT)}
    seen_names: set[str] = set()
    manifest_layers = manifest["layers"]
    for sample_index, (fixed, row) in enumerate(zip(catalog_samples, rows)):
        _require(row.get("sample_index") == sample_index and row.get("frame_id") == sample_index, f"T25 sample/frame 顺序在 {sample_index} 处改变")
        _require(row.get("sample_id") == fixed.get("sample_id"), f"T25 sample ID 顺序在 {sample_index} 处改变")
        _require(row.get("source") == fixed.get("source"), f"T25 sample source 与 catalog 不匹配：{sample_index}")
        _require(row.get("coverage_tags") == fixed.get("coverage_tags"), f"T25 sample coverage 与 catalog 不匹配：{sample_index}")
        _require(row.get("ground_truth_yolo", []) == fixed.get("ground_truth_yolo", []), f"T25 GT 与 catalog 不匹配：{sample_index}")
        _require(row.get("preprocessed_input", {}).get("sha256") == fixed.get("pl_input_sha256"), f"T25 输入张量绑定与 catalog 不匹配：{sample_index}")
        original = row.get("original_input", {})
        _require(original.get("width") == fixed.get("width") and original.get("height") == fixed.get("height"), f"T25 D9 几何与 catalog 不匹配：{sample_index}")

        network = row.get("network", {})
        tensor_rows = network.get("tensors")
        _require(isinstance(tensor_rows, list) and len(tensor_rows) == 38, f"T25 sample {sample_index} tensor 表长度不为 38")
        shard = network.get("compressed_shard", {})
        shard_name = f"sample_{sample_index:03d}.zlib"
        _require(shard.get("path") == f"report/evidence/S2A-T25/tensors/{shard_name}", f"T25 sample {sample_index} shard 路径或顺序改变")
        _require(shard.get("compression_level") == 9, f"T25 sample {sample_index} 压缩级别不符")
        _require(shard.get("compressed_bytes", 0) > 0, f"T25 sample {sample_index} 压缩长度为空")
        seen_names.add(shard_name)

        cursor = 0
        by_index: dict[int, dict[str, Any]] = {}
        for layer_index, (tensor, contract) in enumerate(zip(tensor_rows, manifest_layers)):
            _require(tensor.get("layer_index") == layer_index and contract.get("layer_index") == layer_index, f"T25 sample {sample_index} layer 顺序错误")
            _require(tensor.get("cfg_section") == contract.get("cfg_section"), f"T25 sample {sample_index} layer {layer_index} cfg section 不符")
            _require(tensor.get("op") == contract.get("op"), f"T25 sample {sample_index} layer {layer_index} op 不符")
            _require(tensor.get("shape_nchw") == contract.get("output_shape_nchw"), f"T25 sample {sample_index} layer {layer_index} layout/shape 不符")
            _require(tensor.get("scale") == contract.get("output_scale"), f"T25 sample {sample_index} layer {layer_index} scale 不符")
            _require(tensor.get("element_type") == "int8_twos_complement", f"T25 sample {sample_index} layer {layer_index} element type 不符")
            _require(tensor.get("byte_length") == contract.get("tensor_length_bytes"), f"T25 sample {sample_index} layer {layer_index} byte length 不符")
            _require(isinstance(tensor.get("tensor_sha256"), str) and SHA256_RE.fullmatch(tensor["tensor_sha256"]) is not None, f"T25 sample {sample_index} layer {layer_index} tensor SHA 格式错误")
            offset = tensor.get("byte_offset")
            length = tensor.get("byte_length")
            _require(type(offset) is int and type(length) is int and length == math.prod(tensor["shape_nchw"]), f"T25 sample {sample_index} layer {layer_index} 元素长度与 shape 不符")
            if contract.get("op") == "yolo":
                source_index = contract.get("output_tensor_index")
                _require(tensor.get("stored") is False and tensor.get("alias_of_layer_index") == source_index, f"T25 sample {sample_index} layer {layer_index} YOLO alias 错误")
                source = by_index.get(source_index)
                _require(source is not None and source.get("stored") is True, f"T25 sample {sample_index} layer {layer_index} alias source 缺失")
                _require(offset == source.get("byte_offset") and length == source.get("byte_length") and tensor.get("tensor_sha256") == source.get("tensor_sha256"), f"T25 sample {sample_index} layer {layer_index} alias 描述不一致")
            else:
                _require(tensor.get("stored") is True and tensor.get("alias_of_layer_index") is None, f"T25 sample {sample_index} layer {layer_index} owned tensor 存储标记不符")
                _require(offset == cursor, f"T25 sample {sample_index} layer {layer_index} raw stream offset 不连续")
                cursor += length
            by_index[layer_index] = tensor
        _require(cursor == network.get("unique_output_raw_bytes") == shard.get("decompressed_bytes"), f"T25 sample {sample_index} raw stream 总长度不匹配")
        _require(network.get("raw_stream_sha256") == shard.get("decompressed_sha256"), f"T25 sample {sample_index} raw stream SHA 声明不匹配")
        _require(shard.get("sha256") and SHA256_RE.fullmatch(shard["sha256"]) is not None, f"T25 sample {sample_index} 压缩 SHA 格式错误")
        _require(shard.get("decompressed_sha256") and SHA256_RE.fullmatch(shard["decompressed_sha256"]) is not None, f"T25 sample {sample_index} 解压 SHA 格式错误")
    _require(seen_names == expected_names, "T25 索引 shard 名称集不完整")
    return rows


def _head_bytes(raw: bytes, tensor_rows: list[dict[str, Any]], head: dict[str, Any], name: str) -> tuple[bytes, dict[str, Any]]:
    layer_index = head["source_convolution_layer_index"]
    alias_index = head["yolo_layer_index"]
    tensor = tensor_rows[layer_index]
    alias = tensor_rows[alias_index]
    _require(tensor.get("stored") is True, f"{name} source convolution 未存储")
    _require(alias.get("stored") is False and alias.get("alias_of_layer_index") == layer_index, f"{name} T25 YOLO alias 不匹配")
    offset = tensor["byte_offset"]
    length = tensor["byte_length"]
    payload = raw[offset : offset + length]
    _require(len(payload) == length == head["length_bytes"], f"{name} head bytes 长度不符")
    digest = sha256_bytes(payload)
    _require(digest == tensor["tensor_sha256"] == alias["tensor_sha256"], f"{name} head tensor SHA-256 不匹配")
    _require(tensor["shape_nchw"] == head["shape_nchw"] and tensor["scale"] == head["int8_scale"], f"{name} head shape/scale 不匹配")
    binding = {
        "name": name,
        "source_convolution_layer_index": layer_index,
        "yolo_alias_layer_index": alias_index,
        "shape_nchw": tensor["shape_nchw"],
        "layout": "contiguous NCHW INT8; view [anchor=3,entry=10,row,col]",
        "int8_scale": tensor["scale"],
        "byte_offset": offset,
        "byte_length": length,
        "tensor_sha256": digest,
    }
    return payload, binding


def decode_and_count_candidates(
    head_logits: dict[str, np.ndarray], sample_id: str, width: int, height: int, threshold: float
) -> tuple[list[Any], int]:
    """调用冻结 D9 API，并在其 NMS 入口记录合格候选数。"""

    candidates_seen: list[int] = []
    original_nms = d9.stable_nms

    def observing_nms(predictions: Any, *args: Any, **kwargs: Any) -> list[Any]:
        values = list(predictions)
        candidates_seen.append(len(values))
        return original_nms(values, *args, **kwargs)

    d9.stable_nms = observing_nms
    try:
        predictions = d9.decode_yolov4_tiny416(
            head_logits,
            image_key=sample_id,
            image_width=width,
            image_height=height,
            score_threshold=threshold,
        )
    finally:
        d9.stable_nms = original_nms
    _require(len(candidates_seen) == 1, "D9 解码未恰好调用一次冻结 stable_nms")
    return predictions, candidates_seen[0]


def _validate_predictions(predictions: list[Any], sample_id: str, raw_candidate_count: int, max_outputs: int) -> None:
    _require(0 <= len(predictions) <= max_outputs, f"样本 {sample_id} NMS 输出数超过冻结上限")
    _require(raw_candidate_count >= len(predictions), f"样本 {sample_id} NMS 输出数多于原始候选")
    previous_score = math.inf
    previous_order: int | None = None
    previous_tie_score: float | None = None
    for prediction in predictions:
        _require(prediction.image_key == sample_id, f"样本 {sample_id} D9 image_key 不一致")
        _require(type(prediction.class_id) is int and 0 <= prediction.class_id < len(EXPECTED_CLASSES), f"样本 {sample_id} D9 输出未知类别")
        _require(prediction.name == EXPECTED_CLASSES[prediction.class_id], f"样本 {sample_id} D9 类别名不匹配")
        _require(math.isfinite(float(prediction.confidence)) and prediction.confidence >= 0.25, f"样本 {sample_id} D9 score 非法或低于阈值")
        _require(type(prediction.source_order) is int and prediction.source_order >= 0, f"样本 {sample_id} source_order 非法")
        _require(prediction.confidence <= previous_score, f"样本 {sample_id} D9 输出没有按 score 稳定降序")
        if previous_tie_score == prediction.confidence:
            _require(previous_order is not None and prediction.source_order > previous_order, f"样本 {sample_id} D9 同分 source_order 顺序错误")
        previous_score = prediction.confidence
        previous_tie_score = prediction.confidence
        previous_order = prediction.source_order
        _require(len(prediction.box) == 4, f"样本 {sample_id} D9 xyxy 长度不是 4")
        _require(all(math.isfinite(float(value)) and 0.0 <= value <= 1.0 for value in prediction.box), f"样本 {sample_id} D9 坐标非有限或超出 [0,1]")
        _require(prediction.box[2] > prediction.box[0] and prediction.box[3] > prediction.box[1], f"样本 {sample_id} D9 输出框面积不为正")


def _prediction_json(prediction: Any) -> dict[str, Any]:
    return {
        "class_id": prediction.class_id,
        "class_name": prediction.name,
        "score": float(prediction.confidence),
        "xyxy": [float(value) for value in prediction.box],
        "source_order": prediction.source_order,
    }


def _frozen_fixture_metadata(frozen_fixture: dict[str, Any]) -> dict[str, Any]:
    """只记录 G0 冻结 fixture 元数据，不读取其当前工作区文件。"""

    expected_path = "verification/test_s1_t02_d9_yolo_decode.py"
    _require(frozen_fixture.get("path", "").replace("\\", "/") == expected_path, "冻结 D9 fixture 路径不符")
    frozen_sha = frozen_fixture.get("sha256")
    source_commit = frozen_fixture.get("source_commit")
    _require(isinstance(frozen_sha, str) and SHA256_RE.fullmatch(frozen_sha) is not None, "冻结 D9 fixture SHA 格式错误")
    _require(isinstance(source_commit, str) and GIT_COMMIT_RE.fullmatch(source_commit) is not None, "冻结 D9 fixture 来源提交格式错误")
    return {
        "role": "s1_d9_fixture_reference",
        "path": expected_path,
        "frozen_sha256": frozen_sha,
        "frozen_source_commit": source_commit,
        "used_by_t29": False,
    }


def _load_bindings(root: Path, manifest: dict[str, Any], catalog: dict[str, Any], index: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    bindings = manifest["bindings"]
    d9_binding = bindings.get("d9_decoder_reference", {})
    d2_binding = bindings.get("d2_numeric_reference", {})
    d6_binding = bindings.get("d6_metrics_reference", {})
    _require(d9_binding.get("path", "").replace("\\", "/") == "verification/s1_t02_d9_yolo_decode.py", "manifest D9 文件路径错误")
    _require(d2_binding.get("path", "").replace("\\", "/") == "verification/s1_t02_d2_numeric_reference.py", "manifest D2 文件路径错误")
    _require(d6_binding.get("path", "").replace("\\", "/") == "verification/s1_t02_d6_detection_metrics.py", "manifest D6 文件路径错误")

    evidence_path = "report/evidence/S1-T02/20260917_s1_t02_d9_yolo_decode_r1.json"
    final_freeze_path = "docs/obsidian-project/04-提交材料/阶段验收/阶段1_PC范围冻结补充_20260922.md"
    docs = [
        ("project_rules", "AGENTS.md"),
        ("s2a_g0_specification", G0_SPEC_PATH),
        ("s2a_model_manifest", MODEL_MANIFEST_PATH),
        ("s2a_fixed_sample_catalog", SAMPLE_CATALOG_PATH),
        ("s1_final_freeze_record", final_freeze_path),
        ("s1_d2_specification", "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D2_固定预处理与INT8数值规格.md"),
        ("s1_d3_specification", "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D3_资源性能与阶段验收门槛.md"),
        ("s1_d6_specification", "docs/obsidian-project/04-提交材料/阶段验收/S1-T02-D6_检测评估口径与离线指标基础.md"),
        ("s1_d2_numeric_reference", d2_binding["path"].replace("\\", "/")),
        ("s1_d6_metrics_reference", d6_binding["path"].replace("\\", "/")),
        ("s1_d9_decoder", d9_binding["path"].replace("\\", "/")),
        ("s1_d9_evidence", evidence_path),
        ("t25_exporter", T25_EXPORTER_PATH),
        ("t25_test", T25_TEST_PATH),
        ("t25_index", T25_INDEX_PATH),
        ("t29_generator", "verification/s2a_decode_nms_reference.py"),
        ("t29_test", "verification/test_s2a_decode_nms_reference.py"),
    ]
    result: list[dict[str, Any]] = []
    for role, relative_path in docs:
        expected: str | None = None
        if role == "s2a_model_manifest":
            expected = "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"
        elif role == "s2a_fixed_sample_catalog":
            expected = "ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed"
        elif role == "s1_d2_numeric_reference":
            expected = d2_binding.get("sha256")
        elif role == "s1_d6_metrics_reference":
            expected = d6_binding.get("sha256")
        elif role == "s1_d9_decoder":
            expected = d9_binding.get("sha256")
        elif role in ("t25_exporter", "t25_test"):
            expected = next(row.get("sha256") for row in index["tooling_bindings"] if row.get("role") == role)
        result.append(_repo_binding(root, role, relative_path, expected))

    frozen_fixture = bindings.get("d9_fixture_source", {})
    result.append(_frozen_fixture_metadata(frozen_fixture))
    versions = {"python": sys.version.split()[0], "numpy": np.__version__, "opencv": cv2.__version__, "zlib_compile": zlib.ZLIB_VERSION, "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION}
    return result, versions


def _validate_sample_pair(fixed: dict[str, Any], t25: dict[str, Any], sample_index: int) -> None:
    _require(t25.get("sample_index") == sample_index, f"T25 sample_index 在 {sample_index} 处改变")
    _require(t25.get("frame_id") == fixed.get("frame_id") == sample_index, f"sample/frame 顺序在 {sample_index} 处改变")
    for field in ("sample_id", "source", "coverage_tags"):
        _require(t25.get(field) == fixed.get(field), f"T25 与固定 catalog 的 {field} 不匹配：{sample_index}")
    _require(t25.get("ground_truth_yolo", []) == _sample_ground_truth(fixed), f"T25 与固定 catalog GT 不匹配：{sample_index}")


def generate_evidence(root: Path, progress: Callable[[str], None] | None = None, preflight_only: bool = False) -> dict[str, Any]:
    """验证冻结输入并依序生成 109 个 D9 CPU 参考摘要。"""

    root = root.resolve()
    _require(root.is_dir(), "仓库根目录不存在")
    runtime_head_before = current_git_head(root)
    runtime_head_relation = classify_runtime_head(
        BASELINE_HEAD,
        runtime_head_before,
        lambda ancestor, descendant: _git_is_ancestor(root, ancestor, descendant),
    )

    for exact_path in ("report/evidence", "report/evidence/S2A-T25/tensors"):
        path = _repo_path(root, exact_path)
        _require(path.is_dir() and not path.is_symlink(), f"必需目录缺失或类型错误：{exact_path}")
    out_dir = _repo_path(root, "report/evidence/S2A-T29")
    _require(not out_dir.exists() or (out_dir.is_dir() and not out_dir.is_symlink()), "T29 evidence 目标父目录类型不正确")

    g0_path = _repo_path(root, G0_SPEC_PATH)
    manifest_path = _repo_path(root, MODEL_MANIFEST_PATH)
    catalog_path = _repo_path(root, SAMPLE_CATALOG_PATH)
    index_path = _repo_path(root, T25_INDEX_PATH)
    manifest = _read_json(manifest_path, "S2A-T01 manifest")
    catalog = _read_json(catalog_path, "S2A-T01 fixed sample catalog")
    index = _read_json(index_path, "S2A-T25 golden index")

    _require(sha256_file(g0_path) == "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230", "G0 冻结规格 SHA-256 不符")
    _require(sha256_file(manifest_path) == "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a", "S2A-T01 manifest SHA-256 不符")
    _require(sha256_file(catalog_path) == "ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed", "S2A-T01 sample catalog SHA-256 不符")
    catalog_samples = _validate_catalog(catalog)
    head_specs, decoder_config = _validate_manifest(manifest)

    expected_d9 = manifest["bindings"]["d9_decoder_reference"]["sha256"]
    _require(sha256_file(_repo_path(root, "verification/s1_t02_d9_yolo_decode.py")) == expected_d9, "D9 解码器 SHA-256 与 G0 不符")
    _validate_t25_source_bindings(root, index)
    t25_samples = _validate_t25_index(root, index, catalog_samples, manifest)

    shard_dir = _repo_path(root, "report/evidence/S2A-T25/tensors")
    expected_names = {f"sample_{i:03d}.zlib" for i in range(EXPECTED_SAMPLE_COUNT)}
    entries = list(shard_dir.iterdir())
    _require(all(item.is_file() and not item.is_symlink() for item in entries), "T25 shard 目录含非普通文件项")
    validate_exact_shard_names(expected_names, {item.name for item in entries})

    source_bindings, runtime = _load_bindings(root, manifest, catalog, index)
    if preflight_only:
        _require(current_git_head(root) == runtime_head_before, "T29 前置检查期间 Git HEAD 发生变化")
        return {
            "preflight": "PASS",
            "baseline_git_head": BASELINE_HEAD,
            "runtime_git_head": runtime_head_before,
            "runtime_head_relation": runtime_head_relation,
            "fixed_samples": len(catalog_samples),
            "indexed_shards": len(t25_samples),
            "runtime": runtime,
            "source_binding_count": len(source_bindings),
        }
    samples_out: list[dict[str, Any]] = []
    shard_bindings: list[dict[str, Any]] = []
    source_counts: Counter[str] = Counter()
    tag_counts: Counter[str] = Counter()
    gt_class_counts: Counter[str] = Counter()
    predicted_class_counts: Counter[str] = Counter()
    empty_gt_results: list[dict[str, Any]] = []
    approved_empty_gt_results: list[dict[str, Any]] = []
    empty_prediction_samples = 0
    multi_gt_samples = 0
    multi_prediction_samples = 0
    boundary_samples = 0
    boundary_prediction_count = 0
    extreme_samples = 0
    total_candidates = 0
    total_predictions = 0

    for sample_index, (fixed, t25) in enumerate(zip(catalog_samples, t25_samples)):
        _validate_sample_pair(fixed, t25, sample_index)
        shard = t25["network"]["compressed_shard"]
        shard_path = shard_dir / f"sample_{sample_index:03d}.zlib"
        _require(shard_path.is_file() and not shard_path.is_symlink(), f"T25 shard 缺失或类型错误：sample {sample_index}")
        compressed = shard_path.read_bytes()
        raw = verify_zlib_shard(compressed, shard, t25["network"])

        head13_bytes, head13_binding = _head_bytes(raw, t25["network"]["tensors"], head_specs["head13"], "head13")
        head26_bytes, head26_binding = _head_bytes(raw, t25["network"]["tensors"], head_specs["head26"], "head26")
        head13_int8 = np.frombuffer(head13_bytes, dtype=np.int8).reshape((1, 30, 13, 13))[0].reshape((3, 10, 13, 13))
        head26_int8 = np.frombuffer(head26_bytes, dtype=np.int8).reshape((1, 30, 26, 26))[0].reshape((3, 10, 26, 26))
        head_logits = {
            "13x13": head13_int8.astype(np.float64) * np.float64(head13_binding["int8_scale"]),
            "26x26": head26_int8.astype(np.float64) * np.float64(head26_binding["int8_scale"]),
        }
        width = fixed["width"]
        height = fixed["height"]
        candidates, raw_candidate_count = decode_and_count_candidates(
            head_logits,
            fixed["sample_id"],
            width,
            height,
            decoder_config["score_threshold"],
        )
        _validate_predictions(candidates, fixed["sample_id"], raw_candidate_count, decoder_config["max_outputs"])
        detection_rows = [_prediction_json(item) for item in candidates]
        gt_rows = _sample_ground_truth(fixed)
        gt_count = len(gt_rows)
        if gt_count == 0:
            empty_gt_results.append({"sample_id": fixed["sample_id"], "detection_count": len(detection_rows)})
        if "empty_ground_truth" in fixed["coverage_tags"]:
            _require(gt_count == 0, f"获批空标签样本 {fixed['sample_id']} 意外包含 GT")
            approved_empty_gt_results.append({"sample_id": fixed["sample_id"], "detection_count": len(detection_rows)})
        if gt_count >= 2:
            multi_gt_samples += 1
        if len(detection_rows) == 0:
            empty_prediction_samples += 1
        if len(detection_rows) >= 2:
            multi_prediction_samples += 1
        if "boundary_ground_truth_box" in fixed["coverage_tags"]:
            boundary_samples += 1
        for gt in gt_rows:
            gt_class_counts[EXPECTED_CLASSES[gt[0]]] += 1
        edge_count = sum(1 for item in candidates if any(value in (0.0, 1.0) for value in item.box))
        boundary_prediction_count += edge_count
        for item in candidates:
            predicted_class_counts[item.name] += 1
        source_counts[fixed["source"]] += 1
        tag_counts.update(fixed["coverage_tags"])
        if fixed["source"] == "synthetic_rgb416":
            extreme_samples += 1

        samples_out.append(
            {
                "frame_id": sample_index,
                "sample_id": fixed["sample_id"],
                "data_source": fixed["source"],
                "coverage_tags": fixed["coverage_tags"],
                "input": {
                    "pl_input_sha256": fixed["pl_input_sha256"],
                    "geometry_wh": [width, height],
                },
                "head_tensors": {"head13": head13_binding, "head26": head26_binding},
                "ground_truth_box_count": gt_count,
                "raw_candidate_count_before_stable_nms": raw_candidate_count,
                "nms_output_box_count": len(detection_rows),
                "detections": detection_rows,
                "boundary_coordinate_box_count": edge_count,
            }
        )
        shard_bindings.append(
            {
                "sample_index": sample_index,
                "sample_id": fixed["sample_id"],
                "path": shard["path"],
                "compressed_bytes": len(compressed),
                "compressed_sha256": sha256_bytes(compressed),
                "decompressed_bytes": len(raw),
                "decompressed_sha256": sha256_bytes(raw),
            }
        )
        total_candidates += raw_candidate_count
        total_predictions += len(detection_rows)
        if progress is not None:
            progress(f"sample={sample_index + 1}/{EXPECTED_SAMPLE_COUNT} id={fixed['sample_id']} candidates={raw_candidate_count} nms={len(detection_rows)}")

    declared_empty = set(EMPTY_LABEL_SAMPLE_IDS)
    observed_empty = {row["sample_id"] for row in approved_empty_gt_results}
    _require(observed_empty == declared_empty and len(approved_empty_gt_results) == 3, "T29 输出未保留全部三张获批空标签样本")
    _require(dict(source_counts) == {"official_hagrid_test": 100, "official_hagrid_test_multibox": 2, "approved_train_negative_from_calibration_list": 3, "synthetic_rgb416": 4}, "T29 输出来源计数与 catalog 不一致")
    _require(tag_counts["empty_ground_truth"] == 3 and boundary_samples == 1, "T29 空标签或边界 coverage 实际计数不一致")
    _require(extreme_samples == 4, "T29 合成极值样本数不为 4")
    _require(len(samples_out) == EXPECTED_SAMPLE_COUNT and len(shard_bindings) == EXPECTED_SAMPLE_COUNT, "T29 输出样本或 shard 数不是 109")
    _require(current_git_head(root) == runtime_head_before, "T29 处理期间 Git HEAD 发生变化")

    return {
        "schema_version": "gestureforge_s2a_t29_cpu_decode_nms_reference_v1",
        "task_id": "S2A-T29",
        "status": "CPU_REFERENCE_GENERATED",
        "baseline_git_head": BASELINE_HEAD,
        "runtime_git_head": {
            "observed": runtime_head_before,
            "relation_to_baseline": runtime_head_relation,
            "checked_stable_during_run": True,
        },
        "canonicalization": {
            "runtime_git_head_fields_excluded_from_canonical_digest": ["observed", "relation_to_baseline"],
            "frozen_baseline_field_included": True,
        },
        "scope": {
            "model_id": "tiny416",
            "fixed_sample_count": EXPECTED_SAMPLE_COUNT,
            "reference_only": True,
            "rtl_head_tensor_comparison": "NOT_EXECUTED",
            "rtl_simulation": "NOT_EXECUTED",
            "synthesis": "NOT_EXECUTED",
            "G4": "NOT_MET",
            "G5": "NOT_MET",
            "original_images_read": False,
            "original_images_written": False,
            "large_tensor_shards_written": False,
            "full_tensor_payload_embedded": False,
        },
        "source_bindings": source_bindings,
        "t25_index_binding": {
            "path": T25_INDEX_PATH,
            "sha256": sha256_file(_repo_path(root, T25_INDEX_PATH)),
            "status": index["status"],
            "completed_samples": index["fixed_sample_catalog"]["completed_samples"],
            "layer_count": index["network"]["layer_count"],
        },
        "runtime": runtime,
        "decoder": {
            "api": "decode_yolov4_tiny416",
            "path": "verification/s1_t02_d9_yolo_decode.py",
            "dequantization": "signed int8 value × corresponding G0 head int8_scale in float64",
            "input_layout": decoder_config["head_layout"],
            "score": decoder_config["score"],
            "score_threshold": decoder_config["score_threshold"],
            "nms_iou": decoder_config["nms_iou"],
            "max_outputs": decoder_config["max_outputs"],
            "nms": decoder_config["nms"],
            "coordinate_policy": decoder_config["coordinate_policy"],
            "class_order": decoder_config["class_order"],
            "tie_order": decoder_config["tie_order"],
            "heads": [
                {key: head_specs[name][key] for key in ("name", "source_convolution_layer_index", "yolo_layer_index", "stride", "shape_nchw", "int8_scale", "address", "length_bytes", "layout_view")}
                for name in ("head13", "head26")
            ],
        },
        "coverage": {
            "sample_sources": dict(sorted(source_counts.items())),
            "coverage_tags": dict(sorted(tag_counts.items())),
            "ground_truth_class_box_counts": dict(sorted(gt_class_counts.items())),
            "predicted_class_box_counts_after_nms": dict(sorted(predicted_class_counts.items())),
            "ground_truth_box_total": sum(len(_sample_ground_truth(row)) for row in catalog_samples),
            "approved_empty_label_sample_count": len(approved_empty_gt_results),
            "approved_empty_label_samples_and_prediction_counts": approved_empty_gt_results,
            "catalog_samples_without_ground_truth_entries": len(empty_gt_results),
            "empty_prediction_sample_count": empty_prediction_samples,
            "multi_ground_truth_sample_count": multi_gt_samples,
            "multi_prediction_sample_count": multi_prediction_samples,
            "boundary_ground_truth_sample_count": boundary_samples,
            "post_nms_boxes_touching_normalized_edge_count": boundary_prediction_count,
            "synthetic_extreme_sample_count": extreme_samples,
            "total_raw_candidates_before_nms": total_candidates,
            "total_nms_output_boxes": total_predictions,
        },
        "shard_bindings": shard_bindings,
        "samples": samples_out,
        "limitations": [
            "本证据是 T25 CPU 逐层黄金检测头的 D9 CPU 解码/NMS 参考输出，不含 RTL 检测头逐字节比较。",
            "预测框计数和类别分布不表示模型召回率、分类正确率、mAP 或阶段 2A 通过。",
            "T25 shard 在内存中按索引偏移抽取 head13/head26；其他层张量仅由完整 raw stream SHA-256 绑定，未输出到本证据。",
        ],
    }


def _canonical_json(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _canonical_evidence_bytes(value: dict[str, Any]) -> bytes:
    """序列化可重放证据；运行时 HEAD 观察值不参与稳定摘要。"""

    canonical = dict(value)
    runtime_head = dict(value.get("runtime_git_head", {}))
    runtime_head["observed"] = "RUNTIME_HEAD_OBSERVATION_EXCLUDED"
    runtime_head["relation_to_baseline"] = "RUNTIME_HEAD_RELATION_EXCLUDED"
    canonical["runtime_git_head"] = runtime_head
    return _canonical_json(canonical)


def _default_output(root: Path) -> Path:
    return _repo_path(root, OUTPUT_RELATIVE_PATH)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="生成或确定性复核 tiny416 冻结 D9 CPU 解码/NMS 参考。")
    parser.add_argument("--verify-against", action="store_true", help="完整重跑 109 样本并比较 canonical evidence（保留冻结 baseline，规范化运行 HEAD 观察字段）")
    parser.add_argument("--preflight-only", action="store_true", help="只校验冻结文档、索引、源绑定和 shard 名称，不读取 shard 内容")
    parser.add_argument("--refresh-evidence", action="store_true", help="按当前冻结源码重建 T29 evidence 文件")
    parser.add_argument("--progress-log", type=Path, help="将逐样本进度写入仓库外的临时日志")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    output = _default_output(root)
    progress_stream = None
    try:
        _require(sum((args.preflight_only, args.verify_against, args.refresh_evidence)) <= 1, "preflight、复核与证据重建模式互斥")
        if args.progress_log is not None:
            args.progress_log.parent.mkdir(parents=True, exist_ok=True)
            progress_stream = args.progress_log.open("w", encoding="utf-8", newline="\n")

        def report_progress(line: str) -> None:
            if progress_stream is not None:
                progress_stream.write(line + "\n")
                progress_stream.flush()
            print(line, flush=True)

        evidence = generate_evidence(root, report_progress, preflight_only=args.preflight_only)
        if args.preflight_only:
            print(f"T29_PREFLIGHT_PASS samples={evidence['fixed_samples']} shards={evidence['indexed_shards']} baseline={evidence['baseline_git_head']} runtime={evidence['runtime_git_head']} relation={evidence['runtime_head_relation']} bindings={evidence['source_binding_count']}")
            return 0
        rendered = _canonical_json(evidence)
        canonical_digest = sha256_bytes(_canonical_evidence_bytes(evidence))
        if args.verify_against:
            _require(output.is_file(), f"确定性复核目标证据缺失：{OUTPUT_RELATIVE_PATH}")
            existing_bytes = output.read_bytes()
            try:
                existing = json.loads(existing_bytes.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise ReferenceError("既有 T29 证据不是有效 UTF-8 JSON") from exc
            _require(isinstance(existing, dict) and existing.get("baseline_git_head") == BASELINE_HEAD, "既有证据冻结基线不匹配")
            _require(_canonical_evidence_bytes(existing) == _canonical_evidence_bytes(evidence), "109 样本确定性复跑 canonical evidence 不一致")
            print(f"T29_VERIFY_PASS samples={EXPECTED_SAMPLE_COUNT} canonical_sha256={canonical_digest} stored_evidence_sha256={sha256_bytes(existing_bytes)} runtime_head={evidence['runtime_git_head']['observed']}")
        else:
            _require(args.refresh_evidence or not output.exists(), f"拒绝覆盖已有证据：{OUTPUT_RELATIVE_PATH}")
            output.parent.mkdir(parents=True, exist_ok=True)
            _require(output.parent.is_dir() and not output.parent.is_symlink(), "T29 证据父目录创建后类型异常")
            output.write_bytes(rendered)
            print(f"T29_WRITE_PASS samples={EXPECTED_SAMPLE_COUNT} evidence={OUTPUT_RELATIVE_PATH} evidence_sha256={sha256_bytes(rendered)} canonical_sha256={canonical_digest} runtime_head={evidence['runtime_git_head']['observed']}")
        return 0
    except (ReferenceError, OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        print(f"T29_ERROR: {exc}", file=sys.stderr)
        return 2
    finally:
        if progress_stream is not None:
            progress_stream.close()


if __name__ == "__main__":
    raise SystemExit(main())
