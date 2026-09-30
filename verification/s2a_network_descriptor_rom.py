from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import struct
import sys
from pathlib import Path
from typing import Any


EXPECTED_ROOT = Path(r"D:\FPGA_Competition")
G0_SPEC_PATH = "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
MANIFEST_PATH = "report/evidence/S2A-T01/tiny416_model_manifest.json"
T22_PATH = "report/evidence/S2A-T22/network_dispatch_contract_validation.json"
T23_PATH = "report/evidence/S2A-T23/conv_requant_parameter_table.json"
PACKAGE_PATH = "src/s2a_network_descriptor_pkg.sv"
BINDING_REPORT_PATH = "report/evidence/S2A-T63/descriptor_rom_binding.json"

FROZEN_SHA256 = {
    G0_SPEC_PATH: "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    MANIFEST_PATH: "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    T22_PATH: "611d47cc85bd254474c5412fcab2f8acce3a263138787588f2a6445eac61d9a8",
    T23_PATH: "396dc66aa3ccc41050cc8183bff16b86143a6f5553cf38fed16b0ba8b4eb4ae1",
}
OP_COUNTS = {"convolutional": 21, "maxpool": 3, "route": 11, "upsample": 1, "yolo": 2}
OP_CODE = {"convolutional": 0, "maxpool": 1, "route": 2, "upsample": 3, "yolo": 4}
EXPECTED_ANCHORS = [[10, 14], [23, 27], [37, 58], [81, 82], [135, 169], [344, 319]]
EXPECTED_MASKS = {30: [3, 4, 5], 37: [1, 2, 3]}
MAX_INPUTS = 2
MAX_ANCHORS = 6
MAX_MASK = 3
TOTAL_MQ_CHANNELS = 3164
CHANNEL_CANONICAL_DOMAIN = "T16 candidate stream: channel,positive_Q,positive_M,negative_Q,negative_M\\n"


