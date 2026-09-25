"""S2A-T22：从冻结 manifest 构建并校验 tiny416 整网内部 dispatch contract。"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable


G0_SPEC_PATH = "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
MANIFEST_PATH = "report/evidence/S2A-T01/tiny416_model_manifest.json"
FIXED_SAMPLES_PATH = "report/evidence/S2A-T01/fixed_test_samples.json"
T16_PROOF_PATH = "report/evidence/S2A-T16/conv_requant_proof.json"
T16_SCRIPT_PATH = "verification/s2a_conv_requant_proof.py"

# 文件内容在 T22 基线冻结。改变任一来源时必须先审查来源变化，再更新 pin。
PINNED_SOURCES: tuple[tuple[str, str, str], ...] = (
    (G0_SPEC_PATH, "formal_g0_specification", "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230"),
    (MANIFEST_PATH, "frozen_model_manifest", "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a"),
    (FIXED_SAMPLES_PATH, "fixed_network_input_samples", "ccf741c1e996c72b985ce1dcbd399c5184347c922d286a8c0250ef5f6a755eed"),
    ("verification/s2a_model_delivery.py", "manifest_generator", "4831fff0e8ebb189ac9767ae423ad8d5268fc5bee5e333cc2a132112ccfdaab8"),
    ("src/s2a_runtime_shell.sv", "g0_runtime_shell_and_memory_boundary", "c784de2c94456eb4bdbd9ff763454b9784ebcb8d8821d6505d68707cfc37e52e"),
    ("src/s2a_control_csr.sv", "g0_csr_control_and_global_timeout", "97fc62dd1967ea9486db1c6e48134283d62005805a0ca5ef44d6ea70ab2fc9d2"),
    ("src/s2a_memory_master.sv", "g0_single_outstanding_memory_master", "721d7e09356986d23a6c1f723fe49322057b05aa02ac27e1b5887789b8bacf07"),
    (T16_PROOF_PATH, "t16_exact_requantization_proof", "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24"),
    (T16_SCRIPT_PATH, "t16_requantization_proof_generator", "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9"),
    ("src/s2a_conv_engine.sv", "convolution_scalar_engine", "8656f43f510a8f7c74aaee44f809da74adeb3b8c5fed32f8f009aabecb05c994"),
    ("src/s2a_maxpool_engine.sv", "maxpool_scalar_engine", "3dbb1fd41fbe773debade2629e8e7565554d14051a906466042906bb925de7b7"),
    ("src/s2a_route_engine.sv", "route_scalar_engine", "4748df19474e6b90e11bb760854311da92ba8d19a5b1d4b12e3d7b2b7968fe44"),
    ("src/s2a_upsample_engine.sv", "upsample_scalar_engine", "2c08bbc9c1d85e94de448f613617a5d584fe5682d0c4858d550bf377302e195b"),
    ("src/s2a_upsample_layer_scheduler.sv", "t18_upsample_layer_pilot", "1473fd371c65658e105ff2ad575d523a98a53e5c5ebd8bb9f21ca33b61678bce"),
    ("src/s2a_route_layer_scheduler.sv", "t19_route_layer_pilot", "ff078b830f76ca12baaa307e65f90958c0d0938fd0d1a4489955c2021a5d94d1"),
    ("src/s2a_conv_layer_scheduler.sv", "t20_convolution_layer_pilot", "581625dac4dd08b058af10f7d9f93e63bf13f86d1ec4780d3b20d95668076b55"),
    ("src/s2a_maxpool_layer_scheduler.sv", "t21_maxpool_layer_pilot", "9e0464d472786b5962e2927bcaf036a02f4f095194fbd4bc0602b187da61c9e2"),
    ("sim/tb_s2a_upsample_layer_scheduler.sv", "t18_upsample_layer_pilot_testbench", "ec15fd8a86a6c63e1a0ffa2fe4059c644cb61a78cd01f1ebef03901f917469de"),
    ("verification/test_s2a_upsample_layer_scheduler_rtl.py", "t18_upsample_layer_pilot_runner", "c8ddc62aae0a1da19379c600349de4380287afec85f82727828b0cd55ec5af1b"),
    ("report/evidence/S2A-T18/upsample_layer_scheduler_simulation.json", "t18_upsample_layer_pilot_evidence", "0f2a4a81275ffa225babb78b767bfc42a597320308ef7b150af5f80fd6aac35d"),
    ("sim/tb_s2a_route_layer_scheduler.sv", "t19_route_layer_pilot_testbench", "63a82b0b74e68874ff24810e9598a9d0c1b536bb2da4fd2aaa008ee6e5ff8755"),
    ("verification/test_s2a_route_layer_scheduler_rtl.py", "t19_route_layer_pilot_runner", "9c84dee53e87333f991f2536a0d98719ad3e3964ea095e12ce069406c846bbc0"),
    ("report/evidence/S2A-T19/route_layer_scheduler_simulation.json", "t19_route_layer_pilot_evidence", "e3921f382fc8c6af3dea5ec9edf3fd9795a49e09982381e2501ad8d9aa592880"),
    ("sim/tb_s2a_conv_layer_scheduler.sv", "t20_convolution_layer_pilot_testbench", "2fa2645075e2c7c105415f31795605c86dfd05713496cad7e05e4d1edb0543c3"),
    ("verification/test_s2a_conv_layer_scheduler_rtl.py", "t20_convolution_layer_pilot_runner", "9474108ee39ed1d89113241ebaef1ac177a0d0cca6878dbfc1415f25543117c2"),
    ("report/evidence/S2A-T20/conv_layer_scheduler_simulation.json", "t20_convolution_layer_pilot_evidence", "d6bc16966a2d3c7707d98aafa6b435ae158cd28faa53baa8f795e13e86a17887"),
    ("sim/tb_s2a_maxpool_layer_scheduler.sv", "t21_maxpool_layer_pilot_testbench", "e6ccd72ccac0ef7271a065b3f3b479768bac2b0835a0b600e6df3316da691f10"),
    ("verification/test_s2a_maxpool_layer_scheduler_rtl.py", "t21_maxpool_layer_pilot_runner", "b55d81b2596649f3eec8f231c7719b2465e384adeed477cce26af48899bc4556"),
    ("report/evidence/S2A-T21/maxpool_layer_scheduler_simulation.json", "t21_maxpool_layer_pilot_evidence", "312543ef841e7bb9831f3a98331dda46af95648082787d9bb3f7457f86e9107d"),
    ("sim/tb_s2a_upsample_engine.sv", "t13_upsample_engine_testbench", "bb2e9f83dd1a27f18d16538cd8caf d08c856e309fc5af53428e468e16fa43b9d".replace(" ", "")),
    ("verification/test_s2a_upsample_engine_rtl.py", "t13_upsample_engine_runner", "86c3ebded47494d7683f94a0dc57c3f732352e7b33321b561b553d02690e391a"),
    ("report/evidence/S2A-T13/upsample_simulation.json", "t13_upsample_engine_evidence", "ee9c1c0cdd4500eac6398ef0eb0a893021aee3b66d4845e50930f7cfac15d04e"),
    ("sim/tb_s2a_maxpool_engine.sv", "t14_maxpool_engine_testbench", "e51bbf09926cb3128466830b58f9f5081ef03b88ed193b2e4fec86b03b8684da"),
    ("verification/test_s2a_maxpool_engine_rtl.py", "t14_maxpool_engine_runner", "4d4a336ba352a619f24f416a821a5f713af56f5d1ffae f22959d013bd2a98607".replace(" ", "")),
    ("report/evidence/S2A-T14/maxpool_simulation.json", "t14_maxpool_engine_evidence", "2e681fb5db9037f6858c7516b4620053374d571e66d27c15ded6dfbffb8927e3"),
    ("sim/tb_s2a_route_engine.sv", "t15_route_engine_testbench", "8de3c9bb146527e8017faa919b9b591397ee90bacc36aaed3f742ed3413586eb"),
    ("verification/test_s2a_route_engine_rtl.py", "t15_route_engine_runner", "f49d00c24e22850024209872504bcf5a93165eaf79c2b04fad15f6056e163937"),
    ("report/evidence/S2A-T15/route_simulation.json", "t15_route_engine_evidence", "6011c3272c05b8e428128410b0d7a25a689873a12404631f23dc707f1fa9f124"),
    ("sim/tb_s2a_conv_engine.sv", "t17_convolution_engine_testbench", "2b642eb47cded4644e4e9ba3a1e3fa60d484cf795ec6e51dd8d4cfcc97d2f001"),
    ("verification/test_s2a_conv_engine_rtl.py", "t17_convolution_engine_runner", "adbb7e2574c50fd8e702e386a0898d27a0e4a16aebfc782436e386d56c768357"),
    ("report/evidence/S2A-T17/conv_engine_simulation.json", "t17_convolution_engine_evidence", "4cd1d0f0e5edf7b34907179dea47a9a9c0994eb1d8bd89adfa341067cac17ab2"),
)

EXPECTED_OP_COUNTS = {
    "convolutional": 21,
    "maxpool": 3,
    "route": 11,
    "upsample": 1,
    "yolo": 2,
}
EXPECTED_MODEL_BINDINGS = {
    "cfg": "5475dff0daa8ac791ffbfcd10a188aa63d146244e561d62867ac59d627725376",
    "darknet_weights": "3984affa0a7fdd83ff851646139ea4e734c3df93569bfbaab214774cd92f7d8a",
    "gf8_package": "f6feb6d489318ee9774fc406e9222cd9b881fbe33a40f32362366cf38693cc39",
}
EXPECTED_HEAD_ALIASES = {30: 29, 37: 36}
SHA256_LENGTH = 64


class ContractError(ValueError):
    """输入资料与冻结的 G0/来源绑定不一致。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == SHA256_LENGTH
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def _canonical_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"无法按 UTF-8 JSON 读取 {path}: {exc}") from exc


