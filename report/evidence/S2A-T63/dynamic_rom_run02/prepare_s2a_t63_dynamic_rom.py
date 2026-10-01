from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import struct
import sys
from pathlib import Path
from typing import Any


ROOT = Path("D:/FPGA_Competition")
RUN_REL = "report/evidence/S2A-T63/dynamic_rom_run02"
RUN_DIR = ROOT / RUN_REL
PACKAGE_REL = "src/s2a_network_descriptor_pkg.sv"
TB_NAME = "tb_s2a_t63_descriptor_rom_dynamic.sv"
RUNNER_NAME = "run_s2a_t63_descriptor_rom_dynamic.ps1"
VERIFIER_NAME = "prepare_s2a_t63_dynamic_rom.py"
TEST_NAME = "test_s2a_t63_dynamic_rom.py"
MANIFEST_NAME = "dynamic_rom_fixture_binding.json"
LAYER_FIXTURE_NAME = "expected_layers.mem"
CHANNEL_FIXTURE_NAME = "expected_channels.mem"

FROZEN_INPUTS = {
    "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md":
        "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    "report/evidence/S2A-T01/tiny416_model_manifest.json":
        "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    "report/evidence/S2A-T22/network_dispatch_contract_validation.json":
        "611d47cc85bd254474c5412fcab2f8acce3a263138787588f2a6445eac61d9a8",
    "report/evidence/S2A-T23/conv_requant_parameter_table.json":
        "396dc66aa3ccc41050cc8183bff16b86143a6f5553cf38fed16b0ba8b4eb4ae1",
}

OP_CODE = {
    "convolutional": 0,
    "maxpool": 1,
    "route": 2,
    "upsample": 3,
    "yolo": 4,
}
OP_COUNTS = {
    "convolutional": 21,
    "maxpool": 3,
    "route": 11,
    "upsample": 1,
    "yolo": 2,
}
OP_FIELD_ORDER = tuple(OP_CODE)
EXPECTED_ANCHORS = [[10, 14], [23, 27], [37, 58], [81, 82], [135, 169], [344, 319]]
EXPECTED_MASKS = {30: [3, 4, 5], 37: [1, 2, 3]}
TOTAL_CHANNELS = 3164

# 本顺序与 TB 的 actual_layer 拼接顺序逐项核对。
LAYER_VECTOR_EXPRESSIONS = [
    "S2A_LAYER_INDEX[idx]",
    "S2A_CFG_SECTION[idx]",
    "S2A_OP[idx]",
    "S2A_INPUT_COUNT[idx]",
]
for _slot in range(2):
    LAYER_VECTOR_EXPRESSIONS.extend(
        [
            f"S2A_INPUT_KIND[idx][{_slot}]",
            f"S2A_INPUT_SOURCE_INDEX[idx][{_slot}]",
            f"S2A_INPUT_ADDRESS[idx][{_slot}]",
            f"S2A_INPUT_LENGTH_BYTES[idx][{_slot}]",
            f"S2A_INPUT_N[idx][{_slot}]",
            f"S2A_INPUT_C[idx][{_slot}]",
            f"S2A_INPUT_H[idx][{_slot}]",
            f"S2A_INPUT_W[idx][{_slot}]",
            f"S2A_INPUT_SCALE_BITS[idx][{_slot}]",
            f"S2A_INPUT_ROUTE_CHANNEL_START[idx][{_slot}]",
            f"S2A_INPUT_ROUTE_CHANNEL_END[idx][{_slot}]",
        ]
    )
LAYER_VECTOR_EXPRESSIONS.extend(
    [
        "S2A_OUTPUT_TENSOR_INDEX[idx]",
        "S2A_OUTPUT_ALLOCATION_KIND[idx]",
        "S2A_OUTPUT_ALIAS_LAYER_INDEX[idx]",
        "S2A_OUTPUT_MEMORY_WRITE_REQUIRED[idx]",
        "S2A_OUTPUT_ADDRESS[idx]",
        "S2A_OUTPUT_LENGTH_BYTES[idx]",
        "S2A_OUTPUT_N[idx]",
        "S2A_OUTPUT_C[idx]",
        "S2A_OUTPUT_H[idx]",
        "S2A_OUTPUT_W[idx]",
        "S2A_OUTPUT_SCALE_BITS[idx]",
        "S2A_KERNEL_H[idx]",
        "S2A_KERNEL_W[idx]",
        "S2A_STRIDE_H[idx]",
        "S2A_STRIDE_W[idx]",
        "S2A_PADDING_LEFT[idx]",
        "S2A_PADDING_RIGHT[idx]",
        "S2A_PADDING_TOP[idx]",
        "S2A_PADDING_BOTTOM[idx]",
        "S2A_GROUP_COUNT[idx]",
        "S2A_ROUTE_GROUP_ID[idx]",
        "S2A_PADDING_VALUE_INT8[idx]",
        "S2A_ACTIVATION[idx]",
        "S2A_ACCUMULATOR_BITS[idx]",
        "S2A_WEIGHT_LAYER_INDEX[idx]",
        "S2A_GF8_RECORD_OFFSET[idx]",
        "S2A_GF8_WEIGHT_SCALE_OFFSET[idx]",
        "S2A_GF8_BIAS_OFFSET[idx]",
        "S2A_GF8_WEIGHT_OFFSET[idx]",
        "S2A_GF8_WEIGHT_BYTES[idx]",
        "S2A_GF8_PACKAGE_BASE[idx]",
        "S2A_GF8_PACKAGE_LENGTH[idx]",
        "S2A_GF8_WEIGHT_ADDRESS[idx]",
        "S2A_GF8_BIAS_ADDRESS[idx]",
        "S2A_GF8_BIAS_BYTES[idx]",
        "S2A_T23_MQ_BASE[idx]",
        "S2A_T23_MQ_CHANNEL_COUNT[idx]",
        "S2A_MAXPOOL_DARKNET_PADDING[idx]",
        "S2A_MAXPOOL_ACTUAL_PAD_LEFT[idx]",
        "S2A_MAXPOOL_ACTUAL_PAD_RIGHT[idx]",
        "S2A_MAXPOOL_ACTUAL_PAD_TOP[idx]",
        "S2A_MAXPOOL_ACTUAL_PAD_BOTTOM[idx]",
        "S2A_MAXPOOL_WINDOW_ORIGIN_Y[idx]",
        "S2A_MAXPOOL_WINDOW_ORIGIN_X[idx]",
        "S2A_MAXPOOL_FORMULA[idx]",
        "S2A_UPSAMPLE_SCALE_BITS[idx]",
        "S2A_UPSAMPLE_STRIDE[idx]",
        "S2A_UPSAMPLE_METHOD[idx]",
        "S2A_ROUTE_REQUANTIZATION[idx]",
        "S2A_ROUTE_SLICE_ORDER[idx]",
        "S2A_YOLO_CLASSES[idx]",
        "S2A_YOLO_SCALE_X_Y_BITS[idx]",
        "S2A_YOLO_NEW_COORDS[idx]",
        "S2A_YOLO_HEAD_LOGIT_SCALE_BITS[idx]",
    ]
)
for _slot in range(2):
    LAYER_VECTOR_EXPRESSIONS.append(f"S2A_ROUTE_CHANNEL_START[idx][{_slot}]")
for _slot in range(2):
    LAYER_VECTOR_EXPRESSIONS.append(f"S2A_ROUTE_CHANNEL_END[idx][{_slot}]")
for _slot in range(2):
    LAYER_VECTOR_EXPRESSIONS.append(f"S2A_ROUTE_SOURCE_MULTIPLIER_Q31[idx][{_slot}]")