class DescriptorRomError(ValueError):
    """冻结来源或网络描述符与 G0/T22/T23 不一致。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DescriptorRomError(message)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_channel_digest(channels: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for item in channels:
        digest.update(
            (
                f"{item['channel']},{item['positive_Q']},{item['positive_M']},"
                f"{item['negative_Q']},{item['negative_M']}\n"
            ).encode("ascii")
        )
    return digest.hexdigest()


def _load_module(root: Path, relative_path: str, module_name: str):
    path = root.joinpath(*relative_path.split("/"))
    _require(path.is_file(), f"上游验证器缺失: {relative_path}")
    spec = importlib.util.spec_from_file_location(module_name, path)
    _require(spec is not None and spec.loader is not None, f"无法加载上游验证器: {relative_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _verify_upstream(root: Path, contract: dict[str, Any], table: dict[str, Any]) -> None:
    """复用已冻结的 T22/T23 校验器，核实来源与逐通道候选摘要。"""
    root_text = str(root.resolve())
    if root_text not in sys.path:
        sys.path.insert(0, root_text)

    contract_module = _load_module(
        root,
        "verification/s2a_network_dispatch_contract.py",
        "verification._s2a_network_dispatch_contract_t63",
    )
    expected_contract = contract_module.build_contract(root)
    _require(contract == expected_contract, "T22 文件与冻结来源重建结果不一致")

    table_module = _load_module(
        root,
        "verification/s2a_conv_requant_table.py",
        "verification._s2a_conv_requant_table_t63",
    )
    context, t16 = table_module.build_context(root)
    table_module.validate_parameter_table(table, context, t16)


def load_frozen_inputs(root: Path, verify_upstream: bool = True) -> dict[str, Any]:
    """按冻结 SHA-256 读取 G0、manifest、T22 与 T23。"""
    root = root.resolve()
    _require(os.path.normcase(str(root)) == os.path.normcase(str(EXPECTED_ROOT)), "仓库根目录不是任务卡指定路径")
    documents: dict[str, Any] = {}
    hashes: dict[str, str] = {}
    sizes: dict[str, int] = {}
    for relative_path, expected_sha256 in FROZEN_SHA256.items():
        path = root.joinpath(*relative_path.split("/"))
        _require(path.is_file(), f"冻结输入缺失或不是文件: {relative_path}")
        raw = path.read_bytes()
        actual_sha256 = _sha256_bytes(raw)
        _require(
            actual_sha256 == expected_sha256,
            f"冻结输入 SHA-256 不匹配: {relative_path}: {actual_sha256}",
        )
        hashes[relative_path] = actual_sha256
        sizes[relative_path] = len(raw)
        if relative_path != G0_SPEC_PATH:
            try:
                documents[relative_path] = json.loads(raw.decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise DescriptorRomError(f"冻结 JSON 不能按 UTF-8 解码: {relative_path}: {exc}") from exc

    manifest = documents[MANIFEST_PATH]
    contract = documents[T22_PATH]
    table = documents[T23_PATH]
    if verify_upstream:
        _verify_upstream(root, contract, table)
    return {
        "manifest": manifest,
        "contract": contract,
        "table": table,
        "hashes": hashes,
        "sizes": sizes,
    }


def _checked_int(value: Any, name: str, minimum: int, maximum: int) -> int:
    _require(isinstance(value, int) and not isinstance(value, bool), f"{name} 必须是整数")
    _require(minimum <= value <= maximum, f"{name} 超出 {minimum}..{maximum}: {value}")
    return value


def _checked_shape(value: Any, name: str) -> list[int]:
    _require(
        isinstance(value, list)
        and len(value) == 4
        and all(isinstance(item, int) and not isinstance(item, bool) and 1 <= item <= 0xFFFF for item in value),
        f"{name} 必须是四个可装入 16-bit 的正整数 NCHW",
    )
    return list(value)


def _shape_bytes(shape: list[int], name: str) -> int:
    size = math.prod(shape)
    return _checked_int(size, name, 1, 0xFFFFFFFF)


def _scale_bits(value: Any, name: str) -> int:
    _require(isinstance(value, (int, float)) and not isinstance(value, bool), f"{name} 必须是数值")
    scale = float(value)
    _require(math.isfinite(scale) and scale > 0.0, f"{name} 必须是有限正数")
    return struct.unpack(">Q", struct.pack(">d", scale))[0]


def _field_equal(actual: Any, expected: Any, name: str) -> None:
    _require(actual == expected, f"{name} 与冻结来源不一致")


def _contract_source_binding(contract: dict[str, Any], path: str) -> str:
    bindings = contract.get("source_bindings")
    _require(isinstance(bindings, list), "T22 source_bindings 缺失")
    matches = [item for item in bindings if isinstance(item, dict) and item.get("path") == path]
    _require(len(matches) == 1, f"T22 来源绑定缺失或重复: {path}")
    return str(matches[0].get("sha256", "")).lower()


def _check_input_ref(
    reference: Any,
    actual: dict[str, Any],
    index: int,
    position: int,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    if reference == "network_input":
        _require(index == 0 and position == 0, "network_input 只能是第 0 层唯一输入")
        source = manifest["address_map"]["input"]
        expected = {
            "input_order": position,
            "kind": "network_input",
            "source_index": "network_input",
            "address_space": "G0 logical input",
            "address": source["address"],
            "length_bytes": source["length_bytes"],
            "byte_range_half_open": [source["address"], source["address"] + source["length_bytes"]],
            "shape_nchw": source["shape_nchw"],
            "scale": source["scale"],
            "layout": "NCHW",
            "element_type": "int8_twos_complement",
        }
        _field_equal(actual, expected, f"layer {index} network_input descriptor")
        return {
            "kind": 0,
            "source_index": 0x3F,
            "address": source["address"],
            "length_bytes": source["length_bytes"],
            "shape_nchw": source["shape_nchw"],
            "scale_bits": _scale_bits(source["scale"], f"layer {index} network input scale"),
        }

    source_index = _checked_int(reference, f"layer {index} input ref", 0, index - 1)
    source_layer = manifest["layers"][source_index]
    _require(source_layer["op"] != "yolo", f"layer {index} 把 YOLO alias 当作 producer")
    source_address = source_layer["tensor_address"]
    source_length = source_layer["tensor_length_bytes"]
    source_shape = _checked_shape(source_layer["output_shape_nchw"], f"layer {source_index} output shape")
    source_scale = source_layer["output_scale"]
    expected = {
        "input_order": position,
        "kind": "layer_output",
        "source_index": source_index,
        "address_space": "G0 logical feature workspace",
        "address": source_address,
        "length_bytes": source_length,
        "byte_range_half_open": [source_address, source_address + source_length],
        "shape_nchw": source_shape,
        "scale": source_scale,
        "layout": "NCHW",
        "element_type": "int8_twos_complement",
    }
    _field_equal(actual, expected, f"layer {index} input {position} descriptor")
    return {
        "kind": 1,
        "source_index": source_index,
        "address": source_address,
        "length_bytes": source_length,
        "shape_nchw": source_shape,
        "scale_bits": _scale_bits(source_scale, f"layer {index} input {position} scale"),
    }


def _validate_operator_parameters(
    layer: dict[str, Any],
    contract_layer: dict[str, Any],
    table_layer: dict[str, Any] | None,
) -> dict[str, Any]:
    index = layer["layer_index"]
    op = layer["op"]
    parameters = contract_layer.get("operator_parameters")
    _require(isinstance(parameters, dict), f"layer {index} operator_parameters 缺失")
    result: dict[str, Any] = {}

    if op == "convolutional":
        fields = (
            "kernel_hw",
            "stride_hw",
            "padding_lrtb",
            "groups",
            "padding_value_int8",
            "activation",
            "accumulator_bits",
            "output_scale",
            "weight_layer_index",
            "gf8_parameter_offsets",
        )
        for field in fields:
            _field_equal(parameters.get(field), layer.get(field), f"layer {index} conv.{field}")
        _require(isinstance(table_layer, dict), f"layer {index} T23 conv row 缺失")
        table_parameters = parameters.get("parameters", {})
        t16_source = table_parameters.get("t16_requantization_source", {})
        _field_equal(
            t16_source.get("candidate_parameter_sha256"),
            table_layer.get("candidate_parameter_sha256"),
            f"layer {index} T22/T23 candidate digest",
        )
        _field_equal(table_layer.get("cfg_section"), layer["cfg_section"], f"layer {index} T23 cfg section")
        _field_equal(table_layer.get("activation"), layer["activation"], f"layer {index} T23 activation")
        count = _checked_int(layer["output_shape_nchw"][1], f"layer {index} conv output channels", 1, 0xFFFF)
        _field_equal(table_layer.get("channel_count"), count, f"layer {index} T23 channel count")
        channels = table_layer.get("channels")
        _require(isinstance(channels, list) and len(channels) == count, f"layer {index} T23 通道表长度不符")
        _require(
            [item.get("channel") for item in channels] == list(range(count)),
            f"layer {index} T23 通道顺序缺失或重复",
        )
        _field_equal(
            _canonical_channel_digest(channels),
            table_layer.get("candidate_parameter_sha256"),
            f"layer {index} T23 candidate_parameter_sha256 重算",
        )
        _field_equal(
            layer["weight_layer_index"],
            index,
            f"layer {index} weight_layer_index",
        )
        offsets = layer["gf8_parameter_offsets"]
        _require(isinstance(offsets, dict), f"layer {index} GF8 offset object 缺失")
        result = {
            "kernel_hw": list(layer["kernel_hw"]),
            "stride_hw": list(layer["stride_hw"]),
            "padding_lrtb": list(layer["padding_lrtb"]),
            "groups": _checked_int(layer["groups"], f"layer {index} groups", 1, 0xFFFF),
            "padding_value_int8": _checked_int(layer["padding_value_int8"], f"layer {index} padding value", -128, 127),
            "activation": layer["activation"],
            "accumulator_bits": _checked_int(layer["accumulator_bits"], f"layer {index} accumulator bits", 1, 0xFF),
            "weight_layer_index": _checked_int(layer["weight_layer_index"], f"layer {index} weight layer", 0, 0x3F),
            "gf8_parameter_offsets": offsets,
            "candidate_parameter_sha256": table_layer["candidate_parameter_sha256"],
        }
    elif op == "maxpool":
        fields = (
            "kernel_hw",
            "stride_hw",
            "darknet_padding_parameter",
            "output_hw_formula",
            "window_origin_yx_at_output_0",
            "padding_lrtb_actual",
            "pad_value_int8",
            "output_scale",
        )
        for field in fields:
            _field_equal(parameters.get(field), layer.get(field), f"layer {index} maxpool.{field}")
        result = {
            "kernel_hw": list(layer["kernel_hw"]),
            "stride_hw": list(layer["stride_hw"]),
            "darknet_padding_parameter": _checked_int(
                layer["darknet_padding_parameter"], f"layer {index} Darknet padding", 0, 0xFF
            ),
            "output_hw_formula": layer["output_hw_formula"],
            "window_origin_yx_at_output_0": list(layer["window_origin_yx_at_output_0"]),
            "padding_lrtb_actual": list(layer["padding_lrtb_actual"]),
            "pad_value_int8": _checked_int(layer["pad_value_int8"], f"layer {index} maxpool pad value", -128, 127),
        }
    elif op == "route":
        fields = (
            "route_groups",
            "route_group_id",
            "route_source_channel_ranges",
            "route_group_slice_order",
            "requantization",
            "output_scale",
        )
        for field in fields:
            _field_equal(parameters.get(field), layer.get(field), f"layer {index} route.{field}")
        _field_equal(
            len(parameters["route_source_channel_ranges"]),
            len(contract_layer["input_tensors_in_manifest_order"]),
            f"layer {index} route slice count",
        )
        result = {
            "route_groups": _checked_int(layer["route_groups"], f"layer {index} route groups", 1, 0xFFFF),
            "route_group_id": _checked_int(layer["route_group_id"], f"layer {index} route group id", 0, 0xFFFF),
            "route_source_channel_ranges": [list(item) for item in layer["route_source_channel_ranges"]],
            "route_group_slice_order": layer["route_group_slice_order"],
            "requantization": layer["requantization"],
        }
    elif op == "upsample":
        for field in ("scale", "stride", "method", "output_scale"):
            _field_equal(parameters.get(field), layer.get(field), f"layer {index} upsample.{field}")
        result = {
            "scale_bits": _scale_bits(parameters["scale"], f"layer {index} upsample scale"),
            "stride": _checked_int(parameters["stride"], f"layer {index} upsample stride", 1, 0xFFFF),
            "method": parameters["method"],
        }
    elif op == "yolo":
        fields = (
            "output_tensor_index",
            "classes",
            "scale_x_y",
            "new_coords",
            "head_logit_scale",
            "output_scale",
        )
        for field in fields:
            _field_equal(parameters.get(field), layer.get(field), f"layer {index} yolo.{field}")
        _field_equal(layer.get("anchors_wh"), EXPECTED_ANCHORS, f"layer {index} frozen anchors")
        _field_equal(layer.get("mask"), EXPECTED_MASKS.get(index), f"layer {index} frozen YOLO mask")
        result = {
            "anchors_wh": [list(item) for item in layer["anchors_wh"]],
            "mask": list(layer["mask"]),
            "classes": _checked_int(layer["classes"], f"layer {index} YOLO classes", 1, 0xFFFF),
            "scale_x_y_bits": _scale_bits(layer["scale_x_y"], f"layer {index} YOLO scale_x_y"),
            "new_coords": _checked_int(layer["new_coords"], f"layer {index} YOLO new_coords", 0, 0xFF),
            "head_logit_scale_bits": _scale_bits(layer["head_logit_scale"], f"layer {index} YOLO head logit scale"),
        }
    else:
        raise DescriptorRomError(f"不支持的 op: {op!r}")

    return result


def build_rom_data(
    manifest: dict[str, Any],
    contract: dict[str, Any],
    table: dict[str, Any],
    input_hashes: dict[str, str],
) -> dict[str, Any]:
    """将冻结 JSON 校验为机器可读的 38 层 ROM 与平坦通道表。"""
    _require(input_hashes == FROZEN_SHA256, "输入绑定 SHA-256 与冻结值不符")
    _require(manifest.get("schema_version") == "gestureforge_s2a_model_manifest_v1", "manifest schema 不匹配")
    _require(
        manifest.get("status") == "G0_FROZEN" and manifest.get("model", {}).get("model_id") == "tiny416",
        "manifest 不是冻结 tiny416",
    )
    _require(contract.get("schema_version") == "gestureforge_s2a_network_dispatch_contract_v1", "T22 schema 不匹配")
    _require(contract.get("task_id") == "S2A-T22" and contract.get("artifact_status") == "CONTRACT_VALIDATED", "T22 状态未通过")
    _require(table.get("schema_version") == "gestureforge_s2a_conv_requant_parameter_table_v1", "T23 schema 不匹配")
    _require(table.get("status") == "ALL_CHANNELS_EXACT_AND_T16_DIGEST_MATCH", "T23 状态未通过")

    layers = manifest.get("layers")
    dispatch = contract.get("network_dispatch")
    contract_layers = dispatch.get("layers") if isinstance(dispatch, dict) else None
    table_layers = table.get("layers")
    _require(isinstance(layers, list) and len(layers) == 38, "manifest 层数必须是 38")
    _require(isinstance(contract_layers, list) and len(contract_layers) == 38, "T22 层数必须是 38")
    _require(isinstance(table_layers, list) and len(table_layers) == 21, "T23 卷积层数必须是 21")
    _field_equal(dispatch.get("layer_count"), 38, "T22 layer_count")
    _field_equal(dispatch.get("operator_counts"), OP_COUNTS, "T22 operator_counts")
    _field_equal(
        _contract_source_binding(contract, MANIFEST_PATH),
        FROZEN_SHA256[MANIFEST_PATH],
        f"T22 source binding {MANIFEST_PATH}",
    )
    table_bindings = table.get("source_bindings")
    _require(isinstance(table_bindings, list), "T23 source_bindings 缺失")
    for path in (MANIFEST_PATH, T22_PATH):
        matches = [item for item in table_bindings if isinstance(item, dict) and item.get("path") == path]
        _require(len(matches) == 1 and matches[0].get("sha256") == FROZEN_SHA256[path], f"T23 未绑定冻结来源: {path}")

    table_by_layer = {item.get("layer_index"): item for item in table_layers if isinstance(item, dict)}
    _require(len(table_by_layer) == len(table_layers), "T23 layer_index 重复或无效")
    _require(
        [item.get("layer_index") for item in table_layers] == [i for i, row in enumerate(layers) if row.get("op") == "convolutional"],
        "T23 卷积层顺序与 manifest 不一致",
    )

    timeout = contract.get("dispatch_protocol", {}).get("global_timeout", {})
    _field_equal(timeout.get("scope"), "one deadline from accepted start for the whole network; layer transitions never restart it", "T22 global timeout scope")
    _field_equal(timeout.get("per_layer_timeout_restart_allowed"), False, "T22 per-layer timeout restart")
    _field_equal(contract.get("dispatch_protocol", {}).get("ps_visible_csr"), "unchanged G0 CSR; no per-layer descriptor registers", "T22 PS CSR boundary")
    _field_equal(contract.get("dispatch_protocol", {}).get("memory_interface"), "unchanged G0 single-outstanding T12 memory master contract", "T22 memory boundary")

    rows: list[dict[str, Any]] = []
    channels_flat: list[dict[str, Any]] = []
    operator_counts = {key: 0 for key in OP_COUNTS}
    for index, (layer, contract_layer) in enumerate(zip(layers, contract_layers)):
        _require(isinstance(layer, dict) and isinstance(contract_layer, dict), f"layer {index} row 不是 object")
        _field_equal(layer.get("layer_index"), index, f"manifest layer {index} index")
        _field_equal(layer.get("cfg_section"), index + 1, f"manifest layer {index} cfg_section")
        _field_equal(contract_layer.get("dispatch_order"), index, f"T22 layer {index} dispatch_order")
        _field_equal(contract_layer.get("layer_index"), index, f"T22 layer {index} layer_index")
        _field_equal(contract_layer.get("cfg_section"), index + 1, f"T22 layer {index} cfg_section")
        op = layer.get("op")
        _field_equal(contract_layer.get("op"), op, f"T22 layer {index} op")
        _require(op in OP_COUNTS, f"layer {index} 不支持的 op: {op!r}")
        operator_counts[op] += 1

        manifest_refs = layer.get("input_tensor_indices")
        contract_inputs = contract_layer.get("input_tensors_in_manifest_order")
        _require(isinstance(manifest_refs, list) and 1 <= len(manifest_refs) <= MAX_INPUTS, f"layer {index} 输入引用数无效")
        _require(isinstance(contract_inputs, list) and len(contract_inputs) == len(manifest_refs), f"layer {index} T22 输入数不匹配")
        inputs = [
            _check_input_ref(reference, contract_inputs[position], index, position, manifest)
            for position, reference in enumerate(manifest_refs)
        ]
        source_shapes = [item["shape_nchw"] for item in inputs]
        expected_input_shape: Any = source_shapes if op == "route" else source_shapes[0]
        _field_equal(layer.get("input_shape_nchw"), expected_input_shape, f"layer {index} input NCHW")
        _field_equal(layer.get("layout"), "NCHW", f"layer {index} layout")
        _field_equal(layer.get("element_type"), "int8_twos_complement", f"layer {index} element_type")
        if op == "route":
            input_scales = [struct.unpack(">d", item["scale_bits"].to_bytes(8, "big"))[0] for item in inputs]
            _field_equal(layer.get("input_scales"), input_scales, f"layer {index} route input scales")
        else:
            _field_equal(
                _scale_bits(layer.get("input_scale"), f"layer {index} input scale"),
                inputs[0]["scale_bits"],
                f"layer {index} input scale binding",
            )

        output = contract_layer.get("output_tensor")
        _require(isinstance(output, dict), f"layer {index} output_tensor 缺失")
        output_shape = _checked_shape(layer.get("output_shape_nchw"), f"layer {index} output shape")
        output_length = _checked_int(layer.get("tensor_length_bytes"), f"layer {index} output bytes", 1, 0xFFFFFFFF)
        _field_equal(output_length, _shape_bytes(output_shape, f"layer {index} shape bytes"), f"layer {index} output length")
        output_address = _checked_int(layer.get("tensor_address"), f"layer {index} output address", 0, 0xFFFFFFFF)
        output_scale = _scale_bits(layer.get("output_scale"), f"layer {index} output scale")
        _field_equal(output.get("address"), output_address, f"layer {index} output address binding")
        _field_equal(output.get("length_bytes"), output_length, f"layer {index} output length binding")
        _field_equal(output.get("shape_nchw"), output_shape, f"layer {index} output shape binding")
        _field_equal(_scale_bits(output.get("scale"), f"layer {index} T22 output scale"), output_scale, f"layer {index} output scale binding")
        expected_tensor_index = layer.get("output_tensor_index", index)
        _field_equal(output.get("tensor_index"), expected_tensor_index, f"layer {index} output tensor index")
        is_yolo = op == "yolo"
        expected_alias = manifest_refs[0] if is_yolo else None
        _field_equal(output.get("allocation_kind"), "head_alias" if is_yolo else "owned_feature_tensor", f"layer {index} allocation kind")
        _field_equal(output.get("alias_of_layer_index"), expected_alias, f"layer {index} alias target")
        _field_equal(output.get("memory_write_required"), not is_yolo, f"layer {index} memory write policy")
        _field_equal(output.get("layout"), "NCHW", f"layer {index} output layout")
        _field_equal(output.get("element_type"), "int8_twos_complement", f"layer {index} output element type")
        if is_yolo:
            source = inputs[0]
            _field_equal(output.get("tensor_index"), source["source_index"], f"layer {index} alias tensor index")
            _field_equal(output_address, source["address"], f"layer {index} alias address")
            _field_equal(output_length, source["length_bytes"], f"layer {index} alias length")
            _field_equal(output_shape, source["shape_nchw"], f"layer {index} alias shape")
            _field_equal(output_scale, source["scale_bits"], f"layer {index} alias scale")
        else:
            workspace = manifest["address_map"]["feature_workspace"]
            _require(
                workspace["base_address"] <= output_address
                and output_address + output_length <= workspace["end_address_exclusive"],
                f"layer {index} owned output 超出 feature workspace",
            )

        table_layer = table_by_layer.get(index)
        if op != "convolutional":
            _require(table_layer is None, f"非卷积 layer {index} 出现在 T23")
        parameters = _validate_operator_parameters(layer, contract_layer, table_layer)
        descriptor = {
            "layer_index": index,
            "cfg_section": index + 1,
            "op": op,
            "inputs": inputs,
            "output": {
                "tensor_index": expected_tensor_index,
                "allocation_kind": 1 if is_yolo else 0,
                "alias_of_layer_index": 0x3F if not is_yolo else expected_alias,
                "memory_write_required": not is_yolo,
                "address": output_address,
                "length_bytes": output_length,
                "shape_nchw": output_shape,
                "scale_bits": output_scale,
            },
            "parameters": parameters,
            "mq_base": len(channels_flat) if op == "convolutional" else 0,
            "mq_count": len(table_layer["channels"]) if op == "convolutional" else 0,
            "candidate_parameter_sha256": table_layer["candidate_parameter_sha256"] if op == "convolutional" else "0" * 64,
            "route_contract_sha256": (
                _sha256_bytes(
                    (
                        str(layer["route_group_slice_order"])
                        + "\n"
                        + str(layer["requantization"])
                    ).encode("utf-8")
                )
                if op == "route"
                else "0" * 64
            ),
            "maxpool_formula_sha256": (
                _sha256_bytes(str(layer["output_hw_formula"]).encode("utf-8"))
                if op == "maxpool"
                else "0" * 64
            ),
        }
        rows.append(descriptor)

        if op == "convolutional":
            count = descriptor["mq_count"]
            _field_equal(count, output_shape[1], f"layer {index} M/Q channel count")
            offsets = parameters["gf8_parameter_offsets"]
            package = manifest["address_map"]["weight_package"]
            required_offset_fields = (
                "record_offset",
                "weight_scale_offset",
                "fused_bias_offset",
                "quantized_weight_offset",
                "quantized_weight_bytes",
            )
            for field in required_offset_fields:
                _checked_int(offsets.get(field), f"layer {index} GF8 {field}", 0, 0xFFFFFFFF)
            _field_equal(
                offsets["quantized_weight_bytes"],
                output_shape[1]
                * (inputs[0]["shape_nchw"][1] // parameters["groups"])
                * parameters["kernel_hw"][0]
                * parameters["kernel_hw"][1],
                f"layer {index} GF8 weight bytes",
            )
            _require(
                offsets["quantized_weight_offset"] + offsets["quantized_weight_bytes"] <= package["length_bytes"],
                f"layer {index} GF8 weight range 越界",
            )
            _require(
                offsets["weight_scale_offset"] + 4 * count <= package["length_bytes"],
                f"layer {index} GF8 weight scale range 越界",
            )
            _require(
                offsets["fused_bias_offset"] + 4 * count <= package["length_bytes"],
                f"layer {index} GF8 bias range 越界",
            )
            weight_scales = layer.get("weight_scale_per_output_channel")
            fused_bias = layer.get("fused_bias_float32_per_output_channel")
            accumulator_bias = layer.get("bias_accumulator_int32_per_output_channel")
            for field, values in (
                ("weight_scale_per_output_channel", weight_scales),
                ("fused_bias_float32_per_output_channel", fused_bias),
                ("bias_accumulator_int32_per_output_channel", accumulator_bias),
            ):
                _require(isinstance(values, list) and len(values) == count, f"layer {index} {field} 长度不匹配")
            for channel, item in enumerate(table_layer["channels"]):
                _field_equal(item["channel"], channel, f"layer {index} channel index")
                _field_equal(
                    _scale_bits(item["parameter_source"]["weight_scale"], f"layer {index} channel {channel} T23 weight scale"),
                    _scale_bits(weight_scales[channel], f"layer {index} channel {channel} manifest weight scale"),
                    f"layer {index} channel {channel} weight scale binding",
                )
                _field_equal(item["parameter_source"]["activation"], layer["activation"], f"layer {index} channel {channel} activation")
                weight_scale_bits = _scale_bits(weight_scales[channel], f"layer {index} channel {channel} weight scale")
                fused_bias_bits = struct.unpack(">I", struct.pack(">f", float(fused_bias[channel])))[0]
                bias_value = _checked_int(
                    accumulator_bias[channel],
                    f"layer {index} channel {channel} accumulator bias",
                    -(1 << 31),
                    (1 << 31) - 1,
                )
                channels_flat.append(
                    {
                        "layer_index": index,
                        "channel": channel,
                        "weight_scale_bits": weight_scale_bits,
                        "fused_bias_float32_bits": fused_bias_bits,
                        "bias_accumulator_int32": bias_value,
                        "positive_M": _checked_int(item["positive_M"], f"layer {index} channel {channel} positive_M", 1, 0xFFFFFFFF),
                        "positive_Q": _checked_int(item["positive_Q"], f"layer {index} channel {channel} positive_Q", 0, 65),
                        "negative_M": _checked_int(item["negative_M"], f"layer {index} channel {channel} negative_M", 1, 0xFFFFFFFF),
                        "negative_Q": _checked_int(item["negative_Q"], f"layer {index} channel {channel} negative_Q", 0, 65),
                    }
                )

    _field_equal(operator_counts, OP_COUNTS, "manifest operator counts")
    _field_equal(len(channels_flat), TOTAL_MQ_CHANNELS, "flat M/Q channel count")
    return {
        "layers": rows,
        "channels": channels_flat,
        "weight_package": {
            "address": _checked_int(
                manifest["address_map"]["weight_package"]["address"], "GF8 package base", 0, 0xFFFFFFFF
            ),
            "length_bytes": _checked_int(
                manifest["address_map"]["weight_package"]["length_bytes"],
                "GF8 package length",
                1,
                0xFFFFFFFF,
            ),
        },
        "operator_counts": operator_counts,
        "source_hashes": dict(input_hashes),
        "serial_dispatch": True,
        "global_timeout_one_deadline": True,
        "per_layer_timeout_restart": False,
        "ps_visible_csr_changed": False,
        "memory_outstanding_limit": 1,
    }


def _hex(value: int, width: int) -> str:
    _checked_int(value, f"{width}-bit literal", 0, (1 << width) - 1)
    digits = (width + 3) // 4
    return f"{width}'h{value:0{digits}X}"


def _signed_hex(value: int, width: int) -> str:
    _checked_int(value, f"signed {width}-bit literal", -(1 << (width - 1)), (1 << (width - 1)) - 1)
    return _hex(value & ((1 << width) - 1), width)


def _array_1d(name: str, width: int, values: list[int], comment: str) -> str:
    lines = [f"  // {comment}", f"  localparam logic [{width - 1}:0] {name} [0:{len(values) - 1}] = '{{"]
    chunks = [values[start : start + 8] for start in range(0, len(values), 8)]
    for chunk_index, chunk in enumerate(chunks):
        suffix = "," if chunk_index + 1 < len(chunks) else ""
        lines.append("    " + ", ".join(_hex(value, width) for value in chunk) + suffix)
    lines.append("  };")
    return "\n".join(lines)


def _array_2d(name: str, width: int, values: list[list[int]], comment: str) -> str:
    lines = [f"  // {comment}", f"  localparam logic [{width - 1}:0] {name} [0:{len(values) - 1}][0:{len(values[0]) - 1}] = '{{"]
    for row_index, row in enumerate(values):
        suffix = "," if row_index + 1 < len(values) else ""
        lines.append("    '{" + ", ".join(_hex(value, width) for value in row) + "}" + suffix)
    lines.append("  };")
    return "\n".join(lines)


def _sha_array(name: str, digests: list[str], comment: str) -> str:
    lines = [f"  // {comment}", f"  localparam logic [255:0] {name} [0:{len(digests) - 1}] = '{{"]
    for index, digest in enumerate(digests):
        _require(len(digest) == 64 and all(char in "0123456789abcdef" for char in digest), f"{name}[{index}] SHA-256 格式无效")
        suffix = "," if index + 1 < len(digests) else ""
        lines.append(f"    256'h{digest.upper()}{suffix}")
    lines.append("  };")
    return "\n".join(lines)


def render_sv_package(data: dict[str, Any]) -> bytes:
    """渲染只读 SystemVerilog package；所有实数按 IEEE-754 位模式保存。"""
    rows = data["layers"]
    channels = data["channels"]
    zero_sha = "0" * 64

    def field_values(field: str, fallback: int = 0) -> list[int]:
        return [int(row.get(field, fallback)) for row in rows]

    def parameter_values(field: str, fallback: int = 0) -> list[int]:
        return [int(row["parameters"].get(field, fallback)) for row in rows]

    def pair_values(field: str, fallback: list[int] | None = None) -> list[list[int]]:
        defaults = [0, 0] if fallback is None else fallback
        result = []
        for row in rows:
            values = row["parameters"].get(field, defaults)
            result.append([int(values[0]), int(values[1])])
        return result

    def quad_values(field: str) -> list[list[int]]:
        return [[int(value) for value in row["parameters"].get(field, [0, 0, 0, 0])] for row in rows]

    input_fields = {
        "S2A_INPUT_KIND": ("kind", 1),
        "S2A_INPUT_SOURCE_INDEX": ("source_index", 6),
        "S2A_INPUT_ADDRESS": ("address", 32),
        "S2A_INPUT_LENGTH_BYTES": ("length_bytes", 32),
        "S2A_INPUT_N": ("n", 16),
        "S2A_INPUT_C": ("c", 16),
        "S2A_INPUT_H": ("h", 16),
        "S2A_INPUT_W": ("w", 16),
        "S2A_INPUT_SCALE_BITS": ("scale_bits", 64),
        "S2A_INPUT_ROUTE_CHANNEL_START": ("route_start", 16),
        "S2A_INPUT_ROUTE_CHANNEL_END": ("route_end", 16),
    }
    inputs_matrix: dict[str, list[list[int]]] = {name: [] for name in input_fields}
    for row in rows:
        layer_inputs = row["inputs"]
        route_ranges = row["parameters"].get("route_source_channel_ranges", [])
        values_by_name: dict[str, list[int]] = {name: [] for name in input_fields}
        for slot in range(MAX_INPUTS):
            if slot < len(layer_inputs):
                item = layer_inputs[slot]
                n, c, h, w = item["shape_nchw"]
                route_range = route_ranges[slot] if slot < len(route_ranges) else [0, 0]
                source = {
                    "kind": item["kind"],
                    "source_index": item["source_index"],
                    "address": item["address"],
                    "length_bytes": item["length_bytes"],
                    "n": n,
                    "c": c,
                    "h": h,
                    "w": w,
                    "scale_bits": item["scale_bits"],
                    "route_start": route_range[0],
                    "route_end": route_range[1],
                }
            else:
                source = {key: 0 for key, _ in input_fields.values()}
                source["source_index"] = 0x3F
            for name, (key, _) in input_fields.items():
                values_by_name[name].append(int(source[key]))
        for name in input_fields:
            inputs_matrix[name].append(values_by_name[name])

    output_fields = {
        "S2A_OUTPUT_TENSOR_INDEX": "tensor_index",
        "S2A_OUTPUT_ALLOCATION_KIND": "allocation_kind",
        "S2A_OUTPUT_ALIAS_LAYER_INDEX": "alias_of_layer_index",
        "S2A_OUTPUT_MEMORY_WRITE_REQUIRED": "memory_write_required",
        "S2A_OUTPUT_ADDRESS": "address",
        "S2A_OUTPUT_LENGTH_BYTES": "length_bytes",
        "S2A_OUTPUT_N": "n",
        "S2A_OUTPUT_C": "c",
        "S2A_OUTPUT_H": "h",
        "S2A_OUTPUT_W": "w",
        "S2A_OUTPUT_SCALE_BITS": "scale_bits",
    }
    output_widths = {
        "S2A_OUTPUT_TENSOR_INDEX": 6,
        "S2A_OUTPUT_ALLOCATION_KIND": 1,
        "S2A_OUTPUT_ALIAS_LAYER_INDEX": 6,
        "S2A_OUTPUT_MEMORY_WRITE_REQUIRED": 1,
        "S2A_OUTPUT_ADDRESS": 32,
        "S2A_OUTPUT_LENGTH_BYTES": 32,
        "S2A_OUTPUT_N": 16,
        "S2A_OUTPUT_C": 16,
        "S2A_OUTPUT_H": 16,
        "S2A_OUTPUT_W": 16,
        "S2A_OUTPUT_SCALE_BITS": 64,
    }
    output_matrix: dict[str, list[int]] = {name: [] for name in output_fields}
    for row in rows:
        output = row["output"]
        n, c, h, w = output["shape_nchw"]
        normalized = {
            "tensor_index": output["tensor_index"],
            "allocation_kind": output["allocation_kind"],
            "alias_of_layer_index": output["alias_of_layer_index"],
            "memory_write_required": int(output["memory_write_required"]),
            "address": output["address"],
            "length_bytes": output["length_bytes"],
            "n": n,
            "c": c,
            "h": h,
            "w": w,
            "scale_bits": output["scale_bits"],
        }
        for name, key in output_fields.items():
            output_matrix[name].append(int(normalized[key]))

    lines = [
        "// S2A-T63 由冻结 G0 manifest、T22 contract 与 T23 M/Q 表确定性生成。",
        "// 只读常量包；不增加 PS CSR、逐层 descriptor 接口或计时器。",
        "package s2a_network_descriptor_pkg;",
        f"  localparam int unsigned S2A_LAYER_COUNT = {len(rows)};",
        f"  localparam int unsigned S2A_CONV_CHANNEL_COUNT = {len(channels)};",
        "  localparam int unsigned S2A_MAX_INPUTS = 2;",
        "  localparam logic S2A_SERIAL_DISPATCH = 1'b1;",
        "  localparam logic S2A_TIMEOUT_SCOPE_GLOBAL = 1'b1;",
        "  localparam logic S2A_PER_LAYER_TIMEOUT_RESTART = 1'b0;",
        "  localparam logic S2A_PS_VISIBLE_CSR_CHANGED = 1'b0;",
        "  localparam logic [7:0] S2A_MEMORY_OUTSTANDING_LIMIT = 8'd1;",
        "  localparam logic [255:0] S2A_G0_SPEC_SHA256 = 256'h" + FROZEN_SHA256[G0_SPEC_PATH].upper() + ";",
        "  localparam logic [255:0] S2A_MANIFEST_SHA256 = 256'h" + FROZEN_SHA256[MANIFEST_PATH].upper() + ";",
        "  localparam logic [255:0] S2A_T22_SHA256 = 256'h" + FROZEN_SHA256[T22_PATH].upper() + ";",
        "  localparam logic [255:0] S2A_T23_SHA256 = 256'h" + FROZEN_SHA256[T23_PATH].upper() + ";",
        "",
        "  // op 编码：卷积 0、maxpool 1、route 2、upsample 3、YOLO 4。",
        "  localparam logic [2:0] S2A_OP_CONV = 3'd0;",
        "  localparam logic [2:0] S2A_OP_MAXPOOL = 3'd1;",
        "  localparam logic [2:0] S2A_OP_ROUTE = 3'd2;",
        "  localparam logic [2:0] S2A_OP_UPSAMPLE = 3'd3;",
        "  localparam logic [2:0] S2A_OP_YOLO = 3'd4;",
        "  localparam logic [1:0] S2A_INPUT_NETWORK = 2'd0;",
        "  localparam logic [1:0] S2A_INPUT_LAYER_OUTPUT = 2'd1;",
        "  localparam logic S2A_OUTPUT_OWNED = 1'b0;",
        "  localparam logic S2A_OUTPUT_HEAD_ALIAS = 1'b1;",
        "  localparam logic [1:0] S2A_ACT_NONE = 2'd0;",
        "  localparam logic [1:0] S2A_ACT_LINEAR = 2'd1;",
        "  localparam logic [1:0] S2A_ACT_LEAKY = 2'd2;",
        "  localparam logic [1:0] S2A_ROUTE_REQUANT_NONE = 2'd0;",
        "  // route=1：先按 groups/group_id 切通道，再转换到输出 scale，half-away-from-zero 舍入并饱和到 INT8，最后按来源顺序拼接。",
        "  localparam logic [1:0] S2A_ROUTE_REQUANT_TO_OUTPUT_SCALE = 2'd1;",
        "  localparam logic [1:0] S2A_ROUTE_ORDER_NONE = 2'd0;",
        "  localparam logic [1:0] S2A_ROUTE_ORDER_SLICE_THEN_CFG_CONCAT = 2'd1;",
        "  localparam logic [1:0] S2A_MAXPOOL_FORMULA_NONE = 2'd0;",
        "  // maxpool 输出尺寸按 (input_hw + darknet_padding_parameter - kernel_hw) / stride_hw + 1 取整。",
        "  localparam logic [1:0] S2A_MAXPOOL_FORMULA_DARKNET = 2'd1;",
        "  localparam logic [1:0] S2A_UPSAMPLE_NONE = 2'd0;",
        "  localparam logic [1:0] S2A_UPSAMPLE_NEAREST_REPEAT = 2'd1;",
        "  // 本 ROM 的 Q 字段采用 8-bit 无符号存储；这不是 G0/T23 对 engine 端口位宽的冻结。",
        "  // 消费端接入时须零扩展到现有 32-bit engine 参数端口。",
        "",
        _array_1d("S2A_LAYER_INDEX", 6, [row["layer_index"] for row in rows], "按 cfg 顺序排列的 manifest layer index。"),
        _array_1d("S2A_CFG_SECTION", 6, [row["cfg_section"] for row in rows], "Darknet cfg section 编号。"),
        _array_1d("S2A_OP", 3, [OP_CODE[row["op"]] for row in rows], "每层算子类型编码。"),
        _array_1d("S2A_INPUT_COUNT", 2, [len(row["inputs"]) for row in rows], "每层输入 tensor 引用数。"),
    ]
    for name, (_, width) in input_fields.items():
        lines.append(_array_2d(name, width, inputs_matrix[name], "输入 tensor 引用；unused slot 地址/长度/shape/scale 为零，source index 为 6'h3F。"))
    lines.append(_array_1d("S2A_OUTPUT_TENSOR_INDEX", 6, output_matrix["S2A_OUTPUT_TENSOR_INDEX"], "实际 tensor index；YOLO alias 与来源卷积相同。"))
    lines.append(_array_1d("S2A_OUTPUT_ALLOCATION_KIND", 1, output_matrix["S2A_OUTPUT_ALLOCATION_KIND"], "0=owned feature tensor，1=YOLO head alias。"))
    lines.append(_array_1d("S2A_OUTPUT_ALIAS_LAYER_INDEX", 6, output_matrix["S2A_OUTPUT_ALIAS_LAYER_INDEX"], "无 alias 使用 6'h3F。"))
    lines.append(_array_1d("S2A_OUTPUT_MEMORY_WRITE_REQUIRED", 1, output_matrix["S2A_OUTPUT_MEMORY_WRITE_REQUIRED"], "YOLO alias 为 0，保持 G0 零拷贝语义。"))
    for name in ("S2A_OUTPUT_ADDRESS", "S2A_OUTPUT_LENGTH_BYTES", "S2A_OUTPUT_N", "S2A_OUTPUT_C", "S2A_OUTPUT_H", "S2A_OUTPUT_W", "S2A_OUTPUT_SCALE_BITS"):
        lines.append(_array_1d(name, output_widths[name], output_matrix[name], "输出 tensor 地址、长度、NCHW 或 IEEE-754 scale 位模式。"))

    def op_array(name: str, width: int, values: list[int], comment: str) -> None:
        lines.append(_array_1d(name, width, values, comment))

    op_array("S2A_KERNEL_H", 8, [int(row["parameters"].get("kernel_hw", [0, 0])[0]) for row in rows], "卷积或 maxpool kernel 高度。")
    op_array("S2A_KERNEL_W", 8, [int(row["parameters"].get("kernel_hw", [0, 0])[1]) for row in rows], "卷积或 maxpool kernel 宽度。")
    op_array("S2A_STRIDE_H", 8, [int(row["parameters"].get("stride_hw", [0, 0])[0]) for row in rows], "卷积或 maxpool stride 高度。")
    op_array("S2A_STRIDE_W", 8, [int(row["parameters"].get("stride_hw", [0, 0])[1]) for row in rows], "卷积或 maxpool stride 宽度。")
    op_array("S2A_PADDING_LEFT", 8, [int(row["parameters"].get("padding_lrtb", [0, 0, 0, 0])[0]) for row in rows], "卷积实际左侧 padding。")
    op_array("S2A_PADDING_RIGHT", 8, [int(row["parameters"].get("padding_lrtb", [0, 0, 0, 0])[1]) for row in rows], "卷积实际右侧 padding。")
    op_array("S2A_PADDING_TOP", 8, [int(row["parameters"].get("padding_lrtb", [0, 0, 0, 0])[2]) for row in rows], "卷积实际上侧 padding。")
    op_array("S2A_PADDING_BOTTOM", 8, [int(row["parameters"].get("padding_lrtb", [0, 0, 0, 0])[3]) for row in rows], "卷积实际下侧 padding。")
    op_array("S2A_GROUP_COUNT", 16, [int(row["parameters"].get("groups", row["parameters"].get("route_groups", 0))) for row in rows], "卷积 groups 或 route groups。")
    op_array("S2A_ROUTE_GROUP_ID", 16, [int(row["parameters"].get("route_group_id", 0)) for row in rows], "route 选择的 group id。")
    op_array("S2A_PADDING_VALUE_INT8", 8, [int(row["parameters"].get("padding_value_int8", row["parameters"].get("pad_value_int8", 0))) & 0xFF for row in rows], "有符号 INT8 padding 值的二补码位模式。")
    activation_codes = {"": 0, "linear": 1, "leaky": 2}
    op_array("S2A_ACTIVATION", 2, [activation_codes.get(row["parameters"].get("activation", ""), 0) for row in rows], "卷积 activation 编码。")
    op_array("S2A_ACCUMULATOR_BITS", 8, [int(row["parameters"].get("accumulator_bits", 0)) for row in rows], "卷积累加器宽度。")
    op_array("S2A_WEIGHT_LAYER_INDEX", 6, [int(row["parameters"].get("weight_layer_index", 0x3F)) for row in rows], "卷积对应的 Darknet/GF8 权重层号，非卷积为 6'h3F。")

    offsets = [row["parameters"].get("gf8_parameter_offsets", {}) for row in rows]
    # 权重包地址与长度来自已绑定的 manifest 全局参数。
    for name, key in (
        ("S2A_GF8_RECORD_OFFSET", "record_offset"),
        ("S2A_GF8_WEIGHT_SCALE_OFFSET", "weight_scale_offset"),
        ("S2A_GF8_BIAS_OFFSET", "fused_bias_offset"),
        ("S2A_GF8_WEIGHT_OFFSET", "quantized_weight_offset"),
        ("S2A_GF8_WEIGHT_BYTES", "quantized_weight_bytes"),
    ):
        op_array(name, 32, [int(item.get(key, 0)) for item in offsets], "GFINT8W1 参数包内 byte offset 或权重长度。")
    package_meta = data["weight_package"]
    op_array("S2A_GF8_PACKAGE_BASE", 32, [package_meta["address"] if row["op"] == "convolutional" else 0 for row in rows], "GFINT8W1 逻辑包基地址。")
    op_array("S2A_GF8_PACKAGE_LENGTH", 32, [package_meta["length_bytes"] if row["op"] == "convolutional" else 0 for row in rows], "GFINT8W1 包字节长度。")
    op_array("S2A_GF8_WEIGHT_ADDRESS", 32, [package_meta["address"] + int(offset.get("quantized_weight_offset", 0)) if row["op"] == "convolutional" else 0 for row, offset in zip(rows, offsets)], "GFINT8W1 量化权重绝对逻辑地址。")
    op_array("S2A_GF8_BIAS_ADDRESS", 32, [package_meta["address"] + int(offset.get("fused_bias_offset", 0)) if row["op"] == "convolutional" else 0 for row, offset in zip(rows, offsets)], "GFINT8W1 fused bias 绝对逻辑地址。")
    op_array("S2A_GF8_BIAS_BYTES", 32, [4 * row["mq_count"] if row["op"] == "convolutional" else 0 for row in rows], "GFINT8W1 每层 int32 fused bias 字节数。")
    op_array("S2A_T23_MQ_BASE", 16, [row["mq_base"] for row in rows], "平坦 T23 M/Q ROM 首通道索引。")
    op_array("S2A_T23_MQ_CHANNEL_COUNT", 16, [row["mq_count"] for row in rows], "该卷积层在平坦 T23 M/Q ROM 中的通道数。")
    op_array("S2A_MAXPOOL_DARKNET_PADDING", 8, [int(row["parameters"].get("darknet_padding_parameter", 0)) for row in rows], "maxpool cfg Darknet padding 参数。")
    op_array("S2A_MAXPOOL_ACTUAL_PAD_LEFT", 8, [int(row["parameters"].get("padding_lrtb_actual", [0, 0, 0, 0])[0]) for row in rows], "maxpool 实际左 padding。")
    op_array("S2A_MAXPOOL_ACTUAL_PAD_RIGHT", 8, [int(row["parameters"].get("padding_lrtb_actual", [0, 0, 0, 0])[1]) for row in rows], "maxpool 实际右 padding。")
    op_array("S2A_MAXPOOL_ACTUAL_PAD_TOP", 8, [int(row["parameters"].get("padding_lrtb_actual", [0, 0, 0, 0])[2]) for row in rows], "maxpool 实际上 padding。")
    op_array("S2A_MAXPOOL_ACTUAL_PAD_BOTTOM", 8, [int(row["parameters"].get("padding_lrtb_actual", [0, 0, 0, 0])[3]) for row in rows], "maxpool 实际下 padding。")
    op_array("S2A_MAXPOOL_WINDOW_ORIGIN_Y", 16, [int(row["parameters"].get("window_origin_yx_at_output_0", [0, 0])[0]) for row in rows], "maxpool 第一个输出窗口起始 y。")
    op_array("S2A_MAXPOOL_WINDOW_ORIGIN_X", 16, [int(row["parameters"].get("window_origin_yx_at_output_0", [0, 0])[1]) for row in rows], "maxpool 第一个输出窗口起始 x。")
    op_array("S2A_MAXPOOL_FORMULA", 2, [1 if row["op"] == "maxpool" else 0 for row in rows], "maxpool 输出尺寸公式编码。")
    op_array("S2A_UPSAMPLE_SCALE_BITS", 64, [int(row["parameters"].get("scale_bits", 0)) for row in rows], "nearest-repeat upsample 比例的 IEEE-754 位模式。")
    op_array("S2A_UPSAMPLE_STRIDE", 16, [int(row["parameters"].get("stride", 0)) for row in rows], "nearest-repeat upsample 整数比例。")
    op_array("S2A_UPSAMPLE_METHOD", 2, [1 if row["op"] == "upsample" else 0 for row in rows], "upsample 算法编码。")
    op_array("S2A_ROUTE_REQUANTIZATION", 2, [1 if row["op"] == "route" else 0 for row in rows], "route scale conversion 编码。")
    op_array("S2A_ROUTE_SLICE_ORDER", 2, [1 if row["op"] == "route" else 0 for row in rows], "route 先切片再按 cfg 顺序拼接。")
    op_array("S2A_YOLO_CLASSES", 16, [int(row["parameters"].get("classes", 0)) for row in rows], "YOLO 类别数。")
    op_array("S2A_YOLO_SCALE_X_Y_BITS", 64, [int(row["parameters"].get("scale_x_y_bits", 0)) for row in rows], "YOLO scale_x_y IEEE-754 位模式。")
    op_array("S2A_YOLO_NEW_COORDS", 8, [int(row["parameters"].get("new_coords", 0)) for row in rows], "YOLO new_coords 参数。")
    op_array("S2A_YOLO_HEAD_LOGIT_SCALE_BITS", 64, [int(row["parameters"].get("head_logit_scale_bits", 0)) for row in rows], "YOLO head logit scale 位模式。")
    lines.append(_array_2d("S2A_ROUTE_CHANNEL_START", 16, inputs_matrix["S2A_INPUT_ROUTE_CHANNEL_START"], "按来源顺序排列的 route C 轴切片起点。"))
    lines.append(_array_2d("S2A_ROUTE_CHANNEL_END", 16, inputs_matrix["S2A_INPUT_ROUTE_CHANNEL_END"], "按来源顺序排列的 route C 轴切片终点（exclusive）。"))
    lines.append(_array_2d("S2A_YOLO_ANCHOR_W", 16, [[row["parameters"].get("anchors_wh", [[0, 0]] * MAX_ANCHORS)[slot][0] for slot in range(MAX_ANCHORS)] for row in rows], "YOLO 六组 anchor 宽度。"))
    lines.append(_array_2d("S2A_YOLO_ANCHOR_H", 16, [[row["parameters"].get("anchors_wh", [[0, 0]] * MAX_ANCHORS)[slot][1] for slot in range(MAX_ANCHORS)] for row in rows], "YOLO 六组 anchor 高度。"))
    lines.append(_array_2d("S2A_YOLO_MASK", 16, [[row["parameters"].get("mask", [0] * MAX_MASK)[slot] for slot in range(MAX_MASK)] for row in rows], "YOLO 每个输出头的三项 anchor mask。"))
    lines.append(_sha_array("S2A_CONV_CANDIDATE_SHA256", [row["candidate_parameter_sha256"] for row in rows], "每个卷积层的 T23 canonical candidate digest。"))
    lines.append(_sha_array("S2A_ROUTE_CONTRACT_SHA256", [row["route_contract_sha256"] for row in rows], "原样 route slice/requantization 文本的 SHA-256。"))
    lines.append(_sha_array("S2A_MAXPOOL_FORMULA_SHA256", [row["maxpool_formula_sha256"] for row in rows], "原样 maxpool 公式文本的 SHA-256。"))

    lines.extend(
        [
            "",
            "  // 平坦通道顺序：按 convolutional layer_index 升序，再按 channel 升序。",
            "  // M/Q packed slice：[79:48]=positive_M，[47:40]=positive_Q，[39:8]=negative_M，[7:0]=negative_Q。",
        ]
    )
    for name, width, key, comment in (
        ("S2A_CONV_CHANNEL_LAYER_INDEX", 6, "layer_index", "平坦通道所属卷积层。"),
        ("S2A_CONV_CHANNEL_INDEX", 16, "channel", "平坦通道在本卷积层中的索引。"),
        ("S2A_CONV_WEIGHT_SCALE_BITS", 64, "weight_scale_bits", "原 manifest 每通道 weight scale 的 IEEE-754 binary64 位模式。"),
        ("S2A_CONV_FUSED_BIAS_FLOAT32_BITS", 32, "fused_bias_float32_bits", "原 manifest 每通道 fused bias 的 IEEE-754 binary32 位模式。"),
        ("S2A_CONV_BIAS_ACCUMULATOR_INT32", 32, "bias_accumulator_int32", "原 manifest 每通道 INT32 累加器 bias 的二补码位模式。"),
    ):
        values = []
        for item in channels:
            value = item[key]
            values.append(value & 0xFFFFFFFF if key == "bias_accumulator_int32" else value)
        lines.append(_array_1d(name, width, values, comment))
    mq = [
        (item["positive_M"] << 48)
        | (item["positive_Q"] << 40)
        | (item["negative_M"] << 8)
        | item["negative_Q"]
        for item in channels
    ]
    lines.append(_array_1d("S2A_T23_MQ_ROM", 80, mq, "完整 materialized T23 逐通道 M/Q 平坦 ROM，无重算或精度截断。"))
    lines.extend(["endpackage", ""])
    return "\n".join(lines).encode("utf-8")


def _binding_report(data: dict[str, Any], package_bytes: bytes, sizes: dict[str, int]) -> bytes:
    conv_rows = [
        {
            "layer_index": row["layer_index"],
            "cfg_section": row["cfg_section"],
            "flat_channel_base": row["mq_base"],
            "channel_count": row["mq_count"],
            "candidate_parameter_sha256": row["candidate_parameter_sha256"],
        }
        for row in data["layers"]
        if row["op"] == "convolutional"
    ]
    report = {
        "schema_version": "gestureforge_s2a_network_descriptor_rom_binding_v1",
        "task_id": "S2A-T63",
        "status": "GENERATED_AND_INPUTS_VALIDATED",
        "source_bindings": [
            {"path": path, "sha256": data["source_hashes"][path], "bytes": sizes[path]}
            for path in (G0_SPEC_PATH, MANIFEST_PATH, T22_PATH, T23_PATH)
        ],
        "descriptor_summary": {
            "model_id": "tiny416",
            "layer_count": len(data["layers"]),
            "operator_counts": data["operator_counts"],
            "flat_conv_channels": len(data["channels"]),
            "channel_order": "ascending convolution layer_index, then ascending channel index",
            "requantization_rom_storage_layout": {
                "bits_79_48": "positive_M",
                "bits_47_40": "positive_Q (unsigned 8-bit ROM storage)",
                "bits_39_8": "negative_M",
                "bits_7_0": "negative_Q (unsigned 8-bit ROM storage)",
                "frozen_engine_port_width": False,
                "consumer_rule": "zero extend Q to the existing 32-bit engine parameter port",
            },
            "serial_dispatch": data["serial_dispatch"],
            "global_timeout_one_deadline": data["global_timeout_one_deadline"],
            "per_layer_timeout_restart": data["per_layer_timeout_restart"],
            "ps_visible_csr_changed": data["ps_visible_csr_changed"],
            "memory_outstanding_limit": data["memory_outstanding_limit"],
            "yolo_aliases": [
                {
                    "layer_index": row["layer_index"],
                    "tensor_index": row["output"]["tensor_index"],
                    "alias_of_layer_index": row["output"]["alias_of_layer_index"],
                    "memory_write_required": row["output"]["memory_write_required"],
                    "address": row["output"]["address"],
                    "length_bytes": row["output"]["length_bytes"],
                    "shape_nchw": row["output"]["shape_nchw"],
                    "scale_bits": f"{row['output']['scale_bits']:016X}",
                }
                for row in data["layers"]
                if row["op"] == "yolo"
            ],
            "convolution_candidate_digests": conv_rows,
        },
        "generated_package": {
            "path": PACKAGE_PATH,
            "sha256": _sha256_bytes(package_bytes),
            "bytes": len(package_bytes),
            "format": "read-only SystemVerilog package constants",
            "vivado_or_xsim_run": "NOT_RUN_BY_TASK_SCOPE",
        },
    }
    encoded = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    return encoded.encode("utf-8")


def _output_paths(root: Path) -> tuple[Path, Path]:
    return (
        root.joinpath(*PACKAGE_PATH.split("/")),
        root.joinpath(*BINDING_REPORT_PATH.split("/")),
    )


def generate(root: Path, check_only: bool = False) -> dict[str, Any]:
    """只生成白名单内的 SV package 与绑定报告，且默认拒绝覆盖。"""
    root = root.resolve()
    _require(os.path.normcase(str(root)) == os.path.normcase(str(EXPECTED_ROOT)), "输出根目录不是任务卡指定路径")
    frozen = load_frozen_inputs(root, verify_upstream=True)
    data = build_rom_data(frozen["manifest"], frozen["contract"], frozen["table"], frozen["hashes"])
    weight_package = frozen["manifest"]["address_map"]["weight_package"]
    data["weight_package"] = {
        "address": _checked_int(weight_package["address"], "GF8 package base", 0, 0xFFFFFFFF),
        "length_bytes": _checked_int(weight_package["length_bytes"], "GF8 package length", 1, 0xFFFFFFFF),
    }
    package_bytes = render_sv_package(data)
    report_bytes = _binding_report(data, package_bytes, frozen["sizes"])
    package_path, report_path = _output_paths(root)
    for path in (package_path, report_path):
        _require(path.parent.is_dir(), f"输出父目录不存在: {path.parent}")

    if check_only:
        _require(package_path.is_file() and report_path.is_file(), "检查模式要求 package 与绑定报告已存在")
        _require(package_path.read_bytes() == package_bytes, "现有 SystemVerilog package 与重生成字节不一致")
        _require(report_path.read_bytes() == report_bytes, "现有绑定报告与重生成字节不一致")
    else:
        _require(not package_path.exists(), f"拒绝覆盖已存在 package: {package_path}")
        _require(not report_path.exists(), f"拒绝覆盖已存在绑定报告: {report_path}")
        with package_path.open("xb") as handle:
            handle.write(package_bytes)
        with report_path.open("xb") as handle:
            handle.write(report_bytes)
    return {
        "package_path": package_path,
        "package_sha256": _sha256_bytes(package_bytes),
        "package_bytes": len(package_bytes),
        "binding_report_path": report_path,
        "binding_report_sha256": _sha256_bytes(report_bytes),
        "binding_report_bytes": len(report_bytes),
        "layer_count": len(data["layers"]),
        "channel_count": len(data["channels"]),
        "operator_counts": data["operator_counts"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="确定性生成 S2A-T63 tiny416 只读描述符 ROM")
    parser.add_argument("--repo-root", type=Path, default=EXPECTED_ROOT)
    parser.add_argument("--check", action="store_true", help="只验证已生成文件与确定性重生成字节一致")
    arguments = parser.parse_args(argv)
    try:
        summary = generate(arguments.repo_root, check_only=arguments.check)
    except (DescriptorRomError, OSError, ValueError) as exc:
        print(f"S2A-T63 descriptor error: {exc}", file=sys.stderr)
        return 2
    action = "checked" if arguments.check else "generated"
    counts = ",".join(f"{name}={summary['operator_counts'][name]}" for name in OP_COUNTS)
    print(
        f"S2A-T63 descriptor {action}: layers={summary['layer_count']} channels={summary['channel_count']} "
        f"ops={counts} package_sha256={summary['package_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