def collect_source_bindings(repo_root: Path) -> list[dict[str, str]]:
    """验证固定文件 pin，并返回证据中的相对路径和 SHA-256。"""
    if not repo_root.is_dir():
        raise ContractError(f"仓库根目录不存在或不是目录: {repo_root}")
    records: list[dict[str, str]] = []
    for relative_path, role, expected_sha256 in PINNED_SOURCES:
        source_path = repo_root.joinpath(*relative_path.split("/"))
        if not source_path.is_file():
            raise ContractError(f"来源文件缺失: {relative_path}")
        actual_sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if actual_sha256 != expected_sha256:
            raise ContractError(
                f"来源 SHA-256 不匹配: {relative_path}: "
                f"expected={expected_sha256}, actual={actual_sha256}"
            )
        records.append({"path": relative_path, "role": role, "sha256": actual_sha256})
    validate_source_binding_records(records)
    return records


def validate_source_binding_records(records: Iterable[dict[str, Any]]) -> None:
    """校验 contract 携带了完整且未改写的固定来源清单。"""
    by_path: dict[str, dict[str, Any]] = {}
    for record in records:
        path = record.get("path")
        _require(isinstance(path, str), "来源绑定缺少 path")
        _require(path not in by_path, f"来源绑定重复: {path}")
        by_path[path] = record
    expected_paths = {path for path, _, _ in PINNED_SOURCES}
    _require(set(by_path) == expected_paths, "来源绑定缺项或包含未批准路径")
    for path, role, expected_sha256 in PINNED_SOURCES:
        record = by_path[path]
        _require(record.get("role") == role, f"来源角色不匹配: {path}")
        _require(_is_sha256(record.get("sha256")), f"来源 SHA-256 格式无效: {path}")
        _require(record["sha256"].lower() == expected_sha256, f"来源 SHA-256 pin 不匹配: {path}")


def _shape_nchw(value: Any, name: str) -> list[int]:
    _require(
        isinstance(value, list)
        and len(value) == 4
        and all(isinstance(part, int) and not isinstance(part, bool) and part > 0 for part in value),
        f"{name} 必须是四个正整数的 NCHW 形状",
    )
    return list(value)


def _tensor_bytes(shape: list[int]) -> int:
    result = 1
    for extent in shape:
        result *= extent
    return result