for _slot in range(6):
    LAYER_VECTOR_EXPRESSIONS.append(f"S2A_YOLO_ANCHOR_W[idx][{_slot}]")
for _slot in range(6):
    LAYER_VECTOR_EXPRESSIONS.append(f"S2A_YOLO_ANCHOR_H[idx][{_slot}]")
for _slot in range(3):
    LAYER_VECTOR_EXPRESSIONS.append(f"S2A_YOLO_MASK[idx][{_slot}]")
LAYER_VECTOR_EXPRESSIONS.extend(
    [
        "S2A_CONV_CANDIDATE_SHA256[idx]",
        "S2A_ROUTE_CONTRACT_SHA256[idx]",
        "S2A_MAXPOOL_FORMULA_SHA256[idx]",
    ]
)

CHANNEL_VECTOR_EXPRESSIONS = [
    "S2A_CONV_CHANNEL_LAYER_INDEX[idx]",
    "S2A_CONV_CHANNEL_INDEX[idx]",
    "S2A_CONV_WEIGHT_SCALE_BITS[idx]",
    "S2A_CONV_FUSED_BIAS_FLOAT32_BITS[idx]",
    "S2A_CONV_BIAS_ACCUMULATOR_INT32[idx]",
    "S2A_T23_MQ_ROM[idx]",
]

LAYER_FIELD_WIDTHS = [
    6, 6, 3, 2,
    *([1, 6, 32, 32, 16, 16, 16, 16, 64, 16, 16] * 2),
    6, 1, 6, 1, 32, 32, 16, 16, 16, 16, 64,
    *([8] * 8), 16, 16, 8, 2, 8, 6,
    *([32] * 10), 16, 16,
    8, 8, 8, 8, 8, 16, 16, 2,
    64, 16, 2, 2, 2,
    16, 64, 8, 64,
    *([16] * 4), *([32] * 2), *([16] * 12), *([16] * 3), *([256] * 3),
]
CHANNEL_FIELD_WIDTHS = [6, 16, 64, 32, 32, 80]
LAYER_RECORD_BITS = sum(LAYER_FIELD_WIDTHS)
CHANNEL_RECORD_BITS = sum(CHANNEL_FIELD_WIDTHS)
LAYER_MEMORY_BITS = ((LAYER_RECORD_BITS + 3) // 4) * 4
CHANNEL_MEMORY_BITS = ((CHANNEL_RECORD_BITS + 3) // 4) * 4


class DynamicRomError(ValueError):
    """冻结输入、独立期望记录或 HDL 绑定不匹配。"""


def _need(condition: bool, message: str) -> None:
    if not condition:
        raise DynamicRomError(message)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


_FILE_ATTRIBUTE_REPARSE_POINT = 0x400


def _assert_path_within(path: Path, allowed_root: Path) -> None:
    full_path = os.path.abspath(os.fspath(path))
    full_root = os.path.abspath(os.fspath(allowed_root))
    try:
        common = os.path.commonpath((full_path, full_root))
    except ValueError as exc:
        raise DynamicRomError(f"路径与允许目录不在同一卷: {path}") from exc
    _need(
        os.path.normcase(common) == os.path.normcase(full_root),
        f"拒绝访问允许目录边界外路径: {path}",
    )


def _assert_no_reparse_chain(path: Path, allow_missing_leaf: bool = False) -> None:
    full_path = os.path.abspath(os.fspath(path))
    drive, tail = os.path.splitdrive(full_path)
    _need(bool(drive), f"路径必须是带盘符的绝对路径: {path}")
    cursor = Path(drive + os.sep)
    components = [item for item in re.split(r"[\\/]", tail) if item]
    for index, component in enumerate(components):
        cursor = cursor / component
        try:
            information = os.lstat(os.fspath(cursor))
        except FileNotFoundError:
            _need(
                allow_missing_leaf and index == len(components) - 1,
                f"路径组件不存在: {cursor}",
            )
            return
        except OSError as exc:
            raise DynamicRomError(f"无法检查路径组件: {cursor}: {exc}") from exc
        _need(
            not (getattr(information, "st_file_attributes", 0) & _FILE_ATTRIBUTE_REPARSE_POINT),
            f"拒绝经过 reparse point: {cursor}",
        )


def _assert_new_output(path: Path, allowed_root: Path) -> None:
    _assert_path_within(path, allowed_root)
    full_path = os.path.abspath(os.fspath(path))
    full_root = os.path.abspath(os.fspath(allowed_root))
    _need(
        os.path.normcase(os.path.dirname(full_path)) == os.path.normcase(full_root),
        f"输出必须是任务目录的直接子项: {path}",
    )
    _assert_no_reparse_chain(allowed_root)
    _assert_no_reparse_chain(path, allow_missing_leaf=True)
    _need(not os.path.lexists(full_path), f"拒绝覆盖已有输出: {path}")


def _write_new_bytes(path: Path, content: bytes, allowed_root: Path) -> None:
    _assert_new_output(path, allowed_root)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0)
    try:
        descriptor = os.open(os.fspath(path), flags, 0o600)
    except OSError as exc:
        raise DynamicRomError(f"无法以 create-new 方式创建输出: {path}: {exc}") from exc
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(content)


def _read_json(path: Path, label: str) -> dict[str, Any]:
    _assert_no_reparse_chain(path)
    try:
        value = json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DynamicRomError(f"{label} 无法按 UTF-8 JSON 读取: {exc}") from exc
    _need(isinstance(value, dict), f"{label} 顶层必须是 object")
    return value


def _u(value: Any, width: int, label: str) -> int:
    _need(isinstance(value, int) and not isinstance(value, bool), f"{label} 必须是整数")
    _need(0 <= value < (1 << width), f"{label} 超出无符号 {width}-bit 范围: {value}")
    return value


def _f64(value: Any, label: str) -> int:
    _need(isinstance(value, (int, float)) and not isinstance(value, bool), f"{label} 必须是数值")
    number = float(value)
    _need(math.isfinite(number), f"{label} 不是有限数")
    return struct.unpack(">Q", struct.pack(">d", number))[0]


def _f32(value: Any, label: str) -> int:
    _need(isinstance(value, (int, float)) and not isinstance(value, bool), f"{label} 必须是数值")
    number = float(value)
    _need(math.isfinite(number), f"{label} 不是有限数")
    try:
        return struct.unpack(">I", struct.pack(">f", number))[0]
    except OverflowError as exc:
        raise DynamicRomError(f"{label} 超出 binary32 范围") from exc


def _shape(value: Any, label: str) -> list[int]:
    _need(
        isinstance(value, list)
        and len(value) == 4
        and all(isinstance(x, int) and not isinstance(x, bool) and 0 < x <= 0xFFFF for x in value),
        f"{label} 必须是四个正 16-bit NCHW 数值",
    )
    return list(value)


def _hash_integer(value: str, label: str) -> int:
    _need(isinstance(value, str) and re.fullmatch(r"[0-9a-fA-F]{64}", value) is not None, f"{label} 必须是 SHA-256")
    return int(value, 16)


def _check_root_and_sources() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, str]]:
    _need(ROOT.is_dir(), f"工程根目录不存在: {ROOT}")
    _need(RUN_DIR.is_dir(), f"任务目录不存在: {RUN_DIR}")
    _assert_no_reparse_chain(ROOT)
    _assert_no_reparse_chain(RUN_DIR)
    _assert_path_within(RUN_DIR, ROOT)
    hashes: dict[str, str] = {}
    for relative, expected in FROZEN_INPUTS.items():
        source = ROOT.joinpath(*relative.split("/"))
        _assert_path_within(source, ROOT)
        _assert_no_reparse_chain(source)
        _need(source.is_file(), f"冻结输入不是文件或不存在: {relative}")
        actual = _sha256(source.read_bytes())
        _need(actual == expected, f"冻结输入 SHA-256 不匹配: {relative}: {actual}")
        hashes[relative] = actual

    manifest = _read_json(ROOT / "report/evidence/S2A-T01/tiny416_model_manifest.json", "T01 manifest")
    contract = _read_json(
        ROOT / "report/evidence/S2A-T22/network_dispatch_contract_validation.json",
        "T22 contract",
    )
    table = _read_json(ROOT / "report/evidence/S2A-T23/conv_requant_parameter_table.json", "T23 表")
    package = ROOT / PACKAGE_REL
    _assert_no_reparse_chain(package)
    _need(package.is_file(), f"描述符包不是文件或不存在: {PACKAGE_REL}")
    return manifest, contract, table, hashes


