"""S2A-T24：按冻结 D2 参考生成 CPU 逐层整数张量 pilot。"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import sys
import time
import zlib
from pathlib import Path
from typing import Any

import numpy as np


G0_PATH = "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
MANIFEST_PATH = "report/evidence/S2A-T01/tiny416_model_manifest.json"
SAMPLES_PATH = "report/evidence/S2A-T01/fixed_test_samples.json"
D2_NUMERIC_PATH = "verification/s1_t02_d2_numeric_reference.py"
D2_FORWARD_PATH = "verification/s1_t02_d2_int8_forward.py"
D2_WEIGHT_REFERENCE_PATH = "verification/s1_t02_d2_int8_weight_reference.py"
MODEL_GENERATOR_PATH = "verification/s2a_model_delivery.py"
T22_PATH = "report/evidence/S2A-T22/network_dispatch_contract_validation.json"
T23_EXPORTER_PATH = "verification/s2a_conv_requant_table.py"
T23_TEST_PATH = "verification/test_s2a_conv_requant_table.py"
T23_TABLE_PATH = "report/evidence/S2A-T23/conv_requant_parameter_table.json"
T24_EXPORTER_PATH = "verification/s2a_cpu_layer_goldens.py"
T24_TEST_PATH = "verification/test_s2a_cpu_layer_goldens.py"

PINNED_SHA256 = {
    G0_PATH: "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    MANIFEST_PATH: "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    SAMPLES_PATH: "ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed",
    D2_NUMERIC_PATH: "ea48281fa1c1ba14006f6131ff377c7e4523da8c7e4977b0949d454a7c9ded90",
    D2_FORWARD_PATH: "5dfdbb4a9e57256b362629a2de40b9724df6d28ae225ce6d6622429b9cbad393",
    D2_WEIGHT_REFERENCE_PATH: "c7e6c5282c7b9c24bc6cc82b9d84f7578d6d6d45670cd23a6425cc52382dc196",
    MODEL_GENERATOR_PATH: "4831fff0e8ebb189ac9767ae423ad8d5268fc5bee5e333cc2a132112ccfdaab8",
    T22_PATH: "611d47cc85bd254474c5412fcab2f8acce3a263138787588f2a6445eac61d9a8",
    T23_EXPORTER_PATH: "aa45f5e4ef88c00ac83ce92684449c79d4060c39d3bf5dec2942e355330b86f8",
    T23_TEST_PATH: "2cc8d2fd4387372eeccee4b823d0ed215a87ffa5a407df9ea761e6463e382985",
    T23_TABLE_PATH: "396dc66aa3ccc41050cc8183bff16b86143a6f5553cf38fed16b0ba8b4eb4ae1",
}

EXPECTED_LAYER_COUNT = 38
EXPECTED_SAMPLE_COUNT = 109
EXPECTED_CHANNELS = 3
EXPECTED_WIDTH = 416
EXPECTED_HEIGHT = 416
EXPECTED_UNIQUE_OUTPUT_BYTES = 11_382_150
EXPECTED_SEED = 20260922


class GoldenExportError(ValueError):
    """表示冻结来源、样本输入或逐层整数输出未通过验证。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GoldenExportError(message)


def sha256_bytes(payload: bytes) -> str:
    """计算原始字节的 SHA-256。"""
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    """以分块方式计算文件 SHA-256。"""
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise GoldenExportError(f"无法读取文件 {path.name}: {exc}") from exc
    return digest.hexdigest()


def verify_digest(payload: bytes, expected_sha256: str, field: str) -> str:
    """校验字节流摘要并返回实际 SHA-256。"""
    actual = sha256_bytes(payload)
    _require(actual == expected_sha256, f"{field} SHA-256 不匹配: {actual} != {expected_sha256}")
    return actual


