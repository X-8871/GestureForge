"""核对冻结的 sample0 来源并导出 T66 layer0 完整张量夹具。"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVIDENCE_DIR = ROOT / "report" / "evidence" / "S2A-T66" / "tile01"
FIXED_SAMPLES_PATH = ROOT / "report" / "evidence" / "S2A-T01" / "fixed_test_samples.json"
MODEL_MANIFEST_PATH = ROOT / "report" / "evidence" / "S2A-T01" / "tiny416_model_manifest.json"
T65_RUN02 = ROOT / "report" / "evidence" / "S2A-T65" / "run02"
T65_INPUT_PATH = T65_RUN02 / "fixture" / "sample0_input_chw_int8.bin"
T65_WEIGHT_PATH = T65_RUN02 / "fixture" / "sample0_layer0_gf8_weights.bin"
T65_FIXTURE_MANIFEST = T65_RUN02 / "fixture_manifest.json"
T25_INDEX_PATH = ROOT / "report" / "evidence" / "S2A-T25" / "cpu_layer_golden_index.json"
DESCRIPTOR_PATH = ROOT / "src" / "s2a_network_descriptor_pkg.sv"
ENGINE_PATH = ROOT / "src" / "s2a_conv_tile_engine.sv"
BENCH_PATH = ROOT / "sim" / "tb_s2a_t66_layer0_tile.sv"
RUNNER_PATH = ROOT / "verification" / "run_s2a_t66_layer0_tile.ps1"
VERIFIER_PATH = ROOT / "verification" / "test_s2a_t66_layer0_tile.py"
EXPECTED_INPUT_SHA256 = "da26d3850d23d6f8cb466416799358e77fbeceaa8ee27696ebf7ab365248ab9e"
EXPECTED_WEIGHT_SHA256 = "df49b5d3aeaebd6b4107b99d83ffa791d7a7e24bd7b26df0815c246e5717e633"
EXPECTED_T25_SHARD_SHA256 = "49488538ced503bad996e284a3593d4fc7a1cf3b605d90221b3ca09875c4966e"
EXPECTED_T25_LAYER0_SHA256 = "220499b6b8122c3264bef4d581967d51eedccc9e28813df3e0ff8f8716bc2ed8"
EXPECTED_RAW_NETWORK_SHA256 = "090b1422f8e8d4d22124568af9778ba7bd5e7168407c0125e1e729d4a5a46f80"
EXPECTED_INPUT_BYTES = 519_168
EXPECTED_WEIGHT_BYTES = 864
EXPECTED_LAYER0_BYTES = 1_384_448
CACHE_POLICY = {
    "decision": "A",
    "tile_order": "spatial_tile_major",
    "feature_patch_capacity_bytes": 51_200,
    "feature_patch_loads_per_spatial_tile": 1,
    "feature_patch_reuse_scope": "all_output_channel_groups_in_current_tile",
    "weight_group_capacity_bytes": 36_864,
    "weight_group_output_channel_lanes": 8,
    "weight_group_reuse_scope": "all_spatial_points_in_current_tile",
    "weight_group_loads_per_tile_per_output_channel_group": 1,
    "weight_group_reloads_across_spatial_tiles": "accepted_by_decision_A",
    "output_block_capacity_bytes": 512,
}
LAYER0_TRANSFER_BUDGET = {
    "transaction_unit": "单次 transaction 为一条 32-bit 对齐 word 请求内 one-hot strobe 选中的 1 个字节；计数单位是 byte request",
    "tile_count": 676,
    "feature_patch_bytes_total": 586_092,
    "feature_in_bounds_byte_requests": 583_443,
    "feature_zero_padding_patch_bytes": 2_649,
    "weight_byte_requests": 584_064,
    "output_byte_requests": EXPECTED_LAYER0_BYTES,
    "all_single_byte_requests": 2_551_955,
    "request_latency_cycles": 7_655_865,
    "request_stall_cycles": 6_635_073,
    "response_stall_cycles": 6_635_073,
    "feature_request_stall_cycles": 1_516_947,
    "weight_request_stall_cycles": 1_518_566,
    "output_request_stall_cycles": 3_599_560,
    "feature_response_stall_cycles": 1_516_947,
    "weight_response_stall_cycles": 1_518_566,
    "output_response_stall_cycles": 3_599_560,
    "effective_mac_operations": 37_380_096,
    "parallel_mac_cycles": 4_672_512,
    "requant_cycles": 173_056,
    "point_bias_init_cycles": 170_352,
    "tile_group_control_cycles": 228_488,
    "boundary_padding_scan_cycles": 2_649,
    "estimated_total_cycles": 26_002_716,
    "watchdog_cycles": 75_000_000,
    "stall_pattern": [0, 1, 2, 7, 3],
}


class FixtureError(RuntimeError):
    """表示来源绑定、张量映射或夹具创建失败。"""


def require(condition: bool, message: str) -> None:
    """前置条件不成立时以可定位的信息终止。"""
    if not condition:
        raise FixtureError(message)


def sha256_bytes(payload: bytes) -> str:
    """计算字节流摘要。"""
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    """分块计算文件摘要。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path, label: str) -> dict[str, Any]:
    """读取 UTF-8 JSON 并校验顶层类型。"""
    require(path.is_file() and not path.is_symlink(), f"{label} 精确普通文件路径缺失：{path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FixtureError(f"无法读取 {label}：{path}: {exc}") from exc
    require(isinstance(value, dict), f"{label} 顶层 JSON 必须为对象：{path}")
    return value


def write_new_or_verify(path: Path, payload: bytes) -> None:
    """只创建新文件；已有文件只有逐字节相同才允许复用。"""
    if path.exists():
        require(path.is_file() and not path.is_symlink(), f"夹具目标不是普通文件：{path}")
        require(path.read_bytes() == payload, f"拒绝覆盖内容不同的既有文件：{path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def write_bound_manifest(path: Path, payload: bytes, record: dict[str, Any]) -> None:
    """仅在旧清单属于同一 T66 夹具且原始张量绑定不变时更新源码摘要。"""
    if path.exists():
        require(path.is_file() and not path.is_symlink(), f"清单目标不是普通文件：{path}")
        previous = read_json(path, "既有 T66 夹具清单")
        require(previous.get("task_id") == "S2A-T66-TILE01" and
                previous.get("schema_version") == "gestureforge_s2a_t66_layer0_golden_fixture_v1",
                f"拒绝替换不属于本任务的既有清单：{path}")
        for section, fields in {
            "sample": ("sample_index", "sample_id", "preprocessed_input_sha256", "input_fixture_sha256"),
            "weights": ("weight_layer_index", "quantized_weight_offset_bytes", "quantized_weight_bytes",
                        "source_slice_sha256", "fixture_sha256"),
            "golden": ("layer_index", "shape_nchw", "tensor_byte_offset", "tensor_byte_length",
                       "tensor_sha256", "compressed_shard_sha256", "decompressed_sha256", "fixture_sha256"),
        }.items():
            old_fields = previous.get(section, {})
            new_fields = record.get(section, {})
            require(all(old_fields.get(field) == new_fields.get(field) for field in fields),
                    f"拒绝改变既有 T66 {section} 原始夹具绑定：{path}")
        path.write_bytes(payload)
        return
    with path.open("xb") as stream:
        stream.write(payload)


def write_bound_cache_summary(path: Path, payload: bytes, record: dict[str, Any]) -> None:
    """只允许更新相同决策与 layer0 传输预算对应的缓存策略摘要。"""
    if path.exists():
        require(path.is_file() and not path.is_symlink(), f"缓存策略摘要不是普通文件：{path}")
        previous = read_json(path, "既有 T66 缓存策略摘要")
        require(previous.get("task_id") == record.get("task_id") and
                previous.get("schema_version") == record.get("schema_version") and
                previous.get("cache_policy") == record.get("cache_policy") and
                previous.get("layer0_transfer_budget") == record.get("layer0_transfer_budget"),
                f"拒绝改变既有 T66 缓存策略或预算：{path}")
        path.write_bytes(payload)
        return
    with path.open("xb") as stream:
        stream.write(payload)


def sha256_map(paths: dict[str, Path]) -> dict[str, str]:
    """记录参与本任务的源码和原始绑定摘要。"""
    result: dict[str, str] = {}
    for label, path in paths.items():
        require(path.is_file() and not path.is_symlink(), f"摘要输入精确普通文件缺失：{path}")
        result[label] = sha256_file(path)
    return result


def materialize(evidence_dir: Path) -> dict[str, Any]:
    """绑定 T01/T65/T25 来源并写入完整 layer0 输入、权重和黄金。"""
    evidence_dir = evidence_dir.resolve()
    evidence_root = (ROOT / "report" / "evidence" / "S2A-T66").resolve()
    require(evidence_dir != evidence_root and evidence_root in evidence_dir.parents,
            f"证据目录必须位于 T66 专属目录内：{evidence_dir}")
    require(evidence_dir.parent.is_dir(), f"证据目录父路径缺失：{evidence_dir.parent}")
    require(not evidence_dir.is_symlink(), f"证据目录不能是符号链接：{evidence_dir}")

    input_raw = T65_INPUT_PATH.read_bytes()
    weight_raw = T65_WEIGHT_PATH.read_bytes()
    input_sha = sha256_bytes(input_raw)
    weight_sha = sha256_bytes(weight_raw)
    require(len(input_raw) == EXPECTED_INPUT_BYTES and input_sha == EXPECTED_INPUT_SHA256,
            f"T65 sample0 输入夹具绑定错误：bytes={len(input_raw)} sha256={input_sha}")
    require(len(weight_raw) == EXPECTED_WEIGHT_BYTES and weight_sha == EXPECTED_WEIGHT_SHA256,
            f"T65 GF8 layer0 权重切片绑定错误：bytes={len(weight_raw)} sha256={weight_sha}")

    fixed = read_json(FIXED_SAMPLES_PATH, "T01 固定样本清单")
    manifest = read_json(MODEL_MANIFEST_PATH, "T01 tiny416 模型清单")
    t65 = read_json(T65_FIXTURE_MANIFEST, "T65 sample0 夹具清单")
    t25 = read_json(T25_INDEX_PATH, "T25 CPU 黄金索引")
    require(manifest.get("status") == "G0_FROZEN" and
            manifest.get("model", {}).get("model_id") == "tiny416",
            "T01 模型清单不是冻结 tiny416 基线")
    require(fixed.get("sample_count") == 109 and isinstance(fixed.get("samples"), list) and
            len(fixed["samples"]) == 109,
            "T01 固定样本清单不是 109 项")
    sample = fixed["samples"][0]
    require(sample.get("sample_id") == "test_fist_000" and sample.get("frame_id") == 0 and
            sample.get("pl_input_sha256") == EXPECTED_INPUT_SHA256,
            "T01 sample0 身份或预处理输入摘要与冻结值不符")
    require(t65.get("sample", {}).get("input_sha256") == EXPECTED_INPUT_SHA256 and
            t65.get("sample", {}).get("input_fixture_sha256") == EXPECTED_INPUT_SHA256 and
            t65.get("weights", {}).get("slice_sha256") == EXPECTED_WEIGHT_SHA256,
            "T65 现有夹具清单没有绑定到任务指定的输入/权重摘要")
    require(t25.get("schema_version") == "gestureforge_s2a_cpu_layer_golden_index_v2" and
            t25.get("status") == "COMPLETE",
            "T25 索引未提供 COMPLETE CPU 黄金")
    golden_sample = next((row for row in t25.get("samples", [])
                          if row.get("sample_id") == "test_fist_000"), None)
    require(golden_sample is not None and golden_sample.get("sample_index") == 0 and
            golden_sample.get("preprocessed_input", {}).get("sha256") == EXPECTED_INPUT_SHA256,
            "T25 sample0 身份或预处理输入摘要不匹配")

    layer = manifest.get("layers", [])[0]
    require(layer.get("layer_index") == 0 and layer.get("op") == "convolutional" and
            layer.get("input_shape_nchw") == [1, 3, 416, 416] and
            layer.get("output_shape_nchw") == [1, 32, 208, 208] and
            layer.get("kernel_hw") == [3, 3] and layer.get("stride_hw") == [2, 2] and
            layer.get("padding_lrtb") == [1, 1, 1, 1] and
            layer.get("tensor_address") == 0x01000000 and
            layer.get("tensor_length_bytes") == EXPECTED_LAYER0_BYTES,
            "T01 layer0 frozen descriptor 或 NCHW output 不匹配")

    package_ref = manifest.get("bindings", {}).get("gf8_package", {})
    package_path = Path(package_ref.get("path", ""))
    require(package_path.is_file() and not package_path.is_symlink(),
            f"T01 GF8 package 精确路径缺失：{package_path}")
    package_sha = sha256_file(package_path)
    require(package_sha == package_ref.get("sha256"), "T01 GF8 package 摘要与模型清单不一致")
    package = package_path.read_bytes()
    require(len(package) == package_ref.get("bytes") and package[:8] == b"GFINT8W1",
            "T01 GF8 package 长度或格式标识不匹配")
    version, layer_count, package_width, package_height, package_channels = struct.unpack_from("<IIIII", package, 8)
    require((version, layer_count, package_width, package_height, package_channels) == (1, 21, 416, 416, 3),
            "T01 GF8 package header 与冻结 tiny416 不匹配")
    offsets = layer.get("gf8_parameter_offsets", {})
    weight_offset = offsets.get("quantized_weight_offset")
    weight_length = offsets.get("quantized_weight_bytes")
    require(weight_offset == 316 and weight_length == EXPECTED_WEIGHT_BYTES,
            "T01 layer0 权重 offset/length 与冻结期望不匹配")
    header = struct.unpack_from("<8I", package, 28)
    require(header[0:6] == (0, 32, 3, 1, 3, EXPECTED_WEIGHT_BYTES),
            f"GF8 layer0 记录头不匹配：{header}")
    package_slice = package[weight_offset:weight_offset + weight_length]
    require(len(package_slice) == EXPECTED_WEIGHT_BYTES and
            sha256_bytes(package_slice) == weight_sha,
            "T65 权重切片与 T01 GF8 package 中 offset/length 对应区域不一致")

    shard = golden_sample.get("network", {}).get("compressed_shard", {})
    shard_path = (ROOT / shard.get("path", "")).resolve()
    require(shard_path == (ROOT / "report" / "evidence" / "S2A-T25" / "tensors" / "sample_000.zlib").resolve(),
            f"T25 shard 位置与任务冻结路径不一致：{shard_path}")
    compressed_sha = sha256_file(shard_path)
    require(compressed_sha == shard.get("sha256") == EXPECTED_T25_SHARD_SHA256,
            f"T25 sample0 压缩 shard 摘要不匹配：{compressed_sha}")
    decompressed = zlib.decompress(shard_path.read_bytes())
    decompressed_sha = sha256_bytes(decompressed)
    require(len(decompressed) == shard.get("decompressed_bytes") == 11_382_150 and
            decompressed_sha == shard.get("decompressed_sha256") == EXPECTED_RAW_NETWORK_SHA256,
            "T25 shard 解压长度或摘要不匹配")
    tensor = next((row for row in golden_sample["network"]["tensors"]
                   if row.get("layer_index") == 0), None)
    require(tensor is not None and tensor.get("shape_nchw") == [1, 32, 208, 208] and
            tensor.get("element_type") == "int8_twos_complement" and tensor.get("stored") is True and
            tensor.get("byte_offset") == 0 and tensor.get("byte_length") == EXPECTED_LAYER0_BYTES,
            "T25 layer0 tensor shape/type/offset/length 与规格不符")
    output_end = tensor["byte_offset"] + tensor["byte_length"]
    expected_raw = decompressed[tensor["byte_offset"]:output_end]
    expected_sha = sha256_bytes(expected_raw)
    require(len(expected_raw) == EXPECTED_LAYER0_BYTES and
            expected_sha == tensor.get("tensor_sha256") == EXPECTED_T25_LAYER0_SHA256,
            f"T25 layer0 tensor SHA/长度不匹配：bytes={len(expected_raw)} sha256={expected_sha}")

    fixture_dir = evidence_dir / "fixture"
    require(not fixture_dir.exists() or (fixture_dir.is_dir() and not fixture_dir.is_symlink()),
            f"夹具目录类型不符：{fixture_dir}")
    fixture_dir.mkdir(parents=True, exist_ok=True)
    input_path = fixture_dir / "sample0_input_chw_int8.bin"
    weight_path = fixture_dir / "sample0_layer0_gf8_weights.bin"
    output_path = fixture_dir / "sample0_layer0_expected_nchw_int8.bin"
    write_new_or_verify(input_path, input_raw)
    write_new_or_verify(weight_path, weight_raw)
    write_new_or_verify(output_path, expected_raw)

    sources = sha256_map({
        "preparer": Path(__file__).resolve(),
        "offline_verifier": VERIFIER_PATH,
        "runner": RUNNER_PATH,
        "testbench": BENCH_PATH,
        "tile_engine": ENGINE_PATH,
        "descriptor_package": DESCRIPTOR_PATH,
        "T01_fixed_samples": FIXED_SAMPLES_PATH,
        "T01_model_manifest": MODEL_MANIFEST_PATH,
        "T65_fixture_manifest": T65_FIXTURE_MANIFEST,
        "T25_index": T25_INDEX_PATH,
        "T25_compressed_shard": shard_path,
        "T01_GF8_package": package_path,
        "T65_input_fixture": T65_INPUT_PATH,
        "T65_weight_fixture": T65_WEIGHT_PATH,
    })
    cache_summary_path = evidence_dir / "cache_policy_summary.json"
    cache_summary = {
        "schema_version": "gestureforge_s2a_t66_cache_policy_v1",
        "task_id": "S2A-T66-TILE01",
        "status": "OFFLINE_POLICY_AND_BUDGET_VERIFIED_SIMULATION_NOT_RUN",
        "baseline_commit": "9fb9ab7b380430c22bf147654157858b52151dad",
        "cache_policy": CACHE_POLICY,
        "layer0_transfer_budget": LAYER0_TRANSFER_BUDGET,
        "source_sha256": sources,
    }
    cache_summary_encoded = (
        json.dumps(cache_summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    write_bound_cache_summary(cache_summary_path, cache_summary_encoded, cache_summary)
    record: dict[str, Any] = {
        "schema_version": "gestureforge_s2a_t66_layer0_golden_fixture_v1",
        "task_id": "S2A-T66-TILE01",
        "status": "OFFLINE_FIXTURE_VERIFIED_SIMULATION_NOT_RUN",
        "baseline_commit": "9fb9ab7b380430c22bf147654157858b52151dad",
        "scope": "sample0 layer0 complete NCHW output tensor; no whole-network claim",
        "cache_policy": CACHE_POLICY,
        "layer0_transfer_budget": LAYER0_TRANSFER_BUDGET,
        "cache_policy_summary": {
            "path": str(cache_summary_path.resolve()),
            "sha256": sha256_bytes(cache_summary_encoded),
        },
        "execution_record_path": str((evidence_dir / "execution_record.json").resolve()),
        "sample": {
            "sample_index": 0,
            "sample_id": sample["sample_id"],
            "frame_id": sample["frame_id"],
            "preprocessed_input_sha256": input_sha,
            "input_shape_nchw": [1, 3, 416, 416],
            "input_bytes": len(input_raw),
            "input_fixture_path": str(input_path.resolve()),
            "input_fixture_sha256": sha256_bytes(input_raw),
        },
        "weights": {
            "package_path": str(package_path.resolve()),
            "package_sha256": package_sha,
            "weight_layer_index": 0,
            "layout": "GFINT8W1 signed INT8 output-channel-major, then input-channel/kernel-y/kernel-x",
            "quantized_weight_offset_bytes": weight_offset,
            "quantized_weight_bytes": weight_length,
            "source_slice_sha256": sha256_bytes(package_slice),
            "fixture_path": str(weight_path.resolve()),
            "fixture_sha256": sha256_bytes(weight_raw),
        },
        "golden": {
            "index_path": str(T25_INDEX_PATH.resolve()),
            "index_sha256": sha256_file(T25_INDEX_PATH),
            "compressed_shard_path": str(shard_path),
            "compressed_shard_bytes": len(shard_path.read_bytes()),
            "compressed_shard_sha256": compressed_sha,
            "decompressed_bytes": len(decompressed),
            "decompressed_sha256": decompressed_sha,
            "layer_index": 0,
            "shape_nchw": tensor["shape_nchw"],
            "element_type": tensor["element_type"],
            "tensor_byte_offset": tensor["byte_offset"],
            "tensor_byte_length": tensor["byte_length"],
            "tensor_sha256": expected_sha,
            "fixture_path": str(output_path.resolve()),
            "fixture_sha256": sha256_bytes(expected_raw),
        },
        "source_sha256": sources,
        "fixture_preparation_runtime": {
            "xvlog_started": False,
            "xelab_started": False,
            "xsim_started": False,
            "full_layer0_compared": False,
            "whole_network_compared": False,
        },
    }
    manifest_path = evidence_dir / "fixture_manifest.json"
    encoded = (json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    write_bound_manifest(manifest_path, encoded, record)
    return record


def main() -> int:
    """执行离线来源核对并创建 T66 layer0 夹具。"""
    parser = argparse.ArgumentParser(description="准备 sample0 layer0 完整黄金夹具")
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    args = parser.parse_args()
    result = materialize(args.evidence_dir)
    print("PASS: T66 离线夹具来源、权重切片和 T25 完整 layer0 tensor 均匹配")
    print(f"input_sha256={result['sample']['input_fixture_sha256']}")
    print(f"weights_sha256={result['weights']['fixture_sha256']}")
    print(f"expected_bytes={result['golden']['tensor_byte_length']} expected_sha256={result['golden']['tensor_sha256']}")
    print(f"cache_policy=decision_A_tile_major summary_sha256={result['cache_policy_summary']['sha256']}")
    print("SIMULATION_NOT_RUN")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FixtureError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