def _check_bindings(
    manifest: dict[str, Any], contract: dict[str, Any], table: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[int, dict[str, Any]]]:
    _need(manifest.get("schema_version") == "gestureforge_s2a_model_manifest_v1", "T01 manifest schema 不匹配")
    _need(manifest.get("status") == "G0_FROZEN", "T01 manifest 未冻结")
    _need(manifest.get("model", {}).get("model_id") == "tiny416", "manifest 不是 tiny416")
    manifest_layers = manifest.get("layers")
    _need(isinstance(manifest_layers, list) and len(manifest_layers) == 38, "manifest 必须有 38 层")

    _need(contract.get("schema_version") == "gestureforge_s2a_network_dispatch_contract_v1", "T22 schema 不匹配")
    _need(contract.get("task_id") == "S2A-T22", "T22 task_id 不匹配")
    _need(contract.get("artifact_status") == "CONTRACT_VALIDATED", "T22 contract 未验证")
    dispatch = contract.get("network_dispatch")
    contract_layers = dispatch.get("layers") if isinstance(dispatch, dict) else None
    _need(isinstance(contract_layers, list) and len(contract_layers) == 38, "T22 必须有 38 层")
    _need(dispatch.get("layer_count") == 38, "T22 layer_count 不匹配")
    _need(dispatch.get("operator_counts") == OP_COUNTS, "T22 operator distribution 不匹配")

    manifest_path = "report/evidence/S2A-T01/tiny416_model_manifest.json"
    contract_path = "report/evidence/S2A-T22/network_dispatch_contract_validation.json"
    contract_source = [
        item for item in contract.get("source_bindings", [])
        if isinstance(item, dict) and item.get("path") == manifest_path
    ]
    _need(len(contract_source) == 1, "T22 必须且只能绑定当前 T01 manifest")
    _need(contract_source[0].get("sha256") == FROZEN_INPUTS[manifest_path], "T22 manifest binding 不匹配")

    _need(table.get("schema_version") == "gestureforge_s2a_conv_requant_parameter_table_v1", "T23 schema 不匹配")
    _need(table.get("status") == "ALL_CHANNELS_EXACT_AND_T16_DIGEST_MATCH", "T23 状态不匹配")
    table_sources = table.get("source_bindings")
    _need(isinstance(table_sources, list), "T23 source_bindings 缺失")
    for relative in (manifest_path, contract_path):
        matches = [
            item for item in table_sources
            if isinstance(item, dict) and item.get("path") == relative
        ]
        _need(len(matches) == 1, f"T23 必须且只能绑定 {relative}")
        _need(matches[0].get("sha256") == FROZEN_INPUTS[relative], f"T23 {relative} SHA 不匹配")

    table_layers = table.get("layers")
    _need(isinstance(table_layers, list) and len(table_layers) == OP_COUNTS["convolutional"], "T23 必须有 21 个卷积表项")
    table_by_layer = {item.get("layer_index"): item for item in table_layers if isinstance(item, dict)}
    _need(len(table_by_layer) == len(table_layers), "T23 layer_index 重复")
    expected_conv_indices = [i for i, row in enumerate(manifest_layers) if row.get("op") == "convolutional"]
    _need([item.get("layer_index") for item in table_layers] == expected_conv_indices, "T23 卷积层排序不匹配")
    return contract_layers, table_by_layer


def _route_multiplier_q31(source_scale: Any, target_scale: Any, label: str) -> int:
    source = float(source_scale)
    target = float(target_scale)
    _need(math.isfinite(source) and source > 0.0, f"{label} 源 scale 非法")
    _need(math.isfinite(target) and target > 0.0, f"{label} 目标 scale 非法")
    ratio = source / target
    _need(math.isfinite(ratio) and 0.0 < ratio <= 1.0, f"{label} scale 比例不在 (0,1]")
    result = math.floor(ratio * (1 << 31) + 0.5)
    _need(1 <= result <= (1 << 31), f"{label} Q31 超出范围")
    return result


def _contract_input_check(
    contract_input: dict[str, Any], index: int, slot: int, reference: Any, expected: dict[str, Any]
) -> None:
    _need(contract_input.get("input_order") == slot, f"layer {index} 输入槽 {slot} 顺序不匹配")
    if reference == "network_input":
        _need(contract_input.get("kind") == "network_input", f"layer {index} 输入槽 {slot} kind 不匹配")
        _need(contract_input.get("source_index") == "network_input", f"layer {index} 输入槽 {slot} 来源不匹配")
    else:
        _need(contract_input.get("kind") == "layer_output", f"layer {index} 输入槽 {slot} kind 不匹配")
        _need(contract_input.get("source_index") == reference, f"layer {index} 输入槽 {slot} 来源不匹配")
    _need(contract_input.get("address") == expected["address"], f"layer {index} 输入槽 {slot} 地址不匹配")
    _need(contract_input.get("length_bytes") == expected["length_bytes"], f"layer {index} 输入槽 {slot} 长度不匹配")
    _need(contract_input.get("shape_nchw") == expected["shape_nchw"], f"layer {index} 输入槽 {slot} shape 不匹配")
    _need(contract_input.get("scale") == expected["scale"], f"layer {index} 输入槽 {slot} scale 不匹配")