def _input_ref_descriptors(
    row: dict[str, Any],
    layer_index: int,
    outputs_by_layer: dict[int, dict[str, Any]],
    network_input: dict[str, Any],
) -> list[dict[str, Any]]:
    refs = row.get("input_tensor_indices")
    _require(isinstance(refs, list) and len(refs) > 0, f"layer {layer_index}: input refs 无效")
    descriptors: list[dict[str, Any]] = []
    for ref_position, ref in enumerate(refs):
        if ref == "network_input":
            _require(layer_index == 0 and len(refs) == 1, "network_input 哨兵仅允许作为 layer 0 的唯一输入")
            source = network_input
            descriptor = {
                "input_order": ref_position,
                "kind": "network_input",
                "source_index": "network_input",
                "address_space": "G0 logical input",
                "address": source["address"],
                "length_bytes": source["length_bytes"],
                "byte_range_half_open": [source["address"], source["address"] + source["length_bytes"]],
                "shape_nchw": list(source["shape_nchw"]),
                "scale": source["scale"],
                "layout": "NCHW",
                "element_type": "int8_twos_complement",
            }
        else:
            _require(isinstance(ref, int) and not isinstance(ref, bool), f"layer {layer_index}: 输入 ref 类型无效")
            _require(0 <= ref < layer_index, f"layer {layer_index}: 输入 ref {ref} 不是更早的层")
            _require(ref in outputs_by_layer, f"layer {layer_index}: 输入 ref {ref} 未解析到 producer")
            source = outputs_by_layer[ref]
            _require(source["op"] != "yolo", f"layer {layer_index}: 不得把 YOLO alias 当作 producer")
            descriptor = {
                "input_order": ref_position,
                "kind": "layer_output",
                "source_index": ref,
                "address_space": "G0 logical feature workspace",
                "address": source["address"],
                "length_bytes": source["length_bytes"],
                "byte_range_half_open": list(source["byte_range_half_open"]),
                "shape_nchw": list(source["shape_nchw"]),
                "scale": source["scale"],
                "layout": source["layout"],
                "element_type": source["element_type"],
            }
        descriptors.append(descriptor)

    source_shapes = [descriptor["shape_nchw"] for descriptor in descriptors]
    expected_shapes: Any = source_shapes if row.get("op") == "route" else (source_shapes[0] if len(source_shapes) == 1 else source_shapes)
    _require(row.get("input_shape_nchw") == expected_shapes, f"layer {layer_index}: input shape 与来源 tensor 不一致")
    _require(row.get("layout") == "NCHW", f"layer {layer_index}: layout 不是 NCHW")
    _require(row.get("element_type") == "int8_twos_complement", f"layer {layer_index}: element_type 不是 INT8")
    scales = [descriptor["scale"] for descriptor in descriptors]
    if row.get("op") != "route":
        _require(row.get("input_scale") == scales[0], f"layer {layer_index}: input_scale 与来源不一致")
    if row.get("op") == "route" or len(descriptors) > 1:
        _require(row.get("input_scales") == scales, f"layer {layer_index}: 多输入 scale 顺序/值不一致")
    elif "input_scales" in row:
        _require(row["input_scales"] == scales, f"layer {layer_index}: input_scales 与来源不一致")
    return descriptors


def _check_operator_geometry(row: dict[str, Any], inputs: list[dict[str, Any]], output_shape: list[int], index: int) -> None:
    op = row["op"]
    if op == "convolutional":
        _require(len(inputs) == 1, f"layer {index}: convolutional 必须只有一个输入")
        kernel = row.get("kernel_hw")
        stride = row.get("stride_hw")
        padding = row.get("padding_lrtb")
        _require(isinstance(kernel, list) and len(kernel) == 2, f"layer {index}: convolution kernel 无效")
        _require(isinstance(stride, list) and len(stride) == 2 and min(stride) > 0, f"layer {index}: convolution stride 无效")
        _require(isinstance(padding, list) and len(padding) == 4 and min(padding) >= 0, f"layer {index}: convolution padding 无效")
        source = inputs[0]["shape_nchw"]
        expected_hw = [
            (source[2] + padding[2] + padding[3] - kernel[0]) // stride[0] + 1,
            (source[3] + padding[0] + padding[1] - kernel[1]) // stride[1] + 1,
        ]
        _require(output_shape[0] == source[0] and output_shape[1] > 0, f"layer {index}: convolution N/C 输出无效")
        _require(output_shape[2:] == expected_hw, f"layer {index}: convolution 输出空间尺寸与 kernel/stride/padding 不符")
    elif op == "maxpool":
        _require(len(inputs) == 1, f"layer {index}: maxpool 必须只有一个输入")
        source = inputs[0]["shape_nchw"]
        kernel = row.get("kernel_hw")
        stride = row.get("stride_hw")
        padding_parameter = row.get("darknet_padding_parameter")
        _require(isinstance(kernel, list) and len(kernel) == 2, f"layer {index}: maxpool kernel 无效")
        _require(isinstance(stride, list) and len(stride) == 2 and min(stride) > 0, f"layer {index}: maxpool stride 无效")
        _require(isinstance(padding_parameter, int) and padding_parameter >= 0, f"layer {index}: Darknet padding 无效")
        expected_hw = [
            (source[2] + padding_parameter - kernel[0]) // stride[0] + 1,
            (source[3] + padding_parameter - kernel[1]) // stride[1] + 1,
        ]
        _require(output_shape[0] == source[0] and output_shape[1] == source[1], f"layer {index}: maxpool 不得改变 N/C")
        _require(output_shape[2:] == expected_hw, f"layer {index}: maxpool 输出尺寸与 Darknet 公式不符")
        _require(row.get("padding_lrtb_actual") == [0, 0, 0, 0], f"layer {index}: tiny416 maxpool 实际 padding 应为 0")
        _require(row.get("window_origin_yx_at_output_0") == [0, 0], f"layer {index}: maxpool 窗口原点不符")
    elif op == "upsample":
        _require(len(inputs) == 1, f"layer {index}: upsample 必须只有一个输入")
        source = inputs[0]["shape_nchw"]
        stride = row.get("stride")
        _require(isinstance(stride, int) and stride > 0, f"layer {index}: upsample stride 无效")
        _require(row.get("method") == "nearest_repeat", f"layer {index}: upsample 必须使用 nearest_repeat")
        _require(output_shape == [source[0], source[1], source[2] * stride, source[3] * stride], f"layer {index}: upsample 输出形状不符")
        _require(row.get("output_scale") == inputs[0]["scale"], f"layer {index}: upsample 必须保留输入 scale")
    elif op == "route":
        _require(len(inputs) >= 1, f"layer {index}: route 至少需要一个 cfg 输入")
        source_shapes = [item["shape_nchw"] for item in inputs]
        _require(all(shape[0] == source_shapes[0][0] and shape[2:] == source_shapes[0][2:] for shape in source_shapes), f"layer {index}: route 输入 N/H/W 不一致")
        ranges = row.get("route_source_channel_ranges")
        groups = row.get("route_groups")
        group_id = row.get("route_group_id")
        _require(isinstance(ranges, list) and len(ranges) == len(inputs), f"layer {index}: route source ranges 数量不符")
        _require(isinstance(groups, int) and groups > 0 and isinstance(group_id, int) and 0 <= group_id < groups, f"layer {index}: route groups/group_id 无效")
        selected_channels = 0
        for source_shape, channel_range in zip(source_shapes, ranges):
            _require(isinstance(channel_range, list) and len(channel_range) == 2, f"layer {index}: route channel range 无效")
            low, high = channel_range
            _require(0 <= low < high <= source_shape[1], f"layer {index}: route channel range 越界")
            _require((high - low) * groups == source_shape[1], f"layer {index}: route channel range 与 groups 不符")
            selected_channels += high - low
        _require(output_shape == [source_shapes[0][0], selected_channels, source_shapes[0][2], source_shapes[0][3]], f"layer {index}: route concat 输出形状不符")
        _require(row.get("output_scale") == max(item["scale"] for item in inputs), f"layer {index}: route 目标 scale 不等于输入最大 scale")
    elif op == "yolo":
        _require(len(inputs) == 1, f"layer {index}: yolo alias 必须只有一个来源")
        _require(output_shape == inputs[0]["shape_nchw"], f"layer {index}: yolo alias 形状必须与来源一致")


