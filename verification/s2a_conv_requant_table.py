"""S2A-T23：复用冻结 T16 证明内核，导出全部卷积通道的数学 M/Q 表。"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import struct
import subprocess
import sys
from pathlib import Path
from typing import Any


G0_SPEC_PATH = "docs/obsidian-project/04-提交材料/阶段验收/S2A-T01_模型交付规格与G0接口冻结.md"
MANIFEST_PATH = "report/evidence/S2A-T01/tiny416_model_manifest.json"
T16_SCRIPT_PATH = "verification/s2a_conv_requant_proof.py"
T16_PROOF_PATH = "report/evidence/S2A-T16/conv_requant_proof.json"
T22_CONTRACT_PATH = "report/evidence/S2A-T22/network_dispatch_contract_validation.json"
T23_EXPORTER_PATH = "verification/s2a_conv_requant_table.py"
T23_TEST_PATH = "verification/test_s2a_conv_requant_table.py"

PINNED_SOURCE_SHA256 = {
    G0_SPEC_PATH: "7c2c8684ce0b6377f5742964464b914a23410bd3f6e4f198075e6c97b371f230",
    MANIFEST_PATH: "9dd2477bc6f12b556ded8bed71e5acd9efb22f6e314564973a3bbbda8279453a",
    T16_SCRIPT_PATH: "3bfb6d711160c21ae38147a181a042dcc5fee872d0688ae688f31e5909ebe8c9",
    T16_PROOF_PATH: "edd2e766278849136c806b755b275c6ad089964ff784ebe687032733f2ccbb24",
    T22_CONTRACT_PATH: "611d47cc85bd254474c5412fcab2f8acce3a263138787588f2a6445eac61d9a8",
}


class RequantTableError(ValueError):
    """冻结来源、覆盖范围或 M/Q 数学证明不匹配。"""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RequantTableError(message)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RequantTableError(f"无法按 UTF-8 JSON 读取 {path.name}: {exc}") from exc


def _safe_repo_file(root: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    _require(not candidate.is_absolute(), f"source path 必须是仓库相对路径: {relative_path}")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise RequantTableError(f"source path 越出仓库根目录: {relative_path}") from exc
    _require(resolved.is_file(), f"source file 不存在: {relative_path}")
    return resolved


def _verify_pinned_file(root: Path, relative_path: str, expected_sha256: str) -> dict[str, str]:
    path = _safe_repo_file(root, relative_path)
    actual = _sha256_file(path)
    _require(actual == expected_sha256, f"source hash mismatch: {relative_path}: {actual} != {expected_sha256}")
    return {"path": relative_path, "sha256": actual}


def _git_head(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RequantTableError(f"无法读取 Git HEAD: {exc}") from exc


def _load_frozen_t16_module(root: Path):
    """只在 T16 文件哈希通过后执行其冻结算法模块。"""
    relative_path = T16_SCRIPT_PATH
    path = _safe_repo_file(root, relative_path)
    actual = _sha256_file(path)
    expected = PINNED_SOURCE_SHA256[relative_path]
    _require(actual == expected, f"T16 算法源 hash mismatch: {actual} != {expected}")
    root_text = str(root.resolve())
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    module_name = "verification._s2a_conv_requant_proof_t23_frozen"
    spec = importlib.util.spec_from_file_location(module_name, path)
    _require(spec is not None and spec.loader is not None, "无法加载冻结 T16 算法模块")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _repo_path_for_binding(root: Path, manifest_path: str, proof_path: str, role: str) -> tuple[str, Path]:
    """交叉解析 manifest 与 T16 proof 中的相对路径，不输出绝对路径。"""
    manifest_file = Path(manifest_path)
    proof_file = Path(proof_path)
    _require(not manifest_file.is_absolute() and not proof_file.is_absolute(), f"{role} source path 不是相对路径")
    manifest_resolved = _safe_repo_file(root, manifest_path)
    proof_resolved = _safe_repo_file(root, proof_path)
    _require(manifest_resolved == proof_resolved, f"{role} manifest/proof 指向不同文件")
    return proof_path, proof_resolved


def _verify_bound_d2_sources(root: Path, manifest: dict[str, Any], proof: dict[str, Any]) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    bindings = (
        ("d2_int8_forward_reference", "d2_int8_forward_reference"),
        ("d2_numeric_reference", "d2_numeric_reference"),
    )
    for manifest_key, proof_key in bindings:
        manifest_record = manifest.get("bindings", {}).get(manifest_key, {})
        proof_record = proof.get("binding", {}).get(proof_key, {})
        declared_hash = str(manifest_record.get("sha256", "")).lower()
        proof_hash = str(proof_record.get("sha256", "")).lower()
        _require(declared_hash and declared_hash == proof_hash, f"{manifest_key} manifest/proof hash 不一致")
        relative_path, path = _repo_path_for_binding(
            root,
            str(manifest_record.get("path", "")),
            str(proof_record.get("path", "")),
            manifest_key,
        )
        actual_hash = _sha256_file(path)
        _require(actual_hash == declared_hash, f"{manifest_key} 文件哈希不匹配: {actual_hash} != {declared_hash}")
        sources.append({"role": manifest_key, "path": relative_path, "sha256": actual_hash})
    return sources


def _proof_layer_map(proof: dict[str, Any]) -> dict[int, dict[str, Any]]:
    coverage = proof.get("coverage", {})
    proof_layers = proof.get("layers")
    _require(proof.get("schema") == "GestureForge-S2A-T16-requant-proof-v1", "T16 proof schema 不匹配")
    _require(proof.get("status") == "EXACT_FIXED_POINT_FOUND", "T16 proof status 不是完整精确证明")
    _require(proof.get("failures") == [], "T16 proof failures 不为空")
    _require(coverage.get("complete_tiny416_convolution_model") is True, "T16 proof 未声明完整 tiny416 coverage")
    _require(coverage.get("convolution_layers_audited") == 21, "T16 proof convolution layer coverage 不是 21")
    _require(coverage.get("output_channels_audited") == 3164, "T16 proof output channel coverage 不是 3164")
    _require(coverage.get("output_channels_with_exact_candidate") == 3164, "T16 proof exact channel 数不是 3164")
    _require(coverage.get("failures") == 0, "T16 proof failure count 非零")
    _require(isinstance(proof_layers, list) and len(proof_layers) == 21, "T16 proof layer table 缺层")
    result: dict[int, dict[str, Any]] = {}
    for item in proof_layers:
        _require(isinstance(item, dict), "T16 proof layer 不是 object")
        layer_index = item.get("layer_index")
        _require(isinstance(layer_index, int) and layer_index not in result, "T16 proof layer_index 缺失或重复")
        result[layer_index] = item
    return result


def _verify_context_bindings(root: Path) -> dict[str, Any]:
    _require(root.is_dir(), f"仓库根目录不存在: {root}")
    head = _git_head(root)
    _require(head == "40f992237c36e7dc30bd8063e236502563c41052", f"Git HEAD 与 T23 基线不一致: {head}")
    pinned_records = [
        _verify_pinned_file(root, relative, digest)
        for relative, digest in PINNED_SOURCE_SHA256.items()
    ]
    manifest = _read_json(_safe_repo_file(root, MANIFEST_PATH))
    proof = _read_json(_safe_repo_file(root, T16_PROOF_PATH))
    contract = _read_json(_safe_repo_file(root, T22_CONTRACT_PATH))
    _require(manifest.get("schema_version") == "gestureforge_s2a_model_manifest_v1", "tiny416 manifest schema 不匹配")
    _require(manifest.get("status") == "G0_FROZEN" and manifest.get("model", {}).get("model_id") == "tiny416", "manifest 不是冻结 tiny416")
    _require(manifest.get("bindings", {}).get("generator", {}).get("sha256") == "4831fff0e8ebb189ac9767ae423ad8d5268fc5bee5e333cc2a132112ccfdaab8", "manifest generator hash 不匹配 T22 来源 pin")
    for name in ("cfg", "darknet_weights", "gf8_package"):
        binding = manifest.get("bindings", {}).get(name, {})
        _require(len(str(binding.get("sha256", ""))) == 64, f"manifest {name} 哈希缺失")
    d2_records = _verify_bound_d2_sources(root, manifest, proof)
    proof_binding = proof.get("binding", {})
    _require(proof_binding.get("audit_script", {}).get("path") == T16_SCRIPT_PATH, "T16 proof audit_script path 不匹配")
    _require(proof_binding.get("audit_script", {}).get("sha256") == PINNED_SOURCE_SHA256[T16_SCRIPT_PATH], "T16 proof audit_script hash 不匹配")
    _require(proof_binding.get("manifest", {}).get("path") == MANIFEST_PATH, "T16 proof manifest path 不匹配")
    _require(proof_binding.get("manifest", {}).get("sha256") == PINNED_SOURCE_SHA256[MANIFEST_PATH], "T16 proof manifest hash 不匹配")

    _require(contract.get("schema_version") == "gestureforge_s2a_network_dispatch_contract_v1", "T22 contract schema 不匹配")
    _require(contract.get("task_id") == "S2A-T22" and contract.get("artifact_status") == "CONTRACT_VALIDATED", "T22 contract 未通过")
    network = contract.get("network_dispatch", {})
    _require(network.get("layer_count") == 38 and len(network.get("layers", [])) == 38, "T22 contract 层数不完整")
    _require(network.get("operator_counts") == {"convolutional": 21, "maxpool": 3, "route": 11, "upsample": 1, "yolo": 2}, "T22 contract operator counts 不匹配")
    _require(contract.get("golden_readiness", {}).get("cpu_per_layer_integer_tensor_goldens") == "MISSING", "T22 contract golden readiness 状态改变")
    t22_source_map = {item.get("path"): item.get("sha256") for item in contract.get("source_bindings", []) if isinstance(item, dict)}
    for relative, digest in PINNED_SOURCE_SHA256.items():
        if relative == T22_CONTRACT_PATH:
            continue
        _require(t22_source_map.get(relative) == digest, f"T22 contract 未绑定冻结来源: {relative}")
    t22_conv_rows = {
        row.get("layer_index"): row
        for row in network["layers"]
        if isinstance(row, dict) and row.get("op") == "convolutional"
    }
    proof_layers = _proof_layer_map(proof)
    _require(set(t22_conv_rows) == set(proof_layers), "T22 conv rows 与 T16 proof 层集合不同")
    for index, proof_row in proof_layers.items():
        _require(t22_conv_rows[index].get("cfg_section") == proof_row.get("cfg_section"), f"layer {index}: T22 cfg section 不匹配")
        requant_source = t22_conv_rows[index].get("operator_parameters", {}).get("parameters", {}).get("t16_requantization_source", {})
        _require(requant_source.get("proof_sha256") == PINNED_SOURCE_SHA256[T16_PROOF_PATH], f"layer {index}: T22 未绑定 T16 proof")
        _require(requant_source.get("candidate_parameter_sha256") == proof_row.get("candidate_parameter_sha256"), f"layer {index}: T22/T16 candidate digest 不一致")

    # PINNED_SOURCE_SHA256 已含 T22 contract；不要重复追加同一绑定。
    source_records = pinned_records + d2_records
    return {
        "root": root.resolve(),
        "head": head,
        "manifest": manifest,
        "proof": proof,
        "t22_contract": contract,
        "proof_layers": proof_layers,
        "t22_conv_rows": t22_conv_rows,
        "source_bindings": source_records,
        "dynamic_source_bindings": {
            item["role"]: {"path": item["path"], "sha256": item["sha256"]}
            for item in d2_records
        },
    }


def validate_source_records(
    records: list[dict[str, str]],
    dynamic_source_bindings: dict[str, dict[str, str]] | None = None,
) -> None:
    """对 JSON 来源清单做 fail-closed 校验，供 exporter 和 mutation tests 共用。"""
    expected = dict(PINNED_SOURCE_SHA256)
    roles = {record.get("role"): record for record in records}
    for relative, digest in expected.items():
        matches = [item for item in records if item.get("path") == relative]
        _require(len(matches) == 1, f"source binding missing/duplicate: {relative}")
        _require(matches[0].get("sha256") == digest, f"source binding hash changed: {relative}")
    for record in records:
        _require(len(str(record.get("sha256", ""))) == 64, "source binding SHA-256 格式无效")
        _require(not Path(str(record.get("path", ""))).is_absolute(), "source binding 不得写绝对路径")
    d2_roles = {"d2_int8_forward_reference", "d2_numeric_reference"}
    _require(d2_roles.issubset(roles), "D2 source bindings 缺项")
    _require(
        all(roles[role].get("sha256") == roles[role].get("sha256", "").lower() for role in d2_roles),
        "D2 source binding digest 不是小写 SHA-256",
    )
    if dynamic_source_bindings is not None:
        for role, expected in dynamic_source_bindings.items():
            matches = [item for item in records if item.get("role") == role]
            _require(len(matches) == 1, f"dynamic source binding missing/duplicate: {role}")
            _require(matches[0].get("path") == expected.get("path"), f"dynamic source path changed: {role}")
            _require(matches[0].get("sha256") == expected.get("sha256"), f"dynamic source hash changed: {role}")


def _threshold_digest_from_t16(thresholds, low_endpoint, high_endpoint) -> str:
    """按 T16 固定的字节顺序生成 target threshold summary digest。"""
    digest = hashlib.sha256()
    for channel in range(int(thresholds.shape[0])):
        digest.update(struct.pack("<I", channel))
        digest.update(struct.pack("<ii", int(low_endpoint[channel]), int(high_endpoint[channel])))
        digest.update(thresholds[channel].astype("<i8").tobytes())
    return digest.hexdigest()


def _materialize_layer(context: dict[str, Any], layer: dict[str, Any], t16: Any) -> dict[str, Any]:
    """用 T16 冻结核心计算一个卷积层的 D2 转移点和通道候选参数。"""
    import numpy as np

    index = int(layer["layer_index"])
    proof_row = context["proof_layers"].get(index)
    _require(proof_row is not None, f"T16 proof 缺少 convolution layer {index}")
    _require(layer.get("cfg_section") == proof_row.get("cfg_section"), f"layer {index}: cfg section mismatch")
    activation = str(layer.get("activation"))
    _require(activation in ("linear", "leaky"), f"layer {index}: activation 不支持")
    _require(proof_row.get("activation") == activation, f"layer {index}: T16 activation mismatch")
    input_scale = float(layer["input_scale"])
    output_scale = float(layer["output_scale"])
    weight_scales = np.asarray(layer["weight_scale_per_output_channel"], dtype=np.float64)
    _require(weight_scales.size == int(layer["output_shape_nchw"][1]), f"layer {index}: weight scale channel count mismatch")
    _require(weight_scales.size == proof_row.get("output_channels_audited"), f"layer {index}: T16 output channel coverage mismatch")
    _require(math.isfinite(input_scale) and input_scale > 0.0, f"layer {index}: input_scale invalid")
    _require(math.isfinite(output_scale) and output_scale > 0.0, f"layer {index}: output_scale invalid")
    _require(bool(np.all(np.isfinite(weight_scales))) and bool(np.all(weight_scales > 0.0)), f"layer {index}: weight scale invalid")
    real_scales = np.float64(input_scale) * weight_scales
    maximum_scaled = float(np.max(real_scales)) * (1 << 31) / output_scale
    _require(math.isfinite(maximum_scaled) and maximum_scaled < float((1 << 63) - 1024), f"layer {index}: D2 scale 超出 T16 int64 安全范围")

    thresholds, low_endpoint, high_endpoint = t16._d2_thresholds(real_scales, output_scale, activation)
    _require(thresholds.shape == (weight_scales.size, 254), f"layer {index}: D2 threshold coverage 不是每通道 254 项")
    _require(low_endpoint.shape == (weight_scales.size,) and high_endpoint.shape == (weight_scales.size,), f"layer {index}: D2 endpoint coverage 不符")
    channels: list[dict[str, Any]] = []
    candidate_rows: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
    for channel in range(int(weight_scales.size)):
        target_row = [int(value) for value in thresholds[channel].tolist()]
        positive_targets, negative_targets = t16._branch_magnitude_thresholds(thresholds[channel])
        ideal_positive = float(real_scales[channel]) / output_scale
        ideal_negative = ideal_positive if activation == "linear" else ideal_positive * 0.1
        if activation == "linear":
            positive, negative = t16._find_linear_joint_candidate(
                positive_targets, negative_targets, ideal_positive
            )
        else:
            positive = t16._find_candidate(positive_targets, t16.INT32_MAX, ideal_positive)
            negative = t16._find_candidate(negative_targets, 1 << 31, ideal_negative)
        _require(positive.get("status") == "exact" and negative.get("status") == "exact", f"layer {index} channel {channel}: T16 未找到 exact M/Q")
        candidate_thresholds = t16._candidate_signed_thresholds(positive, negative)
        mismatch = t16._first_threshold_mismatch(target_row, candidate_thresholds)
        _require(mismatch is None, f"layer {index} channel {channel}: 254 个 signed threshold 不匹配: {mismatch}")
        candidate_low = t16._candidate_endpoint_output(negative, 1 << 31, True)
        candidate_high = t16._candidate_endpoint_output(positive, t16.INT32_MAX, False)
        _require(candidate_low == int(low_endpoint[channel]), f"layer {index} channel {channel}: INT32_MIN output mismatch")
        _require(candidate_high == int(high_endpoint[channel]), f"layer {index} channel {channel}: INT32_MAX output mismatch")
        _require(positive["q_shift"] + 1 == positive["q_shifts_examined"], f"layer {index} channel {channel}: positive Q 不是首个可行值")
        _require(negative["q_shift"] + 1 == negative["q_shifts_examined"], f"layer {index} channel {channel}: negative Q 不是首个可行值")
        candidate_rows.append((channel, positive, negative))
        channels.append(
            {
                "channel": channel,
                "parameter_source": {
                    "manifest_layer": f"{MANIFEST_PATH}#/layers/{index}",
                    "input_scale": input_scale,
                    "weight_scale": float(weight_scales[channel]),
                    "real_scale_float64": float(real_scales[channel]),
                    "output_scale": output_scale,
                    "activation": activation,
                    "ideal_positive_slope_float64": ideal_positive,
                    "ideal_negative_slope_float64": ideal_negative,
                },
                "positive_M": int(positive["multiplier"]),
                "positive_Q": int(positive["q_shift"]),
                "negative_M": int(negative["multiplier"]),
                "negative_Q": int(negative["q_shift"]),
                "linear_shared_parameter": activation == "linear",
                "positive_M_bit_length": int(positive["multiplier_bits"]),
                "negative_M_bit_length": int(negative["multiplier_bits"]),
                "positive_first_feasible_q_checks": int(positive["q_shifts_examined"]),
                "negative_first_feasible_q_checks": int(negative["q_shifts_examined"]),
            }
        )

    candidate_digest = t16._candidate_digest(candidate_rows)
    d2_layer_digest = t16._layer_digest(thresholds, low_endpoint, high_endpoint)
    target_digest = _threshold_digest_from_t16(thresholds, low_endpoint, high_endpoint)
    _require(candidate_digest == proof_row.get("candidate_parameter_sha256"), f"layer {index}: candidate_parameter_sha256 与 T16 不符")
    _require(d2_layer_digest == proof_row.get("d2_threshold_and_endpoint_sha256"), f"layer {index}: D2 threshold/endpoint digest 与 T16 不符")
    _require(target_digest == proof_row.get("target_threshold_sha256"), f"layer {index}: target threshold digest 与 T16 不符")
    max_q = max(max(item["positive_Q"], item["negative_Q"]) for item in channels)
    max_bits = max(max(item["positive_M_bit_length"], item["negative_M_bit_length"]) for item in channels)
    _require(max_q == proof_row.get("maximum_q_shift"), f"layer {index}: maximum Q 与 T16 summary 不符")
    _require(max_bits == proof_row.get("maximum_multiplier_bits"), f"layer {index}: maximum M bit length 与 T16 summary 不符")
    return {
        "layer_index": index,
        "cfg_section": int(layer["cfg_section"]),
        "activation": activation,
        "input_scale": input_scale,
        "output_scale": output_scale,
        "channel_count": len(channels),
        "channels": channels,
        "verified_signed_transition_values_per_channel": 254,
        "verified_int32_endpoint_outputs_per_channel": 2,
        "target_threshold_sha256": target_digest,
        "d2_threshold_and_endpoint_sha256": d2_layer_digest,
        "candidate_parameter_sha256": candidate_digest,
        "maximum_q_shift": max_q,
        "maximum_m_multiplier_bit_length": max_bits,
    }


def _table_candidate_digest(layer: dict[str, Any], t16: Any) -> str:
    rows = []
    for item in layer.get("channels", []):
        rows.append(
            (
                item["channel"],
                {"q_shift": item["positive_Q"], "multiplier": item["positive_M"]},
                {"q_shift": item["negative_Q"], "multiplier": item["negative_M"]},
            )
        )
    return t16._candidate_digest(rows)


def validate_parameter_table(table: dict[str, Any], context: dict[str, Any], t16: Any) -> None:
    """校验序列化表完整覆盖 manifest/T16，且通道表重算摘要一致。"""
    _require(table.get("schema_version") == "gestureforge_s2a_conv_requant_parameter_table_v1", "参数表 schema 不匹配")
    _require(table.get("status") == "ALL_CHANNELS_EXACT_AND_T16_DIGEST_MATCH", "参数表状态未通过")
    validate_source_records(table.get("source_bindings", []), context.get("dynamic_source_bindings"))
    _require(table.get("source_bindings") == context["source_bindings"], "参数表 source bindings 被改写")
    conv_layers = [layer for layer in context["manifest"]["layers"] if layer.get("op") == "convolutional"]
    proof_layers = context["proof_layers"]
    table_layers = table.get("layers")
    _require(isinstance(table_layers, list) and len(table_layers) == len(conv_layers) == 21, "参数表层缺失或多余")
    _require([row.get("layer_index") for row in table_layers] == [row["layer_index"] for row in conv_layers], "参数表 layer 顺序不匹配")
    total_channels = 0
    max_q = 0
    max_m_bits = 0
    for table_layer, source_layer in zip(table_layers, conv_layers):
        index = int(source_layer["layer_index"])
        proof_row = proof_layers[index]
        _require(table_layer.get("cfg_section") == source_layer.get("cfg_section") == proof_row.get("cfg_section"), f"layer {index}: cfg section mismatch")
        _require(table_layer.get("activation") == source_layer.get("activation") == proof_row.get("activation"), f"layer {index}: activation mismatch")
        expected_count = len(source_layer["weight_scale_per_output_channel"])
        channels = table_layer.get("channels")
        _require(isinstance(channels, list) and len(channels) == expected_count, f"layer {index}: 通道遗漏或多余")
        _require([item.get("channel") for item in channels] == list(range(expected_count)), f"layer {index}: channel 顺序/索引不匹配")
        for channel_item in channels:
            for field in ("positive_M", "negative_M"):
                _require(isinstance(channel_item.get(field), int) and not isinstance(channel_item.get(field), bool) and channel_item[field] > 0, f"layer {index} channel {channel_item.get('channel')}: {field} 无效")
            for field in ("positive_Q", "negative_Q"):
                _require(isinstance(channel_item.get(field), int) and not isinstance(channel_item.get(field), bool) and 0 <= channel_item[field] <= 65, f"layer {index} channel {channel_item.get('channel')}: {field} 越界")
            _require(channel_item.get("parameter_source", {}).get("activation") == table_layer["activation"], f"layer {index}: channel parameter source activation 不匹配")
            _require(channel_item.get("parameter_source", {}).get("manifest_layer") == f"{MANIFEST_PATH}#/layers/{index}", f"layer {index}: channel manifest source 不匹配")
            _require(channel_item.get("linear_shared_parameter") is (table_layer["activation"] == "linear"), f"layer {index}: linear/leaky branch 标识不匹配")
            if table_layer["activation"] == "linear":
                _require((channel_item["positive_M"], channel_item["positive_Q"]) == (channel_item["negative_M"], channel_item["negative_Q"]), f"layer {index} channel {channel_item['channel']}: linear M/Q 未共享")
            total_channels += 1
            max_q = max(max_q, channel_item["positive_Q"], channel_item["negative_Q"])
            max_m_bits = max(max_m_bits, channel_item["positive_M"].bit_length(), channel_item["negative_M"].bit_length())
        candidate_digest = _table_candidate_digest(table_layer, t16)
        _require(candidate_digest == table_layer.get("candidate_parameter_sha256"), f"layer {index}: table candidate digest 不匹配")
        _require(candidate_digest == proof_row.get("candidate_parameter_sha256"), f"layer {index}: table candidate digest 与 T16 不匹配")
        _require(table_layer.get("d2_threshold_and_endpoint_sha256") == proof_row.get("d2_threshold_and_endpoint_sha256"), f"layer {index}: D2 digest 与 T16 不匹配")
        _require(table_layer.get("target_threshold_sha256") == proof_row.get("target_threshold_sha256"), f"layer {index}: target threshold digest 与 T16 不匹配")
        _require(table_layer.get("channel_count") == expected_count, f"layer {index}: channel count field 不匹配")
        _require(table_layer.get("maximum_q_shift") == proof_row.get("maximum_q_shift"), f"layer {index}: maximum Q 不匹配")
        _require(table_layer.get("maximum_m_multiplier_bit_length") == proof_row.get("maximum_multiplier_bits"), f"layer {index}: maximum M bit length 不匹配")
    _require(total_channels == 3164, f"参数表总通道数不是 3164: {total_channels}")
    coverage = table.get("coverage", {})
    _require(coverage.get("convolution_layers") == 21 and coverage.get("output_channels") == total_channels, "参数表 coverage counters 不匹配")
    _require(coverage.get("candidate_digest_layers_match") == 21, "候选摘要未逐层全部匹配")
    _require(coverage.get("d2_digest_layers_match") == 21, "D2 摘要未逐层全部匹配")
    _require(coverage.get("signed_transition_comparisons") == total_channels * 254, "signed transition comparison count 不匹配")
    _require(coverage.get("int32_endpoint_comparisons") == total_channels * 2, "INT32 endpoint comparison count 不匹配")
    stats = table.get("statistics", {})
    _require(stats.get("maximum_q_shift_observed") == max_q, "全模型 maximum Q 统计不匹配")
    _require(stats.get("maximum_m_multiplier_bit_length_observed") == max_m_bits, "全模型 maximum M bit length 统计不匹配")


def materialize_table(context: dict[str, Any], t16: Any) -> dict[str, Any]:
    manifest = context["manifest"]
    conv_layers = [layer for layer in manifest["layers"] if layer.get("op") == "convolutional"]
    _require(len(conv_layers) == 21, "manifest 中 convolution layer 数量不是 21")
    layers = [_materialize_layer(context, layer, t16) for layer in conv_layers]
    total_channels = sum(layer["channel_count"] for layer in layers)
    _require(total_channels == 3164, f"manifest 派生 channel 数不是 3164: {total_channels}")
    max_q = max(layer["maximum_q_shift"] for layer in layers)
    max_m_bits = max(layer["maximum_m_multiplier_bit_length"] for layer in layers)
    table = {
        "schema_version": "gestureforge_s2a_conv_requant_parameter_table_v1",
        "task_id": "S2A-T23",
        "status": "ALL_CHANNELS_EXACT_AND_T16_DIGEST_MATCH",
        "model_id": "tiny416",
        "source_bindings": context["source_bindings"],
        "proof_semantics": {
            "d2_order": context["proof"]["semantics"]["d2_order"],
            "candidate_rule": context["proof"]["semantics"]["candidate"],
            "q_search_bound_inclusive": 65,
            "q_choice": "first feasible Q in ascending order 0..65; M is nearest ideal scale rounded half away and clamped into the exact integer feasible interval",
            "linear": "positive and negative domains share the same M/Q",
            "leaky": "positive and negative domains may use different M/Q; negative ideal slope uses binary64 0.1 per frozen T16",
            "proof_domain": "all 254 signed output transition values plus INT32_MIN and INT32_MAX endpoint outputs per channel",
            "bias": context["proof"]["semantics"]["bias"],
        },
        "model_parameter_binding": {
            "manifest_path": MANIFEST_PATH,
            "manifest_sha256": PINNED_SOURCE_SHA256[MANIFEST_PATH],
            "cfg_sha256": manifest["bindings"]["cfg"]["sha256"],
            "darknet_weights_sha256": manifest["bindings"]["darknet_weights"]["sha256"],
            "gf8_package_sha256": manifest["bindings"]["gf8_package"]["sha256"],
            "raw_weight_or_model_data_included": False,
        },
        "layers": layers,
        "coverage": {
            "convolution_layers": len(layers),
            "output_channels": total_channels,
            "candidate_digest_layers_match": len(layers),
            "d2_digest_layers_match": len(layers),
            "signed_transition_comparisons": total_channels * 254,
            "int32_endpoint_comparisons": total_channels * 2,
        },
        "statistics": {
            "maximum_q_shift_observed": max_q,
            "maximum_m_multiplier_bit_length_observed": max_m_bits,
            "hardware_multiplier_width": "NOT_FROZEN; mathematical M bit length is reported separately",
            "q_register_width": "NOT_FROZEN",
        },
        "limitations": {
            "parameter_kind": "exact mathematical integer M/Q only; no RTL width, signed packing, bus encoding, or coefficient-memory layout is specified",
            "rtl_integration": "NOT_PERFORMED",
            "resource_estimation": "NOT_PERFORMED",
            "timing_analysis": "NOT_PERFORMED",
            "synthesis": "NOT_PERFORMED",
            "stage_g4_g5": "NOT_CLAIMED",
        },
    }
    validate_parameter_table(table, context, t16)
    return table


def build_context(repo_root: Path) -> tuple[dict[str, Any], Any]:
    context = _verify_context_bindings(repo_root.resolve())
    t16 = _load_frozen_t16_module(repo_root)
    _require(int(t16.MAX_Q_SHIFT) == 65, "加载的 T16 Q 搜索上界不匹配")
    return context, t16


def write_table(repo_root: Path, output_path: Path) -> dict[str, Any]:
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    output_path = output_path.resolve()
    _require(output_path.parent.is_dir(), f"输出父目录不存在: {output_path.parent}")
    context, t16 = build_context(repo_root)
    table = materialize_table(context, t16)
    table["tooling_bindings"] = [
        {"path": T23_EXPORTER_PATH, "sha256": _sha256_file(_safe_repo_file(repo_root, T23_EXPORTER_PATH))},
        {"path": T23_TEST_PATH, "sha256": _sha256_file(_safe_repo_file(repo_root, T23_TEST_PATH))},
    ]
    encoded = json.dumps(table, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    output_path.write_text(encoded, encoding="utf-8", newline="\n")
    return table


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="导出经 T16 数学证明验证的 tiny416 逐通道 M/Q 表")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True, help="唯一输出文件路径；不覆盖其他证据")
    args = parser.parse_args(argv)
    try:
        table = write_table(args.repo_root.resolve(), args.output)
    except (RequantTableError, OSError, ValueError, AssertionError) as exc:
        print(f"S2A-T23 exporter error: {exc}", file=sys.stderr)
        return 2
    print(
        "S2A-T23 parameter table verified: "
        f"layers={table['coverage']['convolution_layers']} "
        f"channels={table['coverage']['output_channels']} "
        f"transition_checks={table['coverage']['signed_transition_comparisons']} "
        f"endpoint_checks={table['coverage']['int32_endpoint_comparisons']} "
        f"max_Q={table['statistics']['maximum_q_shift_observed']} "
        f"max_M_bits={table['statistics']['maximum_m_multiplier_bit_length_observed']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