def _build_layer_record_values(
    index: int,
    layer: dict[str, Any],
    contract_layer: dict[str, Any],
    manifest: dict[str, Any],
    table_layer: dict[str, Any] | None,
    mq_base: int,
) -> tuple[list[tuple[int, int]], int]:
    op = layer.get("op")
    _need(op in OP_CODE, f"layer {index} op 不支持")
    _need(layer.get("layer_index") == index, f"manifest layer {index} index 不匹配")
    _need(layer.get("cfg_section") == index + 1, f"manifest layer {index} cfg section 不匹配")
    _need(contract_layer.get("dispatch_order") == index, f"T22 layer {index} dispatch order 不匹配")
    _need(contract_layer.get("layer_index") == index, f"T22 layer {index} index 不匹配")
    _need(contract_layer.get("cfg_section") == index + 1, f"T22 layer {index} cfg section 不匹配")
    _need(contract_layer.get("op") == op, f"T22 layer {index} op 不匹配")

    refs = layer.get("input_tensor_indices")
    contract_inputs = contract_layer.get("input_tensors_in_manifest_order")
    _need(isinstance(refs, list) and 1 <= len(refs) <= 2, f"layer {index} 输入数不合法")
    _need(isinstance(contract_inputs, list) and len(contract_inputs) == len(refs), f"T22 layer {index} 输入数不匹配")
    range_rows = layer.get("route_source_channel_ranges", [])
    _need(isinstance(range_rows, list), f"layer {index} route channel ranges 类型不匹配")
    inputs: list[dict[str, Any]] = []
    for slot, reference in enumerate(refs):
        if reference == "network_input":
            _need(index == 0 and slot == 0, "network input 只允许作为 layer 0 的输入")
            source = manifest["address_map"]["input"]
            item = {
                "kind": 0,
                "source_index": 0x3F,
                "address": source["address"],
                "length_bytes": source["length_bytes"],
                "shape_nchw": _shape(source["shape_nchw"], f"layer {index} network input shape"),
                "scale": source["scale"],
            }
        else:
            _need(isinstance(reference, int) and not isinstance(reference, bool) and 0 <= reference < index, f"layer {index} 输入引用非法")
            source_layer = manifest["layers"][reference]
            _need(source_layer.get("op") != "yolo", f"layer {index} 不能引用 YOLO alias")
            item = {
                "kind": 1,
                "source_index": reference,
                "address": source_layer["tensor_address"],
                "length_bytes": source_layer["tensor_length_bytes"],
                "shape_nchw": _shape(source_layer["output_shape_nchw"], f"layer {reference} 输出 shape"),
                "scale": source_layer["output_scale"],
            }
        _contract_input_check(contract_inputs[slot], index, slot, reference, item)
        inputs.append(item)

    contract_parameters = contract_layer.get("operator_parameters")
    _need(isinstance(contract_parameters, dict), f"T22 layer {index} operator_parameters 缺失")
    for key in {
        "convolutional": (
            "kernel_hw", "stride_hw", "padding_lrtb", "groups", "padding_value_int8",
            "activation", "accumulator_bits", "output_scale", "weight_layer_index",
            "gf8_parameter_offsets",
        ),
        "maxpool": (
            "kernel_hw", "stride_hw", "darknet_padding_parameter", "output_hw_formula",
            "window_origin_yx_at_output_0", "padding_lrtb_actual", "pad_value_int8", "output_scale",
        ),
        "route": (
            "route_groups", "route_group_id", "route_source_channel_ranges",
            "route_group_slice_order", "requantization", "output_scale",
        ),
        "upsample": ("scale", "stride", "method", "output_scale"),
        "yolo": (
            "output_tensor_index", "classes", "scale_x_y", "new_coords",
            "head_logit_scale", "output_scale",
        ),
    }[op]:
        _need(contract_parameters.get(key) == layer.get(key), f"T22 layer {index} 参数 {key} 不匹配")

    shape = _shape(layer["output_shape_nchw"], f"layer {index} 输出 shape")
    output_address = _u(layer["tensor_address"], 32, f"layer {index} 输出地址")
    output_length = _u(layer["tensor_length_bytes"], 32, f"layer {index} 输出长度")
    _need(math.prod(shape) == output_length, f"layer {index} 输出 length != NCHW 元素数")
    output_scale_bits = _f64(layer["output_scale"], f"layer {index} 输出 scale")
    tensor_index = layer.get("output_tensor_index", index)
    is_yolo = op == "yolo"
    alias_layer = refs[0] if is_yolo else 0x3F
    _need(contract_layer["output_tensor"].get("tensor_index") == tensor_index, f"T22 layer {index} 输出 tensor index 不匹配")
    _need(contract_layer["output_tensor"].get("address") == output_address, f"T22 layer {index} 输出地址不匹配")
    _need(contract_layer["output_tensor"].get("length_bytes") == output_length, f"T22 layer {index} 输出长度不匹配")
    _need(contract_layer["output_tensor"].get("shape_nchw") == shape, f"T22 layer {index} 输出 shape 不匹配")
    _need(contract_layer["output_tensor"].get("scale") == layer["output_scale"], f"T22 layer {index} 输出 scale 不匹配")

    channels_count = 0
    candidate_sha = 0
    is_yolo = op == "yolo"
    expected_alias = refs[0] if is_yolo else None
    output_contract = contract_layer["output_tensor"]
    _need(
        output_contract.get("allocation_kind") == ("head_alias" if is_yolo else "owned_feature_tensor"),
        f"T22 layer {index} allocation_kind 不匹配",
    )
    _need(output_contract.get("alias_of_layer_index") == expected_alias, f"T22 layer {index} alias target 不匹配")
    _need(output_contract.get("memory_write_required") is (not is_yolo), f"T22 layer {index} write policy 不匹配")
    if is_yolo:
        _need(isinstance(expected_alias, int), f"YOLO layer {index} alias source 必须是层号")
        source_layer = manifest["layers"][expected_alias]
        _need(output_address == source_layer["tensor_address"], f"YOLO layer {index} alias address 不匹配")
        _need(output_length == source_layer["tensor_length_bytes"], f"YOLO layer {index} alias length 不匹配")
        _need(shape == source_layer["output_shape_nchw"], f"YOLO layer {index} alias shape 不匹配")
        _need(output_scale_bits == _f64(source_layer["output_scale"], f"YOLO layer {index} source scale"), f"YOLO layer {index} alias scale 不匹配")

    if op == "convolutional":
        _need(isinstance(table_layer, dict), f"layer {index} 缺少 T23 表")
        channels = table_layer.get("channels")
        _need(isinstance(channels, list) and len(channels) == shape[1], f"layer {index} T23 channel count 不匹配")
        _need(table_layer.get("cfg_section") == index + 1, f"layer {index} T23 cfg_section 不匹配")
        _need(table_layer.get("activation") == layer["activation"], f"layer {index} T23 activation 不匹配")
        _need(table_layer.get("channel_count") == shape[1], f"layer {index} T23 channel_count 不匹配")
        stream = "".join(
            f"{item['channel']},{item['positive_Q']},{item['positive_M']},{item['negative_Q']},{item['negative_M']}\n"
            for item in channels
        ).encode("ascii")
        candidate_digest = _sha256(stream)
        _need(candidate_digest == table_layer.get("candidate_parameter_sha256"), f"layer {index} T23 candidate digest 不匹配")
        candidate_sha = _hash_integer(candidate_digest, f"layer {index} candidate digest")
        channels_count = len(channels)
        _need(layer.get("weight_layer_index") == index, f"layer {index} 权重层索引不匹配")
    else:
        _need(table_layer is None, f"非卷积 layer {index} 出现在 T23")

    p = layer
    kernel = p.get("kernel_hw", [0, 0])
    stride = p.get("stride_hw", [0, 0])
    padding = p.get("padding_lrtb", [0, 0, 0, 0])
    maxpool_padding = p.get("padding_lrtb_actual", [0, 0, 0, 0])
    window_origin = p.get("window_origin_yx_at_output_0", [0, 0])
    offsets = p.get("gf8_parameter_offsets", {}) if op == "convolutional" else {}
    package = manifest["address_map"]["weight_package"]
    if op == "route":
        route_ranges = p.get("route_source_channel_ranges")
        _need(isinstance(route_ranges, list) and len(route_ranges) == len(inputs), f"layer {index} route slice 数不匹配")
        route_input_scales = p.get("input_scales")
        _need(isinstance(route_input_scales, list) and len(route_input_scales) == len(inputs), f"layer {index} route input scale 数不匹配")
        for slot, item in enumerate(inputs):
            _need(
                _f64(route_input_scales[slot], f"layer {index} route input scale {slot}")
                == _f64(item["scale"], f"layer {index} input descriptor scale {slot}"),
                f"layer {index} route input scale {slot} 与输入描述符不一致",
            )
        route_multipliers = [
            _route_multiplier_q31(route_input_scales[slot], p["output_scale"], f"layer {index} route {slot}")
            for slot in range(len(inputs))
        ]
        route_bytes = (str(p["route_group_slice_order"]) + "\n" + str(p["requantization"])).encode("utf-8")
        route_digest = _hash_integer(_sha256(route_bytes), f"layer {index} route digest")
    else:
        route_ranges = []
        route_multipliers = []
        route_digest = 0
    if op == "maxpool":
        maxpool_digest = _hash_integer(_sha256(str(p["output_hw_formula"]).encode("utf-8")), f"layer {index} maxpool digest")
    else:
        maxpool_digest = 0

    values: list[tuple[int, int]] = []

    def put(value: Any, width: int, label: str) -> None:
        values.append((_u(value, width, label), width))

    def put_scale(value: Any, label: str) -> None:
        put(_f64(value, label), 64, label)

    def put_signed_byte(value: Any, label: str) -> None:
        _need(isinstance(value, int) and not isinstance(value, bool) and -128 <= value <= 127, f"{label} 超出 INT8 范围")
        put(value & 0xFF, 8, label)

    put(index, 6, f"layer {index} index")
    put(index + 1, 6, f"layer {index} cfg_section")
    put(OP_CODE[op], 3, f"layer {index} op")
    put(len(inputs), 2, f"layer {index} input count")
    for slot in range(2):
        if slot < len(inputs):
            item = inputs[slot]
            route_range = route_ranges[slot] if slot < len(route_ranges) else [0, 0]
            _need(isinstance(route_range, list) and len(route_range) == 2, f"layer {index} route range {slot} 非法")
            fields = (
                (item["kind"], 1, "input kind"),
                (item["source_index"], 6, "input source"),
                (item["address"], 32, "input address"),
                (item["length_bytes"], 32, "input length"),
                (*item["shape_nchw"][:1], 16, "input N"),
                (item["shape_nchw"][1], 16, "input C"),
                (item["shape_nchw"][2], 16, "input H"),
                (item["shape_nchw"][3], 16, "input W"),
            )
            for value, width, name in fields:
                put(value, width, f"layer {index} slot {slot} {name}")
            put_scale(item["scale"], f"layer {index} slot {slot} scale")
            put(route_range[0], 16, f"layer {index} slot {slot} route start")
            put(route_range[1], 16, f"layer {index} slot {slot} route end")
        else:
            for value, width in ((0, 1), (0x3F, 6), (0, 32), (0, 32), (0, 16), (0, 16), (0, 16), (0, 16), (0, 64), (0, 16), (0, 16)):
                put(value, width, f"layer {index} unused input slot {slot}")

    put(tensor_index, 6, f"layer {index} output tensor index")
    put(int(is_yolo), 1, f"layer {index} output allocation")
    put(alias_layer, 6, f"layer {index} alias layer")
    put(int(not is_yolo), 1, f"layer {index} memory write flag")
    put(output_address, 32, f"layer {index} output address")
    put(output_length, 32, f"layer {index} output length")
    for dimension, dimension_name in zip(shape, ("N", "C", "H", "W")):
        put(dimension, 16, f"layer {index} output {dimension_name}")
    put(output_scale_bits, 64, f"layer {index} output scale")

    for value, name in zip(kernel, ("kernel H", "kernel W")):
        put(value, 8, f"layer {index} {name}")
    for value, name in zip(stride, ("stride H", "stride W")):
        put(value, 8, f"layer {index} {name}")
    for value, name in zip(padding, ("left pad", "right pad", "top pad", "bottom pad")):
        put(value, 8, f"layer {index} {name}")
    put(p.get("groups", p.get("route_groups", 0)), 16, f"layer {index} groups")
    put(p.get("route_group_id", 0), 16, f"layer {index} route group id")
    put_signed_byte(p.get("padding_value_int8", p.get("pad_value_int8", 0)), f"layer {index} padding value")
    put({"": 0, "linear": 1, "leaky": 2}.get(p.get("activation", ""), 0), 2, f"layer {index} activation")
    put(p.get("accumulator_bits", 0), 8, f"layer {index} accumulator bits")
    put(p.get("weight_layer_index", 0x3F), 6, f"layer {index} weight layer index")

    for key in ("record_offset", "weight_scale_offset", "fused_bias_offset", "quantized_weight_offset", "quantized_weight_bytes"):
        put(offsets.get(key, 0), 32, f"layer {index} GF8 {key}")
    package_base = package["address"] if op == "convolutional" else 0
    package_length = package["length_bytes"] if op == "convolutional" else 0
    put(package_base, 32, f"layer {index} GF8 package base")
    put(package_length, 32, f"layer {index} GF8 package length")
    put(package_base + offsets.get("quantized_weight_offset", 0) if op == "convolutional" else 0, 32, f"layer {index} GF8 weight address")
    put(package_base + offsets.get("fused_bias_offset", 0) if op == "convolutional" else 0, 32, f"layer {index} GF8 bias address")
    put(4 * channels_count, 32, f"layer {index} GF8 bias bytes")
    put(mq_base if op == "convolutional" else 0, 16, f"layer {index} M/Q base")
    put(channels_count, 16, f"layer {index} M/Q channel count")

    put(p.get("darknet_padding_parameter", 0), 8, f"layer {index} maxpool cfg padding")
    for value, name in zip(maxpool_padding, ("left", "right", "top", "bottom")):
        put(value, 8, f"layer {index} maxpool actual {name} padding")
    for value, name in zip(window_origin, ("Y", "X")):
        put(value, 16, f"layer {index} maxpool origin {name}")
    put(int(op == "maxpool"), 2, f"layer {index} maxpool formula")
    put(_f64(p["scale"], f"layer {index} upsample scale") if op == "upsample" else 0, 64, f"layer {index} upsample scale bits")
    put(p.get("stride", 0) if op == "upsample" else 0, 16, f"layer {index} upsample stride")
    put(int(op == "upsample"), 2, f"layer {index} upsample method")
    put(int(op == "route"), 2, f"layer {index} route requantization")
    put(int(op == "route"), 2, f"layer {index} route slice order")
    put(p.get("classes", 0), 16, f"layer {index} YOLO classes")
    put(_f64(p["scale_x_y"], f"layer {index} YOLO scale_x_y") if op == "yolo" else 0, 64, f"layer {index} YOLO scale_x_y bits")
    put(p.get("new_coords", 0), 8, f"layer {index} YOLO new_coords")
    put(_f64(p["head_logit_scale"], f"layer {index} head logit scale") if op == "yolo" else 0, 64, f"layer {index} YOLO head scale bits")

    for ranges in (
        [route_ranges[slot] if slot < len(route_ranges) else [0, 0] for slot in range(2)],
    ):
        for route_range in ranges:
            put(route_range[0], 16, f"layer {index} route start")
    for ranges in (
        [route_ranges[slot] if slot < len(route_ranges) else [0, 0] for slot in range(2)],
    ):
        for route_range in ranges:
            put(route_range[1], 16, f"layer {index} route end")
    for slot in range(2):
        put(route_multipliers[slot] if slot < len(route_multipliers) else 0, 32, f"layer {index} route Q31 {slot}")

    anchors = p.get("anchors_wh", [[0, 0]] * 6) if op == "yolo" else [[0, 0]] * 6
    masks = p.get("mask", [0] * 3) if op == "yolo" else [0] * 3
    if op == "yolo":
        _need(anchors == EXPECTED_ANCHORS, f"layer {index} YOLO anchors 不匹配冻结值")
        _need(masks == EXPECTED_MASKS[index], f"layer {index} YOLO mask 不匹配冻结值")
    _need(len(anchors) == 6 and all(isinstance(item, list) and len(item) == 2 for item in anchors), f"layer {index} anchors 格式不匹配")
    _need(len(masks) == 3, f"layer {index} mask 长度不匹配")
    for item in anchors:
        put(item[0], 16, f"layer {index} anchor width")
    for item in anchors:
        put(item[1], 16, f"layer {index} anchor height")
    for item in masks:
        put(item, 16, f"layer {index} anchor mask")
    put(candidate_sha, 256, f"layer {index} candidate SHA")
    put(route_digest, 256, f"layer {index} route SHA")
    put(maxpool_digest, 256, f"layer {index} maxpool SHA")

    _need(len(values) == len(LAYER_VECTOR_EXPRESSIONS), f"layer {index} 序列化字段数错误")
    _need(sum(width for _, width in values) == LAYER_RECORD_BITS, f"layer {index} 序列化位宽错误")
    return values, channels_count