def _parameter_hash_info(row: dict[str, Any], key: str, layer_index: int) -> dict[str, Any]:
    value = row.get(key)
    _require(isinstance(value, list), f"layer {layer_index}: manifest 参数 {key} 缺失")
    return {
        "manifest_path": f"{MANIFEST_PATH}#/layers/{layer_index}/{key}",
        "element_count": len(value),
        "canonical_json_sha256": _canonical_sha256(value),
    }


def _conv_parameter_descriptor(
    row: dict[str, Any],
    layer_index: int,
    proof_layers: dict[int, dict[str, Any]],
    manifest: dict[str, Any],
    proof: dict[str, Any],
    proof_sha256: str,
) -> dict[str, Any]:
    output_shape = row["output_shape_nchw"]
    input_shape = row["input_shape_nchw"]
    groups = row.get("groups")
    _require(isinstance(groups, int) and groups > 0 and input_shape[1] % groups == 0, f"layer {layer_index}: convolution groups 无效")
    _require(row.get("weight_layer_index") == layer_index, f"layer {layer_index}: weight_layer_index 与 cfg 层不符")
    offsets = row.get("gf8_parameter_offsets")
    _require(isinstance(offsets, dict), f"layer {layer_index}: GF8 offsets 缺失")
    weight_offset = offsets.get("quantized_weight_offset")
    weight_bytes = offsets.get("quantized_weight_bytes")
    kernel = row["kernel_hw"]
    expected_weight_bytes = output_shape[1] * (input_shape[1] // groups) * kernel[0] * kernel[1]
    _require(isinstance(weight_offset, int) and weight_offset >= 0, f"layer {layer_index}: GF8 weight offset 无效")
    _require(weight_bytes == expected_weight_bytes, f"layer {layer_index}: GF8 weight length 与 cfg dimensions 不符")
    package = manifest["address_map"]["weight_package"]
    _require(weight_offset + weight_bytes <= package["length_bytes"], f"layer {layer_index}: GF8 weight 半开范围越界")
    conv_proof = proof_layers.get(layer_index)
    _require(conv_proof is not None, f"layer {layer_index}: T16 requant proof 缺层")
    _require(conv_proof.get("cfg_section") == row["cfg_section"], f"layer {layer_index}: T16 cfg section 不匹配")
    _require(conv_proof.get("activation") == row["activation"], f"layer {layer_index}: T16 activation 不匹配")
    _require(conv_proof.get("output_channels_audited") == output_shape[1], f"layer {layer_index}: T16 输出通道数不匹配")
    _require(conv_proof.get("channels_with_exact_candidate") == output_shape[1], f"layer {layer_index}: T16 存在未证明通道")
    candidate_hash = conv_proof.get("candidate_parameter_sha256")
    _require(_is_sha256(candidate_hash), f"layer {layer_index}: T16 candidate parameter hash 无效")
    return {
        "cfg_binding": {
            "manifest_path": "manifest.bindings.cfg",
            "source_path": manifest["bindings"]["cfg"]["path"],
            "source_sha256": manifest["bindings"]["cfg"]["sha256"],
            "cfg_section": row["cfg_section"],
            "weight_layer_index": row["weight_layer_index"],
        },
        "gf8_weight": {
            "manifest_path": f"{MANIFEST_PATH}#/layers/{layer_index}/gf8_parameter_offsets",
            "package_source_path": manifest["bindings"]["gf8_package"]["path"],
            "package_sha256": manifest["bindings"]["gf8_package"]["sha256"],
            "package_base_address": package["address"],
            "package_length_bytes": package["length_bytes"],
            "offset_bytes": weight_offset,
            "length_bytes": weight_bytes,
            "package_byte_range_half_open": [weight_offset, weight_offset + weight_bytes],
            "logical_memory_address": package["address"] + weight_offset,
            "logical_memory_range_half_open": [package["address"] + weight_offset, package["address"] + weight_offset + weight_bytes],
            "all_parameter_offsets": dict(offsets),
        },
        "bias_source": {
            "accumulator_bias_int32": _parameter_hash_info(row, "bias_accumulator_int32_per_output_channel", layer_index),
            "fused_bias_float32": _parameter_hash_info(row, "fused_bias_float32_per_output_channel", layer_index),
            "gf8_fused_bias_offset_bytes": offsets.get("fused_bias_offset"),
            "semantics": proof["semantics"]["bias"],
        },
        "weight_scale_source": _parameter_hash_info(row, "weight_scale_per_output_channel", layer_index),
        "t16_requantization_source": {
            "proof_path": T16_PROOF_PATH,
            "proof_sha256": proof_sha256,
            "proof_layer_index": conv_proof["layer_index"],
            "candidate_parameter_sha256": candidate_hash,
            "target_threshold_sha256": conv_proof["target_threshold_sha256"],
            "candidate_algorithm": proof["semantics"]["candidate"],
            "channel_payload_materialized_in_proof_json": False,
            "channel_payload_readiness": "HASH_ONLY; T16 audit computes exact per-channel candidates and hashes them, but its proof JSON stores only the summary and digest",
            "materialization_source": "The pinned T16 audit script can deterministically rederive the channel candidates from the frozen manifest; the current proof JSON does not serialize those values",
            "backend_dependency": "T23 must expose/re-run that deterministic calculation, materialize each output-channel M/Q, and verify the resulting canonical stream against candidate_parameter_sha256 before RTL integration",
        },
    }


def _contains_unexpected_golden_fields(value: Any) -> bool:
    marker_keys = {
        "cpu_per_layer_tensor_goldens",
        "per_layer_tensor_goldens",
        "per_layer_integer_tensor_goldens",
        "cpu_layer_output_tensors",
        "per_layer_golden_path",
        "per_layer_golden_sha256",
    }
    if isinstance(value, dict):
        return any(key in marker_keys or _contains_unexpected_golden_fields(child) for key, child in value.items())
    if isinstance(value, list):
        return any(_contains_unexpected_golden_fields(child) for child in value)
    return False


def derive_contract(
    manifest: dict[str, Any],
    fixed_samples: dict[str, Any],
    t16_proof: dict[str, Any],
    source_bindings: list[dict[str, str]],
) -> dict[str, Any]:
    """从已绑定输入派生规范化的 38 层 contract；不访问或改写工作区。"""
    validate_source_binding_records(source_bindings)
    _require(manifest.get("schema_version") == "gestureforge_s2a_model_manifest_v1", "manifest schema_version 不匹配")
    _require(manifest.get("status") == "G0_FROZEN", "model manifest 尚未冻结为 G0")
    _require(manifest.get("model", {}).get("model_id") == "tiny416", "阶段 2A 默认模型不是 tiny416")
    _require(manifest.get("model", {}).get("architecture") == "YOLOv4-tiny", "架构与 G0 不符")
    _require(manifest.get("model", {}).get("input_wh") == [416, 416], "模型输入尺寸与 tiny416 不符")
    _require(manifest.get("model", {}).get("classes") == 5, "类别数与 G0 不符")
    _require(
        isinstance(manifest.get("operators"), list)
        and len(manifest["operators"]) == len(EXPECTED_OP_COUNTS)
        and set(manifest["operators"]) == set(EXPECTED_OP_COUNTS),
        "manifest operator 清单与 G0 不一致",
    )
    for binding_name, expected_sha256 in EXPECTED_MODEL_BINDINGS.items():
        actual_binding = manifest.get("bindings", {}).get(binding_name, {})
        _require(actual_binding.get("sha256") == expected_sha256, f"manifest {binding_name} hash 与冻结值不符")
    _require(manifest.get("fixed_test_samples_path") == FIXED_SAMPLES_PATH, "manifest 固定样本路径不匹配")

    address_map = manifest.get("address_map", {})
    network_input = address_map.get("input", {})
    feature_workspace = address_map.get("feature_workspace", {})
    weight_package = address_map.get("weight_package", {})
    _require(
        network_input.get("address") == 0
        and network_input.get("length_bytes") == 519168
        and network_input.get("shape_nchw") == [1, 3, 416, 416]
        and network_input.get("scale") == 0.007874015748031496,
        "G0 network input descriptor 不匹配",
    )
    _require(feature_workspace.get("base_address") == 0x01000000, "feature workspace base 与 G0 不匹配")
    _require(feature_workspace.get("alignment_bytes") == 64, "feature workspace alignment 与 G0 不匹配")
    _require(isinstance(feature_workspace.get("end_address_exclusive"), int), "feature workspace end 缺失")
    _require(weight_package.get("address") == 0x00100000, "GF8 package base 与 G0 不匹配")
    _require(weight_package.get("sha256") == EXPECTED_MODEL_BINDINGS["gf8_package"], "GF8 package hash 与 G0 不匹配")
    _require(weight_package.get("length_bytes") == manifest["bindings"]["gf8_package"].get("bytes"), "GF8 package 长度绑定不一致")

    _require(fixed_samples.get("schema_version") == "gestureforge_s2a_fixed_test_samples_v1", "fixed samples schema 不匹配")
    sample_manifest_binding = fixed_samples.get("model_manifest_binding", {})
    _require(sample_manifest_binding.get("path") == MANIFEST_PATH, "fixed samples 指向了不同 manifest")
    _require(sample_manifest_binding.get("sha256") == PINNED_SOURCES[1][2], "fixed samples manifest hash 不匹配")
    samples = fixed_samples.get("samples")
    _require(isinstance(samples, list) and len(samples) == 109, "fixed samples 必须恰有 109 项")
    _require(fixed_samples.get("sample_count") == len(samples), "fixed samples sample_count 与 rows 不一致")
    sample_ids: set[str] = set()
    frame_ids: set[int] = set()
    for sample_index, sample in enumerate(samples):
        _require(isinstance(sample, dict), f"fixed sample {sample_index} 不是 object")
        sample_id = sample.get("sample_id")
        frame_id = sample.get("frame_id")
        _require(isinstance(sample_id, str) and sample_id not in sample_ids, f"fixed sample {sample_index} sample_id 缺失/重复")
        _require(isinstance(frame_id, int) and frame_id not in frame_ids, f"fixed sample {sample_index} frame_id 缺失/重复")
        _require(_is_sha256(sample.get("pl_input_sha256")), f"fixed sample {sample_index} PL input hash 无效")
        sample_ids.add(sample_id)
        frame_ids.add(frame_id)
    input_contract = fixed_samples.get("pl_input_contract", {})
    _require(input_contract.get("tensor_shape_nchw") == network_input["shape_nchw"], "fixed sample NCHW shape 不匹配")
    _require(input_contract.get("tensor_dtype") == "signed int8 two's complement", "fixed sample dtype 不匹配")
    _require(input_contract.get("per_sample_hash") == "pl_input_sha256", "fixed sample input-hash field 不匹配")
    _require(not _contains_unexpected_golden_fields(fixed_samples), "fixed samples 出现未冻结的 per-layer golden 字段；需重新审查 readiness")

    control = manifest.get("control_protocol", {})
    memory = manifest.get("memory_protocol", {})
    timeout_text = control.get("timeout")
    completion_event = control.get("operator_completion_event", {})
    priority = control.get("priority")
    _require(isinstance(timeout_text, str) and "accepted start edge" in timeout_text and "Nth edge" in timeout_text, "G0 global timeout 语义缺失或改变")
    _require(completion_event.get("signals") == ["operator_result_valid", "operator_error_code[2:0]"], "G0 internal completion event 信号改变")
    _require("one-cycle pulse" in completion_event.get("handshake", "") and "no backpressure" in completion_event.get("handshake", ""), "G0 completion event handshake 语义改变")
    _require(priority == ["hard_reset", "soft_reset", "memory_or_argument_or_numeric_error", "completion", "timeout"], "G0 error/completion/timeout 优先级改变")
    _require("cancels a pending request" in memory.get("reset_abort", ""), "G0 abort/reset memory cancel 语义缺失")
    _require(len(manifest.get("layers", [])) == 38, "manifest 必须有 38 个 cfg layer")
    proof_layers_list = t16_proof.get("layers")
    _require(t16_proof.get("schema") == "GestureForge-S2A-T16-requant-proof-v1", "T16 proof schema 不匹配")
    _require(t16_proof.get("status") == "EXACT_FIXED_POINT_FOUND", "T16 proof 未达到精确 fixed-point 状态")
    _require(t16_proof.get("failures") == [], "T16 proof 存在失败")
    _require(isinstance(proof_layers_list, list) and len(proof_layers_list) == EXPECTED_OP_COUNTS["convolutional"], "T16 proof conv layer 数量不匹配")
    _require(t16_proof.get("binding", {}).get("manifest", {}).get("sha256") == PINNED_SOURCES[1][2], "T16 proof manifest 绑定不匹配")
    _require(t16_proof.get("binding", {}).get("audit_script", {}).get("sha256") == dict((path, sha) for path, _, sha in PINNED_SOURCES)[T16_SCRIPT_PATH], "T16 proof script 绑定不匹配")
    proof_layers = {item.get("layer_index"): item for item in proof_layers_list if isinstance(item, dict)}
    _require(len(proof_layers) == len(proof_layers_list), "T16 proof layer_index 重复")

    heads = address_map.get("heads", [])
    heads_by_yolo = {item.get("yolo_layer_index"): item for item in heads if isinstance(item, dict)}
    _require(set(heads_by_yolo) == set(EXPECTED_HEAD_ALIASES), "G0 detection heads/YOLO alias 索引不匹配")
    for yolo_index, producer_index in EXPECTED_HEAD_ALIASES.items():
        _require(heads_by_yolo[yolo_index].get("source_convolution_layer_index") == producer_index, f"YOLO layer {yolo_index} 来源 conv 不匹配")

    network_input_desc = {
        "address": network_input["address"],
        "length_bytes": network_input["length_bytes"],
        "shape_nchw": list(network_input["shape_nchw"]),
        "scale": network_input["scale"],
    }
    feature_base = feature_workspace["base_address"]
    feature_limit = feature_workspace["end_address_exclusive"]
    alignment = feature_workspace["alignment_bytes"]
    rows = manifest["layers"]
    contract_rows: list[dict[str, Any]] = []
    outputs_by_layer: dict[int, dict[str, Any]] = {}
    owned_ranges: list[tuple[int, int, int]] = []
    op_counts: dict[str, int] = {}
    unique_feature_bytes = 0

    for expected_index, row in enumerate(rows):
        _require(isinstance(row, dict), f"layer row {expected_index} 不是 object")
        index = row.get("layer_index")
        _require(index == expected_index, "manifest layer rows 必须按 layer_index 升序且不缺号")
        _require(row.get("cfg_section") == expected_index + 1, f"layer {index}: cfg_section 必须等于 index+1")
        op = row.get("op")
        _require(op in EXPECTED_OP_COUNTS, f"layer {index}: 不支持的 cfg op {op!r}")
        op_counts[op] = op_counts.get(op, 0) + 1
        inputs = _input_ref_descriptors(row, index, outputs_by_layer, network_input_desc)
        output_shape = _shape_nchw(row.get("output_shape_nchw"), f"layer {index} output_shape_nchw")
        _require(row.get("layout") == "NCHW", f"layer {index}: 输出 layout 不是 NCHW")
        _require(row.get("element_type") == "int8_twos_complement", f"layer {index}: 输出 element type 不是 INT8")
        output_scale = row.get("output_scale")
        _require(isinstance(output_scale, (int, float)) and not isinstance(output_scale, bool) and output_scale > 0, f"layer {index}: output scale 无效")
        output_bytes = _tensor_bytes(output_shape)
        _require(row.get("tensor_length_bytes") == output_bytes, f"layer {index}: output NCHW bytes 不匹配")
        address = row.get("tensor_address")
        _require(isinstance(address, int) and not isinstance(address, bool), f"layer {index}: tensor address 无效")
        end_address = address + output_bytes
        _require(feature_base <= address < end_address <= feature_limit, f"layer {index}: feature 半开地址范围越界")
        _check_operator_geometry(row, inputs, output_shape, index)

        is_alias = op == "yolo"
        alias_of: int | None = None
        if is_alias:
            head = heads_by_yolo.get(index)
            _require(head is not None, f"layer {index}: YOLO head metadata 缺失")
            alias_of = head["source_convolution_layer_index"]
            _require(row.get("input_tensor_indices") == [alias_of], f"layer {index}: YOLO input ref 不指向冻结来源 conv")
            producer = outputs_by_layer.get(alias_of)
            _require(producer is not None, f"layer {index}: YOLO 来源 conv 未生成")
            _require(row.get("output_tensor_index") == alias_of, f"layer {index}: output_tensor_index alias 不匹配")
            _require(address == producer["address"] and output_bytes == producer["length_bytes"], f"layer {index}: YOLO view 必須和 conv 共享地址/长度")
            _require(output_shape == producer["shape_nchw"] and output_scale == producer["scale"], f"layer {index}: YOLO view shape/scale 不匹配")
            _require(head.get("address") == address and head.get("length_bytes") == output_bytes, f"layer {index}: G0 head 地址/长度不匹配")
            _require(head.get("shape_nchw") == output_shape and head.get("int8_scale") == output_scale, f"layer {index}: G0 head shape/scale 不匹配")
        else:
            _require(address % alignment == 0, f"layer {index}: 独占 feature tensor 未按 {alignment} 字节对齐")
            owned_ranges.append((address, end_address, index))
            unique_feature_bytes += output_bytes

        params: dict[str, Any]
        if op == "convolutional":
            _require(row.get("activation") in ("linear", "leaky"), f"layer {index}: activation 不在 G0 支持集合")
            _require(row.get("accumulator_bits") == 32, f"layer {index}: accumulator width 不匹配 G0")
            _require(row.get("groups") == 1, f"layer {index}: tiny416 convolution groups 不为 1")
            params = {
                key: row[key]
                for key in ("kernel_hw", "stride_hw", "padding_lrtb", "groups", "padding_value_int8", "activation", "accumulator_bits", "output_scale", "weight_layer_index", "gf8_parameter_offsets")
            }
            out_channels = output_shape[1]
            _require(len(row.get("weight_scale_per_output_channel", [])) == out_channels, f"layer {index}: weight scale 通道数不匹配")
            _require(len(row.get("bias_accumulator_int32_per_output_channel", [])) == out_channels, f"layer {index}: INT32 bias 通道数不匹配")
            _require(len(row.get("fused_bias_float32_per_output_channel", [])) == out_channels, f"layer {index}: fused bias 通道数不匹配")
            params["parameters"] = _conv_parameter_descriptor(
                row,
                index,
                proof_layers,
                manifest,
                t16_proof,
                next(record["sha256"] for record in source_bindings if record["path"] == T16_PROOF_PATH),
            )
        elif op == "maxpool":
            params = {
                key: row[key]
                for key in ("kernel_hw", "stride_hw", "darknet_padding_parameter", "output_hw_formula", "window_origin_yx_at_output_0", "padding_lrtb_actual", "pad_value_int8", "output_scale")
            }
        elif op == "route":
            params = {
                key: row[key]
                for key in ("route_groups", "route_group_id", "route_source_channel_ranges", "route_group_slice_order", "requantization", "output_scale")
            }
        elif op == "upsample":
            params = {key: row[key] for key in ("scale", "stride", "method", "output_scale")}
        else:
            params = {key: row[key] for key in ("output_tensor_index", "classes", "scale_x_y", "new_coords", "head_logit_scale", "output_scale")}
            _require(row.get("classes") == manifest["model"]["classes"], f"layer {index}: YOLO classes 与模型不匹配")

        output_descriptor = {
            "tensor_index": alias_of if is_alias else index,
            "allocation_kind": "head_alias" if is_alias else "owned_feature_tensor",
            "alias_of_layer_index": alias_of,
            "memory_write_required": not is_alias,
            "address_space": "G0 logical feature workspace",
            "address": address,
            "length_bytes": output_bytes,
            "byte_range_half_open": [address, end_address],
            "shape_nchw": output_shape,
            "scale": output_scale,
            "layout": row["layout"],
            "element_type": row["element_type"],
        }
        contract_row = {
            "dispatch_order": expected_index,
            "layer_index": index,
            "cfg_section": row["cfg_section"],
            "op": op,
            "manifest_input_scale": row.get("input_scale"),
            "manifest_input_scale_semantics": (
                "legacy generic sequential-predecessor field; route inputs are authoritative only through input_scales and input_shape_nchw aligned with input_tensor_indices"
                if op == "route"
                else "single-source tensor scale, checked against the resolved input tensor"
            ),
            "manifest_source": f"{MANIFEST_PATH}#/layers/{index}",
            "manifest_source_row_canonical_sha256": _canonical_sha256(row),
            "input_tensors_in_manifest_order": inputs,
            "output_tensor": output_descriptor,
            "operator_parameters": params,
        }
        contract_rows.append(contract_row)
        outputs_by_layer[index] = {
            "op": op,
            "address": address,
            "length_bytes": output_bytes,
            "byte_range_half_open": [address, end_address],
            "shape_nchw": output_shape,
            "scale": output_scale,
            "layout": row["layout"],
            "element_type": row["element_type"],
        }

    _require(op_counts == EXPECTED_OP_COUNTS, f"operator count 与 G0 不匹配: {op_counts}")
    sorted_ranges = sorted(owned_ranges)
    for left, right in zip(sorted_ranges, sorted_ranges[1:]):
        _require(left[1] <= right[0], f"独占 feature tensor 地址重叠: layer {left[2]} 与 layer {right[2]}")
    _require(unique_feature_bytes == sum(row["tensor_length_bytes"] for row in rows if row["op"] != "yolo"), "唯一 feature byte 总数派生异常")
    _require(len([row for row in rows if row["op"] == "yolo"]) == len(EXPECTED_HEAD_ALIASES), "YOLO alias 数量错误")
    conv_indices = {row["layer_index"] for row in rows if row["op"] == "convolutional"}
    _require(set(proof_layers) == conv_indices, "T16 proof 的 conv layer 集合与 manifest 不一致")

    source_sha = {record["path"]: record["sha256"] for record in source_bindings}
    samples_per_sample_bytes = unique_feature_bytes
    return {
        "schema_version": "gestureforge_s2a_network_dispatch_contract_v1",
        "task_id": "S2A-T22",
        "artifact_status": "CONTRACT_VALIDATED",
        "scope": {
            "model_id": "tiny416",
            "purpose": "G1 internal 38-layer serial dispatch contract and frozen-manifest consistency validation",
            "rtl_written": False,
            "ps_visible_csr_changed": False,
            "memory_or_timeout_semantics_changed": False,
            "full_network_implementation": False,
            "g4_or_g5_claim": False,
            "vivado_or_vitis_run": False,
            "board_operation": False,
        },
        "source_bindings": source_bindings,
        "external_model_bindings_from_frozen_manifest": {
            name: {
                "source_path": manifest["bindings"][name]["path"],
                "sha256": manifest["bindings"][name]["sha256"],
                "length_bytes": manifest["bindings"][name].get("bytes"),
                "read_by_checker": False,
                "authority": f"{MANIFEST_PATH}#/bindings/{name}",
            }
            for name in ("cfg", "darknet_weights", "gf8_package")
        },
        "network_input": {
            **network_input_desc,
            "byte_range_half_open": [network_input_desc["address"], network_input_desc["address"] + network_input_desc["length_bytes"]],
            "layout": "NCHW",
            "element_type": "int8_twos_complement",
            "address_authority": f"{MANIFEST_PATH}#/address_map/input",
        },
        "network_dispatch": {
            "layer_count": len(contract_rows),
            "order": "strict ascending layer_index; cfg_section equals layer_index+1",
            "input_reference_rule": "network_input is a tagged external sentinel; integer references resolve only to earlier non-YOLO layer outputs; route input order is preserved verbatim",
            "feature_workspace": {
                "base_address": feature_base,
                "end_address_exclusive": feature_limit,
                "alignment_bytes": alignment,
                "address_space": "G0 logical simulation byte address; not Zynq DDR physical address",
                "legal_overlap_rule": "only YOLO layer 30->conv 29 and YOLO layer 37->conv 36 aliases; all owned feature output ranges are disjoint",
            },
            "operator_counts": op_counts,
            "owned_feature_tensor_bytes_per_sample": samples_per_sample_bytes,
            "fixed_sample_count": len(samples),
            "raw_unique_feature_tensor_bytes_for_fixed_samples": samples_per_sample_bytes * len(samples),
            "layers": contract_rows,
        },
        "operator_engine_mapping": {
            "convolutional": {
                "engine_source": "src/s2a_conv_engine.sv",
                "fixed_layer_scheduler_pilot": "src/s2a_conv_layer_scheduler.sv",
                "fixed_pilot_layer_indices": [36],
                "pilot_evidence": "report/evidence/S2A-T20/conv_layer_scheduler_simulation.json",
                "scope": "scalar engine plus one fixed full-layer pilot; not a 21-layer network backend",
            },
            "maxpool": {
                "engine_source": "src/s2a_maxpool_engine.sv",
                "fixed_layer_scheduler_pilot": "src/s2a_maxpool_layer_scheduler.sv",
                "fixed_pilot_layer_indices": [25],
                "pilot_evidence": "report/evidence/S2A-T21/maxpool_layer_scheduler_simulation.json",
                "scope": "scalar engine plus one fixed full-layer pilot; not a three-layer network backend",
            },
            "route": {
                "engine_source": "src/s2a_route_engine.sv",
                "fixed_layer_scheduler_pilot": "src/s2a_route_layer_scheduler.sv",
                "fixed_pilot_layer_indices": [34],
                "pilot_evidence": "report/evidence/S2A-T19/route_layer_scheduler_simulation.json",
                "scope": "scalar engine plus one fixed full-layer pilot; not an eleven-layer network backend",
            },
            "upsample": {
                "engine_source": "src/s2a_upsample_engine.sv",
                "fixed_layer_scheduler_pilot": "src/s2a_upsample_layer_scheduler.sv",
                "fixed_pilot_layer_indices": [33],
                "pilot_evidence": "report/evidence/S2A-T18/upsample_layer_scheduler_simulation.json",
                "scope": "scalar engine plus one fixed full-layer pilot; not a complete network backend",
            },
            "yolo": {
                "implementation_kind": "head_alias_only",
                "standalone_compute_engine": None,
                "fixed_aliases": {str(alias): source for alias, source in EXPECTED_HEAD_ALIASES.items()},
                "memory_write_required": False,
                "scope": "aliases the two source convolution tensors; does not implement PS decoding/NMS",
            },
        },
        "dispatch_protocol": {
            "ps_visible_csr": "unchanged G0 CSR; no per-layer descriptor registers",
            "memory_interface": "unchanged G0 single-outstanding T12 memory master contract",
            "global_timeout": {
                "source_semantics": timeout_text,
                "scope": "one deadline from accepted start for the whole network; layer transitions never restart it",
                "per_layer_timeout_restart_allowed": False,
                "t20_t21_local_timeout_counters_composable_as_is": False,
                "pilot_timeout_sources": ["src/s2a_conv_layer_scheduler.sv", "src/s2a_maxpool_layer_scheduler.sv"],
                "integration_requirement": "future backend must own one G0 deadline and replace/disable the T20/T21 local pilot timers",
            },
            "completion_event": {
                "source_signals": completion_event["signals"],
                "source_handshake": completion_event["handshake"],
                "source_success": completion_event["success"],
                "source_error": completion_event["error"],
                "source_timeout_boundary": completion_event["timeout_boundary"],
                "producer": "single whole-network backend after all required feature/head writes finish or a terminal error occurs",
                "pulse_cycles": 1,
                "backpressure": False,
                "one_event_per_accepted_task": True,
                "error_priority": list(priority),
            },
            "fault_and_cancel": {
                "memory_reset_timeout_semantics": memory["reset_abort"],
                "downstream_dispatch_after_terminal_fault": False,
                "known_operator_error_codes_1_to_7": "forward unchanged per G0",
                "unknown_nonzero_operator_error": "map to INTERNAL per G0",
            },
        },
        "golden_readiness": {
            "fixed_input_sample_count": len(samples),
            "input_hashes_present": all(_is_sha256(sample.get("pl_input_sha256")) for sample in samples),
            "cpu_per_layer_integer_tensor_goldens": "MISSING",
            "bytewise_full_network_run_for_109_samples": "NOT_RUN",
            "generated_by_t22": False,
            "g4_blocker": True,
            "reason": "fixed_test_samples.json binds input hashes and ground truth only; it contains no CPU per-layer tensor golden payload/path. D2 limited summaries are not per-layer goldens.",
        },
        "validation": {
            "source_binding_count": len(source_bindings),
            "source_bindings_sha256_matched": True,
            "manifest_layer_row_count": len(contract_rows),
            "operator_counts": op_counts,
            "yolo_alias_count": len(EXPECTED_HEAD_ALIASES),
            "owned_feature_tensor_bytes_per_sample": samples_per_sample_bytes,
            "raw_unique_feature_tensor_bytes_for_109_samples": samples_per_sample_bytes * len(samples),
            "manifest_sha256": source_sha[MANIFEST_PATH],
            "fixed_samples_sha256": source_sha[FIXED_SAMPLES_PATH],
            "g0_spec_sha256": source_sha[G0_SPEC_PATH],
            "t16_proof_sha256": source_sha[T16_PROOF_PATH],
            "checks": [
                "all pinned G0/model/sample/RTL/pilot/evidence source hashes match",
                "manifest schema/model/address/protocol bindings match frozen G0",
                "38 rows ordered by layer_index with cfg_section=index+1",
                "all tensor refs resolve to network_input or an earlier non-YOLO producer",
                "all NCHW INT8 byte lengths and half-open address ranges match",
                "all owned feature ranges are disjoint; only the two G0 YOLO aliases overlap",
                "all convolution cfg/GF8/bias/T16 proof references resolve layer-by-layer",
                "T16 candidate parameter hashes are recorded without treating them as materialized M/Q tables",
                "G0 global timeout/final result event/error priority and abort semantics are captured",
                "109 fixed input samples are bound and CPU per-layer golden readiness remains MISSING",
            ],
            "rtl_simulation": "NOT_RUN; contract-only task",
            "synthesis_and_resources": "NOT_RUN; contract-only task",
            "board_test": "NOT_APPLICABLE; no hardware operation authorized",
            "g4": "NOT_MET",
            "g5": "NOT_MET",
        },
    }


def build_contract(repo_root: Path) -> dict[str, Any]:
    """读取精确冻结来源，验证后派生 contract。"""
    source_bindings = collect_source_bindings(repo_root)
    manifest = _read_json(repo_root.joinpath(*MANIFEST_PATH.split("/")))
    fixed_samples = _read_json(repo_root.joinpath(*FIXED_SAMPLES_PATH.split("/")))
    t16_proof = _read_json(repo_root.joinpath(*T16_PROOF_PATH.split("/")))
    return derive_contract(manifest, fixed_samples, t16_proof, source_bindings)


def write_contract(repo_root: Path, output_path: Path) -> dict[str, Any]:
    """只写调用者明确指定的一个 JSON 文件，不自动创建目录。"""
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    output_path = output_path.resolve()
    if not output_path.parent.is_dir():
        raise ContractError(f"输出父目录不存在: {output_path.parent}")
    contract = build_contract(repo_root)
    encoded = json.dumps(contract, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    output_path.write_text(encoded, encoding="utf-8", newline="\n")
    return contract


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="从冻结 tiny416 manifest 构建 S2A-T22 内部 dispatch contract")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True, help="唯一允许写入的 contract JSON 路径")
    args = parser.parse_args(argv)
    try:
        contract = write_contract(args.repo_root.resolve(), args.output)
    except (ContractError, OSError) as exc:
        print(f"S2A-T22 contract error: {exc}", file=sys.stderr)
        return 2
    print(
        "S2A-T22 contract validated: "
        f"layers={contract['network_dispatch']['layer_count']} "
        f"ops={contract['network_dispatch']['operator_counts']} "
        f"owned_bytes={contract['network_dispatch']['owned_feature_tensor_bytes_per_sample']} "
        f"goldens={contract['golden_readiness']['cpu_per_layer_integer_tensor_goldens']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