def _repo_file(root: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    _require(not candidate.is_absolute(), f"仓库来源路径必须为相对路径: {relative_path}")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise GoldenExportError(f"仓库来源路径越界: {relative_path}") from exc
    _require(resolved.is_file(), f"仓库来源文件不存在: {relative_path}")
    return resolved


def _read_json(path: Path, field: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GoldenExportError(f"{field} 读取失败: {exc}") from exc
    _require(isinstance(value, dict), f"{field} 根节点必须为 object")
    return value


def validate_source_bindings(
    actual: list[dict[str, str]], expected: list[dict[str, str]]
) -> None:
    """拒绝来源缺失、重复、改路径或改摘要。"""
    def normalized(rows: list[dict[str, str]]) -> list[tuple[str, str, str]]:
        result = []
        for row in rows:
            _require(isinstance(row, dict), "来源绑定记录必须为 object")
            role = str(row.get("role", ""))
            path = str(row.get("path", ""))
            digest = str(row.get("sha256", ""))
            _require(role and path, "来源绑定缺少 role/path")
            _require(len(digest) == 64 and digest == digest.lower(), f"来源摘要格式无效: {role}")
            result.append((role, path, digest))
        _require(len({item[0] for item in result}) == len(result), "来源绑定 role 重复")
        return sorted(result)

    _require(normalized(actual) == normalized(expected), "来源绑定与冻结清单不一致")


def validate_sample_catalog(samples_doc: dict[str, Any], manifest_sha256: str) -> list[dict[str, Any]]:
    """校验 109 项固定样本目录的顺序、来源类别和摘要字段。"""
    _require(samples_doc.get("schema_version") == "gestureforge_s2a_fixed_test_samples_v1", "固定样本 schema 不匹配")
    _require(samples_doc.get("seed") == EXPECTED_SEED, "固定样本 seed 不匹配")
    _require(samples_doc.get("sample_count") == EXPECTED_SAMPLE_COUNT, "固定样本 count 不为 109")
    _require(
        samples_doc.get("model_manifest_binding", {}).get("sha256") == manifest_sha256,
        "固定样本没有绑定冻结 model manifest",
    )
    samples = samples_doc.get("samples")
    _require(isinstance(samples, list) and len(samples) == EXPECTED_SAMPLE_COUNT, "固定样本列表长度不为 109")
    seen_ids: set[str] = set()
    supported_sources = {
        "official_hagrid_test",
        "official_hagrid_test_multibox",
        "approved_train_negative_from_calibration_list",
        "synthetic_rgb416",
    }
    for index, row in enumerate(samples):
        _require(isinstance(row, dict), f"固定样本 {index} 不是 object")
        _require(row.get("frame_id") == index, f"固定样本 {index} frame_id 顺序错误")
        sample_id = row.get("sample_id")
        _require(isinstance(sample_id, str) and sample_id and sample_id not in seen_ids, f"固定样本 {index} sample_id 缺失或重复")
        seen_ids.add(sample_id)
        _require(row.get("source") in supported_sources, f"固定样本 {index} source 未支持")
        _require(isinstance(row.get("width"), int) and row["width"] > 0, f"固定样本 {index} width 无效")
        _require(isinstance(row.get("height"), int) and row["height"] > 0, f"固定样本 {index} height 无效")
        _require(len(str(row.get("pl_input_sha256", ""))) == 64, f"固定样本 {index} PL input SHA 缺失")
        if row["source"] == "synthetic_rgb416":
            _require(len(str(row.get("rgb_sha256", ""))) == 64, f"合成样本 {index} RGB SHA 缺失")
            _require(row.get("width") == EXPECTED_WIDTH and row.get("height") == EXPECTED_HEIGHT, f"合成样本 {index} 尺寸不匹配")
        else:
            for key in ("relative_image", "relative_label", "image_sha256", "label_sha256"):
                _require(isinstance(row.get(key), str) and row[key], f"固定样本 {index} 缺少 {key}")
            for key in ("image_sha256", "label_sha256"):
                _require(len(row[key]) == 64 and row[key] == row[key].lower(), f"固定样本 {index} {key} 格式无效")
    synthetic = [row for row in samples if row["source"] == "synthetic_rgb416"]
    _require(len(synthetic) == 4, "固定样本必须含 4 个合成 RGB 案例")
    return samples


def _resolve_declared_path(path_text: str) -> Path:
    path = Path(path_text)
    _require(path.is_absolute(), f"外部来源路径必须使用 manifest 中冻结的绝对路径: {path_text}")
    resolved = path.resolve()
    _require(resolved.is_file(), f"外部来源文件不存在: {path_text}")
    return resolved


def _verify_manifest_external_inputs(
    root: Path, manifest: dict[str, Any], samples_doc: dict[str, Any]
) -> list[dict[str, str]]:
    """按 manifest 中原路径校验 cfg、weights、GF8 和官方样本清单。"""
    bindings = manifest.get("bindings", {})
    expected_roles = {
        "cfg": "frozen_cfg",
        "darknet_weights": "frozen_darknet_weights",
        "gf8_package": "frozen_gf8_parameter_package",
        "official_test_manifest": "official_test_manifest",
    }
    result = []
    for key, role in expected_roles.items():
        entry = bindings.get(key, {}) if key != "official_test_manifest" else samples_doc.get("official_test_manifest", {})
        path_text = str(entry.get("path", ""))
        expected = str(entry.get("sha256", "")).lower()
        _require(path_text and len(expected) == 64, f"manifest {key} binding 缺失")
        path = _resolve_declared_path(path_text)
        actual = sha256_file(path)
        _require(actual == expected, f"manifest {key} SHA-256 不匹配: {actual} != {expected}")
        result.append({"role": role, "path": path_text, "sha256": actual})
    return result


def _validate_manifest_contract(
    manifest: dict[str, Any], t22: dict[str, Any], samples_doc: dict[str, Any]
) -> None:
    """逐行核对 G0 manifest 与冻结 T22 dispatch 描述，不另造引用表。"""
    _require(manifest.get("status") == "G0_FROZEN", "tiny416 manifest 尚未 G0_FROZEN")
    _require(manifest.get("model", {}).get("model_id") == "tiny416", "当前 model 不是 tiny416")
    rows = manifest.get("layers")
    dispatch = t22.get("network_dispatch", {})
    dispatch_rows = dispatch.get("layers")
    _require(isinstance(rows, list) and len(rows) == EXPECTED_LAYER_COUNT, "manifest 层数不为 38")
    _require(isinstance(dispatch_rows, list) and len(dispatch_rows) == EXPECTED_LAYER_COUNT, "T22 dispatch 层数不为 38")
    _require(dispatch.get("layer_count") == EXPECTED_LAYER_COUNT, "T22 layer_count 不为 38")
    _require(
        dispatch.get("operator_counts") == {
            "convolutional": 21,
            "maxpool": 3,
            "route": 11,
            "upsample": 1,
            "yolo": 2,
        },
        "T22 operator count 不匹配",
    )
    input_contract = samples_doc.get("pl_input_contract", {})
    _require(input_contract.get("tensor_shape_nchw") == [1, 3, 416, 416], "fixed sample PL input shape 不匹配")
    _require(input_contract.get("tensor_dtype") == "signed int8 two's complement", "fixed sample PL input dtype 不匹配")
    _require(input_contract.get("includes_preprocessing") is True, "fixed sample PL input 未包含预处理")

    for index, (row, contract_row) in enumerate(zip(rows, dispatch_rows)):
        _require(row.get("layer_index") == index, f"manifest layer {index} 顺序错误")
        _require(row.get("cfg_section") == index + 1, f"manifest layer {index} cfg_section 错误")
        _require(contract_row.get("dispatch_order") == index, f"T22 layer {index} dispatch order 错误")
        _require(contract_row.get("layer_index") == index, f"T22 layer {index} 顺序错误")
        _require(contract_row.get("cfg_section") == row["cfg_section"], f"layer {index} cfg section 与 T22 不符")
        _require(contract_row.get("op") == row.get("op"), f"layer {index} op 与 T22 不符")
        _require(
            contract_row.get("manifest_source") == f"{MANIFEST_PATH}#/layers/{index}",
            f"layer {index} T22 manifest source 路径错误",
        )

        inputs = contract_row.get("input_tensors_in_manifest_order")
        refs = row.get("input_tensor_indices")
        _require(isinstance(inputs, list) and isinstance(refs, list) and len(inputs) == len(refs), f"layer {index} 输入引用数量不匹配")
        if row["op"] == "route":
            expected_shapes = row.get("input_shape_nchw")
            expected_scales = row.get("input_scales")
            _require(isinstance(expected_shapes, list) and isinstance(expected_scales, list), f"route {index} 缺 per-ref shape/scale")
            _require(len(expected_shapes) == len(inputs) == len(expected_scales), f"route {index} per-ref 元数据长度不匹配")
        else:
            expected_shapes = [row.get("input_shape_nchw")]
            expected_scales = [row.get("input_scale")]
        for input_order, (descriptor, reference, shape, scale) in enumerate(
            zip(inputs, refs, expected_shapes, expected_scales)
        ):
            if reference == "network_input":
                _require(descriptor.get("kind") == "network_input" and descriptor.get("source_index") == "network_input", "网络输入 sentinel 语义改变")
                _require(shape == [1, 3, 416, 416], "network input manifest shape 不匹配")
                _require(descriptor.get("address") == 0 and descriptor.get("length_bytes") == 519168, "network input 地址/长度不匹配")
            else:
                _require(descriptor.get("kind") == "layer_output", f"layer {index} input {input_order} 不是 layer_output")
                _require(descriptor.get("source_index") == reference, f"layer {index} input ref 顺序与 T22 不符")
                _require(isinstance(reference, int) and 0 <= reference < index, f"layer {index} 存在 forward/cyclic ref")
            _require(descriptor.get("shape_nchw") == shape, f"layer {index} input {input_order} shape 不匹配")
            _require(descriptor.get("scale") == scale, f"layer {index} input {input_order} scale 不匹配")
            _require(descriptor.get("layout") == "NCHW", f"layer {index} input {input_order} layout 不匹配")
            _require(descriptor.get("element_type") == "int8_twos_complement", f"layer {index} input {input_order} dtype 不匹配")

        output = contract_row.get("output_tensor", {})
        shape = row.get("output_shape_nchw")
        _require(output.get("shape_nchw") == shape, f"layer {index} output shape 与 T22 不符")
        _require(output.get("scale") == row.get("output_scale"), f"layer {index} output scale 与 T22 不符")
        expected_bytes = math.prod(shape)
        _require(row.get("tensor_length_bytes") == expected_bytes, f"layer {index} manifest tensor length 与 shape 不符")
        _require(output.get("length_bytes") == expected_bytes, f"layer {index} T22 tensor length 与 shape 不符")
        _require(output.get("address") == row.get("tensor_address"), f"layer {index} tensor address 与 T22 不符")
        _require(output.get("layout") == row.get("layout") == "NCHW", f"layer {index} output layout 不匹配")
        _require(row.get("element_type") == "int8_twos_complement", f"layer {index} manifest element type 不为 signed int8")
        _require(output.get("element_type") == row.get("element_type"), f"layer {index} output element type 与 manifest 不符")

        if row["op"] == "yolo":
            _require(output.get("allocation_kind") == "head_alias", f"YOLO layer {index} 未标为 head_alias")
            _require(output.get("memory_write_required") is False, f"YOLO layer {index} 不应产生 memory write")
            alias = output.get("alias_of_layer_index")
            _require(alias == row.get("output_tensor_index"), f"YOLO layer {index} alias index 与 manifest 不符")
            _require(len(inputs) == 1 and inputs[0].get("source_index") == alias, f"YOLO layer {index} input alias ref 不匹配")
            source_row = dispatch_rows[alias]
            source_output = source_row.get("output_tensor", {})
            validate_yolo_alias(contract_row, source_row)
            _require(source_output.get("address") == output.get("address"), f"YOLO layer {index} 地址未 alias")
        else:
            _require(output.get("allocation_kind") == "owned_feature_tensor", f"layer {index} 非 alias 输出未拥有 storage")
            _require(output.get("memory_write_required") is True, f"layer {index} owned output 未标记写入")
            _require(output.get("alias_of_layer_index") is None, f"layer {index} 意外 alias")
            _require(output.get("tensor_index") == index, f"layer {index} tensor index 不匹配")

    unique_bytes = sum(
        int(row["tensor_length_bytes"]) for row in rows if row["op"] != "yolo"
    )
    _require(unique_bytes == EXPECTED_UNIQUE_OUTPUT_BYTES, f"非 YOLO 输出总字节数意外: {unique_bytes}")


def validate_yolo_alias(alias_row: dict[str, Any], source_row: dict[str, Any]) -> None:
    """验证 YOLO 输出只引用其来源卷积张量，不分配重复字节。"""
    _require(alias_row.get("op") == "yolo", "alias row 不是 yolo")
    output = alias_row.get("output_tensor", {})
    source_output = source_row.get("output_tensor", {})
    source_index = source_row.get("layer_index")
    _require(source_row.get("op") == "convolutional", "YOLO alias source 不是 convolutional")
    _require(output.get("allocation_kind") == "head_alias", "YOLO 输出 allocation kind 不匹配")
    _require(output.get("memory_write_required") is False, "YOLO alias 不应写 memory")
    _require(output.get("alias_of_layer_index") == source_index, "YOLO alias_of_layer_index 不匹配")
    _require(output.get("tensor_index") == source_output.get("tensor_index"), "YOLO tensor index 未指向来源")
    for key in ("address", "length_bytes", "shape_nchw", "scale", "layout", "element_type"):
        _require(output.get(key) == source_output.get(key), f"YOLO alias {key} 与来源不匹配")


def _verify_runtime(manifest: dict[str, Any]) -> dict[str, str]:
    """核对本次执行版本与冻结预处理 runtime。"""
    import cv2
    import platform

    runtime = manifest.get("bindings", {}).get("preprocess_runtime", {})
    actual = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "opencv": cv2.__version__,
    }
    for key, value in actual.items():
        _require(runtime.get(key) == value, f"runtime {key} 与 G0 不一致: {value} != {runtime.get(key)}")
    return actual


def _load_modules(root: Path) -> dict[str, Any]:
    root_text = str(root.resolve())
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    return {
        "numeric": importlib.import_module("verification.s1_t02_d2_numeric_reference"),
        "forward": importlib.import_module("verification.s1_t02_d2_int8_forward"),
        "delivery": importlib.import_module("verification.s2a_model_delivery"),
    }


def load_context(repo_root: Path) -> dict[str, Any]:
    """验证全部冻结输入和来源摘要，再加载只读参考模块。"""
    root = repo_root.resolve()
    _require(root.is_dir(), f"仓库根目录不存在: {root}")
    pinned = []
    for relative, expected in PINNED_SHA256.items():
        actual = sha256_file(_repo_file(root, relative))
        _require(actual == expected, f"冻结来源 hash mismatch: {relative}")
        pinned.append({"role": f"repo:{relative}", "path": relative, "sha256": actual})

    manifest = _read_json(_repo_file(root, MANIFEST_PATH), "tiny416 manifest")
    samples_doc = _read_json(_repo_file(root, SAMPLES_PATH), "fixed samples")
    t22 = _read_json(_repo_file(root, T22_PATH), "T22 contract")
    t23 = _read_json(_repo_file(root, T23_TABLE_PATH), "T23 M/Q table")
    _require(manifest.get("schema_version") == "gestureforge_s2a_model_manifest_v1", "manifest schema 不匹配")
    _require(samples_doc.get("model_manifest_binding", {}).get("sha256") == PINNED_SHA256[MANIFEST_PATH], "sample manifest binding 不匹配")
    _require(t22.get("schema_version") == "gestureforge_s2a_network_dispatch_contract_v1", "T22 schema 不匹配")
    _require(t22.get("artifact_status") == "CONTRACT_VALIDATED", "T22 contract 未通过")
    _require(t23.get("schema_version") == "gestureforge_s2a_conv_requant_parameter_table_v1", "T23 table schema 不匹配")
    _require(t23.get("status") == "ALL_CHANNELS_EXACT_AND_T16_DIGEST_MATCH", "T23 table 未通过")
    _require(t23.get("coverage", {}).get("convolution_layers") == 21, "T23 conv coverage 不为 21")
    _require(t23.get("coverage", {}).get("output_channels") == 3164, "T23 channel coverage 不为 3164")
    t23_tool_bindings = {
        (str(item.get("path")), str(item.get("sha256")))
        for item in t23.get("tooling_bindings", [])
        if isinstance(item, dict)
    }
    _require(
        (T23_EXPORTER_PATH, PINNED_SHA256[T23_EXPORTER_PATH]) in t23_tool_bindings
        and (T23_TEST_PATH, PINNED_SHA256[T23_TEST_PATH]) in t23_tool_bindings,
        "T23 JSON tooling bindings 与已冻结工具不符",
    )
    samples = validate_sample_catalog(samples_doc, PINNED_SHA256[MANIFEST_PATH])
    _validate_manifest_contract(manifest, t22, samples_doc)
    runtime = _verify_runtime(manifest)
    external = _verify_manifest_external_inputs(root, manifest, samples_doc)
    source_bindings = pinned + external
    _require(len({row["role"] for row in source_bindings}) == len(source_bindings), "source binding role 重复")
    modules = _load_modules(root)
    return {
        "root": root,
        "manifest": manifest,
        "samples_doc": samples_doc,
        "samples": samples,
        "t22": t22,
        "t23": t23,
        "runtime": runtime,
        "source_bindings": source_bindings,
        "modules": modules,
        "external": external,
    }


def _synthetic_rgb_inputs(delivery: Any, seed: int) -> dict[str, np.ndarray]:
    """按冻结 generator 的四种 synthetic case 还原 RGB 原始输入。"""
    _require(seed == EXPECTED_SEED, "synthetic seed 不匹配冻结值")
    y, x = np.indices((EXPECTED_HEIGHT, EXPECTED_WIDTH))
    checker = np.where((x + y) & 1, 255, 0).astype(np.uint8)
    random = np.frombuffer(
        delivery.xorshift32(seed, EXPECTED_WIDTH * EXPECTED_HEIGHT * 3), dtype=np.uint8
    ).reshape(EXPECTED_HEIGHT, EXPECTED_WIDTH, 3)
    return {
        "synthetic_black": np.zeros((EXPECTED_HEIGHT, EXPECTED_WIDTH, 3), dtype=np.uint8),
        "synthetic_white": np.full((EXPECTED_HEIGHT, EXPECTED_WIDTH, 3), 255, dtype=np.uint8),
        "synthetic_checkerboard": np.repeat(checker[:, :, None], 3, axis=2),
        "synthetic_xorshift32": random,
    }


def verify_synthetic_replay(context: dict[str, Any]) -> list[dict[str, Any]]:
    """复用冻结 synthetic_cases 清单，并用 D2 numeric oracle 重算四种输入。"""
    delivery = context["modules"]["delivery"]
    numeric = context["modules"]["numeric"]
    seed = context["samples_doc"].get("seed")
    generated = delivery.synthetic_cases(seed)
    expected_by_id = {row["sample_id"]: row for row in generated}
    fixed_by_id = {
        row["sample_id"]: row for row in context["samples"] if row["source"] == "synthetic_rgb416"
    }
    _require(set(expected_by_id) == set(fixed_by_id), "synthetic_cases 与 fixed samples ID 不一致")
    raw_inputs = _synthetic_rgb_inputs(delivery, seed)
    checks = []
    for sample_id, rgb in raw_inputs.items():
        generated_row = expected_by_id[sample_id]
        fixed_row = fixed_by_id[sample_id]
        raw = np.ascontiguousarray(rgb).tobytes(order="C")
        rgb_hash = sha256_bytes(raw)
        _require(rgb_hash == generated_row.get("rgb_sha256") == fixed_row.get("rgb_sha256"), f"{sample_id} RGB SHA 不匹配")
        d2_result = np.asarray(numeric.preprocess_rgb_uint8_to_chw_int8(rgb.tolist(), EXPECTED_WIDTH, EXPECTED_HEIGHT), dtype=np.int8)
        _require(list(d2_result.shape) == [3, EXPECTED_HEIGHT, EXPECTED_WIDTH], f"{sample_id} D2 input shape 错误")
        pl_hash = sha256_bytes(np.ascontiguousarray(d2_result).tobytes(order="C"))
        _require(pl_hash == generated_row.get("pl_input_sha256") == fixed_row.get("pl_input_sha256"), f"{sample_id} PL-input SHA 不匹配")
        checks.append({"sample_id": sample_id, "rgb_sha256": rgb_hash, "pl_input_sha256": pl_hash})
    return checks


def validate_preprocessed_input(
    tensor: np.ndarray, expected_shape_nchw: list[int], expected_sha256: str
) -> tuple[bytes, str]:
    """验证 D2 数值预处理输出形状、INT8 域和逐字节摘要。"""
    array = np.asarray(tensor)
    _require(array.dtype == np.int8, "PL 输入 dtype 不是 int8")
    _require([1, *list(array.shape)] == expected_shape_nchw, "PL 输入 NCHW shape 不匹配")
    _require(array.ndim == 3 and array.shape[0] == EXPECTED_CHANNELS, "PL 输入必须为 CHW")
    _require(array.size == math.prod(expected_shape_nchw), "PL 输入元素数错误")
    _require(int(array.min()) >= -127 and int(array.max()) <= 127, "PL 输入超出对称 INT8 范围")
    raw = np.ascontiguousarray(array).tobytes(order="C")
    digest = verify_digest(raw, expected_sha256, "PL input")
    return raw, digest


def validate_tensor_payload(
    layer_index: int,
    op: str,
    values: np.ndarray,
    scale: float,
    output_descriptor: dict[str, Any],
    expected_sha256: str | None = None,
) -> tuple[bytes, dict[str, Any]]:
    """验证单层输出 NCHW、scale、长度与逐 tensor 摘要。"""
    array = np.asarray(values)
    _require(array.dtype == np.int8, f"layer {layer_index} output dtype 不是 int8")
    _require(array.ndim == 3, f"layer {layer_index} output 必须是 CHW")
    shape_nchw = [1, *[int(value) for value in array.shape]]
    _require(shape_nchw == output_descriptor.get("shape_nchw"), f"layer {layer_index} output shape 不匹配")
    _require(float(scale) == output_descriptor.get("scale"), f"layer {layer_index} output scale 不匹配")
    _require(int(array.min()) >= -127 and int(array.max()) <= 127, f"layer {layer_index} 输出超出对称 INT8")
    raw = np.ascontiguousarray(array).tobytes(order="C")
    expected_length = int(output_descriptor.get("length_bytes", -1))
    _require(len(raw) == expected_length == math.prod(shape_nchw), f"layer {layer_index} output byte length 不匹配")
    digest = sha256_bytes(raw)
    if expected_sha256 is not None:
        _require(digest == expected_sha256, f"layer {layer_index} output SHA-256 不匹配")
    return raw, {
        "layer_index": layer_index,
        "op": op,
        "shape_nchw": shape_nchw,
        "scale": float(scale),
        "element_type": "int8_twos_complement",
        "byte_length": len(raw),
        "tensor_sha256": digest,
    }


def validate_no_conv_overflow(stats: dict[str, Any]) -> None:
    """任何 raw/bias/with-bias INT32 越界均拒绝该卷积样本。"""
    count_fields = (
        "int32_overflow_count",
        "raw_accumulator_int32_overflow_count",
        "bias_accumulator_int32_overflow_count",
        "accumulator_with_bias_int32_overflow_count",
    )
    nonzero = {key: int(stats.get(key, 0)) for key in count_fields if int(stats.get(key, 0)) != 0}
    _require(not nonzero, f"卷积 INT32 overflow_count 非零: {nonzero}")


def validate_pilot_index(index: dict[str, Any]) -> None:
    """保证本证据只表达 pilot，不误称全量或阶段验收。"""
    _require(index.get("schema_version") == "gestureforge_s2a_cpu_layer_golden_index_v1", "T24 index schema 不匹配")
    _require(index.get("status") == "PILOT_ONLY", "T24 index 不再是 PILOT_ONLY")
    _require(index.get("stage_acceptance") == {"G4": "NOT_MET", "G5": "NOT_MET"}, "T24 G4/G5 状态不匹配")
    pilot = index.get("pilot_sample", {})
    catalog = index.get("fixed_sample_catalog", {})
    _require(pilot.get("sample_index") == 0 and pilot.get("sample_id") == "test_fist_000", "T24 pilot 样本不是 sample0")
    _require(catalog.get("total_samples") == EXPECTED_SAMPLE_COUNT, "T24 catalog count 不为 109")
    _require(catalog.get("completed_samples") == 1 and catalog.get("remaining_samples") == 108, "T24 pilot 覆盖计数不匹配")
    _require(index.get("network", {}).get("layer_count") == EXPECTED_LAYER_COUNT, "T24 pilot layer count 不为 38")


def validate_tensor_stream(raw_stream: bytes, tensor_rows: list[dict[str, Any]]) -> None:
    """验证存储张量 offset 连续，YOLO alias 指向来源区间且摘要一致。"""
    cursor = 0
    by_layer: dict[int, dict[str, Any]] = {}
    for row in tensor_rows:
        index = int(row["layer_index"])
        _require(index not in by_layer, f"tensor layer {index} 重复")
        by_layer[index] = row
        offset = int(row["byte_offset"])
        length = int(row["byte_length"])
        if row.get("stored") is True:
            _require(offset == cursor, f"layer {index} stream offset 不连续")
            _require(length > 0 and offset + length <= len(raw_stream), f"layer {index} stream range 越界")
            payload = raw_stream[offset : offset + length]
            _require(sha256_bytes(payload) == row.get("tensor_sha256"), f"layer {index} tensor SHA 不匹配")
            cursor += length
        else:
            source_index = row.get("alias_of_layer_index")
            _require(isinstance(source_index, int) and source_index in by_layer, f"layer {index} alias source 不存在或非前向")
            source = by_layer[source_index]
            _require(source.get("stored") is True, f"layer {index} alias source 本身不是存储 tensor")
            _require(offset == source["byte_offset"] and length == source["byte_length"], f"layer {index} alias offset/length 不匹配")
            _require(row.get("tensor_sha256") == source.get("tensor_sha256"), f"layer {index} alias SHA 与来源不匹配")
    _require(cursor == len(raw_stream), "tensor stream 存在未绑定尾部字节")


def serialize_tensor_stream(
    captures: list[dict[str, Any]], contract_rows: list[dict[str, Any]]
) -> tuple[bytes, bytes, list[dict[str, Any]]]:
    """按 dispatch 顺序生成唯一 tensor 原始流和确定性 zlib shard。"""
    _require(len(captures) == len(contract_rows) and len(captures) > 0, "capture/dispatch 行数不匹配")
    capture_by_index = {int(row["layer_index"]): row for row in captures}
    _require(len(capture_by_index) == EXPECTED_LAYER_COUNT, "capture layer index 重复")
    stream = bytearray()
    records: list[dict[str, Any]] = []
    for index, contract_row in enumerate(contract_rows):
        capture = capture_by_index.get(index)
        _require(capture is not None, f"capture 缺少 layer {index}")
        descriptor = contract_row["output_tensor"]
        raw = capture["raw_bytes"]
        digest = sha256_bytes(raw)
        _require(len(raw) == descriptor["length_bytes"], f"layer {index} raw bytes 与 T22 length 不符")
        alias_index = descriptor.get("alias_of_layer_index")
        if descriptor.get("allocation_kind") == "head_alias":
            _require(capture.get("op") == "yolo" and isinstance(alias_index, int), f"layer {index} alias metadata 无效")
            source = next((item for item in records if item["layer_index"] == alias_index), None)
            _require(source is not None and source["stored"] is True, f"layer {index} alias source 缺失")
            _require(source["tensor_sha256"] == digest and source["byte_length"] == len(raw), f"layer {index} alias payload 与来源不一致")
            _require(source["shape_nchw"] == capture["shape_nchw"] and source["scale"] == capture["scale"], f"layer {index} alias shape/scale 不匹配")
            offset = int(source["byte_offset"])
            stored = False
        else:
            _require(alias_index is None and descriptor.get("memory_write_required") is True, f"layer {index} owned tensor descriptor 无效")
            offset = len(stream)
            stream.extend(raw)
            stored = True
        record = {
            "layer_index": index,
            "cfg_section": int(contract_row["cfg_section"]),
            "op": str(contract_row["op"]),
            "shape_nchw": capture["shape_nchw"],
            "scale": float(capture["scale"]),
            "element_type": "int8_twos_complement",
            "byte_offset": offset,
            "byte_length": len(raw),
            "tensor_sha256": digest,
            "stored": stored,
            "alias_of_layer_index": alias_index,
        }
        records.append(record)

    raw_stream = bytes(stream)
    expected_stored_bytes = sum(
        int(row["output_tensor"]["length_bytes"])
        for row in contract_rows
        if row["output_tensor"].get("allocation_kind") != "head_alias"
    )
    _require(len(raw_stream) == expected_stored_bytes, "unique tensor stream length 与 owned outputs 不符")
    validate_tensor_stream(raw_stream, records)
    compressed = zlib.compress(raw_stream, level=9)
    decompressed = zlib.decompress(compressed)
    _require(decompressed == raw_stream, "zlib stream roundtrip 不一致")
    validate_tensor_stream(decompressed, records)
    return raw_stream, compressed, records


def _check_deadline(started: float, limit_seconds: float, stage: str) -> None:
    elapsed = time.monotonic() - started
    _require(elapsed <= limit_seconds, f"pilot 超过 {limit_seconds:.0f} 秒上限，停止于 {stage}，已用 {elapsed:.1f} 秒")


def _sample_paths(context: dict[str, Any], sample: dict[str, Any]) -> tuple[Path, Path]:
    root = Path(context["samples_doc"]["official_test_manifest"]["path"]).resolve().parent
    result = []
    for key in ("relative_image", "relative_label"):
        relative = Path(str(sample.get(key, "")))
        _require(not relative.is_absolute() and ".." not in relative.parts, f"sample {key} 必须是安全相对路径")
        resolved = (root / relative).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise GoldenExportError(f"sample {key} 越出官方数据根目录") from exc
        _require(resolved.is_file(), f"sample {key} 不存在")
        result.append(resolved)
    return result[0], result[1]


def _check_input_descriptors(
    layer_index: int,
    contract_row: dict[str, Any],
    outputs: list[Any],
    network_input: Any,
) -> list[Any]:
    """用 T22 有序 input refs 核对已捕获的输入 Tensor。"""
    descriptors = contract_row["input_tensors_in_manifest_order"]
    tensors = []
    for descriptor in descriptors:
        if descriptor.get("kind") == "network_input":
            _require(descriptor.get("source_index") == "network_input", "network_input sentinel 被转成层号")
            tensor = network_input
        else:
            source = descriptor.get("source_index")
            _require(isinstance(source, int) and 0 <= source < layer_index, f"layer {layer_index} 存在 forward ref")
            tensor = outputs[source]
        actual_shape = [1, *[int(value) for value in tensor.values.shape]]
        _require(actual_shape == descriptor.get("shape_nchw"), f"layer {layer_index} input shape 与 T22 不匹配")
        _require(float(tensor.scale) == descriptor.get("scale"), f"layer {layer_index} input scale 与 T22 不匹配")
        tensors.append(tensor)
    return tensors


def run_sample0_pilot(context: dict[str, Any], max_seconds: float = 600.0) -> dict[str, Any]:
    """执行唯一允许的 sample0 完整网络整数前向并捕获 38 层输出。"""
    _require(max_seconds > 0.0, "pilot timeout 必须为正")
    started = time.monotonic()
    modules = context["modules"]
    numeric = modules["numeric"]
    forward = modules["forward"]
    delivery = modules["delivery"]
    sample = context["samples"][0]
    _require(sample.get("frame_id") == 0 and sample.get("sample_id") == "test_fist_000", "sample0 identity 不匹配")

    synthetic_checks = verify_synthetic_replay(context)
    _check_deadline(started, max_seconds, "synthetic 输入闭环")

    image_path, label_path = _sample_paths(context, sample)
    image_digest = verify_digest(image_path.read_bytes(), sample["image_sha256"], "sample0 original image")
    label_digest = verify_digest(label_path.read_bytes(), sample["label_sha256"], "sample0 label")
    rgb = delivery.decode_rgb(image_path)
    _require(rgb.dtype == np.uint8 and list(rgb.shape) == [sample["height"], sample["width"], 3], "sample0 RGB decode shape/dtype 不匹配")
    preprocessed = np.asarray(
        numeric.preprocess_rgb_uint8_to_chw_int8(rgb.tolist(), EXPECTED_WIDTH, EXPECTED_HEIGHT),
        dtype=np.int8,
    )
    input_desc = context["t22"]["network_dispatch"]["layers"][0]["input_tensors_in_manifest_order"][0]
    input_raw, input_digest = validate_preprocessed_input(
        preprocessed, input_desc["shape_nchw"], sample["pl_input_sha256"]
    )
    _check_deadline(started, max_seconds, "sample0 D2 preprocessing")

    manifest = context["manifest"]
    layers = manifest["layers"]
    dispatch_rows = context["t22"]["network_dispatch"]["layers"]
    cfg_path = _resolve_declared_path(manifest["bindings"]["cfg"]["path"])
    gf8_path = _resolve_declared_path(manifest["bindings"]["gf8_package"]["path"])
    sections = forward.parse_cfg_sections(cfg_path)
    _require(len(sections) == EXPECTED_LAYER_COUNT + 1, "cfg section 数量不为 net+38")
    package_header, package_layers = forward.parse_package(gf8_path)
    _require(package_header["width"] == EXPECTED_WIDTH and package_header["height"] == EXPECTED_HEIGHT, "GF8 输入尺寸不匹配")
    _require(package_header["channels"] == EXPECTED_CHANNELS, "GF8 输入通道数不匹配")
    _require(package_header["layer_count"] == 21, "GF8 卷积层数不为 21")

    network_input = forward.Tensor(preprocessed, float(input_desc["scale"]))
    outputs: list[Any] = []
    captures = []
    convolution_stats = []
    for index, (row, contract_row, section) in enumerate(zip(layers, dispatch_rows, sections[1:])):
        _check_deadline(started, max_seconds, f"layer {index} 前")
        op = row["op"]
        _require(section.kind == op, f"layer {index} cfg op 与 manifest 不一致")
        input_tensors = _check_input_descriptors(index, contract_row, outputs, network_input)
        output_descriptor = contract_row["output_tensor"]

        if op == "convolutional":
            _require(len(input_tensors) == 1, f"conv {index} 必须有一个输入")
            package_layer = package_layers.get(index)
            _require(package_layer is not None, f"conv {index} GF8 参数缺失")
            _require(package_layer.filters == row["output_shape_nchw"][1], f"conv {index} filters 与 manifest 不符")
            _require(package_layer.input_channels == input_tensors[0].values.shape[0], f"conv {index} input channels 不符")
            _require(package_layer.groups == int(row["groups"]), f"conv {index} groups 不符")
            _require(
                np.array_equal(package_layer.weight_scales, np.asarray(row["weight_scale_per_output_channel"], dtype=np.float64)),
                f"conv {index} GF8 weight scales 与 manifest 不符",
            )
            size = forward.cfg_int(section.options, "size")
            stride, padding = forward.convolution_parameters(section.options, size)
            activation = section.options.get("activation", "linear").lower()
            _require(activation == row["activation"], f"conv {index} activation 与 manifest 不符")
            output, stats = forward.conv_int8(
                input_tensors[0],
                package_layer,
                float(row["output_scale"]),
                activation,
                stride,
                padding,
            )
            validate_no_conv_overflow(stats)
            _require(stats["input_scale"] == contract_row["input_tensors_in_manifest_order"][0]["scale"], f"conv {index} D2 input scale 不符")
            _require(stats["output_scale"] == output_descriptor["scale"], f"conv {index} D2 output scale 不符")
            convolution_stats.append(
                {
                    "layer_index": index,
                    "input_scale": stats["input_scale"],
                    "output_scale": stats["output_scale"],
                    "raw_accumulator_int32_overflow_count": stats["raw_accumulator_int32_overflow_count"],
                    "bias_accumulator_int32_overflow_count": stats["bias_accumulator_int32_overflow_count"],
                    "accumulator_with_bias_int32_overflow_count": stats["accumulator_with_bias_int32_overflow_count"],
                    "int32_overflow_count": stats["int32_overflow_count"],
                    "raw_accumulator_min": stats["raw_accumulator_min"],
                    "raw_accumulator_max": stats["raw_accumulator_max"],
                    "accumulator_with_bias_min": stats["accumulator_with_bias_min"],
                    "accumulator_with_bias_max": stats["accumulator_with_bias_max"],
                    "saturated_count": stats["saturated_count"],
                }
            )
        elif op == "route":
            raw_refs = [int(value.strip(), 10) for value in section.options.get("layers", "").split(",") if value.strip()]
            resolved_refs = [forward.resolve_reference(ref, index) for ref in raw_refs]
            contract_refs = [item["source_index"] for item in contract_row["input_tensors_in_manifest_order"]]
            _require(resolved_refs == contract_refs, f"route {index} cfg ref 顺序与 T22 不符")
            groups = forward.cfg_int(section.options, "groups", 1)
            group_id = forward.cfg_int(section.options, "group_id", 0)
            _require(groups == row["route_groups"] and group_id == row["route_group_id"], f"route {index} group 参数不匹配")
            output = forward.route_int8(outputs, raw_refs, index, groups, group_id)
            _require(output.scale == output_descriptor["scale"], f"route {index} output scale 不匹配")
        elif op == "maxpool":
            size = forward.cfg_int(section.options, "size")
            _, stride, padding = forward.maxpool_parameters(section.options, size)
            values = forward.maxpool(input_tensors[0].values, size, stride, padding)
            output = forward.Tensor(values, input_tensors[0].scale)
        elif op == "upsample":
            stride = forward.upsample_stride(section.options)
            values = np.repeat(np.repeat(input_tensors[0].values, stride, axis=1), stride, axis=2)
            output = forward.Tensor(values, input_tensors[0].scale)
        elif op == "yolo":
            alias_index = int(output_descriptor["alias_of_layer_index"])
            validate_yolo_alias(contract_row, dispatch_rows[alias_index])
            _require(alias_index < index and len(input_tensors) == 1, f"YOLO {index} alias input 不合法")
            _require(contract_row["input_tensors_in_manifest_order"][0]["source_index"] == alias_index, f"YOLO {index} source ref 不匹配")
            output = outputs[alias_index]
        else:
            raise GoldenExportError(f"不支持的 cfg op: {op}")

        raw, tensor_metadata = validate_tensor_payload(index, op, output.values, output.scale, output_descriptor)
        _require(tensor_metadata["shape_nchw"] == row["output_shape_nchw"], f"layer {index} output shape 与 manifest 不匹配")
        _require(tensor_metadata["scale"] == row["output_scale"], f"layer {index} output scale 与 manifest 不匹配")
        outputs.append(output)
        captures.append(
            {
                "layer_index": index,
                "op": op,
                "shape_nchw": tensor_metadata["shape_nchw"],
                "scale": tensor_metadata["scale"],
                "raw_bytes": raw,
            }
        )
        _check_deadline(started, max_seconds, f"layer {index} 后")

    _require(len(outputs) == EXPECTED_LAYER_COUNT, "捕获输出不是完整 38 层")
    _require(len(convolution_stats) == 21, "卷积 overflow/shape/scale 统计未覆盖 21 层")
    raw_stream, compressed, tensor_rows = serialize_tensor_stream(captures, dispatch_rows)
    _require(len(tensor_rows) == EXPECTED_LAYER_COUNT, "序列化 tensor row 数不为 38")
    _require(len(raw_stream) == EXPECTED_UNIQUE_OUTPUT_BYTES, f"unique tensor stream length 意外: {len(raw_stream)}")
    _check_deadline(started, max_seconds, "stream 压缩和验证")
    return {
        "sample": sample,
        "image_path": image_path,
        "label_path": label_path,
        "image_sha256": image_digest,
        "label_sha256": label_digest,
        "rgb_shape_hwc": list(rgb.shape),
        "input_raw_bytes": len(input_raw),
        "input_sha256": input_digest,
        "synthetic_checks": synthetic_checks,
        "raw_stream": raw_stream,
        "compressed_stream": compressed,
        "tensor_rows": tensor_rows,
        "convolution_stats": convolution_stats,
        "elapsed_seconds": time.monotonic() - started,
    }


def build_index(context: dict[str, Any], pilot: dict[str, Any], shard_relative_path: str) -> dict[str, Any]:
    """构造不含时间戳、仓库绝对路径的 pilot 索引。"""
    root = context["root"]
    tooling = [
        {
            "role": "t24_exporter",
            "path": T24_EXPORTER_PATH,
            "sha256": sha256_file(_repo_file(root, T24_EXPORTER_PATH)),
        },
        {
            "role": "t24_test",
            "path": T24_TEST_PATH,
            "sha256": sha256_file(_repo_file(root, T24_TEST_PATH)),
        },
    ]
    table_path = context["samples_doc"]["official_test_manifest"]["path"]
    index = {
        "schema_version": "gestureforge_s2a_cpu_layer_golden_index_v1",
        "task_id": "S2A-T24",
        "status": "PILOT_ONLY",
        "model_id": "tiny416",
        "stage_acceptance": {"G4": "NOT_MET", "G5": "NOT_MET"},
        "runtime": context["runtime"],
        "source_bindings": context["source_bindings"],
        "tooling_bindings": tooling,
        "fixed_sample_catalog": {
            "path": SAMPLES_PATH,
            "sha256": PINNED_SHA256[SAMPLES_PATH],
            "total_samples": len(context["samples"]),
            "seed": context["samples_doc"]["seed"],
            "catalog_rows_structurally_validated": len(context["samples"]),
            "completed_samples": 1,
            "remaining_samples": len(context["samples"]) - 1,
            "synthetic_rgb_preprocess_replays": pilot["synthetic_checks"],
        },
        "network": {
            "layer_count": EXPECTED_LAYER_COUNT,
            "operator_counts": context["t22"]["network_dispatch"]["operator_counts"],
            "non_alias_tensor_count": sum(row["stored"] for row in pilot["tensor_rows"]),
            "unique_output_raw_bytes": len(pilot["raw_stream"]),
            "raw_stream_sha256": sha256_bytes(pilot["raw_stream"]),
            "compressed_shard": {
                "path": shard_relative_path,
                "codec": "zlib",
                "compression_level": 9,
                "zlib_version": zlib.ZLIB_VERSION,
                "compressed_bytes": len(pilot["compressed_stream"]),
                "sha256": sha256_bytes(pilot["compressed_stream"]),
                "decompressed_bytes": len(pilot["raw_stream"]),
                "decompressed_sha256": sha256_bytes(pilot["raw_stream"]),
            },
            "tensors": pilot["tensor_rows"],
            "convolution_stats": pilot["convolution_stats"],
        },
        "pilot_sample": {
            "sample_index": 0,
            "sample_id": pilot["sample"]["sample_id"],
            "frame_id": pilot["sample"]["frame_id"],
            "source": pilot["sample"]["source"],
            "original_image": {
                "path": pilot["sample"]["relative_image"],
                "sha256": pilot["image_sha256"],
                "width": pilot["sample"]["width"],
                "height": pilot["sample"]["height"],
                "rgb_shape_hwc": pilot["rgb_shape_hwc"],
            },
            "label": {
                "path": pilot["sample"]["relative_label"],
                "sha256": pilot["label_sha256"],
            },
            "preprocessed_input": {
                "oracle_path": D2_NUMERIC_PATH,
                "oracle_callable": "preprocess_rgb_uint8_to_chw_int8",
                "shape_nchw": [1, 3, 416, 416],
                "dtype": "signed int8 two's complement",
                "raw_bytes": pilot["input_raw_bytes"],
                "sha256": pilot["input_sha256"],
            },
            "ground_truth_yolo": pilot["sample"].get("ground_truth_yolo", []),
        },
        "limitations": {
            "completed_fixed_samples": 1,
            "pending_fixed_samples": len(context["samples"]) - 1,
            "cpu_per_layer_goldens": "PILOT_ONLY",
            "full_109_sample_run": "NOT_RUN",
            "ps_decode_nms_comparison": "NOT_RUN",
            "rtl_or_vivado": "NOT_RUN",
            "G4": "NOT_MET",
            "G5": "NOT_MET",
        },
    }
    validate_pilot_index(index)
    return index


def write_pilot(repo_root: Path, output_dir: Path, max_seconds: float = 600.0) -> dict[str, Any]:
    """执行 sample0 pilot，校验完成后只创建指定 evidence 目录中的 index/shard。"""
    root = repo_root.resolve()
    target_dir = output_dir if output_dir.is_absolute() else root / output_dir
    target_dir = target_dir.resolve()
    try:
        target_dir.relative_to(root)
    except ValueError as exc:
        raise GoldenExportError("T24 输出目录必须位于指定仓库内") from exc
    _require(target_dir.parent.is_dir(), f"输出父目录不存在: {target_dir.parent}")
    _require(not target_dir.exists(), f"输出目录已存在，拒绝覆盖: {target_dir}")

    context = load_context(root)
    pilot = run_sample0_pilot(context, max_seconds)
    shard_path = target_dir / "tensors" / "sample_000.zlib"
    index_path = target_dir / "cpu_layer_golden_index.json"
    shard_rel = shard_path.relative_to(root).as_posix()
    index = build_index(context, pilot, shard_rel)
    _require(not shard_path.exists() and not index_path.exists(), "T24 输出目标发生冲突，拒绝覆盖")

    target_dir.mkdir()
    shard_path.parent.mkdir()
    shard_path.write_bytes(pilot["compressed_stream"])
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    return index


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成 sample0 的 tiny416 CPU 逐层整数张量 pilot")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-seconds", type=float, default=600.0)
    args = parser.parse_args(argv)
    started = time.monotonic()
    try:
        index = write_pilot(args.repo_root, args.output_dir, args.max_seconds)
    except (GoldenExportError, OSError, ValueError, OverflowError, ImportError, AssertionError) as exc:
        print(f"S2A-T24 pilot error: {exc}", file=sys.stderr)
        return 2
    pilot = index["pilot_sample"]
    network = index["network"]
    print(
        "S2A-T24 PILOT_ONLY verified: "
        f"sample={pilot['sample_id']} layers={network['layer_count']} "
        f"unique_bytes={network['unique_output_raw_bytes']} "
        f"compressed_bytes={network['compressed_shard']['compressed_bytes']} "
        f"elapsed_seconds={time.monotonic()-started:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