def _build_expected(
    manifest: dict[str, Any],
    contract: dict[str, Any],
    table: dict[str, Any],
) -> tuple[list[int], list[int], dict[str, int]]:
    contract_layers, table_by_layer = _check_bindings(manifest, contract, table)
    layer_records: list[int] = []
    channel_records: list[int] = []
    op_counts = {name: 0 for name in OP_FIELD_ORDER}
    mq_base = 0
    for index, layer in enumerate(manifest["layers"]):
        op = layer["op"]
        op_counts[op] += 1
        table_layer = table_by_layer.get(index)
        fields, channel_count = _build_layer_record_values(
            index, layer, contract_layers[index], manifest, table_layer, mq_base
        )
        packed = 0
        for value, width in fields:
            packed = (packed << width) | value
        layer_records.append(packed)
        if op == "convolutional":
            channels = table_layer["channels"]
            scales = layer.get("weight_scale_per_output_channel")
            biases = layer.get("fused_bias_float32_per_output_channel")
            accumulator_biases = layer.get("bias_accumulator_int32_per_output_channel")
            _need(isinstance(scales, list) and len(scales) == channel_count, f"layer {index} weight scale 列表长度不匹配")
            _need(isinstance(biases, list) and len(biases) == channel_count, f"layer {index} fused bias 列表长度不匹配")
            _need(isinstance(accumulator_biases, list) and len(accumulator_biases) == channel_count, f"layer {index} accumulator bias 列表长度不匹配")
            for channel_index, item in enumerate(channels):
                _need(item.get("channel") == channel_index, f"layer {index} channel index 不连续")
                _need(1 <= item.get("positive_M", 0) <= 0xFFFFFFFF, f"layer {index} channel {channel_index} positive_M 非法")
                _need(1 <= item.get("negative_M", 0) <= 0xFFFFFFFF, f"layer {index} channel {channel_index} negative_M 非法")
                _need(0 <= item.get("positive_Q", -1) <= 65, f"layer {index} channel {channel_index} positive_Q 超出 T23 范围")
                _need(0 <= item.get("negative_Q", -1) <= 65, f"layer {index} channel {channel_index} negative_Q 超出 T23 范围")
                accumulator_bias = accumulator_biases[channel_index]
                _need(
                    isinstance(accumulator_bias, int)
                    and not isinstance(accumulator_bias, bool)
                    and -(1 << 31) <= accumulator_bias < (1 << 31),
                    f"layer {index} channel {channel_index} accumulator bias 超出 INT32",
                )
                channel_values: list[tuple[int, int]] = [
                    (_u(index, 6, f"layer {index} channel layer index"), 6),
                    (_u(channel_index, 16, f"layer {index} channel index"), 16),
                    (_f64(scales[channel_index], f"layer {index} weight scale"), 64),
                    (_f32(biases[channel_index], f"layer {index} fused bias"), 32),
                    (_u(accumulator_biases[channel_index] & 0xFFFFFFFF, 32, f"layer {index} accumulator bias"), 32),
                ]
                mq = (
                    (_u(item["positive_M"], 32, "positive M") << 48)
                    | (_u(item["positive_Q"], 8, "positive Q") << 40)
                    | (_u(item["negative_M"], 32, "negative M") << 8)
                    | _u(item["negative_Q"], 8, "negative Q")
                )
                channel_values.append((mq, 80))
                _need(sum(width for _, width in channel_values) == CHANNEL_RECORD_BITS, "channel record 位宽错误")
                packed_channel = 0
                for value, width in channel_values:
                    packed_channel = (packed_channel << width) | value
                channel_records.append(packed_channel)
            mq_base += channel_count
    _need(op_counts == OP_COUNTS, f"manifest operator distribution 不匹配: {op_counts}")
    _need(len(layer_records) == 38, "期望描述符记录数不是 38")
    _need(len(channel_records) == TOTAL_CHANNELS and mq_base == TOTAL_CHANNELS, "期望 M/Q 通道记录数不是 3164")
    return layer_records, channel_records, op_counts


def _hex_lines(records: list[int], width_bits: int) -> bytes:
    digits = width_bits // 4
    return ("\n".join(f"{item:0{digits}X}" for item in records) + "\n").encode("ascii")


def check_fixture_bytes(actual: bytes, expected: bytes, label: str) -> None:
    _need(actual == expected, f"{label} 不等于冻结 JSON 的独立重建结果")


def _declared_package_names(package_text: str) -> tuple[set[str], set[str]]:
    declarations = re.findall(
        r"^\s*localparam\b[^\n]*?\b(S2A_[A-Z0-9_]+)\s*(\[|=)",
        package_text,
        re.MULTILINE,
    )
    arrays = {name for name, suffix in declarations if suffix == "["}
    scalars = {name for name, suffix in declarations if suffix == "="}
    return arrays, scalars


def _declared_package_widths(package_text: str) -> dict[str, int]:
    matches = re.findall(
        r"^\s*localparam\s+logic\s+\[(\d+):(\d+)\]\s+(S2A_[A-Z0-9_]+)\b[^\n]*=",
        package_text,
        re.MULTILINE,
    )
    return {name: abs(int(msb) - int(lsb)) + 1 for msb, lsb, name in matches}


def _parse_package_arrays(package_text: str) -> tuple[dict[str, list[int]], dict[str, tuple[int, ...]]]:
    declaration = re.compile(
        r"^\s*localparam\s+logic\s+\[(\d+):(\d+)\]\s+(S2A_[A-Z0-9_]+)\s*((?:\s*\[\d+:\d+\])+)\s*=\s*'\{(.*?)\};",
        re.MULTILINE | re.DOTALL,
    )
    numeral = re.compile(r"(?:(\d+)'([hHdDbBoO])([0-9a-fA-F_xXzZ?]+)|(-?\d+))")
    base_by_letter = {"h": 16, "d": 10, "b": 2, "o": 8}
    values_by_name: dict[str, list[int]] = {}
    dimensions_by_name: dict[str, tuple[int, ...]] = {}
    for msb, lsb, name, dimensions, initializer in declaration.findall(package_text):
        width = abs(int(msb) - int(lsb)) + 1
        shape = tuple(int(high) + 1 for _, high in re.findall(r"\[(\d+):(\d+)\]", dimensions))
        body = re.sub(r"//[^\n]*", "", initializer)
        parsed: list[int] = []
        for match in numeral.finditer(body):
            size, base_letter, digits, decimal = match.groups()
            if decimal is not None:
                number = int(decimal, 10)
            else:
                _need(size is not None and base_letter is not None and digits is not None, f"{name} 字面量解析失败")
                _need(not re.search(r"[xXzZ?]", digits), f"{name} initializer 含有未知位")
                number = int(digits.replace("_", ""), base_by_letter[base_letter.lower()])
            _need(0 <= number < (1 << width), f"{name} initializer 超出 {width}-bit")
            parsed.append(number)
        remainder = numeral.sub(" ", body)
        _need(not remainder.strip(" \t\r\n{}',"), f"{name} initializer 含有未解析字符")
        _need(name not in values_by_name, f"package array 重复声明: {name}")
        values_by_name[name] = parsed
        dimensions_by_name[name] = shape
    return values_by_name, dimensions_by_name


def _decode_records(records: list[int], widths: list[int], record_bits: int, memory_bits: int) -> list[list[int]]:
    pad_bits = memory_bits - record_bits
    _need(pad_bits >= 0, "fixture memory 位宽小于有效记录位宽")
    decoded_records: list[list[int]] = []
    for record in records:
        _need(0 <= record < (1 << memory_bits), "fixture record 超出 memory 位宽")
        _need(record >> record_bits == 0, "fixture 高位填充必须为零")
        packed = record & ((1 << record_bits) - 1)
        values = [0] * len(widths)
        for position in range(len(widths) - 1, -1, -1):
            width = widths[position]
            values[position] = packed & ((1 << width) - 1)
            packed >>= width
        _need(packed == 0, "fixture record 解码后仍有剩余位")
        decoded_records.append(values)
    return decoded_records


def cross_check_package_literals(
    layer_records: list[int], channel_records: list[int]
) -> dict[str, int]:
    """将独立期望 fixture 解码后与 package 源文本中的所有数组常量逐项比较。"""
    package_path = ROOT / PACKAGE_REL
    _assert_no_reparse_chain(package_path)
    package_text = package_path.read_text(encoding="utf-8")
    package_values, package_dimensions = _parse_package_arrays(package_text)
    expected_values: dict[str, list[int]] = {
        expression.split("[", 1)[0]: []
        for expression in LAYER_VECTOR_EXPRESSIONS + CHANNEL_VECTOR_EXPRESSIONS
    }
    for record_values in _decode_records(
        layer_records, LAYER_FIELD_WIDTHS, LAYER_RECORD_BITS, LAYER_MEMORY_BITS
    ):
        for expression, value in zip(LAYER_VECTOR_EXPRESSIONS, record_values):
            expected_values[expression.split("[", 1)[0]].append(value)
    for record_values in _decode_records(
        channel_records, CHANNEL_FIELD_WIDTHS, CHANNEL_RECORD_BITS, CHANNEL_MEMORY_BITS
    ):
        for expression, value in zip(CHANNEL_VECTOR_EXPRESSIONS, record_values):
            expected_values[expression.split("[", 1)[0]].append(value)

    _need(set(package_values) == set(expected_values), "package array initializer 集合与独立 fixture 不同")
    layer_array_names = {
        expression.split("[", 1)[0]
        for expression in LAYER_VECTOR_EXPRESSIONS
    }
    for name, expected in expected_values.items():
        actual = package_values[name]
        _need(len(actual) == len(expected), f"{name} package 元素数不匹配: {len(actual)} != {len(expected)}")
        first_difference = next(
            (index for index, (left, right) in enumerate(zip(actual, expected)) if left != right),
            None,
        )
        if first_difference is not None:
            raise DynamicRomError(
                f"{name}[flat={first_difference}] package={actual[first_difference]:X} "
                f"fixture={expected[first_difference]:X}"
            )
        if name in layer_array_names:
            _need(len(package_dimensions[name]) in (1, 2), f"{name} package dimension rank mismatch")
            _need(package_dimensions[name][0] == 38, f"{name} package layer dimension mismatch")
        else:
            _need(package_dimensions[name] == (3164,), f"{name} package channel dimension mismatch")
        _need(math.prod(package_dimensions[name]) == len(expected), f"{name} package declared dimensions mismatch")
    return {"array_count": len(expected_values), "array_element_count": sum(map(len, expected_values.values()))}


def _check_hdl_scope() -> dict[str, Any]:
    _assert_no_reparse_chain(RUN_DIR)
    package_path = ROOT / PACKAGE_REL
    tb_path = RUN_DIR / TB_NAME
    runner_path = RUN_DIR / RUNNER_NAME
    verifier_path = RUN_DIR / VERIFIER_NAME
    test_path = RUN_DIR / TEST_NAME
    for path, label in (
        (package_path, "描述符 package"),
        (tb_path, "动态 ROM TB"),
        (runner_path, "运行脚本"),
        (verifier_path, "独立 expected 构造器"),
        (test_path, "离线测试"),
    ):
        _assert_no_reparse_chain(path)
        _need(path.is_file(), f"{label} 不是文件或不存在: {path}")
    package_text = package_path.read_text(encoding="utf-8")
    tb_text = tb_path.read_text(encoding="utf-8")
    arrays, scalars = _declared_package_names(package_text)
    expected_arrays = {
        expression.split("[", 1)[0]
        for expression in LAYER_VECTOR_EXPRESSIONS + CHANNEL_VECTOR_EXPRESSIONS
    }
    _need(arrays == expected_arrays, f"TB ROM array 覆盖集合不完整: missing={sorted(arrays - expected_arrays)} extra={sorted(expected_arrays - arrays)}")
    tb_references = set(re.findall(r"\bS2A_[A-Z0-9_]+\b", tb_text))
    _need(scalars <= tb_references, f"TB 未检查 package scalar 常量: {sorted(scalars - tb_references)}")
    widths = _declared_package_widths(package_text)
    try:
        actual_layer_widths = [widths[item.split("[", 1)[0]] for item in LAYER_VECTOR_EXPRESSIONS]
        actual_channel_widths = [widths[item.split("[", 1)[0]] for item in CHANNEL_VECTOR_EXPRESSIONS]
    except KeyError as exc:
        raise DynamicRomError(f"package 字段位宽缺失: {exc}") from exc
    _need(actual_layer_widths == LAYER_FIELD_WIDTHS, "TB layer fixture 位宽与 package 声明顺序不匹配")
    _need(actual_channel_widths == CHANNEL_FIELD_WIDTHS, "TB channel fixture 位宽与 package 声明顺序不匹配")
    actual_layer = _function_expression_refs(tb_text, "actual_layer")
    actual_channel = _function_expression_refs(tb_text, "actual_channel")
    _need(actual_layer == LAYER_VECTOR_EXPRESSIONS, "TB actual_layer 字段顺序与独立 expected fixture 绑定不一致")
    _need(actual_channel == CHANNEL_VECTOR_EXPRESSIONS, "TB actual_channel 字段顺序与独立 expected fixture 绑定不一致")
    return {
        "package_sha256": _sha256(package_path.read_bytes()),
        "tb_sha256": _sha256(tb_path.read_bytes()),
        "runner_sha256": _sha256(runner_path.read_bytes()),
        "verifier_sha256": _sha256(verifier_path.read_bytes()),
        "test_sha256": _sha256(test_path.read_bytes()),
        "package_array_count": len(arrays),
        "package_scalar_count": len(scalars),
        "layer_fields_per_record": len(LAYER_VECTOR_EXPRESSIONS),
        "layer_record_bits": LAYER_RECORD_BITS,
        "channel_fields_per_record": len(CHANNEL_VECTOR_EXPRESSIONS),
        "channel_record_bits": CHANNEL_RECORD_BITS,
    }


def _function_expression_refs(text: str, function_name: str) -> list[str]:
    match = re.search(
        rf"function\s+automatic\s+logic\s+\[[^\]]+\]\s+{re.escape(function_name)}\b(.*?)endfunction",
        text,
        re.DOTALL,
    )
    _need(match is not None, f"TB 缺少 {function_name} function")
    return [
        re.sub(r"\s+", "", item)
        for item in re.findall(r"\bS2A_[A-Z0-9_]+\s*(?:\[[^\]]+\]){1,2}", match.group(1))
    ]


def _write_utf8(path: Path, content: bytes) -> None:
    _write_new_bytes(path, content, RUN_DIR)


def prepare() -> dict[str, Any]:
    manifest, contract, table, input_hashes = _check_root_and_sources()
    layer_records, channel_records, op_counts = _build_expected(manifest, contract, table)
    scope = _check_hdl_scope()
    layer_bytes = _hex_lines(layer_records, LAYER_MEMORY_BITS)
    channel_bytes = _hex_lines(channel_records, CHANNEL_MEMORY_BITS)
    layer_path = RUN_DIR / LAYER_FIXTURE_NAME
    channel_path = RUN_DIR / CHANNEL_FIXTURE_NAME
    manifest_path = RUN_DIR / MANIFEST_NAME
    for output_path in (layer_path, channel_path, manifest_path):
        _assert_new_output(output_path, RUN_DIR)
    _write_utf8(layer_path, layer_bytes)
    _write_utf8(channel_path, channel_bytes)
    binding = {
        "schema_version": "s2a_t63_dynamic_rom_fixture_binding_v1",
        "task_id": "S2A-T63-DYNAMIC-ROM",
        "status": "FIXTURE_PREPARED_NOT_SIMULATED",
        "source": "独立解析冻结 T01 manifest、T22 contract、T23 M/Q 表后生成；不读取或导入 SV package 生成器作为 expected 数据源",
        "frozen_input_sha256": input_hashes,
        "package": {"path": PACKAGE_REL, "sha256": scope["package_sha256"]},
        "testbench": {"path": f"{RUN_REL}/{TB_NAME}", "sha256": scope["tb_sha256"]},
        "runner": {"path": f"{RUN_REL}/{RUNNER_NAME}", "sha256": scope["runner_sha256"]},
        "independent_verifier": {"path": f"{RUN_REL}/{VERIFIER_NAME}", "sha256": scope["verifier_sha256"]},
        "offline_tests": {"path": f"{RUN_REL}/{TEST_NAME}", "sha256": scope["test_sha256"]},
        "fixtures": {
            LAYER_FIXTURE_NAME: {"records": len(layer_records), "record_bits": LAYER_MEMORY_BITS, "sha256": _sha256(layer_bytes)},
            CHANNEL_FIXTURE_NAME: {"records": len(channel_records), "record_bits": CHANNEL_MEMORY_BITS, "sha256": _sha256(channel_bytes)},
        },
        "runtime_coverage": {
            "layers": 38,
            "descriptor_fields_per_layer": len(LAYER_VECTOR_EXPRESSIONS),
            "descriptor_record_bits_before_padding": LAYER_RECORD_BITS,
            "convolution_channels": len(channel_records),
            "channel_fields_per_record": len(CHANNEL_VECTOR_EXPRESSIONS),
            "channel_record_bits_before_padding": CHANNEL_RECORD_BITS,
            "operator_counts": op_counts,
            "dynamic_alias_layers": {"30": 29, "37": 36},
            "global_rom_array_count": scope["package_array_count"],
        },
        "execution": {"vivado_run": False, "xvlog_run": False, "xelab_run": False, "xsim_run": False},
    }
    manifest_path = RUN_DIR / MANIFEST_NAME
    _write_utf8(manifest_path, (json.dumps(binding, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return binding


def validate() -> dict[str, Any]:
    manifest, contract, table, input_hashes = _check_root_and_sources()
    layer_records, channel_records, op_counts = _build_expected(manifest, contract, table)
    scope = _check_hdl_scope()
    binding_path = RUN_DIR / MANIFEST_NAME
    _assert_no_reparse_chain(binding_path)
    binding = _read_json(binding_path, "fixture binding")
    _need(binding.get("schema_version") == "s2a_t63_dynamic_rom_fixture_binding_v1", "fixture binding schema 不匹配")
    _need(binding.get("status") == "FIXTURE_PREPARED_NOT_SIMULATED", "fixture binding 状态不匹配")
    _need(binding.get("frozen_input_sha256") == input_hashes, "fixture binding 的冻结源 SHA 不匹配")
    _need(binding.get("package", {}).get("sha256") == scope["package_sha256"], "fixture binding 的 package SHA 不匹配")
    _need(
        binding.get("testbench") == {
            "path": f"{RUN_REL}/{TB_NAME}",
            "sha256": scope["tb_sha256"],
        },
        "fixture binding 的 testbench 路径/SHA 不匹配",
    )
    _need(
        binding.get("runner") == {
            "path": f"{RUN_REL}/{RUNNER_NAME}",
            "sha256": scope["runner_sha256"],
        },
        "fixture binding 的 runner 路径/SHA 不匹配",
    )
    _need(
        binding.get("independent_verifier") == {
            "path": f"{RUN_REL}/{VERIFIER_NAME}",
            "sha256": scope["verifier_sha256"],
        },
        "fixture binding 的独立验证器路径/SHA 不匹配",
    )
    _need(
        binding.get("offline_tests") == {
            "path": f"{RUN_REL}/{TEST_NAME}",
            "sha256": scope["test_sha256"],
        },
        "fixture binding 的离线测试路径/SHA 不匹配",
    )
    for name, data, records, record_bits in (
        (LAYER_FIXTURE_NAME, _hex_lines(layer_records, LAYER_MEMORY_BITS), len(layer_records), LAYER_MEMORY_BITS),
        (CHANNEL_FIXTURE_NAME, _hex_lines(channel_records, CHANNEL_MEMORY_BITS), len(channel_records), CHANNEL_MEMORY_BITS),
    ):
        path = RUN_DIR / name
        _assert_no_reparse_chain(path)
        _need(path.is_file(), f"fixture 不是文件或不存在: {name}")
        actual = path.read_bytes()
        entry = binding.get("fixtures", {}).get(name, {})
        check_fixture_bytes(actual, data, name)
        _need(entry.get("records") == records, f"{name} 记录数绑定不匹配")
        _need(entry.get("record_bits") == record_bits, f"{name} 位宽绑定不匹配")
        _need(entry.get("sha256") == _sha256(actual), f"{name} SHA-256 不匹配")
    _need(binding.get("runtime_coverage", {}).get("operator_counts") == op_counts, "operator distribution binding 不匹配")
    return {
        "status": "OFFLINE_FIXTURE_VALID",
        "layers": len(layer_records),
        "layer_fields_per_record": len(LAYER_VECTOR_EXPRESSIONS),
        "layer_record_bits": LAYER_RECORD_BITS,
        "channels": len(channel_records),
        "channel_fields_per_record": len(CHANNEL_VECTOR_EXPRESSIONS),
        "channel_record_bits": CHANNEL_RECORD_BITS,
        "operator_counts": op_counts,
        "vivado_run": False,
        "xvlog_run": False,
        "xelab_run": False,
        "xsim_run": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="从冻结 JSON 准备/核验 T63 动态 ROM expected fixture")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--prepare", action="store_true", help="生成任务目录内的 expected fixture 和绑定")
    group.add_argument("--validate", action="store_true", help="离线核验冻结源、fixture 和 HDL 字段覆盖")
    args = parser.parse_args(argv)
    try:
        result = prepare() if args.prepare else validate()
    except (DynamicRomError, OSError, KeyError, TypeError, ValueError, OverflowError) as exc:
        print(f"S2A-T63 dynamic ROM error: {exc}", file=sys.stderr)
        return 1
    if args.prepare:
        print(
            "T63 动态 ROM fixture 已准备："
            f"layers={result['runtime_coverage']['layers']}，"
            f"字段/层={result['runtime_coverage']['descriptor_fields_per_layer']}，"
            f"conv_channels={result['runtime_coverage']['convolution_channels']}，"
            f"全局 ROM 数组={result['runtime_coverage']['global_rom_array_count']}；未运行 Vivado/XSim"
        )
    else:
        print(
            "T63 动态 ROM fixture 离线核验通过："
            f"layers={result['layers']}，"
            f"conv_channels={result['channels']}，"
            f"operator_counts={result['operator_counts']}；未运行 Vivado/XSim"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
